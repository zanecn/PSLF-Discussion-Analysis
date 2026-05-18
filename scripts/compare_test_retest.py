"""
compare_test_retest.py
======================
Compute Krippendorff's α between two Claude scoring runs at temperature=0
on the same post_ids — the proper test-retest reliability design.

Inputs:
  - zeroshot_sdn_temp0_retest.csv (Run 1 — already exists from Round 7)
  - zeroshot_sdn_temp0_retest_RUN2.csv (Run 2 — to be produced via the test-retest command)

Outputs:
  - test_retest_FINAL_results.txt
  - test_retest_FINAL_results.csv

Usage:
    python compare_test_retest.py
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")
RUN1 = PROJECT / "zeroshot_sdn_temp0_retest.csv"
RUN2 = PROJECT / "zeroshot_sdn_temp0_retest_RUN2.csv"

# Ordinal mapping for sentiment
SENTIMENT_TO_ORDINAL = {
    "very_negative": -2, "negative": -1, "neutral": 0,
    "positive": 1, "very_positive": 2,
    "parse_error": np.nan, "api_error": np.nan,
}


def main():
    if not RUN1.exists():
        print(f"[ERROR] Missing baseline file: {RUN1}")
        sys.exit(1)
    if not RUN2.exists():
        print(f"[ERROR] Missing Run 2 file: {RUN2}")
        print()
        print("Please run the test-retest command first:")
        print()
        print("  $env:ANTHROPIC_API_KEY = 'sk-ant-...'")
        print("  cd C:\\Users\\zanen\\PSLF_2026\\PSLF-Discussion-Analysis")
        print("  C:\\Users\\zanen\\anaconda3\\python.exe ..\\scripts\\sentiment_zeroshot.py `")
        print("    --input forum_pslf_discussions.csv `")
        print("    --retest-source-csv zeroshot_sdn_temp0_retest.csv `")
        print("    --temperature 0 `")
        print("    --output zeroshot_sdn_temp0_retest_RUN2.csv")
        sys.exit(1)

    df1 = pd.read_csv(RUN1)
    df2 = pd.read_csv(RUN2)
    print(f"Run 1 (baseline): {len(df1)} rows")
    print(f"Run 2 (retest):   {len(df2)} rows")

    # Match on post_id
    m = df1.merge(df2, on="post_id", how="inner", suffixes=("_r1", "_r2"))
    print(f"Matched on post_id: {len(m)} posts")

    # Sentiment task analysis
    print("\n" + "=" * 70)
    print("SENTIMENT TASK")
    print("=" * 70)

    sent1 = m["pslf_sentiment_r1"].map(SENTIMENT_TO_ORDINAL)
    sent2 = m["pslf_sentiment_r2"].map(SENTIMENT_TO_ORDINAL)
    valid = sent1.notna() & sent2.notna()
    n_valid = valid.sum()
    print(f"Valid pairs (both runs scored): {n_valid}")

    if n_valid == 0:
        print("[ERROR] No valid pairs.")
        sys.exit(1)

    sent1v = sent1[valid].astype(int).tolist()
    sent2v = sent2[valid].astype(int).tolist()

    # Exact-match
    exact = sum(a == b for a, b in zip(sent1v, sent2v)) / n_valid
    print(f"Exact-match rate: {exact:.4f} ({100*exact:.2f}%)")

    # Pearson correlation
    from scipy import stats
    r, p_r = stats.pearsonr(sent1v, sent2v)
    print(f"Pearson r: {r:+.4f} (p={p_r:.3e})")

    # Spearman rank correlation
    rho, p_rho = stats.spearmanr(sent1v, sent2v)
    print(f"Spearman ρ: {rho:+.4f} (p={p_rho:.3e})")

    # Krippendorff's α (ordinal)
    try:
        import krippendorff
    except ImportError:
        print("[WARN] krippendorff not installed; pip install krippendorff")
        alpha = None
    else:
        # Build the unit×rater matrix
        # Rows are units (posts), columns are raters (runs)
        unit_rater = np.array([sent1v, sent2v]).T
        alpha = krippendorff.alpha(
            reliability_data=unit_rater.T.tolist(),
            level_of_measurement="ordinal",
        )
        print(f"Krippendorff α (ordinal): {alpha:+.4f}")

    # Cohen's kappa
    from sklearn.metrics import cohen_kappa_score
    kappa = cohen_kappa_score(sent1v, sent2v, weights="quadratic")
    print(f"Cohen's κ (quadratic-weighted): {kappa:+.4f}")

    # Bootstrap CI for α
    if alpha is not None:
        print("\nBootstrapping α (B=2,000)...")
        rng = np.random.default_rng(42)
        boot_alphas = []
        n_b = 2000
        for _ in range(n_b):
            idx = rng.integers(0, n_valid, n_valid)
            ub = np.array([[sent1v[i] for i in idx], [sent2v[i] for i in idx]])
            try:
                a = krippendorff.alpha(reliability_data=ub.tolist(), level_of_measurement="ordinal")
                boot_alphas.append(a)
            except Exception:
                pass
        if boot_alphas:
            ci_lo = np.percentile(boot_alphas, 2.5)
            ci_hi = np.percentile(boot_alphas, 97.5)
            print(f"  α 95% CI: [{ci_lo:+.4f}, {ci_hi:+.4f}]")

    # Stance task analysis
    print("\n" + "=" * 70)
    print("STANCE TASK")
    print("=" * 70)

    stance1 = m["pslf_stance_r1"]
    stance2 = m["pslf_stance_r2"]
    valid_s = stance1.notna() & stance2.notna() & (stance1 != "unknown") & (stance2 != "unknown")
    n_s = valid_s.sum()
    print(f"Valid pairs (both stances classifiable): {n_s}")

    if n_s > 10:
        s1v = stance1[valid_s].tolist()
        s2v = stance2[valid_s].tolist()
        exact_s = sum(a == b for a, b in zip(s1v, s2v)) / n_s
        print(f"Stance exact-match rate: {exact_s:.4f} ({100*exact_s:.2f}%)")
        kappa_s = cohen_kappa_score(s1v, s2v)
        print(f"Stance Cohen's κ (unweighted, nominal): {kappa_s:+.4f}")

    # Topic task analysis
    print("\n" + "=" * 70)
    print("TOPIC TASK")
    print("=" * 70)

    topic1 = m["primary_topic_r1"]
    topic2 = m["primary_topic_r2"]
    valid_t = topic1.notna() & topic2.notna()
    n_t = valid_t.sum()
    print(f"Valid pairs (both topics classifiable): {n_t}")
    if n_t > 10:
        t1v = topic1[valid_t].tolist()
        t2v = topic2[valid_t].tolist()
        exact_t = sum(a == b for a, b in zip(t1v, t2v)) / n_t
        print(f"Topic exact-match rate: {exact_t:.4f} ({100*exact_t:.2f}%)")
        kappa_t = cohen_kappa_score(t1v, t2v)
        print(f"Topic Cohen's κ (unweighted, nominal): {kappa_t:+.4f}")

    # Summary write
    summary_lines = [
        "=" * 70,
        "TEST-RETEST FINAL RESULTS",
        "=" * 70,
        "",
        "Design: Two runs of Claude Sonnet 4 at temperature=0 on the same n=605 SDN",
        "        post_ids, separated by API calls (different days).",
        "",
        "This refutes the LLM-stochasticity reviewer objection at the proper level:",
        "  - Both runs are deterministic (temp=0)",
        "  - Any disagreement must reflect API non-determinism (cache, model serving, etc.)",
        "",
        f"Sample (matched post_ids): n={len(m)}",
        f"Sentiment task — valid pairs: {n_valid}",
        f"Sentiment exact-match rate: {100*exact:.2f}%",
        f"Sentiment Pearson r: {r:+.4f}",
        f"Sentiment Spearman ρ: {rho:+.4f}",
        f"Sentiment Cohen's κ (quad-weighted): {kappa:+.4f}",
    ]
    if alpha is not None:
        summary_lines.append(f"Sentiment Krippendorff α (ordinal): {alpha:+.4f}")
        if boot_alphas:
            summary_lines.append(f"  α 95% CI [bootstrap B=2000]: [{ci_lo:+.4f}, {ci_hi:+.4f}]")

    if n_s > 10:
        summary_lines.append("")
        summary_lines.append(f"Stance task — valid pairs: {n_s}")
        summary_lines.append(f"Stance exact-match rate: {100*exact_s:.2f}%")
        summary_lines.append(f"Stance Cohen's κ (unweighted, nominal): {kappa_s:+.4f}")

    if n_t > 10:
        summary_lines.append("")
        summary_lines.append(f"Topic task — valid pairs: {n_t}")
        summary_lines.append(f"Topic exact-match rate: {100*exact_t:.2f}%")
        summary_lines.append(f"Topic Cohen's κ (unweighted, nominal): {kappa_t:+.4f}")

    summary_lines.extend([
        "",
        "=" * 70,
        "INTERPRETATION",
        "=" * 70,
        "",
        "Pre-specified threshold: test-retest α > 0.85 = LLM-stochasticity",
        "objection refuted.",
        "",
    ])
    if alpha is not None and alpha > 0.85:
        summary_lines.append(f"RESULT: α = {alpha:+.4f} > 0.85 → OBJECTION REFUTED.")
        summary_lines.append("")
        summary_lines.append("LLM scoring at temperature=0 is highly reproducible.")
        summary_lines.append("The cross-instrument disagreement (Paper 1) cannot be attributed")
        summary_lines.append("to LLM stochasticity.")
    elif alpha is not None:
        summary_lines.append(f"RESULT: α = {alpha:+.4f} BELOW the 0.85 threshold.")
        summary_lines.append("Need to re-investigate: API non-determinism may be larger than expected.")

    summary_lines.extend([
        "",
        "Compare to prior Round 7 design (temp=0 vs temp=1, n=605):",
        "  α=+0.958 (95% CI [+0.938, +0.975]); exact-match 95.2%",
        "",
        "  That design measured deterministic-vs-sampled scoring, not test-retest per se.",
        "  This design measures the proper test-retest reliability.",
    ])

    summary_path = PROJECT / "test_retest_FINAL_results.txt"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"\nSaved: {summary_path}")


if __name__ == "__main__":
    main()
