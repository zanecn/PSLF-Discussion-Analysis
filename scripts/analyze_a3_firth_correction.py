"""
analyze_a3_firth_correction.py
================================
A3 follow-up: apply Firth penalized logistic regression and Haldane-Anscombe
corrected OR to handle the d=1 cell driving SDN-attending OR=0.02.

Output: a3_firth_corrected_results.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

# Try Firth via firthlogist (preferred) or hand-code via penalty
try:
    from firthlogist import FirthLogisticRegression
    HAS_FIRTH = True
except ImportError:
    HAS_FIRTH = False
    print("[INFO] firthlogist not installed — using Haldane-Anscombe sensitivity only")
    print("       (pip install firthlogist for full Firth penalized regression)")

from sentiment_triangulation import load_zeroshot, attach_textblob_vader
from analyze_mediation_career_stage import classify_career_stage, PROF_TO_COHORT

OUT_TXT = "a3_firth_corrected_results.txt"
OUT_CSV = "a3_firth_corrected_results.csv"


def haldane_anscombe_or(a, b, c, d):
    """OR with +0.5 added to each cell — handles zero/one cells."""
    a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    or_val = (a * d) / (b * c)
    log_or = np.log(or_val)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    return or_val, np.exp(log_or - 1.96 * se), np.exp(log_or + 1.96 * se)


def firth_or(X, y):
    """Firth penalized logistic OR with profile likelihood CI (approximate via SE)."""
    if not HAS_FIRTH:
        return None
    model = FirthLogisticRegression()
    model.fit(X, y)
    log_or = model.coef_[0]
    se = model.bse_[0]
    return float(np.exp(log_or)), float(np.exp(log_or - 1.96 * se)), float(np.exp(log_or + 1.96 * se))


def main():
    print("=" * 80)
    print("A3 follow-up: Firth penalized logistic regression for sparse-cell ORs")
    print("=" * 80)

    # Reload data using same pipeline
    zs = load_zeroshot()
    m = attach_textblob_vader(zs)
    m["post_id"] = m["post_id"].astype(str)

    text_frames = []
    for f, text_col, prof_col, id_col in [
        ("reddit_professions_pslf.csv", "combined_text", "profession", "id"),
        ("reddit_arctic_shift_pslf.csv", "combined_text", "profession", "id"),
        ("reddit_new_subs_pslf.csv", "combined_text", "profession", "id"),
        ("comprehensive_medical_pslf_discussions.csv", "combined_text", None, "id"),
        ("comprehensive_teacher_pslf_discussions.csv", "combined_text", None, "id"),
        ("forum_pslf_discussions.csv", "body", None, "post_id"),
    ]:
        if not os.path.exists(f): continue
        try: d = pd.read_csv(f, usecols=lambda c: c in (id_col, prof_col, text_col))
        except: continue
        if id_col != "post_id": d = d.rename(columns={id_col: "post_id"})
        if prof_col is None:
            d["profession"] = ("sdn_medical" if "forum" in f else
                                "medical" if "medical" in f else
                                "teaching" if "teacher" in f else "")
        d["post_id"] = d["post_id"].astype(str)
        text_frames.append(pd.DataFrame({
            "post_id": d["post_id"].values,
            "profession": d["profession"].astype(str).values,
            "combined_text": d[text_col].astype(str).values if text_col in d.columns else "",
        }))
    texts = pd.concat(text_frames, ignore_index=True).drop_duplicates("post_id")
    df = m.merge(texts, on="post_id", how="left")
    df["profession"] = df["profession"].fillna("").astype(str)
    df["cohort"] = df["profession"].map(PROF_TO_COHORT).fillna("Other")
    if "source" in df.columns:
        df.loc[df["source"].fillna("").astype(str).str.lower() == "sdn", "cohort"] = "SDN (Medical)"
    df = df.dropna(subset=["pslf_sentiment", "pslf_stance"])
    df = df[~df["pslf_stance"].isin(["unknown"])]
    df = df[df["pslf_sentiment"].isin(["very_negative", "negative", "neutral",
                                          "positive", "very_positive"])]
    df["career_stage"] = df["combined_text"].fillna("").apply(classify_career_stage)

    rows = []
    targets = [
        ("SDN (Medical)", "ALL", "pooled"),
        ("SDN (Medical)", "resident", "stratified"),
        ("SDN (Medical)", "attending", "stratified"),
        ("SDN (Medical)", "fellow", "stratified"),
        ("Reddit r/PSLF", "ALL", "pooled"),
        ("Reddit Finance", "ALL", "pooled"),
    ]

    print(f"{'cohort':<22s} {'cs':<14s} {'a':>4s} {'b':>4s} {'c':>4s} {'d':>4s} "
          f"{'naive_OR':>10s} {'HA_OR':>10s} {'Firth_OR':>10s}")
    for cohort, cs, kind in targets:
        sub = df[df["cohort"] == cohort]
        if cs != "ALL":
            sub = sub[sub["career_stage"] == cs]
        if len(sub) < 30: continue
        sub = sub.copy()
        sub["is_neg"] = sub["pslf_sentiment"].isin(["very_negative", "negative"]).astype(int)
        sub["is_pur"] = sub["pslf_stance"].isin(["pursuing", "considering"]).astype(int)
        a = int(((sub["is_neg"] == 1) & (sub["is_pur"] == 1)).sum())
        b = int(((sub["is_neg"] == 1) & (sub["is_pur"] == 0)).sum())
        c = int(((sub["is_neg"] == 0) & (sub["is_pur"] == 1)).sum())
        d = int(((sub["is_neg"] == 0) & (sub["is_pur"] == 0)).sum())
        # Naive OR
        try:
            naive_or = (a * d) / (b * c) if b * c > 0 else float("nan")
        except: naive_or = float("nan")
        # Haldane-Anscombe
        ha_or, ha_lo, ha_hi = haldane_anscombe_or(a, b, c, d)
        # Firth
        if HAS_FIRTH:
            X = sub[["is_neg"]].values.astype(float)
            y = sub["is_pur"].values.astype(int)
            try:
                f_or, f_lo, f_hi = firth_or(X, y)
            except Exception as e:
                f_or, f_lo, f_hi = float("nan"), float("nan"), float("nan")
        else:
            f_or, f_lo, f_hi = float("nan"), float("nan"), float("nan")

        print(f"{cohort:<22s} {cs:<14s} {a:>4} {b:>4} {c:>4} {d:>4} "
              f"{naive_or:>10.3f} {ha_or:>10.3f} {f_or if not np.isnan(f_or) else 0:>10.3f}")

        rows.append({
            "cohort": cohort, "career_stage": cs, "kind": kind,
            "n": len(sub), "a": a, "b": b, "c": c, "d": d,
            "naive_OR": naive_or,
            "HA_OR": ha_or, "HA_lo": ha_lo, "HA_hi": ha_hi,
            "Firth_OR": f_or, "Firth_lo": f_lo, "Firth_hi": f_hi,
        })

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("A3 FIRTH-CORRECTED ODDS RATIOS\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Original A3 SDN attending OR=0.016 was driven by d=1 cell.\n")
        f.write("Firth penalized regression (Firth 1993) and Haldane-Anscombe\n")
        f.write("(adding 0.5 to each cell) provide bias-corrected estimates that\n")
        f.write("DO NOT diverge to 0/inf when cells are tiny.\n\n")

        f.write(f"{'cohort':<22s} {'cs':<14s} {'naive':>10s} {'HA':>10s} "
                f"{'Firth':>10s} {'Firth 95% CI':>22s}\n")
        for r in rows:
            ci_str = (f"[{r['Firth_lo']:.2f},{r['Firth_hi']:.2f}]"
                      if not np.isnan(r["Firth_OR"]) else "n/a")
            f.write(f"{r['cohort']:<22s} {r['career_stage']:<14s} "
                    f"{r['naive_OR']:>10.3f} {r['HA_OR']:>10.3f} "
                    f"{r['Firth_OR'] if not np.isnan(r['Firth_OR']) else 0:>10.3f} "
                    f"{ci_str:>22s}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        sdn_att = next((r for r in rows if r["cohort"] == "SDN (Medical)"
                         and r["career_stage"] == "attending"), None)
        if sdn_att:
            f.write(f"SDN attending: naive OR={sdn_att['naive_OR']:.3f}, "
                    f"HA OR={sdn_att['HA_OR']:.3f}, Firth OR={sdn_att['Firth_OR']:.3f}\n")
            if abs(np.log(sdn_att["HA_OR"]) - np.log(sdn_att["naive_OR"])) > 1.0:
                f.write("  -> Naive OR is materially biased by sparse cells. Use Firth/HA.\n")
            else:
                f.write("  -> Sparse-cell bias is modest. Naive OR is approximately valid.\n")
            f.write(f"  -> Cell counts: a(neg+pur)={sdn_att['a']} b(neg+not_pur)={sdn_att['b']} "
                    f"c(not_neg+pur)={sdn_att['c']} d(not_neg+not_pur)={sdn_att['d']}\n")
            f.write(f"  -> The d=1 cell drives the naive estimate.\n")
        f.write("\nCanonical reporting recommendation: report Firth OR + 95% CI as\n")
        f.write("primary; naive OR as sensitivity. Magnitude claim 'extreme decoupling'\n")
        f.write("must be tempered to actual Firth estimate.\n")

    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")


if __name__ == "__main__":
    main()
