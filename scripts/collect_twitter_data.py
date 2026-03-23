"""
collect_twitter_data.py
=======================
Collects PSLF-related tweets/posts from X (Twitter).

Supports two collection methods:
  1. X API v2 (Academic/Pro/Basic tier) — preferred, structured
  2. Nitter instances (fallback, no API key needed but less reliable)

Produces: twitter_pslf_discussions.csv (separate from forum data)

Requires:
    pip install tweepy textblob tqdm requests beautifulsoup4

Usage (X API v2):
    python collect_twitter_data.py \
        --bearer_token YOUR_BEARER_TOKEN \
        --method api \
        --start_date 2021-01-01 \
        --end_date 2025-12-31

Usage (Nitter fallback):
    python collect_twitter_data.py --method nitter

Notes:
    - X API Basic tier: 10,000 tweets/month, 100 requests/15 min
    - X API Pro tier: 1M tweets/month, full-archive search
    - Academic Research: best option, apply at developer.x.com
    - Rate limits are handled automatically with backoff
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from textblob import TextBlob
from tqdm import tqdm

try:
    import tweepy
    HAS_TWEEPY = True
except ImportError:
    HAS_TWEEPY = False
    print("[WARN] tweepy not installed. API method unavailable. pip install tweepy")

from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_FILE = "twitter_pslf_discussions.csv"

FIELDS = [
    "tweet_id",
    "author_id",
    "author_username",
    "text",
    "created_at",
    "retweet_count",
    "like_count",
    "reply_count",
    "quote_count",
    "impression_count",
    "lang",
    "conversation_id",
    "is_reply",
    "is_retweet",
    "is_quote",
    "hashtags",
    "query_matched",        # which search query found this tweet
    "polarity",
    "subjectivity",
    "word_count",
    "collection_method",    # 'api' or 'nitter'
    "scraped_at",
]

# Search queries — combine PSLF keywords with profession-specific terms
SEARCH_QUERIES = [
    # Core PSLF queries
    "PSLF -is:retweet",
    '"Public Service Loan Forgiveness" -is:retweet',
    '"loan forgiveness" residency -is:retweet',
    '"loan forgiveness" teacher -is:retweet',

    # Medical-specific
    "PSLF (residency OR fellowship OR attending OR physician) -is:retweet",
    "PSLF (medical school OR med school OR medical student) -is:retweet",
    '"student loans" (residency OR fellowship) (forgiveness OR PSLF) -is:retweet',
    "PSLF specialty (primary care OR family medicine OR pediatrics) -is:retweet",

    # Teacher-specific
    "PSLF (teacher OR teaching OR education OR educator) -is:retweet",
    '"Teacher Loan Forgiveness" -is:retweet',
    "(PSLF OR loan forgiveness) (Title I OR public school) -is:retweet",

    # Policy-specific (2024-2026)
    "PSLF (SAVE plan OR SAVE injunction OR court) -is:retweet",
    'PSLF ("one big beautiful bill" OR OBBBA OR reconciliation) -is:retweet',
    "PSLF (buyback OR qualifying employer) -is:retweet",
    "PSLF (Trump OR executive order) -is:retweet",
    "#PSLF -is:retweet",
    "#MedTwitter (loan OR debt OR PSLF OR forgiveness) -is:retweet",
    "#EdTwitter (loan OR debt OR PSLF OR forgiveness) -is:retweet",
]

# Simplified queries for Nitter (no operators)
NITTER_QUERIES = [
    "PSLF",
    "Public Service Loan Forgiveness",
    "PSLF residency",
    "PSLF teacher",
    "PSLF SAVE plan",
    "student loan forgiveness doctor",
    "student loan forgiveness teacher",
    "PSLF buyback",
]

NITTER_INSTANCES = [
    # Updated 2026-03 — checked via status.d420.de
    "https://xcancel.com",                   # 97% uptime, Nitter fork
    "https://nitter.net",                    # 94% uptime
    "https://nitter.privacyredirect.com",    # 92% uptime
    "https://nitter.catsarch.com",           # 65% uptime
    "https://nitter.space",                  # 96% uptime (outdated version)
]

RATE_LIMIT_SLEEP = 2.0


# ---------------------------------------------------------------------------
# Sentiment
# ---------------------------------------------------------------------------
def analyze_sentiment(text: str) -> tuple[float, float]:
    try:
        # Clean tweet text: remove URLs, mentions, hashtags for cleaner sentiment
        import re
        clean = re.sub(r'https?://\S+', '', text)
        clean = re.sub(r'@\w+', '', clean)
        blob = TextBlob(clean.strip())
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return 0.0, 0.0


# ---------------------------------------------------------------------------
# X API v2 Collector
# ---------------------------------------------------------------------------
class XAPICollector:
    """Collect tweets via X API v2 (requires bearer token)."""

    def __init__(self, bearer_token: str):
        if not HAS_TWEEPY:
            raise RuntimeError("tweepy required for API method. pip install tweepy")
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            wait_on_rate_limit=True,
        )

    def search(
        self,
        query: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        max_results: int = 500,
    ) -> list[dict]:
        """Search tweets using X API v2 full-archive or recent search."""
        tweets_data = []

        tweet_fields = [
            "created_at", "public_metrics", "lang",
            "conversation_id", "referenced_tweets",
        ]
        user_fields = ["username", "name"]
        expansions = ["author_id"]

        try:
            # Try full-archive search first (Academic/Pro tier)
            paginator = tweepy.Paginator(
                self.client.search_all_tweets,
                query=query,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                expansions=expansions,
                max_results=min(100, max_results),  # API max per page
            )
        except Exception:
            # Fall back to recent search (Basic tier, last 7 days only)
            print(f"    [INFO] Full-archive unavailable, using recent search for: {query[:50]}")
            paginator = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=tweet_fields,
                user_fields=user_fields,
                expansions=expansions,
                max_results=min(100, max_results),
            )

        collected = 0
        for response in paginator:
            if not response.data:
                break

            # Build user lookup
            users = {}
            if response.includes and "users" in response.includes:
                for u in response.includes["users"]:
                    users[u.id] = u.username

            for tweet in response.data:
                metrics = tweet.public_metrics or {}

                # Determine tweet type
                is_reply = False
                is_retweet = False
                is_quote = False
                if tweet.referenced_tweets:
                    for ref in tweet.referenced_tweets:
                        if ref.type == "replied_to":
                            is_reply = True
                        elif ref.type == "retweeted":
                            is_retweet = True
                        elif ref.type == "quoted":
                            is_quote = True

                pol, subj = analyze_sentiment(tweet.text)

                tweets_data.append({
                    "tweet_id": str(tweet.id),
                    "author_id": str(tweet.author_id),
                    "author_username": users.get(tweet.author_id, ""),
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
                    "retweet_count": metrics.get("retweet_count", 0),
                    "like_count": metrics.get("like_count", 0),
                    "reply_count": metrics.get("reply_count", 0),
                    "quote_count": metrics.get("quote_count", 0),
                    "impression_count": metrics.get("impression_count", 0),
                    "lang": tweet.lang or "",
                    "conversation_id": str(tweet.conversation_id) if tweet.conversation_id else "",
                    "is_reply": is_reply,
                    "is_retweet": is_retweet,
                    "is_quote": is_quote,
                    "hashtags": "",  # extracted from entities if available
                    "query_matched": query[:100],
                    "polarity": pol,
                    "subjectivity": subj,
                    "word_count": len(tweet.text.split()),
                    "collection_method": "api",
                    "scraped_at": datetime.utcnow().isoformat(),
                })

                collected += 1
                if collected >= max_results:
                    return tweets_data

        return tweets_data


# ---------------------------------------------------------------------------
# Nitter Fallback Collector
# ---------------------------------------------------------------------------
class NitterCollector:
    """Scrape tweets via Nitter instances (no API key needed)."""

    def __init__(self):
        self.session = requests.Session()
        self.working_instance = None

    def _find_working_instance(self) -> Optional[str]:
        """Find a responsive Nitter instance."""
        for instance in NITTER_INSTANCES:
            try:
                resp = self.session.get(instance, timeout=10)
                if resp.status_code == 200:
                    self.working_instance = instance
                    return instance
            except Exception:
                continue
        return None

    def search(self, query: str, max_pages: int = 5) -> list[dict]:
        """Search tweets via Nitter/xcancel instances.

        Updated 2026-03 for xcancel.com HTML structure:
          .timeline-item > .tweet-body
            .fullname-and-username > .username
            .tweet-content.media-body  (tweet text)
            .tweet-date a              (timestamp with title attr)
            .tweet-stats > .tweet-stat (4 stats: comments, RTs, quotes, likes)
          .show-more a                 (pagination cursor link)
        """
        if not self.working_instance:
            if not self._find_working_instance():
                print("  [ERROR] No working Nitter instance found")
                return []

        import hashlib
        tweets_data = []
        next_url = None

        for page in range(1, max_pages + 1):
            try:
                if next_url:
                    resp = self.session.get(next_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    }, timeout=15)
                else:
                    resp = self.session.get(
                        f"{self.working_instance}/search",
                        params={"f": "tweets", "q": query},
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        },
                        timeout=15,
                    )
                if resp.status_code != 200:
                    # Try next instance if first page fails
                    if page == 1:
                        self.working_instance = None
                        if self._find_working_instance():
                            continue
                    break
                soup = BeautifulSoup(resp.text, "lxml")

                # xcancel/Nitter tweet containers
                tweet_items = soup.select(".timeline-item")
                if not tweet_items:
                    break

                for item in tweet_items:
                    # Username — .username inside .fullname-and-username
                    username_el = item.select_one(".username")
                    username = username_el.get_text(strip=True).lstrip("@") if username_el else ""

                    # Tweet text — .tweet-content.media-body
                    text_el = item.select_one(".tweet-content.media-body, .tweet-content")
                    text = text_el.get_text(separator=" ", strip=True) if text_el else ""

                    # Date — .tweet-date a (title attribute has readable date)
                    date_el = item.select_one(".tweet-date a")
                    date_str = ""
                    if date_el:
                        date_str = date_el.get("title", "") or date_el.get_text(strip=True)

                    # Tweet link — extract tweet ID from a.tweet-link href
                    link_el = item.select_one("a.tweet-link")
                    real_tweet_id = ""
                    if link_el:
                        href = link_el.get("href", "")
                        id_match = re.search(r'/status/(\d+)', href)
                        if id_match:
                            real_tweet_id = id_match.group(1)

                    # Stats — .tweet-stat elements (order: comments, RTs, quotes, likes)
                    stat_els = item.select(".tweet-stat")
                    stat_values = []
                    for s in stat_els:
                        val = self._parse_count(s.get_text(strip=True))
                        stat_values.append(val)
                    # Pad to 4 elements
                    while len(stat_values) < 4:
                        stat_values.append(0)

                    if text:
                        pol, subj = analyze_sentiment(text)
                        tid = real_tweet_id or hashlib.md5(
                            f"{username}:{text[:50]}:{date_str}".encode()
                        ).hexdigest()[:16]

                        tweets_data.append({
                            "tweet_id": tid,
                            "author_id": "",
                            "author_username": username,
                            "text": text[:1000],
                            "created_at": date_str,
                            "retweet_count": stat_values[1],
                            "like_count": stat_values[3],
                            "reply_count": stat_values[0],
                            "quote_count": stat_values[2],
                            "impression_count": 0,
                            "lang": "",
                            "conversation_id": "",
                            "is_reply": False,
                            "is_retweet": False,
                            "is_quote": False,
                            "hashtags": "",
                            "query_matched": query,
                            "polarity": pol,
                            "subjectivity": subj,
                            "word_count": len(text.split()),
                            "collection_method": "nitter",
                            "scraped_at": datetime.utcnow().isoformat(),
                        })

                # Pagination — .show-more a with cursor param
                next_link = soup.select_one(".show-more a")
                if next_link:
                    from urllib.parse import urljoin
                    next_url = urljoin(self.working_instance, next_link.get("href", ""))
                else:
                    break

                time.sleep(RATE_LIMIT_SLEEP)
            except Exception as e:
                print(f"  [Nitter error] {query}: {e}")
                break

        return tweets_data

    @staticmethod
    def _parse_count(text: str) -> int:
        import re
        nums = re.findall(r'[\d,]+', text)
        if nums:
            return int(nums[0].replace(",", ""))
        return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect PSLF tweets from X/Twitter")
    parser.add_argument("--method", choices=["api", "nitter"], default="api")
    parser.add_argument("--bearer_token", default=os.environ.get("X_BEARER_TOKEN", ""))
    parser.add_argument("--start_date", default="2021-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", default="2026-03-23", help="End date (YYYY-MM-DD)")
    parser.add_argument("--max_per_query", type=int, default=500, help="Max tweets per query")
    parser.add_argument("--output", default=OUTPUT_FILE)
    args = parser.parse_args()

    print(f"PSLF Twitter/X Collection")
    print(f"  Method: {args.method}")
    print(f"  Date range: {args.start_date} to {args.end_date}")
    print(f"  Output: {args.output}")

    all_tweets = []
    seen_ids = set()

    if args.method == "api":
        if not args.bearer_token:
            print("[ERROR] --bearer_token required for API method")
            print("  Set via argument or X_BEARER_TOKEN environment variable")
            print("  Get one at https://developer.x.com/en/portal/dashboard")
            sys.exit(1)

        collector = XAPICollector(args.bearer_token)
        queries = SEARCH_QUERIES

        # Format dates for API
        start_time = f"{args.start_date}T00:00:00Z"
        end_time = f"{args.end_date}T23:59:59Z"

        for query in tqdm(queries, desc="Searching X API"):
            try:
                tweets = collector.search(
                    query=query,
                    start_time=start_time,
                    end_time=end_time,
                    max_results=args.max_per_query,
                )
                for t in tweets:
                    if t["tweet_id"] not in seen_ids:
                        seen_ids.add(t["tweet_id"])
                        all_tweets.append(t)
                tqdm.write(f"  {query[:60]}: {len(tweets)} tweets")
            except Exception as e:
                tqdm.write(f"  [ERROR] {query[:40]}: {e}")
            time.sleep(1)

    else:  # nitter
        from urllib.parse import urljoin
        collector = NitterCollector()
        queries = NITTER_QUERIES

        for query in tqdm(queries, desc="Searching Nitter"):
            tweets = collector.search(query, max_pages=5)
            for t in tweets:
                if t["tweet_id"] not in seen_ids:
                    seen_ids.add(t["tweet_id"])
                    all_tweets.append(t)
            tqdm.write(f"  {query}: {len(tweets)} tweets")

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for tweet in all_tweets:
            writer.writerow(tweet)

    # Summary
    print(f"\n{'='*60}")
    print(f"X/Twitter collection complete!")
    print(f"  Total unique tweets: {len(all_tweets):,}")
    if all_tweets:
        # Date range of collected tweets
        dates = [t["created_at"] for t in all_tweets if t["created_at"]]
        if dates:
            print(f"  Date range: {min(dates)[:10]} to {max(dates)[:10]}")
        # Engagement summary
        total_likes = sum(t.get("like_count", 0) for t in all_tweets)
        total_rts = sum(t.get("retweet_count", 0) for t in all_tweets)
        print(f"  Total likes: {total_likes:,}")
        print(f"  Total retweets: {total_rts:,}")
        # Sentiment
        pols = [t["polarity"] for t in all_tweets]
        print(f"  Mean polarity: {sum(pols)/len(pols):.4f}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
