"""Final summary report for PSLF Discussion Analysis.

Round-5 update: aligned with canonical 8-event list from
gen_legislative_timeline.py; added length-residualised analysis, Glass's
delta_pre, and dynamic date stamp. The canonical headline numbers live in
legislative_timeline_results.txt — this script is a top-level overview.

Output is teed to stdout AND a persistent artifact file (default
final_summary_report.txt) so the summary is tracked alongside the other
*_results.txt artifacts.
"""
import argparse
import io
import os
import sys
import warnings
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")


class _Tee:
    """Write to multiple streams (stdout + file). Lightweight; no buffering tricks."""
    def __init__(self, *streams):
        self._streams = streams

    def write(self, data):
        for s in self._streams:
            s.write(data)

    def flush(self):
        for s in self._streams:
            try:
                s.flush()
            except Exception:
                pass

import numpy as np
import pandas as pd
from scipy import stats

from pslf_search_terms import filter_pslf_relevant

MIN_WORDS = 20
W = 80


def load():
    frames = []
    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teacher")]:
        if os.path.exists(f):
            df = pd.read_csv(f)
            df["profession"] = prof
            df["platform"] = "Reddit"
            df["source"] = "reddit"
            df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"), unit="s")
            df["text"] = df["combined_text"].fillna("")
            frames.append(df)

    if os.path.exists("reddit_professions_pslf.csv"):
        pf = pd.read_csv("reddit_professions_pslf.csv")
        tm = filter_pslf_relevant(pf["combined_text"])
        tt = filter_pslf_relevant(pf["title"])
        pf = pf[tm | tt].copy()
        pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
        pf["text"] = pf["combined_text"].fillna("")
        pf["platform"] = "Reddit"
        pf["source"] = "reddit_prof"
        frames.append(pf)

    reddit = pd.concat(frames, ignore_index=True)
    reddit["date"] = pd.to_datetime(reddit["date"], utc=True).dt.tz_localize(None)
    wc = reddit["text"].str.split().str.len()
    reddit["word_count"] = wc
    reddit.loc[wc < MIN_WORDS, "polarity"] = np.nan
    if "vader_compound" in reddit.columns:
        reddit.loc[wc < MIN_WORDS, "vader_compound"] = np.nan

    sdn = pd.read_csv("forum_pslf_discussions.csv")
    bm = filter_pslf_relevant(sdn["body"])
    ttm = filter_pslf_relevant(sdn["thread_title"])
    sdn = sdn[bm | ttm].copy()
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn["text"] = sdn["body"].fillna("")
    sdn["platform"] = "SDN Forum"
    sdn["profession"] = "sdn_medical"
    sdn["source"] = "sdn"
    wc2 = sdn["text"].str.split().str.len()
    sdn["word_count"] = wc2
    sdn.loc[wc2 < MIN_WORDS, "polarity"] = np.nan

    return reddit, sdn


def length_residualise(combined):
    """Regress polarity ~ log(word_count) + source + profession; return residuals."""
    d = combined.dropna(subset=["polarity"]).copy()
    d["log_wc"] = np.log1p(d["word_count"])
    src_dum = pd.get_dummies(d["source"], prefix="src", drop_first=True, dtype=float)
    prof_dum = pd.get_dummies(d["profession"], prefix="prof", drop_first=True, dtype=float)
    X = pd.concat([pd.Series(1.0, index=d.index, name="intercept"),
                   d["log_wc"], src_dum, prof_dum], axis=1).to_numpy(dtype=float)
    # QR rank check (round-5 fix: drop perfect collinearity, e.g. src_sdn ≡ prof_sdn_medical)
    _, R = np.linalg.qr(X)
    rank_tol = max(R.shape) * np.spacing(np.linalg.norm(X))
    keep = np.abs(np.diag(R)) > rank_tol
    X = X[:, keep]
    y = d["polarity"].to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    d["polarity_resid"] = y - X @ beta
    return d


def hedges_g(pre, post):
    n1, n2 = len(pre), len(post)
    if n1 < 2 or n2 < 2:
        return float("nan")
    v1, v2 = float(pre.var(ddof=1)), float(post.var(ddof=1))
    sp = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    if sp <= 0:
        return 0.0
    d_cohen = (post.mean() - pre.mean()) / sp
    J = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    return d_cohen * J


def glass_delta_pre(pre, post):
    pre_sd = float(pre.std(ddof=1)) if len(pre) >= 2 else 0.0
    if pre_sd <= 0:
        return 0.0
    return (post.mean() - pre.mean()) / pre_sd


# Canonical 8-event list (matches gen_legislative_timeline.py)
EVENTS = [
    ("Limited PSLF Waiver", "2021-10-06", 90),
    ("IDR Account Adjustment", "2022-04-19", 90),
    ("Biden Mass Forgiveness", "2022-08-24", 90),
    ("Biden v. Nebraska SCOTUS", "2023-06-30", 90),
    ("Payments Restart", "2023-10-01", 90),
    ("SAVE Admin Forbearance", "2024-08-09", 90),
    ("Trump PSLF Exec Order", "2025-03-07", 60),
    ("Final Trump PSLF Rule", "2025-10-30", 60),
]


def main():
    parser = argparse.ArgumentParser(description="Final summary report for PSLF Discussion Analysis")
    parser.add_argument("--out", default="final_summary_report.txt",
                        help="Path for persistent artifact (default: final_summary_report.txt). "
                             "Pass empty string to skip writing a file.")
    parser.add_argument("--no-stdout", action="store_true",
                        help="Suppress stdout; only write to --out file.")
    args = parser.parse_args()

    # Tee stdout to a file artifact so the summary is captured like other *_results.txt
    if args.out:
        out_f = open(args.out, "w", encoding="utf-8")
        if args.no_stdout:
            sys.stdout = out_f
        else:
            sys.stdout = _Tee(sys.stdout, out_f)

    reddit, sdn = load()
    total = len(reddit) + len(sdn)
    valid = reddit["polarity"].notna().sum() + sdn["polarity"].notna().sum()

    print("=" * W)
    print("PSLF DISCUSSION ANALYSIS: FINAL SUMMARY REPORT")
    print("=" * W)
    print(f"Generated: {date.today().isoformat()}")
    print(f"Total posts: {total:,} ({len(reddit):,} Reddit + {len(sdn):,} SDN)")
    print(f"After sentiment filter (>={MIN_WORDS} words): {valid:,}")
    print("Platforms: 20 communities (18 subreddits + SDN forum)")
    print("Scoring: TextBlob polarity + VADER compound (dual)")
    print("Scope: online PSLF discourse, not the borrower population.")

    # === 1. Profession breakdown ===
    print(f"\n{'=' * W}")
    print("1. PROFESSION BREAKDOWN (PSLF-filtered, TextBlob)")
    print("=" * W)
    prof_stats = reddit.groupby("profession")["polarity"].agg(
        valid=lambda x: x.notna().sum(),
        mean=lambda x: x.dropna().mean(),
        pct_neg=lambda x: (x.dropna() < 0).mean() * 100,
    ).sort_values("pct_neg", ascending=False)
    print(f"\n  {'Profession':30s} {'n':>6s} {'Polarity':>9s} {'%Neg':>7s}")
    print(f"  {'-' * 54}")
    for prof, row in prof_stats.iterrows():
        if row["valid"] >= 20:
            print(f"  {prof:30s} {int(row['valid']):6d} {row['mean']:9.4f} {row['pct_neg']:6.1f}%")
    s_pol = sdn["polarity"].dropna()
    print(f"  {'SDN Forum':30s} {len(s_pol):6d} {s_pol.mean():9.4f} {(s_pol < 0).mean() * 100:6.1f}%")

    # === 2. Policy events (length-adjusted) ===
    print(f"\n{'=' * W}")
    print("2. POLICY EVENT IMPACTS (canonical 8 events; raw + length-residualised)")
    print("=" * W)
    print("  Pre/post is associational, NOT causal (no ITS counterfactual).")
    print(f"  Bonferroni alpha across 8 tests: {0.05 / 8:.4f}")

    combined_cols = ["date", "polarity", "word_count", "source", "profession"]
    combined = pd.concat([reddit[combined_cols], sdn[combined_cols]],
                         ignore_index=True).dropna(subset=["date", "polarity"])
    combined_resid = length_residualise(combined)

    print(f"\n  {'Event':<28s} {'date':<11s} {'win':>4s} "
          f"{'g_raw':>7s} {'g_resid':>8s} {'glass':>7s} {'p':>9s} {'Bonf':>5s}")
    alpha_b = 0.05 / 8
    for name, date_str, window in EVENTS:
        dt = pd.Timestamp(date_str)
        pre_r = combined_resid[(combined_resid["date"] >= dt - pd.Timedelta(days=window)) &
                               (combined_resid["date"] < dt)]
        post_r = combined_resid[(combined_resid["date"] >= dt) &
                                (combined_resid["date"] <= dt + pd.Timedelta(days=window))]
        if len(pre_r) < 10 or len(post_r) < 10:
            print(f"  {name:<28s} {date_str:<11s} {window:>4d}   insufficient data")
            continue
        g_raw = hedges_g(pre_r["polarity"], post_r["polarity"])
        g_res = hedges_g(pre_r["polarity_resid"], post_r["polarity_resid"])
        gd = glass_delta_pre(pre_r["polarity"], post_r["polarity"])
        _, p_param = stats.ttest_ind(pre_r["polarity"], post_r["polarity"], equal_var=False)
        bonf = "Y" if p_param < alpha_b else "n"
        print(f"  {name:<28s} {date_str:<11s} {window:>4d} "
              f"{g_raw:>+7.3f} {g_res:>+8.3f} {gd:>+7.3f} {p_param:>9.4f} {bonf:>5s}")
    print("\n  See legislative_timeline_results.txt for bootstrap p-values "
          "and per-event detail.")

    # === 3. Present day ===
    print(f"\n{'=' * W}")
    print("3. PRESENT DAY")
    print("=" * W)
    today = pd.Timestamp(date.today())
    last30 = combined[combined["date"] >= today - pd.Timedelta(days=30)]
    baseline = combined[(combined["date"] >= "2024-06-01") & (combined["date"] < "2025-01-01")]
    peak = combined[(combined["date"] >= "2021-10-06") & (combined["date"] <= "2022-01-31")]
    for label, df in [("Last 30 days", last30),
                      ("2024 H2 baseline", baseline),
                      ("Post-waiver peak (2021-10 to 2022-01)", peak)]:
        n = len(df)
        if n == 0:
            print(f"  {label}: n=0")
            continue
        print(f"  {label:38s} n={n:6,d}, polarity={df['polarity'].mean():+.4f}, "
              f"%neg={(df['polarity'] < 0).mean() * 100:.1f}%")
    if len(last30) >= 10 and len(baseline) >= 10:
        t, p = stats.ttest_ind(last30["polarity"], baseline["polarity"], equal_var=False)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"\n  Present vs 2024H2: t={t:+.3f}, p={p:.6f} {sig}")

    # === 4. Platform comparison ===
    print(f"\n{'=' * W}")
    print("4. PLATFORM COMPARISON (raw + length-adjusted note)")
    print("=" * W)
    r_pol = reddit["polarity"].dropna()
    t, p = stats.ttest_ind(r_pol, s_pol, equal_var=False)
    print(f"  Reddit: n={len(r_pol):,}, pol={r_pol.mean():+.4f}, "
          f"%neg={(r_pol < 0).mean() * 100:.1f}%, "
          f"mean words={reddit['text'].str.split().str.len().mean():.0f}")
    print(f"  SDN:    n={len(s_pol):,}, pol={s_pol.mean():+.4f}, "
          f"%neg={(s_pol < 0).mean() * 100:.1f}%, "
          f"mean words={sdn['text'].str.split().str.len().mean():.0f}")
    print(f"  Welch t={t:+.3f}, p={p:.6f}")
    print("  NOTE: cross-platform delta is confounded with population (SDN is medical-only)")
    print("        and post length. See confound_audit_results.txt.")

    if "vader_compound" in reddit.columns:
        r_v = reddit["vader_compound"].dropna()
        s_v = sdn["vader_compound"].dropna() if "vader_compound" in sdn.columns else pd.Series(dtype=float)
        if len(r_v) > 0 and len(s_v) > 0:
            print("\n  VADER comparison:")
            print(f"    Reddit VADER: mean={r_v.mean():+.4f}, %neg={(r_v < -0.05).mean() * 100:.1f}%")
            print(f"    SDN VADER:    mean={s_v.mean():+.4f}, %neg={(s_v < -0.05).mean() * 100:.1f}%")
            corr_r = reddit[["polarity", "vader_compound"]].dropna().corr().iloc[0, 1]
            print(f"    TextBlob-VADER r={corr_r:.3f} (Reddit) — weak agreement.")

    # === 5. Outputs ===
    print(f"\n{'=' * W}")
    print("5. OUTPUTS")
    print("=" * W)
    artifacts = [
        "multi_source_sentiment_comparison.png",
        "pslf_wordcloud_timecourse.png",
        "pslf_sentiment_legislative_timeline.png",
        "pslf_pre_post_events.png",
        "pslf_profession_timecourse.png",
        "legislative_timeline_results.txt",
        "legislative_timeline_results.csv",
        "admin_correlation_results.txt",
        "confound_audit_results.txt",
    ]
    for f in artifacts:
        if os.path.exists(f):
            sz = os.path.getsize(f) / 1024 / 1024
            print(f"  {f}: {sz:.2f} MB")
        else:
            print(f"  {f}: [missing]")

    print(f"\n{'=' * W}")
    print("6. REPOSITORY")
    print("=" * W)
    print("  Fork: https://github.com/zanecn/PSLF-Discussion-Analysis")
    print("  PR: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis/pull/1")
    print("  Branch: playwright-sdn-scraper")
    print("=" * W)


if __name__ == "__main__":
    main()
