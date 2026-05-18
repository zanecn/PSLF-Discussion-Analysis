"""
analyze_topic_per_cohort_per_event.py
=======================================
Tests whether DIFFERENT COHORTS shift to DIFFERENT TOPICS around the same
PSLF policy event. Extends the cohort-heterogeneity finding from a 2D
(cohort × sentiment) interaction to a 3D (cohort × event × topic) one.

Hypothesis: SDN-Medical processes events through career-decision frame
(career_impact, financial_planning) while r/PSLF processes through
servicer/policy frame (servicer_issues, policy_uncertainty). If true,
different cohorts shift to different topics on the same event.

Output: topic_per_cohort_per_event_results.{txt,csv}
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

from sentiment_triangulation import EVENTS, load_zeroshot, attach_textblob_vader

OUT_TXT = "topic_per_cohort_per_event_results.txt"
OUT_CSV = "topic_per_cohort_per_event_results.csv"

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

TOPICS = [
    "servicer_issues", "policy_uncertainty", "financial_planning",
    "career_impact", "success_story", "general_question", "frustration_venting"
]


def cramers_v(ct: np.ndarray) -> float:
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.sum()
    if n == 0:
        return float("nan")
    r, k = ct.shape
    if min(r-1, k-1) == 0:
        return float("nan")
    return float(np.sqrt(chi2 / (n * min(r-1, k-1))))


def main():
    print("=" * 80)
    print("Per-cohort × per-event TOPIC restructuring")
    print("=" * 80)

    print("\nLoading zeroshot data + merging profession from source CSVs...")
    zs = load_zeroshot()
    merged = attach_textblob_vader(zs)
    merged["post_id"] = merged["post_id"].astype(str)

    # Re-merge profession from source CSVs (attach_textblob_vader strips it)
    prof_frames = []
    for f in ["reddit_professions_pslf.csv", "reddit_arctic_shift_pslf.csv",
              "reddit_new_subs_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv"]:
        if not os.path.exists(f):
            continue
        try:
            d = pd.read_csv(f, usecols=lambda c: c in ("id", "post_id", "profession"))
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
        prof_frames.append(d[["post_id", "profession"]])
    profs = pd.concat(prof_frames, ignore_index=True).drop_duplicates("post_id")
    df = merged.merge(profs, on="post_id", how="left")
    df["profession"] = df["profession"].fillna("").astype(str)
    df["cohort"] = df["profession"].map(PROF_TO_COHORT).fillna("Other")
    if "source" in df.columns:
        sdn_mask = df["source"].fillna("").astype(str).str.lower() == "sdn"
        df.loc[sdn_mask, "cohort"] = "SDN (Medical)"

    df = df.dropna(subset=["primary_topic", "date"])
    df = df[~df["primary_topic"].isin(["", "parse_error", "api_error"])]
    print(f"  Posts with topic + date + cohort: {len(df):,}")
    print(f"  Cohort breakdown:")
    for c, n in df["cohort"].value_counts().items():
        print(f"    {c:<26s}  {n:>5,}")

    # For each (event, cohort), compute topic distribution shift
    print("\nComputing per-event × per-cohort topic shifts...")
    rows = []
    for ev_name, ev_date, win in EVENTS:
        dt = pd.Timestamp(ev_date)
        for cohort in sorted(df["cohort"].unique()):
            sub = df[df["cohort"] == cohort]
            pre = sub[(sub["date"] >= dt - pd.Timedelta(days=win)) & (sub["date"] < dt)]
            post = sub[(sub["date"] >= dt) & (sub["date"] <= dt + pd.Timedelta(days=win))]
            n_pre, n_post = len(pre), len(post)
            if n_pre < 20 or n_post < 20:
                continue
            # Build contingency table on the 7 canonical topics
            present_topics = sorted(set(pre["primary_topic"]) | set(post["primary_topic"]))
            ct = np.zeros((2, len(present_topics)), dtype=int)
            for j, t in enumerate(present_topics):
                ct[0, j] = (pre["primary_topic"] == t).sum()
                ct[1, j] = (post["primary_topic"] == t).sum()
            # Drop columns where both rows are zero
            keep = ct.sum(axis=0) > 0
            ct = ct[:, keep]
            present_topics = [t for t, k in zip(present_topics, keep) if k]
            if ct.shape[1] < 2:
                continue
            v = cramers_v(ct)
            chi2_stat, chi2_p, _, _ = stats.chi2_contingency(ct)
            # Per-topic deltas
            topic_pcts_pre = ct[0] / max(ct[0].sum(), 1) * 100
            topic_pcts_post = ct[1] / max(ct[1].sum(), 1) * 100
            deltas = topic_pcts_post - topic_pcts_pre
            # Top 3 absolute-magnitude deltas
            top_idx = np.argsort(np.abs(deltas))[::-1][:3]
            top_shifts = [(present_topics[i], float(deltas[i])) for i in top_idx]
            rows.append({
                "event": ev_name,
                "cohort": cohort,
                "n_pre": n_pre,
                "n_post": n_post,
                "cramers_v": v,
                "chi2_p": chi2_p,
                "top_shift_1": f"{top_shifts[0][0]}: {top_shifts[0][1]:+.1f}pp" if len(top_shifts) > 0 else "",
                "top_shift_2": f"{top_shifts[1][0]}: {top_shifts[1][1]:+.1f}pp" if len(top_shifts) > 1 else "",
                "top_shift_3": f"{top_shifts[2][0]}: {top_shifts[2][1]:+.1f}pp" if len(top_shifts) > 2 else "",
                # Per-topic deltas (as separate columns)
                **{f"delta_{t}": float(deltas[i]) for i, t in enumerate(present_topics)},
            })
    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # === Test the headline hypothesis: do different cohorts shift to different topics? ===
    print("\nHEADLINE TEST: do cohorts shift to different topics on the same event?")
    headline_rows = []
    for ev_name, _, _ in EVENTS:
        sub = out[out["event"] == ev_name]
        if len(sub) < 2:
            continue
        # For each topic, get the per-cohort delta vector
        for topic in TOPICS:
            col = f"delta_{topic}"
            if col not in sub.columns:
                continue
            deltas = sub[[col, "cohort"]].dropna()
            if len(deltas) < 2:
                continue
            # Standard deviation of deltas across cohorts (high = cohorts disagree on topic)
            sd_across_cohorts = float(deltas[col].std())
            range_across_cohorts = float(deltas[col].max() - deltas[col].min())
            headline_rows.append({
                "event": ev_name, "topic": topic,
                "n_cohorts": len(deltas),
                "sd_across_cohorts": sd_across_cohorts,
                "range_across_cohorts": range_across_cohorts,
                "max_cohort": deltas.loc[deltas[col].idxmax(), "cohort"],
                "max_delta": float(deltas[col].max()),
                "min_cohort": deltas.loc[deltas[col].idxmin(), "cohort"],
                "min_delta": float(deltas[col].min()),
            })
    headline = pd.DataFrame(headline_rows)
    # Largest cohort-disagreement on topic shift per event
    headline = headline.sort_values("range_across_cohorts", ascending=False)

    # Write report
    print(f"\nWriting {OUT_TXT}...")
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Per-cohort × per-event TOPIC restructuring\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether different cohorts shift to different TOPICS around the same\n")
        f.write("PSLF policy event. Extends cohort-heterogeneity from sentiment-only to\n")
        f.write("multi-dimensional cohort × event × topic interaction.\n\n")

        f.write("PER-EVENT × PER-COHORT TOPIC SHIFTS (cells with n_pre AND n_post >= 20)\n")
        f.write("-" * 80 + "\n")
        for ev_name, _, _ in EVENTS:
            sub = out[out["event"] == ev_name].sort_values("cramers_v", ascending=False)
            if len(sub) == 0:
                continue
            f.write(f"\n{ev_name}:\n")
            f.write(f"  {'cohort':<26s} {'n_pre':>6s} {'n_post':>6s} {'V':>5s} {'p':>9s}  Top topic shifts\n")
            for _, r in sub.iterrows():
                shifts = [s for s in [r["top_shift_1"], r["top_shift_2"], r["top_shift_3"]] if s]
                f.write(f"  {r['cohort']:<26s} {int(r['n_pre']):>6d} {int(r['n_post']):>6d} "
                        f"{r['cramers_v']:>5.3f} {r['chi2_p']:>9.4g}  {' | '.join(shifts)}\n")

        f.write("\n\nLARGEST COHORT-DISAGREEMENT ON TOPIC SHIFT (per event × topic)\n")
        f.write("-" * 80 + "\n")
        f.write("Tests headline hypothesis: do cohorts shift to different topics on same event?\n")
        f.write("Higher 'range across cohorts' = cohorts shift to OPPOSITE topic directions.\n\n")
        f.write(f"{'event':<28s} {'topic':<22s} {'range':>6s} {'max_cohort':<26s} {'max_Δ':>7s} "
                f"{'min_cohort':<26s} {'min_Δ':>7s}\n")
        for _, r in headline.head(30).iterrows():
            f.write(f"{r['event']:<28s} {r['topic']:<22s} {r['range_across_cohorts']:>6.1f} "
                    f"{r['max_cohort']:<26s} {r['max_delta']:>+7.1f} "
                    f"{r['min_cohort']:<26s} {r['min_delta']:>+7.1f}\n")

        # Cleanest cohort-divergence cells (where cohorts move in OPPOSITE directions)
        f.write("\n\nCOHORT-OPPOSITE-DIRECTION TOPIC SHIFTS (max > +5pp AND min < -5pp on same event×topic)\n")
        f.write("-" * 80 + "\n")
        opposite = headline[(headline["max_delta"] > 5) & (headline["min_delta"] < -5)]
        for _, r in opposite.iterrows():
            f.write(f"  {r['event']:<28s} {r['topic']:<22s}: "
                    f"{r['max_cohort']} +{r['max_delta']:.1f}pp vs "
                    f"{r['min_cohort']} {r['min_delta']:.1f}pp\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")

    print("\nTop 10 cohort-disagreement-on-topic-shift cells:")
    print(headline.head(10)[["event", "topic", "range_across_cohorts",
                              "max_cohort", "max_delta", "min_cohort", "min_delta"]].to_string(index=False))


if __name__ == "__main__":
    main()
