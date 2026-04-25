"""
analyze_multi_source.py
=======================
Unified sentiment analysis across all data sources:
  1. Reddit posts (existing data)
  2. Reddit comments (from collect_reddit_comments.py)
  3. Forum data — SDN + WCI (from collect_forum_data.py)
  4. X/Twitter data (from collect_twitter_data.py)

Produces comparative visualizations and statistical tests.

Usage:
    python analyze_multi_source.py
"""

import os
import sys
import warnings
from collections import Counter
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# Import shared PSLF filter regex for consistency across all scripts
try:
    from pslf_search_terms import PSLF_STRICT_REGEX
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    from pslf_search_terms import PSLF_STRICT_REGEX

# Minimum word count for reliable sentiment scoring (TextBlob is unreliable on <20 words)
MIN_WORDS_FOR_SENTIMENT = 20

# m7 fix: only suppress specific noisy warnings, not all
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _nullify_short_polarity(df: pd.DataFrame) -> pd.DataFrame:
    """Set polarity to NaN for posts shorter than MIN_WORDS_FOR_SENTIMENT.

    TextBlob gives extreme scores (±1.0) on very short texts like
    "Student Loans- Best Banks" which distort profession-level means.
    """
    if "polarity" in df.columns and "text" in df.columns:
        wc = df["text"].fillna("").str.split().str.len()
        df.loc[wc < MIN_WORDS_FOR_SENTIMENT, "polarity"] = float("nan")
    return df


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------
def load_reddit_posts() -> pd.DataFrame:
    """Load existing Reddit post data."""
    frames = []
    for f, prof in [
        ("comprehensive_medical_pslf_discussions.csv", "medical"),
        ("comprehensive_teacher_pslf_discussions.csv", "teacher"),
    ]:
        if os.path.exists(f):
            df = pd.read_csv(f)
            df["profession"] = prof
            df["data_source"] = "reddit_post"
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    df["created_utc"] = pd.to_numeric(df["created_utc"], errors="coerce")
    df["date"] = pd.to_datetime(df["created_utc"], unit="s")
    # combined_text already includes title; don't double-count (B16 fix)
    df["text"] = df["combined_text"].fillna("")
    return _nullify_short_polarity(df)


def load_reddit_comments() -> pd.DataFrame:
    """Load Reddit comments data."""
    f = "reddit_comments_pslf.csv"
    if not os.path.exists(f):
        print(f"  [SKIP] {f} not found. Run collect_reddit_comments.py first.")
        return pd.DataFrame()
    df = pd.read_csv(f)
    df["data_source"] = "reddit_comment"
    df["date"] = pd.to_datetime(df["created_utc"], unit="s", errors="coerce")
    df["text"] = df["body"].fillna("")
    df["score"] = df["score"].fillna(0)
    return _nullify_short_polarity(df)


def load_reddit_professions() -> pd.DataFrame:
    """Load Reddit profession-specific PSLF posts, filtered for PSLF relevance."""
    f = "reddit_professions_pslf.csv"
    if not os.path.exists(f):
        print(f"  [SKIP] {f} not found. Run collect_reddit_professions.py first.")
        return pd.DataFrame()
    df = pd.read_csv(f)

    # Filter to PSLF-relevant posts (same filter as SDN forum data)
    pre_filter = len(df)
    text_match = df["combined_text"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    title_match = df["title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    df = df[text_match | title_match].copy()
    print(f"  [FILTER] {len(df):,}/{pre_filter:,} PSLF-relevant profession posts retained")

    df["data_source"] = "reddit_" + df["profession"].fillna("unknown")
    df["date"] = pd.to_datetime(df["created_utc"], unit="s", errors="coerce")
    df["text"] = df["combined_text"].fillna("")
    df["score"] = df["score"].fillna(0)
    return _nullify_short_polarity(df)


def load_forum_data() -> pd.DataFrame:
    """Load SDN forum data, filtered to PSLF-relevant posts only.

    The scraper collects entire threads that matched PSLF search queries,
    but many replies within those threads are off-topic (general career
    discussion, salary, rotations, etc.). Filter to posts where the body
    text or thread title mentions PSLF/loan-forgiveness keywords.
    """
    f = "forum_pslf_discussions.csv"
    if not os.path.exists(f):
        print(f"  [SKIP] {f} not found. Run collect_forum_data.py first.")
        return pd.DataFrame()
    df = pd.read_csv(f)

    # Filter to PSLF-relevant posts using shared regex
    body_match = df["body"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    title_match = df["thread_title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    df = df[body_match | title_match].copy()
    print(f"  [FILTER] {len(df):,} PSLF-relevant posts retained from forum data")

    df["data_source"] = "forum_" + df["source"].fillna("unknown")
    df["date"] = pd.to_datetime(df["date_posted"], errors="coerce")
    df["text"] = df["body"].fillna("")
    df["score"] = 0
    return _nullify_short_polarity(df)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def source_summary(dfs: dict[str, pd.DataFrame]):
    """Print summary stats for each data source."""
    print("\n" + "=" * 70)
    print("DATA SOURCE SUMMARY")
    print("=" * 70)
    for name, df in dfs.items():
        if df.empty:
            print(f"  {name}: NO DATA")
            continue
        valid_dates = df["date"].dropna()
        pol_col = "polarity" if "polarity" in df.columns else None
        print(f"\n  {name}:")
        print(f"    Records: {len(df):,}")
        if not valid_dates.empty:
            print(f"    Date range: {valid_dates.min():%Y-%m-%d} to {valid_dates.max():%Y-%m-%d}")
        if pol_col and df[pol_col].notna().any():
            print(f"    Mean polarity: {df[pol_col].mean():.4f} (std: {df[pol_col].std():.4f})")
            print(f"    % Negative: {(df[pol_col] < 0).mean() * 100:.1f}%")
        print(f"    Mean word count: {df['text'].str.split().str.len().mean():.0f}")


def cross_source_sentiment_comparison(dfs: dict[str, pd.DataFrame]):
    """Compare sentiment distributions across sources."""
    print("\n" + "=" * 70)
    print("CROSS-SOURCE SENTIMENT COMPARISON")
    print("=" * 70)

    valid_sources = {}
    for name, df in dfs.items():
        if not df.empty and "polarity" in df.columns and df["polarity"].notna().any():
            valid_sources[name] = df["polarity"].dropna()

    if len(valid_sources) < 2:
        print("  Need at least 2 sources with polarity data for comparison")
        return

    # Pairwise comparisons with Bonferroni correction.
    # Tests: Welch's t (parametric) + Mann-Whitney U (non-parametric).
    # Effect size: Hedges' g (Hedges 1981) — pooled SD with small-sample correction.
    # Switched from "Glass's delta with larger-group SD" (which is non-standard) per
    # 2026-04 audit consensus. Hedges' g is symmetric and the standard choice for
    # observational two-group comparisons of unequal n.
    source_names = list(valid_sources.keys())
    n_comparisons = len(source_names) * (len(source_names) - 1) // 2
    if n_comparisons == 0:
        return
    alpha_corrected = 0.05 / n_comparisons  # Bonferroni
    print(f"  Bonferroni-corrected alpha: {alpha_corrected:.4f} ({n_comparisons} comparisons)")
    print(f"  Effect size: Hedges' g (Hedges 1981) — pooled SD with bias correction")
    print(f"  Tests: Welch's t (parametric) + Mann-Whitney U (non-parametric)\n")

    MIN_GROUP_SIZE = 20  # minimum for reliable statistical comparison

    for i in range(len(source_names)):
        for j in range(i + 1, len(source_names)):
            s1, s2 = source_names[i], source_names[j]
            g1, g2 = valid_sources[s1], valid_sources[s2]
            n1, n2 = len(g1), len(g2)

            if n1 < MIN_GROUP_SIZE or n2 < MIN_GROUP_SIZE:
                print(f"  {s1} vs {s2}: SKIPPED (n1={n1}, n2={n2}, min={MIN_GROUP_SIZE})")
                continue

            t_stat, p_welch = stats.ttest_ind(g1, g2, equal_var=False)
            u_stat, p_mw = stats.mannwhitneyu(g1, g2, alternative="two-sided")

            # Hedges' g (Hedges 1981, J. Educ. Stat.):
            #   d = (m1 - m2) / s_pooled
            #   s_pooled = sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1 + n2 - 2))
            #   g = d * (1 - 3/(4(n1+n2)-9))   [bias correction for small samples]
            var1, var2 = float(g1.var(ddof=1)), float(g2.var(ddof=1))
            s_pooled = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
            d_cohen = (g1.mean() - g2.mean()) / s_pooled if s_pooled > 0 else 0.0
            J = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)  # Hedges bias correction
            hedges_g = d_cohen * J

            abs_g = abs(hedges_g)
            g_label = "large" if abs_g >= 0.8 else "medium" if abs_g >= 0.5 else "small" if abs_g >= 0.2 else "negligible"

            sig = "***" if p_welch < 0.001 else "**" if p_welch < 0.01 else "*" if p_welch < 0.05 else "ns"
            bonf_sig = " (Bonf.)" if p_welch < alpha_corrected else ""
            mw_sig = "***" if p_mw < 0.001 else "**" if p_mw < 0.01 else "*" if p_mw < 0.05 else "ns"

            print(f"  {s1} vs {s2}:")
            print(f"    Welch t={t_stat:.3f}, p={p_welch:.6f} {sig}{bonf_sig} | MW U={u_stat:.0f}, p={p_mw:.6f} {mw_sig}")
            print(f"    Hedges' g={hedges_g:+.3f} ({g_label}), n1={n1}, n2={n2}")


def temporal_comparison(dfs: dict[str, pd.DataFrame], output_dir: str = "."):
    """Generate temporal sentiment comparison across sources."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(
        "PSLF Sentiment: Multi-Source Temporal Comparison",
        fontsize=14, fontweight="bold", y=0.98,
    )

    colors = {
        "reddit_posts": "#FF6B35",
        "reddit_comments": "#FFA500",
        "forum_sdn": "#2196F3",
        "reddit_nursing": "#E91E63",
        "reddit_social_work": "#9C27B0",
        "reddit_federal_employee": "#3F51B5",
        "reddit_law": "#009688",
        "reddit_pharmacy": "#795548",
        "reddit_physician_assistant": "#607D8B",
        "reddit_occupational_therapy": "#FF9800",
        "reddit_speech_language_pathology": "#8BC34A",
    }

    policy_events = [
        ("2021-10-06", "Waiver"),
        ("2022-10-31", "Deadline"),
        ("2024-07-01", "SAVE\nBlocked"),
        ("2025-03-07", "Trump\nEO"),
        ("2025-07-04", "OBBBA"),
    ]

    def add_events(ax):
        for date_str, label in policy_events:
            ax.axvline(x=pd.Timestamp(date_str), color="gray", linestyle="--", alpha=0.4)

    # Panel 1: Monthly polarity by source
    ax1 = axes[0, 0]
    for name, df in dfs.items():
        if df.empty or "polarity" not in df.columns:
            continue
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty:
            continue
        monthly = tmp.set_index("date").resample("ME")["polarity"].agg(["mean", "count"])
        monthly = monthly[monthly["count"] >= 3]
        if not monthly.empty:
            label = name.replace("_", " ").title()
            ax1.plot(monthly.index, monthly["mean"], label=label,
                     color=colors.get(name, "gray"), alpha=0.8, linewidth=1.5)
    add_events(ax1)
    ax1.set_title("Monthly Mean Polarity by Source")
    ax1.set_ylabel("Polarity")
    ax1.legend(fontsize=8)
    ax1.axhline(y=0, color="black", linewidth=0.5)

    # Panel 2: Volume by source
    ax2 = axes[0, 1]
    for name, df in dfs.items():
        if df.empty:
            continue
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty:
            continue
        monthly = tmp.set_index("date").resample("ME").size()
        if not monthly.empty:
            label = name.replace("_", " ").title()
            ax2.plot(monthly.index, monthly.values, label=label,
                     color=colors.get(name, "gray"), alpha=0.8)
    add_events(ax2)
    ax2.set_title("Monthly Post/Comment/Tweet Volume")
    ax2.set_ylabel("Count")
    ax2.legend(fontsize=8)

    # Panel 3: Negative sentiment % by source
    ax3 = axes[1, 0]
    for name, df in dfs.items():
        if df.empty or "polarity" not in df.columns:
            continue
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty:
            continue
        monthly = tmp.set_index("date").resample("ME")["polarity"].agg(
            lambda x: (x < 0).mean() * 100 if len(x) >= 3 else np.nan
        ).dropna()
        if not monthly.empty:
            label = name.replace("_", " ").title()
            ax3.plot(monthly.index, monthly.values, label=label,
                     color=colors.get(name, "gray"), alpha=0.8)
    add_events(ax3)
    ax3.set_title("% Negative Posts by Source (Monthly)")
    ax3.set_ylabel("% Negative")
    ax3.legend(fontsize=8)

    # Panel 4: Polarity distributions (violin/box)
    ax4 = axes[1, 1]
    plot_data = []
    plot_labels = []
    for name, df in dfs.items():
        if not df.empty and "polarity" in df.columns:
            pol = df["polarity"].dropna()
            if len(pol) > 10:
                plot_data.append(pol.values)
                plot_labels.append(name.replace("_", "\n").title())
    if plot_data:
        parts = ax4.violinplot(plot_data, showmeans=True, showmedians=True)
        ax4.set_xticks(range(1, len(plot_labels) + 1))
        ax4.set_xticklabels(plot_labels, fontsize=8)
        ax4.set_title("Polarity Distribution by Source")
        ax4.set_ylabel("Polarity")
        ax4.axhline(y=0, color="black", linewidth=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    outpath = os.path.join(output_dir, "multi_source_sentiment_comparison.png")
    plt.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)  # B1 fix: prevent figure memory leak
    print(f"\n  Saved: {outpath}")


def reddit_post_vs_comment_analysis(posts: pd.DataFrame, comments: pd.DataFrame):
    """Compare sentiment between posts and their comments."""
    if comments.empty:
        print("\n  [SKIP] No comment data available")
        return

    print("\n" + "=" * 70)
    print("REDDIT POSTS vs COMMENTS SENTIMENT")
    print("=" * 70)

    # Overall comparison
    post_pol = posts["polarity"].dropna()
    comment_pol = comments["polarity"].dropna()

    print(f"  Posts:    n={len(post_pol):,}, mean={post_pol.mean():.4f}")
    print(f"  Comments: n={len(comment_pol):,}, mean={comment_pol.mean():.4f}")

    t, p = stats.ttest_ind(post_pol, comment_pol, equal_var=False)
    print(f"  t={t:.3f}, p={p:.4f}")

    # Comments on high-engagement vs low-engagement posts
    if "post_id" in comments.columns:
        post_scores = posts.set_index("id")["score"]
        high_eng_ids = post_scores[post_scores >= 50].index
        low_eng_ids = post_scores[post_scores < 50].index

        high_comments = comments[comments["post_id"].isin(high_eng_ids)]["polarity"]
        low_comments = comments[comments["post_id"].isin(low_eng_ids)]["polarity"]

        if len(high_comments) > 10 and len(low_comments) > 10:
            print(f"\n  Comments on high-engagement posts: n={len(high_comments):,}, mean={high_comments.mean():.4f}")
            print(f"  Comments on low-engagement posts:  n={len(low_comments):,}, mean={low_comments.mean():.4f}")


def forum_vs_reddit_analysis(reddit: pd.DataFrame, forums: pd.DataFrame):
    """Compare forum discourse characteristics to Reddit."""
    if forums.empty:
        print("\n  [SKIP] No forum data available")
        return
    if reddit.empty or "text" not in reddit.columns:
        print("\n  [SKIP] No Reddit data available for comparison")
        return

    print("\n" + "=" * 70)
    print("FORUM vs REDDIT DISCOURSE COMPARISON")
    print("=" * 70)

    # Word count comparison (forums tend toward longer posts)
    reddit_wc = reddit["text"].str.split().str.len()
    forum_wc = forums["text"].str.split().str.len()
    print(f"  Reddit mean word count: {reddit_wc.mean():.0f} (median: {reddit_wc.median():.0f})")
    print(f"  Forum mean word count:  {forum_wc.mean():.0f} (median: {forum_wc.median():.0f})")

    # Sentiment comparison
    if "polarity" in forums.columns:
        for source in forums["data_source"].unique():
            subset = forums[forums["data_source"] == source]["polarity"].dropna()
            if len(subset) > 5:
                print(f"\n  {source}: n={len(subset)}, polarity={subset.mean():.4f}")

    # Topic keywords unique to each platform
    def top_keywords(texts, n=15):
        words = " ".join(texts.fillna("").str.lower()).split()
        stop = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                "being", "have", "has", "had", "do", "does", "did", "will",
                "would", "could", "should", "may", "might", "shall", "can",
                "to", "of", "in", "for", "on", "with", "at", "by", "from",
                "it", "its", "this", "that", "these", "those", "i", "you",
                "he", "she", "we", "they", "my", "your", "and", "or", "but",
                "not", "no", "if", "so", "as", "just", "about", "than", "more",
                "very", "too", "also", "up", "out", "all", "any", "some", "into"}
        filtered = [w for w in words if len(w) > 2 and w not in stop and w.isalpha()]
        return Counter(filtered).most_common(n)

    print(f"\n  Top Reddit keywords: {[w for w, _ in top_keywords(reddit['text'])]}")
    if not forums.empty:
        print(f"  Top Forum keywords:  {[w for w, _ in top_keywords(forums['text'])]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("PSLF MULTI-SOURCE SENTIMENT ANALYSIS")
    print(f"Run at: {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}")
    print("=" * 70)

    # Load all sources
    reddit_posts = load_reddit_posts()
    reddit_comments = load_reddit_comments()
    reddit_professions = load_reddit_professions()
    forums = load_forum_data()

    # Build unified dict
    sources = {}
    if not reddit_posts.empty:
        sources["reddit_posts"] = reddit_posts
    if not reddit_comments.empty:
        sources["reddit_comments"] = reddit_comments
    if not reddit_professions.empty:
        # Group by profession for cross-profession comparison (B11 fix: .copy())
        for prof in reddit_professions["profession"].unique():
            key = f"reddit_{prof}"
            sources[key] = reddit_professions[reddit_professions["profession"] == prof].copy()
    if not forums.empty:
        for src in forums["data_source"].unique():
            sources[src] = forums[forums["data_source"] == src].copy()

    if not sources:
        print("[ERROR] No data sources found. Run collection scripts first.")
        sys.exit(1)

    # Run analyses
    source_summary(sources)
    cross_source_sentiment_comparison(sources)
    temporal_comparison(sources)
    reddit_post_vs_comment_analysis(reddit_posts, reddit_comments)
    forum_vs_reddit_analysis(reddit_posts, forums)

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
