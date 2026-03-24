"""Generate high-resolution (300 DPI) figures for PSLF analysis.

Usage:
    python scripts/gen_hires_figs.py
    # Run from the PSLF-Discussion-Analysis directory (where CSVs live)
"""
import argparse
import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud
from collections import Counter

warnings.filterwarnings("ignore", category=FutureWarning)

# Import shared PSLF filter regex
try:
    from pslf_search_terms import PSLF_FILTER_REGEX
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pslf_search_terms import PSLF_FILTER_REGEX

# M13 fix: use argparse or script-relative paths instead of hardcoded chdir
parser = argparse.ArgumentParser()
parser.add_argument("--data-dir", default=None, help="Directory containing CSV files")
args, _ = parser.parse_known_args()
if args.data_dir:
    os.chdir(args.data_dir)
elif os.path.exists("comprehensive_medical_pslf_discussions.csv"):
    pass  # already in the right directory
elif os.path.exists(os.path.join(os.path.dirname(__file__), "..", "PSLF-Discussion-Analysis")):
    os.chdir(os.path.join(os.path.dirname(__file__), "..", "PSLF-Discussion-Analysis"))

# ---- Load Reddit ----
frames = []
for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                ("comprehensive_teacher_pslf_discussions.csv", "teacher")]:
    if os.path.exists(f):
        df = pd.read_csv(f)
        df["profession"] = prof
        frames.append(df)
if not frames:
    print("[ERROR] No Reddit CSV files found. Place comprehensive_*_pslf_discussions.csv in data dir.")
    sys.exit(1)
reddit = pd.concat(frames, ignore_index=True)
reddit["date"] = pd.to_datetime(
    pd.to_numeric(reddit["created_utc"], errors="coerce"), unit="s", utc=True
).dt.tz_localize(None)
reddit["text"] = reddit["combined_text"].fillna("") + " " + reddit["title"].fillna("")

# Recompute polarity uniformly with TextBlob for both sources
from textblob import TextBlob

def textblob_polarity(text):
    try:
        return round(TextBlob(str(text)[:5000]).sentiment.polarity, 6)
    except Exception:
        return np.nan

print("Recomputing Reddit polarity with TextBlob (consistent with SDN)...")
reddit["polarity"] = reddit["text"].apply(textblob_polarity)

# ---- Load SDN (PSLF-filtered) ----
sdn = pd.read_csv("forum_pslf_discussions.csv")
body_m = sdn["body"].fillna("").str.lower().str.contains(PSLF_FILTER_REGEX, na=False)
title_m = sdn["thread_title"].fillna("").str.lower().str.contains(PSLF_FILTER_REGEX, na=False)
sdn = sdn[body_m | title_m].copy()
sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
sdn["text"] = sdn["body"].fillna("")

# Recompute SDN polarity with same TextBlob method for consistency
print("Recomputing SDN polarity with TextBlob...")
sdn["polarity"] = sdn["text"].apply(textblob_polarity)

print(f"Reddit: {len(reddit):,} | SDN (filtered): {len(sdn):,}")

# ============================================================
# FIG 1: Multi-Source Sentiment (300 DPI)
# ============================================================
sources = {"reddit_posts": reddit, "forum_sdn": sdn}
colors = {"reddit_posts": "#FF6B35", "forum_sdn": "#2196F3"}
events = [("2021-10-06", "Waiver"), ("2022-10-31", "Deadline"),
          ("2024-07-01", "SAVE\nBlocked"), ("2025-03-07", "Trump\nEO")]

fig, axes = plt.subplots(2, 2, figsize=(24, 16))
fig.suptitle(
    f"PSLF Sentiment: Multi-Source Temporal Comparison\n"
    f"Reddit (n={len(reddit):,}) vs SDN Forum (n={len(sdn):,}, PSLF-filtered)",
    fontsize=18, fontweight="bold", y=0.98,
)

def add_events(ax):
    for ds, label in events:
        ax.axvline(x=pd.Timestamp(ds), color="gray", linestyle="--", alpha=0.5, linewidth=1)

# Panel 1: Monthly polarity
ax1 = axes[0, 0]
for name, df in sources.items():
    tmp = df.dropna(subset=["date"]).copy()
    if tmp.empty or "polarity" not in tmp.columns:
        continue
    monthly = tmp.set_index("date").resample("ME")["polarity"].agg(["mean", "count"])
    monthly = monthly[monthly["count"] >= 3]
    if not monthly.empty:
        ax1.plot(monthly.index, monthly["mean"], label=name.replace("_", " ").title(),
                 color=colors.get(name, "gray"), alpha=0.8, linewidth=2)
add_events(ax1)
ax1.set_title("Monthly Mean Polarity by Source", fontsize=14, fontweight="bold")
ax1.set_ylabel("Polarity", fontsize=12)
ax1.legend(fontsize=11)
ax1.axhline(y=0, color="black", linewidth=0.5)
ax1.grid(alpha=0.3)

# Panel 2: Volume
ax2 = axes[0, 1]
for name, df in sources.items():
    tmp = df.dropna(subset=["date"]).copy()
    if tmp.empty:
        continue
    monthly = tmp.set_index("date").resample("ME").size()
    if not monthly.empty:
        ax2.plot(monthly.index, monthly.values, label=name.replace("_", " ").title(),
                 color=colors.get(name, "gray"), alpha=0.8, linewidth=2)
add_events(ax2)
ax2.set_title("Monthly Post Volume", fontsize=14, fontweight="bold")
ax2.set_ylabel("Count", fontsize=12)
ax2.legend(fontsize=11)
ax2.grid(alpha=0.3)

# Panel 3: % Negative
ax3 = axes[1, 0]
for name, df in sources.items():
    tmp = df.dropna(subset=["date"]).copy()
    if tmp.empty or "polarity" not in tmp.columns:
        continue
    monthly = tmp.set_index("date").resample("ME")["polarity"].agg(
        lambda x: (x < 0).mean() * 100 if len(x) >= 3 else np.nan
    ).dropna()
    if not monthly.empty:
        ax3.plot(monthly.index, monthly.values, label=name.replace("_", " ").title(),
                 color=colors.get(name, "gray"), alpha=0.8, linewidth=2)
add_events(ax3)
ax3.set_title("% Negative Posts by Source (Monthly)", fontsize=14, fontweight="bold")
ax3.set_ylabel("% Negative", fontsize=12)
ax3.legend(fontsize=11)
ax3.grid(alpha=0.3)

# Panel 4: Violin
ax4 = axes[1, 1]
plot_data, plot_labels, plot_colors = [], [], []
for name, df in sources.items():
    if not df.empty and "polarity" in df.columns:
        pol = df["polarity"].dropna()
        if len(pol) > 10:
            plot_data.append(pol.values)
            plot_labels.append(name.replace("_", "\n").title())
            plot_colors.append(colors.get(name, "gray"))
if plot_data:
    parts = ax4.violinplot(plot_data, showmeans=True, showmedians=True)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(plot_colors[i])
        pc.set_alpha(0.6)
    ax4.set_xticks(range(1, len(plot_labels) + 1))
    ax4.set_xticklabels(plot_labels, fontsize=12)
    ax4.set_title("Polarity Distribution by Source", fontsize=14, fontweight="bold")
    ax4.set_ylabel("Polarity", fontsize=12)
    ax4.axhline(y=0, color="black", linewidth=0.5)
    ax4.grid(alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("multi_source_sentiment_comparison.png", dpi=300, bbox_inches="tight")
print("Saved Fig 1 at 300 DPI")
plt.close()

# ============================================================
# FIG 2: Word Cloud Timecourse (300 DPI)
# ============================================================
periods = [
    ("Pre-Waiver (2016-2021)", pd.Timestamp("2016-01-01"), pd.Timestamp("2021-10-05")),
    ("PSLF Waiver (2021-2022)", pd.Timestamp("2021-10-06"), pd.Timestamp("2022-10-31")),
    ("Post-Waiver (2022-2024)", pd.Timestamp("2022-11-01"), pd.Timestamp("2024-06-30")),
    ("SAVE Crisis (2024-2026)", pd.Timestamp("2024-07-01"), pd.Timestamp("2026-12-31")),
]

stop = set(
    "the a an is are was were be been being have has had do does did will would "
    "could should may might shall can to of in for on with at by from it its "
    "this that these those i you he she we they my your and or but not no if so "
    "as just about than more very too also up out all any some into what how like "
    "get who when their know because them there which one our even don much going "
    "really still got make way want think need year years many well now back people "
    "time new said only after before over other most first then through own where "
    "here each made between since long right same such take come good him her two "
    "find day http https www com amp deleted removed click".split()
)


def mkwc(texts, title, ax):
    words = " ".join(texts.fillna("").str.lower()).split()
    freq = Counter(w for w in words if len(w) > 2 and w not in stop and w.isalpha())
    if len(freq) < 5:
        ax.text(0.5, 0.5, "Insufficient data", ha="center", va="center", fontsize=16)
        ax.set_title(title, fontsize=13)
        ax.axis("off")
        return
    wc = WordCloud(
        width=800, height=600, background_color="white", colormap="RdYlGn",
        max_words=100, prefer_horizontal=0.7, scale=2,
    )
    wc.generate_from_frequencies(freq)
    ax.imshow(wc, interpolation="bilinear")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.axis("off")


fig2, axes2 = plt.subplots(2, 4, figsize=(28, 14))
fig2.suptitle(
    "PSLF Discussion Word Clouds by Policy Era (Filtered to PSLF-Relevant Posts)\n"
    "Reddit (top) vs SDN Forum (bottom)",
    fontsize=18, fontweight="bold", y=0.99,
)

for i, (label, s, e) in enumerate(periods):
    sub = reddit[(reddit["date"] >= s) & (reddit["date"] <= e)]
    pol = sub["polarity"].mean() if "polarity" in sub.columns and len(sub) > 0 else 0
    mkwc(sub["text"], f"Reddit: {label}\n(n={len(sub):,}, pol={pol:.3f})", axes2[0, i])

for i, (label, s, e) in enumerate(periods):
    sub = sdn[(sdn["date"] >= s) & (sdn["date"] <= e)]
    pol = sub["polarity"].mean() if "polarity" in sub.columns and len(sub) > 0 else 0
    mkwc(sub["text"], f"SDN: {label}\n(n={len(sub):,}, pol={pol:.3f})", axes2[1, i])

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig("pslf_wordcloud_timecourse.png", dpi=300, bbox_inches="tight")
print("Saved Fig 2 at 300 DPI")
plt.close()
