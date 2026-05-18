"""
sentiment_zeroshot_openweight.py
==================================
Re-scores the same PSLF posts with an OPEN-WEIGHT LLM (GPT-4o or Llama 3) for
methods-paper "not just Claude" defense.

Default: Together AI's Llama 3.1 70B Instruct (cheap; ~$0.88/1M tokens).
Alternative: OpenAI GPT-4o via OpenAI SDK.

Why important:
  Round-9 audit identified this as the single highest-leverage methods-paper
  upgrade. Required for Political Analysis venue tier. Converts every methods
  finding from "Claude-specific" to "general LLM behavior".

Same prompt as Claude scoring (sentiment_zeroshot.py SYSTEM_PROMPT) so results
are directly comparable.

Setup:
  Together AI (recommended, ~$5-15 for full corpus):
    pip install together
    Get key: https://api.together.xyz/settings/api-keys
    $env:TOGETHER_API_KEY = "your-key"

  OR OpenAI GPT-4o (~$25-50):
    pip install openai
    $env:OPENAI_API_KEY = "your-key"

Usage:
  python sentiment_zeroshot_openweight.py --provider together
  python sentiment_zeroshot_openweight.py --provider openai
  python sentiment_zeroshot_openweight.py --max-posts 100  # for testing
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import time
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from tqdm import tqdm

SYSTEM_PROMPT = """You are a sentiment analysis expert specializing in Public Service Loan Forgiveness (PSLF) discussions.

For each post, classify:

1. **pslf_sentiment**: The poster's sentiment TOWARD PSLF specifically (not general mood).
   - very_negative: Angry/frustrated with PSLF, believes it's broken/worthless
   - negative: Concerned/worried about PSLF, skeptical it will work
   - neutral: Asking factual questions, sharing info without strong opinion
   - positive: Hopeful/optimistic about PSLF, believes it's worth pursuing
   - very_positive: Enthusiastic, celebrating PSLF success, strongly advocating

2. **primary_topic**: One of these categories:
   - servicer_issues: MOHELA/FedLoan delays, lost payments, processing errors
   - policy_uncertainty: Legislative changes, executive orders, court decisions
   - financial_planning: IDR plan choice, repayment strategy, debt calculations
   - career_impact: Job/specialty choice influenced by PSLF eligibility
   - success_story: Forgiveness received or imminent
   - general_question: Basic PSLF eligibility/process questions
   - frustration_venting: Expressing anger/despair about student debt/PSLF

3. **pslf_stance**: pursuing, considering, rejecting, completed, unknown

Respond ONLY with valid JSON, no markdown:
{"pslf_sentiment": "...", "primary_topic": "...", "pslf_stance": "..."}"""


def classify_with_together(client, text: str, model: str = "meta-llama/Llama-3.1-70B-Instruct-Turbo") -> dict:
    """Together AI Llama 3 70B classification."""
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:4000]},
            ],
            max_tokens=120,
            temperature=0,
        )
        out = resp.choices[0].message.content.strip()
        if out.startswith("```"):
            out = out.split("```")[1].lstrip("json\n").rstrip("`").strip()
        return json.loads(out)
    except Exception as e:
        return {"pslf_sentiment": "parse_error", "primary_topic": "parse_error",
                "pslf_stance": "parse_error", "error": str(e)[:200]}


def classify_with_openai(client, text: str, model: str = "gpt-4o") -> dict:
    """OpenAI GPT-4o classification."""
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:4000]},
            ],
            max_tokens=120,
            temperature=0,
            response_format={"type": "json_object"},
        )
        out = resp.choices[0].message.content.strip()
        return json.loads(out)
    except Exception as e:
        return {"pslf_sentiment": "parse_error", "primary_topic": "parse_error",
                "pslf_stance": "parse_error", "error": str(e)[:200]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["together", "openai"], default="together")
    parser.add_argument("--input", default="reddit_professions_pslf.csv",
                        help="Source CSV with text + post_id")
    parser.add_argument("--retest-source-csv",
                        default="zeroshot_reddit_n1000.csv",
                        help="Restrict to post_ids from this prior Claude-scored CSV")
    parser.add_argument("--output", default=None,
                        help="Default: zeroshot_{provider}_replication.csv")
    parser.add_argument("--max-posts", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--model", default=None,
                        help="Override default model")
    args = parser.parse_args()

    if args.output is None:
        args.output = f"zeroshot_{args.provider}_replication.csv"

    # Setup client
    if args.provider == "together":
        try:
            from together import Together
        except ImportError:
            print("[ABORT] pip install together")
            sys.exit(1)
        api_key = os.environ.get("TOGETHER_API_KEY", "")
        if not api_key:
            print("[ABORT] Set TOGETHER_API_KEY env var")
            print("        Get key at https://api.together.xyz/settings/api-keys")
            sys.exit(1)
        client = Together(api_key=api_key)
        model = args.model or "meta-llama/Llama-3.1-70B-Instruct-Turbo"
        classify = lambda t: classify_with_together(client, t, model=model)
    else:
        try:
            from openai import OpenAI
        except ImportError:
            print("[ABORT] pip install openai")
            sys.exit(1)
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            print("[ABORT] Set OPENAI_API_KEY env var")
            sys.exit(1)
        client = OpenAI(api_key=api_key)
        model = args.model or "gpt-4o"
        classify = lambda t: classify_with_openai(client, t, model=model)

    # Load source
    print(f"Loading {args.input}...")
    df = pd.read_csv(args.input)
    if "id" in df.columns:
        df = df.rename(columns={"id": "post_id"})
    print(f"  Total rows: {len(df):,}")

    # Filter to retest_source_csv post_ids
    if args.retest_source_csv:
        retest = pd.read_csv(args.retest_source_csv)
        retest_ids = set(retest["post_id"].astype(str))
        df["post_id"] = df["post_id"].astype(str)
        df = df[df["post_id"].isin(retest_ids)].copy()
        print(f"  After retest-source filter: {len(df):,}")

    # Determine text column
    text_col = ("combined_text" if "combined_text" in df.columns
                else "selftext" if "selftext" in df.columns
                else "body" if "body" in df.columns else None)
    if not text_col:
        print("[ABORT] No text column found")
        sys.exit(1)
    df = df[df[text_col].notna()].copy()
    df = df[df[text_col].astype(str).str.split().str.len() >= 20].copy()
    print(f"  After wc>=20: {len(df):,}")

    if args.max_posts:
        df = df.head(args.max_posts)
        print(f"  --max-posts: limited to {len(df):,}")

    # Resume support
    done = set()
    mode = "w"
    if args.resume and os.path.exists(args.output):
        prev = pd.read_csv(args.output)
        done = set(prev["post_id"].astype(str))
        df = df[~df["post_id"].astype(str).isin(done)]
        mode = "a"
        print(f"  --resume: skipping {len(done):,}; remaining {len(df):,}")

    estimated_cost = (len(df) * 0.0004) if args.provider == "together" else (len(df) * 0.005)
    print(f"\n  Provider: {args.provider}, model: {model}")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    print(f"  Estimated wall-time: {len(df) * 1.5 / 60:.0f} min")

    # Pre-flight test
    print("\n[Pre-flight test]")
    test = classify("I'm cautiously optimistic about PSLF. The Limited Waiver helped a lot, but I worry about the Trump administration changing things.")
    print(f"  Result: {test}")
    if test.get("pslf_sentiment") == "parse_error":
        print(f"[ABORT] Pre-flight failed: {test.get('error', '')}")
        sys.exit(1)

    # Classify all
    print(f"\nClassifying {len(df):,} posts...")
    fields = ["post_id", "pslf_sentiment", "primary_topic", "pslf_stance",
              "raw_response", "error"]
    with open(args.output, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if mode == "w":
            writer.writeheader()
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Classifying"):
            result = classify(row[text_col])
            result["post_id"] = row["post_id"]
            writer.writerow(result)

    print(f"\nSaved: {args.output}")
    out = pd.read_csv(args.output)
    valid = out[~out["pslf_sentiment"].isin(["parse_error", ""])]
    print(f"Valid: {len(valid):,}/{len(out):,} ({100*len(valid)/len(out):.1f}%)")
    print("\nSentiment distribution:")
    print(valid["pslf_sentiment"].value_counts().to_string())

    # Quick comparison to Claude (if retest-source-csv was used)
    if args.retest_source_csv and os.path.exists(args.retest_source_csv):
        print("\n[Cross-LLM comparison vs Claude]")
        cl = pd.read_csv(args.retest_source_csv)
        cl = cl[~cl["pslf_sentiment"].isin(["parse_error", "api_error"])]
        cl["post_id"] = cl["post_id"].astype(str)
        valid["post_id"] = valid["post_id"].astype(str)
        merged = valid.merge(cl[["post_id", "pslf_sentiment"]],
                              on="post_id", how="inner",
                              suffixes=("_ow", "_claude"))
        print(f"  Cross-LLM intersection: {len(merged):,}")
        if len(merged) > 50:
            agreement = (merged["pslf_sentiment_ow"] == merged["pslf_sentiment_claude"]).mean()
            print(f"  Exact-match rate (OW vs Claude): {agreement*100:.1f}%")


if __name__ == "__main__":
    main()
