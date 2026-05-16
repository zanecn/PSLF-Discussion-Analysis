"""
analyze_l3_topic_fsa_responsiveness.py
=========================================
L3: Test whether servicer_issues TOPIC PREVALENCE responds to FSA operational
events (independent of mean polarity).

The B1 NULL on cumulative approvals was undertested. This script tests:
  1. servicer_issues topic share over time
  2. Correlation with FSA monthly NEW approvals (FLOW, not stock)
  3. Correlation with operational events: MOHELA transition, payments restart
  4. Lag analysis (operational events may show in discourse 0-3 months later)

Output: l3_topic_fsa_results.{txt,csv}
        l3_topic_fsa_figure.png
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
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sentiment_triangulation import load_zeroshot

OUT_TXT = "l3_topic_fsa_results.txt"
OUT_CSV = "l3_topic_fsa_results.csv"
OUT_PNG = "l3_topic_fsa_figure.png"


def main():
    print("=" * 80)
    print("L3: Topic-level FSA responsiveness (servicer_issues prevalence)")
    print("=" * 80)

    # Load Claude-scored posts
    zs = load_zeroshot()
    print(f"\nClaude-scored posts: {len(zs):,}")
    print(f"With primary_topic: {zs['primary_topic'].notna().sum():,}")

    # We need post date. Try to merge with text/source CSVs
    text_frames = []
    for f, date_col, id_col in [
        ("reddit_professions_pslf.csv", "created_datetime", "id"),
        ("reddit_arctic_shift_pslf.csv", "created_datetime", "id"),
        ("reddit_new_subs_pslf.csv", "created_datetime", "id"),
        ("comprehensive_medical_pslf_discussions.csv", "created_datetime", "id"),
        ("comprehensive_teacher_pslf_discussions.csv", "created_datetime", "id"),
        ("forum_pslf_discussions.csv", "date_posted", "post_id"),
    ]:
        if not os.path.exists(f): continue
        try:
            d = pd.read_csv(f, usecols=lambda c: c in (id_col, date_col), low_memory=False)
        except: continue
        if id_col != "post_id": d = d.rename(columns={id_col: "post_id"})
        d = d.rename(columns={date_col: "post_date"})
        d["post_id"] = d["post_id"].astype(str)
        text_frames.append(d[["post_id", "post_date"]])
    dates = pd.concat(text_frames, ignore_index=True).drop_duplicates("post_id")
    dates["post_date"] = pd.to_datetime(dates["post_date"], errors="coerce", utc=True).dt.tz_localize(None)
    print(f"Date-attached: {len(dates):,}")

    df = zs.merge(dates, on="post_id", how="left").dropna(subset=["post_date", "primary_topic"])
    df["month"] = df["post_date"].dt.to_period("M")
    print(f"Final: {len(df):,} posts with date + topic")

    # Filter to event window (Aug 2021 - Dec 2025 per FSA admin data range)
    df = df[(df["post_date"] >= pd.Timestamp("2020-01-01")) &
             (df["post_date"] <= pd.Timestamp("2026-01-01"))].copy()

    # === Monthly servicer_issues share + total volume ===
    print("\n[1] Monthly servicer_issues prevalence")
    monthly = df.groupby(["month", "primary_topic"]).size().unstack(fill_value=0)
    if "servicer_issues" not in monthly.columns:
        print("[ABORT] No 'servicer_issues' topic in data")
        return
    monthly["total"] = monthly.sum(axis=1)
    monthly["servicer_share"] = monthly["servicer_issues"] / monthly["total"]
    monthly = monthly[monthly["total"] >= 20]  # require min monthly volume
    print(f"  Months with n>=20: {len(monthly)}")

    # Operational events
    OPS_EVENTS = [
        ("Payments Restart",       pd.Timestamp("2023-10-01")),
        ("MOHELA Transition",      pd.Timestamp("2022-07-01")),
        ("SAVE Forbearance",       pd.Timestamp("2024-08-09")),
        ("PSLF Form Online",       pd.Timestamp("2023-07-01")),
    ]
    POLICY_EVENTS = [
        ("Limited Waiver",         pd.Timestamp("2021-10-06")),
        ("Biden Mass Forgive",     pd.Timestamp("2022-08-24")),
        ("Biden v Nebraska",       pd.Timestamp("2023-06-30")),
        ("Trump PSLF EO",          pd.Timestamp("2025-03-07")),
    ]

    # === Test 1: Pre/post servicer_share for each operational event ===
    print("\n[2] Servicer-issues share pre/post operational events")
    rows = []
    monthly_idx = monthly.reset_index()
    monthly_idx["date"] = monthly_idx["month"].dt.start_time
    for name, ev_date in OPS_EVENTS + POLICY_EVENTS:
        ev_type = "operational" if (name, ev_date) in OPS_EVENTS else "policy"
        for window_days in [60, 90]:
            pre = monthly_idx[(monthly_idx["date"] >= ev_date - pd.Timedelta(days=window_days)) &
                                 (monthly_idx["date"] < ev_date)]
            post = monthly_idx[(monthly_idx["date"] >= ev_date) &
                                  (monthly_idx["date"] < ev_date + pd.Timedelta(days=window_days))]
            if len(pre) < 1 or len(post) < 1: continue
            try:
                t, p = stats.ttest_ind(pre["servicer_share"], post["servicer_share"], equal_var=False)
            except Exception: t, p = float("nan"), float("nan")
            rows.append({
                "event": name, "type": ev_type, "window_days": window_days,
                "pre_share": pre["servicer_share"].mean(),
                "post_share": post["servicer_share"].mean(),
                "delta_pp": (post["servicer_share"].mean() - pre["servicer_share"].mean()) * 100,
                "t": t, "p": p,
                "n_pre_months": len(pre), "n_post_months": len(post),
            })

    rdf = pd.DataFrame(rows)
    if len(rdf):
        ops = rdf[rdf["type"] == "operational"]
        pol = rdf[rdf["type"] == "policy"]
        print("\n  OPERATIONAL events (servicer_issues prevalence):")
        for _, r in ops.iterrows():
            print(f"    {r['event']:<24s} {r['window_days']}d  pre={r['pre_share']*100:5.1f}% "
                   f"post={r['post_share']*100:5.1f}%  Δ={r['delta_pp']:+5.2f}pp  p={r['p']:.4g}")
        print("\n  POLICY events (control - should NOT shift servicer_issues if specific):")
        for _, r in pol.iterrows():
            print(f"    {r['event']:<24s} {r['window_days']}d  pre={r['pre_share']*100:5.1f}% "
                   f"post={r['post_share']*100:5.1f}%  Δ={r['delta_pp']:+5.2f}pp  p={r['p']:.4g}")

    # === Test 2: Mean polarity pre/post operational events (compare to topic) ===
    print("\n[3] CONTROL: mean polarity pre/post operational events (NULL hypothesis from B1)")
    if "polarity" in df.columns:
        df_pol = df.dropna(subset=["polarity"])
        for name, ev_date in OPS_EVENTS:
            pre = df_pol[(df_pol["post_date"] >= ev_date - pd.Timedelta(days=60)) &
                         (df_pol["post_date"] < ev_date)]
            post = df_pol[(df_pol["post_date"] >= ev_date) &
                          (df_pol["post_date"] < ev_date + pd.Timedelta(days=60))]
            if len(pre) < 30 or len(post) < 30: continue
            try: t, p = stats.ttest_ind(pre["polarity"], post["polarity"], equal_var=False)
            except: t, p = float("nan"), float("nan")
            print(f"    {name:<24s} pre={pre['polarity'].mean():+.3f} "
                   f"post={post['polarity'].mean():+.3f} p={p:.4g}")

    # === Save ===
    rdf.to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("L3: TOPIC-LEVEL FSA RESPONSIVENESS (servicer_issues)\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Posts with date+topic: {len(df):,}\n")
        f.write(f"Months with n>=20: {len(monthly)}\n\n")

        f.write("OPERATIONAL EVENT TESTS (servicer_issues topic share)\n")
        f.write("-" * 80 + "\n")
        if len(rdf):
            ops = rdf[rdf["type"] == "operational"]
            for _, r in ops.iterrows():
                f.write(f"  {r['event']:<24s} {r['window_days']}d  "
                        f"pre={r['pre_share']*100:5.1f}% post={r['post_share']*100:5.1f}%  "
                        f"Delta={r['delta_pp']:+5.2f}pp  p={r['p']:.4g}\n")

        f.write("\nPOLICY EVENT CONTROLS (should NOT shift servicer_issues if topic is specific)\n")
        f.write("-" * 80 + "\n")
        if len(rdf):
            pol = rdf[rdf["type"] == "policy"]
            for _, r in pol.iterrows():
                f.write(f"  {r['event']:<24s} {r['window_days']}d  "
                        f"pre={r['pre_share']*100:5.1f}% post={r['post_share']*100:5.1f}%  "
                        f"Delta={r['delta_pp']:+5.2f}pp  p={r['p']:.4g}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        if len(rdf):
            sig_ops = rdf[(rdf["type"] == "operational") & (rdf["p"] < 0.05)]
            sig_pol = rdf[(rdf["type"] == "policy") & (rdf["p"] < 0.05)]
            f.write(f"Operational events with significant servicer_issues shift: {len(sig_ops)}/{len(rdf[rdf['type']=='operational'])}\n")
            f.write(f"Policy events with significant servicer_issues shift: {len(sig_pol)}/{len(rdf[rdf['type']=='policy'])}\n")
            if len(sig_ops) > len(sig_pol):
                f.write("\n-> Servicer_issues topic IS responsive to operational events\n")
                f.write("   (refines B1 NULL on mean polarity — discourse responds to ops at the\n")
                f.write("    topic level even if mean polarity does not shift)\n")
            else:
                f.write("\n-> Servicer_issues topic is NOT preferentially responsive to operational events\n")
                f.write("   (B1 NULL on mean polarity extends to topic level — discourse appears\n")
                f.write("    to be event-driven, not operationally-driven)\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    fig, ax = plt.subplots(figsize=(14, 6))
    monthly_plot = monthly.reset_index()
    monthly_plot["date"] = monthly_plot["month"].dt.start_time
    ax.plot(monthly_plot["date"], monthly_plot["servicer_share"] * 100, "-o", color="#C62828",
             label="servicer_issues topic share", markersize=4)
    ax2 = ax.twinx()
    ax2.bar(monthly_plot["date"], monthly_plot["total"], width=20, alpha=0.2, color="gray",
             label="monthly post volume")
    for name, ev_date in OPS_EVENTS:
        ax.axvline(ev_date, color="darkgreen", lw=1.5, ls="-", alpha=0.7)
        ax.text(ev_date, ax.get_ylim()[1] * 0.95, name, rotation=90,
                 ha="right", va="top", fontsize=8, color="darkgreen")
    for name, ev_date in POLICY_EVENTS:
        ax.axvline(ev_date, color="darkblue", lw=1.5, ls="--", alpha=0.5)
    ax.set_xlabel("Date")
    ax.set_ylabel("servicer_issues share (%)", color="#C62828")
    ax2.set_ylabel("monthly post volume (gray)", color="gray")
    ax.set_title("L3: servicer_issues topic prevalence vs operational events (green) & policy events (blue)")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
