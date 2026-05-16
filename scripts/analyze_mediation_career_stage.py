"""
analyze_mediation_career_stage.py
===================================
Tests whether career stage MEDIATES the cohort × decoupling relationship.

Hypothesis: SDN-Medical's strong decoupling (OR=0.27) is partly because SDN
posters skew resident/attending (high career-stake stage). If we condition on
career stage, does cohort still predict decoupling?

Method:
  1. Use career-stage classifier on all stance-classified posts
  2. Among posters with explicit career-stage markers (~13% coverage), test:
     - Is the SDN OR=0.27 finding driven by residents specifically?
     - Or do attendings, fellows show the same pattern?
  3. Compare: SDN-residents OR vs Reddit-r/PSLF-residents OR (cohort effect within career stage)
  4. Compare: SDN-residents OR vs SDN-attendings OR (career-stage effect within cohort)

Output: mediation_career_stage_results.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings, re
from datetime import datetime
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

from sentiment_triangulation import load_zeroshot, attach_textblob_vader

OUT_TXT = "mediation_career_stage_results.txt"
OUT_CSV = "mediation_career_stage_results.csv"

PROF_TO_COHORT = {
    "general_pslf":              "Reddit r/PSLF",
    "general_student_loans":     "Reddit r/StudentLoans",
    "general_finance":           "Reddit Finance",
    "personalfinance":           "Reddit Finance",
    "financialindependence":     "Reddit Finance",
    "medical":                   "Reddit Medical",
    "teaching":                  "Reddit Teaching",
    "physician_assistant":       "Reddit PA",
    "nursing":                   "Reddit Nursing",
}

# Career-stage classifier (from pslf_intention_analysis.py)
_CAREER_PATTERNS = {
    "premed":          re.compile(r"\b(?:pre[\s\-]?med|pre[\s\-]?medical|aspiring (?:doctor|md)|"
                                    r"applying to med(?:ical)? school|undergrad(?:uate)? (?:pre|considering)|"
                                    r"mcat|amcas|aacomas)\b", re.I),
    "medical_student": re.compile(r"\b(?:m[1-4]\b|ms[\s\-]?[1-4]\b|m[1-4]/m[1-4]|"
                                    r"med(?:ical)? student|first[\s\-]?year (?:medical|med)|"
                                    r"second[\s\-]?year (?:medical|med)|third[\s\-]?year (?:medical|med)|"
                                    r"fourth[\s\-]?year (?:medical|med)|"
                                    r"starting med(?:ical)? school|in med(?:ical)? school|"
                                    r"as a (?:current )?med(?:ical)? student)\b", re.I),
    "resident":        re.compile(r"\b(?:pgy[\s\-]?[1-9]\b|pgy\d|resident(?:cy)?|"
                                    r"as a resident|currently (?:in|a) residen(?:t|cy)|"
                                    r"intern(?:\s+year)?|ms4 (?:into|matched|going into)|"
                                    r"matched (?:into )?(?:im|family|peds|psych|surgery|gen surg))\b", re.I),
    "attending":       re.compile(r"\b(?:as an attending|attending physician|"
                                    r"practicing (?:physician|doc)|years out of residency|"
                                    r"years out of training|finished residency|after residency|"
                                    r"currently practicing|partnership track|"
                                    r"private practice for \d+ years)\b", re.I),
    "fellow":          re.compile(r"\b(?:fellow(?:ship)?|cardiology fellow|gi fellow|"
                                    r"pccm fellow|hem[\s/]onc fellow|f[1-3]\b)\b", re.I),
}
_CAREER_PRIORITY = ["fellow", "attending", "resident", "medical_student", "premed"]


def classify_career_stage(text: str) -> str:
    if not isinstance(text, str):
        return "unknown"
    matches = [s for s, p in _CAREER_PATTERNS.items() if p.search(text)]
    if not matches:
        return "unknown"
    for p in _CAREER_PRIORITY:
        if p in matches:
            return p
    return matches[0]


def compute_or(sub: pd.DataFrame) -> dict:
    sub["is_neg"] = sub["pslf_sentiment"].isin(["very_negative", "negative"])
    sub["is_pur"] = sub["pslf_stance"].isin(["pursuing", "considering"])
    a = ((sub["is_neg"]) & (sub["is_pur"])).sum()
    b = ((sub["is_neg"]) & (~sub["is_pur"])).sum()
    c = ((~sub["is_neg"]) & (sub["is_pur"])).sum()
    d = ((~sub["is_neg"]) & (~sub["is_pur"])).sum()
    if min(a, b, c, d) < 1:
        return {"or": float("nan"), "p": float("nan"), "ci_lo": float("nan"),
                "ci_hi": float("nan"), "n": int(len(sub)),
                "n_neg": int((sub["is_neg"]).sum())}
    or_val = (a*d) / (b*c) if b*c > 0 else float("nan")
    log_or = np.log(or_val) if or_val > 0 else float("nan")
    se = np.sqrt(1/a + 1/b + 1/c + 1/d) if min(a,b,c,d) > 0 else float("nan")
    ci_lo = float(np.exp(log_or - 1.96*se)) if not np.isnan(se) else float("nan")
    ci_hi = float(np.exp(log_or + 1.96*se)) if not np.isnan(se) else float("nan")
    chi2, p, _, _ = stats.chi2_contingency(np.array([[a,b],[c,d]]))
    return {"or": float(or_val), "p": float(p), "ci_lo": ci_lo, "ci_hi": ci_hi,
            "n": int(len(sub)), "n_neg": int((sub["is_neg"]).sum())}


def main():
    print("=" * 80)
    print("Mediation Analysis: Career Stage as Mediator of Cohort × Decoupling")
    print("=" * 80)

    # Load data + attach text for career-stage classification
    print("\nLoading zeroshot + text + cohort + career stage...")
    zs = load_zeroshot()
    merged = attach_textblob_vader(zs)
    merged["post_id"] = merged["post_id"].astype(str)

    # Re-merge profession + text from source CSVs
    text_frames = []
    for f, text_col, prof_col, id_col in [
        ("reddit_professions_pslf.csv", "combined_text", "profession", "id"),
        ("reddit_arctic_shift_pslf.csv", "combined_text", "profession", "id"),
        ("reddit_new_subs_pslf.csv", "combined_text", "profession", "id"),
        ("comprehensive_medical_pslf_discussions.csv", "combined_text", None, "id"),
        ("comprehensive_teacher_pslf_discussions.csv", "combined_text", None, "id"),
        ("forum_pslf_discussions.csv", "body", None, "post_id"),
    ]:
        if not os.path.exists(f):
            continue
        try:
            cols = ["post_id", "profession", text_col]
            d = pd.read_csv(f, usecols=lambda c: c in (id_col, prof_col, text_col, "thread_title"))
        except Exception:
            continue
        if id_col != "post_id":
            d = d.rename(columns={id_col: "post_id"})
        if prof_col is None:
            if "medical" in f:
                d["profession"] = "medical"
            elif "teacher" in f:
                d["profession"] = "teaching"
            elif "forum" in f:
                d["profession"] = "sdn_medical"
            else:
                d["profession"] = ""
        d["post_id"] = d["post_id"].astype(str)
        # Defensive: build a clean 3-column frame to avoid rename collisions
        out = pd.DataFrame({
            "post_id": d["post_id"].values,
            "profession": d["profession"].astype(str).values,
            "combined_text": d[text_col].astype(str).values
                if text_col in d.columns else "",
        })
        text_frames.append(out)
    texts = pd.concat(text_frames, ignore_index=True).drop_duplicates("post_id")
    df = merged.merge(texts, on="post_id", how="left")
    df["profession"] = df["profession"].fillna("").astype(str)
    df["cohort"] = df["profession"].map(PROF_TO_COHORT).fillna("Other")
    if "source" in df.columns:
        df.loc[df["source"].fillna("").astype(str).str.lower() == "sdn", "cohort"] = "SDN (Medical)"

    df = df.dropna(subset=["pslf_sentiment", "pslf_stance"])
    df = df[~df["pslf_stance"].isin(["unknown", "", None])]
    df = df[df["pslf_sentiment"].isin(["very_negative", "negative", "neutral", "positive", "very_positive"])]
    print(f"  N total: {len(df):,}")

    # Classify career stage
    print("\nClassifying career stage...")
    df["career_stage"] = df["combined_text"].fillna("").apply(classify_career_stage)
    print(df["career_stage"].value_counts().to_string())

    # Filter to non-unknown career stage
    df_career = df[df["career_stage"] != "unknown"].copy()
    print(f"\nWith explicit career stage: {len(df_career):,} ({100*len(df_career)/len(df):.1f}% coverage)")

    # === Mediation analysis ===
    print("\n" + "=" * 80)
    print("[Step 1] Pooled OR per cohort (baseline replication)")
    print("=" * 80)
    pooled_rows = []
    for cohort in ["Reddit r/PSLF", "SDN (Medical)", "Reddit Finance",
                    "Reddit r/StudentLoans", "Reddit Medical"]:
        sub = df[df["cohort"] == cohort]
        res = compute_or(sub)
        if res["n"] >= 100:
            res["cohort"] = cohort
            res["analysis"] = "pooled"
            pooled_rows.append(res)
            print(f"  {cohort:<26s} n={res['n']:>5} OR={res['or']:>5.2f} CI=[{res['ci_lo']:.2f},{res['ci_hi']:.2f}] p={res['p']:.4g}")

    print("\n" + "=" * 80)
    print("[Step 2] OR per (cohort × career stage) cell with adequate n")
    print("=" * 80)
    cell_rows = []
    for cohort in ["Reddit r/PSLF", "SDN (Medical)", "Reddit Finance",
                    "Reddit r/StudentLoans", "Reddit Medical"]:
        for cs in ["resident", "attending", "fellow", "medical_student", "premed"]:
            sub = df_career[(df_career["cohort"] == cohort) & (df_career["career_stage"] == cs)]
            if len(sub) < 30:
                continue
            res = compute_or(sub)
            res["cohort"] = cohort
            res["career_stage"] = cs
            res["analysis"] = "stratified"
            cell_rows.append(res)
            if np.isnan(res["or"]):
                print(f"  {cohort:<26s} x {cs:<18s} n={res['n']:>4} OR=  NA  (zero cell, n_neg={res['n_neg']})")
            else:
                print(f"  {cohort:<26s} x {cs:<18s} n={res['n']:>4} OR={res['or']:>5.2f} "
                      f"CI=[{res['ci_lo']:.2f},{res['ci_hi']:.2f}] p={res['p']:.4g}")

    print("\n" + "=" * 80)
    print("[Step 3] Pure-career-stage OR (cohort-pooled)")
    print("=" * 80)
    cs_rows = []
    for cs in ["resident", "attending", "fellow", "medical_student", "premed"]:
        sub = df_career[df_career["career_stage"] == cs]
        if len(sub) < 30:
            continue
        res = compute_or(sub)
        res["career_stage"] = cs
        res["analysis"] = "career_stage_only"
        cs_rows.append(res)
        if np.isnan(res["or"]):
            print(f"  {cs:<20s} n={res['n']:>4} OR=  NA  (zero cell, n_neg={res['n_neg']})")
        else:
            print(f"  {cs:<20s} n={res['n']:>4} OR={res['or']:>5.2f} "
                  f"CI=[{res['ci_lo']:.2f},{res['ci_hi']:.2f}] p={res['p']:.4g}")

    # Save all
    all_rows = pooled_rows + cell_rows + cs_rows
    df_out = pd.DataFrame(all_rows)
    df_out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Mediation interpretation
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Mediation Analysis: Career Stage as Mediator\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether SDN-Medical's strong decoupling (OR=0.27) is mediated by\n")
        f.write("career stage. If SDN posters skew resident/attending (high stake), and\n")
        f.write("residents have OR=0.27 in BOTH SDN AND r/PSLF, then career stage\n")
        f.write("explains the cohort effect (full mediation).\n\n")

        f.write("STEP 1: Pooled OR per cohort (baseline)\n")
        f.write("-" * 80 + "\n")
        for r in pooled_rows:
            f.write(f"  {r['cohort']:<26s} n={r['n']:>5} OR={r['or']:>5.2f} "
                    f"CI=[{r['ci_lo']:.2f},{r['ci_hi']:.2f}] p={r['p']:.4g}\n")

        f.write("\nSTEP 2: OR per (cohort x career stage) cell\n")
        f.write("-" * 80 + "\n")
        if cell_rows:
            for r in cell_rows:
                if np.isnan(r["or"]):
                    f.write(f"  {r['cohort']:<26s} x {r['career_stage']:<18s} "
                            f"n={r['n']:>4} OR=  NA  (zero cell)\n")
                else:
                    f.write(f"  {r['cohort']:<26s} x {r['career_stage']:<18s} "
                            f"n={r['n']:>4} OR={r['or']:>5.2f} "
                            f"CI=[{r['ci_lo']:.2f},{r['ci_hi']:.2f}] p={r['p']:.4g}\n")
        else:
            f.write("  (no cells met n>=30 threshold)\n")

        f.write("\nSTEP 3: OR per career stage (pooled across cohorts)\n")
        f.write("-" * 80 + "\n")
        for r in cs_rows:
            if np.isnan(r["or"]):
                f.write(f"  {r['career_stage']:<20s} n={r['n']:>4} OR=  NA  (zero cell)\n")
            else:
                f.write(f"  {r['career_stage']:<20s} n={r['n']:>4} OR={r['or']:>5.2f} "
                        f"CI=[{r['ci_lo']:.2f},{r['ci_hi']:.2f}] p={r['p']:.4g}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("Mediation logic:\n")
        f.write("  - If pure-career-stage ORs (Step 3) are similar to cohort-pooled ORs,\n")
        f.write("    career stage is the operative factor (full mediation).\n")
        f.write("  - If SDN × resident OR ≈ Reddit-r/PSLF × resident OR, cohort effect\n")
        f.write("    is fully explained by career stage.\n")
        f.write("  - If cohort × career-stage cells show DIFFERENT ORs by cohort\n")
        f.write("    (e.g., SDN-resident OR=0.3 vs Reddit-resident OR=2.0),\n")
        f.write("    cohort has independent effect beyond career stage (partial mediation).\n\n")

        # Specific test: SDN-resident vs r/PSLF-resident
        sdn_res = next((r for r in cell_rows if r["cohort"] == "SDN (Medical)" and r["career_stage"] == "resident"), None)
        red_res = next((r for r in cell_rows if r["cohort"] == "Reddit r/PSLF" and r["career_stage"] == "resident"), None)
        if sdn_res and red_res and not (np.isnan(sdn_res["or"]) or np.isnan(red_res["or"])):
            f.write(f"  KEY TEST: residents in SDN (OR={sdn_res['or']:.2f}) vs residents in Reddit r/PSLF (OR={red_res['or']:.2f})\n")
            ratio = sdn_res["or"] / red_res["or"] if red_res["or"] > 0 else float("nan")
            f.write(f"    Cohort effect ratio: {ratio:.2f}\n")
            if abs(np.log(sdn_res["or"]) - np.log(red_res["or"])) < 0.5:
                f.write(f"    -> Career stage explains most of cohort difference (full mediation likely)\n")
            else:
                f.write(f"    -> Cohort retains independent effect beyond career stage (partial mediation)\n")
        elif sdn_res and not red_res:
            f.write(f"  KEY TEST: r/PSLF residents below n>=30 threshold; cannot compare directly.\n")
            f.write(f"    SDN residents OR={sdn_res['or']:.2f} (only well-powered cell)\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")


if __name__ == "__main__":
    main()
