"""
plot_event_timecourses.py
=========================
Event-study timecourse plot: for each of the 8 PSLF events, show daily
mean sentiment by profession in the +/-90d window around the event.

Designed to make the cohort-heterogeneity finding visually obvious. The
two largest cohorts (SDN-Medical, r/PSLF) often move opposite directions
within the same event window; this plot shows it.

Inputs:  same source CSVs as gen_legislative_timeline.py + Arctic Shift
Outputs:
  - pslf_event_timecourses.png    (8-panel grid, TextBlob)
  - pslf_event_timecourses_vader.png (8-panel grid, VADER)
  - pslf_event_timecourses_combined.png (one big composite figure)

Usage:
  python plot_event_timecourses.py
  python plot_event_timecourses.py --scorer vader
  python plot_event_timecourses.py --window 60   # short window
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import warnings
from datetime import datetime

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
    ("Limited PSLF Waiver",            "2021-10-06", 90),
    ("IDR Account Adjustment",         "2022-04-19", 90),
    ("Biden Mass Forgiveness",         "2022-08-24", 90),
    ("Biden v. Nebraska SCOTUS",       "2023-06-30", 90),
    ("Payments Restart",               "2023-10-01", 90),
    ("SAVE Admin Forbearance",         "2024-08-09", 90),
    ("Trump PSLF EO",                  "2025-03-07", 60),
    ("Final Trump PSLF Rule",          "2025-10-30", 60),
]

# Colors per cohort (consistent across panels)
COHORT_COLORS = {
    "SDN (Medical)":            "#C2185B",  # raspberry
    "Reddit r/PSLF":            "#1565C0",  # blue
    "Reddit r/StudentLoans":    "#388E3C",  # green
    "Reddit Finance":           "#F57C00",  # orange
    "Reddit Medical":           "#6A1B9A",  # purple
    "Reddit PA":                "#00838F",  # teal
    "Other professions":        "#757575",  # grey
}

PROF_LABEL = {
    "medical": "Reddit Medical",
    "teaching": "Reddit Teaching",
    "nursing": "Reddit Nursing",
    "law": "Reddit Law",
    "pharmacy": "Reddit Pharmacy",
    "physician_assistant": "Reddit PA",
    "social_work": "Other professions",
    "occupational_therapy": "Other professions",
    "speech_language_pathology": "Other professions",
    "federal_employee": "Other professions",
    "general_pslf": "Reddit r/PSLF",
    "general_student_loans": "Reddit r/StudentLoans",
    "general_finance": "Reddit Finance",
    "personalfinance": "Reddit Finance",
    "financialindependence": "Reddit Finance",
    "sdn_medical": "SDN (Medical)",
    "sdn": "SDN (Medical)",
}


def load_corpus() -> pd.DataFrame:
    """Reused logic from analyze_per_profession_per_event.py."""
    frames = []

    needed = ["date", "polarity", "vader_compound", "profession", "word_count"]

    def _slim(d, prof_default=None, text_col_for_wc=None):
        if "profession" not in d.columns and prof_default:
            d["profession"] = prof_default
        if "vader_compound" not in d.columns:
            d["vader_compound"] = np.nan
        if "word_count" not in d.columns:
            wc_text = d[text_col_for_wc].fillna("") if text_col_for_wc else ""
            d["word_count"] = (wc_text.str.split().str.len() if text_col_for_wc
                                else 100)  # legacy fallback - assume long enough
        return d[needed]

    for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                    ("comprehensive_teacher_pslf_discussions.csv", "teaching")]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
            d["profession"] = prof
            tcol = ("combined_text" if "combined_text" in d.columns
                    else "selftext" if "selftext" in d.columns else None)
            frames.append(_slim(d, text_col_for_wc=tcol))

    if os.path.exists("reddit_professions_pslf.csv"):
        d = pd.read_csv("reddit_professions_pslf.csv")
        tm = filter_pslf_relevant(d["combined_text"].fillna(""))
        tt = filter_pslf_relevant(d["title"].fillna(""))
        d = d[tm | tt].copy()
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        frames.append(_slim(d, text_col_for_wc="combined_text"))

    if os.path.exists("reddit_arctic_shift_pslf.csv"):
        d = pd.read_csv("reddit_arctic_shift_pslf.csv")
        d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"), unit="s")
        frames.append(_slim(d, text_col_for_wc="combined_text"))

    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        bm = filter_pslf_relevant(d["body"].fillna(""))
        ttm = filter_pslf_relevant(d["thread_title"].fillna(""))
        d = d[bm | ttm].copy()
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        d["profession"] = "sdn_medical"
        frames.append(_slim(d, text_col_for_wc="body"))

    big = pd.concat(frames, ignore_index=True)
    big = big.dropna(subset=["date", "polarity"])
    big = big[big["word_count"].fillna(0) >= 20]
    big["date"] = pd.to_datetime(big["date"], utc=True, errors="coerce").dt.tz_localize(None)
    big["cohort"] = big["profession"].map(PROF_LABEL).fillna("Other professions")
    return big


def event_panel(ax, df, event_name, event_date, window, scorer_col,
                cohorts_to_plot, smooth_days=14, min_n_per_day=3):
    """Plot daily mean sentiment by cohort in a +/-window day span around event."""
    dt = pd.Timestamp(event_date)
    sub = df[(df["date"] >= dt - pd.Timedelta(days=window)) &
             (df["date"] <= dt + pd.Timedelta(days=window))].copy()
    sub["day_offset"] = (sub["date"] - dt).dt.days

    # Per-cohort daily mean + count
    has_data = []
    for cohort in cohorts_to_plot:
        c_sub = sub[sub["cohort"] == cohort]
        if len(c_sub) < min_n_per_day * window:  # rough adequacy check
            continue
        daily = (c_sub.groupby("day_offset")[scorer_col]
                 .agg(["mean", "count"]).reset_index())
        # Hide days with too few posts
        daily.loc[daily["count"] < min_n_per_day, "mean"] = np.nan
        # Rolling mean smooth (centered)
        daily["smooth"] = (daily["mean"]
                            .rolling(smooth_days, center=True, min_periods=3)
                            .mean())
        # Plot
        ax.plot(daily["day_offset"], daily["smooth"],
                color=COHORT_COLORS.get(cohort, "#888888"), linewidth=2.0,
                label=f"{cohort} (n={len(c_sub):,})", alpha=0.9)
        has_data.append(cohort)

    # Pre-event mean reference (across all plotted cohorts)
    pre = sub[sub["day_offset"] < 0]
    if len(pre):
        pre_mean = pre[scorer_col].mean()
        ax.axhline(y=pre_mean, color="#222222", linewidth=0.8, linestyle=":", alpha=0.4)

    # Event date vertical line
    ax.axvline(x=0, color="#C62828", linewidth=1.5, alpha=0.7)
    ax.set_title(f"{event_name}\n({event_date}, +/-{window}d)",
                 fontsize=11, fontweight="bold")
    ax.set_xlabel("Days from event", fontsize=9)
    ax.set_ylabel("polarity (smoothed)" if "polarity" in scorer_col else "VADER (smoothed)",
                  fontsize=9)
    ax.grid(True, alpha=0.3)
    return has_data


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--scorer", choices=["textblob", "vader", "both"],
                        default="both", help="Which scorer(s) to plot")
    parser.add_argument("--window", type=int, default=None,
                        help="Override window size (days); default uses event-specific window")
    parser.add_argument("--smooth-days", type=int, default=14,
                        help="Rolling-mean smoothing window in days")
    parser.add_argument("--min-n-per-day", type=int, default=3,
                        help="Minimum posts per day to plot a daily mean")
    args = parser.parse_args()

    print("=" * 78)
    print("PSLF Event-Time Timecourse Plot")
    print("=" * 78)

    print("\nLoading corpus...")
    df = load_corpus()
    print(f"  Total docs: {len(df):,}")
    print(f"  Cohorts: {df['cohort'].value_counts().to_dict()}")

    cohorts_to_plot = [
        "SDN (Medical)", "Reddit r/PSLF", "Reddit r/StudentLoans",
        "Reddit Finance", "Reddit Medical",
    ]

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
        "legend.frameon": False,
        "font.family": "DejaVu Sans",
    })

    scorers = []
    if args.scorer in ("textblob", "both"):
        scorers.append(("polarity", "TextBlob polarity", "pslf_event_timecourses.png"))
    if args.scorer in ("vader", "both"):
        scorers.append(("vader_compound", "VADER compound", "pslf_event_timecourses_vader.png"))

    for scorer_col, scorer_label, out_png in scorers:
        print(f"\nGenerating {out_png} ({scorer_label})...")
        fig, axes = plt.subplots(4, 2, figsize=(16, 18))
        axes_flat = axes.flatten()
        for i, (ev_name, ev_date, win) in enumerate(EVENTS):
            window = args.window or win
            event_panel(axes_flat[i], df, ev_name, ev_date, window,
                        scorer_col, cohorts_to_plot,
                        smooth_days=args.smooth_days,
                        min_n_per_day=args.min_n_per_day)
            if i == 0:
                axes_flat[i].legend(loc="upper left", fontsize=8,
                                    ncol=1, framealpha=0.9, frameon=True)
        fig.suptitle(f"PSLF Sentiment Timecourse around 8 Policy Events ({scorer_label})\n"
                     f"Daily mean, {args.smooth_days}-day rolling smooth, "
                     f"by cohort. Vertical red = event; dotted = pre-event mean",
                     fontsize=14, fontweight="bold", y=1.005)
        plt.tight_layout()
        plt.savefig(out_png, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"  Saved: {out_png}")

    # Composite figure: TextBlob + VADER side by side for the 4 most informative events
    if args.scorer == "both":
        print("\nGenerating composite figure (TextBlob + VADER for 4 key events)...")
        key_events = [("Trump PSLF EO", "2025-03-07", 60),
                      ("SAVE Admin Forbearance", "2024-08-09", 90),
                      ("Payments Restart", "2023-10-01", 90),
                      ("Final Trump PSLF Rule", "2025-10-30", 60)]
        fig, axes = plt.subplots(4, 2, figsize=(16, 18))
        for i, (ev_name, ev_date, win) in enumerate(key_events):
            window = args.window or win
            event_panel(axes[i, 0], df, ev_name, ev_date, window,
                        "polarity", cohorts_to_plot,
                        smooth_days=args.smooth_days,
                        min_n_per_day=args.min_n_per_day)
            event_panel(axes[i, 1], df, ev_name, ev_date, window,
                        "vader_compound", cohorts_to_plot,
                        smooth_days=args.smooth_days,
                        min_n_per_day=args.min_n_per_day)
            axes[i, 0].set_title(f"{ev_name} (TextBlob)", fontsize=11, fontweight="bold")
            axes[i, 1].set_title(f"{ev_name} (VADER)", fontsize=11, fontweight="bold")
            if i == 0:
                axes[i, 0].legend(loc="upper left", fontsize=8, framealpha=0.9, frameon=True)
        fig.suptitle("PSLF Sentiment Timecourse: 4 key events, two scorers side-by-side\n"
                     "TextBlob (left) vs VADER (right). Cohorts often move opposite directions.",
                     fontsize=14, fontweight="bold", y=1.005)
        plt.tight_layout()
        out_combined = "pslf_event_timecourses_combined.png"
        plt.savefig(out_combined, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"  Saved: {out_combined}")


if __name__ == "__main__":
    main()
