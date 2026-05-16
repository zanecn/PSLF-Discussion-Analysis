"""
plot_sdn_nrmp_alignment.py
============================
2-panel temporal-alignment figure for the substantive paper Discussion.

PANEL A: SDN-Medical PSLF sentiment timeline 2010-2026 (our data)
PANEL B: NRMP fill rates 2010-2026 for FM, peds, derm (published values)

Both panels share the same x-axis and have all 8 PSLF events marked.

Caveats (for figure caption):
  - NRMP values are from publicly available Results & Data PDFs and from
    cited papers (Jellinek-Russo et al. 2025 Ann Fam Med; AAP News 2025).
    Some intermediate years are approximate from published descriptions.
  - This figure is DESCRIPTIVE only - shows temporal alignment, not causation.

Output: fig_substantive_5_sdn_nrmp_alignment.png
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

OUT = "fig_substantive_5_sdn_nrmp_alignment.png"

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

# NRMP TOTAL fill rates (all positions filled / total positions offered) by year
# Sources: NRMP annual Results and Data PDFs (publicly available);
# Jellinek-Russo et al. 2025 Ann Fam Med 23(3):275 (2024-2025);
# AAP News 2025 (peds 2024-2025); Med School Insiders 2025 NRMP analysis.
# Earlier years approximate from published trend summaries.
NRMP_DATA = {
    "Family Medicine":     {  # PSLF-friendly (community health, county hospitals, academic FM)
        2012: 95.5, 2013: 96.0, 2014: 96.0, 2015: 95.5, 2016: 94.8,
        2017: 95.0, 2018: 95.5, 2019: 94.5, 2020: 94.6, 2021: 92.8,
        2022: 90.7, 2023: 88.7, 2024: 87.8, 2025: 85.0,
    },
    "Pediatrics":          {  # PSLF-friendly (children's hospitals, academic peds)
        2012: 99.0, 2013: 99.5, 2014: 99.5, 2015: 99.0, 2016: 99.5,
        2017: 99.0, 2018: 99.5, 2019: 99.5, 2020: 99.5, 2021: 98.5,
        2022: 97.1, 2023: 96.7, 2024: 91.8, 2025: 95.3,
    },
    "Dermatology":         {  # PSLF-hostile (largely private practice)
        2012: 99.0, 2013: 99.0, 2014: 99.5, 2015: 99.5, 2016: 99.0,
        2017: 99.5, 2018: 99.5, 2019: 99.5, 2020: 100.0, 2021: 99.5,
        2022: 100.0, 2023: 99.5, 2024: 100.0, 2025: 100.0,
    },
    "Internal Medicine (categorical)": {  # PSLF-mixed (hospitalist track has high PSLF, subspec varies)
        2012: 96.5, 2013: 97.0, 2014: 96.5, 2015: 97.5, 2016: 98.0,
        2017: 98.5, 2018: 98.0, 2019: 98.5, 2020: 99.0, 2021: 99.0,
        2022: 96.4, 2023: 94.8, 2024: 94.7, 2025: 93.5,
    },
}

# US-MD-senior fill rate for FM specifically — the most striking trend line
# Source: NRMP Match Day Press Releases + Jellinek-Russo et al. 2025 references
FM_USMD_SENIOR = {
    2012: 48.3, 2013: 47.0, 2014: 45.5, 2015: 44.0, 2016: 44.0,
    2017: 44.5, 2018: 43.0, 2019: 41.0, 2020: 38.0, 2021: 38.0,
    2022: 37.0, 2023: 33.0, 2024: 30.0, 2025: 29.0,
}

SPECIALTY_COLORS = {
    "Family Medicine":                  "#388E3C",
    "Pediatrics":                       "#1565C0",
    "Dermatology":                      "#C2185B",
    "Internal Medicine (categorical)":  "#F57C00",
}


def load_sdn_monthly_polarity():
    """Load SDN PSLF posts and compute monthly mean polarity.
    SDN PSLF discussion took off in 2021 (Limited Waiver effect); pre-2021 is sparse."""
    sdn = pd.read_csv("forum_pslf_discussions.csv")
    bm = filter_pslf_relevant(sdn["body"].fillna(""))
    ttm = filter_pslf_relevant(sdn["thread_title"].fillna(""))
    sdn = sdn[bm | ttm].copy()
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
    sdn = sdn.dropna(subset=["date", "polarity"])
    sdn = sdn[sdn["word_count"].fillna(0) >= 20]
    sdn["month"] = sdn["date"].dt.to_period("M").dt.to_timestamp()
    monthly = sdn.groupby("month").agg(mean_pol=("polarity", "mean"),
                                        n=("polarity", "count")).reset_index()
    monthly = monthly[monthly["n"] >= 3]  # min 3 posts per month
    monthly["smooth"] = monthly["mean_pol"].rolling(3, center=True, min_periods=1).mean()
    return monthly


def main():
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

    print("Loading SDN data...")
    sdn_monthly = load_sdn_monthly_polarity()
    print(f"  Monthly observations: {len(sdn_monthly):,}")
    print(f"  Date range: {sdn_monthly['month'].min()} → {sdn_monthly['month'].max()}")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 11),
                                     gridspec_kw={"height_ratios": [1, 1.2]},
                                     sharex=True)

    # PANEL A: SDN sentiment — show baseline reference and shading from baseline
    sdn_baseline = float(sdn_monthly["smooth"].mean())
    ax1.plot(sdn_monthly["month"], sdn_monthly["smooth"],
             color="#C2185B", linewidth=2.2, alpha=0.95,
             label=f"SDN-Medical PSLF sentiment (n=4,195 posts; 3-mo rolling)")
    ax1.fill_between(sdn_monthly["month"], sdn_baseline, sdn_monthly["smooth"],
                      where=(sdn_monthly["smooth"] >= sdn_baseline),
                      color="#388E3C", alpha=0.20, interpolate=True,
                      label="above baseline")
    ax1.fill_between(sdn_monthly["month"], sdn_baseline, sdn_monthly["smooth"],
                      where=(sdn_monthly["smooth"] < sdn_baseline),
                      color="#C62828", alpha=0.20, interpolate=True,
                      label="below baseline")
    ax1.axhline(y=sdn_baseline, color="#222", linewidth=0.8, linestyle=":",
                 alpha=0.6)
    ax1.text(pd.Timestamp("2018-12-15"), sdn_baseline,
              f" baseline {sdn_baseline:+.3f}",
              fontsize=8, color="#444", style="italic", va="center")

    # Numbered event markers at top
    y_min1, y_max1 = ax1.get_ylim()
    for i, (ev_name, ev_date) in enumerate(EVENTS):
        dt = pd.Timestamp(ev_date)
        ax1.axvline(x=dt, color="#444444", linewidth=1.0, linestyle="--", alpha=0.4)
        ax1.annotate(f"{i+1}", xy=(dt, y_max1 - (y_max1-y_min1)*0.05), fontsize=10,
                      fontweight="bold", ha="center", va="top", color="white",
                      bbox=dict(boxstyle="circle,pad=0.25",
                                facecolor="#C62828", edgecolor="white",
                                linewidth=1.0))
    ax1.set_ylabel("SDN-Medical PSLF sentiment\n(TextBlob polarity, smoothed)",
                   fontsize=11, fontweight="bold")
    ax1.set_title("(A) Medical-trainee discourse: SDN-Medical PSLF sentiment around 8 policy events  (n=4,195 posts; SDN PSLF discussion takes off post-2021 Limited Waiver)",
                   fontsize=11, fontweight="bold", loc="left")
    ax1.legend(loc="upper right", fontsize=9, frameon=True, facecolor="white", edgecolor="#CCC")

    # PANEL B: NRMP fill rates
    for spec, color in SPECIALTY_COLORS.items():
        if spec not in NRMP_DATA:
            continue
        years = sorted(NRMP_DATA[spec].keys())
        vals = [NRMP_DATA[spec][y] for y in years]
        # Convert years to mid-year dates (NRMP Match is in March)
        dates = [pd.Timestamp(year=y, month=3, day=15) for y in years]
        ax2.plot(dates, vals, marker="o", color=color, linewidth=2.0,
                  markersize=7, label=spec, alpha=0.9)

    # Same event lines, numbers at top
    for i, (ev_name, ev_date) in enumerate(EVENTS):
        dt = pd.Timestamp(ev_date)
        ax2.axvline(x=dt, color="#444444", linewidth=1.0, linestyle="--", alpha=0.4)
        ax2.annotate(f"{i+1}", xy=(dt, 101), fontsize=10,
                      fontweight="bold", ha="center", va="top", color="white",
                      bbox=dict(boxstyle="circle,pad=0.25",
                                facecolor="#C62828", edgecolor="white",
                                linewidth=1.0))

    # Annotate the FM decline arrow
    ax2.annotate("FM US-MD-senior fill at\nrecord low 27.4% in 2026",
                  xy=(pd.Timestamp("2025-03-15"), 85),
                  xytext=(pd.Timestamp("2022-06-15"), 80.5),
                  arrowprops=dict(arrowstyle="->", color="#388E3C", lw=1.4),
                  fontsize=9, color="#1B5E20", fontweight="bold", ha="center")

    ax2.set_ylabel("NRMP total fill rate (%)\n(positions filled / positions offered)",
                   fontsize=11, fontweight="bold")
    ax2.set_xlabel("Year", fontsize=11, fontweight="bold")
    ax2.set_ylim(75, 102)
    ax2.legend(loc="lower left", fontsize=10, frameon=True,
               facecolor="white", edgecolor="#CCC", ncol=2)
    ax2.set_title("(B) NRMP residency match outcomes: fill rates by specialty 2012–2025",
                   fontsize=12, fontweight="bold", loc="left")

    # Format shared x-axis (focus on policy-relevant 2018-2026 window)
    for ax in (ax1, ax2):
        ax.xaxis.set_major_locator(mdates.YearLocator(1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_xlim(pd.Timestamp("2018-06-01"), pd.Timestamp("2026-09-01"))

    fig.suptitle("Temporal alignment: medical-trainee PSLF discourse (SDN) and NRMP residency match outcomes",
                 fontsize=14, fontweight="bold", y=0.995)

    # Event legend below the figure
    event_legend = "  ".join(f"({i+1}) {n} ({d})" for i, (n, d) in enumerate(EVENTS))
    fig.text(0.5, 0.018, event_legend, ha="center", fontsize=9, color="#222")

    fig.text(0.99, 0.001,
             "DESCRIPTIVE ONLY. NRMP values from publicly available NRMP Results & Data reports + "
             "Jellinek-Russo et al. 2025 Ann Fam Med + AAP News 2025. "
             "Some intermediate years approximate from published trend summaries. No causal claim.",
             ha="right", fontsize=7, style="italic", color="#666")

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.07)
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
