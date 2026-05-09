"""
pslf_intention_analysis.py
==========================
Analyze PSLF *intention* (Claude `pslf_stance`) separately from *sentiment*
(`pslf_sentiment`), addressing the project's substantive research question:
how do online discussants' stated intention to pursue PSLF vary by profession
and shift around policy events?

Contrast with sentiment_triangulation.py:
  - That script measures how three sentiment instruments DISAGREE.
  - This script measures behavioral intention as a separate construct.
  - Intention is sticky; affect isn't. So intention shifts around events are
    expected to be SMALLER than sentiment shifts — but more policy-relevant.

Outputs:
  - intention_results.txt — full text artifact
  - intention_results.csv — per-event stance shift table
  - intention_trajectory.png — proportion of pursuing/rejecting over time, by
    profession
  - intention_event_forest.png — pre/post rejecting-rate change per event
"""
from __future__ import annotations

import io
import os
import sys
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ---- Aesthetic theme (consistent with other figs) ----
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
    "font.family": "DejaVu Sans",
})

# Canonical 8-event list
EVENTS = [
    ("Limited PSLF Waiver", "2021-10-06", 90),
    ("IDR Account Adjustment", "2022-04-19", 90),
    ("Biden Mass Forgiveness", "2022-08-24", 90),
    ("Biden v. Nebraska SCOTUS", "2023-06-30", 90),
    ("Payments Restart", "2023-10-01", 90),
    ("SAVE Admin Forbearance", "2024-08-09", 90),
    ("Trump PSLF EO", "2025-03-07", 60),
    ("Final Trump PSLF Rule", "2025-10-30", 60),
]

# Profession label normalization (subreddit-to-profession map)
PROF_LABEL = {
    "medical": "Medical",
    "teacher": "Teaching",
    "teaching": "Teaching",
    "general_pslf": "r/PSLF",
    "general_student_loans": "r/StudentLoans",
    "nursing": "Nursing",
    "law": "Law",
    "social_work": "Social Work",
    "federal_employee": "Federal",
    "pharmacy": "Pharmacy",
    "physician_assistant": "PA",
    "occupational_therapy": "OT",
    "speech_language_pathology": "SLP",
    "general_finance": "Finance",
    "personalfinance": "Finance",
    "sdn_medical": "SDN (Medical)",
    "sdn": "SDN (Medical)",
}


def load_zeroshot_with_meta():
    """Load all zeroshot CSVs and join with original CSVs to get date + profession.

    Returns a single DataFrame with columns:
      post_id, pslf_sentiment, pslf_stance, primary_topic,
      profession_norm, source_csv, date, claude_subsample
    """
    candidates = [
        ("zeroshot_reddit_n1000.csv", "reddit_cross"),
        ("zeroshot_sdn_n1000.csv", "sdn_cross"),
        ("zeroshot_reddit_eventstrat.csv", "reddit_eventstrat"),
        ("zeroshot_reddit_eventfull.csv", "reddit_eventfull"),
        ("zeroshot_sdn_eventfull.csv", "sdn_eventfull"),
    ]
    zs_frames = []
    for f, label in candidates:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        d = d[~d["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
        d["claude_subsample"] = label
        zs_frames.append(d[["post_id", "pslf_sentiment", "pslf_stance",
                            "primary_topic", "profession", "source",
                            "claude_subsample"]])
    if not zs_frames:
        raise FileNotFoundError("No zeroshot_*.csv found.")
    zs = pd.concat(zs_frames, ignore_index=True)
    # Dedup by post_id (eventstrat/eventfull may overlap with cross-source)
    zs = zs.drop_duplicates("post_id", keep="first").reset_index(drop=True)
    print(f"Loaded {len(zs):,} unique zeroshot rows from {len(zs_frames)} CSVs")

    # Merge dates from source CSVs
    reddit_frames = []
    for f in ["reddit_professions_pslf.csv",
              "comprehensive_medical_pslf_discussions.csv",
              "comprehensive_teacher_pslf_discussions.csv"]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            d = d.rename(columns={"id": "post_id"})
            keep = ["post_id"]
            if "created_utc" in d.columns:
                d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"],
                                                          errors="coerce"),
                                            unit="s")
                keep.append("date")
            if "subreddit" in d.columns:
                keep.append("subreddit")
            if "profession" in d.columns:
                d = d.rename(columns={"profession": "profession_orig"})
                keep.append("profession_orig")
            reddit_frames.append(d[keep])
    reddit_src = pd.concat(reddit_frames, ignore_index=True).drop_duplicates("post_id")

    sdn = pd.read_csv("forum_pslf_discussions.csv")
    sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce",
                                  utc=True).dt.tz_localize(None)
    sdn_src = sdn[["post_id", "date"]].drop_duplicates("post_id")

    zs = zs.merge(reddit_src, on="post_id", how="left", suffixes=("", "_r"))
    zs = zs.merge(sdn_src, on="post_id", how="left", suffixes=("", "_s"))
    if "date_s" in zs.columns:
        zs["date"] = zs["date"].fillna(zs["date_s"])
    zs = zs.drop(columns=[c for c in zs.columns if c.endswith("_s")
                          or c.endswith("_r")], errors="ignore")
    zs["date"] = pd.to_datetime(zs["date"], utc=True, errors="coerce").dt.tz_localize(None)

    # Profession: prefer original, fall back to zeroshot output
    if "profession_orig" in zs.columns:
        zs["profession_norm"] = (zs["profession_orig"].fillna("")
                                 .where(zs["profession_orig"].notna() &
                                        (zs["profession_orig"] != ""),
                                        zs["profession"]))
    else:
        zs["profession_norm"] = zs["profession"]
    # SDN fallback
    sdn_mask = zs["claude_subsample"].isin(["sdn_cross", "sdn_eventfull"])
    zs.loc[sdn_mask & zs["profession_norm"].isna(), "profession_norm"] = "sdn_medical"
    zs.loc[sdn_mask & (zs["profession_norm"] == ""), "profession_norm"] = "sdn_medical"

    # Map to display labels
    zs["profession_display"] = (zs["profession_norm"].map(PROF_LABEL)
                                 .fillna(zs["profession_norm"].fillna("Other")))

    print(f"  Merged: {zs['date'].notna().sum():,} have dates, "
          f"{(zs['pslf_stance'] != 'unknown').sum():,} have non-unknown stance")
    return zs


def overall_distributions(zs):
    """Return overall stance, sentiment, topic distributions."""
    return {
        "stance": zs["pslf_stance"].value_counts(),
        "sentiment": zs["pslf_sentiment"].value_counts(),
        "topic": zs["primary_topic"].value_counts(),
    }


def stance_by_profession(zs, min_n=20):
    """Stance proportions by profession (excludes unknown)."""
    valid = zs[zs["pslf_stance"] != "unknown"].copy()
    counts = valid.groupby(["profession_display", "pslf_stance"]).size().unstack(fill_value=0)
    n = counts.sum(axis=1)
    counts = counts[n >= min_n].copy()
    n_filt = counts.sum(axis=1)
    props = counts.div(n_filt, axis=0)
    props["n_total"] = n_filt
    return counts, props


def stance_pre_post_event(zs, event_name, event_date, window_days):
    """For a single event, compute stance distribution pre vs post + chi-sq."""
    dt = pd.Timestamp(event_date)
    valid = zs[(zs["pslf_stance"] != "unknown") & zs["date"].notna()].copy()
    pre = valid[(valid["date"] >= dt - pd.Timedelta(days=window_days)) &
                 (valid["date"] < dt)]
    post = valid[(valid["date"] >= dt) &
                  (valid["date"] <= dt + pd.Timedelta(days=window_days))]
    if len(pre) < 10 or len(post) < 10:
        return None
    pre_counts = pre["pslf_stance"].value_counts()
    post_counts = post["pslf_stance"].value_counts()
    all_categories = sorted(set(pre_counts.index) | set(post_counts.index))
    pre_v = [pre_counts.get(c, 0) for c in all_categories]
    post_v = [post_counts.get(c, 0) for c in all_categories]
    # Chi-square test of independence (stance × pre/post)
    contingency = np.array([pre_v, post_v])
    try:
        chi2, p_chi, dof, _ = stats.chi2_contingency(contingency)
    except Exception:
        chi2, p_chi = float("nan"), float("nan")
    pre_total = sum(pre_v)
    post_total = sum(post_v)
    # Specifically: rejecting-rate change
    pre_rej = pre_counts.get("rejecting", 0) / pre_total if pre_total > 0 else 0.0
    post_rej = post_counts.get("rejecting", 0) / post_total if post_total > 0 else 0.0
    pre_pursuing = pre_counts.get("pursuing", 0) / pre_total if pre_total > 0 else 0.0
    post_pursuing = post_counts.get("pursuing", 0) / post_total if post_total > 0 else 0.0
    # 2-prop z-test for rejecting rate
    if pre_total > 0 and post_total > 0:
        # Pooled rate
        pooled_rej = (pre_counts.get("rejecting", 0) + post_counts.get("rejecting", 0)) / (pre_total + post_total)
        se_rej = np.sqrt(pooled_rej * (1 - pooled_rej) * (1/pre_total + 1/post_total))
        z_rej = (post_rej - pre_rej) / se_rej if se_rej > 0 else 0.0
        p_rej = 2 * (1 - stats.norm.cdf(abs(z_rej)))
    else:
        z_rej, p_rej = float("nan"), float("nan")
    return {
        "event": event_name, "date": event_date, "window": window_days,
        "n_pre": pre_total, "n_post": post_total,
        "categories": all_categories,
        "pre_counts": dict(zip(all_categories, pre_v)),
        "post_counts": dict(zip(all_categories, post_v)),
        "pre_rejecting_rate": pre_rej, "post_rejecting_rate": post_rej,
        "delta_rejecting_pp": (post_rej - pre_rej) * 100,
        "z_rejecting": z_rej, "p_rejecting": p_rej,
        "pre_pursuing_rate": pre_pursuing, "post_pursuing_rate": post_pursuing,
        "delta_pursuing_pp": (post_pursuing - pre_pursuing) * 100,
        "chi2": chi2, "p_chi2": p_chi,
    }


def stance_topic_cross(zs):
    """Stance × topic cross-tab."""
    valid = zs[(zs["pslf_stance"] != "unknown") &
                ~zs["primary_topic"].isin(["parse_error", "api_error"])].copy()
    ct = pd.crosstab(valid["primary_topic"], valid["pslf_stance"])
    ct["n_total"] = ct.sum(axis=1)
    ct["pct_rejecting"] = (ct.get("rejecting", 0) / ct["n_total"] * 100).round(1)
    ct["pct_pursuing"] = (ct.get("pursuing", 0) / ct["n_total"] * 100).round(1)
    return ct.sort_values("n_total", ascending=False)


def stance_sentiment_decoupling(zs):
    """Cross-tab of sentiment × stance to show how much they decouple.

    The substantive question: of `negative` and `very_negative` sentiment
    posts, what fraction are still `pursuing`? If high, sentiment shifts
    overstate the meaning for behavior.
    """
    valid = zs[(zs["pslf_stance"] != "unknown")].copy()
    ct = pd.crosstab(valid["pslf_sentiment"], valid["pslf_stance"])
    ct["n_total"] = ct.sum(axis=1)
    if "pursuing" in ct.columns:
        ct["pct_pursuing"] = (ct["pursuing"] / ct["n_total"] * 100).round(1)
    if "rejecting" in ct.columns:
        ct["pct_rejecting"] = (ct["rejecting"] / ct["n_total"] * 100).round(1)
    # Order by sentiment ordinal
    sent_order = ["very_negative", "negative", "neutral", "positive", "very_positive"]
    ct = ct.reindex([s for s in sent_order if s in ct.index])
    return ct


def fig_intention_trajectory(zs, path="intention_trajectory.png"):
    """Quarterly stacked-area plot of stance composition, faceted by profession."""
    valid = zs[(zs["pslf_stance"] != "unknown") & zs["date"].notna()].copy()
    valid = valid[valid["date"] >= "2018-01-01"]
    # Top professions by n
    top_profs = valid["profession_display"].value_counts().head(6).index.tolist()
    fig, axes = plt.subplots(len(top_profs), 1, figsize=(14, 2 * len(top_profs)),
                              sharex=True)
    if len(top_profs) == 1:
        axes = [axes]
    stance_order = ["pursuing", "considering", "rejecting", "completed"]
    stance_colors = {
        "pursuing": "#43A047",      # green
        "considering": "#FB8C00",   # orange
        "rejecting": "#E53935",     # red
        "completed": "#1E88E5",     # blue
    }
    for ax, prof in zip(axes, top_profs):
        sub = valid[valid["profession_display"] == prof]
        if len(sub) < 30:
            ax.text(0.5, 0.5, f"{prof}: n={len(sub)} (too sparse)",
                    transform=ax.transAxes, ha="center", va="center")
            ax.set_yticks([])
            continue
        sub = sub.set_index("date").sort_index()
        # Quarterly counts
        q = sub.groupby([pd.Grouper(freq="QE"), "pslf_stance"]).size().unstack(fill_value=0)
        # Reindex to ensure all stance categories present
        for s in stance_order:
            if s not in q.columns:
                q[s] = 0
        q = q[stance_order]
        # Drop empty quarters
        q = q[q.sum(axis=1) > 0]
        if q.empty:
            continue
        q_prop = q.div(q.sum(axis=1), axis=0) * 100
        ax.stackplot(q_prop.index,
                     [q_prop[s].values for s in stance_order],
                     labels=stance_order,
                     colors=[stance_colors[s] for s in stance_order],
                     alpha=0.8)
        # Event vlines
        for ev_name, ev_date, _ in EVENTS:
            ax.axvline(pd.Timestamp(ev_date), color="#222222",
                        linestyle="--", linewidth=0.5, alpha=0.5)
        ax.set_ylabel("%")
        ax.set_title(f"{prof}  (n={len(sub):,})", fontsize=11, loc="left")
        ax.set_ylim(0, 100)
        if ax is axes[0]:
            ax.legend(loc="upper left", fontsize=9, frameon=True,
                       facecolor="white", edgecolor="#CCCCCC", ncol=4)
    fig.suptitle("PSLF Intention Composition Over Time, by Profession (quarterly)",
                  fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def fig_event_forest(event_results, path="intention_event_forest.png"):
    """Forest plot of pre/post rejecting-rate change for each event."""
    deltas = [(r["event"], r["delta_rejecting_pp"], r["p_rejecting"], r["n_pre"],
               r["n_post"]) for r in event_results if r is not None]
    if not deltas:
        return
    deltas.sort(key=lambda x: x[1])
    labels = [f"{e}\n(n_pre={np_}, n_post={np2})"
              for e, _, _, np_, np2 in deltas]
    vals = [d[1] for d in deltas]
    ps = [d[2] for d in deltas]
    fig, ax = plt.subplots(figsize=(11, 7))
    y = np.arange(len(deltas))
    colors = ["#E53935" if v > 0 else "#43A047" for v in vals]
    ax.barh(y, vals, color=colors, alpha=0.75, edgecolor="white")
    ax.axvline(0, color="#222222", linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Δ Rejecting Rate (percentage points, post − pre)",
                   fontsize=12, fontweight="bold")
    ax.set_title("Pre/Post Change in PSLF Rejecting Rate, by Event",
                  fontsize=14, fontweight="bold", loc="left")
    # Annotate p-values
    for yi, (v, p) in enumerate(zip(vals, ps)):
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        ax.text(v + (0.3 if v >= 0 else -0.3), yi,
                 f"{v:+.1f}pp  p={p:.3f} {sig}",
                 va="center", ha="left" if v >= 0 else "right", fontsize=9)
    ax.grid(axis="x", alpha=0.4, linestyle=":")
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def write_artifacts(zs, dists, prof_counts, prof_props, event_results,
                     topic_ct, sent_stance_ct, path="intention_results.txt"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("PSLF Intention Analysis (Claude pslf_stance)\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/pslf_intention_analysis.py\n")
        f.write("=" * 80 + "\n\n")
        f.write("This script analyses INTENTION (Claude pslf_stance: pursuing,\n")
        f.write("considering, rejecting, completed) as a separate construct from\n")
        f.write("SENTIMENT (Claude pslf_sentiment) and AFFECT (TextBlob).\n")
        f.write("Substantive research question: how does stated intention to\n")
        f.write("pursue PSLF vary by profession and shift around policy events?\n\n")

        # Sample
        n_total = len(zs)
        n_stance = (zs["pslf_stance"] != "unknown").sum()
        n_dated = (zs["date"].notna() & (zs["pslf_stance"] != "unknown")).sum()
        f.write(f"Sample: n={n_total:,} unique posts with valid Claude scoring\n")
        f.write(f"  with non-unknown stance: {n_stance:,}\n")
        f.write(f"  with non-unknown stance AND date:  {n_dated:,}\n\n")

        # Overall stance
        f.write("-" * 80 + "\n")
        f.write("OVERALL STANCE DISTRIBUTION\n")
        f.write("-" * 80 + "\n")
        for s, c in dists["stance"].items():
            f.write(f"  {s:<15s} {c:>6,d}  ({c/n_total*100:.1f}%)\n")
        f.write(f"  {'TOTAL':<15s} {n_total:>6,d}\n\n")

        # Stance × profession
        f.write("-" * 80 + "\n")
        f.write("STANCE BY PROFESSION (% of non-unknown stance posts; n>=20)\n")
        f.write("-" * 80 + "\n")
        for prof, row in prof_props.iterrows():
            n = int(row["n_total"])
            f.write(f"\n  {prof}  (n={n:,})\n")
            for s in ["pursuing", "considering", "rejecting", "completed"]:
                if s in row:
                    pct = row[s] * 100
                    f.write(f"    {s:<15s} {pct:>5.1f}%\n")

        # Per-event stance shifts
        f.write("\n" + "-" * 80 + "\n")
        f.write("PRE/POST INTENTION SHIFTS BY EVENT\n")
        f.write("Δ Rejecting Rate (pp) and 2-prop z-test; chi-sq for full distribution.\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Event':<28s} {'win':>4s} {'n_pre':>6s} {'n_post':>7s} "
                f"{'rej_pre%':>9s} {'rej_post%':>10s} {'Δ pp':>7s} "
                f"{'p_rej':>8s} {'p_chi2':>8s}\n")
        for r in event_results:
            if r is None:
                continue
            f.write(f"{r['event']:<28s} {r['window']:>4d} "
                    f"{r['n_pre']:>6,d} {r['n_post']:>7,d} "
                    f"{r['pre_rejecting_rate']*100:>9.1f} "
                    f"{r['post_rejecting_rate']*100:>10.1f} "
                    f"{r['delta_rejecting_pp']:>+7.2f} "
                    f"{r['p_rejecting']:>8.4f} "
                    f"{r['p_chi2']:>8.4f}\n")

        # Sentiment-stance decoupling (the headline cross-tab)
        f.write("\n" + "-" * 80 + "\n")
        f.write("SENTIMENT × STANCE DECOUPLING\n")
        f.write("If sentiment and intention were tightly coupled, negative-sentiment\n")
        f.write("posts would be mostly rejecting. They aren't.\n")
        f.write("-" * 80 + "\n")
        f.write(sent_stance_ct.to_string())
        f.write("\n")
        # Pull out the headline number
        if "pursuing" in sent_stance_ct.columns and "negative" in sent_stance_ct.index:
            n_neg_pursuing = sent_stance_ct.loc["negative", "pursuing"] if "pursuing" in sent_stance_ct.columns else 0
            n_neg = sent_stance_ct.loc["negative", "n_total"]
            pct = n_neg_pursuing / n_neg * 100 if n_neg > 0 else 0
            f.write(f"\nHeadline: of {n_neg} 'negative'-sentiment posts, "
                    f"{n_neg_pursuing} ({pct:.1f}%) are still pursuing PSLF.\n")
            f.write("Sentiment and intention are partially decoupled — affect doesn't determine commitment.\n")

        # Topic × stance
        f.write("\n" + "-" * 80 + "\n")
        f.write("TOPIC × STANCE (which topics drive which intention?)\n")
        f.write("-" * 80 + "\n")
        f.write(topic_ct.to_string())
        f.write("\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")
    print(f"Saved: {path}")

    # CSV mirror of per-event results
    csv_path = path.rsplit(".", 1)[0] + ".csv"
    rows = [r for r in event_results if r is not None]
    if rows:
        df = pd.DataFrame([{
            "event": r["event"], "date": r["date"], "window": r["window"],
            "n_pre": r["n_pre"], "n_post": r["n_post"],
            "pre_rejecting_rate": r["pre_rejecting_rate"],
            "post_rejecting_rate": r["post_rejecting_rate"],
            "delta_rejecting_pp": r["delta_rejecting_pp"],
            "z_rejecting": r["z_rejecting"], "p_rejecting": r["p_rejecting"],
            "pre_pursuing_rate": r["pre_pursuing_rate"],
            "post_pursuing_rate": r["post_pursuing_rate"],
            "delta_pursuing_pp": r["delta_pursuing_pp"],
            "chi2": r["chi2"], "p_chi2": r["p_chi2"],
        } for r in rows])
        df.to_csv(csv_path, index=False, float_format="%.6f")
        print(f"Saved: {csv_path}")


def main():
    print("Loading and merging zeroshot data with source CSVs...")
    zs = load_zeroshot_with_meta()

    print("\nComputing distributions...")
    dists = overall_distributions(zs)
    print(f"  Stance: {dict(dists['stance'])}")

    print("\nStance by profession...")
    prof_counts, prof_props = stance_by_profession(zs)

    print("\nPer-event intention shifts...")
    event_results = []
    for ev_name, ev_date, win in EVENTS:
        r = stance_pre_post_event(zs, ev_name, ev_date, win)
        event_results.append(r)
        if r is not None:
            print(f"  {ev_name}: rej {r['pre_rejecting_rate']*100:.1f}% → "
                  f"{r['post_rejecting_rate']*100:.1f}% "
                  f"(Δ {r['delta_rejecting_pp']:+.1f} pp, p={r['p_rejecting']:.4f})")

    print("\nSentiment × stance decoupling cross-tab...")
    sent_stance = stance_sentiment_decoupling(zs)
    print(sent_stance)

    print("\nTopic × stance cross-tab...")
    topic_ct = stance_topic_cross(zs)
    print(topic_ct)

    print("\nGenerating figures...")
    fig_intention_trajectory(zs)
    fig_event_forest(event_results)

    print("\nWriting artifacts...")
    write_artifacts(zs, dists, prof_counts, prof_props, event_results,
                     topic_ct, sent_stance)

    print("\nDone.")


if __name__ == "__main__":
    main()
