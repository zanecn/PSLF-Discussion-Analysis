"""
placebo_test_topical_near.py
============================
Placebo (negative-control) test for the per-event PSLF sentiment shifts.

Design (better than r/AskReddit, which has only n=24 posts spread across
2019-2025):
  Use the topical-near baseline (n=7,750 OFF-PSLF posts in the SAME 21
  subreddits over the same period). If a PSLF policy event causes the
  OFF-PSLF posts in r/medicalschool, r/PSLF, r/Residency, etc. to ALSO show
  the same pre/post shift, then the "PSLF event effect" is actually a
  general-community-mood effect, not PSLF-specific. If the off-PSLF posts
  show ~zero shift, the PSLF-specificity claim is strengthened.

For comparison, r/AskReddit (n=177; 86% of posts in 2026) is included where
cells permit (mostly only Trump EO 2025-03 + Final Trump Rule 2025-10 have
adequate pre+post coverage).

Outputs:
  - placebo_results.txt - canonical artifact
  - placebo_results.csv - per-event side-by-side table

Usage:
  python placebo_test_topical_near.py
"""
from __future__ import annotations

import io
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

from sentiment_triangulation import (
    EVENTS,
    hedges_g,
    block_permutation_p,
)

OUT_TXT = "placebo_results.txt"
OUT_CSV = "placebo_results.csv"

# Files needed
TOPICAL_NEAR_CSV = "reddit_baseline_topical_near.csv"
ASKREDDIT_CSV = "reddit_baseline_askreddit.csv"
PSLF_CSV = "reddit_professions_pslf.csv"  # for the PSLF reference effect
ARCTIC_SHIFT_CSV = "reddit_arctic_shift_pslf.csv"  # round-7+ historical pull


def load_with_dates(path: str, date_col: str = "created_utc") -> pd.DataFrame:
    """Load CSV and ensure a 'date' datetime column exists."""
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True).dt.tz_localize(None)
    elif date_col in df.columns:
        df["date"] = pd.to_datetime(pd.to_numeric(df[date_col], errors="coerce"),
                                    unit="s", errors="coerce")
    return df


def per_event_g(df: pd.DataFrame, scorer_col: str, label: str) -> pd.DataFrame:
    """Per-event pre/post Hedges' g and block-permutation p on a scorer column."""
    if df.empty or scorer_col not in df.columns or "date" not in df.columns:
        return pd.DataFrame()
    es = df.dropna(subset=[scorer_col, "date"]).copy()
    rows = []
    for event_name, event_date, window in EVENTS:
        dt = pd.Timestamp(event_date)
        pre = es[(es["date"] >= dt - pd.Timedelta(days=window)) & (es["date"] < dt)]
        post = es[(es["date"] >= dt) & (es["date"] <= dt + pd.Timedelta(days=window))]
        n_pre, n_post = len(pre), len(post)
        if n_pre < 5 or n_post < 5:
            rows.append({
                "subset": label, "event": event_name, "scorer": scorer_col,
                "n_pre": n_pre, "n_post": n_post,
                "g": float("nan"), "p_boot": float("nan"),
                "mean_pre": float("nan"), "mean_post": float("nan"),
            })
            continue
        a = pre[scorer_col].dropna().to_numpy()
        b = post[scorer_col].dropna().to_numpy()
        g = hedges_g(a, b) if (len(a) >= 2 and len(b) >= 2) else float("nan")
        p_boot = block_permutation_p(
            pre[["date", scorer_col]], post[["date", scorer_col]],
            scorer_col=scorer_col, B=1000, seed=42)
        rows.append({
            "subset": label, "event": event_name, "scorer": scorer_col,
            "n_pre": n_pre, "n_post": n_post,
            "g": g, "p_boot": p_boot,
            "mean_pre": float(a.mean()) if len(a) else float("nan"),
            "mean_post": float(b.mean()) if len(b) else float("nan"),
        })
    return pd.DataFrame(rows)


def classify_placebo_verdict(g_pslf: float, g_placebo: float,
                              n_pre_placebo: int, n_post_placebo: int) -> str:
    """Classify the placebo cell:
      ADEQUATE_NULL  - placebo n>=20 AND |g_placebo| < 0.1: PSLF effect is specific
      MAGNITUDE_OK   - placebo n>=20 AND |g_placebo| < 0.5*|g_pslf|: PSLF effect is mostly specific
      CONFOUNDED     - placebo n>=20 AND |g_placebo| >= 0.5*|g_pslf| same-direction:
                       general mood shift, not PSLF-specific
      OPPOSITE       - placebo |g| meaningful but opposite sign: PSLF effect is opposite-of-mood
      UNDERPOWERED   - placebo n_pre or n_post < 20
      ORIGINAL_NA    - PSLF effect itself was nan
    """
    if np.isnan(g_pslf):
        return "ORIGINAL_NA"
    if n_pre_placebo < 20 or n_post_placebo < 20:
        return "UNDERPOWERED"
    if np.isnan(g_placebo) or abs(g_placebo) < 0.1:
        return "ADEQUATE_NULL"
    if abs(g_pslf) > 0:
        ratio = abs(g_placebo) / abs(g_pslf)
        same_sign = np.sign(g_placebo) == np.sign(g_pslf)
        if same_sign and ratio >= 0.5:
            return "CONFOUNDED"
        if not same_sign and abs(g_placebo) > 0.2:
            return "OPPOSITE"
        return "MAGNITUDE_OK"
    return "ADEQUATE_NULL"


def main():
    print("=" * 78)
    print("Placebo / Negative-Control Test (topical-near baseline)")
    print("=" * 78)

    # === Load all four corpora ===
    print("\nLoading corpora...")
    pslf = load_with_dates(PSLF_CSV)
    arctic = load_with_dates(ARCTIC_SHIFT_CSV)
    # Apply PSLF filter to Arctic Shift (collector should have done this; defensive)
    if not arctic.empty:
        try:
            from pslf_search_terms import filter_pslf_relevant
            tcol = "combined_text" if "combined_text" in arctic.columns else "selftext"
            mask = (filter_pslf_relevant(arctic[tcol].fillna(""))
                    | filter_pslf_relevant(arctic.get("title", pd.Series("", index=arctic.index)).fillna("")))
            arctic = arctic[mask].copy()
        except ImportError:
            pass
        # Concatenate Arctic Shift onto the PSLF reference (drop dup ids)
        common_cols = [c for c in pslf.columns if c in arctic.columns]
        pslf = pd.concat([pslf[common_cols], arctic[common_cols]],
                          ignore_index=True).drop_duplicates(subset="id" if "id" in common_cols else None)

    near = load_with_dates(TOPICAL_NEAR_CSV)
    ar = load_with_dates(ASKREDDIT_CSV)
    print(f"  PSLF reference (incl Arctic Shift): {len(pslf):>6,} rows  "
          f"(date range {pslf['date'].min()} -> {pslf['date'].max()})" if not pslf.empty else "  PSLF: missing")
    print(f"  Topical-near:                       {len(near):>6,} rows  "
          f"(date range {near['date'].min()} -> {near['date'].max()})" if not near.empty else "  Topical-near: missing")
    print(f"  r/AskReddit:                        {len(ar):>6,} rows  "
          f"(date range {ar['date'].min()} -> {ar['date'].max()})" if not ar.empty else "  AskReddit: missing")

    # === Per-event g for each scorer x corpus ===
    print("\nComputing per-event Hedges' g (B=1000)...")
    all_results = []
    for label, df, cols in [
        ("PSLF",         pslf, ["polarity", "vader_compound"]),
        ("topical_near", near, ["polarity", "vader_compound"]),
        ("askreddit",    ar,   ["polarity"]),  # AskReddit has no VADER
    ]:
        for col in cols:
            if col not in df.columns:
                continue
            sub = per_event_g(df, scorer_col=col, label=f"{label}_{col}")
            all_results.append(sub)
            print(f"  {label:>13s} x {col:<14s}: {len(sub)} events processed")

    big = pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()

    # === Build comparison table: PSLF vs each placebo ===
    print("\nBuilding comparison table...")
    comparisons = []
    for event_name, _, _ in EVENTS:
        for scorer_short, col in [("textblob", "polarity"), ("vader", "vader_compound")]:
            pslf_row = big[(big["subset"] == f"PSLF_{col}") & (big["event"] == event_name)]
            if pslf_row.empty:
                continue
            pslf_row = pslf_row.iloc[0]
            for placebo_label in ["topical_near", "askreddit"]:
                placebo_subset = f"{placebo_label}_{col}"
                placebo_row = big[(big["subset"] == placebo_subset) & (big["event"] == event_name)]
                if placebo_row.empty:
                    continue
                placebo_row = placebo_row.iloc[0]
                comparisons.append({
                    "event": event_name,
                    "scorer": scorer_short,
                    "placebo": placebo_label,
                    "g_pslf": pslf_row["g"],
                    "g_placebo": placebo_row["g"],
                    "p_boot_pslf": pslf_row["p_boot"],
                    "p_boot_placebo": placebo_row["p_boot"],
                    "n_pslf_pre_post": f"{int(pslf_row['n_pre'])}/{int(pslf_row['n_post'])}",
                    "n_placebo_pre_post": f"{int(placebo_row['n_pre'])}/{int(placebo_row['n_post'])}",
                    "verdict": classify_placebo_verdict(
                        pslf_row["g"], placebo_row["g"],
                        int(placebo_row["n_pre"]), int(placebo_row["n_post"])),
                })

    comp_df = pd.DataFrame(comparisons)

    # === Write artifacts ===
    print(f"\nWriting {OUT_TXT}...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Placebo / Negative-Control Test\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/placebo_test_topical_near.py\n")
        f.write("=" * 80 + "\n\n")

        f.write("DESIGN\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether per-event sentiment shifts in PSLF posts could be a\n")
        f.write("general-community-mood effect rather than a PSLF-specific effect.\n\n")
        f.write("Comparators (placebos):\n")
        f.write(f"  * topical_near (n={len(near):,}): OFF-PSLF posts in the SAME 21 subreddits\n")
        f.write("    over the same period. The strongest placebo design: same audience,\n")
        f.write("    same posting norms, just non-PSLF content.\n")
        f.write(f"  * askreddit    (n={len(ar):,}): general r/AskReddit posts. Limited\n")
        f.write("    coverage (most posts are 2026); useful only for late-period events.\n\n")

        f.write("VERDICT KEY\n")
        f.write("  ADEQUATE_NULL  - placebo |g| < 0.1: PSLF effect is community-specific\n")
        f.write("  MAGNITUDE_OK   - placebo |g| < 50% of PSLF |g|: mostly PSLF-specific\n")
        f.write("  CONFOUNDED     - placebo |g| >= 50% of PSLF |g|, same direction:\n")
        f.write("                   general community mood shift, not PSLF-specific\n")
        f.write("  OPPOSITE       - placebo direction opposite of PSLF: PSLF runs against mood\n")
        f.write("  UNDERPOWERED   - placebo n_pre or n_post < 20: cannot adjudicate\n")
        f.write("  ORIGINAL_NA    - PSLF effect itself was unestimable\n\n")

        f.write("COMPARISON TABLE (per event x scorer x placebo)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Event':<26s} {'sc':<3s} {'placebo':<13s} "
                f"{'g_pslf':>7s} {'g_plac':>7s} {'n_PSLF':>10s} {'n_plac':>10s} "
                f"{'verdict':<14s}\n")
        for _, r in comp_df.iterrows():
            gp = f"{r['g_pslf']:+.3f}" if not pd.isna(r['g_pslf']) else "  n/a "
            gx = f"{r['g_placebo']:+.3f}" if not pd.isna(r['g_placebo']) else "  n/a "
            f.write(f"{r['event']:<26s} {r['scorer'][:3]:<3s} {r['placebo']:<13s} "
                    f"{gp:>7s} {gx:>7s} {r['n_pslf_pre_post']:>10s} "
                    f"{r['n_placebo_pre_post']:>10s} {r['verdict']:<14s}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("SUMMARY VERDICTS\n")
        f.write("-" * 80 + "\n")
        v_counts = comp_df["verdict"].value_counts()
        for v, c in v_counts.items():
            f.write(f"  {v:<14s}  {c:>3d} of {len(comp_df)} comparisons\n")

        # Topical-near only summary (the strong design)
        tn = comp_df[comp_df["placebo"] == "topical_near"]
        f.write(f"\nTopical-near only ({len(tn)} comparisons; strongest placebo design):\n")
        for v, c in tn["verdict"].value_counts().items():
            f.write(f"  {v:<14s}  {c:>3d}\n")

        f.write("\nKey questions for paper Discussion:\n")
        f.write("  1. Are the PSLF shifts ADEQUATE_NULL/MAGNITUDE_OK against topical_near?\n"
                "     If yes, PSLF-specificity claim is supported.\n")
        f.write("  2. Any CONFOUNDED cells? Those events' apparent PSLF effects are likely\n"
                "     subreddit-mood shifts, not PSLF reactions.\n")
        f.write("  3. Any OPPOSITE cells? Those PSLF reactions ran AGAINST general mood;\n"
                "     specifically interpretable as PSLF-driven divergence.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    comp_df.to_csv(OUT_CSV, index=False, float_format="%.4f")
    print(f"Saved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")
    print(f"\nQuick summary of {len(comp_df)} comparisons:")
    print(comp_df["verdict"].value_counts().to_string())
    print("\nTopical-near only:")
    print(comp_df[comp_df["placebo"] == "topical_near"]["verdict"].value_counts().to_string())


if __name__ == "__main__":
    main()
