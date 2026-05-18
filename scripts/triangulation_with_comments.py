"""
triangulation_with_comments.py
==============================
Re-runs the TextBlob x VADER triangulation on Reddit COMMENTS (vs the
original post-level analysis). The comments corpus is ~50x larger than
posts and stylistically distinct (replies vs top-level posts), so this
extension tests whether the construct-disagreement finding generalizes.

Two passes:

  1. TB x VADER full-comment pairwise (Krippendorff's alpha + Pearson)
     - Adds vader_compound to the comments file in-place if missing
     - Uses ALL comments (typically ~350K once collector finishes)
     - This is the BIG sample test: does TB-VADER r ~ +0.30 hold at 50x scale?

  2. TB x VADER x Claude on a stratified sample of N=2,000 comments
     - Costs ~$10-15 in Claude API spend (zero-shot)
     - Run only with --score-claude flag (so default execution is FREE)
     - Stratified by post_subreddit to ensure coverage across communities
     - Optional: writes zeroshot_comments_sample.csv for later re-use

Outputs:
  - triangulation_comments_results.txt - canonical artifact
  - triangulation_comments_results.csv - per-cell numbers

Usage:
  python triangulation_with_comments.py
  python triangulation_with_comments.py --score-claude  # adds 3-rater pass
  python triangulation_with_comments.py --comments-csv reddit_comments_pslf.csv
"""
from __future__ import annotations

import argparse
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

import krippendorff
from sentiment_triangulation import (
    textblob_to_5,
    vader_to_5,
    CLAUDE_NUMERIC,
    alpha_bootstrap_ci,
)

DEFAULT_COMMENTS_CSV = "reddit_comments_pslf.csv"
DEFAULT_SAMPLE_CSV = "zeroshot_comments_sample.csv"
OUT_TXT = "triangulation_comments_results.txt"
OUT_CSV = "triangulation_comments_results.csv"


def add_vader_inplace(df: pd.DataFrame) -> pd.DataFrame:
    """Add vader_compound column to comments DataFrame if missing.
    Lazy import of vaderSentiment to avoid hard dependency for users who
    only want to run the post-level triangulation."""
    if "vader_compound" in df.columns and df["vader_compound"].notna().sum() > 0:
        return df
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except ImportError:
        print("[ABORT] vaderSentiment not installed. pip install vaderSentiment")
        sys.exit(1)
    print("  Computing VADER scores for comments (one-time)...")
    sia = SentimentIntensityAnalyzer()
    bodies = df["body"].fillna("").astype(str).tolist()
    n = len(bodies)
    compounds = np.empty(n, dtype=float)
    for i, b in enumerate(bodies):
        if not b:
            compounds[i] = np.nan
        else:
            try:
                compounds[i] = sia.polarity_scores(b[:5000])["compound"]
            except Exception:
                compounds[i] = np.nan
        if (i + 1) % 5000 == 0:
            print(f"    {i+1:,}/{n:,} comments scored")
    df["vader_compound"] = compounds
    return df


def two_rater_alpha(merged: pd.DataFrame, scorer_a_col: str, scorer_b_col: str,
                    a_label: str, b_label: str, B_boot: int = 2000) -> dict:
    """Pairwise Krippendorff's alpha (ordinal, 5-level) + Pearson + Spearman."""
    sub = merged[[scorer_a_col, scorer_b_col]].dropna()
    n = len(sub)
    rd = np.array([
        sub[scorer_a_col].astype(float).to_numpy(),
        sub[scorer_b_col].astype(float).to_numpy(),
    ])
    try:
        alpha = krippendorff.alpha(reliability_data=rd, level_of_measurement="ordinal")
    except Exception:
        alpha = float("nan")
    # Continuous correlations on the raw scores (not the discretized ones)
    pearson = stats.pearsonr(sub[scorer_a_col], sub[scorer_b_col]) if n >= 30 else (np.nan, np.nan)
    spearman = stats.spearmanr(sub[scorer_a_col], sub[scorer_b_col]) if n >= 30 else (np.nan, np.nan)
    # Bootstrap CI for alpha
    print(f"  Bootstrap CI for {a_label} x {b_label} (B={B_boot})...")
    ci_lo, ci_hi, B_actual = alpha_bootstrap_ci(rd, level="ordinal", B=B_boot)
    return {
        "pair": f"{a_label} x {b_label}",
        "n": int(n),
        "alpha_ordinal": float(alpha),
        "alpha_ci95_lo": float(ci_lo),
        "alpha_ci95_hi": float(ci_hi),
        "alpha_boot_B": int(B_actual),
        "pearson_r": float(pearson[0]),
        "pearson_p": float(pearson[1]),
        "spearman_rho": float(spearman[0]),
        "spearman_p": float(spearman[1]),
    }


def stratified_sample_for_claude(df: pd.DataFrame, n_target: int = 2000,
                                  seed: int = 42) -> pd.DataFrame:
    """Stratify by post_subreddit so all communities are represented."""
    rng = np.random.default_rng(seed)
    if "post_subreddit" not in df.columns:
        return df.sample(n=min(n_target, len(df)), random_state=seed)
    groups = df.groupby("post_subreddit")
    n_subs = groups.ngroups
    per_sub = max(int(np.ceil(n_target / n_subs)), 1)
    samples = []
    for sub, g in groups:
        n_take = min(per_sub, len(g))
        idx = rng.choice(g.index.to_numpy(), size=n_take, replace=False)
        samples.append(df.loc[idx])
    out = pd.concat(samples, ignore_index=True)
    if len(out) > n_target:
        out = out.sample(n=n_target, random_state=seed).reset_index(drop=True)
    return out


def run_claude_scoring(sample_df: pd.DataFrame, output_csv: str):
    """Lazy invocation of sentiment_zeroshot.py's Claude scorer on the sample.
    Adapts the existing script's interface — see sentiment_zeroshot.py for the
    exact prompt template and output schema."""
    print("\n[--score-claude] Running Claude zero-shot on stratified sample...")
    print(f"  Sample size: {len(sample_df):,}")
    print(f"  Estimated cost: ~${len(sample_df) * 0.005:.2f}")
    # Write the sample to a temp CSV in the format sentiment_zeroshot.py expects
    tmp = "_comments_sample_for_claude.csv"
    cols = {"comment_id": "id", "body": "combined_text",
            "post_subreddit": "subreddit"}
    sample_df = sample_df.rename(columns=cols)[["id", "subreddit", "combined_text"]].copy()
    sample_df["combined_text"] = sample_df["combined_text"].fillna("")
    sample_df.to_csv(tmp, index=False)
    cmd = (f'C:/Users/zanen/anaconda3/python.exe sentiment_zeroshot.py '
           f'--input "{tmp}" --output "{output_csv}"')
    print(f"  Run manually:\n    {cmd}")
    print(f"  After it finishes, re-run this script (without --score-claude) to integrate.")


def integrate_claude_results(comments_df: pd.DataFrame, claude_csv: str) -> pd.DataFrame:
    """Merge Claude's `pslf_sentiment` back onto comments via comment_id."""
    if not os.path.exists(claude_csv):
        return comments_df
    cl = pd.read_csv(claude_csv)
    # zeroshot output has post_id, pslf_sentiment, primary_topic, pslf_stance, etc.
    # Our 'id' was comment_id, so post_id == comment_id in the temp CSV.
    cl = cl.rename(columns={"post_id": "comment_id"})
    cl = cl[~cl["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
    cl["claude_numeric"] = cl["pslf_sentiment"].map(CLAUDE_NUMERIC)
    keep = ["comment_id", "claude_numeric", "pslf_sentiment", "primary_topic", "pslf_stance"]
    keep = [c for c in keep if c in cl.columns]
    return comments_df.merge(cl[keep], on="comment_id", how="left")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--comments-csv", default=DEFAULT_COMMENTS_CSV)
    parser.add_argument("--sample-csv", default=DEFAULT_SAMPLE_CSV,
                        help="Path to Claude-scored stratified sample (output of sentiment_zeroshot.py)")
    parser.add_argument("--score-claude", action="store_true",
                        help="Generate the stratified sample and print the command "
                             "to score it with Claude (~$10-15)")
    parser.add_argument("--n-sample", type=int, default=2000,
                        help="Target N for stratified Claude sample (default 2000)")
    parser.add_argument("--bootstrap-B", type=int, default=2000,
                        help="Bootstrap iterations for alpha CI (default 2000)")
    args = parser.parse_args()

    print("=" * 78)
    print("Comments-level Triangulation: TextBlob x VADER (and Claude if scored)")
    print("=" * 78)

    if not os.path.exists(args.comments_csv):
        print(f"\n[ABORT] Comments file not found: {args.comments_csv}")
        print("  Run: python collect_reddit_comments_no_auth.py")
        sys.exit(1)

    print(f"\nLoading comments: {args.comments_csv}")
    df = pd.read_csv(args.comments_csv)
    print(f"  Total comments:          {len(df):,}")

    # MIN_WORDS filter to match post-level analysis convention
    df = df[df["word_count"].fillna(0) >= 5].copy()  # comments are shorter; min 5
    print(f"  After word_count >= 5:   {len(df):,}")

    # === Add VADER if missing ===
    df = add_vader_inplace(df)

    # === Discretize TB and VADER to 5-level ordinal ===
    df["textblob_5"] = df["polarity"].apply(textblob_to_5)
    df["vader_5"] = df["vader_compound"].apply(vader_to_5)
    n_both = df[["textblob_5", "vader_5"]].dropna().shape[0]
    print(f"  Comments with both TB+VADER 5-level scores: {n_both:,}")

    # === Pass 1: TB x VADER on all comments ===
    print("\n[Pass 1] TextBlob x VADER on all comments...")
    tb_va = two_rater_alpha(df, "textblob_5", "vader_5",
                            "TextBlob", "VADER", B_boot=args.bootstrap_B)
    print(f"  TB x VADER alpha = {tb_va['alpha_ordinal']:+.4f} "
          f"95% CI [{tb_va['alpha_ci95_lo']:+.4f}, {tb_va['alpha_ci95_hi']:+.4f}] "
          f"(n={tb_va['n']:,}, B={tb_va['alpha_boot_B']})")
    print(f"  Pearson r={tb_va['pearson_r']:+.4f} (p={tb_va['pearson_p']:.4g})")
    print(f"  Spearman rho={tb_va['spearman_rho']:+.4f} (p={tb_va['spearman_p']:.4g})")

    # === Comparison to post-level numbers ===
    # These are the published post-level numbers from triangulation_results.txt
    post_level = {
        "TB x VADER alpha (canonical)":   {"value": 0.34, "n": 6975, "source": "posts (n=6975)"},
        "TB x VADER Pearson r":           {"value": 0.30, "n": 6975, "source": "posts (n=6975)"},
    }

    # === Pass 2 (optional): generate stratified sample for Claude ===
    if args.score_claude:
        sample = stratified_sample_for_claude(df, n_target=args.n_sample)
        sample_out = "_comments_sample_for_claude.csv"
        run_claude_scoring(sample, args.sample_csv)
        sample.to_csv(sample_out, index=False)
        print(f"\nStratified sample written to: {sample_out}")

    # === Pass 3 (if Claude results exist): 3-rater alpha on the sample ===
    three_rater = None
    if os.path.exists(args.sample_csv):
        print(f"\n[Pass 3] Found {args.sample_csv}; integrating Claude scores...")
        df_with_claude = integrate_claude_results(df, args.sample_csv)
        n_3 = df_with_claude.dropna(
            subset=["textblob_5", "vader_5", "claude_numeric"]).shape[0]
        print(f"  Comments with all 3 scorers: {n_3:,}")
        if n_3 >= 100:
            sub = df_with_claude.dropna(
                subset=["textblob_5", "vader_5", "claude_numeric"]).copy()
            rd = np.array([
                sub["textblob_5"].astype(float).to_numpy(),
                sub["vader_5"].astype(float).to_numpy(),
                sub["claude_numeric"].astype(float).to_numpy(),
            ])
            alpha_3 = krippendorff.alpha(reliability_data=rd, level_of_measurement="ordinal")
            ci_lo, ci_hi, B_actual = alpha_bootstrap_ci(rd, level="ordinal", B=args.bootstrap_B)
            three_rater = {
                "n": int(n_3),
                "alpha_3rater": float(alpha_3),
                "ci95": (float(ci_lo), float(ci_hi)),
                "B_actual": int(B_actual),
            }
            print(f"  3-rater alpha = {alpha_3:+.4f} "
                  f"95% CI [{ci_lo:+.4f}, {ci_hi:+.4f}]")

    # === Write artifacts ===
    print(f"\nWriting {OUT_TXT}...")
    rows_for_csv = [tb_va]
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Triangulation - COMMENTS (TextBlob x VADER, optionally + Claude)\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/triangulation_with_comments.py\n")
        f.write("=" * 80 + "\n\n")

        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether the post-level construct-mismatch finding (alpha=-0.027 / +0.17\n")
        f.write("on n=6,975 posts) replicates on COMMENTS, which are:\n")
        f.write("  * ~50x larger sample (~350K rows once collector finishes)\n")
        f.write("  * Stylistically distinct (replies/discussion vs top-level posts)\n")
        f.write("  * Typically shorter and more conversational\n")
        f.write("If the cross-instrument disagreement persists at this scale and register,\n")
        f.write("the finding is not corpus-specific. This is the SINGLE largest strengthener\n")
        f.write("for the methods paper.\n\n")

        f.write("PASS 1: TEXTBLOB x VADER ON ALL COMMENTS\n")
        f.write("-" * 80 + "\n")
        f.write(f"  N (both scorers present):  {tb_va['n']:,}\n")
        f.write(f"  Krippendorff alpha (ord):  {tb_va['alpha_ordinal']:+.4f}\n")
        f.write(f"    95% CI:                  [{tb_va['alpha_ci95_lo']:+.4f}, "
                f"{tb_va['alpha_ci95_hi']:+.4f}]\n")
        f.write(f"    Bootstrap B (valid):     {tb_va['alpha_boot_B']:,}\n")
        f.write(f"  Pearson r:                 {tb_va['pearson_r']:+.4f} "
                f"(p={tb_va['pearson_p']:.4g})\n")
        f.write(f"  Spearman rho:              {tb_va['spearman_rho']:+.4f} "
                f"(p={tb_va['spearman_p']:.4g})\n\n")

        f.write("COMPARISON TO POST-LEVEL TRIANGULATION\n")
        f.write("-" * 80 + "\n")
        for label, ref in post_level.items():
            f.write(f"  {label:<35s} posts: {ref['value']:+.4f}  ({ref['source']})\n")
        f.write(f"  TB x VADER alpha (canonical)        comments: {tb_va['alpha_ordinal']:+.4f}  "
                f"(comments n={tb_va['n']:,})\n")
        f.write(f"  TB x VADER Pearson r                comments: {tb_va['pearson_r']:+.4f}\n\n")

        if abs(tb_va['alpha_ordinal'] - 0.34) < 0.10:
            f.write("VERDICT: TB x VADER alpha REPLICATES on comments (within 0.10 of post-level).\n")
            f.write("The instrument-disagreement pattern is not specific to top-level posts.\n\n")
        elif tb_va['alpha_ordinal'] > 0.34 + 0.10:
            f.write("VERDICT: TB x VADER alpha is HIGHER on comments. Possible reason:\n")
            f.write("comments are shorter and more direct, reducing room for lexical-affect\n")
            f.write("vs expressive-arousal divergence.\n\n")
        else:
            f.write("VERDICT: TB x VADER alpha is LOWER on comments. The disagreement is\n")
            f.write("more pronounced at the comment level - finding STRENGTHENS.\n\n")

        if three_rater:
            f.write("PASS 3: THREE-RATER ALPHA ON CLAUDE-SCORED SAMPLE\n")
            f.write("-" * 80 + "\n")
            f.write(f"  N (3 scorers, sampled):     {three_rater['n']:,}\n")
            f.write(f"  Three-rater alpha (ord):    {three_rater['alpha_3rater']:+.4f}\n")
            f.write(f"  95% CI:                     [{three_rater['ci95'][0]:+.4f}, "
                    f"{three_rater['ci95'][1]:+.4f}]\n")
            f.write(f"  Post-level reference:       -0.027 (canonical) / +0.17 (charitable)\n\n")
            rows_for_csv.append({
                "pair": "TB x VADER x Claude (3-rater, comments sample)",
                "n": three_rater["n"],
                "alpha_ordinal": three_rater["alpha_3rater"],
                "alpha_ci95_lo": three_rater["ci95"][0],
                "alpha_ci95_hi": three_rater["ci95"][1],
                "alpha_boot_B": three_rater["B_actual"],
                "pearson_r": float("nan"),
                "pearson_p": float("nan"),
                "spearman_rho": float("nan"),
                "spearman_p": float("nan"),
            })
        else:
            f.write("PASS 3: NOT YET RUN\n")
            f.write("-" * 80 + "\n")
            f.write("To add the 3-rater test on a Claude-scored sample (~$10-15):\n")
            f.write("  1. python triangulation_with_comments.py --score-claude\n")
            f.write("     (writes _comments_sample_for_claude.csv)\n")
            f.write("  2. python sentiment_zeroshot.py \\\n")
            f.write("       --input _comments_sample_for_claude.csv \\\n")
            f.write(f"       --output {DEFAULT_SAMPLE_CSV}\n")
            f.write("  3. Re-run this script (without --score-claude) to integrate.\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    pd.DataFrame(rows_for_csv).to_csv(OUT_CSV, index=False, float_format="%.6f")
    print(f"Saved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")
    print()
    print("KEY RESULT (TB x VADER on all comments):")
    print(f"  alpha = {tb_va['alpha_ordinal']:+.4f}  "
          f"95% CI [{tb_va['alpha_ci95_lo']:+.4f}, {tb_va['alpha_ci95_hi']:+.4f}]  "
          f"(n={tb_va['n']:,})")
    print(f"  vs post-level reference alpha = +0.34")


if __name__ == "__main__":
    main()
