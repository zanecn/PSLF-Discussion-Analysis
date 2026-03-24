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

RATE_LIMIT = 2.0  # seconds between requests (old.reddit.com rate limit ~30/min for unauthenticated)

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

# Subreddits mapped to profession labels
SUBREDDIT_PROFESSIONS = {
    # Nursing
    "nursing": "nursing",
    "StudentNurse": "nursing",
    "nursepractitioner": "nursing",
    # Social work
    "socialwork": "social_work",
    # Government / Federal
    "fednews": "federal_employee",
    "govfire": "federal_employee",
    # Law
    "LawSchool": "law",
    # Pharmacy
    "pharmacy": "pharmacy",
    # Allied health
    "physicianassistant": "physician_assistant",
    "OccupationalTherapy": "occupational_therapy",
    "slp": "speech_language_pathology",
    # General PSLF (captures all professions)
    "PSLF": "general_pslf",
    "StudentLoans": "general_student_loans",
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


def search_subreddit_json(
    session: requests.Session,
    subreddit: str,
    query: str,
    max_results: int = 100,
) -> list[dict]:
    """Search a subreddit using old.reddit.com JSON endpoint.

    Paginates with 'after' cursor. Returns raw post dicts.
    """
    posts = []
    after = None
    per_page = 25  # Reddit max per page for JSON

    while len(posts) < max_results:
        params = {
            "q": query,
            "restrict_sr": "on",
            "sort": "relevance",
            "t": "all",
            "limit": per_page,
        }
        if after:
            params["after"] = after

        url = f"https://old.reddit.com/r/{subreddit}/search.json"

        for attempt in range(3):
            try:
                resp = session.get(url, params=params, headers=HEADERS_HTTP, timeout=15)
                if resp.status_code == 200:
                    break
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 10))
                    tqdm.write(f"    Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                if resp.status_code in (403, 451):
                    return posts  # subreddit restricted/quarantined
                time.sleep(RATE_LIMIT * (attempt + 1))
            except requests.exceptions.RequestException as e:
                if attempt == 2:
                    tqdm.write(f"    [ERROR] r/{subreddit} search: {e}")
                    return posts
                time.sleep(RATE_LIMIT * (attempt + 1))

        if resp.status_code != 200:
            break

        try:
            data = resp.json()
        except json.JSONDecodeError:
            break

        children = data.get("data", {}).get("children", [])
        if not children:
            break

        for child in children:
            if child.get("kind") == "t3":  # link/post
                posts.append(child["data"])

        # Pagination
        after = data.get("data", {}).get("after")
        if not after:
            break

        time.sleep(RATE_LIMIT)

    return posts[:max_results]


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
