"""
analyze_sdn_subthread_consistency.py
======================================
Within-SDN consistency check: does SDN's distinctive per-event response
hold across SDN sub-thread types (residency vs medical-school vs admissions
vs other)? Audit (Round 9) flagged this as critical for the substantive
paper because reviewers will ask whether SDN's "cohort effect" is uniform
or driven by specific sub-communities.

Approach:
  1. Classify SDN posts by sub-thread type via thread_title regex
  2. For each event x sub-thread cell with adequate n, compute Hedges' g
  3. Report whether different SDN sub-threads agree on direction or split
  4. Test: are SDN sub-threads internally consistent on Trump EO, Payments
     Restart, Final Trump Rule (the BH-FDR-significant SDN cells)?

Output: sdn_subthread_consistency.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings
from datetime import datetime
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import re
import numpy as np
import pandas as pd

from sentiment_triangulation import EVENTS, hedges_g, block_permutation_p
from pslf_search_terms import filter_pslf_relevant

OUT_TXT = "sdn_subthread_consistency.txt"
OUT_CSV = "sdn_subthread_consistency.csv"

# SDN sub-thread classification regex (applied to thread_title)
THREAD_PATTERNS = [
    ("residency",        re.compile(r"\b(?:residency|residen[ct]|match|nrmp|pgy|fellowship)\b", re.I)),
    ("medical_school",   re.compile(r"\b(?:medical\s*school|med\s*school|m\s*[1-4]\b|ms\s*[1-4]|mcat|amcas)\b", re.I)),
    ("admissions",       re.compile(r"\b(?:admit|admission|application|interview|secondary|wait[\s-]*list|acceptance)\b", re.I)),
    ("step_boards",      re.compile(r"\b(?:step\s*[1-3]|usmle|comlex|nbme|shelf)\b", re.I)),
    ("specialty",        re.compile(r"\b(?:psych|surgery|gen\s*surg|anesthesiology|family\s*med|im\s*residency|pediatrics)\b", re.I)),
    ("financial",        re.compile(r"\b(?:loan|debt|forgive|salary|finance|repay|mortgage|invest)\b", re.I)),
    ("nontrad",          re.compile(r"\b(?:nontrad|career\s*change|second\s*career|reapplicant)\b", re.I)),
    ("hpsp_military",    re.compile(r"\b(?:hpsp|military|navy|army|usuhs|gmo|mtf)\b", re.I)),
]


def classify_thread(title: str) -> str:
    """Apply patterns in priority order; return first match or 'other'."""
    if not isinstance(title, str):
        return "other"
    for label, pat in THREAD_PATTERNS:
        if pat.search(title):
            return label
    return "other"


def main():
    print("=" * 80)
    print("SDN within-cohort consistency check")
    print("=" * 80)

    print("\nLoading SDN posts...")
    sdn = pd.read_csv("forum_pslf_discussions.csv")
    bm = filter_pslf_relevant(sdn["body"].fillna(""))
    ttm = filter_pslf_relevant(sdn["thread_title"].fillna(""))
    sdn = sdn[bm | ttm].copy()
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn = sdn.dropna(subset=["date", "polarity"])
    sdn = sdn[sdn["word_count"].fillna(0) >= 20]
    print(f"  PSLF-filtered SDN posts (wc>=20): {len(sdn):,}")
    print(f"  Unique threads: {sdn['thread_id'].nunique():,}")

    # Classify
    sdn["subthread"] = sdn["thread_title"].fillna("").apply(classify_thread)
    print("\n  Sub-thread distribution:")
    print(sdn["subthread"].value_counts().to_string().replace("\n", "\n    "))

    # Per-event x per-subthread Hedges' g
    print("\nComputing per-event x per-subthread g...")
    rows = []
    for event_name, event_date, win in EVENTS:
        dt = pd.Timestamp(event_date)
        for subthread in sdn["subthread"].value_counts().index:
            sub = sdn[sdn["subthread"] == subthread]
            pre = sub[(sub["date"] >= dt - pd.Timedelta(days=win)) &
                      (sub["date"] < dt) & sub["polarity"].notna()]
            post = sub[(sub["date"] >= dt) &
                       (sub["date"] <= dt + pd.Timedelta(days=win)) &
                       sub["polarity"].notna()]
            n_pre, n_post = len(pre), len(post)
            if n_pre < 15 or n_post < 15:
                continue
            a = pre["polarity"].to_numpy()
            b = post["polarity"].to_numpy()
            g = hedges_g(a, b)
            p_boot = block_permutation_p(
                pre[["date", "polarity"]], post[["date", "polarity"]],
                scorer_col="polarity", B=1000, seed=42)
            rows.append({
                "event": event_name,
                "subthread": subthread,
                "n_pre": n_pre,
                "n_post": n_post,
                "mean_pre": float(a.mean()),
                "mean_post": float(b.mean()),
                "g": g,
                "p_boot": p_boot,
            })
    df = pd.DataFrame(rows)
    df.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Summary: for each event, count sub-threads agreeing on sign
    print("\nWithin-SDN consistency per event:")
    consistency = []
    for event_name, _, _ in EVENTS:
        sub = df[df["event"] == event_name]
        if len(sub) < 2:
            continue
        n_pos = (sub["g"] > 0.05).sum()
        n_neg = (sub["g"] < -0.05).sum()
        n_null = (sub["g"].abs() <= 0.05).sum()
        n_total = len(sub)
        if n_pos >= 0.7 * n_total:
            verdict = f"POS-DOMINANT ({n_pos}/{n_total})"
        elif n_neg >= 0.7 * n_total:
            verdict = f"NEG-DOMINANT ({n_neg}/{n_total})"
        elif n_pos >= 2 and n_neg >= 2:
            verdict = f"SPLIT ({n_pos} pos, {n_neg} neg)"
        else:
            verdict = f"MIXED ({n_pos} pos, {n_neg} neg, {n_null} null)"
        consistency.append({
            "event": event_name,
            "n_subthreads_with_data": n_total,
            "n_positive_g": n_pos,
            "n_negative_g": n_neg,
            "n_null_g": n_null,
            "median_g": float(sub["g"].median()),
            "verdict": verdict,
        })
        print(f"  {event_name:<30s}: {verdict}, median g={sub['g'].median():+.3f}")

    # Write report
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SDN within-cohort consistency check\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether SDN's distinctive per-event response is consistent across\n")
        f.write("SDN sub-thread types (residency, medical_school, admissions, financial,\n")
        f.write("etc.) or driven by specific sub-communities.\n\n")
        f.write(f"Sample: {len(sdn):,} PSLF-filtered SDN posts (wc>=20) across "
                f"{sdn['thread_id'].nunique():,} unique threads.\n\n")

        f.write("SUB-THREAD DISTRIBUTION\n")
        f.write("-" * 80 + "\n")
        for label, n in sdn["subthread"].value_counts().items():
            f.write(f"  {label:<20s}  {n:>5,}\n")

        f.write("\nPER-EVENT x PER-SUBTHREAD HEDGES' G\n")
        f.write("-" * 80 + "\n")
        for event_name, _, _ in EVENTS:
            sub = df[df["event"] == event_name].sort_values("g")
            if len(sub) == 0:
                continue
            f.write(f"\n{event_name}:\n")
            f.write(f"  {'subthread':<20s} {'n_pre':>6s} {'n_post':>6s} "
                    f"{'g':>7s} {'p_boot':>8s}\n")
            for _, r in sub.iterrows():
                sig = "***" if r["p_boot"] < 0.001 else "**" if r["p_boot"] < 0.01 else "*" if r["p_boot"] < 0.05 else ""
                f.write(f"  {r['subthread']:<20s} {int(r['n_pre']):>6d} {int(r['n_post']):>6d} "
                        f"{r['g']:>+7.3f} {r['p_boot']:>8.4f} {sig}\n")

        f.write("\nWITHIN-SDN CONSISTENCY VERDICTS\n")
        f.write("-" * 80 + "\n")
        for c in consistency:
            f.write(f"  {c['event']:<30s} {c['verdict']:<35s} "
                    f"median g={c['median_g']:+.3f}  "
                    f"({c['n_subthreads_with_data']} sub-threads with adequate n)\n")

        f.write("\nKEY TESTS (BH-FDR-significant SDN cells from per_profession)\n")
        f.write("-" * 80 + "\n")
        bh_sig_events_for_sdn = [
            ("Trump PSLF EO", "expected: NEGATIVE direction in all SDN sub-threads"),
            ("SAVE Admin Forbearance", "expected: POSITIVE direction (g=+1.69 in pooled SDN)"),
        ]
        for ev, expectation in bh_sig_events_for_sdn:
            sub = df[df["event"] == ev]
            if len(sub) == 0:
                f.write(f"\n  {ev}: NO SUB-THREADS HAVE ADEQUATE n\n")
                continue
            f.write(f"\n  {ev} ({expectation}):\n")
            for _, r in sub.iterrows():
                sig = "***" if r["p_boot"] < 0.001 else "**" if r["p_boot"] < 0.01 else "*" if r["p_boot"] < 0.05 else "-"
                f.write(f"    {r['subthread']:<20s} g={r['g']:+.3f} {sig} (n={int(r['n_pre'])}/{int(r['n_post'])})\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")


if __name__ == "__main__":
    main()
