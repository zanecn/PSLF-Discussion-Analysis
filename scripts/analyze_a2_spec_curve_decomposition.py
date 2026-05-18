"""
analyze_a2_spec_curve_decomposition.py
========================================
A2 follow-up: WHICH spec dimension causes r/PSLF to flip direction in 33% of
specifications? Decompose flips by negative_def, pursuing_def, exclude_arctic,
exclude_sdn, min_cell_n, wc_min.

Output: spec_curve_decomposition.{txt,csv}
"""
from __future__ import annotations
import io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import pandas as pd
import numpy as np

OUT_TXT = "spec_curve_decomposition.txt"
OUT_CSV = "spec_curve_decomposition.csv"


def main():
    df = pd.read_csv("spec_curve_results.csv")
    print(f"Loaded {len(df)} specifications")
    print("Columns:", list(df.columns))

    rp = df[df["cohort"] == "Reddit r/PSLF"].copy()
    print(f"\nRedit r/PSLF specs: {len(rp)}")
    rp["direction"] = rp["or"].apply(lambda x: "or_gt_1" if x > 1 else "or_lt_1" if x < 1 else "neutral")
    print(rp["direction"].value_counts())
    print()

    # For each spec dimension, compute % flipped
    cat_dims = [c for c in ["neg_def", "pur_def", "excl_arctic",
                            "excl_sdn", "min_n", "wc_min"]
                if c in rp.columns]
    print(f"\nSpec dimensions found: {cat_dims}")

    print("=" * 80)
    print("WHICH dimensions flip r/PSLF direction?")
    print("=" * 80)

    rows = []
    for dim in cat_dims:
        print(f"\n  {dim}:")
        ct = pd.crosstab(rp[dim], rp["direction"], normalize="index") * 100
        print(ct.round(1).to_string())
        for v in rp[dim].unique():
            sub = rp[rp[dim] == v]
            rows.append({
                "dim": dim,
                "value": v,
                "n_specs": len(sub),
                "pct_or_gt_1": (sub["or"] > 1).mean() * 100,
                "pct_or_lt_1": (sub["or"] < 1).mean() * 100,
                "median_or": sub["or"].median(),
                "median_p": sub["p"].median() if "p" in sub.columns else float("nan"),
            })

    decomp_df = pd.DataFrame(rows)
    decomp_df.to_csv(OUT_CSV, index=False, float_format="%.4f")
    print(f"\nSaved: {OUT_CSV}")

    # Honest takeaway: which dim drives r/PSLF flip?
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("A2 r/PSLF FLIP DECOMPOSITION\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total r/PSLF specs: {len(rp)}\n")
        f.write(f"% OR>1 (venting culture direction): {(rp['or']>1).mean()*100:.1f}%\n")
        f.write(f"% OR<1 (decoupling direction):      {(rp['or']<1).mean()*100:.1f}%\n\n")

        f.write("Per-dimension flip rates (% with OR>1):\n")
        for dim in cat_dims:
            f.write(f"\n  {dim}:\n")
            for v in sorted(rp[dim].dropna().unique()):
                sub = rp[rp[dim] == v]
                pct_gt1 = (sub["or"] > 1).mean() * 100
                pct_lt1 = (sub["or"] < 1).mean() * 100
                f.write(f"    {v}: n={len(sub)}, OR>1={pct_gt1:.1f}%, OR<1={pct_lt1:.1f}%, "
                        f"median OR={sub['or'].median():.2f}\n")

        f.write("\n\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        # Find the dimension with the largest spread between values
        biggest_spread = max(cat_dims, key=lambda d:
            rp.groupby(d)["or"].apply(lambda x: (x > 1).mean()).max() -
            rp.groupby(d)["or"].apply(lambda x: (x > 1).mean()).min())
        f.write(f"Dimension with widest flip spread: {biggest_spread}\n")
        spreads = rp.groupby(biggest_spread)["or"].apply(lambda x: (x > 1).mean())
        f.write(f"  {biggest_spread} flip-rate by value:\n")
        for v, p in spreads.items():
            f.write(f"    {v}: {p*100:.1f}% OR>1\n")
        f.write("\nThis is the choice that determines whether r/PSLF supports the\n")
        f.write("'venting culture' (OR>1) or 'decoupling' (OR<1) framing.\n")

    print(f"Saved: {OUT_TXT}")


if __name__ == "__main__":
    main()
