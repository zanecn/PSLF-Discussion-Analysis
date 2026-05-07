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
from pslf_search_terms import PSLF_STRICT_REGEX, filter_pslf_relevant

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
        tm = filter_pslf_relevant(pf["combined_text"])
        tt = filter_pslf_relevant(pf["title"])
        pf = pf[tm | tt].copy()
        pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
        pf["text"] = pf["combined_text"].fillna("")
        pf["source"] = "reddit_prof"
        frames.append(pf[["date", "polarity", "text", "source", "profession"]])

    # SDN forum
    if os.path.exists("forum_pslf_discussions.csv"):
        sdn = pd.read_csv("forum_pslf_discussions.csv")
        bm = filter_pslf_relevant(sdn["body"])
        ttm = filter_pslf_relevant(sdn["thread_title"])
        sdn = sdn[bm | ttm].copy()
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_convert(None)
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
    ax2.set_title("Discussion Volume (PSLF-filtered)  •  REFLECTS DATA-COLLECTION GEOMETRY, NOT TRUE VOLUME",
                  fontsize=12, fontweight="bold", loc="left", color="#C62828")
    # Volume artifact disclaimer per round-2 audit
    ax2.text(0.01, 0.97,
             "Caveat: Reddit's 1000-result API cap + sort=new bias makes pre-2020 posts\n"
             "systematically unreachable in active subs. r/PSLF was created Sep 2017 but\n"
             "earliest scraped post is Oct 2021 — 4 years missing.",
             transform=ax2.transAxes, fontsize=8, va="top", ha="left",
             color="#777777", style="italic",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFEBEE",
                       edgecolor="#C62828", linewidth=0.7, alpha=0.9))
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

    # Layout: violins on left (4 rows x 2 cols), forest plot summary on right.
    # Wider canvas + more left margin so forest plot row labels don't collide.
    fig = plt.figure(figsize=(28, 24))
    gs = fig.add_gridspec(4, 3, width_ratios=[1, 1, 2.0], hspace=0.65, wspace=0.45)

    fig.suptitle(
        "PSLF Sentiment: Pre/Post Policy Event Analysis",
        fontsize=24, fontweight="bold", y=0.995,
    )
    fig.text(0.5, 0.974,
             f"Strict filter, min {MIN_WORDS} words; Welch's t-test, Hedges' g (Bonferroni-corrected, "
             f"associational, NOT causal)",
             ha="center", fontsize=13, style="italic", color="#555555")

    results = []

    for idx, (event_name, event_date, window) in enumerate(key_events):
        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        event_dt = pd.Timestamp(event_date)

        # Keep date for proper moving-block bootstrap
        pre_df = all_data[
            (all_data["date"] >= event_dt - pd.Timedelta(days=window)) &
            (all_data["date"] < event_dt)
        ][["date", "polarity"]].dropna(subset=["polarity"]).sort_values("date")
        post_df = all_data[
            (all_data["date"] >= event_dt) &
            (all_data["date"] <= event_dt + pd.Timedelta(days=window))
        ][["date", "polarity"]].dropna(subset=["polarity"]).sort_values("date")
        pre = pre_df["polarity"]
        post = post_df["polarity"]

        if len(pre) >= 10 and len(post) >= 10:
            t, p = stats.ttest_ind(pre, post, equal_var=False)
            u, p_mw = stats.mannwhitneyu(pre, post, alternative="two-sided")
            n1, n2 = len(pre), len(post)
            var1, var2 = float(pre.var(ddof=1)), float(post.var(ddof=1))
            # Hedges' g (Hedges 1981) — pooled SD, bias-corrected
            s_pooled = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            d_cohen = (post.mean() - pre.mean()) / s_pooled if s_pooled > 0 else 0.0
            J = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
            d = d_cohen * J  # Hedges' g
            # Glass's delta (Δ_pre) — pre-period SD as reference
            # (round-2 audit: pre/post designs need pre as control)
            pre_sd = float(pre.std(ddof=1))
            glass_delta = (post.mean() - pre.mean()) / pre_sd if pre_sd > 0 else 0.0
            # Moving-block bootstrap to preserve autocorrelation (Künsch 1989).
            # Round-3 audit fix: previous implementation was iid permutation
            # despite comments claiming otherwise. Now actually resamples
            # contiguous time-ordered blocks.
            #
            # Block length L ~ n^(1/3) per Carlstein (1986); auto-selected.
            # B=2000 reps for stable p-values around 0.005 (MC SE < 0.0016).
            try:
                rng = np.random.default_rng(42)
                combined_sorted = pd.concat([pre_df, post_df]).sort_values("date").reset_index(drop=True)
                vals = combined_sorted["polarity"].to_numpy()
                n_total = len(vals)
                block_len = max(int(np.ceil(n_total ** (1/3))), 5)
                obs_t = abs((post.mean() - pre.mean()) / np.sqrt(var1/n1 + var2/n2))
                B = 2000
                count_extreme = 0
                # Build all possible block start indices (overlapping blocks)
                block_starts = np.arange(0, n_total - block_len + 1)
                blocks_per_resample = int(np.ceil(n_total / block_len))
                for _ in range(B):
                    # Sample contiguous blocks WITH replacement (Künsch 1989)
                    starts = rng.choice(block_starts, size=blocks_per_resample, replace=True)
                    resampled = np.concatenate([vals[s:s + block_len] for s in starts])[:n_total]
                    # Re-assign first n1 to "pre" group, rest to "post"
                    a_vals = resampled[:n1]
                    b_vals = resampled[n1:n1 + n2]
                    if a_vals.std() == 0 or b_vals.std() == 0:
                        continue
                    t_b = abs((b_vals.mean() - a_vals.mean()) /
                              np.sqrt(a_vals.var(ddof=1)/n1 + b_vals.var(ddof=1)/n2))
                    if t_b >= obs_t:
                        count_extreme += 1
                p_perm = (count_extreme + 1) / (B + 1)
            except Exception:
                p_perm = float("nan")
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
            # Wrap long event names; show stats on second line
            display_name = event_name if len(event_name) <= 32 else event_name[:30] + "..."
            ax.set_title(
                f"{display_name}\n{event_date}  •  t={t:.2f}, p={p:.4f} {sig}  •  g={d:+.2f}",
                fontsize=13, fontweight="bold", color=direction_color, pad=10,
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
                "t": t, "p": p, "d": d, "glass_delta": glass_delta,
                "p_perm": p_perm,
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
        # Bonferroni correction across the family of pre/post tests
        n_tests = len(sorted_results)
        alpha_bonf = 0.05 / n_tests if n_tests > 0 else 0.05
        # 95% CI for Hedges' g (Hedges & Olkin 1985):
        #   var(g) = (n1+n2)/(n1*n2) + g^2 / (2*(n1+n2-2))
        ci_lower, ci_upper = [], []
        labels = []
        colors_pt = []
        for r in sorted_results:
            n1, n2, d = r["n_pre"], r["n_post"], r["d"]
            var_g = (n1 + n2) / (n1 * n2) + d ** 2 / (2.0 * (n1 + n2 - 2))
            se_d = np.sqrt(var_g)
            ci_lower.append(d - 1.96 * se_d)
            ci_upper.append(d + 1.96 * se_d)
            # Significance markers — separately reported for uncorrected and Bonferroni
            if r["p"] < 0.001:
                sig = "***"
            elif r["p"] < 0.01:
                sig = "**"
            elif r["p"] < 0.05:
                sig = "*"
            else:
                sig = "ns"
            bonf_mark = " (B)" if r["p"] < alpha_bonf else ""
            labels.append(f"{r['event']}\n({r['date']}) {sig}{bonf_mark}")
            colors_pt.append("#2E7D32" if d > 0 else "#C62828")

        # Plot CI bars (faded shading for emphasis on point estimates)
        for i, (lo, hi, c) in enumerate(zip(ci_lower, ci_upper, colors_pt)):
            ax_forest.plot([lo, hi], [i, i], color=c, linewidth=3.5, alpha=0.55,
                           solid_capstyle="round")
            # Whiskers at CI ends
            for end in (lo, hi):
                ax_forest.plot([end, end], [i - 0.15, i + 0.15],
                               color=c, linewidth=1.5, alpha=0.7)

        # Plot point estimates as larger filled circles
        ax_forest.scatter(d_values, y_pos, s=180, c=colors_pt, zorder=5,
                          edgecolors="white", linewidths=2)

        ax_forest.axvline(x=0, color="#222222", linewidth=1.2, linestyle="-")

        # Cohen (1988) effect size reference bands (subtle backgrounds)
        ax_forest.axvspan(-1.0, -0.8, color="#FFCDD2", alpha=0.25, zorder=0)
        ax_forest.axvspan(-0.8, -0.5, color="#FFE0B2", alpha=0.25, zorder=0)
        ax_forest.axvspan(-0.5, -0.2, color="#FFF9C4", alpha=0.25, zorder=0)
        ax_forest.axvspan(0.2, 0.5, color="#FFF9C4", alpha=0.25, zorder=0)
        ax_forest.axvspan(0.5, 0.8, color="#DCEDC8", alpha=0.25, zorder=0)
        ax_forest.axvspan(0.8, 1.0, color="#C8E6C9", alpha=0.25, zorder=0)

        # Effect-size threshold labels (top of plot, less cluttered)
        for ref, lbl in [(-0.8, "Large"), (-0.5, "Med"), (-0.2, "Small"),
                         (0.2, "Small"), (0.5, "Med"), (0.8, "Large")]:
            ax_forest.axvline(x=ref, color="#999999", linewidth=0.6,
                              linestyle=":", alpha=0.5)
            ax_forest.text(ref, len(sorted_results) - 0.15, lbl, fontsize=9,
                           ha="center", color="#666666", fontweight="bold")

        # Annotate each row's g value next to its point
        for d, i, c in zip(d_values, y_pos, colors_pt):
            ax_forest.annotate(f"g={d:+.2f}", xy=(d, i),
                               xytext=(0, 12 if d < 0 else -12),
                               textcoords="offset points",
                               ha="center", va="bottom" if d < 0 else "top",
                               fontsize=9, fontweight="bold", color=c)

        ax_forest.set_yticks(y_pos)
        ax_forest.set_yticklabels(labels, fontsize=11)
        ax_forest.set_xlabel("Hedges' g (Effect Size, 95% CI)",
                             fontsize=13, fontweight="bold")
        ax_forest.set_title("Effect Size Summary (sorted by magnitude)",
                            fontsize=15, fontweight="bold", loc="left", pad=12)
        ax_forest.set_xlim(min(min(ci_lower) - 0.05, -0.7), max(max(ci_upper) + 0.05, 0.7))
        ax_forest.set_ylim(-0.7, len(sorted_results) - 0.05)
        ax_forest.grid(axis="x", alpha=0.4, linestyle=":")
        ax_forest.tick_params(axis="y", which="both", length=0)
        ax_forest.set_axisbelow(True)

    fig.text(0.99, 0.005,
             "*p<0.05, **p<0.01, ***p<0.001  |  Effect-size thresholds: Cohen (1988)",
             ha="right", fontsize=9, style="italic", color="#888888")

    plt.savefig("pslf_pre_post_events.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: pslf_pre_post_events.png")

    # ---- Sensitivity analysis: rerun all events at 30/60/90/180-day windows ----
    print("\n" + "=" * 80)
    print("WINDOW SENSITIVITY ANALYSIS (Hedges' g across 30/60/90/180d windows)")
    print(f"  {'Event':<40s} {'30d':>7s} {'60d':>7s} {'90d':>7s} {'180d':>7s}")
    print("=" * 80)
    sens_rows = []
    for event_name, event_date, _ in key_events:
        event_dt = pd.Timestamp(event_date)
        row = [event_name]
        for w in (30, 60, 90, 180):
            pre_w = all_data[(all_data["date"] >= event_dt - pd.Timedelta(days=w)) &
                             (all_data["date"] < event_dt)]["polarity"].dropna()
            post_w = all_data[(all_data["date"] >= event_dt) &
                              (all_data["date"] <= event_dt + pd.Timedelta(days=w))]["polarity"].dropna()
            if len(pre_w) >= 10 and len(post_w) >= 10:
                v1, v2 = float(pre_w.var(ddof=1)), float(post_w.var(ddof=1))
                sp = np.sqrt(((len(pre_w) - 1) * v1 + (len(post_w) - 1) * v2) /
                             (len(pre_w) + len(post_w) - 2))
                d_c = (post_w.mean() - pre_w.mean()) / sp if sp > 0 else 0.0
                JJ = 1.0 - 3.0 / (4.0 * (len(pre_w) + len(post_w)) - 9.0)
                row.append(f"{d_c * JJ:+.3f}")
            else:
                row.append("n/a")
        sens_rows.append(row)
        print(f"  {row[0]:<40s} {row[1]:>7s} {row[2]:>7s} {row[3]:>7s} {row[4]:>7s}")
    print("=" * 80)

    # Print results
    print("\n" + "=" * 80)
    print("SENTIMENT EVOLUTION ACROSS LEGISLATIVE CHANGES")
    print(f"  Pre/post Welch's t-tests, Hedges' g effect size.")
    print(f"  Bonferroni-corrected alpha (n={len(results)} tests): {0.05/max(len(results),1):.4f}")
    print(f"  Note: pre/post is associational, not causal (no ITS counterfactual).")
    print("=" * 80)
    for r in results:
        sig = "***" if r["p"] < 0.001 else "**" if r["p"] < 0.01 else "*" if r["p"] < 0.05 else "ns"
        bonf = " (Bonf.)" if r["p"] < (0.05 / max(len(results), 1)) else ""
        d_label = "large" if abs(r["d"]) >= 0.8 else "medium" if abs(r["d"]) >= 0.5 else "small" if abs(r["d"]) >= 0.2 else "negligible"
        print(f"\n  {r['event']} ({r['date']}, {r['window']}d window):")
        print(f"    Before: n={r['n_pre']:,}, polarity={r['pol_pre']:.4f}, %neg={r['neg_pre']:.1f}%")
        print(f"    After:  n={r['n_post']:,}, polarity={r['pol_post']:.4f}, %neg={r['neg_post']:.1f}%")
        print(f"    Change: {r['pol_post']-r['pol_pre']:+.4f} polarity, {r['neg_post']-r['neg_pre']:+.1f}pp negativity")
        print(f"    Welch t={r['t']:.3f}, p={r['p']:.6f} {sig}{bonf}, Hedges' g={r['d']:+.3f} ({d_label})")
        print(f"    Glass's delta_pre={r['glass_delta']:+.3f}, permutation p={r['p_perm']:.4f}")


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
