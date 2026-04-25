"""
gen_legislative_timeline.py
============================
Generates sentiment timeline aligned with PSLF legislative events.

Produces:
  1. pslf_sentiment_legislative_timeline.png — 3-panel timeline
  2. pslf_pre_post_events.png — pre/post violin plots for key events
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from pslf_search_terms import PSLF_STRICT_REGEX

MIN_WORDS = 20

# ---- Aesthetic theme (consistent across figures) ----
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#222222",
    "axes.titlecolor": "#111111",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linestyle": "-",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "xtick.color": "#444444",
    "ytick.color": "#444444",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.frameon": False,
    "legend.fontsize": 11,
    "font.family": "DejaVu Sans",
    "axes.titlepad": 10,
    "axes.labelpad": 8,
})


def load_all_data():
    """Load and combine all data sources with strict PSLF filter."""
    frames = []

    # Reddit medical/teacher (original)
    for f, prof in [
        ("comprehensive_medical_pslf_discussions.csv", "medical"),
        ("comprehensive_teacher_pslf_discussions.csv", "teacher"),
    ]:
        if os.path.exists(f):
            df = pd.read_csv(f)
            df["profession"] = prof
            df["source"] = "reddit"
            df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"), unit="s")
            df["text"] = df["combined_text"].fillna("")
            frames.append(df[["date", "polarity", "text", "source", "profession"]])

    # Reddit professions
    if os.path.exists("reddit_professions_pslf.csv"):
        pf = pd.read_csv("reddit_professions_pslf.csv")
        tm = pf["combined_text"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        tt = pf["title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        pf = pf[tm | tt].copy()
        pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
        pf["text"] = pf["combined_text"].fillna("")
        pf["source"] = "reddit_prof"
        frames.append(pf[["date", "polarity", "text", "source", "profession"]])

    # SDN forum
    if os.path.exists("forum_pslf_discussions.csv"):
        sdn = pd.read_csv("forum_pslf_discussions.csv")
        bm = sdn["body"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        ttm = sdn["thread_title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        sdn = sdn[bm | ttm].copy()
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce")
        sdn["text"] = sdn["body"].fillna("")
        sdn["source"] = "sdn"
        sdn["profession"] = "sdn_medical"
        frames.append(sdn[["date", "polarity", "text", "source", "profession"]])

    all_data = pd.concat(frames, ignore_index=True)
    all_data = all_data.dropna(subset=["date", "polarity"])

    # Normalize all dates to tz-naive
    all_data["date"] = pd.to_datetime(all_data["date"], utc=True).dt.tz_localize(None)

    # Min word count filter
    wc = all_data["text"].str.split().str.len()
    all_data.loc[wc < MIN_WORDS, "polarity"] = np.nan
    all_data = all_data.dropna(subset=["polarity"])
    all_data = all_data[
        (all_data["date"] >= pd.Timestamp("2009-01-01")) &
        (all_data["date"] <= pd.Timestamp("2026-04-01"))
    ]

    return all_data


# Policy events (chronological)
EVENTS = [
    ("2010-10-01", "First PSLF\nEligible", "First borrowers complete 10 years"),
    ("2017-08-31", "First PSLF\nDenials", "~99% of first applications denied"),
    ("2018-06-01", "TEPSLF\nCreated", "Temporary expanded PSLF"),
    ("2020-03-13", "COVID Pause\nBegins", "Payment & interest pause"),
    ("2021-10-06", "Limited PSLF\nWaiver", "Any payment type counts"),
    ("2022-04-19", "IDR Account\nAdjustment", "Past forbearance counts toward PSLF"),
    ("2022-07-01", "MOHELA\nTakes Over", "Replaces FedLoan as PSLF servicer"),
    ("2022-08-24", "Biden Mass\nForgiveness", "$10K-20K plan announced"),
    ("2022-10-31", "Waiver\nDeadline", "Last day for limited waiver"),
    ("2023-06-30", "Biden v.\nNebraska", "SCOTUS strikes down mass forgiveness"),
    ("2023-07-01", "SAVE Plan\nLaunched", "Most generous IDR plan"),
    ("2023-10-01", "Payments\nRestart", "COVID forbearance ends"),
    ("2024-02-13", "First SAVE\nBlock (10C)", "10th Circuit Kansas injunction"),
    ("2024-07-01", "SAVE Plan\nBlocked", "8th Circuit injunction"),
    ("2024-08-09", "SAVE Admin\nForbearance", "All SAVE borrowers stuck in limbo"),
    ("2025-03-07", "Trump PSLF\nExec Order", "Restricts PSLF processing"),
    ("2025-05-22", "OBBBA\nPassed", "Caps/changes IDR"),
    ("2025-10-30", "Final Trump\nPSLF Rule", "Excludes 'illegal purpose' employers"),
    ("2025-11-15", "Cities\nLawsuit", "Boston/Chicago/SF/ABQ sue admin"),
    ("2025-12-31", "Tax Exempt\nExpires", "IDR forgiveness becomes taxable"),
    ("2026-04-24", "Present\nDay", "Current analysis date"),
]

COLORS = {"reddit": "#FF6B35", "reddit_prof": "#E91E63", "sdn": "#2196F3"}
LABELS = {
    "reddit": "Reddit (Medical+Teacher)",
    "reddit_prof": "Reddit (All Professions)",
    "sdn": "SDN Forum",
}


def fig1_timeline(all_data):
    """3-panel sentiment timeline with policy events.

    Layout: tall narrow event-label band above main chart, with leader
    lines connecting labels to event vlines (avoids overlap).
    """
    fig = plt.figure(figsize=(24, 22))
    gs = fig.add_gridspec(4, 1, height_ratios=[1.2, 3, 2, 2], hspace=0.35)
    ax_evt = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax_evt)
    ax2 = fig.add_subplot(gs[2], sharex=ax_evt)
    ax3 = fig.add_subplot(gs[3], sharex=ax_evt)

    fig.suptitle(
        "PSLF Sentiment Evolution Across Legislative Changes",
        fontsize=22, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.972,
             f"Strict PSLF filter, min {MIN_WORDS} words; n={len(all_data):,} posts across Reddit + SDN",
             ha="center", fontsize=12, style="italic", color="#555555")

    # ---- Event label band (top) ----
    # Stagger labels into 4 rows so they never overlap
    n_rows = 4
    for i, (date_str, label, _) in enumerate(EVENTS):
        dt = pd.Timestamp(date_str)
        row = i % n_rows
        y_label = 0.85 - row * 0.22
        ax_evt.axvline(x=dt, ymin=0, ymax=y_label + 0.12, color="#888888",
                       linestyle="--", alpha=0.55, linewidth=0.9, zorder=1)
        # Leader dot
        ax_evt.plot([dt], [y_label + 0.05], marker="o", markersize=4,
                    color="#FF6B35", zorder=3)
        ax_evt.annotate(
            label.replace("\n", " "),
            xy=(dt, y_label),
            ha="center", va="top", fontsize=8.5, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#FFF7E6",
                      edgecolor="#FFB347", linewidth=0.7, alpha=0.95),
            zorder=4,
        )
    ax_evt.set_ylim(-0.05, 1.05)
    ax_evt.set_yticks([])
    ax_evt.set_xticks([])
    ax_evt.set_title("Policy Events Timeline", fontsize=14, fontweight="bold")
    for spine in ax_evt.spines.values():
        spine.set_visible(False)
    ax_evt.grid(False)

    # ---- Panel 1: Monthly polarity with CI bands ----
    for src in ["reddit", "reddit_prof", "sdn"]:
        sub = all_data[all_data["source"] == src].set_index("date").resample("ME")["polarity"]
        monthly = sub.agg(["mean", "count", "std"])
        monthly = monthly[monthly["count"] >= 5]
        if monthly.empty:
            continue
        ax1.plot(monthly.index, monthly["mean"], label=LABELS[src],
                 color=COLORS[src], linewidth=2.2, alpha=0.9)
        se = monthly["std"] / np.sqrt(monthly["count"])
        ax1.fill_between(monthly.index, monthly["mean"] - 1.96 * se,
                         monthly["mean"] + 1.96 * se,
                         color=COLORS[src], alpha=0.12)

    # Subtle event vlines on data panel
    for date_str, _, _ in EVENTS:
        ax1.axvline(x=pd.Timestamp(date_str), color="#BBBBBB",
                    linestyle="--", alpha=0.5, linewidth=0.8)

    ax1.axhline(y=0, color="#222222", linewidth=0.6)
    ax1.set_ylabel("Mean Polarity (95% CI)", fontsize=13, fontweight="bold")
    ax1.set_title("Monthly Sentiment", fontsize=14, fontweight="bold", loc="left")
    ax1.legend(fontsize=11, loc="lower left", frameon=True, facecolor="white",
               edgecolor="#CCCCCC")
    ax1.set_xlim(pd.Timestamp("2012-01-01"), pd.Timestamp("2026-05-01"))

    # ---- Panel 2: Volume (log scale to handle 100x dynamic range) ----
    for src in ["reddit", "reddit_prof", "sdn"]:
        sub = all_data[all_data["source"] == src].set_index("date").resample("ME").size()
        if not sub.empty:
            ax2.fill_between(sub.index, 0.5, sub.values, label=LABELS[src],
                             color=COLORS[src], alpha=0.35)
            ax2.plot(sub.index, sub.values, color=COLORS[src], linewidth=1.2)
    for date_str, _, _ in EVENTS:
        ax2.axvline(x=pd.Timestamp(date_str), color="#BBBBBB",
                    linestyle="--", alpha=0.5, linewidth=0.8)
    ax2.set_yscale("log")
    ax2.set_ylim(0.5, None)
    ax2.set_ylabel("Monthly Post Count (log)", fontsize=13, fontweight="bold")
    ax2.set_title("Discussion Volume (PSLF-filtered)", fontsize=14,
                  fontweight="bold", loc="left")
    ax2.legend(fontsize=11, loc="upper left", frameon=True, facecolor="white",
               edgecolor="#CCCCCC")
    ax2.set_xlim(pd.Timestamp("2012-01-01"), pd.Timestamp("2026-05-01"))

    # ---- Panel 3: % Negative (quarterly) ----
    for src in ["reddit", "reddit_prof", "sdn"]:
        sub = all_data[all_data["source"] == src].set_index("date").resample("QE")["polarity"].agg(
            lambda x: (x < 0).mean() * 100 if len(x) >= 5 else np.nan
        ).dropna()
        if not sub.empty:
            ax3.plot(sub.index, sub.values, label=LABELS[src], color=COLORS[src],
                     linewidth=2.2, marker="o", markersize=5,
                     markerfacecolor="white", markeredgewidth=1.5)
    for date_str, _, _ in EVENTS:
        ax3.axvline(x=pd.Timestamp(date_str), color="#BBBBBB",
                    linestyle="--", alpha=0.5, linewidth=0.8)
    ax3.set_ylabel("% Negative Posts (quarterly)", fontsize=13, fontweight="bold")
    ax3.set_title("Negativity Rate Over Time", fontsize=14,
                  fontweight="bold", loc="left")
    ax3.legend(fontsize=11, loc="upper left", frameon=True, facecolor="white",
               edgecolor="#CCCCCC")
    ax3.set_xlim(pd.Timestamp("2012-01-01"), pd.Timestamp("2026-05-01"))

    # Source attribution
    fig.text(0.99, 0.005,
             "Sources: Reddit (18 subreddits) + Student Doctor Network forum  |  "
             "Sentiment: TextBlob polarity",
             ha="right", fontsize=9, style="italic", color="#888888")

    plt.savefig("pslf_sentiment_legislative_timeline.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: pslf_sentiment_legislative_timeline.png")


def fig2_pre_post(all_data):
    """Pre/post violin plots for key policy events."""
    key_events = [
        ("Limited PSLF Waiver", "2021-10-06", 90),
        ("IDR Account Adjustment", "2022-04-19", 90),
        ("Biden Mass Forgiveness Announcement", "2022-08-24", 90),
        ("Biden v. Nebraska SCOTUS", "2023-06-30", 90),
        ("Payments Restart", "2023-10-01", 90),
        ("SAVE Admin Forbearance", "2024-08-09", 90),
        ("Trump PSLF Executive Order", "2025-03-07", 60),
        ("Final Trump PSLF Rule", "2025-10-30", 60),
    ]

    # Layout: violins on left (4 rows x 2 cols), forest plot summary on right
    fig = plt.figure(figsize=(24, 22))
    gs = fig.add_gridspec(4, 3, width_ratios=[1, 1, 1.4], hspace=0.55, wspace=0.3)

    fig.suptitle(
        "PSLF Sentiment: Pre/Post Policy Event Analysis",
        fontsize=22, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.973,
             f"Strict filter, min {MIN_WORDS} words; Welch's t-test, Glass's delta",
             ha="center", fontsize=12, style="italic", color="#555555")

    results = []

    for idx, (event_name, event_date, window) in enumerate(key_events):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        event_dt = pd.Timestamp(event_date)

        pre = all_data[
            (all_data["date"] >= event_dt - pd.Timedelta(days=window)) &
            (all_data["date"] < event_dt)
        ]["polarity"].dropna()

        post = all_data[
            (all_data["date"] >= event_dt) &
            (all_data["date"] <= event_dt + pd.Timedelta(days=window))
        ]["polarity"].dropna()

        if len(pre) >= 10 and len(post) >= 10:
            t, p = stats.ttest_ind(pre, post, equal_var=False)
            u, p_mw = stats.mannwhitneyu(pre, post, alternative="two-sided")
            ref_std = pre.std() if len(pre) >= len(post) else post.std()
            d = (post.mean() - pre.mean()) / ref_std if ref_std > 0 else 0.0
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            direction_color = "#2E7D32" if (post.mean() - pre.mean()) > 0 else "#C62828"

            parts = ax.violinplot([pre.values, post.values], showmeans=True,
                                  showmedians=True, widths=0.75)
            parts["bodies"][0].set_facecolor("#FF6B35")
            parts["bodies"][0].set_alpha(0.65)
            parts["bodies"][0].set_edgecolor("#B33E0E")
            parts["bodies"][1].set_facecolor("#2196F3")
            parts["bodies"][1].set_alpha(0.65)
            parts["bodies"][1].set_edgecolor("#0D47A1")
            for key in ("cbars", "cmins", "cmaxes", "cmeans", "cmedians"):
                if key in parts:
                    parts[key].set_color("#333333")
                    parts[key].set_linewidth(1.2)

            ax.set_xticks([1, 2])
            ax.set_xticklabels(
                [f"Before\nn={len(pre)}", f"After\nn={len(post)}"],
                fontsize=11,
            )
            ax.set_title(
                f"{event_name}\n{event_date}  |  t={t:.2f}, p={p:.4f} {sig}, d={d:+.2f}",
                fontsize=12, fontweight="bold", color=direction_color,
            )
            ax.set_ylabel("Polarity", fontsize=11)
            ax.axhline(y=0, color="#555555", linewidth=0.6, linestyle="-")

            # Mean labels
            ax.annotate(f"{pre.mean():+.3f}", xy=(1, pre.mean()),
                        xytext=(0.65, pre.mean()), fontsize=10, fontweight="bold",
                        color="#B33E0E", ha="right", va="center")
            ax.annotate(f"{post.mean():+.3f}", xy=(2, post.mean()),
                        xytext=(2.35, post.mean()), fontsize=10, fontweight="bold",
                        color="#0D47A1", ha="left", va="center")

            pre_neg = (pre < 0).mean() * 100
            post_neg = (post < 0).mean() * 100
            results.append({
                "event": event_name, "date": event_date, "window": window,
                "n_pre": len(pre), "n_post": len(post),
                "pol_pre": pre.mean(), "pol_post": post.mean(),
                "neg_pre": pre_neg, "neg_post": post_neg,
                "t": t, "p": p, "d": d,
            })
        else:
            ax.text(0.5, 0.5, f"Insufficient data\npre={len(pre)}, post={len(post)}",
                    ha="center", va="center", fontsize=12, transform=ax.transAxes)
            ax.set_title(f"{event_name} ({event_date})", fontsize=12, fontweight="bold")

    # ---- Right column: Forest plot summary of effect sizes ----
    ax_forest = fig.add_subplot(gs[:, 2])
    if results:
        # Sort by effect size for clearer visualization
        sorted_results = sorted(results, key=lambda r: r["d"])
        y_pos = np.arange(len(sorted_results))
        d_values = [r["d"] for r in sorted_results]
        # Approximate 95% CI for Glass's delta using SE = sqrt((n1+n2)/(n1*n2) + d^2/(2*n2))
        ci_lower, ci_upper = [], []
        labels = []
        colors_pt = []
        for r in sorted_results:
            n1, n2, d = r["n_pre"], r["n_post"], r["d"]
            se_d = np.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * n2))
            ci_lower.append(d - 1.96 * se_d)
            ci_upper.append(d + 1.96 * se_d)
            sig = "***" if r["p"] < 0.001 else "**" if r["p"] < 0.01 else "*" if r["p"] < 0.05 else "ns"
            labels.append(f"{r['event']}\n({r['date']}) {sig}")
            colors_pt.append("#2E7D32" if d > 0 else "#C62828")

        # Plot CI bars
        for i, (lo, hi, c) in enumerate(zip(ci_lower, ci_upper, colors_pt)):
            ax_forest.plot([lo, hi], [i, i], color=c, linewidth=2.2, alpha=0.7)
        # Plot point estimates
        ax_forest.scatter(d_values, y_pos, s=130, c=colors_pt, zorder=5,
                          edgecolors="white", linewidths=1.5)

        ax_forest.axvline(x=0, color="#555555", linewidth=1, linestyle="-")
        # Cohen's d effect size reference lines
        for ref, lbl in [(-0.8, "Large -"), (-0.5, "Med -"), (-0.2, "Small -"),
                         (0.2, "Small +"), (0.5, "Med +"), (0.8, "Large +")]:
            ax_forest.axvline(x=ref, color="#CCCCCC", linewidth=0.5, linestyle=":")
            ax_forest.text(ref, len(sorted_results) - 0.3, lbl, fontsize=8,
                           ha="center", color="#777777")

        ax_forest.set_yticks(y_pos)
        ax_forest.set_yticklabels(labels, fontsize=10)
        ax_forest.set_xlabel("Glass's delta (Effect Size, 95% CI)", fontsize=12, fontweight="bold")
        ax_forest.set_title("Effect Size Summary", fontsize=14, fontweight="bold", loc="left")
        ax_forest.set_xlim(min(min(ci_lower), -0.6), max(max(ci_upper), 0.6))
        ax_forest.set_ylim(-0.7, len(sorted_results) - 0.3)
        ax_forest.grid(axis="x", alpha=0.5)

    fig.text(0.99, 0.005,
             "*p<0.05, **p<0.01, ***p<0.001  |  Effect-size thresholds: Cohen (1988)",
             ha="right", fontsize=9, style="italic", color="#888888")

    plt.savefig("pslf_pre_post_events.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: pslf_pre_post_events.png")

    # Print results
    print("\n" + "=" * 80)
    print("SENTIMENT EVOLUTION ACROSS LEGISLATIVE CHANGES")
    print("=" * 80)
    for r in results:
        sig = "***" if r["p"] < 0.001 else "**" if r["p"] < 0.01 else "*" if r["p"] < 0.05 else "ns"
        d_label = "large" if abs(r["d"]) >= 0.8 else "medium" if abs(r["d"]) >= 0.5 else "small" if abs(r["d"]) >= 0.2 else "negligible"
        print(f"\n  {r['event']} ({r['date']}, {r['window']}d window):")
        print(f"    Before: n={r['n_pre']:,}, polarity={r['pol_pre']:.4f}, %neg={r['neg_pre']:.1f}%")
        print(f"    After:  n={r['n_post']:,}, polarity={r['pol_post']:.4f}, %neg={r['neg_post']:.1f}%")
        print(f"    Change: {r['pol_post']-r['pol_pre']:+.4f} polarity, {r['neg_post']-r['neg_pre']:+.1f}pp negativity")
        print(f"    Welch t={r['t']:.3f}, p={r['p']:.6f} {sig}, Glass d={r['d']:+.3f} ({d_label})")


def fig3_profession_timeline(all_data):
    """Per-profession sentiment timecourse aligned with policy events."""
    # Map to clean profession labels
    prof_map = {
        "medical": "Medical", "teacher": "Teaching",
        "general_pslf": "r/PSLF", "general_student_loans": "r/StudentLoans",
        "nursing": "Nursing", "law": "Law", "social_work": "Social Work",
        "federal_employee": "Federal", "pharmacy": "Pharmacy",
        "physician_assistant": "PA", "occupational_therapy": "OT",
        "speech_language_pathology": "SLP", "sdn_medical": "SDN Forum",
        "sdn": "SDN Forum",
    }
    colors_prof = {
        "Medical": "#E53935", "Teaching": "#8E24AA", "r/PSLF": "#1E88E5",
        "r/StudentLoans": "#00ACC1", "Nursing": "#43A047", "Law": "#FB8C00",
        "Social Work": "#5E35B1", "Federal": "#3949AB", "Pharmacy": "#00897B",
        "PA": "#757575", "OT": "#F4511E", "SLP": "#C0CA33", "SDN Forum": "#1565C0",
    }

    all_data = all_data.copy()
    all_data["prof_label"] = all_data["profession"].map(prof_map).fillna("Other")

    # Only include professions with enough data for meaningful timecourse
    min_total = 80
    prof_counts = all_data["prof_label"].value_counts()
    valid_profs = prof_counts[prof_counts >= min_total].index.tolist()

    # Pre-compute average polarity to determine line ordering (most positive on top)
    prof_avg = {}
    for prof in valid_profs:
        sub = all_data[all_data["prof_label"] == prof]
        prof_avg[prof] = sub["polarity"].mean()
    valid_profs_sorted = sorted(valid_profs, key=lambda p: -prof_avg[p])

    fig = plt.figure(figsize=(26, 16))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 2], hspace=0.35)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    fig.suptitle(
        "PSLF Sentiment by Profession Over Time",
        fontsize=22, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.972,
             f"Quarterly aggregation, min 10 posts/quarter, strict PSLF filter; n={len(all_data):,}",
             ha="center", fontsize=12, style="italic", color="#555555")

    # ---- Panel 1: Quarterly polarity with end-of-line labels ----
    last_points = []
    for prof in valid_profs_sorted:
        sub = all_data[all_data["prof_label"] == prof].set_index("date").resample("QE")["polarity"]
        quarterly = sub.agg(["mean", "count"])
        quarterly = quarterly[quarterly["count"] >= 10]
        if quarterly.empty or len(quarterly) < 3:
            continue
        color = colors_prof.get(prof, "gray")
        ax1.plot(quarterly.index, quarterly["mean"], label=prof, color=color,
                 linewidth=2.2, alpha=0.85, marker="o", markersize=3.5,
                 markerfacecolor="white", markeredgewidth=1.2)
        # End-of-line label
        last_points.append((quarterly.index[-1], quarterly["mean"].iloc[-1], prof, color))

    # Subtle event vlines, no labels (labels are on the timeline figure)
    for date_str, _, _ in EVENTS:
        dt = pd.Timestamp(date_str)
        if dt >= pd.Timestamp("2018-01-01"):
            ax1.axvline(x=dt, color="#CCCCCC", linestyle="--", alpha=0.5, linewidth=0.7)

    # Place end-of-line labels with simple anti-overlap
    last_points.sort(key=lambda x: -x[1])
    for x, y, prof, color in last_points:
        ax1.annotate(prof, xy=(x, y),
                     xytext=(8, 0), textcoords="offset points",
                     fontsize=9, fontweight="bold", color=color,
                     va="center")

    ax1.axhline(y=0, color="#222222", linewidth=0.6)
    ax1.set_ylabel("Mean Polarity (quarterly)", fontsize=13, fontweight="bold")
    ax1.set_title("Sentiment Trajectory by Profession", fontsize=15,
                  fontweight="bold", loc="left")
    ax1.set_xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2026-09-01"))
    # Hide redundant legend; end-labels do the work
    ax1.legend().remove() if ax1.get_legend() else None

    # ---- Panel 2: Stacked area volume ----
    pivot = all_data[all_data["prof_label"].isin(valid_profs)].copy()
    pivot = pivot.set_index("date").groupby("prof_label").resample("QE").size().unstack(level=0, fill_value=0)
    col_order = pivot.sum().sort_values(ascending=False).index.tolist()
    pivot = pivot[col_order]
    stack_colors = [colors_prof.get(p, "gray") for p in col_order]
    ax2.stackplot(pivot.index, *[pivot[c].values for c in col_order],
                  labels=col_order, colors=stack_colors, alpha=0.78,
                  edgecolor="white", linewidth=0.4)

    for date_str, _, _ in EVENTS:
        dt = pd.Timestamp(date_str)
        if dt >= pd.Timestamp("2018-01-01"):
            ax2.axvline(x=dt, color="#888888", linestyle="--", alpha=0.4, linewidth=0.7)

    ax2.set_ylabel("Posts per Quarter", fontsize=13, fontweight="bold")
    ax2.set_title("Discussion Volume by Profession", fontsize=15,
                  fontweight="bold", loc="left")
    ax2.legend(fontsize=9, ncol=4, loc="upper left", frameon=True,
               facecolor="white", edgecolor="#CCCCCC")
    ax2.set_xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2026-05-01"))

    fig.text(0.99, 0.005,
             "Reddit (18 subreddits) + SDN Forum  |  TextBlob polarity",
             ha="right", fontsize=9, style="italic", color="#888888")

    plt.savefig("pslf_profession_timecourse.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: pslf_profession_timecourse.png")


if __name__ == "__main__":
    all_data = load_all_data()
    print(f"Total posts: {len(all_data):,}")
    fig1_timeline(all_data)
    fig2_pre_post(all_data)
    fig3_profession_timeline(all_data)
