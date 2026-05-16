"""
analyze_per_profession_per_event.py
====================================
Per-event x per-profession sentiment Hedges' g, using the full
post-Arctic-Shift corpus. Reports which (event, profession) cells are
well-powered (n_pre >= 20 AND n_post >= 20) and the effect size +
block-permutation p-value within each cell.

This complements gen_legislative_timeline.py (which pools across
profession) and is essential for the substantive paper because the
Arctic Shift expansion was heavily weighted to general_pslf +
general_student_loans subs (~67K of the 72K new posts), so the
profession-stratified picture is qualitatively different from the
pooled analysis.

Inputs:
  - comprehensive_medical_pslf_discussions.csv
  - comprehensive_teacher_pslf_discussions.csv
  - reddit_professions_pslf.csv          (PSLF-filtered at load)
  - reddit_arctic_shift_pslf.csv         (round-7 historical pull)
  - reddit_new_subs_pslf.csv             (round-7 PA/NP top-up)
  - forum_pslf_discussions.csv           (SDN, PSLF-filtered at load)

Outputs:
  - per_profession_per_event_results.txt
  - per_profession_per_event_results.csv

Usage:
  python analyze_per_profession_per_event.py
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

from pslf_search_terms import filter_pslf_relevant
from sentiment_triangulation import EVENTS, hedges_g, block_permutation_p

OUT_TXT = "per_profession_per_event_results.txt"
OUT_CSV = "per_profession_per_event_results.csv"

# Display labels for professions (matches pslf_intention_analysis.py convention)
PROF_LABEL = {
    "medical": "Reddit Medical",
    "teaching": "Reddit Teaching",
    "nursing": "Reddit Nursing",
    "law": "Reddit Law",
    "pharmacy": "Reddit Pharmacy",
    "physician_assistant": "Reddit PA",
    "social_work": "Reddit SocialWork",
    "occupational_therapy": "Reddit OT",
    "speech_language_pathology": "Reddit SLP",
    "federal_employee": "Reddit Federal",
    "general_pslf": "Reddit r/PSLF",
    "general_student_loans": "Reddit r/StudentLoans",
    "general_finance": "Reddit Finance",
    "personalfinance": "Reddit r/personalfinance",
    "financialindependence": "Reddit r/FI",
    "sdn_medical": "SDN (Medical)",
    "sdn": "SDN (Medical)",
}

MIN_CELL_N = 20  # n_pre AND n_post must each be >= this for the cell to report


def load_corpus() -> pd.DataFrame:
    """Load + concatenate all five Reddit + SDN sources, applying strict
    PSLF filter and harmonizing column names."""
    frames = []

    # 1) Legacy Reddit medical/teacher CSVs
    for f, prof in [
        ("comprehensive_medical_pslf_discussions.csv", "medical"),
        ("comprehensive_teacher_pslf_discussions.csv", "teaching"),
    ]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
            d["profession"] = prof
            d["source"] = "reddit_legacy"
            keep = ["date", "polarity", "vader_compound", "profession", "source", "word_count"]
            keep = [c for c in keep if c in d.columns]
            frames.append(d[keep])
            print(f"  reddit_legacy {prof:<10s}:        {len(d):>6,}")

    # 2) Reddit professions corpus (PSLF-filtered at load)
    if os.path.exists("reddit_professions_pslf.csv"):
        d = pd.read_csv("reddit_professions_pslf.csv")
        n_raw = len(d)
        tm = filter_pslf_relevant(d["combined_text"].fillna(""))
        tt = filter_pslf_relevant(d["title"].fillna(""))
        d = d[tm | tt].copy()
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        d["source"] = "reddit_prof"
        # Already has 'profession' column
        keep = ["date", "polarity", "vader_compound", "profession", "source", "word_count"]
        keep = [c for c in keep if c in d.columns]
        frames.append(d[keep])
        print(f"  reddit_professions_pslf:           {n_raw:>6,} raw -> {len(d):>6,} PSLF-filtered")

    # 3) Round-7 PA/NP additions
    if os.path.exists("reddit_new_subs_pslf.csv"):
        d = pd.read_csv("reddit_new_subs_pslf.csv")
        n_raw = len(d)
        tcol = "combined_text" if "combined_text" in d.columns else "selftext"
        tm = filter_pslf_relevant(d[tcol].fillna(""))
        tt = (filter_pslf_relevant(d["title"].fillna(""))
              if "title" in d.columns else pd.Series(False, index=d.index))
        d = d[tm | tt].copy()
        if len(d):
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
            d["source"] = "reddit_new_subs"
            keep = ["date", "polarity", "vader_compound", "profession", "source", "word_count"]
            keep = [c for c in keep if c in d.columns]
            frames.append(d[keep])
            print(f"  reddit_new_subs_pslf:              {n_raw:>6,} raw -> {len(d):>6,} PSLF-filtered")

    # 4) Arctic Shift Reddit (round-7+)
    if os.path.exists("reddit_arctic_shift_pslf.csv"):
        d = pd.read_csv("reddit_arctic_shift_pslf.csv")
        # Already strict-filtered at collection, but apply defensively
        n_raw = len(d)
        tcol = "combined_text" if "combined_text" in d.columns else "selftext"
        tm = filter_pslf_relevant(d[tcol].fillna(""))
        tt = (filter_pslf_relevant(d["title"].fillna(""))
              if "title" in d.columns else pd.Series(False, index=d.index))
        d = d[tm | tt].copy()
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        d["source"] = "reddit_arctic_shift"
        keep = ["date", "polarity", "vader_compound", "profession", "source", "word_count"]
        keep = [c for c in keep if c in d.columns]
        frames.append(d[keep])
        print(f"  reddit_arctic_shift_pslf:          {n_raw:>6,} raw -> {len(d):>6,} PSLF-filtered")

    # 5) SDN forum (PSLF-filtered at load)
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        n_raw = len(d)
        bm = filter_pslf_relevant(d["body"].fillna(""))
        ttm = filter_pslf_relevant(d["thread_title"].fillna(""))
        d = d[bm | ttm].copy()
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        d["profession"] = "sdn_medical"
        d["source"] = "sdn"
        keep = ["date", "polarity", "vader_compound", "profession", "source", "word_count"]
        keep = [c for c in keep if c in d.columns]
        frames.append(d[keep])
        print(f"  forum_pslf_discussions (SDN):      {n_raw:>6,} raw -> {len(d):>6,} PSLF-filtered")

    big = pd.concat(frames, ignore_index=True)
    n_pre_drop = len(big)
    big = big.dropna(subset=["date", "polarity"])
    if "word_count" in big.columns:
        big = big[big["word_count"].fillna(0) >= 20].copy()
    big["date"] = pd.to_datetime(big["date"], utc=True, errors="coerce").dt.tz_localize(None)
    big = big[(big["date"] >= pd.Timestamp("2009-01-01")) &
              (big["date"] <= pd.Timestamp("2026-04-01"))]
    print(f"  Combined corpus (after dedup, wc>=20, date trim): {n_pre_drop:>7,} -> {len(big):>7,}")
    return big


def per_event_per_profession_g(corpus: pd.DataFrame, scorer_col: str,
                                 min_cell_n: int = MIN_CELL_N) -> pd.DataFrame:
    """For each (event, profession) cell with n_pre AND n_post >= min_cell_n,
    compute Hedges' g and block-permutation p."""
    rows = []
    professions = sorted(corpus["profession"].dropna().unique())
    for event_name, event_date, window in EVENTS:
        dt = pd.Timestamp(event_date)
        for prof in professions:
            sub = corpus[corpus["profession"] == prof]
            pre = sub[(sub["date"] >= dt - pd.Timedelta(days=window)) &
                      (sub["date"] < dt) & sub[scorer_col].notna()]
            post = sub[(sub["date"] >= dt) &
                       (sub["date"] <= dt + pd.Timedelta(days=window)) &
                       sub[scorer_col].notna()]
            n_pre, n_post = len(pre), len(post)
            if n_pre < min_cell_n or n_post < min_cell_n:
                continue
            a = pre[scorer_col].to_numpy()
            b = post[scorer_col].to_numpy()
            g = hedges_g(a, b)
            p = block_permutation_p(
                pre[["date", scorer_col]], post[["date", scorer_col]],
                scorer_col=scorer_col, B=1000, seed=42)
            rows.append({
                "event": event_name,
                "event_date": event_date,
                "window_days": window,
                "profession": prof,
                "profession_label": PROF_LABEL.get(prof, prof),
                "scorer": scorer_col,
                "n_pre": n_pre,
                "n_post": n_post,
                "mean_pre": float(a.mean()),
                "mean_post": float(b.mean()),
                "g": g,
                "p_boot": p,
            })
    return pd.DataFrame(rows)


def main():
    print("=" * 80)
    print("Per-event x Per-profession Sentiment Hedges' g (post-Arctic-Shift)")
    print("=" * 80)

    print("\nLoading corpus...")
    corpus = load_corpus()
    print()
    print("Per-profession totals (PSLF-filtered, wc>=20):")
    prof_counts = corpus.groupby("profession").agg(
        n=("polarity", "count"),
        date_min=("date", "min"),
        date_max=("date", "max")).sort_values("n", ascending=False)
    for prof, row in prof_counts.iterrows():
        label = PROF_LABEL.get(prof, prof)
        print(f"  {label:<28s} n={int(row['n']):>7,}  "
              f"({row['date_min'].date()} -> {row['date_max'].date()})")

    print(f"\nComputing per-event x per-profession g (TextBlob + VADER, B=1000)...")
    print(f"  (cells must have n_pre AND n_post >= {MIN_CELL_N})")
    tb = per_event_per_profession_g(corpus, "polarity", MIN_CELL_N)
    va = per_event_per_profession_g(corpus, "vader_compound", MIN_CELL_N)
    print(f"  TextBlob cells reported:    {len(tb)}")
    print(f"  VADER cells reported:       {len(va)}")

    big = pd.concat([tb, va], ignore_index=True)
    big.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Build readable summary text
    print(f"\nWriting {OUT_TXT}...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Per-event x Per-profession Sentiment Hedges' g\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/analyze_per_profession_per_event.py\n")
        f.write("=" * 80 + "\n\n")

        f.write("SCOPE\n")
        f.write("-" * 80 + "\n")
        f.write("Profession-stratified per-event sentiment shift, full post-Arctic-Shift\n")
        f.write("corpus. Reports cells with n_pre AND n_post >= 20 only. p_boot is\n")
        f.write("block-permutation (B=1000, autocorrelation-aware).\n\n")

        f.write("CORPUS COMPOSITION (PSLF-filtered, wc>=20)\n")
        f.write("-" * 80 + "\n")
        for prof, row in prof_counts.iterrows():
            label = PROF_LABEL.get(prof, prof)
            f.write(f"  {label:<28s} n={int(row['n']):>7,}  "
                    f"({row['date_min'].date()} -> {row['date_max'].date()})\n")
        total = int(prof_counts["n"].sum())
        f.write(f"  {'TOTAL':<28s} n={total:>7,}\n\n")

        for scorer_label, df in [("TEXTBLOB", tb), ("VADER", va)]:
            f.write("=" * 80 + "\n")
            f.write(f"{scorer_label} - per-event x per-profession Hedges' g\n")
            f.write("=" * 80 + "\n\n")
            for event_name, _, _ in EVENTS:
                sub = df[df["event"] == event_name].sort_values("g")
                if len(sub) == 0:
                    continue
                f.write(f"{event_name}:\n")
                f.write(f"  {'profession':<28s} {'n_pre':>7s} {'n_post':>7s} "
                        f"{'g':>7s} {'p_boot':>8s} {'sig?':>5s}\n")
                for _, r in sub.iterrows():
                    sig = ("***" if r["p_boot"] < 0.001 else
                           "**" if r["p_boot"] < 0.01 else
                           "*" if r["p_boot"] < 0.05 else
                           "")
                    f.write(f"  {r['profession_label']:<28s} {int(r['n_pre']):>7d} "
                            f"{int(r['n_post']):>7d} {r['g']:>+7.3f} "
                            f"{r['p_boot']:>8.4f} {sig:>5s}\n")
                f.write("\n")

        # Cross-profession concordance summary
        f.write("=" * 80 + "\n")
        f.write("CROSS-PROFESSION CONCORDANCE PER EVENT (TextBlob)\n")
        f.write("-" * 80 + "\n")
        f.write("For each event, lists professions sorted by g; flags whether the\n")
        f.write("profession effects are mostly same-sign (concordant) or split.\n\n")
        for event_name, _, _ in EVENTS:
            sub = tb[tb["event"] == event_name]
            if len(sub) < 2:
                continue
            n_neg = (sub["g"] < -0.05).sum()
            n_pos = (sub["g"] > 0.05).sum()
            n_null = (sub["g"].abs() <= 0.05).sum()
            n_total = len(sub)
            if n_neg >= 0.7 * n_total:
                pattern = f"NEGATIVE-DOMINANT ({n_neg}/{n_total} cells g<-0.05)"
            elif n_pos >= 0.7 * n_total:
                pattern = f"POSITIVE-DOMINANT ({n_pos}/{n_total} cells g>+0.05)"
            elif n_neg >= 2 and n_pos >= 2:
                pattern = f"SPLIT ({n_neg} negative, {n_pos} positive, {n_null} null cells)"
            else:
                pattern = f"NULL/MIXED ({n_neg} neg, {n_pos} pos, {n_null} null)"
            f.write(f"  {event_name:<32s}: {pattern}\n")
        f.write("\n")

        # Headline cells (Bonferroni significant): p_boot < 0.05/n_cells_per_event
        f.write("=" * 80 + "\n")
        f.write("HEADLINE CELLS (Bonferroni-corrected within each event family)\n")
        f.write("-" * 80 + "\n")
        f.write("Cells where p_boot survives Bonferroni correction at the per-event level\n")
        f.write("(alpha = 0.05 / n_cells_per_event_per_scorer).\n\n")
        for scorer_label, df in [("TextBlob", tb), ("VADER", va)]:
            for event_name, _, _ in EVENTS:
                sub = df[df["event"] == event_name].copy()
                n = len(sub)
                if n == 0:
                    continue
                threshold = 0.05 / n
                sig = sub[sub["p_boot"] < threshold].sort_values("p_boot")
                if len(sig) == 0:
                    continue
                f.write(f"  {scorer_label} x {event_name} (alpha/8 cells = {threshold:.4f}):\n")
                for _, r in sig.iterrows():
                    f.write(f"    {r['profession_label']:<28s} g={r['g']:+.3f} "
                            f"p_boot={r['p_boot']:.4f}  n={int(r['n_pre'])}/{int(r['n_post'])}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")

    # Console summary
    print(f"\nKey result: {len(tb)} TextBlob cells + {len(va)} VADER cells with n>=20 both sides.")
    print(f"\n=== TextBlob g-by-event-by-profession (sorted by event, then |g|): ===")
    for event_name, _, _ in EVENTS:
        sub = tb[tb["event"] == event_name].sort_values("g")
        if len(sub) == 0:
            continue
        print(f"\n  {event_name}:")
        for _, r in sub.iterrows():
            sig = "***" if r["p_boot"] < 0.001 else "**" if r["p_boot"] < 0.01 else "*" if r["p_boot"] < 0.05 else ""
            print(f"    {r['profession_label']:<28s} g={r['g']:+.3f} "
                  f"p_boot={r['p_boot']:.4f} {sig:>3s}  n={int(r['n_pre'])}/{int(r['n_post'])}")


if __name__ == "__main__":
    main()
