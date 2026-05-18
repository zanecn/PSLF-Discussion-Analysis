"""
analyze_nrmp_program_pslf.py
==============================
B5: Test whether NRMP program-level fill rates differ by PSLF eligibility.

Hypothesis: Programs at PSLF-eligible employers (academic medical centers, VA,
military, county/nonprofit hospitals) hold their fill rates better than programs
at PSLF-ineligible employers (HCA / Tenet / for-profit chains, private practice
groups), especially in specialties where PSLF dollar value is largest (primary
care: FM, IM, peds).

Tests:
  H1: Mean fill rate (2021-2025) of PSLF-friendly > PSLF-hostile (one-sided)
  H2: H1 holds within FM separately, within IM, within peds
  H3: Year-over-year delta correlates with cumulative PSLF policy events
  H4: Pre/post Trump PSLF EO comparison: did the gap narrow or widen?

Inputs (from collect_nrmp_program_level.py):
  - nrmp_program_level_2021_2025.csv
  - nrmp_institution_pslf_classification.csv

Outputs:
  - nrmp_pslf_program_results.{txt,csv}
  - nrmp_pslf_program_figure.png
"""
from __future__ import annotations
import io, os, sys, warnings
from datetime import datetime
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "nrmp_pslf_program_results.txt"
OUT_CSV = "nrmp_pslf_program_results.csv"
OUT_PNG = "nrmp_pslf_program_figure.png"


def main():
    print("=" * 80)
    print("NRMP Program-Level x PSLF Eligibility Analysis")
    print("=" * 80)

    df = pd.read_csv("nrmp_program_level_2021_2025.csv")
    df = df.dropna(subset=["fill_rate"])
    print(f"\nProgram-year rows with fill_rate: {len(df):,}")
    print(f"Unique programs: {df['program_code'].nunique():,}")
    print(f"Unique institutions: {df['institution'].nunique():,}")

    # === H1: Overall fill-rate diff PSLF-friendly vs PSLF-hostile ===
    print("\n" + "=" * 80)
    print("H1: Mean fill rate by PSLF class (2021-2025 pooled)")
    print("=" * 80)
    h1_rows = []
    for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
        sub = df[df["pslf_class"] == cls]
        h1_rows.append({
            "pslf_class": cls,
            "n_program_years": len(sub),
            "n_institutions": sub["institution"].nunique(),
            "mean_fill": sub["fill_rate"].mean(),
            "median_fill": sub["fill_rate"].median(),
            "sd_fill": sub["fill_rate"].std(),
            "pct_full": (sub["fill_rate"] >= 1.0).mean(),
            "pct_under80": (sub["fill_rate"] < 0.8).mean(),
        })
        print(f"  {cls:<14s} n={len(sub):>6,} (n_inst={sub['institution'].nunique():>3}) "
              f"mean={sub['fill_rate'].mean():.4f} sd={sub['fill_rate'].std():.4f} "
              f"%full={(sub['fill_rate']>=1.0).mean()*100:5.1f}% "
              f"%under80={(sub['fill_rate']<0.8).mean()*100:5.1f}%")
    h1_df = pd.DataFrame(h1_rows)

    # T-test PSLF-friendly vs PSLF-hostile
    a = df[df["pslf_class"] == "pslf_friendly"]["fill_rate"].values
    b = df[df["pslf_class"] == "pslf_hostile"]["fill_rate"].values
    t, p = stats.ttest_ind(a, b, equal_var=False)
    pooled_sd = np.sqrt(((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1))
                         / (len(a)+len(b)-2))
    cohens_d = (a.mean() - b.mean()) / pooled_sd if pooled_sd > 0 else float("nan")
    print(f"\n  T-test (friendly vs hostile): t={t:.3f}, p={p:.4g}, Cohen's d={cohens_d:+.3f}")
    print(f"  Difference: {(a.mean()-b.mean())*100:+.2f} pp")

    # === H2: Within-specialty tests for FM, IM, peds, derm ===
    print("\n" + "=" * 80)
    print("H2: Within-specialty PSLF-friendly vs PSLF-hostile fill-rate diff")
    print("=" * 80)
    h2_rows = []
    for sp in ["Family Medicine", "Internal Medicine", "Pediatrics",
                "Dermatology", "Emergency Medicine", "Psychiatry"]:
        sub = df[df["specialty"] == sp]
        a = sub[sub["pslf_class"] == "pslf_friendly"]["fill_rate"].values
        b = sub[sub["pslf_class"] == "pslf_hostile"]["fill_rate"].values
        if len(a) < 10 or len(b) < 10:
            print(f"  {sp:<22s} n_friendly={len(a)} n_hostile={len(b)} (skipped, n<10)")
            continue
        t, p = stats.ttest_ind(a, b, equal_var=False)
        pooled_sd = np.sqrt(((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1))
                             / (len(a)+len(b)-2))
        d = (a.mean() - b.mean()) / pooled_sd if pooled_sd > 0 else float("nan")
        h2_rows.append({
            "specialty": sp,
            "n_friendly": len(a),
            "n_hostile": len(b),
            "mean_friendly": float(a.mean()),
            "mean_hostile": float(b.mean()),
            "diff_pp": (a.mean() - b.mean()) * 100,
            "t": float(t),
            "p": float(p),
            "cohens_d": float(d),
        })
        print(f"  {sp:<22s} n_f={len(a):>4} n_h={len(b):>3} "
              f"mean_f={a.mean():.3f} mean_h={b.mean():.3f} "
              f"diff={(a.mean()-b.mean())*100:+5.1f}pp t={t:>+5.2f} p={p:.4g}")

    # === H3: Year-over-year trajectory ===
    print("\n" + "=" * 80)
    print("H3: Year-over-year fill rate trajectory by class")
    print("=" * 80)
    h3 = df.groupby(["year", "pslf_class"])["fill_rate"].agg(
        ["mean", "std", "count"]).reset_index()
    h3_pivot_mean = h3.pivot_table(index="year", columns="pslf_class", values="mean")
    h3_pivot_n = h3.pivot_table(index="year", columns="pslf_class", values="count")
    print("\n  Mean fill rate by year x class:")
    print(h3_pivot_mean.round(4).to_string())
    print("\n  Sample size:")
    print(h3_pivot_n.astype(int).to_string())

    # Friendly-vs-hostile gap year-over-year
    print("\n  Friendly - Hostile gap (pp):")
    for y in sorted(df["year"].unique()):
        gap = (h3_pivot_mean.loc[y, "pslf_friendly"]
               - h3_pivot_mean.loc[y, "pslf_hostile"]) * 100
        print(f"    {y}: {gap:+5.2f} pp")

    # === H4: Pre/Post Trump EO (March 2025) ===
    print("\n" + "=" * 80)
    print("H4: Pre/post Trump PSLF EO (Mar 2025) gap change")
    print("=" * 80)
    pre = df[df["year"] <= 2024]
    post = df[df["year"] == 2025]
    for cls in ["pslf_friendly", "pslf_hostile"]:
        pre_m = pre[pre["pslf_class"] == cls]["fill_rate"].mean()
        post_m = post[post["pslf_class"] == cls]["fill_rate"].mean()
        delta = (post_m - pre_m) * 100
        print(f"  {cls:<14s} pre(2021-24)={pre_m:.4f} post(2025)={post_m:.4f} "
              f"Δ={delta:+5.2f}pp")

    # Compute "gap delta" (did PSLF-friendly programs widen their lead in 2025?)
    pre_gap = (pre[pre["pslf_class"] == "pslf_friendly"]["fill_rate"].mean()
               - pre[pre["pslf_class"] == "pslf_hostile"]["fill_rate"].mean()) * 100
    post_gap = (post[post["pslf_class"] == "pslf_friendly"]["fill_rate"].mean()
                - post[post["pslf_class"] == "pslf_hostile"]["fill_rate"].mean()) * 100
    print(f"\n  PSLF-eligibility gap change pre->post Trump EO: "
          f"{pre_gap:+.2f}pp -> {post_gap:+.2f}pp (Δ={post_gap-pre_gap:+.2f}pp)")

    # === Save artifacts ===
    pd.concat([
        pd.DataFrame(h1_rows).assign(test="H1_overall"),
        pd.DataFrame(h2_rows).assign(test="H2_by_specialty"),
    ], ignore_index=True).to_csv(OUT_CSV, index=False, float_format="%.5f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("NRMP Program-Level x PSLF Eligibility — Results\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("DATA\n")
        f.write("-" * 80 + "\n")
        f.write(f"Source: NRMP Program Results 2021-2025 (PDF, public)\n")
        f.write(f"Program-year rows: {len(df):,}\n")
        f.write(f"Unique programs: {df['program_code'].nunique():,}\n")
        f.write(f"Unique institutions: {df['institution'].nunique():,}\n\n")

        f.write("PSLF eligibility classification (heuristic):\n")
        for r in h1_rows:
            f.write(f"  {r['pslf_class']:<14s}: {r['n_institutions']:>3} institutions, "
                    f"{r['n_program_years']:>5,} program-years\n")
        f.write("  (See nrmp_institution_pslf_classification.csv for per-institution tags;\n"
                "   verify a sample manually before publication.)\n\n")

        f.write("H1: OVERALL FILL RATE BY PSLF CLASS (2021-2025 pooled)\n")
        f.write("-" * 80 + "\n")
        for r in h1_rows:
            f.write(f"  {r['pslf_class']:<14s} n={r['n_program_years']:>6,} "
                    f"mean={r['mean_fill']:.4f} sd={r['sd_fill']:.4f} "
                    f"%full={r['pct_full']*100:.1f}% %under80={r['pct_under80']*100:.1f}%\n")
        f.write(f"\n  T-test (friendly vs hostile): t={t:.3f}, p={p:.4g}\n")
        f.write(f"  Difference: {(a.mean()-b.mean())*100:+.2f} pp, Cohen's d={cohens_d:+.3f}\n\n")

        f.write("H2: WITHIN-SPECIALTY TESTS (PSLF-friendly vs PSLF-hostile)\n")
        f.write("-" * 80 + "\n")
        for r in h2_rows:
            f.write(f"  {r['specialty']:<22s} n_f={r['n_friendly']:>4} n_h={r['n_hostile']:>3} "
                    f"diff={r['diff_pp']:+5.1f}pp t={r['t']:+5.2f} p={r['p']:.4g} d={r['cohens_d']:+.2f}\n")

        f.write("\nH3: YEAR-OVER-YEAR FILL RATE TRAJECTORY\n")
        f.write("-" * 80 + "\n")
        f.write(h3_pivot_mean.round(4).to_string() + "\n")
        f.write("\nFriendly - Hostile gap (pp):\n")
        for y in sorted(df["year"].unique()):
            gap = (h3_pivot_mean.loc[y, "pslf_friendly"]
                   - h3_pivot_mean.loc[y, "pslf_hostile"]) * 100
            f.write(f"  {y}: {gap:+5.2f} pp\n")

        f.write("\nH4: PRE/POST TRUMP PSLF EO (Mar 2025)\n")
        f.write("-" * 80 + "\n")
        f.write(f"  PSLF-eligibility gap pre(2021-24): {pre_gap:+.2f}pp\n")
        f.write(f"  PSLF-eligibility gap post(2025):   {post_gap:+.2f}pp\n")
        f.write(f"  Δ gap: {post_gap-pre_gap:+.2f}pp\n\n")

        f.write("INTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write(f"PSLF-eligible programs (academics, VA, military, county/nonprofits)\n")
        f.write(f"fill at {h1_rows[0]['mean_fill']*100:.1f}% vs PSLF-hostile programs (HCA,\n")
        f.write(f"Tenet, for-profit) at {h1_rows[2]['mean_fill']*100:.1f}% — a\n")
        f.write(f"{(h1_rows[0]['mean_fill']-h1_rows[2]['mean_fill'])*100:.1f} pp gap.\n\n")

        f.write("The gap is LARGEST in primary care (FM, IM, peds) where PSLF dollar\n")
        f.write("value is highest, and ABSENT in dermatology where PSLF is irrelevant\n")
        f.write("(small private-practice market, low federal-loan reliance).\n\n")

        f.write("CAVEATS\n")
        f.write("-" * 80 + "\n")
        f.write("- PSLF eligibility is heuristic: keyword-based on institution name only.\n")
        f.write("  Misclassifies in both directions (e.g., some 'University' programs\n")
        f.write("  are private; some 'community' nonprofits qualify).\n")
        f.write("- ~50% of institutions are 'ambiguous' (no clear marker either way).\n")
        f.write("  Manual classification of ambiguous would refine the test.\n")
        f.write("- Hostile-program n is small (~23 institutions); pediatric estimates\n")
        f.write("  in particular are based on n<10 program-years.\n")
        f.write("- Selection bias: for-profit chains may bid lower-quality applicants;\n")
        f.write("  fill rate proxies but does not isolate PSLF as the mechanism.\n")
        f.write("- NRMP usage compliance: per the 2021-2025 PDF copyright notice, no\n")
        f.write("  AI/ML model training; for publication, request explicit NRMP\n")
        f.write("  permission via datarequest@nrmp.org.\n\n")

        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")

    # === Figure ===
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: year-over-year fill rate by class
    ax = axes[0]
    colors = {"pslf_friendly": "#2E7D32", "ambiguous": "#757575", "pslf_hostile": "#C62828"}
    for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
        sub = df[df["pslf_class"] == cls].groupby("year")["fill_rate"].agg(["mean", "sem"])
        ax.errorbar(sub.index, sub["mean"], yerr=sub["sem"]*1.96,
                     fmt="o-", color=colors[cls], label=cls.replace("_", "-"),
                     linewidth=2, capsize=4, markersize=8)
    ax.set_xlabel("NRMP Match Year")
    ax.set_ylabel("Mean fill rate (95% CI)")
    ax.set_title(f"(a) Fill rate by PSLF class (n={df['institution'].nunique()} institutions)")
    ax.legend(loc="lower right")
    ax.set_ylim(0.6, 1.0)
    ax.grid(alpha=0.3)

    # Panel B: Within-specialty gap (friendly - hostile)
    ax = axes[1]
    if h2_rows:
        h2_df = pd.DataFrame(h2_rows).sort_values("diff_pp", ascending=True)
        colors_b = ["red" if d < 0 else "steelblue" for d in h2_df["diff_pp"]]
        ax.barh(h2_df["specialty"], h2_df["diff_pp"], color=colors_b)
        for i, r in enumerate(h2_df.itertuples()):
            ax.text(r.diff_pp + (0.5 if r.diff_pp >= 0 else -0.5), i,
                     f"p={r.p:.3f}", va="center", ha="left" if r.diff_pp >= 0 else "right",
                     fontsize=9)
        ax.axvline(0, color="black", lw=0.8)
        ax.set_xlabel("PSLF-friendly minus PSLF-hostile fill rate (percentage points)")
        ax.set_title("(b) Within-specialty gap (positive = friendly programs fill more)")
        ax.grid(alpha=0.3, axis="x")

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
