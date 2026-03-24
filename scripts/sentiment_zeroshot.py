"""
sentiment_zeroshot.py
=====================
Zero-shot PSLF sentiment classification using Claude API.

Classifies each post's sentiment toward PSLF specifically (not general tone),
on a 5-point scale: very_negative, negative, neutral, positive, very_positive.

Also extracts:
  - Primary concern/topic (e.g., "servicer delays", "specialty choice", "debt burden")
  - Whether the poster is pursuing/considering/rejecting PSLF

Requires: ANTHROPIC_API_KEY environment variable

Usage:
    python sentiment_zeroshot.py --input reddit_professions_pslf.csv --sample 200
    python sentiment_zeroshot.py --input forum_pslf_discussions.csv --sample 200
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
    print("[WARN] anthropic SDK not installed. pip install anthropic")

import pandas as pd
import numpy as np
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


def classify_batch(client, posts: list[dict], model: str = "claude-sonnet-4-20250514") -> list[dict]:
    """Classify a batch of posts using Claude API."""
    results = []

    for post in tqdm(posts, desc="Classifying"):
        text = post.get("text", "")[:2000]  # Cap for token efficiency
        title = post.get("title", "")[:200]

        prompt = f"Post title: {title}\n\nPost text: {text}"

        try:
            response = client.messages.create(
                model=model,
                max_tokens=150,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text.strip()
            # Parse JSON response
            parsed = json.loads(content)
            parsed["post_id"] = post.get("post_id", post.get("id", ""))
            parsed["source"] = post.get("source", "")
            parsed["profession"] = post.get("profession", "")
            results.append(parsed)

        except json.JSONDecodeError:
            results.append({
                "post_id": post.get("post_id", post.get("id", "")),
                "pslf_sentiment": "parse_error",
                "primary_topic": "parse_error",
                "pslf_stance": "unknown",
                "raw_response": content[:200] if "content" in dir() else "",
            })
        except Exception as e:
            results.append({
                "post_id": post.get("post_id", post.get("id", "")),
                "pslf_sentiment": "api_error",
                "primary_topic": "api_error",
                "pslf_stance": "unknown",
                "error": str(e)[:200],
            })

        # Rate limit: ~50 req/min for Sonnet
        time.sleep(0.5)

    return results


def main():
    parser = argparse.ArgumentParser(description="Zero-shot PSLF sentiment with Claude API")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", default="zeroshot_sentiment.csv", help="Output CSV")
    parser.add_argument("--sample", type=int, default=200, help="Number of posts to classify (0=all)")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("[ERROR] pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERROR] Set ANTHROPIC_API_KEY environment variable")
        print("  Get a key at https://console.anthropic.com/settings/keys")
        sys.exit(1)

    # Load and filter data
    df = pd.read_csv(args.input)
    print(f"Loaded {len(df):,} posts from {args.input}")

    # Determine text/title columns based on file format
    if "combined_text" in df.columns:
        text_col, title_col = "combined_text", "title"
    elif "body" in df.columns:
        text_col, title_col = "body", "thread_title"
    else:
        print("[ERROR] Cannot find text column in CSV")
        sys.exit(1)

    # Apply strict PSLF filter
    tm = df[text_col].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    tt = df[title_col].fillna("").str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    df = df[tm | tt].copy()
    print(f"After PSLF filter: {len(df):,} posts")

    # Min word count
    wc = df[text_col].fillna("").str.split().str.len()
    df = df[wc >= 20].copy()
    print(f"After min 20 words: {len(df):,} posts")

    # Sample if requested
    if args.sample > 0 and len(df) > args.sample:
        df = df.sample(n=args.sample, random_state=args.seed)
        print(f"Sampled {args.sample} posts")

    # Prepare posts for classification
    posts = []
    for _, row in df.iterrows():
        posts.append({
            "text": str(row.get(text_col, "")),
            "title": str(row.get(title_col, "")),
            "post_id": str(row.get("post_id", row.get("id", ""))),
            "source": str(row.get("source", row.get("subreddit", ""))),
            "profession": str(row.get("profession", "")),
        })

    # Classify
    client = anthropic.Anthropic(api_key=api_key)
    print(f"\nClassifying {len(posts)} posts with {args.model}...")
    results = classify_batch(client, posts, model=args.model)

    # Save results
    if results:
        keys = set()
        for r in results:
            keys.update(r.keys())
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(keys))
            writer.writeheader()
            for r in results:
                writer.writerow(r)

    # Summary
    sentiments = [r.get("pslf_sentiment", "") for r in results if r.get("pslf_sentiment") not in ("parse_error", "api_error")]
    topics = [r.get("primary_topic", "") for r in results if r.get("primary_topic") not in ("parse_error", "api_error")]
    stances = [r.get("pslf_stance", "") for r in results if r.get("pslf_stance") not in ("unknown",)]

    from collections import Counter

    print(f"\n{'='*60}")
    print(f"Zero-shot classification complete!")
    print(f"  Classified: {len(results)}")
    print(f"  Output: {args.output}")

    print(f"\n  Sentiment distribution:")
    for s, c in Counter(sentiments).most_common():
        print(f"    {s:20s}: {c:4d} ({c/len(sentiments)*100:.1f}%)")

    print(f"\n  Topic distribution:")
    for t, c in Counter(topics).most_common():
        print(f"    {t:25s}: {c:4d} ({c/len(topics)*100:.1f}%)")

    print(f"\n  PSLF stance:")
    for s, c in Counter(stances).most_common():
        print(f"    {s:15s}: {c:4d} ({c/len(stances)*100:.1f}%)")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
