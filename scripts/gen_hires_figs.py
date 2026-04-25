"""Generate high-resolution (300 DPI) figures for PSLF analysis.

Usage:
    python scripts/gen_hires_figs.py
    python scripts/gen_hires_figs.py --data-dir path/to/csvs
"""
import argparse
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud
from collections import Counter

warnings.filterwarnings("ignore", category=FutureWarning)

# Import shared PSLF filter regex
try:
    from pslf_search_terms import PSLF_FILTER_REGEX
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import PSLF_FILTER_REGEX


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def textblob_polarity(text: str) -> float:
    """Compute TextBlob polarity. Returns NaN on error."""
    from textblob import TextBlob
    try:
        return round(TextBlob(str(text)[:5000]).sentiment.polarity, 6)
    except Exception:
        return np.nan


def safe_mean_polarity(series: pd.Series) -> float:
    """Return mean polarity, or 0.0 if all NaN (avoids 'nan' in figure titles)."""
    valid = series.dropna()
    return valid.mean() if len(valid) > 0 else 0.0


# Literature-validated stopword filtering:
#   1. NLTK English stopwords (Bird, Klein & Loper 2009; widely cited NLP standard)
#   2. scikit-learn ENGLISH_STOP_WORDS (Pedregosa et al. 2011)
#   3. Domain-specific augmentation per Manning, Raghavan & Schütze
#      (Introduction to Information Retrieval 2008, Ch.2 §2.2.2):
#      "very high-frequency terms with no discriminative power for the
#       specific task" should be added to the stoplist.
def _build_stopwords() -> set:
    sw: set = set()
    try:
        from nltk.corpus import stopwords as _nltk_sw
        sw.update(_nltk_sw.words("english"))
    except Exception:
        try:
            import nltk
            nltk.download("stopwords", quiet=True)
            from nltk.corpus import stopwords as _nltk_sw
            sw.update(_nltk_sw.words("english"))
        except Exception:
            pass
    try:
        from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as _sk_sw
        sw.update(_sk_sw)
    except Exception:
        pass
    # Reddit/forum artifacts (deleted/removed user content, hyperlink fragments)
    sw.update({"http", "https", "www", "com", "amp", "deleted", "removed",
               "click", "edit", "x200b", "nbsp", "imgur", "youtube"})
    # PSLF-specific high-frequency non-discriminative terms.
    # Rationale (Manning IIR §2.2.2): every post in our corpus is, by selection,
    # about loans/PSLF/payments. These terms thus have ~0 discriminative power
    # and should be excluded to surface era-specific content. Keep narrower
    # terms like "save", "mohela", "fedloan", "buyback", "waiver", which DO
    # vary across eras.
    sw.update({"loan", "loans", "student", "pslf", "forgiveness", "payment",
               "payments", "pay", "paying", "paid", "school", "schools",
               "would", "could", "should", "really", "much", "going", "still",
               "got", "make", "want", "need", "think", "know", "like", "get",
               "one", "two", "year", "years", "month", "months", "day", "days",
               "way", "people", "time", "new", "back", "even", "also", "lot",
               "say", "said", "see", "saw", "go", "going", "anyone", "someone"})
    return sw


STOP_WORDS = _build_stopwords()


def make_wordcloud(texts: pd.Series, title: str, ax: plt.Axes) -> None:
    """Generate a word cloud from text series and plot on axis.

    Filters by:
      - alphabetic tokens only
      - length >= 3 chars
      - not in STOP_WORDS (NLTK + sklearn + domain-specific)
    """
    import re as _re
    text_blob = " ".join(texts.fillna("").str.lower())
    # Tokenize on word boundaries (Bird et al. 2009 NLTK convention)
    tokens = _re.findall(r"\b[a-z]{3,}\b", text_blob)
    freq = Counter(t for t in tokens if t not in STOP_WORDS)
    if len(freq) < 5:
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center", fontsize=16)
        ax.set_title(title, fontsize=13)
        ax.axis("off")
        return
    wc = WordCloud(
        width=800, height=600, background_color="white", colormap="RdYlGn",
        max_words=100, prefer_horizontal=0.7, scale=2,
    )
    wc.generate_from_frequencies(freq)
    ax.imshow(wc, interpolation="bilinear")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.axis("off")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_data(data_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and prepare Reddit + SDN data from data_dir."""
    # Reddit
    frames = []
    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teacher")]:
        path = os.path.join(data_dir, f)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["profession"] = prof
            frames.append(df)
    if not frames:
        print("[ERROR] No Reddit CSV files found in", data_dir)
        sys.exit(1)
    reddit = pd.concat(frames, ignore_index=True)
    reddit["date"] = pd.to_datetime(pd.to_numeric(reddit["created_utc"], errors="coerce"), unit="s")
    # combined_text already includes title; don't double-count
    reddit["text"] = reddit["combined_text"].fillna("")

    print("Recomputing Reddit polarity with TextBlob (consistent with SDN)...")
    reddit["polarity"] = reddit["text"].apply(textblob_polarity)

    # SDN
    sdn_path = os.path.join(data_dir, "forum_pslf_discussions.csv")
    if not os.path.exists(sdn_path):
        print("[ERROR] forum_pslf_discussions.csv not found in", data_dir)
        sys.exit(1)
    sdn = pd.read_csv(sdn_path)
    body_m = sdn["body"].fillna("").str.lower().str.contains(PSLF_FILTER_REGEX, na=False)
    title_m = sdn["thread_title"].fillna("").str.lower().str.contains(PSLF_FILTER_REGEX, na=False)
    sdn = sdn[body_m | title_m].copy()
    # Strip timezone info after parsing so all dates are tz-naive (consistent with Reddit)
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn["text"] = sdn["body"].fillna("")

    print("Recomputing SDN polarity with TextBlob...")
    sdn["polarity"] = sdn["text"].apply(textblob_polarity)

    print(f"Reddit: {len(reddit):,} | SDN (filtered): {len(sdn):,}")
    return reddit, sdn


# ---------------------------------------------------------------------------
# Figure 1: Multi-Source Sentiment Comparison
# ---------------------------------------------------------------------------
def generate_fig1(reddit: pd.DataFrame, sdn: pd.DataFrame, output_dir: str) -> None:
    sources = {"reddit_posts": reddit, "forum_sdn": sdn}
    colors = {"reddit_posts": "#FF6B35", "forum_sdn": "#2196F3"}
    events = [("2021-10-06", "Waiver"), ("2022-10-31", "Deadline"),
              ("2024-07-01", "SAVE\nBlocked"), ("2025-03-07", "Trump\nEO")]

    fig, axes = plt.subplots(2, 2, figsize=(24, 16))
    fig.suptitle(
        f"PSLF Sentiment: Multi-Source Temporal Comparison\n"
        f"Reddit (n={len(reddit):,}) vs SDN Forum (n={len(sdn):,}, PSLF-filtered)",
        fontsize=18, fontweight="bold", y=0.98,
    )

    def add_events(ax):
        for ds, label in events:
            ax.axvline(x=pd.Timestamp(ds), color="gray", linestyle="--", alpha=0.5, linewidth=1)

    # Panel 1: Monthly polarity
    ax1 = axes[0, 0]
    for name, df in sources.items():
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty or "polarity" not in tmp.columns:
            continue
        monthly = tmp.set_index("date").resample("ME")["polarity"].agg(["mean", "count"])
        monthly = monthly[monthly["count"] >= 3]
        if not monthly.empty:
            ax1.plot(monthly.index, monthly["mean"], label=name.replace("_", " ").title(),
                     color=colors.get(name, "gray"), alpha=0.8, linewidth=2)
    add_events(ax1)
    ax1.set_title("Monthly Mean Polarity by Source", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Polarity", fontsize=12)
    ax1.legend(fontsize=11)
    ax1.axhline(y=0, color="black", linewidth=0.5)
    ax1.grid(alpha=0.3)

    # Panel 2: Volume
    ax2 = axes[0, 1]
    for name, df in sources.items():
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty:
            continue
        monthly = tmp.set_index("date").resample("ME").size()
        if not monthly.empty:
            ax2.plot(monthly.index, monthly.values, label=name.replace("_", " ").title(),
                     color=colors.get(name, "gray"), alpha=0.8, linewidth=2)
    add_events(ax2)
    ax2.set_title("Monthly Post Volume", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Count", fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(alpha=0.3)

    # Panel 3: % Negative
    ax3 = axes[1, 0]
    for name, df in sources.items():
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty or "polarity" not in tmp.columns:
            continue
        monthly = tmp.set_index("date").resample("ME")["polarity"].agg(
            lambda x: (x < 0).mean() * 100 if len(x) >= 3 else np.nan
        ).dropna()
        if not monthly.empty:
            ax3.plot(monthly.index, monthly.values, label=name.replace("_", " ").title(),
                     color=colors.get(name, "gray"), alpha=0.8, linewidth=2)
    add_events(ax3)
    ax3.set_title("% Negative Posts by Source (Monthly)", fontsize=14, fontweight="bold")
    ax3.set_ylabel("% Negative", fontsize=12)
    ax3.legend(fontsize=11)
    ax3.grid(alpha=0.3)

    # Panel 4: Violin
    ax4 = axes[1, 1]
    plot_data, plot_labels, plot_colors = [], [], []
    for name, df in sources.items():
        if not df.empty and "polarity" in df.columns:
            pol = df["polarity"].dropna()
            if len(pol) > 10:
                plot_data.append(pol.values)
                plot_labels.append(name.replace("_", "\n").title())
                plot_colors.append(colors.get(name, "gray"))
    if plot_data:
        parts = ax4.violinplot(plot_data, showmeans=True, showmedians=True)
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(plot_colors[i])
            pc.set_alpha(0.6)
        ax4.set_xticks(range(1, len(plot_labels) + 1))
        ax4.set_xticklabels(plot_labels, fontsize=12)
        ax4.set_title("Polarity Distribution by Source", fontsize=14, fontweight="bold")
        ax4.set_ylabel("Polarity", fontsize=12)
        ax4.axhline(y=0, color="black", linewidth=0.5)
        ax4.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    outpath = os.path.join(output_dir, "multi_source_sentiment_comparison.png")
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 1 at 300 DPI: {outpath}")


# ---------------------------------------------------------------------------
# Figure 2: Word Cloud Timecourse
# ---------------------------------------------------------------------------
def generate_fig2(reddit: pd.DataFrame, sdn: pd.DataFrame, output_dir: str) -> None:
    periods = [
        ("Pre-Waiver (2016-2021)", pd.Timestamp("2016-01-01"), pd.Timestamp("2021-10-05")),
        ("PSLF Waiver (2021-2022)", pd.Timestamp("2021-10-06"), pd.Timestamp("2022-10-31")),
        ("Post-Waiver (2022-2024)", pd.Timestamp("2022-11-01"), pd.Timestamp("2024-06-30")),
        ("SAVE Crisis (2024-2026)", pd.Timestamp("2024-07-01"), pd.Timestamp("2026-12-31")),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(28, 14))
    fig.suptitle(
        "PSLF Discussion Word Clouds by Policy Era (Filtered to PSLF-Relevant Posts)\n"
        "Reddit (top) vs SDN Forum (bottom)",
        fontsize=18, fontweight="bold", y=0.99,
    )

    for i, (label, s, e) in enumerate(periods):
        sub = reddit[(reddit["date"] >= s) & (reddit["date"] <= e)]
        pol = safe_mean_polarity(sub["polarity"]) if "polarity" in sub.columns else 0.0
        make_wordcloud(sub["text"], f"Reddit: {label}\n(n={len(sub):,}, pol={pol:.3f})", axes[0, i])

    for i, (label, s, e) in enumerate(periods):
        sub = sdn[(sdn["date"] >= s) & (sdn["date"] <= e)]
        pol = safe_mean_polarity(sub["polarity"]) if "polarity" in sub.columns else 0.0
        make_wordcloud(sub["text"], f"SDN: {label}\n(n={len(sub):,}, pol={pol:.3f})", axes[1, i])

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    outpath = os.path.join(output_dir, "pslf_wordcloud_timecourse.png")
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 2 at 300 DPI: {outpath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate high-res PSLF figures")
    parser.add_argument("--data-dir", default=None, help="Directory containing CSV files")
    args = parser.parse_args()

    # Resolve data directory
    if args.data_dir:
        data_dir = args.data_dir
    elif os.path.exists("comprehensive_medical_pslf_discussions.csv"):
        data_dir = "."
    elif os.path.exists(os.path.join(os.path.dirname(__file__), "..", "PSLF-Discussion-Analysis")):
        data_dir = os.path.join(os.path.dirname(__file__), "..", "PSLF-Discussion-Analysis")
    else:
        data_dir = "."

    reddit, sdn = load_data(data_dir)
    generate_fig1(reddit, sdn, data_dir)
    generate_fig2(reddit, sdn, data_dir)


if __name__ == "__main__":
    main()
