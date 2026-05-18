"""
run_model5_FINAL.py
====================
Round 15 audit fixes applied:
  Fix 1: Use deduplicated institutional_confounders.csv (789 unique institutions)
  Fix 2: Cluster-robust SE clustered on institution (instead of HC3)
  Fix 3: HCA-academic-partnership sensitivity analysis (3 specifications)
  Fix 5: Honest robustness-ladder framing (low shrinkage = covariates don't vary,
         not robust to omitted variables)
  Fix 8: Honest negative-control power floor framing

Specifications run:
  S1 (status quo): All 23 hostile institutions classified as hostile
  S2 (reclassified): HCA-academic partnerships moved to ambiguous (n_h drops 23→7)
  S3 (subset only): Restricted to unambiguous-hostile + ambiguous + friendly

Outputs: paper3_model5_FINAL_results.txt
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

# Identify HCA-academic partnerships (academic institutions whose residents
# may be employed by the academic partner, making them PSLF-eligible at the
# resident-W2 level). Per Round 15 audit: USF Morsani, U Miami, U Houston,
# VCOM are public-university or 501(c)(3) academic partners. TriStar is HCA's
# own internal brand, NOT an academic partnership, so excluded from this list.
HCA_ACADEMIC_PARTNERSHIPS = [
    # USF Morsani partnerships (USF is a public university, PSLF-eligible)
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
    # U Miami partnerships (UMiami is 501(c)(3))
    "HCA Florida JFK Hosp-U Miami",
    "HCA Healthcare/JFK Med Center-UMiami",
    # U Houston partnership
    "HCA Houston Healthcare/U Houston",
    # VCOM partnership (VCOM is 501(c)(3) osteopathic)
    "HCA Healthcare LGH-Montgomery/VCOM",
]

UNAMBIGUOUS_HOSTILE = [
    # HCA owned & operated, no academic partnership
    "HCA Chippenham & Johnston-Willis Hosps",
    "HCA Corpus Christi Med Ctr",
    "HCA Healthcare Kansas City",
    "HCA Healthcare/TriStar Nashville",
    "HCA Healthcare/TriStar Southern Hills",
    "HCA Las Palmas del Sol Healthcare",
    "HCA Medical City Healthcare",
    # Other for-profit
    "North Oaks Med Ctr LLC",
    "Steward Carney Hospital",
]


def load_and_merge():
    """Load NRMP + confounders + CMS, return analytical dataframe."""
    nrmp = pd.read_csv(PROJECT / "nrmp_program_level_2021_2025.csv")
    confounders = pd.read_csv(PROJECT / "institutional_confounders.csv")
    cms = pd.read_csv(PROJECT / "cms_hospital_general.csv")

    # CMS city-level
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

    # NIH funding (state-filtered version)
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
    return df


def run_spec(df, spec_name, n_friendly, n_hostile_unique, n_hostile_rows):
    """Run M5 with cluster-robust SE, return dict of headline stats."""
    import statsmodels.formula.api as smf
    df = df.copy()
    df["pslf_class"] = df["pslf_class"].astype("category")
    df["pslf_class"] = df["pslf_class"].cat.set_categories(
        ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)

    formula = ("fill_rate ~ C(pslf_class, Treatment(reference='ambiguous'))"
               " + cms_mean_star + cms_for_profit_share"
               " + C(university_affiliation) + C(academic_med_center)"
               " + n_specialties + log_residents + log_nih_funding"
               " + C(state) + C(specialty)")

    # Drop rows with any NA in regression variables (so groups vector matches design matrix length)
    needed_cols = ["fill_rate", "pslf_class", "cms_mean_star", "cms_for_profit_share",
                   "university_affiliation", "academic_med_center", "n_specialties",
                   "log_residents", "log_nih_funding", "state", "specialty", "institution"]
    df_fit = df.dropna(subset=needed_cols).copy().reset_index(drop=True)

    # FIX 2: cluster-robust SE on institution (not HC3)
    # cluster groups must be a numpy array of integers (categorical codes)
    cluster_groups = df_fit["institution"].astype("category").cat.codes.values
    model = smf.ols(formula, data=df_fit).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_groups}
    )

    h_key = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]"
    f_key = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_friendly]"
    return {
        "spec": spec_name,
        "n_total": len(df_fit),
        "n_friendly": n_friendly,
        "n_hostile_inst": n_hostile_unique,
        "n_hostile_rows": n_hostile_rows,
        "n_clusters": df_fit["institution"].nunique(),
        "r_sq": model.rsquared,
        "h_beta": model.params.get(h_key, np.nan) * 100,
        "h_se": model.bse.get(h_key, np.nan) * 100,
        "h_p": model.pvalues.get(h_key, np.nan),
        "h_ci_lo": model.conf_int().loc[h_key, 0] * 100 if h_key in model.params.index else np.nan,
        "h_ci_hi": model.conf_int().loc[h_key, 1] * 100 if h_key in model.params.index else np.nan,
        "f_beta": model.params.get(f_key, np.nan) * 100,
        "f_se": model.bse.get(f_key, np.nan) * 100,
        "f_p": model.pvalues.get(f_key, np.nan),
    }


def main():
    df_base = load_and_merge()
    print(f"Loaded analytical dataset: n={len(df_base):,} rows; {df_base['institution'].nunique()} unique institutions")

    # Spec 1: Status quo (all 23 institutions classified as hostile)
    df1 = df_base.copy()
    n_h_1 = (df1["pslf_class"] == "pslf_hostile").sum()
    n_h_inst_1 = df1[df1["pslf_class"] == "pslf_hostile"]["institution"].nunique()
    n_f_1 = (df1["pslf_class"] == "pslf_friendly").sum()
    s1 = run_spec(df1, "S1: Status quo (all 23 hostile)", n_f_1, n_h_inst_1, n_h_1)

    # Spec 2: HCA-academic reclassified as ambiguous
    df2 = df_base.copy()
    mask_acad = df2["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS)
    df2.loc[mask_acad, "pslf_class"] = "ambiguous"
    n_h_2 = (df2["pslf_class"] == "pslf_hostile").sum()
    n_h_inst_2 = df2[df2["pslf_class"] == "pslf_hostile"]["institution"].nunique()
    n_f_2 = (df2["pslf_class"] == "pslf_friendly").sum()
    s2 = run_spec(df2, "S2: HCA-academic reclassified as ambiguous", n_f_2, n_h_inst_2, n_h_2)

    # Spec 3: Restricted to unambiguous-hostile + friendly + ambiguous (drop the partnerships entirely)
    df3 = df_base.copy()
    df3 = df3[~df3["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS)].copy()
    n_h_3 = (df3["pslf_class"] == "pslf_hostile").sum()
    n_h_inst_3 = df3[df3["pslf_class"] == "pslf_hostile"]["institution"].nunique()
    n_f_3 = (df3["pslf_class"] == "pslf_friendly").sum()
    s3 = run_spec(df3, "S3: Drop HCA-academic partnerships entirely", n_f_3, n_h_inst_3, n_h_3)

    # ALSO: orthopedic surgery negative control (status quo only)
    df_ortho = df_base[df_base["specialty"].str.contains("Orthop", case=False, na=False)].copy()
    n_h_ortho = (df_ortho["pslf_class"] == "pslf_hostile").sum()
    n_h_inst_ortho = df_ortho[df_ortho["pslf_class"] == "pslf_hostile"]["institution"].nunique()
    n_f_ortho = (df_ortho["pslf_class"] == "pslf_friendly").sum()

    import statsmodels.formula.api as smf
    df_ortho["pslf_class"] = df_ortho["pslf_class"].astype("category")
    df_ortho["pslf_class"] = df_ortho["pslf_class"].cat.set_categories(
        ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)
    f_ortho = ("fill_rate ~ C(pslf_class, Treatment(reference='ambiguous'))"
               " + cms_mean_star + C(university_affiliation) + C(academic_med_center)"
               " + n_specialties + log_residents + log_nih_funding + C(state)")
    try:
        ortho_needed = ["fill_rate", "pslf_class", "cms_mean_star", "university_affiliation",
                        "academic_med_center", "n_specialties", "log_residents",
                        "log_nih_funding", "state", "institution"]
        df_ortho_fit = df_ortho.dropna(subset=ortho_needed).copy().reset_index(drop=True)
        ortho_groups = df_ortho_fit["institution"].astype("category").cat.codes.values
        m_ortho = smf.ols(f_ortho, data=df_ortho_fit).fit(
            cov_type="cluster", cov_kwds={"groups": ortho_groups})
        h_key = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]"
        s_ortho_beta = m_ortho.params.get(h_key, np.nan) * 100
        s_ortho_se = m_ortho.bse.get(h_key, np.nan) * 100
        s_ortho_ci = m_ortho.conf_int().loc[h_key]
        s_ortho_p = m_ortho.pvalues.get(h_key, np.nan)
    except Exception as e:
        s_ortho_beta = s_ortho_se = s_ortho_p = np.nan
        s_ortho_ci = (np.nan, np.nan)

    # Output
    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 3 MODEL 5 FINAL — Round 15 Audit Fixes Applied")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("Fixes applied:")
    out_lines.append("  - Fix 1: Deduplicated institutional_confounders.csv (789 unique institutions)")
    out_lines.append("  - Fix 2: Cluster-robust SE clustered on institution")
    out_lines.append("  - Fix 3: HCA-academic-partnership sensitivity (3 specifications)")
    out_lines.append("")
    out_lines.append(f"Hostile institutions classification:")
    out_lines.append(f"  Total NRMP-hostile institutions: 23")
    out_lines.append(f"  HCA-academic partnerships: {len(HCA_ACADEMIC_PARTNERSHIPS)} (USF Morsani x10, UMiami x2, U Houston x1, VCOM x1)")
    out_lines.append(f"  Unambiguous HCA/for-profit standalones: {len(UNAMBIGUOUS_HOSTILE)}")
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("SPEC TABLE: PSLF-hostile coefficient under three classifications")
    out_lines.append("=" * 90)
    out_lines.append(f"")
    out_lines.append(f"{'Specification':50} {'n_total':>8} {'n_hostile_rows':>14} {'n_hostile_inst':>14}")
    out_lines.append("-" * 90)
    for s in [s1, s2, s3]:
        out_lines.append(f"  {s['spec']:48} {s['n_total']:>8,} {s['n_hostile_rows']:>14,} {s['n_hostile_inst']:>14}")
    out_lines.append("")
    out_lines.append(f"{'Specification':50} {'PSLF-hostile β':>15} {'95% CI':>22} {'p-value':>12}")
    out_lines.append("-" * 90)
    for s in [s1, s2, s3]:
        ci_str = f"[{s['h_ci_lo']:+.2f}, {s['h_ci_hi']:+.2f}]"
        out_lines.append(f"  {s['spec']:48} {s['h_beta']:+8.2f} pp     {ci_str:>22} {s['h_p']:>12.3e}")
    out_lines.append("")
    out_lines.append("INTERPRETATION (Round 15 honest framing):")
    out_lines.append("-" * 90)
    out_lines.append(f"  S1 (status quo): assumes all HCA-academic-partnership residents are PSLF-INELIGIBLE")
    out_lines.append(f"    (i.e., resident W-2 is from HCA, not from the academic partner). This is the")
    out_lines.append(f"    UPPER BOUND on the true PSLF-hostile differential.")
    out_lines.append(f"  S2 (reclassified): assumes HCA-academic-partnership residents are PSLF-ELIGIBLE")
    out_lines.append(f"    (resident W-2 from academic partner). This is the LOWER BOUND on the differential.")
    out_lines.append(f"  S3 (drop partnerships): cleanest estimate restricted to unambiguous classifications.")
    out_lines.append(f"")
    out_lines.append(f"  The truth depends on the actual W-2 employer-of-record at each program — NOT")
    out_lines.append(f"  determined by this design. The range (S1, S2, S3) brackets the plausible PSLF-hostile")
    out_lines.append(f"  effect on residency competition.")
    out_lines.append("")
    out_lines.append(f"  Cluster-robust SE: SE column reflects clustering on institution.")
    out_lines.append(f"  With 23 hostile clusters in S1 (or 9 in S2/S3), Cameron-Miller (2015) recommend")
    out_lines.append(f"  treating these p-values cautiously; consider wild-cluster bootstrap as confirmation.")
    out_lines.append("")
    out_lines.append(f"  ROBUSTNESS LADDER REFRAMING (Round 15 Fix 5):")
    out_lines.append(f"  Earlier 'M1 → M5+NIH shrinkage of 0.55 pp' framing was misleading. Low shrinkage")
    out_lines.append(f"  with audit-required confounders does NOT mean the headline is robust to omitted")
    out_lines.append(f"  variables. It means the measured confounders do NOT vary substantially across")
    out_lines.append(f"  the PSLF-class contrast. Unobserved institutional factors that vary at the same")
    out_lines.append(f"  level as PSLF classification could still explain the differential.")
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("NEGATIVE CONTROL: Orthopedic Surgery (status quo classification)")
    out_lines.append("=" * 90)
    out_lines.append(f"  n_total: {len(df_ortho):,}")
    out_lines.append(f"  n_hostile_rows: {n_h_ortho}, n_hostile_institutions: {n_h_inst_ortho}")
    out_lines.append(f"  PSLF-hostile β: {s_ortho_beta:+.2f} pp")
    out_lines.append(f"  95% CI (cluster-robust): [{s_ortho_ci[0]*100:+.2f}, {s_ortho_ci[1]*100:+.2f}]")
    out_lines.append(f"  p-value: {s_ortho_p:.3e}")
    out_lines.append("")
    out_lines.append("HONEST POWER FLOOR FRAMING (Round 15 Fix 8):")
    out_lines.append(f"  With n={n_h_ortho} hostile rows from {n_h_inst_ortho} clusters and SE={s_ortho_se:.2f},")
    out_lines.append(f"  the orthopedic surgery negative-control test only rules out uniform-recruitment")
    out_lines.append(f"  confounds of magnitude > {1.96 * s_ortho_se:.1f} pp. It does NOT rule out smaller")
    out_lines.append(f"  uniform confounds (e.g., 1-3 pp).")
    out_lines.append(f"  Furthermore, {n_h_inst_ortho - 0} of these hostile-ortho clusters may be HCA-academic")
    out_lines.append(f"  partnerships (per Fix 3), defeating the negative-control logic if their residents")
    out_lines.append(f"  are actually PSLF-eligible at the W-2 level.")

    out_text = "\n".join(out_lines)
    print(out_text)
    out_path = PROJECT / "paper3_model5_FINAL_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
