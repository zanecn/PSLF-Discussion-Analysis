"""
collect_allnurses.py
====================
Scrapes PSLF-related discussions from allnurses.com (XenForo/Invision).

Uses Playwright headless Chromium to bypass Cloudflare/anti-bot.
Thread content extracted with requests+BS4 after cookies are harvested
from the Playwright session.

Produces: allnurses_pslf_discussions.csv

Requires: pip install playwright requests beautifulsoup4 textblob tqdm lxml
          python -m playwright install chromium

Usage:
    python collect_allnurses.py
"""

import argparse
import csv
import hashlib
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from tqdm import tqdm

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[WARN] playwright not installed")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_FILE = "allnurses_pslf_discussions.csv"
BASE_URL = "https://allnurses.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
}

RATE_LIMIT = 2.0

FIELDS = [
    "source",
    "thread_id",
    "thread_title",
    "thread_url",
    "post_id",
    "post_number",
    "author",
    "body",
    "date_posted",
    "is_thread_start",
    "word_count",
    "polarity",
    "subjectivity",
    "scraped_at",
]

try:
    from pslf_search_terms import SEARCH_TERMS
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import SEARCH_TERMS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def analyze_sentiment(text: str) -> tuple:
    if not text or not text.strip():
        return float("nan"), float("nan")
    try:
        blob = TextBlob(text[:5000])
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return float("nan"), float("nan")


def make_post_id(source: str, thread_id: str, post_number: int) -> str:
    raw = f"{source}:{thread_id}:{post_number}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Allnurses Search via Playwright
# ---------------------------------------------------------------------------
def search_allnurses(search_terms: list[str], max_pages: int = 3) -> list[dict]:
    """Search allnurses.com using Playwright to bypass Cloudflare."""
    if not HAS_PLAYWRIGHT:
        print("  [ERROR] Playwright required")
        return [], []

    threads = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # First visit to pass Cloudflare challenge
        print("  Passing Cloudflare challenge...")
        page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)

        # Use DuckDuckGo HTML (Google blocks headless with CAPTCHA)
        from urllib.parse import unquote as url_unquote

        ddg_session = requests.Session()
        ddg_headers = {"User-Agent": HEADERS["User-Agent"]}

        for term in tqdm(search_terms, desc="Searching allnurses"):
            try:
                resp = ddg_session.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": f'site:allnurses.com "{term}"'},
                    headers=ddg_headers,
                    timeout=15,
                )
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                for link in soup.select("a.result__a, a[href*='allnurses']"):
                    href = link.get("href", "")
                    url_match = re.search(r'uddg=([^&]+)', href)
                    real_url = url_unquote(url_match.group(1)) if url_match else href

                    if "allnurses.com" not in real_url:
                        continue
                    clean_url = real_url.split("?")[0].split("#")[0]
                    if clean_url in seen_urls:
                        continue

                    tid_match = re.search(r'-t(\d+)', clean_url)
                    if not tid_match:
                        tid_match = re.search(r'\.(\d+)/?$', clean_url)
                    if tid_match:
                        title = link.get_text(strip=True)
                        seen_urls.add(clean_url)
                        threads.append({
                            "url": clean_url,
                            "title": title,
                            "thread_id": tid_match.group(1),
                        })

            except Exception as e:
                tqdm.write(f"  [DDG search error] '{term}': {e}")

            time.sleep(RATE_LIMIT)

        # Also try on-site search if we have few results
        if len(threads) < 20:
            for term in search_terms[:5]:
                try:
                    page.goto(f"{BASE_URL}/search/?q={term}&type=post", wait_until="networkidle", timeout=20000)
                    page.wait_for_timeout(3000)

                    links = page.query_selector_all("a[href]")
                    for link in links:
                        href = link.get_attribute("href") or ""
                        if ("-t" in href or "/threads/" in href) and "allnurses.com" in (href if "http" in href else BASE_URL + href):
                            full_url = urljoin(BASE_URL, href).split("?")[0].split("#")[0]
                            if full_url in seen_urls:
                                continue
                            tid_match = re.search(r'-t(\d+)', full_url) or re.search(r'\.(\d+)/?$', full_url)
                            if tid_match:
                                title = link.inner_text().strip()
                                seen_urls.add(full_url)
                                threads.append({
                                    "url": full_url,
                                    "title": title,
                                    "thread_id": tid_match.group(1),
                                })
                except Exception as e:
                    tqdm.write(f"  [On-site search error] '{term}': {e}")
                page.wait_for_timeout(int(RATE_LIMIT * 1000))

        # Harvest cookies for requests session
        cookies = context.cookies()
        browser.close()

    return threads, cookies


def scrape_allnurses_thread(
    session: requests.Session,
    thread_info: dict,
    max_pages: int = 10,
) -> list[dict]:
    """Scrape posts from an allnurses thread using requests + cookies."""
    posts = []
    base_url = thread_info["url"]
    post_counter = 0

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}page-{page_num}/" if page_num > 1 else base_url

        try:
            resp = session.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                break
            soup = BeautifulSoup(resp.text, "lxml")

            # XenForo / Invision post containers
            messages = soup.select(
                "article.message--post, article.message, "
                ".cPost, .ipsComment, .message"
            )
            if not messages and page_num > 1:
                break

            for msg in messages:
                # Author
                author_el = msg.select_one(
                    ".message-userDetails a, .username, .ipsComment_author a, "
                    ".cAuthorPane_author a, [data-author]"
                )
                author = author_el.get_text(strip=True) if author_el else "Unknown"

                # Body — strip quotes
                body_el = msg.select_one(
                    ".message-body .bbWrapper, .cPost_contentWrap, "
                    ".ipsComment_content, .message-content, [data-role='commentContent']"
                )
                if body_el:
                    for bq in body_el.find_all("blockquote"):
                        bq.decompose()
                    body = body_el.get_text(separator=" ", strip=True)
                else:
                    body = ""

                # Date
                time_el = msg.select_one("time, .ipsComment_meta time, .message-date time")
                date_str = ""
                if time_el:
                    date_str = time_el.get("datetime", "") or time_el.get("title", "") or time_el.get_text(strip=True)

                pol, subj = analyze_sentiment(body)

                posts.append({
                    "source": "allnurses",
                    "thread_id": thread_info["thread_id"],
                    "thread_title": thread_info["title"],
                    "thread_url": thread_info["url"],
                    "post_id": make_post_id("allnurses", thread_info["thread_id"], post_counter),
                    "post_number": post_counter,
                    "author": author,
                    "body": body[:10000],
                    "date_posted": date_str,
                    "is_thread_start": post_counter == 0,
                    "word_count": len(body.split()),
                    "polarity": pol,
                    "subjectivity": subj,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                })
                post_counter += 1

            time.sleep(RATE_LIMIT)
        except Exception as e:
            print(f"  [Thread error] {url}: {e}")
            break

    return posts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect PSLF discussions from allnurses.com")
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max_threads", type=int, default=100)
    parser.add_argument("--thread_pages", type=int, default=10)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("allnurses.com PSLF Discussion Collector")
    print(f"{'='*60}")

    # Phase 1: Discover threads
    print(f"\nPhase 1: Searching ({len(SEARCH_TERMS)} queries)...")
    threads, cookies = search_allnurses(SEARCH_TERMS)
    threads = threads[:args.max_threads]
    print(f"  Found {len(threads)} unique threads")

    if not threads:
        print("  [WARN] No threads found")
        return

    # Phase 2: Scrape with harvested cookies
    print(f"\nPhase 2: Scraping threads...")
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for c in cookies:
            session.cookies.set(c["name"], c["value"], domain=c.get("domain", ""))

        all_posts = []
        for thread in tqdm(threads, desc="Scraping allnurses"):
            posts = scrape_allnurses_thread(session, thread, max_pages=args.thread_pages)
            all_posts.extend(posts)

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for post in all_posts:
            writer.writerow(post)

    n_threads = len(set(p["thread_id"] for p in all_posts))
    print(f"\n{'='*60}")
    print(f"allnurses collection complete!")
    print(f"  Threads: {n_threads}")
    print(f"  Posts: {len(all_posts):,}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
