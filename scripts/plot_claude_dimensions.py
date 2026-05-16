"""
plot_claude_dimensions.py
==========================
Multi-panel figure showing the three orthogonal dimensions Claude scoring
captures per post:
  1. pslf_sentiment  - 5-level ordinal affect/stance toward PSLF
  2. primary_topic    - 7-category content theme
  3. pslf_stance      - 5-category behavioral intention

Layout:
  Row 1 (3 panels):  Marginal distributions of each dimension
  Row 2 (3 panels):  Cross-tabulations (sentiment x stance, sentiment x topic, topic x stance)
  Row 3 (1 panel, wide):  Per-cohort breakdown of stance distribution

Output: pslf_claude_dimensions.png
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ZEROSHOT_CSVS = [
    "zeroshot_reddit_n1000.csv",
    "zeroshot_sdn_n1000.csv",
    "zeroshot_reddit_eventstrat.csv",
    "zeroshot_reddit_eventfull.csv",
    "zeroshot_sdn_eventfull.csv",
    "zeroshot_pa_np_expansion.csv",
    "zeroshot_reddit_fullcorpus.csv",
    "zeroshot_reddit_arctic_shift_fill.csv",  # round-8 (when present)
]

# Display order + colors
SENTIMENT_ORDER = ["very_negative", "negative", "neutral", "positive", "very_positive"]
SENTIMENT_COLORS = ["#B71C1C", "#E57373", "#9E9E9E", "#81C784", "#1B5E20"]  # red->grey->green
SENTIMENT_LABELS = ["very neg", "negative", "neutral", "positive", "very pos"]

STANCE_ORDER = ["rejecting", "considering", "unknown", "pursuing", "completed"]
# Red for rejecting (negative), yellow for considering (uncertain), grey for unknown,
# light green for pursuing (positive), dark green for completed (best)
STANCE_COLORS = ["#C62828", "#FBC02D", "#9E9E9E", "#66BB6A", "#1B5E20"]

TOPIC_ORDER = ["servicer_issues", "policy_uncertainty", "financial_planning",
               "career_impact", "success_story", "general_question",
               "frustration_venting"]
TOPIC_COLORS = ["#5D4037", "#C2185B", "#F57C00", "#1565C0",
                "#2E7D32", "#7B1FA2", "#37474F"]

PROF_LABEL = {
    "general_pslf": "Reddit r/PSLF",
    "general_student_loans": "Reddit r/StudentLoans",
    "general_finance": "Reddit Finance",
    "personalfinance": "Reddit Finance",
    "financialindependence": "Reddit Finance",
    "sdn_medical": "SDN (Medical)",
    "sdn": "SDN (Medical)",
    "medical": "Reddit Medical",
    "teaching": "Reddit Teaching",
    "physician_assistant": "Reddit PA",
    "nursing": "Reddit Nursing",
}


def load_claude():
    frames = []
    for f in ZEROSHOT_CSVS:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        d = d[~d["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
        # SDN zeroshot CSVs have empty profession but source='sdn'.
        # Fall back to source-based mapping when profession is missing/empty.
        if "profession" not in d.columns:
            d["profession"] = ""
        d["profession"] = d["profession"].fillna("").astype(str)
        if "source" in d.columns:
            sdn_mask = (d["profession"] == "") & (d["source"].fillna("").astype(str).str.lower() == "sdn")
            d.loc[sdn_mask, "profession"] = "sdn_medical"
        keep = ["post_id", "pslf_sentiment", "primary_topic", "pslf_stance", "profession"]
        frames.append(d[keep].copy())
        print(f"  {f}: {len(d):,}")
    big = pd.concat(frames, ignore_index=True).drop_duplicates("post_id")
    big["cohort"] = big["profession"].map(PROF_LABEL).fillna("Other")
    print(f"  Combined unique: {len(big):,}")
    print(f"  Cohort counts: {big['cohort'].value_counts().to_dict()}")
    return big


def stacked_bar_pct(ax, counts_dict, order, colors, labels=None, title=""):
    """Single horizontal stacked-bar showing % distribution."""
    total = sum(counts_dict.get(k, 0) for k in order)
    if total == 0:
        return
    pcts = [100 * counts_dict.get(k, 0) / total for k in order]
    left = 0
    for pct, color, k in zip(pcts, colors, order):
        ax.barh(0, pct, left=left, color=color, edgecolor="white", linewidth=0.7)
        if pct >= 4:
            label = labels[order.index(k)] if labels else k
            ax.text(left + pct/2, 0, f"{label}\n{pct:.1f}%",
                    ha="center", va="center", fontsize=8,
                    color="white" if k in ("very_negative", "rejecting") else "black",
                    fontweight="bold")
        left += pct
    ax.set_yticks([])
    ax.set_xlim(0, 100)
    ax.set_xlabel("% of posts", fontsize=9)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.spines["left"].set_visible(False)
    ax.set_axisbelow(True)


def heatmap_crosstab(ax, df, row_col, col_col, row_order, col_order,
                     row_labels=None, col_labels=None, title="", normalize="row"):
    """Cross-tabulation heatmap. normalize: 'row' (% within row) or 'all' (% of total)."""
    ct = pd.crosstab(df[row_col], df[col_col])
    # Reorder
    ct = ct.reindex(index=row_order, columns=col_order, fill_value=0)
    if normalize == "row":
        ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100
    elif normalize == "col":
        ct_pct = ct.div(ct.sum(axis=0), axis=1) * 100
    else:
        ct_pct = ct / ct.values.sum() * 100
    im = ax.imshow(ct_pct.values, cmap="Blues", aspect="auto", vmin=0,
                   vmax=max(60, ct_pct.values.max()))
    # Annotate cells
    for i in range(len(row_order)):
        for j in range(len(col_order)):
            v = ct_pct.iloc[i, j]
            n = int(ct.iloc[i, j])
            color = "white" if v > 35 else "#222"
            ax.text(j, i, f"{v:.0f}%\n(n={n})", ha="center", va="center",
                    fontsize=7.5, color=color, fontweight="bold")
    ax.set_xticks(range(len(col_order)))
    ax.set_xticklabels(col_labels or col_order, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(row_order)))
    ax.set_yticklabels(row_labels or row_order, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel(col_col, fontsize=9)
    ax.set_ylabel(row_col, fontsize=9)
    return ct, ct_pct


def main():
    print("Loading Claude scores from all zeroshot CSVs...")
    df = load_claude()
    print()
    print("Cohorts:")
    print(df["cohort"].value_counts().to_string())

    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#DDDDDD",
        "grid.linewidth": 0.4,
        "grid.alpha": 0.5,
        "legend.frameon": False,
        "font.family": "DejaVu Sans",
    })

    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(3, 3, height_ratios=[0.7, 1.6, 1.4],
                           hspace=0.55, wspace=0.35)

    # ---- ROW 1: Marginal distributions ----
    ax_sm = fig.add_subplot(gs[0, 0])
    s_counts = df["pslf_sentiment"].value_counts().to_dict()
    stacked_bar_pct(ax_sm, s_counts, SENTIMENT_ORDER, SENTIMENT_COLORS,
                    SENTIMENT_LABELS, "(a) Sentiment distribution (5-level ordinal)")

    ax_st = fig.add_subplot(gs[0, 1])
    stance_counts = df["pslf_stance"].fillna("unknown").value_counts().to_dict()
    stacked_bar_pct(ax_st, stance_counts, STANCE_ORDER, STANCE_COLORS,
                    title="(b) Behavioral stance toward PSLF")

    ax_tp = fig.add_subplot(gs[0, 2])
    topic_counts = df["primary_topic"].value_counts().to_dict()
    stacked_bar_pct(ax_tp, topic_counts, TOPIC_ORDER, TOPIC_COLORS,
                    title="(c) Primary topic")

    # ---- ROW 2: Cross-tabs ----
    ax_cs1 = fig.add_subplot(gs[1, 0])
    df_clean = df[df["pslf_stance"].notna() & ~df["pslf_stance"].isin(["unknown", ""])]
    heatmap_crosstab(ax_cs1, df_clean, "pslf_sentiment", "pslf_stance",
                     SENTIMENT_ORDER, [s for s in STANCE_ORDER if s != "unknown"],
                     SENTIMENT_LABELS,
                     title="(d) Sentiment x Stance (% within sentiment row)")

    ax_cs2 = fig.add_subplot(gs[1, 1])
    df_t = df[df["primary_topic"].notna() & (df["primary_topic"] != "")]
    heatmap_crosstab(ax_cs2, df_t, "pslf_sentiment", "primary_topic",
                     SENTIMENT_ORDER, TOPIC_ORDER, SENTIMENT_LABELS,
                     title="(e) Sentiment x Topic (% within sentiment row)")

    ax_cs3 = fig.add_subplot(gs[1, 2])
    df_ts = df[df["primary_topic"].notna() & df["pslf_stance"].notna()
                & ~df["pslf_stance"].isin(["unknown", ""])]
    heatmap_crosstab(ax_cs3, df_ts, "primary_topic", "pslf_stance",
                     TOPIC_ORDER, [s for s in STANCE_ORDER if s != "unknown"],
                     title="(f) Topic x Stance (% within topic row)")

    # ---- ROW 3: Per-cohort stance breakdown (the cohort heterogeneity finding) ----
    ax_co = fig.add_subplot(gs[2, :])
    cohorts = sorted(df["cohort"].value_counts().head(8).index.tolist(),
                     key=lambda c: -df[df["cohort"] == c].shape[0])
    cohort_n = {c: int(df[df["cohort"] == c].shape[0]) for c in cohorts}

    # Stacked horizontal bars: one row per cohort, 100% width split by stance
    y_pos = np.arange(len(cohorts))
    left = np.zeros(len(cohorts))
    for stance, color in zip(STANCE_ORDER, STANCE_COLORS):
        widths = []
        for c in cohorts:
            sub = df[df["cohort"] == c]
            sub = sub[sub["pslf_stance"].notna() & ~sub["pslf_stance"].isin(["unknown", ""])]
            n = len(sub)
            w = (sub["pslf_stance"] == stance).sum() / n * 100 if n else 0
            widths.append(w)
        ax_co.barh(y_pos, widths, left=left, color=color, label=stance,
                   edgecolor="white", linewidth=0.6)
        for i, w in enumerate(widths):
            if w >= 4:
                ax_co.text(left[i] + w/2, y_pos[i], f"{w:.0f}",
                           ha="center", va="center", fontsize=8,
                           color="white" if stance in ("rejecting",) else "black",
                           fontweight="bold")
        left = left + np.array(widths)

    ax_co.set_yticks(y_pos)
    ax_co.set_yticklabels([f"{c}\n(n={cohort_n[c]:,})" for c in cohorts], fontsize=9)
    ax_co.invert_yaxis()
    ax_co.set_xlim(0, 100)
    ax_co.set_xlabel("% within cohort (excluding unknown stance)", fontsize=10)
    ax_co.set_title("(g) Stance distribution by cohort\n"
                    "Reveals cohort heterogeneity: medical vs general PSLF cohorts have substantially different stance mixes",
                    fontsize=12, fontweight="bold")
    ax_co.legend(loc="upper right", fontsize=9, ncol=4, frameon=True,
                 facecolor="white", edgecolor="#CCCCCC")
    ax_co.set_axisbelow(True)
    ax_co.grid(axis="x", alpha=0.4)

    # Title
    n_total = len(df)
    fig.suptitle(f"Claude Sonnet 4 zero-shot scoring: three orthogonal dimensions per post  (n={n_total:,} unique PSLF posts)\n"
                 f"Sentiment (affect toward PSLF) x Stance (behavioral intention) x Topic (content theme) capture different latent constructs.",
                 fontsize=14, fontweight="bold", y=1.005)

    # Footer
    fig.text(0.99, 0.005,
             "Claude prompt: 5-level sentiment + 7-category topic + 5-category stance, returned per post as JSON. "
             "Cross-tabs in row 2 normalize within row.",
             ha="right", fontsize=8, style="italic", color="#666666")

    out = "pslf_claude_dimensions.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out}")

    # Print key cross-tab numbers for reference
    print("\nKey numbers from the cross-tabs:")
    print("\nSentiment x Stance (% within sentiment row):")
    sub = df[df["pslf_stance"].notna() & ~df["pslf_stance"].isin(["unknown", ""])]
    ct = pd.crosstab(sub["pslf_sentiment"], sub["pslf_stance"], normalize="index") * 100
    print(ct.round(1).to_string())
    print(f"\nFraction of 'negative' or 'very_negative' posts that are still pursuing/considering:")
    neg_sub = sub[sub["pslf_sentiment"].isin(["very_negative", "negative"])]
    pur_con = (neg_sub["pslf_stance"].isin(["pursuing", "considering"])).sum() / len(neg_sub) * 100
    print(f"  {pur_con:.1f}% of {len(neg_sub):,} negative-sentiment posts are still pursuing or considering PSLF")


if __name__ == "__main__":
    main()
