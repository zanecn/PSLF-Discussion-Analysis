"""
plot_master_timeline.py
========================
ONE complete calendar-time timeline showing PSLF discourse from 2010-2026:
  - Top panel:   monthly polarity by cohort (SDN, r/PSLF, r/StudentLoans, Finance)
  - Bottom panel: monthly post volume by cohort (log scale, stacked area)
  - All 8 policy events marked as vertical lines with labels

Output: pslf_master_timeline.png
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


def load_corpus():
    frames = []
    needed = ["date", "polarity", "profession", "word_count"]

    def _slim(d, prof_default=None, text_col_for_wc=None):
        if "profession" not in d.columns and prof_default:
            d["profession"] = prof_default
        if "word_count" not in d.columns:
            d["word_count"] = (d[text_col_for_wc].fillna("").str.split().str.len()
                                if text_col_for_wc else 100)
        return d[needed].copy()

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
    big["cohort"] = big["profession"].map(PROF_LABEL).fillna("Other")
    big = big[big["cohort"] != "Other"].copy()
    big = big[(big["date"] >= pd.Timestamp("2010-01-01")) &
              (big["date"] <= pd.Timestamp("2026-04-01"))]
    return big


def main():
    print("Loading corpus...")
    df = load_corpus()
    print(f"  Total: {len(df):,}")
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

    fig, (ax_sent, ax_vol) = plt.subplots(2, 1, figsize=(20, 11),
                                           gridspec_kw={"height_ratios": [2.2, 1]},
                                           sharex=True)

    # ---- Top: sentiment ----
    cohorts_to_plot = ["SDN (Medical)", "Reddit r/PSLF",
                       "Reddit r/StudentLoans", "Reddit Finance"]

    for cohort in cohorts_to_plot:
        sub = df[df["cohort"] == cohort]
        if len(sub) < 100:
            continue
        monthly = (sub.groupby("month")["polarity"]
                   .agg(["mean", "count"]).reset_index())
        monthly = monthly[monthly["count"] >= 5]  # require min 5 posts/month
        # 3-month centered rolling mean for smoothing
        monthly["smooth"] = (monthly["mean"]
                              .rolling(3, center=True, min_periods=1).mean())
        ax_sent.plot(monthly["month"], monthly["smooth"],
                     color=COHORT_COLORS[cohort], linewidth=2.0,
                     label=f"{cohort} (n={len(sub):,})", alpha=0.95)

    # Event vertical lines + numbered markers (legend below the plot)
    # Numbering avoids label overlap when events cluster 2021-2025.
    y_min, y_max = ax_sent.get_ylim()
    for i, (ev_name, ev_date) in enumerate(EVENTS):
        dt = pd.Timestamp(ev_date)
        ax_sent.axvline(x=dt, color="#444444", linewidth=1.0,
                        linestyle="--", alpha=0.5)
        # Numbered marker at top of plot
        ax_sent.annotate(f"{i+1}", xy=(dt, y_max * 0.97), fontsize=10,
                         fontweight="bold", ha="center", va="top",
                         color="white",
                         bbox=dict(boxstyle="circle,pad=0.3",
                                   facecolor="#C62828", edgecolor="white",
                                   linewidth=1.2))

    ax_sent.set_ylabel("TextBlob polarity (3-mo smoothed)", fontsize=12, fontweight="bold")
    ax_sent.set_title("PSLF Discourse Sentiment 2010–2026 by Cohort, with Policy Events Marked\n"
                      f"Full corpus including Arctic Shift historical pull (n={len(df):,} posts; min 5 posts/month)",
                      fontsize=14, fontweight="bold", loc="left")
    ax_sent.legend(loc="upper left", fontsize=10, frameon=True,
                   facecolor="white", edgecolor="#CCCCCC")
    ax_sent.set_axisbelow(True)
    ax_sent.axhline(y=0, color="#222", linewidth=0.6)

    # ---- Bottom: post volume by cohort ----
    vol = (df.groupby(["month", "cohort"])
           .size().reset_index(name="n").pivot(index="month", columns="cohort",
                                                 values="n").fillna(0))
    # Reorder columns by total
    vol = vol[sorted(vol.columns, key=lambda c: vol[c].sum(), reverse=True)]
    # Plot stacked area (linear, since log breaks 0s)
    ax_vol.stackplot(vol.index,
                      [vol[c].values for c in vol.columns],
                      labels=vol.columns.tolist(),
                      colors=[COHORT_COLORS.get(c, "#888888") for c in vol.columns],
                      alpha=0.75)
    ax_vol.set_ylabel("Posts per month", fontsize=11, fontweight="bold")
    ax_vol.set_xlabel("Date", fontsize=11, fontweight="bold")

    # Same event lines on volume panel (no labels to avoid clutter)
    for ev_name, ev_date in EVENTS:
        dt = pd.Timestamp(ev_date)
        ax_vol.axvline(x=dt, color="#444444", linewidth=1.0,
                       linestyle="--", alpha=0.4)

    ax_vol.legend(loc="upper left", fontsize=9, ncol=4)
    ax_vol.set_axisbelow(True)

    # Format x-axis
    for ax in (ax_sent, ax_vol):
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.set_xlim(pd.Timestamp("2010-06-01"), pd.Timestamp("2026-04-01"))

    # Event legend at bottom
    event_legend = "  ".join(f"({i+1}) {n} ({d})" for i, (n, d) in enumerate(EVENTS))
    fig.text(0.5, 0.012, event_legend,
             ha="center", fontsize=9, color="#222222")
    fig.text(0.99, 0.001,
             "Sentiment: TextBlob polarity, 3-month centered rolling mean. Volume: monthly post count, stacked.\n"
             "Cohorts: SDN (medical-vocational forum), Reddit r/PSLF (general PSLF), r/StudentLoans (general SL), Finance.",
             ha="right", fontsize=7, style="italic", color="#666666")

    plt.tight_layout()
    out = "pslf_master_timeline.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
