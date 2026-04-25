"""
collect_reddit_professions.py
==============================
Collects PSLF-related posts from profession-specific subreddits using
Reddit's public JSON endpoints (no API key required).

Subreddits: nursing, socialwork, fednews, LawSchool, pharmacy, govfire,
            StudentNurse, nursepractitioner, physicianassistant,
            OccupationalTherapy, slp (speech-language pathology)

Produces: reddit_professions_pslf.csv

Uses old.reddit.com/.json endpoints (rate limit: ~60 req/min).
Paginates with 'after' cursor to collect all available results.

Requires: pip install requests textblob tqdm

Usage:
    python collect_reddit_professions.py
    python collect_reddit_professions.py --max_per_sub 500
"""

import argparse
import csv
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone

import requests
from textblob import TextBlob
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_FILE = "reddit_professions_pslf.csv"

HEADERS_HTTP = {
    "User-Agent": "PSLF-Analysis/2.0 (academic research, github.com/zanecn/PSLF-Discussion-Analysis)",
}

RATE_LIMIT = 2.5  # seconds between requests (old.reddit.com rate limit ~30/min for unauthenticated)

# Sort modes — use 2 to balance coverage vs rate limiting
SORT_MODES = ["relevance", "new"]

FIELDS = [
    "id",
    "subreddit",
    "profession",
    "title",
    "selftext",
    "combined_text",
    "author",
    "score",
    "num_comments",
    "created_utc",
    "created_datetime",
    "permalink",
    "url",
    "upvote_ratio",
    "is_self",
    "link_flair_text",
    "word_count",
    "polarity",
    "subjectivity",
    "query_matched",
    "scraped_at",
]

# Subreddits where PSLF is a PRIMARY topic — people making loan/career decisions
# based on forgiveness policy, not general profession discussion.
SUBREDDIT_PROFESSIONS = {
    # PSLF-specific communities (core)
    "PSLF": "general_pslf",
    "StudentLoans": "general_student_loans",
    # Medical — high debt ($200K+), PSLF shapes specialty/employer choice
    "Residency": "medical",
    "medicalschool": "medical",
    # Nursing — PSLF/NHSC eligible, nonprofit hospital employment
    "nursing": "nursing",
    "StudentNurse": "nursing",
    "nursepractitioner": "nursing",
    # Teaching — Teacher Loan Forgiveness + PSLF, Title I schools
    "Teachers": "teaching",
    # Law — $130K+ debt, public interest law vs biglaw driven by PSLF
    "LawSchool": "law",
    # Social work — nearly universal PSLF eligibility (nonprofit/govt)
    "socialwork": "social_work",
    # Federal employees — automatic PSLF qualifying employer
    "fednews": "federal_employee",
    "govfire": "federal_employee",
    # Pharmacy — $170K avg debt, hospital/VA employment for PSLF
    "pharmacy": "pharmacy",
    # Allied health — OT/PT/SLP with grad school debt + nonprofit employers
    "physicianassistant": "physician_assistant",
    "OccupationalTherapy": "occupational_therapy",
    "slp": "speech_language_pathology",
    # General-finance subs that incidentally discuss PSLF (added post-hoc 2026-04;
    # documented in audit consensus to align CSV with config)
    "personalfinance": "general_finance",
    "financialindependence": "general_finance",
}

try:
    from pslf_search_terms import SEARCH_TERMS_SIMPLE as SEARCH_QUERIES
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import SEARCH_TERMS_SIMPLE as SEARCH_QUERIES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def analyze_sentiment(text: str) -> tuple:
    """Return (polarity, subjectivity) via TextBlob. NaN on error."""
    if not text or not text.strip():
        return float("nan"), float("nan")
    try:
        blob = TextBlob(text[:5000])
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return float("nan"), float("nan")


def _fetch_search_page(
    session: requests.Session,
    subreddit: str,
    params: dict,
) -> tuple[list[dict], str | None]:
    """Fetch one page of Reddit search results. Returns (posts, after_cursor)."""
    url = f"https://old.reddit.com/r/{subreddit}/search.json"
    resp = None

    for attempt in range(3):
        try:
            resp = session.get(url, params=params, headers=HEADERS_HTTP, timeout=15)
            if resp.status_code == 200:
                break
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 15))
                time.sleep(wait)
                continue
            if resp.status_code in (403, 451):
                return [], None
            time.sleep(RATE_LIMIT * (attempt + 1))
        except requests.exceptions.RequestException:
            if attempt == 2:
                return [], None
            time.sleep(RATE_LIMIT * (attempt + 1))

    if resp is None or resp.status_code != 200:
        return [], None

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return [], None

    children = data.get("data", {}).get("children", [])
    posts = [c["data"] for c in children if c.get("kind") == "t3"]
    after = data.get("data", {}).get("after")
    return posts, after


def search_subreddit_json(
    session: requests.Session,
    subreddit: str,
    query: str,
    max_results: int = 500,
) -> list[dict]:
    """Search a subreddit using old.reddit.com JSON endpoint.

    Uses multiple sort modes (relevance, new, top, comments) and
    paginates each to maximize unique results beyond Reddit's per-query cap.
    """
    all_posts = {}  # id -> post dict (dedup by ID)

    for sort in SORT_MODES:
        if len(all_posts) >= max_results:
            break

        after = None
        pages_fetched = 0
        max_pages = 20  # 20 pages × 25 = 500 results per sort mode

        while pages_fetched < max_pages and len(all_posts) < max_results:
            params = {
                "q": query,
                "restrict_sr": "on",
                "sort": sort,
                "t": "all",
                "limit": 25,
            }
            if after:
                params["after"] = after

            posts, after = _fetch_search_page(session, subreddit, params)

            if not posts:
                break

            new_count = 0
            for p in posts:
                pid = p.get("id", "")
                if pid and pid not in all_posts:
                    all_posts[pid] = p
                    new_count += 1

            pages_fetched += 1

            # If this page returned zero new posts, this sort mode is exhausted
            if new_count == 0:
                break

            if not after:
                break

            time.sleep(RATE_LIMIT)

    return list(all_posts.values())[:max_results]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Collect PSLF posts from profession-specific subreddits"
    )
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max_per_sub", type=int, default=200,
                        help="Max posts per subreddit (across all queries)")
    parser.add_argument("--subreddits", nargs="*", default=None,
                        help="Specific subreddits to scrape (default: all)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("Reddit Multi-Profession PSLF Collector (JSON API)")
    print(f"{'='*60}")

    subs_to_scrape = args.subreddits or list(SUBREDDIT_PROFESSIONS.keys())
    print(f"  Subreddits: {len(subs_to_scrape)}")
    print(f"  Search queries: {len(SEARCH_QUERIES)}")
    print(f"  Max per sub: {args.max_per_sub}")

    all_posts = []
    seen_ids = set()

    with requests.Session() as session:
        for sub in tqdm(subs_to_scrape, desc="Subreddits"):
            profession = SUBREDDIT_PROFESSIONS.get(sub, sub)
            sub_posts = []

            for query in SEARCH_QUERIES:
                raw_posts = search_subreddit_json(
                    session, sub, query,
                    max_results=args.max_per_sub - len(sub_posts),
                )

                for p in raw_posts:
                    pid = p.get("id", "")
                    if pid in seen_ids:
                        continue
                    seen_ids.add(pid)

                    title = p.get("title", "")
                    selftext = p.get("selftext", "")
                    combined = f"{title} {selftext}".strip()
                    pol, subj = analyze_sentiment(combined)
                    created = p.get("created_utc", 0)

                    row = {
                        "id": pid,
                        "subreddit": p.get("subreddit", sub),
                        "profession": profession,
                        "title": title,
                        "selftext": selftext[:10000],
                        "combined_text": combined[:10000],
                        "author": p.get("author", "[deleted]"),
                        "score": p.get("score", 0),
                        "num_comments": p.get("num_comments", 0),
                        "created_utc": created,
                        "created_datetime": datetime.fromtimestamp(
                            created, tz=timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S") if created else "",
                        "permalink": p.get("permalink", ""),
                        "url": p.get("url", ""),
                        "upvote_ratio": p.get("upvote_ratio", 0),
                        "is_self": p.get("is_self", True),
                        "link_flair_text": p.get("link_flair_text", "") or "",
                        "word_count": len(combined.split()),
                        "polarity": pol,
                        "subjectivity": subj,
                        "query_matched": query,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    }
                    sub_posts.append(row)

                if len(sub_posts) >= args.max_per_sub:
                    break

            all_posts.extend(sub_posts)
            tqdm.write(f"  r/{sub}: {len(sub_posts)} posts ({profession})")

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for post in all_posts:
            writer.writerow(post)

    # Summary
    print(f"\n{'='*60}")
    print("Collection complete!")
    print(f"  Total unique posts: {len(all_posts):,}")
    from collections import Counter
    prof_counts = Counter(p["profession"] for p in all_posts)
    for prof, count in prof_counts.most_common():
        subs = set(p["subreddit"] for p in all_posts if p["profession"] == prof)
        print(f"    {prof}: {count:,} posts from {', '.join(sorted(subs))}")
    if all_posts:
        import math
        pols = [p["polarity"] for p in all_posts if not math.isnan(p["polarity"])]
        if pols:
            print(f"  Mean polarity: {sum(pols)/len(pols):.4f}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
