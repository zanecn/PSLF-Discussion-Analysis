"""
generate_p1_figS_paraphrase_replication.py
==========================================
Paper 1 SUPPLEMENTARY figure: paraphrase-robustness K-α replication forest plot.

Shows n=200 (R16 Strengthener 2, original) vs n=400 (R17++ #3 replication) with
0.85 pre-specified threshold + 0.667 / 0.80 reliability floors highlighted.

Output: PSLF-Discussion-Analysis/paper1_figS_paraphrase_replication.png (300 DPI)

Reads:
  - paper1_paraphrase_robustness_results.txt (current run; expected to be n=400)

Falls back to hardcoded n=200 historical values from R16 Strengthener 2.
"""
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")

# n=200 historical (locked, R16 Strengthener 2)
N200 = {"n": 200, "alpha": 0.9011, "lo": 0.8571, "hi": 0.9380}

# Parse current run from the text output (expected n=400 after R17++ #3)
def parse_current_run():
    txt = (PROJECT / "paper1_paraphrase_robustness_results.txt").read_text(encoding="utf-8")
    n_match = re.search(r"Sample: n=(\d+) posts", txt)
    a_match = re.search(r"3-prompt Krippendorff α: ([+-][\d.]+)", txt)
    ci_match = re.search(r"Bootstrap 95% CI \[B=\d+\]: \[([+-][\d.]+), ([+-][\d.]+)\]", txt)
    if not (n_match and a_match and ci_match):
        raise RuntimeError("Could not parse current run from paraphrase results .txt")
    return {
        "n": int(n_match.group(1)),
        "alpha": float(a_match.group(1)),
        "lo": float(ci_match.group(1)),
        "hi": float(ci_match.group(2)),
    }

def main():
    current = parse_current_run()
    print(f"n=200 historical: α={N200['alpha']:+.4f} [{N200['lo']:+.4f}, {N200['hi']:+.4f}]")
    print(f"n={current['n']} current: α={current['alpha']:+.4f} [{current['lo']:+.4f}, {current['hi']:+.4f}]")

    rows = [
        ("n=200 (R16 Strengthener 2; original)", N200),
        (f"n={current['n']} (R17++ #3 replication)", current),
    ]

    fig, ax = plt.subplots(figsize=(8.5, 3.5))

    # Reliability-floor backgrounds (Krippendorff 1980)
    # < 0.667 = below tentative; 0.667-0.80 = tentative; >= 0.80 = satisfactory
    ax.axvspan(0.50, 0.667, color="#fee", alpha=0.5)
    ax.axvspan(0.667, 0.80, color="#ffe", alpha=0.5)
    ax.axvspan(0.80, 1.00, color="#efe", alpha=0.5)

    # Pre-specified paraphrase threshold (Round 16 Strengthener 2)
    ax.axvline(0.85, color="#c00", linestyle="--", linewidth=1.2, alpha=0.8, zorder=2)
    ax.text(0.85, len(rows) + 0.18, "0.85\npre-specified\nthreshold",
            ha="center", va="bottom", fontsize=8, color="#c00")

    # 0.667 + 0.80 Krippendorff floors
    ax.axvline(0.667, color="#888", linestyle=":", linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(0.667, -0.5, "0.667\n(Krippendorff 1980\ntentative floor)",
            ha="center", va="top", fontsize=7, color="#666")
    ax.axvline(0.80, color="#888", linestyle=":", linewidth=0.8, alpha=0.6, zorder=1)
    ax.text(0.80, -0.5, "0.80\n(satisfactory\nfloor)",
            ha="center", va="top", fontsize=7, color="#666")

    # Plot the two CIs
    for i, (label, vals) in enumerate(rows):
        y = len(rows) - i - 0.5  # top to bottom
        # CI bar
        ax.plot([vals["lo"], vals["hi"]], [y, y], color="#1a4480", linewidth=2.5, zorder=4)
        # End caps
        ax.plot([vals["lo"], vals["lo"]], [y - 0.08, y + 0.08], color="#1a4480", linewidth=2, zorder=4)
        ax.plot([vals["hi"], vals["hi"]], [y - 0.08, y + 0.08], color="#1a4480", linewidth=2, zorder=4)
        # Point estimate
        ax.scatter([vals["alpha"]], [y], s=80, color="#1a4480", zorder=5)
        # Numeric annotation
        ax.text(vals["hi"] + 0.005, y,
                f" α={vals['alpha']:+.4f}  [{vals['lo']:+.4f}, {vals['hi']:+.4f}]  (half-width={(vals['hi']-vals['lo'])/2:.4f})",
                va="center", fontsize=9, color="#222")

    ax.set_yticks([len(rows) - i - 0.5 for i in range(len(rows))])
    ax.set_yticklabels([label for label, _ in rows], fontsize=10)
    ax.set_xlabel("3-prompt Krippendorff α (sentiment task, 5-level ordinal)", fontsize=10)
    ax.set_xlim(0.50, 1.10)
    ax.set_ylim(-1.1, len(rows) + 0.5)
    ax.set_title("Paper 1 Supplementary Figure: paraphrase-robustness α replication (n=200 → n=400)\n"
                 "Claude Sonnet 4 (temp=0) on SDN-medical 5-instrument intersection",
                 fontsize=10, pad=22)
    ax.grid(axis="x", linestyle="-", alpha=0.2)

    # Legend for color bands
    legend_handles = [
        mpatches.Patch(color="#fee", alpha=0.5, label="α < 0.667 (below tentative floor)"),
        mpatches.Patch(color="#ffe", alpha=0.5, label="0.667 ≤ α < 0.80 (tentative reliability)"),
        mpatches.Patch(color="#efe", alpha=0.5, label="α ≥ 0.80 (satisfactory reliability)"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", fontsize=8, framealpha=0.9)

    fig.text(0.02, 0.005,
             "Note: 3-prompt α tests robustness of Claude Sonnet 4 classifications to LEXICAL-FORMAT paraphrasing of the system prompt "
             "(semantically identical, worded differently). Bootstrap B=2,000, random_state=42. "
             "Both samples drawn from same 615-post SDN-baseline pool with deterministic random_state=42; n=400 is a superset-like resample, not the same posts as n=200.",
             ha="left", va="bottom", fontsize=7, style="italic", color="#444", wrap=True)

    plt.tight_layout(rect=[0, 0.04, 1, 0.93])
    out_path = PROJECT / "paper1_figS_paraphrase_replication.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
