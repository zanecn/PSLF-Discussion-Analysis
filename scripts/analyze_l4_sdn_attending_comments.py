"""
analyze_l4_sdn_attending_comments.py
======================================
L4: Test the A3 finding (SDN attendings show stronger sentiment-stance
decoupling than residents) at COMMENTS scale.

Comments don't have Claude pslf_stance, so we use sentiment INTENSITY proxies:
  - Mean polarity: do attendings post more negatively than residents?
  - Polarity DISPERSION (sd): do attendings have wider spread?
  - Polarity-quantile differences

Also stratify by post_subreddit (proxy for SDN-Medical from comments)
since SDN comments aren't in the Reddit comments dataset.

NOTE: This is intensity-only, not OR-style decoupling. The closest analog
to A3's mechanism (negative posts have different stance distribution by
career stage) requires Claude scoring on comments which we don't have.

Output: l4_sdn_attending_comments_results.{txt,csv}
"""
from __future__ import annotations
import io, os, sys, warnings, re
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

from analyze_mediation_career_stage import classify_career_stage

OUT_TXT = "l4_sdn_attending_comments_results.txt"
OUT_CSV = "l4_sdn_attending_comments_results.csv"


def main():
    print("=" * 80)
    print("L4: SDN attending pattern at COMMENTS scale (intensity-only)")
    print("=" * 80)

    # NOTE: Reddit comments DOES include r/Residency, r/medicine — partial proxy
    # for SDN-Medical-like population. SDN comments not in this dataset.
    if not os.path.exists("reddit_comments_pslf.csv"):
        print("[ABORT] reddit_comments_pslf.csv not found")
        return

    cols = ["comment_id", "post_id", "post_subreddit", "body",
            "polarity", "word_count"]
    df = pd.read_csv("reddit_comments_pslf.csv", usecols=cols, low_memory=False)
    df = df.dropna(subset=["polarity", "body"])
    df = df[df["word_count"] >= 5]
    print(f"\nReddit comments after filter: {len(df):,}")

    # Restrict to medical-adjacent subreddits (proxy for SDN-Medical population)
    medical_subs = {"medicine", "Residency", "medicalschool", "Step1",
                     "step2", "step3", "premed", "Internalmedicine"}
    df["is_medical"] = df["post_subreddit"].isin(medical_subs)
    print(f"Medical-subreddit comments: {df['is_medical'].sum():,}")

    # Classify career stage
    print("\nClassifying career stage on comment body...")
    df["career_stage"] = df["body"].fillna("").apply(classify_career_stage)
    print(df["career_stage"].value_counts().to_string())

    # === Test 1: Sentiment intensity by career stage (within medical comments) ===
    print("\n[1] Sentiment intensity by career stage (medical-subreddit comments)")
    med = df[df["is_medical"]].copy()
    rows = []
    for cs in ["resident", "attending", "fellow", "medical_student", "premed"]:
        sub = med[med["career_stage"] == cs]
        if len(sub) < 100: continue
        rows.append({
            "career_stage": cs,
            "subset": "medical_subs_only",
            "n": len(sub),
            "mean_polarity": sub["polarity"].mean(),
            "sd_polarity": sub["polarity"].std(),
            "median_polarity": sub["polarity"].median(),
            "pct_negative": (sub["polarity"] < -0.05).mean() * 100,
            "pct_very_negative": (sub["polarity"] < -0.3).mean() * 100,
            "pct_positive": (sub["polarity"] > 0.05).mean() * 100,
        })
        print(f"  {cs:<18s} n={len(sub):>6,} mean={sub['polarity'].mean():+.4f} "
               f"sd={sub['polarity'].std():.3f} %neg={(sub['polarity']<-0.05).mean()*100:5.1f}% "
               f"%pos={(sub['polarity']>0.05).mean()*100:5.1f}%")

    # === Test 2: All-Reddit comments by career stage (whole corpus) ===
    print("\n[2] Sentiment intensity by career stage (ALL Reddit comments)")
    for cs in ["resident", "attending", "fellow", "medical_student", "premed"]:
        sub = df[df["career_stage"] == cs]
        if len(sub) < 100: continue
        rows.append({
            "career_stage": cs,
            "subset": "all_reddit",
            "n": len(sub),
            "mean_polarity": sub["polarity"].mean(),
            "sd_polarity": sub["polarity"].std(),
            "median_polarity": sub["polarity"].median(),
            "pct_negative": (sub["polarity"] < -0.05).mean() * 100,
            "pct_very_negative": (sub["polarity"] < -0.3).mean() * 100,
            "pct_positive": (sub["polarity"] > 0.05).mean() * 100,
        })
        print(f"  {cs:<18s} n={len(sub):>6,} mean={sub['polarity'].mean():+.4f} "
               f"sd={sub['polarity'].std():.3f} %neg={(sub['polarity']<-0.05).mean()*100:5.1f}%")

    # === Test 3: Pairwise comparisons (attending vs resident) ===
    print("\n[3] Pairwise t-test: attending vs resident polarity")
    pairs = []
    for subset_label, subset_df in [("medical_subs_only", med), ("all_reddit", df)]:
        att = subset_df[subset_df["career_stage"] == "attending"]["polarity"]
        res = subset_df[subset_df["career_stage"] == "resident"]["polarity"]
        if len(att) < 30 or len(res) < 30: continue
        t, p = stats.ttest_ind(att, res, equal_var=False)
        pooled = np.sqrt(((len(att)-1)*att.var() + (len(res)-1)*res.var())
                          / (len(att)+len(res)-2))
        d = (att.mean() - res.mean()) / pooled if pooled > 0 else float("nan")
        pairs.append({
            "subset": subset_label,
            "n_attending": len(att), "n_resident": len(res),
            "mean_attending": att.mean(), "mean_resident": res.mean(),
            "diff": att.mean() - res.mean(),
            "t": t, "p": p, "cohens_d": d,
        })
        print(f"  {subset_label}:  n_att={len(att):,} n_res={len(res):,}  "
               f"att_mean={att.mean():+.4f} res_mean={res.mean():+.4f}  "
               f"diff={att.mean()-res.mean():+.4f}  d={d:+.3f}  p={p:.4g}")

    # === Save ===
    out = pd.DataFrame(rows)
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("L4: SDN ATTENDING PATTERN AT COMMENTS SCALE (intensity-only)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Reddit comments analyzed: {len(df):,}\n")
        f.write(f"Medical-subreddit comments: {df['is_medical'].sum():,}\n\n")

        f.write("SENTIMENT INTENSITY BY CAREER STAGE\n")
        f.write("-" * 80 + "\n")
        for r in rows:
            f.write(f"  [{r['subset']}] {r['career_stage']:<18s} n={r['n']:>6,} "
                    f"mean={r['mean_polarity']:+.4f} sd={r['sd_polarity']:.3f} "
                    f"%neg={r['pct_negative']:5.1f}%\n")

        f.write("\nATTENDING vs RESIDENT PAIRWISE\n")
        f.write("-" * 80 + "\n")
        for p in pairs:
            f.write(f"  [{p['subset']}] n_att={p['n_attending']:,} n_res={p['n_resident']:,}  "
                    f"diff={p['diff']:+.4f}  d={p['cohens_d']:+.3f}  p={p['p']:.4g}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        f.write("Comments are TextBlob-only — cannot replicate A3's stance-decoupling\n")
        f.write("OR analysis directly. This script tests whether the underlying\n")
        f.write("INTENSITY pattern (attendings post more negatively than residents)\n")
        f.write("holds at comments scale.\n\n")
        if pairs:
            for p in pairs:
                if p["p"] < 0.05:
                    direction = "more negative" if p["diff"] < 0 else "more positive"
                    f.write(f"  [{p['subset']}] Attendings are {direction} than residents "
                            f"(d={p['cohens_d']:+.3f}, p={p['p']:.4g}) — partially supports A3\n")
                else:
                    f.write(f"  [{p['subset']}] No significant attending-resident polarity diff\n")
        f.write("\nNote: Reddit comments do not include SDN. This is a partial proxy.\n")
        f.write("A direct test of the A3 finding requires Claude scoring on comments\n")
        f.write("(estimated cost ~$2,300 for 460K comments at current pricing).\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")


if __name__ == "__main__":
    main()
