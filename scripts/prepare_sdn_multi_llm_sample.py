"""
prepare_sdn_multi_llm_sample.py
=================================
Round 16 Strengthener 1: prepare a stratified sample of SDN posts that already
have Claude scoring, ready for Llama + DeepSeek scoring to expand the
multi-LLM intersection beyond Reddit-only.

Currently:
  - n=701 5-instrument intersection has 0 SDN posts (Round 15 audit Fix 6)
  - SDN posts only have TextBlob + VADER + Claude scoring
  - Llama + DeepSeek prioritized Reddit due to scoring-cost constraints

This script:
  1. Loads SDN posts with Claude scoring (zeroshot_sdn_*.csv)
  2. Picks n=300 posts with stratified sample on pslf_sentiment + primary_topic
  3. Saves a CSV ready for sentiment_zeroshot_openweight.py

Output: sdn_for_multi_llm_scoring.csv

Then USER runs:
  python scripts/sentiment_zeroshot_openweight.py --provider together \\
    --model meta-llama/Llama-3.3-70B-Instruct-Turbo \\
    --output zeroshot_llama_sdn.csv \\
    --retest-source-csv sdn_for_multi_llm_scoring.csv

  python scripts/sentiment_zeroshot_openweight.py --provider together \\
    --model deepseek-ai/DeepSeek-V3.1 \\
    --output zeroshot_deepseek_sdn.csv \\
    --retest-source-csv sdn_for_multi_llm_scoring.csv

Cost: ~$30 (300 posts × 2 LLMs × ~$0.02-0.05/post via Together AI)
Time: ~30 min total
"""
import sys
from pathlib import Path

import pandas as pd
import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def main():
    # Load all SDN Claude scoring files
    sdn_files = ["zeroshot_sdn_n1000.csv", "zeroshot_sdn_eventfull.csv",
                 "zeroshot_sdn_temp0_retest.csv", "zeroshot_sdn_forum.csv"]
    dfs = []
    for f in sdn_files:
        p = PROJECT / f
        if p.exists():
            d = pd.read_csv(p)
            if "post_id" in d.columns and "pslf_sentiment" in d.columns:
                dfs.append(d[["post_id", "pslf_sentiment", "primary_topic", "pslf_stance"]])
    sdn = pd.concat(dfs, ignore_index=True).drop_duplicates(subset="post_id", keep="first")
    print(f"SDN Claude-scored posts available: {len(sdn):,}")

    # Filter to valid scorings (no parse_error or api_error)
    sdn = sdn[sdn["pslf_sentiment"].isin(["very_negative", "negative", "neutral", "positive", "very_positive"])]
    print(f"Valid Claude scorings: {len(sdn):,}")

    # Verify text is available (need post text to send to Llama/DeepSeek)
    forum = pd.read_csv(PROJECT / "forum_pslf_discussions.csv", usecols=["post_id", "body", "thread_title"])
    sdn = sdn.merge(forum, on="post_id", how="inner")
    sdn = sdn[sdn["body"].notna() & (sdn["body"].str.len() > 50)]
    print(f"With text >50 chars: {len(sdn):,}")

    # Stratified sample: balance across sentiment + topic
    sdn["sentiment_topic"] = sdn["pslf_sentiment"].astype(str) + "_" + sdn["primary_topic"].astype(str)
    print(f"\nSentiment x Topic distribution (top 15):")
    print(sdn["sentiment_topic"].value_counts().head(15))

    # Sample n=300 with balanced strata
    target_n = 300
    rng = np.random.default_rng(42)
    strata = sdn.groupby("sentiment_topic")
    n_strata = len(strata)
    per_stratum = max(2, target_n // n_strata)
    sampled = []
    for name, group in strata:
        n_take = min(len(group), per_stratum)
        sampled.append(group.sample(n=n_take, random_state=42))
    out = pd.concat(sampled, ignore_index=True)
    if len(out) > target_n:
        out = out.sample(n=target_n, random_state=42)
    elif len(out) < target_n:
        # Top up with random additional
        remaining = sdn[~sdn["post_id"].isin(out["post_id"])]
        need = target_n - len(out)
        if len(remaining) >= need:
            out = pd.concat([out, remaining.sample(n=need, random_state=42)], ignore_index=True)
    print(f"\nFinal sample: {len(out)}")
    print(f"Sentiment distribution: {out['pslf_sentiment'].value_counts().to_dict()}")

    out_path = PROJECT / "sdn_for_multi_llm_scoring.csv"
    out[["post_id", "pslf_sentiment", "primary_topic", "pslf_stance"]].to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    print(f"\nNext steps for USER (~30 min, ~$30):")
    print(f'  $env:TOGETHER_API_KEY = "your_key_here"')
    print(f"  cd C:\\Users\\zanen\\PSLF_2026\\PSLF-Discussion-Analysis")
    print(f"  python ..\\scripts\\sentiment_zeroshot_openweight.py --provider together \\")
    print(f"    --model meta-llama/Llama-3.3-70B-Instruct-Turbo \\")
    print(f"    --output zeroshot_llama_sdn.csv \\")
    print(f"    --retest-source-csv sdn_for_multi_llm_scoring.csv")
    print(f"  python ..\\scripts\\sentiment_zeroshot_openweight.py --provider together \\")
    print(f"    --model deepseek-ai/DeepSeek-V3.1 \\")
    print(f"    --output zeroshot_deepseek_sdn.csv \\")
    print(f"    --retest-source-csv sdn_for_multi_llm_scoring.csv")


if __name__ == "__main__":
    main()
