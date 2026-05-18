"""
analyze_time_to_recovery.py
=============================
For each (event, cohort), measures how long after the event the cohort's
sentiment returns to its pre-event baseline. Tests whether cohorts have
different temporal "stickiness" — does SDN's reaction persist longer
(stake-driven sustained attention) or shrink faster than Reddit?

Method:
  1. For each (event, cohort), compute baseline = mean(polarity) in [-90d, 0d]
  2. Compute 14-day rolling mean polarity from event date onward
  3. Find first day t where rolling mean returns to within 0.5 SD of baseline
  4. Report t (days to recovery), with right-censoring at +180d

Output: time_to_recovery_results.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings
from datetime import datetime
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from sentiment_triangulation import EVENTS
from pslf_search_terms import filter_pslf_relevant

OUT_TXT = "time_to_recovery_results.txt"
OUT_CSV = "time_to_recovery_results.csv"

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

LOOKAHEAD_DAYS = 180  # right-censor recovery time at this many days
ROLLING_DAYS = 14
RECOVERY_TOL_SD = 0.5  # within 0.5 SD of baseline = "recovered"


def load_corpus():
    frames = []
    needed = ["date", "polarity", "profession", "word_count"]

    def _slim(d, prof_default=None, text_col=None):
        if "profession" not in d.columns and prof_default:
            d["profession"] = prof_default
        if "word_count" not in d.columns:
            d["word_count"] = (d[text_col].fillna("").str.split().str.len()
                                if text_col else 100)
        return d[needed]

    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teaching")]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
            d["profession"] = prof
            tcol = ("combined_text" if "combined_text" in d.columns
                    else "selftext" if "selftext" in d.columns else None)
            frames.append(_slim(d, text_col=tcol))
    if os.path.exists("reddit_professions_pslf.csv"):
        d = pd.read_csv("reddit_professions_pslf.csv")
        tm = filter_pslf_relevant(d["combined_text"].fillna(""))
        tt = filter_pslf_relevant(d["title"].fillna(""))
        d = d[tm | tt].copy()
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        frames.append(_slim(d, text_col="combined_text" if "combined_text" in d.columns else ("body" if "body" in d.columns else None)))
    if os.path.exists("reddit_arctic_shift_pslf.csv"):
        d = pd.read_csv("reddit_arctic_shift_pslf.csv")
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        frames.append(_slim(d, text_col="combined_text" if "combined_text" in d.columns else ("body" if "body" in d.columns else None)))
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        bm = filter_pslf_relevant(d["body"].fillna(""))
        ttm = filter_pslf_relevant(d["thread_title"].fillna(""))
        d = d[bm | ttm].copy()
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        d["profession"] = "sdn_medical"
        frames.append(_slim(d, text_col="combined_text" if "combined_text" in d.columns else ("body" if "body" in d.columns else None)))
    big = pd.concat(frames, ignore_index=True)
    big = big.dropna(subset=["date", "polarity"])
    big = big[big["word_count"].fillna(0) >= 20]
    big["date"] = pd.to_datetime(big["date"], utc=True, errors="coerce").dt.tz_localize(None)
    big["cohort"] = big["profession"].map(PROF_TO_COHORT).fillna("Other")
    if "sdn_medical" in PROF_TO_COHORT:
        pass
    big.loc[big["profession"] == "sdn_medical", "cohort"] = "SDN (Medical)"
    return big


def find_recovery_day(daily_post: pd.Series, baseline: float, baseline_sd: float,
                      tol_sd: float = 0.5, max_days: int = 180) -> int | None:
    """daily_post: rolling mean indexed by day-from-event. Returns first day
    where rolling mean is within tol_sd*baseline_sd of baseline. None if never."""
    if baseline_sd <= 0:
        baseline_sd = 0.05  # avoid division by zero
    band_lo = baseline - tol_sd * baseline_sd
    band_hi = baseline + tol_sd * baseline_sd
    for day, val in daily_post.items():
        if pd.isna(val):
            continue
        if band_lo <= val <= band_hi:
            return int(day)
    return None


def main():
    print("=" * 80)
    print("Time-to-recovery analysis: per-event × per-cohort")
    print("=" * 80)

    df = load_corpus()
    print(f"  Total docs: {len(df):,}")
    print(f"  Cohorts:")
    for c, n in df["cohort"].value_counts().items():
        print(f"    {c:<26s}  {n:>6,}")

    # Restrict to cohorts with enough data
    cohorts = ["SDN (Medical)", "Reddit r/PSLF", "Reddit r/StudentLoans",
               "Reddit Finance", "Reddit Medical"]

    print("\nComputing recovery times...")
    rows = []
    for ev_name, ev_date, win in EVENTS:
        dt = pd.Timestamp(ev_date)
        for cohort in cohorts:
            sub = df[df["cohort"] == cohort]
            # Baseline: 90 days pre-event
            baseline_window = sub[(sub["date"] >= dt - pd.Timedelta(days=90)) &
                                   (sub["date"] < dt)]
            if len(baseline_window) < 30:
                continue
            baseline_mean = float(baseline_window["polarity"].mean())
            baseline_sd = float(baseline_window["polarity"].std())

            # Post-event: up to LOOKAHEAD_DAYS
            post = sub[(sub["date"] >= dt) &
                       (sub["date"] <= dt + pd.Timedelta(days=LOOKAHEAD_DAYS))]
            if len(post) < 30:
                continue
            post = post.copy()
            post["day_from_event"] = (post["date"] - dt).dt.days
            # 14-day rolling mean of polarity, indexed by day
            daily = post.groupby("day_from_event")["polarity"].agg(["mean", "count"]).reset_index()
            # Require at least 3 posts/day
            daily.loc[daily["count"] < 3, "mean"] = np.nan
            daily = daily.set_index("day_from_event")["mean"]
            daily = daily.reindex(range(0, LOOKAHEAD_DAYS + 1))
            rolling = daily.rolling(ROLLING_DAYS, center=False, min_periods=3).mean()

            # Initial shock magnitude
            initial = post[post["day_from_event"] <= 14]["polarity"].mean()
            shift_magnitude = initial - baseline_mean if not pd.isna(initial) else float("nan")

            # Recovery day
            recovery_day = find_recovery_day(rolling, baseline_mean, baseline_sd,
                                              tol_sd=RECOVERY_TOL_SD,
                                              max_days=LOOKAHEAD_DAYS)

            rows.append({
                "event": ev_name,
                "cohort": cohort,
                "baseline_mean": baseline_mean,
                "baseline_sd": baseline_sd,
                "n_baseline": len(baseline_window),
                "initial_post_mean": float(initial) if not pd.isna(initial) else float("nan"),
                "shift_magnitude": shift_magnitude,
                "recovery_day": recovery_day if recovery_day is not None else -1,  # -1 = censored
                "censored": recovery_day is None,
                "n_post": len(post),
            })
    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # === Compare recovery times across cohorts per event ===
    print("\nWriting report...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Time-to-recovery: per-event × per-cohort\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("For each (event, cohort), measures how many days after the event the\n")
        f.write(f"cohort's {ROLLING_DAYS}-day rolling polarity returns to within "
                f"{RECOVERY_TOL_SD} SD of\n")
        f.write(f"the pre-event baseline. Right-censored at {LOOKAHEAD_DAYS} days.\n\n")
        f.write("Recovery_day = -1 means the cohort did NOT return to baseline within\n")
        f.write("the observation window (right-censored).\n\n")

        f.write("PER-EVENT COMPARISON\n")
        f.write("-" * 80 + "\n")
        for ev_name, _, _ in EVENTS:
            sub = out[out["event"] == ev_name].sort_values("recovery_day", ascending=True)
            if len(sub) == 0:
                continue
            f.write(f"\n{ev_name}:\n")
            f.write(f"  {'cohort':<26s} {'baseline':>9s} {'shift':>7s} {'recovery':>10s} {'n_post':>7s}\n")
            for _, r in sub.iterrows():
                rec_str = "censored" if r["recovery_day"] == -1 else f"{int(r['recovery_day'])}d"
                f.write(f"  {r['cohort']:<26s} {r['baseline_mean']:>+9.4f} "
                        f"{r['shift_magnitude']:>+7.4f} {rec_str:>10s} {int(r['n_post']):>7d}\n")

        f.write("\n\nSUMMARY: Median recovery day per cohort (across events with non-censored recovery)\n")
        f.write("-" * 80 + "\n")
        for cohort in cohorts:
            sub = out[(out["cohort"] == cohort) & (out["censored"] == False)]
            if len(sub) == 0:
                f.write(f"  {cohort:<26s}: all events censored (no recovery observed within {LOOKAHEAD_DAYS}d)\n")
                continue
            f.write(f"  {cohort:<26s}: median {int(sub['recovery_day'].median())}d, "
                    f"range {int(sub['recovery_day'].min())}-{int(sub['recovery_day'].max())}d, "
                    f"{int((sub['censored'] == False).sum())}/{int(len(out[out['cohort']==cohort]))} events recovered\n")

        f.write("\n\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("- Shorter recovery time = sentiment shock dissipates faster\n")
        f.write("- Longer recovery time / censored = persistent attention to event\n")
        f.write("- If SDN-Medical recovery times > Reddit-general: stake-driven persistence\n")
        f.write("- If SDN-Medical recovery times < Reddit-general: analytical-quick-update\n")
        f.write("- 'censored' = sentiment never returned to baseline in 180-day window\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")

    # Console summary
    print("\nMedian recovery day by cohort (non-censored events only):")
    for cohort in cohorts:
        sub = out[(out["cohort"] == cohort) & (out["censored"] == False)]
        if len(sub):
            print(f"  {cohort:<26s}: median {int(sub['recovery_day'].median())}d, "
                  f"{len(sub)}/{len(out[out['cohort']==cohort])} events recovered")
        else:
            print(f"  {cohort:<26s}: all events censored")


if __name__ == "__main__":
    main()
