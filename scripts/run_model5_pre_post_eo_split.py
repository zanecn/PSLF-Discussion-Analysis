"""
run_model5_pre_post_eo_split.py
=================================
Cleaner pre/post-EO comparison: fit Model 5 separately on 2021-2025 (pre-EO)
and 2026 (first post-EO Match) data, then compare the PSLF-hostile β values
across the two periods.

This approach avoids the multicollinearity issue with year × PSLF-class
interactions in a fully-specified regression with state + specialty fixed
effects.
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
    df = nrmp.merge(cms_city[["city_norm", "state_norm", "cms_mean_star",
                                "cms_for_profit_share", "cms_n_hospitals"]],
                     on=["city_norm", "state_norm"], how="left")
    df = df.merge(confounders[["institution", "n_unique_programs", "n_specialties",
                                "annual_residents_pgy1", "university_affiliation",
                                "academic_med_center"]],
                  on="institution", how="left")
    nih_path = PROJECT / "nih_reporter_FY2023_state.csv"
    if nih_path.exists():
        nih = pd.read_csv(nih_path)
        nih_inst = nih.groupby("institution").agg(
            nih_total_award=("total_award_amount", "sum")).reset_index()
        df = df.merge(nih_inst, on="institution", how="left")
        df["nih_total_award"] = df["nih_total_award"].fillna(0)
    else:
        df["nih_total_award"] = 0
    df["log_nih_funding"] = np.log1p(df["nih_total_award"])
    df["log_residents"] = np.log1p(df["annual_residents_pgy1"].fillna(0))
    df = df.dropna(subset=["fill_rate", "pslf_class"]).copy()
    return df


def run_spec(df, spec_label, period_label):
    """Fit Model 5 with cluster-robust SE on a given subset of years."""
    import statsmodels.formula.api as smf
    df = df.copy()
    df["pslf_class"] = df["pslf_class"].astype("category")
    df["pslf_class"] = df["pslf_class"].cat.set_categories(
        ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)
    needed = ["fill_rate", "pslf_class", "cms_mean_star", "cms_for_profit_share",
              "university_affiliation", "academic_med_center", "n_specialties",
              "log_residents", "log_nih_funding", "state", "specialty", "institution"]
    df_fit = df.dropna(subset=needed).copy().reset_index(drop=True)
    if len(df_fit) < 100:
        return None
    cluster_groups = df_fit["institution"].astype("category").cat.codes.values
    formula = ("fill_rate ~ C(pslf_class, Treatment(reference='ambiguous'))"
               " + cms_mean_star + cms_for_profit_share"
               " + C(university_affiliation) + C(academic_med_center)"
               " + n_specialties + log_residents + log_nih_funding"
               " + C(state) + C(specialty)")
    try:
        model = smf.ols(formula, data=df_fit).fit(
            cov_type="cluster", cov_kwds={"groups": cluster_groups})
    except Exception as e:
        print(f"  [error] {spec_label} {period_label}: {e}")
        return None
    h_key = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]"
    if h_key not in model.params.index:
        return None
    return {
        "spec": spec_label, "period": period_label,
        "n": len(df_fit), "n_clusters": df_fit["institution"].nunique(),
        "n_hostile_inst": df_fit[df_fit["pslf_class"] == "pslf_hostile"]["institution"].nunique(),
        "n_hostile_rows": (df_fit["pslf_class"] == "pslf_hostile").sum(),
        "h_beta": model.params[h_key] * 100,
        "h_se": model.bse[h_key] * 100,
        "h_p": model.pvalues[h_key],
        "h_ci_lo": model.conf_int().loc[h_key, 0] * 100,
        "h_ci_hi": model.conf_int().loc[h_key, 1] * 100,
    }


def main():
    df_base = load_and_merge()
    print(f"Loaded analytical dataset (2021-2026): n={len(df_base):,}")
    print()

    print("=" * 95)
    print("PRE/POST-EO PSLF-HOSTILE β COMPARISON (separate regressions)")
    print("=" * 95)
    print()

    specs = [
        ("S1: Status quo (all 23 hostile)", lambda d: d),
        ("S2: HCA-academic reclassified as ambiguous", lambda d: d.assign(
            pslf_class=d["pslf_class"].where(
                ~d["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS), "ambiguous"))),
        ("S3: Drop HCA-academic partnerships", lambda d: d[
            ~d["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS)]),
    ]

    out_lines = []
    out_lines.append("=" * 95)
    out_lines.append("PAPER 3 PRE/POST-EO MODEL 5 (2021-2025 vs 2026, separate regressions)")
    out_lines.append("=" * 95)
    out_lines.append("")
    out_lines.append("Trump PSLF EO signed March 7, 2025. 2025 ROL deadline was Feb 24, 2025 (BEFORE EO).")
    out_lines.append("So 2025 reflects pre-EO preferences. 2026 is the first post-EO Match cycle.")
    out_lines.append("")

    for spec_label, df_modify in specs:
        df = df_modify(df_base.copy())
        df["pslf_class"] = df["pslf_class"].astype("category")
        df["pslf_class"] = df["pslf_class"].cat.set_categories(
            ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)
        df_pre = df[df["year"] <= 2025]
        df_post = df[df["year"] == 2026]
        r_pre = run_spec(df_pre, spec_label, "Pre-EO (2021-2025)")
        r_post = run_spec(df_post, spec_label, "Post-EO (2026)")
        out_lines.append(f"{spec_label}")
        out_lines.append("-" * 95)
        if r_pre:
            print(f"  {spec_label} | Pre-EO (2021-2025) | n={r_pre['n']:>6,} | "
                  f"n_hostile={r_pre['n_hostile_rows']:>4} | "
                  f"β={r_pre['h_beta']:+7.2f} pp [{r_pre['h_ci_lo']:+.2f}, {r_pre['h_ci_hi']:+.2f}] | p={r_pre['h_p']:.3e}")
            out_lines.append(f"  Pre-EO (2021-2025): n={r_pre['n']:,}, n_hostile={r_pre['n_hostile_rows']}")
            out_lines.append(f"    β={r_pre['h_beta']:+.2f} pp [95% CI {r_pre['h_ci_lo']:+.2f}, {r_pre['h_ci_hi']:+.2f}], p={r_pre['h_p']:.3e}")
        if r_post:
            print(f"  {spec_label} | Post-EO (2026)      | n={r_post['n']:>6,} | "
                  f"n_hostile={r_post['n_hostile_rows']:>4} | "
                  f"β={r_post['h_beta']:+7.2f} pp [{r_post['h_ci_lo']:+.2f}, {r_post['h_ci_hi']:+.2f}] | p={r_post['h_p']:.3e}")
            out_lines.append(f"  Post-EO (2026):     n={r_post['n']:,}, n_hostile={r_post['n_hostile_rows']}")
            out_lines.append(f"    β={r_post['h_beta']:+.2f} pp [95% CI {r_post['h_ci_lo']:+.2f}, {r_post['h_ci_hi']:+.2f}], p={r_post['h_p']:.3e}")
        if r_pre and r_post:
            shrinkage = r_post["h_beta"] - r_pre["h_beta"]
            print(f"  {spec_label} | Δ (post-pre) = {shrinkage:+.2f} pp ← post-EO change in differential")
            out_lines.append(f"  Δ (post − pre) = {shrinkage:+.2f} pp ← post-EO change in PSLF-hostile differential")
            ses_combined = np.sqrt(r_pre["h_se"]**2 + r_post["h_se"]**2)
            z_stat = shrinkage / ses_combined
            from scipy import stats
            two_sided_p = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            out_lines.append(f"  Naive z-test for Δ ≠ 0: z={z_stat:.2f}, two-sided p={two_sided_p:.3e}")
            out_lines.append(f"    (Note: independent-sample assumption is approximate; same institutions")
            out_lines.append(f"    may appear in both periods, so this z-test slightly understates SE.)")
        out_lines.append("")
        print()

    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 95)
    out_lines.append("  Pre-EO β: PSLF-hostile coefficient on 2021-2025 sample (locked Round 16 result)")
    out_lines.append("  Post-EO β: PSLF-hostile coefficient on 2026-only sample (NEW Round 16 strengthener)")
    out_lines.append("  Δ = Post-EO β − Pre-EO β. Positive Δ = differential narrowed in first post-EO Match.")
    out_lines.append("")
    out_lines.append("  Descriptive numbers: 2025 vs 2026 mean fill rates")
    out_lines.append("    pslf_friendly: 0.940 → 0.935 (Δ = −0.5 pp)")
    out_lines.append("    ambiguous:     0.926 → 0.914 (Δ = −1.2 pp)")
    out_lines.append("    pslf_hostile:  0.836 → 0.864 (Δ = +2.8 pp)")
    out_lines.append("    DiD (hostile vs friendly): +3.4 pp narrowing of the gap")
    out_lines.append("")
    out_lines.append("  Caveat (Round 17+ revised): Power is limited. Only ~171 hostile program-year observations")
    out_lines.append("  in 2026 from ~9 unambiguous (or 23 status-quo) institutions. The post-EO regression has")
    out_lines.append("  wide CIs; the descriptive comparison should NOT be read as causal evidence of an EO")
    out_lines.append("  effect. Per the trend regression (paper3_trend_regression_results.txt), the 2026")
    out_lines.append("  narrowing is statistically indistinguishable from continuation of the 2021–2025 trend")
    out_lines.append("  (is_2026 indicator beyond linear trend p=0.46 NS). This file is descriptive ONLY.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper3_model5_pre_post_eo_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
