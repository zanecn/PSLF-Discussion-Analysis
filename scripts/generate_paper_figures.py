"""
generate_paper_figures.py
==========================
Builds 8 publication-ready figures for the methods + substantive papers,
all consistent in styling. Each figure is self-contained and saves to
the project root with a descriptive filename.

Substantive paper figures (4):
  fig_substantive_1_decoupling_forest.png  — cohort-conditional decoupling OR
  fig_substantive_2_recovery_times.png      — time-to-recovery by cohort
  fig_substantive_3_rejection_reasons.png   — rejection_reason × cohort × event
  fig_substantive_4_topic_3d_heatmap.png    — per-cohort × per-event topic shifts

Methods paper figures (4):
  fig_methods_1_op_vs_reply_cohort.png       — OP vs Reply by cohort
  fig_methods_2_trump_eo_joint.png           — Trump EO 3-vector + joint test
  fig_methods_3_alpha_stability.png          — K-α sample-stability across rounds
  fig_methods_4_per_event_cohort_forest.png  — per-event cohort-heterogeneity (BH-FDR)
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

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

COHORT_COLORS = {
    "SDN (Medical)":            "#C2185B",
    "Reddit r/PSLF":            "#1565C0",
    "Reddit r/StudentLoans":    "#388E3C",
    "Reddit Finance":           "#F57C00",
    "Reddit Medical":           "#6A1B9A",
    "Reddit PA":                "#00838F",
    "Reddit Teaching":          "#E65100",
    "Reddit Nursing":           "#558B2F",
    "Other":                    "#757575",
}


# ============================================================
# FIG 1: Cohort-conditional decoupling forest plot
# ============================================================
def fig_substantive_1():
    """Forest plot of OR by cohort showing directional reversal."""
    print("\n[Fig 1] Cohort-conditional decoupling forest plot...")
    if not os.path.exists("decoupling_by_cohort.csv"):
        print("  [SKIP] decoupling_by_cohort.csv not found")
        return
    df = pd.read_csv("decoupling_by_cohort.csv")
    df = df.sort_values("odds_ratio", ascending=True)

    fig, ax = plt.subplots(figsize=(13, 7))
    y = np.arange(len(df))

    for i, (_, r) in enumerate(df.iterrows()):
        color = COHORT_COLORS.get(r["cohort"], "#888888")
        # Effect direction
        is_decoupling = r["odds_ratio"] < 1
        # Plot CI
        ax.plot([r["or_ci_lo"], r["or_ci_hi"]], [y[i], y[i]],
                color=color, linewidth=2.5, alpha=0.7, solid_capstyle="round")
        ax.scatter(r["odds_ratio"], y[i], s=200, color=color,
                   edgecolors="white", linewidths=2, zorder=10)
        # Sig stars
        sig = ("***" if r["chi2_p"] < 1e-10 else
               "**" if r["chi2_p"] < 0.01 else
               "*" if r["chi2_p"] < 0.05 else "")
        # Label
        label = f"{r['cohort']} (n={int(r['n_total']):,})"
        ax.text(0.04, y[i], f" {sig}", ha="left", va="center",
                fontsize=11, fontweight="bold", color=color)

    ax.axvline(x=1.0, color="#222", linewidth=1.0, linestyle="--", alpha=0.6,
               label="OR=1 (no decoupling)")
    ax.set_xscale("log")
    ax.set_xlim(0.05, 30)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['cohort']} (n={int(r['n_total']):,})" for _, r in df.iterrows()],
                       fontsize=10)
    ax.set_xlabel("Odds Ratio: P(pursuing | negative sentiment) / P(pursuing | non-negative)",
                  fontsize=11, fontweight="bold")
    ax.set_title("Sentiment-Stance Decoupling is COHORT-CONDITIONAL AND DIRECTIONALLY OPPOSITE\n"
                 "OR < 1 = negativity predicts disengagement; OR > 1 = negativity predicts MORE pursuing (venting culture)",
                 fontsize=13, fontweight="bold", loc="left")

    # Annotations: move down to lower middle area to avoid title overlap
    ax.axvspan(0.05, 1, alpha=0.05, color="#C62828")
    ax.axvspan(1, 30, alpha=0.05, color="#1565C0")
    ax.text(0.12, 0.5, "ANALYTICAL DECOUPLING\n(negativity → exit)",
            fontsize=10, color="#C62828", style="italic", va="center", ha="center",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#C62828", alpha=0.85))
    ax.text(8, 0.5, "VENTING-WHILE-COMMITTED\n(negativity → MORE pursuing)",
            fontsize=10, color="#1565C0", style="italic", va="center", ha="center",
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#1565C0", alpha=0.85))

    plt.tight_layout()
    out = "fig_substantive_1_decoupling_forest.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 2: Time-to-recovery comparison
# ============================================================
def fig_substantive_2():
    """Bar chart of median recovery days by cohort + per-event scatter."""
    print("\n[Fig 2] Time-to-recovery comparison...")
    if not os.path.exists("time_to_recovery_results.csv"):
        print("  [SKIP] time_to_recovery_results.csv not found")
        return
    df = pd.read_csv("time_to_recovery_results.csv")
    cohorts_order = ["Reddit r/PSLF", "Reddit r/StudentLoans", "Reddit Finance",
                     "SDN (Medical)", "Reddit Medical"]
    df = df[df["cohort"].isin(cohorts_order)]
    # Replace -1 (censored) with 180 (window cap) for plotting
    df["recovery_day_plot"] = df["recovery_day"].replace(-1, 180)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                     gridspec_kw={"width_ratios": [1, 1.4]})

    # Panel A: median recovery days by cohort
    medians = []
    for cohort in cohorts_order:
        sub = df[(df["cohort"] == cohort) & (df["censored"] == False)]
        med = sub["recovery_day"].median() if len(sub) else np.nan
        n_recovered = (df[df["cohort"] == cohort]["censored"] == False).sum()
        n_total = (df["cohort"] == cohort).sum()
        medians.append({"cohort": cohort, "median": med,
                        "n_recovered": n_recovered, "n_total": n_total})
    md = pd.DataFrame(medians)

    bars = ax1.barh(np.arange(len(md)), md["median"],
                     color=[COHORT_COLORS.get(c, "#888888") for c in md["cohort"]],
                     edgecolor="white", linewidth=1.5)
    for i, (_, r) in enumerate(md.iterrows()):
        if not np.isnan(r["median"]):
            ax1.text(r["median"] + 1.5, i, f" {int(r['median'])}d ({int(r['n_recovered'])}/{int(r['n_total'])})",
                     va="center", fontsize=10, fontweight="bold")
    ax1.set_yticks(np.arange(len(md)))
    ax1.set_yticklabels(md["cohort"], fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel("Median days to sentiment recovery (within 0.5 SD of pre-event baseline)",
                   fontsize=10, fontweight="bold")
    ax1.set_title("(a) Median recovery time by cohort", fontweight="bold", loc="left")

    # Panel B: per-event scatter
    EVENTS_ORDER = ["Limited PSLF Waiver", "IDR Account Adjustment", "Biden Mass Forgiveness",
                    "Biden v. Nebraska SCOTUS", "Payments Restart", "SAVE Admin Forbearance",
                    "Trump PSLF EO", "Final Trump PSLF Rule"]
    for cohort in cohorts_order:
        sub = df[df["cohort"] == cohort]
        if len(sub) == 0:
            continue
        sub = sub.set_index("event").reindex(EVENTS_ORDER).reset_index()
        x = np.arange(len(sub))
        y = sub["recovery_day_plot"].values
        # Triangles for censored, circles for recovered
        for i, (_, r) in enumerate(sub.iterrows()):
            if pd.isna(r["recovery_day"]):
                continue
            if r["censored"]:
                ax2.scatter(x[i], 180, marker="^", s=120,
                            color=COHORT_COLORS.get(cohort), alpha=0.6,
                            edgecolors="white", linewidths=1.5, zorder=5)
            else:
                ax2.scatter(x[i], r["recovery_day"], marker="o", s=120,
                            color=COHORT_COLORS.get(cohort), alpha=0.85,
                            edgecolors="white", linewidths=1.5, zorder=5,
                            label=cohort if i == 0 else "")
    # Legend with all cohorts represented
    handles = [mpatches.Patch(color=COHORT_COLORS.get(c, "#888"), label=c) for c in cohorts_order]
    handles.append(mpatches.Patch(color="#888", label="▲ = censored at 180d"))
    ax2.legend(handles=handles, loc="upper left", fontsize=9, frameon=True,
                facecolor="white", edgecolor="#CCC")
    ax2.set_xticks(np.arange(len(EVENTS_ORDER)))
    ax2.set_xticklabels([e.replace(" PSLF", "").replace("Account Adjustment", "Adj")
                         for e in EVENTS_ORDER], rotation=35, ha="right", fontsize=9)
    ax2.set_ylabel("Days to recovery", fontsize=10, fontweight="bold")
    ax2.set_ylim(-5, 195)
    ax2.set_title("(b) Per-event recovery by cohort", fontweight="bold", loc="left")
    ax2.axhline(y=180, color="#999", linestyle=":", linewidth=0.8, alpha=0.6)

    fig.suptitle("Time-to-Recovery: Cohort-Heterogeneity in Temporal Persistence of Policy-Event Sentiment Shocks",
                 fontsize=13, fontweight="bold", y=1.005)
    fig.text(0.99, 0.005,
             "Recovery = first day where 14-day rolling polarity returns to within 0.5 SD of "
             "[-90, 0]-day pre-event baseline. Right-censored at 180d.",
             ha="right", fontsize=8, style="italic", color="#666")

    plt.tight_layout()
    out = "fig_substantive_2_recovery_times.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 3: Rejection-reason × cohort × event heatmap
# ============================================================
def fig_substantive_3():
    """Two-panel heatmap: cohort × rejection_reason and event × rejection_reason."""
    print("\n[Fig 3] Rejection-reason heatmaps...")
    if not os.path.exists("rejection_reasons.csv"):
        print("  [SKIP] rejection_reasons.csv not found")
        return
    rr = pd.read_csv("rejection_reasons.csv")
    rr["post_id"] = rr["post_id"].astype(str)
    rr = rr[~rr["rejection_reason"].isin(["parse_error", ""])]

    # Re-merge cohort + event from the analysis output
    if not os.path.exists("rejection_reason_analysis_results.csv"):
        print("  [SKIP] need rejection_reason_analysis_results.csv (run analyze_rejection_reasons.py first)")
        return
    full = pd.read_csv("rejection_reason_analysis_results.csv")
    # Re-derive event from date (the saved CSV doesn't have event column)
    if "event" not in full.columns and "date" in full.columns:
        full["date"] = pd.to_datetime(full["date"], utc=True, errors="coerce").dt.tz_localize(None)
        EVENTS_INNER = [
            ("Limited PSLF Waiver",            "2021-10-06", 90),
            ("IDR Account Adjustment",         "2022-04-19", 90),
            ("Biden Mass Forgiveness",         "2022-08-24", 90),
            ("Biden v. Nebraska SCOTUS",       "2023-06-30", 90),
            ("Payments Restart",               "2023-10-01", 90),
            ("SAVE Admin Forbearance",         "2024-08-09", 90),
            ("Trump PSLF EO",                  "2025-03-07", 60),
            ("Final Trump PSLF Rule",          "2025-10-30", 60),
        ]
        full["event"] = None
        for ev_name, ev_date, win in EVENTS_INNER:
            dt = pd.Timestamp(ev_date)
            mask = (full["date"] >= dt - pd.Timedelta(days=win)) & (full["date"] <= dt + pd.Timedelta(days=win))
            full.loc[mask & full["event"].isna(), "event"] = ev_name

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 7),
                                     gridspec_kw={"width_ratios": [1.1, 1]})

    REASONS_ORDER = ["servicer_distrust", "employer_mismatch", "alternative_strategy",
                      "timeline_too_long", "job_change", "cost_complexity",
                      "forbearance_fatigue", "other", "no_reason_given"]
    cohorts_order = ["SDN (Medical)", "Reddit r/PSLF", "Reddit r/StudentLoans",
                     "Reddit Finance", "Reddit Medical", "Reddit PA", "Reddit Teaching",
                     "Reddit Nursing", "Other"]
    cohorts_order = [c for c in cohorts_order if c in full["cohort"].values]
    ct1 = pd.crosstab(full["cohort"], full["rejection_reason"], normalize="index") * 100
    ct1 = ct1.reindex(index=cohorts_order, columns=REASONS_ORDER).fillna(0)
    n_per_cohort = full["cohort"].value_counts().to_dict()

    im1 = ax1.imshow(ct1.values, cmap="RdYlGn_r", vmin=0, vmax=50, aspect="auto")
    for i, cohort in enumerate(ct1.index):
        for j, reason in enumerate(ct1.columns):
            v = ct1.iloc[i, j]
            color = "white" if v > 30 else "#222"
            ax1.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                     color=color, fontweight="bold")
    ax1.set_xticks(range(len(REASONS_ORDER)))
    ax1.set_xticklabels(REASONS_ORDER, rotation=35, ha="right", fontsize=9)
    ax1.set_yticks(range(len(ct1.index)))
    ax1.set_yticklabels([f"{c} (n={n_per_cohort.get(c, 0)})" for c in ct1.index], fontsize=9)
    ax1.set_title("(a) Cohort × Rejection Reason (% within cohort row)",
                   fontweight="bold", loc="left")

    # Event panel
    if "event" in full.columns:
        full_ev = full.dropna(subset=["event"])
        EVENTS_ORDER = ["Limited PSLF Waiver", "IDR Account Adjustment",
                         "Biden Mass Forgiveness", "Biden v. Nebraska SCOTUS",
                         "Payments Restart", "SAVE Admin Forbearance",
                         "Trump PSLF EO", "Final Trump PSLF Rule"]
        ct2 = pd.crosstab(full_ev["event"], full_ev["rejection_reason"], normalize="index") * 100
        ct2 = ct2.reindex(index=EVENTS_ORDER, columns=REASONS_ORDER).fillna(0)
        n_per_event = full_ev["event"].value_counts().to_dict()

        im2 = ax2.imshow(ct2.values, cmap="RdYlGn_r", vmin=0, vmax=50, aspect="auto")
        for i, ev in enumerate(ct2.index):
            for j, reason in enumerate(ct2.columns):
                v = ct2.iloc[i, j]
                color = "white" if v > 30 else "#222"
                ax2.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                         color=color, fontweight="bold")
        ax2.set_xticks(range(len(REASONS_ORDER)))
        ax2.set_xticklabels(REASONS_ORDER, rotation=35, ha="right", fontsize=9)
        ax2.set_yticks(range(len(ct2.index)))
        ax2.set_yticklabels([f"{e} (n={n_per_event.get(e, 0)})" for e in ct2.index], fontsize=9)
        ax2.set_title("(b) Event Window × Rejection Reason (% within event row)",
                       fontweight="bold", loc="left")

    fig.suptitle(f"PSLF Rejection Reasons by Cohort and Event Window  (n={len(full):,} rejecting posts)",
                 fontsize=14, fontweight="bold", y=1.005)
    plt.tight_layout()
    out = "fig_substantive_3_rejection_reasons.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 4: Topic-restructuring 3D heatmap
# ============================================================
def fig_substantive_4():
    """Per-event × per-cohort × per-topic delta heatmap (3D as panels)."""
    print("\n[Fig 4] Topic-restructuring 3D heatmap...")
    if not os.path.exists("topic_per_cohort_per_event_results.csv"):
        print("  [SKIP] topic_per_cohort_per_event_results.csv not found")
        return
    df = pd.read_csv("topic_per_cohort_per_event_results.csv")
    EVENTS_ORDER = ["Limited PSLF Waiver", "IDR Account Adjustment",
                     "Biden Mass Forgiveness", "Biden v. Nebraska SCOTUS",
                     "Payments Restart", "SAVE Admin Forbearance",
                     "Trump PSLF EO", "Final Trump PSLF Rule"]
    TOPICS = ["servicer_issues", "policy_uncertainty", "financial_planning",
              "career_impact", "success_story", "general_question", "frustration_venting"]
    delta_cols = [f"delta_{t}" for t in TOPICS if f"delta_{t}" in df.columns]

    cohorts_present = [c for c in
                        ["SDN (Medical)", "Reddit r/PSLF", "Reddit r/StudentLoans",
                         "Reddit Finance", "Reddit Medical"]
                        if c in df["cohort"].values]

    fig, axes = plt.subplots(1, len(cohorts_present),
                              figsize=(4.2 * len(cohorts_present), 7.5),
                              sharey=True)
    if len(cohorts_present) == 1:
        axes = [axes]

    for ax, cohort in zip(axes, cohorts_present):
        sub = df[df["cohort"] == cohort].set_index("event").reindex(EVENTS_ORDER)
        # Build matrix
        mat = np.array([[sub.iloc[i].get(c, np.nan) if not sub.iloc[i].isna().all() else np.nan
                          for c in delta_cols]
                         for i in range(len(EVENTS_ORDER))])
        norm = mcolors.TwoSlopeNorm(vmin=-50, vcenter=0, vmax=50)
        im = ax.imshow(mat, cmap="RdYlGn", norm=norm, aspect="auto")
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                v = mat[i, j]
                if np.isnan(v):
                    ax.text(j, i, "—", ha="center", va="center", fontsize=9, color="#888")
                else:
                    color = "white" if abs(v) > 35 else "#222"
                    ax.text(j, i, f"{v:+.0f}", ha="center", va="center",
                            fontsize=8, color=color, fontweight="bold")
        ax.set_xticks(range(len(delta_cols)))
        ax.set_xticklabels([t.replace("delta_", "").replace("_", "\n") for t in delta_cols],
                            rotation=0, ha="center", fontsize=8)
        if ax == axes[0]:
            ax.set_yticks(range(len(EVENTS_ORDER)))
            ax.set_yticklabels(EVENTS_ORDER, fontsize=9)
        ax.set_title(cohort, fontweight="bold", color=COHORT_COLORS.get(cohort, "#222"),
                      fontsize=11)

    fig.suptitle("Per-Event × Per-Cohort TOPIC Restructuring (Δ pp from pre to post)\n"
                 "Different cohorts shift to DIFFERENT topics on the same event",
                 fontsize=13, fontweight="bold", y=1.005)
    fig.text(0.99, 0.005,
             "Cells show post-window topic % minus pre-window topic %. "
             "Cells with n_pre or n_post < 20 shown as '—'. Color: green = topic INCREASED, red = topic DECREASED.",
             ha="right", fontsize=8, style="italic", color="#666")

    plt.tight_layout()
    out = "fig_substantive_4_topic_3d_heatmap.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 5: OP vs Reply by cohort
# ============================================================
def fig_methods_1():
    """Side-by-side bar charts of OP-Reply diffs by cohort for TB and VADER."""
    print("\n[Fig 5] OP vs Reply by cohort...")
    if not os.path.exists("per_profession_breakdowns.txt"):
        print("  [SKIP] per_profession_breakdowns.txt not found")
        return
    # Hard-coded from per_profession_breakdowns output
    data = [
        ("Reddit r/PSLF",          10645, -0.0121, 0.221, "***"),
        ("Reddit r/StudentLoans",   2539, -0.0262, 0.248, "***"),
        ("Reddit Finance",           624, -0.0271, 0.305, "***"),
        ("Reddit Medical",           546, -0.0260, 0.199, "***"),
        ("Other",                    507, -0.0132, 0.215, "**"),
        ("Reddit PA",                236, -0.0276, 0.341, "**"),
        ("Reddit Teaching",          181, -0.0105, 0.269, "*"),
        ("Reddit Nursing",           106, -0.0058, 0.227, "*"),
    ]
    df = pd.DataFrame(data, columns=["cohort", "n", "tb_diff", "va_diff", "sig"])
    df = df.sort_values("n", ascending=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    y = np.arange(len(df))

    ax1.barh(y, df["tb_diff"],
             color=[COHORT_COLORS.get(c, "#888") for c in df["cohort"]],
             edgecolor="white", linewidth=1.5)
    # Bar labels positioned to the LEFT of the zero line (since bars go negative)
    for i, r in enumerate(df.itertuples()):
        ax1.text(0.0005, i, f"  {r.tb_diff:+.4f} {r.sig}",
                  ha="left", va="center", fontsize=9, fontweight="bold",
                  color="#222")
    ax1.axvline(x=0, color="#222", linewidth=1.0)
    ax1.set_yticks(y)
    ax1.set_yticklabels([f"{r.cohort} (n={r.n:,})" for r in df.itertuples()], fontsize=9)
    ax1.set_xlim(-0.040, 0.018)
    ax1.set_xlabel("TextBlob: OP polarity − mean reply polarity",
                    fontsize=10, fontweight="bold")
    ax1.set_title("(a) TextBlob: replies MORE positive than OPs in 8/8 cohorts",
                   fontweight="bold", loc="left")
    ax1.text(-0.020, -0.5, "(negative = replies more positive)",
              fontsize=9, color="#666", style="italic", ha="center")

    ax2.barh(y, df["va_diff"],
             color=[COHORT_COLORS.get(c, "#888") for c in df["cohort"]],
             edgecolor="white", linewidth=1.5)
    for i, r in enumerate(df.itertuples()):
        ax2.text(r.va_diff + 0.008, i, f"+{r.va_diff:.3f} {r.sig}",
                  ha="left", va="center", fontsize=9, fontweight="bold",
                  color="#222")
    ax2.axvline(x=0, color="#222", linewidth=1.0)
    ax2.set_yticks(y)
    ax2.set_yticklabels([])
    ax2.set_xlim(0, 0.45)
    ax2.set_xlabel("VADER: OP compound − mean reply compound",
                    fontsize=10, fontweight="bold")
    ax2.set_title("(b) VADER: OPs MORE arousal than replies in 8/8 cohorts (OPPOSITE direction from TextBlob)",
                   fontweight="bold", loc="left")
    ax2.text(0.20, -0.5, "(positive = OPs more aroused)",
              fontsize=9, color="#666", style="italic", ha="center")

    fig.suptitle("OP vs Reply: TextBlob and VADER show OPPOSITE-DIRECTION sentiment differences\n"
                 "within the same posts (n=15,550). Cohort-invariant construct mismatch.",
                 fontsize=13, fontweight="bold", y=1.005)
    fig.text(0.99, 0.005,
             "Cluster bootstrap CI by post_id. Both columns: bootstrap p=0 (zero of 2,000 iterations crossed null).",
             ha="right", fontsize=8, style="italic", color="#666")

    plt.tight_layout()
    out = "fig_methods_1_op_vs_reply_cohort.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 6: Trump EO joint Hotelling visualization
# ============================================================
def fig_methods_2():
    """Trump EO 3-vector visualization with joint significance."""
    print("\n[Fig 6] Trump EO joint Hotelling visualization...")
    fig, ax = plt.subplots(figsize=(11, 7))

    scorers = [("TextBlob (lexical affect)", -0.325, 0.007, "#FF6B35"),
                ("VADER (expressive arousal)", 0.161, 0.174, "#2196F3"),
                ("Claude (LLM-prompted stance)", 0.335, 0.005, "#7B1FA2")]
    y = np.arange(len(scorers))
    for i, (name, g, p, color) in enumerate(scorers):
        ax.barh(y[i], g, color=color, edgecolor="white", linewidth=1.5, height=0.6)
        sig = ("***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s.")
        # Place value label just past the bar tip, opposite the bar's direction
        if g > 0:
            ax.text(g + 0.02, i, f"  g={g:+.3f}, p={p:.3g} {sig}",
                    ha="left", va="center", fontsize=11, fontweight="bold", color="#222")
        else:
            ax.text(g - 0.02, i, f"g={g:+.3f}, p={p:.3g} {sig}  ",
                    ha="right", va="center", fontsize=11, fontweight="bold", color="#222")
    ax.axvline(x=0, color="#222", linewidth=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in scorers], fontsize=11)
    ax.set_xlabel("Hedges' g (Trump PSLF EO ±60d window, n=771 pre / 559 post)",
                  fontsize=11, fontweight="bold")
    ax.set_xlim(-0.65, 0.65)
    ax.set_ylim(-0.5, 2.5)

    title = ("Trump PSLF EO (2025-03-07): Three Scorers Disagree on DIRECTION on the Same n=1,330 Posts\n"
             "Joint Hotelling T² = 93.0, F(3, 1326) = 30.95, p = 1.11×10⁻¹⁶  →  joint shift IS non-zero, components disagree on direction")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=15)

    # Place callout box at bottom-center (clear of bars and title)
    ax.text(0, -0.42,
             "Joint mean-shift vector ≠ 0 (decisively significant), but its components disagree on direction "
             "→ instruments measure DIFFERENT constructs",
             fontsize=10, color="#444", style="italic",
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFE082", edgecolor="#666", alpha=0.85),
             ha="center", va="center")

    plt.tight_layout()
    out = "fig_methods_2_trump_eo_joint.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 7: K-α sample-stability across rounds
# ============================================================
def fig_methods_3():
    """Sample-stability of three-rater alpha across 3 corpus expansions."""
    print("\n[Fig 7] K-alpha sample-stability across rounds...")
    fig, ax = plt.subplots(figsize=(12, 7))

    # Manual data: round, n, alpha_canonical, alpha_canonical_lo/hi, alpha_charitable, charitable_lo/hi
    rounds = [
        ("Round 6/7\n(initial Path C)", 4838, -0.027, -0.045, -0.012, 0.150, 0.140, 0.160),
        ("Round 7\n(fullcorpus +44%)", 6975, -0.027, -0.041, -0.012, 0.170, 0.155, 0.185),
        ("Round 8/9\n(Arctic Shift +33%)", 9242, -0.0174, -0.0306, -0.0049, 0.196, 0.183, 0.208),
    ]
    x = np.arange(len(rounds))
    n_vals = [r[1] for r in rounds]
    alpha_canon = [r[2] for r in rounds]
    canon_lo = [r[3] for r in rounds]
    canon_hi = [r[4] for r in rounds]
    alpha_chari = [r[5] for r in rounds]
    chari_lo = [r[6] for r in rounds]
    chari_hi = [r[7] for r in rounds]

    # Plot canonical
    ax.errorbar(x - 0.15, alpha_canon,
                 yerr=[np.array(alpha_canon) - np.array(canon_lo),
                       np.array(canon_hi) - np.array(alpha_canon)],
                 fmt="o-", color="#C2185B", linewidth=2, markersize=12,
                 capsize=8, label="Canonical α (fixed thresholds)", elinewidth=2)
    # Plot charitable
    ax.errorbar(x + 0.15, alpha_chari,
                 yerr=[np.array(alpha_chari) - np.array(chari_lo),
                       np.array(chari_hi) - np.array(alpha_chari)],
                 fmt="s-", color="#388E3C", linewidth=2, markersize=12,
                 capsize=8, label="Charitable α (percentile-matched)", elinewidth=2)

    # Annotate point estimates
    for i in range(len(rounds)):
        ax.text(x[i] - 0.15, alpha_canon[i] - 0.04, f"{alpha_canon[i]:+.3f}",
                ha="center", fontsize=9, color="#C2185B", fontweight="bold")
        ax.text(x[i] + 0.15, alpha_chari[i] + 0.025, f"{alpha_chari[i]:+.3f}",
                ha="center", fontsize=9, color="#388E3C", fontweight="bold")

    ax.axhline(y=0.667, color="#999", linestyle="--", linewidth=1.0, alpha=0.7)
    ax.text(2, 0.69, "0.667 floor for tentative reliability (Krippendorff 1980)",
             fontsize=9, color="#666", style="italic", ha="center")
    ax.axhline(y=0, color="#222", linewidth=0.6, alpha=0.5)

    # Round-9 test-retest callout (separate axis on right showing the "noise floor")
    ax.text(2.55, 0.95,
             "Test-retest:\n"
             "α = +0.934 (Reddit, temp=1 vs temp=1)\n"
             "α = +0.958 (SDN, temp=0 vs temp=1)\n"
             "→ LLM noise far above α reliability floor;\n"
             "cross-instrument α near 0 ≠ measurement noise",
             fontsize=9, color="#222", style="italic",
             bbox=dict(boxstyle="round,pad=0.6", facecolor="#E1F5FE",
                       edgecolor="#1565C0", alpha=0.9),
             ha="center", va="top")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{r[0]}\nn = {r[1]:,}" for r in rounds], fontsize=10)
    ax.set_ylabel("Krippendorff's three-rater α", fontsize=11, fontweight="bold")
    ax.set_ylim(-0.1, 1.05)
    ax.set_xlim(-0.5, 3.2)
    ax.legend(loc="upper left", fontsize=10, frameon=True,
              facecolor="white", edgecolor="#CCC")
    ax.set_title("Three-Rater Krippendorff's α Sample-Stability + Test-Retest Reliability\n"
                 "Cross-instrument α (red/green) far below 0.667 reliability floor; same-instrument re-test α (callout) far above it",
                 fontsize=12, fontweight="bold", loc="left")

    plt.tight_layout()
    out = "fig_methods_3_alpha_stability.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


# ============================================================
# FIG 8: Per-event cohort-heterogeneity BH-FDR forest
# ============================================================
def fig_methods_4():
    """Forest plot of per-event × per-cohort g with BH-FDR significance highlighted."""
    print("\n[Fig 8] Per-event cohort-heterogeneity BH-FDR forest...")
    if not os.path.exists("per_profession_per_event_results.csv"):
        print("  [SKIP] per_profession_per_event_results.csv not found")
        return
    df = pd.read_csv("per_profession_per_event_results.csv")
    df = df[df["scorer"] == "polarity"] if "scorer" in df.columns else df
    df = df.dropna(subset=["g", "p_boot"])
    # BH FDR within family
    df_sorted = df.sort_values("p_boot").reset_index(drop=True)
    n = len(df_sorted)
    df_sorted["bh_threshold"] = (df_sorted.index + 1) * 0.05 / n
    df_sorted["bh_pass"] = df_sorted["p_boot"] <= df_sorted["bh_threshold"]
    if df_sorted["bh_pass"].any():
        max_pass_idx = df_sorted[df_sorted["bh_pass"]].index.max()
        df_sorted.loc[:max_pass_idx, "bh_pass"] = True

    # Reorder by event for display
    EVENTS_ORDER = ["Limited PSLF Waiver", "IDR Account Adjustment",
                     "Biden Mass Forgiveness", "Biden v. Nebraska SCOTUS",
                     "Payments Restart", "SAVE Admin Forbearance",
                     "Trump PSLF EO", "Final Trump PSLF Rule"]
    df_sorted["event_order"] = df_sorted["event"].map(
        {e: i for i, e in enumerate(EVENTS_ORDER)})
    df_sorted = df_sorted.sort_values(["event_order", "g"])

    fig, ax = plt.subplots(figsize=(13, 11))
    y = np.arange(len(df_sorted))
    for i, (_, r) in enumerate(df_sorted.iterrows()):
        color = COHORT_COLORS.get(r["profession_label"], "#888")
        alpha = 1.0 if r["bh_pass"] else 0.35
        ax.scatter(r["g"], y[i], s=180 if r["bh_pass"] else 80,
                   color=color, alpha=alpha, edgecolors="white" if r["bh_pass"] else "none",
                   linewidths=2 if r["bh_pass"] else 0, zorder=10)
        # Marker for BH-pass
        if r["bh_pass"]:
            ax.text(r["g"] + (0.05 if r["g"] > 0 else -0.05), i, "★",
                     color="#C62828", fontsize=14, fontweight="bold",
                     ha="left" if r["g"] > 0 else "right", va="center")

    ax.axvline(x=0, color="#222", linewidth=1.5)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r['event']}: {r['profession_label']} (n={int(r['n_pre'])}/{int(r['n_post'])})"
                        for _, r in df_sorted.iterrows()], fontsize=8)
    ax.set_xlabel("Hedges' g (per-event × per-cohort, polarity)",
                   fontsize=11, fontweight="bold")
    ax.set_title("Per-Event × Per-Cohort Sentiment Shifts (★ = BH FDR q=0.05 significant)\n"
                 "Cohort heterogeneity: same event produces different magnitudes (and sometimes opposite signs) across cohorts",
                  fontsize=12, fontweight="bold", loc="left")
    ax.set_xlim(-1, 2.0)

    # Cohort legend
    cohorts_in_data = df_sorted["profession_label"].unique()
    handles = [mpatches.Patch(color=COHORT_COLORS.get(c, "#888"), label=c)
               for c in cohorts_in_data if c in COHORT_COLORS]
    ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=True,
              facecolor="white", edgecolor="#CCC")

    plt.tight_layout()
    out = "fig_methods_4_per_event_cohort_forest.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out}")


def main():
    print("=" * 80)
    print("Generating 8 paper-ready figures")
    print("=" * 80)
    fig_substantive_1()
    fig_substantive_2()
    fig_substantive_3()
    fig_substantive_4()
    fig_methods_1()
    fig_methods_2()
    fig_methods_3()
    fig_methods_4()
    print("\nAll done.")


if __name__ == "__main__":
    main()
