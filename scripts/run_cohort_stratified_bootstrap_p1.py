"""
run_cohort_stratified_bootstrap_p1.py
======================================
R17++ Agent 1 C4 fix: cohort-stratified bootstrap for combined 3-LLM K-α.

The existing compare_multi_llm_with_sdn.py bootstrap uses simple random
resample on the combined Reddit (n=701) + SDN (n=300) sample. This means a
bootstrap iteration could draw all 1,001 from one cohort. Given Reddit-only
α=+0.69 and SDN-only α=+0.83, the simple bootstrap likely under-estimates the
combined-sample CI half-width.

This script:
1. Loads the 5-instrument intersection CSV (already produced by
   compare_multi_llm_with_sdn.py)
2. Computes the combined 3-LLM Krippendorff α point estimate
3. Bootstrap (B=2000) with stratification: within each iteration, resample
   Reddit and SDN observations SEPARATELY, then combine. This preserves the
   cohort mix in every bootstrap draw.
4. Reports stratified vs simple CI for direct comparison.

Output: paper1_cohort_stratified_bootstrap_results.txt
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def krippendorff_alpha_ordinal(data):
    """Wrapper around krippendorff library for ordinal data."""
    try:
        import krippendorff
        # Convert to nan-padded reliability_data format
        max_n = max(len(rater) for rater in data)
        reliability_data = []
        for rater in data:
            padded = list(rater) + [np.nan] * (max_n - len(rater))
            reliability_data.append(padded)
        return krippendorff.alpha(reliability_data=reliability_data, level_of_measurement="ordinal")
    except Exception:
        return np.nan


def bootstrap_simple(ratings, b=2000, seed=42):
    """Standard bootstrap: resample n observations from combined sample."""
    n = ratings.shape[0]
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(b):
        idx = rng.integers(0, n, n)
        sampled = ratings[idx]
        sampled_lists = [sampled[:, j].tolist() for j in range(ratings.shape[1])]
        a = krippendorff_alpha_ordinal(sampled_lists)
        if not np.isnan(a):
            boots.append(a)
    return np.array(boots)


def bootstrap_stratified(ratings, strata_labels, b=2000, seed=42):
    """Stratified bootstrap: within each iteration, resample observations
    SEPARATELY within each stratum, then concatenate.

    This preserves the cohort proportions (Reddit n=701 + SDN n=300 in our case)
    in every bootstrap draw, avoiding the situation where all 1,001 are drawn
    from one cohort.
    """
    rng = np.random.default_rng(seed)
    boots = []
    # Identify stratum indices
    strata = np.unique(strata_labels)
    stratum_idx = {s: np.where(strata_labels == s)[0] for s in strata}

    for _ in range(b):
        # Resample within each stratum
        sampled_indices = []
        for s in strata:
            s_idx = stratum_idx[s]
            n_s = len(s_idx)
            resampled = rng.integers(0, n_s, n_s)
            sampled_indices.append(s_idx[resampled])
        all_idx = np.concatenate(sampled_indices)
        sampled = ratings[all_idx]
        sampled_lists = [sampled[:, j].tolist() for j in range(ratings.shape[1])]
        a = krippendorff_alpha_ordinal(sampled_lists)
        if not np.isnan(a):
            boots.append(a)
    return np.array(boots)


def main():
    # Load files matching compare_multi_llm_with_sdn.py
    cl_r = pd.read_csv(PROJECT / "zeroshot_reddit_n1000.csv")
    cl_s = pd.read_csv(PROJECT / "zeroshot_sdn_n1000.csv")
    ll_r = pd.read_csv(PROJECT / "zeroshot_llama_replication.csv")
    ll_s = pd.read_csv(PROJECT / "zeroshot_llama_sdn.csv")
    ds_r = pd.read_csv(PROJECT / "zeroshot_third_llm_replication.csv")
    ds_s = pd.read_csv(PROJECT / "zeroshot_deepseek_sdn.csv")

    # Map sentiment ordinal 1..5
    sent_map = {"very_negative": 1, "negative": 2, "neutral": 3, "positive": 4, "very_positive": 5}

    # Build combined Claude (Reddit + SDN)
    cl_r["cohort"] = "Reddit"
    cl_s["cohort"] = "SDN"
    claude = pd.concat([cl_r[["post_id", "pslf_sentiment", "cohort"]],
                          cl_s[["post_id", "pslf_sentiment", "cohort"]]], ignore_index=True)
    claude["claude_int"] = claude["pslf_sentiment"].map(sent_map)

    llama = pd.concat([ll_r[["post_id", "pslf_sentiment"]],
                          ll_s[["post_id", "pslf_sentiment"]]], ignore_index=True)
    llama["llama_int"] = llama["pslf_sentiment"].map(sent_map)

    deepseek = pd.concat([ds_r[["post_id", "pslf_sentiment"]],
                            ds_s[["post_id", "pslf_sentiment"]]], ignore_index=True)
    deepseek["ds_int"] = deepseek["pslf_sentiment"].map(sent_map)

    # Merge on post_id
    df = claude.merge(llama[["post_id", "llama_int"]], on="post_id", how="inner")
    df = df.merge(deepseek[["post_id", "ds_int"]], on="post_id", how="inner")
    df = df.dropna(subset=["claude_int", "llama_int", "ds_int"]).copy()
    df = df.rename(columns={"claude_int": "sentiment_int"})
    print(f"Combined 3-LLM intersection: n={len(df)}")
    print(f"  Reddit: n={(df['cohort'] == 'Reddit').sum()}")
    print(f"  SDN:    n={(df['cohort'] == 'SDN').sum()}")

    ratings = df[["sentiment_int", "llama_int", "ds_int"]].astype(int).to_numpy()
    strata = df["cohort"].values

    # Point estimate
    point = krippendorff_alpha_ordinal([ratings[:, j].tolist() for j in range(ratings.shape[1])])
    print(f"\nPoint estimate: 3-LLM α = {point:.4f}")

    # Simple bootstrap
    print("Running SIMPLE bootstrap (B=2000)...")
    boots_simple = bootstrap_simple(ratings, b=2000, seed=42)
    ci_simple = (np.percentile(boots_simple, 2.5), np.percentile(boots_simple, 97.5))
    print(f"  Simple CI: [{ci_simple[0]:.4f}, {ci_simple[1]:.4f}]")

    # Stratified bootstrap
    print("Running STRATIFIED bootstrap (B=2000, stratified by Reddit/SDN)...")
    boots_strat = bootstrap_stratified(ratings, strata, b=2000, seed=42)
    ci_strat = (np.percentile(boots_strat, 2.5), np.percentile(boots_strat, 97.5))
    print(f"  Stratified CI: [{ci_strat[0]:.4f}, {ci_strat[1]:.4f}]")

    # CI half-widths
    hw_simple = (ci_simple[1] - ci_simple[0]) / 2
    hw_strat = (ci_strat[1] - ci_strat[0]) / 2

    # Save
    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 1 COHORT-STRATIFIED BOOTSTRAP (R17++ Agent 1 C4 fix)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append(f"5-instrument intersection: n={len(df)} (Reddit {(df['cohort'] == 'Reddit').sum()} + SDN {(df['cohort'] == 'SDN').sum()})")
    out_lines.append(f"3-LLM point estimate (Claude + Llama + DeepSeek, ordinal K-α): {point:.4f}")
    out_lines.append("")
    out_lines.append(f"{'Bootstrap method':40} {'95% CI':>25} {'Half-width':>12}")
    out_lines.append("-" * 80)
    out_lines.append(f"{'Simple (existing implementation)':40} {f'[{ci_simple[0]:.4f}, {ci_simple[1]:.4f}]':>25} {hw_simple:>10.5f}")
    out_lines.append(f"{'Stratified by cohort (R17++ NEW)':40} {f'[{ci_strat[0]:.4f}, {ci_strat[1]:.4f}]':>25} {hw_strat:>10.5f}")
    out_lines.append("")
    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 90)
    delta_hw = hw_strat - hw_simple
    out_lines.append(f"  Stratified bootstrap half-width minus simple: {delta_hw:+.5f}")
    out_lines.append("")
    if abs(delta_hw) < 0.005:
        out_lines.append("  The two bootstrap methods give essentially identical CIs (Δ < 0.005). The")
        out_lines.append("  cohort composition is preserved approximately by the simple bootstrap due to")
        out_lines.append("  the large sample size; explicit stratification provides no material benefit.")
    elif delta_hw > 0:
        out_lines.append("  The stratified bootstrap gives a WIDER CI than the simple bootstrap. The simple")
        out_lines.append("  bootstrap was slightly UNDERESTIMATING the CI half-width due to occasional")
        out_lines.append("  resamples that drew disproportionately from one cohort. Report the stratified CI.")
    else:
        out_lines.append("  The stratified bootstrap gives a NARROWER CI than the simple bootstrap. This is")
        out_lines.append("  the expected direction when stratification reduces between-cluster variance in")
        out_lines.append("  the resampling distribution. The simple-bootstrap CI is conservative; stratified")
        out_lines.append("  is the appropriate published estimate.")
    out_lines.append("")
    out_lines.append("Whichever direction, the stratified estimate is the methodologically defensible one")
    out_lines.append("for cohort-mixed samples per Hayes & Krippendorff 2007.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper1_cohort_stratified_bootstrap_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\n{out_text}")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
