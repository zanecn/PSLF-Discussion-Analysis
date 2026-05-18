"""
P1 R17++ #6 EXTENSION (high-yield mechanism investigation):

Why do TextBlob and VADER systematically disagree on OP-vs-Reply directional
contrasts across 8/8 cohorts? Per agent review, this is the highest-impact
reviewer critique to close. The hypothesis space:
  H1: OPs use more emotionally-loaded first-person language (helps VADER)
  H2: VADER weights punctuation + capitalization heavily; OPs have more
  H3: TextBlob is closer to bag-of-words; replies have more positive content
      words while OPs carry emotional energy VADER catches
  H4: Some combination of above

This script:
  1. Loads OPs + comments with raw text
  2. Computes linguistic features per OP and per comment:
     - Word count
     - Character count
     - Exclamation marks (per 100 words)
     - Question marks (per 100 words)
     - All-caps words (per 100 words; VADER-favored)
     - First-person pronouns (I, me, my, mine, myself) per 100 words
     - Negation words (not, never, no, n't) per 100 words
     - Intensifier words (very, really, so, extremely, totally) per 100 words
     - URLs (per 100 words; sentiment scorers often handle URLs poorly)
  3. Per-cohort + overall, compute OP vs reply means + differences
  4. Correlate feature differences with per-cohort TB and VADER Δ
  5. Identify which features most explain the directional split

Output: paper1_op_vs_reply_feature_mechanism_results.txt
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd
from scipy import stats

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")

# Cohort mapping (mirrors analyze_op_vs_reply.py)
PROF_TO_COHORT = {
    "physician": "Reddit Medical", "medical_student": "Reddit Medical",
    "resident": "Reddit Medical", "premed": "Reddit Medical",
    "lawyer": "Reddit Finance", "finance": "Reddit Finance",
    "accountant": "Reddit Finance",
    "teacher": "Reddit Teaching", "education": "Reddit Teaching",
    "nurse": "Reddit Nursing", "nursing_student": "Reddit Nursing",
    "physician_assistant": "Reddit PA", "pa_student": "Reddit PA",
}

# Feature regex patterns
FIRST_PERSON_RE = re.compile(r"\b(i|me|my|mine|myself)\b", re.IGNORECASE)
NEGATION_RE = re.compile(r"\b(not|never|no|nothing|nobody|none|n't)\b", re.IGNORECASE)
INTENSIFIER_RE = re.compile(r"\b(very|really|so|extremely|totally|absolutely|completely|incredibly|definitely)\b", re.IGNORECASE)
URL_RE = re.compile(r"https?://\S+|www\.\S+")
ALLCAPS_RE = re.compile(r"\b[A-Z]{2,}\b")  # 2+ uppercase letters in a row (whole word)


def compute_features(text: str) -> dict:
    """Compute linguistic features for a single text."""
    if not isinstance(text, str) or not text.strip():
        return {
            "n_words": 0, "n_chars": 0,
            "excl_per100": np.nan, "quest_per100": np.nan,
            "allcaps_per100": np.nan, "firstperson_per100": np.nan,
            "negation_per100": np.nan, "intensifier_per100": np.nan,
            "urls_per100": np.nan,
        }
    n_chars = len(text)
    words = text.split()
    n_words = len(words)
    if n_words == 0:
        return {
            "n_words": 0, "n_chars": n_chars,
            "excl_per100": np.nan, "quest_per100": np.nan,
            "allcaps_per100": np.nan, "firstperson_per100": np.nan,
            "negation_per100": np.nan, "intensifier_per100": np.nan,
            "urls_per100": np.nan,
        }
    n_excl = text.count("!")
    n_quest = text.count("?")
    n_allcaps = len(ALLCAPS_RE.findall(text))
    n_first = len(FIRST_PERSON_RE.findall(text))
    n_neg = len(NEGATION_RE.findall(text))
    n_int = len(INTENSIFIER_RE.findall(text))
    n_url = len(URL_RE.findall(text))
    per100 = 100.0 / n_words
    return {
        "n_words": n_words,
        "n_chars": n_chars,
        "excl_per100": n_excl * per100,
        "quest_per100": n_quest * per100,
        "allcaps_per100": n_allcaps * per100,
        "firstperson_per100": n_first * per100,
        "negation_per100": n_neg * per100,
        "intensifier_per100": n_int * per100,
        "urls_per100": n_url * per100,
    }


# === LOAD OPs ===
print("Loading OPs from 4 sources (aligned with analyze_op_vs_reply.py)...")
op_frames = []
for f in ["reddit_professions_pslf.csv",
          "comprehensive_medical_pslf_discussions.csv",
          "comprehensive_teacher_pslf_discussions.csv",
          "reddit_arctic_shift_pslf.csv"]:
    path = PROJECT / f
    if not path.exists():
        continue
    d = pd.read_csv(path, low_memory=False)
    id_col = "post_id" if "post_id" in d.columns else "id"
    if id_col not in d.columns:
        continue
    if id_col != "post_id":
        d = d.rename(columns={id_col: "post_id"})
    # OP text: prefer 'selftext' if available; fall back to 'title' + 'body' if present
    if "selftext" in d.columns:
        d["op_text"] = d["selftext"].fillna("").astype(str)
    elif "body" in d.columns:
        d["op_text"] = d["body"].fillna("").astype(str)
    elif "text" in d.columns:
        d["op_text"] = d["text"].fillna("").astype(str)
    else:
        continue
    if "title" in d.columns:
        d["op_text"] = d["title"].fillna("").astype(str) + " " + d["op_text"]
    if "polarity" not in d.columns:
        continue
    if "profession" not in d.columns:
        d["profession"] = ""
    if "subreddit" not in d.columns:
        d["subreddit"] = ""
    if "word_count" not in d.columns:
        d["word_count"] = d["op_text"].str.split().str.len()
    op_frames.append(d[["post_id", "polarity", "op_text", "profession", "subreddit", "word_count"]])
    print(f"  Loaded {f}: {len(d):,} rows")

ops = pd.concat(op_frames, ignore_index=True).drop_duplicates("post_id")
ops["post_id"] = ops["post_id"].astype(str)
ops = ops.dropna(subset=["polarity"])
ops = ops[ops["word_count"].fillna(0) >= 20]
ops["cohort"] = ops["profession"].map(PROF_TO_COHORT)
sub_to_cohort = {"PSLF": "Reddit r/PSLF", "StudentLoans": "Reddit r/StudentLoans", "personalfinance": "Reddit Finance"}
sub_cohort = ops["subreddit"].map(sub_to_cohort)
ops["cohort"] = ops["cohort"].fillna(sub_cohort).fillna("Other")
print(f"  Total unique OPs (wc>=20): {len(ops):,}")

# === LOAD COMMENTS ===
print("Loading comments from reddit_comments_pslf.csv...")
cm_path = PROJECT / "reddit_comments_pslf.csv"
cm = pd.read_csv(cm_path, low_memory=False)
cm["post_id"] = cm["post_id"].astype(str)
cm = cm[cm["polarity"].notna()]
cm = cm[cm["word_count"].fillna(0) >= 5]
print(f"  Loaded comments: {len(cm):,}")

# === COMPUTE FEATURES (OPs and comments) ===
print("\nComputing features for OPs...")
op_features = []
for i, row in ops.iterrows():
    feat = compute_features(row["op_text"])
    feat["post_id"] = row["post_id"]
    feat["cohort"] = row["cohort"]
    op_features.append(feat)
    if (i + 1) % 20000 == 0:
        print(f"  OPs processed: {i+1:,}")
op_feat_df = pd.DataFrame(op_features)
print(f"  Done: {len(op_feat_df):,} OP feature rows")

print("\nComputing features for comments (~520K)...")
# Process in chunks for speed; for each comment compute features
cm_features = []
for i, (_, row) in enumerate(cm.iterrows()):
    feat = compute_features(row.get("body", ""))
    feat["post_id"] = row["post_id"]
    cm_features.append(feat)
    if (i + 1) % 100000 == 0:
        print(f"  Comments processed: {i+1:,}")
cm_feat_df = pd.DataFrame(cm_features)
print(f"  Done: {len(cm_feat_df):,} comment feature rows")

# Aggregate comments per post (mean features over all comments per post)
print("\nAggregating comment features per post...")
FEATURES = ["n_words", "n_chars", "excl_per100", "quest_per100", "allcaps_per100",
            "firstperson_per100", "negation_per100", "intensifier_per100", "urls_per100"]
cm_agg = cm_feat_df.groupby("post_id")[FEATURES].mean().reset_index()
cm_agg = cm_agg.rename(columns={f: f"cmt_{f}" for f in FEATURES})

# Merge OP features with comment features
merged = op_feat_df.merge(cm_agg, on="post_id", how="inner")
print(f"  Merged: {len(merged):,} post-rows with both OP + comment features")

# Per-post deltas
for f in FEATURES:
    merged[f"delta_{f}"] = merged[f] - merged[f"cmt_{f}"]

# === SUMMARY: per-cohort feature means + deltas ===
print("\n" + "=" * 90)
print("PER-COHORT FEATURE COMPARISON: OP vs Comment means + Δ (OP − Comment)")
print("=" * 90)

cohorts_ordered = merged["cohort"].value_counts().head(10).index.tolist()

out_lines = []
out_lines.append("=" * 100)
out_lines.append("PAPER 1 OP-VS-REPLY FEATURE MECHANISM INVESTIGATION")
out_lines.append("(R17++ #6 EXTENSION — explains WHY TB and VADER systematically disagree on OP-vs-Reply)")
out_lines.append("=" * 100)
out_lines.append("")
out_lines.append(f"Sample: n={len(merged):,} posts with both OP + comment features")
out_lines.append("Features computed per OP and per comment (mean per post):")
out_lines.append("  - word count, char count")
out_lines.append("  - exclamation marks per 100 words (VADER-favored signal)")
out_lines.append("  - question marks per 100 words")
out_lines.append("  - all-caps words per 100 words (VADER amplifies caps)")
out_lines.append("  - first-person pronouns per 100 words (I, me, my, mine, myself)")
out_lines.append("  - negation words per 100 words (not, never, no, n't, etc.)")
out_lines.append("  - intensifier words per 100 words (very, really, so, extremely, etc.)")
out_lines.append("  - URLs per 100 words")
out_lines.append("")

for cohort in cohorts_ordered:
    sub = merged[merged["cohort"] == cohort]
    n = len(sub)
    if n < 50:
        continue
    out_lines.append(f"--- Cohort: {cohort} (n={n:,}) ---")
    out_lines.append(f"  {'feature':25s} {'OP_mean':>10s}  {'cmt_mean':>10s}  {'Δ (OP-cmt)':>12s}  {'t-stat':>8s}  {'p-value':>10s}")
    for f in ["n_words", "excl_per100", "quest_per100", "allcaps_per100",
              "firstperson_per100", "negation_per100", "intensifier_per100", "urls_per100"]:
        op_vals = sub[f].dropna()
        cmt_vals = sub[f"cmt_{f}"].dropna()
        delta = sub[f"delta_{f}"].dropna()
        if len(delta) < 10:
            continue
        op_mean = op_vals.mean()
        cmt_mean = cmt_vals.mean()
        delta_mean = delta.mean()
        t, p = stats.ttest_1samp(delta, 0)
        out_lines.append(f"  {f:25s} {op_mean:>10.3f}  {cmt_mean:>10.3f}  {delta_mean:>+12.3f}  {t:>+8.2f}  {p:>10.2e}")
    out_lines.append("")

# === MECHANISM HYPOTHESIS TEST: which feature differences correlate with TB / VADER Δ? ===
# Per-cohort: compute (1) cohort-mean feature deltas, (2) cohort-mean TB Δ + VADER Δ
# Then correlate feature-Δ with TB Δ and VADER Δ across cohorts.

# Get per-cohort TB + VADER Δ from already-loaded ops/cm (need to merge with comment polarity)
print("\nComputing per-cohort TB + VADER Δ to correlate with feature deltas...")
cm_polarity = cm[["post_id", "polarity"]].copy()
# Need VADER for cm too — try to load _with_vader file
cm_v_path = PROJECT / "reddit_comments_pslf_with_vader.csv"
if cm_v_path.exists():
    cm_v = pd.read_csv(cm_v_path, low_memory=False, usecols=["post_id", "vader_compound"])
    cm_v["post_id"] = cm_v["post_id"].astype(str)
    cm_polarity = cm_polarity.merge(cm_v, on="post_id", how="left")
else:
    cm_polarity["vader_compound"] = np.nan

cm_pol_agg = cm_polarity.groupby("post_id").agg(
    cmt_polarity=("polarity", "mean"),
    cmt_vader=("vader_compound", "mean"),
).reset_index()

ops_pol = ops[["post_id", "polarity", "cohort"]].copy()
ops_pol["op_polarity"] = ops_pol["polarity"]
ops_pol = ops_pol.drop("polarity", axis=1)
# Add VADER from arctic shift if available
ops_arctic_path = PROJECT / "reddit_arctic_shift_pslf.csv"
if ops_arctic_path.exists():
    arctic_v = pd.read_csv(ops_arctic_path, low_memory=False, usecols=["id", "vader_compound"]).rename(columns={"id": "post_id"})
    arctic_v["post_id"] = arctic_v["post_id"].astype(str)
    ops_pol = ops_pol.merge(arctic_v, on="post_id", how="left").rename(columns={"vader_compound": "op_vader"})

del_df = ops_pol.merge(cm_pol_agg, on="post_id", how="inner")
del_df["delta_pol"] = del_df["op_polarity"] - del_df["cmt_polarity"]
del_df["delta_vader"] = del_df["op_vader"] - del_df["cmt_vader"]

# Per-cohort TB + VADER Δ
cohort_sentiment = del_df.groupby("cohort").agg(
    n=("post_id", "count"),
    tb_delta=("delta_pol", "mean"),
    vader_delta=("delta_vader", "mean"),
).reset_index()
print(cohort_sentiment.to_string(index=False))

# Per-cohort feature deltas
feature_deltas_per_cohort = merged.groupby("cohort").agg({
    f"delta_{f}": "mean" for f in ["excl_per100", "quest_per100", "allcaps_per100",
                                     "firstperson_per100", "negation_per100",
                                     "intensifier_per100", "urls_per100", "n_words"]
}).reset_index()

# Merge with sentiment deltas
analysis = cohort_sentiment.merge(feature_deltas_per_cohort, on="cohort")
analysis = analysis[analysis["n"] >= 30]
out_lines.append("=" * 100)
out_lines.append("MECHANISM HYPOTHESIS: cross-cohort correlation between feature Δ and TB / VADER Δ")
out_lines.append("=" * 100)
out_lines.append("")
out_lines.append("If TB consistently sees replies as MORE positive (TB Δ < 0) because replies have more positive content words,")
out_lines.append("then features that drive TextBlob (word count, simple word polarity) should NOT correlate with TB Δ across cohorts.")
out_lines.append("If VADER consistently sees OPs as MORE positive (VADER Δ > 0) because OPs have more VADER-favored signals,")
out_lines.append("then exclamation/caps/first-person/intensifier features should POSITIVELY correlate with VADER Δ.")
out_lines.append("")
out_lines.append("Per-cohort Δ values (mean of OP - mean of comments):")
out_lines.append(f"{'cohort':30s} {'n':>6s}  {'TB Δ':>10s}  {'VADER Δ':>10s}")
for _, r in analysis.iterrows():
    out_lines.append(f"  {r['cohort']:30s} {int(r['n']):>6,d}  {r['tb_delta']:>+10.4f}  {r['vader_delta']:>+10.4f}")
out_lines.append("")

if len(analysis) >= 3:
    # Pearson correlation of each feature Δ with TB Δ and VADER Δ across cohorts
    out_lines.append("Cross-cohort correlations (feature Δ vs TB Δ + VADER Δ):")
    out_lines.append(f"  {'feature':30s} {'r(TB Δ)':>10s}  {'r(VADER Δ)':>10s}")
    out_lines.append("  " + "-" * 55)
    for f in ["excl_per100", "quest_per100", "allcaps_per100",
              "firstperson_per100", "negation_per100", "intensifier_per100",
              "urls_per100", "n_words"]:
        col = f"delta_{f}"
        x = analysis[col].values
        if np.isnan(x).any() or len(x) < 3:
            continue
        r_tb, _ = stats.pearsonr(x, analysis["tb_delta"].values)
        r_va, _ = stats.pearsonr(x, analysis["vader_delta"].values)
        out_lines.append(f"  {f:30s} {r_tb:>+10.3f}  {r_va:>+10.3f}")

# Per-post: regress per-post TB Δ + VADER Δ on per-post feature Δ
out_lines.append("")
out_lines.append("=" * 100)
out_lines.append("PER-POST MULTIVARIATE EXPLANATION: feature Δs as predictors of sentiment Δ (linear regression)")
out_lines.append("=" * 100)
out_lines.append("")
reg = merged.merge(del_df[["post_id", "delta_pol", "delta_vader"]], on="post_id", how="inner")
reg = reg.dropna(subset=["delta_pol", "delta_vader"])
print(f"\nMultivariate regression sample: n={len(reg):,}")

# Build feature delta matrix
feature_delta_cols = ["delta_excl_per100", "delta_quest_per100", "delta_allcaps_per100",
                      "delta_firstperson_per100", "delta_negation_per100",
                      "delta_intensifier_per100", "delta_urls_per100", "delta_n_words"]
reg2 = reg.dropna(subset=feature_delta_cols)
X = reg2[feature_delta_cols].values
y_tb = reg2["delta_pol"].values
y_va = reg2["delta_vader"].values
# Add intercept
X1 = np.column_stack([np.ones(len(X)), X])

# Standardize predictors for comparable coefficients
Xz = (X - X.mean(axis=0)) / X.std(axis=0)
X1z = np.column_stack([np.ones(len(Xz)), Xz])

# OLS via lstsq
beta_tb, *_ = np.linalg.lstsq(X1z, y_tb, rcond=None)
beta_va, *_ = np.linalg.lstsq(X1z, y_va, rcond=None)

# Compute R²
yhat_tb = X1z @ beta_tb
yhat_va = X1z @ beta_va
r2_tb = 1 - ((y_tb - yhat_tb)**2).sum() / ((y_tb - y_tb.mean())**2).sum()
r2_va = 1 - ((y_va - yhat_va)**2).sum() / ((y_va - y_va.mean())**2).sum()

out_lines.append(f"Sample for regression: n={len(reg2):,} posts with all feature Δs non-missing")
out_lines.append(f"Predictors: 8 feature Δs (z-standardized)")
out_lines.append(f"Outcomes: TB Δ (delta_pol), VADER Δ (delta_vader)")
out_lines.append("")
out_lines.append(f"{'predictor (z-scored)':30s} {'β (TB Δ)':>12s}  {'β (VADER Δ)':>15s}")
out_lines.append("-" * 60)
out_lines.append(f"{'intercept':30s} {beta_tb[0]:>+12.5f}  {beta_va[0]:>+15.5f}")
for i, fname in enumerate(feature_delta_cols):
    out_lines.append(f"{fname:30s} {beta_tb[i+1]:>+12.5f}  {beta_va[i+1]:>+15.5f}")
out_lines.append(f"\nR² (TB Δ):    {r2_tb:.4f}")
out_lines.append(f"R² (VADER Δ): {r2_va:.4f}")

out_lines.append("")
out_lines.append("=" * 100)
out_lines.append("MECHANISM INTERPRETATION")
out_lines.append("=" * 100)
out_lines.append("")

# Identify largest-magnitude standardized coefs
tb_largest = sorted(enumerate(beta_tb[1:]), key=lambda x: abs(x[1]), reverse=True)[:3]
va_largest = sorted(enumerate(beta_va[1:]), key=lambda x: abs(x[1]), reverse=True)[:3]
out_lines.append("Top 3 predictors of TB Δ (by |β|, z-standardized):")
for idx, b in tb_largest:
    out_lines.append(f"  {feature_delta_cols[idx]:30s} β = {b:+.5f}")
out_lines.append("")
out_lines.append("Top 3 predictors of VADER Δ (by |β|, z-standardized):")
for idx, b in va_largest:
    out_lines.append(f"  {feature_delta_cols[idx]:30s} β = {b:+.5f}")
out_lines.append("")
out_lines.append("Interpretation:")
out_lines.append("  - If 'delta_excl_per100' or 'delta_allcaps_per100' has large +β for VADER but ~0 for TB,")
out_lines.append("    that supports H2 (VADER weights punctuation + caps; OPs have more).")
out_lines.append("  - If 'delta_firstperson_per100' has large +β for VADER, supports H1.")
out_lines.append("  - If 'delta_negation_per100' has large effect, suggests OP/reply differ in negation density.")
out_lines.append("  - If multiple features have small β and R² is low (<0.05), the directional split is NOT")
out_lines.append("    explained by these surface features — it's deeper instrument-property difference.")

out_text = "\n".join(out_lines)
out_path = PROJECT / "paper1_op_vs_reply_feature_mechanism_results.txt"
out_path.write_text(out_text, encoding="utf-8")
print(out_text[-3000:])  # print last part
print(f"\nSaved: {out_path}")
