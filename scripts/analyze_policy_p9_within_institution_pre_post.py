"""
analyze_policy_p9_within_institution_pre_post.py
====================================================
P9 (policy): Within-institution pre/post Limited PSLF Waiver fill-rate
trajectory.

This addresses the P8 quality-confound concern: by comparing each institution
to ITSELF before/after the Waiver, time-invariant quality, prestige, location,
and reputation are all controlled by within-institution differencing.

If PSLF salience increase had a treatment effect, we should see institutions'
fill rates shift differentially based on their PSLF eligibility — independent
of their baseline quality.

Method:
  1. For each institution observed in BOTH 2016-2020 (backfill) and 2022-2025,
     compute pre and post mean fill rates
  2. Difference: Δfill_rate = post_mean - pre_mean
  3. Test: does Δ vary by PSLF eligibility class?
  4. Stratify by specialty

Output: policy_p9_within_institution_results.{txt,csv,png}
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

OUT_TXT = "policy_p9_within_institution_results.txt"
OUT_CSV = "policy_p9_within_institution_results.csv"
OUT_PNG = "policy_p9_within_institution_results.png"


def main():
    print("=" * 80)
    print("P9: Within-institution pre/post Limited PSLF Waiver")
    print("=" * 80)

    pre = pd.read_csv("nrmp_program_level_2016_2020_backfill.csv")
    pre = pre.dropna(subset=["fill_rate"])
    post = pd.read_csv("nrmp_program_level_2021_2025.csv")
    post = post.dropna(subset=["fill_rate"])

    # Use post's PSLF classifications (heuristic) for pre-post consistency
    inst_class = post[["institution", "state", "pslf_class"]].drop_duplicates()
    pre = pre.merge(inst_class, on=["institution", "state"], how="left")

    # Filter to institutions in BOTH eras
    pre_insts = set(zip(pre["institution"], pre["state"]))
    post_insts = set(zip(post["institution"], post["state"]))
    overlap = pre_insts & post_insts
    print(f"\nInstitutions in pre-only: {len(pre_insts - post_insts)}")
    print(f"Institutions in post-only: {len(post_insts - pre_insts)}")
    print(f"Institutions in BOTH eras: {len(overlap)}")

    # Compute within-institution pre/post mean fill
    pre = pre[pre.set_index(["institution", "state"]).index.isin(overlap)]
    post = post[post.set_index(["institution", "state"]).index.isin(overlap)]

    # Pre = 2016-2020, Post = 2022-2025 (skip 2021 transition)
    pre_means = pre[pre["year"] <= 2020].groupby(
        ["institution", "state", "pslf_class"]
    ).agg(pre_fill=("fill_rate", "mean"),
           pre_quota=("quota", "sum"),
           pre_n_program_years=("fill_rate", "count")).reset_index()

    post_means = post[post["year"] >= 2022].groupby(
        ["institution", "state", "pslf_class"]
    ).agg(post_fill=("fill_rate", "mean"),
           post_quota=("quota", "sum"),
           post_n_program_years=("fill_rate", "count")).reset_index()

    merged = pre_means.merge(post_means, on=["institution", "state", "pslf_class"], how="inner")
    merged["delta_fill"] = merged["post_fill"] - merged["pre_fill"]
    merged["delta_pp"] = merged["delta_fill"] * 100
    print(f"\nInstitutions with pre AND post means: {len(merged):,}")

    # === Within-institution change by class ===
    print("\n[1] Within-institution Δ fill rate by PSLF class")
    rows = []
    for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
        sub = merged[merged["pslf_class"] == cls]
        if len(sub) < 10: continue
        rows.append({
            "pslf_class": cls,
            "n_institutions": len(sub),
            "mean_delta_pp": float(sub["delta_pp"].mean()),
            "median_delta_pp": float(sub["delta_pp"].median()),
            "sd_delta_pp": float(sub["delta_pp"].std()),
        })
        print(f"  {cls:<14s}: n={len(sub):,}, "
              f"mean Δ={sub['delta_pp'].mean():+5.2f}pp, "
              f"median={sub['delta_pp'].median():+5.2f}pp, "
              f"sd={sub['delta_pp'].std():.2f}pp")

    # === Pairwise tests ===
    print("\n[2] Pairwise t-tests on Δ fill rate")
    f = merged[merged["pslf_class"] == "pslf_friendly"]["delta_pp"]
    h = merged[merged["pslf_class"] == "pslf_hostile"]["delta_pp"]
    a = merged[merged["pslf_class"] == "ambiguous"]["delta_pp"]
    if len(f) >= 10 and len(h) >= 5:
        t, p = stats.ttest_ind(f, h, equal_var=False)
        print(f"  friendly Δ vs hostile Δ:   t={t:+.3f}, p={p:.4g}")
        print(f"    friendly mean Δ={f.mean():+.2f}pp, hostile mean Δ={h.mean():+.2f}pp")
        print(f"    Difference of differences: {f.mean()-h.mean():+.2f}pp")

    # KEY: did PSLF-hostile institutions IMPROVE less than PSLF-friendly?
    # If PSLF salience matters, friendly should hold or improve, hostile should decline more
    print("\n[3] KEY TEST: Did PSLF-hostile programs decline MORE than PSLF-friendly post-Waiver?")
    print("    (If PSLF salience affects recruitment, expect: hostile Δ < friendly Δ)")

    # Specialty-stratified
    print("\n[4] Per-specialty within-institution analysis")
    sp_rows = []
    for sp in ["Family Medicine", "Internal Medicine", "Pediatrics",
                "Dermatology", "Emergency Medicine"]:
        # Use program-level rather than institution-level for specialty
        # Need to re-aggregate at (inst, state, specialty)
        pre_sp = pre[(pre["specialty"] == sp) & (pre["year"] <= 2020)].groupby(
            ["institution", "state", "pslf_class"]
        )["fill_rate"].mean().reset_index().rename(columns={"fill_rate": "pre_fill"})
        post_sp = post[(post["specialty"] == sp) & (post["year"] >= 2022)].groupby(
            ["institution", "state", "pslf_class"]
        )["fill_rate"].mean().reset_index().rename(columns={"fill_rate": "post_fill"})
        m = pre_sp.merge(post_sp, on=["institution", "state", "pslf_class"], how="inner")
        m["delta_pp"] = (m["post_fill"] - m["pre_fill"]) * 100

        if len(m) < 10: continue
        f = m[m["pslf_class"] == "pslf_friendly"]["delta_pp"]
        h = m[m["pslf_class"] == "pslf_hostile"]["delta_pp"]
        if len(f) >= 5 and len(h) >= 2:
            t_stat, p_val = stats.ttest_ind(f, h, equal_var=False) if len(h) >= 5 else (float("nan"), float("nan"))
            sp_rows.append({
                "specialty": sp,
                "n_friendly": len(f), "n_hostile": len(h),
                "friendly_mean_delta": float(f.mean()),
                "hostile_mean_delta": float(h.mean()) if len(h) > 0 else float("nan"),
                "did_pp": float(f.mean() - h.mean()) if len(h) > 0 else float("nan"),
                "p": float(p_val),
            })
            print(f"  {sp:<22s}: n_f={len(f):>3} (mean Δ={f.mean():+5.2f}pp), "
                  f"n_h={len(h):>2} (mean Δ={h.mean():+5.2f}pp), "
                  f"DiD={f.mean()-h.mean():+5.2f}pp, p={p_val:.4g}")

    # === Save ===
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")
    pd.DataFrame(sp_rows).to_csv(OUT_CSV.replace(".csv", "_by_specialty.csv"),
                                   index=False, float_format="%.4f")
    merged.to_csv(OUT_CSV.replace(".csv", "_per_institution.csv"),
                    index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P9: WITHIN-INSTITUTION PRE/POST LIMITED PSLF WAIVER\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Institutions in BOTH 2016-2020 AND 2022-2025: {len(overlap):,}\n")
        f.write(f"Institutions with computable pre+post means: {len(merged):,}\n\n")

        f.write("WITHIN-INSTITUTION Δ FILL RATE (post 2022-25 minus pre 2016-20)\n")
        f.write("-" * 80 + "\n")
        for r in rows:
            f.write(f"  {r['pslf_class']:<14s}: n={r['n_institutions']:,}, "
                    f"mean Δ={r['mean_delta_pp']:+5.2f}pp, "
                    f"median={r['median_delta_pp']:+5.2f}pp, "
                    f"sd={r['sd_delta_pp']:.2f}pp\n")

        if len(merged[merged['pslf_class']=='pslf_friendly']) >= 10 and \
           len(merged[merged['pslf_class']=='pslf_hostile']) >= 5:
            ff = merged[merged["pslf_class"] == "pslf_friendly"]["delta_pp"]
            hh = merged[merged["pslf_class"] == "pslf_hostile"]["delta_pp"]
            t, p = stats.ttest_ind(ff, hh, equal_var=False)
            f.write(f"\nDIFFERENCE-IN-DIFFERENCES: friendly Δ vs hostile Δ\n")
            f.write(f"  friendly mean Δ: {ff.mean():+.2f}pp\n")
            f.write(f"  hostile mean Δ:  {hh.mean():+.2f}pp\n")
            f.write(f"  DiD:             {ff.mean()-hh.mean():+.2f}pp (t={t:.3f}, p={p:.4g})\n")
            if p < 0.05:
                if ff.mean() > hh.mean():
                    f.write("  -> Significant: friendly programs improved MORE than hostile\n"
                             "     (consistent with PSLF salience strengthening academic-vs-for-profit gap)\n")
                else:
                    f.write("  -> Significant: hostile programs improved MORE than friendly\n"
                             "     (PSLF salience may have actually narrowed the structural gap)\n")
            else:
                f.write("  -> Not significant: pre/post change is similar across PSLF classes\n"
                         "     (consistent with the gap being STRUCTURAL, not Waiver-driven)\n")

        f.write("\nPER-SPECIALTY DIFFERENCE-IN-DIFFERENCES\n")
        f.write("-" * 80 + "\n")
        for r in sp_rows:
            f.write(f"  {r['specialty']:<22s}: n_f={r['n_friendly']:>3}, n_h={r['n_hostile']:>2}, "
                    f"friendly Δ={r['friendly_mean_delta']:+5.2f}pp, "
                    f"hostile Δ={r['hostile_mean_delta']:+5.2f}pp, DiD={r['did_pp']:+5.2f}pp, "
                    f"p={r['p']:.4g}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("Within-institution analysis controls for time-invariant quality,\n")
        f.write("prestige, location, and reputation. If PSLF salience increase (Limited\n")
        f.write("Waiver) had a treatment effect on physician choice, we should see\n")
        f.write("differential pre/post fill-rate trajectories by PSLF class.\n\n")
        f.write("If DiD ≈ 0 for friendly vs hostile, the +12.86pp B5 cross-sectional\n")
        f.write("gap is structural (each institution's fill rate is stable; gap is\n")
        f.write("between-institution composition). PSLF salience did not differentially\n")
        f.write("affect institutions of different PSLF classes.\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    fig, ax = plt.subplots(figsize=(11, 6))
    classes_present = [r["pslf_class"] for r in rows]
    means = [r["mean_delta_pp"] for r in rows]
    medians = [r["median_delta_pp"] for r in rows]
    n_insts = [r["n_institutions"] for r in rows]
    x = np.arange(len(classes_present))
    width = 0.35
    ax.bar(x - width/2, means, width, label="Mean Δ", color="steelblue")
    ax.bar(x + width/2, medians, width, label="Median Δ", color="orange")
    for i, n in enumerate(n_insts):
        ax.text(x[i], max(means[i], medians[i]) + 0.2, f"n={n}",
                 ha="center", fontsize=9)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(classes_present)
    ax.set_ylabel("Within-institution Δ fill rate, post-Waiver minus pre (pp)")
    ax.set_title("P9: Within-institution pre/post Limited PSLF Waiver\n"
                  "(controls for time-invariant quality / prestige / location)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
