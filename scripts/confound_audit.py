"""
confound_audit.py
=================
Round-3 audit follow-up: explicitly test for confounds in headline findings.

Tests:
  1. Platform-vs-population confound: stratify SDN-vs-Reddit comparison
     by profession (medical only) to isolate platform effect.
  2. Year × profession sampling confound: do professions have different
     year distributions that drive apparent sentiment differences?
  3. Length × polarity confound: regress polarity ~ word_count to see
     if observed effects are length-driven.
  4. Pre/post window length confound: are post-event windows systematically
     longer/shorter than pre-event, biasing polarity comparisons?

Output: confound_audit_results.txt
"""
from __future__ import annotations

import io
import os
import sys

# Force UTF-8 stdout so '×' and other non-ASCII chars survive redirect on Windows
# (otherwise cp1252 mangles them into '�' in the captured artifact file).
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import filter_pslf_relevant

MIN_WORDS = 20


def load_data():
    frames = []
    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teacher")]:
        if os.path.exists(f):
            df = pd.read_csv(f); df["profession"] = prof; df["platform"] = "Reddit"
            df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"), unit="s")
            df["text"] = df["combined_text"].fillna("")
            frames.append(df)

    pf = pd.read_csv("reddit_professions_pslf.csv")
    tm = filter_pslf_relevant(pf["combined_text"])
    tt = filter_pslf_relevant(pf["title"])
    pf = pf[tm | tt].copy()
    pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
    pf["text"] = pf["combined_text"].fillna(""); pf["platform"] = "Reddit"
    frames.append(pf)
    reddit = pd.concat(frames, ignore_index=True)
    reddit["date"] = pd.to_datetime(reddit["date"], utc=True).dt.tz_localize(None)

    sdn = pd.read_csv("forum_pslf_discussions.csv")
    bm = filter_pslf_relevant(sdn["body"])
    ttm = filter_pslf_relevant(sdn["thread_title"])
    sdn = sdn[bm | ttm].copy()
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn["text"] = sdn["body"].fillna("")
    sdn["profession"] = "sdn_medical"
    sdn["platform"] = "SDN"

    for df in (reddit, sdn):
        wc = df["text"].str.split().str.len()
        df["word_count"] = wc
        df.loc[wc < MIN_WORDS, "polarity"] = np.nan

    return reddit, sdn


def confound_1_platform_vs_population(reddit, sdn):
    """Compare medical-only Reddit vs SDN to isolate platform from population."""
    print("=" * 80)
    print("CONFOUND 1: Platform-vs-Population (SDN > Reddit polarity)")
    print("=" * 80)
    print("\nNaive comparison (all Reddit vs all SDN):")
    r_pol = reddit["polarity"].dropna()
    s_pol = sdn["polarity"].dropna()
    t, p = stats.ttest_ind(r_pol, s_pol, equal_var=False)
    print(f"  Reddit (all): n={len(r_pol):,}, pol={r_pol.mean():.4f}")
    print(f"  SDN: n={len(s_pol):,}, pol={s_pol.mean():.4f}")
    print(f"  Welch t={t:.3f}, p={p:.6f}")

    # Stratified: medical-only Reddit vs SDN (SDN is ~all medical)
    print("\nStratified (medical Reddit only vs SDN):")
    med_subs = ["Residency", "medicalschool"]
    rmed = reddit[(reddit["profession"] == "medical") |
                  (reddit["subreddit"].isin(med_subs) if "subreddit" in reddit.columns else False)]
    rmed_pol = rmed["polarity"].dropna()
    if len(rmed_pol) > 50:
        t2, p2 = stats.ttest_ind(rmed_pol, s_pol, equal_var=False)
        print(f"  Reddit medical: n={len(rmed_pol):,}, pol={rmed_pol.mean():.4f}")
        print(f"  SDN: n={len(s_pol):,}, pol={s_pol.mean():.4f}")
        print(f"  Welch t={t2:.3f}, p={p2:.6f}")
        naive_delta = s_pol.mean() - r_pol.mean()
        strat_delta = s_pol.mean() - rmed_pol.mean()
        print(f"  -> Naive delta={naive_delta:+.4f}; Stratified delta={strat_delta:+.4f}")
        # Round-7 fix: previous condition only fired when stratification HALVED
        # the effect (population was inflating the gap). Real-world case here is
        # the opposite — stratification GROWS the gap (population was suppressing
        # it). Either direction signals population confounding; check abs ratio
        # in either direction.
        if abs(naive_delta) > 0:
            ratio = abs(strat_delta) / abs(naive_delta)
            if ratio < 0.5:
                print("  [!]  CONFOUND DETECTED: Stratified effect is <50% of naive effect "
                      "(population was inflating the gap)")
                print("     The 'SDN > Reddit polarity' finding is largely population-driven.")
            elif ratio > 1.5:
                print("  [!]  CONFOUND DETECTED: Stratified effect is >150% of naive effect "
                      "(population was suppressing the gap)")
                print("     SDN > Reddit-medical platform gap is LARGER than naive comparison "
                      "suggested — population mix was masking platform effect.")


def confound_2_year_profession(reddit, sdn):
    """Do professions have different year distributions?"""
    print("\n" + "=" * 80)
    print("CONFOUND 2: Year × Profession sampling")
    print("=" * 80)
    reddit["year"] = reddit["date"].dt.year
    print("\nMedian year per profession (Reddit):")
    prof_years = reddit.groupby("profession")["year"].agg(["median", "count"]).sort_values("median")
    print(prof_years.to_string())
    range_med = prof_years["median"].max() - prof_years["median"].min()
    print(f"\nRange of median years: {range_med}")
    if range_med > 2:
        print("  [!]  CONFOUND: Some professions sampled from systematically different eras.")
        print("     Cross-profession sentiment comparisons may reflect time, not profession.")


def confound_3_length_polarity(reddit, sdn):
    """Is polarity correlated with word count?"""
    print("\n" + "=" * 80)
    print("CONFOUND 3: Length × Polarity")
    print("=" * 80)
    for label, df in [("Reddit", reddit), ("SDN", sdn)]:
        d = df.dropna(subset=["polarity", "word_count"])
        if len(d) > 100:
            r, p = stats.pearsonr(d["word_count"], d["polarity"])
            rho, p_s = stats.spearmanr(d["word_count"], d["polarity"])
            print(f"\n{label}:")
            print(f"  Pearson r(word_count, polarity) = {r:+.3f}, p={p:.6f}")
            print(f"  Spearman rho = {rho:+.3f}, p={p_s:.6f}")
            if abs(r) > 0.05 and p < 0.05:
                print("  [!]  Length-polarity correlation is significant.")
                print("     Cross-platform comparisons should adjust for word count.")


def confound_4_window_length(reddit, sdn):
    """Are pre-event windows systematically longer/shorter than post?"""
    print("\n" + "=" * 80)
    print("CONFOUND 4: Pre/post window mean word count")
    print("=" * 80)
    all_data = pd.concat([reddit[["date","polarity","word_count"]],
                          sdn[["date","polarity","word_count"]]], ignore_index=True)
    all_data = all_data.dropna(subset=["polarity"])
    events = [
        ("Limited PSLF Waiver", "2021-10-06", 90),
        ("IDR Account Adjustment", "2022-04-19", 90),
        ("Biden Mass Forgiveness", "2022-08-24", 90),
        ("Biden v. Nebraska SCOTUS", "2023-06-30", 90),
        ("Payments Restart", "2023-10-01", 90),
        ("SAVE Admin Forbearance", "2024-08-09", 90),
        ("Trump PSLF EO", "2025-03-07", 60),
        ("Final Trump PSLF Rule", "2025-10-30", 60),
    ]
    print(f"\n{'Event':<35s} {'Pre wc':>8s} {'Post wc':>8s} {'delta':>7s} {'p':>10s}")
    flagged = 0
    for name, date_str, win in events:
        dt = pd.Timestamp(date_str)
        pre = all_data[(all_data["date"] >= dt - pd.Timedelta(days=win)) & (all_data["date"] < dt)]
        post = all_data[(all_data["date"] >= dt) & (all_data["date"] <= dt + pd.Timedelta(days=win))]
        if len(pre) > 10 and len(post) > 10:
            t, p = stats.ttest_ind(pre["word_count"], post["word_count"], equal_var=False)
            d_wc = post["word_count"].mean() - pre["word_count"].mean()
            flag = " [!]" if p < 0.05 else ""
            if p < 0.05:
                flagged += 1
            print(f"{name:<35s} {pre['word_count'].mean():>8.0f} {post['word_count'].mean():>8.0f} "
                  f"{d_wc:>+7.0f} {p:>10.4f}{flag}")
    if flagged > 0:
        print(f"\n  [!]  {flagged}/{len(events)} events have significantly different pre/post word counts.")
        print("     Polarity differences may partly reflect length, not sentiment.")


def main():
    print("PSLF Confound Audit (Round-3 follow-up)\n")
    reddit, sdn = load_data()
    print(f"Loaded Reddit n={len(reddit):,}, SDN n={len(sdn):,}\n")

    confound_1_platform_vs_population(reddit, sdn)
    confound_2_year_profession(reddit, sdn)
    confound_3_length_polarity(reddit, sdn)
    confound_4_window_length(reddit, sdn)

    print("\n" + "=" * 80)
    print("SUMMARY: see [!] markers for detected confounds.")
    print("=" * 80)


if __name__ == "__main__":
    main()
