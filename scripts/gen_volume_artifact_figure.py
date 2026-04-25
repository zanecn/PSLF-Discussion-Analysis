"""
gen_volume_artifact_figure.py
==============================
Generates a figure visualizing the Reddit-vs-CFPB volume divergence,
making the API-cap artifact visible to readers.

Output: pslf_volume_artifact.png

Per round-2 audit: the volume curve in pslf_sentiment_legislative_timeline.png
shows ~84x growth, but only ~6.5x is real (per CFPB). This figure shows
the divergence directly.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import filter_pslf_relevant

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "legend.frameon": False,
    "font.family": "DejaVu Sans",
})


def main():
    # Load CFPB
    cfpb = pd.read_csv("admin_data_pslf_complaints.csv")
    cfpb["date"] = pd.to_datetime(cfpb["date"], errors="coerce", utc=True).dt.tz_localize(None)
    cfpb["year"] = cfpb["date"].dt.year

    # Load Reddit
    pf = pd.read_csv("reddit_professions_pslf.csv")
    tm = filter_pslf_relevant(pf["combined_text"])
    tt = filter_pslf_relevant(pf["title"])
    pf = pf[tm | tt].copy()
    pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
    pf["year"] = pf["date"].dt.year

    cfpb_yearly = cfpb.groupby("year").size()
    reddit_yearly = pf.groupby("year").size()

    common_years = sorted(set(cfpb_yearly.index) & set(reddit_yearly.index))
    common_years = [y for y in common_years if 2016 <= y <= 2026]

    cfpb_norm = [cfpb_yearly.get(y, 0) for y in common_years]
    reddit_norm = [reddit_yearly.get(y, 0) for y in common_years]
    ratio = [r / c if c > 0 else 0 for r, c in zip(reddit_norm, cfpb_norm)]

    # ---- Figure ----
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle(
        "Volume Artifact Diagnostic: Reddit vs CFPB Complaints (Real vs API-Cap)",
        fontsize=18, fontweight="bold", y=0.99,
    )
    fig.text(0.5, 0.945,
             "If volume increase were entirely real, Reddit/CFPB ratio (right panel) would be flat. "
             "It explodes 84× — confirming API-cap artifact.",
             ha="center", fontsize=11, style="italic", color="#555555")

    # Panel 1: Side-by-side absolute counts
    ax1 = axes[0]
    width = 0.4
    x = range(len(common_years))
    ax1.bar([i - width/2 for i in x], cfpb_norm, width, label="CFPB Complaints", color="#1976D2", alpha=0.85)
    ax1.bar([i + width/2 for i in x], reddit_norm, width, label="Reddit (scraped)", color="#FF6B35", alpha=0.85)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels([str(y) for y in common_years], rotation=45)
    ax1.set_ylabel("Annual Posts/Complaints", fontsize=12, fontweight="bold")
    ax1.set_title("Absolute Volume by Year", fontsize=13, fontweight="bold", loc="left")
    ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#CCCCCC")

    # Panel 2: Normalized to 2016 (relative growth)
    ax2 = axes[1]
    base_idx = 0  # 2016 baseline
    cfpb_rel = [c / cfpb_norm[base_idx] for c in cfpb_norm] if cfpb_norm[base_idx] else cfpb_norm
    reddit_rel = [r / reddit_norm[base_idx] for r in reddit_norm] if reddit_norm[base_idx] else reddit_norm
    ax2.plot(common_years, cfpb_rel, "o-", color="#1976D2", linewidth=2.5, label="CFPB (real growth)", markersize=7)
    ax2.plot(common_years, reddit_rel, "o-", color="#FF6B35", linewidth=2.5, label="Reddit (scraped)", markersize=7)
    ax2.set_ylabel(f"Relative growth (2016 = 1×)", fontsize=12, fontweight="bold")
    ax2.set_title("Growth Indexed to 2016", fontsize=13, fontweight="bold", loc="left")
    ax2.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#CCCCCC")
    ax2.set_yscale("log")
    ax2.set_xticks(common_years)
    ax2.set_xticklabels([str(y) for y in common_years], rotation=45)

    # Panel 3: Reddit/CFPB ratio (the artifact signature)
    ax3 = axes[2]
    bars = ax3.bar(common_years, ratio, color="#C62828", alpha=0.8, edgecolor="white", linewidth=1.5)
    ax3.set_ylabel("Reddit / CFPB ratio", fontsize=12, fontweight="bold")
    ax3.set_title("Reddit/CFPB Ratio  ⤴︎ = artifact growing", fontsize=13, fontweight="bold", loc="left")
    ax3.set_xticks(common_years)
    ax3.set_xticklabels([str(y) for y in common_years], rotation=45)
    # Annotate dramatic change
    for i, (y, r) in enumerate(zip(common_years, ratio)):
        if r > 0.5:
            ax3.text(y, r + 0.1, f"{r:.2f}", ha="center", fontsize=9, fontweight="bold")
    # Reference line at "constant ratio" expectation (mean of pre-2024)
    pre_2024_mean = sum(r for y, r in zip(common_years, ratio) if y < 2024) / sum(1 for y in common_years if y < 2024)
    ax3.axhline(y=pre_2024_mean, color="#888888", linestyle="--", linewidth=1, label=f"Pre-2024 mean ({pre_2024_mean:.2f})")
    ax3.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#CCCCCC")

    fig.text(0.99, 0.005,
             "Source: CFPB Consumer Complaints Database (no API cap) vs Reddit JSON API (1000-result cap)  |  "
             "Round-2 audit diagnostic",
             ha="right", fontsize=9, style="italic", color="#888888")

    plt.tight_layout(rect=[0, 0.02, 1, 0.92])
    plt.savefig("pslf_volume_artifact.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: pslf_volume_artifact.png")
    print(f"\n2017 R/C ratio: {ratio[common_years.index(2017)]:.3f}" if 2017 in common_years else "")
    if 2026 in common_years:
        print(f"2026 R/C ratio: {ratio[common_years.index(2026)]:.3f}")
        print(f"Ratio increase 2017->2026: {ratio[common_years.index(2026)] / ratio[common_years.index(2017)]:.0f}x")


if __name__ == "__main__":
    main()
