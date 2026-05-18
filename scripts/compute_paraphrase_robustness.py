"""
compute_paraphrase_robustness.py
==================================
Round 16 Strengthener 2 final analysis: compute K-α across the original
temperature=0 baseline and two paraphrase variants.

Inputs:
  - zeroshot_sdn_temp0_retest.csv (Round 7 baseline; original prompt)
  - zeroshot_sdn_paraphrase_v1.csv (paraphrase 1)
  - zeroshot_sdn_paraphrase_v2.csv (paraphrase 2)

Outputs:
  - paper1_paraphrase_robustness_results.txt
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

SENTIMENT_TO_ORDINAL = {
    "very_negative": 0, "negative": 1, "neutral": 2,
    "positive": 3, "very_positive": 4,
}


def main():
    baseline = pd.read_csv(PROJECT / "zeroshot_sdn_temp0_retest.csv")
    p1_path = PROJECT / "zeroshot_sdn_paraphrase_v1.csv"
    p2_path = PROJECT / "zeroshot_sdn_paraphrase_v2.csv"

    if not p1_path.exists():
        print(f"[ERROR] Missing {p1_path}")
        print("Run: python scripts/sentiment_zeroshot_paraphrase.py --prompt-variant 1 ...")
        sys.exit(1)
    if not p2_path.exists():
        print(f"[ERROR] Missing {p2_path}")
        print("Run: python scripts/sentiment_zeroshot_paraphrase.py --prompt-variant 2 ...")
        sys.exit(1)

    p1 = pd.read_csv(p1_path)
    p2 = pd.read_csv(p2_path)
    print(f"Baseline: {len(baseline)}; Paraphrase 1: {len(p1)}; Paraphrase 2: {len(p2)}")

    # Add ordinal columns
    for d, name in [(baseline, "base"), (p1, "p1"), (p2, "p2")]:
        d[f"{name}_ord"] = d["pslf_sentiment"].map(SENTIMENT_TO_ORDINAL)

    # Merge on post_id
    m = baseline[["post_id", "base_ord", "pslf_stance", "primary_topic"]].rename(
        columns={"pslf_stance": "base_stance", "primary_topic": "base_topic"}
    ).merge(
        p1[["post_id", "p1_ord", "pslf_stance", "primary_topic"]].rename(
            columns={"pslf_stance": "p1_stance", "primary_topic": "p1_topic"}),
        on="post_id"
    ).merge(
        p2[["post_id", "p2_ord", "pslf_stance", "primary_topic"]].rename(
            columns={"pslf_stance": "p2_stance", "primary_topic": "p2_topic"}),
        on="post_id"
    )
    m = m.dropna(subset=["base_ord", "p1_ord", "p2_ord"])
    n = len(m)
    print(f"3-way merge: n={n}")

    # ===== SENTIMENT TASK =====
    print("\n" + "=" * 70)
    print("SENTIMENT TASK — paraphrase robustness")
    print("=" * 70)
    pairs = [
        ("Baseline vs Paraphrase 1", "base_ord", "p1_ord"),
        ("Baseline vs Paraphrase 2", "base_ord", "p2_ord"),
        ("Paraphrase 1 vs 2", "p1_ord", "p2_ord"),
    ]

    from sklearn.metrics import cohen_kappa_score
    from scipy import stats
    try:
        import krippendorff
        has_kripp = True
    except ImportError:
        has_kripp = False

    rows = []
    for name, c1, c2 in pairs:
        em = (m[c1] == m[c2]).mean()
        r, _ = stats.pearsonr(m[c1].astype(float), m[c2].astype(float))
        kappa = cohen_kappa_score(m[c1].astype(int), m[c2].astype(int), weights="quadratic")
        print(f"  {name:35} exact_match={em:.4f}  r={r:+.4f}  κ_quad={kappa:+.4f}")
        rows.append({"pair": name, "exact_match": em, "pearson_r": r, "kappa_quad": kappa})

    if has_kripp:
        # 3-rater K-α (ordinal) across baseline + 2 paraphrases
        data = [m["base_ord"].astype(int).tolist(),
                m["p1_ord"].astype(int).tolist(),
                m["p2_ord"].astype(int).tolist()]
        alpha = krippendorff.alpha(reliability_data=data, level_of_measurement="ordinal")
        print(f"\n  3-prompt Krippendorff α (sentiment, ordinal): {alpha:+.4f}")

        # Bootstrap CI
        rng = np.random.default_rng(42)
        boots = []
        for _ in range(2000):
            idx = rng.integers(0, n, n)
            db = [[d[i] for i in idx] for d in data]
            try:
                boots.append(krippendorff.alpha(reliability_data=db, level_of_measurement="ordinal"))
            except Exception:
                pass
        if boots:
            lo, hi = np.percentile(boots, 2.5), np.percentile(boots, 97.5)
            print(f"  Bootstrap 95% CI [B={len(boots)}]: [{lo:+.4f}, {hi:+.4f}]")
        else:
            lo, hi = np.nan, np.nan

    # ===== STANCE TASK =====
    print("\n" + "=" * 70)
    print("STANCE TASK — paraphrase robustness")
    print("=" * 70)
    valid_s = m["base_stance"].notna() & m["p1_stance"].notna() & m["p2_stance"].notna() & \
              (m["base_stance"] != "unknown") & (m["p1_stance"] != "unknown") & (m["p2_stance"] != "unknown")
    n_s = valid_s.sum()
    print(f"  Valid stance pairs: {n_s}")
    if n_s > 10:
        for name, c1, c2 in [("Baseline vs P1", "base_stance", "p1_stance"),
                              ("Baseline vs P2", "base_stance", "p2_stance"),
                              ("P1 vs P2", "p1_stance", "p2_stance")]:
            sub = m[valid_s]
            em = (sub[c1] == sub[c2]).mean()
            kappa = cohen_kappa_score(sub[c1], sub[c2])
            print(f"  {name:35} exact_match={em:.4f}  κ={kappa:+.4f}")

    # ===== TOPIC TASK =====
    print("\n" + "=" * 70)
    print("TOPIC TASK — paraphrase robustness")
    print("=" * 70)
    valid_t = m["base_topic"].notna() & m["p1_topic"].notna() & m["p2_topic"].notna()
    n_t = valid_t.sum()
    print(f"  Valid topic pairs: {n_t}")
    if n_t > 10:
        for name, c1, c2 in [("Baseline vs P1", "base_topic", "p1_topic"),
                              ("Baseline vs P2", "base_topic", "p2_topic"),
                              ("P1 vs P2", "p1_topic", "p2_topic")]:
            sub = m[valid_t]
            em = (sub[c1] == sub[c2]).mean()
            kappa = cohen_kappa_score(sub[c1], sub[c2])
            print(f"  {name:35} exact_match={em:.4f}  κ={kappa:+.4f}")

    # ===== n=200 HISTORICAL COMPARISON (locked baseline; see ..._n200_historical.csv backups) =====
    N200_ALPHA = 0.9011
    N200_LO, N200_HI = 0.8571, 0.9380
    THRESHOLD = 0.85

    # ===== SAVE =====
    out_lines = [
        "=" * 70,
        "PARAPHRASE ROBUSTNESS RESULTS (R16 Strengthener 2; R17 Fix C2; R17++ #3 n=400 replication 2026-05-17)",
        "=" * 70,
        "",
        f"Design: re-score n={n} SDN posts with Claude Sonnet 4 at temperature=0",
        "        using THREE different system prompts (semantically identical, ",
        "        worded differently). Tests robustness to LEXICAL-FORMAT paraphrase",
        "        (NOT semantic-restructuring or task-redefinition; see Paper 1 L0b).",
        "",
        f"Sample: n={n} posts (3-way merge across baseline + 2 paraphrases)",
        f"Pool: 615 SDN posts in zeroshot_sdn_temp0_retest.csv; deterministic sample with random_state=42",
        "",
        "INTERPRETATION:",
        "  - If α > 0.85: Claude classifications are robust to lexical-format prompt phrasing.",
        "  - If α < 0.85: Classifications depend on prompt phrasing.",
        "",
        "RESULTS — SENTIMENT TASK (5-level ordinal):",
    ]
    if has_kripp:
        out_lines.append(f"  3-prompt Krippendorff α: {alpha:+.4f}")
        if boots:
            out_lines.append(f"  Bootstrap 95% CI [B={len(boots)}]: [{lo:+.4f}, {hi:+.4f}]")
    out_lines.append("")
    out_lines.append("  Pairwise sentiment exact-match:")
    for name, c1, c2 in pairs:
        em = (m[c1] == m[c2]).mean()
        r, _ = stats.pearsonr(m[c1].astype(float), m[c2].astype(float))
        kappa = cohen_kappa_score(m[c1].astype(int), m[c2].astype(int), weights="quadratic")
        out_lines.append(f"    {name:35} exact_match={em:.4f}  Pearson r={r:+.4f}  κ_quad={kappa:+.4f}")

    # Stance task persistence
    out_lines.append("")
    out_lines.append("RESULTS — STANCE TASK (5-class nominal):")
    if n_s > 10:
        sub = m[valid_s]
        for name, c1, c2 in [("Baseline vs Paraphrase 1", "base_stance", "p1_stance"),
                              ("Baseline vs Paraphrase 2", "base_stance", "p2_stance"),
                              ("Paraphrase 1 vs 2", "p1_stance", "p2_stance")]:
            em = (sub[c1] == sub[c2]).mean()
            kappa = cohen_kappa_score(sub[c1], sub[c2])
            out_lines.append(f"  {name:35} exact_match={em:.4f}  κ={kappa:+.4f}")
        em_vals_s = [(sub["base_stance"] == sub["p1_stance"]).mean(),
                      (sub["base_stance"] == sub["p2_stance"]).mean(),
                      (sub["p1_stance"] == sub["p2_stance"]).mean()]
        out_lines.append(f"  Stance pairwise exact-match range: {min(em_vals_s):.4f} – {max(em_vals_s):.4f}")
        out_lines.append(f"  Valid pairs (both stances classifiable): n={n_s}")

    # Topic task persistence
    out_lines.append("")
    out_lines.append("RESULTS — TOPIC TASK (7-class nominal):")
    if n_t > 10:
        sub = m[valid_t]
        for name, c1, c2 in [("Baseline vs Paraphrase 1", "base_topic", "p1_topic"),
                              ("Baseline vs Paraphrase 2", "base_topic", "p2_topic"),
                              ("Paraphrase 1 vs 2", "p1_topic", "p2_topic")]:
            em = (sub[c1] == sub[c2]).mean()
            kappa = cohen_kappa_score(sub[c1], sub[c2])
            out_lines.append(f"  {name:35} exact_match={em:.4f}  κ={kappa:+.4f}")
        em_vals_t = [(sub["base_topic"] == sub["p1_topic"]).mean(),
                      (sub["base_topic"] == sub["p2_topic"]).mean(),
                      (sub["p1_topic"] == sub["p2_topic"]).mean()]
        out_lines.append(f"  Topic pairwise exact-match range: {min(em_vals_t):.4f} – {max(em_vals_t):.4f}")
        out_lines.append(f"  Valid pairs (both topics classifiable): n={n_t}")

    # Comparison to n=200 historical baseline (R16 Strengthener 2)
    out_lines.append("")
    out_lines.append("=" * 70)
    out_lines.append("REPLICATION COMPARISON — n=200 historical vs current run")
    out_lines.append("=" * 70)
    out_lines.append(f"  n=200 (R16, locked):  α={N200_ALPHA:+.4f}  CI [{N200_LO:+.4f}, {N200_HI:+.4f}]  half-width={(N200_HI-N200_LO)/2:.4f}")
    if has_kripp and alpha is not None and boots:
        cur_hw = (hi - lo) / 2
        delta_alpha = alpha - N200_ALPHA
        delta_lo = lo - N200_LO
        out_lines.append(f"  n={n:<3} (current):       α={alpha:+.4f}  CI [{lo:+.4f}, {hi:+.4f}]  half-width={cur_hw:.4f}")
        out_lines.append(f"  Δα (current − historical):     {delta_alpha:+.4f}")
        out_lines.append(f"  Δ lower-CI bound:              {delta_lo:+.4f}  (positive = more headroom above {THRESHOLD} threshold)")
        out_lines.append(f"  CI half-width ratio (cur/n200): {cur_hw/((N200_HI-N200_LO)/2):.3f}  (expect ~0.71 if Bessel scaling at 2× sample)")
        out_lines.append(f"  Lower-CI headroom above {THRESHOLD}: n=200 = +{N200_LO-THRESHOLD:.4f}  ·  n={n} = {lo-THRESHOLD:+.4f}")

    out_lines.append("")
    out_lines.append("VERDICT:")
    if has_kripp and alpha is not None:
        if alpha > 0.85:
            out_lines.append(f"  Paraphrase-robustness CONFIRMED for sentiment task (α={alpha:+.4f} > 0.85 threshold).")
            out_lines.append(f"  Paper 1 L0b updated: 'test-retest reliability under LEXICAL-FORMAT prompt variation = α={alpha:+.4f}'.")
            if boots and lo > 0.85:
                out_lines.append(f"  Lower CI bound also above 0.85 ({lo:+.4f} > 0.85): strong replication.")
            elif boots:
                out_lines.append(f"  Lower CI bound straddles 0.85 ({lo:+.4f}): point-estimate confirms but bound is close.")
            out_lines.append(f"  CAVEAT: this tests robustness to lexical/format rewording, NOT to semantic restructuring,")
            out_lines.append(f"  task redefinition, or category reordering. Stronger prompt-design robustness remains untested.")
        else:
            out_lines.append(f"  Paraphrase-robustness NOT confirmed (α={alpha:+.4f} < 0.85).")
            out_lines.append(f"  Paper 1 L0b should be revised: 'API determinism only; prompt-sensitivity present at n={n}.'")
            out_lines.append(f"  This is a falsification of the R16 result; investigate sample composition vs n=200 historical.")

    out_path = PROJECT / "paper1_paraphrase_robustness_results.txt"
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
