"""
sentiment_triangulation.py
==========================
Three-scorer triangulation: TextBlob × VADER × Claude Sonnet 4 (zero-shot).

Round-5 follow-up to the audit. Computes:
  1. Krippendorff's alpha (ordinal) across the 3 scorers on the union of
     all three zero-shot subsamples (Reddit cross-source n=721, SDN
     cross-platform n=615, Reddit event-stratified n=715).
  2. Per-event pre/post Welch's t + Hedges' g on the Claude scorer using
     the event-stratified subsample (50 pre + 50 post per event).
  3. Figure 7: side-by-side forest plot of Hedges' g for all 3 scorers
     across the 8 canonical events (using the event-stratified n=715
     subset for a fair head-to-head comparison).

Outputs:
  - triangulation_results.txt  — text artifact (canonical numbers)
  - triangulation_results.csv  — CSV mirror
  - triangulation_figure7.png  — 3-scorer forest plot
"""
from __future__ import annotations

import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import krippendorff
from pslf_search_terms import filter_pslf_relevant

# ---- Aesthetic theme (consistent with other figs) ----
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#333333",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#DDDDDD",
    "grid.linewidth": 0.5,
    "grid.alpha": 0.7,
    "font.family": "DejaVu Sans",
})

# Canonical 8-event list (matches gen_legislative_timeline.py + final_summary.py)
EVENTS = [
    ("Limited PSLF Waiver", "2021-10-06", 90),
    ("IDR Account Adjustment", "2022-04-19", 90),
    ("Biden Mass Forgiveness", "2022-08-24", 90),
    ("Biden v. Nebraska SCOTUS", "2023-06-30", 90),
    ("Payments Restart", "2023-10-01", 90),
    ("SAVE Admin Forbearance", "2024-08-09", 90),
    ("Trump PSLF EO", "2025-03-07", 60),
    ("Final Trump PSLF Rule", "2025-10-30", 60),
]

# Claude 5-level ordinal encoding
CLAUDE_NUMERIC = {
    "very_negative": -2,
    "negative": -1,
    "neutral": 0,
    "positive": 1,
    "very_positive": 2,
}

# 5-level ordinal discretization for TextBlob & VADER
# (chosen so very_neg/very_pos are tail behaviors; matches Claude's bin spirit)
def discretize_to_5(score, very_neg, neg_thr, pos_thr, very_pos):
    """Map a continuous score to the same 5-level ordinal scale Claude uses."""
    if pd.isna(score):
        return np.nan
    if score < very_neg:
        return -2
    if score < neg_thr:
        return -1
    if score <= pos_thr:
        return 0
    if score <= very_pos:
        return 1
    return 2


# Standard VADER thresholds (Hutto & Gilbert 2014: ±0.05 for neutral cutoff)
def vader_to_5(c):
    return discretize_to_5(c, -0.5, -0.05, 0.05, 0.5)

# TextBlob analogous thresholds (no canonical convention; use mirrored cutoffs)
def textblob_to_5(p):
    return discretize_to_5(p, -0.4, -0.1, 0.1, 0.4)


def hedges_g(pre, post):
    pre = np.asarray(pre, dtype=float)
    post = np.asarray(post, dtype=float)
    n1, n2 = len(pre), len(post)
    if n1 < 2 or n2 < 2:
        return float("nan")
    v1, v2 = float(np.var(pre, ddof=1)), float(np.var(post, ddof=1))
    sp = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    if sp <= 0:
        return 0.0
    d = (post.mean() - pre.mean()) / sp
    J = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    return d * J


def block_permutation_p(pre_dated, post_dated, scorer_col,
                        B=2000, seed=42):
    """Block-permutation p-value for two-sample mean difference (Bickel et al. 1989).

    Round-7 should-fix #9: per-event triangulation tests previously used
    parametric Welch's t, which ignores within-window autocorrelation.
    Block permutation preserves it.

    pre_dated, post_dated: DataFrames with 'date' + scorer_col columns.
    Returns p-value (two-sided absolute t).
    """
    rng = np.random.default_rng(seed)
    pre_dated = pre_dated.dropna(subset=["date", scorer_col])
    post_dated = post_dated.dropna(subset=["date", scorer_col])
    n1 = len(pre_dated)
    n2 = len(post_dated)
    if n1 < 5 or n2 < 5:
        return float("nan")
    combined = pd.concat([pre_dated, post_dated]).sort_values("date").reset_index(drop=True)
    vals = combined[scorer_col].to_numpy(dtype=float)
    n_total = len(vals)
    block_len = max(int(np.ceil(n_total ** (1/3))), 5)
    n_blocks = int(np.ceil(n_total / block_len))
    block_slices = [(b * block_len, min((b + 1) * block_len, n_total))
                    for b in range(n_blocks)]
    pre = vals[:n1]   # original order; pre is earlier dates
    # Wait — combined is sorted by date, so first n1 elements aren't necessarily pre.
    # Use the actual pre/post group means as the observed statistic.
    a_obs = pre_dated[scorer_col].to_numpy(dtype=float)
    b_obs = post_dated[scorer_col].to_numpy(dtype=float)
    if a_obs.std() == 0 or b_obs.std() == 0:
        return float("nan")
    t_obs = abs((b_obs.mean() - a_obs.mean()) /
                np.sqrt(a_obs.var(ddof=1) / n1 + b_obs.var(ddof=1) / n2))
    count_extreme = 0
    B_actual = 0
    for _ in range(B):
        perm = rng.permutation(n_blocks)
        resampled = np.concatenate([vals[s:e] for b in perm
                                     for s, e in [block_slices[b]]])
        a_vals = resampled[:n1]
        b_vals = resampled[n1:n1 + n2]
        if a_vals.std() == 0 or b_vals.std() == 0:
            continue
        t_b = abs((b_vals.mean() - a_vals.mean()) /
                  np.sqrt(a_vals.var(ddof=1) / n1 + b_vals.var(ddof=1) / n2))
        if t_b >= t_obs:
            count_extreme += 1
        B_actual += 1
    return (count_extreme + 1) / (B_actual + 1) if B_actual > 0 else float("nan")


def alpha_bootstrap_ci(reliability_data, level="ordinal",
                       B=2000, alpha=0.05, seed=42):
    """Stratified bootstrap CI for Krippendorff's alpha.

    Round-7 audit fix #3: previously reported alpha as a point estimate only.
    Hayes & Krippendorff (2007, Communication Methods & Measures) recommend
    bootstrap CIs (typically B=10,000) since alpha lacks an analytic SE.
    Implementation: resample units (columns of reliability_data) with
    replacement, recompute alpha, take percentile interval.

    B=2000 is a quality-vs-speed tradeoff (B=10,000 takes ~5x longer for
    n=4,787 units). User can pass B=10000 explicitly for the manuscript.
    """
    rng = np.random.default_rng(seed)
    n_units = reliability_data.shape[1]
    boot_alphas = []
    for _ in range(B):
        idx = rng.choice(n_units, size=n_units, replace=True)
        rd_b = reliability_data[:, idx]
        try:
            a = krippendorff.alpha(reliability_data=rd_b,
                                    level_of_measurement=level)
            if not np.isnan(a):
                boot_alphas.append(a)
        except Exception:
            continue
    if len(boot_alphas) < 100:
        return float("nan"), float("nan"), len(boot_alphas)
    boot_alphas = np.asarray(boot_alphas)
    lo = float(np.percentile(boot_alphas, 100 * alpha / 2))
    hi = float(np.percentile(boot_alphas, 100 * (1 - alpha / 2)))
    return lo, hi, len(boot_alphas)


def hedges_g_var(g, n1, n2):
    """Variance of Hedges' g with J^2 small-sample correction.

    Round-7 audit fix: previously used Hedges & Olkin (1985) eq. 6.13 which
    is the large-sample approximation that omits J^2 on the second term.
    Borenstein et al. (2009, eq. 4.24) gives the corrected form:
        var(g) = J^2 * [(n1+n2)/(n1*n2) + d^2/(2*(n1+n2-2))]
    where J = 1 - 3/(4*(n1+n2)-9). For n=100-600 the J^2 correction
    changes CI width by ~1-2%; matters at any methods-aware venue.
    """
    n_total = n1 + n2
    if n_total <= 2:
        return float("nan")
    df = n_total - 2
    J = 1.0 - 3.0 / (4.0 * n_total - 9.0)
    # Convert g back to d for the variance formula (var formula uses d^2)
    d = g / J if J > 0 else g
    # var(d) = (n1+n2)/(n1*n2) + d^2/(2*df); var(g) = J^2 * var(d)
    var_g = (J**2) * ((n_total) / (n1 * n2) + d**2 / (2.0 * df))
    return var_g


# ============================================================
# Step 1: Build unified merged DataFrame (post_id × scorer matrix)
# ============================================================
def load_zeroshot():
    """Load all available zero-shot CSVs and tag with subsample.

    Round-5 Path C addition: zeroshot_reddit_eventfull.csv and
    zeroshot_sdn_eventfull.csv are scored over the FULL set of posts in any
    of the 8 canonical event windows (after deduping against the cross-source
    and event-stratified subsamples). Loaded if present; skipped otherwise.
    """
    candidates = [
        ("zeroshot_reddit_n1000.csv", "reddit_cross"),
        ("zeroshot_sdn_n1000.csv", "sdn_cross"),
        ("zeroshot_reddit_eventstrat.csv", "reddit_eventstrat"),
        ("zeroshot_reddit_eventfull.csv", "reddit_eventfull"),
        ("zeroshot_sdn_eventfull.csv", "sdn_eventfull"),
    ]
    frames = []
    for f, label in candidates:
        if not os.path.exists(f):
            continue
        df = pd.read_csv(f)
        df = df[df["pslf_sentiment"].notna()].copy()
        # Drop parse_error / api_error rows: they don't have valid sentiment
        df = df[~df["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
        df["claude_numeric"] = df["pslf_sentiment"].map(CLAUDE_NUMERIC)
        df["subsample"] = label
        cols = ["post_id", "pslf_sentiment", "claude_numeric",
                "primary_topic", "pslf_stance", "source", "subsample"]
        for c in cols:
            if c not in df.columns:
                df[c] = pd.NA
        frames.append(df[cols])
        print(f"  Loaded {len(df):,} from {f} (subsample={label})")
    if not frames:
        raise FileNotFoundError("No zeroshot_*.csv found in working directory.")
    out = pd.concat(frames, ignore_index=True)
    # Deduplicate by post_id (event-stratified posts may be a subset of
    # event-full posts after filling). Keep the first occurrence so the
    # cross-source subsample takes precedence over the event-stratified.
    out = out.drop_duplicates("post_id", keep="first").reset_index(drop=True)
    return out


def attach_textblob_vader(zs):
    """Merge polarity + vader_compound from the source CSVs into the zeroshot frame."""
    # Reddit sources
    reddit_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv"]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            cols = {"id": "post_id"}
            d = d.rename(columns=cols)
            keep = ["post_id", "polarity", "vader_compound"]
            if "created_utc" in d.columns:
                d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"],
                                                         errors="coerce"),
                                           unit="s")
                keep.append("date")
            reddit_frames.append(d[keep])
    reddit_src = pd.concat(reddit_frames, ignore_index=True).drop_duplicates("post_id")

    # SDN
    sdn_src = pd.read_csv("forum_pslf_discussions.csv")
    sdn_src["date"] = pd.to_datetime(sdn_src["date_posted"], errors="coerce",
                                     utc=True).dt.tz_localize(None)
    sdn_src = sdn_src[["post_id", "polarity", "vader_compound", "date"]].drop_duplicates("post_id")

    # Merge: try Reddit first, fall back to SDN
    zs = zs.merge(reddit_src, on="post_id", how="left", suffixes=("", "_r"))
    zs = zs.merge(sdn_src, on="post_id", how="left", suffixes=("", "_s"))
    zs["polarity"] = zs["polarity"].fillna(zs["polarity_s"])
    zs["vader_compound"] = zs["vader_compound"].fillna(zs["vader_compound_s"])
    zs["date"] = zs["date"].fillna(zs["date_s"])
    zs = zs.drop(columns=[c for c in zs.columns if c.endswith("_s") or c.endswith("_r")],
                 errors="ignore")
    zs["date"] = pd.to_datetime(zs["date"], utc=True, errors="coerce").dt.tz_localize(None)
    return zs


# ============================================================
# Step 2: Krippendorff's alpha
# ============================================================
def compute_alpha(merged):
    """Compute ordinal Krippendorff's alpha across the 3 scorers."""
    # Discretize TextBlob & VADER to the same 5-level scale Claude uses
    merged["textblob_5"] = merged["polarity"].apply(textblob_to_5)
    merged["vader_5"] = merged["vader_compound"].apply(vader_to_5)

    # Reliability data: 3 raters x N units. NaN encodes "missing".
    # Krippendorff's alpha tolerates missing values.
    reliability_data = np.array([
        merged["textblob_5"].astype(float).to_numpy(),
        merged["vader_5"].astype(float).to_numpy(),
        merged["claude_numeric"].astype(float).to_numpy(),
    ])
    n_units = reliability_data.shape[1]

    alpha_ordinal = krippendorff.alpha(reliability_data=reliability_data,
                                       level_of_measurement="ordinal")
    alpha_nominal = krippendorff.alpha(reliability_data=reliability_data,
                                       level_of_measurement="nominal")
    alpha_interval = krippendorff.alpha(reliability_data=reliability_data,
                                        level_of_measurement="interval")

    # Pairwise: TextBlob×VADER, TextBlob×Claude, VADER×Claude
    pairs = {
        ("TextBlob", "VADER"): krippendorff.alpha(
            reliability_data=reliability_data[[0, 1], :],
            level_of_measurement="ordinal"),
        ("TextBlob", "Claude"): krippendorff.alpha(
            reliability_data=reliability_data[[0, 2], :],
            level_of_measurement="ordinal"),
        ("VADER", "Claude"): krippendorff.alpha(
            reliability_data=reliability_data[[1, 2], :],
            level_of_measurement="ordinal"),
    }

    # Pearson + Spearman correlations (continuous, scale-free) — supplementary
    sub = merged[["polarity", "vader_compound", "claude_numeric"]].dropna()
    pearson = {}
    spearman = {}
    if len(sub) > 10:
        pearson[("TextBlob", "VADER")] = stats.pearsonr(sub["polarity"], sub["vader_compound"])
        pearson[("TextBlob", "Claude")] = stats.pearsonr(sub["polarity"], sub["claude_numeric"])
        pearson[("VADER", "Claude")] = stats.pearsonr(sub["vader_compound"], sub["claude_numeric"])
        spearman[("TextBlob", "VADER")] = stats.spearmanr(sub["polarity"], sub["vader_compound"])
        spearman[("TextBlob", "Claude")] = stats.spearmanr(sub["polarity"], sub["claude_numeric"])
        spearman[("VADER", "Claude")] = stats.spearmanr(sub["vader_compound"], sub["claude_numeric"])

    # Sensitivity: percentile-based discretization to match marginal distributions
    # (rules out alpha being depressed purely by class-frequency mismatch).
    pct = sub.copy()
    pct["TB_pct"] = pd.qcut(pct["polarity"], q=5, labels=[-2, -1, 0, 1, 2],
                            duplicates="drop").astype(float)
    pct["VA_pct"] = pd.qcut(pct["vader_compound"], q=5, labels=[-2, -1, 0, 1, 2],
                            duplicates="drop").astype(float)
    rd_pct = np.array([
        pct["TB_pct"].astype(float).to_numpy(),
        pct["VA_pct"].astype(float).to_numpy(),
        pct["claude_numeric"].astype(float).to_numpy(),
    ])
    alpha_pct = krippendorff.alpha(reliability_data=rd_pct,
                                   level_of_measurement="ordinal")
    pairs_pct = {
        ("TextBlob", "VADER"): krippendorff.alpha(
            reliability_data=rd_pct[[0, 1], :], level_of_measurement="ordinal"),
        ("TextBlob", "Claude"): krippendorff.alpha(
            reliability_data=rd_pct[[0, 2], :], level_of_measurement="ordinal"),
        ("VADER", "Claude"): krippendorff.alpha(
            reliability_data=rd_pct[[1, 2], :], level_of_measurement="ordinal"),
    }

    # Marginal class distributions (diagnostic)
    margins = {
        "claude": merged["claude_numeric"].astype(float).value_counts().sort_index().to_dict(),
        "textblob": merged["polarity"].apply(textblob_to_5).astype(float).value_counts().sort_index().to_dict(),
        "vader": merged["vader_compound"].apply(vader_to_5).astype(float).value_counts().sort_index().to_dict(),
    }

    # Subsample provenance: which zeroshot CSVs contributed (load_zeroshot tags
    # rows with a 'subsample' column). Reported in the artifact so the count
    # of subsamples isn't hardcoded.
    if "subsample" in merged.columns:
        subsamples = sorted(merged["subsample"].dropna().unique().tolist())
    else:
        subsamples = []

    # Bootstrap CI for the headline three-rater alpha (both fixed and pct).
    # B=2000 by default; manuscript run can use B=10000 by passing larger.
    print("  Bootstrap CI on three-rater alpha (B=2000)...")
    ci_fixed = alpha_bootstrap_ci(reliability_data, level="ordinal", B=2000)
    ci_pct = alpha_bootstrap_ci(rd_pct, level="ordinal", B=2000)

    return {
        "n_units": n_units,
        "n_complete": int(len(sub)),  # rows with all 3 scorers (non-NaN)
        "subsamples": subsamples,
        "alpha_ordinal": alpha_ordinal,
        "alpha_nominal": alpha_nominal,
        "alpha_interval": alpha_interval,
        "alpha_ordinal_ci95": ci_fixed[:2],     # (lo, hi)
        "alpha_pct_ci95": ci_pct[:2],
        "alpha_boot_B": ci_fixed[2],            # # of valid bootstrap iterations
        "pairs": pairs,
        "alpha_pct_3rater": alpha_pct,
        "pairs_pct": pairs_pct,
        "pearson": pearson,
        "spearman": spearman,
        "margins": margins,
    }


# ============================================================
# Step 3: Per-event Claude pre/post tests (event-stratified subset)
# ============================================================
def per_event_tests(merged):
    """For each of the 8 canonical events, compute pre/post on all 3 scorers
    using only the event-stratified subsample (where Claude was applied).
    """
    # Path C fix: use ALL posts in event windows that have all 3 scorers,
    # regardless of which subsample (cross-source / event-stratified /
    # event-fill) they came from. The previous code filtered to just
    # subsample=='reddit_eventstrat', which under-counted after the
    # round-5 dedup moved overlap-with-cross-source posts into the
    # reddit_cross subsample, AND ignored the new event-fill subsamples
    # entirely.
    es = merged.dropna(subset=["polarity", "vader_compound",
                                "claude_numeric", "date"]).copy()
    rows = []
    for event_name, event_date, window in EVENTS:
        dt = pd.Timestamp(event_date)
        pre = es[(es["date"] >= dt - pd.Timedelta(days=window)) & (es["date"] < dt)]
        post = es[(es["date"] >= dt) & (es["date"] <= dt + pd.Timedelta(days=window))]
        if len(pre) < 5 or len(post) < 5:
            continue
        row = {"event": event_name, "date": event_date, "window": window,
               "n_pre": len(pre), "n_post": len(post),
               "n_pre_subsamples": ",".join(sorted(pre["subsample"].dropna().unique())),
               "n_post_subsamples": ",".join(sorted(post["subsample"].dropna().unique()))}
        for s_idx, (scorer, col) in enumerate([("textblob", "polarity"),
                                                ("vader", "vader_compound"),
                                                ("claude", "claude_numeric")]):
            a = pre[col].dropna().to_numpy()
            b = post[col].dropna().to_numpy()
            if len(a) < 2 or len(b) < 2:
                row[f"g_{scorer}"] = float("nan")
                row[f"p_{scorer}"] = float("nan")
                row[f"p_boot_{scorer}"] = float("nan")
                row[f"mean_pre_{scorer}"] = float("nan")
                row[f"mean_post_{scorer}"] = float("nan")
                continue
            g = hedges_g(a, b)
            t, p = stats.ttest_ind(a, b, equal_var=False)
            # Round-7 should-fix #9: add block-permutation p (autocorrelation-aware)
            p_boot = block_permutation_p(
                pre[["date", col]], post[["date", col]], scorer_col=col,
                B=2000, seed=42 + s_idx)
            row[f"g_{scorer}"] = g
            row[f"p_{scorer}"] = p
            row[f"p_boot_{scorer}"] = p_boot
            row[f"mean_pre_{scorer}"] = float(a.mean())
            row[f"mean_post_{scorer}"] = float(b.mean())
        rows.append(row)
    return pd.DataFrame(rows)


# ============================================================
# Step 4: Figure 7 — three-scorer forest plot
# ============================================================
def figure7(per_event):
    """Forest plot: Hedges' g for TextBlob, VADER, Claude across 8 events."""
    fig, ax = plt.subplots(figsize=(13, 9))

    n_events = len(per_event)
    y_pos = np.arange(n_events)
    width = 0.27
    offsets = {"textblob": -width, "vader": 0.0, "claude": width}
    colors = {"textblob": "#FF6B35", "vader": "#2196F3", "claude": "#7B1FA2"}
    labels = {"textblob": "TextBlob (lexicon)",
              "vader": "VADER (social-media)",
              "claude": "Claude Sonnet 4 (LLM zero-shot)"}

    for scorer, off in offsets.items():
        gs = per_event[f"g_{scorer}"].to_numpy()
        n_pre = per_event["n_pre"].to_numpy()
        n_post = per_event["n_post"].to_numpy()
        # 95% CI for Hedges' g (Hedges & Olkin 1985)
        var_g = np.array([
            hedges_g_var(g, n1, n2) if not np.isnan(g) else np.nan
            for g, n1, n2 in zip(gs, n_pre, n_post)
        ])
        se = np.sqrt(var_g)
        ci_lo = gs - 1.96 * se
        ci_hi = gs + 1.96 * se

        ys = y_pos + off
        for i, (g_val, lo, hi) in enumerate(zip(gs, ci_lo, ci_hi)):
            if np.isnan(g_val):
                continue
            ax.plot([lo, hi], [ys[i], ys[i]], color=colors[scorer],
                    linewidth=2.5, alpha=0.5, solid_capstyle="round")
            for end in (lo, hi):
                ax.plot([end, end], [ys[i] - 0.07, ys[i] + 0.07],
                        color=colors[scorer], linewidth=1.2, alpha=0.7)
        ax.scatter(gs, ys, s=110, c=colors[scorer], zorder=5,
                   edgecolors="white", linewidths=1.6, label=labels[scorer])

    # Reference markers
    ax.axvline(x=0, color="#222222", linewidth=1.0)
    for ref, lbl in [(-0.8, "Large"), (-0.5, "Med"), (-0.2, "Small"),
                     (0.2, "Small"), (0.5, "Med"), (0.8, "Large")]:
        ax.axvline(x=ref, color="#999999", linewidth=0.5, linestyle=":", alpha=0.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{r['event']}\n({r['date']}, n_pre={r['n_pre']}/n_post={r['n_post']})"
                       for _, r in per_event.iterrows()], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Hedges' g (95% CI)", fontsize=12, fontweight="bold")
    ax.set_title("Three-Scorer Triangulation: Pre/Post Effect Sizes by Event\n"
                 "(event-stratified subset, ~50 pre + ~50 post per event)",
                 fontsize=14, fontweight="bold", loc="left")
    ax.legend(loc="lower right", fontsize=10, frameon=True,
              facecolor="white", edgecolor="#CCCCCC")
    ax.grid(axis="x", alpha=0.4, linestyle=":")
    ax.set_axisbelow(True)

    fig.text(0.99, 0.01,
             "TextBlob & VADER continuous; Claude 5-level ordinal mapped to {-2,-1,0,1,2}.",
             ha="right", fontsize=8, style="italic", color="#888888")

    plt.tight_layout()
    plt.savefig("triangulation_figure7.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved: triangulation_figure7.png")


# ============================================================
# Step 4.5: Claude test-retest reliability (Round-7 critical fix #5)
# ============================================================
def claude_test_retest(retest_csv_path, original_csv_path):
    """Compute Krippendorff's alpha between two Claude scoring passes
    on the same posts (e.g. default-temperature run vs temperature=0
    deterministic re-score). Returns dict with alpha, CI, and per-class
    confusion table.

    Round-7 critical fix #5: Claude scoring uses default temperature=1.0
    (sampled, stochastic). Without test-retest reliability, the Claude
    column has unknown ceiling. This function provides the ceiling.

    The retest run should be produced via:
        sentiment_zeroshot.py --input ... \\
          --retest-source-csv ORIGINAL_CSV \\
          --temperature 0 \\
          --output RETEST_CSV
    """
    if not (os.path.exists(retest_csv_path) and os.path.exists(original_csv_path)):
        return None
    a = pd.read_csv(original_csv_path)
    b = pd.read_csv(retest_csv_path)
    a_n_total = len(a)
    b_n_total = len(b)
    a = a[~a["pslf_sentiment"].isin(["parse_error", "api_error"])][["post_id", "pslf_sentiment"]].copy()
    b = b[~b["pslf_sentiment"].isin(["parse_error", "api_error"])][["post_id", "pslf_sentiment"]].copy()
    a["claude_a"] = a["pslf_sentiment"].map(CLAUDE_NUMERIC)
    b["claude_b"] = b["pslf_sentiment"].map(CLAUDE_NUMERIC)
    merged = a[["post_id", "claude_a"]].merge(
        b[["post_id", "claude_b"]], on="post_id", how="inner")
    merged = merged.dropna(subset=["claude_a", "claude_b"])
    # Round-7 re-audit fix: log all three sample sizes so silent shrinkage
    # (e.g. from filter changes between runs) is visible.
    print(f"  [test-retest sizes] original CSV: {a_n_total}, retest CSV: {b_n_total}, "
          f"valid intersection: {len(merged)}")
    if len(merged) < a_n_total * 0.5:
        print(f"  [test-retest WARNING] merged n ({len(merged)}) is <50% of original "
              f"({a_n_total}); large shrinkage suggests filter divergence.")
    if len(merged) < 50:
        return {"n": int(len(merged)), "error": "insufficient overlap"}
    rd = np.array([
        merged["claude_a"].astype(float).to_numpy(),
        merged["claude_b"].astype(float).to_numpy(),
    ])
    alpha_ord = krippendorff.alpha(reliability_data=rd, level_of_measurement="ordinal")
    alpha_nom = krippendorff.alpha(reliability_data=rd, level_of_measurement="nominal")
    ci_lo, ci_hi, B_actual = alpha_bootstrap_ci(rd, level="ordinal", B=2000)
    # Per-class agreement (exact match rate by class)
    same_class = (merged["claude_a"] == merged["claude_b"]).mean()
    # Confusion matrix
    confusion = pd.crosstab(merged["claude_a"], merged["claude_b"],
                             rownames=["temp=1 (default)"],
                             colnames=["temp=0 (retest)"]).fillna(0).astype(int)
    return {
        "n": int(len(merged)),
        "alpha_ordinal": float(alpha_ord),
        "alpha_nominal": float(alpha_nom),
        "ci95": (float(ci_lo), float(ci_hi)),
        "exact_match_rate": float(same_class),
        "confusion": confusion.to_string(),
    }


# ============================================================
# Step 5: Persist text + CSV artifacts
# ============================================================
def write_artifacts(alpha_results, per_event, test_retest_results=None):
    txt = "triangulation_results.txt"
    with open(txt, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Sentiment Triangulation — TextBlob × VADER × Claude Sonnet 4\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/sentiment_triangulation.py\n")
        f.write("=" * 80 + "\n\n")

        # ---- Krippendorff's alpha ----
        f.write("INTER-RATER RELIABILITY (Krippendorff's alpha)\n")
        f.write("-" * 80 + "\n")
        subs = alpha_results.get("subsamples", [])
        n_sub = len(subs) if subs else 0
        n_complete = alpha_results.get("n_complete", alpha_results["n_units"])
        if subs:
            f.write(f"Sample: union of {n_sub} zero-shot subsamples "
                    f"({', '.join(subs)})\n")
        else:
            f.write("Sample: union of zero-shot subsamples\n")
        f.write(f"  n_units (total rows after dedup):          {alpha_results['n_units']:,}\n")
        f.write(f"  n_complete (all 3 scorers non-missing):    {n_complete:,}\n")
        f.write("Encoding: TextBlob & VADER discretized to 5-level ordinal {-2,-1,0,1,2};\n")
        f.write("          Claude pslf_sentiment mapped to same scale.\n")
        f.write(f"  TextBlob thresholds: < -0.4 / -0.1 / +0.1 / +0.4\n")
        f.write(f"  VADER thresholds:    < -0.5 / -0.05 / +0.05 / +0.5 (Hutto & Gilbert 2014)\n\n")
        f.write("Three-rater alpha (TextBlob, VADER, Claude):\n")
        ci_lo, ci_hi = alpha_results.get("alpha_ordinal_ci95", (float("nan"), float("nan")))
        boot_B = alpha_results.get("alpha_boot_B", 0)
        f.write(f"  Ordinal:  alpha = {alpha_results['alpha_ordinal']:+.4f}  "
                f"95% CI [{ci_lo:+.4f}, {ci_hi:+.4f}]  (bootstrap B={boot_B})\n")
        f.write(f"  Nominal:  alpha = {alpha_results['alpha_nominal']:+.4f}\n")
        f.write(f"  Interval: alpha = {alpha_results['alpha_interval']:+.4f}\n\n")
        f.write("Pairwise alpha (ordinal, fixed thresholds):\n")
        for (a, b), v in alpha_results["pairs"].items():
            f.write(f"  {a:>9s} x {b:<9s}: alpha = {v:+.4f}\n")
        f.write("\nUpper-bound sensitivity: alpha with percentile-matched marginals\n")
        f.write("  (Round 7 caveat: this is a CHARITABLE upper bound, not the canonical\n")
        f.write("  number. Forcing equal-frequency quintiles aligns marginals between\n")
        f.write("  TextBlob and VADER but NOT with Claude's true asymmetric distribution\n")
        f.write("  (5%/18%/48%/25%/4%), which mechanically inflates alpha. Report the\n")
        f.write("  fixed-threshold alpha as canonical and this as an upper bound.)\n")
        ci_lo_p, ci_hi_p = alpha_results.get("alpha_pct_ci95", (float("nan"), float("nan")))
        f.write(f"  3-rater ordinal alpha (percentile, upper bound): "
                f"{alpha_results['alpha_pct_3rater']:+.4f}  "
                f"95% CI [{ci_lo_p:+.4f}, {ci_hi_p:+.4f}]\n")
        for (a, b), v in alpha_results["pairs_pct"].items():
            f.write(f"  {a:>9s} x {b:<9s}: alpha = {v:+.4f}\n")
        f.write("\nContinuous Pearson r (supplementary, on raw scores):\n")
        for (a, b), pres in alpha_results["pearson"].items():
            r, p = pres
            f.write(f"  {a:>9s} x {b:<9s}: r = {r:+.4f}, p = {p:.4g}\n")
        f.write("\nSpearman rank correlation (scale-free):\n")
        for (a, b), sres in alpha_results["spearman"].items():
            rho, p = sres
            f.write(f"  {a:>9s} x {b:<9s}: rho = {rho:+.4f}, p = {p:.4g}\n")
        f.write("\nMarginal class distributions (5-level ordinal):\n")
        for scorer, dist in alpha_results["margins"].items():
            total = sum(dist.values())
            pcts = ", ".join(f"{int(k)}: {v:>4d} ({100*v/total:.1f}%)"
                             for k, v in sorted(dist.items()))
            f.write(f"  {scorer:>9s}: {pcts}\n")
        f.write("\n")
        f.write("Krippendorff (1980) interpretation thresholds:\n")
        f.write("  alpha >= 0.800  reliable conclusions\n")
        f.write("  alpha >= 0.667  tentative conclusions only\n")
        f.write("  alpha <  0.667  too unreliable for substantive claims\n")
        f.write("\n")

        # ---- Per-event ----
        f.write("=" * 80 + "\n")
        f.write("PER-EVENT PRE/POST TESTS (well-powered after Path C event-window fill)\n")
        f.write("-" * 80 + "\n")
        # Round-7 fix: was hardcoded "~50 pre + ~50 post" from before Path C.
        # Now uses ALL posts in event windows that have all 3 scorers, drawing
        # from cross-source + event-stratified + event-fill subsamples.
        if not per_event.empty:
            f.write(f"Sample: all posts in event windows from any zeroshot subsample "
                    f"(n_pre range {per_event['n_pre'].min()}–{per_event['n_pre'].max()}, "
                    f"n_post range {per_event['n_post'].min()}–{per_event['n_post'].max()})\n")
            f.write("p_boot is block-permutation (Bickel et al. 1989, B=2000); "
                    "preserves within-window autocorrelation.\n")
            f.write("p_param is Welch's t (parametric, ignores autocorrelation; "
                    "shown for comparison only).\n")
        else:
            f.write("Sample: empty.\n")

        # Helper to format p-values APA-style (Round-7 should-fix #11)
        def fmt_p(p):
            if p is None or (isinstance(p, float) and np.isnan(p)):
                return "  n/a"
            if p < 1e-7:
                return "<1e-7"
            if p < 1e-4:
                return f"{p:.1e}"
            return f"{p:.4f}"

        f.write(f"\n{'Event':<28s} {'win':>4s} {'n_pre':>5s} {'n_post':>6s} "
                f"{'g_TB':>7s} {'pBootTB':>8s} {'g_VA':>7s} {'pBootVA':>8s} "
                f"{'g_CL':>7s} {'pBootCL':>8s}\n")
        f.write("-" * 100 + "\n")
        for _, r in per_event.iterrows():
            f.write(f"{r['event']:<28s} {int(r['window']):>4d} "
                    f"{int(r['n_pre']):>5d} {int(r['n_post']):>6d} "
                    f"{r['g_textblob']:>+7.3f} {fmt_p(r.get('p_boot_textblob', float('nan'))):>8s} "
                    f"{r['g_vader']:>+7.3f} {fmt_p(r.get('p_boot_vader', float('nan'))):>8s} "
                    f"{r['g_claude']:>+7.3f} {fmt_p(r.get('p_boot_claude', float('nan'))):>8s}\n")
        f.write("\n(parametric p shown in CSV; not in this table since it is "
                "known-inflated by autocorrelation)\n")

        # Direction concordance
        f.write("\nDirection concordance (sign of Hedges' g):\n")
        for _, r in per_event.iterrows():
            signs = {
                "TB": np.sign(r["g_textblob"]) if not np.isnan(r["g_textblob"]) else 0,
                "VA": np.sign(r["g_vader"]) if not np.isnan(r["g_vader"]) else 0,
                "CL": np.sign(r["g_claude"]) if not np.isnan(r["g_claude"]) else 0,
            }
            concordant = signs["TB"] == signs["VA"] == signs["CL"] != 0
            sign_str = " ".join(f"{k}:{('+' if v > 0 else '-' if v < 0 else '0')}"
                                for k, v in signs.items())
            mark = " [CONCORDANT]" if concordant else ""
            f.write(f"  {r['event']:<32s}  {sign_str}{mark}\n")

        # ---- Claude test-retest (Round 7 critical fix #5) ----
        if test_retest_results:
            f.write("\n" + "=" * 80 + "\n")
            f.write("CLAUDE TEST-RETEST RELIABILITY (temperature=1 vs temperature=0)\n")
            f.write("Round-7 critical fix #5: ceiling reliability of stochastic single-pass\n")
            f.write("Claude scoring. The default API call uses temperature=1.0 (sampled).\n")
            f.write("A re-score at temperature=0 (deterministic) gives the upper bound\n")
            f.write("on the alpha that any single-pass Claude scoring can achieve. If the\n")
            f.write("test-retest alpha is well below 0.667, no amount of improved prompting\n")
            f.write("or re-scoring can rescue the cross-instrument alpha; the LLM ceiling\n")
            f.write("itself is the limit.\n")
            f.write("-" * 80 + "\n")
            for source, tr in test_retest_results.items():
                f.write(f"\nSource: {source}\n")
                f.write(f"  n (overlap):              {tr['n']:,}\n")
                f.write(f"  alpha (ordinal):          {tr['alpha_ordinal']:+.4f}  "
                        f"95% CI [{tr['ci95'][0]:+.4f}, {tr['ci95'][1]:+.4f}]\n")
                f.write(f"  alpha (nominal):          {tr['alpha_nominal']:+.4f}\n")
                f.write(f"  exact-match rate:         {tr['exact_match_rate']:.3f}\n")
                f.write(f"  Confusion matrix:\n")
                for line in tr["confusion"].split("\n"):
                    f.write(f"    {line}\n")
        else:
            f.write("\n" + "-" * 80 + "\n")
            f.write("CLAUDE TEST-RETEST RELIABILITY\n")
            f.write("-" * 80 + "\n")
            f.write("Not yet run. To compute, score 200+ posts at temperature=0:\n")
            f.write("  python sentiment_zeroshot.py \\\n")
            f.write("    --input forum_pslf_discussions.csv \\\n")
            f.write("    --retest-source-csv zeroshot_sdn_n1000.csv \\\n")
            f.write("    --temperature 0 \\\n")
            f.write("    --output zeroshot_sdn_temp0_retest.csv\n")
            f.write("Then re-run sentiment_triangulation.py.\n")
            f.write("Cost: ~$3 for 615 SDN posts. Establishes Claude's deterministic\n")
            f.write("ceiling (Round 7 critical fix #5).\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {txt}")

    # CSV
    csv = "triangulation_results.csv"
    per_event.to_csv(csv, index=False, float_format="%.6f")
    print(f"Saved: {csv}")


def main():
    print("Loading zero-shot CSVs...")
    zs = load_zeroshot()
    print(f"  Combined zero-shot rows: {len(zs):,}")

    # Round-7 critical fix #5: Claude test-retest reliability
    # Auto-detected from filename convention zeroshot_*_temp0_retest.csv
    test_retest_results = {}
    for original, retest in [
        ("zeroshot_sdn_n1000.csv", "zeroshot_sdn_temp0_retest.csv"),
        ("zeroshot_reddit_n1000.csv", "zeroshot_reddit_temp0_retest.csv"),
    ]:
        if os.path.exists(retest):
            print(f"\n[test-retest] Found {retest}; computing Claude test-retest alpha "
                  f"vs {original}...")
            tr = claude_test_retest(retest, original)
            if tr and "error" not in tr:
                test_retest_results[original] = tr
                print(f"  n={tr['n']}, alpha_ordinal={tr['alpha_ordinal']:+.4f} "
                      f"95% CI [{tr['ci95'][0]:+.4f}, {tr['ci95'][1]:+.4f}], "
                      f"exact-match={tr['exact_match_rate']:.3f}")

    print("Merging with TextBlob + VADER scores...")
    merged = attach_textblob_vader(zs)
    n_merged = (merged[["polarity", "vader_compound", "claude_numeric"]]
                .notna().all(axis=1).sum())
    print(f"  Rows with all 3 scorers present: {n_merged:,}")

    print("\nComputing Krippendorff's alpha...")
    alpha_results = compute_alpha(merged)
    print(f"  Three-rater ordinal alpha = {alpha_results['alpha_ordinal']:+.4f}")
    for (a, b), v in alpha_results["pairs"].items():
        print(f"  {a} x {b}: alpha = {v:+.4f}")

    print("\nPer-event pre/post tests...")
    per_event = per_event_tests(merged)
    print(per_event[["event", "n_pre", "n_post",
                     "g_textblob", "g_vader", "g_claude"]].to_string(index=False))

    print("\nGenerating Figure 7...")
    figure7(per_event)

    print("\nWriting artifacts...")
    write_artifacts(alpha_results, per_event, test_retest_results=test_retest_results)

    print("\nTriangulation complete.")


if __name__ == "__main__":
    main()
