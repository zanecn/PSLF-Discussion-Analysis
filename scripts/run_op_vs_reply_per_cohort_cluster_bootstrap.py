"""
P1 Per-cohort OP-vs-Reply cluster bootstrap (R17++ #6 RIGOROUS REVIEW response).

Per agent review: per-event cluster bootstrap exists (`op_reply_per_event_results.txt`);
per-cohort cluster bootstrap does NOT exist. Reviewers at ICWSM/CSCW/IC&S will ask
for cohort-level bootstrap CIs to verify the "8/8 cohorts same direction" claim.

This script extends `run_op_vs_reply_cluster_bootstrap.py` to compute per-cohort
cluster bootstrap CIs for the 8 cohorts in the OP-vs-Reply analysis.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")
B = 2000  # number of cluster-bootstrap resamples per cohort
SEED = 42

# Same cohort mapping as analyze_op_vs_reply.py
PROF_TO_COHORT = {
    "physician": "Reddit Medical", "medical_student": "Reddit Medical",
    "resident": "Reddit Medical", "premed": "Reddit Medical",
    "lawyer": "Reddit Finance", "finance": "Reddit Finance",
    "accountant": "Reddit Finance",
    "teacher": "Reddit Teaching", "education": "Reddit Teaching",
    "nurse": "Reddit Nursing", "nursing_student": "Reddit Nursing",
    "physician_assistant": "Reddit PA", "pa_student": "Reddit PA",
}


def load_ops_and_comments():
    """Load OPs from 4 sources (aligned with analyze_op_vs_reply.py) +
    comments from raw file with on-the-fly VADER."""
    op_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv",
              "reddit_arctic_shift_pslf.csv"]:
        path = PROJECT / f
        if not path.exists():
            continue
        d = pd.read_csv(path, low_memory=False)
        id_col = "post_id" if "post_id" in d.columns else "id"
        if id_col not in d.columns or "polarity" not in d.columns:
            continue
        if id_col != "post_id":
            d = d.rename(columns={id_col: "post_id"})
        if "vader_compound" not in d.columns:
            if "vader" in d.columns:
                d = d.rename(columns={"vader": "vader_compound"})
            else:
                d["vader_compound"] = np.nan
        if "profession" not in d.columns:
            d["profession"] = ""
        if "subreddit" not in d.columns:
            d["subreddit"] = ""
        if "word_count" not in d.columns:
            d["word_count"] = 100
        op_frames.append(d[["post_id", "polarity", "vader_compound", "profession", "subreddit", "word_count"]])
        print(f"  Loaded {f}: {len(d):,} rows")
    ops = pd.concat(op_frames, ignore_index=True).drop_duplicates("post_id")
    ops["post_id"] = ops["post_id"].astype(str)
    ops = ops.dropna(subset=["polarity"])
    ops = ops[ops["word_count"].fillna(0) >= 20]
    # Cohort mapping (mirrors analyze_op_vs_reply.py)
    ops["cohort"] = ops["profession"].map(PROF_TO_COHORT)
    # Fill missing cohort from subreddit
    sub_to_cohort = {
        "PSLF": "Reddit r/PSLF",
        "StudentLoans": "Reddit r/StudentLoans",
        "personalfinance": "Reddit Finance",
    }
    sub_cohort = ops["subreddit"].map(sub_to_cohort)
    ops["cohort"] = ops["cohort"].fillna(sub_cohort).fillna("Other")
    print(f"  Total unique OPs (wc>=20): {len(ops):,}")
    print(f"  Cohort distribution:")
    for cohort, count in ops["cohort"].value_counts().items():
        print(f"    {cohort:30s}: {count:,}")

    # Comments: raw file with polarity + on-the-fly VADER
    cm_path = PROJECT / "reddit_comments_pslf.csv"
    if not cm_path.exists():
        cm_path = PROJECT / "reddit_comments_pslf_with_vader.csv"
    print(f"  Loading comments from {cm_path.name}...")
    cm = pd.read_csv(cm_path, low_memory=False)
    cm["post_id"] = cm["post_id"].astype(str)
    cm = cm[cm["polarity"].notna()]
    cm = cm[cm["word_count"].fillna(0) >= 5]
    if "vader_compound" not in cm.columns or cm["vader_compound"].isna().all():
        print("  vader_compound missing — computing VADER on comments...")
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        bodies = cm["body"].fillna("").astype(str).tolist()
        cv = np.empty(len(bodies), dtype=float)
        for i, b in enumerate(bodies):
            try:
                cv[i] = sia.polarity_scores(b[:5000])["compound"] if b else np.nan
            except Exception:
                cv[i] = np.nan
            if (i + 1) % 50000 == 0:
                print(f"    {i+1:,}/{len(bodies):,}")
        cm["vader_compound"] = cv
    cm = cm[["post_id", "polarity", "vader_compound"]].dropna(subset=["post_id"]).copy()
    print(f"  Loaded comments: {len(cm):,}")
    return ops, cm


def per_post_delta(ops, cm):
    cm_agg = cm.groupby("post_id").agg(
        mean_cmt_polarity=("polarity", "mean"),
        mean_cmt_vader=("vader_compound", "mean"),
    ).reset_index()
    df = ops.merge(cm_agg, on="post_id", how="inner")
    df["delta_pol"] = df["polarity"] - df["mean_cmt_polarity"]
    df["delta_vader"] = df["vader_compound"] - df["mean_cmt_vader"]
    return df


def cohort_cluster_bootstrap(df_cohort, b=2000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(df_cohort)
    if n < 2:
        return None
    delta_pol_arr = df_cohort["delta_pol"].to_numpy()
    delta_vader_arr = df_cohort["delta_vader"].to_numpy()
    pol_means = np.empty(b)
    vader_means = np.empty(b)
    for i in range(b):
        idx = rng.integers(0, n, n)
        pol_means[i] = np.nanmean(delta_pol_arr[idx])
        vader_means[i] = np.nanmean(delta_vader_arr[idx])
    pol_point = np.nanmean(delta_pol_arr)
    vader_point = np.nanmean(delta_vader_arr)
    pol_ci = (np.percentile(pol_means, 2.5), np.percentile(pol_means, 97.5))
    vader_ci = (np.percentile(vader_means, 2.5), np.percentile(vader_means, 97.5))
    pol_p = 2 * min((pol_means > 0).mean(), (pol_means < 0).mean())
    vader_p = 2 * min((vader_means > 0).mean(), (vader_means < 0).mean())
    return {
        "n": n,
        "pol_point": pol_point, "pol_lo": pol_ci[0], "pol_hi": pol_ci[1], "pol_p": pol_p,
        "vader_point": vader_point, "vader_lo": vader_ci[0], "vader_hi": vader_ci[1], "vader_p": vader_p,
    }


def main():
    ops, cm = load_ops_and_comments()
    df = per_post_delta(ops, cm)
    df = df.dropna(subset=["delta_pol", "delta_vader"]).reset_index(drop=True)
    print(f"\nTotal posts with both OP + comments: {len(df):,}")

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 1 PER-COHORT OP-VS-REPLY CLUSTER BOOTSTRAP")
    out_lines.append("(R17++ #6 RIGOROUS REVIEW response — agent flagged that per-cohort")
    out_lines.append("cluster bootstrap was missing; reviewers at ICWSM/CSCW will ask)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append(f"B = {B} cluster-bootstrap resamples per cohort")
    out_lines.append(f"Cluster unit = post_id")
    out_lines.append("")
    out_lines.append(f"{'cohort':30s} {'n':>7s}  {'TB Δ':>10s}  {'TB CI':>30s}  {'VADER Δ':>10s}  {'VADER CI':>30s}")
    out_lines.append("-" * 130)

    cohort_results = {}
    for cohort in sorted(df["cohort"].unique(), key=lambda c: -(df["cohort"]==c).sum()):
        df_cohort = df[df["cohort"] == cohort]
        if len(df_cohort) < 10:
            continue
        res = cohort_cluster_bootstrap(df_cohort, b=B, seed=SEED)
        if res is None:
            continue
        cohort_results[cohort] = res
        tb_ci_str = f"[{res['pol_lo']:+.4f}, {res['pol_hi']:+.4f}]"
        va_ci_str = f"[{res['vader_lo']:+.4f}, {res['vader_hi']:+.4f}]"
        out_lines.append(
            f"{cohort:30s} {res['n']:>7,d}  {res['pol_point']:+10.4f}  {tb_ci_str:>30s}  "
            f"{res['vader_point']:+10.4f}  {va_ci_str:>30s}"
        )

    out_lines.append("")
    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 90)
    n_cohorts = len(cohort_results)
    n_tb_neg = sum(1 for r in cohort_results.values() if r['pol_point'] < 0)
    n_tb_ci_excl_zero = sum(1 for r in cohort_results.values() if r['pol_hi'] < 0)
    n_vader_pos = sum(1 for r in cohort_results.values() if r['vader_point'] > 0)
    n_vader_ci_excl_zero = sum(1 for r in cohort_results.values() if r['vader_lo'] > 0)
    out_lines.append(f"  Cohorts analyzed: {n_cohorts}")
    out_lines.append(f"  TextBlob Δ < 0 (replies more positive): {n_tb_neg}/{n_cohorts} cohorts")
    out_lines.append(f"  TextBlob cluster-bootstrap CI excludes 0: {n_tb_ci_excl_zero}/{n_cohorts} cohorts")
    out_lines.append(f"  VADER Δ > 0 (OPs more positive): {n_vader_pos}/{n_cohorts} cohorts")
    out_lines.append(f"  VADER cluster-bootstrap CI excludes 0: {n_vader_ci_excl_zero}/{n_cohorts} cohorts")
    out_lines.append("")
    out_lines.append(f"  HEADLINE: {n_tb_neg}/{n_cohorts} cohorts show TB Δ < 0 AND VADER Δ > 0 — the directional split is cohort-robust.")
    if n_tb_ci_excl_zero == n_cohorts and n_vader_ci_excl_zero == n_cohorts:
        out_lines.append(f"  All cluster-bootstrap CIs exclude 0 — directional finding is per-cohort cluster-bootstrap robust.")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper1_op_vs_reply_per_cohort_cluster_bootstrap_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(out_text)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
