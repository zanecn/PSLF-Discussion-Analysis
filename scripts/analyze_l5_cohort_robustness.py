"""
analyze_l5_cohort_robustness.py
================================
L5: Cross-validate cohort heterogeneity finding using ALTERNATIVE classifiers
to test instrument-conditional sensitivity.

Test combinations:
  Sentiment proxy: Claude pslf_sentiment vs TextBlob polarity vs VADER compound
  Stance proxy: Claude pslf_stance (pursuing/considering) vs polarity-extreme proxy

For each cohort, compute:
  OR_1 (TB-neg × Claude-pursuing) — original
  OR_2 (VADER-neg × Claude-pursuing) — VADER as sentiment
  OR_3 (Claude-neg × Claude-pursuing) — original Round 9
  OR_4 (TB-neg × Claude-rejecting-only) — alternative stance definition

If all 4 ORs agree on direction within cohort -> ROBUST.
If they disagree -> cohort heterogeneity is instrument-dependent.

Output: l5_cohort_robustness_results.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

from sentiment_triangulation import load_zeroshot, attach_textblob_vader
from analyze_mediation_career_stage import PROF_TO_COHORT

OUT_TXT = "l5_cohort_robustness_results.txt"
OUT_CSV = "l5_cohort_robustness_results.csv"


def compute_or_simple(neg_arr, pur_arr):
    a = ((neg_arr == 1) & (pur_arr == 1)).sum()
    b = ((neg_arr == 1) & (pur_arr == 0)).sum()
    c = ((neg_arr == 0) & (pur_arr == 1)).sum()
    d = ((neg_arr == 0) & (pur_arr == 0)).sum()
    if min(a, b, c, d) < 1:
        # Haldane-Anscombe
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    or_val = (a * d) / (b * c)
    log_or = np.log(or_val)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    return float(or_val), float(np.exp(log_or - 1.96*se)), float(np.exp(log_or + 1.96*se))


def main():
    print("=" * 80)
    print("L5: Cohort heterogeneity ROBUSTNESS to instrument choice")
    print("=" * 80)

    zs = load_zeroshot()
    m = attach_textblob_vader(zs)
    m["post_id"] = m["post_id"].astype(str)

    # Re-merge profession from source CSVs
    text_frames = []
    for f, prof_col, id_col in [
        ("reddit_professions_pslf.csv", "profession", "id"),
        ("reddit_arctic_shift_pslf.csv", "profession", "id"),
        ("reddit_new_subs_pslf.csv", "profession", "id"),
    ]:
        if not os.path.exists(f): continue
        try: d = pd.read_csv(f, usecols=lambda c: c in (id_col, prof_col))
        except: continue
        if id_col != "post_id": d = d.rename(columns={id_col: "post_id"})
        d["post_id"] = d["post_id"].astype(str)
        text_frames.append(d[["post_id", "profession"]])
    profs = pd.concat(text_frames, ignore_index=True).drop_duplicates("post_id")
    df = m.merge(profs, on="post_id", how="left")
    df["profession"] = df["profession"].fillna("").astype(str)
    df["cohort"] = df["profession"].map(PROF_TO_COHORT).fillna("Other")
    if "source" in df.columns:
        df.loc[df["source"].fillna("").astype(str).str.lower() == "sdn", "cohort"] = "SDN (Medical)"
    df = df.dropna(subset=["pslf_sentiment", "pslf_stance"])
    df = df[~df["pslf_stance"].isin(["unknown"])]

    # Build the four sentiment + stance flags
    df["claude_neg"] = df["pslf_sentiment"].isin(["very_negative", "negative"]).astype(int)
    df["claude_pur"] = df["pslf_stance"].isin(["pursuing", "considering"]).astype(int)
    df["claude_pur_only"] = df["pslf_stance"].isin(["pursuing"]).astype(int)
    df["claude_rej"] = df["pslf_stance"].isin(["rejecting"]).astype(int)
    df["claude_pur_or_completed"] = df["pslf_stance"].isin(["pursuing", "considering", "completed"]).astype(int)

    # TextBlob negative: polarity < -0.05 (standard threshold)
    df["tb_neg"] = (df["polarity"] < -0.05).astype(int)
    # VADER negative: compound < -0.05
    if "vader_compound" in df.columns:
        df["vader_neg"] = (df["vader_compound"] < -0.05).astype(int)
        has_vader = True
    else:
        has_vader = False

    cohorts = ["Reddit r/PSLF", "SDN (Medical)", "Reddit Finance",
                "Reddit r/StudentLoans", "Reddit Medical"]

    rows = []
    for cohort in cohorts:
        sub = df[df["cohort"] == cohort]
        if len(sub) < 100: continue

        # OR_3 (original): Claude-neg x Claude-pur
        or_val, lo, hi = compute_or_simple(sub["claude_neg"].values, sub["claude_pur"].values)
        rows.append({"cohort": cohort, "spec": "Claude-neg x Claude-pur (original)",
                      "n": len(sub), "OR": or_val, "ci_lo": lo, "ci_hi": hi,
                      "direction": "OR>1" if or_val > 1 else "OR<1"})

        # OR_1 (TB-neg x Claude-pur)
        or_val, lo, hi = compute_or_simple(sub["tb_neg"].values, sub["claude_pur"].values)
        rows.append({"cohort": cohort, "spec": "TB-neg x Claude-pur",
                      "n": len(sub), "OR": or_val, "ci_lo": lo, "ci_hi": hi,
                      "direction": "OR>1" if or_val > 1 else "OR<1"})

        # OR_2 (VADER-neg x Claude-pur)
        if has_vader:
            or_val, lo, hi = compute_or_simple(sub["vader_neg"].values, sub["claude_pur"].values)
            rows.append({"cohort": cohort, "spec": "VADER-neg x Claude-pur",
                          "n": len(sub), "OR": or_val, "ci_lo": lo, "ci_hi": hi,
                          "direction": "OR>1" if or_val > 1 else "OR<1"})

        # OR_4 (Claude-neg x Claude-pursuing-only [no considering])
        or_val, lo, hi = compute_or_simple(sub["claude_neg"].values, sub["claude_pur_only"].values)
        rows.append({"cohort": cohort, "spec": "Claude-neg x Claude-pur-only",
                      "n": len(sub), "OR": or_val, "ci_lo": lo, "ci_hi": hi,
                      "direction": "OR>1" if or_val > 1 else "OR<1"})

        # OR_5 (Claude-neg x Claude-pursuing-OR-completed)
        or_val, lo, hi = compute_or_simple(sub["claude_neg"].values,
                                              sub["claude_pur_or_completed"].values)
        rows.append({"cohort": cohort, "spec": "Claude-neg x Claude-pur-or-completed",
                      "n": len(sub), "OR": or_val, "ci_lo": lo, "ci_hi": hi,
                      "direction": "OR>1" if or_val > 1 else "OR<1"})

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Print + write
    print(f"\n{'cohort':<22s} {'spec':<40s} {'n':>5s} {'OR':>8s} {'95% CI':>20s}")
    for _, r in out.iterrows():
        ci = f"[{r['ci_lo']:.2f},{r['ci_hi']:.2f}]"
        print(f"{r['cohort']:<22s} {r['spec']:<40s} {r['n']:>5} {r['OR']:>8.3f} {ci:>20s}")

    # Direction concordance per cohort
    print("\n" + "=" * 80)
    print("CONCORDANCE: do all spec combinations agree on direction within cohort?")
    print("=" * 80)
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("L5 COHORT HETEROGENEITY ROBUSTNESS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'cohort':<22s} {'spec':<40s} {'n':>5s} {'OR':>8s} {'CI':>20s} {'dir':>5s}\n")
        for _, r in out.iterrows():
            ci = f"[{r['ci_lo']:.2f},{r['ci_hi']:.2f}]"
            f.write(f"{r['cohort']:<22s} {r['spec']:<40s} {r['n']:>5} {r['OR']:>8.3f} "
                    f"{ci:>20s} {r['direction']:>5s}\n")

        f.write("\nDIRECTION CONCORDANCE PER COHORT\n")
        f.write("-" * 80 + "\n")
        for cohort in cohorts:
            sub = out[out["cohort"] == cohort]
            if len(sub) == 0: continue
            n_gt1 = (sub["direction"] == "OR>1").sum()
            n_lt1 = (sub["direction"] == "OR<1").sum()
            verdict = "CONCORDANT" if (n_gt1 == 0 or n_lt1 == 0) else "DISCORDANT"
            f.write(f"  {cohort:<22s} {n_gt1} OR>1 / {n_lt1} OR<1 -> {verdict}\n")
            print(f"  {cohort:<22s} {n_gt1} OR>1 / {n_lt1} OR<1 -> {verdict}")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        concordant_cohorts = []
        for cohort in cohorts:
            sub = out[out["cohort"] == cohort]
            if len(sub) == 0: continue
            n_gt1 = (sub["direction"] == "OR>1").sum()
            n_lt1 = (sub["direction"] == "OR<1").sum()
            if n_gt1 == 0 or n_lt1 == 0:
                concordant_cohorts.append(cohort)
        f.write(f"\nCohorts with CONCORDANT direction across all instrument choices: {len(concordant_cohorts)}/{len(cohorts)}\n")
        for c in concordant_cohorts:
            f.write(f"  - {c}\n")
        f.write("\nThe cohort heterogeneity finding holds robustly when all instrument\n")
        f.write("choices agree on direction. For cohorts where direction is sensitive\n")
        f.write("to instrument choice, the magnitude finding should be reported with\n")
        f.write("explicit acknowledgment of which specs flip.\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")


if __name__ == "__main__":
    main()
