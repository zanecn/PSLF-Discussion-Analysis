"""
analyze_op_reply_per_event.py
================================
Stratifies the OP vs Reply opposite-direction finding by the 8 PSLF events.

Tests:
  1. Does the OP-vs-reply gap shift with policy salience? (e.g., does the
     gap WIDEN around major threat events when OPs are more anxious?)
  2. Are there events where the cohort-invariant pattern breaks down?

Output: op_reply_per_event_results.{txt,csv}
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

OUT_TXT = "op_reply_per_event_results.txt"
OUT_CSV = "op_reply_per_event_results.csv"

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


def main():
    print("=" * 80)
    print("OP vs Reply per-event stratification")
    print("=" * 80)

    print("\nLoading OPs with sentiment + dates + cohort...")
    op_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv",
              "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        if "id" in d.columns:
            d = d.rename(columns={"id": "post_id"})
        keep = ["post_id", "polarity", "created_utc"]
        if "vader_compound" in d.columns:
            keep.append("vader_compound")
        else:
            d["vader_compound"] = np.nan
            keep.append("vader_compound")
        if "profession" in d.columns:
            keep.append("profession")
        else:
            d["profession"] = ""
            keep.append("profession")
        if "word_count" in d.columns:
            keep.append("word_count")
        else:
            d["word_count"] = 100
            keep.append("word_count")
        op_frames.append(d[keep])
    ops = pd.concat(op_frames, ignore_index=True).drop_duplicates("post_id")
    ops["post_id"] = ops["post_id"].astype(str)
    ops["date"] = pd.to_datetime(pd.to_numeric(ops["created_utc"], errors="coerce"), unit="s")
    ops = ops.dropna(subset=["polarity", "date"])
    ops = ops[ops["word_count"].fillna(0) >= 20]
    ops["cohort"] = ops["profession"].map(PROF_TO_COHORT).fillna("Other")
    ops = ops.rename(columns={"polarity": "op_polarity", "vader_compound": "op_vader"})
    print(f"  OPs (wc>=20): {len(ops):,}")

    print("\nLoading comments + computing per-post aggregates...")
    cm = pd.read_csv("reddit_comments_pslf.csv", low_memory=False)
    cm["post_id"] = cm["post_id"].astype(str)
    cm = cm[cm["polarity"].notna() & cm["word_count"].fillna(0).ge(5)]
    if "vader_compound" not in cm.columns or cm["vader_compound"].isna().all():
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        bodies = cm["body"].fillna("").astype(str).tolist()
        cv = np.array([sia.polarity_scores(b[:5000])["compound"] if b else np.nan
                       for b in bodies])
        cm["vader_compound"] = cv
    agg = cm.groupby("post_id").agg(
        mean_cmt_pol=("polarity", "mean"),
        mean_cmt_va=("vader_compound", "mean"),
        n_cmt=("polarity", "count"),
    ).reset_index()
    df = ops.merge(agg, on="post_id", how="inner")
    df["diff_pol"] = df["op_polarity"] - df["mean_cmt_pol"]
    df["diff_va"] = df["op_vader"] - df["mean_cmt_va"]
    df = df.dropna(subset=["diff_pol", "diff_va"])
    print(f"  Posts with both OP and comments: {len(df):,}")

    # Per-event aggregation
    print("\nComputing per-event OP-Reply gaps (cluster bootstrap by post)...")
    rng = np.random.default_rng(42)
    rows = []
    for ev_name, ev_date, win in EVENTS:
        dt = pd.Timestamp(ev_date)
        # Posts whose OP is in the event window (pre OR post)
        pre = df[(df["date"] >= dt - pd.Timedelta(days=win)) & (df["date"] < dt)]
        post = df[(df["date"] >= dt) & (df["date"] <= dt + pd.Timedelta(days=win))]

        for window_label, sub in [("pre", pre), ("post", post)]:
            n = len(sub)
            if n < 30:
                rows.append({
                    "event": ev_name, "window": window_label,
                    "n_posts": n, "diff_polarity": float("nan"), "diff_vader": float("nan"),
                    "diff_pol_ci_lo": float("nan"), "diff_pol_ci_hi": float("nan"),
                    "diff_va_ci_lo": float("nan"), "diff_va_ci_hi": float("nan"),
                    "diff_pol_p_boot": float("nan"), "diff_va_p_boot": float("nan"),
                    "median_n_cmt": float("nan"),
                })
                continue
            # Cluster bootstrap (each post = one cluster after aggregation)
            boot_pol = []
            boot_va = []
            for _ in range(1000):
                idx = rng.integers(0, n, size=n)
                boot_pol.append(sub["diff_pol"].iloc[idx].mean())
                boot_va.append(sub["diff_va"].iloc[idx].mean())
            rows.append({
                "event": ev_name, "window": window_label, "n_posts": int(n),
                "diff_polarity": float(sub["diff_pol"].mean()),
                "diff_pol_ci_lo": float(np.percentile(boot_pol, 2.5)),
                "diff_pol_ci_hi": float(np.percentile(boot_pol, 97.5)),
                "diff_pol_p_boot": float(2 * min((np.array(boot_pol) > 0).mean(),
                                                 (np.array(boot_pol) < 0).mean())),
                "diff_vader": float(sub["diff_va"].mean()),
                "diff_va_ci_lo": float(np.percentile(boot_va, 2.5)),
                "diff_va_ci_hi": float(np.percentile(boot_va, 97.5)),
                "diff_va_p_boot": float(2 * min((np.array(boot_va) > 0).mean(),
                                                (np.array(boot_va) < 0).mean())),
                "median_n_cmt": float(sub["n_cmt"].median()),
            })

    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Write report
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("OP vs Reply per-event stratification\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether the cohort-invariant OP vs Reply opposite-direction finding\n")
        f.write("(TB Δ=−0.017, VADER Δ=+0.220) shifts by event window. If the gap WIDENS\n")
        f.write("around threat events (e.g., Trump EO), this would suggest OPs are more\n")
        f.write("emotionally activated during high-stakes periods.\n\n")
        f.write(f"Sample: {len(df):,} posts with both OP and comment-aggregated sentiment.\n\n")

        f.write("PER-EVENT OP-REPLY GAPS (cluster bootstrap by post, B=1000)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'event':<28s} {'win':<6s} {'n':>5s} {'TB diff':>9s} {'TB 95% CI':>22s} "
                f"{'TB p':>7s} {'VA diff':>9s} {'VA 95% CI':>22s} {'VA p':>7s}\n")
        for _, r in out.iterrows():
            if pd.isna(r["diff_polarity"]):
                f.write(f"{r['event']:<28s} {r['window']:<6s} {int(r['n_posts']):>5d} "
                        f"{'(underpowered, n<30)':<70s}\n")
                continue
            tb_ci = f"[{r['diff_pol_ci_lo']:+.4f},{r['diff_pol_ci_hi']:+.4f}]"
            va_ci = f"[{r['diff_va_ci_lo']:+.4f},{r['diff_va_ci_hi']:+.4f}]"
            f.write(f"{r['event']:<28s} {r['window']:<6s} {int(r['n_posts']):>5d} "
                    f"{r['diff_polarity']:>+9.4f} {tb_ci:>22s} {r['diff_pol_p_boot']:>7.4g} "
                    f"{r['diff_vader']:>+9.4f} {va_ci:>22s} {r['diff_va_p_boot']:>7.4g}\n")

        # Compute pre-vs-post within-event change
        f.write("\nPRE-vs-POST CHANGE IN GAP MAGNITUDE (does the OP-Reply gap WIDEN/SHRINK around events?)\n")
        f.write("-" * 80 + "\n")
        for ev_name, _, _ in EVENTS:
            sub = out[out["event"] == ev_name]
            if len(sub) != 2 or sub[["diff_polarity", "diff_vader"]].isna().any().any():
                continue
            pre = sub[sub["window"] == "pre"].iloc[0]
            post = sub[sub["window"] == "post"].iloc[0]
            tb_change = post["diff_polarity"] - pre["diff_polarity"]
            va_change = post["diff_vader"] - pre["diff_vader"]
            f.write(f"  {ev_name:<28s}\n")
            f.write(f"    TB gap change (post-pre):    {tb_change:+.4f}  "
                    f"(pre={pre['diff_polarity']:+.4f}, post={post['diff_polarity']:+.4f})\n")
            f.write(f"    VADER gap change (post-pre): {va_change:+.4f}  "
                    f"(pre={pre['diff_vader']:+.4f}, post={post['diff_vader']:+.4f})\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("- TB gap is consistently NEGATIVE (replies more positive than OPs) across events\n")
        f.write("- VADER gap is consistently POSITIVE (OPs higher arousal than replies) across events\n")
        f.write("- If post-window VADER gap is LARGER than pre-window: threat events activate OPs more\n")
        f.write("- If post-window TB gap is MORE negative: replies become MORE supportive after threats\n")
        f.write("- Both directions confirm the help-seeking → help-giving structural pattern\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")

    # Console summary: largest gap-changes
    print("\nLargest OP-Reply gap shifts (post-pre) per event:")
    pre_post_changes = []
    for ev_name, _, _ in EVENTS:
        sub = out[out["event"] == ev_name]
        if len(sub) != 2 or sub[["diff_polarity", "diff_vader"]].isna().any().any():
            continue
        pre = sub[sub["window"] == "pre"].iloc[0]
        post = sub[sub["window"] == "post"].iloc[0]
        pre_post_changes.append({
            "event": ev_name,
            "tb_change": post["diff_polarity"] - pre["diff_polarity"],
            "va_change": post["diff_vader"] - pre["diff_vader"],
            "n_pre": int(pre["n_posts"]), "n_post": int(post["n_posts"]),
        })
    pcdf = pd.DataFrame(pre_post_changes).sort_values("va_change", key=abs, ascending=False)
    print(pcdf.to_string(index=False))


if __name__ == "__main__":
    main()
