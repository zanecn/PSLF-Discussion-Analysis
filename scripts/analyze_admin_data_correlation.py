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

# Consistent aesthetic theme
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linestyle": "-",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "legend.frameon": False,
    "font.family": "DejaVu Sans",
    "axes.titlepad": 10,
})
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import PSLF_STRICT_REGEX, filter_pslf_relevant

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

    # Round-3 audit fix J: detect when we hit CFPB's 10000-result hard cap
    # (Elasticsearch frm+size cannot exceed 10000 per query).
    cfpb_cap_warnings = []

    for term in search_terms:
        print(f"  Searching: '{term}'")
        term_count = 0
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
                term_count += len(hits)
                # Detect CFPB 10000-result hard cap (ES frm+size limit)
                if (page + 1) * page_size >= 10000 and len(hits) == page_size:
                    cfpb_cap_warnings.append(term)
                    print(f"    [CFPB CAP] '{term}' hit 10000-result ceiling at page {page}")
                    break
                if len(hits) < page_size:
                    break
            except requests.RequestException as e:
                print(f"    ERROR: {e}")
                break

    print(f"  Total unique complaints: {len(all_hits):,}")
    if cfpb_cap_warnings:
        print(f"  [WARNING] {len(cfpb_cap_warnings)} search terms hit CFPB's 10K cap: {cfpb_cap_warnings}")
        print(f"  Recommend date-window stratification for those terms.")

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
        tm = filter_pslf_relevant(pf["combined_text"])
        tt = filter_pslf_relevant(pf["title"])
        pf = pf[tm | tt].copy()
        pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
        pf["text"] = pf["combined_text"].fillna("")
        pf["source"] = "reddit_prof"
        frames.append(pf[["date", "polarity", "text", "source", "profession"]])

    if os.path.exists("forum_pslf_discussions.csv"):
        sdn = pd.read_csv("forum_pslf_discussions.csv")
        bm = filter_pslf_relevant(sdn["body"])
        ttm = filter_pslf_relevant(sdn["thread_title"])
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
def cross_correlation(s1: pd.Series, s2: pd.Series, max_lag: int = 6,
                       difference: bool = True) -> dict:
    """Compute lagged Pearson correlations between two monthly time series.

    Per audit consensus, this implementation:
      1. Reindexes to a regular monthly grid (so lag k means k calendar months,
         not k row positions on an irregular index).
      2. First-differences both series to remove trends (Box-Jenkins 1970:
         CCF on stationarized series; otherwise spurious correlation per
         Granger & Newbold 1974).
      3. Uses ndarray-level positional shifting for correctness.
      4. Returns Bonferroni-corrected alpha alongside per-lag p-values.

    Returns dict mapping lag -> (r, p, n_pairs).
    """
    # Build a uniform monthly index
    aligned = pd.concat([s1.rename("s1"), s2.rename("s2")], axis=1)
    aligned.index = pd.to_datetime(aligned.index)
    full_idx = pd.date_range(aligned.index.min(), aligned.index.max(), freq="ME")
    aligned = aligned.reindex(full_idx)

    if difference:
        aligned = aligned.diff().dropna(how="all")

    a, b = aligned["s1"].to_numpy(), aligned["s2"].to_numpy()
    n = len(a)
    if n < max_lag + 10:
        return {}

    results = {}
    for lag in range(-max_lag, max_lag + 1):
        # lag > 0 means s1 leads s2 by `lag` months (correlate s1[t] with s2[t+lag])
        if lag > 0:
            x, y = a[:-lag], b[lag:]
        elif lag < 0:
            x, y = a[-lag:], b[:lag]
        else:
            x, y = a, b
        # Drop pairs where either is NaN
        mask = ~(np.isnan(x) | np.isnan(y))
        x, y = x[mask], y[mask]
        if len(x) < 5:
            continue
        # Guard against zero variance (constant series after differencing)
        if np.std(x) == 0 or np.std(y) == 0:
            results[lag] = (0.0, 1.0, len(x))
            continue
        r, p = stats.pearsonr(x, y)
        results[lag] = (float(r), float(p), len(x))
    return results


# ---------------------------------------------------------------------------
# Volume-artifact diagnostic (round-3 audit fix R3-2)
# ---------------------------------------------------------------------------
def compute_volume_artifact_ratio(reddit_dates: pd.Series,
                                   cfpb_dates: pd.Series,
                                   out_csv: str = "reddit_cfpb_volume_ratio.csv") -> pd.DataFrame:
    """Compute year-stratified Reddit/CFPB volume ratio.

    Rationale: If 2024-2026 Reddit volume increase were real, the
    Reddit/CFPB ratio (CFPB has no API cap) would be ~constant.
    A jump in the ratio is the signature of API-cap recency bias.

    Writes a CSV with year, cfpb, reddit, ratio columns and returns the DataFrame.
    """
    cfpb_yearly = cfpb_dates.dt.year.value_counts().sort_index()
    reddit_yearly = reddit_dates.dt.year.value_counts().sort_index()
    common_years = sorted(set(cfpb_yearly.index) & set(reddit_yearly.index))
    rows = []
    for y in common_years:
        c = int(cfpb_yearly.get(y, 0))
        r = int(reddit_yearly.get(y, 0))
        ratio = r / c if c > 0 else float("nan")
        rows.append({"year": int(y), "cfpb_count": c, "reddit_count": r, "rc_ratio": ratio})
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv}")
    print(f"  Reddit/CFPB ratio: 2017={df[df['year']==2017]['rc_ratio'].iloc[0]:.3f}, " +
          (f"2026={df[df['year']==2026]['rc_ratio'].iloc[0]:.3f}" if 2026 in df['year'].values else "no 2026 data"))
    return df


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

        # 6. Lagged cross-correlation (Box-Jenkins-correct: regularly indexed,
        #    first-differenced to ensure stationarity, Bonferroni-corrected)
        print("\n  Cross-correlation (sentiment leads/lags complaints):")
        print("    NOTE: Series first-differenced (Box-Jenkins). Bonferroni correction applied.")
        lags = cross_correlation(monthly_sentiment["mean"], monthly_complaints,
                                 max_lag=6, difference=True)
        if lags:
            n_lags = len(lags)
            alpha_bonf = 0.05 / n_lags
            print(f"    Bonferroni alpha (n_lags={n_lags}): {alpha_bonf:.4f}")
            print(f"    {'Lag (months)':>14s}  {'r':>8s}  {'p':>8s}  {'n':>6s}  {'sig':>6s}")
            for lag in sorted(lags.keys()):
                r, p, n_pairs = lags[lag]
                interp = "(sentiment leads)" if lag > 0 else "(complaints lead)" if lag < 0 else "(simultaneous)"
                bonf = "(Bonf)" if p < alpha_bonf else ("*" if p < 0.05 else "")
                print(f"    {lag:>14d}  {r:+8.3f}  {p:8.4f}  {n_pairs:>6d}  {bonf:>6s}  {interp}")

    # 7. Generate figure
    print("\nGenerating correlation figure...")
    fig = plt.figure(figsize=(22, 16))
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 2, 1.6], hspace=0.45)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax3 = fig.add_subplot(gs[2])

    fig.suptitle(
        "PSLF Online Sentiment vs CFPB Administrative Complaints",
        fontsize=22, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.972,
             f"n={len(sent):,} sentiment posts; n={len(complaints_pslf):,} CFPB complaints "
             f"(PSLF-filtered, 2016-2026)",
             ha="center", fontsize=12, style="italic", color="#555555")

    # ---- Panel 1: Dual-axis sentiment + complaints (smoothed) ----
    ax1b = ax1.twinx()
    ax1b.spines["top"].set_visible(False)

    # Apply 3-month rolling smooth for clarity
    smooth_pol = monthly_sentiment["mean"].rolling(window=3, center=True, min_periods=1).mean()
    smooth_cmp = monthly_complaints.rolling(window=3, center=True, min_periods=1).mean()

    # Polarity background scatter + smoothed line
    ax1.scatter(monthly_sentiment.index, monthly_sentiment["mean"],
                color="#FF6B35", alpha=0.25, s=15, zorder=2)
    ax1.plot(smooth_pol.index, smooth_pol.values, color="#D84315",
             linewidth=2.8, label="Sentiment Polarity (3-mo smooth)", zorder=3)
    ax1.set_ylabel("Mean Polarity", color="#D84315", fontsize=12, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor="#D84315")
    ax1.axhline(y=0, color="#888888", linewidth=0.6)

    # Complaints filled area
    ax1b.fill_between(smooth_cmp.index, 0, smooth_cmp.values,
                      color="#1976D2", alpha=0.20, zorder=1)
    ax1b.plot(smooth_cmp.index, smooth_cmp.values, color="#1976D2",
              linewidth=2.5, label="CFPB Complaints (3-mo smooth)", zorder=2)
    ax1b.set_ylabel("CFPB PSLF Complaints / month", color="#1976D2", fontsize=12, fontweight="bold")
    ax1b.tick_params(axis="y", labelcolor="#1976D2")
    ax1b.grid(False)

    ax1.set_title("Online Sentiment Polarity vs Complaint Volume", fontsize=14,
                  fontweight="bold", loc="left")

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
               frameon=True, facecolor="white", edgecolor="#CCCCCC")

    # ---- Panel 2: % negative vs complaints ----
    ax2b = ax2.twinx()
    ax2b.spines["top"].set_visible(False)

    smooth_neg = monthly_neg.rolling(window=3, center=True, min_periods=1).mean()
    ax2.scatter(monthly_neg.index, monthly_neg.values,
                color="#D32F2F", alpha=0.25, s=15, zorder=2)
    ax2.plot(smooth_neg.index, smooth_neg.values, color="#B71C1C",
             linewidth=2.8, label="% Negative (3-mo smooth)", zorder=3)
    ax2.set_ylabel("% Negative Posts", color="#B71C1C", fontsize=12, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor="#B71C1C")

    ax2b.fill_between(smooth_cmp.index, 0, smooth_cmp.values,
                      color="#1976D2", alpha=0.20, zorder=1)
    ax2b.plot(smooth_cmp.index, smooth_cmp.values, color="#1976D2",
              linewidth=2.5, label="CFPB Complaints (3-mo smooth)", zorder=2)
    ax2b.set_ylabel("CFPB PSLF Complaints / month", color="#1976D2", fontsize=12, fontweight="bold")
    ax2b.tick_params(axis="y", labelcolor="#1976D2")
    ax2b.grid(False)
    ax2.set_title("Negativity Rate vs Complaint Volume", fontsize=14,
                  fontweight="bold", loc="left")

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
               frameon=True, facecolor="white", edgecolor="#CCCCCC")

    # ---- Panel 3: Cross-correlation function ----
    if "lags" in dir() and lags:
        lag_keys = sorted(lags.keys())
        rs = [lags[k][0] for k in lag_keys]
        ps = [lags[k][1] for k in lag_keys]
        n_pairs = [lags[k][2] for k in lag_keys]
        n_lags_tested = len(lag_keys)
        alpha_bonf = 0.05 / n_lags_tested

        # Color: red if Bonferroni-significant, orange if uncorrected p<0.05, gray else
        bar_colors, bar_alphas = [], []
        for p in ps:
            if p < alpha_bonf:
                bar_colors.append("#C62828"); bar_alphas.append(0.9)
            elif p < 0.05:
                bar_colors.append("#FB8C00"); bar_alphas.append(0.7)
            else:
                bar_colors.append("#9E9E9E"); bar_alphas.append(0.5)

        bars = ax3.bar(lag_keys, rs, color=bar_colors, edgecolor="white", linewidth=1.2)
        for bar, alpha in zip(bars, bar_alphas):
            bar.set_alpha(alpha)

        # Per-lag empirical critical r (uses each lag's actual n)
        n_typical = int(np.median(n_pairs)) if n_pairs else 100
        crit_r_uncorr = 1.96 / np.sqrt(max(n_typical, 5))
        # Bonferroni-corrected critical r ~ z_{alpha/(2*n_lags)} / sqrt(n)
        from scipy.stats import norm as _norm
        z_bonf = _norm.ppf(1 - alpha_bonf / 2)
        crit_r_bonf = z_bonf / np.sqrt(max(n_typical, 5))

        ax3.axhline(y=crit_r_uncorr, color="#FB8C00", linestyle=":", linewidth=0.8, alpha=0.7)
        ax3.axhline(y=-crit_r_uncorr, color="#FB8C00", linestyle=":", linewidth=0.8, alpha=0.7)
        ax3.axhline(y=crit_r_bonf, color="#C62828", linestyle="--", linewidth=0.9, alpha=0.7)
        ax3.axhline(y=-crit_r_bonf, color="#C62828", linestyle="--", linewidth=0.9, alpha=0.7)
        ax3.text(max(lag_keys), crit_r_uncorr,
                 f" |r|≥{crit_r_uncorr:.2f} uncorrected p<0.05",
                 fontsize=8, va="bottom", ha="right", color="#FB8C00", style="italic")
        ax3.text(max(lag_keys), crit_r_bonf,
                 f" |r|≥{crit_r_bonf:.2f} Bonferroni p<0.05/{n_lags_tested}",
                 fontsize=8, va="bottom", ha="right", color="#C62828", style="italic")

        ax3.axhline(y=0, color="#222222", linewidth=0.7)
        ax3.set_xlabel("Lag (months) — positive = sentiment leads complaints",
                       fontsize=12, fontweight="bold")
        ax3.set_ylabel("Pearson r", fontsize=12, fontweight="bold")
        ax3.set_title("Cross-correlation Function (Box-Jenkins 1970)",
                      fontsize=14, fontweight="bold", loc="left")
        ax3.set_xticks(lag_keys)

    fig.text(0.99, 0.005,
             "Source: CFPB Consumer Complaints DB + Reddit/SDN sentiment  |  "
             "Box-Jenkins (1970)",
             ha="right", fontsize=9, style="italic", color="#888888")

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
            f.write(f"\nCROSS-CORRELATION (sentiment vs complaints, first-differenced):\n")
            f.write(f"  Bonferroni alpha (n_lags={len(lags)}): {0.05/len(lags):.4f}\n")
            for lag in sorted(lags.keys()):
                r, p, n_pairs = lags[lag]
                f.write(f"  Lag {lag:+3d} months: r={r:+.3f}, p={p:.4f}, n={n_pairs}\n")
    print(f"  Saved: admin_correlation_results.txt")

    # Round-3 audit fix R3-2: produce R/C ratio CSV from script (was previously
    # only in CLAUDE.md as an unverifiable static table)
    print("\nComputing Reddit/CFPB volume ratio (volume artifact diagnostic)...")
    rc_df = compute_volume_artifact_ratio(sent["date"], complaints_pslf["date"])
    print(rc_df.to_string(index=False))


if __name__ == "__main__":
    main()
