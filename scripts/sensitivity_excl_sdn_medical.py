"""
sensitivity_excl_sdn_medical.py
================================
SDN-Medical-excluded sensitivity recomputation. Round-7 audit response:
SDN (Medical) accounts for ~40% of the sentiment-eligible corpus and dominates
many per-event x per-profession cells. Any reviewer at a methods or policy venue
will ask whether the headline findings depend on the SDN-Medical subsample.

This script re-runs the four main result families with SDN-Medical excluded,
side-by-side with the full-sample version, and classifies each finding as:
  SURVIVES    - same direction; effect-size magnitude reduced <=30%
  WEAKENED    - same direction; magnitude reduced >30% but still present
  COLLAPSED   - effect drops below 0.1 or sample becomes underpowered (n<10)
  REVERSED    - sign flips
  UNDERPOWERED - excluded subsample leaves n_pre or n_post < 10

Result families re-run:
  A) Three-rater Krippendorff's alpha (canonical + percentile-matched)
  B) Per-event pre/post Hedges' g (TextBlob, VADER, Claude)
  C) Per-event pslf_stance rejecting-rate shifts
  D) Per-event topic-distribution shifts (Cramer's V on 7-class topic)

Outputs:
  - sensitivity_results.txt - canonical text artifact with verdicts
  - sensitivity_results.csv - per-finding side-by-side table

Usage:
  python sensitivity_excl_sdn_medical.py
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

import krippendorff

# Reuse existing infrastructure rather than duplicating it
from sentiment_triangulation import (
    EVENTS,
    CLAUDE_NUMERIC,
    textblob_to_5,
    vader_to_5,
    hedges_g,
    block_permutation_p,
    load_zeroshot,
    attach_textblob_vader,
)

OUT_TXT = "sensitivity_results.txt"
OUT_CSV = "sensitivity_results.csv"


# ============================================================
# SDN-Medical identification
# ============================================================
def tag_sdn_medical(merged: pd.DataFrame) -> pd.Series:
    """Boolean mask for SDN-Medical posts.

    Convention (matches pslf_intention_analysis.py):
      - source == 'sdn' (forum source, all SDN content is medical-leaning)
      - OR subsample tag starts with 'sdn_' (zeroshot provenance)
      - OR profession in {'medical', 'sdn_medical'} on a sdn-sourced row
    """
    if "source" in merged.columns:
        is_sdn_source = merged["source"].fillna("").astype(str).str.lower() == "sdn"
    else:
        is_sdn_source = pd.Series(False, index=merged.index)
    if "subsample" in merged.columns:
        is_sdn_sub = merged["subsample"].fillna("").astype(str).str.startswith("sdn_")
    else:
        is_sdn_sub = pd.Series(False, index=merged.index)
    return is_sdn_source | is_sdn_sub


# ============================================================
# A) Krippendorff's alpha — three-rater, full vs excluded
# ============================================================
def alpha_three_rater(merged: pd.DataFrame, label: str = ""):
    """Compute three-rater alpha (canonical fixed thresholds + percentile-matched).
    Returns dict with both estimates and the n used."""
    df = merged.copy()
    df["textblob_5"] = df["polarity"].apply(textblob_to_5)
    df["vader_5"] = df["vader_compound"].apply(vader_to_5)
    rd = np.array([
        df["textblob_5"].astype(float).to_numpy(),
        df["vader_5"].astype(float).to_numpy(),
        df["claude_numeric"].astype(float).to_numpy(),
    ])
    n_units = rd.shape[1]
    try:
        alpha_fixed = krippendorff.alpha(reliability_data=rd, level_of_measurement="ordinal")
    except Exception:
        alpha_fixed = float("nan")

    # Percentile-matched (charitable upper bound)
    sub = df[["polarity", "vader_compound", "claude_numeric"]].dropna()
    n_complete = len(sub)
    alpha_pct = float("nan")
    if n_complete > 50:
        pct = sub.copy()
        try:
            pct["TB_pct"] = pd.qcut(pct["polarity"], q=5, labels=[-2, -1, 0, 1, 2],
                                    duplicates="drop").astype(float)
            pct["VA_pct"] = pd.qcut(pct["vader_compound"], q=5, labels=[-2, -1, 0, 1, 2],
                                    duplicates="drop").astype(float)
            rd_pct = np.array([
                pct["TB_pct"].astype(float).to_numpy(),
                pct["VA_pct"].astype(float).to_numpy(),
                pct["claude_numeric"].astype(float).to_numpy(),
            ])
            alpha_pct = krippendorff.alpha(reliability_data=rd_pct, level_of_measurement="ordinal")
        except Exception:
            alpha_pct = float("nan")

    return {
        "label": label,
        "n_units": int(n_units),
        "n_complete": int(n_complete),
        "alpha_canonical": float(alpha_fixed) if not np.isnan(alpha_fixed) else float("nan"),
        "alpha_pct_charitable": float(alpha_pct) if not np.isnan(alpha_pct) else float("nan"),
    }


# ============================================================
# B) Per-event Hedges' g (TextBlob, VADER, Claude)
# ============================================================
def per_event_g(merged: pd.DataFrame, label: str = "") -> pd.DataFrame:
    """Per-event pre/post Hedges' g across all three scorers."""
    es = merged.dropna(subset=["polarity", "vader_compound",
                                "claude_numeric", "date"]).copy()
    rows = []
    for event_name, event_date, window in EVENTS:
        dt = pd.Timestamp(event_date)
        pre = es[(es["date"] >= dt - pd.Timedelta(days=window)) & (es["date"] < dt)]
        post = es[(es["date"] >= dt) & (es["date"] <= dt + pd.Timedelta(days=window))]
        if len(pre) < 5 or len(post) < 5:
            rows.append({
                "subset": label, "event": event_name,
                "n_pre": len(pre), "n_post": len(post),
                "g_textblob": float("nan"), "g_vader": float("nan"), "g_claude": float("nan"),
                "p_boot_textblob": float("nan"), "p_boot_vader": float("nan"),
                "p_boot_claude": float("nan"),
            })
            continue
        row = {"subset": label, "event": event_name,
               "n_pre": len(pre), "n_post": len(post)}
        for s_idx, (scorer, col) in enumerate([("textblob", "polarity"),
                                                ("vader", "vader_compound"),
                                                ("claude", "claude_numeric")]):
            a = pre[col].dropna().to_numpy()
            b = post[col].dropna().to_numpy()
            if len(a) < 2 or len(b) < 2:
                row[f"g_{scorer}"] = float("nan")
                row[f"p_boot_{scorer}"] = float("nan")
                continue
            row[f"g_{scorer}"] = hedges_g(a, b)
            row[f"p_boot_{scorer}"] = block_permutation_p(
                pre[["date", col]], post[["date", col]], scorer_col=col,
                B=1000, seed=42 + s_idx)  # B=1000 for sensitivity (faster)
        rows.append(row)
    return pd.DataFrame(rows)


# ============================================================
# C) Per-event pslf_stance rejecting-rate shifts
# ============================================================
def per_event_stance(merged: pd.DataFrame, label: str = "") -> pd.DataFrame:
    """Per-event pre/post change in proportion 'rejecting' (2-prop z-test)."""
    if "pslf_stance" not in merged.columns:
        return pd.DataFrame()
    es = merged.dropna(subset=["pslf_stance", "date"]).copy()
    es = es[~es["pslf_stance"].isin(["unknown", "parse_error", "api_error", ""])]
    rows = []
    for event_name, event_date, window in EVENTS:
        dt = pd.Timestamp(event_date)
        pre = es[(es["date"] >= dt - pd.Timedelta(days=window)) & (es["date"] < dt)]
        post = es[(es["date"] >= dt) & (es["date"] <= dt + pd.Timedelta(days=window))]
        n_pre, n_post = len(pre), len(post)
        if n_pre < 10 or n_post < 10:
            rows.append({
                "subset": label, "event": event_name,
                "n_pre": n_pre, "n_post": n_post,
                "pct_rejecting_pre": float("nan"), "pct_rejecting_post": float("nan"),
                "delta_pp": float("nan"), "p_two_prop_z": float("nan"),
            })
            continue
        rej_pre = (pre["pslf_stance"] == "rejecting").sum()
        rej_post = (post["pslf_stance"] == "rejecting").sum()
        p_pre = rej_pre / n_pre
        p_post = rej_post / n_post
        delta = (p_post - p_pre) * 100
        # Two-proportion z-test
        p_pool = (rej_pre + rej_post) / (n_pre + n_post)
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n_pre + 1/n_post))
        z = (p_post - p_pre) / se if se > 0 else 0.0
        p_val = 2 * (1 - stats.norm.cdf(abs(z)))
        rows.append({
            "subset": label, "event": event_name,
            "n_pre": n_pre, "n_post": n_post,
            "pct_rejecting_pre": p_pre * 100,
            "pct_rejecting_post": p_post * 100,
            "delta_pp": delta,
            "p_two_prop_z": p_val,
        })
    return pd.DataFrame(rows)


# ============================================================
# D) Per-event topic-distribution shifts (Cramer's V)
# ============================================================
def cramers_v(contingency: np.ndarray) -> float:
    """Cramer's V from a contingency table."""
    chi2 = stats.chi2_contingency(contingency)[0]
    n = contingency.sum()
    if n == 0:
        return float("nan")
    r, k = contingency.shape
    if min(r - 1, k - 1) == 0:
        return float("nan")
    return float(np.sqrt(chi2 / (n * min(r - 1, k - 1))))


def per_event_topic_v(merged: pd.DataFrame, label: str = "") -> pd.DataFrame:
    """Per-event Cramer's V on the 7-category topic distribution shift."""
    if "primary_topic" not in merged.columns:
        return pd.DataFrame()
    es = merged.dropna(subset=["primary_topic", "date"]).copy()
    es = es[~es["primary_topic"].isin(["parse_error", "api_error", ""])]
    rows = []
    for event_name, event_date, window in EVENTS:
        dt = pd.Timestamp(event_date)
        pre = es[(es["date"] >= dt - pd.Timedelta(days=window)) & (es["date"] < dt)]
        post = es[(es["date"] >= dt) & (es["date"] <= dt + pd.Timedelta(days=window))]
        n_pre, n_post = len(pre), len(post)
        if n_pre < 20 or n_post < 20:
            rows.append({
                "subset": label, "event": event_name,
                "n_pre": n_pre, "n_post": n_post,
                "cramers_v": float("nan"), "chi2_p": float("nan"),
            })
            continue
        topics = sorted(set(pre["primary_topic"]).union(set(post["primary_topic"])))
        ct = np.zeros((2, len(topics)), dtype=int)
        for j, t in enumerate(topics):
            ct[0, j] = (pre["primary_topic"] == t).sum()
            ct[1, j] = (post["primary_topic"] == t).sum()
        # Drop columns where either row is zero (chi2 needs >0 expected)
        keep = (ct.sum(axis=0) > 0)
        ct = ct[:, keep]
        if ct.shape[1] < 2:
            rows.append({
                "subset": label, "event": event_name,
                "n_pre": n_pre, "n_post": n_post,
                "cramers_v": float("nan"), "chi2_p": float("nan"),
            })
            continue
        v = cramers_v(ct)
        _, p = stats.chi2_contingency(ct)[:2]
        rows.append({
            "subset": label, "event": event_name,
            "n_pre": n_pre, "n_post": n_post,
            "cramers_v": v, "chi2_p": p,
        })
    return pd.DataFrame(rows)


# ============================================================
# Verdict classification
# ============================================================
def classify_g_verdict(g_full: float, g_excl: float, n_pre_excl: int, n_post_excl: int) -> str:
    """Classify how an effect-size finding survives SDN-Medical exclusion."""
    if np.isnan(g_full):
        return "ORIGINAL_NA"
    if n_pre_excl < 10 or n_post_excl < 10:
        return "UNDERPOWERED"
    if np.isnan(g_excl):
        return "COLLAPSED"
    if abs(g_excl) < 0.1:
        return "COLLAPSED"
    if np.sign(g_excl) != np.sign(g_full):
        return "REVERSED"
    if abs(g_full) > 0:
        ratio = abs(g_excl) / abs(g_full)
        if ratio >= 0.7:
            return "SURVIVES"
        return "WEAKENED"
    return "SURVIVES"


def classify_pp_verdict(d_full: float, d_excl: float, n_pre: int, n_post: int) -> str:
    """Classify a percentage-point finding."""
    if np.isnan(d_full):
        return "ORIGINAL_NA"
    if n_pre < 10 or n_post < 10:
        return "UNDERPOWERED"
    if np.isnan(d_excl):
        return "COLLAPSED"
    if abs(d_excl) < 2.0:
        return "COLLAPSED"
    if np.sign(d_excl) != np.sign(d_full):
        return "REVERSED"
    if abs(d_full) > 0:
        ratio = abs(d_excl) / abs(d_full)
        if ratio >= 0.7:
            return "SURVIVES"
        return "WEAKENED"
    return "SURVIVES"


# ============================================================
# Main
# ============================================================
def main():
    print("=" * 78)
    print("SDN-Medical-excluded sensitivity recomputation")
    print("=" * 78)

    print("\nLoading zero-shot subsamples (mirrors sentiment_triangulation.py)...")
    zs = load_zeroshot()
    print(f"  Combined zero-shot rows (deduped): {len(zs):,}")

    print("Merging with TextBlob + VADER + dates...")
    merged = attach_textblob_vader(zs)
    print(f"  Total merged rows: {len(merged):,}")

    sdn_med = tag_sdn_medical(merged)
    print(f"\n  SDN-Medical rows:        {sdn_med.sum():,} ({100*sdn_med.mean():.1f}%)")
    print(f"  Non-SDN-Medical rows:    {(~sdn_med).sum():,} ({100*(~sdn_med).mean():.1f}%)")

    # Verify a meaningful subset remains
    n_excl = (~sdn_med).sum()
    if n_excl < 1000:
        print(f"\n[ABORT] Only {n_excl:,} rows remain after excluding SDN-Medical.")
        sys.exit(1)

    full = merged.copy()
    excl = merged[~sdn_med].copy()

    # === A) Krippendorff's alpha ===
    print("\n[A] Three-rater Krippendorff's alpha...")
    alpha_full = alpha_three_rater(full, "FULL")
    alpha_excl = alpha_three_rater(excl, "EXCL_SDN_MED")
    print(f"  Canonical alpha:    full={alpha_full['alpha_canonical']:+.4f} (n={alpha_full['n_complete']:,})  "
          f"excl={alpha_excl['alpha_canonical']:+.4f} (n={alpha_excl['n_complete']:,})")
    print(f"  Charitable alpha:   full={alpha_full['alpha_pct_charitable']:+.4f}  "
          f"excl={alpha_excl['alpha_pct_charitable']:+.4f}")

    # === B) Per-event Hedges' g ===
    print("\n[B] Per-event pre/post Hedges' g across 3 scorers (B=1000 for sensitivity)...")
    g_full = per_event_g(full, "FULL")
    g_excl = per_event_g(excl, "EXCL_SDN_MED")

    # === C) Per-event stance shifts ===
    print("\n[C] Per-event pslf_stance rejecting-rate shifts...")
    s_full = per_event_stance(full, "FULL")
    s_excl = per_event_stance(excl, "EXCL_SDN_MED")

    # === D) Per-event topic shifts ===
    print("\n[D] Per-event topic-distribution Cramer's V...")
    t_full = per_event_topic_v(full, "FULL")
    t_excl = per_event_topic_v(excl, "EXCL_SDN_MED")

    # === Build comparison table ===
    print("\nBuilding comparison table...")
    comparisons = []

    # B: per-event g (3 scorers x 8 events = up to 24 rows)
    for event_name, _, _ in EVENTS:
        gf = g_full[g_full["event"] == event_name]
        ge = g_excl[g_excl["event"] == event_name]
        if gf.empty or ge.empty:
            continue
        gf = gf.iloc[0]
        ge = ge.iloc[0]
        for scorer in ["textblob", "vader", "claude"]:
            comparisons.append({
                "family": "B_g",
                "event": event_name,
                "metric": f"g_{scorer}",
                "full_value": gf[f"g_{scorer}"],
                "excl_value": ge[f"g_{scorer}"],
                "full_n": f"{int(gf['n_pre'])}/{int(gf['n_post'])}",
                "excl_n": f"{int(ge['n_pre'])}/{int(ge['n_post'])}",
                "verdict": classify_g_verdict(
                    gf[f"g_{scorer}"], ge[f"g_{scorer}"],
                    int(ge["n_pre"]), int(ge["n_post"])),
            })

    # C: per-event stance shifts
    for event_name, _, _ in EVENTS:
        sf = s_full[s_full["event"] == event_name]
        se = s_excl[s_excl["event"] == event_name]
        if sf.empty or se.empty:
            continue
        sf = sf.iloc[0]
        se = se.iloc[0]
        comparisons.append({
            "family": "C_stance",
            "event": event_name,
            "metric": "delta_rejecting_pp",
            "full_value": sf["delta_pp"],
            "excl_value": se["delta_pp"],
            "full_n": f"{int(sf['n_pre'])}/{int(sf['n_post'])}",
            "excl_n": f"{int(se['n_pre'])}/{int(se['n_post'])}",
            "verdict": classify_pp_verdict(
                sf["delta_pp"], se["delta_pp"],
                int(se["n_pre"]), int(se["n_post"])),
        })

    # D: per-event topic Cramer's V (ratio-based survival)
    for event_name, _, _ in EVENTS:
        tf = t_full[t_full["event"] == event_name]
        te = t_excl[t_excl["event"] == event_name]
        if tf.empty or te.empty:
            continue
        tf = tf.iloc[0]
        te = te.iloc[0]
        # For Cramer's V (always positive), survival = ratio against full
        v_full = tf["cramers_v"]
        v_excl = te["cramers_v"]
        if np.isnan(v_full):
            verdict = "ORIGINAL_NA"
        elif int(te["n_pre"]) < 20 or int(te["n_post"]) < 20:
            verdict = "UNDERPOWERED"
        elif np.isnan(v_excl) or v_excl < 0.05:
            verdict = "COLLAPSED"
        elif v_full > 0:
            r = v_excl / v_full
            if r >= 0.7:
                verdict = "SURVIVES"
            elif r >= 0.4:
                verdict = "WEAKENED"
            else:
                verdict = "COLLAPSED"
        else:
            verdict = "SURVIVES"
        comparisons.append({
            "family": "D_topic_v",
            "event": event_name,
            "metric": "cramers_v",
            "full_value": v_full,
            "excl_value": v_excl,
            "full_n": f"{int(tf['n_pre'])}/{int(tf['n_post'])}",
            "excl_n": f"{int(te['n_pre'])}/{int(te['n_post'])}",
            "verdict": verdict,
        })

    comp_df = pd.DataFrame(comparisons)

    # === Write artifacts ===
    print(f"\nWriting {OUT_TXT}...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Sensitivity Analysis - SDN-Medical-Excluded Recomputation\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/sensitivity_excl_sdn_medical.py\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("SDN (Medical) accounts for ~40% of the sentiment-eligible corpus and dominates\n")
        f.write("many per-event x per-profession cells. This artifact re-runs main findings with\n")
        f.write("SDN-Medical excluded to bound the 'SDN-driven artifact' critique.\n\n")
        f.write("VERDICT KEY\n")
        f.write("  SURVIVES    - same direction; magnitude ratio (excl/full) >= 0.7\n")
        f.write("  WEAKENED    - same direction; magnitude ratio 0.3-0.7\n")
        f.write("  COLLAPSED   - effect drops below threshold or sample inadequate\n")
        f.write("  REVERSED    - sign flips between full and excluded\n")
        f.write("  UNDERPOWERED - excluded subsample has n_pre or n_post < 10 (g) or < 20 (V)\n\n")

        f.write("SAMPLE SIZES\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Full corpus (3-scorer):       n={alpha_full['n_complete']:,}\n")
        f.write(f"  SDN-Medical-excluded:         n={alpha_excl['n_complete']:,} "
                f"({100*alpha_excl['n_complete']/max(alpha_full['n_complete'],1):.1f}%)\n")
        f.write(f"  SDN-Medical excluded count:   {sdn_med.sum():,} rows\n\n")

        f.write("[A] KRIPPENDORFF'S ALPHA - INSTRUMENT DISAGREEMENT\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Canonical (fixed thresholds):      "
                f"full={alpha_full['alpha_canonical']:+.4f}  "
                f"excl={alpha_excl['alpha_canonical']:+.4f}  "
                f"delta={alpha_excl['alpha_canonical']-alpha_full['alpha_canonical']:+.4f}\n")
        f.write(f"  Charitable (percentile-matched):   "
                f"full={alpha_full['alpha_pct_charitable']:+.4f}  "
                f"excl={alpha_excl['alpha_pct_charitable']:+.4f}  "
                f"delta={alpha_excl['alpha_pct_charitable']-alpha_full['alpha_pct_charitable']:+.4f}\n")
        f.write("  Interpretation: if alpha barely moves, the construct-mismatch finding is\n")
        f.write("  not SDN-driven; if it jumps toward 0.667, SDN-Medical was the disagreement\n")
        f.write("  source.\n\n")

        f.write("[B] PER-EVENT HEDGES' g (3 scorers, 8 events)\n")
        f.write("-" * 80 + "\n")
        b_rows = comp_df[comp_df["family"] == "B_g"]
        f.write(f"{'Event':<28s} {'metric':<10s} {'full':>7s} {'excl':>7s} "
                f"{'full_n':>10s} {'excl_n':>10s} {'verdict':<12s}\n")
        for _, r in b_rows.iterrows():
            fv = f"{r['full_value']:+.3f}" if not pd.isna(r['full_value']) else "  n/a "
            ev = f"{r['excl_value']:+.3f}" if not pd.isna(r['excl_value']) else "  n/a "
            f.write(f"{r['event']:<28s} {r['metric']:<10s} {fv:>7s} {ev:>7s} "
                    f"{r['full_n']:>10s} {r['excl_n']:>10s} {r['verdict']:<12s}\n")

        f.write("\n[C] PER-EVENT STANCE-REJECTING-RATE SHIFT (pp)\n")
        f.write("-" * 80 + "\n")
        c_rows = comp_df[comp_df["family"] == "C_stance"]
        f.write(f"{'Event':<28s} {'full_pp':>9s} {'excl_pp':>9s} "
                f"{'full_n':>10s} {'excl_n':>10s} {'verdict':<12s}\n")
        for _, r in c_rows.iterrows():
            fv = f"{r['full_value']:+.2f}" if not pd.isna(r['full_value']) else "  n/a"
            ev = f"{r['excl_value']:+.2f}" if not pd.isna(r['excl_value']) else "  n/a"
            f.write(f"{r['event']:<28s} {fv:>9s} {ev:>9s} "
                    f"{r['full_n']:>10s} {r['excl_n']:>10s} {r['verdict']:<12s}\n")

        f.write("\n[D] PER-EVENT TOPIC SHIFTS - CRAMER'S V (composition-immune)\n")
        f.write("-" * 80 + "\n")
        d_rows = comp_df[comp_df["family"] == "D_topic_v"]
        f.write(f"{'Event':<28s} {'full_V':>7s} {'excl_V':>7s} "
                f"{'full_n':>10s} {'excl_n':>10s} {'verdict':<12s}\n")
        for _, r in d_rows.iterrows():
            fv = f"{r['full_value']:.3f}" if not pd.isna(r['full_value']) else "  n/a"
            ev = f"{r['excl_value']:.3f}" if not pd.isna(r['excl_value']) else "  n/a"
            f.write(f"{r['event']:<28s} {fv:>7s} {ev:>7s} "
                    f"{r['full_n']:>10s} {r['excl_n']:>10s} {r['verdict']:<12s}\n")

        # Summary verdicts
        f.write("\n" + "=" * 80 + "\n")
        f.write("SUMMARY VERDICTS\n")
        f.write("-" * 80 + "\n")
        v_counts = comp_df["verdict"].value_counts()
        for v, c in v_counts.items():
            f.write(f"  {v:<14s}  {c:>3d} of {len(comp_df)} comparisons\n")
        f.write("\nKey questions for paper Discussion:\n")
        f.write("  1. Did Krippendorff's alpha shift materially toward 0.667 in [A]? "
                "If no, the\n     construct-mismatch finding is not SDN-driven.\n")
        f.write("  2. Which events in [B], [C], [D] survive vs collapse? Survivors are\n"
                "     defensible without SDN-Medical; collapses must be reframed as\n"
                "     SDN-Medical-specific.\n")
        f.write("  3. Topic-shift survivals [D] are the strongest signal because Cramer's V\n"
                "     is composition-immune. If [D] survives broadly, the substantive paper's\n"
                "     topic-restructuring claim is robust.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    comp_df.to_csv(OUT_CSV, index=False, float_format="%.4f")
    print(f"Saved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")
    print(f"\nQuick summary of {len(comp_df)} comparisons:")
    print(comp_df["verdict"].value_counts().to_string())


if __name__ == "__main__":
    main()
