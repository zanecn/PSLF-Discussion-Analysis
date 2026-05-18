"""
collect_youtube_pslf.py
========================
Collects PSLF-related YouTube comments via the YouTube Data API v3.

Strategy:
  1. Search videos for PSLF-related keywords (10K-unit daily quota allows ~10 searches)
  2. For each video, fetch metadata + commentThreads + replies
  3. Apply strict PSLF anchored filter to comments at load
  4. Tag each comment with a "youtube" cohort for cross-platform analysis

Quota budget (10K/day free):
  - search.list = 100 units/call (max 50 results/call)
  - 10 keyword searches × 10 pages × 100 = 10,000 units
  - That's 1 day's quota for video discovery alone
  - commentThreads.list = 1 unit/call → comments are cheap once we have video IDs
  - Spread collection over 2-3 days for full corpus

Alternative: youtube-comment-downloader (no API key) for bulk comment-only mode.

Setup:
  1. Get YouTube Data API key:
     https://console.cloud.google.com → enable "YouTube Data API v3" → Credentials → API Key
  2. Set: $env:YOUTUBE_API_KEY = "your-key"
  3. pip install google-api-python-client

Outputs:
  - youtube_pslf_videos.csv     (video metadata)
  - youtube_pslf_comments.csv   (comments + replies, PSLF-strict-filtered)
"""
from __future__ import annotations

import argparse
import csv
import io
import os
import sys
import time
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_API = True
except ImportError:
    HAS_API = False
    print("[WARN] google-api-python-client not installed.")
    print("       pip install google-api-python-client")

import pandas as pd
from textblob import TextBlob

try:
    from pslf_search_terms import filter_pslf_relevant
    HAS_PSLF_FILTER = True
except ImportError:
    HAS_PSLF_FILTER = False

# Search terms (mirrors the project's PSLF_SEARCH_TERMS for consistency)
SEARCH_KEYWORDS = [
    "PSLF",
    "Public Service Loan Forgiveness",
    "PSLF tutorial",
    "PSLF qualifying employment",
    "PSLF MOHELA",
    "student loan forgiveness 2025",
    "PSLF Trump",
    "PSLF SAVE plan",
    "PSLF Limited Waiver",
    "PSLF residency",
]

VIDEO_FIELDS = [
    "video_id", "title", "channel_id", "channel_title", "published_at",
    "view_count", "like_count", "comment_count", "duration",
    "description_excerpt", "search_term",
]
COMMENT_FIELDS = [
    "comment_id", "video_id", "video_title", "parent_id", "author",
    "body", "like_count", "published_at", "depth", "is_top_level",
    "polarity", "subjectivity", "word_count",
]


def search_videos(youtube, query: str, max_results: int = 100) -> list[dict]:
    """Search YouTube for videos matching query. Returns list of video dicts."""
    videos = []
    next_page = None
    while len(videos) < max_results:
        page_size = min(50, max_results - len(videos))
        try:
            req = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=page_size,
                order="relevance",
                pageToken=next_page,
            )
            resp = req.execute()
        except HttpError as e:
            print(f"  [ERROR] search.list: {e}")
            break
        for item in resp.get("items", []):
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel_id": item["snippet"]["channelId"],
                "channel_title": item["snippet"]["channelTitle"],
                "published_at": item["snippet"]["publishedAt"],
                "search_term": query,
            })
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return videos


def fetch_video_metadata(youtube, video_ids: list[str]) -> dict:
    """Get view_count, like_count, comment_count, duration for batch of videos."""
    out = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        try:
            req = youtube.videos().list(
                part="statistics,contentDetails",
                id=",".join(batch),
            )
            resp = req.execute()
        except HttpError as e:
            print(f"  [WARN] videos.list: {e}")
            continue
        for item in resp.get("items", []):
            stats = item.get("statistics", {})
            out[item["id"]] = {
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration": item.get("contentDetails", {}).get("duration", ""),
            }
    return out


def fetch_comments(youtube, video_id: str, video_title: str,
                    max_comments: int = 1000) -> list[dict]:
    """Fetch top-level comments + replies for a video."""
    comments = []
    next_page = None
    while len(comments) < max_comments:
        try:
            req = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page,
                textFormat="plainText",
                order="time",
            )
            resp = req.execute()
        except HttpError as e:
            err_str = str(e)
            if "commentsDisabled" in err_str or "videoNotFound" in err_str:
                return []
            print(f"  [WARN] commentThreads {video_id}: {err_str[:100]}")
            return comments
        for item in resp.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(_parse_comment(top, video_id, video_title,
                                            comment_id=item["snippet"]["topLevelComment"]["id"],
                                            parent_id=video_id, depth=0))
            # Replies
            for reply_item in item.get("replies", {}).get("comments", []):
                rs = reply_item["snippet"]
                comments.append(_parse_comment(rs, video_id, video_title,
                                                comment_id=reply_item["id"],
                                                parent_id=item["snippet"]["topLevelComment"]["id"],
                                                depth=1))
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    return comments


def _parse_comment(s: dict, video_id: str, video_title: str,
                    comment_id: str, parent_id: str, depth: int) -> dict:
    body = s.get("textDisplay", "")
    pol = sub = float("nan")
    try:
        b = TextBlob(body[:5000])
        pol, sub = round(b.sentiment.polarity, 6), round(b.sentiment.subjectivity, 6)
    except Exception:
        pass
    return {
        "comment_id": comment_id,
        "video_id": video_id,
        "video_title": video_title,
        "parent_id": parent_id,
        "author": s.get("authorDisplayName", "[unknown]"),
        "body": body,
        "like_count": int(s.get("likeCount", 0)),
        "published_at": s.get("publishedAt", ""),
        "depth": depth,
        "is_top_level": depth == 0,
        "polarity": pol,
        "subjectivity": sub,
        "word_count": len(body.split()),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-videos-per-query", type=int, default=50)
    parser.add_argument("--max-comments-per-video", type=int, default=500)
    parser.add_argument("--video-output", default="youtube_pslf_videos.csv")
    parser.add_argument("--comment-output", default="youtube_pslf_comments.csv")
    parser.add_argument("--api-key", default=None,
                        help="Override YOUTUBE_API_KEY env var")
    parser.add_argument("--keywords", nargs="*", default=None,
                        help="Override default search keywords")
    args = parser.parse_args()

    if not HAS_API:
        print("[ABORT] pip install google-api-python-client")
        sys.exit(1)
    api_key = args.api_key or os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        print("[ABORT] Set YOUTUBE_API_KEY env var")
        print("        Get key at https://console.cloud.google.com (enable YouTube Data API v3)")
        sys.exit(1)

    keywords = args.keywords or SEARCH_KEYWORDS
    youtube = build("youtube", "v3", developerKey=api_key)

    print("=" * 80)
    print("YouTube PSLF Data Collection")
    print("=" * 80)
    print(f"  Keywords: {len(keywords)}")
    print(f"  Max videos per keyword: {args.max_videos_per_query}")
    print(f"  Max comments per video: {args.max_comments_per_video}")

    # Step 1: discover videos
    print("\n[Step 1] Searching videos...")
    all_videos = []
    seen_ids = set()
    for kw in keywords:
        print(f"  '{kw}'...")
        videos = search_videos(youtube, kw, max_results=args.max_videos_per_query)
        new_count = 0
        for v in videos:
            if v["video_id"] not in seen_ids:
                seen_ids.add(v["video_id"])
                all_videos.append(v)
                new_count += 1
        print(f"    {len(videos)} returned, {new_count} new")
    print(f"\n  Unique videos: {len(all_videos):,}")

    # Step 2: fetch metadata
    print("\n[Step 2] Fetching video metadata...")
    meta = fetch_video_metadata(youtube, [v["video_id"] for v in all_videos])
    for v in all_videos:
        m = meta.get(v["video_id"], {})
        v.update(m)
    pd.DataFrame(all_videos)[VIDEO_FIELDS[:11]].to_csv(args.video_output, index=False)
    print(f"  Saved: {args.video_output}")

    # Step 3: fetch comments per video
    print(f"\n[Step 3] Fetching comments (rate-limited; this will take time)...")
    all_comments = []
    for i, v in enumerate(all_videos):
        n_comments = v.get("comment_count", 0)
        if n_comments == 0:
            continue
        print(f"  [{i+1}/{len(all_videos)}] {v['video_id']} '{v['title'][:60]}' ({n_comments} comments expected)")
        cmts = fetch_comments(youtube, v["video_id"], v["title"],
                                max_comments=args.max_comments_per_video)
        all_comments.extend(cmts)
        time.sleep(0.1)  # polite

    print(f"\n  Total raw comments collected: {len(all_comments):,}")

    # Step 4: PSLF strict filter
    if HAS_PSLF_FILTER and all_comments:
        df = pd.DataFrame(all_comments)
        mask = filter_pslf_relevant(df["body"].fillna(""))
        df_filtered = df[mask]
        print(f"  After PSLF strict filter: {len(df_filtered):,} ({100*len(df_filtered)/len(all_comments):.1f}%)")
        df_filtered.to_csv(args.comment_output, index=False)
    else:
        pd.DataFrame(all_comments).to_csv(args.comment_output, index=False)
    print(f"  Saved: {args.comment_output}")

    # Step 5: summary
    print(f"\n{'=' * 60}")
    print(f"Collection complete:")
    print(f"  Unique videos: {len(all_videos):,}")
    print(f"  Total comments: {len(all_comments):,}")
    if HAS_PSLF_FILTER:
        print(f"  PSLF-strict-filtered: {len(df_filtered):,}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
