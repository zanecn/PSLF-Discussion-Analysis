"""
generate_p2_figures.py
=======================
R17++ figure generator for Paper 2 (JCSS).

Outputs:
- paper2_fig1_cohort_or_forest.png — cohort heterogeneity OR forest (5 cohorts × 3 specs)
- paper2_fig2_topic_shifts_heatmap.png — per-event topic-shift heatmap
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


def fig1_cohort_or_forest():
    """Cohort OR forest: 5 cohorts × 3 operationalizations (same-scorer + 2 cross-scorer)."""
    # Numbers from MASTER_LOCKED_NUMBERS.md Paper 2 OR table
    # (cohort, n, same_or, same_ci_lo, same_ci_hi, tb_cross_or, tb_ci_lo, tb_ci_hi, va_cross_or, va_ci_lo, va_ci_hi)
    rows = [
        ("SDN-Medical",         1960, 0.272, 0.22, 0.34, 0.147, 0.10, 0.22, 0.334, 0.26, 0.43),
        ("Reddit r/PSLF",       1469, 7.329, 4.20, 12.78, 1.655, 0.97, 2.83, 2.526, 1.53, 4.18),
        ("Reddit Finance",       999, 0.182, 0.11, 0.30, 1.103, 0.33, 3.66, 1.423, 0.72, 2.82),
        ("Reddit r/StudentLoans", 969, 1.411, 0.85, 2.34, 2.495, 0.99, 6.28, 0.990, 0.56, 1.74),
        ("Reddit Medical",       566, 0.726, 0.33, 1.61, 1.191, 0.40, 3.54, 0.841, 0.35, 2.03),
    ]
    df = pd.DataFrame(rows, columns=["cohort", "n", "same_or", "same_lo", "same_hi",
                                       "tb_or", "tb_lo", "tb_hi", "va_or", "va_lo", "va_hi"])

    fig, ax = plt.subplots(figsize=(12, 7))
    # Log scale for OR (interpretable on log scale)
    ax.set_xscale("log")

    # 3 markers per cohort, offset vertically
    y_base = np.arange(len(df))[::-1] * 1.0
    offset = 0.25
    color_map = {"same": "tab:blue", "tb": "tab:orange", "va": "tab:green"}

    for i, row in df.iterrows():
        yp = y_base[i]
        # Same-scorer (Claude × Claude)
        ax.plot([row["same_lo"], row["same_hi"]], [yp + offset, yp + offset], color=color_map["same"], linewidth=2)
        ax.scatter(row["same_or"], yp + offset, color=color_map["same"], s=70, zorder=5)
        # TB cross-scorer
        ax.plot([row["tb_lo"], row["tb_hi"]], [yp, yp], color=color_map["tb"], linewidth=2)
        ax.scatter(row["tb_or"], yp, color=color_map["tb"], s=70, zorder=5)
        # VADER cross-scorer
        ax.plot([row["va_lo"], row["va_hi"]], [yp - offset, yp - offset], color=color_map["va"], linewidth=2)
        ax.scatter(row["va_or"], yp - offset, color=color_map["va"], s=70, zorder=5)

    ax.axvline(1.0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_yticks(y_base)
    ax.set_yticklabels([f"{row['cohort']}\n(n={row['n']:,})" for _, row in df.iterrows()], fontsize=10)
    ax.set_xlabel("Odds Ratio: P(pursuing | negative-sentiment) / P(pursuing | non-negative) (log scale)", fontsize=10)
    ax.set_xlim(0.04, 18)
    ax.set_title(
        "Paper 2 Figure 1: Cohort-conditional sentiment-stance coupling\n"
        "(R17++ canonical; 5 cohorts × 3 operationalizations)",
        fontsize=12)

    # Legend
    legend_handles = [
        mpatches.Patch(color=color_map["same"], label="Same-scorer: Claude-neg × Claude-pursuing"),
        mpatches.Patch(color=color_map["tb"], label="Cross-scorer: TB-neg × Claude-pursuing"),
        mpatches.Patch(color=color_map["va"], label="Cross-scorer: VADER-neg × Claude-pursuing"),
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=9)

    # Annotations
    ax.text(0.05, y_base[0] + offset, "SDN-Medical: 5/5 specs OR<1 (cross-instrument concordant decoupling)",
            ha="left", va="center", fontsize=8, color="tab:blue", style="italic")
    ax.text(0.05, y_base[2] + offset, "Reddit Finance: same-scorer OR=0.18 flips to OR=1.10–1.42 cross-scorer\n(construct-misalignment exemplar)",
            ha="left", va="center", fontsize=8, color="tab:orange", style="italic")
    ax.text(15, y_base[1] + offset, "r/PSLF: 4/5 specs OR>1 (coupling)",
            ha="right", va="center", fontsize=8, color="tab:blue", style="italic")

    fig.text(0.02, 0.02,
             "Note: R17++ post-level scope (R17 Option A). SDN-Medical is the only cohort with full cross-instrument concordance. "
             "Reddit Finance is the construct-misalignment exemplar: same-scorer 'decoupling' OR=0.18 flips to 'coupling' OR=1.10–1.42 "
             "with cross-scorer operationalization. r/PSLF 'coupling' holds under 4 of 5 specs; the 1 spec flip (Claude-pur-or-completed) "
             "is mechanically driven by low base rate of 'completed' stance.",
             fontsize=8, style="italic", wrap=True)

    plt.tight_layout(rect=[0, 0.06, 1, 1])
    out_path = PROJECT / "paper2_fig1_cohort_or_forest.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def fig2_topic_shifts_heatmap():
    """Per-event Cramér's V heatmap with significance overlay."""
    # Numbers from MASTER_LOCKED_NUMBERS.md Paper 2 per-event topic restructuring table
    # 8 events × 1 metric (Cramér's V); annotate p<10⁻⁴ vs NS
    events = [
        ("IDR Account Adjustment",     234, 179, 0.42, "<0.0001", True),
        ("Limited PSLF Waiver",        422, 314, 0.31, "<0.0001", True),
        ("Biden Mass Forgiveness",     198, 305, 0.28, "<0.0001", True),
        ("SAVE Admin Forbearance",     203, 168, 0.27, "0.0003",  True),
        ("Biden v. Nebraska SCOTUS",   466, 417, 0.24, "0.4435",  False),
        ("Payments Restart",           376, 391, 0.22, "0.3665",  False),
        ("Trump PSLF EO",              661, 524, 0.21, "0.0071",  True),
        ("Final Trump PSLF Rule",      152, 218, 0.18, "<0.0001", True),
    ]
    df = pd.DataFrame(events, columns=["event", "n_pre", "n_post", "cramers_v", "p_chi2", "significant"])

    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(df))[::-1]
    colors = ["tab:blue" if s else "lightgrey" for s in df["significant"]]
    bars = ax.barh(y, df["cramers_v"], color=colors, edgecolor="black", linewidth=0.6)

    # Annotate each bar
    for i, (yp, row) in enumerate(zip(y, df.itertuples(index=False))):
        ax.text(row.cramers_v + 0.01, yp,
                f"V={row.cramers_v:.2f}, p={row.p_chi2}, n_pre={row.n_pre}, n_post={row.n_post}",
                va="center", fontsize=9)

    # Effect-size thresholds (Cohen for Cramér's V at df=6: 0.05 small, 0.17 medium, 0.29 large)
    for thresh, label, color in [(0.05, "small", "grey"), (0.17, "medium", "tab:orange"), (0.29, "large", "tab:red")]:
        ax.axvline(thresh, color=color, linestyle="--", linewidth=0.8, alpha=0.6)
        ax.text(thresh, len(df) - 0.3, label, ha="center", fontsize=8, color=color)

    ax.set_yticks(y)
    ax.set_yticklabels(df["event"], fontsize=10)
    ax.set_xlabel("Cramér's V (5-stance × 2-window chi-sq family)", fontsize=11)
    ax.set_xlim(0, 0.65)
    ax.set_title(
        "Paper 2 Figure 2: Per-event stance-distribution shift magnitudes (Cramér's V)\n"
        "R17 corrected: 6 of 8 events significant after Holm-Bonferroni at family-wise α=0.05",
        fontsize=12)

    legend_handles = [
        mpatches.Patch(color="tab:blue", label="Significant after Holm-Bonferroni (α_family=0.05)"),
        mpatches.Patch(color="lightgrey", label="Not significant"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9)

    fig.text(0.02, 0.02,
             "Note: R17 audit caught earlier 'all 8 events p<10⁻⁴' claim was FALSE: Biden v. Nebraska SCOTUS p=0.44 NS, Payments Restart p=0.37 NS. "
             "R17++ Agent 5 M5 formally verified via Holm-Bonferroni step-down (thresholds α/(m−rank+1) = 0.00625, 0.00714, ..., 0.05); "
             "6 of 8 events remain significant after family-wise correction; same conclusion as raw-p comparison. Topic restructuring is robust to "
             "instrument choice but NOT composition-immune (topic mix shift coupled with poster turnover; R17 retraction of composition-immune claim).",
             fontsize=8, style="italic", wrap=True)

    plt.tight_layout(rect=[0, 0.07, 1, 1])
    out_path = PROJECT / "paper2_fig2_topic_shifts_heatmap.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    fig1_cohort_or_forest()
    fig2_topic_shifts_heatmap()
    print("\nPaper 2 figures complete.")
