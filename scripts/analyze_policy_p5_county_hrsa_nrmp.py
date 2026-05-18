"""
analyze_policy_p5_county_hrsa_nrmp.py
========================================
P5 (policy): County-level HRSA HPSA × NRMP cross-reference.

Now that NRMP institutions have city populated (extract_nrmp_cities.py),
match (city, state) -> county via simpler heuristic + existing public sources,
then aggregate HPSA designations to county level and re-test the PSLF gap.

Approach:
  1. Use HPSA's `Common County Name` + state to build (state, county) -> n_hpsas
  2. For each NRMP institution, map (city, state) -> county via lookup table
     (build from HPSA data which has both county and city info, or use a
     simple state+major-city -> county mapping)
  3. Compute county-level metrics: PSLF-friendly fill, PSLF-hostile fill,
     n_hpsas in that county
  4. Test correlation: county HPSA designation count vs PSLF-eligibility gap

Output: policy_p5_county_hrsa_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "policy_p5_county_hrsa_results.txt"
OUT_CSV = "policy_p5_county_hrsa_results.csv"
OUT_PNG = "policy_p5_county_hrsa_results.png"


def main():
    print("=" * 80)
    print("P5: County-level HRSA HPSA x NRMP")
    print("=" * 80)

    # Load HPSA — already filtered to designated primary care
    hpsa = pd.read_csv("hrsa_hpsa_primary_care.csv", low_memory=False)
    hpsa = hpsa[hpsa["HPSA Status"].astype(str).str.contains("Designated",
                                                                na=False, case=False)]
    print(f"\nDesignated HPSAs: {len(hpsa):,}")

    # County metrics
    county_metrics = hpsa.groupby(
        ["Common State Abbreviation", "Common County Name"]
    ).agg(
        n_hpsas=("HPSA ID", "nunique"),
        mean_score=("HPSA Score", "mean"),
        max_score=("HPSA Score", "max"),
        sum_population=("HPSA Designation Population", "sum"),
    ).reset_index()
    county_metrics.columns = ["state", "county", "n_hpsas",
                                "mean_hpsa_score", "max_hpsa_score", "hpsa_population"]
    print(f"  Counties with HPSAs: {len(county_metrics):,}")

    # Load NRMP with city
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate"])
    print(f"\nNRMP rows with fill_rate: {len(nrmp):,}")
    print(f"  Rows with city: {nrmp['city'].notna().sum():,}")

    # Build city -> county lookup from US Cities database (SimpleMaps)
    print("\n[1] City -> county mapping via SimpleMaps US Cities")
    cities = pd.read_csv("uscities.csv",
                          usecols=["city_ascii", "state_id", "county_name", "population"])
    # Pick most-populous match per (state, city) for ambiguous duplicates
    cities = cities.sort_values("population", ascending=False)
    cities = cities.drop_duplicates(subset=["state_id", "city_ascii"], keep="first")
    cities["city_lower"] = cities["city_ascii"].str.lower().str.strip()
    cities["county_lower"] = cities["county_name"].str.lower().str.strip()

    nrmp["city_lower"] = nrmp["city"].fillna("").str.lower().str.strip()
    nrmp_with_county = nrmp.merge(
        cities[["state_id", "city_lower", "county_lower", "county_name"]],
        left_on=["state", "city_lower"], right_on=["state_id", "city_lower"],
        how="left")
    matched_county = nrmp_with_county["county_name"].notna().sum()
    print(f"  NRMP institutions matched to county: {matched_county:,} / {len(nrmp):,} "
          f"({matched_county/len(nrmp)*100:.1f}%)")

    # Now merge with HPSA county metrics
    # HPSA format: "Jefferson County, AL" -> strip both "County" and ", XX" suffix
    county_metrics["county_lower"] = county_metrics["county"].fillna("").str.lower().str.strip()
    county_metrics["county_lower"] = county_metrics["county_lower"].str.replace(
        r"\s+county,?\s*[a-z]{0,2}\s*$", "", regex=True)
    county_metrics["county_lower"] = county_metrics["county_lower"].str.replace(
        r",\s*[a-z]{2}\s*$", "", regex=True)
    # For Alaska boroughs and Louisiana parishes:
    county_metrics["county_lower"] = county_metrics["county_lower"].str.replace(
        r"\s+(?:borough|parish|census area|city and borough),?\s*[a-z]{0,2}\s*$",
        "", regex=True)
    county_metrics["county_lower"] = county_metrics["county_lower"].str.strip()

    nrmp_county = nrmp_with_county.merge(
        county_metrics, left_on=["state", "county_lower"],
        right_on=["state", "county_lower"], how="left", suffixes=("", "_hpsa"))
    matched = nrmp_county["n_hpsas"].notna().sum()
    print(f"  NRMP-county matched to HPSA: {matched:,} / {len(nrmp_county):,} "
          f"({matched/len(nrmp_county)*100:.1f}%)")

    # Compute per-county metrics
    nrmp_county = nrmp_county.dropna(subset=["n_hpsas"])
    if len(nrmp_county) == 0:
        print("[ABORT] No matched institutions to county-level HPSA")
        return
    nrmp_county["hpsa_severity_tier"] = pd.qcut(
        nrmp_county["n_hpsas"].rank(method="first"),
        q=3, labels=["low", "medium", "high"], duplicates="drop")

    print("\n[2] PSLF-eligibility gap by county HPSA-severity tier")
    rows = []
    for tier in ["low", "medium", "high"]:
        sub = nrmp_county[nrmp_county["hpsa_severity_tier"] == tier]
        a = sub[sub["pslf_class"] == "pslf_friendly"]["fill_rate"]
        b = sub[sub["pslf_class"] == "pslf_hostile"]["fill_rate"]
        if len(a) < 30: continue
        a_mean = float(a.mean())
        if len(b) < 5:
            print(f"  {tier:<8s}: friendly={a_mean:.4f} (n={len(a):,}), "
                   f"hostile insufficient (n={len(b)})")
            rows.append({"tier": tier, "n_friendly": len(a), "n_hostile": len(b),
                          "friendly_fill": a_mean, "hostile_fill": float("nan"),
                          "gap_pp": float("nan"), "p": float("nan")})
            continue
        t, p = stats.ttest_ind(a, b, equal_var=False)
        rows.append({
            "tier": tier, "n_friendly": len(a), "n_hostile": len(b),
            "friendly_fill": a_mean, "hostile_fill": float(b.mean()),
            "gap_pp": (a_mean - b.mean()) * 100,
            "t": float(t), "p": float(p),
        })
        print(f"  {tier:<8s}: friendly={a_mean:.4f} (n={len(a):,}), "
              f"hostile={b.mean():.4f} (n={len(b):,}), "
              f"Δ={(a_mean-b.mean())*100:+.2f}pp, p={p:.4g}")

    # County-level per-program type
    print("\n[3] Top 15 most-shortage counties with NRMP programs")
    county_summary = nrmp_county.groupby(["state", "county"]).agg(
        n_programs=("program_code", "nunique"),
        mean_fill=("fill_rate", "mean"),
        n_hpsas=("n_hpsas", "first"),
        max_hpsa_score=("max_hpsa_score", "first"),
    ).reset_index().sort_values("max_hpsa_score", ascending=False)
    print(county_summary.head(15).round(2).to_string(index=False))

    # === Save ===
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")
    county_summary.to_csv(OUT_CSV.replace(".csv", "_counties.csv"),
                            index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P5: COUNTY-LEVEL HRSA HPSA x NRMP\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Designated HPSAs: {len(hpsa):,}\n")
        f.write(f"Counties with HPSAs: {len(county_metrics):,}\n")
        f.write(f"NRMP institutions matched to counties: {nrmp_county['institution'].nunique():,}\n")
        f.write(f"Match rate (direct city==county): {matched/len(nrmp):.1%}\n\n")

        f.write("PSLF-ELIGIBILITY GAP BY COUNTY HPSA-SEVERITY TIER\n")
        f.write("-" * 80 + "\n")
        for r in rows:
            ci_str = (f"Δ={r['gap_pp']:+.2f}pp, p={r['p']:.4g}"
                      if not np.isnan(r["gap_pp"]) else "n_hostile insufficient")
            f.write(f"  {r['tier']:<8s}: n_friendly={r['n_friendly']:,} "
                    f"friendly_fill={r['friendly_fill']:.4f}  {ci_str}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        valid_rows = [r for r in rows if not np.isnan(r["gap_pp"])]
        if len(valid_rows) >= 2:
            high = next((r for r in valid_rows if r["tier"] == "high"), None)
            low = next((r for r in valid_rows if r["tier"] == "low"), None)
            if high and low:
                f.write(f"  High-shortage county gap: {high['gap_pp']:+.2f} pp\n")
                f.write(f"  Low-shortage county gap:  {low['gap_pp']:+.2f} pp\n")
                if high["gap_pp"] > low["gap_pp"] + 3:
                    f.write("  -> Gap WIDER in high-shortage counties.\n"
                             "     PSLF preferentially channels physicians to underserved counties via 501(c)(3) employers.\n")
                elif high["gap_pp"] < low["gap_pp"] - 3:
                    f.write("  -> Gap NARROWER in high-shortage counties.\n"
                             "     PSLF benefit is muted in highest-shortage areas where for-profit alternatives may not exist.\n")
                else:
                    f.write("  -> Gap is similar across county shortage tiers.\n"
                             "     PSLF supports 501(c)(3) recruitment uniformly regardless of geographic shortage.\n")

        f.write("\nCAVEATS\n")
        f.write("-" * 80 + "\n")
        f.write("- Direct city==county-name matching captures only some institutions;\n")
        f.write("  ZIP-level geocoding would improve coverage substantially\n")
        f.write("- HPSA designations are population-/geographic-/facility-typed; this\n")
        f.write("  analysis pools all designation types within a county\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    if len(nrmp_county) >= 100:
        fig, ax = plt.subplots(figsize=(10, 6))
        county_summary_plot = county_summary[county_summary["n_programs"] >= 1].copy()
        scatter = ax.scatter(county_summary_plot["n_hpsas"],
                              county_summary_plot["mean_fill"],
                              s=np.sqrt(county_summary_plot["n_programs"]) * 5,
                              alpha=0.6,
                              c=county_summary_plot["max_hpsa_score"],
                              cmap="Reds")
        ax.set_xlabel("Number of HPSAs in county")
        ax.set_ylabel("Mean NRMP fill rate")
        ax.set_title(f"P5: County-level HRSA HPSA × NRMP fill (n_counties={len(county_summary_plot)})")
        plt.colorbar(scatter, ax=ax, label="Max HPSA score (severity)")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
        print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
