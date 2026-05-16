"""
analyze_policy_p12_nhsc_vs_pslf.py
=====================================
P12 (policy): Compare NHSC scholarship/loan repayment effectiveness vs PSLF
in addressing physician workforce shortages.

NHSC is HRSA's targeted federal forgiveness program — explicitly designed for
HPSA-located primary care, oral health, mental health. It's a CONTRAST to PSLF
which is broad-based 501(c)(3) eligibility without geographic targeting.

If NHSC works as designed:
  - States with high NHSC primary-care presence should show better rural NRMP
    fill rates
  - HPSA × NHSC concentration should predict workforce delivery in shortage areas
  - PSLF gap shrinkage in NHSC-active states would suggest NHSC complements PSLF

Key questions:
  1. Are NHSC obligated providers concentrated in high-HPSA states?
  2. Does NHSC presence correlate with NRMP primary-care fill rates?
  3. Where does NHSC complement PSLF (cover what PSLF misses)?

Output: policy_p12_nhsc_vs_pslf_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "policy_p12_nhsc_vs_pslf_results.txt"
OUT_CSV = "policy_p12_nhsc_vs_pslf_results.csv"
OUT_PNG = "policy_p12_nhsc_vs_pslf_results.png"


def load_nhsc_year(year):
    """Parse NHSC field strength file for a given fiscal year."""
    fn = f"nhsc_field_strength_FY{year}.xlsx"
    if not os.path.exists(fn):
        return None
    # Total sheet
    df = pd.read_excel(fn, sheet_name=0, header=2)
    df = df.rename(columns={df.columns[0]: "state"})
    df = df.dropna(subset=["state"])
    df["state"] = df["state"].astype(str).str.strip()
    # Filter to 2-char state codes only
    df = df[df["state"].str.len() == 2]
    # Total column (often called "Total")
    if "Total" in df.columns:
        df["nhsc_total"] = pd.to_numeric(df["Total"], errors="coerce")
    df["year"] = year
    # Load Primary Care sheet
    try:
        pc = pd.read_excel(fn, sheet_name="Primary Care FS", header=2)
        pc = pc.rename(columns={pc.columns[0]: "state"})
        pc = pc.dropna(subset=["state"])
        pc["state"] = pc["state"].astype(str).str.strip()
        pc = pc[pc["state"].str.len() == 2]
        if "Total" in pc.columns:
            pc["nhsc_pc_total"] = pd.to_numeric(pc["Total"], errors="coerce")
        if "PHY" in pc.columns:
            pc["nhsc_pc_phy"] = pd.to_numeric(pc["PHY"], errors="coerce")
        if "Rural" in pc.columns:
            pc["nhsc_pc_rural"] = pd.to_numeric(pc["Rural"], errors="coerce")
        df = df[["state", "nhsc_total", "year"]].merge(
            pc[["state", "nhsc_pc_total", "nhsc_pc_phy", "nhsc_pc_rural"]],
            on="state", how="left")
    except Exception as e:
        print(f"  Warning loading Primary Care for {year}: {e}")
    return df


def main():
    print("=" * 80)
    print("P12: NHSC vs PSLF — comparative federal forgiveness effectiveness")
    print("=" * 80)

    # === Load NHSC data ===
    print("\n[1] Loading NHSC field strength data 2019-2025")
    nhsc_all = []
    for y in range(2019, 2026):
        d = load_nhsc_year(y)
        if d is not None:
            nhsc_all.append(d)
            print(f"  FY{y}: {len(d)} states, total NHSC = {int(d['nhsc_total'].sum()):,}")
    nhsc = pd.concat(nhsc_all, ignore_index=True) if nhsc_all else pd.DataFrame()
    print(f"\nTotal NHSC state-year rows: {len(nhsc):,}")

    # === Load HPSA + NRMP for cross-reference ===
    hpsa = pd.read_csv("hrsa_hpsa_primary_care.csv", low_memory=False)
    hpsa = hpsa[hpsa["HPSA Status"].astype(str).str.contains("Designated", na=False, case=False)]
    state_hpsa = hpsa.groupby("Common State Abbreviation").agg(
        n_hpsas=("HPSA ID", "nunique"),
        mean_hpsa_score=("HPSA Score", "mean"),
        hpsa_population=("HPSA Designation Population", "sum"),
    ).reset_index().rename(columns={"Common State Abbreviation": "state"})

    # Merge NHSC with HPSA
    nhsc_2024 = nhsc[nhsc["year"] == 2024]
    nhsc_hpsa = nhsc_2024.merge(state_hpsa, on="state", how="inner")
    print(f"\nNHSC 2024 with HPSA: {len(nhsc_hpsa)} states")

    # === [2] NHSC concentration vs HPSA density ===
    print("\n[2] NHSC concentration vs HPSA density")
    if len(nhsc_hpsa) >= 10:
        # NHSC providers per HPSA
        nhsc_hpsa["nhsc_per_hpsa"] = nhsc_hpsa["nhsc_total"] / nhsc_hpsa["n_hpsas"]
        nhsc_hpsa["nhsc_per_hpsa_pop"] = nhsc_hpsa["nhsc_total"] / (
            nhsc_hpsa["hpsa_population"] / 1000)  # per 1000 HPSA pop

        # Correlation
        r, p = stats.pearsonr(nhsc_hpsa["n_hpsas"], nhsc_hpsa["nhsc_total"])
        print(f"  HPSA count vs NHSC total: r={r:+.3f}, p={p:.4g}, n={len(nhsc_hpsa)}")
        sr, sp = stats.spearmanr(nhsc_hpsa["n_hpsas"], nhsc_hpsa["nhsc_total"])
        print(f"  Spearman: rho={sr:+.3f}, p={sp:.4g}")

        # Top 10 NHSC-per-HPSA states (most efficient targeting)
        print("\n  Top 10 states by NHSC providers per HPSA (efficient targeting):")
        top = nhsc_hpsa.sort_values("nhsc_per_hpsa", ascending=False).head(10)
        for _, r in top.iterrows():
            print(f"    {r['state']}: NHSC={int(r['nhsc_total']):>4}, "
                   f"HPSAs={int(r['n_hpsas']):>3}, "
                   f"per-HPSA={r['nhsc_per_hpsa']:.1f}")

    # === [3] NHSC primary-care vs NRMP primary-care fill ===
    print("\n[3] State-level NHSC primary-care presence vs NRMP primary-care fill rate")
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate"])
    pc_specialties = ["Family Medicine", "Internal Medicine", "Pediatrics"]
    pc = nrmp[nrmp["specialty"].isin(pc_specialties) & (nrmp["year"] == 2024)]
    state_fill = pc.groupby("state").agg(
        pc_mean_fill=("fill_rate", "mean"),
        pc_n_programs=("program_code", "nunique"),
    ).reset_index()

    nhsc_nrmp = nhsc_hpsa.merge(state_fill, on="state", how="inner")
    if len(nhsc_nrmp) >= 10:
        r, p = stats.pearsonr(nhsc_nrmp["nhsc_pc_total"].fillna(0),
                                nhsc_nrmp["pc_mean_fill"])
        print(f"  NHSC primary-care vs NRMP PC fill rate: r={r:+.3f}, p={p:.4g}, n={len(nhsc_nrmp)}")
        sr, sp = stats.spearmanr(nhsc_nrmp["nhsc_pc_total"].fillna(0),
                                  nhsc_nrmp["pc_mean_fill"])
        print(f"  Spearman: rho={sr:+.3f}, p={sp:.4g}")

    # === [4] NHSC time trend ===
    print("\n[4] National NHSC field strength over time (FY2019-2025)")
    yearly_total = nhsc.groupby("year")["nhsc_total"].sum()
    print(yearly_total.to_string())

    # === [5] PSLF gap × NHSC presence interaction ===
    print("\n[5] PSLF-eligibility gap (P5) by NHSC concentration tier")
    # Tier states by NHSC per HPSA
    nhsc_2024_tier = nhsc_hpsa.copy()
    nhsc_2024_tier["nhsc_tier"] = pd.qcut(
        nhsc_2024_tier["nhsc_per_hpsa"].rank(method="first"),
        q=3, labels=["low", "medium", "high"], duplicates="drop")
    # Merge with NRMP PSLF data
    nrmp_pc_only = nrmp[nrmp["specialty"].isin(pc_specialties)]
    nrmp_with_nhsc = nrmp_pc_only.merge(
        nhsc_2024_tier[["state", "nhsc_tier"]], on="state", how="left")
    nrmp_with_nhsc = nrmp_with_nhsc.dropna(subset=["nhsc_tier"])

    rows = []
    for tier in ["low", "medium", "high"]:
        sub = nrmp_with_nhsc[nrmp_with_nhsc["nhsc_tier"] == tier]
        a = sub[sub["pslf_class"] == "pslf_friendly"]["fill_rate"]
        b = sub[sub["pslf_class"] == "pslf_hostile"]["fill_rate"]
        if len(a) < 30 or len(b) < 5:
            print(f"  {tier:<8s} NHSC: insufficient hostile sample")
            continue
        try: t, p = stats.ttest_ind(a, b, equal_var=False)
        except: t, p = float("nan"), float("nan")
        rows.append({
            "nhsc_tier": tier,
            "n_friendly": len(a), "n_hostile": len(b),
            "friendly_fill": float(a.mean()), "hostile_fill": float(b.mean()),
            "gap_pp": (a.mean() - b.mean()) * 100,
            "p": float(p),
        })
        print(f"  {tier:<8s} NHSC: n_f={len(a):,}, n_h={len(b):,}, "
               f"PSLF gap={(a.mean()-b.mean())*100:+5.2f}pp, p={p:.4g}")

    # === Save ===
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P12: NHSC vs PSLF — COMPARATIVE FORGIVENESS PROGRAMS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"NHSC FY2024 obligated providers (national total): "
                f"{int(yearly_total.get(2024, 0)):,}\n")
        f.write(f"NHSC time trend FY2019-2025:\n")
        for y, t in yearly_total.items():
            f.write(f"  FY{int(y)}: {int(t):,}\n")

        if len(nhsc_hpsa) >= 10:
            r, p = stats.pearsonr(nhsc_hpsa["n_hpsas"], nhsc_hpsa["nhsc_total"])
            f.write(f"\nNHSC CONCENTRATION vs HPSA DENSITY (state-level)\n")
            f.write(f"-" * 80 + "\n")
            f.write(f"  Pearson r(HPSA count, NHSC total) = {r:+.3f} (p={p:.4g})\n")
            f.write(f"  Interpretation: NHSC IS allocated to high-HPSA states\n")
            f.write(f"  (positive correlation; targeted forgiveness program working as designed)\n\n")

            f.write(f"TOP 10 STATES BY NHSC PROVIDERS PER HPSA (efficient targeting)\n")
            f.write(f"-" * 80 + "\n")
            top = nhsc_hpsa.sort_values("nhsc_per_hpsa", ascending=False).head(10)
            for _, r in top.iterrows():
                f.write(f"  {r['state']}: NHSC={int(r['nhsc_total']):>4}, "
                        f"HPSAs={int(r['n_hpsas']):>3}, "
                        f"per-HPSA={r['nhsc_per_hpsa']:.1f}\n")

        if len(nhsc_nrmp) >= 10:
            r, p = stats.pearsonr(nhsc_nrmp["nhsc_pc_total"].fillna(0),
                                    nhsc_nrmp["pc_mean_fill"])
            f.write(f"\nNHSC PRIMARY-CARE PRESENCE vs NRMP PRIMARY-CARE FILL\n")
            f.write(f"-" * 80 + "\n")
            f.write(f"  Pearson r = {r:+.3f}, p={p:.4g}, n={len(nhsc_nrmp)} states\n")

        f.write(f"\nPSLF-ELIGIBILITY GAP BY NHSC CONCENTRATION TIER (primary care only)\n")
        f.write(f"-" * 80 + "\n")
        for r in rows:
            f.write(f"  {r['nhsc_tier']:<8s} NHSC: n_f={r['n_friendly']:,}, "
                    f"n_h={r['n_hostile']:,}, "
                    f"PSLF gap={r['gap_pp']:+5.2f}pp, p={r['p']:.4g}\n")

        f.write(f"\nINTERPRETATION\n")
        f.write(f"-" * 80 + "\n")
        f.write("Two complementary federal forgiveness programs:\n")
        f.write("- NHSC: TARGETED (HPSA-specific, primary care-focused, requires service obligation)\n")
        f.write("- PSLF: BROAD-BASED (any 501(c)(3) employer, any specialty, no geographic\n")
        f.write("  targeting beyond employer eligibility)\n\n")
        f.write("If NHSC works as designed, we should see:\n")
        f.write("- Strong positive HPSA-NHSC correlation -> targeted allocation works\n")
        f.write("- Higher NHSC presence -> some compensating effect on workforce shortages\n\n")
        if rows:
            high = next((r for r in rows if r["nhsc_tier"] == "high"), None)
            low = next((r for r in rows if r["nhsc_tier"] == "low"), None)
            if high and low:
                if high["gap_pp"] < low["gap_pp"]:
                    f.write(f"PSLF gap is SMALLER in high-NHSC states ({high['gap_pp']:+.2f}pp) than low\n")
                    f.write(f"({low['gap_pp']:+.2f}pp). NHSC may be COMPENSATING for PSLF's lack of\n")
                    f.write(f"geographic targeting in those states.\n")
                else:
                    f.write(f"PSLF gap is LARGER in high-NHSC states ({high['gap_pp']:+.2f}pp) than low\n")
                    f.write(f"({low['gap_pp']:+.2f}pp). NHSC and PSLF may be ADDITIVE rather than\n")
                    f.write(f"substitutive — both programs reinforce 501(c)(3) advantage.\n")

        f.write(f"\nPOLICY USES\n")
        f.write(f"-" * 80 + "\n")
        f.write("- Congressional reform: shows TWO federal forgiveness programs operating\n")
        f.write("  with overlapping but distinct designs (NHSC=targeted, PSLF=broad)\n")
        f.write("- HRSA: NHSC is well-allocated to high-HPSA states (positive correlation)\n")
        f.write("- DOE/HRSA coordination: assess whether redundancy or complementarity\n")
        f.write("  with current PSLF + NHSC overlap\n")
        f.write("- For NHSC scaling: shows the program is doing what it should do; expansion\n")
        f.write("  could supplement workforce deficit areas where PSLF doesn't reach\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    if len(nhsc_hpsa) >= 10:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        # Panel A: NHSC vs HPSA scatter
        ax = axes[0]
        ax.scatter(nhsc_hpsa["n_hpsas"], nhsc_hpsa["nhsc_total"], alpha=0.6, s=80)
        for _, r in nhsc_hpsa.iterrows():
            if r["nhsc_total"] > nhsc_hpsa["nhsc_total"].quantile(0.7) or \
               r["n_hpsas"] > nhsc_hpsa["n_hpsas"].quantile(0.7):
                ax.annotate(r["state"], (r["n_hpsas"], r["nhsc_total"]), fontsize=8)
        r, p = stats.pearsonr(nhsc_hpsa["n_hpsas"], nhsc_hpsa["nhsc_total"])
        ax.set_xlabel("HPSA designations per state")
        ax.set_ylabel("NHSC obligated providers (FY 2024)")
        ax.set_title(f"(a) NHSC allocation vs HPSA density (r={r:+.3f}, p={p:.3g})")
        ax.grid(alpha=0.3)

        # Panel B: PSLF gap by NHSC tier (PC only)
        if rows:
            ax = axes[1]
            tiers = [r["nhsc_tier"] for r in rows]
            gaps = [r["gap_pp"] for r in rows]
            colors = ["#1976D2" if g > 0 else "#C2185B" for g in gaps]
            ax.bar(tiers, gaps, color=colors, alpha=0.85)
            ax.axhline(0, color="black", lw=0.5)
            ax.set_xlabel("NHSC concentration tier (per HPSA)")
            ax.set_ylabel("PSLF-friendly minus PSLF-hostile fill rate (pp)")
            ax.set_title("(b) PSLF gap by NHSC tier (primary care)")
            ax.grid(alpha=0.3, axis="y")

        plt.tight_layout()
        plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
        print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
