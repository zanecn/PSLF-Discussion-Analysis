"""
analyze_per_profession_breakdowns.py
======================================
Stratifies the round-9 substantive findings by profession/cohort:

  1. Sentiment-stance decoupling (OR + delta_pp) per cohort
  2. OP vs Reply opposite-direction (TB Δ, VADER Δ) per cohort
  3. Cumulative stance distribution per cohort (already computed; for context)
  4. Pooled per-event sentiment shifts per cohort (re-summary from existing table)
  5. Per-event topic restructuring (Cramer's V) per cohort

Goal: identify which findings are uniform across cohorts vs cohort-conditional.

Output: per_profession_breakdowns.{txt,csv}
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

from sentiment_triangulation import load_zeroshot, attach_textblob_vader
from pslf_search_terms import filter_pslf_relevant

OUT_TXT = "per_profession_breakdowns.txt"
OUT_CSV = "per_profession_breakdowns.csv"

PROF_LABEL = {
    "general_pslf":              "Reddit r/PSLF",
    "general_student_loans":     "Reddit r/StudentLoans",
    "general_finance":           "Reddit Finance",
    "personalfinance":           "Reddit Finance",
    "financialindependence":     "Reddit Finance",
    "medical":                   "Reddit Medical",
    "teaching":                  "Reddit Teaching",
    "physician_assistant":       "Reddit PA",
    "nursing":                   "Reddit Nursing",
    "sdn_medical":               "SDN (Medical)",
    "sdn":                       "SDN (Medical)",
}

MIN_COHORT_N = 100  # cohort needs >= 100 posts/comments for inclusion


def fix_decoupling_per_cohort(merged: pd.DataFrame) -> pd.DataFrame:
    """For each cohort, compute negative-vs-non-negative pursuing rates + OR.

    BUG FIX: attach_textblob_vader strips the profession column. Re-merge
    profession from source CSVs by post_id.
    """
    df = merged.copy()
    df["post_id"] = df["post_id"].astype(str)

    # Re-merge profession from source CSVs (Reddit) + tag SDN by source
    prof_frames = []
    for f in ["reddit_professions_pslf.csv",
              "reddit_arctic_shift_pslf.csv",
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
            # legacy CSVs may not have profession; tag based on file
            if "medical" in f:
                d["profession"] = "medical"
            elif "teacher" in f:
                d["profession"] = "teaching"
            else:
                continue
        d["post_id"] = d["post_id"].astype(str)
        prof_frames.append(d[["post_id", "profession"]])
    profs = pd.concat(prof_frames, ignore_index=True).drop_duplicates("post_id")
    df = df.merge(profs, on="post_id", how="left")
    df["profession"] = df["profession"].fillna("").astype(str)

    # Cohort assignment
    df["cohort"] = df["profession"].map(PROF_LABEL).fillna("Other")
    if "source" in df.columns:
        sdn_mask = df["source"].fillna("").astype(str).str.lower() == "sdn"
        df.loc[sdn_mask, "cohort"] = "SDN (Medical)"
    df = df.dropna(subset=["pslf_sentiment", "pslf_stance"])
    df = df[~df["pslf_stance"].isin(["unknown", "", None])]
    df = df[df["pslf_sentiment"].isin(["very_negative", "negative", "neutral", "positive", "very_positive"])]
    df["is_neg_sent"] = df["pslf_sentiment"].isin(["very_negative", "negative"])
    df["is_pursuing"] = df["pslf_stance"].isin(["pursuing", "considering"])

    rows = []
    for cohort in df["cohort"].value_counts().index:
        sub = df[df["cohort"] == cohort]
        n = len(sub)
        n_neg = sub["is_neg_sent"].sum()
        n_pos = (~sub["is_neg_sent"]).sum()
        if n_neg < 30 or n_pos < 30:
            continue
        marg = float(sub["is_pursuing"].mean())
        pur_neg = float(sub[sub["is_neg_sent"]]["is_pursuing"].mean())
        pur_nonneg = float(sub[~sub["is_neg_sent"]]["is_pursuing"].mean())
        # 2x2 OR + chi-sq
        a = ((sub["is_neg_sent"]) & (sub["is_pursuing"])).sum()
        b = ((sub["is_neg_sent"]) & (~sub["is_pursuing"])).sum()
        c = ((~sub["is_neg_sent"]) & (sub["is_pursuing"])).sum()
        d = ((~sub["is_neg_sent"]) & (~sub["is_pursuing"])).sum()
        if min(a, b, c, d) >= 1:
            or_val = float((a*d) / (b*c)) if b*c > 0 else float("nan")
            log_or = np.log(or_val) if or_val > 0 else float("nan")
            se_log = np.sqrt(1/a + 1/b + 1/c + 1/d) if min(a,b,c,d) > 0 else float("nan")
            ci_lo = float(np.exp(log_or - 1.96 * se_log)) if not np.isnan(se_log) else float("nan")
            ci_hi = float(np.exp(log_or + 1.96 * se_log)) if not np.isnan(se_log) else float("nan")
            ct = np.array([[a, b], [c, d]])
            try:
                chi2, p_chi, _, _ = stats.chi2_contingency(ct)
            except Exception:
                chi2, p_chi = float("nan"), float("nan")
        else:
            or_val = ci_lo = ci_hi = chi2 = p_chi = float("nan")
        rows.append({
            "cohort": cohort,
            "n_total": int(n),
            "n_negative_sent": int(n_neg),
            "marginal_pursuing_pct": marg * 100,
            "pursuing_among_neg_pct": pur_neg * 100,
            "pursuing_among_nonneg_pct": pur_nonneg * 100,
            "delta_pp": (pur_neg - marg) * 100,
            "odds_ratio": or_val,
            "or_ci_lo": ci_lo,
            "or_ci_hi": ci_hi,
            "chi2": chi2,
            "chi2_p": p_chi,
        })
    return pd.DataFrame(rows).sort_values("n_total", ascending=False)


def fix_op_reply_per_cohort() -> pd.DataFrame:
    """For each cohort, compute OP vs Reply diff in TextBlob and VADER."""
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
        keep = ["post_id", "polarity"]
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
    ops = ops.dropna(subset=["polarity"])
    ops = ops[ops["word_count"].fillna(0) >= 20]
    ops["cohort"] = ops["profession"].map(PROF_LABEL).fillna("Other")
    ops = ops.rename(columns={"polarity": "op_polarity", "vader_compound": "op_vader"})

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

    rows = []
    rng = np.random.default_rng(42)
    for cohort in df["cohort"].value_counts().index:
        sub = df[df["cohort"] == cohort]
        n = len(sub)
        if n < 100:
            continue
        # Cluster bootstrap (each post is one cluster)
        boot_pol_means = []
        boot_va_means = []
        for _ in range(1000):
            idx = rng.integers(0, n, size=n)
            boot_pol_means.append(sub["diff_pol"].iloc[idx].mean())
            boot_va_means.append(sub["diff_va"].iloc[idx].mean())
        rows.append({
            "cohort": cohort,
            "n_posts": int(n),
            "diff_polarity": float(sub["diff_pol"].mean()),
            "diff_polarity_ci95": (float(np.percentile(boot_pol_means, 2.5)),
                                    float(np.percentile(boot_pol_means, 97.5))),
            "diff_polarity_p_boot": float(2 * min((np.array(boot_pol_means) > 0).mean(),
                                                   (np.array(boot_pol_means) < 0).mean())),
            "diff_vader": float(sub["diff_va"].mean()),
            "diff_vader_ci95": (float(np.percentile(boot_va_means, 2.5)),
                                 float(np.percentile(boot_va_means, 97.5))),
            "diff_vader_p_boot": float(2 * min((np.array(boot_va_means) > 0).mean(),
                                                (np.array(boot_va_means) < 0).mean())),
            "mean_n_cmt_per_post": float(sub["n_cmt"].mean()),
        })
    return pd.DataFrame(rows).sort_values("n_posts", ascending=False)


def fix_per_event_per_cohort_summary() -> pd.DataFrame:
    """Re-summarize the per-profession per-event findings — which cohort × event
    cells survive BH FDR (q=0.05) within the cohort × event family (n=76)?"""
    if not os.path.exists("per_profession_per_event_results.csv"):
        return pd.DataFrame()
    df = pd.read_csv("per_profession_per_event_results.csv")
    df = df[df["scorer"] == "polarity"] if "scorer" in df.columns else df
    df = df.dropna(subset=["p_boot"])
    # BH FDR within family
    n = len(df)
    df_sorted = df.sort_values("p_boot").reset_index(drop=True)
    df_sorted["bh_threshold"] = (df_sorted.index + 1) * 0.05 / n
    df_sorted["bh_pass"] = df_sorted["p_boot"] <= df_sorted["bh_threshold"]
    if df_sorted["bh_pass"].any():
        max_pass_idx = df_sorted[df_sorted["bh_pass"]].index.max()
        df_sorted.loc[:max_pass_idx, "bh_pass"] = True
    return df_sorted


def main():
    print("=" * 80)
    print("Per-Profession Breakdowns of Round-9 Substantive Findings")
    print("=" * 80)

    print("\n[1] Loading zero-shot data + merge...")
    zs = load_zeroshot()
    merged = attach_textblob_vader(zs)
    print(f"  Merged rows: {len(merged):,}")

    print("\n[2] Sentiment-stance decoupling per cohort...")
    decoupling = fix_decoupling_per_cohort(merged)
    print(decoupling.to_string(index=False))
    decoupling.to_csv("decoupling_by_cohort.csv", index=False, float_format="%.4f")

    print("\n[3] OP vs Reply per cohort...")
    op_reply = fix_op_reply_per_cohort()
    op_reply_display = op_reply.copy()
    op_reply_display["diff_polarity_ci95"] = op_reply_display["diff_polarity_ci95"].astype(str)
    op_reply_display["diff_vader_ci95"] = op_reply_display["diff_vader_ci95"].astype(str)
    print(op_reply_display.to_string(index=False))

    print("\n[4] Per-event per-cohort BH FDR pass list...")
    per_event = fix_per_event_per_cohort_summary()
    if len(per_event):
        bh_pass = per_event[per_event["bh_pass"] == True]
        print(f"  N tests: {len(per_event)}")
        print(f"  BH FDR (q=0.05) passing: {len(bh_pass)}")
        cols_to_show = [c for c in ["event", "profession_label", "g", "p_boot",
                                     "n_pre", "n_post"] if c in bh_pass.columns]
        print(bh_pass[cols_to_show].to_string(index=False))

    # Write main artifact
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Per-Profession Breakdowns of Round-9 Substantive Findings\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")

        f.write("FINDING 1: Sentiment-stance decoupling, BY COHORT\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether the (-5pp, OR=0.58) pooled decoupling holds in each cohort,\n")
        f.write("and whether magnitude is cohort-conditional.\n\n")
        f.write(f"{'cohort':<26s} {'n':>6s} {'n_neg':>6s} {'pur_marg':>9s} "
                f"{'pur_neg':>8s} {'delta':>7s} {'OR':>6s} {'OR_lo':>7s} {'OR_hi':>7s} {'chi2_p':>9s}\n")
        for _, r in decoupling.iterrows():
            f.write(f"{r['cohort']:<26s} {int(r['n_total']):>6d} {int(r['n_negative_sent']):>6d} "
                    f"{r['marginal_pursuing_pct']:>8.1f}% {r['pursuing_among_neg_pct']:>7.1f}% "
                    f"{r['delta_pp']:>+6.2f} {r['odds_ratio']:>6.2f} "
                    f"{r['or_ci_lo']:>7.2f} {r['or_ci_hi']:>7.2f} {r['chi2_p']:>9.4g}\n")
        f.write("\nReading: a smaller OR means STRONGER decoupling in that cohort.\n")
        f.write("Marginal pursuing varies by cohort (selection effect); the negative-cohort\n")
        f.write("delta_pp tells you whether sentiment carries information ON TOP OF cohort selection.\n\n")

        f.write("FINDING 2: OP vs Reply opposite-direction, BY COHORT\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether the cohort-pooled finding (TB diff -0.017, VADER diff +0.220)\n")
        f.write("holds in each cohort separately. Reports cluster-bootstrap CIs.\n\n")
        f.write(f"{'cohort':<26s} {'n_posts':>8s} {'n_cmt/post':>10s} "
                f"{'TB diff':>8s} {'TB CI95':>20s} {'TB p':>8s} "
                f"{'VA diff':>8s} {'VA CI95':>20s} {'VA p':>8s}\n")
        for _, r in op_reply.iterrows():
            tb_ci = f"[{r['diff_polarity_ci95'][0]:+.4f},{r['diff_polarity_ci95'][1]:+.4f}]"
            va_ci = f"[{r['diff_vader_ci95'][0]:+.4f},{r['diff_vader_ci95'][1]:+.4f}]"
            f.write(f"{r['cohort']:<26s} {int(r['n_posts']):>8d} {r['mean_n_cmt_per_post']:>10.1f} "
                    f"{r['diff_polarity']:>+8.4f} {tb_ci:>20s} {r['diff_polarity_p_boot']:>8.4g} "
                    f"{r['diff_vader']:>+8.4f} {va_ci:>20s} {r['diff_vader_p_boot']:>8.4g}\n")
        f.write("\nReading: TB diff is 'OP - mean reply'. Negative TB diff means OPs are LESS positive than replies (reply skew).\n")
        f.write("Positive VADER diff means OPs have MORE expressive arousal than replies.\n")
        f.write("If sign is CONSISTENT across cohorts: cohort-invariant finding.\n")
        f.write("If sign FLIPS: cohort-specific finding.\n\n")

        if len(per_event):
            f.write("FINDING 3: Per-event per-cohort sentiment shifts (BH FDR q=0.05)\n")
            f.write("-" * 80 + "\n")
            f.write(f"  N tests: {len(per_event)}\n")
            f.write(f"  BH FDR passing: {(per_event['bh_pass'] == True).sum()}\n\n")
            bh_pass = per_event[per_event["bh_pass"] == True].sort_values("event")
            f.write(f"{'event':<28s} {'cohort':<26s} {'g':>7s} {'p_boot':>9s} {'n_pre/n_post':>14s}\n")
            for _, r in bh_pass.iterrows():
                f.write(f"{r['event']:<28s} {r['profession_label']:<26s} "
                        f"{r['g']:>+7.3f} {r['p_boot']:>9.4f} "
                        f"{int(r['n_pre']):>5d}/{int(r['n_post']):>5d}\n")
            f.write("\nReading: cells listed here are BH-FDR-significant within the\n")
            f.write("per-cohort × per-event family (n=76 tests, q=0.05).\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: decoupling_by_cohort.csv")


if __name__ == "__main__":
    main()
