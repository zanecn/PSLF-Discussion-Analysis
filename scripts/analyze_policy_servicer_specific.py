"""
analyze_policy_servicer_specific.py
=====================================
P2 (policy): Servicer-specific sentiment timeline.

MOHELA was the consolidated PSLF servicer 2022-July-2024. Before that, FedLoan
Servicing held that role. After 2024, multiple servicers handle PSLF.

Tracks discourse mentions of MOHELA, FedLoan, Nelnet, Aidvantage over time
to inform future PSLF servicer contract decisions.

Output: policy_servicer_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, sys, re, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "policy_servicer_results.txt"
OUT_CSV = "policy_servicer_results.csv"
OUT_PNG = "policy_servicer_results.png"

SERVICERS = {
    "MOHELA": [r"\bMOHELA\b", r"\bMOHELA's\b"],
    "FedLoan": [r"\bFedLoan\b", r"\bPHEAA\b", r"\bFedloan\b"],
    "Nelnet": [r"\bNelnet\b"],
    "Aidvantage": [r"\bAidvantage\b"],
    "Navient": [r"\bNavient\b"],
    "Great Lakes": [r"\bGreat Lakes\b"],
    "EdFinancial": [r"\bEdFinancial\b", r"\bEdfinancial\b"],
    "Sallie Mae": [r"\bSallie Mae\b"],
}

# Servicer-related events
SERVICER_EVENTS = [
    ("MOHELA assumes PSLF", "2022-07-01"),
    ("Payments restart", "2023-10-01"),
    ("PSLF servicer transition (multiple)", "2024-07-01"),
]


def main():
    print("=" * 80)
    print("P2: PSLF servicer-specific discourse timeline")
    print("=" * 80)

    all_rows = []

    # SDN PSLF posts
    if os.path.exists("forum_pslf_discussions.csv"):
        from pslf_search_terms import filter_pslf_relevant
        sdn = pd.read_csv("forum_pslf_discussions.csv", low_memory=False)
        bm = filter_pslf_relevant(sdn["body"].fillna(""))
        ttm = filter_pslf_relevant(sdn["thread_title"].fillna(""))
        sdn = sdn[bm | ttm].copy()
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        sdn = sdn.dropna(subset=["date", "polarity"])
        sdn["text"] = sdn["body"].fillna("") + " " + sdn["thread_title"].fillna("")
        for _, row in sdn.iterrows():
            for srv, pats in SERVICERS.items():
                for p in pats:
                    if re.search(p, str(row["text"]), re.IGNORECASE):
                        all_rows.append({
                            "source": "SDN", "date": row["date"], "servicer": srv,
                            "polarity": float(row["polarity"]),
                        })
                        break

    # Reddit posts
    for f in ["reddit_professions_pslf.csv", "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f): continue
        try: d = pd.read_csv(f, usecols=lambda c: c in
                              ("combined_text", "polarity", "created_datetime"),
                              low_memory=False)
        except: continue
        d["date"] = pd.to_datetime(d["created_datetime"], errors="coerce", utc=True).dt.tz_localize(None)
        d = d.dropna(subset=["date", "polarity", "combined_text"])
        for _, row in d.iterrows():
            for srv, pats in SERVICERS.items():
                for p in pats:
                    if re.search(p, str(row["combined_text"]), re.IGNORECASE):
                        all_rows.append({
                            "source": "Reddit posts", "date": row["date"], "servicer": srv,
                            "polarity": float(row["polarity"]),
                        })
                        break

    # Reddit comments (sample for speed)
    if os.path.exists("reddit_comments_pslf.csv"):
        df = pd.read_csv("reddit_comments_pslf.csv",
                          usecols=["body", "created_datetime", "polarity", "word_count"],
                          low_memory=False)
        df["date"] = pd.to_datetime(df["created_datetime"], errors="coerce", utc=True).dt.tz_localize(None)
        df = df.dropna(subset=["date", "polarity", "body"])
        df = df[df["word_count"] >= 5]
        # Quick filter by servicer keyword to speed extraction
        servicer_pat = re.compile("|".join([p for pats in SERVICERS.values() for p in pats]),
                                    re.IGNORECASE)
        mask = df["body"].fillna("").str.contains(servicer_pat, regex=True, na=False)
        df = df[mask]
        print(f"\nReddit comments mentioning servicers: {len(df):,}")
        for _, row in df.iterrows():
            for srv, pats in SERVICERS.items():
                for p in pats:
                    if re.search(p, str(row["body"]), re.IGNORECASE):
                        all_rows.append({
                            "source": "Reddit comments", "date": row["date"], "servicer": srv,
                            "polarity": float(row["polarity"]),
                        })
                        break

    df = pd.DataFrame(all_rows)
    print(f"\nTotal servicer-mention rows: {len(df):,}")
    if df.empty:
        print("[ABORT] No servicer mentions")
        return

    df["year"] = df["date"].dt.year
    df["yearmonth"] = df["date"].dt.to_period("M").dt.to_timestamp()

    # === Servicer summary ===
    print("\n[1] Servicer summary")
    summary = df.groupby("servicer").agg(
        n=("polarity", "count"),
        mean_polarity=("polarity", "mean"),
        sd_polarity=("polarity", "std"),
        pct_negative=("polarity", lambda x: (x < -0.05).mean() * 100),
        pct_positive=("polarity", lambda x: (x > 0.05).mean() * 100),
    ).sort_values("n", ascending=False)
    print(summary.round(4).to_string())

    # === Year-over-year ===
    print("\n[2] Year-over-year mean polarity by servicer")
    pivot = df.groupby(["year", "servicer"])["polarity"].mean().unstack()
    print(pivot.round(4).to_string())

    # === MOHELA-specific timeline (since 2022 takeover) ===
    print("\n[3] MOHELA monthly sentiment 2022-2025")
    moh = df[df["servicer"] == "MOHELA"].copy()
    moh = moh[moh["year"] >= 2022]
    monthly = moh.groupby("yearmonth")["polarity"].agg(["mean", "count"])
    monthly = monthly[monthly["count"] >= 30]
    print(f"  months with n>=30: {len(monthly)}")

    # === Save ===
    summary.to_csv(OUT_CSV, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P2: PSLF SERVICER-SPECIFIC DISCOURSE\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total servicer-mention rows: {len(df):,}\n")
        f.write(f"Date range: {df['date'].min()} to {df['date'].max()}\n\n")

        f.write("SERVICER SUMMARY (pooled 2018-2025)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'servicer':<14s} {'n':>7s} {'mean_pol':>10s} {'sd':>7s} "
                f"{'%neg':>7s} {'%pos':>7s}\n")
        for srv, row in summary.iterrows():
            f.write(f"{srv:<14s} {int(row['n']):>7,} {row['mean_polarity']:>+10.4f} "
                    f"{row['sd_polarity']:>7.3f} {row['pct_negative']:>6.2f}% "
                    f"{row['pct_positive']:>6.2f}%\n")

        f.write("\nYEAR-OVER-YEAR MEAN POLARITY BY SERVICER\n")
        f.write("-" * 80 + "\n")
        f.write(pivot.round(4).to_string() + "\n")

        f.write("\nKEY POLICY POINTS\n")
        f.write("-" * 80 + "\n")
        # Compare MOHELA before/after 2022 takeover
        moh_pre = df[(df["servicer"] == "MOHELA") & (df["year"] < 2022)]
        moh_post = df[(df["servicer"] == "MOHELA") & (df["year"] >= 2022)]
        if len(moh_pre) > 30 and len(moh_post) > 30:
            f.write(f"MOHELA pre-2022 takeover (n={len(moh_pre):,}): "
                    f"mean polarity {moh_pre['polarity'].mean():+.4f}\n")
            f.write(f"MOHELA post-2022 takeover (n={len(moh_post):,}): "
                    f"mean polarity {moh_post['polarity'].mean():+.4f}\n")
            f.write(f"Δ: {moh_post['polarity'].mean() - moh_pre['polarity'].mean():+.4f}\n\n")

        # FedLoan baseline (was the previous PSLF servicer 2012-2022)
        fed = df[df["servicer"] == "FedLoan"]
        if len(fed) > 30:
            f.write(f"FedLoan (previous PSLF servicer 2012-2022, n={len(fed):,}): "
                    f"mean polarity {fed['polarity'].mean():+.4f}\n")

        f.write("\nPOLICY USES\n")
        f.write("-" * 80 + "\n")
        f.write("- Future PSLF servicer contract decisions: identify which servicers\n")
        f.write("  generate the most consistent borrower complaints\n")
        f.write("- Performance benchmarking: compare servicer-specific sentiment\n")
        f.write("  trajectories vs administrative metrics (KPIs)\n")
        f.write("- DOE oversight: target audits to servicers with sustained negative\n")
        f.write("  discourse not reflected in formal CFPB complaints\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure: monthly sentiment trajectory per servicer
    fig, ax = plt.subplots(figsize=(14, 7))
    for srv in summary.head(4).index:
        srv_df = df[df["servicer"] == srv].copy()
        srv_df = srv_df[srv_df["year"] >= 2019]
        m = srv_df.groupby("yearmonth")["polarity"].agg(["mean", "count"])
        m = m[m["count"] >= 30]
        if len(m) > 0:
            ax.plot(m.index, m["mean"], "-o", label=f"{srv} (n_total={int(summary.loc[srv,'n']):,})",
                     markersize=4, alpha=0.8)
    for name, ev_date in SERVICER_EVENTS:
        ax.axvline(pd.Timestamp(ev_date), color="black", lw=1, ls="--", alpha=0.5)
        ax.text(pd.Timestamp(ev_date), ax.get_ylim()[1] * 0.95, name,
                 rotation=90, ha="right", va="top", fontsize=9)
    ax.axhline(0, color="gray", lw=0.5)
    ax.set_xlabel("Month")
    ax.set_ylabel("Mean polarity (TextBlob)")
    ax.set_title("Servicer-specific monthly mean polarity (PSLF discussion mentioning each servicer)")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
