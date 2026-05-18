"""
compare_openweight_vs_claude.py
=================================
After running sentiment_zeroshot_openweight.py, compare LLM cross-scoring
to Claude scoring to validate the construct mismatch finding generalizes
beyond Claude (closes the "just one LLM" critique).

Output: openweight_vs_claude_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats

OUT_TXT = "openweight_vs_claude_results.txt"
OUT_CSV = "openweight_vs_claude_results.csv"
OUT_PNG = "openweight_vs_claude_results.png"


def krippendorff_alpha_ordinal(df_long, sentiment_order):
    """Compute Krippendorff's alpha for ordinal data via cross-tab variance."""
    # df_long has columns: post_id, scorer, sentiment_int
    pivot = df_long.pivot_table(index="post_id", columns="scorer",
                                  values="sentiment_int", aggfunc="first")
    pivot = pivot.dropna()
    n_posts = len(pivot)
    if n_posts < 30: return float("nan"), 0
    # Compute observed vs expected disagreement
    scorers = list(pivot.columns)
    n_pairs = 0
    obs_disagreement = 0
    for i, s1 in enumerate(scorers):
        for s2 in scorers[i+1:]:
            d = abs(pivot[s1] - pivot[s2]).pow(2).sum()
            obs_disagreement += d
            n_pairs += 1
    obs = obs_disagreement / (n_pairs * n_posts)
    # Expected: pool all values
    all_vals = pd.concat([pivot[s] for s in scorers])
    n = len(all_vals)
    expected = (all_vals.var(ddof=0) * 2 * n / (n - 1)) if n > 1 else 1
    if expected == 0: return float("nan"), n_posts
    alpha = 1 - (obs / expected)
    return float(alpha), n_posts


def main():
    print("=" * 80)
    print("Open-weight LLM vs Claude — construct mismatch generalization test")
    print("=" * 80)

    # Find open-weight result file
    candidates = ["zeroshot_together_replication.csv",
                   "zeroshot_openai_replication.csv"]
    ow_file = None
    for c in candidates:
        if os.path.exists(c):
            ow_file = c; break
    if not ow_file:
        print("[ABORT] No open-weight scoring result found.")
        print("        Expected: zeroshot_together_replication.csv OR zeroshot_openai_replication.csv")
        print()
        print("        To generate, run:")
        print("        python ../scripts/sentiment_zeroshot_openweight.py --provider together")
        print("        (after setting TOGETHER_API_KEY env var)")
        sys.exit(1)

    print(f"\nLoading open-weight scoring: {ow_file}")
    ow = pd.read_csv(ow_file)
    ow = ow[ow["pslf_sentiment"] != "parse_error"].copy()
    print(f"  {len(ow):,} valid open-weight scorings")

    # Load Claude scoring
    print("\nLoading Claude scoring: zeroshot_reddit_n1000.csv")
    cl = pd.read_csv("zeroshot_reddit_n1000.csv")
    cl = cl[~cl["pslf_sentiment"].isin(["parse_error", "api_error"])].copy()
    print(f"  {len(cl):,} valid Claude scorings")

    # Load TextBlob + VADER from source
    print("\nLoading TextBlob/VADER from source corpus...")
    tb_vader_frames = []
    for f in ["reddit_professions_pslf.csv", "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f): continue
        try:
            d = pd.read_csv(f, usecols=lambda c: c in
                             ("id", "polarity", "vader_compound"))
            d = d.rename(columns={"id": "post_id"})
            tb_vader_frames.append(d)
        except: continue
    tb_vader = pd.concat(tb_vader_frames, ignore_index=True).drop_duplicates("post_id")
    tb_vader["post_id"] = tb_vader["post_id"].astype(str)
    print(f"  TextBlob+VADER from {len(tb_vader):,} posts")

    # Merge all four scorers
    cl["post_id"] = cl["post_id"].astype(str)
    ow["post_id"] = ow["post_id"].astype(str)
    df = (ow[["post_id", "pslf_sentiment", "primary_topic", "pslf_stance"]]
            .rename(columns={"pslf_sentiment": "ow_sentiment",
                              "primary_topic": "ow_topic",
                              "pslf_stance": "ow_stance"})
            .merge(cl[["post_id", "pslf_sentiment", "primary_topic", "pslf_stance"]]
                    .rename(columns={"pslf_sentiment": "cl_sentiment",
                                      "primary_topic": "cl_topic",
                                      "pslf_stance": "cl_stance"}),
                    on="post_id", how="inner")
            .merge(tb_vader, on="post_id", how="left"))
    print(f"\nFour-scorer intersection: {len(df):,} posts")

    # Map sentiment to ordinal
    sentiment_order = ["very_negative", "negative", "neutral", "positive", "very_positive"]
    sentiment_map = {s: i for i, s in enumerate(sentiment_order)}
    df["ow_sent_int"] = df["ow_sentiment"].map(sentiment_map)
    df["cl_sent_int"] = df["cl_sentiment"].map(sentiment_map)
    # TB/VADER discretization: percentile-matched to Claude marginals for fair compare
    if "polarity" in df.columns:
        # Match marginals: assign to quintiles
        df["tb_sent_int"] = pd.qcut(df["polarity"].rank(method="first"), q=5,
                                       labels=range(5), duplicates="drop").astype(float)
    if "vader_compound" in df.columns:
        df["va_sent_int"] = pd.qcut(df["vader_compound"].rank(method="first"), q=5,
                                       labels=range(5), duplicates="drop").astype(float)

    # === Pairwise agreement ===
    print("\n[1] Pairwise sentiment agreement (Pearson + exact match + Cohen's kappa)")
    pairs = [
        ("Claude", "ow_sent_int", "cl_sent_int", "Claude vs Open-weight LLM"),
        ("Claude", "tb_sent_int", "cl_sent_int", "Claude vs TextBlob"),
        ("Claude", "va_sent_int", "cl_sent_int", "Claude vs VADER"),
        ("OW", "tb_sent_int", "ow_sent_int", "Open-weight LLM vs TextBlob"),
        ("OW", "va_sent_int", "ow_sent_int", "Open-weight LLM vs VADER"),
        ("TB-VADER", "tb_sent_int", "va_sent_int", "TextBlob vs VADER"),
    ]
    rows = []
    for ref, a, b, label in pairs:
        if a not in df.columns or b not in df.columns: continue
        sub = df[[a, b]].dropna()
        if len(sub) < 30: continue
        r, p = stats.pearsonr(sub[a], sub[b])
        exact = (sub[a] == sub[b]).mean()
        try:
            from sklearn.metrics import cohen_kappa_score
            kappa = cohen_kappa_score(sub[a].astype(int), sub[b].astype(int))
        except: kappa = float("nan")
        rows.append({"comparison": label, "n": len(sub),
                      "pearson_r": r, "exact_match": exact, "cohens_kappa": kappa,
                      "p": p})
        print(f"  {label:<32s} n={len(sub):,} r={r:+.3f}, exact={exact:.3f}, "
               f"kappa={kappa:+.3f}")

    # === Three-rater Krippendorff alpha (Claude + OW + each lexical) ===
    print("\n[2] Three-rater Krippendorff alpha tests")
    # Build long-form for each three-rater combination
    three_rater_results = []
    for combo in [
        ("Claude+OW+TB", ["cl_sent_int", "ow_sent_int", "tb_sent_int"]),
        ("Claude+OW+VADER", ["cl_sent_int", "ow_sent_int", "va_sent_int"]),
        ("Claude+OW", ["cl_sent_int", "ow_sent_int"]),
    ]:
        cols = combo[1]
        if not all(c in df.columns for c in cols): continue
        long = pd.concat([
            df[["post_id", c]].rename(columns={c: "sentiment_int"}).assign(scorer=c)
            for c in cols
        ], ignore_index=True).dropna()
        alpha, n = krippendorff_alpha_ordinal(long, sentiment_order)
        three_rater_results.append({"combo": combo[0], "n_posts": n, "alpha": alpha})
        print(f"  {combo[0]}: alpha = {alpha:+.4f}, n = {n:,}")

    # === KEY TEST: does open-weight LLM agree with Claude on stance? ===
    print("\n[3] Open-weight LLM vs Claude on STANCE (the most divergent dimension)")
    df_stance = df.dropna(subset=["ow_stance", "cl_stance"])
    df_stance = df_stance[~df_stance["ow_stance"].isin(["unknown"])]
    df_stance = df_stance[~df_stance["cl_stance"].isin(["unknown"])]
    if len(df_stance) > 0:
        agreement = (df_stance["ow_stance"] == df_stance["cl_stance"]).mean()
        print(f"  Stance exact-match Claude vs OW: {agreement*100:.1f}% (n={len(df_stance):,})")
        # Per-stance agreement
        for s in ["pursuing", "considering", "rejecting", "completed"]:
            cl_s = df_stance[df_stance["cl_stance"] == s]
            if len(cl_s) > 0:
                ow_s = (cl_s["ow_stance"] == s).mean()
                print(f"  Claude says {s:<14s}: OW agrees on {ow_s*100:.1f}% (n={len(cl_s):,})")

    # === Save ===
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("OPEN-WEIGHT LLM vs CLAUDE — CONSTRUCT MISMATCH GENERALIZATION\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Open-weight LLM scoring source: {ow_file}\n")
        f.write(f"Four-scorer intersection: {len(df):,} posts\n\n")

        f.write("PAIRWISE SENTIMENT AGREEMENT\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Comparison':<32s} {'n':>6s} {'r':>7s} {'exact':>7s} {'kappa':>7s}\n")
        for r in rows:
            f.write(f"{r['comparison']:<32s} {r['n']:>6,} {r['pearson_r']:>+7.3f} "
                    f"{r['exact_match']:>6.3f} {r['cohens_kappa']:>+7.3f}\n")

        f.write("\nTHREE-RATER KRIPPENDORFF ALPHA\n")
        f.write("-" * 80 + "\n")
        for r in three_rater_results:
            f.write(f"  {r['combo']}: alpha = {r['alpha']:+.4f}, n = {r['n_posts']:,}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        # Find Claude vs OW agreement
        cl_ow_row = next((r for r in rows if "Claude vs Open-weight" in r["comparison"]), None)
        cl_tb_row = next((r for r in rows if "Claude vs TextBlob" in r["comparison"]), None)
        cl_va_row = next((r for r in rows if "Claude vs VADER" in r["comparison"]), None)
        if cl_ow_row and cl_tb_row:
            f.write(f"Inter-LLM agreement (Claude vs OW): r={cl_ow_row['pearson_r']:+.3f}, "
                    f"exact={cl_ow_row['exact_match']*100:.1f}%\n")
            f.write(f"Claude vs TextBlob (lexical):       r={cl_tb_row['pearson_r']:+.3f}, "
                    f"exact={cl_tb_row['exact_match']*100:.1f}%\n")
            if cl_va_row:
                f.write(f"Claude vs VADER (arousal):          r={cl_va_row['pearson_r']:+.3f}, "
                        f"exact={cl_va_row['exact_match']*100:.1f}%\n")
            f.write("\n")
            if cl_ow_row['pearson_r'] > 0.6 and cl_tb_row['pearson_r'] < 0.3:
                f.write("VERDICT: Open-weight LLM AGREES with Claude (high r), but DISAGREES with\n")
                f.write("TextBlob/VADER (low r). The construct mismatch is THUS LLM-vs-lexical,\n")
                f.write("NOT Claude-specific. The methods finding is generalizable.\n")
            elif cl_ow_row['pearson_r'] < 0.3:
                f.write("VERDICT: Open-weight LLM DISAGREES with Claude even at LLM-vs-LLM level.\n")
                f.write("This complicates the methods finding — instrument disagreement extends\n")
                f.write("to LLM-vs-LLM, not just LLM-vs-lexical. Worth investigating.\n")
            else:
                f.write("VERDICT: Mixed result — see detailed analysis.\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")


if __name__ == "__main__":
    main()
