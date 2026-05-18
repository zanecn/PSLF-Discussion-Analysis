"""
analyze_policy_state_heatmap.py
=================================
P1 (policy): Where is PSLF distress concentrated geographically?

Extracts state mentions from Reddit + SDN posts and comments, computes
mean polarity + post volume per (state, year). Output is a directly policy-
actionable map for federal/state outreach prioritization.

Output: policy_state_discourse.{txt,csv,png}
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

OUT_TXT = "policy_state_discourse.txt"
OUT_CSV = "policy_state_discourse.csv"
OUT_PNG = "policy_state_discourse.png"

# Full state names + abbreviations
STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "DC": "DC", "District of Columbia": "DC",
}

# Build regex: full name OR abbreviation with word boundary
def build_state_regex():
    """Two regexes:
       - Full state names: case insensitive
       - Abbreviations: case sensitive (CAPITALIZED only) AND require comma/space context
         to avoid false positives like 'in', 'me', 'or', 'ok', 'hi', 'me', 'us'
    """
    full_parts = []
    for full in STATES:
        if full == "DC": continue
        full_parts.append(rf"\b{re.escape(full)}\b")
    full_re = re.compile("|".join(full_parts), re.IGNORECASE)

    # Abbreviations: only match if preceded by space/comma/start AND
    # followed by space/comma/period/end. AND uppercase-required.
    abbr_parts = []
    AMBIGUOUS_ABBRS = {"IN", "ME", "OR", "OK", "HI", "MS", "AL", "AR", "MT", "VA", "DE",
                        "PA", "MA", "CA", "ID", "MI", "DC", "OH", "WA", "WI", "NY", "NJ"}
    for full, abbr in STATES.items():
        if abbr in AMBIGUOUS_ABBRS:
            # Require comma + space context: "live in Texas, TX" or ", VA "
            abbr_parts.append(rf"(?:[,\s]\s*){abbr}(?:[,.\s\b])")
        else:
            abbr_parts.append(rf"\b{abbr}\b")
    abbr_re = re.compile("|".join(abbr_parts))  # case-sensitive

    return full_re, abbr_re


def extract_states(text, full_re, abbr_re):
    """Find all state mentions in text. Returns set of state codes."""
    if not isinstance(text, str): return set()
    found = set()
    for m in full_re.finditer(text):
        token = m.group().strip().lower()
        for full, abbr in STATES.items():
            if token == full.lower():
                found.add(abbr); break
    for m in abbr_re.finditer(text):
        token = m.group().strip().rstrip(",.").strip()
        if len(token) == 2 and token.isupper():
            found.add(token)
    return found


def main():
    print("=" * 80)
    print("P1: State-level PSLF discourse heat map")
    print("=" * 80)

    full_re, abbr_re = build_state_regex()

    all_rows = []

    # 1) SDN PSLF posts
    if os.path.exists("forum_pslf_discussions.csv"):
        from pslf_search_terms import filter_pslf_relevant
        sdn = pd.read_csv("forum_pslf_discussions.csv", low_memory=False)
        bm = filter_pslf_relevant(sdn["body"].fillna(""))
        ttm = filter_pslf_relevant(sdn["thread_title"].fillna(""))
        sdn = sdn[bm | ttm].copy()
        sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        sdn = sdn.dropna(subset=["date", "polarity"])
        sdn["text"] = sdn["body"].fillna("") + " " + sdn["thread_title"].fillna("")
        sdn["year"] = sdn["date"].dt.year
        sdn = sdn[(sdn["year"] >= 2018) & (sdn["year"] <= 2025)]
        print(f"\nSDN posts: {len(sdn):,}")
        for _, row in sdn.iterrows():
            states = extract_states(row["text"], full_re, abbr_re)
            for st in states:
                all_rows.append({
                    "source": "SDN",
                    "year": int(row["year"]),
                    "state": st,
                    "polarity": float(row["polarity"]),
                    "word_count": int(str(row["text"]).split().__len__()),
                })

    # 2) Reddit professions PSLF posts
    for f in ["reddit_professions_pslf.csv", "reddit_arctic_shift_pslf.csv",
                "reddit_new_subs_pslf.csv"]:
        if not os.path.exists(f): continue
        try:
            d = pd.read_csv(f, usecols=lambda c: c in
                             ("combined_text", "polarity", "created_datetime"),
                             low_memory=False)
        except: continue
        d["date"] = pd.to_datetime(d["created_datetime"], errors="coerce", utc=True).dt.tz_localize(None)
        d = d.dropna(subset=["date", "polarity", "combined_text"])
        d["year"] = d["date"].dt.year
        d = d[(d["year"] >= 2018) & (d["year"] <= 2025)]
        print(f"  {f}: {len(d):,} posts")
        for _, row in d.iterrows():
            states = extract_states(row["combined_text"], full_re, abbr_re)
            for st in states:
                all_rows.append({
                    "source": f.replace("reddit_", "").replace("_pslf.csv", ""),
                    "year": int(row["year"]),
                    "state": st,
                    "polarity": float(row["polarity"]),
                    "word_count": 0,
                })

    # 3) Reddit comments
    if os.path.exists("reddit_comments_pslf.csv"):
        print("\nLoading Reddit comments...")
        df = pd.read_csv("reddit_comments_pslf.csv",
                          usecols=["body", "created_datetime", "polarity", "word_count"],
                          low_memory=False)
        df["date"] = pd.to_datetime(df["created_datetime"], errors="coerce", utc=True).dt.tz_localize(None)
        df = df.dropna(subset=["date", "polarity", "body"])
        df = df[df["word_count"] >= 5]
        df["year"] = df["date"].dt.year
        df = df[(df["year"] >= 2018) & (df["year"] <= 2025)]
        print(f"Reddit comments: {len(df):,}")
        # Sample 100K for speed (state-level patterns are stable)
        if len(df) > 100000:
            df = df.sample(n=100000, random_state=42)
            print(f"  sampled 100K for state extraction")
        for _, row in df.iterrows():
            states = extract_states(row["body"], full_re, abbr_re)
            for st in states:
                all_rows.append({
                    "source": "reddit_comments",
                    "year": int(row["year"]),
                    "state": st,
                    "polarity": float(row["polarity"]),
                    "word_count": int(row["word_count"]),
                })

    print(f"\nTotal state-mention rows: {len(all_rows):,}")
    df = pd.DataFrame(all_rows)
    if df.empty:
        print("[ABORT] No state mentions found")
        return

    # === Aggregate by state x year ===
    print("\n[1] State x year sentiment summary (top 15 states by volume)")
    state_year = df.groupby(["state", "year"]).agg(
        n=("polarity", "count"),
        mean_polarity=("polarity", "mean"),
        sd_polarity=("polarity", "std"),
        pct_negative=("polarity", lambda x: (x < -0.05).mean() * 100),
    ).reset_index()

    state_summary = df.groupby("state").agg(
        n_total=("polarity", "count"),
        mean_polarity=("polarity", "mean"),
        sd_polarity=("polarity", "std"),
        pct_negative=("polarity", lambda x: (x < -0.05).mean() * 100),
    ).sort_values("n_total", ascending=False)

    print(f"\n{'state':>5s} {'n':>8s} {'mean_pol':>10s} {'%neg':>6s}")
    for state, row in state_summary.head(15).iterrows():
        print(f"{state:>5s} {int(row['n_total']):>8,} "
               f"{row['mean_polarity']:>+10.4f} {row['pct_negative']:>6.2f}%")

    # === Identify "PSLF distress hotspots" ===
    print("\n[2] PSLF distress hotspots (high volume + below-median polarity)")
    state_summary_filtered = state_summary[state_summary["n_total"] >= 100]
    median_pol = state_summary_filtered["mean_polarity"].median()
    hotspots = state_summary_filtered[
        state_summary_filtered["mean_polarity"] < median_pol
    ].sort_values("mean_polarity").head(10)
    print(f"  median mean_polarity (states n>=100): {median_pol:+.4f}")
    print(f"  top 10 distress hotspots:")
    for state, row in hotspots.iterrows():
        print(f"    {state}: n={int(row['n_total']):>5,} mean_pol={row['mean_polarity']:>+.4f} "
               f"%neg={row['pct_negative']:>5.1f}%")

    # === Year-over-year shifts (Trump EO impact by state) ===
    print("\n[3] PSLF EO impact by state (2024 vs 2025)")
    pre = df[df["year"] == 2024].groupby("state")["polarity"].agg(["mean", "count"])
    post = df[df["year"] == 2025].groupby("state")["polarity"].agg(["mean", "count"])
    eo_impact = pre.merge(post, left_index=True, right_index=True,
                            suffixes=("_2024", "_2025"))
    eo_impact = eo_impact[(eo_impact["count_2024"] >= 50) & (eo_impact["count_2025"] >= 50)]
    eo_impact["delta"] = eo_impact["mean_2025"] - eo_impact["mean_2024"]
    eo_impact = eo_impact.sort_values("delta")
    print(f"  states with >=50 obs in both years: {len(eo_impact)}")
    print(f"  largest negative shift (Trump EO impact):")
    for state, row in eo_impact.head(10).iterrows():
        print(f"    {state}: 2024={row['mean_2024']:+.4f} 2025={row['mean_2025']:+.4f} "
               f"Δ={row['delta']:+.4f}  (n_24={int(row['count_2024'])}, n_25={int(row['count_2025'])})")

    # === Save ===
    state_year.to_csv(OUT_CSV, index=False, float_format="%.5f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P1: State-level PSLF discourse heat map\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total state-mention observations: {len(df):,}\n")
        f.write(f"States with at least one mention: {df['state'].nunique()}\n")
        f.write(f"Years covered: {sorted(df['year'].unique().tolist())}\n\n")

        f.write("TOP 15 STATES BY DISCOURSE VOLUME\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'state':>5s} {'n':>8s} {'mean_pol':>10s} {'sd':>7s} {'%neg':>7s}\n")
        for state, row in state_summary.head(15).iterrows():
            f.write(f"{state:>5s} {int(row['n_total']):>8,} "
                    f"{row['mean_polarity']:>+10.4f} {row['sd_polarity']:>7.3f} "
                    f"{row['pct_negative']:>6.2f}%\n")

        f.write("\nPSLF DISTRESS HOTSPOTS (high volume + below-median mean polarity)\n")
        f.write("-" * 80 + "\n")
        for state, row in hotspots.iterrows():
            f.write(f"  {state}: n={int(row['n_total']):>5,} "
                    f"mean_pol={row['mean_polarity']:>+.4f} "
                    f"%neg={row['pct_negative']:>5.1f}%\n")

        f.write("\nTRUMP PSLF EO IMPACT BY STATE (2024 vs 2025)\n")
        f.write("-" * 80 + "\n")
        f.write("Largest negative shifts (states most affected):\n")
        for state, row in eo_impact.head(10).iterrows():
            f.write(f"  {state}: 2024={row['mean_2024']:+.4f} 2025={row['mean_2025']:+.4f} "
                    f"Δ={row['delta']:+.4f}  (n_24={int(row['count_2024'])}, n_25={int(row['count_2025'])})\n")
        f.write("\nLeast affected (or improved):\n")
        for state, row in eo_impact.tail(10).iterrows():
            f.write(f"  {state}: 2024={row['mean_2024']:+.4f} 2025={row['mean_2025']:+.4f} "
                    f"Δ={row['delta']:+.4f}  (n_24={int(row['count_2024'])}, n_25={int(row['count_2025'])})\n")

        f.write("\nPOLICY USES\n")
        f.write("-" * 80 + "\n")
        f.write("- Federal Student Aid: prioritize outreach in distress hotspots\n")
        f.write("- State financial counseling: target states with sustained negative discourse\n")
        f.write("- DOE communication: track state-level reception of policy announcements\n")
        f.write("- HRSA: cross-reference with HPSA designations (next analysis)\n")
        f.write("\nCAVEATS\n")
        f.write("-" * 80 + "\n")
        f.write("- State mentions are noisy; many posts mention multiple states\n")
        f.write("- Reddit/SDN demographics skew young/educated/white (not representative\n")
        f.write("  of full PSLF-eligible borrower population)\n")
        f.write("- TextBlob polarity is one of three sentiment instruments; results would\n")
        f.write("  shift if using VADER or Claude\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure: state-level mean polarity vs volume scatter
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    ax = axes[0]
    plot_df = state_summary[state_summary["n_total"] >= 30]
    ax.scatter(plot_df["n_total"], plot_df["mean_polarity"],
                s=np.sqrt(plot_df["n_total"]), alpha=0.6, color="steelblue")
    for state, row in plot_df.iterrows():
        ax.annotate(state, (row["n_total"], row["mean_polarity"]),
                     fontsize=8, ha="center")
    ax.axhline(plot_df["mean_polarity"].median(), color="red", lw=1, ls="--",
                label=f"median = {plot_df['mean_polarity'].median():+.3f}")
    ax.set_xscale("log")
    ax.set_xlabel("PSLF discourse volume (log scale)")
    ax.set_ylabel("Mean polarity")
    ax.set_title("(a) State-level PSLF discourse: volume vs sentiment")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axes[1]
    eo_plot = eo_impact.head(15)
    colors = ["red" if d < 0 else "steelblue" for d in eo_plot["delta"]]
    ax.barh(eo_plot.index, eo_plot["delta"], color=colors)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Δ mean polarity (2025 - 2024)")
    ax.set_title("(b) Trump PSLF EO impact by state — most negative shifts")
    ax.grid(alpha=0.3, axis="x")

    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
