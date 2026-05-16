"""
plot_claude_dimensions_by_event.py
===================================
For each of the 8 PSLF policy events, show pre-vs-post distribution shifts
across all three Claude scoring dimensions:
  - Sentiment (5 levels)
  - Stance (5 categories)
  - Topic (7 categories)

Layout:
  Row 1 (3 heatmaps): Pre->Post percentage-point deltas, pooled across cohorts
                      Rows = 8 events, Cols = categories, Cells = delta_pp
                      Colormap: diverging (red=decreased, blue=increased)
  Row 2 (3 heatmaps): Same, but for SDN (Medical) ONLY (the cohort with
                      the largest event responses)
  Row 3 (3 heatmaps): Same, but for Reddit r/PSLF + r/StudentLoans pooled
                      (the general-PSLF audience)

The three rows together show the cohort heterogeneity: SDN and general
Reddit move differently within the same event window.

Output: pslf_claude_dimensions_by_event.png
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
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
    "zeroshot_reddit_arctic_shift_fill.csv",
]

# Source CSVs holding dates for the post_ids
SOURCE_CSVS_REDDIT = [
    "reddit_professions_pslf.csv",
    "comprehensive_medical_pslf_discussions.csv",
    "comprehensive_teacher_pslf_discussions.csv",
    "reddit_new_subs_pslf.csv",
    "reddit_arctic_shift_pslf.csv",
]
SOURCE_CSV_SDN = "forum_pslf_discussions.csv"

EVENTS = [
    ("Limited PSLF Waiver",            "2021-10-06", 90),
    ("IDR Account Adjustment",         "2022-04-19", 90),
    ("Biden Mass Forgiveness",         "2022-08-24", 90),
    ("Biden v. Nebraska SCOTUS",       "2023-06-30", 90),
    ("Payments Restart",               "2023-10-01", 90),
    ("SAVE Admin Forbearance",         "2024-08-09", 90),
    ("Trump PSLF EO",                  "2025-03-07", 60),
    ("Final Trump PSLF Rule",          "2025-10-30", 60),
]

# Display category orders (chosen for visual logic: positive->negative or pursuing->rejecting)
SENTIMENT_ORDER = ["very_negative", "negative", "neutral", "positive", "very_positive"]
SENTIMENT_LABELS = ["very neg", "negative", "neutral", "positive", "very pos"]
STANCE_ORDER = ["rejecting", "considering", "pursuing", "completed"]
TOPIC_ORDER = ["servicer_issues", "policy_uncertainty", "financial_planning",
               "career_impact", "success_story", "general_question",
               "frustration_venting"]

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


def load_claude_with_dates():
    """Load Claude scores from all zeroshot CSVs, joining with dates from source CSVs."""
    # Step 1: load Claude scores
    cl_frames = []
    for f in ZEROSHOT_CSVS:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        d = d[~d["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
        if "profession" not in d.columns:
            d["profession"] = ""
        d["profession"] = d["profession"].fillna("").astype(str)
        if "source" in d.columns:
            sdn_mask = (d["profession"] == "") & (d["source"].fillna("").astype(str).str.lower() == "sdn")
            d.loc[sdn_mask, "profession"] = "sdn_medical"
        keep = ["post_id", "pslf_sentiment", "primary_topic", "pslf_stance", "profession"]
        cl_frames.append(d[keep].copy())
        print(f"  Claude {f}: {len(d):,}")
    cl = pd.concat(cl_frames, ignore_index=True).drop_duplicates("post_id")
    print(f"  Combined unique Claude rows: {len(cl):,}")

    # Step 2: load dates from source CSVs
    dates_frames = []
    for f in SOURCE_CSVS_REDDIT:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f, usecols=lambda c: c in ("id", "post_id", "created_utc"))
        if "id" in d.columns and "post_id" not in d.columns:
            d = d.rename(columns={"id": "post_id"})
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"),
                                    unit="s", errors="coerce")
        dates_frames.append(d[["post_id", "date"]])
    if os.path.exists(SOURCE_CSV_SDN):
        d = pd.read_csv(SOURCE_CSV_SDN, usecols=lambda c: c in ("post_id", "date_posted"))
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        dates_frames.append(d[["post_id", "date"]])
    dates = pd.concat(dates_frames, ignore_index=True).drop_duplicates("post_id")
    cl["post_id"] = cl["post_id"].astype(str)
    dates["post_id"] = dates["post_id"].astype(str)
    cl = cl.merge(dates, on="post_id", how="left")
    cl = cl.dropna(subset=["date"])
    cl["date"] = pd.to_datetime(cl["date"], utc=True, errors="coerce").dt.tz_localize(None)
    cl["cohort"] = cl["profession"].map(PROF_LABEL).fillna("Other")
    print(f"  After date join: {len(cl):,} (cohort distribution shown below)")
    print(cl["cohort"].value_counts().to_string())
    return cl


def deltas_for_dim(df, dim_col, categories, min_n=10):
    """For each event, compute pre and post % distribution for `dim_col` and
    return a DataFrame of (event x category) percentage-point deltas.
    """
    rows = []
    for ev_name, ev_date, win in EVENTS:
        dt = pd.Timestamp(ev_date)
        pre = df[(df["date"] >= dt - pd.Timedelta(days=win)) & (df["date"] < dt)]
        post = df[(df["date"] >= dt) & (df["date"] <= dt + pd.Timedelta(days=win))]
        # Filter to non-null in dim_col + non-empty
        pre = pre[pre[dim_col].notna() & (pre[dim_col].astype(str) != "")
                  & ~pre[dim_col].isin(["unknown"])]
        post = post[post[dim_col].notna() & (post[dim_col].astype(str) != "")
                    & ~post[dim_col].isin(["unknown"])]
        n_pre, n_post = len(pre), len(post)
        # Compute distributions
        row = {"event": ev_name, "n_pre": n_pre, "n_post": n_post}
        for cat in categories:
            pre_pct = (pre[dim_col] == cat).sum() / n_pre * 100 if n_pre >= min_n else np.nan
            post_pct = (post[dim_col] == cat).sum() / n_post * 100 if n_post >= min_n else np.nan
            row[cat] = (post_pct - pre_pct) if (not np.isnan(pre_pct) and not np.isnan(post_pct)) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def plot_delta_heatmap(ax, deltas_df, categories, labels, title, vmax=20):
    """Heatmap of pre->post deltas. Rows=events, Cols=categories, Cells=delta_pp.
    Convention: positive deltas = green, negative deltas = red (RdYlGn).
    Reader interprets in context per column label (e.g. positive delta in
    'rejecting' column = more rejection)."""
    matrix = deltas_df[categories].values  # (n_events, n_categories)
    cmap = plt.get_cmap("RdYlGn")
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    im = ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    # Annotate
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]
            if np.isnan(v):
                ax.text(j, i, "n/a", ha="center", va="center", fontsize=6.5,
                        color="#666")
            else:
                color = "white" if abs(v) > vmax * 0.55 else "#222"
                ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=7.5,
                        color=color, fontweight="bold")

    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(deltas_df)))
    # Event labels include n_pre/n_post for transparency
    yticklabels = [f"{r['event']}\n({int(r['n_pre'])}/{int(r['n_post'])})"
                    for _, r in deltas_df.iterrows()]
    ax.set_yticklabels(yticklabels, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight="bold")
    return im


def main():
    print("Loading Claude scores with dates...")
    df = load_claude_with_dates()

    # Compute deltas for each dimension x cohort group
    print("\nComputing pre/post deltas...")
    sentiment_pooled = deltas_for_dim(df, "pslf_sentiment", SENTIMENT_ORDER)
    stance_pooled    = deltas_for_dim(df, "pslf_stance",    STANCE_ORDER)
    topic_pooled     = deltas_for_dim(df, "primary_topic",  TOPIC_ORDER)

    df_sdn = df[df["cohort"] == "SDN (Medical)"]
    sentiment_sdn = deltas_for_dim(df_sdn, "pslf_sentiment", SENTIMENT_ORDER, min_n=8)
    stance_sdn    = deltas_for_dim(df_sdn, "pslf_stance",    STANCE_ORDER, min_n=8)
    topic_sdn     = deltas_for_dim(df_sdn, "primary_topic",  TOPIC_ORDER, min_n=8)

    df_red = df[df["cohort"].isin(["Reddit r/PSLF", "Reddit r/StudentLoans"])]
    sentiment_red = deltas_for_dim(df_red, "pslf_sentiment", SENTIMENT_ORDER, min_n=8)
    stance_red    = deltas_for_dim(df_red, "pslf_stance",    STANCE_ORDER, min_n=8)
    topic_red     = deltas_for_dim(df_red, "primary_topic",  TOPIC_ORDER, min_n=8)

    # Plot
    plt.rcParams.update({
        "figure.facecolor": "white",
        "font.family": "DejaVu Sans",
    })
    fig, axes = plt.subplots(3, 3, figsize=(18, 14),
                              gridspec_kw={"hspace": 0.55, "wspace": 0.35,
                                            "width_ratios": [1, 1, 1.5]})

    # Row 1: pooled
    plot_delta_heatmap(axes[0, 0], sentiment_pooled, SENTIMENT_ORDER, SENTIMENT_LABELS,
                       "Sentiment Δ pp (pooled)", vmax=20)
    plot_delta_heatmap(axes[0, 1], stance_pooled, STANCE_ORDER, STANCE_ORDER,
                       "Stance Δ pp (pooled)", vmax=20)
    plot_delta_heatmap(axes[0, 2], topic_pooled, TOPIC_ORDER, TOPIC_ORDER,
                       "Topic Δ pp (pooled)", vmax=30)

    # Row 2: SDN-Medical only
    plot_delta_heatmap(axes[1, 0], sentiment_sdn, SENTIMENT_ORDER, SENTIMENT_LABELS,
                       "Sentiment Δ pp (SDN-Medical)", vmax=30)
    plot_delta_heatmap(axes[1, 1], stance_sdn, STANCE_ORDER, STANCE_ORDER,
                       "Stance Δ pp (SDN-Medical)", vmax=40)
    plot_delta_heatmap(axes[1, 2], topic_sdn, TOPIC_ORDER, TOPIC_ORDER,
                       "Topic Δ pp (SDN-Medical)", vmax=50)

    # Row 3: Reddit r/PSLF + r/StudentLoans
    plot_delta_heatmap(axes[2, 0], sentiment_red, SENTIMENT_ORDER, SENTIMENT_LABELS,
                       "Sentiment Δ pp (Reddit r/PSLF + r/SL)", vmax=20)
    plot_delta_heatmap(axes[2, 1], stance_red, STANCE_ORDER, STANCE_ORDER,
                       "Stance Δ pp (Reddit r/PSLF + r/SL)", vmax=20)
    im = plot_delta_heatmap(axes[2, 2], topic_red, TOPIC_ORDER, TOPIC_ORDER,
                            "Topic Δ pp (Reddit r/PSLF + r/SL)", vmax=30)

    fig.suptitle("Pre→Post percentage-point shifts in three Claude dimensions, by event and cohort\n"
                 f"Rows: pooled / SDN-Medical only / Reddit-general only.  "
                 f"Cells = (post % − pre %).  Green = positive Δ, Red = negative Δ.  "
                 f"Read in context per column (e.g. green in 'rejecting' = more rejection).  "
                 f"Y-axis labels show n_pre/n_post.",
                 fontsize=13, fontweight="bold", y=1.005)

    fig.text(0.99, 0.005,
             "Cells with n_pre or n_post < 10 (pooled) / < 8 (cohort-specific) shown as 'n/a'. "
             "Stance excludes 'unknown' before computing percentages.",
             ha="right", fontsize=8, style="italic", color="#666666")

    out = "pslf_claude_dimensions_by_event.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out}")

    # Print key numbers
    print("\nKey shifts (large absolute values):")
    for label, df_delta, dim_order in [
        ("POOLED Sentiment", sentiment_pooled, SENTIMENT_ORDER),
        ("POOLED Stance",    stance_pooled,    STANCE_ORDER),
        ("POOLED Topic",     topic_pooled,     TOPIC_ORDER),
        ("SDN Sentiment",    sentiment_sdn,    SENTIMENT_ORDER),
        ("SDN Stance",       stance_sdn,       STANCE_ORDER),
        ("SDN Topic",        topic_sdn,        TOPIC_ORDER),
    ]:
        for _, row in df_delta.iterrows():
            for cat in dim_order:
                if not np.isnan(row[cat]) and abs(row[cat]) >= 15:
                    print(f"  {label:20s} {row['event']:25s} {cat:25s} "
                          f"Δ={row[cat]:+.1f}pp  (n_pre={int(row['n_pre'])}, n_post={int(row['n_post'])})")


if __name__ == "__main__":
    main()
