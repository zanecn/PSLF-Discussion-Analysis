"""
run_model5_with_confounders.py
==============================
Run Model 5 (Paper 3 audit-required regression) with the full confounder set.

Confounders:
  - PSLF class (3-level: friendly / ambiguous / hostile) — primary exposure
  - University affiliation flag (binary) — academic intensity proxy
  - Academic medical center flag (binary) — additional academic marker
  - n_specialties (continuous) — institution academic depth
  - log(annual_residents_pgy1) — institution scale
  - city CMS Star Rating (continuous) — quality
  - city CMS for-profit share (continuous) — quality + ownership
  - State fixed effects
  - Specialty fixed effects
  - HC3 robust standard errors

NIH funding will be added when nih_reporter_FY2023.csv lands.
Negative-control specialty (orthopedic surgery) is run separately at the end.

Outputs:
  - paper3_model5_results.txt
  - paper3_model5_results.csv
  - paper3_model5_neg_control.txt

Usage:
    python run_model5_with_confounders.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure UTF-8 output for Greek symbols (β, ², ⁻⁷⁵, etc.)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def main():
    # Load data sources
    nrmp = pd.read_csv(PROJECT / "nrmp_program_level_2021_2025.csv")
    confounders = pd.read_csv(PROJECT / "institutional_confounders.csv")
    cms = pd.read_csv(PROJECT / "cms_hospital_general.csv")

    # Map CMS to city-level aggregates
    cms = cms.rename(columns={"Hospital Ownership": "ownership", "City/Town": "city",
                                "State": "state", "Hospital overall rating": "star",
                                "Hospital Type": "hospital_type"})
    cms["star_num"] = pd.to_numeric(cms["star"], errors="coerce")
    cms["is_for_profit"] = (cms["ownership"] == "Proprietary").astype(int)
    cms["is_government"] = cms["ownership"].str.startswith("Government", na=False).astype(int)

    cms_city = cms.groupby(["city", "state"]).agg(
        cms_mean_star=("star_num", "mean"),
        cms_for_profit_share=("is_for_profit", "mean"),
        cms_gov_share=("is_government", "mean"),
        cms_n_hospitals=("Facility ID", "count"),
    ).reset_index()
    print(f"CMS city aggregates: {len(cms_city)}")

    # Standardize NRMP city/state for join
    nrmp["city_norm"] = nrmp["city"].fillna("").str.strip().str.upper()
    nrmp["state_norm"] = nrmp["state"].fillna("").str.strip().str.upper()
    cms_city["city_norm"] = cms_city["city"].str.strip().str.upper()
    cms_city["state_norm"] = cms_city["state"].str.strip().str.upper()
    # Round 17 fix: dedup case-collision duplicates (e.g., "Boston" vs "BOSTON";
    # also affects San Diego, Jacksonville, El Paso, Bethesda — adds ~300 phantom rows
    # if not deduped).
    cms_city = cms_city.drop_duplicates(subset=["city_norm", "state_norm"], keep="first")

    # Merge: NRMP + CMS (city, state)
    df = nrmp.merge(
        cms_city[["city_norm", "state_norm", "cms_mean_star",
                   "cms_for_profit_share", "cms_gov_share", "cms_n_hospitals"]],
        on=["city_norm", "state_norm"], how="left",
    )

    # Merge: + institutional confounders
    df = df.merge(
        confounders[["institution", "n_unique_programs", "n_specialties",
                      "annual_residents_pgy1", "university_affiliation",
                      "academic_med_center", "ntee_top_level"]],
        on="institution", how="left",
    )

    # Try to add NIH if available
    nih_path = PROJECT / "nih_reporter_FY2023.csv"
    if nih_path.exists():
        nih = pd.read_csv(nih_path)
        # Aggregate by institution (sum across FYs if multi-year)
        nih_inst = nih.groupby("institution").agg(
            nih_total_award=("total_award_amount", "sum"),
            nih_n_projects=("n_projects", "sum"),
        ).reset_index()
        df = df.merge(nih_inst, on="institution", how="left")
        df["log_nih_funding"] = np.log1p(df["nih_total_award"].fillna(0))
        nih_available = True
    else:
        df["log_nih_funding"] = 0.0
        nih_available = False

    # Drop missing fill_rate
    df = df.dropna(subset=["fill_rate", "pslf_class"]).copy()
    df["log_residents"] = np.log1p(df["annual_residents_pgy1"].fillna(0))

    print(f"\nAnalytical sample: {len(df):,} program-year rows")
    print(f"Unique institutions: {df['institution'].nunique():,}")
    print(f"Years: {sorted(df['year'].unique())}")
    print(f"Specialties: {df['specialty'].nunique()}")

    # Run regressions
    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
    except ImportError:
        print("[ERROR] pip install statsmodels")
        sys.exit(1)

    # Convert categorical pslf_class to dummies (reference: ambiguous)
    df["pslf_class"] = df["pslf_class"].astype("category")
    df["pslf_class"] = df["pslf_class"].cat.set_categories(
        ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)

    # M5 regression: PSLF + city CMS + univ aff + AMC + n_specialties + log(residents)
    #                 + (NIH if available) + state FE + specialty FE
    formula_parts = [
        "C(pslf_class, Treatment(reference='ambiguous'))",
        "cms_mean_star",
        "cms_for_profit_share",
        "C(university_affiliation)",
        "C(academic_med_center)",
        "n_specialties",
        "log_residents",
    ]
    if nih_available:
        formula_parts.append("log_nih_funding")
    formula_parts.append("C(state)")
    formula_parts.append("C(specialty)")

    formula = "fill_rate ~ " + " + ".join(formula_parts)
    print(f"\nM5 formula:\n  {formula}\n")

    # Fit with HC3 robust SEs
    model = smf.ols(formula, data=df).fit(cov_type="HC3")

    out_lines = []
    out_lines.append("=" * 80)
    out_lines.append("PAPER 3 MODEL 5: PSLF FILL-RATE WITH AUDIT-REQUIRED CONFOUNDERS")
    out_lines.append("=" * 80)
    out_lines.append("")
    out_lines.append(f"Sample: n={len(df):,} program-year rows; {df['institution'].nunique()} institutions")
    out_lines.append(f"Years: {sorted(df['year'].unique())}")
    out_lines.append(f"Specialties: {df['specialty'].nunique()}")
    out_lines.append(f"NIH funding included: {nih_available}")
    out_lines.append(f"R²: {model.rsquared:.4f}")
    out_lines.append(f"Adjusted R²: {model.rsquared_adj:.4f}")
    out_lines.append("")
    out_lines.append("KEY COEFFICIENTS (HC3 robust SEs)")
    out_lines.append("-" * 80)

    # Pull only the headline coefficients
    headlines = [
        "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_friendly]",
        "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]",
        "cms_mean_star",
        "cms_for_profit_share",
        "C(university_affiliation)[T.True]",
        "C(academic_med_center)[T.True]",
        "n_specialties",
        "log_residents",
    ]
    if nih_available:
        headlines.append("log_nih_funding")

    params = model.params
    bse = model.bse
    pvalues = model.pvalues
    conf_int = model.conf_int()

    for h in headlines:
        if h in params.index:
            label = h.replace("C(pslf_class, Treatment(reference='ambiguous'))", "PSLF").replace("[T.", "[")
            label = label.replace("C(university_affiliation)", "Univ.affil").replace("C(academic_med_center)", "Acad.MC")
            beta = params[h] * 100  # Convert to pp
            se = bse[h] * 100
            p = pvalues[h]
            lo = conf_int.loc[h, 0] * 100
            hi = conf_int.loc[h, 1] * 100
            stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            out_lines.append(f"  {label:55} β={beta:+7.2f} pp [SE={se:.2f}, 95% CI ({lo:+7.2f}, {hi:+7.2f})], p={p:.3e} {stars}")

    out_lines.append("")
    out_lines.append("INTERPRETATION")
    out_lines.append("-" * 80)
    pslf_h = params.get("C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]", 0) * 100
    pslf_f = params.get("C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_friendly]", 0) * 100
    out_lines.append(f"  PSLF-hostile vs ambiguous: {pslf_h:+.2f} pp")
    out_lines.append(f"  PSLF-friendly vs ambiguous: {pslf_f:+.2f} pp")
    out_lines.append("  (Reference: ambiguous; positive = higher fill rate)")
    out_lines.append("")
    out_lines.append("Compare to original Model 4 (no audit confounders):")
    out_lines.append("  PSLF-hostile β = -18.56 pp (95% CI [-21.0, -16.1]; p<10⁻⁷⁵)")
    out_lines.append("  PSLF-friendly β = -0.15 pp (NS)")
    out_lines.append("")
    out_lines.append("The full Model 5 result tells us whether the headline survives the")
    out_lines.append("audit-required confounders. Substantial attenuation (e.g., to >-10 pp)")
    out_lines.append("would weaken the headline; minor attenuation (-15 to -19 pp) supports it.")

    # Save
    out_text = "\n".join(out_lines)
    print(out_text)
    out_path = PROJECT / "paper3_model5_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")

    # Also save a clean coefficient table
    coef_table = pd.DataFrame({
        "coefficient": params.values * 100,
        "std_error": bse.values * 100,
        "p_value": pvalues.values,
        "ci_low": conf_int[0].values * 100,
        "ci_high": conf_int[1].values * 100,
    }, index=params.index)
    coef_table.to_csv(PROJECT / "paper3_model5_results.csv")
    print(f"Saved: {PROJECT / 'paper3_model5_results.csv'}")

    # ======================================================================
    # NEGATIVE CONTROL: Orthopedic surgery (PSLF less material; no expected
    # PSLF-hostile differential)
    # ======================================================================
    print("\n" + "=" * 80)
    print("NEGATIVE CONTROL: Orthopedic Surgery")
    print("=" * 80)

    df_ortho = df[df["specialty"].str.contains("Orthop", case=False, na=False)].copy()
    print(f"Orthopedic surgery rows: {len(df_ortho)}")
    if len(df_ortho) >= 50:
        # Drop specialty FE (only one specialty)
        formula_ortho_parts = [p for p in formula_parts if not p.startswith("C(specialty)")]
        formula_ortho = "fill_rate ~ " + " + ".join(formula_ortho_parts)
        try:
            ortho_model = smf.ols(formula_ortho, data=df_ortho).fit(cov_type="HC3")
            print(f"Ortho R²: {ortho_model.rsquared:.4f}")
            print(f"Ortho n: {len(df_ortho)}")
            print()
            for h in headlines:
                if h in ortho_model.params.index:
                    label = h.replace("C(pslf_class, Treatment(reference='ambiguous'))", "PSLF").replace("[T.", "[")
                    label = label.replace("C(university_affiliation)", "Univ.affil").replace("C(academic_med_center)", "Acad.MC")
                    beta = ortho_model.params[h] * 100
                    p = ortho_model.pvalues[h]
                    print(f"  Ortho {label:55} β={beta:+7.2f} pp, p={p:.3e}")

            # Save
            ortho_path = PROJECT / "paper3_model5_neg_control_orthopedics.txt"
            ortho_text = f"NEGATIVE CONTROL: ORTHOPEDIC SURGERY\nn={len(df_ortho)}\nR²={ortho_model.rsquared:.4f}\n\n"
            for h in headlines:
                if h in ortho_model.params.index:
                    label = h.replace("C(pslf_class, Treatment(reference='ambiguous'))", "PSLF").replace("[T.", "[")
                    label = label.replace("C(university_affiliation)", "Univ.affil").replace("C(academic_med_center)", "Acad.MC")
                    beta = ortho_model.params[h] * 100
                    se = ortho_model.bse[h] * 100
                    p = ortho_model.pvalues[h]
                    ci_low = ortho_model.conf_int().loc[h, 0] * 100
                    ci_high = ortho_model.conf_int().loc[h, 1] * 100
                    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                    ortho_text += f"  {label:55} β={beta:+7.2f} pp [SE={se:.2f}, CI ({ci_low:+7.2f}, {ci_high:+7.2f})], p={p:.3e} {stars}\n"
            ortho_text += "\nInterpretation: if PSLF-hostile β is much smaller in orthopedic surgery\n"
            ortho_text += "than in primary care, this is consistent with PSLF financial-incentive theory\n"
            ortho_text += "(higher attending compensation in orthopedics makes PSLF less material).\n"
            ortho_text += "If PSLF-hostile β is similar to primary care, this is a CONFOUND warning.\n"
            ortho_path.write_text(ortho_text, encoding="utf-8")
            print(f"\nSaved: {ortho_path}")
        except Exception as e:
            print(f"Ortho regression failed: {e}")
    else:
        print(f"Insufficient sample for orthopedic-surgery negative control")


if __name__ == "__main__":
    main()
