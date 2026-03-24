"""
collect_bogleheads.py
=====================
Scrapes PSLF-related discussions from bogleheads.org forums (phpBB).

Bogleheads uses aggressive Cloudflare protection (403 to requests).
Uses Playwright headless Chromium, then extracts content via BS4.

Produces: bogleheads_pslf_discussions.csv

Requires: pip install playwright requests beautifulsoup4 textblob tqdm lxml
          python -m playwright install chromium

Usage:
    python collect_bogleheads.py
"""

import argparse
import csv
import hashlib
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from textblob import TextBlob
from tqdm import tqdm

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("[WARN] playwright not installed")

try:
    from pslf_search_terms import SEARCH_TERMS
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import SEARCH_TERMS


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_FILE = "bogleheads_pslf_discussions.csv"
BASE_URL = "https://www.bogleheads.org/forum"

RATE_LIMIT = 2.5  # be extra polite to Bogleheads

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
# Bogleheads Search + Scrape via Playwright
# ---------------------------------------------------------------------------
def collect_bogleheads(
    search_terms: list[str],
    max_threads: int = 100,
    max_thread_pages: int = 10,
) -> list[dict]:
    """Use Playwright for everything — Cloudflare blocks all requests."""
    if not HAS_PLAYWRIGHT:
        print("  [ERROR] Playwright required for Bogleheads")
        return []

    all_posts = []
    seen_thread_urls = set()
    threads = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # Skip direct Cloudflare challenge — go via Google instead
        print("  Starting Google site-search (bypasses Cloudflare)...")

        # Phase 1: Discover threads via DuckDuckGo HTML site-search
        # (Google blocks headless Playwright with CAPTCHA; Bogleheads Cloudflare blocks direct search)
        print(f"\n  Phase 1: Searching via DuckDuckGo ({len(search_terms)} queries)...")

        import requests as req_lib
        from urllib.parse import unquote as url_unquote

        ddg_session = req_lib.Session()
        ddg_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        for term in tqdm(search_terms, desc="Searching Bogleheads"):
            try:
                resp = ddg_session.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": f'site:bogleheads.org/forum "{term}"'},
                    headers=ddg_headers,
                    timeout=15,
                )
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                for link in soup.select("a.result__a, a[href*='bogleheads']"):
                    href = link.get("href", "")
                    # DDG wraps URLs in redirect: ...uddg=ENCODED_URL...
                    url_match = re.search(r'uddg=([^&]+)', href)
                    if url_match:
                        real_url = url_unquote(url_match.group(1))
                    else:
                        real_url = href

                    if "viewtopic.php" not in real_url:
                        continue
                    tid_match = re.search(r't=(\d+)', real_url)
                    if not tid_match:
                        continue

                    tid = tid_match.group(1)
                    clean_url = f"{BASE_URL}/viewtopic.php?t={tid}"
                    if clean_url not in seen_thread_urls:
                        seen_thread_urls.add(clean_url)
                        title = link.get_text(strip=True)
                        threads.append({
                            "url": clean_url,
                            "title": title,
                            "thread_id": tid,
                        })

            except Exception as e:
                tqdm.write(f"  [DDG search error] '{term}': {e}")

            time.sleep(RATE_LIMIT)

        threads = threads[:max_threads]
        print(f"  Found {len(threads)} unique threads")

        if not threads:
            browser.close()
            return []

        # Phase 2: Scrape thread contents via Playwright
        print(f"\n  Phase 2: Scraping threads...")
        for thread_info in tqdm(threads, desc="Scraping Bogleheads"):
            post_counter = 0

            for page_num in range(max_thread_pages):
                url = thread_info["url"]
                if page_num > 0:
                    url += f"&start={page_num * 20}"  # phpBB default 20 posts/page

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=45000)
                    page.wait_for_timeout(3000)

                    html = page.content()
                    soup = BeautifulSoup(html, "lxml")

                    # phpBB post containers
                    posts_els = soup.select(".post, .postbody, div[id^='post_content']")
                    if not posts_els:
                        posts_els = soup.select("[class*='post']")
                        posts_els = [el for el in posts_els if el.select_one(".content, .postbody")]

                    if not posts_els and page_num > 0:
                        break

                    for post_el in posts_els:
                        # Author
                        author_el = post_el.select_one(
                            ".author a, .username, .postprofile a, dt a"
                        )
                        author = author_el.get_text(strip=True) if author_el else "Unknown"

                        # Body — strip quotes
                        body_el = post_el.select_one(".content, .postbody")
                        if body_el:
                            for bq in body_el.find_all("blockquote"):
                                bq.decompose()
                            body = body_el.get_text(separator=" ", strip=True)
                        else:
                            body = ""

                        # Date
                        date_el = post_el.select_one("time, .author, p.author")
                        date_str = ""
                        if date_el:
                            date_str = date_el.get("datetime", "") or date_el.get_text(strip=True)

                        if body.strip():
                            pol, subj = analyze_sentiment(body)
                            all_posts.append({
                                "source": "bogleheads",
                                "thread_id": thread_info["thread_id"],
                                "thread_title": thread_info["title"],
                                "thread_url": thread_info["url"],
                                "post_id": make_post_id("bogleheads", thread_info["thread_id"], post_counter),
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

                    # Check for next page
                    next_link = soup.select_one(".arrow.next a, a[rel='next']")
                    if not next_link:
                        break

                except Exception as e:
                    tqdm.write(f"  [Thread error] {url}: {e}")
                    break

                page.wait_for_timeout(int(RATE_LIMIT * 1000))

        browser.close()

    return all_posts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect PSLF discussions from Bogleheads")
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max_threads", type=int, default=100)
    parser.add_argument("--thread_pages", type=int, default=10)
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("Bogleheads PSLF Discussion Collector (Playwright)")
    print(f"{'='*60}")

    all_posts = collect_bogleheads(
        SEARCH_TERMS,
        max_threads=args.max_threads,
        max_thread_pages=args.thread_pages,
    )

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for post in all_posts:
            writer.writerow(post)

    n_threads = len(set(p["thread_id"] for p in all_posts))
    print(f"\n{'='*60}")
    print(f"Bogleheads collection complete!")
    print(f"  Threads: {n_threads}")
    print(f"  Posts: {len(all_posts):,}")
    if all_posts:
        pols = [p["polarity"] for p in all_posts if p["polarity"] == p["polarity"]]
        if pols:
            print(f"  Mean polarity: {sum(pols)/len(pols):.4f}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
