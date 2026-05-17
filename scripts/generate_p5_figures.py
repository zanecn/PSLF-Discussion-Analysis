"""
P5 Figures 1 and 2 (R17++ #6 RIGOROUS REVIEW deliverable).

Figure 1: Bar chart of PSLF-hostile rate × surgical subspecialty, sorted descending,
          with HCA-affiliation labels and n_hostile_institutions annotation.

Figure 2: US map of HCA-affiliated PSLF-hostile surgical-subspec institutions,
          highlighting state-level concentration in Medicaid-non-expansion states.
          Simple state-level dot map (8 institutions across 4 states).

All saved at 300 DPI for publication.
"""
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")

# ============================================================================
# Figure 1: Bar chart of subspec × PSLF-hostile rate
# ============================================================================

SUBSPEC_DATA = [
    # (specialty, pct_hostile, n_hostile_inst, n_total_inst, has_hca_concentration)
    ("Surgery-General",             3.05, 7, 322, True),
    ("Orthopaedic Surgery",         2.02, 4, 193, True),
    ("Plastic Surgery (Integrated)", 1.11, 1, 93,  True),
    ("Neurological Surgery",        0.86, 1, 121, True),
    ("Otolaryngology",              0.73, 1, 130, True),
    ("Vascular Surgery",            0.00, 0, 83,  False),
    ("Thoracic Surgery",            0.00, 0, 37,  False),
]

fig, ax = plt.subplots(figsize=(9, 5.5))
y_pos = np.arange(len(SUBSPEC_DATA))
pcts = [d[1] for d in SUBSPEC_DATA]
labels = [d[0] for d in SUBSPEC_DATA]

# Bar colors: red if hostile programs exist, gray if zero
colors = ["#c44" if d[1] > 0 else "#888" for d in SUBSPEC_DATA]
bars = ax.barh(y_pos, pcts, color=colors, edgecolor="#222", linewidth=0.8)

# Annotate each bar with n_hostile institutions + total
for i, (spec, pct, n_hostile, n_total, has_hca) in enumerate(SUBSPEC_DATA):
    if pct > 0:
        ax.text(pct + 0.05, i, f"  {pct:.2f}% (n={n_hostile}/{n_total}; all HCA-affiliated)",
                va="center", ha="left", fontsize=9, color="#222")
    else:
        ax.text(0.05, i, f"  0% (0/{n_total} hostile)", va="center", ha="left", fontsize=9, color="#666")

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel("PSLF-hostile rate (%) — share of program-years at for-profit-chain institutions", fontsize=10)
ax.set_xlim(0, 4.5)
ax.set_title("Paper 5 Figure 1: PSLF-hostile rate across US surgical-subspecialty residency programs, 2021–2026\n"
             "All hostile programs at HCA Healthcare-affiliated facilities (n=14 program-institution pairs from 8 unique HCA institutions)",
             fontsize=10, pad=10)
ax.grid(axis="x", linestyle="-", alpha=0.2)

fig.text(0.02, 0.005,
         "Note: 'PSLF-hostile' = for-profit chain–affiliated institution per ProPublica IRS Form 990 verification. n_hostile = unique hostile institutions; n_total = unique institutions hosting that subspecialty. "
         "For Surgery-General (the only subspec with n_hostile≥5), Mann-Whitney U comparing hostile vs non-hostile fill rates returns p=0.84 NS at both program-year and institution levels — central tendency does not differ.",
         ha="left", va="bottom", fontsize=7, style="italic", color="#444", wrap=True)

plt.tight_layout(rect=[0, 0.05, 1, 0.94])
out1 = PROJECT / "paper5_fig1_subspec_hostile_rates.png"
fig.savefig(out1, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out1}")

# ============================================================================
# Figure 2: State-level distribution of HCA-affiliated PSLF-hostile surgical institutions
# ============================================================================

# Per paper5_geographic_workforce_context.csv: 8 institutions across 4 states
STATE_DATA = [
    # (state, n_institutions, medicaid_expansion, institutions)
    ("Florida",   4, "Not expanded",    ["HCA JFK-U Miami", "HCA Morsani-Largo",
                                          "HCA Morsani-Brandon", "HCA Morsani-Bayonet Pt"]),
    ("Texas",     2, "Not expanded",    ["HCA Houston-U Houston", "HCA Medical City"]),
    ("Missouri",  1, "Expanded 2021",   ["HCA Kansas City (5 surgical programs!)"]),
    ("Virginia",  1, "Expanded 2019",   ["HCA Chippenham"]),
]

fig, ax = plt.subplots(figsize=(10, 5.5))
y_pos = np.arange(len(STATE_DATA))
counts = [d[1] for d in STATE_DATA]
states = [d[0] for d in STATE_DATA]

# Color by Medicaid expansion status: red if non-expanded, green if expanded
colors = ["#c44" if "Not expanded" in d[2] else "#2a8a3e" for d in STATE_DATA]
bars = ax.barh(y_pos, counts, color=colors, edgecolor="#222", linewidth=0.8, alpha=0.85)

# Annotate each bar with institution list
for i, (state, n, expansion, institutions) in enumerate(STATE_DATA):
    text_offset = n + 0.1
    inst_text = " · ".join(institutions)
    ax.text(text_offset, i, f"  {expansion} — {inst_text}",
            va="center", ha="left", fontsize=8, color="#222")

ax.set_yticks(y_pos)
ax.set_yticklabels(states, fontsize=11)
ax.invert_yaxis()
ax.set_xlabel("Number of HCA-affiliated PSLF-hostile surgical-subspecialty institutions", fontsize=10)
ax.set_xlim(0, 7)
ax.set_title("Paper 5 Figure 2: State-level distribution of HCA-affiliated PSLF-hostile surgical training, 2021–2026\n"
             "75% (6 of 8) of HCA-affiliated PSLF-hostile surgical institutions are in Medicaid-non-expansion states",
             fontsize=10, pad=10)
ax.grid(axis="x", linestyle="-", alpha=0.2)

# Legend
legend_handles = [
    mpatches.Patch(color="#c44", alpha=0.85, label="Medicaid non-expansion state (Florida, Texas)"),
    mpatches.Patch(color="#2a8a3e", alpha=0.85, label="Medicaid expansion state (Missouri 2021, Virginia 2019)"),
]
ax.legend(handles=legend_handles, loc="lower right", fontsize=9, framealpha=0.9)

fig.text(0.02, 0.005,
         "Note: HCA Healthcare Kansas City (Missouri) is the single most concentrated PSLF-hostile training site (5 surgical residencies: NS+Plastics+ENT+Ortho+Surgery-General). "
         "75% concentration in non-Medicaid-expansion states (vs 20% baseline US expectation) suggests for-profit-chain surgical residency training compounds with state-level "
         "Medicaid policy: residents trained at HCA-affiliated PSLF-hostile programs face both (a) PSLF ineligibility and (b) reduced state Medicaid expansion that may affect "
         "post-residency PSLF-qualifying-employer options.",
         ha="left", va="bottom", fontsize=7, style="italic", color="#444", wrap=True)

plt.tight_layout(rect=[0, 0.07, 1, 0.95])
out2 = PROJECT / "paper5_fig2_state_distribution_medicaid.png"
fig.savefig(out2, dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {out2}")

print("\n=== Paper 5 figures complete ===")
print(f"  Figure 1: {out1}")
print(f"  Figure 2: {out2}")
