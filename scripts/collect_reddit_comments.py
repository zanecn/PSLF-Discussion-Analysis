"""
collect_reddit_comments.py
==========================
Collects top-level and nested comments for all posts in the existing
PSLF Discussion Analysis datasets. Produces a separate comments CSV
that can be joined to posts via `post_id`.

Requires: pip install praw textblob tqdm

Usage:
    python collect_reddit_comments.py \
        --client_id YOUR_ID \
        --client_secret YOUR_SECRET \
        --user_agent "PSLF-Analysis/2.0"
"""

import argparse
import csv
import os
import time
from datetime import datetime, timezone

import praw
from textblob import TextBlob
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
POST_FILES = [
    "comprehensive_medical_pslf_discussions.csv",
    "comprehensive_teacher_pslf_discussions.csv",
]
OUTPUT_FILE = "reddit_comments_pslf.csv"
MAX_COMMENT_DEPTH = 5          # max nesting depth to collect
MAX_COMMENTS_PER_POST = 200    # limit "More Comments" expansion
RATE_LIMIT_SLEEP = 1.0         # seconds between posts (be polite)

COMMENT_FIELDS = [
    "comment_id",
    "post_id",
    "post_subreddit",
    "parent_id",
    "author",
    "body",
    "score",
    "created_utc",
    "created_datetime",
    "depth",
    "is_top_level",
    "profession",        # inherited from parent post
    "polarity",
    "subjectivity",
    "word_count",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_post_ids(files: list[str]) -> list[dict]:
    """Load post IDs and metadata from existing CSVs."""
    posts = []
    seen = set()
    for fpath in files:
        if not os.path.exists(fpath):
            print(f"  [WARN] File not found: {fpath}, skipping.")
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row.get("id", "").strip()
                if pid and pid not in seen:
                    seen.add(pid)
                    posts.append({
                        "id": pid,
                        "subreddit": row.get("subreddit", ""),
                        "profession": row.get("profession", ""),
                        "permalink": row.get("permalink", ""),
                    })
    return posts


def analyze_sentiment(text: str) -> tuple[float | None, float | None]:
    """Return (polarity, subjectivity) via TextBlob.

    Returns (NaN, NaN) on error or empty text (M1 fix).
    """
    if not text or not text.strip():
        return float("nan"), float("nan")
    try:
        blob = TextBlob(text[:5000])  # M8 fix: cap length for performance
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return float("nan"), float("nan")


def flatten_comments(comment_forest, post_meta: dict, max_depth: int) -> list[dict]:
    """Recursively flatten a comment forest into rows.

    M6 fix: reverse initial stack so pop() processes in correct order.
    """
    rows = []
    stack = [(c, 0) for c in reversed(list(comment_forest))]
    while stack:
        comment, depth = stack.pop()
        if isinstance(comment, praw.models.MoreComments):
            continue
        if depth > max_depth:
            continue

        body = comment.body or ""
        pol, subj = analyze_sentiment(body)
        created = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc)

        rows.append({
            "comment_id": comment.id,
            "post_id": post_meta["id"],
            "post_subreddit": post_meta["subreddit"],
            "parent_id": comment.parent_id,
            "author": str(comment.author) if comment.author else "[deleted]",
            "body": body,
            "score": comment.score,
            "created_utc": comment.created_utc,
            "created_datetime": created.strftime("%Y-%m-%d %H:%M:%S"),
            "depth": depth,
            "is_top_level": depth == 0,
            "profession": post_meta["profession"],
            "polarity": pol,
            "subjectivity": subj,
            "word_count": len(body.split()),
        })

        # Add replies to stack (reversed for correct ordering with LIFO pop)
        for reply in reversed(list(comment.replies)):
            stack.append((reply, depth + 1))

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect Reddit comments for PSLF posts")
    parser.add_argument("--client_id", required=True, help="Reddit API client ID")
    parser.add_argument("--client_secret", required=True, help="Reddit API client secret")
    parser.add_argument("--user_agent", default="PSLF-Analysis/2.0", help="Reddit API user agent")
    parser.add_argument("--output", default=OUTPUT_FILE, help="Output CSV path")
    parser.add_argument("--resume", action="store_true", help="Skip posts already collected")
    args = parser.parse_args()

    # Initialize Reddit client (read-only)
    reddit = praw.Reddit(
        client_id=args.client_id,
        client_secret=args.client_secret,
        user_agent=args.user_agent,
    )
    print(f"Reddit client initialized (read-only: {reddit.read_only})")

    # Load existing post IDs
    posts = load_post_ids(POST_FILES)
    print(f"Loaded {len(posts)} unique posts from {len(POST_FILES)} files")

    # Resume support
    collected_post_ids = set()
    if args.resume and os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                collected_post_ids.add(row["post_id"])
        print(f"Resuming: {len(collected_post_ids)} posts already collected")

    # Open output file (M5 fix: use context manager to prevent file handle leak)
    mode = "a" if args.resume and collected_post_ids else "w"
    total_comments = 0
    errors = 0

    with open(args.output, mode, newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=COMMENT_FIELDS)
        if mode == "w":
            writer.writeheader()

        for post_meta in tqdm(posts, desc="Collecting comments"):
            pid = post_meta["id"]
            if pid in collected_post_ids:
                continue

            try:
                submission = reddit.submission(id=pid)
                submission.comments.replace_more(limit=MAX_COMMENTS_PER_POST)
                # C4 fix: single flatten call using comment forest (not .list())
                rows = flatten_comments(submission.comments, post_meta, MAX_COMMENT_DEPTH)
                for row in rows:
                    writer.writerow(row)
                total_comments += len(rows)

            except Exception as e:
                errors += 1
                tqdm.write(f"  [ERROR] Post {pid}: {e}")

            time.sleep(RATE_LIMIT_SLEEP)

    print(f"\n{'='*60}")
    print(f"Collection complete!")
    print(f"  Total comments collected: {total_comments:,}")
    print(f"  Errors: {errors}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
