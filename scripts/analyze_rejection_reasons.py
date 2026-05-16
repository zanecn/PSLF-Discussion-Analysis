"""
analyze_rejection_reasons.py
==============================
Analyzes rejection_reason classifications (from extract_rejection_reasons.py)
by cohort × event × original sentiment. Tests:

  1. Does SDN-Medical's high rejection rate (24%) reflect distinct REASONS
     (e.g., employer_mismatch / job_change due to residency) compared to
     other cohorts (which might cite alternative_strategy / servicer_distrust)?
  2. Do specific events trigger specific rejection reasons?
     (e.g., does Trump EO trigger forbearance_fatigue + servicer_distrust spike?
      does IDR Adjustment trigger cost_complexity spike?)
  3. Cross-classify by sentiment: are very_negative posts more likely to cite
     servicer_distrust while neutral are more likely to cite alternative_strategy?

Runs when rejection_reasons.csv lands.

Output: rejection_reason_analysis_results.{txt,csv}
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

from sentiment_triangulation import EVENTS, load_zeroshot

OUT_TXT = "rejection_reason_analysis_results.txt"
OUT_CSV = "rejection_reason_analysis_results.csv"

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

CATEGORIES = [
    "cost_complexity", "employer_mismatch", "job_change",
    "forbearance_fatigue", "timeline_too_long", "servicer_distrust",
    "alternative_strategy", "other", "no_reason_given"
]


def main():
    if not os.path.exists("rejection_reasons.csv"):
        print("[WAIT] rejection_reasons.csv not yet on disk.")
        print("       Run extract_rejection_reasons.py first.")
        sys.exit(0)

    print("=" * 80)
    print("Rejection-reason cross-classification analysis")
    print("=" * 80)

    print("\nLoading rejection_reasons.csv...")
    rr = pd.read_csv("rejection_reasons.csv")
    rr = rr[~rr["rejection_reason"].isin(["parse_error", ""])].copy()
    rr["post_id"] = rr["post_id"].astype(str)
    print(f"  Classified posts: {len(rr):,}")
    print(f"  Marginal distribution:")
    for cat, n in rr["rejection_reason"].value_counts().items():
        print(f"    {cat:<25s} {n:>5,} ({100*n/len(rr):.1f}%)")

    # Load Claude data + merge with profession + dates
    print("\nLoading zeroshot + merging cohort + dates...")
    zs = load_zeroshot()
    zs["post_id"] = zs["post_id"].astype(str)

    # Profession from source CSVs (not in zeroshot for SDN)
    prof_frames = []
    for f in ["reddit_professions_pslf.csv", "reddit_arctic_shift_pslf.csv",
              "reddit_new_subs_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv"]:
        if not os.path.exists(f):
            continue
        try:
            d = pd.read_csv(f, usecols=lambda c: c in ("id", "post_id", "profession", "created_utc"))
        except Exception:
            continue
        if "id" in d.columns and "post_id" not in d.columns:
            d = d.rename(columns={"id": "post_id"})
        if "profession" not in d.columns:
            if "medical" in f:
                d["profession"] = "medical"
            elif "teacher" in f:
                d["profession"] = "teaching"
            else:
                continue
        d["post_id"] = d["post_id"].astype(str)
        if "created_utc" in d.columns:
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        prof_frames.append(d[["post_id", "profession", "date"]])
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv", usecols=lambda c: c in ("post_id", "date_posted"))
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        d["profession"] = "sdn_medical"
        d["post_id"] = d["post_id"].astype(str)
        prof_frames.append(d[["post_id", "profession", "date"]])
    profs = pd.concat(prof_frames, ignore_index=True).drop_duplicates("post_id")

    # Merge: rr → profession → cohort + date + sentiment
    rr = rr.merge(profs, on="post_id", how="left")
    rr = rr.merge(zs[["post_id", "pslf_sentiment", "source"]], on="post_id", how="left")
    rr["profession"] = rr["profession"].fillna("").astype(str)
    rr["cohort"] = rr["profession"].map(PROF_TO_COHORT).fillna("Other")
    if "source" in rr.columns:
        sdn_mask = rr["source"].fillna("").astype(str).str.lower() == "sdn"
        rr.loc[sdn_mask, "cohort"] = "SDN (Medical)"

    print(f"  Merged: {len(rr):,} rejecting posts with reason + cohort + (date + sentiment when available)")

    # === Cross-tab 1: cohort × rejection_reason ===
    print("\n[1] Cohort × rejection_reason cross-tab...")
    ct1 = pd.crosstab(rr["cohort"], rr["rejection_reason"], normalize="index") * 100
    ct1_n = pd.crosstab(rr["cohort"], rr["rejection_reason"])
    print(ct1.round(1).to_string())

    # === Cross-tab 2: event × rejection_reason ===
    print("\n[2] Event × rejection_reason cross-tab...")
    rr_with_date = rr.dropna(subset=["date"])
    rr_with_date["date"] = pd.to_datetime(rr_with_date["date"], utc=True, errors="coerce").dt.tz_localize(None)
    event_assignments = []
    for _, row in rr_with_date.iterrows():
        for ev_name, ev_date, win in EVENTS:
            dt = pd.Timestamp(ev_date)
            if dt - pd.Timedelta(days=win) <= row["date"] <= dt + pd.Timedelta(days=win):
                event_assignments.append({
                    "post_id": row["post_id"],
                    "rejection_reason": row["rejection_reason"],
                    "cohort": row["cohort"],
                    "event": ev_name,
                })
    ev_df = pd.DataFrame(event_assignments)
    if len(ev_df):
        ct2 = pd.crosstab(ev_df["event"], ev_df["rejection_reason"], normalize="index") * 100
        ct2_n = pd.crosstab(ev_df["event"], ev_df["rejection_reason"])
        print(ct2.round(1).to_string())
    else:
        ct2 = pd.DataFrame()
        ct2_n = pd.DataFrame()

    # === Cross-tab 3: sentiment × rejection_reason ===
    print("\n[3] Sentiment × rejection_reason cross-tab...")
    rr_with_sent = rr.dropna(subset=["pslf_sentiment"])
    rr_with_sent = rr_with_sent[rr_with_sent["pslf_sentiment"].isin(
        ["very_negative", "negative", "neutral", "positive", "very_positive"])]
    if len(rr_with_sent):
        ct3 = pd.crosstab(rr_with_sent["pslf_sentiment"], rr_with_sent["rejection_reason"], normalize="index") * 100
        ct3_n = pd.crosstab(rr_with_sent["pslf_sentiment"], rr_with_sent["rejection_reason"])
        print(ct3.round(1).to_string())

    # Write report
    print(f"\nWriting {OUT_TXT}...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Rejection-reason analysis\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total rejecting posts with reason: {len(rr):,}\n\n")

        f.write("MARGINAL REJECTION REASON DISTRIBUTION\n")
        f.write("-" * 80 + "\n")
        for cat, n in rr["rejection_reason"].value_counts().items():
            f.write(f"  {cat:<25s} {n:>5,} ({100*n/len(rr):.1f}%)\n")

        f.write("\n[1] COHORT × REJECTION REASON (% within cohort row)\n")
        f.write("-" * 80 + "\n")
        f.write(ct1.round(1).to_string())
        f.write("\n\nN counts:\n")
        f.write(ct1_n.to_string())

        f.write("\n\n[2] EVENT × REJECTION REASON (% within event row)\n")
        f.write("-" * 80 + "\n")
        if len(ct2):
            f.write(ct2.round(1).to_string())
            f.write("\n\nN counts:\n")
            f.write(ct2_n.to_string())
        else:
            f.write("  (no event-window cells with adequate n)\n")

        f.write("\n\n[3] SENTIMENT × REJECTION REASON (% within sentiment row)\n")
        f.write("-" * 80 + "\n")
        if len(rr_with_sent):
            f.write(ct3.round(1).to_string())
            f.write("\n\nN counts:\n")
            f.write(ct3_n.to_string())

        # Substantive interpretation hooks
        f.write("\n\nINTERPRETATION HOOKS\n")
        f.write("-" * 80 + "\n")
        f.write("Look for:\n")
        f.write("  - Cohort distinctiveness: which reasons are over/under-represented in SDN?\n")
        f.write("  - Event triggers: does Trump EO trigger forbearance_fatigue spike?\n")
        f.write("  - Sentiment-reason mapping: is servicer_distrust concentrated in very_negative?\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {OUT_TXT}")
    rr.to_csv(OUT_CSV, index=False)
    print(f"Saved: {OUT_CSV}")


if __name__ == "__main__":
    main()
