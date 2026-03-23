"""
collect_forum_data.py
=====================
Scrapes PSLF-related discussions from:
  1. Student Doctor Network (SDN) forums
  2. White Coat Investor (WCI) forum

Produces: forum_pslf_discussions.csv (posts + replies in one file)

Each forum uses different scraping strategies:
  - SDN: vBulletin forum, paginated thread listings + thread pages
  - WCI: vBulletin forum, similar structure

Requires: pip install requests beautifulsoup4 textblob tqdm lxml

Usage:
    python collect_forum_data.py --source sdn
    python collect_forum_data.py --source wci
    python collect_forum_data.py --source all
"""

import argparse
import csv
import hashlib
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from tqdm import tqdm


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_FILE = "forum_pslf_discussions.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

RATE_LIMIT = 2.0  # seconds between requests — be respectful

FIELDS = [
    "source",           # 'sdn' or 'wci'
    "thread_id",
    "thread_title",
    "thread_url",
    "post_id",
    "post_number",      # position within thread
    "author",
    "body",
    "date_posted",
    "is_thread_start",  # True for OP
    "word_count",
    "polarity",
    "subjectivity",
    "scraped_at",
]

# Search queries to find PSLF-related threads
SEARCH_TERMS = [
    "PSLF",
    "Public Service Loan Forgiveness",
    "loan forgiveness residency",
    "student loan forgiveness",
    "SAVE plan",
    "income driven repayment",
    "loan forgiveness specialty",
    "buyback PSLF",
    "qualifying employer",
    "PSLF residency",
    "student debt specialty choice",
    "nonprofit hospital loan",
]

# SDN subforums most likely to contain PSLF discussions (updated 2026-03)
SDN_SUBFORUMS = [
    # Financial Aid
    "https://forums.studentdoctor.net/forums/financial-aid.30/",
    # Medical Students (MD)
    "https://forums.studentdoctor.net/forums/medical-students-md.11/",
    # Residents & Fellows — General Residency Issues
    "https://forums.studentdoctor.net/forums/general-residency-issues.49/",
    # Pre-Medical (MD)
    "https://forums.studentdoctor.net/forums/pre-medical-md.10/",
]

# WCI forum sections
WCI_BASE = "https://forum.whitecoatinvestor.com/"
WCI_SEARCH_URL = "https://forum.whitecoatinvestor.com/search"


# ---------------------------------------------------------------------------
# Sentiment
# ---------------------------------------------------------------------------
def analyze_sentiment(text: str) -> tuple[float, float]:
    try:
        blob = TextBlob(text[:5000])  # cap length for performance
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return 0.0, 0.0


def make_post_id(source: str, thread_id: str, post_number: int) -> str:
    raw = f"{source}:{thread_id}:{post_number}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# SDN Scraper
# ---------------------------------------------------------------------------
class SDNScraper:
    """Scrape Student Doctor Network forums for PSLF discussions."""

    BASE = "https://forums.studentdoctor.net"

    def __init__(self, session: requests.Session):
        self.session = session

    def search_threads(self, query: str, max_pages: int = 3) -> list[dict]:
        """Search SDN forums for threads matching query.

        SDN renders search results via JavaScript, so server-side HTML
        scraping returns an empty page. Strategy:
          1. Try XenForo JSON search endpoint
          2. Fall back to Google site-search
          3. Fall back to scanning subforum thread listings for keyword matches
        """
        threads = []

        # Attempt 1: Google site-search (most reliable)
        try:
            google_url = "https://www.google.com/search"
            params = {"q": f'site:forums.studentdoctor.net "{query}"', "num": 20}
            resp = self.session.get(google_url, params=params, headers=HEADERS, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                for a in soup.select("a[href]"):
                    href = a.get("href", "")
                    if "forums.studentdoctor.net" in href and "/threads/" in href:
                        url_match = re.search(
                            r'(https?://forums\.studentdoctor\.net/threads/[^\s&"]+)', href
                        )
                        if url_match:
                            clean_url = url_match.group(1).split("?")[0].split("#")[0].split("/page-")[0].rstrip("/")
                            tid = re.search(r'\.(\d+)/?$', clean_url)
                            title = a.get_text(strip=True)
                            if tid:
                                threads.append({
                                    "url": clean_url,
                                    "title": title,
                                    "thread_id": tid.group(1),
                                })
            time.sleep(RATE_LIMIT)
        except Exception as e:
            print(f"  [SDN Google search error] {query}: {e}")

        # Attempt 2: Scan subforum pages for threads with matching keywords
        if not threads:
            query_lower = query.lower()
            for forum_url in SDN_SUBFORUMS:
                try:
                    resp = self.session.get(forum_url, headers=HEADERS, timeout=15)
                    if resp.status_code != 200:
                        continue
                    soup = BeautifulSoup(resp.text, "lxml")
                    for a in soup.select("a[href*='/threads/']"):
                        title = a.get_text(strip=True)
                        if query_lower in title.lower():
                            href = a.get("href", "")
                            full_url = urljoin(self.BASE, href).split("/page-")[0].rstrip("/")
                            tid = re.search(r'\.(\d+)/?', href)
                            threads.append({
                                "url": full_url,
                                "title": title,
                                "thread_id": tid.group(1) if tid else href,
                            })
                    time.sleep(RATE_LIMIT)
                except Exception:
                    continue

        # Deduplicate by URL
        seen = set()
        unique = []
        for t in threads:
            if t["url"] not in seen:
                seen.add(t["url"])
                unique.append(t)
        return unique

    def scrape_thread(self, thread_info: dict, max_pages: int = 5) -> list[dict]:
        """Scrape all posts from a single SDN thread."""
        posts = []
        base_url = thread_info["url"]

        for page in range(1, max_pages + 1):
            url = f"{base_url}/page-{page}" if page > 1 else base_url
            try:
                resp = self.session.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "lxml")

                # SDN uses XenForo — message containers
                messages = soup.select("article.message--post, article.message")
                if not messages:
                    messages = soup.select(".message--post, .message")

                if not messages and page > 1:
                    break  # no more pages

                for i, msg in enumerate(messages):
                    # Extract author
                    author_el = msg.select_one(
                        ".message-userDetails a, .username, "
                        "[data-author], .message-name a"
                    )
                    author = author_el.get_text(strip=True) if author_el else "Unknown"
                    if not author and msg.get("data-author"):
                        author = msg.get("data-author")

                    # Extract body
                    body_el = msg.select_one(
                        ".message-body .bbWrapper, .messageContent .bbWrapper, "
                        ".message-content .bbWrapper, .bbWrapper"
                    )
                    body = body_el.get_text(separator=" ", strip=True) if body_el else ""

                    # Extract date
                    time_el = msg.select_one("time, .message-date time, .DateTime")
                    date_str = ""
                    if time_el:
                        date_str = time_el.get("datetime", "") or time_el.get("title", "") or time_el.get_text(strip=True)

                    post_num = (page - 1) * len(messages) + i
                    pol, subj = analyze_sentiment(body)

                    posts.append({
                        "source": "sdn",
                        "thread_id": thread_info["thread_id"],
                        "thread_title": thread_info["title"],
                        "thread_url": thread_info["url"],
                        "post_id": make_post_id("sdn", thread_info["thread_id"], post_num),
                        "post_number": post_num,
                        "author": author,
                        "body": body[:10000],  # cap field length
                        "date_posted": date_str,
                        "is_thread_start": post_num == 0,
                        "word_count": len(body.split()),
                        "polarity": pol,
                        "subjectivity": subj,
                        "scraped_at": datetime.utcnow().isoformat(),
                    })

                time.sleep(RATE_LIMIT)
            except Exception as e:
                print(f"  [SDN thread error] {url}: {e}")
                break

        return posts


# ---------------------------------------------------------------------------
# WCI Scraper
# ---------------------------------------------------------------------------
class WCIScraper:
    """Scrape White Coat Investor forums for PSLF discussions."""

    BASE = "https://forum.whitecoatinvestor.com"

    def __init__(self, session: requests.Session):
        self.session = session

    def search_threads(self, query: str, max_pages: int = 3) -> list[dict]:
        """Search WCI forum for threads.

        WCI blocks automated requests (403). Try direct search first,
        then fall back to Google site-search to discover thread URLs.
        """
        threads = []

        # Attempt 1: direct WCI search
        search_url = f"{self.BASE}/search"
        try:
            resp = self.session.get(
                search_url,
                params={"q": query, "searchJSON": "", "page": 1},
                headers=HEADERS,
                timeout=15,
            )
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                for item in soup.select("a.topic-title, .searchresult a, h3.title a, a[href*='/threads/']"):
                    href = item.get("href", "")
                    if "/threads/" in href or "thread" in href.lower():
                        full_url = urljoin(self.BASE, href)
                        tid = re.search(r'(\d+)', href.split("/")[-1] or href)
                        threads.append({
                            "url": full_url.split("?")[0].split("#")[0],
                            "title": item.get_text(strip=True),
                            "thread_id": tid.group(1) if tid else href,
                        })
            elif resp.status_code == 403:
                print(f"  [WCI] 403 Forbidden on direct search — trying Google site-search fallback")
            else:
                print(f"  [WCI] HTTP {resp.status_code} on search")
        except Exception as e:
            print(f"  [WCI search error] {query}: {e}")

        # Attempt 2: Google site-search fallback
        if not threads:
            try:
                google_url = "https://www.google.com/search"
                params = {"q": f"site:forum.whitecoatinvestor.com {query}", "num": 10}
                resp = self.session.get(google_url, params=params, headers=HEADERS, timeout=15)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    for a in soup.select("a[href]"):
                        href = a.get("href", "")
                        if "forum.whitecoatinvestor.com" in href and "/threads/" in href:
                            # Extract clean URL from Google redirect
                            url_match = re.search(r'(https?://forum\.whitecoatinvestor\.com/[^\s&"]+)', href)
                            if url_match:
                                clean_url = url_match.group(1).split("?")[0].split("#")[0]
                                tid = re.search(r'(\d+)', clean_url.split("/")[-1] or clean_url)
                                title = a.get_text(strip=True)
                                threads.append({
                                    "url": clean_url,
                                    "title": title,
                                    "thread_id": tid.group(1) if tid else clean_url,
                                })
                time.sleep(RATE_LIMIT)
            except Exception as e:
                print(f"  [WCI Google fallback error] {query}: {e}")

        seen = set()
        unique = []
        for t in threads:
            if t["url"] not in seen:
                seen.add(t["url"])
                unique.append(t)
        return unique

    def scrape_thread(self, thread_info: dict, max_pages: int = 5) -> list[dict]:
        """Scrape all posts from a WCI thread."""
        posts = []
        base_url = thread_info["url"]

        for page in range(1, max_pages + 1):
            url = f"{base_url}?p={page}" if page > 1 else base_url
            try:
                resp = self.session.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    break
                soup = BeautifulSoup(resp.text, "lxml")

                # vBulletin post containers
                messages = soup.select(
                    ".b-post, .js-post, article.post, "
                    ".postcontainer, .postcontent, .message"
                )
                if not messages and page > 1:
                    break

                for i, msg in enumerate(messages):
                    author_el = msg.select_one(
                        ".b-post__user-name, .username, .author a, "
                        ".postcreator, [itemprop='name']"
                    )
                    author = author_el.get_text(strip=True) if author_el else "Unknown"

                    body_el = msg.select_one(
                        ".b-post__content, .postcontent, .postbody, "
                        ".message-content, [itemprop='text']"
                    )
                    body = body_el.get_text(separator=" ", strip=True) if body_el else ""

                    time_el = msg.select_one(
                        "time, .b-post__timestamp, .postdate, .date"
                    )
                    date_str = ""
                    if time_el:
                        date_str = (
                            time_el.get("datetime", "")
                            or time_el.get("title", "")
                            or time_el.get_text(strip=True)
                        )

                    post_num = (page - 1) * max(len(messages), 1) + i
                    pol, subj = analyze_sentiment(body)

                    posts.append({
                        "source": "wci",
                        "thread_id": thread_info["thread_id"],
                        "thread_title": thread_info["title"],
                        "thread_url": thread_info["url"],
                        "post_id": make_post_id("wci", thread_info["thread_id"], post_num),
                        "post_number": post_num,
                        "author": author,
                        "body": body[:10000],
                        "date_posted": date_str,
                        "is_thread_start": post_num == 0,
                        "word_count": len(body.split()),
                        "polarity": pol,
                        "subjectivity": subj,
                        "scraped_at": datetime.utcnow().isoformat(),
                    })

                time.sleep(RATE_LIMIT)
            except Exception as e:
                print(f"  [WCI thread error] {url}: {e}")
                break

        return posts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect PSLF forum discussions from SDN and WCI")
    parser.add_argument("--source", choices=["sdn", "wci", "all"], default="all")
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max_threads", type=int, default=100, help="Max threads per source")
    parser.add_argument("--search_pages", type=int, default=3, help="Search result pages per query")
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    all_posts = []
    sources_to_run = ["sdn", "wci"] if args.source == "all" else [args.source]

    for source_name in sources_to_run:
        print(f"\n{'='*60}")
        print(f"Collecting from: {source_name.upper()}")
        print(f"{'='*60}")

        if source_name == "sdn":
            scraper = SDNScraper(session)
        else:
            scraper = WCIScraper(session)

        # Discover threads via search
        all_threads = []
        for term in tqdm(SEARCH_TERMS, desc=f"Searching {source_name.upper()}"):
            threads = scraper.search_threads(term, max_pages=args.search_pages)
            all_threads.extend(threads)
            time.sleep(RATE_LIMIT)

        # Deduplicate threads
        seen = set()
        unique_threads = []
        for t in all_threads:
            if t["url"] not in seen:
                seen.add(t["url"])
                unique_threads.append(t)

        unique_threads = unique_threads[:args.max_threads]
        print(f"  Found {len(unique_threads)} unique threads")

        # Scrape each thread
        for thread in tqdm(unique_threads, desc=f"Scraping {source_name.upper()} threads"):
            posts = scraper.scrape_thread(thread)
            all_posts.extend(posts)

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for post in all_posts:
            writer.writerow(post)

    # Summary
    print(f"\n{'='*60}")
    print(f"Forum collection complete!")
    print(f"  Total posts: {len(all_posts):,}")
    if all_posts:
        from collections import Counter
        src_counts = Counter(p["source"] for p in all_posts)
        for src, count in src_counts.items():
            print(f"    {src.upper()}: {count:,} posts across "
                  f"{len(set(p['thread_id'] for p in all_posts if p['source'] == src))} threads")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
