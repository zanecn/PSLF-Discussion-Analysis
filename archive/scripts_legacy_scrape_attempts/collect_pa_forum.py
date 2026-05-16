"""
collect_pa_forum.py
===================
Scrapes PSLF-related threads from physicianassistantforum.com.

STATUS (Round-7 expansion attempt, 2026-05-08): **CLOUDFLARE-BLOCKED.**
Joins allnurses.com and bogleheads.org as forums whose search endpoints
are protected by an active Cloudflare Turnstile JS challenge that blocks
all programmatic access we tried:
  1. requests.Session with realistic Chrome UA + Referer chain → 403
  2. cloudscraper (purpose-built Cloudflare bypass library) → 403
  3. Playwright headless + cookie transfer to requests → 403
  4. Playwright direct fetch of search endpoint → "Just a moment..." page
     (real Turnstile challenge that blocks even a real browser headless)
The HOMEPAGE loads fine via Playwright but the SEARCH endpoint specifically
triggers a stricter check. Direct topic URLs (if known) might work via
Playwright but that requires a thread-discovery channel we don't have
without search.

Audit feasibility-investigation (2026-05-08) had identified PAF as
"easy-medium" but appears to have hit the homepage only. The search
endpoint is the gate. Forum PSLF threads exist (verified via WebFetch
returning 16KB of /topic/72154 content with 86 PSLF mentions) — they're
just not bulk-discoverable.

Code is preserved here as a starting point if Cloudflare protection
loosens, or for use with residential proxies / paid Cloudflare-bypass
services (CapSolver etc.). Not run in the current pipeline.

Software: forum runs Invision Community (IPS), URL pattern /topic/{id}-slug/.

Original output target: pa_forum_pslf_discussions.csv (same schema as
forum_pslf_discussions.csv).

Usage (will fail with Cloudflare 403 / Just-a-moment as of 2026-05-08):
    python collect_pa_forum.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from tqdm import tqdm

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import filter_pslf_relevant

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL = "https://www.physicianassistantforum.com"
OUTPUT_FILE = "pa_forum_pslf_discussions.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

RATE_LIMIT = 2.5  # seconds between thread page requests

FIELDS = [
    "source", "thread_id", "thread_title", "thread_url",
    "post_id", "post_number", "author", "body", "date_posted",
    "is_thread_start", "word_count", "polarity", "subjectivity",
    "scraped_at",
]

# PSLF-targeted search queries (broad enough to surface PSLF discussion in
# loan-forgiveness, public-service, and policy threads)
SEARCH_QUERIES = [
    "PSLF",
    "public service loan forgiveness",
    "loan forgiveness",
    "MOHELA",
]


def _polarity(text: str) -> tuple[float, float]:
    if not text or len(text) < 5:
        return float("nan"), float("nan")
    try:
        blob = TextBlob(text)
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return float("nan"), float("nan")


def _post_id(thread_id: str, post_number: int) -> str:
    raw = f"pa_forum:{thread_id}:{post_number}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _strip_quotes(soup: BeautifulSoup) -> None:
    """Remove quoted content from a post body (don't double-count quoted text)."""
    for q in soup.select("blockquote, .ipsQuote, .ipsComment_quoteContainer"):
        q.decompose()


def make_session() -> requests.Session:
    """Set up a requests session with Cloudflare-friendly headers."""
    sess = requests.Session()
    sess.headers.update(HEADERS)
    return sess


def warmup_session_playwright(sess: requests.Session) -> bool:
    """Use Playwright headless to pass Cloudflare, then transfer cookies to
    requests session. This is the SDN-scraper pattern (round-2 fix for
    JavaScript-rendered Cloudflare challenges).
    """
    if not HAS_PLAYWRIGHT:
        print("[ERROR] Playwright required for Cloudflare-protected sites. "
              "Run: pip install playwright && python -m playwright install chromium")
        return False
    print("  Launching Playwright headless to bypass Cloudflare...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 800},
                locale="en-US",
            )
            page = context.new_page()
            try:
                page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
            except Exception:
                pass  # may timeout but still get part-loaded with cookie
            page.wait_for_timeout(8000)  # let CF challenge finish
            # Diagnostic: check page state
            title = page.title()
            print(f"  Page title after warmup: {title!r}")
            if "just a moment" in title.lower() or "checking" in title.lower():
                print("  [WARN] Cloudflare challenge still in progress; waiting more...")
                page.wait_for_timeout(8000)
            # Extract cookies into the requests session
            for c in context.cookies():
                sess.cookies.set(c["name"], c["value"], domain=c.get("domain"),
                                  path=c.get("path", "/"))
            browser.close()
        sess.headers["Referer"] = BASE_URL
        # Verify the session works by re-hitting homepage
        r = sess.get(BASE_URL, timeout=15)
        if r.status_code != 200:
            print(f"[WARN] After Playwright warmup, requests still got {r.status_code}")
            return False
        print(f"  Cookies transferred. requests session works (status={r.status_code}).")
        return True
    except Exception as e:
        print(f"[ERROR] Playwright warmup failed: {e}")
        return False


def search_pa_forum(sess: requests.Session, query: str, max_pages: int = 5) -> list[dict]:
    """Search PA forum for query; return list of thread dicts.

    IPS search URL: /search/?q=PSLF&type=forums_topic
    """
    threads = []
    seen_urls = set()
    for page in range(1, max_pages + 1):
        params = {"q": query, "type": "forums_topic"}
        if page > 1:
            params["page"] = page
        try:
            r = sess.get(f"{BASE_URL}/search/", params=params, timeout=20,
                         allow_redirects=True)
            if r.status_code != 200:
                if page == 1:
                    print(f"  [WARN] Search '{query}' returned {r.status_code}")
                break
            soup = BeautifulSoup(r.text, "lxml")
            # IPS search results: each <li class="ipsStreamItem"> contains a thread
            results = soup.select("li.ipsStreamItem")
            if not results:
                # Fallback selector
                results = soup.select(".ipsContained .ipsStreamItem, .ipsType_break")
            for li in results:
                # Find the topic title link
                a = li.select_one("a[href*='/topic/']")
                if not a:
                    continue
                url = a.get("href", "")
                if not url:
                    continue
                # Normalize URL
                if not url.startswith("http"):
                    url = urljoin(BASE_URL, url)
                # Strip page/comment fragments to get base thread URL
                url = re.sub(r"[?#].*$", "", url)
                url = re.sub(r"/page/\d+/?$", "/", url)
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                title = a.get_text(" ", strip=True)
                # Extract thread id from URL pattern /topic/12345-slug/
                m = re.search(r"/topic/(\d+)-", url)
                tid = m.group(1) if m else url.split("/")[-1] or url
                threads.append({
                    "thread_id": tid,
                    "thread_url": url,
                    "thread_title": title,
                })
            if not results:
                break
            time.sleep(1.5)
        except Exception as e:
            print(f"  [WARN] Search page {page} failed: {e}")
            break
    return threads


def parse_thread_page(html: str, thread_url: str, thread_id: str,
                      thread_title: str, base_post_number: int) -> list[dict]:
    """Extract posts from one thread page (IPS forum HTML)."""
    soup = BeautifulSoup(html, "lxml")
    posts = []
    # IPS post articles
    post_articles = soup.select("article.cPost, article.ipsComment, .cPost_main")
    if not post_articles:
        # Less specific fallback
        post_articles = soup.select("[id^='comment-']")
    for i, art in enumerate(post_articles):
        # Author
        author_el = (art.select_one(".ipsType_break a, .cAuthorPane_author a, "
                                     ".author a, h3 a"))
        author = author_el.get_text(strip=True) if author_el else "unknown"
        # Date (ISO timestamp in <time datetime="...">)
        time_el = art.select_one("time[datetime]")
        date_iso = time_el.get("datetime", "") if time_el else ""
        # Body — strip quoted content
        body_el = (art.select_one(".cPost_contentWrap [data-role='commentContent'], "
                                   ".cPost_contentWrap, .ipsComment_content, "
                                   "[data-role='commentContent']"))
        if not body_el:
            continue
        body_copy = BeautifulSoup(str(body_el), "lxml")
        _strip_quotes(body_copy)
        body_text = body_copy.get_text(" ", strip=True)
        body_text = re.sub(r"\s+", " ", body_text)
        if not body_text or len(body_text) < 5:
            continue
        post_num = base_post_number + i
        wc = len(body_text.split())
        pol, subj = _polarity(body_text)
        posts.append({
            "source": "pa_forum",
            "thread_id": thread_id,
            "thread_title": thread_title,
            "thread_url": thread_url,
            "post_id": _post_id(thread_id, post_num),
            "post_number": post_num,
            "author": author,
            "body": body_text,
            "date_posted": date_iso,
            "is_thread_start": (post_num == 1),
            "word_count": wc,
            "polarity": pol,
            "subjectivity": subj,
            "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
    return posts


def scrape_thread(sess: requests.Session, thread: dict, max_pages: int = 20) -> list[dict]:
    """Walk through all pages of a thread and extract posts."""
    all_posts = []
    base_url = thread["thread_url"].rstrip("/") + "/"
    page = 1
    base_post_number = 1
    while page <= max_pages:
        url = base_url if page == 1 else f"{base_url}page/{page}/"
        try:
            r = sess.get(url, timeout=20, allow_redirects=True)
            if r.status_code == 404:
                break
            if r.status_code != 200:
                if page == 1:
                    print(f"  [WARN] {thread['thread_id']} returned {r.status_code}")
                break
            page_posts = parse_thread_page(r.text, thread["thread_url"],
                                           thread["thread_id"],
                                           thread["thread_title"],
                                           base_post_number)
            if not page_posts:
                break
            all_posts.extend(page_posts)
            base_post_number += len(page_posts)
            # Check for "next page" link; if absent we're at the last page
            soup = BeautifulSoup(r.text, "lxml")
            next_el = soup.select_one("li.ipsPagination_next:not(.ipsPagination_inactive) a, "
                                       "a[rel='next']")
            if not next_el:
                break
            page += 1
            time.sleep(RATE_LIMIT)
        except Exception as e:
            print(f"  [WARN] {thread['thread_id']} page {page} failed: {e}")
            break
    return all_posts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_threads", type=int, default=200)
    parser.add_argument("--search_pages", type=int, default=5)
    parser.add_argument("--max_thread_pages", type=int, default=20)
    parser.add_argument("--output", default=OUTPUT_FILE)
    parser.add_argument("--dry_run", action="store_true",
                        help="Search and discover threads, then exit (no thread fetches).")
    args = parser.parse_args()

    sess = make_session()
    print("Warming up session (Playwright -> requests cookie transfer)...")
    if not warmup_session_playwright(sess):
        print("[ABORT] Could not establish session.")
        sys.exit(1)

    # Search for PSLF-related threads
    print(f"\nSearching for PSLF-related threads ({len(SEARCH_QUERIES)} queries)...")
    all_threads = {}
    for q in SEARCH_QUERIES:
        print(f"  Query: '{q}'")
        thr = search_pa_forum(sess, q, max_pages=args.search_pages)
        for t in thr:
            if t["thread_id"] not in all_threads:
                all_threads[t["thread_id"]] = t
        print(f"    Cumulative unique threads: {len(all_threads)}")
        time.sleep(1.0)

    threads = list(all_threads.values())[:args.max_threads]
    print(f"\nDiscovered {len(threads)} unique threads (cap={args.max_threads})")

    if args.dry_run:
        print("\n[DRY RUN] First 10 thread titles:")
        for t in threads[:10]:
            print(f"  {t['thread_id']}: {t['thread_title'][:80]}")
        print(f"\n[DRY RUN] {len(threads)} total threads would be scraped.")
        print(f"  Estimated wall-time: ~{len(threads) * 0.5:.0f} min "
              f"(assuming 2-3 pages per thread, {RATE_LIMIT}s/page rate limit)")
        return

    # Scrape each thread
    print(f"\nScraping thread bodies (rate limit {RATE_LIMIT}s/page)...")
    all_posts = []
    for t in tqdm(threads, desc="Threads"):
        posts = scrape_thread(sess, t, max_pages=args.max_thread_pages)
        all_posts.extend(posts)

    print(f"\nCollected {len(all_posts):,} raw posts from {len(threads)} threads")

    # Apply strict PSLF filter
    if all_posts:
        bodies = [p["body"] for p in all_posts]
        import pandas as pd
        body_series = pd.Series(bodies)
        title_series = pd.Series([p["thread_title"] for p in all_posts])
        pslf_match_body = filter_pslf_relevant(body_series)
        pslf_match_title = filter_pslf_relevant(title_series)
        keep = (pslf_match_body | pslf_match_title).to_numpy()
        filtered = [p for p, k in zip(all_posts, keep) if k]
        print(f"After PSLF strict filter: {len(filtered):,} posts")
    else:
        filtered = []

    # Write output
    if filtered:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for p in filtered:
                w.writerow({k: p.get(k, "") for k in FIELDS})
        print(f"\nWrote {len(filtered):,} posts to {args.output}")
    else:
        print(f"\n[WARN] No PSLF-filtered posts; not writing {args.output}")


if __name__ == "__main__":
    main()
