"""
analyze_admin_data_correlation.py
==================================
Pulls publicly available PSLF / student loan administrative data and
correlates it with our online-community sentiment time series.

Public data sources used:
  1. CFPB Consumer Complaints Database (free public API)
     - Filters student loan complaints with PSLF/forgiveness mentions
     - Available through Socrata + raw API
  2. Department of Education FSA quarterly PSLF reports (where parseable)
  3. AAMC physician debt data (where parseable)

Produces:
  - admin_data_pslf_complaints.csv  (CFPB complaints, PSLF-filtered)
  - admin_sentiment_correlation.png (multi-panel comparison figure)
  - admin_correlation_results.txt   (Pearson/Spearman + lag analysis)

References:
  - CFPB API: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/
  - Granger (1969): tests for predictive causality between time series
  - Box-Jenkins (1970): cross-correlation function for time-series alignment
"""
from __future__ import annotations

import argparse
import os
import sys
import warnings
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from scipy import stats

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import PSLF_STRICT_REGEX

CFPB_API = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
HEADERS = {
    "User-Agent": "PSLF-Analysis/2.0 (academic research)",
}


# ---------------------------------------------------------------------------
# CFPB Complaints
# ---------------------------------------------------------------------------
def fetch_cfpb_complaints(date_min: str = "2016-01-01",
                          date_max: str = "2026-04-24",
                          page_size: int = 1000,
                          max_pages: int = 50) -> pd.DataFrame:
    """Fetch CFPB student loan complaints mentioning PSLF/forgiveness.

    Uses CFPB's public Socrata-style API. Each page returns up to 1000 rows.
    """
    print(f"Fetching CFPB complaints {date_min} to {date_max}...")
    all_hits = []
    seen = set()

    # Try multiple search angles to capture varied complaint vocabulary
    search_terms = ["PSLF", "public service loan forgiveness", "loan forgiveness",
                    "MOHELA", "FedLoan", "income driven", "SAVE plan"]

    for term in search_terms:
        print(f"  Searching: '{term}'")
        for page in range(max_pages):
            params = {
                "search_term": term,
                "date_received_min": date_min,
                "date_received_max": date_max,
                "product": "Student loan",
                "size": page_size,
                "frm": page * page_size,
                "format": "json",
            }
            try:
                r = requests.get(CFPB_API, params=params, headers=HEADERS, timeout=30)
                if r.status_code != 200:
                    print(f"    HTTP {r.status_code}")
                    break
                data = r.json()
                # CFPB API returns either {"hits":{"hits":[...]}} or a flat list of hits
                if isinstance(data, dict):
                    hits = data.get("hits", {}).get("hits", []) if isinstance(data.get("hits"), dict) else data.get("hits", [])
                elif isinstance(data, list):
                    hits = data
                else:
                    hits = []
                if not hits:
                    break
                for hit in hits:
                    src = hit.get("_source", hit) if isinstance(hit, dict) else {}
                    cid = src.get("complaint_id", hit.get("_id", "") if isinstance(hit, dict) else "")
                    if cid and cid not in seen:
                        seen.add(cid)
                        src["query_matched"] = term
                        all_hits.append(src)
                if len(hits) < page_size:
                    break
            except requests.RequestException as e:
                print(f"    ERROR: {e}")
                break

    print(f"  Total unique complaints: {len(all_hits):,}")

    if not all_hits:
        return pd.DataFrame()

    df = pd.DataFrame(all_hits)
    # Parse dates as tz-naive (CFPB returns ISO strings; normalize to match sentiment data)
    if "date_received" in df.columns:
        df["date"] = pd.to_datetime(df["date_received"], errors="coerce", utc=True).dt.tz_localize(None)
    return df


# ---------------------------------------------------------------------------
# Load sentiment data
# ---------------------------------------------------------------------------
def load_sentiment_data() -> pd.DataFrame:
    """Load combined sentiment data with strict PSLF filter."""
    frames = []
    for f, prof in [
        ("comprehensive_medical_pslf_discussions.csv", "medical"),
        ("comprehensive_teacher_pslf_discussions.csv", "teacher"),
    ]:
        if os.path.exists(f):
            df = pd.read_csv(f)
            df["profession"] = prof
            df["source"] = "reddit"
            df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"), unit="s")
            df["text"] = df["combined_text"].fillna("")
            frames.append(df[["date", "polarity", "text", "source", "profession"]])

    if os.path.exists("reddit_professions_pslf.csv"):
        pf = pd.read_csv("reddit_professions_pslf.csv")
        tm = pf["combined_text"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        tt = pf["title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        pf = pf[tm | tt].copy()
        pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
        pf["text"] = pf["combined_text"].fillna("")
        pf["source"] = "reddit_prof"
        frames.append(pf[["date", "polarity", "text", "source", "profession"]])

    if os.path.exists("forum_pslf_discussions.csv"):
        sdn = pd.read_csv("forum_pslf_discussions.csv")
        bm = sdn["body"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        ttm = sdn["thread_title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        sdn = sdn[bm | ttm].copy()
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce")
        sdn["text"] = sdn["body"].fillna("")
        sdn["source"] = "sdn"
        sdn["profession"] = "sdn_medical"
        frames.append(sdn[["date", "polarity", "text", "source", "profession"]])

    all_data = pd.concat(frames, ignore_index=True).dropna(subset=["date", "polarity"])
    all_data["date"] = pd.to_datetime(all_data["date"], utc=True).dt.tz_localize(None)
    wc = all_data["text"].str.split().str.len()
    all_data.loc[wc < 20, "polarity"] = np.nan
    return all_data.dropna(subset=["polarity"])


# ---------------------------------------------------------------------------
# Cross-correlation analysis (Box-Jenkins 1970)
# ---------------------------------------------------------------------------
def cross_correlation(s1: pd.Series, s2: pd.Series, max_lag: int = 6) -> dict:
    """Compute lagged Pearson correlations between two monthly series."""
    aligned = pd.concat([s1.rename("s1"), s2.rename("s2")], axis=1).dropna()
    if len(aligned) < max_lag + 5:
        return {}

    results = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            r, p = stats.pearsonr(aligned["s1"].shift(-lag).dropna(),
                                  aligned["s2"].iloc[-lag:].iloc[:len(aligned["s1"].shift(-lag).dropna())])
        elif lag > 0:
            shifted = aligned["s2"].shift(-lag).dropna()
            r, p = stats.pearsonr(aligned["s1"].iloc[:len(shifted)], shifted)
        else:
            r, p = stats.pearsonr(aligned["s1"], aligned["s2"])
        results[lag] = (r, p)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-fetch", action="store_true",
                        help="Skip CFPB API fetch, reuse cached file")
    parser.add_argument("--cache", default="admin_data_pslf_complaints.csv")
    args = parser.parse_args()

    # 1. Get CFPB complaints
    if args.no_fetch and os.path.exists(args.cache):
        print(f"Loading cached complaints from {args.cache}")
        complaints = pd.read_csv(args.cache)
        complaints["date"] = pd.to_datetime(complaints["date"], errors="coerce", utc=True).dt.tz_localize(None)
    else:
        complaints = fetch_cfpb_complaints()
        if not complaints.empty:
            complaints.to_csv(args.cache, index=False)
            print(f"  Saved to {args.cache}")

    if complaints.empty:
        print("[ERROR] No CFPB data — cannot proceed")
        return

    # 2. Filter to PSLF-relevant complaints
    text_cols = [c for c in ["complaint_what_happened", "issue", "sub_issue",
                             "sub_product", "product"] if c in complaints.columns]
    if text_cols:
        text_blob = complaints[text_cols].fillna("").agg(" ".join, axis=1).str.lower()
        pslf_mask = text_blob.str.contains(PSLF_STRICT_REGEX, na=False)
        complaints_pslf = complaints[pslf_mask].copy()
    else:
        complaints_pslf = complaints.copy()

    print(f"\nCFPB student loan complaints: {len(complaints):,}")
    print(f"PSLF-relevant after strict filter: {len(complaints_pslf):,}")

    # 3. Load sentiment data
    print("\nLoading sentiment data...")
    sent = load_sentiment_data()
    print(f"  Sentiment posts: {len(sent):,}")

    # 4. Build monthly time series
    monthly_complaints = complaints_pslf.set_index("date").resample("ME").size()
    monthly_sentiment = sent.set_index("date").resample("ME")["polarity"].agg(["mean", "count", "std"])
    monthly_sentiment = monthly_sentiment[monthly_sentiment["count"] >= 5]
    monthly_neg = sent.set_index("date").resample("ME")["polarity"].apply(
        lambda x: (x < 0).mean() * 100 if len(x) >= 5 else np.nan
    ).dropna()

    # Trim to common date range
    common_start = max(monthly_complaints.index.min(), monthly_sentiment.index.min())
    common_end = min(monthly_complaints.index.max(), monthly_sentiment.index.max())
    monthly_complaints = monthly_complaints[(monthly_complaints.index >= common_start) &
                                            (monthly_complaints.index <= common_end)]
    monthly_sentiment = monthly_sentiment[(monthly_sentiment.index >= common_start) &
                                          (monthly_sentiment.index <= common_end)]
    monthly_neg = monthly_neg[(monthly_neg.index >= common_start) &
                              (monthly_neg.index <= common_end)]

    # 5. Correlation analyses
    print("\n" + "=" * 70)
    print("CORRELATION: SENTIMENT VS CFPB COMPLAINT VOLUME")
    print("=" * 70)

    # Contemporaneous
    aligned = pd.concat([
        monthly_complaints.rename("complaints"),
        monthly_sentiment["mean"].rename("polarity"),
        monthly_neg.rename("pct_neg"),
    ], axis=1).dropna()

    if len(aligned) >= 10:
        r1, p1 = stats.pearsonr(aligned["complaints"], aligned["polarity"])
        r2, p2 = stats.pearsonr(aligned["complaints"], aligned["pct_neg"])
        rho1, pp1 = stats.spearmanr(aligned["complaints"], aligned["polarity"])
        rho2, pp2 = stats.spearmanr(aligned["complaints"], aligned["pct_neg"])

        print(f"\n  Pearson:")
        print(f"    Complaint volume vs polarity:  r = {r1:+.3f}, p = {p1:.4f}")
        print(f"    Complaint volume vs % negative: r = {r2:+.3f}, p = {p2:.4f}")
        print(f"\n  Spearman (rank, robust to outliers):")
        print(f"    Complaint volume vs polarity:  rho = {rho1:+.3f}, p = {pp1:.4f}")
        print(f"    Complaint volume vs % negative: rho = {rho2:+.3f}, p = {pp2:.4f}")
        print(f"  N (months overlap): {len(aligned)}")

        # 6. Lagged cross-correlation
        print("\n  Cross-correlation (sentiment leads/lags complaints):")
        lags = cross_correlation(monthly_sentiment["mean"], monthly_complaints, max_lag=6)
        if lags:
            print(f"    {'Lag (months)':>14s}  {'r':>8s}  {'p':>8s}")
            for lag in sorted(lags.keys()):
                r, p = lags[lag]
                interp = "(sentiment leads)" if lag > 0 else "(complaints lead)" if lag < 0 else "(simultaneous)"
                print(f"    {lag:>14d}  {r:+8.3f}  {p:8.4f}  {interp}")

    # 7. Generate figure
    print("\nGenerating correlation figure...")
    fig, axes = plt.subplots(3, 1, figsize=(20, 14), gridspec_kw={"height_ratios": [2, 2, 2]})
    fig.suptitle(
        f"PSLF Online Sentiment vs CFPB Complaints (Public Administrative Data)\n"
        f"(n={len(sent):,} posts | n={len(complaints_pslf):,} complaints)",
        fontsize=18, fontweight="bold", y=0.99,
    )

    # Panel 1: Dual-axis sentiment + complaints
    ax1 = axes[0]
    ax1b = ax1.twinx()
    ax1.plot(monthly_sentiment.index, monthly_sentiment["mean"], color="#FF6B35",
             linewidth=2, label="Mean Sentiment Polarity (left)")
    ax1.set_ylabel("Mean Polarity", color="#FF6B35", fontsize=12)
    ax1.tick_params(axis="y", labelcolor="#FF6B35")
    ax1.axhline(y=0, color="gray", linewidth=0.5)
    ax1b.plot(monthly_complaints.index, monthly_complaints.values, color="#1976D2",
              linewidth=2, alpha=0.8, label="CFPB Complaints (right)")
    ax1b.set_ylabel("CFPB PSLF Complaints (monthly)", color="#1976D2", fontsize=12)
    ax1b.tick_params(axis="y", labelcolor="#1976D2")
    ax1.set_title("Online Sentiment vs Administrative Complaint Volume", fontsize=14, fontweight="bold")
    ax1.grid(alpha=0.3)

    # Panel 2: % negative vs complaints
    ax2 = axes[1]
    ax2b = ax2.twinx()
    ax2.plot(monthly_neg.index, monthly_neg.values, color="#D32F2F",
             linewidth=2, label="% Negative Posts (left)")
    ax2.set_ylabel("% Negative Posts", color="#D32F2F", fontsize=12)
    ax2.tick_params(axis="y", labelcolor="#D32F2F")
    ax2b.plot(monthly_complaints.index, monthly_complaints.values, color="#1976D2",
              linewidth=2, alpha=0.8, label="CFPB Complaints (right)")
    ax2b.set_ylabel("CFPB PSLF Complaints (monthly)", color="#1976D2", fontsize=12)
    ax2b.tick_params(axis="y", labelcolor="#1976D2")
    ax2.set_title("Negativity Rate vs Complaint Volume", fontsize=14, fontweight="bold")
    ax2.grid(alpha=0.3)

    # Panel 3: Cross-correlation function
    ax3 = axes[2]
    if "lags" in dir() and lags:
        lag_keys = sorted(lags.keys())
        rs = [lags[k][0] for k in lag_keys]
        ps = [lags[k][1] for k in lag_keys]
        colors = ["#D32F2F" if p < 0.05 else "#9E9E9E" for p in ps]
        ax3.bar(lag_keys, rs, color=colors, alpha=0.7, edgecolor="black")
        ax3.axhline(y=0, color="black", linewidth=0.5)
        ax3.set_xlabel("Lag in months (positive = sentiment leads complaints)", fontsize=12)
        ax3.set_ylabel("Pearson r", fontsize=12)
        ax3.set_title("Cross-correlation Function (Sentiment vs CFPB Complaints)", fontsize=14, fontweight="bold")
        ax3.grid(alpha=0.3)
        ax3.set_xticks(lag_keys)
        # Highlight significant
        for k, r, p in zip(lag_keys, rs, ps):
            if p < 0.05:
                ax3.annotate(f"p={p:.3f}", (k, r), fontsize=8, ha="center",
                             va="bottom" if r > 0 else "top")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("admin_sentiment_correlation.png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: admin_sentiment_correlation.png")

    # 8. Save text summary
    with open("admin_correlation_results.txt", "w", encoding="utf-8") as f:
        f.write("PSLF SENTIMENT vs ADMINISTRATIVE DATA CORRELATION ANALYSIS\n")
        f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"\nData: {len(sent):,} sentiment posts, {len(complaints_pslf):,} CFPB complaints\n")
        f.write(f"Date range: {common_start.date()} to {common_end.date()}\n")
        f.write(f"\nCONTEMPORANEOUS CORRELATIONS (n={len(aligned)} months):\n")
        if len(aligned) >= 10:
            f.write(f"  Pearson r (volume vs polarity): {r1:+.3f}, p={p1:.4f}\n")
            f.write(f"  Pearson r (volume vs %neg):     {r2:+.3f}, p={p2:.4f}\n")
            f.write(f"  Spearman rho (volume vs polarity): {rho1:+.3f}, p={pp1:.4f}\n")
            f.write(f"  Spearman rho (volume vs %neg):     {rho2:+.3f}, p={pp2:.4f}\n")
        if lags:
            f.write(f"\nCROSS-CORRELATION (sentiment vs complaints):\n")
            for lag in sorted(lags.keys()):
                r, p = lags[lag]
                f.write(f"  Lag {lag:+3d} months: r={r:+.3f}, p={p:.4f}\n")
    print(f"  Saved: admin_correlation_results.txt")


if __name__ == "__main__":
    main()
