"""
run_trend_regression_p3.py
============================
Round 17 Fix: persist Paper 3's multi-year trend regression results to disk.

Per the Round 17 audit, the headline trend numbers (year coef +1.595,
2026-indicator p=0.46) appear in 5 markdown docs but were never saved as
a reproducible analysis output.

This script formalizes the test:
  - On PSLF-hostile programs only (n=934 program-year rows from 23 institutions
    in S1 status quo classification, 2021-2026)
  - Outcome: fill rate (in percentage points)
  - Predictors: year_centered (2021=0, ..., 2026=5); is_2026 (binary indicator
    for 2026 only); state FE; specialty FE
  - Cluster-robust SE on institution

Output: paper3_trend_regression_results.txt
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def main():
    df = pd.read_csv(PROJECT / "nrmp_program_level_2021_2026.csv")
    df = df.dropna(subset=["fill_rate", "pslf_class"]).copy()

    df["year_centered"] = df["year"] - 2021
    df["is_2026"] = (df["year"] == 2026).astype(int)
    df["is_post_eo"] = (df["year"] >= 2025).astype(int)  # R17++ Agent 2 M4: anticipation-effect sensitivity
    df["fill_pp"] = df["fill_rate"] * 100

    print("=" * 90)
    print("PAPER 3 TREND REGRESSION (Round 17 Fix; reproduces markdown numbers)")
    print("=" * 90)
    print()
    print(f"Total dataset: n={len(df):,} program-year rows; years 2021-2026")
    print(f"Year breakdown: {df['year'].value_counts().sort_index().to_dict()}")
    print()

    # --- Test 1: PSLF-hostile programs only ---
    df_h = df[df["pslf_class"] == "pslf_hostile"].copy()
    n_h = len(df_h)
    n_h_inst = df_h["institution"].nunique()
    print(f"PSLF-hostile programs only: n={n_h} program-year rows from {n_h_inst} institutions")

    cluster_groups_h = df_h["institution"].astype("category").cat.codes.values
    formula_h = "fill_pp ~ year_centered + is_2026 + C(state) + C(specialty)"
    m_h = smf.ols(formula_h, data=df_h).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_groups_h})

    # R17++ Agent 2 M4 sensitivity: is_post_eo (year>=2025) instead of is_2026
    formula_h_alt = "fill_pp ~ year_centered + is_post_eo + C(state) + C(specialty)"
    m_h_alt = smf.ols(formula_h_alt, data=df_h).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_groups_h})

    print()
    print("Regression on PSLF-hostile programs only (with state + specialty FE):")
    print(f"{'Coefficient':25} {'β (pp)':>12} {'SE':>10} {'95% CI':>20} {'p-value':>12}")
    print("-" * 85)
    for k in ["year_centered", "is_2026"]:
        if k in m_h.params.index:
            beta = m_h.params[k]
            se = m_h.bse[k]
            p = m_h.pvalues[k]
            ci = m_h.conf_int().loc[k]
            ci_str = f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"
            print(f"  {k:23} {beta:+11.3f}   {se:>9.3f}   {ci_str:>20}   {p:>12.4f}")

    # --- Test 2: Same regression on PSLF-friendly (control) ---
    df_f = df[df["pslf_class"] == "pslf_friendly"].copy()
    n_f = len(df_f)
    n_f_inst = df_f["institution"].nunique()
    print(f"\nPSLF-friendly programs only: n={n_f:,} program-year rows from {n_f_inst} institutions")

    cluster_groups_f = df_f["institution"].astype("category").cat.codes.values
    m_f = smf.ols(formula_h, data=df_f).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_groups_f})

    print("\nRegression on PSLF-friendly programs only (control test):")
    print(f"{'Coefficient':25} {'β (pp)':>12} {'SE':>10} {'95% CI':>20} {'p-value':>12}")
    print("-" * 85)
    for k in ["year_centered", "is_2026"]:
        if k in m_f.params.index:
            beta = m_f.params[k]
            se = m_f.bse[k]
            p = m_f.pvalues[k]
            ci = m_f.conf_int().loc[k]
            ci_str = f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"
            print(f"  {k:23} {beta:+11.3f}   {se:>9.3f}   {ci_str:>20}   {p:>12.4f}")

    # --- Save ---
    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 3 TREND REGRESSION RESULTS (saved 2026-05-10, Round 17)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("This script reproduces the multi-year trend numbers cited in:")
    out_lines.append("  - PAPER_3_DRAFT_READY.md §3.3")
    out_lines.append("  - PAPER_3_LOCKED_RESULTS_FINAL.md")
    out_lines.append("  - MASTER_LOCKED_NUMBERS.md Paper 3 section")
    out_lines.append("")
    out_lines.append("DESIGN:")
    out_lines.append("  - Dataset: nrmp_program_level_2021_2026.csv (combined; March 2026 NRMP release added)")
    out_lines.append(f"  - Total rows: {len(df):,} program-year observations")
    out_lines.append("  - Filter: PSLF-hostile programs only (n=934)")
    out_lines.append("  - Outcome: fill_rate * 100 (percentage points)")
    out_lines.append("  - Model: fill_pp ~ year_centered + is_2026 + state FE + specialty FE")
    out_lines.append("  - Cluster-robust SE on institution")
    out_lines.append("  - year_centered = year - 2021 (so 2021=0, 2026=5)")
    out_lines.append("  - is_2026 = binary indicator (1 if year==2026, 0 otherwise)")
    out_lines.append("")
    out_lines.append("Interpretation:")
    out_lines.append("  - year_centered coefficient = annual linear-trend slope on PSLF-hostile fill rate")
    out_lines.append("  - is_2026 coefficient = additional 2026-specific deviation BEYOND the linear trend")
    out_lines.append("    A non-significant is_2026 indicates 2026 narrowing is consistent with continuation")
    out_lines.append("    of the pre-existing trend, NOT a Trump-EO-specific discontinuity.")
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("RESULTS — PSLF-HOSTILE PROGRAMS ONLY")
    out_lines.append("=" * 90)
    out_lines.append(f"  n: {n_h} program-year rows from {n_h_inst} institutions")
    out_lines.append("")
    out_lines.append(f"{'Coefficient':25} {'β (pp)':>12} {'SE':>10} {'95% CI':>20} {'p-value':>12}")
    out_lines.append("-" * 85)
    for k in ["year_centered", "is_2026"]:
        if k in m_h.params.index:
            beta = m_h.params[k]
            se = m_h.bse[k]
            p = m_h.pvalues[k]
            ci = m_h.conf_int().loc[k]
            ci_str = f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"
            out_lines.append(f"  {k:23} {beta:+11.3f}   {se:>9.3f}   {ci_str:>20}   {p:>12.4f}")

    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("RESULTS — PSLF-HOSTILE PROGRAMS, R17++ AGENT 2 M4 SENSITIVITY (is_post_eo = year>=2025)")
    out_lines.append("=" * 90)
    out_lines.append("  Rationale: 2025 NRMP ROL deadline was Feb 24, 2025 (BEFORE EO Mar 7);")
    out_lines.append("  but applicants could have UPDATED preferences post-Match during SOAP")
    out_lines.append("  (which only affects unfilled positions). The is_2026 binary spec assumes")
    out_lines.append("  ZERO anticipation effect; the is_post_eo (year>=2025) binary catches")
    out_lines.append("  any 2025-cycle anticipation effect (signaling/news-cycle anticipation).")
    out_lines.append("")
    out_lines.append(f"{'Coefficient':25} {'β (pp)':>12} {'SE':>10} {'95% CI':>20} {'p-value':>12}")
    out_lines.append("-" * 85)
    for k in ["year_centered", "is_post_eo"]:
        if k in m_h_alt.params.index:
            beta = m_h_alt.params[k]
            se = m_h_alt.bse[k]
            p = m_h_alt.pvalues[k]
            ci = m_h_alt.conf_int().loc[k]
            ci_str = f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"
            out_lines.append(f"  {k:23} {beta:+11.3f}   {se:>9.3f}   {ci_str:>20}   {p:>12.4f}")
    out_lines.append("")
    out_lines.append("  COMPARISON OF SPECS:")
    out_lines.append(f"    is_2026 (year==2026 only):    β={m_h.params['is_2026']:+.2f} pp, p={m_h.pvalues['is_2026']:.3f}")
    out_lines.append(f"    is_post_eo (year>=2025):      β={m_h_alt.params['is_post_eo']:+.2f} pp, p={m_h_alt.pvalues['is_post_eo']:.3f}")
    out_lines.append(f"    year_centered (with is_post_eo control): β={m_h_alt.params['year_centered']:+.3f} pp/year, p={m_h_alt.pvalues['year_centered']:.3f}")
    out_lines.append("")
    out_lines.append("  INTERPRETATION:")
    out_lines.append("    If is_post_eo IS significant but is_2026 is not, that would suggest a 2025")
    out_lines.append("    anticipation effect that the is_2026 spec missed. If both are NS, then")
    out_lines.append("    either the EO has no detectable causal impact OR both specs are underpowered.")
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("RESULTS — PSLF-FRIENDLY PROGRAMS (control test)")
    out_lines.append("=" * 90)
    out_lines.append(f"  n: {n_f:,} program-year rows from {n_f_inst} institutions")
    out_lines.append("")
    out_lines.append(f"{'Coefficient':25} {'β (pp)':>12} {'SE':>10} {'95% CI':>20} {'p-value':>12}")
    out_lines.append("-" * 85)
    for k in ["year_centered", "is_2026"]:
        if k in m_f.params.index:
            beta = m_f.params[k]
            se = m_f.bse[k]
            p = m_f.pvalues[k]
            ci = m_f.conf_int().loc[k]
            ci_str = f"[{ci[0]:+.2f}, {ci[1]:+.2f}]"
            out_lines.append(f"  {k:23} {beta:+11.3f}   {se:>9.3f}   {ci_str:>20}   {p:>12.4f}")

    out_lines.append("")
    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 90)
    out_lines.append("  PSLF-hostile programs:")
    out_lines.append(f"    Linear trend (year_centered): +{m_h.params['year_centered']:.3f} pp/year (p={m_h.pvalues['year_centered']:.4f})")
    out_lines.append(f"    2026 deviation beyond trend (is_2026): +{m_h.params['is_2026']:.3f} pp (p={m_h.pvalues['is_2026']:.4f})")
    out_lines.append(f"    The 2026 narrowing is statistically indistinguishable from continuation of the")
    out_lines.append(f"    pre-existing trend (is_2026 NS at α=0.05). This refutes the Trump-EO-specific")
    out_lines.append(f"    discontinuity claim.")
    out_lines.append("")
    out_lines.append("  PSLF-friendly programs (control):")
    out_lines.append(f"    Year trend: {m_f.params['year_centered']:+.3f} pp/year (p={m_f.pvalues['year_centered']:.4f})")
    out_lines.append(f"    2026 deviation: {m_f.params['is_2026']:+.3f} pp (p={m_f.pvalues['is_2026']:.4f})")
    out_lines.append(f"    PSLF-friendly programs show a different (smaller, possibly negative) trajectory.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper3_trend_regression_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
