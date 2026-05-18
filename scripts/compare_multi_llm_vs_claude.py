"""
compare_multi_llm_vs_claude.py
================================
Compares Claude + Llama + (3rd LLM) scoring against TextBlob + VADER on the
same posts. Strengthens the methods paper finding by demonstrating that LLM-
class agreement holds across THREE independent organizations.

Inputs (auto-detected):
  - zeroshot_reddit_n1000.csv (Claude)
  - zeroshot_llama_replication.csv OR zeroshot_together_replication.csv (Llama)
  - zeroshot_third_llm_replication.csv (3rd LLM — REQUIRED for full 3-LLM analysis)

Outputs:
  - multi_llm_comparison_results.{txt,csv,png}
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_TXT = "multi_llm_comparison_results.txt"
OUT_CSV = "multi_llm_comparison_results.csv"
OUT_PNG = "multi_llm_comparison_results.png"


def krippendorff_alpha_ordinal(df_long):
    """Compute Krippendorff's alpha for ordinal data via cross-tab variance."""
    pivot = df_long.pivot_table(index="post_id", columns="scorer",
                                  values="sentiment_int", aggfunc="first")
    pivot = pivot.dropna()
    n_posts = len(pivot)
    if n_posts < 30: return float("nan"), 0
    scorers = list(pivot.columns)
    n_pairs = 0
    obs_disagreement = 0
    for i, s1 in enumerate(scorers):
        for s2 in scorers[i+1:]:
            d = abs(pivot[s1] - pivot[s2]).pow(2).sum()
            obs_disagreement += d
            n_pairs += 1
    obs = obs_disagreement / (n_pairs * n_posts)
    all_vals = pd.concat([pivot[s] for s in scorers])
    n = len(all_vals)
    expected = (all_vals.var(ddof=0) * 2 * n / (n - 1)) if n > 1 else 1
    if expected == 0: return float("nan"), n_posts
    alpha = 1 - (obs / expected)
    return float(alpha), n_posts


def main():
    print("=" * 80)
    print("Multi-LLM (Claude + Llama + 3rd) vs Lexical Construct Mismatch Test")
    print("=" * 80)

    # === Load Claude (required) ===
    print("\n[1] Loading Claude scoring (zeroshot_reddit_n1000.csv)")
    cl = pd.read_csv("zeroshot_reddit_n1000.csv")
    cl = cl[~cl["pslf_sentiment"].isin(["parse_error","api_error",""])].copy()
    cl["post_id"] = cl["post_id"].astype(str)
    print(f"  {len(cl):,} valid Claude scorings")

    # === Load Llama (required) ===
    llama_files = ["zeroshot_llama_replication.csv", "zeroshot_together_replication.csv"]
    llama_file = None
    for f in llama_files:
        if os.path.exists(f):
            llama_file = f
            break
    if not llama_file:
        print("[ABORT] No Llama scoring found. Run sentiment_zeroshot_openweight.py first.")
        sys.exit(1)
    print(f"\n[2] Loading Llama scoring ({llama_file})")
    ll = pd.read_csv(llama_file)
    ll = ll[~ll["pslf_sentiment"].isin(["parse_error",""])].copy()
    ll["post_id"] = ll["post_id"].astype(str)
    print(f"  {len(ll):,} valid Llama scorings")

    # === Load 3rd LLM if available ===
    third_files = ["zeroshot_third_llm_replication.csv",
                    "zeroshot_mistral_replication.csv",
                    "zeroshot_deepseek_replication.csv",
                    "zeroshot_nemotron_replication.csv",
                    "zeroshot_qwen_replication.csv"]
    third_file = None
    for f in third_files:
        if os.path.exists(f):
            third_file = f
            break
    if third_file:
        print(f"\n[3] Loading 3rd LLM scoring ({third_file})")
        th = pd.read_csv(third_file)
        th = th[~th["pslf_sentiment"].isin(["parse_error",""])].copy()
        th["post_id"] = th["post_id"].astype(str)
        third_label = third_file.replace("zeroshot_","").replace("_replication.csv","").replace("_"," ").title()
        print(f"  {len(th):,} valid {third_label} scorings")
    else:
        print("\n[3] No 3rd LLM scoring found; running 2-LLM analysis only.")
        th = None
        third_label = None

    # === Load TextBlob + VADER ===
    print("\n[4] Loading TextBlob + VADER from source corpus...")
    tb_va_frames = []
    for f in ["reddit_professions_pslf.csv", "reddit_arctic_shift_pslf.csv"]:
        if not os.path.exists(f): continue
        try:
            d = pd.read_csv(f, usecols=lambda c: c in ("id","polarity","vader_compound"))
            d = d.rename(columns={"id":"post_id"})
            d["post_id"] = d["post_id"].astype(str)
            tb_va_frames.append(d)
        except: continue
    tb_va = pd.concat(tb_va_frames, ignore_index=True).drop_duplicates("post_id")
    print(f"  {len(tb_va):,} posts with TextBlob+VADER")

    # === Build merged DataFrame ===
    df = cl[["post_id","pslf_sentiment","pslf_stance"]].rename(
            columns={"pslf_sentiment":"cl_sentiment","pslf_stance":"cl_stance"})
    df = df.merge(ll[["post_id","pslf_sentiment","pslf_stance"]].rename(
                    columns={"pslf_sentiment":"ll_sentiment","pslf_stance":"ll_stance"}),
                  on="post_id", how="inner")
    if th is not None:
        df = df.merge(th[["post_id","pslf_sentiment","pslf_stance"]].rename(
                        columns={"pslf_sentiment":"th_sentiment","pslf_stance":"th_stance"}),
                      on="post_id", how="inner")
    df = df.merge(tb_va, on="post_id", how="left")
    print(f"\nMulti-rater intersection: {len(df):,} posts")

    # === Convert to ordinal ===
    sentiment_order = ["very_negative","negative","neutral","positive","very_positive"]
    sentiment_map = {s:i for i,s in enumerate(sentiment_order)}
    df["cl_sent_int"] = df["cl_sentiment"].map(sentiment_map)
    df["ll_sent_int"] = df["ll_sentiment"].map(sentiment_map)
    if th is not None:
        df["th_sent_int"] = df["th_sentiment"].map(sentiment_map)
    # Discretize TB/VADER to percentile-matched quintiles
    if "polarity" in df.columns:
        df["tb_sent_int"] = pd.qcut(df["polarity"].rank(method="first"), q=5,
                                       labels=range(5), duplicates="drop").astype(float)
    if "vader_compound" in df.columns:
        df["va_sent_int"] = pd.qcut(df["vader_compound"].rank(method="first"), q=5,
                                       labels=range(5), duplicates="drop").astype(float)

    # === Pairwise agreement ===
    print("\n[5] Pairwise sentiment agreement (Pearson + exact-match + Cohen's kappa)")
    pairs = [("Claude","Llama","cl_sent_int","ll_sent_int")]
    if th is not None:
        pairs.append(("Claude", third_label, "cl_sent_int", "th_sent_int"))
        pairs.append(("Llama", third_label, "ll_sent_int", "th_sent_int"))
    pairs.extend([
        ("Claude","TextBlob","cl_sent_int","tb_sent_int"),
        ("Claude","VADER","cl_sent_int","va_sent_int"),
        ("Llama","TextBlob","ll_sent_int","tb_sent_int"),
        ("Llama","VADER","ll_sent_int","va_sent_int"),
    ])
    if th is not None:
        pairs.append((third_label,"TextBlob","th_sent_int","tb_sent_int"))
        pairs.append((third_label,"VADER","th_sent_int","va_sent_int"))
    pairs.append(("TextBlob","VADER","tb_sent_int","va_sent_int"))

    rows = []
    for n1, n2, a, b in pairs:
        if a not in df.columns or b not in df.columns: continue
        sub = df[[a,b]].dropna()
        if len(sub) < 30: continue
        r, p = stats.pearsonr(sub[a], sub[b])
        exact = (sub[a]==sub[b]).mean()
        try:
            from sklearn.metrics import cohen_kappa_score
            kappa = cohen_kappa_score(sub[a].astype(int), sub[b].astype(int))
        except: kappa = float("nan")
        label = f"{n1} vs {n2}"
        rows.append({"comparison":label, "n":len(sub), "pearson_r":r,
                      "exact_match":exact, "cohens_kappa":kappa, "p":p})
        print(f"  {label:<40s} n={len(sub):,} r={r:+.3f}  exact={exact:.3f}  kappa={kappa:+.3f}")

    # === Krippendorff alpha ===
    print("\n[6] Krippendorff alpha tests")
    alpha_combos = []
    if th is not None:
        # 3-LLM only
        long = pd.concat([
            df[["post_id","cl_sent_int"]].rename(columns={"cl_sent_int":"sentiment_int"}).assign(scorer="Claude"),
            df[["post_id","ll_sent_int"]].rename(columns={"ll_sent_int":"sentiment_int"}).assign(scorer="Llama"),
            df[["post_id","th_sent_int"]].rename(columns={"th_sent_int":"sentiment_int"}).assign(scorer=third_label),
        ], ignore_index=True).dropna()
        a, n = krippendorff_alpha_ordinal(long)
        alpha_combos.append({"combo":f"Claude+Llama+{third_label} (3-LLM only)", "alpha":a, "n":n})
        print(f"  Claude+Llama+{third_label} (3-LLM only): alpha={a:+.4f}, n={n:,}")

        # 4-rater: 3 LLMs + TB
        long2 = pd.concat([long,
            df[["post_id","tb_sent_int"]].rename(columns={"tb_sent_int":"sentiment_int"}).assign(scorer="TextBlob"),
        ], ignore_index=True).dropna()
        a, n = krippendorff_alpha_ordinal(long2)
        alpha_combos.append({"combo":f"Claude+Llama+{third_label}+TextBlob", "alpha":a, "n":n})
        print(f"  +TextBlob: alpha={a:+.4f}, n={n:,}")

        # 4-rater: 3 LLMs + VADER
        long3 = pd.concat([long,
            df[["post_id","va_sent_int"]].rename(columns={"va_sent_int":"sentiment_int"}).assign(scorer="VADER"),
        ], ignore_index=True).dropna()
        a, n = krippendorff_alpha_ordinal(long3)
        alpha_combos.append({"combo":f"Claude+Llama+{third_label}+VADER", "alpha":a, "n":n})
        print(f"  +VADER: alpha={a:+.4f}, n={n:,}")
    else:
        # 2-LLM only
        long = pd.concat([
            df[["post_id","cl_sent_int"]].rename(columns={"cl_sent_int":"sentiment_int"}).assign(scorer="Claude"),
            df[["post_id","ll_sent_int"]].rename(columns={"ll_sent_int":"sentiment_int"}).assign(scorer="Llama"),
        ], ignore_index=True).dropna()
        a, n = krippendorff_alpha_ordinal(long)
        alpha_combos.append({"combo":"Claude+Llama (2-LLM only)", "alpha":a, "n":n})
        print(f"  Claude+Llama (2-LLM only): alpha={a:+.4f}, n={n:,}")

    # === Stance agreement (LLMs only) ===
    print("\n[7] LLM stance agreement (3-LLM)")
    stance_rows = []
    df_st = df.dropna(subset=["cl_stance","ll_stance"])
    df_st = df_st[~df_st["cl_stance"].isin(["unknown",""])]
    df_st = df_st[~df_st["ll_stance"].isin(["unknown",""])]
    print(f"  Claude vs Llama stance: exact-match {(df_st['cl_stance']==df_st['ll_stance']).mean()*100:.1f}% (n={len(df_st):,})")
    if th is not None:
        df_st3 = df_st.dropna(subset=["th_stance"])
        df_st3 = df_st3[~df_st3["th_stance"].isin(["unknown",""])]
        if len(df_st3) > 30:
            cl_th = (df_st3["cl_stance"]==df_st3["th_stance"]).mean()*100
            ll_th = (df_st3["ll_stance"]==df_st3["th_stance"]).mean()*100
            all3 = ((df_st3["cl_stance"]==df_st3["ll_stance"]) & (df_st3["ll_stance"]==df_st3["th_stance"])).mean()*100
            print(f"  Claude vs {third_label} stance: {cl_th:.1f}% (n={len(df_st3):,})")
            print(f"  Llama vs {third_label} stance: {ll_th:.1f}% (n={len(df_st3):,})")
            print(f"  All 3 LLMs agree: {all3:.1f}%")

    # === Save ===
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False, float_format="%.4f")
    pd.DataFrame(alpha_combos).to_csv(OUT_CSV.replace(".csv","_alpha.csv"),
                                        index=False, float_format="%.4f")

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("MULTI-LLM CONSTRUCT MISMATCH TEST\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Multi-rater intersection: {len(df):,} posts\n")
        f.write(f"LLMs included: Claude{(', Llama' if ll is not None else '')}{(', '+third_label if th is not None else '')}\n")
        f.write(f"Lexical: TextBlob, VADER\n\n")

        f.write("PAIRWISE AGREEMENT\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Comparison':<40s} {'n':>5s} {'r':>7s} {'exact':>7s} {'kappa':>7s}\n")
        for r in rows:
            f.write(f"{r['comparison']:<40s} {r['n']:>5,} {r['pearson_r']:>+7.3f} "
                    f"{r['exact_match']:>6.3f} {r['cohens_kappa']:>+7.3f}\n")

        f.write("\nKRIPPENDORFF ALPHA\n")
        f.write("-" * 80 + "\n")
        for c in alpha_combos:
            f.write(f"  {c['combo']:<60s} alpha={c['alpha']:+.4f}, n={c['n']:,}\n")

        f.write("\nINTERPRETATION\n")
        f.write("-" * 80 + "\n")
        if th is not None and len(alpha_combos) >= 3:
            llm_only = alpha_combos[0]['alpha']
            with_tb = alpha_combos[1]['alpha']
            with_va = alpha_combos[2]['alpha']
            f.write(f"3-LLM-only alpha: {llm_only:+.4f}\n")
            f.write(f"With TextBlob:    {with_tb:+.4f} (drop of {llm_only-with_tb:+.4f})\n")
            f.write(f"With VADER:       {with_va:+.4f} (drop of {llm_only-with_va:+.4f})\n\n")
            if llm_only > 0.5 and with_tb < 0.4:
                f.write("VERDICT: 3 LLMs from 3 organizations achieve substantial agreement.\n")
                f.write("Adding any lexical instrument collapses 3-rater alpha.\n")
                f.write("The construct boundary is LLM-CLASS vs LEXICAL-CLASS, not single-LLM-specific.\n")
                f.write("This rules out 'shared training data' as the explanation for inter-LLM agreement.\n")
        else:
            f.write("Only 2 LLMs analyzed. Add 3rd LLM for stronger 'shared training data' refutation.\n")

    print(f"\nSaved: {OUT_TXT}, {OUT_CSV}")

    # === Figure ===
    if rows:
        fig, ax = plt.subplots(figsize=(12, 6))
        labels = [r["comparison"] for r in rows]
        rs = [r["pearson_r"] for r in rows]
        kappas = [r["cohens_kappa"] for r in rows]
        x = np.arange(len(labels))
        width = 0.35
        # Color: LLM-LLM pairs in green, LLM-lexical in red, lexical-lexical in gray
        colors = []
        for r in rows:
            comp = r["comparison"]
            if "TextBlob vs VADER" in comp:
                colors.append("#9E9E9E")
            elif "TextBlob" in comp or "VADER" in comp:
                colors.append("#C62828")
            else:
                colors.append("#2E7D32")
        ax.bar(x - width/2, rs, width, label="Pearson r", color=colors, alpha=0.85)
        ax.bar(x + width/2, kappas, width, label="Cohen's κ", color=colors, alpha=0.55, hatch="//")
        ax.axhline(0, color="black", lw=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("Agreement coefficient")
        ax.set_title("Multi-LLM construct mismatch — pairwise agreement\n"
                      "Green = LLM×LLM, Red = LLM×lexical, Gray = lexical×lexical")
        ax.grid(alpha=0.3, axis="y")
        ax.legend()
        plt.tight_layout()
        plt.savefig(OUT_PNG, dpi=200, bbox_inches="tight")
        print(f"Saved: {OUT_PNG}")


if __name__ == "__main__":
    main()
