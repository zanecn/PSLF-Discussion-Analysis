"""
analyze_policy_hrsa_hpsa_nrmp.py
==================================
P4 (policy): Cross-reference NRMP residency programs with HRSA Health Professional
Shortage Area (HPSA) data.

Key policy question: Does PSLF actually channel physicians INTO underserved areas
(its stated workforce policy goal)? Test by comparing fill rates of PSLF-eligible
vs PSLF-ineligible programs in HPSAs vs non-HPSAs.

If the PSLF mechanism is working as intended:
  - PSLF-eligible programs in HPSAs should fill especially well (PSLF + mission alignment)
  - PSLF-ineligible programs in HPSAs should fill especially poorly (no PSLF benefit
    in already-underserved areas)
  - Gap should widen in HPSAs

If PSLF doesn't reach shortage areas as designed:
  - HPSA designation would not interact with PSLF eligibility

Output: policy_hrsa_hpsa_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, sys, urllib.request, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "policy_hrsa_hpsa_results.txt"
OUT_CSV = "policy_hrsa_hpsa_results.csv"
OUT_PNG = "policy_hrsa_hpsa_results.png"
HPSA_CSV = "hrsa_hpsa_primary_care.csv"

# HRSA HPSA download URL — primary care HPSA data, public
# Most current dataset URL is at https://data.hrsa.gov/data/download
# Try the standard pattern first
HPSA_URLS = [
    # Primary care HPSA (csv export)
    "https://data.hrsa.gov/DataDownload/DD_Files/BCD_HPSA_FCT_DET_PC.csv",
    # Alternative: zip with multiple types
    "https://data.hrsa.gov/DataDownload/DD_Files/HPSA_PRIMARY_CARE.csv",
]


def download_hpsa():
    """Try multiple URL patterns for the HRSA HPSA file."""
    if os.path.exists(HPSA_CSV) and os.path.getsize(HPSA_CSV) > 1_000_000:
        print(f"  HPSA file exists: {HPSA_CSV} ({os.path.getsize(HPSA_CSV)/1024/1024:.1f} MB)")
        return True
    for url in HPSA_URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) < 100_000:
                print(f"  Too small at {url}: {len(data)} bytes")
                continue
            with open(HPSA_CSV, "wb") as f: f.write(data)
            print(f"  Downloaded {url} -> {HPSA_CSV} ({len(data)/1024/1024:.1f} MB)")
            return True
        except Exception as e:
            print(f"  Failed {url}: {str(e)[:120]}")
    return False


def main():
    print("=" * 80)
    print("P4: NRMP residency programs x HRSA HPSA designation")
    print("=" * 80)

    # Step 1: get HPSA data
    print("\n[1] Downloading HRSA HPSA primary-care data...")
    if not download_hpsa():
        print("\n[FALLBACK] Cannot auto-download. Manual steps:")
        print("  1. Visit https://data.hrsa.gov/data/download")
        print("  2. Download 'HPSA - Primary Care' CSV")
        print(f"  3. Save as: {HPSA_CSV}")
        print("\nFor now, using STATE-level proxy: states with high HPSA designation rate")
        # Use a hand-curated approximation from public HRSA HPSA Annual Report
        # 2024 state HPSA primary-care designation density (approximate)
        STATE_HPSA_DENSITY = {
            # Top decile (most underserved)
            "AK": "high", "MS": "high", "NM": "high", "WV": "high", "AL": "high",
            "AR": "high", "OK": "high", "TX": "high", "LA": "high", "KY": "high",
            # Bottom decile (least underserved)
            "MA": "low", "RI": "low", "CT": "low", "NJ": "low", "MD": "low",
            "DE": "low", "VT": "low", "NH": "low", "CA": "low", "MN": "low",
        }
        return run_state_proxy(STATE_HPSA_DENSITY)

    # Step 2: load HPSA data
    print("\n[2] Loading HPSA data...")
    hpsa = pd.read_csv(HPSA_CSV, low_memory=False)
    print(f"  Loaded {len(hpsa):,} HPSA records, columns: {list(hpsa.columns)[:10]}")

    # NRMP data
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate"])

    # State-level HPSA density (proportion of population in HPSA)
    state_col = "Primary State Abbreviation"
    score_col = "HPSA Score"
    status_col = "HPSA Status"
    if state_col not in hpsa.columns:
        # Try alternatives
        state_col = next((c for c in hpsa.columns if "state" in c.lower()
                           and "abbr" in c.lower()), None)
    if not state_col:
        print(f"  Cannot find state column; columns are: {list(hpsa.columns)}")
        return

    # Filter to currently DESIGNATED (not withdrawn/proposed) primary care
    if status_col in hpsa.columns:
        hpsa = hpsa[hpsa[status_col].astype(str).str.contains("Designated", na=False, case=False)]
        print(f"  After Designated filter: {len(hpsa):,}")

    # Compute per-state HPSA density (number of HPSAs, mean HPSA score severity)
    print(f"  Using state column: {state_col}")
    state_metrics = hpsa.groupby(state_col).agg(
        n_hpsas=(state_col, "count"),
    )
    if score_col in hpsa.columns:
        state_metrics["mean_hpsa_score"] = hpsa.groupby(state_col)[score_col].mean()

    # Define tier by n_hpsas (top third = high; bottom third = low)
    state_metrics["n_hpsas_rank"] = state_metrics["n_hpsas"].rank(pct=True)
    state_metrics["hpsa_tier"] = pd.cut(
        state_metrics["n_hpsas_rank"], bins=[0, 0.34, 0.67, 1.01],
        labels=["low", "medium", "high"])
    state_tier = state_metrics["hpsa_tier"].to_dict()

    # Cross-reference with NRMP
    nrmp["hpsa_tier"] = nrmp["state"].map(state_tier)
    nrmp["hpsa_tier"] = nrmp["hpsa_tier"].fillna("medium")

    print("\n[3] PSLF-eligibility gap by HPSA tier")
    gap_rows = []
    for tier in ["high", "medium", "low"]:
        sub = nrmp[nrmp["hpsa_tier"] == tier]
        a = sub[sub["pslf_class"] == "pslf_friendly"]["fill_rate"]
        b = sub[sub["pslf_class"] == "pslf_hostile"]["fill_rate"]
        if len(a) < 30 or len(b) < 10: continue
        try: t, p = stats.ttest_ind(a, b, equal_var=False)
        except: t, p = float("nan"), float("nan")
        gap_rows.append({
            "hpsa_tier": tier,
            "n_friendly": len(a), "n_hostile": len(b),
            "mean_friendly": float(a.mean()), "mean_hostile": float(b.mean()),
            "gap_pp": (a.mean() - b.mean()) * 100,
            "t": float(t), "p": float(p),
        })
        print(f"  {tier:<8s}: friendly={a.mean():.4f} (n={len(a):,}), "
               f"hostile={b.mean():.4f} (n={len(b):,}), Δ={(a.mean()-b.mean())*100:+5.2f}pp, p={p:.4g}")

    # State-level mean fill rate × HPSA density scatter
    print("\n[4] State-level analysis")
    state_fill = nrmp.groupby("state").agg(
        mean_fill=("fill_rate", "mean"),
        n_programs=("program_code", "nunique"),
    ).reset_index()
    state_fill["n_hpsas"] = state_fill["state"].map(state_metrics["n_hpsas"].to_dict())
    state_fill = state_fill.dropna()

    # Correlation: state HPSA density vs mean fill rate
    if len(state_fill) >= 10:
        r, p = stats.pearsonr(state_fill["n_hpsas"], state_fill["mean_fill"])
        print(f"  State HPSA count vs mean fill: r={r:+.3f}, p={p:.4g}, n={len(state_fill)}")
        sr, sp = stats.spearmanr(state_fill["n_hpsas"], state_fill["mean_fill"])
        print(f"  Spearman: rho={sr:+.3f}, p={sp:.4g}")

    # Save
    pd.DataFrame(gap_rows).to_csv(OUT_CSV.replace(".csv", "_gap.csv"),
                                    index=False, float_format="%.4f")
    state_fill.to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P4: PSLF x HRSA HPSA INTERACTION\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"HPSA primary-care records: {len(hpsa):,} (designated)\n")
        f.write(f"NRMP program-years: {len(nrmp):,}\n")
        f.write(f"States with data: {len(state_fill)}\n\n")

        f.write("PSLF-ELIGIBILITY GAP BY STATE HPSA TIER\n")
        f.write("-" * 80 + "\n")
        for r in gap_rows:
            f.write(f"  {r['hpsa_tier']:<8s}: n_friendly={r['n_friendly']:,}, "
                    f"n_hostile={r['n_hostile']:,}\n")
            f.write(f"            friendly_fill={r['mean_friendly']:.4f}, "
                    f"hostile_fill={r['mean_hostile']:.4f}\n")
            f.write(f"            Δ={r['gap_pp']:+5.2f}pp, p={r['p']:.4g}\n\n")

        f.write("STATE-LEVEL CORRELATION: HPSA density vs mean NRMP fill rate\n")
        f.write("-" * 80 + "\n")
        if len(state_fill) >= 10:
            r, p = stats.pearsonr(state_fill["n_hpsas"], state_fill["mean_fill"])
            sr, sp = stats.spearmanr(state_fill["n_hpsas"], state_fill["mean_fill"])
            f.write(f"  Pearson r={r:+.3f}, p={p:.4g}\n")
            f.write(f"  Spearman rho={sr:+.3f}, p={sp:.4g}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        if len(gap_rows) >= 2:
            high = next((g for g in gap_rows if g["hpsa_tier"] == "high"), None)
            low = next((g for g in gap_rows if g["hpsa_tier"] == "low"), None)
            if high and low:
                f.write(f"  High-HPSA states (most underserved): PSLF gap = {high['gap_pp']:+.2f}pp\n")
                f.write(f"  Low-HPSA states (least underserved): PSLF gap = {low['gap_pp']:+.2f}pp\n\n")
                if high["gap_pp"] > low["gap_pp"] + 3:
                    f.write("  -> Gap WIDER in high-HPSA states. Consistent with PSLF channeling\n"
                             "     physicians to underserved-area 501c3 employers as program intends.\n")
                elif high["gap_pp"] < low["gap_pp"] - 3:
                    f.write("  -> Gap NARROWER in high-HPSA states. PSLF may NOT preferentially\n"
                             "     channel physicians to shortage areas — structural prestige factors\n"
                             "     may dominate in high-shortage states.\n")
                else:
                    f.write("  -> Gap is similar across HPSA tiers. PSLF eligibility matters about\n"
                             "     equally regardless of geographic underservice.\n")

        f.write("\nPOLICY USES\n")
        f.write("-" * 80 + "\n")
        f.write("- HRSA workforce planning: does PSLF reach shortage areas as designed?\n")
        f.write("- Congress: testing PSLF's stated workforce-targeting goal\n")
        f.write("- DOE: data for PSLF program defense or reform discussions\n")
        f.write("- Future: ZIP-level matching of NRMP institution addresses to HPSA boundaries\n")

    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")


def run_state_proxy(state_hpsa_density):
    """Fallback when HRSA download fails: use hand-curated state HPSA density bins."""
    nrmp = pd.read_csv("nrmp_program_level_2021_2025.csv")
    nrmp = nrmp.dropna(subset=["fill_rate"])

    nrmp["hpsa_density"] = nrmp["state"].map(state_hpsa_density).fillna("medium")

    # Test PSLF-eligible vs PSLF-ineligible × HPSA-density
    print("\n[3] State HPSA-density tier x PSLF eligibility")
    summary = nrmp.groupby(["hpsa_density", "pslf_class"]).agg(
        mean_fill=("fill_rate", "mean"),
        n_program_years=("fill_rate", "count"),
        n_institutions=("institution", "nunique"),
    ).reset_index()
    print(summary.round(4).to_string())

    # PSLF-friendly vs PSLF-hostile gap by HPSA density
    print("\n[4] Gap (friendly - hostile) by HPSA density")
    gap_rows = []
    for d in ["high", "medium", "low"]:
        sub = nrmp[nrmp["hpsa_density"] == d]
        a = sub[sub["pslf_class"] == "pslf_friendly"]["fill_rate"]
        b = sub[sub["pslf_class"] == "pslf_hostile"]["fill_rate"]
        if len(a) < 30 or len(b) < 30: continue
        try: t, p = stats.ttest_ind(a, b, equal_var=False)
        except: t, p = float("nan"), float("nan")
        gap_rows.append({
            "hpsa_density": d,
            "n_friendly": len(a), "n_hostile": len(b),
            "mean_friendly": a.mean(), "mean_hostile": b.mean(),
            "gap_pp": (a.mean() - b.mean()) * 100,
            "t": t, "p": p,
        })
        print(f"  {d:<8s} HPSA: friendly={a.mean():.4f} (n={len(a):,}), "
               f"hostile={b.mean():.4f} (n={len(b):,}), Δ={(a.mean()-b.mean())*100:+5.2f}pp, p={p:.4g}")

    pd.DataFrame(gap_rows).to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P4: PSLF x HPSA INTERACTION (state-density proxy)\n")
        f.write("=" * 80 + "\n\n")
        f.write("Hypothesis: If PSLF reaches shortage areas as designed, the\n")
        f.write("PSLF-eligibility gap should widen in high-HPSA states (more\n")
        f.write("dependence on PSLF for recruitment).\n\n")
        f.write("CAVEAT: Using hand-curated state-level HPSA-density tiers as proxy\n")
        f.write("(downloaded HRSA HPSA file failed — see policy_hrsa_hpsa_results.csv\n")
        f.write("for source URL retry).\n\n")
        f.write("STATE HPSA TIERS\n")
        f.write("-" * 80 + "\n")
        for tier in ["high", "medium", "low"]:
            states = [s for s, d in state_hpsa_density.items() if d == tier]
            f.write(f"  {tier:<8s}: {sorted(states)}\n")

        f.write("\nGAP (PSLF-friendly minus PSLF-hostile fill rate) BY HPSA DENSITY\n")
        f.write("-" * 80 + "\n")
        for r in gap_rows:
            f.write(f"  {r['hpsa_density']:<8s}: friendly={r['mean_friendly']:.4f} "
                    f"(n={r['n_friendly']:,}), hostile={r['mean_hostile']:.4f} "
                    f"(n={r['n_hostile']:,}), Δ={r['gap_pp']:+5.2f}pp, p={r['p']:.4g}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        if len(gap_rows) >= 2:
            high_gap = next((r["gap_pp"] for r in gap_rows if r["hpsa_density"] == "high"), None)
            low_gap = next((r["gap_pp"] for r in gap_rows if r["hpsa_density"] == "low"), None)
            if high_gap and low_gap:
                f.write(f"  High-HPSA gap: {high_gap:+.2f} pp\n")
                f.write(f"  Low-HPSA gap:  {low_gap:+.2f} pp\n")
                if high_gap > low_gap + 3:
                    f.write("  -> Gap WIDER in high-HPSA states. PSLF mechanism plausibly\n"
                             "     channels physicians toward underserved-area 501c3 employers.\n")
                elif high_gap < low_gap - 3:
                    f.write("  -> Gap NARROWER in high-HPSA states. PSLF may not preferentially\n"
                             "     channel physicians to shortage areas; structural factors dominate.\n")
                else:
                    f.write("  -> Gap is similar across HPSA tiers. PSLF eligibility matters\n"
                             "     about equally regardless of geographic underservice.\n")

        f.write("\nPOLICY USES\n")
        f.write("-" * 80 + "\n")
        f.write("- HRSA workforce planning: identify whether PSLF-financed residencies\n")
        f.write("  are concentrated in shortage areas (testing the program's stated goal)\n")
        f.write("- DOE: support for PSLF as workforce-targeting tool\n")
        f.write("- Future: replace state proxy with actual ZIP-level HPSA × institution lookup\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")


if __name__ == "__main__":
    main()
