"""
analyze_comment_cohort_heterogeneity.py
=========================================
Tests whether the cohort-heterogeneity finding (SDN-Medical and Reddit-general
respond opposite-sign on PSLF events) replicates at the COMMENT level.

Why important:
  - The post-level finding rests on 5K-30K post cells per cohort
  - Comments give 5-15x more text per post
  - Comments come from MORE distinct authors per post (replies pull in
    different posters than the OP)
  - If cohort heterogeneity holds at the comment level, the substantive
    paper's headline gains a major defensibility upgrade
  - If it does NOT hold, that's a critical caveat (suggests the post-level
    finding is driven by OP-selection, not cohort-level reactions)

Inputs:
  - reddit_comments_pslf.csv    (108K comments from 4,137 covered posts)
  - reddit_professions_pslf.csv  (post metadata: subreddit, profession)
  - forum_pslf_discussions.csv   (SDN posts WITHOUT comments since SDN is forum-thread, not API)

Note: SDN comments are baked into forum_pslf_discussions.csv as separate rows
(each post within a thread is a "comment" of sorts). For this comment-level
analysis on Reddit, SDN serves as the reference cohort using its full data.

Outputs:
  - comment_cohort_heterogeneity_results.{txt,csv}
  - comment_cohort_heterogeneity.png

Usage:
  python analyze_comment_cohort_heterogeneity.py
"""
from __future__ import annotations

import io
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from scipy import stats

from pslf_search_terms import filter_pslf_relevant
from sentiment_triangulation import EVENTS, hedges_g, block_permutation_p

OUT_TXT = "comment_cohort_heterogeneity_results.txt"
OUT_CSV = "comment_cohort_heterogeneity_results.csv"
OUT_PNG = "comment_cohort_heterogeneity.png"

PROF_TO_COHORT = {
    "general_pslf": "Reddit r/PSLF",
    "general_student_loans": "Reddit r/StudentLoans",
    "general_finance": "Reddit Finance",
    "personalfinance": "Reddit Finance",
    "financialindependence": "Reddit Finance",
    "medical": "Reddit Medical",
    "teaching": "Reddit Teaching",
    "physician_assistant": "Reddit PA",
    "nursing": "Reddit Nursing",
}

COHORT_COLORS = {
    "SDN (Medical)":          "#C2185B",
    "Reddit r/PSLF":          "#1565C0",
    "Reddit r/StudentLoans":  "#388E3C",
    "Reddit Finance":         "#F57C00",
    "Reddit Medical":         "#6A1B9A",
}

MIN_CELL_N = 30  # comment cells need higher n than post cells


def load_comments_with_cohort() -> pd.DataFrame:
    """Load comments and tag with cohort by joining post profession via post_id."""
    print("Loading comments...")
    cm = pd.read_csv("reddit_comments_pslf.csv", low_memory=False)
    print(f"  Total comments: {len(cm):,}")
    print(f"  Unique posts covered: {cm['post_id'].nunique():,}")
    cm["date"] = pd.to_datetime(pd.to_numeric(cm["created_utc"], errors="coerce"),
                                  unit="s", errors="coerce")
    cm = cm.dropna(subset=["date", "polarity"])
    cm = cm[cm["word_count"].fillna(0) >= 5]  # min 5 words for comments
    print(f"  After date+polarity+wc>=5: {len(cm):,}")

    # Load posts to get profession/cohort by post_id
    post_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv",
              "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f, usecols=lambda c: c in ("id", "subreddit", "profession"))
        if "id" in d.columns:
            d = d.rename(columns={"id": "post_id"})
        post_frames.append(d[["post_id", "profession", "subreddit"]])
    posts = pd.concat(post_frames, ignore_index=True).drop_duplicates("post_id")

    cm["post_id"] = cm["post_id"].astype(str)
    posts["post_id"] = posts["post_id"].astype(str)
    cm = cm.merge(posts[["post_id", "profession"]], on="post_id", how="left",
                   suffixes=("", "_post"))
    # If we got profession from the post, use it; otherwise from the comment row's profession
    cm["profession"] = cm["profession_post"].fillna(cm.get("profession", ""))
    cm["cohort"] = cm["profession"].map(PROF_TO_COHORT).fillna("Other")
    n_with_cohort = (cm["cohort"] != "Other").sum()
    print(f"  Comments with mapped cohort: {n_with_cohort:,} ({100*n_with_cohort/len(cm):.1f}%)")

    # Add SDN as reference - SDN forum_pslf already has body posts that act as comments
    if os.path.exists("forum_pslf_discussions.csv"):
        sdn = pd.read_csv("forum_pslf_discussions.csv")
        bm = filter_pslf_relevant(sdn["body"].fillna(""))
        ttm = filter_pslf_relevant(sdn["thread_title"].fillna(""))
        sdn = sdn[bm | ttm].copy()
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        sdn = sdn.dropna(subset=["date", "polarity"])
        sdn = sdn[sdn["word_count"].fillna(0) >= 5]
        sdn["cohort"] = "SDN (Medical)"
        sdn["body"] = sdn["body"]
        # Make schema-compatible with comments
        sdn_compat = pd.DataFrame({
            "post_id": sdn["post_id"],
            "date": sdn["date"],
            "polarity": sdn["polarity"],
            "vader_compound": sdn.get("vader_compound", pd.Series(np.nan, index=sdn.index)),
            "word_count": sdn["word_count"],
            "cohort": sdn["cohort"],
        })
        # Make Reddit comments compatible
        cm_compat = pd.DataFrame({
            "post_id": cm["post_id"],
            "date": cm["date"],
            "polarity": cm["polarity"],
            "vader_compound": cm.get("vader_compound", pd.Series(np.nan, index=cm.index)),
            "word_count": cm["word_count"],
            "cohort": cm["cohort"],
        })
        out = pd.concat([cm_compat, sdn_compat], ignore_index=True)
        print(f"  After adding SDN ({len(sdn):,}): {len(out):,} total comment-equivalents")
        return out
    return cm


def per_event_per_cohort_g(df: pd.DataFrame, scorer_col: str,
                            cohorts: list[str], min_n: int = MIN_CELL_N) -> pd.DataFrame:
    rows = []
    for ev_name, ev_date, win in EVENTS:
        dt = pd.Timestamp(ev_date)
        for cohort in cohorts:
            sub = df[df["cohort"] == cohort]
            pre = sub[(sub["date"] >= dt - pd.Timedelta(days=win)) &
                      (sub["date"] < dt) & sub[scorer_col].notna()]
            post = sub[(sub["date"] >= dt) &
                       (sub["date"] <= dt + pd.Timedelta(days=win)) &
                       sub[scorer_col].notna()]
            n_pre, n_post = len(pre), len(post)
            if n_pre < min_n or n_post < min_n:
                continue
            a = pre[scorer_col].to_numpy()
            b = post[scorer_col].to_numpy()
            g = hedges_g(a, b)
            p = block_permutation_p(
                pre[["date", scorer_col]], post[["date", scorer_col]],
                scorer_col=scorer_col, B=1000, seed=42)
            rows.append({
                "event": ev_name, "cohort": cohort, "scorer": scorer_col,
                "n_pre": n_pre, "n_post": n_post,
                "mean_pre": float(a.mean()), "mean_post": float(b.mean()),
                "g": g, "p_boot": p,
            })
    return pd.DataFrame(rows)


def main():
    print("=" * 80)
    print("Comment-level Cohort Heterogeneity Test")
    print("=" * 80)

    df = load_comments_with_cohort()
    print()
    print("Cohort breakdown:")
    print(df["cohort"].value_counts().to_string())

    cohorts = [c for c in df["cohort"].value_counts().index
               if c in COHORT_COLORS and df[df["cohort"] == c].shape[0] >= 500]
    print(f"\nCohorts with n>=500 comments: {cohorts}")

    print(f"\nComputing per-event x per-cohort g (TextBlob, B=1000, min_cell_n={MIN_CELL_N})...")
    tb = per_event_per_cohort_g(df, "polarity", cohorts, MIN_CELL_N)
    if "vader_compound" in df.columns:
        va = per_event_per_cohort_g(df, "vader_compound", cohorts, MIN_CELL_N)
    else:
        va = pd.DataFrame()
    print(f"  TextBlob cells reported: {len(tb)}")
    print(f"  VADER cells reported:    {len(va)}")

    out = pd.concat([tb, va], ignore_index=True) if len(va) else tb
    out.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Compare to post-level cohort heterogeneity findings
    POST_LEVEL = {
        ("Limited PSLF Waiver", "SDN (Medical)"):           +0.42,
        ("Limited PSLF Waiver", "Reddit r/StudentLoans"):   -0.29,
        ("Limited PSLF Waiver", "Reddit r/PSLF"):           -0.08,
        ("Payments Restart", "SDN (Medical)"):              +0.59,
        ("Payments Restart", "Reddit r/PSLF"):              -0.12,
        ("Payments Restart", "Reddit r/StudentLoans"):      -0.17,
        ("SAVE Admin Forbearance", "SDN (Medical)"):        +1.69,
        ("SAVE Admin Forbearance", "Reddit r/PSLF"):        +0.01,
        ("SAVE Admin Forbearance", "Reddit r/StudentLoans"): -0.09,
        ("Trump PSLF EO", "SDN (Medical)"):                 -0.45,
        ("Trump PSLF EO", "Reddit r/PSLF"):                 -0.14,
        ("Trump PSLF EO", "Reddit r/StudentLoans"):         -0.05,
        ("Final Trump PSLF Rule", "SDN (Medical)"):         +0.66,
        ("Final Trump PSLF Rule", "Reddit r/PSLF"):         +0.14,
    }

    # Write text artifact
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Comment-Level Cohort Heterogeneity Replication Test\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether the post-level cohort-heterogeneity finding (SDN-Medical\n")
        f.write("and Reddit-general respond opposite-sign on multiple PSLF events)\n")
        f.write("replicates at the COMMENT level.\n\n")
        f.write(f"Sample: {len(df):,} comments+SDN-equivalents with cohort labels.\n")
        f.write(f"Cell threshold: n_pre AND n_post >= {MIN_CELL_N}.\n\n")

        # TextBlob cells side by side with post-level
        f.write("TEXTBLOB CELL COMPARISON: post-level g vs comment-level g\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Event':<28s} {'Cohort':<26s} {'g_post':>7s} {'g_cmt':>7s} "
                f"{'Δ':>7s} {'n_cmt_pre/post':>16s} {'sig?':>5s}  Verdict\n")
        for (ev, coh), g_post in POST_LEVEL.items():
            row = tb[(tb["event"] == ev) & (tb["cohort"] == coh) &
                      (tb["scorer"] == "polarity")]
            if row.empty:
                f.write(f"{ev:<28s} {coh:<26s} {g_post:>+7.3f} {'n/a':>7s} "
                        f"{'n/a':>7s} {'underpowered':>16s} {'-':>5s}  COMMENT-CELL UNDERPOWERED\n")
                continue
            r = row.iloc[0]
            g_cmt = r["g"]
            delta = g_cmt - g_post
            sig = "***" if r["p_boot"] < 0.001 else "**" if r["p_boot"] < 0.01 else "*" if r["p_boot"] < 0.05 else ""
            # Verdict
            if np.sign(g_post) == np.sign(g_cmt) and abs(g_cmt) >= 0.5 * abs(g_post):
                verdict = "REPLICATES"
            elif np.sign(g_post) == np.sign(g_cmt):
                verdict = "WEAKER same-sign"
            elif abs(g_cmt) < 0.05:
                verdict = "NULL on comments"
            else:
                verdict = "REVERSED"
            f.write(f"{ev:<28s} {coh:<26s} {g_post:>+7.3f} {g_cmt:>+7.3f} "
                    f"{delta:>+7.3f} {f'{int(r[chr(110)+chr(95)+chr(112)+chr(114)+chr(101)])}/{int(r[chr(110)+chr(95)+chr(112)+chr(111)+chr(115)+chr(116)])}':>16s} "
                    f"{sig:>5s}  {verdict}\n")

        f.write("\n\nALL COMMENT-LEVEL CELLS (TextBlob)\n")
        f.write("-" * 80 + "\n")
        for ev_name, _, _ in EVENTS:
            sub = tb[(tb["event"] == ev_name) & (tb["scorer"] == "polarity")].sort_values("g")
            if len(sub) == 0:
                continue
            f.write(f"{ev_name}:\n")
            for _, r in sub.iterrows():
                sig = "***" if r["p_boot"] < 0.001 else "**" if r["p_boot"] < 0.01 else "*" if r["p_boot"] < 0.05 else ""
                f.write(f"  {r['cohort']:<26s} g={r['g']:+.3f} p_boot={r['p_boot']:.4f} {sig:>3s}  "
                        f"n={int(r['n_pre'])}/{int(r['n_post'])}\n")
            f.write("\n")

        # Replication verdict summary
        replicates = []
        weaker = []
        null = []
        reversed_cells = []
        underpowered = []
        for (ev, coh), g_post in POST_LEVEL.items():
            row = tb[(tb["event"] == ev) & (tb["cohort"] == coh) & (tb["scorer"] == "polarity")]
            if row.empty:
                underpowered.append((ev, coh))
                continue
            g_cmt = row.iloc[0]["g"]
            if np.sign(g_post) == np.sign(g_cmt) and abs(g_cmt) >= 0.5 * abs(g_post):
                replicates.append((ev, coh, g_post, g_cmt))
            elif np.sign(g_post) == np.sign(g_cmt):
                weaker.append((ev, coh, g_post, g_cmt))
            elif abs(g_cmt) < 0.05:
                null.append((ev, coh, g_post, g_cmt))
            else:
                reversed_cells.append((ev, coh, g_post, g_cmt))

        f.write("\nREPLICATION SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"  REPLICATES (same sign, magnitude >= 50% of post-level): {len(replicates)}\n")
        for ev, coh, gp, gc in replicates:
            f.write(f"    {ev:<30s} x {coh:<26s}  g_post={gp:+.3f}  g_cmt={gc:+.3f}\n")
        f.write(f"  WEAKER same-sign:                                       {len(weaker)}\n")
        for ev, coh, gp, gc in weaker:
            f.write(f"    {ev:<30s} x {coh:<26s}  g_post={gp:+.3f}  g_cmt={gc:+.3f}\n")
        f.write(f"  NULL on comments (post effect dies):                    {len(null)}\n")
        for ev, coh, gp, gc in null:
            f.write(f"    {ev:<30s} x {coh:<26s}  g_post={gp:+.3f}  g_cmt={gc:+.3f}\n")
        f.write(f"  REVERSED:                                               {len(reversed_cells)}\n")
        for ev, coh, gp, gc in reversed_cells:
            f.write(f"    {ev:<30s} x {coh:<26s}  g_post={gp:+.3f}  g_cmt={gc:+.3f}\n")
        f.write(f"  UNDERPOWERED (no comment cell, n<{MIN_CELL_N}):                       {len(underpowered)}\n")
        for ev, coh in underpowered:
            f.write(f"    {ev:<30s} x {coh:<26s}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")

    # Console summary
    print(f"\nReplication summary (TextBlob):")
    print(f"  REPLICATES:      {len(replicates)}")
    print(f"  WEAKER same-sign:{len(weaker)}")
    print(f"  NULL on comments:{len(null)}")
    print(f"  REVERSED:        {len(reversed_cells)}")
    print(f"  UNDERPOWERED:    {len(underpowered)}")


if __name__ == "__main__":
    main()
