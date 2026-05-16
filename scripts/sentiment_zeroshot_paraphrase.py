"""
sentiment_zeroshot_paraphrase.py
=================================
Round 16 Strengthener 2: paraphrase-robustness test-retest.

The original test-retest (sentiment_zeroshot.py --temperature 0 twice) measures
API determinism, NOT test-retest reliability under prompt variation. This script
addresses that critique by re-scoring the same n=200 posts with 2 alternative
system prompt phrasings (same semantic meaning, different wording).

If Claude classifications are robust to prompt phrasing, the K-α across the
three prompts should be high (>0.85). If classifications are prompt-sensitive,
α will be lower and the original 100% determinism claim is misleading.

Usage:
  # First run (the OFFICIAL paraphrase 1)
  python scripts/sentiment_zeroshot_paraphrase.py \\
      --prompt-variant 1 \\
      --retest-source-csv zeroshot_sdn_temp0_retest.csv \\
      --output zeroshot_sdn_paraphrase_v1.csv

  # Second run (the OFFICIAL paraphrase 2)
  python scripts/sentiment_zeroshot_paraphrase.py \\
      --prompt-variant 2 \\
      --retest-source-csv zeroshot_sdn_temp0_retest.csv \\
      --output zeroshot_sdn_paraphrase_v2.csv

Cost: ~$5 total (200 posts × 2 paraphrases = 400 Claude calls × ~$0.01)
Time: ~7 minutes
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pslf_search_terms import PSLF_STRICT_REGEX

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

import pandas as pd
import numpy as np
from tqdm import tqdm


# ALTERNATIVE SYSTEM PROMPTS (same semantic content, different phrasing)
# These are paraphrases of the original prompt; the classification scheme is
# IDENTICAL but the wording differs to test prompt-sensitivity.

PROMPT_VARIANT_1 = """You are an expert in analyzing online discussions about the Public Service Loan Forgiveness (PSLF) program. Your task: assign each post to three categorical variables.

Variable 1 — pslf_sentiment (5-level ordinal). What is the poster's emotional valence toward PSLF specifically?
  • very_negative: The poster expresses anger or strong frustration with PSLF, suggesting the program is fundamentally broken or worthless.
  • negative: The poster is worried, concerned, or skeptical about PSLF.
  • neutral: The post is informational, factual, or contains neither strong positive nor negative sentiment toward PSLF.
  • positive: The poster is hopeful, optimistic about PSLF.
  • very_positive: The poster celebrates PSLF success or strongly advocates for it.

Variable 2 — primary_topic (categorical, choose ONE):
  • servicer_issues: Problems with MOHELA / FedLoan / loan servicers (processing delays, errors).
  • policy_uncertainty: Discussions about legislation, executive orders, court rulings affecting PSLF.
  • financial_planning: IDR plan selection, repayment strategy, debt math.
  • career_impact: How PSLF affects job/specialty/employment choices.
  • success_story: Achieved or imminent PSLF forgiveness.
  • general_question: Basic eligibility, process, or how-to questions.
  • frustration_venting: General anger about student debt or PSLF without specifics.

Variable 3 — pslf_stance (categorical): pursuing, considering, rejecting, completed, or unknown.

Output ONLY a JSON object, no markdown:
{"pslf_sentiment": "<label>", "primary_topic": "<label>", "pslf_stance": "<label>"}"""

PROMPT_VARIANT_2 = """Classify the following PSLF-related post on three dimensions.

DIMENSION 1: pslf_sentiment
Possible labels (5-level ordinal):
- very_negative — author angry/frustrated, sees PSLF as broken
- negative — author concerned/skeptical
- neutral — author asks factual questions or shares info without affect
- positive — author hopeful PSLF will work for them
- very_positive — author enthusiastic, celebrates PSLF success

DIMENSION 2: primary_topic
Possible labels:
- servicer_issues — MOHELA, FedLoan, processing problems
- policy_uncertainty — legislation, court rulings, executive orders
- financial_planning — IDR choice, debt repayment math
- career_impact — job/specialty decisions driven by PSLF
- success_story — received or imminent forgiveness
- general_question — basic eligibility questions
- frustration_venting — angry posts about student debt

DIMENSION 3: pslf_stance
Possible labels: pursuing, considering, rejecting, completed, unknown

Return your classification as a JSON object on ONE line:
{"pslf_sentiment": "X", "primary_topic": "X", "pslf_stance": "X"}

No explanation needed. JSON only."""


def classify_batch(client, posts, system_prompt, model="claude-sonnet-4-20250514",
                   max_consecutive_errors=5, temperature=0.0):
    import anthropic as _anth
    results = []
    consecutive_errors = 0
    for i, post in enumerate(tqdm(posts, desc="Classifying")):
        text = post.get("text", "")[:2000]
        title = post.get("title", "")[:200]
        prompt = f"Post title: {title}\n\nPost text: {text}"
        content = ""
        try:
            response = client.messages.create(
                model=model, max_tokens=250, temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text.strip()
            parsed = json.loads(content)
            parsed["post_id"] = post.get("post_id", "")
            parsed["source"] = post.get("source", "sdn")
            results.append(parsed)
            consecutive_errors = 0
        except (_anth.AuthenticationError, _anth.PermissionDeniedError) as e:
            print(f"\n[FATAL] Auth: {e}")
            return results
        except json.JSONDecodeError:
            results.append({"post_id": post.get("post_id", ""), "pslf_sentiment": "parse_error",
                           "primary_topic": "parse_error", "pslf_stance": "unknown"})
            consecutive_errors += 1
        except Exception as e:
            results.append({"post_id": post.get("post_id", ""), "pslf_sentiment": "api_error",
                           "primary_topic": "api_error", "pslf_stance": "unknown"})
            consecutive_errors += 1
        if consecutive_errors >= max_consecutive_errors:
            print(f"\n[ABORT] {consecutive_errors} consecutive errors at {i+1}")
            return results
        time.sleep(0.5)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-variant", type=int, choices=[1, 2], required=True)
    parser.add_argument("--retest-source-csv", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--input-corpus", default="C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/forum_pslf_discussions.csv")
    parser.add_argument("--sample", type=int, default=200, help="Max posts to score (subset of retest source)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("pip install anthropic")
        sys.exit(1)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERROR] Set ANTHROPIC_API_KEY")
        sys.exit(1)

    # Pick the prompt
    system_prompt = PROMPT_VARIANT_1 if args.prompt_variant == 1 else PROMPT_VARIANT_2
    print(f"Using paraphrase variant {args.prompt_variant} ({len(system_prompt)} chars)")

    # Load retest-source post IDs
    retest = pd.read_csv(args.retest_source_csv)
    print(f"Retest source: {len(retest)} post_ids")

    # Load full corpus to get text
    corpus = pd.read_csv(args.input_corpus, usecols=["post_id", "body", "thread_title"])
    df = retest.merge(corpus, on="post_id", how="inner")
    df = df[df["body"].notna() & (df["body"].str.len() > 50)]
    print(f"After text join: {len(df)} posts")

    # Sample down to args.sample if needed
    if len(df) > args.sample:
        df = df.sample(n=args.sample, random_state=args.seed)
    print(f"Final sample: {len(df)}")

    # Build posts list
    posts = [{"post_id": r["post_id"], "title": str(r.get("thread_title", "")),
              "text": str(r["body"]), "source": "sdn"} for _, r in df.iterrows()]

    client = anthropic.Anthropic(api_key=api_key)
    print(f"\n[Pre-flight test]")
    try:
        r = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=20, temperature=0.0,
                                    system="Reply with one word.", messages=[{"role": "user", "content": "Say OK."}])
        print(f"  OK: {r.content[0].text.strip()}")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    print(f"\nClassifying {len(posts)} posts with paraphrase variant {args.prompt_variant}...")
    results = classify_batch(client, posts, system_prompt)
    out_df = pd.DataFrame(results)
    out_df.to_csv(args.output, index=False)
    print(f"\nSaved: {args.output}")
    print(f"  {len(out_df)} rows")
    valid = (out_df["pslf_sentiment"].isin(["very_negative", "negative", "neutral", "positive", "very_positive"])).sum()
    print(f"  Valid: {valid} ({100*valid/len(out_df):.1f}%)")


if __name__ == "__main__":
    main()
