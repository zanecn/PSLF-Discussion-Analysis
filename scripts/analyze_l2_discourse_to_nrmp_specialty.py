"""
analyze_l2_discourse_to_nrmp_specialty.py
===========================================
L2: Test whether SDN-Medical sentiment about a specialty (year-1) predicts
NRMP fill rates for that specialty (year). The cleanest discourse-to-behavior
linking analysis given existing data.

Method:
  1. For each (year, specialty) cell, extract SDN-Medical posts mentioning
     that specialty (keyword match on body)
  2. Compute mean polarity of those posts
  3. For each (year, specialty), look up NRMP fill rate (from B5 dataset)
  4. Test: does mean SDN sentiment(year-1, specialty) predict NRMP fill(year, specialty)?
  5. Also: does sentiment(year, specialty) correlate with fill(year, specialty)?

Output: l2_discourse_nrmp_results.{txt,csv}
        l2_discourse_nrmp_figure.png
"""
from __future__ import annotations
import io, os, sys, warnings, re
from datetime import datetime
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pslf_search_terms import filter_pslf_relevant

OUT_TXT = "l2_discourse_nrmp_results.txt"
OUT_CSV = "l2_discourse_nrmp_results.csv"
OUT_PNG = "l2_discourse_nrmp_figure.png"

# Specialty keyword patterns (matched on SDN body / thread title)
SPECIALTY_KEYWORDS = {
    "Family Medicine": [r"\bfamily med", r"\bFM(?:\s|\b)", r"\bfamily practice"],
    "Internal Medicine": [r"\binternal med", r"\bIM(?:\s|\b)", r"\binternist"],
    "Pediatrics": [r"\bpedi", r"\bpeds(?:\s|\b)", r"\bchildren\W*hosp"],
    "Dermatology": [r"\bderm(?:atolog)?(?:\s|\b)"],
    "Emergency Medicine": [r"\bemergency med", r"\bER(?:\s|\b)", r"\bEM(?:\s|\b|\.)", r"\bemerg"],
    "Psychiatry": [r"\bpsych(?:iatr)?(?:\s|\b)"],
    "Anesthesiology": [r"\banesth(?:esia)?", r"\bgas(?:\s|\b)"],
    "Surgery-General": [r"\bgen surg", r"\bgeneral surgery", r"\bGS(?:\s|\b)"],
    "Radiology-Diagnostic": [r"\bradiology", r"\brads(?:\s|\b)", r"\bdiag rad"],
    "Pathology": [r"\bpath(?:ology)?(?:\s|\b)", r"\bpathologist"],
    "Neurology": [r"\bneuro(?:\s|\b)", r"\bneurology"],
    "Obstetrics-Gynecology": [r"\bOB[\W]?GYN", r"\bobstetric", r"\bgyn", r"\bobgyn"],
    "Orthopaedic Surgery": [r"\borthop", r"\bortho(?:\s|\b)", r"\bortho surg"],
}


def main():
    print("=" * 80)
    print("L2: Discourse -> NRMP fill rates (specialty-year cells)")
    print("=" * 80)

    # Load NRMP data (specialty x year, average across institutions weighted by quota)
    if not os.path.exists("nrmp_program_level_2021_2025.csv"):
        print("[ABORT] nrmp_program_level_2021_2025.csv not found")
        return
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate"])
    print(f"\nNRMP rows: {len(nrmp):,}")

    nrmp_agg = (nrmp.groupby(["specialty", "year"])
                  .apply(lambda g: pd.Series({
                      "fill_rate": (g["filled"].sum() / g["quota"].sum()
                                     if g["quota"].sum() > 0 else float("nan")),
                      "n_programs": g["program_code"].nunique(),
                      "total_quota": g["quota"].sum(),
                  })).reset_index())
    print(f"Specialty-year cells: {len(nrmp_agg)}")

    # Load SDN posts
    print("\nLoading SDN posts...")
    sdn = pd.read_csv("forum_pslf_discussions.csv", low_memory=False)
    bm = filter_pslf_relevant(sdn["body"].fillna(""))
    ttm = filter_pslf_relevant(sdn["thread_title"].fillna(""))
    sdn = sdn[bm | ttm].copy()
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn = sdn.dropna(subset=["date", "polarity"])
    sdn["year"] = sdn["date"].dt.year
    sdn = sdn[(sdn["year"] >= 2018) & (sdn["year"] <= 2025)]
    print(f"SDN PSLF posts after filter: {len(sdn):,}")

    # Tag each post with mentioned specialties
    sdn["text"] = (sdn["body"].fillna("") + " " + sdn["thread_title"].fillna(""))
    print("\nTagging specialties...")
    for sp, kws in SPECIALTY_KEYWORDS.items():
        pattern = "|".join(kws)
        sdn[f"mention_{sp}"] = sdn["text"].str.contains(pattern, case=False, regex=True, na=False)

    # Build year x specialty sentiment table
    print("\nComputing per-(year, specialty) mean polarity...")
    cells = []
    for sp in SPECIALTY_KEYWORDS:
        sub = sdn[sdn[f"mention_{sp}"]]
        for yr in sorted(sub["year"].unique()):
            yr_sub = sub[sub["year"] == yr]
            if len(yr_sub) < 10: continue
            cells.append({
                "specialty": sp, "year": int(yr),
                "n_sdn_posts": len(yr_sub),
                "sdn_mean_polarity": float(yr_sub["polarity"].mean()),
                "sdn_sd_polarity": float(yr_sub["polarity"].std()),
                "sdn_pct_negative": float((yr_sub["polarity"] < -0.05).mean()),
            })
    sdn_cells = pd.DataFrame(cells)
    print(f"  Specialty-year sentiment cells (n>=10): {len(sdn_cells)}")

    # Merge with NRMP
    merged = sdn_cells.merge(nrmp_agg, on=["specialty", "year"], how="inner")
    print(f"\nMerged cells: {len(merged)}")

    # Test: contemporaneous correlation
    print("\n[A] CONTEMPORANEOUS: SDN sentiment(year, sp) vs NRMP fill(year, sp)")
    if len(merged) >= 10:
        r, p = stats.pearsonr(merged["sdn_mean_polarity"], merged["fill_rate"])
        sr, sp_p = stats.spearmanr(merged["sdn_mean_polarity"], merged["fill_rate"])
        print(f"  Pearson r={r:+.3f}, p={p:.4g}, n={len(merged)}")
        print(f"  Spearman rho={sr:+.3f}, p={sp_p:.4g}")

    # Test: lagged (year-1 sentiment -> year fill)
    print("\n[B] LAGGED: SDN sentiment(year-1, sp) vs NRMP fill(year, sp)")
    sdn_lag = sdn_cells.copy()
    sdn_lag["year"] = sdn_lag["year"] + 1
    sdn_lag = sdn_lag.rename(columns={
        "sdn_mean_polarity": "sdn_mean_polarity_lag1",
        "n_sdn_posts": "n_sdn_posts_lag1",
        "sdn_pct_negative": "sdn_pct_negative_lag1",
    })
    merged_lag = sdn_lag[["specialty", "year", "sdn_mean_polarity_lag1",
                            "n_sdn_posts_lag1", "sdn_pct_negative_lag1"]].merge(
        nrmp_agg, on=["specialty", "year"], how="inner")
    print(f"  Lagged cells: {len(merged_lag)}")
    if len(merged_lag) >= 10:
        r, p = stats.pearsonr(merged_lag["sdn_mean_polarity_lag1"], merged_lag["fill_rate"])
        sr, sp_p = stats.spearmanr(merged_lag["sdn_mean_polarity_lag1"], merged_lag["fill_rate"])
        print(f"  Pearson r={r:+.3f}, p={p:.4g}")
        print(f"  Spearman rho={sr:+.3f}, p={sp_p:.4g}")

    # Per-specialty year-over-year change correlation
    print("\n[C] FIRST-DIFFERENCE: ΔSDN sentiment vs ΔNRMP fill (within specialty)")
    deltas = []
    for sp in merged["specialty"].unique():
        sub = merged[merged["specialty"] == sp].sort_values("year")
        if len(sub) < 2: continue
        sub["d_sentiment"] = sub["sdn_mean_polarity"].diff()
        sub["d_fill"] = sub["fill_rate"].diff()
        for _, r in sub.iterrows():
            if not (np.isnan(r["d_sentiment"]) or np.isnan(r["d_fill"])):
                deltas.append({"specialty": sp, "year": r["year"],
                                "d_sentiment": r["d_sentiment"], "d_fill": r["d_fill"]})
    delta_df = pd.DataFrame(deltas)
    if len(delta_df) >= 10:
        r, p = stats.pearsonr(delta_df["d_sentiment"], delta_df["d_fill"])
        print(f"  Δ-Δ Pearson r={r:+.3f}, p={p:.4g}, n={len(delta_df)}")

    # Save
    merged.to_csv(OUT_CSV, index=False, float_format="%.5f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("L2: DISCOURSE -> NRMP FILL RATES\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"SDN PSLF posts in 2018-2025: {len(sdn):,}\n")
        f.write(f"NRMP specialty-year cells (2021-2025): {len(nrmp_agg)}\n")
        f.write(f"Merged sentiment×fill cells: {len(merged)}\n\n")

        f.write("CONTEMPORANEOUS CORRELATIONS\n")
        f.write("-" * 80 + "\n")
        if len(merged) >= 10:
            r, p = stats.pearsonr(merged["sdn_mean_polarity"], merged["fill_rate"])
            sr, sp_p = stats.spearmanr(merged["sdn_mean_polarity"], merged["fill_rate"])
            f.write(f"  Pearson r={r:+.3f}, p={p:.4g}, n={len(merged)}\n")
            f.write(f"  Spearman rho={sr:+.3f}, p={sp_p:.4g}\n")

        f.write("\nLAGGED CORRELATION (year-1 sentiment -> year fill)\n")
        f.write("-" * 80 + "\n")
        if len(merged_lag) >= 10:
            r, p = stats.pearsonr(merged_lag["sdn_mean_polarity_lag1"], merged_lag["fill_rate"])
            f.write(f"  Pearson r={r:+.3f}, p={p:.4g}, n={len(merged_lag)}\n")

        f.write("\nFIRST-DIFFERENCE (within-specialty year-over-year)\n")
        f.write("-" * 80 + "\n")
        if len(delta_df) >= 10:
            r, p = stats.pearsonr(delta_df["d_sentiment"], delta_df["d_fill"])
            f.write(f"  Δ-Δ r={r:+.3f}, p={p:.4g}, n={len(delta_df)}\n")

        f.write("\nPER-SPECIALTY YEAR-OVER-YEAR (descriptive)\n")
        f.write("-" * 80 + "\n")
        for sp in merged["specialty"].unique():
            sub = merged[merged["specialty"] == sp].sort_values("year")
            if len(sub) < 2: continue
            f.write(f"\n  {sp}:\n")
            for _, r in sub.iterrows():
                f.write(f"    {int(r['year'])}: n_sdn={int(r['n_sdn_posts']):>4} "
                        f"polar={r['sdn_mean_polarity']:+.3f}  "
                        f"fill={r['fill_rate']*100:5.1f}%  ({int(r['n_programs'])} programs)\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    if len(merged) >= 10:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        ax = axes[0]
        ax.scatter(merged["sdn_mean_polarity"], merged["fill_rate"],
                    s=merged["n_sdn_posts"]/2, alpha=0.6)
        for _, r in merged.iterrows():
            ax.annotate(f"{r['specialty'][:8]} {int(r['year'])}",
                         (r["sdn_mean_polarity"], r["fill_rate"]),
                         fontsize=7, alpha=0.6)
        r, p = stats.pearsonr(merged["sdn_mean_polarity"], merged["fill_rate"])
        ax.set_xlabel("SDN-Medical mean polarity (PSLF posts mentioning specialty)")
        ax.set_ylabel("NRMP fill rate")
        ax.set_title(f"(a) Contemporaneous: r={r:+.3f}, p={p:.3g}, n={len(merged)}")
        ax.grid(alpha=0.3)

        ax = axes[1]
        if len(merged_lag) >= 10:
            ax.scatter(merged_lag["sdn_mean_polarity_lag1"], merged_lag["fill_rate"],
                        s=merged_lag["n_sdn_posts_lag1"]/2, alpha=0.6)
            r, p = stats.pearsonr(merged_lag["sdn_mean_polarity_lag1"], merged_lag["fill_rate"])
            ax.set_xlabel("SDN polarity (year-1)")
            ax.set_ylabel("NRMP fill (year)")
            ax.set_title(f"(b) Lagged: r={r:+.3f}, p={p:.3g}, n={len(merged_lag)}")
            ax.grid(alpha=0.3)

        plt.tight_layout()
        plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
        print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
