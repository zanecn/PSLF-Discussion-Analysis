"""
gen_volume_artifact_arctic_shift.py
====================================
Re-quantifies the Reddit JSON-API 1000-result-cap volume artifact using
Arctic Shift (Pushshift successor) as the actual longitudinal baseline.

Round-7 limitation made rigorous: the original R/C diagnostic
(`gen_volume_artifact_figure.py`) used the JSON-API Reddit corpus -- which
IS the artifact being measured -- against CFPB Consumer Complaints. With
Arctic Shift's full 2010-present historical pull, we now have an actual
non-capped Reddit baseline. The ratio
    (R_JSON-API / CFPB) / (R_Arctic-Shift / CFPB)
isolates the API-cap bias (>1 = JSON-API over-counts that year, <1 =
JSON-API under-counts that year).

Inputs:
  - admin_data_pslf_complaints.csv     (CFPB PSLF ground truth)
  - reddit_professions_pslf.csv        (JSON-API Reddit -- capped)
  - reddit_arctic_shift_pslf.csv       (Arctic Shift Reddit -- uncapped)

Outputs:
  - volume_artifact_arctic_shift.png   (3-panel figure)
  - volume_artifact_arctic_shift.txt   (canonical numbers)
  - volume_artifact_arctic_shift.csv   (year-level table)

Usage:
  python gen_volume_artifact_arctic_shift.py
"""
from __future__ import annotations

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
import numpy as np
import pandas as pd

from pslf_search_terms import filter_pslf_relevant

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

YEAR_MIN = 2014  # r/PSLF created 2014-08-21; CFPB starts 2016 but we show 2014+
YEAR_MAX = 2025  # 2026 incomplete on both ends


def yearly_count(df: pd.DataFrame, date_col: str = "date") -> pd.Series:
    s = df.groupby(df[date_col].dt.year).size()
    s.index.name = "year"
    return s


def load_jsonapi_reddit() -> pd.Series:
    df = pd.read_csv("reddit_professions_pslf.csv")
    tm = filter_pslf_relevant(df["combined_text"].fillna(""))
    tt = filter_pslf_relevant(df["title"].fillna(""))
    df = df[tm | tt].copy()
    df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"),
                                 unit="s", errors="coerce")
    df = df.dropna(subset=["date"])
    return yearly_count(df)


def load_arctic_shift_reddit() -> pd.Series:
    df = pd.read_csv("reddit_arctic_shift_pslf.csv")
    text_col = "combined_text" if "combined_text" in df.columns else "selftext"
    title_col = "title" if "title" in df.columns else None
    tm = filter_pslf_relevant(df[text_col].fillna(""))
    tt = (filter_pslf_relevant(df[title_col].fillna("")) if title_col
          else pd.Series(False, index=df.index))
    df = df[tm | tt].copy()
    if "created_utc" in df.columns:
        df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"),
                                     unit="s", errors="coerce")
    else:
        df["date"] = pd.to_datetime(df.get("created_datetime", ""),
                                     errors="coerce", utc=True).dt.tz_localize(None)
    df = df.dropna(subset=["date"])
    return yearly_count(df)


def load_cfpb() -> pd.Series:
    df = pd.read_csv("admin_data_pslf_complaints.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True).dt.tz_localize(None)
    df = df.dropna(subset=["date"])
    return yearly_count(df)


def main():
    print("=" * 78)
    print("R/C Volume Artifact - Arctic Shift Baseline Comparison")
    print("=" * 78)

    print("\nLoading series...")
    cfpb = load_cfpb()
    json_api = load_jsonapi_reddit()
    arctic = load_arctic_shift_reddit()
    print(f"  CFPB                   total: {cfpb.sum():>7,}  years: {cfpb.index.min()}-{cfpb.index.max()}")
    print(f"  Reddit JSON-API        total: {json_api.sum():>7,}  years: {json_api.index.min()}-{json_api.index.max()}")
    print(f"  Reddit Arctic Shift    total: {arctic.sum():>7,}  years: {arctic.index.min()}-{arctic.index.max()}")

    # Combine on year axis
    years = list(range(YEAR_MIN, YEAR_MAX + 1))
    table = pd.DataFrame({
        "year": years,
        "CFPB": [int(cfpb.get(y, 0)) for y in years],
        "Reddit_JSONAPI": [int(json_api.get(y, 0)) for y in years],
        "Reddit_ArcticShift": [int(arctic.get(y, 0)) for y in years],
    })

    # R/C ratios; guard divides-by-zero
    table["RC_JSONAPI"] = table.apply(
        lambda r: r["Reddit_JSONAPI"] / r["CFPB"] if r["CFPB"] > 0 else float("nan"), axis=1)
    table["RC_ArcticShift"] = table.apply(
        lambda r: r["Reddit_ArcticShift"] / r["CFPB"] if r["CFPB"] > 0 else float("nan"), axis=1)

    # Bias factor: (JSON-API ratio) / (Arctic Shift ratio)
    # >1 = JSON-API over-counts that year RELATIVE TO uncapped baseline
    # <1 = JSON-API under-counts that year (typical for older years where the
    # cap pushed posts off the visible window)
    table["bias_factor"] = table.apply(
        lambda r: (r["RC_JSONAPI"] / r["RC_ArcticShift"]
                   if (not np.isnan(r["RC_ArcticShift"])) and r["RC_ArcticShift"] > 0
                   else float("nan")),
        axis=1)

    # Direct under-count factor: how many TIMES MORE posts Arctic Shift sees per year
    table["arctic_to_jsonapi_x"] = table.apply(
        lambda r: r["Reddit_ArcticShift"] / r["Reddit_JSONAPI"]
                  if r["Reddit_JSONAPI"] > 0 else float("nan"),
        axis=1)

    print("\nYear-level table:")
    print(table.to_string(index=False, float_format=lambda x: f"{x:>7.2f}"))

    # ---- 3-panel figure ----
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))

    # Panel 1: absolute volumes (log scale)
    ax = axes[0]
    ax.plot(table["year"], table["CFPB"], marker="o", color="#222222",
            label="CFPB Complaints (ground truth)", linewidth=2)
    ax.plot(table["year"], table["Reddit_JSONAPI"], marker="s", color="#FF6B35",
            label="Reddit JSON-API (capped)", linewidth=2)
    ax.plot(table["year"], table["Reddit_ArcticShift"], marker="^", color="#1565C0",
            label="Reddit Arctic Shift (uncapped)", linewidth=2)
    ax.set_yscale("log")
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Posts/Complaints (log scale)", fontweight="bold")
    ax.set_title("Annual PSLF Volume by Source", fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, which="both", alpha=0.3)

    # Panel 2: R/C ratios over time
    ax = axes[1]
    ax.plot(table["year"], table["RC_JSONAPI"], marker="s", color="#FF6B35",
            label="JSON-API / CFPB", linewidth=2)
    ax.plot(table["year"], table["RC_ArcticShift"], marker="^", color="#1565C0",
            label="Arctic Shift / CFPB", linewidth=2)
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("R / C ratio", fontweight="bold")
    ax.set_title("Reddit-to-CFPB Ratio (Capped vs Uncapped)", fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)

    # Panel 3: bias factor (JSON-API over- or under-statement)
    ax = axes[2]
    bf = table["bias_factor"].copy()
    valid = bf.notna()
    colors = ["#FF6B35" if b >= 1 else "#1565C0" for b in bf[valid]]
    ax.bar(table["year"][valid], bf[valid], color=colors, edgecolor="white", linewidth=0.8)
    ax.axhline(y=1.0, color="#222222", linewidth=1.2, linestyle="--", label="No bias (=1)")
    ax.set_xlabel("Year", fontweight="bold")
    ax.set_ylabel("Bias factor: (JSON-API / CFPB) / (Arctic Shift / CFPB)", fontweight="bold")
    ax.set_title("API-Cap Bias by Year\n>1 = JSON-API over-states  <1 = under-states",
                 fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)

    fig.suptitle("Reddit JSON-API 1000-Result-Cap Volume Artifact, Quantified Against\n"
                 "Arctic Shift (Pushshift Successor) as Uncapped Longitudinal Baseline",
                 fontsize=14, fontweight="bold", y=1.02)

    plt.tight_layout()
    out_png = "volume_artifact_arctic_shift.png"
    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"\nSaved: {out_png}")

    # ---- Text artifact ----
    out_txt = "volume_artifact_arctic_shift.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Volume Artifact Diagnostic - Arctic Shift Baseline Comparison\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/gen_volume_artifact_arctic_shift.py\n")
        f.write("=" * 80 + "\n\n")

        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Quantifies the magnitude of the Reddit JSON-API 1000-result-per-listing\n")
        f.write("cap as a volume-growth artifact, using Arctic Shift (Pushshift successor;\n")
        f.write("uncapped historical access) as the actual longitudinal Reddit baseline.\n")
        f.write("Compared to the previous diagnostic which only had CFPB as ground truth\n")
        f.write("(and used the artifact-affected series as the 'Reddit' input).\n\n")

        f.write("TOTALS (PSLF-strict-filtered)\n")
        f.write("-" * 80 + "\n")
        f.write(f"  CFPB Complaints:                {cfpb.sum():>8,}\n")
        f.write(f"  Reddit JSON-API (capped):       {json_api.sum():>8,}\n")
        f.write(f"  Reddit Arctic Shift (uncapped): {arctic.sum():>8,}  "
                f"({arctic.sum()/max(json_api.sum(),1):.1f}x JSON-API)\n\n")

        f.write("YEAR-LEVEL TABLE\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'year':>4s} {'CFPB':>6s} {'JSON-API':>9s} {'Arctic':>8s} "
                f"{'RC_JA':>7s} {'RC_AS':>7s} {'bias':>7s} {'AS/JA':>7s}\n")
        for _, r in table.iterrows():
            bf = f"{r['bias_factor']:.2f}" if not np.isnan(r['bias_factor']) else "  n/a"
            asja = f"{r['arctic_to_jsonapi_x']:.1f}" if not np.isnan(r['arctic_to_jsonapi_x']) else "  n/a"
            rcja = f"{r['RC_JSONAPI']:.2f}" if not np.isnan(r['RC_JSONAPI']) else "  n/a"
            rcas = f"{r['RC_ArcticShift']:.2f}" if not np.isnan(r['RC_ArcticShift']) else "  n/a"
            f.write(f"{int(r['year']):>4d} {int(r['CFPB']):>6d} {int(r['Reddit_JSONAPI']):>9d} "
                    f"{int(r['Reddit_ArcticShift']):>8d} {rcja:>7s} {rcas:>7s} "
                    f"{bf:>7s} {asja:>7s}\n")

        # Key claims for the methods paper
        f.write("\nKEY METHODS-PAPER CLAIMS\n")
        f.write("-" * 80 + "\n")
        # Find years where JSON-API undercounts (bias < 1) and overcounts (bias > 1)
        undercount = table[(table["bias_factor"].notna()) & (table["bias_factor"] < 0.5)]
        overcount = table[(table["bias_factor"].notna()) & (table["bias_factor"] > 2.0)]
        if len(undercount):
            f.write(f"  YEARS WHERE JSON-API UNDER-COUNTS BY 2x OR MORE:\n")
            for _, r in undercount.iterrows():
                f.write(f"    {int(r['year'])}: bias={r['bias_factor']:.2f} "
                        f"(Arctic Shift sees {r['arctic_to_jsonapi_x']:.0f}x more posts than JSON-API)\n")
        if len(overcount):
            f.write(f"\n  YEARS WHERE JSON-API OVER-STATES VOLUME BY 2x OR MORE:\n")
            for _, r in overcount.iterrows():
                f.write(f"    {int(r['year'])}: bias={r['bias_factor']:.2f}\n")

        # The peak recency-bias multiplier
        nz_bias = table[table["bias_factor"].notna() & (table["bias_factor"] > 0)]
        if len(nz_bias) >= 2:
            min_bias = nz_bias.loc[nz_bias["bias_factor"].idxmin()]
            max_bias = nz_bias.loc[nz_bias["bias_factor"].idxmax()]
            recency_mult = max_bias["bias_factor"] / min_bias["bias_factor"]
            f.write(f"\n  PEAK RECENCY-BIAS MULTIPLIER:\n")
            f.write(f"    Min bias: {min_bias['bias_factor']:.3f} in {int(min_bias['year'])}\n")
            f.write(f"    Max bias: {max_bias['bias_factor']:.3f} in {int(max_bias['year'])}\n")
            f.write(f"    Multiplier (max/min): ~{recency_mult:.0f}x recency bias in JSON-API\n")
            f.write(f"\n  This is the canonical methods-paper claim, made rigorous:\n")
            f.write(f"  the Reddit JSON-API 1000-cap creates ~{recency_mult:.0f}x recency bias\n")
            f.write(f"  when measured against an uncapped longitudinal baseline.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {out_txt}")

    out_csv = "volume_artifact_arctic_shift.csv"
    table.to_csv(out_csv, index=False, float_format="%.4f")
    print(f"Saved: {out_csv}")

    print("\nKEY RESULT:")
    nz = table[table["bias_factor"].notna() & (table["bias_factor"] > 0)]
    if len(nz) >= 2:
        print(f"  Min bias: {nz['bias_factor'].min():.3f}  Max bias: {nz['bias_factor'].max():.3f}")
        print(f"  ~{nz['bias_factor'].max()/nz['bias_factor'].min():.0f}x recency bias")


if __name__ == "__main__":
    main()
