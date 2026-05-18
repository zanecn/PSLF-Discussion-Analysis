"""
analyze_c1_threshold_sensitivity.py
=====================================
C1 follow-up: test sensitivity of time-to-recovery findings to the ±X threshold.

Original used ±0.02. Test ±0.005, ±0.01, ±0.02, ±0.05, ±0.10.

Output: c1_threshold_sensitivity.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd

OUT_TXT = "c1_threshold_sensitivity.txt"
OUT_CSV = "c1_threshold_sensitivity.csv"

SUBREDDIT_TO_COHORT = {
    "PSLF": "Reddit r/PSLF",
    "StudentLoans": "Reddit r/StudentLoans",
    "personalfinance": "Reddit Finance",
    "financialindependence": "Reddit Finance",
    "medicalschool": "Reddit Medical",
    "medicine": "Reddit Medical",
    "Residency": "Reddit Medical",
    "physicianassistant": "Reddit PA",
    "PAstudent": "Reddit PA",
    "prephysicianassistant": "Reddit PA",
    "nursing": "Reddit Nursing",
    "CRNA": "Reddit Nursing",
    "Teachers": "Reddit Teaching",
    "Teaching": "Reddit Teaching",
    "lawschool": "Reddit Law",
    "pharmacy": "Reddit Pharmacy",
    "OccupationalTherapy": "Reddit OT",
    "slp": "Reddit SLP",
}


def main():
    df = pd.read_csv("reddit_comments_pslf.csv",
                       usecols=["post_subreddit", "created_datetime",
                                "polarity", "word_count"], low_memory=False)
    df = df.dropna(subset=["polarity", "created_datetime"])
    df["created_datetime"] = pd.to_datetime(df["created_datetime"], errors="coerce", utc=True)
    df = df.dropna(subset=["created_datetime"])
    df["date"] = df["created_datetime"].dt.tz_convert(None).dt.normalize()
    df = df[df["word_count"] >= 5]
    df["cohort"] = df["post_subreddit"].map(SUBREDDIT_TO_COHORT).fillna("Other")
    print(f"Comments after filter: {len(df):,}")

    cohorts = ["Reddit r/PSLF", "Reddit r/StudentLoans", "Reddit Finance",
                "Reddit Medical", "Reddit PA"]
    ev_date = pd.to_datetime("2025-03-07")  # Trump PSLF EO
    thresholds = [0.005, 0.01, 0.02, 0.05, 0.10]

    rows = []
    print("\nTime-to-recovery (Trump PSLF EO, 7-day rolling, multiple thresholds)")
    print(f"{'cohort':<22s} {'pre_mean':>10s} {'post30':>10s} "
           f"{'thr=0.005':>11s} {'0.01':>6s} {'0.02':>6s} {'0.05':>6s} {'0.10':>6s}")
    for c in cohorts:
        sub = df[df["cohort"] == c].copy()
        if len(sub) < 200: continue
        pre_window = sub[(sub["date"] >= ev_date - pd.Timedelta(days=90)) &
                          (sub["date"] < ev_date)]
        post = sub[(sub["date"] >= ev_date) &
                    (sub["date"] < ev_date + pd.Timedelta(days=90))].copy()
        if len(pre_window) < 30 or len(post) < 30: continue
        pre_mean = pre_window["polarity"].mean()
        post30 = post[post["date"] < ev_date + pd.Timedelta(days=30)]["polarity"].mean()

        daily = post.groupby("date")["polarity"].agg(["mean", "count"]).reset_index()
        daily = daily[daily["count"] >= 5]
        daily["rolling7"] = daily["mean"].rolling(7, min_periods=3).mean()

        recovery_days = {}
        for t in thresholds:
            recovered = daily[abs(daily["rolling7"] - pre_mean) < t]
            recovery_days[t] = (int((recovered["date"].iloc[0] - ev_date).days)
                                  if len(recovered) > 0 else -1)

        row = {
            "cohort": c, "pre_mean": pre_mean, "post30_mean": post30,
        }
        for t in thresholds:
            row[f"recover_thr_{t}"] = recovery_days[t]
        rows.append(row)
        cells = [f"{recovery_days[t]:>5}d" if recovery_days[t] >= 0 else " >90d" for t in thresholds]
        print(f"{c:<22s} {pre_mean:>+10.4f} {post30:>+10.4f}  {cells[0]:>10s} "
               f"{cells[1]:>6s} {cells[2]:>6s} {cells[3]:>6s} {cells[4]:>6s}")

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("C1 TIME-TO-RECOVERY THRESHOLD SENSITIVITY\n")
        f.write("=" * 80 + "\n\n")
        f.write("Original C1 used threshold ±0.02 of pre-event mean.\n")
        f.write("Sensitivity analysis: ±0.005, 0.01, 0.02, 0.05, 0.10.\n\n")
        f.write(f"{'cohort':<22s} {'pre':>10s} {'post30':>10s} {'rec.005':>9s} "
                f"{'rec.01':>8s} {'rec.02':>8s} {'rec.05':>8s} {'rec.10':>8s}\n")
        for r in rows:
            cells = []
            for t in thresholds:
                v = r[f"recover_thr_{t}"]
                cells.append(f"{v:>5}d" if v >= 0 else " >90d ")
            f.write(f"{r['cohort']:<22s} {r['pre_mean']:>+10.4f} {r['post30_mean']:>+10.4f} "
                    f"{cells[0]:>9s} {cells[1]:>8s} {cells[2]:>8s} {cells[3]:>8s} {cells[4]:>8s}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        # For each cohort, compute consistency
        for r in rows:
            recovery_pattern = [(t, r[f"recover_thr_{t}"]) for t in thresholds]
            n_no_recovery = sum(1 for _, d in recovery_pattern if d < 0)
            f.write(f"  {r['cohort']:<22s}: ")
            if n_no_recovery >= 4:
                f.write("NO recovery at any reasonable threshold (sustained shift)\n")
            elif n_no_recovery == 0:
                f.write("Recovers at ALL thresholds (immediate revert)\n")
            else:
                f.write(f"Threshold-sensitive — partial recovery in {5-n_no_recovery} of 5 thresholds\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")


if __name__ == "__main__":
    main()
