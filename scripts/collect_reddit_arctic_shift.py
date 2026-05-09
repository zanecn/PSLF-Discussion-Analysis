"""
collect_reddit_arctic_shift.py
==============================
Pulls Reddit PSLF posts via the Arctic Shift API (the spiritual successor
to Pushshift). Bypasses Reddit's 1000-result-per-listing JSON-API cap by
querying the full historical Reddit dump.

Output schema matches `reddit_professions_pslf.csv` for drop-in compatibility
with the existing pipeline. Posts new to this collector are appended to the
main CSV; existing IDs are skipped.

Why this exists:
- Reddit JSON API caps each listing at 1000 results regardless of sort/window.
- The R/C volume artifact diagnostic (~10x recency-bias estimate) implies the
  project's pre-2018 Reddit coverage is severely incomplete.
- Arctic Shift hosts full historical Reddit dumps (2005-present) accessible
  via a free API (~2000 req per rate-limit window).
- Critical for the substantive paper: the current corpus has almost no
  pre-2018 r/PSLF posts because that's behind the API cap.

Rate limiting:
- Arctic Shift returns X-RateLimit-Remaining and X-RateLimit-Reset headers.
- We respect these honestly: if remaining < 100, sleep until reset.
- Typical per-call: ~50-100 ms. Comfortable to pull 50K posts in ~1 hour.

Usage:
    python collect_reddit_arctic_shift.py
    python collect_reddit_arctic_shift.py --subreddits PSLF Residency
    python collect_reddit_arctic_shift.py --year-end 2018 --output reddit_arctic_pre2018.csv
    python collect_reddit_arctic_shift.py --dry-run
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import re
import sys
import time
from datetime import datetime, timezone

# Force UTF-8 stdout so Unicode arrows don't crash on Windows cp1252
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import requests
from textblob import TextBlob
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import filter_pslf_relevant
from collect_reddit_professions import SUBREDDIT_PROFESSIONS

API_BASE = "https://arctic-shift.photon-reddit.com/api"
DEFAULT_OUTPUT = "reddit_arctic_shift_pslf.csv"

# PSLF-relevant search terms (broad anchors; strict filter applied post-hoc)
SEARCH_TERMS = [
    "PSLF",
    "public service loan forgiveness",
    "MOHELA",
    "qualifying employment",
    "loan forgiveness",
    "TEPSLF",
    "income-driven repayment",
    "SAVE plan",
    "PAYE",
    "REPAYE",
]

# Output schema mirrors reddit_professions_pslf.csv exactly so the new posts
# can be appended without schema mismatch
FIELDS = [
    "id", "subreddit", "profession", "title", "selftext", "combined_text",
    "author", "score", "num_comments", "created_utc", "created_datetime",
    "permalink", "url", "upvote_ratio", "is_self", "link_flair_text",
    "word_count", "polarity", "subjectivity", "query_matched", "scraped_at",
]


def make_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "PSLF-Discussion-Analysis/2.0 (academic research; "
                       "https://github.com/zanecn/PSLF-Discussion-Analysis)",
        "Accept": "application/json",
    })
    return sess


def respect_rate_limit(response: requests.Response):
    """If we're close to the rate-limit floor, sleep until reset.

    Round-7 fix: was overly aggressive (triggered at remaining<50). The API
    returns ~30 remaining frequently in normal use without imminent
    throttling. Now only triggers when remaining is genuinely low (<5).
    """
    remaining = response.headers.get("X-RateLimit-Remaining")
    reset = response.headers.get("X-RateLimit-Reset")
    if remaining is None or reset is None:
        return
    try:
        remaining_i = int(remaining)
        reset_i = int(reset)
    except ValueError:
        return
    if remaining_i < 5:
        wait = max(reset_i + 2, 5)
        tqdm.write(f"  [rate-limit] {remaining_i} remaining, sleeping {wait}s for reset")
        time.sleep(wait)


def search_arctic_shift(sess: requests.Session, subreddit: str, after: int,
                         before: int, search_term: str | None = None,
                         limit: int = 100) -> list[dict]:
    """Single search call to Arctic Shift posts API.

    Arctic Shift max limit per call is 100 (NOT 1000 — that's a recent change
    that bit us in early testing). We page by created_utc using
    `after`/`before` timestamps.

    Note: Arctic Shift's full-text search is approximate; we apply the
    project's anchored PSLF filter locally as a post-hoc verification.
    """
    params = {
        "subreddit": subreddit,
        "after": after,
        "before": before,
        "sort": "asc",
        "limit": limit,
    }
    if search_term:
        # Arctic Shift API uses 'query' (not 'q' as in some other clones)
        params["query"] = search_term
    try:
        r = sess.get(f"{API_BASE}/posts/search", params=params, timeout=60)
        if r.status_code != 200:
            tqdm.write(f"  [WARN] {subreddit} {search_term!r}: HTTP {r.status_code}")
            return []
        respect_rate_limit(r)
        data = r.json()
        return data.get("data", [])
    except Exception as e:
        tqdm.write(f"  [ERROR] {subreddit} {search_term!r}: {e}")
        return []


def paginate_subreddit_year(sess: requests.Session, subreddit: str,
                              year_start: int, year_end: int,
                              search_term: str | None = None) -> list[dict]:
    """Paginate through a subreddit between years, using created_utc cursor."""
    all_posts = []
    seen_ids = set()
    after = int(datetime(year_start, 1, 1, tzinfo=timezone.utc).timestamp())
    before = int(datetime(year_end, 1, 1, tzinfo=timezone.utc).timestamp())
    safety_iters = 200  # 200 pages × 100 = 20K posts max per (sub × term × year-range)
    iter_count = 0
    while iter_count < safety_iters:
        page = search_arctic_shift(sess, subreddit, after, before, search_term)
        if not page:
            break
        new = [p for p in page if p.get("id") and p["id"] not in seen_ids]
        for p in new:
            seen_ids.add(p["id"])
        all_posts.extend(new)
        if len(page) < 100:
            break  # no more results in this window (limit is 100/page)
        # Advance cursor: take the latest created_utc and continue
        max_ts = max(p.get("created_utc", 0) for p in page)
        if max_ts <= after:
            break  # no progress, abort
        after = max_ts + 1
        iter_count += 1
        time.sleep(0.5)  # polite pause between pages
    return all_posts


def normalize_post(post: dict, subreddit: str, profession: str,
                    search_term: str) -> dict | None:
    """Convert Arctic Shift post dict to project schema."""
    pid = post.get("id")
    if not pid:
        return None
    title = post.get("title") or ""
    selftext = post.get("selftext") or ""
    combined = f"{title} {selftext}".strip()
    if not combined:
        return None
    created_utc = post.get("created_utc", 0)
    try:
        created_iso = datetime.fromtimestamp(int(created_utc),
                                              tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        created_iso = ""
    # Sentiment
    pol = subj = float("nan")
    try:
        if combined and len(combined) >= 5:
            blob = TextBlob(combined[:5000])
            pol = round(blob.sentiment.polarity, 6)
            subj = round(blob.sentiment.subjectivity, 6)
    except Exception:
        pass
    return {
        "id": pid,
        "subreddit": subreddit,
        "profession": profession,
        "title": title,
        "selftext": selftext,
        "combined_text": combined,
        "author": post.get("author") or "",
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "created_utc": int(created_utc) if created_utc else 0,
        "created_datetime": created_iso,
        "permalink": post.get("permalink") or "",
        "url": post.get("url") or "",
        "upvote_ratio": post.get("upvote_ratio", ""),
        "is_self": post.get("is_self", True),
        "link_flair_text": post.get("link_flair_text") or "",
        "word_count": len(combined.split()),
        "polarity": pol,
        "subjectivity": subj,
        "query_matched": search_term,
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def load_existing_ids(csv_paths: list[str]) -> set[str]:
    """Load all post IDs from existing CSVs to avoid duplicate scraping."""
    ids = set()
    for p in csv_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        pid = row.get("id") or row.get("post_id")
                        if pid:
                            ids.add(pid)
            except Exception as e:
                print(f"  [WARN] Could not read {p}: {e}")
    return ids


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--subreddits", nargs="*", default=None,
                        help="Specific subreddits (default: all from SUBREDDIT_PROFESSIONS)")
    parser.add_argument("--year-start", type=int, default=2010)
    parser.add_argument("--year-end", type=int, default=2026)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--exclude-existing", nargs="*",
                        default=["reddit_professions_pslf.csv",
                                 "comprehensive_medical_pslf_discussions.csv",
                                 "comprehensive_teacher_pslf_discussions.csv",
                                 "reddit_new_subs_pslf.csv"],
                        help="CSVs whose IDs we should skip (already in main corpus)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Test API and report counts; do not write output")
    parser.add_argument("--search-terms", nargs="*", default=None,
                        help="Override default PSLF search terms")
    args = parser.parse_args()

    subs_to_query = args.subreddits or list(SUBREDDIT_PROFESSIONS.keys())
    search_terms = args.search_terms or SEARCH_TERMS
    existing_ids = load_existing_ids(args.exclude_existing)
    print(f"Loaded {len(existing_ids):,} existing post IDs to skip")
    print(f"Subreddits: {len(subs_to_query)}; search terms: {len(search_terms)}")
    print(f"Year range: {args.year_start}-{args.year_end}")
    print(f"Output: {args.output}")

    sess = make_session()

    # Test API
    print("\nTesting Arctic Shift API...")
    test = search_arctic_shift(sess, "PSLF", 1577836800, 1577923200, "PSLF", limit=5)
    if not test:
        print("[ABORT] API test failed. Check connectivity.")
        sys.exit(1)
    print(f"  Test OK: {len(test)} sample posts retrieved.")

    if args.dry_run:
        # Just discover counts via paginated calls (limit=100 max per call)
        print("\n[DRY RUN] Discovering post counts per subreddit-year (limit=100/call)...")
        total_found = 0
        for sub in subs_to_query[:5]:  # limit to first 5 for dry run
            sub_total = 0
            for year in range(args.year_start, args.year_end + 1):
                # Single call per year for the dry-run estimate (will undercount
                # if there are >100 PSLF posts that year — flag those subs)
                page = search_arctic_shift(
                    sess, sub,
                    int(datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()),
                    int(datetime(year + 1, 1, 1, tzinfo=timezone.utc).timestamp()),
                    "PSLF", limit=100)
                if page:
                    new_count = sum(1 for p in page if p.get("id") not in existing_ids)
                    flag = " (>=100 — pagination needed)" if len(page) >= 100 else ""
                    sub_total += new_count
                    if new_count > 0:
                        print(f"  r/{sub} {year}: {len(page):>3d} total, "
                              f"{new_count:>3d} new{flag}")
                time.sleep(0.3)
            total_found += sub_total
            print(f"  → r/{sub} subtotal: ~{sub_total} new posts (single search term, undercount)\n")
        print(f"[DRY RUN] Discovered ~{total_found} new posts across first 5 subreddits "
              f"with 1 search term ('PSLF').\n"
              f"Full run uses {len(search_terms)} search terms across {len(subs_to_query)} subs;\n"
              f"realistic total estimate: {total_found * len(search_terms) * len(subs_to_query) // 5} "
              f"new posts (overlapping; actual after dedup likely 30-50% of this).")
        return

    # Full run: per subreddit, per search term, paginate over year ranges
    rows = []
    seen_in_run = set(existing_ids)
    print(f"\nStarting Arctic Shift pull for {len(subs_to_query)} subreddits...")
    pbar = tqdm(total=len(subs_to_query) * len(search_terms), desc="Subreddit×Term")
    for sub in subs_to_query:
        prof = SUBREDDIT_PROFESSIONS.get(sub, sub)
        for term in search_terms:
            try:
                posts = paginate_subreddit_year(sess, sub, args.year_start,
                                                  args.year_end, term)
                # Filter to new IDs and apply project's PSLF strict filter
                new_posts = [p for p in posts if p.get("id") not in seen_in_run]
                if new_posts:
                    import pandas as pd
                    titles = pd.Series([p.get("title", "") for p in new_posts])
                    bodies = pd.Series([(p.get("title", "") + " " +
                                         p.get("selftext", "")) for p in new_posts])
                    pslf_match = (filter_pslf_relevant(titles) |
                                  filter_pslf_relevant(bodies))
                    new_filt = [p for p, m in zip(new_posts, pslf_match) if m]
                    for p in new_filt:
                        norm = normalize_post(p, sub, prof, term)
                        if norm:
                            rows.append(norm)
                            seen_in_run.add(p.get("id"))
                pbar.set_postfix({"sub": sub, "term": term[:15],
                                   "new_posts_so_far": len(rows)})
            except Exception as e:
                tqdm.write(f"  [ERROR] r/{sub} '{term}': {e}")
            pbar.update(1)
            time.sleep(0.3)
    pbar.close()

    print(f"\nCollected {len(rows):,} new PSLF-filtered posts from Arctic Shift")

    # Write output
    if rows:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        print(f"Wrote {args.output}")

        # Summary by subreddit
        print("\nPosts per subreddit:")
        from collections import Counter
        for sub, n in Counter(r["subreddit"] for r in rows).most_common():
            print(f"  r/{sub:<25s} {n:>5d}")
        # Year breakdown
        print("\nPosts per year:")
        years = Counter()
        for r in rows:
            try:
                y = datetime.fromtimestamp(int(r["created_utc"]), tz=timezone.utc).year
                years[y] += 1
            except (ValueError, OSError):
                pass
        for y in sorted(years.keys()):
            print(f"  {y}: {years[y]:>5d}")
    else:
        print("[WARN] No new posts to write")


if __name__ == "__main__":
    main()
