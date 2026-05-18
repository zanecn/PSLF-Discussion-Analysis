"""
generate_p1_figures.py
=======================
R17++ figure generator for Paper 1 (EPJ Data Science).

Outputs:
- paper1_fig1_correlation_matrix.png — 5x5 instrument correlation matrix with
  within-class vs across-class coloring
- paper1_fig2_op_vs_reply_forest.png — OP-vs-Reply Δ by cohort with magnitude bars
- paper1_fig3_cohort_alpha.png — cohort-stratified 3-LLM K-α with 0.667 and
  0.80 Krippendorff floors annotated
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")
plt.rcParams.update({"font.size": 11, "figure.dpi": 300, "savefig.dpi": 300})


def fig1_correlation_matrix():
    """5x5 instrument correlation matrix colored by within/across class."""
    # Pearson r values from PAPER_1_LOCKED_RESULTS_FINAL.md (combined Reddit+SDN n=1,001)
    instruments = ["Claude", "Llama", "DeepSeek", "TextBlob", "VADER"]
    corr = np.array([
        [1.000, 0.737, 0.785, 0.021, 0.089],
        [0.737, 1.000, 0.811, 0.092, 0.247],
        [0.785, 0.811, 1.000, 0.028, 0.194],
        [0.021, 0.092, 0.028, 1.000, 0.333],
        [0.089, 0.247, 0.194, 0.333, 1.000],
    ])

    # Class membership: LLM (Claude, Llama, DeepSeek) vs Lexical (TextBlob, VADER)
    is_llm = [True, True, True, False, False]

    fig, ax = plt.subplots(figsize=(8.5, 7))
    cmap = LinearSegmentedColormap.from_list("custom", ["white", "tab:blue"], N=256)
    im = ax.imshow(corr, cmap=cmap, vmin=0, vmax=1.0, aspect="equal")

    # Annotate cells with r values + bold border for within-class pairs
    for i in range(5):
        for j in range(5):
            r = corr[i, j]
            color = "white" if r > 0.55 else "black"
            text = f"{r:+.3f}" if i != j else "—"
            ax.text(j, i, text, ha="center", va="center", color=color, fontsize=11,
                    fontweight="bold" if i != j and is_llm[i] == is_llm[j] else "normal")

    # Class-block borders (3x3 LLM block top-left; 2x2 lexical block bottom-right)
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((-0.5, -0.5), 3, 3, fill=False, edgecolor="tab:green", linewidth=3))
    ax.add_patch(Rectangle((2.5, 2.5), 2, 2, fill=False, edgecolor="tab:orange", linewidth=3))

    ax.set_xticks(range(5))
    ax.set_yticks(range(5))
    ax.set_xticklabels(instruments, fontsize=11)
    ax.set_yticklabels(instruments, fontsize=11)
    ax.set_title(
        "Paper 1 Figure 1: 5-instrument pairwise correlation matrix (Pearson r)\n"
        "5-instrument intersection n=1,001 (combined Reddit + SDN)",
        fontsize=12)
    plt.colorbar(im, ax=ax, label="Pearson r (bold = within-class pair)")

    # Legend
    green_patch = mpatches.Patch(color="none", ec="tab:green", linewidth=2, label="LLM-class (Claude, Llama, DeepSeek)")
    orange_patch = mpatches.Patch(color="none", ec="tab:orange", linewidth=2, label="Lexical-class (TextBlob, VADER)")
    ax.legend(handles=[green_patch, orange_patch], loc="upper center",
              bbox_to_anchor=(0.5, -0.08), fontsize=10, ncol=2)

    fig.text(0.02, 0.02,
             "Note: All inter-LLM r ≥ 0.737; all LLM-vs-lexical r ≤ 0.247. Within-LLM mean r=0.778; "
             "within-Lexical r=0.333; across-class mean r=0.114. Asymmetric construct boundary "
             "between LLM-class and lexical-class.",
             fontsize=8, style="italic")

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out_path = PROJECT / "paper1_fig1_correlation_matrix.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def fig2_op_vs_reply_forest():
    """OP-vs-Reply Δ by cohort: TB (always negative) vs VADER (always positive)."""
    # Per-cohort numbers from MASTER_LOCKED_NUMBERS.md Paper 1 OP-vs-Reply per-cohort table
    cohorts = [
        ("Reddit r/PSLF",        10645, -0.0121, +0.2214),
        ("Reddit r/StudentLoans", 6965, -0.0144, +0.2499),
        ("Reddit Finance",        1968, -0.0247, +0.3021),
        ("Reddit Medical",         668, -0.0255, +0.2061),
        ("Other",                  608, -0.0148, +0.2040),
        ("Reddit PA",              268, -0.0241, +0.3170),
        ("Reddit Teaching",        211, -0.0067, +0.2384),
        ("Reddit Nursing",         120, -0.0081, +0.2581),
    ]
    df = pd.DataFrame(cohorts, columns=["cohort", "n_posts", "tb_delta", "vader_delta"])

    fig, ax = plt.subplots(figsize=(11, 6.5))
    y = np.arange(len(df))[::-1]

    # TB and VADER markers
    ax.scatter(df["tb_delta"], y, color="tab:red", marker="o", s=120, label="TextBlob Δ (OP − reply)", zorder=5)
    ax.scatter(df["vader_delta"], y, color="tab:blue", marker="s", s=120, label="VADER Δ (OP − reply)", zorder=5)

    # Connector lines from 0 to each marker to highlight magnitudes
    for i, row in df.iterrows():
        yp = y[i]
        ax.plot([0, row["tb_delta"]], [yp, yp], color="tab:red", linewidth=2, alpha=0.5)
        ax.plot([0, row["vader_delta"]], [yp, yp], color="tab:blue", linewidth=2, alpha=0.5)
        # n_posts annotation
        ax.text(0.34, yp, f"n_posts={row['n_posts']:,}", va="center", fontsize=9, color="grey")

    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(df["cohort"], fontsize=10)
    ax.set_xlabel("Δ (OP polarity − reply polarity)", fontsize=11)
    ax.set_xlim(-0.05, 0.42)
    ax.set_title(
        "Paper 1 Figure 2: OP-vs-Reply directional mismatch — TextBlob vs VADER\n"
        "Same threads, same cohorts, opposite directions (8/8 cohorts)",
        fontsize=12)
    ax.legend(loc="lower right", fontsize=10)

    # Overall headline
    fig.text(0.50, 0.93,
             "Overall: TB Δ=−0.0146 (t=−15.10, p=2.8×10⁻⁵¹) · VADER Δ=+0.2387 (t=+60.40, p≈0) · "
             "magnitude split ~16×",
             ha="center", fontsize=10, style="italic")

    fig.text(0.02, 0.02,
             "Note: Inference is 1-sample t-test on per-post mean differences (n=21,453 OPs from 506,639 comments; mean 23.6 comments/post). "
             "Earlier 'cluster-bootstrap p≈0' framing was a misstatement (Round 17++ corrected); proper cluster-bootstrap on "
             "(post, comment) pairs is recommended for the published version.",
             fontsize=8, style="italic", wrap=True)

    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    out_path = PROJECT / "paper1_fig2_op_vs_reply_forest.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def fig3_cohort_alpha_floors():
    """Cohort-stratified 3-LLM Krippendorff α with 0.667 and 0.80 reliability floors."""
    # Numbers from PAPER_1_LOCKED_RESULTS_FINAL.md
    data = [
        ("Combined (Reddit + SDN)", 1001, 0.7590, 0.7241, 0.7868),
        ("Reddit only",              701, 0.6901, 0.6462, 0.7302),
        ("SDN only",                 300, 0.8306, 0.7870, 0.8661),
    ]
    df = pd.DataFrame(data, columns=["sample", "n", "alpha", "ci_lo", "ci_hi"])

    fig, ax = plt.subplots(figsize=(10, 5.5))
    y = np.arange(len(df))[::-1]

    # Reliability floor bands
    ax.axvspan(0.0, 0.667, color="lightcoral", alpha=0.2, label="Below tentative-reliability floor (α < 0.667)")
    ax.axvspan(0.667, 0.80, color="khaki", alpha=0.3, label="Tentative reliability (0.667 ≤ α < 0.80)")
    ax.axvspan(0.80, 1.00, color="lightgreen", alpha=0.3, label="Satisfactory reliability (α ≥ 0.80)")
    ax.axvline(0.667, color="darkred", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.axvline(0.80, color="darkgreen", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.text(0.667, -0.5, "0.667\n(Krippendorff 1980 tentative)", ha="center", va="top", fontsize=8, color="darkred")
    ax.text(0.80, -0.5, "0.80\n(Krippendorff 1980 satisfactory)", ha="center", va="top", fontsize=8, color="darkgreen")

    # 3-LLM α with CI bars
    for i, row in df.iterrows():
        yp = y[i]
        ax.plot([row["ci_lo"], row["ci_hi"]], [yp, yp], color="tab:blue", linewidth=2.5)
        ax.scatter(row["alpha"], yp, color="tab:blue", s=150, zorder=5)
        # Label
        ax.text(row["ci_hi"] + 0.015, yp, f"α={row['alpha']:.4f} [{row['ci_lo']:.4f}, {row['ci_hi']:.4f}], n={row['n']:,}",
                va="center", fontsize=10)

    ax.set_yticks(y)
    ax.set_yticklabels(df["sample"], fontsize=11)
    ax.set_xlabel("3-LLM Krippendorff α (sentiment task)", fontsize=11)
    ax.set_xlim(0.50, 1.05)
    ax.set_ylim(-1.0, len(df) - 0.5)
    ax.set_title(
        "Paper 1 Figure 3: 3-LLM convergence α with cohort heterogeneity\n"
        "Krippendorff (1980) reliability floors annotated",
        fontsize=12)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.85)

    fig.text(0.02, 0.02,
             "Note: 3-LLM = Claude Sonnet 4 + Llama 3.3 70B Instruct Turbo + DeepSeek V3.1. Combined sample CI entirely above "
             "0.667 floor; SDN-only above 0.80 floor; Reddit-only lower CI bound (0.6462) BELOW 0.667 floor. "
             "Together AI infrastructure caveat: 2/3 LLMs share serving infrastructure. Bootstrap CI: B=2,000 (simple resample within sample; "
             "cohort-stratified version pending for published draft per R17++ Agent 1 C4).",
             fontsize=8, style="italic", wrap=True)

    plt.tight_layout(rect=[0, 0.07, 1, 1])
    out_path = PROJECT / "paper1_fig3_cohort_alpha.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    fig1_correlation_matrix()
    fig2_op_vs_reply_forest()
    fig3_cohort_alpha_floors()
    print("\nPaper 1 figures complete.")
