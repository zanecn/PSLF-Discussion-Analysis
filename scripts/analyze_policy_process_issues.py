"""
analyze_policy_process_issues.py
==================================
P3 (policy): Specific PSLF process issue prevalence.

Identifies what specific PSLF processes generate discussion. Useful for
federal student aid process-improvement prioritization.

Process buckets:
  - PSLF Buyback (controversial new program for missing months)
  - Employment Certification Form (ECF) issues
  - Income-Driven Repayment (IDR) recertification
  - Payment count / qualifying-payment disputes
  - PSLF Form processing delays
  - Servicer transitions
  - Loan consolidation requirements
  - Public service employer determination

Output: policy_process_issues_results.{txt,csv,png}
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

OUT_TXT = "policy_process_issues_results.txt"
OUT_CSV = "policy_process_issues_results.csv"
OUT_PNG = "policy_process_issues_results.png"

# Specific PSLF process keywords + concern markers
PROCESSES = {
    "PSLF_Buyback": [r"\bbuyback\b", r"\bbuy[\s-]?back\b"],
    "Employment_Certification": [r"\bECF\b", r"\bemployment certification\b",
                                    r"\bcert\.?\s*form\b"],
    "IDR_Recertification": [r"\bIDR recert", r"\brecertify\b", r"\brecertification\b",
                              r"\bincome[\s\-]?driven\b"],
    "Payment_Count_Dispute": [r"\bpayment count\b", r"\bqualifying payment",
                                r"\bcredit count\b", r"\bcount\s+(?:wrong|missing|disputed)\b"],
    "Form_Processing_Delay": [r"\bprocessing\b.*\b(?:delay|slow|stuck|months)\b",
                                 r"\bin (?:review|process)\b",
                                 r"\bwaiting\b.*\b(?:approval|review|process)\b"],
    "Loan_Consolidation": [r"\bconsolidat\w*\b", r"\bDirect Consolidation\b"],
    "Employer_Determination": [r"\bemployer\b.*\b(?:eligib|qualifying|approve|deny|reject)\b",
                                 r"\bnon[\s\-]?profit\b.*\b(?:status|determ)\b"],
    "PSLF_Help_Tool": [r"\bPSLF Help Tool\b", r"\bPSLF tool\b"],
    "Limited_Waiver": [r"\blimited waiver\b", r"\bLimited PSLF Waiver\b"],
    "IDR_Adjustment": [r"\bIDR (?:adjustment|account adjustment)\b",
                         r"\b(?:account|payment)\s+adjustment\b"],
    "MOHELA_Specific_Issue": [r"\bMOHELA\b.*\b(?:lost|wrong|delay|stuck|incompetent|nightmare)\b"],
}

# Concern markers (presence amplifies the issue signal)
CONCERN_PATTERNS = re.compile(
    r"\b(?:problem|issue|stuck|wrong|denied|reject|nightmare|frustrat|confus|"
    r"struggle|hassle|incorrect|missing|lost|broken|delay|months\s+(?:waiting|to))\b",
    re.IGNORECASE,
)


def main():
    print("=" * 80)
    print("P3: PSLF process-specific issue prevalence")
    print("=" * 80)

    all_rows = []
    for f, text_col, date_col in [
        ("forum_pslf_discussions.csv", "body", "date_posted"),
        ("reddit_professions_pslf.csv", "combined_text", "created_datetime"),
        ("reddit_arctic_shift_pslf.csv", "combined_text", "created_datetime"),
    ]:
        if not os.path.exists(f): continue
        try: d = pd.read_csv(f, usecols=lambda c: c in (text_col, date_col, "polarity",
                                                          "thread_title", "id"),
                              low_memory=False)
        except: continue
        d["date"] = pd.to_datetime(d[date_col], errors="coerce", utc=True).dt.tz_localize(None)
        d = d.dropna(subset=["date", "polarity"])
        if "thread_title" in d.columns:
            d["text"] = d[text_col].fillna("") + " " + d["thread_title"].fillna("")
        else:
            d["text"] = d[text_col].fillna("")
        for _, row in d.iterrows():
            text = str(row["text"])
            has_concern = bool(CONCERN_PATTERNS.search(text))
            for proc, pats in PROCESSES.items():
                for p in pats:
                    if re.search(p, text, re.IGNORECASE):
                        all_rows.append({
                            "source": f.replace(".csv", ""),
                            "date": row["date"],
                            "process": proc,
                            "polarity": float(row["polarity"]),
                            "has_concern": has_concern,
                        })
                        break

    # Reddit comments (sample)
    if os.path.exists("reddit_comments_pslf.csv"):
        df = pd.read_csv("reddit_comments_pslf.csv",
                          usecols=["body", "created_datetime", "polarity", "word_count"],
                          low_memory=False)
        df["date"] = pd.to_datetime(df["created_datetime"], errors="coerce", utc=True).dt.tz_localize(None)
        df = df.dropna(subset=["date", "polarity", "body"])
        df = df[df["word_count"] >= 5]
        # Pre-filter for any process keyword
        all_pats = re.compile("|".join([p for pats in PROCESSES.values() for p in pats]),
                                re.IGNORECASE)
        mask = df["body"].fillna("").str.contains(all_pats, regex=True, na=False)
        df = df[mask]
        print(f"\nReddit comments matching any process: {len(df):,}")
        for _, row in df.iterrows():
            text = str(row["body"])
            has_concern = bool(CONCERN_PATTERNS.search(text))
            for proc, pats in PROCESSES.items():
                for p in pats:
                    if re.search(p, text, re.IGNORECASE):
                        all_rows.append({
                            "source": "reddit_comments",
                            "date": row["date"],
                            "process": proc,
                            "polarity": float(row["polarity"]),
                            "has_concern": has_concern,
                        })
                        break

    df = pd.DataFrame(all_rows)
    print(f"\nTotal process-mention rows: {len(df):,}")

    # === Summary by process ===
    print("\n[1] Process-issue summary")
    summary = df.groupby("process").agg(
        n=("polarity", "count"),
        mean_polarity=("polarity", "mean"),
        pct_concern=("has_concern", "mean"),
        pct_negative=("polarity", lambda x: (x < -0.05).mean()),
    ).sort_values("n", ascending=False)
    summary["pct_concern"] = summary["pct_concern"] * 100
    summary["pct_negative"] = summary["pct_negative"] * 100
    print(summary.round(3).to_string())

    # === Time trends ===
    df["year"] = df["date"].dt.year
    print("\n[2] Year-over-year process mention volume")
    yr_pivot = df.groupby(["year", "process"]).size().unstack(fill_value=0)
    print(yr_pivot.tail(8).to_string())

    # === Save ===
    summary.to_csv(OUT_CSV, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("POLICY P3: PSLF PROCESS-SPECIFIC ISSUE PREVALENCE\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total process-mention rows: {len(df):,}\n\n")

        f.write("PROCESS SUMMARY (sorted by mention volume)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'process':<28s} {'n':>6s} {'mean_pol':>10s} "
                f"{'%concern':>9s} {'%neg':>7s}\n")
        for proc, row in summary.iterrows():
            f.write(f"{proc:<28s} {int(row['n']):>6,} {row['mean_polarity']:>+10.4f} "
                    f"{row['pct_concern']:>8.1f}% {row['pct_negative']:>6.1f}%\n")

        f.write("\nYEAR-OVER-YEAR MENTION VOLUME (last 8 years)\n")
        f.write("-" * 80 + "\n")
        f.write(yr_pivot.tail(8).to_string() + "\n")

        f.write("\nKEY POLICY POINTS\n")
        f.write("-" * 80 + "\n")
        # Identify top "concern" processes (high pct_concern, mean_polarity negative)
        problematic = summary[(summary["pct_concern"] > 50) &
                              (summary["mean_polarity"] < 0)].sort_values("pct_concern", ascending=False)
        if len(problematic) > 0:
            f.write("\nMost problematic processes (>50% mention concern markers, mean polarity <0):\n")
            for proc, row in problematic.iterrows():
                f.write(f"  - {proc}: n={int(row['n']):,}, %concern={row['pct_concern']:.1f}%, "
                        f"mean polarity {row['mean_polarity']:+.4f}\n")

        f.write("\nPOLICY USES\n")
        f.write("-" * 80 + "\n")
        f.write("- Federal Student Aid: prioritize process-improvement work for top issues\n")
        f.write("- DOE rule-making: target rule simplification at top complaint sources\n")
        f.write("- Servicer SLAs: tie performance to specific process metrics that drive complaints\n")
        f.write("- CFPB: use as triage signal for which processes warrant deeper investigation\n")
        f.write("\nCAVEATS\n")
        f.write("-" * 80 + "\n")
        f.write("- Self-selected discussion: not representative of all PSLF borrowers\n")
        f.write("- Keyword extraction may miss informal references / abbreviations\n")
        f.write("- 'has_concern' marker is heuristic — manual coding sample would refine\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # Figure
    fig, ax = plt.subplots(figsize=(14, 8))
    plot_df = summary.head(11).copy()
    plot_df = plot_df.sort_values("pct_concern")
    colors = ["red" if v > 60 else "orange" if v > 40 else "lightgreen"
              for v in plot_df["pct_concern"]]
    ax.barh(plot_df.index, plot_df["pct_concern"], color=colors)
    for i, (proc, row) in enumerate(plot_df.iterrows()):
        ax.text(row["pct_concern"] + 1, i,
                 f"n={int(row['n']):,}, mean_pol={row['mean_polarity']:+.3f}",
                 va="center", fontsize=9)
    ax.set_xlabel("% of mentions containing concern markers (problem/stuck/denied/etc.)")
    ax.set_title("PSLF process issues — share of mentions expressing concern\n"
                  "(red=>60%, orange=40-60%, green=<40%)")
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
    print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
