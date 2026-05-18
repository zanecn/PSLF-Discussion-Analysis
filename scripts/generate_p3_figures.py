"""
generate_p3_figures.py
=======================
R17++ figure generator for Paper 3 (JGME).

Outputs:
- paper3_fig1_year_by_year_gap.png — year-by-year PSLF-hostile vs PSLF-friendly
  fill-rate gap 2016–2026 with sample-size annotations
- paper3_fig2_forest_plot.png — forest plot of S1/S2/S3 PSLF-hostile β with
  negative controls (orthopedic + dermatology)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")
plt.rcParams.update({"font.size": 11, "figure.dpi": 300, "savefig.dpi": 300})


def fig1_year_by_year():
    """Year-by-year fill-rate gap PSLF-hostile vs PSLF-friendly 2016–2026."""
    # Numbers from MASTER_LOCKED_NUMBERS.md Paper 3 year-by-year table
    data = pd.DataFrame({
        "year": [2016, 2017, 2020, 2021, 2022, 2023, 2024, 2025, 2026],
        "n_friendly": [2190, 2437, 2269, 3353, 3451, 3518, 3597, 3677, 3887],
        "n_hostile": [6, 8, 54, 129, 149, 159, 159, 167, 171],
        "fill_friendly": [0.9408, 0.9377, 0.9355, 0.9394, 0.9415, 0.9346, 0.9397, 0.9404, 0.9348],
        "fill_hostile": [0.7900, 0.9250, 0.7793, 0.7994, 0.7767, 0.8028, 0.8326, 0.8356, 0.8645],
    })
    data["gap_pp"] = (data["fill_hostile"] - data["fill_friendly"]) * 100
    data["adequate_n"] = data["n_hostile"] >= 20  # 2016+2017 below threshold

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_xlabel("Match year", fontsize=12)
    ax1.set_ylabel("Fill-rate gap (PSLF-hostile − PSLF-friendly, pp)", fontsize=12, color="tab:red")

    # Bars: gap (adequate-n colored red; insufficient-n grey)
    bar_colors = ["lightgrey" if not a else "tab:red" for a in data["adequate_n"]]
    bars = ax1.bar(data["year"], data["gap_pp"], color=bar_colors, edgecolor="black", linewidth=0.6, alpha=0.85)
    ax1.axhline(0, color="black", linewidth=0.8)
    ax1.set_ylim(-20, 5)
    ax1.tick_params(axis="y", labelcolor="tab:red")

    # Annotate gap value above/below each bar
    for i, row in data.iterrows():
        y_offset = -1.5 if row["gap_pp"] < 0 else 0.5
        ax1.annotate(f"{row['gap_pp']:+.1f}", xy=(row["year"], row["gap_pp"]),
                     ha="center", va="top" if row["gap_pp"] < 0 else "bottom",
                     fontsize=9, xytext=(0, y_offset), textcoords="offset points")

    # Secondary axis: n_hostile counts
    ax2 = ax1.twinx()
    ax2.set_ylabel("n_hostile (PSLF-hostile program-years)", fontsize=11, color="tab:blue")
    ax2.plot(data["year"], data["n_hostile"], "o-", color="tab:blue", markersize=7, linewidth=1.5)
    for _, row in data.iterrows():
        ax2.annotate(f"n={row['n_hostile']}", xy=(row["year"], row["n_hostile"]),
                     xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color="tab:blue")
    ax2.tick_params(axis="y", labelcolor="tab:blue")
    ax2.set_ylim(0, 220)

    # Title + legend
    ax1.set_title(
        "Paper 3 Figure 1: PSLF-eligibility fill-rate gap by year, 2016–2026\n"
        "(NRMP Main Match; ProPublica IRS-verified institution classification)",
        fontsize=13)
    grey_patch = mpatches.Patch(color="lightgrey", label="n_hostile < 20 (insufficient)")
    red_patch = mpatches.Patch(color="tab:red", alpha=0.85, label="n_hostile ≥ 20 (adequate)")
    blue_line = plt.Line2D([0], [0], color="tab:blue", marker="o", label="n_hostile (right axis)")
    ax1.legend(handles=[red_patch, grey_patch, blue_line], loc="lower right", fontsize=9)

    # Caption text
    fig.text(0.02, 0.02,
             "Note: 2016–2017 omitted from inferential analyses (n_hostile ≤ 8). "
             "2026 = first post-Trump-EO Match cycle. Trend regression shows "
             "is_2026 indicator beyond linear trend = +3.0 pp NS (95% CI [−4.96, +10.92]) — "
             "design lacks power to identify EO discontinuity.",
             fontsize=8, style="italic")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out_path = PROJECT / "paper3_fig1_year_by_year_gap.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def fig2_forest_plot():
    """Forest plot: S1/S2/S3 PSLF-hostile β + negative controls (orthopedic + dermatology)."""
    # All numbers from MASTER_LOCKED_NUMBERS.md Paper 3 section (R17 dedup-corrected)
    rows = [
        # (label, beta_pp, ci_lo, ci_hi, p_value, n_hostile_rows, group)
        ("S1: All 23 hostile (5-yr 2021–2025)",       -18.07, -24.80, -11.35, "<0.0005", 763, "main"),
        ("S2: HCA-academic reclassified (5-yr)",      -16.25, -21.66, -10.83, "0.017",   358, "main"),
        ("S3: HCA-academic dropped (5-yr)",           -17.14, -22.48, -11.80, "0.006",   358, "main"),
        ("M5 + state-filtered NIH (5-yr)",            -18.07, -21.28, -14.87, "2.1×10⁻²⁸", 763, "main"),
        ("S1: 6-year pooled (2021–2026)",             -16.31, -22.49, -10.14, "—",       645, "trajectory"),
        ("S2: 6-year pooled (2021–2026)",             -13.68, -18.36,  -9.01, "—",       165, "trajectory"),
        ("S3: 6-year pooled (2021–2026)",             -14.50, -19.15,  -9.84, "—",       165, "trajectory"),
        ("NEG CTL: Orthopedic surgery (5-yr)",         +0.67,  -0.66,  +2.00, "0.33 NS",  11, "negctl"),
        ("NEG CTL: Orthopedic surgery (6-yr)",         +0.54,  -0.53,  +1.60, "0.32 NS",  16, "negctl"),
        ("NEG CTL: Dermatology (5-yr, R17++)",         -7.20, -16.92,  +2.52, "0.147 NS", 27, "negctl"),
        ("NEG CTL: Dermatology (6-yr, R17++)",         -6.28, -14.57,  +2.01, "0.138 NS", 33, "negctl"),
    ]
    df = pd.DataFrame(rows, columns=["label", "beta", "ci_lo", "ci_hi", "p", "n_h", "group"])

    fig, ax = plt.subplots(figsize=(11, 7))
    y_pos = np.arange(len(df))[::-1]  # top to bottom

    color_map = {"main": "tab:blue", "trajectory": "tab:cyan", "negctl": "tab:orange"}
    colors = [color_map[g] for g in df["group"]]

    # Forest plot
    for i, (yp, row) in enumerate(zip(y_pos, df.itertuples(index=False))):
        ax.plot([row.ci_lo, row.ci_hi], [yp, yp], color=colors[i], linewidth=2)
        ax.scatter(row.beta, yp, color=colors[i], s=80, zorder=5)
        # Annotate beta + p
        x_text = row.ci_hi + 0.6
        ax.text(x_text, yp, f"β={row.beta:+.2f}, p={row.p}, n_h={row.n_h}",
                va="center", fontsize=9)

    # Zero line + labels
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df["label"], fontsize=10)
    ax.set_xlabel("PSLF-hostile coefficient (percentage points)", fontsize=11)
    ax.set_xlim(-28, 14)
    ax.set_title(
        "Paper 3 Figure 2: PSLF-hostile fill-rate differential — forest plot across\n"
        "specifications + negative controls (R17 dedup-corrected; R17++ dermatology added)",
        fontsize=12)

    # Legend
    legend_patches = [
        mpatches.Patch(color="tab:blue", label="Main 5-year specifications (S1/S2/S3 + M5+NIH)"),
        mpatches.Patch(color="tab:cyan", label="6-year pooled specifications (trajectory)"),
        mpatches.Patch(color="tab:orange", label="Negative controls (orthopedic + dermatology)"),
    ]
    ax.legend(handles=legend_patches, loc="upper right", fontsize=9)

    # Caption
    fig.text(0.02, 0.02,
             "Note: 5-year baseline (n=29,349) is the headline cross-sectional sample. 6-year sample (n=35,193 post-OLS) shows "
             "narrowing pulled by 2026 narrowing. NIH funding does NOT absorb PSLF effect (M5 → M5+NIH shift only +0.17 pp). "
             "Orthopedic surgery is the cleanest negative control (clean null); dermatology shows β=−6 to −7 pp NS — point "
             "estimate notably negative but power-limited (admits both null AND substantial differential).",
             fontsize=8, style="italic", wrap=True)

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    out_path = PROJECT / "paper3_fig2_forest_plot.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    fig1_year_by_year()
    fig2_forest_plot()
    print("\nPaper 3 figures complete.")
