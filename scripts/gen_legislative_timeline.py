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


def holm_bonferroni(pvals, alpha=0.05):
    """Holm-Bonferroni step-down correction (Holm 1979).

    Round-7 should-fix #7: naive Bonferroni at α/k is overly conservative
    when only a few tests are likely null. Holm-Bonferroni controls the
    same family-wise error rate but is uniformly more powerful.

    Returns (adjusted_pvals, reject_flags) where reject_flags are bool
    masks indicating which null hypotheses are rejected at family-wise
    error rate `alpha`.
    """
    pvals = np.asarray(pvals, dtype=float)
    k = len(pvals)
    if k == 0:
        return np.array([]), np.array([], dtype=bool)
    # Sort p-values ascending; remember original index
    order = np.argsort(pvals)
    sorted_p = pvals[order]
    # Holm-adjusted p_i = (k - i) * sorted_p_i, monotonized
    adj_sorted = np.maximum.accumulate(
        np.minimum(1.0, sorted_p * (k - np.arange(k)))
    )
    # Restore original order
    adj = np.empty_like(adj_sorted)
    adj[order] = adj_sorted
    reject = adj < alpha
    return adj, reject

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
    """Load and combine all data sources with strict PSLF filter.

    Round-4 audit fix: keeps `text`, `source`, `profession`, AND `word_count`
    for the length-residualised analysis (regress polarity ~ log(wc) + source
    + profession; use residuals as the outcome).
    """
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
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce")
        sdn["text"] = sdn["body"].fillna("")
        sdn["source"] = "sdn"
        sdn["profession"] = "sdn_medical"
        frames.append(sdn[["date", "polarity", "text", "source", "profession"]])

    all_data = pd.concat(frames, ignore_index=True)
    all_data = all_data.dropna(subset=["date", "polarity"])

    # Normalize all dates to tz-naive
    all_data["date"] = pd.to_datetime(all_data["date"], utc=True).dt.tz_localize(None)

    # Compute word count BEFORE the polarity-nullification filter
    all_data["word_count"] = all_data["text"].str.split().str.len()

    # Min word count filter
    all_data.loc[all_data["word_count"] < MIN_WORDS, "polarity"] = np.nan
    all_data = all_data.dropna(subset=["polarity"])
    all_data = all_data[
        (all_data["date"] >= pd.Timestamp("2009-01-01")) &
        (all_data["date"] <= pd.Timestamp("2026-04-01"))
    ]

    # Length-residualised polarity (round-4 audit fix):
    # Regress polarity on log(word_count) + categorical source + profession.
    # Use residuals as a length-, platform-, and profession-adjusted outcome.
    # This addresses the Round-3 confound that 4/8 events have significantly
    # different pre/post word counts (Payments Restart +292, SAVE -96, Trump EO +86, Final +70).
    all_data["log_wc"] = np.log1p(all_data["word_count"])
    # OLS: residualize polarity on log_wc + source + profession.
    # Round-5 audit fix: SDN posts have source=='sdn' AND profession=='sdn_medical',
    # which makes those two dummies perfectly collinear. Filter rank-deficient cols.
    src_dum = pd.get_dummies(all_data["source"], prefix="src", drop_first=True, dtype=float)
    prof_dum = pd.get_dummies(all_data["profession"], prefix="prof", drop_first=True, dtype=float)
    X_raw = pd.concat(
        [pd.Series(1.0, index=all_data.index, name="intercept"),
         all_data["log_wc"], src_dum, prof_dum],
        axis=1,
    )
    # Drop perfectly-collinear columns (e.g., src_sdn ≡ prof_sdn_medical).
    # Use QR-based rank check on the design matrix.
    X_arr = X_raw.to_numpy(dtype=float)
    _, R = np.linalg.qr(X_arr)
    rank_tol = max(R.shape) * np.spacing(np.linalg.norm(X_arr))
    keep = np.abs(np.diag(R)) > rank_tol
    if not keep.all():
        dropped = [c for c, k in zip(X_raw.columns, keep) if not k]
        print(f"[length-resid] Dropped collinear columns: {dropped}")
    X_design = X_arr[:, keep]
    y = all_data["polarity"].to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    yhat = X_design @ beta
    all_data["polarity_resid"] = y - yhat

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
            # Block-permutation test for autocorrelation-aware two-sample p-value
            # (Bickel et al. 1989; Politis & Romano 1994).
            #
            # Round-7 audit fix: the previous implementation resampled blocks
            # WITH REPLACEMENT from the combined series and re-cut at index n1.
            # That biases the null distribution because the surrogate "pre" sample
            # is biased toward whichever group is more common at the resampled
            # block-starts. The standard two-sample autocorrelation-aware test
            # PERMUTES blocks WITHOUT REPLACEMENT, preserving within-block
            # autocorrelation while breaking between-group correlation.
            #
            # Algorithm:
            #   1. Sort combined pre+post by date.
            #   2. Divide into contiguous blocks of length L = ceil(n^(1/3))
            #      (Carlstein 1986 — note this rate is for sample-mean variance;
            #      for two-sample tests Hall et al. 1995 give different rates,
            #      but n^(1/3) is conventional and produces L=9-11 for our n).
            #   3. For each iteration: permute the block ORDER (without replacement),
            #      take first n1 elements as surrogate "pre", next n2 as surrogate
            #      "post". Compute Welch t. Repeat B times.
            #   4. p = (count_extreme + 1) / (B_actual + 1), per Davison & Hinkley
            #      (1997) eq. 4.11.
            #
            # Round-5 audit fixes preserved:
            #   - Per-event seed (idx-based) to decorrelate event bootstraps
            #   - Track B_actual (skip zero-variance surrogates correctly)
            try:
                rng = np.random.default_rng(42 + idx)  # per-event seed
                combined_sorted = pd.concat([pre_df, post_df]).sort_values("date").reset_index(drop=True)
                vals = combined_sorted["polarity"].to_numpy()
                n_total = len(vals)
                block_len = max(int(np.ceil(n_total ** (1/3))), 5)
                n_blocks = int(np.ceil(n_total / block_len))
                obs_t = abs((post.mean() - pre.mean()) / np.sqrt(var1/n1 + var2/n2))
                B = 2000
                count_extreme = 0
                B_actual = 0
                # Pre-compute block boundaries (last block may be shorter)
                block_slices = [(b * block_len, min((b + 1) * block_len, n_total))
                                for b in range(n_blocks)]
                for _ in range(B):
                    # Permute block order WITHOUT replacement (Bickel et al. 1989)
                    perm = rng.permutation(n_blocks)
                    resampled = np.concatenate([vals[s:e] for b in perm
                                                for s, e in [block_slices[b]]])
                    # Concatenated array is length n_total by construction
                    a_vals = resampled[:n1]
                    b_vals = resampled[n1:n1 + n2]
                    if a_vals.std() == 0 or b_vals.std() == 0:
                        continue
                    t_b = abs((b_vals.mean() - a_vals.mean()) /
                              np.sqrt(a_vals.var(ddof=1)/n1 + b_vals.var(ddof=1)/n2))
                    if t_b >= obs_t:
                        count_extreme += 1
                    B_actual += 1
                p_perm = (count_extreme + 1) / (B_actual + 1) if B_actual > 0 else float("nan")
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

    # ---- LENGTH-RESIDUALISED ANALYSIS (round-4 audit fix #1) ----
    # Re-run all 8 pre/post tests on polarity_resid (raw polarity minus the
    # OLS fit on log(word_count) + source + profession). If headline effects
    # survive on residuals, length confound is ruled out.
    print("\n" + "=" * 80)
    print("LENGTH-RESIDUALISED PRE/POST ANALYSIS")
    print("  Outcome = residuals of polarity ~ log(word_count) + source + profession.")
    print("  This adjusts for the Round-3 confound that 4/8 events have")
    print("  significantly different pre/post word counts.")
    print("=" * 80)
    print(f"  {'Event':<40s} {'g_raw':>8s} {'g_resid':>9s} {'p_raw':>9s} {'p_resid':>9s}")
    resid_results = []
    if "polarity_resid" not in all_data.columns:
        print("  [SKIP] polarity_resid column not found")
    else:
        for event_name, event_date, window in key_events:
            event_dt = pd.Timestamp(event_date)
            mask_pre = (all_data["date"] >= event_dt - pd.Timedelta(days=window)) & \
                       (all_data["date"] < event_dt)
            mask_post = (all_data["date"] >= event_dt) & \
                        (all_data["date"] <= event_dt + pd.Timedelta(days=window))
            pre_raw = all_data.loc[mask_pre, "polarity"].dropna()
            post_raw = all_data.loc[mask_post, "polarity"].dropna()
            pre_res = all_data.loc[mask_pre, "polarity_resid"].dropna()
            post_res = all_data.loc[mask_post, "polarity_resid"].dropna()
            if min(len(pre_raw), len(post_raw), len(pre_res), len(post_res)) < 10:
                continue
            # Hedges' g on raw
            n1, n2 = len(pre_raw), len(post_raw)
            v1, v2 = float(pre_raw.var(ddof=1)), float(post_raw.var(ddof=1))
            sp = np.sqrt(((n1-1)*v1 + (n2-1)*v2) / (n1+n2-2))
            d_raw = (post_raw.mean() - pre_raw.mean()) / sp * (1 - 3/(4*(n1+n2)-9)) if sp > 0 else 0.0
            _, p_raw = stats.ttest_ind(pre_raw, post_raw, equal_var=False)
            # Hedges' g on residuals
            n1r, n2r = len(pre_res), len(post_res)
            v1r, v2r = float(pre_res.var(ddof=1)), float(post_res.var(ddof=1))
            spr = np.sqrt(((n1r-1)*v1r + (n2r-1)*v2r) / (n1r+n2r-2))
            d_res = (post_res.mean() - pre_res.mean()) / spr * (1 - 3/(4*(n1r+n2r)-9)) if spr > 0 else 0.0
            _, p_res = stats.ttest_ind(pre_res, post_res, equal_var=False)
            # Flag if residual analysis kills significance
            flag = ""
            if p_raw < 0.05 and p_res >= 0.05:
                flag = "  [!] LOST sig on residuals"
            elif p_raw >= 0.05 and p_res < 0.05:
                flag = "  [!] GAINED sig on residuals"
            elif abs(d_raw - d_res) > 0.15:
                flag = "  [!] Effect size changed >0.15"
            print(f"  {event_name:<40s} {d_raw:>+8.3f} {d_res:>+9.3f} "
                  f"{p_raw:>9.4f} {p_res:>9.4f}{flag}")
            resid_results.append({
                "event": event_name, "date": event_date, "window": window,
                "n_pre": n1r, "n_post": n2r,
                "g_raw": d_raw, "g_resid": d_res,
                "p_raw": p_raw, "p_resid": p_res, "flag": flag.strip(),
            })
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

    return results, resid_results, sens_rows


def write_results_artifact(results, resid_results, sens_rows, n_total,
                           path="legislative_timeline_results.txt"):
    """Persist headline numbers to a static text artifact for traceability.

    Round-5 audit fix: previously the g_resid=+0.58 SAVE Forbearance number,
    the 8-event Bonferroni table, and the bootstrap p-values existed only in
    transient stdout. A reviewer could not independently verify the table
    without re-running. This writer emits a parallel artefact alongside the
    figures (compare admin_correlation_results.txt, confound_audit_results.txt).

    Also emits a parallel CSV at legislative_timeline_results.csv for easy
    downstream consumption.
    """
    import csv
    from datetime import datetime

    n_tests = len(results)
    alpha_bonf = 0.05 / n_tests if n_tests > 0 else 0.05

    # Round-7 should-fix #7: Holm-Bonferroni step-down adjustment.
    # Compute on bootstrap p (the autocorrelation-corrected one) since the
    # parametric p is known-inflated 30-100x.
    p_boot_array = [r.get("p_perm", float("nan")) for r in results]
    p_boot_holm, holm_reject = holm_bonferroni(
        [p if not np.isnan(p) else 1.0 for p in p_boot_array], alpha=0.05)
    p_param_array = [r["p"] for r in results]
    p_param_holm, _ = holm_bonferroni(p_param_array, alpha=0.05)

    # Build a date-indexed map of residualised stats
    resid_map = {(r["event"], r["date"]): r for r in resid_results}

    # Helper for APA-style p-value reporting (Round-7 should-fix #11)
    def fmt_p(p):
        if p is None or (isinstance(p, float) and np.isnan(p)):
            return "  n/a"
        if p < 1e-7:
            return "<1e-7"
        if p < 1e-4:
            return f"{p:.1e}"
        return f"{p:.4f}"

    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Legislative Timeline — Pre/Post Event Analysis Results\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/gen_legislative_timeline.py\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Sample: n={n_total:,} posts (Reddit + SDN, strict PSLF filter, "
                f"min {MIN_WORDS} words)\n")
        f.write(f"Tests: {n_tests} pre/post events; Welch's t + block-permutation "
                f"test (Bickel et al. 1989, B=2000, per-event seed). Round-7 fix:\n")
        f.write(f"  was moving-block bootstrap WITH replacement; now block "
                f"PERMUTATION (without replacement), correct two-sample null.\n")
        f.write(f"Bonferroni alpha (n={n_tests}): {alpha_bonf:.5f}\n")
        f.write(f"Holm-Bonferroni step-down also applied (Round-7 should-fix #7); "
                f"controls same FWER but uniformly more powerful.\n")
        f.write("Effect size: Hedges' g (Hedges 1981, bias-corrected) "
                "+ Glass's delta_pre (Lakens 2013)\n")
        f.write("Length adjustment: residuals of polarity ~ log(word_count) "
                "+ source + profession (round-4)\n")
        f.write("Caveat: pre/post is associational, NOT causal — no ITS "
                "counterfactual.\n\n")

        # ---- Headline table ----
        f.write("-" * 80 + "\n")
        f.write("HEADLINE TABLE: g_raw, g_resid, parametric + bootstrap p (raw + Holm-adjusted)\n")
        f.write("-" * 80 + "\n")
        header = (f"{'Event':<40s} {'date':<11s} {'win':>4s} "
                  f"{'n_pre':>6s} {'n_post':>6s} {'g_raw':>8s} {'g_resid':>9s} "
                  f"{'glass_d':>8s} {'p_param':>9s} {'p_boot':>9s} "
                  f"{'p_holm':>9s} {'Bonf':>5s} {'Holm':>5s}\n")
        f.write(header)
        f.write("-" * len(header) + "\n")
        for i, r in enumerate(results):
            key = (r["event"], r["date"])
            g_resid = resid_map.get(key, {}).get("g_resid", float("nan"))
            bonf_mark = "Y" if (not np.isnan(r["p_perm"]) and r["p_perm"] < alpha_bonf) else "n"
            holm_mark = "Y" if holm_reject[i] else "n"
            f.write(
                f"{r['event']:<40s} {r['date']:<11s} {r['window']:>4d} "
                f"{r['n_pre']:>6d} {r['n_post']:>6d} {r['d']:>+8.3f} "
                f"{g_resid:>+9.3f} {r['glass_delta']:>+8.3f} "
                f"{fmt_p(r['p']):>9s} {fmt_p(r['p_perm']):>9s} "
                f"{fmt_p(p_boot_holm[i]):>9s} {bonf_mark:>5s} {holm_mark:>5s}\n"
            )

        # ---- Window sensitivity ----
        # Round-7 should-fix #10: report SD across the 4 window choices to
        # flag events with high window-dependence (e.g. SAVE Forbearance
        # ranges +1.03 → +0.25 across 30d/180d).
        f.write("\n" + "-" * 80 + "\n")
        f.write("WINDOW SENSITIVITY: Hedges' g across 30/60/90/180-day windows + SD\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Event':<40s} {'30d':>8s} {'60d':>8s} {'90d':>8s} "
                f"{'180d':>8s} {'SD':>7s} {'flag':>6s}\n")
        for row in sens_rows:
            # row = [event_name, '30d_str', '60d_str', '90d_str', '180d_str']
            try:
                gs = [float(row[i]) for i in (1, 2, 3, 4) if row[i] != "n/a"]
                sd = float(np.std(gs, ddof=1)) if len(gs) >= 2 else float("nan")
                flag = " HIGH" if (not np.isnan(sd) and sd > 0.20) else ""
            except (ValueError, IndexError):
                sd = float("nan")
                flag = ""
            sd_str = f"{sd:.3f}" if not np.isnan(sd) else "  n/a"
            f.write(f"{row[0]:<40s} {row[1]:>8s} {row[2]:>8s} {row[3]:>8s} "
                    f"{row[4]:>8s} {sd_str:>7s} {flag:>6s}\n")
        f.write("  [HIGH = window-sensitivity SD > 0.20; effect highly window-dependent]\n")

        # ---- Length-residualised flags ----
        f.write("\n" + "-" * 80 + "\n")
        f.write("LENGTH-RESIDUALISED FLAGS\n")
        f.write("-" * 80 + "\n")
        any_flag = False
        for r in resid_results:
            if r["flag"]:
                f.write(f"{r['event']:<40s} ({r['date']})  {r['flag']}\n")
                any_flag = True
        if not any_flag:
            f.write("None — all primary findings survive length adjustment.\n")

        # ---- Per-event detail block ----
        f.write("\n" + "-" * 80 + "\n")
        f.write("PER-EVENT DETAIL\n")
        f.write("-" * 80 + "\n")
        for r in results:
            key = (r["event"], r["date"])
            rr = resid_map.get(key, {})
            sig = "***" if r["p"] < 0.001 else "**" if r["p"] < 0.01 else \
                  "*" if r["p"] < 0.05 else "ns"
            bonf = " (Bonf.)" if r["p"] < alpha_bonf else ""
            d_label = ("large" if abs(r["d"]) >= 0.8 else
                       "medium" if abs(r["d"]) >= 0.5 else
                       "small" if abs(r["d"]) >= 0.2 else "negligible")
            f.write(f"\n{r['event']} ({r['date']}, {r['window']}d window):\n")
            f.write(f"  Before: n={r['n_pre']:,}, polarity={r['pol_pre']:+.4f}, "
                    f"%neg={r['neg_pre']:.1f}%\n")
            f.write(f"  After:  n={r['n_post']:,}, polarity={r['pol_post']:+.4f}, "
                    f"%neg={r['neg_post']:.1f}%\n")
            f.write(f"  Change: {r['pol_post']-r['pol_pre']:+.4f} polarity, "
                    f"{r['neg_post']-r['neg_pre']:+.1f}pp negativity\n")
            f.write(f"  Welch t={r['t']:+.3f}, p={r['p']:.6f} {sig}{bonf}\n")
            f.write(f"  Hedges' g={r['d']:+.3f} ({d_label}), "
                    f"Glass's delta_pre={r['glass_delta']:+.3f}\n")
            f.write(f"  Moving-block bootstrap p={r['p_perm']:.4f} "
                    f"(B=2000, per-event seed)\n")
            if rr:
                f.write(f"  Length-residualised: g_resid={rr['g_resid']:+.3f}, "
                        f"p_resid={rr['p_resid']:.4f}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    print(f"Saved: {path}")

    # ---- Parallel CSV ----
    csv_path = path.rsplit(".", 1)[0] + ".csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "event", "date", "window_days", "n_pre", "n_post",
            "pol_pre", "pol_post", "pct_neg_pre", "pct_neg_post",
            "welch_t", "p_param", "g_hedges", "glass_delta_pre",
            "p_bootstrap", "g_resid", "p_resid", "bonferroni_sig",
        ])
        for r in results:
            key = (r["event"], r["date"])
            rr = resid_map.get(key, {})
            w.writerow([
                r["event"], r["date"], r["window"], r["n_pre"], r["n_post"],
                f"{r['pol_pre']:.6f}", f"{r['pol_post']:.6f}",
                f"{r['neg_pre']:.3f}", f"{r['neg_post']:.3f}",
                f"{r['t']:.4f}", f"{r['p']:.6f}", f"{r['d']:.4f}",
                f"{r['glass_delta']:.4f}", f"{r['p_perm']:.6f}",
                f"{rr.get('g_resid', float('nan')):.4f}",
                f"{rr.get('p_resid', float('nan')):.6f}",
                "Y" if r["p"] < alpha_bonf else "n",
            ])
    print(f"Saved: {csv_path}")


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
    results, resid_results, sens_rows = fig2_pre_post(all_data)
    fig3_profession_timeline(all_data)
    write_results_artifact(results, resid_results, sens_rows, n_total=len(all_data))
