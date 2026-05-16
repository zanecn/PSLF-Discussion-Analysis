"""
plot_master_timeline_3scorer.py
================================
Master calendar timeline with ALL THREE scorers + volume:
  Panel 1: TextBlob polarity (continuous, lexical affect)
  Panel 2: VADER compound (continuous, expressive arousal)
  Panel 3: Claude pslf_sentiment (5-level ordinal mapped to -2..+2, stance)
  Panel 4: monthly post volume by cohort (stacked area)

Each sentiment panel: monthly mean by cohort, 3-month rolling smooth.
Claude panel additionally shaded to indicate months with thin coverage
(< 10 Claude-scored posts in any cohort).

Output: pslf_master_timeline_3scorer.png
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from pslf_search_terms import filter_pslf_relevant

EVENTS = [
    ("Limited PSLF Waiver",            "2021-10-06"),
    ("IDR Account Adjustment",         "2022-04-19"),
    ("Biden Mass Forgiveness",         "2022-08-24"),
    ("Biden v. Nebraska SCOTUS",       "2023-06-30"),
    ("Payments Restart",               "2023-10-01"),
    ("SAVE Admin Forbearance",         "2024-08-09"),
    ("Trump PSLF EO",                  "2025-03-07"),
    ("Final Trump PSLF Rule",          "2025-10-30"),
]

COHORT_COLORS = {
    "SDN (Medical)":            "#C2185B",
    "Reddit r/PSLF":            "#1565C0",
    "Reddit r/StudentLoans":    "#388E3C",
    "Reddit Finance":           "#F57C00",
}

PROF_LABEL = {
    "general_pslf": "Reddit r/PSLF",
    "general_student_loans": "Reddit r/StudentLoans",
    "general_finance": "Reddit Finance",
    "personalfinance": "Reddit Finance",
    "financialindependence": "Reddit Finance",
    "sdn_medical": "SDN (Medical)",
    "sdn": "SDN (Medical)",
}

CLAUDE_NUMERIC = {
    "very_negative": -2, "negative": -1, "neutral": 0,
    "positive": 1, "very_positive": 2,
}

ZEROSHOT_CSVS = [
    "zeroshot_reddit_n1000.csv",
    "zeroshot_sdn_n1000.csv",
    "zeroshot_reddit_eventstrat.csv",
    "zeroshot_reddit_eventfull.csv",
    "zeroshot_sdn_eventfull.csv",
    "zeroshot_pa_np_expansion.csv",
    "zeroshot_reddit_fullcorpus.csv",
    "zeroshot_reddit_arctic_shift_fill.csv",  # round-8 (when present)
]


def load_corpus_with_all_scorers():
    """Load corpus with TB+VADER from source CSVs and Claude from zeroshot CSVs.
    Returns DataFrame with: date, polarity, vader_compound, claude_numeric, profession, cohort, word_count.
    Claude_numeric will be NaN for posts that haven't been Claude-scored.
    """
    frames = []
    needed_with_claude = ["date", "polarity", "vader_compound", "profession", "word_count", "post_id"]

    def _slim(d, prof_default=None, text_col_for_wc=None, id_col=None):
        if "profession" not in d.columns and prof_default:
            d["profession"] = prof_default
        if "vader_compound" not in d.columns:
            d["vader_compound"] = np.nan
        if "word_count" not in d.columns:
            d["word_count"] = (d[text_col_for_wc].fillna("").str.split().str.len()
                                if text_col_for_wc else 100)
        if id_col and id_col != "post_id":
            d = d.rename(columns={id_col: "post_id"})
        if "post_id" not in d.columns:
            d["post_id"] = ""
        return d[needed_with_claude].copy()

    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teaching")]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
            d["profession"] = prof
            tcol = "combined_text" if "combined_text" in d.columns else "selftext"
            frames.append(_slim(d, text_col_for_wc=tcol, id_col="id"))

    if os.path.exists("reddit_professions_pslf.csv"):
        d = pd.read_csv("reddit_professions_pslf.csv")
        tm = filter_pslf_relevant(d["combined_text"].fillna(""))
        tt = filter_pslf_relevant(d["title"].fillna(""))
        d = d[tm | tt].copy()
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        frames.append(_slim(d, text_col_for_wc="combined_text", id_col="id"))

    if os.path.exists("reddit_arctic_shift_pslf.csv"):
        d = pd.read_csv("reddit_arctic_shift_pslf.csv")
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        frames.append(_slim(d, text_col_for_wc="combined_text", id_col="id"))

    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        bm = filter_pslf_relevant(d["body"].fillna(""))
        ttm = filter_pslf_relevant(d["thread_title"].fillna(""))
        d = d[bm | ttm].copy()
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        d["profession"] = "sdn_medical"
        frames.append(_slim(d, text_col_for_wc="body"))  # SDN already has post_id

    big = pd.concat(frames, ignore_index=True)
    big = big.dropna(subset=["date", "polarity"])
    big = big[big["word_count"].fillna(0) >= 20]
    big["date"] = pd.to_datetime(big["date"], utc=True, errors="coerce").dt.tz_localize(None)
    big["cohort"] = big["profession"].map(PROF_LABEL).fillna("Other")
    big = big[big["cohort"] != "Other"].copy()
    big = big[(big["date"] >= pd.Timestamp("2010-01-01")) &
              (big["date"] <= pd.Timestamp("2026-04-01"))]

    # Now merge Claude scores
    print(f"Loaded {len(big):,} TB/VADER-scored posts. Loading Claude scores...")
    claude_frames = []
    for f in ZEROSHOT_CSVS:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        if "post_id" not in d.columns:
            continue
        d = d[~d["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
        d["claude_numeric"] = d["pslf_sentiment"].map(CLAUDE_NUMERIC)
        claude_frames.append(d[["post_id", "claude_numeric"]])
        print(f"  {f}: {len(d):,} Claude-scored posts")
    if claude_frames:
        claude = pd.concat(claude_frames, ignore_index=True).drop_duplicates("post_id")
        big["post_id"] = big["post_id"].astype(str)
        claude["post_id"] = claude["post_id"].astype(str)
        big = big.merge(claude, on="post_id", how="left")
        n_claude = big["claude_numeric"].notna().sum()
        print(f"  Claude coverage on master corpus: {n_claude:,}/{len(big):,} "
              f"({100*n_claude/len(big):.1f}%)")
    else:
        big["claude_numeric"] = np.nan

    return big


def main():
    df = load_corpus_with_all_scorers()
    print()
    print(df["cohort"].value_counts().to_string())

    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

    plt.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#DDDDDD",
        "grid.linewidth": 0.5,
        "grid.alpha": 0.6,
        "legend.frameon": False,
        "font.family": "DejaVu Sans",
    })

    fig, axes = plt.subplots(4, 1, figsize=(20, 16),
                              gridspec_kw={"height_ratios": [1.4, 1.4, 1.4, 1.0]},
                              sharex=True)
    ax_tb, ax_va, ax_cl, ax_vol = axes

    cohorts_to_plot = ["SDN (Medical)", "Reddit r/PSLF",
                       "Reddit r/StudentLoans", "Reddit Finance"]

    def plot_scorer(ax, scorer_col, scorer_label, min_n=5, smooth=3):
        for cohort in cohorts_to_plot:
            sub = df[(df["cohort"] == cohort) & df[scorer_col].notna()]
            if len(sub) < 100:
                continue
            monthly = (sub.groupby("month")[scorer_col]
                       .agg(["mean", "count"]).reset_index())
            monthly = monthly[monthly["count"] >= min_n]
            monthly["smooth"] = (monthly["mean"]
                                  .rolling(smooth, center=True, min_periods=1).mean())
            n_months = len(monthly)
            n_total = int(sub.shape[0])
            ax.plot(monthly["month"], monthly["smooth"],
                    color=COHORT_COLORS[cohort], linewidth=1.8,
                    label=f"{cohort} (n={n_total:,}, {n_months} mo)", alpha=0.95)

        # Event vertical lines + numbered markers
        y_min, y_max = ax.get_ylim()
        for i, (ev_name, ev_date) in enumerate(EVENTS):
            dt = pd.Timestamp(ev_date)
            ax.axvline(x=dt, color="#444444", linewidth=1.0,
                       linestyle="--", alpha=0.5)
            ax.annotate(f"{i+1}", xy=(dt, y_max * 0.97), fontsize=9,
                        fontweight="bold", ha="center", va="top",
                        color="white",
                        bbox=dict(boxstyle="circle,pad=0.25",
                                  facecolor="#C62828", edgecolor="white",
                                  linewidth=1.0))
        ax.set_ylabel(scorer_label, fontsize=11, fontweight="bold")
        ax.legend(loc="upper left", fontsize=8, frameon=True,
                  facecolor="white", edgecolor="#CCCCCC", ncol=2)
        ax.set_axisbelow(True)
        ax.axhline(y=0, color="#222", linewidth=0.6, alpha=0.4)

    plot_scorer(ax_tb, "polarity",        "TextBlob polarity\n(lexical affect)", min_n=5, smooth=3)
    plot_scorer(ax_va, "vader_compound",  "VADER compound\n(expressive arousal)", min_n=5, smooth=3)
    plot_scorer(ax_cl, "claude_numeric",  "Claude pslf_sentiment\n(stance, -2..+2)",
                min_n=3, smooth=3)  # Claude has thinner coverage; allow lower min_n

    ax_tb.set_title("PSLF Discourse Sentiment 2010-2026 by Cohort, Three Scorers + Volume\n"
                    f"Full corpus including Arctic Shift historical pull (n={len(df):,} posts)",
                    fontsize=14, fontweight="bold", loc="left")

    # Volume panel (stacked area)
    vol = (df.groupby(["month", "cohort"])
           .size().reset_index(name="n").pivot(index="month", columns="cohort",
                                                 values="n").fillna(0))
    vol = vol[sorted(vol.columns, key=lambda c: vol[c].sum(), reverse=True)]
    ax_vol.stackplot(vol.index,
                      [vol[c].values for c in vol.columns],
                      labels=vol.columns.tolist(),
                      colors=[COHORT_COLORS.get(c, "#888888") for c in vol.columns],
                      alpha=0.75)
    for ev_name, ev_date in EVENTS:
        dt = pd.Timestamp(ev_date)
        ax_vol.axvline(x=dt, color="#444444", linewidth=1.0,
                       linestyle="--", alpha=0.4)
    ax_vol.set_ylabel("Posts per month\n(stacked)", fontsize=11, fontweight="bold")
    ax_vol.set_xlabel("Date", fontsize=11, fontweight="bold")
    ax_vol.legend(loc="upper left", fontsize=8, ncol=4)
    ax_vol.set_axisbelow(True)

    for ax in axes:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.set_xlim(pd.Timestamp("2010-06-01"), pd.Timestamp("2026-04-01"))

    event_legend = "  ".join(f"({i+1}) {n} ({d})" for i, (n, d) in enumerate(EVENTS))
    fig.text(0.5, 0.012, event_legend,
             ha="center", fontsize=9, color="#222222")
    fig.text(0.99, 0.001,
             "All sentiment panels: monthly mean by cohort, 3-month centered rolling smooth.\n"
             "TextBlob/VADER use full corpus (n=73K+); Claude uses subsample with PSLF-stance scoring (~9K posts after Arctic Shift fill).",
             ha="right", fontsize=7, style="italic", color="#666666")

    plt.tight_layout()
    out = "pslf_master_timeline_3scorer.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
