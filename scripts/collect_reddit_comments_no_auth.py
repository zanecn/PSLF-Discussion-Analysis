"""
collect_reddit_comments_no_auth.py
==================================
Collects Reddit comment trees using the public JSON API (NO PRAW credentials
required). This is the fallback for when Reddit's OAuth app creation form
silently fails (which it does for many users in 2025).

Same output schema as collect_reddit_comments.py (the PRAW version) so
downstream pipeline doesn't care which collector produced the comments.

Tradeoffs vs PRAW:
- Pro: no client_id/client_secret needed; no Reddit OAuth dance
- Pro: same public JSON endpoints the project's post collectors already use
- Con: rate limit is ~30 req/min sustained (vs 100/min with OAuth)
- Con: can only fetch first page of comment trees (~500 per post max);
       deeper comments below the "MoreComments" stub are unreachable
- Con: ~2-3x longer wall-time than PRAW for the same posts

For the PSLF corpus this is fine — most PSLF posts have <100 comments,
well under the no-auth ceiling.

Usage:
    python collect_reddit_comments_no_auth.py
    python collect_reddit_comments_no_auth.py --resume
    python collect_reddit_comments_no_auth.py --max-posts 100  # for testing
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import time
from datetime import datetime, timezone

# Force UTF-8 stdout (for Windows cp1252 + comment bodies with emoji)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import requests
from textblob import TextBlob
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pslf_search_terms import filter_pslf_relevant
    HAS_PSLF_FILTER = True
except ImportError:
    HAS_PSLF_FILTER = False

# Same schema as the PRAW collector for drop-in compatibility
COMMENT_FIELDS = [
    "comment_id", "post_id", "post_subreddit", "parent_id", "author",
    "body", "score", "created_utc", "created_datetime", "depth",
    "is_top_level", "profession", "polarity", "subjectivity", "word_count",
]

POST_FILES = [
    "reddit_professions_pslf.csv",                    # 11,845 raw → 3,806 PSLF
    "comprehensive_medical_pslf_discussions.csv",     # 605 (legacy)
    "comprehensive_teacher_pslf_discussions.csv",     # 521 (legacy)
    "reddit_new_subs_pslf.csv",                       # 52 PSLF (PA/NP)
    "reddit_arctic_shift_pslf.csv",                   # if present
]
OUTPUT_FILE = "reddit_comments_pslf.csv"

# Conservative rate limit (Reddit unauth = 60/min, we go ~half)
RATE_LIMIT_SLEEP = 2.0  # seconds between post fetches
MAX_RETRIES_PER_POST = 3
MAX_DEPTH = 5

HEADERS = {
    "User-Agent": (
        "PSLF-Discussion-Analysis/2.0 (academic research; "
        "https://github.com/zanecn/PSLF-Discussion-Analysis)"
    ),
    "Accept": "application/json",
}


def load_post_ids() -> list[dict]:
    """Load PSLF-filtered post IDs from all source CSVs (with strict filter)."""
    import pandas as pd
    posts = []
    seen = set()
    for fpath in POST_FILES:
        if not os.path.exists(fpath):
            continue
        try:
            df = pd.read_csv(fpath)
            text_col = ("combined_text" if "combined_text" in df.columns
                        else "selftext" if "selftext" in df.columns else None)
            title_col = "title" if "title" in df.columns else None
            if HAS_PSLF_FILTER and text_col and title_col:
                tm = filter_pslf_relevant(df[text_col].fillna(""))
                tt = filter_pslf_relevant(df[title_col].fillna(""))
                df = df[tm | tt].copy()
            n_added = 0
            for _, row in df.iterrows():
                pid = str(row.get("id", "")).strip()
                if pid and pid not in seen:
                    seen.add(pid)
                    posts.append({
                        "id": pid,
                        "subreddit": row.get("subreddit", ""),
                        "profession": row.get("profession", ""),
                    })
                    n_added += 1
            print(f"  Loaded {n_added:,} PSLF-filtered posts from {fpath}")
        except Exception as e:
            print(f"  [WARN] {fpath}: {e}")
    return posts


def analyze_sentiment(text: str) -> tuple[float, float]:
    if not text or not text.strip():
        return float("nan"), float("nan")
    try:
        blob = TextBlob(text[:5000])
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return float("nan"), float("nan")


def fetch_post_comments(sess: requests.Session, post_id: str) -> list[dict] | None:
    """Fetch the JSON for a single post and return the raw comments listing."""
    url = f"https://old.reddit.com/comments/{post_id}.json?limit=500&depth=10&showmore=false"
    for attempt in range(MAX_RETRIES_PER_POST):
        try:
            r = sess.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and len(data) >= 2:
                    return data[1].get("data", {}).get("children", [])
                return []
            if r.status_code == 429:
                # Rate-limited; back off and retry
                time.sleep(60 + attempt * 30)
                continue
            if r.status_code in (404, 403):
                # Deleted, removed, or quarantined — skip silently
                return []
            tqdm.write(f"  [WARN] {post_id}: HTTP {r.status_code}")
            return []
        except requests.exceptions.RequestException as e:
            tqdm.write(f"  [WARN] {post_id}: {e}")
            time.sleep(5)
    return None


def flatten_comments(children, post_meta: dict, max_depth: int = MAX_DEPTH,
                     depth: int = 0) -> list[dict]:
    """Recursively flatten a JSON comment tree into rows."""
    rows = []
    for child in children:
        if not isinstance(child, dict):
            continue
        kind = child.get("kind")
        cdata = child.get("data", {})
        if kind == "more":
            continue  # skip "MoreComments" stubs
        if kind != "t1":
            continue  # only actual comments
        if depth > max_depth:
            continue

        body = cdata.get("body") or ""
        if not body:
            continue
        pol, subj = analyze_sentiment(body)
        created_utc = cdata.get("created_utc", 0)
        try:
            created_dt = datetime.fromtimestamp(int(created_utc),
                                                  tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, OSError):
            created_dt = ""

        rows.append({
            "comment_id": cdata.get("id", ""),
            "post_id": post_meta["id"],
            "post_subreddit": post_meta["subreddit"],
            "parent_id": cdata.get("parent_id", ""),
            "author": cdata.get("author") or "[deleted]",
            "body": body,
            "score": cdata.get("score", 0),
            "created_utc": created_utc,
            "created_datetime": created_dt,
            "depth": depth,
            "is_top_level": depth == 0,
            "profession": post_meta["profession"],
            "polarity": pol,
            "subjectivity": subj,
            "word_count": len(body.split()),
        })

        # Recurse into replies
        replies = cdata.get("replies")
        if isinstance(replies, dict):
            sub_children = replies.get("data", {}).get("children", [])
            rows.extend(flatten_comments(sub_children, post_meta, max_depth, depth + 1))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--resume", action="store_true",
                        help="Skip posts already collected")
    parser.add_argument("--max-posts", type=int, default=None,
                        help="Max posts to process (for testing)")
    args = parser.parse_args()

    sess = requests.Session()
    sess.headers.update(HEADERS)

    # Pre-flight test
    print("Pre-flight: testing Reddit JSON API connectivity...")
    test = sess.get("https://old.reddit.com/r/PSLF/about.json", timeout=15)
    if test.status_code != 200:
        print(f"[ABORT] Reddit JSON API returned {test.status_code}. Check connectivity.")
        sys.exit(1)
    print(f"  OK (HTTP {test.status_code})")

    # Load posts
    print("\nLoading PSLF-filtered post IDs...")
    posts = load_post_ids()
    print(f"\n→ {len(posts):,} unique PSLF-filtered posts to process")

    if args.max_posts:
        posts = posts[: args.max_posts]
        print(f"→ Limiting to first {len(posts)} posts (--max-posts)")

    # Resume
    collected = set()
    if args.resume and os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                collected.add(row["post_id"])
        print(f"→ Resuming: {len(collected):,} posts already collected")

    mode = "a" if (args.resume and collected) else "w"
    total_comments = 0
    errors = 0
    deleted_or_404 = 0

    with open(args.output, mode, newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=COMMENT_FIELDS)
        if mode == "w":
            writer.writeheader()

        for post_meta in tqdm(posts, desc="Comments", unit="post"):
            pid = post_meta["id"]
            if pid in collected:
                continue
            children = fetch_post_comments(sess, pid)
            if children is None:
                errors += 1
                continue
            if not children:
                deleted_or_404 += 1
                time.sleep(RATE_LIMIT_SLEEP)
                continue
            rows = flatten_comments(children, post_meta)
            for r in rows:
                writer.writerow(r)
            total_comments += len(rows)
            time.sleep(RATE_LIMIT_SLEEP)

    print(f"\n{'=' * 60}")
    print("Collection complete!")
    print(f"  Posts processed:           {len(posts) - len(collected):,}")
    print(f"  Total comments collected:  {total_comments:,}")
    print(f"  Posts with no comments:    {deleted_or_404:,}")
    print(f"  Posts with errors:         {errors:,}")
    print(f"  Output:                    {args.output}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
