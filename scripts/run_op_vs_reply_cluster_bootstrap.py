"""
run_op_vs_reply_cluster_bootstrap.py
=====================================
R17++ Agent 1 C1 strengthener: proper cluster-bootstrap on (post, comment) pairs
for the OP-vs-Reply Δ test.

Background: existing analyze_op_vs_reply.py aggregates comments to per-post
means first, then does a 1-sample t-test on per-post Δ. That's correct as far
as it goes, but R17++ audit flagged that earlier drafts incorrectly attributed
"cluster-bootstrap p≈0" with fabricated CIs like [−0.019, −0.014] and
[+0.212, +0.230]. This script provides the PROPER cluster-bootstrap to
generate REAL CIs.

Cluster-bootstrap design (Cameron-Miller 2015):
- Cluster unit: post_id
- Resample posts WITH replacement; within each resampled post, include ALL
  its comments
- For each bootstrap iteration:
    1. Resample N posts (with replacement)
    2. Compute per-post Δ = mean(OP polarity) − mean(reply polarity)
    3. Compute overall mean of Δ across resampled posts
- B=2,000 iterations
- 95% percentile CI from bootstrap distribution

Output: paper1_op_vs_reply_cluster_bootstrap_results.txt
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def load_op_and_comments():
    """Load OP polarity (per post) + comment polarity (per comment), aligned."""
    # OPs (posts with sentiment + post_id) from the master Arctic Shift + SDN combo
    # Use the same logic as analyze_op_vs_reply.py
    # We need: post_id, polarity, vader_compound for OPs
    # And: post_id, polarity, vader_compound for comments (one row per comment)

    # OPs source: combine reddit_arctic_shift_pslf with VADER + TextBlob
    # If the VADER-enriched file exists, use it. Otherwise fall back.
    op_files = [
        "reddit_arctic_shift_pslf.csv",
        "reddit_arctic_shift_pslf_with_vader.csv",
    ]
    # We want the version with both polarity (TextBlob) and vader_compound
    for f in op_files:
        path = PROJECT / f
        if path.exists():
            df = pd.read_csv(path, low_memory=False)
            # Arctic Shift CSV uses "id" not "post_id"
            id_col = "post_id" if "post_id" in df.columns else "id"
            if id_col in df.columns and "polarity" in df.columns and ("vader_compound" in df.columns or "vader" in df.columns):
                if "vader" in df.columns and "vader_compound" not in df.columns:
                    df = df.rename(columns={"vader": "vader_compound"})
                ops = df[[id_col, "polarity", "vader_compound"]].dropna(subset=[id_col]).copy()
                if id_col != "post_id":
                    ops = ops.rename(columns={id_col: "post_id"})
                print(f"Loaded OPs from {f}: {len(ops):,}")
                break
    else:
        # Fallback: read TextBlob + VADER separately
        print("Trying fallback OP load...")
        return None, None

    # Comments source
    cm_path = PROJECT / "reddit_comments_pslf_with_vader.csv"
    if not cm_path.exists():
        print("Comments CSV not found; cannot run cluster bootstrap.")
        return ops, None
    print(f"Loading comments from {cm_path.name} (~170 MB)...")
    cm = pd.read_csv(cm_path, low_memory=False)
    # We need: post_id, polarity, vader_compound (one row per comment)
    cm = cm[["post_id", "polarity", "vader_compound"]].dropna(subset=["post_id"]).copy()
    print(f"Loaded comments: {len(cm):,}")
    return ops, cm


def per_post_delta(ops, cm):
    """Compute per-post Δ = OP polarity − mean(comment polarity)."""
    # Aggregate comments to per-post means
    cm_agg = cm.groupby("post_id").agg(
        mean_cmt_polarity=("polarity", "mean"),
        mean_cmt_vader=("vader_compound", "mean"),
        n_cmts=("post_id", "count"),
    ).reset_index()
    # Merge with OPs (inner = only posts with both OP + comments)
    df = ops.merge(cm_agg, on="post_id", how="inner")
    df["delta_pol"] = df["polarity"] - df["mean_cmt_polarity"]
    df["delta_vader"] = df["vader_compound"] - df["mean_cmt_vader"]
    return df


def cluster_bootstrap(df, b=2000, seed=42):
    """Cluster-bootstrap on post_id: resample posts WITH replacement.

    Returns:
        For TextBlob and VADER separately:
        point_estimate, lower_CI, upper_CI, bootstrap_p_two_sided
    """
    rng = np.random.default_rng(seed)
    n = len(df)
    delta_pol_arr = df["delta_pol"].to_numpy()
    delta_vader_arr = df["delta_vader"].to_numpy()

    pol_means = []
    vader_means = []
    for _ in range(b):
        idx = rng.integers(0, n, n)
        pol_means.append(np.nanmean(delta_pol_arr[idx]))
        vader_means.append(np.nanmean(delta_vader_arr[idx]))
    pol_means = np.array(pol_means)
    vader_means = np.array(vader_means)

    # Point estimates from the actual data
    pol_point = np.nanmean(delta_pol_arr)
    vader_point = np.nanmean(delta_vader_arr)

    # 95% percentile CIs
    pol_ci = (np.percentile(pol_means, 2.5), np.percentile(pol_means, 97.5))
    vader_ci = (np.percentile(vader_means, 2.5), np.percentile(vader_means, 97.5))

    # Two-sided bootstrap p-value: 2 * min(frac > 0, frac < 0)
    pol_p = 2 * min((pol_means > 0).mean(), (pol_means < 0).mean())
    vader_p = 2 * min((vader_means > 0).mean(), (vader_means < 0).mean())

    return (pol_point, pol_ci[0], pol_ci[1], pol_p,
            vader_point, vader_ci[0], vader_ci[1], vader_p,
            pol_means, vader_means)


def main():
    ops, cm = load_op_and_comments()
    if ops is None or cm is None:
        print("Cannot proceed without both OPs and comments.")
        sys.exit(1)

    df = per_post_delta(ops, cm)
    print(f"\nPer-post merged: n={len(df):,} OPs with comments")

    # Drop rows with missing Δ (no comments etc.)
    df = df.dropna(subset=["delta_pol", "delta_vader"]).reset_index(drop=True)
    print(f"After dropna: n={len(df):,}")

    # T-test (matches existing analyze_op_vs_reply.py)
    t_pol, p_pol = stats.ttest_1samp(df["delta_pol"], 0)
    t_vader, p_vader = stats.ttest_1samp(df["delta_vader"], 0)

    # Cluster bootstrap (B=2,000)
    print("Running cluster bootstrap (B=2,000)...")
    (pol_point, pol_lo, pol_hi, pol_boot_p,
     vader_point, vader_lo, vader_hi, vader_boot_p, _, _) = cluster_bootstrap(df, b=2000, seed=42)

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 1 OP-VS-REPLY CLUSTER BOOTSTRAP (R17++ Agent 1 C1 strengthener)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("R17++ context: earlier drafts of PAPER_1_LOCKED_RESULTS_FINAL.md and")
    out_lines.append("PAPER_1_DRAFT_READY.md attributed 'cluster-bootstrap p≈0' to the OP-vs-Reply")
    out_lines.append("test with fabricated CIs ([−0.019, −0.014] for TB; [+0.212, +0.230] for VADER).")
    out_lines.append("The actual analyze_op_vs_reply.py implements only stats.ttest_1samp on per-post")
    out_lines.append("Δ means — NO cluster bootstrap. R17++ Agent 1 C1 flagged this as an integrity")
    out_lines.append("issue. This script provides the proper cluster-bootstrap (Cameron-Miller 2015)")
    out_lines.append("with REAL CIs, cluster unit = post_id, B=2,000 resamples with replacement.")
    out_lines.append("")
    out_lines.append(f"Sample: n={len(df):,} posts with both OP polarity and ≥1 comment")
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("RESULTS")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append(f"{'Test':25} {'point':>10} {'cluster-boot CI':>25} {'boot p':>12} {'t-test p':>12}")
    out_lines.append("-" * 85)
    out_lines.append(f"  {'TextBlob Δ (OP−reply)':25} {pol_point:+10.4f} "
                       f"{f'[{pol_lo:+.4f}, {pol_hi:+.4f}]':>25} "
                       f"{pol_boot_p:>12.4f} {p_pol:>12.2e}")
    out_lines.append(f"  {'VADER Δ (OP−reply)':25} {vader_point:+10.4f} "
                       f"{f'[{vader_lo:+.4f}, {vader_hi:+.4f}]':>25} "
                       f"{vader_boot_p:>12.4f} {p_vader:>12.2e}")
    out_lines.append("")
    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 90)
    out_lines.append(f"  TextBlob point estimate: {pol_point:+.4f}")
    out_lines.append(f"  TextBlob cluster-bootstrap CI: [{pol_lo:+.4f}, {pol_hi:+.4f}]")
    if pol_lo < 0 < pol_hi:
        out_lines.append("  TB CI INCLUDES 0 — direction uncertain at cluster-level")
    else:
        out_lines.append(f"  TB CI does NOT include 0 — directional finding is cluster-bootstrap robust")
    out_lines.append("")
    out_lines.append(f"  VADER point estimate: {vader_point:+.4f}")
    out_lines.append(f"  VADER cluster-bootstrap CI: [{vader_lo:+.4f}, {vader_hi:+.4f}]")
    if vader_lo < 0 < vader_hi:
        out_lines.append("  VADER CI INCLUDES 0 — direction uncertain at cluster-level")
    else:
        out_lines.append("  VADER CI does NOT include 0 — directional finding is cluster-bootstrap robust")
    out_lines.append("")
    out_lines.append(f"  Magnitude ratio (|VADER|/|TB|): {abs(vader_point)/abs(pol_point):.1f}×")
    out_lines.append("")
    out_lines.append("REPLACES the fabricated CIs in earlier drafts. The proper cluster-bootstrap CIs")
    out_lines.append("above should be cited in the published version of Paper 1 §5.5.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper1_op_vs_reply_cluster_bootstrap_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(out_text)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
