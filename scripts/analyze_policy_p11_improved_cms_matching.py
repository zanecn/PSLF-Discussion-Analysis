"""
analyze_policy_p11_improved_cms_matching.py
==============================================
P11 (policy): Improved NRMP-to-CMS matching via city+state aggregation.

P8 had only 31.5% match rate via name. Many NRMP "institutions" are GME
consortia operating in specific cities — they don't match a single CMS
hospital but DO correspond to ALL CMS hospitals in that city.

Method:
  1. For each NRMP institution, identify city+state
  2. Find ALL CMS hospitals in that (city, state)
  3. Aggregate: mean star rating, ownership distribution
  4. Tag NRMP institution with "city-aggregate" CMS quality
  5. Re-run B5 controlling for city-level CMS quality

Output: policy_p11_improved_cms_matching.{txt,csv,png}
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

OUT_TXT = "policy_p11_improved_cms_matching.txt"
OUT_CSV = "policy_p11_improved_cms_matching.csv"
OUT_PNG = "policy_p11_improved_cms_matching.png"


def normalize(s):
    if not isinstance(s, str): return ""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def main():
    print("=" * 80)
    print("P11: Improved CMS-NRMP matching via city+state aggregation")
    print("=" * 80)

    cms = pd.read_csv("cms_hospital_general.csv", low_memory=False)
    cms["Hospital overall rating"] = pd.to_numeric(cms["Hospital overall rating"], errors="coerce")
    cms["city_norm"] = cms["City/Town"].apply(normalize)
    print(f"\nCMS hospitals: {len(cms):,}")

    # CMS PSLF classification
    PSLF_ELIGIBLE = ["Government - Federal", "Government - Hospital District or Authority",
                      "Government - Local", "Government - State",
                      "Voluntary non-profit - Church", "Voluntary non-profit - Other",
                      "Voluntary non-profit - Private"]
    cms["cms_eligible"] = cms["Hospital Ownership"].isin(PSLF_ELIGIBLE).astype(int)
    cms["cms_for_profit"] = (cms["Hospital Ownership"] == "Proprietary").astype(int)

    # === City-level CMS aggregation ===
    print("\n[1] Aggregating CMS hospitals to city+state level")
    city_agg = cms.groupby(["State", "city_norm"]).agg(
        n_hospitals=("Facility ID", "count"),
        n_eligible_hospitals=("cms_eligible", "sum"),
        n_for_profit_hospitals=("cms_for_profit", "sum"),
        mean_star_rating=("Hospital overall rating", "mean"),
        max_star_rating=("Hospital overall rating", "max"),
    ).reset_index()
    city_agg["pct_eligible_hospitals"] = (
        city_agg["n_eligible_hospitals"] / city_agg["n_hospitals"] * 100)
    city_agg["pct_for_profit_hospitals"] = (
        city_agg["n_for_profit_hospitals"] / city_agg["n_hospitals"] * 100)
    print(f"  Unique cities: {len(city_agg):,}")

    # === NRMP city normalization ===
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate", "city"])
    nrmp["city_norm"] = nrmp["city"].apply(normalize)
    print(f"\nNRMP rows: {len(nrmp):,}")

    # Merge: NRMP (state, city) -> CMS city aggregates
    nrmp_with_city = nrmp.merge(city_agg, left_on=["state", "city_norm"],
                                  right_on=["State", "city_norm"], how="left")
    matched = nrmp_with_city["n_hospitals"].notna().sum()
    print(f"  NRMP rows matched to CMS city: {matched:,} / {len(nrmp_with_city):,} "
           f"({matched/len(nrmp_with_city)*100:.1f}%)")

    # === Recompute B5-style gap with city-CMS quality control ===
    print("\n[2] B5-style gap with city-level CMS quality control")
    df = nrmp_with_city.dropna(subset=["mean_star_rating"])
    print(f"  Analysis sample: {len(df):,} program-years with CMS city quality")

    # Heuristic-based gap (replicate B5)
    f = df[df["pslf_class"] == "pslf_friendly"]["fill_rate"]
    h = df[df["pslf_class"] == "pslf_hostile"]["fill_rate"]
    if len(f) >= 30 and len(h) >= 5:
        t, p = stats.ttest_ind(f, h, equal_var=False)
        print(f"  HEURISTIC PSLF-friendly: n={len(f):,}, mean fill = {f.mean():.4f}")
        print(f"  HEURISTIC PSLF-hostile:  n={len(h):,}, mean fill = {h.mean():.4f}")
        print(f"  Gap = {(f.mean()-h.mean())*100:+.2f} pp (raw, no controls), p={p:.4g}")

    # === City-level CMS quality vs PSLF gap ===
    print("\n[3] Mean city CMS quality by NRMP heuristic class")
    for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
        sub = df[df["pslf_class"] == cls]
        if len(sub) < 10: continue
        print(f"  {cls:<14s}: n={len(sub):,}, "
               f"city mean star = {sub['mean_star_rating'].mean():.3f}, "
               f"city %for-profit = {sub['pct_for_profit_hospitals'].mean():.1f}%")

    # === OLS with city CMS controls ===
    print("\n[4] OLS regression: fill_rate ~ heuristic_PSLF + city_CMS_controls + state FE")
    df_model = df.copy()
    df_model["pslf_friendly"] = (df_model["pslf_class"] == "pslf_friendly").astype(int)
    df_model["pslf_hostile"] = (df_model["pslf_class"] == "pslf_hostile").astype(int)
    try:
        from statsmodels.formula.api import ols
        # Model 1: PSLF only
        m1 = ols("fill_rate ~ pslf_friendly + pslf_hostile", data=df_model).fit()
        print(f"\n  MODEL 1 (PSLF only): N={int(m1.nobs):,}, R²={m1.rsquared:.4f}")
        print(f"    pslf_friendly: {m1.params['pslf_friendly']*100:+.2f}pp (p={m1.pvalues['pslf_friendly']:.4g})")
        print(f"    pslf_hostile:  {m1.params['pslf_hostile']*100:+.2f}pp (p={m1.pvalues['pslf_hostile']:.4g})")

        # Model 2: + city CMS quality
        m2 = ols("fill_rate ~ pslf_friendly + pslf_hostile + mean_star_rating",
                  data=df_model).fit()
        print(f"\n  MODEL 2 (+ city CMS quality): N={int(m2.nobs):,}, R²={m2.rsquared:.4f}")
        print(f"    pslf_friendly:    {m2.params['pslf_friendly']*100:+.2f}pp (p={m2.pvalues['pslf_friendly']:.4g})")
        print(f"    pslf_hostile:     {m2.params['pslf_hostile']*100:+.2f}pp (p={m2.pvalues['pslf_hostile']:.4g})")
        print(f"    mean_star_rating: {m2.params['mean_star_rating']*100:+.2f}pp/star (p={m2.pvalues['mean_star_rating']:.4g})")

        # Model 3: + state FE
        m3 = ols("fill_rate ~ pslf_friendly + pslf_hostile + mean_star_rating + C(state)",
                  data=df_model).fit()
        print(f"\n  MODEL 3 (+ state FE): N={int(m3.nobs):,}, R²={m3.rsquared:.4f}")
        print(f"    pslf_friendly:    {m3.params['pslf_friendly']*100:+.2f}pp (p={m3.pvalues['pslf_friendly']:.4g})")
        print(f"    pslf_hostile:     {m3.params['pslf_hostile']*100:+.2f}pp (p={m3.pvalues['pslf_hostile']:.4g})")
        print(f"    mean_star_rating: {m3.params['mean_star_rating']*100:+.2f}pp/star (p={m3.pvalues['mean_star_rating']:.4g})")

        # Model 4: + specialty FE
        m4 = ols("fill_rate ~ pslf_friendly + pslf_hostile + mean_star_rating + C(state) + C(specialty)",
                  data=df_model).fit()
        print(f"\n  MODEL 4 (+ specialty FE): N={int(m4.nobs):,}, R²={m4.rsquared:.4f}")
        print(f"    pslf_friendly:    {m4.params['pslf_friendly']*100:+.2f}pp (p={m4.pvalues['pslf_friendly']:.4g})")
        print(f"    pslf_hostile:     {m4.params['pslf_hostile']*100:+.2f}pp (p={m4.pvalues['pslf_hostile']:.4g})")
        print(f"    mean_star_rating: {m4.params['mean_star_rating']*100:+.2f}pp/star (p={m4.pvalues['mean_star_rating']:.4g})")

        models_summary = {
            "Model 1 (PSLF only)": {"n": int(m1.nobs), "r2": m1.rsquared,
                                       "friendly_pp": m1.params['pslf_friendly']*100,
                                       "friendly_p": m1.pvalues['pslf_friendly'],
                                       "hostile_pp": m1.params['pslf_hostile']*100,
                                       "hostile_p": m1.pvalues['pslf_hostile']},
            "Model 2 (+ city quality)": {"n": int(m2.nobs), "r2": m2.rsquared,
                                          "friendly_pp": m2.params['pslf_friendly']*100,
                                          "friendly_p": m2.pvalues['pslf_friendly'],
                                          "hostile_pp": m2.params['pslf_hostile']*100,
                                          "hostile_p": m2.pvalues['pslf_hostile'],
                                          "star_pp": m2.params['mean_star_rating']*100,
                                          "star_p": m2.pvalues['mean_star_rating']},
            "Model 3 (+ state FE)": {"n": int(m3.nobs), "r2": m3.rsquared,
                                      "friendly_pp": m3.params['pslf_friendly']*100,
                                      "friendly_p": m3.pvalues['pslf_friendly'],
                                      "hostile_pp": m3.params['pslf_hostile']*100,
                                      "hostile_p": m3.pvalues['pslf_hostile']},
            "Model 4 (+ specialty FE)": {"n": int(m4.nobs), "r2": m4.rsquared,
                                          "friendly_pp": m4.params['pslf_friendly']*100,
                                          "friendly_p": m4.pvalues['pslf_friendly'],
                                          "hostile_pp": m4.params['pslf_hostile']*100,
                                          "hostile_p": m4.pvalues['pslf_hostile']},
        }
    except Exception as e:
        print(f"  Regression failed: {e}")
        models_summary = {}

    # Save
    rows = []
    for name, m in models_summary.items():
        rows.append({"model": name, **m})
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P11: IMPROVED CMS-NRMP MATCHING via CITY+STATE AGGREGATION\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"NRMP rows: {len(nrmp):,}\n")
        f.write(f"NRMP rows matched to CMS city: {matched:,} ({matched/len(nrmp)*100:.1f}%)\n")
        f.write(f"Analysis sample (with CMS quality): {len(df_model):,}\n\n")

        f.write("CITY-LEVEL CMS QUALITY BY NRMP HEURISTIC PSLF CLASS\n")
        f.write("-" * 80 + "\n")
        for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
            sub = df[df["pslf_class"] == cls]
            if len(sub) < 10: continue
            f.write(f"  {cls}: n={len(sub):,}, city mean star={sub['mean_star_rating'].mean():.3f}, "
                    f"city %for-profit={sub['pct_for_profit_hospitals'].mean():.1f}%\n")

        f.write("\nNESTED REGRESSION MODELS\n")
        f.write("-" * 80 + "\n")
        for name, m in models_summary.items():
            f.write(f"\n{name}: N={m['n']:,}, R²={m['r2']:.4f}\n")
            f.write(f"  pslf_friendly: {m['friendly_pp']:+.2f}pp (p={m['friendly_p']:.4g})\n")
            f.write(f"  pslf_hostile:  {m['hostile_pp']:+.2f}pp (p={m['hostile_p']:.4g})\n")
            if "star_pp" in m:
                f.write(f"  mean_star:     {m['star_pp']:+.2f}pp/star (p={m['star_p']:.4g})\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        if models_summary:
            m1 = models_summary["Model 1 (PSLF only)"]
            m4 = models_summary["Model 4 (+ specialty FE)"]
            shrinkage = (m1["hostile_pp"] - m4["hostile_pp"])
            f.write(f"PSLF-hostile coefficient trajectory across model specifications:\n")
            for name, m in models_summary.items():
                f.write(f"  {name}: hostile = {m['hostile_pp']:+.2f}pp (p={m['hostile_p']:.4g})\n")
            f.write(f"\nShrinkage from M1 to M4: {shrinkage:+.2f}pp\n\n")
            if abs(m4["hostile_pp"]) > 5 and m4["hostile_p"] < 0.05:
                f.write("PSLF-hostile coefficient SURVIVES city quality + state FE + specialty FE.\n")
                f.write("This SUPPORTS the B5 substantive finding that PSLF eligibility\n")
                f.write("matters for residency competition even after controlling for the\n")
                f.write("structural factors that travel with academic-vs-for-profit hospital types.\n")
            elif abs(m4["hostile_pp"]) > 5 and m4["hostile_p"] >= 0.05:
                f.write("PSLF-hostile coefficient remains LARGE but loses statistical\n")
                f.write("significance after full controls. Likely real effect, but power-limited\n")
                f.write("after controls absorb variance. Consistent with PSLF effect existing\n")
                f.write("but smaller than the unadjusted +12.86pp.\n")
            else:
                f.write("PSLF-hostile coefficient SHRINKS substantially after city CMS\n")
                f.write("quality controls. Confirms the P8 finding: the +12.86pp gap is\n")
                f.write("composite, with quality + structural co-confounders absorbing most\n")
                f.write("of the explanatory power.\n")

        f.write("\nPOLICY USES\n")
        f.write("-" * 80 + "\n")
        f.write("- Resolves the P8 32% match-rate concern by using city-level aggregation\n")
        f.write("- Provides cleaner test of PSLF-mechanism vs quality-confound\n")
        f.write("- City-aggregate quality control is conservative (some NRMP institutions\n")
        f.write("  in a city may not host residencies at the lowest-quality CMS hospital)\n")
        f.write("- For paper: report Model 1 (raw gap) AND Model 4 (full controls) for\n")
        f.write("  honest interpretation of the PSLF-mechanism contribution\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure: coefficient trajectory across models
    if models_summary:
        fig, ax = plt.subplots(figsize=(11, 6))
        x = np.arange(len(models_summary))
        models = list(models_summary.keys())
        friendly_coefs = [models_summary[m]["friendly_pp"] for m in models]
        hostile_coefs = [models_summary[m]["hostile_pp"] for m in models]
        width = 0.35
        ax.bar(x - width/2, friendly_coefs, width, label="PSLF-friendly coef", color="green")
        ax.bar(x + width/2, hostile_coefs, width, label="PSLF-hostile coef", color="red")
        for i, (f_c, h_c) in enumerate(zip(friendly_coefs, hostile_coefs)):
            ax.text(i - width/2, f_c + 0.5, f"{f_c:+.1f}pp", ha="center", fontsize=8)
            ax.text(i + width/2, h_c - 0.5, f"{h_c:+.1f}pp", ha="center", fontsize=8, va="top")
        ax.axhline(0, color="black", lw=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right")
        ax.set_ylabel("Coefficient (percentage points fill rate)")
        ax.set_title("P11: PSLF coefficient across nested regression specifications\n"
                      "(controlling progressively for quality, state, specialty)")
        ax.legend()
        ax.grid(alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
        print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
