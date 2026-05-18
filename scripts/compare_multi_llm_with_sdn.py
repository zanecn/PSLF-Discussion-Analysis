"""
compare_multi_llm_with_sdn.py
==============================
Round 16 Strengthener 1 final analysis: re-run the multi-LLM comparison
with SDN posts NOW INCLUDED in the intersection.

Inputs:
  - zeroshot_reddit_n1000.csv          (Claude on Reddit; from prior session)
  - zeroshot_llama_replication.csv     (Llama on Reddit; from prior session)
  - zeroshot_third_llm_replication.csv (DeepSeek on Reddit; from prior session)
  - zeroshot_sdn_n1000.csv             (Claude on SDN; from prior session)
  - zeroshot_llama_sdn.csv             (Llama on SDN; Strengthener 1 NEW)
  - zeroshot_deepseek_sdn.csv          (DeepSeek on SDN; Strengthener 1 NEW)

For each cohort split (Reddit-only, SDN-only, combined), compute:
  - Pairwise r, exact-match, kappa for all 10 instrument pairs
  - 3-LLM K-α with bootstrap CI
  - 4-rater K-α with TextBlob (FIXED + qcut)
  - 4-rater K-α with VADER (FIXED + qcut)
  - All 5 K-α with bootstrap CIs

Output: paper1_multi_llm_with_sdn_results.{txt,csv}
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")

SENTIMENT_TO_ORDINAL = {
    "very_negative": 0, "negative": 1, "neutral": 2,
    "positive": 3, "very_positive": 4,
}

FIXED_THRESHOLDS = [-0.5, -0.05, 0.05, 0.5]


def bin_continuous_fixed(s):
    s = pd.to_numeric(s, errors="coerce")
    bins = [-np.inf] + FIXED_THRESHOLDS + [np.inf]
    return pd.cut(s, bins=bins, labels=[0, 1, 2, 3, 4]).astype(float)


def bin_continuous_qcut(s):
    s = pd.to_numeric(s, errors="coerce")
    return pd.qcut(s.rank(method="first"), q=5, labels=[0, 1, 2, 3, 4]).astype(float)


def krippendorff_alpha_ordinal(reliability_data):
    try:
        import krippendorff
        return krippendorff.alpha(reliability_data=reliability_data, level_of_measurement="ordinal")
    except Exception:
        return np.nan


def bootstrap_alpha(data_dict, b=2000, seed=42):
    raters = list(data_dict.keys())
    arrs = [np.asarray(data_dict[r]) for r in raters]
    n = len(arrs[0])
    point = krippendorff_alpha_ordinal([list(a) for a in arrs])
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(b):
        idx = rng.integers(0, n, n)
        sampled = [list(a[idx]) for a in arrs]
        try:
            boots.append(krippendorff_alpha_ordinal(sampled))
        except Exception:
            pass
    boots = [x for x in boots if not np.isnan(x)]
    if len(boots) < 100:
        return point, np.nan, np.nan
    return point, np.percentile(boots, 2.5), np.percentile(boots, 97.5)


def main():
    # Load Reddit Claude/Llama/DeepSeek (Round 13)
    cl_r = pd.read_csv(PROJECT / "zeroshot_reddit_n1000.csv")
    ll_r = pd.read_csv(PROJECT / "zeroshot_llama_replication.csv")
    ds_r = pd.read_csv(PROJECT / "zeroshot_third_llm_replication.csv")

    # Load SDN Claude scorings — need ALL SDN Claude sources because the
    # sdn_for_multi_llm_scoring.csv sample was drawn from the union of these
    sdn_claude_files = ["zeroshot_sdn_n1000.csv", "zeroshot_sdn_eventfull.csv",
                         "zeroshot_sdn_temp0_retest.csv", "zeroshot_sdn_forum.csv",
                         "zeroshot_sdn_temp0_retest_RUN2.csv"]
    cl_s_dfs = []
    for f in sdn_claude_files:
        p = PROJECT / f
        if p.exists():
            d = pd.read_csv(p)
            if "post_id" in d.columns and "pslf_sentiment" in d.columns:
                cl_s_dfs.append(d[["post_id", "pslf_sentiment"]])
    cl_s = pd.concat(cl_s_dfs, ignore_index=True).drop_duplicates(subset="post_id", keep="first")
    print(f"SDN Claude scorings combined: {len(cl_s)}")

    # SDN Llama and DeepSeek (Round 16 Strengthener 1)
    ll_s = pd.read_csv(PROJECT / "zeroshot_llama_sdn.csv")
    ds_s = pd.read_csv(PROJECT / "zeroshot_deepseek_sdn.csv")

    # Tag with cohort source
    cl_r["cohort_source"] = "reddit"
    ll_r["cohort_source"] = "reddit"
    ds_r["cohort_source"] = "reddit"
    cl_s["cohort_source"] = "sdn"
    ll_s["cohort_source"] = "sdn"
    ds_s["cohort_source"] = "sdn"

    # Concat Reddit + SDN per LLM
    claude = pd.concat([cl_r, cl_s], ignore_index=True)
    llama = pd.concat([ll_r, ll_s], ignore_index=True)
    deepseek = pd.concat([ds_r, ds_s], ignore_index=True)

    # Add ordinal
    for d, name in [(claude, "claude"), (llama, "llama"), (deepseek, "deepseek")]:
        d[f"{name}_ord"] = d["pslf_sentiment"].map(SENTIMENT_TO_ORDINAL)

    claude = claude[claude["claude_ord"].notna()][["post_id", "claude_ord", "cohort_source"]].copy()
    llama = llama[llama["llama_ord"].notna()][["post_id", "llama_ord"]].copy()
    deepseek = deepseek[deepseek["deepseek_ord"].notna()][["post_id", "deepseek_ord"]].copy()

    # Merge: 3-LLM intersection
    m = claude.merge(llama, on="post_id").merge(deepseek, on="post_id")
    print(f"3-LLM intersection (Reddit + SDN): n={len(m)}")
    print(f"  Reddit: {(m['cohort_source']=='reddit').sum()}")
    print(f"  SDN:    {(m['cohort_source']=='sdn').sum()}")

    # Add TB+VADER from source
    srcs = []
    for f, key in [("reddit_arctic_shift_pslf.csv", "id"),
                    ("reddit_professions_pslf.csv", "id"),
                    ("forum_pslf_discussions.csv", "post_id")]:
        p = PROJECT / f
        if p.exists():
            d = pd.read_csv(p, usecols=[key, "polarity", "vader_compound"])
            d = d.rename(columns={key: "post_id"})
            srcs.append(d)
    src = pd.concat(srcs, ignore_index=True).drop_duplicates(subset="post_id", keep="first")
    src["post_id"] = src["post_id"].astype(str)
    m["post_id"] = m["post_id"].astype(str)
    m = m.merge(src, on="post_id", how="inner")
    m = m.dropna(subset=["polarity", "vader_compound"])
    print(f"5-instrument intersection (Reddit + SDN): n={len(m)}")
    print(f"  Reddit: {(m['cohort_source']=='reddit').sum()}")
    print(f"  SDN:    {(m['cohort_source']=='sdn').sum()}")

    # Compute both binnings
    m["tb_fixed"] = bin_continuous_fixed(m["polarity"])
    m["tb_qcut"] = bin_continuous_qcut(m["polarity"])
    m["va_fixed"] = bin_continuous_fixed(m["vader_compound"])
    m["va_qcut"] = bin_continuous_qcut(m["vader_compound"])
    m = m.dropna(subset=["tb_fixed", "tb_qcut", "va_fixed", "va_qcut"]).reset_index(drop=True)
    n_total = len(m)
    n_reddit = (m["cohort_source"] == "reddit").sum()
    n_sdn = (m["cohort_source"] == "sdn").sum()

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 1 MULTI-LLM WITH SDN INCLUDED (Round 16 Strengthener 1)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append(f"5-instrument intersection: n={n_total} (Reddit={n_reddit}, SDN={n_sdn})")
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("PAIRWISE EXACT-MATCH AND PEARSON r — STRATIFIED BY COHORT")
    out_lines.append("=" * 90)
    out_lines.append("")

    pairs = [
        ("Claude × Llama (within-LLM)", "claude_ord", "llama_ord", "claude_ord", "llama_ord"),
        ("Claude × DeepSeek (within-LLM)", "claude_ord", "deepseek_ord", "claude_ord", "deepseek_ord"),
        ("Llama × DeepSeek (within-LLM)", "llama_ord", "deepseek_ord", "llama_ord", "deepseek_ord"),
        ("Claude × TextBlob", "claude_ord", "tb_fixed", "claude_ord", "tb_qcut"),
        ("Claude × VADER", "claude_ord", "va_fixed", "claude_ord", "va_qcut"),
        ("Llama × TextBlob", "llama_ord", "tb_fixed", "llama_ord", "tb_qcut"),
        ("Llama × VADER", "llama_ord", "va_fixed", "llama_ord", "va_qcut"),
        ("DeepSeek × TextBlob", "deepseek_ord", "tb_fixed", "deepseek_ord", "tb_qcut"),
        ("DeepSeek × VADER", "deepseek_ord", "va_fixed", "deepseek_ord", "va_qcut"),
        ("TextBlob × VADER (within-lex)", "tb_fixed", "va_fixed", "tb_qcut", "va_qcut"),
    ]

    for cohort_label, cohort_filter in [
        ("ALL (Reddit + SDN)", lambda d: d),
        ("Reddit only", lambda d: d[d["cohort_source"] == "reddit"]),
        ("SDN only", lambda d: d[d["cohort_source"] == "sdn"]),
    ]:
        df_c = cohort_filter(m).reset_index(drop=True)
        if len(df_c) < 30:
            continue
        out_lines.append(f"--- {cohort_label} (n={len(df_c)}) ---")
        out_lines.append(f"{'Pair':40} {'Fixed':>10} {'qcut':>10} {'Pearson r':>12}")
        out_lines.append("-" * 80)
        for name, f1, f2, q1, q2 in pairs:
            em_fixed = (df_c[f1] == df_c[f2]).mean()
            em_qcut = (df_c[q1] == df_c[q2]).mean()
            r, _ = stats.pearsonr(df_c[f1].astype(float), df_c[f2].astype(float))
            out_lines.append(f"  {name:40} {em_fixed:>9.3f}  {em_qcut:>9.3f}  {r:>+11.3f}")
        out_lines.append("")

    out_lines.append("=" * 90)
    out_lines.append("MULTI-RATER KRIPPENDORFF α WITH BOOTSTRAP 95% CI")
    out_lines.append("=" * 90)
    out_lines.append("")

    rater_combos = [
        ("3-LLM (Claude+Llama+DeepSeek)", ["claude_ord", "llama_ord", "deepseek_ord"]),
        ("3-LLM + TextBlob (FIXED)", ["claude_ord", "llama_ord", "deepseek_ord", "tb_fixed"]),
        ("3-LLM + TextBlob (QCUT)", ["claude_ord", "llama_ord", "deepseek_ord", "tb_qcut"]),
        ("3-LLM + VADER (FIXED)", ["claude_ord", "llama_ord", "deepseek_ord", "va_fixed"]),
        ("3-LLM + VADER (QCUT)", ["claude_ord", "llama_ord", "deepseek_ord", "va_qcut"]),
        ("All 5 (FIXED)", ["claude_ord", "llama_ord", "deepseek_ord", "tb_fixed", "va_fixed"]),
        ("All 5 (QCUT)", ["claude_ord", "llama_ord", "deepseek_ord", "tb_qcut", "va_qcut"]),
    ]
    for cohort_label, cohort_filter in [
        ("ALL (Reddit + SDN)", lambda d: d),
        ("Reddit only", lambda d: d[d["cohort_source"] == "reddit"]),
        ("SDN only", lambda d: d[d["cohort_source"] == "sdn"]),
    ]:
        df_c = cohort_filter(m).reset_index(drop=True)
        if len(df_c) < 30:
            continue
        out_lines.append(f"--- {cohort_label} (n={len(df_c)}) ---")
        out_lines.append(f"{'Combo':45} {'α':>8} {'95% CI':>22}")
        out_lines.append("-" * 80)
        for name, raters in rater_combos:
            data_dict = {r: df_c[r].astype(float).values for r in raters}
            point, lo, hi = bootstrap_alpha(data_dict, b=2000)
            ci_str = f"[{lo:+.4f}, {hi:+.4f}]" if not np.isnan(lo) else "(boot fail)"
            out_lines.append(f"  {name:45} {point:>+8.4f} {ci_str:>22}")
        out_lines.append("")

    out_text = "\n".join(out_lines)
    print(out_text)
    out_path = PROJECT / "paper1_multi_llm_with_sdn_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
