"""Final summary report for PSLF Discussion Analysis."""
import os, sys, warnings
sys.stdout = __import__("io").TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from scipy import stats
from pslf_search_terms import PSLF_STRICT_REGEX, filter_pslf_relevant

MIN_WORDS = 20

# === Load ===
frames = []
for f, prof in [("comprehensive_medical_pslf_discussions.csv", "medical"),
                ("comprehensive_teacher_pslf_discussions.csv", "teacher")]:
    if os.path.exists(f):
        df = pd.read_csv(f); df["profession"] = prof; df["platform"] = "Reddit"
        df["date"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"), unit="s")
        df["text"] = df["combined_text"].fillna(""); frames.append(df)

pf = pd.read_csv("reddit_professions_pslf.csv")
tm = filter_pslf_relevant(pf["combined_text"])
tt = filter_pslf_relevant(pf["title"])
pf = pf[tm | tt].copy()
pf["date"] = pd.to_datetime(pd.to_numeric(pf["created_utc"], errors="coerce"), unit="s")
pf["text"] = pf["combined_text"].fillna(""); pf["platform"] = "Reddit"; frames.append(pf)

reddit = pd.concat(frames, ignore_index=True)
reddit["date"] = pd.to_datetime(reddit["date"], utc=True).dt.tz_localize(None)
wc = reddit["text"].str.split().str.len()
reddit.loc[wc < MIN_WORDS, "polarity"] = np.nan
if "vader_compound" in reddit.columns:
    reddit.loc[wc < MIN_WORDS, "vader_compound"] = np.nan

sdn = pd.read_csv("forum_pslf_discussions.csv")
bm = filter_pslf_relevant(sdn["body"])
ttm = filter_pslf_relevant(sdn["thread_title"])
sdn = sdn[bm | ttm].copy()
sdn["date"] = pd.to_datetime(sdn["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
sdn["text"] = sdn["body"].fillna(""); sdn["platform"] = "SDN Forum"; sdn["profession"] = "sdn_medical"
wc2 = sdn["text"].str.split().str.len()
sdn.loc[wc2 < MIN_WORDS, "polarity"] = np.nan

total = len(reddit) + len(sdn)
W = 80

print("=" * W)
print("PSLF DISCUSSION ANALYSIS: FINAL SUMMARY REPORT")
print("=" * W)
print(f"Date: 2026-03-24")
print(f"Total posts: {total:,} ({len(reddit):,} Reddit + {len(sdn):,} SDN)")
print(f"After sentiment filter (>={MIN_WORDS} words): {reddit['polarity'].notna().sum() + sdn['polarity'].notna().sum():,}")
print(f"Platforms: 20 communities (18 subreddits + SDN forum)")
print(f"Scoring: TextBlob polarity + VADER compound (dual)")

# 1. Profession breakdown
print(f"\n{'=' * W}")
print("1. PROFESSION BREAKDOWN (PSLF-filtered, TextBlob)")
print("=" * W)

prof_stats = reddit.groupby("profession")["polarity"].agg(
    n="count", valid=lambda x: x.notna().sum(),
    mean=lambda x: x.dropna().mean(),
    pct_neg=lambda x: (x.dropna() < 0).mean() * 100,
).sort_values("pct_neg", ascending=False)

print(f"\n  {'Profession':30s} {'n':>6s} {'Polarity':>9s} {'%Neg':>7s}")
print(f"  {'-'*54}")
for prof, row in prof_stats.iterrows():
    if row["valid"] >= 20:
        print(f"  {prof:30s} {int(row['valid']):6d} {row['mean']:9.4f} {row['pct_neg']:6.1f}%")

s_pol = sdn["polarity"].dropna()
print(f"  {'SDN Forum':30s} {len(s_pol):6d} {s_pol.mean():9.4f} {(s_pol<0).mean()*100:6.1f}%")

# 2. Policy events
print(f"\n{'=' * W}")
print("2. POLICY EVENT IMPACTS (pre/post, all sources combined)")
print("=" * W)

all_data = pd.concat([
    reddit[["date","polarity"]],
    sdn[["date","polarity"]],
], ignore_index=True).dropna(subset=["date","polarity"])

events = [
    ("Limited PSLF Waiver",  "2021-10-06", 90),
    ("Payments Restart",     "2023-10-01", 90),
    ("SAVE Plan Blocked",    "2024-07-01", 90),
    ("Trump Exec Order",     "2025-03-07", 60),
]

for name, date_str, window in events:
    dt = pd.Timestamp(date_str)
    pre = all_data[(all_data["date"] >= dt - pd.Timedelta(days=window)) & (all_data["date"] < dt)]["polarity"]
    post = all_data[(all_data["date"] >= dt) & (all_data["date"] <= dt + pd.Timedelta(days=window))]["polarity"]
    if len(pre) >= 10 and len(post) >= 10:
        t, p = stats.ttest_ind(pre, post, equal_var=False)
        # Hedges' g (Hedges 1981) — pooled SD with bias correction
        n1, n2 = len(pre), len(post)
        var1, var2 = float(pre.var(ddof=1)), float(post.var(ddof=1))
        s_pooled = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        d_cohen = (post.mean() - pre.mean()) / s_pooled if s_pooled > 0 else 0
        J = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
        g = d_cohen * J
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        arrow = "+" if post.mean() > pre.mean() else ""
        print(f"\n  {name} ({date_str}):")
        print(f"    Polarity: {pre.mean():.4f} -> {post.mean():.4f} ({arrow}{post.mean()-pre.mean():.4f}) {sig}")
        print(f"    Neg rate: {(pre<0).mean()*100:.1f}% -> {(post<0).mean()*100:.1f}%")
        print(f"    Hedges' g={g:+.3f}, n_pre={len(pre)}, n_post={len(post)}")
        print(f"    NOTE: associational only; pre/post is not interrupted time series.")

# 3. Present day
print(f"\n{'=' * W}")
print("3. PRESENT DAY (March 2026)")
print("=" * W)

last30 = all_data[all_data["date"] >= pd.Timestamp("2026-02-22")]
baseline = all_data[(all_data["date"] >= "2024-06-01") & (all_data["date"] < "2025-01-01")]
peak = all_data[(all_data["date"] >= "2021-10-06") & (all_data["date"] <= "2022-01-31")]

print(f"  Last 30 days:     n={len(last30):,}, polarity={last30['polarity'].mean():.4f}, %neg={(last30['polarity']<0).mean()*100:.1f}%")
print(f"  2024 H2 baseline: n={len(baseline):,}, polarity={baseline['polarity'].mean():.4f}, %neg={(baseline['polarity']<0).mean()*100:.1f}%")
print(f"  Post-waiver peak: n={len(peak):,}, polarity={peak['polarity'].mean():.4f}, %neg={(peak['polarity']<0).mean()*100:.1f}%")

if len(last30) >= 10 and len(baseline) >= 10:
    t, p = stats.ttest_ind(last30["polarity"], baseline["polarity"], equal_var=False)
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    print(f"\n  Present vs 2024H2: t={t:.3f}, p={p:.6f} {sig}")

# 4. Platform comparison
print(f"\n{'=' * W}")
print("4. PLATFORM COMPARISON")
print("=" * W)

r_pol = reddit["polarity"].dropna()
t, p = stats.ttest_ind(r_pol, s_pol, equal_var=False)
print(f"  Reddit: n={len(r_pol):,}, pol={r_pol.mean():.4f}, %neg={(r_pol<0).mean()*100:.1f}%, mean words={reddit['text'].str.split().str.len().mean():.0f}")
print(f"  SDN:    n={len(s_pol):,}, pol={s_pol.mean():.4f}, %neg={(s_pol<0).mean()*100:.1f}%, mean words={sdn['text'].str.split().str.len().mean():.0f}")
print(f"  t={t:.3f}, p={p:.6f}")

if "vader_compound" in reddit.columns:
    r_v = reddit["vader_compound"].dropna()
    s_v = sdn["vader_compound"].dropna() if "vader_compound" in sdn.columns else pd.Series()
    if len(r_v) > 0 and len(s_v) > 0:
        print(f"\n  VADER comparison:")
        print(f"  Reddit VADER: mean={r_v.mean():.4f}, %neg={(r_v<-0.05).mean()*100:.1f}%")
        print(f"  SDN VADER:    mean={s_v.mean():.4f}, %neg={(s_v<-0.05).mean()*100:.1f}%")
        corr_r = reddit[["polarity","vader_compound"]].dropna().corr().iloc[0,1]
        print(f"  TextBlob-VADER r={corr_r:.3f} (Reddit)")

# 5. Figures
print(f"\n{'=' * W}")
print("5. OUTPUTS")
print("=" * W)
for f in ["multi_source_sentiment_comparison.png", "pslf_wordcloud_timecourse.png",
          "pslf_sentiment_legislative_timeline.png", "pslf_pre_post_events.png",
          "pslf_profession_timecourse.png"]:
    sz = os.path.getsize(f) / 1024 / 1024 if os.path.exists(f) else 0
    print(f"  {f}: {sz:.1f} MB")

print(f"\n  Scripts: {len([f for f in os.listdir('../scripts') if f.endswith('.py')])} Python files")
print(f"  Data: {sum(os.path.getsize(f)/1024/1024 for f in [x for x in os.listdir('.') if x.endswith('.csv')])} MB total CSV")

print(f"\n{'=' * W}")
print("6. REPOSITORY")
print("=" * W)
print(f"  Fork: https://github.com/zanecn/PSLF-Discussion-Analysis")
print(f"  PR: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis/pull/1")
print(f"  Branch: playwright-sdn-scraper")
print("=" * W)
