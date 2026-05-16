"""
analyze_op_vs_reply.py
========================
For each post that received comments, compare:
  - OP (original post) sentiment via TextBlob and VADER
  - Mean comment sentiment (TextBlob, VADER) across all replies
  - Mean comment sentiment by depth tier (top-level vs reply-to-reply)

Tests:
  1. **Reply skew hypothesis**: do replies systematically diverge from the OP?
  2. **Depth escalation hypothesis**: does sentiment shift as conversation
     goes deeper into the comment tree?
  3. **Cohort × OP-reply pattern**: does the OP-reply gap differ across cohorts?

Why this matters for the methods paper:
If replies systematically diverge from OPs in TB but agree on Claude stance,
that would mean TB is reading the lexical noise of replies while Claude reads
the underlying stance posture - additional construct-mismatch evidence.

Output: op_vs_reply_results.{txt,csv}
"""
from __future__ import annotations

import io
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

OUT_TXT = "op_vs_reply_results.txt"
OUT_CSV = "op_vs_reply_results.csv"

PROF_TO_COHORT = {
    "general_pslf": "Reddit r/PSLF",
    "general_student_loans": "Reddit r/StudentLoans",
    "general_finance": "Reddit Finance",
    "personalfinance": "Reddit Finance",
    "financialindependence": "Reddit Finance",
    "medical": "Reddit Medical",
    "teaching": "Reddit Teaching",
    "physician_assistant": "Reddit PA",
    "nursing": "Reddit Nursing",
}


def main():
    print("=" * 80)
    print("OP vs Reply sentiment analysis")
    print("=" * 80)

    # Load OPs (Reddit posts, with sentiment + cohort)
    print("\nLoading OPs (Reddit posts with sentiment)...")
    op_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv",
              "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        if "id" in d.columns:
            d = d.rename(columns={"id": "post_id"})
        keep_cols = ["post_id", "polarity"]
        if "vader_compound" in d.columns:
            keep_cols.append("vader_compound")
        else:
            d["vader_compound"] = np.nan
            keep_cols.append("vader_compound")
        if "profession" in d.columns:
            keep_cols.append("profession")
        else:
            d["profession"] = ""
            keep_cols.append("profession")
        if "subreddit" in d.columns:
            keep_cols.append("subreddit")
        if "word_count" in d.columns:
            keep_cols.append("word_count")
        else:
            d["word_count"] = 100
            keep_cols.append("word_count")
        op_frames.append(d[keep_cols])
    ops = pd.concat(op_frames, ignore_index=True).drop_duplicates("post_id")
    ops["post_id"] = ops["post_id"].astype(str)
    ops = ops.dropna(subset=["polarity"])
    ops = ops[ops["word_count"].fillna(0) >= 20]
    ops["cohort"] = ops["profession"].map(PROF_TO_COHORT).fillna("Other")
    print(f"  Reddit OPs (wc>=20): {len(ops):,}")

    # Load comments (with sentiment + depth)
    print("\nLoading comments...")
    cm = pd.read_csv("reddit_comments_pslf.csv", low_memory=False)
    cm["post_id"] = cm["post_id"].astype(str)
    cm = cm[cm["polarity"].notna()]
    cm = cm[cm["word_count"].fillna(0) >= 5]
    print(f"  Comments (wc>=5): {len(cm):,}")
    print(f"  Unique posts with comments: {cm['post_id'].nunique():,}")

    # Add VADER to comments if missing
    if "vader_compound" not in cm.columns or cm["vader_compound"].isna().all():
        print("  Computing VADER on comments (no vader_compound column)...")
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        bodies = cm["body"].fillna("").astype(str).tolist()
        cv = np.empty(len(bodies), dtype=float)
        for i, b in enumerate(bodies):
            try:
                cv[i] = sia.polarity_scores(b[:5000])["compound"] if b else np.nan
            except Exception:
                cv[i] = np.nan
            if (i + 1) % 20000 == 0:
                print(f"    {i+1:,}/{len(bodies):,}")
        cm["vader_compound"] = cv

    # Per-post: mean comment sentiment + by depth tier
    print("\nAggregating per-post...")
    agg = cm.groupby("post_id").agg(
        n_comments=("comment_id", "count"),
        mean_cmt_polarity=("polarity", "mean"),
        mean_cmt_vader=("vader_compound", "mean"),
        max_depth=("depth", "max"),
    ).reset_index()
    print(f"  Posts with aggregated comments: {len(agg):,}")

    # Top-level only vs deep-reply only
    cm_top = cm[cm["depth"] == 0]
    agg_top = cm_top.groupby("post_id").agg(
        n_top_cmts=("comment_id", "count"),
        mean_top_polarity=("polarity", "mean"),
        mean_top_vader=("vader_compound", "mean"),
    ).reset_index()

    cm_deep = cm[cm["depth"] >= 2]
    agg_deep = cm_deep.groupby("post_id").agg(
        n_deep_cmts=("comment_id", "count"),
        mean_deep_polarity=("polarity", "mean"),
        mean_deep_vader=("vader_compound", "mean"),
    ).reset_index()

    # Merge OPs with aggregations
    df = ops.merge(agg, on="post_id", how="inner")
    df = df.merge(agg_top, on="post_id", how="left")
    df = df.merge(agg_deep, on="post_id", how="left")
    df["op_minus_cmt_polarity"] = df["polarity"] - df["mean_cmt_polarity"]
    df["op_minus_cmt_vader"] = df["vader_compound"] - df["mean_cmt_vader"]
    df["top_minus_deep_polarity"] = df["mean_top_polarity"] - df["mean_deep_polarity"]
    print(f"  Posts with both OP and comments: {len(df):,}")

    # === Statistical tests ===
    # H1: Reply skew - replies systematically more negative than OP
    diff_pol = df["op_minus_cmt_polarity"].dropna()
    t_pol, p_pol = stats.ttest_1samp(diff_pol, 0)
    diff_va = df["op_minus_cmt_vader"].dropna()
    t_va, p_va = stats.ttest_1samp(diff_va, 0)

    # H2: Depth escalation - top-level vs deep-reply
    diff_depth = df["top_minus_deep_polarity"].dropna()
    if len(diff_depth) >= 30:
        t_depth, p_depth = stats.ttest_1samp(diff_depth, 0)
    else:
        t_depth, p_depth = float("nan"), float("nan")

    # H3: Per-cohort breakdown
    cohort_summary = []
    for cohort in df["cohort"].dropna().unique():
        sub = df[df["cohort"] == cohort]
        if len(sub) < 30:
            continue
        cohort_summary.append({
            "cohort": cohort,
            "n_posts": len(sub),
            "mean_op_polarity": float(sub["polarity"].mean()),
            "mean_cmt_polarity": float(sub["mean_cmt_polarity"].mean()),
            "mean_op_minus_cmt_polarity": float(sub["op_minus_cmt_polarity"].mean()),
            "mean_op_vader": float(sub["vader_compound"].mean()),
            "mean_cmt_vader": float(sub["mean_cmt_vader"].mean()),
            "mean_op_minus_cmt_vader": float(sub["op_minus_cmt_vader"].mean()),
            "mean_n_comments": float(sub["n_comments"].mean()),
        })
    cohort_df = pd.DataFrame(cohort_summary).sort_values("n_posts", ascending=False)

    # === Write report ===
    cohort_df.to_csv(OUT_CSV, index=False, float_format="%.4f")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("OP vs Reply Sentiment Analysis\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("SAMPLE\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Posts (OPs) with comments analyzed: {len(df):,}\n")
        f.write(f"  Total comments aggregated:           {df['n_comments'].sum():,}\n")
        f.write(f"  Mean comments per post:              {df['n_comments'].mean():.1f}\n\n")

        f.write("H1: REPLY SKEW (do replies diverge from OP?)\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Mean OP polarity:                    {df['polarity'].mean():+.4f}\n")
        f.write(f"  Mean reply polarity:                 {df['mean_cmt_polarity'].mean():+.4f}\n")
        f.write(f"  Mean (OP - reply) polarity:          {diff_pol.mean():+.4f}\n")
        f.write(f"    1-sample t vs 0:                   t={t_pol:.2f}, p={p_pol:.4g}\n")
        f.write(f"  Mean OP VADER:                       {df['vader_compound'].mean():+.4f}\n")
        f.write(f"  Mean reply VADER:                    {df['mean_cmt_vader'].mean():+.4f}\n")
        f.write(f"  Mean (OP - reply) VADER:             {diff_va.mean():+.4f}\n")
        f.write(f"    1-sample t vs 0:                   t={t_va:.2f}, p={p_va:.4g}\n\n")

        if abs(diff_pol.mean()) > 0.01:
            direction_pol = "more positive" if diff_pol.mean() > 0 else "more negative"
            f.write(f"  Verdict polarity: OPs are {abs(diff_pol.mean())*100:.2f} pp {direction_pol} "
                    f"than replies on average\n")
        if abs(diff_va.mean()) > 0.01:
            direction_va = "more positive" if diff_va.mean() > 0 else "more negative"
            f.write(f"  Verdict VADER:    OPs are {abs(diff_va.mean()):.4f} {direction_va} "
                    f"than replies on average\n")
        f.write("\n")

        f.write("H2: DEPTH ESCALATION (top-level vs reply-to-reply)\n")
        f.write("-" * 80 + "\n")
        if not np.isnan(p_depth):
            f.write(f"  Posts with both top-level and deep replies: {len(diff_depth):,}\n")
            f.write(f"  Mean (top-level - deep) polarity:    {diff_depth.mean():+.4f}\n")
            f.write(f"    1-sample t vs 0:                   t={t_depth:.2f}, p={p_depth:.4g}\n")
            if abs(diff_depth.mean()) > 0.005:
                d = "more positive" if diff_depth.mean() > 0 else "more negative"
                f.write(f"  Verdict: top-level replies are {abs(diff_depth.mean()):.4f} {d} "
                        f"than deeper replies on average\n")
        else:
            f.write("  Insufficient data\n")
        f.write("\n")

        f.write("H3: PER-COHORT OP-vs-REPLY GAP\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'cohort':<26s} {'n_posts':>8s} {'OP_pol':>8s} {'cmt_pol':>8s} {'op-cmt':>8s} "
                f"{'OP_VA':>8s} {'cmt_VA':>8s} {'op-cmt':>8s} {'avg_cmts':>9s}\n")
        for _, r in cohort_df.iterrows():
            f.write(f"{r['cohort']:<26s} {int(r['n_posts']):>8d} {r['mean_op_polarity']:>+8.4f} "
                    f"{r['mean_cmt_polarity']:>+8.4f} {r['mean_op_minus_cmt_polarity']:>+8.4f} "
                    f"{r['mean_op_vader']:>+8.4f} {r['mean_cmt_vader']:>+8.4f} "
                    f"{r['mean_op_minus_cmt_vader']:>+8.4f} {r['mean_n_comments']:>9.1f}\n")
        f.write("\n")
        f.write("Cohort patterns to look for:\n")
        f.write("  - Negative op-cmt = replies MORE positive than OP (sympathy/encouragement)\n")
        f.write("  - Positive op-cmt = replies MORE negative than OP (criticism/skepticism)\n")
        f.write("  - Cohorts with notably different op-cmt gaps suggest different reply norms\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")
    print()
    print(f"Quick summary:")
    print(f"  Mean (OP - reply) polarity: {diff_pol.mean():+.4f} (p={p_pol:.4g})")
    print(f"  Mean (OP - reply) VADER:    {diff_va.mean():+.4f} (p={p_va:.4g})")
    print()
    print("Per-cohort op-cmt polarity gap (top 5):")
    print(cohort_df[["cohort", "n_posts", "mean_op_minus_cmt_polarity",
                       "mean_op_minus_cmt_vader"]].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
