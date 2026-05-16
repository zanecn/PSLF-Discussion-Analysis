"""
run_model5_with_2026_post_eo.py
=================================
Round 16 follow-up: re-run Model 5 on the combined 2021-2026 dataset, with
explicit pre-EO (2025 and earlier) vs post-EO (2026) comparison.

The Trump PSLF Executive Order was signed March 7, 2025, AFTER the 2025 NRMP
ROL deadline (Feb 24, 2025). The 2025 Match therefore reflects PRE-EO
applicant preferences. The 2026 Match (ROL deadline Feb 23, 2026, Match Day
Mar 20, 2026) is the FIRST post-EO Match cycle.

This script:
  1. Loads nrmp_program_level_2021_2026.csv
  2. Re-runs Model 5 (cluster-robust SE on institution; HCA-academic 3-spec
     sensitivity) on the full 2021-2026 sample
  3. Adds a YEAR=2026 × PSLF-class interaction to test the post-EO change
  4. Reports the pre/post EO descriptive table + the DiD-style interaction

Output: paper3_model5_with_2026_results.txt
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

HCA_ACADEMIC_PARTNERSHIPS = [
    "HCA Healthcare/USF Morsani GME-Blake",
    "HCA Healthcare/USF Morsani GME-Brandon",
    "HCA Healthcare/USF Morsani GME-Citrus",
    "HCA Healthcare/USF Morsani GME-Largo",
    "HCA Healthcare/USF Morsani GME-Oak Hill",
    "HCA Healthcare/USF Morsani GME-Sarasota",
    "HCA Healthcare/USF Morsani GME-St Pete",
    "HCA Healthcare/USF Morsani GME-Trinity",
    "HCA Healthcare/USF Morsani-Bayonet Pt",
    "HCA Healthcare/USF Morsani-Northside",
    "HCA Florida JFK Hosp-U Miami",
    "HCA Healthcare/JFK Med Center-UMiami",
    "HCA Houston Healthcare/U Houston",
    "HCA Healthcare LGH-Montgomery/VCOM",
]


def load_and_merge():
    nrmp = pd.read_csv(PROJECT / "nrmp_program_level_2021_2026.csv")
    confounders = pd.read_csv(PROJECT / "institutional_confounders.csv")
    cms = pd.read_csv(PROJECT / "cms_hospital_general.csv")

    cms = cms.rename(columns={"Hospital Ownership": "ownership", "City/Town": "city",
                                "State": "state", "Hospital overall rating": "star",
                                "Hospital Type": "hospital_type"})
    cms["star_num"] = pd.to_numeric(cms["star"], errors="coerce")
    cms["is_for_profit"] = (cms["ownership"] == "Proprietary").astype(int)
    cms_city = cms.groupby(["city", "state"]).agg(
        cms_mean_star=("star_num", "mean"),
        cms_for_profit_share=("is_for_profit", "mean"),
        cms_n_hospitals=("Facility ID", "count"),
    ).reset_index()
    cms_city["city_norm"] = cms_city["city"].str.strip().str.upper()
    cms_city["state_norm"] = cms_city["state"].str.strip().str.upper()
    # Round 17 fix: dedup case-collision duplicates (e.g., "Boston" vs "BOSTON")
    cms_city = cms_city.drop_duplicates(subset=["city_norm", "state_norm"], keep="first")
    nrmp["city_norm"] = nrmp["city"].fillna("").str.strip().str.upper()
    nrmp["state_norm"] = nrmp["state"].fillna("").str.strip().str.upper()

    df = nrmp.merge(
        cms_city[["city_norm", "state_norm", "cms_mean_star",
                   "cms_for_profit_share", "cms_n_hospitals"]],
        on=["city_norm", "state_norm"], how="left",
    )
    df = df.merge(
        confounders[["institution", "n_unique_programs", "n_specialties",
                      "annual_residents_pgy1", "university_affiliation",
                      "academic_med_center"]],
        on="institution", how="left",
    )

    nih_path = PROJECT / "nih_reporter_FY2023_state.csv"
    if nih_path.exists():
        nih = pd.read_csv(nih_path)
        nih_inst = nih.groupby("institution").agg(
            nih_total_award=("total_award_amount", "sum"),
        ).reset_index()
        df = df.merge(nih_inst, on="institution", how="left")
        df["nih_total_award"] = df["nih_total_award"].fillna(0)
    else:
        df["nih_total_award"] = 0
    df["log_nih_funding"] = np.log1p(df["nih_total_award"])
    df["log_residents"] = np.log1p(df["annual_residents_pgy1"].fillna(0))
    df = df.dropna(subset=["fill_rate", "pslf_class"]).copy()
    df["post_eo"] = (df["year"] == 2026).astype(int)
    return df


def run_spec_with_eo(df, spec_name):
    """Run M5 with year=2026 × pslf_class interaction (post-EO test).
    Returns dict with pre-EO and post-EO PSLF-hostile coefficients."""
    import statsmodels.formula.api as smf
    df = df.copy()
    df["pslf_class"] = df["pslf_class"].astype("category")
    df["pslf_class"] = df["pslf_class"].cat.set_categories(
        ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)

    needed = ["fill_rate", "pslf_class", "cms_mean_star", "cms_for_profit_share",
              "university_affiliation", "academic_med_center", "n_specialties",
              "log_residents", "log_nih_funding", "state", "specialty",
              "institution", "post_eo"]
    df_fit = df.dropna(subset=needed).copy().reset_index(drop=True)
    cluster_groups = df_fit["institution"].astype("category").cat.codes.values

    # Model with year=2026 × pslf_class interaction
    formula = ("fill_rate ~ C(pslf_class, Treatment(reference='ambiguous')) * post_eo"
               " + cms_mean_star + cms_for_profit_share"
               " + C(university_affiliation) + C(academic_med_center)"
               " + n_specialties + log_residents + log_nih_funding"
               " + C(state) + C(specialty)")

    model = smf.ols(formula, data=df_fit).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_groups}
    )

    h_pre = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]"
    h_post = ("C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]:post_eo")

    return {
        "spec": spec_name,
        "n_total": len(df_fit),
        "n_clusters": df_fit["institution"].nunique(),
        "h_pre_beta": model.params.get(h_pre, np.nan) * 100,
        "h_pre_se": model.bse.get(h_pre, np.nan) * 100,
        "h_pre_p": model.pvalues.get(h_pre, np.nan),
        "h_pre_ci_lo": model.conf_int().loc[h_pre, 0] * 100 if h_pre in model.params.index else np.nan,
        "h_pre_ci_hi": model.conf_int().loc[h_pre, 1] * 100 if h_pre in model.params.index else np.nan,
        "h_post_diff_beta": model.params.get(h_post, np.nan) * 100,
        "h_post_diff_se": model.bse.get(h_post, np.nan) * 100,
        "h_post_diff_p": model.pvalues.get(h_post, np.nan),
        "h_post_diff_ci_lo": model.conf_int().loc[h_post, 0] * 100 if h_post in model.params.index else np.nan,
        "h_post_diff_ci_hi": model.conf_int().loc[h_post, 1] * 100 if h_post in model.params.index else np.nan,
        "model": model,
    }


def main():
    df_base = load_and_merge()
    print(f"Loaded analytical dataset (2021-2026): n={len(df_base):,}")
    print(f"Year breakdown:")
    print(df_base["year"].value_counts().sort_index().to_dict())
    print()

    # ===== Descriptive: pre vs post EO =====
    print("=" * 80)
    print("DESCRIPTIVE: 2025 (pre-EO) vs 2026 (first post-EO Match) fill rates")
    print("=" * 80)
    df_25 = df_base[df_base["year"] == 2025]
    df_26 = df_base[df_base["year"] == 2026]
    desc_rows = []
    for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
        s25 = df_25[df_25["pslf_class"] == cls]
        s26 = df_26[df_26["pslf_class"] == cls]
        d_pp = (s26["fill_rate"].mean() - s25["fill_rate"].mean()) * 100
        desc_rows.append({"class": cls, "n_2025": len(s25), "fill_2025": s25["fill_rate"].mean(),
                           "n_2026": len(s26), "fill_2026": s26["fill_rate"].mean(),
                           "delta_pp": d_pp})
        print(f"  {cls:20} 2025: n={len(s25):>5,} fill={s25['fill_rate'].mean():.4f} | "
              f"2026: n={len(s26):>5,} fill={s26['fill_rate'].mean():.4f} | "
              f"Δ = {d_pp:+.2f} pp")

    # DiD (PSLF-hostile change minus PSLF-friendly change)
    d_h = next(r["delta_pp"] for r in desc_rows if r["class"] == "pslf_hostile")
    d_f = next(r["delta_pp"] for r in desc_rows if r["class"] == "pslf_friendly")
    did_descriptive = d_h - d_f
    print(f"\n  Descriptive DiD (hostile change − friendly change) = {did_descriptive:+.2f} pp")
    print(f"  Interpretation: positive DiD = PSLF-hostile programs IMPROVED relative to friendly")
    print(f"                  in the first post-EO Match cycle (consistent with EO mechanism)")

    # ===== Regression: 3 specs with year=2026 × pslf_class interaction =====
    print("\n" + "=" * 80)
    print("REGRESSION: Model 5 + (year=2026 × PSLF-class interaction); cluster-robust SE")
    print("=" * 80)

    specs = [
        ("S1: Status quo (all 23 hostile)", lambda d: d),
        ("S2: HCA-academic reclassified as ambiguous", lambda d: d.assign(
            pslf_class=d["pslf_class"].where(
                ~d["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS), "ambiguous"))),
        ("S3: Drop HCA-academic partnerships", lambda d: d[
            ~d["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS)]),
    ]
    results = []
    for spec_name, df_modify in specs:
        df = df_modify(df_base.copy())
        df["pslf_class"] = df["pslf_class"].astype("category")
        df["pslf_class"] = df["pslf_class"].cat.set_categories(
            ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)
        r = run_spec_with_eo(df, spec_name)
        results.append(r)

    print(f"\n{'Specification':50} {'Pre-EO β':>12} {'Post-EO Δ β':>14} {'Post-EO p':>12}")
    print("-" * 95)
    for r in results:
        pre_str = f"{r['h_pre_beta']:+7.2f} pp" if not np.isnan(r['h_pre_beta']) else "n/a"
        diff_str = f"{r['h_post_diff_beta']:+7.2f} pp" if not np.isnan(r['h_post_diff_beta']) else "n/a"
        p_str = f"{r['h_post_diff_p']:.3e}" if not np.isnan(r['h_post_diff_p']) else "n/a"
        print(f"  {r['spec']:48} {pre_str:>12} {diff_str:>14} {p_str:>12}")

    print()
    print("INTERPRETATION:")
    print("  Pre-EO β = PSLF-hostile coefficient (vs ambiguous reference) for years 2021-2025.")
    print("  Post-EO Δ β = additional change in PSLF-hostile coefficient in year 2026.")
    print("  If Post-EO Δ β > 0, the PSLF-hostile differential NARROWED in the first post-EO Match.")
    print("  If Post-EO Δ β = 0 (or NS), no detectable post-EO change.")
    print()
    print("  Note: The 2026 sample has only ~171 hostile program-year observations from")
    print("  ~9 institutions in S2/S3 (or ~23 in S1). Power to detect a small interaction")
    print("  is limited — interpret cautiously.")

    # Save output
    out_lines = []
    out_lines.append("=" * 80)
    out_lines.append("PAPER 3 MODEL 5 + 2026 — DESCRIPTIVE 6-YEAR EXTENSION (Round 17+ revised)")
    out_lines.append("=" * 80)
    out_lines.append("")
    out_lines.append("*** Round 17+ retraction: This file is DESCRIPTIVE only. ***")
    out_lines.append("The 2026-vs-2021-2025 difference does NOT identify a causal Trump EO effect:")
    out_lines.append("  - Linear trend regression: year_centered = +1.6 pp/year (p=0.105)")
    out_lines.append("  - is_2026 indicator beyond linear trend = +2.98 pp (p=0.46, NS)")
    out_lines.append("  - 95% CI on is_2026: [−4.96, +10.92] pp — design lacks power to distinguish")
    out_lines.append("    trend continuation from a meaningful EO contribution.")
    out_lines.append("See paper3_trend_regression_results.txt for the trend test.")
    out_lines.append("")
    out_lines.append(f"Sample: 2021-2026 NRMP program-year observations")
    out_lines.append(f"Years included: {sorted(df_base['year'].unique())}")
    out_lines.append(f"Year breakdown: {df_base['year'].value_counts().sort_index().to_dict()}")
    out_lines.append("")
    out_lines.append("CONTEXT:")
    out_lines.append("  - Trump PSLF Executive Order signed March 7, 2025")
    out_lines.append("  - 2025 NRMP ROL deadline was Feb 24, 2025 (BEFORE EO)")
    out_lines.append("  - 2025 Match Day was March 21, 2025 (after EO but ROLs locked)")
    out_lines.append("  - 2026 Match Day was March 20, 2026 — FIRST post-EO Match cycle")
    out_lines.append("    (applicants had 12 months to respond when forming preferences)")
    out_lines.append("")
    out_lines.append("DESCRIPTIVE: 2025 vs 2026 mean fill rates by PSLF class")
    out_lines.append("-" * 80)
    out_lines.append(f"{'Class':22} {'n_2025':>8} {'fill_2025':>11} {'n_2026':>8} {'fill_2026':>11} {'Δ (pp)':>10}")
    for r in desc_rows:
        out_lines.append(f"  {r['class']:20} {r['n_2025']:>8,} {r['fill_2025']:>11.4f} "
                         f"{r['n_2026']:>8,} {r['fill_2026']:>11.4f} {r['delta_pp']:>+9.2f}")
    out_lines.append(f"\n  Descriptive DiD (hostile Δ minus friendly Δ): {did_descriptive:+.2f} pp")
    out_lines.append("")
    out_lines.append("REGRESSION: Pre-EO β + Post-EO Δ β (cluster-robust SE on institution)")
    out_lines.append("-" * 80)
    out_lines.append(f"{'Spec':50} {'Pre-EO β':>12} {'Post-EO Δ':>14} {'Δ p-value':>12}")
    for r in results:
        pre_str = f"{r['h_pre_beta']:+7.2f} pp" if not np.isnan(r['h_pre_beta']) else "n/a"
        ci_pre = f"[{r['h_pre_ci_lo']:+.2f}, {r['h_pre_ci_hi']:+.2f}]" if not np.isnan(r['h_pre_ci_lo']) else ""
        diff_str = f"{r['h_post_diff_beta']:+7.2f} pp" if not np.isnan(r['h_post_diff_beta']) else "n/a"
        ci_post = f"[{r['h_post_diff_ci_lo']:+.2f}, {r['h_post_diff_ci_hi']:+.2f}]" if not np.isnan(r['h_post_diff_ci_lo']) else ""
        p_str = f"{r['h_post_diff_p']:.3e}" if not np.isnan(r['h_post_diff_p']) else "n/a"
        out_lines.append(f"  {r['spec']:48} {pre_str:>12}  {diff_str:>14}  {p_str:>12}")
        out_lines.append(f"      Pre-EO 95% CI: {ci_pre}; Post-EO Δ 95% CI: {ci_post}")
    out_lines.append("")
    out_lines.append("INTERPRETATION (Round 17+ revised — descriptive only):")
    out_lines.append("  Pre-EO β: PSLF-hostile coefficient for years 2021-2025 (vs ambiguous reference)")
    out_lines.append("  Post-EO Δ β: additional change in PSLF-hostile coefficient in year 2026")
    out_lines.append("  Positive Δ β = PSLF-hostile differential narrowed in 2026 vs 2021-2025 (DESCRIPTIVE)")
    out_lines.append("  The narrowing is consistent with a 5-year pre-existing trend, NOT a causal EO effect")
    out_lines.append("  (per trend regression: is_2026 indicator beyond linear trend p=0.46, NS)")
    out_lines.append("")
    out_lines.append("CAUTION:")
    out_lines.append("  Only n_hostile_2026 = ~171 program-years from ~9 unique institutions in S2/S3")
    out_lines.append("  (or ~23 in S1). Power to detect small interactions is limited.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper3_model5_with_2026_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
