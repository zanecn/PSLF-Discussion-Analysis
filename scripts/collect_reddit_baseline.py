"""
collect_reddit_baseline.py
==========================
Collects two non-PSLF Reddit baselines for sentiment calibration.

Round-3 audit fix R3-3:
  Original baseline (n=330) used sort=top/hot/new which biases toward
  viral content. This version:
    1. Uses ONLY sort=relevance and sort=new (matching PSLF collector)
    2. Targets n>=1000 per baseline
    3. Adds a TOPICALLY-NEAR baseline: posts in our own subreddits that
       FAIL the strict PSLF filter — same population, same platform,
       same year distribution, but off-topic.
    4. Reports length-matched comparisons (re-weight by word-count quintile).

Outputs:
  reddit_baseline_askreddit.csv      — generic Reddit baseline
  reddit_baseline_topical_near.csv   — same-population off-PSLF baseline
"""
from __future__ import annotations

import csv
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd
import requests
from textblob import TextBlob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import filter_pslf_relevant

USER_AGENT = "PSLF-Analysis/2.0 (academic research; baseline calibration)"
HEADERS = {"User-Agent": USER_AGENT}
RATE_LIMIT = 2.5
MIN_WORDS = 20


def textblob_pol(text: str) -> float:
    if not text or not text.strip():
        return float("nan")
    try:
        return round(TextBlob(text[:5000]).sentiment.polarity, 6)
    except Exception:
        return float("nan")


# ---------------------------------------------------------------------------
# Generic baseline: r/AskReddit (relevance + new sort modes only)
# ---------------------------------------------------------------------------
def fetch_askreddit_baseline(n_target: int = 1000) -> list[dict]:
    """Fetch r/AskReddit posts using sort modes matching PSLF collector."""
    out = []
    seen = set()
    # Match PSLF collector sort modes (drop 'top' to avoid viral bias)
    for sort in ("relevance", "new"):
        for time_window in ("year", "all", "month", "week"):
            after = None
            for page in range(15):
                if len(out) >= n_target:
                    return out
                if sort == "relevance":
                    # Relevance requires a query; use a generic seed
                    url = "https://old.reddit.com/r/AskReddit/search.json"
                    params = {"q": "everyone", "restrict_sr": "on",
                              "sort": sort, "t": time_window, "limit": 100}
                else:
                    url = "https://old.reddit.com/r/AskReddit/new.json"
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
                        if not pid or pid in seen:
                            continue
                        title = d.get("title", "") or ""
                        body = d.get("selftext", "") or ""
                        text = (title + " " + body).strip()
                        wc = len(text.split())
                        if wc < MIN_WORDS:
                            continue
                        pol = textblob_pol(text)
                        seen.add(pid)
                        out.append({
                            "id": pid, "subreddit": "AskReddit",
                            "title": title[:500],
                            "combined_text": text[:5000],
                            "score": d.get("score", 0),
                            "num_comments": d.get("num_comments", 0),
                            "created_utc": d.get("created_utc"),
                            "polarity": pol, "word_count": wc,
                            "sort": sort, "time_window": time_window,
                        })
                    after = data.get("data", {}).get("after")
                    if not after:
                        break
                    time.sleep(RATE_LIMIT)
                except Exception as e:
                    print(f"  ERROR: {e}")
                    break
    return out


# ---------------------------------------------------------------------------
# Topically-near baseline: posts in our subs that FAIL strict PSLF filter
# ---------------------------------------------------------------------------
def make_topical_near_baseline() -> pd.DataFrame:
    """Use the existing reddit_professions_pslf.csv but invert the filter.

    Posts in the same subreddits that DON'T pass strict PSLF filter give us
    a same-population, same-platform off-topic comparison.
    """
    if not os.path.exists("reddit_professions_pslf.csv"):
        print("  reddit_professions_pslf.csv not found, skipping topical-near")
        return pd.DataFrame()
    df = pd.read_csv("reddit_professions_pslf.csv")
    tm = filter_pslf_relevant(df["combined_text"])
    tt = filter_pslf_relevant(df["title"])
    off_topic = df[~(tm | tt)].copy()
    if "polarity" not in off_topic.columns or off_topic["polarity"].isna().all():
        # Recompute polarity if missing
        off_topic["polarity"] = off_topic["combined_text"].fillna("").apply(textblob_pol)
    # Apply word count filter consistently
    off_topic["word_count"] = off_topic["combined_text"].fillna("").str.split().str.len()
    off_topic = off_topic[off_topic["word_count"] >= MIN_WORDS]
    return off_topic


# ---------------------------------------------------------------------------
# Length-matched comparison
# ---------------------------------------------------------------------------
def length_matched_comparison(baseline_df: pd.DataFrame,
                              pslf_df: pd.DataFrame) -> dict:
    """Re-weight baseline polarity by PSLF corpus word-count distribution.

    Standard inverse-propensity weighting on word-count quintiles.
    """
    bl = baseline_df.copy()
    pl = pslf_df.copy()
    bl["wc"] = bl["combined_text"].fillna("").str.split().str.len() if "combined_text" in bl.columns else bl.get("word_count", pd.Series([0] * len(bl)))
    pl["wc"] = pl["combined_text"].fillna("").str.split().str.len() if "combined_text" in pl.columns else pl.get("word_count", pd.Series([0] * len(pl)))
    # Quintiles based on PSLF distribution (the target)
    pl_q = pd.qcut(pl["wc"].clip(lower=1), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    pl["q"] = pl_q
    pl_weights = pl["q"].value_counts(normalize=True).sort_index()
    # Bin baseline by same edges
    edges = pd.qcut(pl["wc"].clip(lower=1), q=5, retbins=True, duplicates="drop")[1]
    bl["q"] = pd.cut(bl["wc"], bins=edges, labels=[i + 1 for i in range(len(edges) - 1)],
                     include_lowest=True)
    # Compute weighted mean
    bl_means = bl.groupby("q", observed=True)["polarity"].mean()
    weighted_mean = sum(bl_means.get(q, 0) * w for q, w in pl_weights.items())
    return {
        "baseline_raw_mean": float(bl["polarity"].mean()),
        "baseline_lengthmatched_mean": float(weighted_mean),
        "pslf_mean": float(pl["polarity"].mean()),
        "n_baseline": len(bl),
        "n_pslf": len(pl),
    }


def main():
    print("=== Collecting r/AskReddit baseline (n_target=1000) ===")
    posts = fetch_askreddit_baseline(n_target=1000)
    print(f"  Collected {len(posts):,} posts")
    if posts:
        pols = [p["polarity"] for p in posts if p["polarity"] == p["polarity"]]
        if pols:
            mean_p = sum(pols) / len(pols)
            pct_neg = sum(1 for x in pols if x < 0) / len(pols) * 100
            n = len(pols)
            se_p = (mean_p * (1 - mean_p) / n) ** 0.5 if 0 <= mean_p <= 1 else 0  # rough
            print(f"  AskReddit polarity: {mean_p:.4f} ({pct_neg:.1f}% negative, n={n})")
            print(f"  95% CI on %neg: [{pct_neg - 196*((pct_neg/100)*(1-pct_neg/100)/n)**0.5:.1f}%, "
                  f"{pct_neg + 196*((pct_neg/100)*(1-pct_neg/100)/n)**0.5:.1f}%]")
        fields = list(posts[0].keys())
        with open("reddit_baseline_askreddit.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for p in posts:
                writer.writerow(p)
        print("  Saved: reddit_baseline_askreddit.csv")

    print("\n=== Building topical-near baseline (off-PSLF posts in our subs) ===")
    near = make_topical_near_baseline()
    print(f"  Collected {len(near):,} off-topic posts from PSLF subs")
    if not near.empty:
        m = near["polarity"].dropna().mean()
        n = (near["polarity"] < 0).sum()
        total = near["polarity"].notna().sum()
        print(f"  Topical-near polarity: {m:.4f} ({n/total*100:.1f}% negative, n={total})")
        near.to_csv("reddit_baseline_topical_near.csv", index=False)
        print("  Saved: reddit_baseline_topical_near.csv")

    # Length-matched comparison
    print("\n=== Length-matched comparison ===")
    if posts and not near.empty:
        bl_df = pd.DataFrame(posts)
        # Compare against PSLF medical
        if os.path.exists("comprehensive_medical_pslf_discussions.csv"):
            pslf_med = pd.read_csv("comprehensive_medical_pslf_discussions.csv")
            pslf_med["combined_text"] = pslf_med["combined_text"].fillna("")
            wc = pslf_med["combined_text"].str.split().str.len()
            pslf_med = pslf_med[wc >= MIN_WORDS]
            res = length_matched_comparison(bl_df, pslf_med)
            print(f"  AskReddit raw: {res['baseline_raw_mean']:.4f} (n={res['n_baseline']})")
            print(f"  AskReddit length-matched to PSLF medical: {res['baseline_lengthmatched_mean']:.4f}")
            print(f"  PSLF medical: {res['pslf_mean']:.4f} (n={res['n_pslf']})")


if __name__ == "__main__":
    main()
