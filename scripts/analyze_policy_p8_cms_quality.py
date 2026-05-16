"""
analyze_policy_p8_cms_quality.py
==================================
P8 (policy): Test whether PSLF fill-rate gap is QUALITY-driven or PSLF-driven.

Major audit concern: Are HCA hospitals less competitive because they're for-profit
(PSLF mechanism) or because they're lower quality?

Method:
  1. Match NRMP institutions to CMS Hospital Compare records by name + state
  2. Get hospital quality (overall rating 1-5) and CMS ownership classification
  3. Test: does the PSLF gap survive controlling for hospital quality?

CMS ownership categories that should be PSLF-relevant:
  - Government - Federal | Government - Hospital District or Authority |
    Government - Local | Government - State -> PSLF-eligible
  - Voluntary non-profit - Church | Voluntary non-profit - Other |
    Voluntary non-profit - Private -> PSLF-eligible
  - Proprietary -> NOT PSLF-eligible (this is the for-profit category)
  - Physician -> ambiguous (independent physician-owned, often for-profit but small)

Output: policy_p8_cms_quality_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, re, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "policy_p8_cms_quality_results.txt"
OUT_CSV = "policy_p8_cms_quality_results.csv"
OUT_PNG = "policy_p8_cms_quality_results.png"


def normalize_name(s):
    """Normalize hospital name for fuzzy matching."""
    if not isinstance(s, str): return ""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    # Remove common suffixes
    for suffix in ["medical center", "med ctr", "medical ctr", "med center",
                    "hospital", "hosp", "hospitals", "health system",
                    "health", "healthcare", "system", "ctr", "center", "inc",
                    "llc", "the"]:
        s = re.sub(rf"\b{suffix}\b", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def main():
    print("=" * 80)
    print("P8: PSLF gap vs CMS Hospital quality — confounding test")
    print("=" * 80)

    # Load CMS
    cms = pd.read_csv("cms_hospital_general.csv", low_memory=False)
    print(f"\nCMS hospitals: {len(cms):,}")
    print(f"Ownership distribution:")
    print(cms["Hospital Ownership"].value_counts().to_string())

    # Coerce overall rating to numeric
    cms["Hospital overall rating"] = pd.to_numeric(cms["Hospital overall rating"], errors="coerce")
    print(f"\nRating distribution (where available):")
    print(cms["Hospital overall rating"].value_counts(dropna=False).sort_index().to_string())

    # Map CMS ownership -> PSLF eligibility
    PSLF_ELIGIBLE_OWNERSHIPS = [
        "Government - Federal", "Government - Hospital District or Authority",
        "Government - Local", "Government - State",
        "Voluntary non-profit - Church", "Voluntary non-profit - Other",
        "Voluntary non-profit - Private",
    ]
    PSLF_INELIGIBLE_OWNERSHIPS = ["Proprietary"]
    cms["cms_pslf_class"] = cms["Hospital Ownership"].apply(
        lambda x: "pslf_eligible" if x in PSLF_ELIGIBLE_OWNERSHIPS
        else "pslf_ineligible_for_profit" if x in PSLF_INELIGIBLE_OWNERSHIPS
        else "ambiguous"
    )
    print(f"\nCMS-derived PSLF classification:")
    print(cms["cms_pslf_class"].value_counts().to_string())

    # Load NRMP
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate"])
    nrmp_inst = nrmp[["institution", "state", "city", "pslf_class"]].drop_duplicates()
    print(f"\nNRMP institutions: {len(nrmp_inst):,}")

    # Build name lookup
    cms["name_norm"] = cms["Facility Name"].apply(normalize_name)
    nrmp_inst["name_norm"] = nrmp_inst["institution"].apply(normalize_name)

    # Match on (state, name_norm)
    print("\n[1] Matching NRMP <-> CMS by (state, normalized name)")
    cms_lite = cms[["Facility ID", "Facility Name", "State", "City/Town",
                      "County/Parish", "Hospital Type", "Hospital Ownership",
                      "Hospital overall rating", "cms_pslf_class", "name_norm"]].copy()
    cms_lite = cms_lite.rename(columns={"State": "state"})

    matched = nrmp_inst.merge(cms_lite, on=["state", "name_norm"], how="left",
                                suffixes=("", "_cms"))
    n_matched = matched["Facility ID"].notna().sum()
    print(f"  Direct matches (state + normalized name): "
           f"{n_matched:,} / {len(nrmp_inst):,} ({n_matched/len(nrmp_inst)*100:.1f}%)")

    # For unmatched NRMP institutions, try fuzzy match on first 3 words of name
    unmatched = matched[matched["Facility ID"].isna()].copy()
    if len(unmatched) > 0:
        print(f"  Trying first-3-words fuzzy match on {len(unmatched):,} unmatched...")
        cms_lite["name_short"] = cms_lite["name_norm"].apply(lambda s: " ".join(s.split()[:3]))
        unmatched["name_short"] = unmatched["name_norm"].apply(lambda s: " ".join(s.split()[:3]))
        fuzzy = unmatched.drop(columns=[c for c in cms_lite.columns if c not in ["state", "name_short"]],
                                 errors="ignore")
        fuzzy = fuzzy.merge(cms_lite, on=["state", "name_short"], how="left", suffixes=("", "_cms"))
        n_fuzzy = fuzzy["Facility ID"].notna().sum()
        print(f"  First-3-words matches: {n_fuzzy:,}")

        # Combine: use original direct match where available, otherwise fuzzy
        matched_idx = set(matched[matched["Facility ID"].notna()].index)
        for idx, row in fuzzy.iterrows():
            if pd.notna(row["Facility ID"]) and idx not in matched_idx:
                matched.loc[idx, ["Facility ID", "Facility Name", "City/Town",
                                    "County/Parish", "Hospital Type", "Hospital Ownership",
                                    "Hospital overall rating", "cms_pslf_class"]] = (
                    row[["Facility ID", "Facility Name", "City/Town", "County/Parish",
                          "Hospital Type", "Hospital Ownership", "Hospital overall rating",
                          "cms_pslf_class"]].values
                )
        n_matched = matched["Facility ID"].notna().sum()
        print(f"  Total after fuzzy: {n_matched:,} ({n_matched/len(nrmp_inst)*100:.1f}%)")

    # Merge back to per-program-year NRMP data
    nrmp_with_cms = nrmp.merge(
        matched[["institution", "state", "Facility ID", "Hospital Ownership",
                  "Hospital overall rating", "cms_pslf_class"]],
        on=["institution", "state"], how="left")
    print(f"\nNRMP rows with CMS data: {nrmp_with_cms['Facility ID'].notna().sum():,}")

    # === Concordance: NRMP heuristic class vs CMS ownership-based class ===
    print("\n[2] Heuristic PSLF class vs CMS ownership-based PSLF class")
    matched_with_cms = matched.dropna(subset=["cms_pslf_class"])
    confusion = pd.crosstab(matched_with_cms["pslf_class"],
                              matched_with_cms["cms_pslf_class"])
    print(confusion.to_string())
    # Concordance rate
    diag = sum(confusion.loc[r, c] for r in confusion.index for c in confusion.columns
                if (r == "pslf_friendly" and c == "pslf_eligible") or
                   (r == "pslf_hostile" and c == "pslf_ineligible_for_profit"))
    total = confusion.values.sum()
    print(f"\n  Concordant (heuristic == CMS): {diag}/{total} = {diag/total*100:.1f}%")

    # === PSLF gap by CMS-derived class (more authoritative) ===
    print("\n[3] PSLF-eligibility gap using CMS-DERIVED ownership classification")
    a = nrmp_with_cms[nrmp_with_cms["cms_pslf_class"] == "pslf_eligible"]["fill_rate"]
    b = nrmp_with_cms[nrmp_with_cms["cms_pslf_class"] == "pslf_ineligible_for_profit"]["fill_rate"]
    if len(a) >= 30 and len(b) >= 5:
        t, p = stats.ttest_ind(a, b, equal_var=False)
        print(f"  CMS PSLF-eligible    : n={len(a):,}, mean fill = {a.mean():.4f}")
        print(f"  CMS PSLF-ineligible  : n={len(b):,}, mean fill = {b.mean():.4f}")
        print(f"  Δ = {(a.mean()-b.mean())*100:+.2f} pp, p={p:.4g}")

    # === Quality (star rating) by PSLF class ===
    print("\n[4] Hospital quality (1-5 star rating) by CMS PSLF class")
    for cls in ["pslf_eligible", "pslf_ineligible_for_profit", "ambiguous"]:
        sub = nrmp_with_cms[nrmp_with_cms["cms_pslf_class"] == cls].dropna(subset=["Hospital overall rating"])
        if len(sub) < 10: continue
        print(f"  {cls}: n={len(sub):,}, mean rating = "
               f"{sub['Hospital overall rating'].mean():.2f} (sd={sub['Hospital overall rating'].std():.2f})")

    # === KEY TEST: does PSLF gap survive controlling for star rating? ===
    print("\n[5] PSLF gap WITHIN star-rating tier (matched-quality comparison)")
    rows = []
    for star in [1.0, 2.0, 3.0, 4.0, 5.0]:
        sub = nrmp_with_cms[nrmp_with_cms["Hospital overall rating"] == star]
        a = sub[sub["cms_pslf_class"] == "pslf_eligible"]["fill_rate"]
        b = sub[sub["cms_pslf_class"] == "pslf_ineligible_for_profit"]["fill_rate"]
        if len(a) < 30 or len(b) < 5:
            print(f"  {star} stars: insufficient (n_e={len(a)}, n_i={len(b)})")
            rows.append({"stars": star, "n_eligible": len(a), "n_ineligible": len(b),
                          "gap_pp": float("nan")})
            continue
        try: t, p = stats.ttest_ind(a, b, equal_var=False)
        except: t, p = float("nan"), float("nan")
        rows.append({
            "stars": star, "n_eligible": len(a), "n_ineligible": len(b),
            "mean_eligible": float(a.mean()), "mean_ineligible": float(b.mean()),
            "gap_pp": (a.mean() - b.mean()) * 100, "p": float(p),
        })
        print(f"  {star} stars: n_e={len(a):,}, n_i={len(b):,}, "
               f"e_mean={a.mean():.4f}, i_mean={b.mean():.4f}, "
               f"Δ={(a.mean()-b.mean())*100:+5.2f}pp, p={p:.4g}")

    # OLS regression: fill_rate ~ pslf_eligible + star_rating + state FE
    print("\n[6] OLS regression: fill_rate ~ PSLF_eligible + star_rating + state FE")
    model_df = nrmp_with_cms.dropna(subset=["cms_pslf_class", "Hospital overall rating"])
    model_df = model_df[model_df["cms_pslf_class"].isin(["pslf_eligible", "pslf_ineligible_for_profit"])]
    if len(model_df) >= 100:
        try:
            import statsmodels.api as sm
            from statsmodels.formula.api import ols
            model_df["pslf_eligible"] = (model_df["cms_pslf_class"] == "pslf_eligible").astype(int)
            model_df["star"] = model_df["Hospital overall rating"]
            model = ols("fill_rate ~ pslf_eligible + star + C(state)", data=model_df).fit()
            print(f"  N={int(model.nobs)}, R^2={model.rsquared:.3f}")
            print(f"  PSLF_eligible coef: {model.params['pslf_eligible']:+.4f} "
                   f"(SE={model.bse['pslf_eligible']:.4f}, p={model.pvalues['pslf_eligible']:.4g})")
            print(f"  Star coef:          {model.params['star']:+.4f} "
                   f"(SE={model.bse['star']:.4f}, p={model.pvalues['star']:.4g})")
            ols_summary = {
                "n_obs": int(model.nobs),
                "r_squared": model.rsquared,
                "pslf_coef_pp": model.params["pslf_eligible"] * 100,
                "pslf_se_pp": model.bse["pslf_eligible"] * 100,
                "pslf_p": model.pvalues["pslf_eligible"],
                "star_coef_pp": model.params["star"] * 100,
                "star_se_pp": model.bse["star"] * 100,
                "star_p": model.pvalues["star"],
            }
        except Exception as e:
            print(f"  Regression failed: {e}")
            ols_summary = None
    else:
        ols_summary = None

    # Save
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P8: PSLF GAP vs HOSPITAL QUALITY (CMS Care Compare)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"CMS hospitals: {len(cms):,}\n")
        f.write(f"NRMP institutions: {len(nrmp_inst):,}\n")
        f.write(f"NRMP-CMS matched: {n_matched:,} ({n_matched/len(nrmp_inst)*100:.1f}%)\n")
        f.write(f"NRMP rows with CMS data: {nrmp_with_cms['Facility ID'].notna().sum():,}\n\n")

        f.write("HEURISTIC PSLF CLASS vs CMS-OWNERSHIP-DERIVED PSLF CLASS\n")
        f.write("-" * 80 + "\n")
        f.write(confusion.to_string() + "\n")
        f.write(f"\nConcordance rate: {diag/total*100:.1f}%\n\n")

        f.write("CMS-DERIVED PSLF GAP\n")
        f.write("-" * 80 + "\n")
        if len(a) >= 30 and len(b) >= 5:
            f.write(f"  CMS PSLF-eligible:     n={len(a):,}, mean fill = {a.mean():.4f}\n")
            f.write(f"  CMS PSLF-ineligible:   n={len(b):,}, mean fill = {b.mean():.4f}\n")
            f.write(f"  Gap: {(a.mean()-b.mean())*100:+.2f} pp, p={p:.4g}\n\n")

        f.write("HOSPITAL QUALITY (Overall Star Rating) BY PSLF CLASS\n")
        f.write("-" * 80 + "\n")
        for cls in ["pslf_eligible", "pslf_ineligible_for_profit", "ambiguous"]:
            sub = nrmp_with_cms[nrmp_with_cms["cms_pslf_class"] == cls].dropna(subset=["Hospital overall rating"])
            if len(sub) < 10: continue
            f.write(f"  {cls}: n={len(sub):,}, mean rating = "
                    f"{sub['Hospital overall rating'].mean():.2f}\n")

        f.write("\nWITHIN-STAR-TIER PSLF GAP (matched-quality comparison)\n")
        f.write("-" * 80 + "\n")
        for r in rows:
            if not np.isnan(r["gap_pp"]):
                f.write(f"  {r['stars']} stars: n_e={r['n_eligible']:,}, n_i={r['n_ineligible']:,}, "
                        f"gap={r['gap_pp']:+.2f}pp, p={r['p']:.4g}\n")

        if ols_summary:
            f.write("\nOLS REGRESSION: fill_rate ~ PSLF_eligible + star_rating + state_FE\n")
            f.write("-" * 80 + "\n")
            f.write(f"  N obs: {ols_summary['n_obs']:,}\n")
            f.write(f"  R-squared: {ols_summary['r_squared']:.4f}\n")
            f.write(f"  PSLF-eligible coef: {ols_summary['pslf_coef_pp']:+.2f} pp "
                    f"(SE={ols_summary['pslf_se_pp']:.2f}pp, p={ols_summary['pslf_p']:.4g})\n")
            f.write(f"  Star rating coef: {ols_summary['star_coef_pp']:+.2f} pp/star "
                    f"(SE={ols_summary['star_se_pp']:.2f}, p={ols_summary['star_p']:.4g})\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("Critical test: if the PSLF-eligibility coefficient survives controlling\n")
        f.write("for hospital quality (star rating) and state fixed effects, the +12.86pp\n")
        f.write("PSLF gap reflects the PSLF mechanism, not a quality differential.\n\n")
        if ols_summary and ols_summary["pslf_p"] < 0.05:
            f.write(f"VERDICT: PSLF-eligibility coefficient = {ols_summary['pslf_coef_pp']:+.2f}pp "
                    f"(p={ols_summary['pslf_p']:.4g}) — \n")
            f.write("the PSLF effect SURVIVES quality controls. The fill-rate gap is\n")
            f.write("not just a quality artifact.\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: gap by star rating
    ax = axes[0]
    plot_rows = [r for r in rows if not np.isnan(r["gap_pp"])]
    if plot_rows:
        stars = [r["stars"] for r in plot_rows]
        gaps = [r["gap_pp"] for r in plot_rows]
        ax.bar(stars, gaps, color="steelblue", alpha=0.85)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_xlabel("CMS hospital overall star rating")
        ax.set_ylabel("PSLF-eligible − ineligible fill-rate gap (pp)")
        ax.set_title("(a) PSLF gap WITHIN each quality tier (matched-quality)")
        ax.grid(alpha=0.3, axis="y")

    # Panel B: quality distribution by class
    ax = axes[1]
    for cls, color in [("pslf_eligible", "green"), ("pslf_ineligible_for_profit", "red"),
                         ("ambiguous", "gray")]:
        sub = nrmp_with_cms[nrmp_with_cms["cms_pslf_class"] == cls].dropna(subset=["Hospital overall rating"])
        if len(sub) < 10: continue
        ax.hist(sub["Hospital overall rating"], bins=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
                 alpha=0.5, label=f"{cls} (n={len(sub):,})", color=color)
    ax.set_xlabel("Hospital overall star rating")
    ax.set_ylabel("Number of NRMP program-years")
    ax.set_title("(b) Quality distribution by PSLF class")
    ax.legend()

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
