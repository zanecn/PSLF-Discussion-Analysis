"""
run_negative_control_with_2026.py
===================================
Round 17 Fix: re-run the orthopedic-surgery negative-control test on the
combined 2021-2026 dataset (was previously 2021-2025 only).

Per Round 17 audit: the locked β=+0.76, n=1,079 came from the 5-year sample.
With 2026 data added (~3-4 more hostile-ortho rows), need to refresh.

Output: paper3_negative_control_2021_2026_results.txt
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
    return df.dropna(subset=["fill_rate", "pslf_class"]).copy()


def run_neg_control(df, label):
    df = df[df["specialty"].str.contains("Orthop", case=False, na=False)].copy()
    df["pslf_class"] = df["pslf_class"].astype("category")
    df["pslf_class"] = df["pslf_class"].cat.set_categories(
        ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)
    needed = ["fill_rate", "pslf_class", "cms_mean_star", "cms_for_profit_share",
              "university_affiliation", "academic_med_center", "n_specialties",
              "log_residents", "log_nih_funding", "state", "institution"]
    df_fit = df.dropna(subset=needed).copy().reset_index(drop=True)
    if len(df_fit) < 20:
        return None
    cluster_groups = df_fit["institution"].astype("category").cat.codes.values
    formula = ("fill_rate ~ C(pslf_class, Treatment(reference='ambiguous'))"
               " + cms_mean_star + cms_for_profit_share"
               " + C(university_affiliation) + C(academic_med_center)"
               " + n_specialties + log_residents + log_nih_funding + C(state)")
    try:
        m = smf.ols(formula, data=df_fit).fit(
            cov_type="cluster", cov_kwds={"groups": cluster_groups})
        h_key = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]"
        return {
            "label": label, "n": len(df_fit),
            "n_hostile_inst": df_fit[df_fit["pslf_class"] == "pslf_hostile"]["institution"].nunique(),
            "n_hostile_rows": (df_fit["pslf_class"] == "pslf_hostile").sum(),
            "h_beta": m.params.get(h_key, np.nan) * 100,
            "h_se": m.bse.get(h_key, np.nan) * 100,
            "h_p": m.pvalues.get(h_key, np.nan),
            "h_ci_lo": m.conf_int().loc[h_key, 0] * 100 if h_key in m.params.index else np.nan,
            "h_ci_hi": m.conf_int().loc[h_key, 1] * 100 if h_key in m.params.index else np.nan,
        }
    except Exception as e:
        print(f"  Error fitting {label}: {e}")
        return None


def main():
    df_full = load_and_merge()

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 3 NEGATIVE-CONTROL ORTHOPEDIC SURGERY — 2021-2026 (Round 17 update)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("Comparison: prior 2021-2025-only result (β=+0.76, SE=0.66, n=1,079) vs")
    out_lines.append("current 2021-2026 result (with one additional Match year added).")
    out_lines.append("")

    # Run on 2021-2025 subset (replicates prior result for comparison)
    print("Running negative control 2021-2025 (replication baseline)...")
    r_2125 = run_neg_control(df_full[df_full["year"] <= 2025].copy(), "2021-2025 (baseline replication)")
    if r_2125:
        ci = f"[{r_2125['h_ci_lo']:+.2f}, {r_2125['h_ci_hi']:+.2f}]"
        line = f"  2021-2025: n={r_2125['n']:,}, n_hostile_rows={r_2125['n_hostile_rows']}, n_hostile_inst={r_2125['n_hostile_inst']}, β={r_2125['h_beta']:+.2f} pp, SE={r_2125['h_se']:.2f}, 95% CI {ci}, p={r_2125['h_p']:.3f}"
        print(line)
        out_lines.append(line)

    # Run on 2021-2026 (NEW)
    print("\nRunning negative control 2021-2026 (NEW)...")
    r_2126 = run_neg_control(df_full.copy(), "2021-2026 (Round 17 update)")
    if r_2126:
        ci = f"[{r_2126['h_ci_lo']:+.2f}, {r_2126['h_ci_hi']:+.2f}]"
        line = f"  2021-2026: n={r_2126['n']:,}, n_hostile_rows={r_2126['n_hostile_rows']}, n_hostile_inst={r_2126['n_hostile_inst']}, β={r_2126['h_beta']:+.2f} pp, SE={r_2126['h_se']:.2f}, 95% CI {ci}, p={r_2126['h_p']:.3f}"
        print(line)
        out_lines.append(line)

    # 2026-only descriptive
    df_ortho_2026 = df_full[(df_full["specialty"].str.contains("Orthop", case=False, na=False)) & (df_full["year"] == 2026)]
    n_ortho_2026 = len(df_ortho_2026)
    n_h_ortho_2026 = (df_ortho_2026["pslf_class"] == "pslf_hostile").sum()
    print(f"\n2026 ortho descriptive: n={n_ortho_2026}, n_hostile_rows={n_h_ortho_2026}")
    out_lines.append(f"")
    out_lines.append(f"2026 ortho descriptive: n={n_ortho_2026}, n_hostile_rows={n_h_ortho_2026}")

    if r_2125 and r_2126:
        # Power floor (MDE 80%)
        mde_2125 = 1.96 * r_2125["h_se"]
        mde_2126 = 1.96 * r_2126["h_se"]
        out_lines.append("")
        out_lines.append("POWER FLOOR (95% CI half-width = uniform-confound rule-out threshold):")
        out_lines.append(f"  2021-2025: rules out uniform-recruitment confounds > {mde_2125:.2f} pp")
        out_lines.append(f"  2021-2026: rules out uniform-recruitment confounds > {mde_2126:.2f} pp")
        out_lines.append("")
        out_lines.append("INTERPRETATION:")
        out_lines.append(f"  Adding 2026 data {'modestly improves' if r_2126['h_se'] < r_2125['h_se'] else 'leaves'} negative-control precision.")
        out_lines.append(f"  Headline finding (PSLF-hostile β NS in orthopedic surgery) is {'CONSISTENT' if abs(r_2126['h_beta']) < 3 and r_2126['h_p'] > 0.05 else 'DIFFERENT'} with prior 2021-2025-only result.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper3_negative_control_2021_2026_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
