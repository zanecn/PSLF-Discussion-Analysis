"""
analyze_per_author_with_comments.py
=====================================
Re-evaluates per-author longitudinal panel feasibility AND within-person
stance dynamics by adding COMMENTS to the per-author observation set.

Round 8 found: at the post level, only 1/8 events (Trump EO) meets n>=10
returning-with-stance authors. Author overlap 18-42% across events.

This script asks: when we count an author as "present in event window" if
they posted EITHER an OP or a comment in that window, do more events become
feasible? And do the within-person stance shifts that emerge tell a different
story than the pooled composition shifts?

Key methodological choice: stance must come from a Claude-scored OP because
comments don't have stance labels. So a returning author needs:
- An OP in pre-window with Claude stance label, AND
- An OP in post-window with Claude stance label, OR
- An OP in EITHER window plus comments in the OTHER window (showing they
  were present and engaged but didn't post a stance-classifiable OP)

For the most rigorous within-person stance comparison, we still need pre+post
OPs with stance. The expanded observation set helps with PRESENCE but not
with stance classification.

Outputs:
  - per_author_with_comments_results.{txt,csv}
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

import numpy as np
import pandas as pd
from scipy import stats

EVENTS = [
    ("Limited PSLF Waiver",            "2021-10-06", 90),
    ("IDR Account Adjustment",         "2022-04-19", 90),
    ("Biden Mass Forgiveness",         "2022-08-24", 90),
    ("Biden v. Nebraska SCOTUS",       "2023-06-30", 90),
    ("Payments Restart",               "2023-10-01", 90),
    ("SAVE Admin Forbearance",         "2024-08-09", 90),
    ("Trump PSLF EO",                  "2025-03-07", 60),
    ("Final Trump PSLF Rule",          "2025-10-30", 60),
]

ZEROSHOT_CSVS = [
    "zeroshot_reddit_n1000.csv",
    "zeroshot_sdn_n1000.csv",
    "zeroshot_reddit_eventstrat.csv",
    "zeroshot_reddit_eventfull.csv",
    "zeroshot_sdn_eventfull.csv",
    "zeroshot_pa_np_expansion.csv",
    "zeroshot_reddit_fullcorpus.csv",
    "zeroshot_reddit_arctic_shift_fill.csv",
]

OUT_TXT = "per_author_with_comments_results.txt"
OUT_CSV = "per_author_with_comments_results.csv"


def load_posts_with_authors_and_stance() -> pd.DataFrame:
    """Load all PSLF posts with author + date + Claude stance (where scored)."""
    # Load Claude-scored stances
    cl_frames = []
    for f in ZEROSHOT_CSVS:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        d = d[~d["pslf_sentiment"].isin(["parse_error", "api_error"])]
        d = d[~d.get("pslf_stance", pd.Series(dtype=str)).fillna("unknown").isin(["unknown", ""])]
        if "post_id" not in d.columns or "pslf_stance" not in d.columns:
            continue
        cl_frames.append(d[["post_id", "pslf_stance"]])
    cl = pd.concat(cl_frames, ignore_index=True).drop_duplicates("post_id")
    print(f"  Claude-stance-classified posts: {len(cl):,}")

    # Load post sources with authors
    post_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv",
              "reddit_new_subs_pslf.csv",
              "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        if "id" in d.columns:
            d = d.rename(columns={"id": "post_id"})
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        keep = ["post_id", "author", "date"]
        if "subreddit" in d.columns:
            keep.append("subreddit")
        post_frames.append(d[keep])
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        d["subreddit"] = "sdn"
        post_frames.append(d[["post_id", "author", "date", "subreddit"]])

    posts = pd.concat(post_frames, ignore_index=True).drop_duplicates("post_id")
    posts["post_id"] = posts["post_id"].astype(str)
    cl["post_id"] = cl["post_id"].astype(str)
    posts = posts.merge(cl, on="post_id", how="left")
    posts = posts.dropna(subset=["author", "date"])
    posts = posts[~posts["author"].isin(["[deleted]", "AutoModerator", ""])]
    print(f"  Total non-deleted authored posts: {len(posts):,}")
    print(f"  Posts with Claude stance:         {posts['pslf_stance'].notna().sum():,}")
    return posts


def load_comments_with_authors() -> pd.DataFrame:
    """Comments with author + date for presence-tracking only (no stance)."""
    if not os.path.exists("reddit_comments_pslf.csv"):
        return pd.DataFrame()
    cm = pd.read_csv("reddit_comments_pslf.csv", low_memory=False)
    cm["date"] = pd.to_datetime(pd.to_numeric(cm["created_utc"], errors="coerce"), unit="s")
    cm = cm.dropna(subset=["author", "date"])
    cm = cm[~cm["author"].isin(["[deleted]", "AutoModerator", ""])]
    print(f"  Total non-deleted authored comments: {len(cm):,}")
    return cm


def author_overlap_per_event(posts: pd.DataFrame, comments: pd.DataFrame) -> pd.DataFrame:
    """Count author overlap pre/post for each event, both posts-only and posts+comments."""
    rows = []
    for ev_name, ev_date, win in EVENTS:
        dt = pd.Timestamp(ev_date)
        # Posts-only
        pre_p = posts[(posts["date"] >= dt - pd.Timedelta(days=win)) & (posts["date"] < dt)]
        post_p = posts[(posts["date"] >= dt) & (posts["date"] <= dt + pd.Timedelta(days=win))]
        pre_authors_p = set(pre_p["author"])
        post_authors_p = set(post_p["author"])
        overlap_p = pre_authors_p & post_authors_p

        # Posts + comments (presence)
        pre_c = comments[(comments["date"] >= dt - pd.Timedelta(days=win)) & (comments["date"] < dt)]
        post_c = comments[(comments["date"] >= dt) & (comments["date"] <= dt + pd.Timedelta(days=win))]
        pre_authors_pc = pre_authors_p | set(pre_c["author"])
        post_authors_pc = post_authors_p | set(post_c["author"])
        overlap_pc = pre_authors_pc & post_authors_pc

        # Stance-classifiable overlap (still needs Claude-stance OP in BOTH windows)
        pre_stance = pre_p[pre_p["pslf_stance"].notna()]
        post_stance = post_p[post_p["pslf_stance"].notna()]
        ret_with_stance = set(pre_stance["author"]) & set(post_stance["author"])

        # Stance-classifiable + comment-presence overlap (returning by either modality)
        # Not directly used for within-person stance but useful for context
        pre_stance_or_cmt = set(pre_stance["author"]) | set(pre_c["author"])
        post_stance_or_cmt = set(post_stance["author"]) | set(post_c["author"])
        ret_present = pre_stance_or_cmt & post_stance_or_cmt

        rows.append({
            "event": ev_name,
            "n_pre_post_only": len(pre_authors_p),
            "n_post_post_only": len(post_authors_p),
            "overlap_post_only": len(overlap_p),
            "pct_overlap_post_only": (100*len(overlap_p)/max(len(pre_authors_p|post_authors_p),1)),
            "n_pre_with_cmt": len(pre_authors_pc),
            "n_post_with_cmt": len(post_authors_pc),
            "overlap_with_cmt": len(overlap_pc),
            "pct_overlap_with_cmt": (100*len(overlap_pc)/max(len(pre_authors_pc|post_authors_pc),1)),
            "returning_with_stance": len(ret_with_stance),  # both windows have stance OP
            "returning_present_either": len(ret_present),
        })
    return pd.DataFrame(rows)


def within_person_stance_shift(posts: pd.DataFrame, event: str,
                                  ev_date: str, window: int) -> dict:
    """For each author with a stance-classifiable OP in BOTH pre and post windows,
    compute their within-person stance change (was rejecting -> now pursuing? etc.)
    """
    dt = pd.Timestamp(ev_date)
    pre = posts[(posts["date"] >= dt - pd.Timedelta(days=window)) & (posts["date"] < dt)
                & posts["pslf_stance"].notna()]
    post = posts[(posts["date"] >= dt) & (posts["date"] <= dt + pd.Timedelta(days=window))
                  & posts["pslf_stance"].notna()]

    # Get the LAST stance per author per window (in case they posted multiple times)
    pre_stance = pre.sort_values("date").groupby("author")["pslf_stance"].last()
    post_stance = post.sort_values("date").groupby("author")["pslf_stance"].last()

    # Returning authors with stance in BOTH windows
    common_authors = set(pre_stance.index) & set(post_stance.index)
    n_returning = len(common_authors)

    if n_returning < 5:
        return {"n_returning": n_returning, "feasible": False,
                "rejecting_pre": np.nan, "rejecting_post": np.nan,
                "delta_rejecting_pp": np.nan, "mcnemar_p": np.nan,
                "to_rejecting": 0, "from_rejecting": 0, "stable": 0}

    # Within-person counts
    pre_rej = pre_stance.loc[list(common_authors)] == "rejecting"
    post_rej = post_stance.loc[list(common_authors)] == "rejecting"

    pre_rej_count = pre_rej.sum()
    post_rej_count = post_rej.sum()
    delta = (post_rej_count - pre_rej_count) / n_returning * 100

    # McNemar's test on stance change matrix
    # b = # who went rejecting -> not rejecting
    # c = # who went not rejecting -> rejecting
    b = ((pre_rej) & (~post_rej)).sum()
    c = ((~pre_rej) & (post_rej)).sum()
    stable = ((pre_rej == post_rej)).sum()

    # McNemar's p
    if b + c >= 5:
        mc_stat = (abs(b - c) - 1)**2 / (b + c) if (b + c) > 0 else 0
        mc_p = 1 - stats.chi2.cdf(mc_stat, df=1)
    else:
        # Use exact binomial
        if b + c > 0:
            mc_p = stats.binomtest(min(b, c), b + c, p=0.5).pvalue
        else:
            mc_p = 1.0

    return {
        "n_returning": n_returning,
        "feasible": n_returning >= 10,
        "rejecting_pre": float(pre_rej_count) / n_returning * 100,
        "rejecting_post": float(post_rej_count) / n_returning * 100,
        "delta_rejecting_pp": delta,
        "mcnemar_p": float(mc_p),
        "to_rejecting": int(c),
        "from_rejecting": int(b),
        "stable": int(stable),
    }


def main():
    print("=" * 80)
    print("Per-Author Longitudinal Re-Evaluation with Comments")
    print("=" * 80)

    print("\nLoading posts...")
    posts = load_posts_with_authors_and_stance()
    print("\nLoading comments...")
    comments = load_comments_with_authors()

    print("\nComputing author overlap per event (posts-only vs posts+comments)...")
    overlap_df = author_overlap_per_event(posts, comments)

    print("\nComputing within-person stance shifts...")
    stance_rows = []
    for ev_name, ev_date, win in EVENTS:
        d = within_person_stance_shift(posts, ev_name, ev_date, win)
        d["event"] = ev_name
        stance_rows.append(d)
    stance_df = pd.DataFrame(stance_rows)

    # Merge for output
    merged = overlap_df.merge(stance_df, on="event")
    merged.to_csv(OUT_CSV, index=False, float_format="%.4f")

    # Text report
    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("Per-Author Longitudinal Re-Evaluation (with comments expansion)\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Round 8 found per-author longitudinal panel infeasible for 7/8 events\n")
        f.write("at post-level. This re-evaluation:\n")
        f.write("  - Adds comments to the author-presence universe (does adding comments\n")
        f.write("    expand author overlap meaningfully?)\n")
        f.write("  - Recomputes within-person stance shifts (which still require\n")
        f.write("    Claude-stance OPs in BOTH pre and post windows)\n\n")

        f.write("AUTHOR OVERLAP COMPARISON: posts-only vs posts+comments\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Event':<28s} {'pct_post':>9s} {'pct_p+c':>8s} "
                f"{'n_ret_stance':>14s} {'verdict':<25s}\n")
        for _, r in merged.iterrows():
            v = "FEASIBLE (n>=10)" if r["returning_with_stance"] >= 10 else "INFEASIBLE (n<10)"
            f.write(f"{r['event']:<28s} {r['pct_overlap_post_only']:>9.1f} "
                    f"{r['pct_overlap_with_cmt']:>8.1f} "
                    f"{int(r['returning_with_stance']):>14d} {v:<25s}\n")

        f.write("\nWITHIN-PERSON STANCE SHIFT (returning authors with Claude OP in both windows)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Event':<28s} {'n_ret':>6s} {'rej_pre%':>9s} {'rej_post%':>9s} "
                f"{'Δpp':>6s} {'McNm_p':>7s} {'to_rej':>7s} {'from_rej':>9s} {'stable':>7s}\n")
        for _, r in merged.iterrows():
            n = int(r["n_returning"])
            if n < 5:
                f.write(f"{r['event']:<28s} {n:>6d} {'-':>9s} {'-':>9s} {'-':>6s} "
                        f"{'-':>7s} {'-':>7s} {'-':>9s} {'-':>7s}\n")
                continue
            f.write(f"{r['event']:<28s} {n:>6d} {r['rejecting_pre']:>8.1f}%{r['rejecting_post']:>8.1f}%"
                    f"{r['delta_rejecting_pp']:>+6.1f} {r['mcnemar_p']:>7.4f} "
                    f"{int(r['to_rejecting']):>7d} {int(r['from_rejecting']):>9d} {int(r['stable']):>7d}\n")

        # Summary
        n_feasible_post = (merged["returning_with_stance"] >= 10).sum()
        f.write(f"\nFEASIBILITY SUMMARY (Round 8 post-level threshold)\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Events meeting n>=10 returning-with-stance: {n_feasible_post}/8\n")
        f.write(f"  (Round 8 post-level result: 1/8; comments don't help directly because\n")
        f.write(f"   stance still requires a Claude-scored OP in both windows.)\n\n")

        f.write(f"  Events where ADDING comments raised author overlap >5pp:\n")
        big_help = merged[(merged["pct_overlap_with_cmt"] - merged["pct_overlap_post_only"]) > 5]
        if len(big_help) == 0:
            f.write("    (none) - comments don't substantially expand author-presence overlap\n")
        else:
            for _, r in big_help.iterrows():
                f.write(f"    {r['event']:<28s} {r['pct_overlap_post_only']:>5.1f}% -> "
                        f"{r['pct_overlap_with_cmt']:>5.1f}%  (+{r['pct_overlap_with_cmt']-r['pct_overlap_post_only']:.1f}pp)\n")

        f.write("\nWITHIN-PERSON STANCE SHIFTS: SIGNIFICANT MOVEMENTS\n")
        f.write("-" * 80 + "\n")
        f.write("  Cells where McNemar p<0.05 with n_returning>=10:\n")
        sig = merged[(merged["n_returning"] >= 10) & (merged["mcnemar_p"] < 0.05)]
        if len(sig) == 0:
            f.write("    (none) - no Bonferroni-uncorrected significant within-person shifts\n")
        else:
            for _, r in sig.iterrows():
                f.write(f"    {r['event']:<28s} n={int(r['n_returning'])} "
                        f"Δrej={r['delta_rejecting_pp']:+.1f}pp McNemar p={r['mcnemar_p']:.4f}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"\nSaved: {OUT_TXT}")
    print(f"Saved: {OUT_CSV}")
    print()
    print("Quick summary:")
    print(merged[["event", "pct_overlap_post_only", "pct_overlap_with_cmt",
                   "returning_with_stance"]].to_string(index=False))


if __name__ == "__main__":
    main()
