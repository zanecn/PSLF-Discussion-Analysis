"""
collect_forum_data.py
=====================
Scrapes PSLF-related discussions from Student Doctor Network (SDN) forums.

Uses Playwright (headless Chromium) for SDN search since XenForo renders
search results via JavaScript. Thread pages are scraped with requests+BS4
(server-rendered HTML works fine for individual threads).

Produces: forum_pslf_discussions.csv

Requires: pip install playwright requests beautifulsoup4 textblob tqdm lxml
          python -m playwright install chromium

Usage:
    python collect_forum_data.py
    python collect_forum_data.py --max_threads 200 --search_pages 5
"""

import argparse
import csv
import hashlib
import os
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
    print("[WARN] playwright not installed. pip install playwright && python -m playwright install chromium")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_FILE = "forum_pslf_discussions.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
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
    # Fallback if module not on path
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import SEARCH_TERMS

SDN_BASE = "https://forums.studentdoctor.net"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def analyze_sentiment(text: str) -> tuple[float | None, float | None]:
    """Return (polarity, subjectivity) via TextBlob.

    Returns (NaN, NaN) on error so downstream analysis can distinguish
    failures from genuinely neutral text (M1 fix).
    """
    if not text or not text.strip():
        return float("nan"), float("nan")
    try:
        blob = TextBlob(text[:5000])
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return float("nan"), float("nan")


def make_post_id(source: str, thread_id: str, post_number: int) -> str:
    raw = f"{source}:{thread_id}:{post_number}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]  # m2 fix: SHA-256, 16 chars


# ---------------------------------------------------------------------------
# SDN Search via Playwright (headless browser)
# ---------------------------------------------------------------------------
def sdn_search_playwright(search_terms: list[str], max_pages: int = 5) -> list[dict]:
    """Use Playwright to search SDN forums via XenForo's JS-rendered search.

    Returns deduplicated list of {url, title, thread_id} dicts.
    """
    if not HAS_PLAYWRIGHT:
        print("  [ERROR] Playwright required for SDN search")
        return []

    threads = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        for term in tqdm(search_terms, desc="Searching SDN (Playwright)"):
            try:
                # Navigate to search form page
                page.goto(f"{SDN_BASE}/search/", wait_until="networkidle", timeout=20000)
                page.wait_for_timeout(1000)

                # SDN's keyword input is hidden behind a collapsed UI.
                # Use JS to set the value and submit the form directly.
                page.evaluate(f"""(() => {{
                    const input = document.querySelector('input[name="keywords"]');
                    if (input) {{
                        input.value = {repr(term)};
                        input.dispatchEvent(new Event('input', {{bubbles: true}}));
                    }}
                    const form = document.querySelector('form[action*="search"]');
                    if (form) form.submit();
                }})()""")

                # Wait for results page to load
                page.wait_for_load_state("networkidle", timeout=15000)
                page.wait_for_timeout(2000)

                # Wait for search results to render
                try:
                    page.wait_for_selector(".contentRow-title a", timeout=8000)
                except Exception:
                    # Maybe no results for this term
                    tqdm.write(f"  [SDN] No results for '{term}'")
                    continue

                # Paginate through results
                for pg in range(max_pages):
                    # Extract thread links from current page
                    links = page.query_selector_all(".contentRow-title a")
                    for link in links:
                        href = link.get_attribute("href") or ""
                        if "/threads/" not in href:
                            continue
                        full_url = urljoin(SDN_BASE, href)
                        clean_url = full_url.split("/page-")[0].split("/post-")[0].rstrip("/")
                        if clean_url in seen_urls:
                            continue
                        tid = re.search(r'\.(\d+)/?$', clean_url)
                        if not tid:
                            continue
                        title = link.inner_text().strip()
                        seen_urls.add(clean_url)
                        threads.append({
                            "url": clean_url,
                            "title": title,
                            "thread_id": tid.group(1),
                        })

                    # Try to go to next page
                    next_btn = page.query_selector("a.pageNav-jump--next")
                    if next_btn and pg < max_pages - 1:
                        next_btn.click()
                        page.wait_for_timeout(1500)
                        try:
                            page.wait_for_selector(".contentRow-title a", timeout=5000)
                        except Exception:
                            break
                    else:
                        break

            except Exception as e:
                tqdm.write(f"  [SDN search] '{term}': {e}")

            page.wait_for_timeout(int(RATE_LIMIT * 1000))

        browser.close()

    return threads


# ---------------------------------------------------------------------------
# SDN Thread Scraper (requests + BS4 — works without JS)
# ---------------------------------------------------------------------------
def scrape_sdn_thread(
    session: requests.Session,
    thread_info: dict,
    max_pages: int = 10,
    max_retries: int = 2,
) -> list[dict]:
    """Scrape all posts from a single SDN XenForo thread.

    Fixes applied:
      C1 — Running post counter instead of page-relative formula
      C2 — Strip <blockquote> elements before extracting body text
      M3 — Retry with backoff on transient failures
    """
    posts = []
    base_url = thread_info["url"]
    post_counter = 0  # C1 fix: running counter across pages

    for page in range(1, max_pages + 1):
        url = f"{base_url}/page-{page}" if page > 1 else base_url

        # M3 fix: retry with backoff
        resp = None
        for attempt in range(max_retries + 1):
            try:
                resp = session.get(url, headers=HEADERS, timeout=15)
                if resp.status_code == 200:
                    break
                if resp.status_code in (429, 503) and attempt < max_retries:
                    time.sleep(RATE_LIMIT * (attempt + 2))
                    continue
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries:
                    time.sleep(RATE_LIMIT * (attempt + 2))
                    continue
                print(f"  [SDN thread error] {url}: {e}")
                return posts  # return what we have so far

        if resp is None or resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "lxml")

        # XenForo message containers
        messages = soup.select("article.message--post, article.message")
        if not messages:
            messages = soup.select(".message--post, .message")
        if not messages and page > 1:
            break

        for msg in messages:
            # Author
            author_el = msg.select_one(
                ".message-userDetails a, .username, "
                "[data-author], .message-name a"
            )
            author = author_el.get_text(strip=True) if author_el else "Unknown"
            if not author and msg.get("data-author"):
                author = msg.get("data-author")

            # Body — C2 fix: strip blockquotes before extracting text
            body_el = msg.select_one(
                ".message-body .bbWrapper, .messageContent .bbWrapper, "
                ".message-content .bbWrapper, .bbWrapper"
            )
            if body_el:
                # Remove quoted content to avoid sentiment contamination
                for bq in body_el.find_all("blockquote"):
                    bq.decompose()
                # Also remove "Click to expand..." remnants
                for expand in body_el.find_all(class_="js-expandLink"):
                    expand.decompose()
                body = body_el.get_text(separator=" ", strip=True)
            else:
                body = ""

            # Date
            time_el = msg.select_one("time, .message-date time, .DateTime")
            date_str = ""
            if time_el:
                date_str = (
                    time_el.get("datetime", "")
                    or time_el.get("title", "")
                    or time_el.get_text(strip=True)
                )

            pol, subj = analyze_sentiment(body)

            posts.append({
                "source": "sdn",
                "thread_id": thread_info["thread_id"],
                "thread_title": thread_info["title"],
                "thread_url": thread_info["url"],
                "post_id": make_post_id("sdn", thread_info["thread_id"], post_counter),
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

    return posts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Collect PSLF forum discussions from SDN")
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--max_threads", type=int, default=200, help="Max threads to scrape")
    parser.add_argument("--search_pages", type=int, default=5, help="Search result pages per query")
    parser.add_argument("--thread_pages", type=int, default=10, help="Max pages per thread")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"SDN Forum PSLF Discussion Collector (Playwright + BS4)")
    print(f"{'='*60}")

    # Phase 1: Discover threads via headless browser search
    print(f"\nPhase 1: Searching SDN forums ({len(SEARCH_TERMS)} queries, up to {args.search_pages} pages each)...")
    threads = sdn_search_playwright(SEARCH_TERMS, max_pages=args.search_pages)
    threads = threads[:args.max_threads]
    print(f"  Found {len(threads)} unique PSLF-related threads")

    if not threads:
        print("  [ERROR] No threads found. Check network/Playwright installation.")
        return

    # Phase 2: Scrape thread contents with requests (M4 fix: use context manager)
    print(f"\nPhase 2: Scraping thread contents (up to {args.thread_pages} pages per thread)...")

    all_posts = []
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for thread in tqdm(threads, desc="Scraping SDN threads"):
            posts = scrape_sdn_thread(session, thread, max_pages=args.thread_pages)
            all_posts.extend(posts)

    # Write output
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for post in all_posts:
            writer.writerow(post)

    # Summary
    n_threads = len(set(p["thread_id"] for p in all_posts))
    print(f"\n{'='*60}")
    print(f"SDN collection complete!")
    print(f"  Threads scraped: {n_threads}")
    print(f"  Total posts: {len(all_posts):,}")
    if all_posts:
        import math
        pols = [p["polarity"] for p in all_posts if not math.isnan(p["polarity"])]
        if pols:
            print(f"  Mean polarity: {sum(pols)/len(pols):.4f} ({len(pols)} valid)")
        wcs = [p["word_count"] for p in all_posts]
        print(f"  Mean word count: {sum(wcs)/len(wcs):.0f}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
