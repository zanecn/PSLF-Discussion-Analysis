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

# Consistent aesthetic theme across figures
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
    "legend.frameon": False,
    "font.family": "DejaVu Sans",
    "axes.titlepad": 10,
})

# Import shared PSLF filter regex
try:
    from pslf_search_terms import PSLF_STRICT_REGEX
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import PSLF_STRICT_REGEX


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


def _get_lemmatizer():
    """Return a WordNet lemmatizer (Miller 1995). Cached on first call.

    WordNet lemmatization is the field-standard method for combining
    inflected forms in NLP/word-cloud research:
      - Bird, Klein & Loper (2009) NLTK book, Ch.3 §3.6
      - Manning, Raghavan & Schutze (2008) IIR §2.2.4
      - Miller (1995) "WordNet: A Lexical Database for English"
    Produces actual English words (unlike stemming which produces roots).
    """
    if not hasattr(_get_lemmatizer, "_cache"):
        try:
            from nltk.stem import WordNetLemmatizer
            try:
                from nltk.corpus import wordnet  # noqa: F401
            except LookupError:
                import nltk
                nltk.download("wordnet", quiet=True)
                nltk.download("omw-1.4", quiet=True)
            _get_lemmatizer._cache = WordNetLemmatizer()
        except Exception:
            _get_lemmatizer._cache = None
    return _get_lemmatizer._cache


def _normalize_token(token: str, lemmatizer) -> str:
    """Lemmatize as both noun and verb; pick the shorter (more reduced) form.

    Standard practice when POS-tagging is unavailable: try multiple POS
    and prefer the more reduced form (Manning IIR §2.2.4 footnote).
    Examples: loans -> loan, paying -> pay, schools -> school.
    """
    if lemmatizer is None:
        return token
    n_form = lemmatizer.lemmatize(token, pos="n")
    v_form = lemmatizer.lemmatize(token, pos="v")
    return v_form if len(v_form) < len(n_form) else n_form


def make_wordcloud(texts: pd.Series, title: str, ax: plt.Axes) -> None:
    """Generate a word cloud from text series and plot on axis.

    Field-standard preprocessing pipeline:
      1. Lowercase normalization
      2. Tokenize on word boundaries (Bird et al. 2009)
      3. Filter alpha tokens, length >= 3
      4. Remove stopwords (NLTK + sklearn + Manning IIR domain stops)
      5. WordNet lemmatization (combines plurals/conjugations)
      6. Re-filter post-lemmatization stopwords
    """
    import re as _re
    lemmatizer = _get_lemmatizer()
    text_blob = " ".join(texts.fillna("").str.lower())
    tokens = _re.findall(r"\b[a-z]{3,}\b", text_blob)
    # Stage 1 stopword filter (pre-lemmatization)
    filtered = [t for t in tokens if t not in STOP_WORDS]
    # Lemmatize
    lemmatized = [_normalize_token(t, lemmatizer) for t in filtered]
    # Stage 2 stopword filter (post-lemmatization, e.g. "loans" -> "loan")
    final = [t for t in lemmatized if len(t) >= 3 and t not in STOP_WORDS]
    freq = Counter(final)
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
MIN_WORDS = 20  # consistent with analyze_multi_source.py and gen_legislative_timeline.py


def _nullify_short_polarity(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Set polarity to NaN where word count < MIN_WORDS.

    TextBlob produces extreme +/-1.0 values on very short text (1-3 words)
    that distort downstream means. This filter mirrors the application in
    analyze_multi_source.py / gen_legislative_timeline.py / final_summary.py
    so that figures are computed on the SAME population as reported numbers.
    """
    wc = df[text_col].fillna("").str.split().str.len()
    df.loc[wc < MIN_WORDS, "polarity"] = np.nan
    return df


def load_data(data_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load + filter Reddit (medical/teacher + professions) + SDN data.

    Both sources pass through:
      - PSLF_STRICT_REGEX filter (consistent with all analysis scripts)
      - TextBlob polarity recomputation
      - MIN_WORDS=20 nullification (TextBlob unreliable on short text)
    """
    # ---- Reddit (medical + teacher original) ----
    frames = []
    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teacher")]:
        path = os.path.join(data_dir, f)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df["profession"] = prof
            frames.append(df)

    # ---- Reddit (profession-specific scrape) ----
    prof_path = os.path.join(data_dir, "reddit_professions_pslf.csv")
    if os.path.exists(prof_path):
        pf = pd.read_csv(prof_path)
        # Apply same strict filter the analysis scripts use
        tm = pf["combined_text"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        tt = pf["title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
        pf = pf[tm | tt].copy()
        frames.append(pf)

    if not frames:
        print("[ERROR] No Reddit CSV files found in", data_dir)
        sys.exit(1)
    reddit = pd.concat(frames, ignore_index=True)

    # Apply strict filter to medical/teacher sets too (idempotent on already-filtered data)
    rm = reddit["combined_text"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    rt = reddit["title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False) \
         if "title" in reddit.columns else pd.Series(False, index=reddit.index)
    reddit = reddit[rm | rt].copy()

    reddit["date"] = pd.to_datetime(pd.to_numeric(reddit["created_utc"], errors="coerce"), unit="s")
    # combined_text already includes title; don't double-count
    reddit["text"] = reddit["combined_text"].fillna("")

    print("Recomputing Reddit polarity with TextBlob (consistent with SDN)...")
    reddit["polarity"] = reddit["text"].apply(textblob_polarity)
    reddit = _nullify_short_polarity(reddit, "text")

    # ---- SDN ----
    sdn_path = os.path.join(data_dir, "forum_pslf_discussions.csv")
    if not os.path.exists(sdn_path):
        print("[ERROR] forum_pslf_discussions.csv not found in", data_dir)
        sys.exit(1)
    sdn = pd.read_csv(sdn_path)
    body_m = sdn["body"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    title_m = sdn["thread_title"].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    sdn = sdn[body_m | title_m].copy()
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn["text"] = sdn["body"].fillna("")

    print("Recomputing SDN polarity with TextBlob...")
    sdn["polarity"] = sdn["text"].apply(textblob_polarity)
    sdn = _nullify_short_polarity(sdn, "text")

    print(f"Reddit: {len(reddit):,} (strict filter, MIN_WORDS={MIN_WORDS}) | "
          f"SDN: {len(sdn):,} (strict filter, MIN_WORDS={MIN_WORDS})")
    return reddit, sdn


# ---------------------------------------------------------------------------
# Figure 1: Multi-Source Sentiment Comparison
# ---------------------------------------------------------------------------
def generate_fig1(reddit: pd.DataFrame, sdn: pd.DataFrame, output_dir: str) -> None:
    sources = {"Reddit": reddit, "SDN Forum": sdn}
    colors = {"Reddit": "#FF6B35", "SDN Forum": "#2196F3"}
    events = [("2021-10-06", "Waiver"), ("2023-06-30", "Biden v.\nNebraska"),
              ("2024-07-01", "SAVE\nBlocked"), ("2025-03-07", "Trump\nEO")]

    fig, axes = plt.subplots(2, 2, figsize=(24, 16))
    fig.suptitle(
        "PSLF Sentiment: Multi-Source Temporal Comparison",
        fontsize=22, fontweight="bold", y=0.98,
    )
    fig.text(0.5, 0.953,
             f"Reddit n={len(reddit):,} vs SDN Forum n={len(sdn):,} (PSLF-filtered)",
             ha="center", fontsize=12, style="italic", color="#555555")

    def add_events(ax, label_top=False):
        for ds, label in events:
            dt = pd.Timestamp(ds)
            ax.axvline(x=dt, color="#BBBBBB", linestyle="--", alpha=0.55, linewidth=0.8)
            if label_top:
                ymax = ax.get_ylim()[1]
                ax.text(dt, ymax * 0.96, label, fontsize=8, ha="center", va="top",
                        color="#666666",
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="#FFF7E6",
                                  edgecolor="#FFB347", linewidth=0.5, alpha=0.9))

    # Panel 1: Monthly polarity (smoothed)
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
            ax1.scatter(monthly.index, monthly["mean"], color=colors[name],
                        alpha=0.25, s=12, zorder=2)
            smooth = monthly["mean"].rolling(window=3, center=True, min_periods=1).mean()
            ax1.plot(smooth.index, smooth.values, label=f"{name} (3-mo smooth)",
                     color=colors[name], linewidth=2.4, alpha=0.95, zorder=3)
    ax1.axhline(y=0, color="#222222", linewidth=0.6)
    add_events(ax1, label_top=True)
    ax1.set_title("Monthly Mean Polarity by Source", fontsize=14,
                  fontweight="bold", loc="left")
    ax1.set_ylabel("Polarity", fontsize=12, fontweight="bold")
    ax1.legend(fontsize=11, loc="lower left", frameon=True, facecolor="white",
               edgecolor="#CCCCCC")

    # Panel 2: Volume (log scale to handle 100x range)
    ax2 = axes[0, 1]
    for name, df in sources.items():
        tmp = df.dropna(subset=["date"]).copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])
        if tmp.empty:
            continue
        monthly = tmp.set_index("date").resample("ME").size()
        if not monthly.empty:
            ax2.fill_between(monthly.index, 0.5, monthly.values, color=colors[name],
                             alpha=0.3, label=name)
            ax2.plot(monthly.index, monthly.values, color=colors[name], linewidth=1.5)
    ax2.set_yscale("log")
    ax2.set_ylim(0.5, None)
    add_events(ax2)
    ax2.set_title("Monthly Post Volume (log scale)", fontsize=14,
                  fontweight="bold", loc="left")
    ax2.set_ylabel("Count (log)", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=11, loc="upper left", frameon=True, facecolor="white",
               edgecolor="#CCCCCC")

    # Panel 3: % Negative (smoothed)
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
            ax3.scatter(monthly.index, monthly.values, color=colors[name],
                        alpha=0.25, s=12, zorder=2)
            smooth = monthly.rolling(window=3, center=True, min_periods=1).mean()
            ax3.plot(smooth.index, smooth.values, label=f"{name} (3-mo smooth)",
                     color=colors[name], linewidth=2.4, alpha=0.95, zorder=3)
    add_events(ax3)
    ax3.set_title("% Negative Posts by Source", fontsize=14,
                  fontweight="bold", loc="left")
    ax3.set_ylabel("% Negative", fontsize=12, fontweight="bold")
    ax3.legend(fontsize=11, loc="upper left", frameon=True, facecolor="white",
               edgecolor="#CCCCCC")

    # Panel 4: Violin distributions with mean/median annotations
    ax4 = axes[1, 1]
    plot_data, plot_labels, plot_colors = [], [], []
    for name, df in sources.items():
        if not df.empty and "polarity" in df.columns:
            pol = df["polarity"].dropna()
            if len(pol) > 10:
                plot_data.append(pol.values)
                plot_labels.append(f"{name}\nn={len(pol):,}")
                plot_colors.append(colors[name])
    if plot_data:
        parts = ax4.violinplot(plot_data, showmeans=True, showmedians=True, widths=0.75)
        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(plot_colors[i])
            pc.set_edgecolor("#333333")
            pc.set_linewidth(1)
            pc.set_alpha(0.65)
        for key in ("cbars", "cmins", "cmaxes", "cmeans", "cmedians"):
            if key in parts:
                parts[key].set_color("#333333")
                parts[key].set_linewidth(1.2)
        ax4.set_xticks(range(1, len(plot_labels) + 1))
        ax4.set_xticklabels(plot_labels, fontsize=12, fontweight="bold")
        for i, data in enumerate(plot_data):
            mean_val = float(np.nanmean(data))
            ax4.annotate(f"μ={mean_val:+.3f}", xy=(i + 1, mean_val),
                         xytext=(8, 0), textcoords="offset points",
                         fontsize=10, fontweight="bold", color="#222222",
                         va="center")
        ax4.set_title("Polarity Distribution by Source", fontsize=14,
                      fontweight="bold", loc="left")
        ax4.set_ylabel("Polarity", fontsize=12, fontweight="bold")
        ax4.axhline(y=0, color="#222222", linewidth=0.6)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    fig.text(0.99, 0.005,
             "Sources: Reddit (18 subreddits) + Student Doctor Network",
             ha="right", fontsize=9, style="italic", color="#888888")
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

    fig, axes = plt.subplots(2, 4, figsize=(28, 15))
    fig.suptitle(
        "PSLF Discussion Word Clouds by Policy Era",
        fontsize=22, fontweight="bold", y=0.985,
    )
    fig.text(0.5, 0.952,
             "Strict PSLF filter; lemmatized (WordNet) + NLTK/sklearn stopwords + domain stops; "
             "Reddit (top row) vs SDN Forum (bottom row)",
             ha="center", fontsize=12, style="italic", color="#555555")

    # Era column headers (above each column, single bold line)
    for i, (label, _, _) in enumerate(periods):
        axes[0, i].text(0.5, 1.18, label,
                        transform=axes[0, i].transAxes,
                        ha="center", va="bottom",
                        fontsize=14, fontweight="bold", color="#222222")

    for i, (label, s, e) in enumerate(periods):
        sub = reddit[(reddit["date"] >= s) & (reddit["date"] <= e)]
        pol = safe_mean_polarity(sub["polarity"]) if "polarity" in sub.columns else 0.0
        pol_color = "#2E7D32" if pol > 0.05 else "#C62828" if pol < -0.05 else "#666666"
        axes[0, i].imshow(_wc_for(sub["text"]), interpolation="bilinear")
        axes[0, i].axis("off")
        axes[0, i].set_title(f"Reddit  •  n={len(sub):,}  •  μ={pol:+.3f}",
                             fontsize=11, color=pol_color, fontweight="bold", pad=6)

    for i, (label, s, e) in enumerate(periods):
        sub = sdn[(sdn["date"] >= s) & (sdn["date"] <= e)]
        pol = safe_mean_polarity(sub["polarity"]) if "polarity" in sub.columns else 0.0
        pol_color = "#2E7D32" if pol > 0.05 else "#C62828" if pol < -0.05 else "#666666"
        axes[1, i].imshow(_wc_for(sub["text"]), interpolation="bilinear")
        axes[1, i].axis("off")
        axes[1, i].set_title(f"SDN  •  n={len(sub):,}  •  μ={pol:+.3f}",
                             fontsize=11, color=pol_color, fontweight="bold", pad=6)

    fig.text(0.99, 0.005,
             "Color: green = positive, red = negative mean polarity (μ)",
             ha="right", fontsize=9, style="italic", color="#888888")

    plt.tight_layout(rect=[0, 0.02, 1, 0.94])
    outpath = os.path.join(output_dir, "pslf_wordcloud_timecourse.png")
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved Fig 2 at 300 DPI: {outpath}")


def _wc_for(texts):
    """Build a WordCloud image from a text series, applying stopwords + lemmatization."""
    import re as _re
    lemmatizer = _get_lemmatizer()
    text_blob = " ".join(texts.fillna("").str.lower())
    tokens = _re.findall(r"\b[a-z]{3,}\b", text_blob)
    filtered = [t for t in tokens if t not in STOP_WORDS]
    lemmatized = [_normalize_token(t, lemmatizer) for t in filtered]
    final = [t for t in lemmatized if len(t) >= 3 and t not in STOP_WORDS]
    freq = Counter(final)
    if len(freq) < 5:
        # Return a small white image
        return np.ones((600, 800, 3))
    wc = WordCloud(
        width=800, height=600, background_color="white", colormap="RdYlGn",
        max_words=100, prefer_horizontal=0.7, scale=2,
    )
    wc.generate_from_frequencies(freq)
    return wc.to_array()


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
