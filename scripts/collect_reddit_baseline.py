"""
collect_reddit_baseline.py
==========================
Collects a non-PSLF Reddit baseline from r/AskReddit (general off-topic
discussion) and computes TextBlob polarity using the same pipeline as
the PSLF analysis. Used as a calibration reference.

Per round-2 audit: the headline finding "PSLF posts are negative
(pol ~0.07)" is meaningless without a Reddit-typical baseline.

Output: reddit_baseline_askreddit.csv
"""
from __future__ import annotations

import csv
import os
import sys
import time
from datetime import datetime, timezone

import requests
from textblob import TextBlob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

USER_AGENT = "PSLF-Analysis/2.0 (academic research; baseline calibration)"
HEADERS = {"User-Agent": USER_AGENT}
RATE_LIMIT = 2.5
OUT = "reddit_baseline_askreddit.csv"


def fetch_baseline(n_posts: int = 500) -> list[dict]:
    """Fetch top general-discussion posts from r/AskReddit."""
    sub = "AskReddit"
    out = []
    after = None

    for sort in ("top", "hot", "new"):
        for time_window in ("year", "month", "week"):
            after = None
            for page in range(10):
                if len(out) >= n_posts:
                    return out
                url = f"https://old.reddit.com/r/{sub}/{sort}.json"
                params = {"limit": 100, "t": time_window}
                if after:
                    params["after"] = after
                try:
                    r = requests.get(url, params=params, headers=HEADERS, timeout=20)
                    if r.status_code != 200:
                        time.sleep(RATE_LIMIT * 2)
                        break
                    data = r.json()
                    posts = data.get("data", {}).get("children", [])
                    if not posts:
                        break
                    for p in posts:
                        d = p.get("data", {})
                        pid = d.get("id")
                        if not pid or any(o["id"] == pid for o in out):
                            continue
                        title = d.get("title", "") or ""
                        body = d.get("selftext", "") or ""
                        text = (title + " " + body).strip()
                        if len(text.split()) < 20:
                            continue
                        try:
                            pol = round(TextBlob(text[:5000]).sentiment.polarity, 6)
                        except Exception:
                            pol = float("nan")
                        out.append({
                            "id": pid,
                            "subreddit": sub,
                            "title": title,
                            "selftext": body[:5000],
                            "combined_text": text[:5000],
                            "score": d.get("score", 0),
                            "num_comments": d.get("num_comments", 0),
                            "created_utc": d.get("created_utc"),
                            "polarity": pol,
                            "word_count": len(text.split()),
                            "sort": sort,
                            "time_window": time_window,
                        })
                    after = data.get("data", {}).get("after")
                    if not after:
                        break
                    time.sleep(RATE_LIMIT)
                except Exception as e:
                    print(f"  ERROR: {e}")
                    break
    return out


def main():
    print(f"Collecting r/AskReddit baseline (general discussion, no PSLF)")
    posts = fetch_baseline(n_posts=500)
    print(f"  Collected {len(posts):,} posts")
    if not posts:
        print("  No data collected")
        return

    # Compute summary stats
    pols = [p["polarity"] for p in posts if p["polarity"] == p["polarity"]]
    if pols:
        mean_pol = sum(pols) / len(pols)
        pct_neg = sum(1 for x in pols if x < 0) / len(pols) * 100
        print(f"  Baseline polarity: {mean_pol:.4f}")
        print(f"  Baseline %neg: {pct_neg:.1f}%")
        print(f"  (For comparison: PSLF medical pol=0.070, %neg=22.3%)")

    fields = list(posts[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in posts:
            writer.writerow(p)
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
