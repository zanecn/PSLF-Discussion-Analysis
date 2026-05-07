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
    parser.add_argument("--stratify-events", action="store_true",
                        help="Sample N posts per event (pre + post window) instead of overall random sample. "
                             "Use with --sample to control posts per event (default 100). "
                             "Yields per-event triangulation power.")
    parser.add_argument("--per-event", type=int, default=100,
                        help="When --stratify-events is set, posts per event (pre+post combined)")
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

    # Event-stratified sampling: sample N posts per event window (round-4 audit)
    if args.stratify_events:
        # 8 policy events with 90d / 60d windows around each
        EVENTS = [
            ("Limited PSLF Waiver",            "2021-10-06", 90),
            ("IDR Account Adjustment",         "2022-04-19", 90),
            ("Biden Mass Forgiveness",         "2022-08-24", 90),
            ("Biden v. Nebraska SCOTUS",       "2023-06-30", 90),
            ("Payments Restart",               "2023-10-01", 90),
            ("SAVE Admin Forbearance",         "2024-08-09", 90),
            ("Trump PSLF EO",                  "2025-03-07", 60),
            ("Final Trump PSLF Rule",          "2025-10-30", 60),
        ]
        if "created_utc" in df.columns:
            df["_dt"] = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"),
                                       unit="s", utc=True).dt.tz_localize(None)
        elif "date_posted" in df.columns:
            df["_dt"] = pd.to_datetime(df["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        else:
            print("[ERROR] Cannot find date column for event stratification")
            sys.exit(1)
        rng = np.random.default_rng(args.seed)
        per_event = args.per_event
        sampled_indices = set()
        n_per_window = per_event // 2
        per_event_summary = []
        for ev_name, ev_date, win in EVENTS:
            dt = pd.Timestamp(ev_date)
            pre_mask = (df["_dt"] >= dt - pd.Timedelta(days=win)) & (df["_dt"] < dt)
            post_mask = (df["_dt"] >= dt) & (df["_dt"] <= dt + pd.Timedelta(days=win))
            pre_idx = df[pre_mask].index.tolist()
            post_idx = df[post_mask].index.tolist()
            pre_sample = list(rng.choice(pre_idx, size=min(n_per_window, len(pre_idx)),
                                          replace=False)) if pre_idx else []
            post_sample = list(rng.choice(post_idx, size=min(n_per_window, len(post_idx)),
                                           replace=False)) if post_idx else []
            sampled_indices.update(pre_sample)
            sampled_indices.update(post_sample)
            per_event_summary.append((ev_name, len(pre_sample), len(post_sample)))
        df = df.loc[sorted(sampled_indices)].drop(columns=["_dt"])
        print(f"Event-stratified sample: {len(df)} posts across {len(EVENTS)} events")
        print(f"  {'Event':<35s} {'pre':>5s} {'post':>5s}")
        for n, p, q in per_event_summary:
            print(f"  {n:<35s} {p:>5d} {q:>5d}")
    elif args.sample > 0 and len(df) > args.sample:
        # Build a stratification key
        if "created_utc" in df.columns:
            yr = pd.to_datetime(pd.to_numeric(df["created_utc"], errors="coerce"),
                                unit="s", utc=True).dt.year.fillna(2020).astype(int)
        elif "date_posted" in df.columns:
            yr = pd.to_datetime(df["date_posted"], errors="coerce", utc=True).dt.year.fillna(2020).astype(int)
        else:
            yr = pd.Series(2020, index=df.index)
        src = df.get("subreddit", df.get("source", pd.Series("unk", index=df.index)))
        df = df.assign(_strat=yr.astype(str) + "_" + src.astype(str))
        # Stratified sample: at least 1 from each stratum, then proportional fill
        try:
            df_strat = df.groupby("_strat", group_keys=False).apply(
                lambda g: g.sample(n=min(len(g), max(1, args.sample // df["_strat"].nunique())),
                                   random_state=args.seed)
            )
            if len(df_strat) > args.sample:
                df_strat = df_strat.sample(n=args.sample, random_state=args.seed)
            df = df_strat.drop(columns=["_strat"])
            print(f"Stratified sample: {len(df)} posts across {df.get('subreddit', df.get('source')).nunique()} sources × years")
        except Exception:
            df = df.sample(n=args.sample, random_state=args.seed)
            print(f"Fallback random sample: {len(df)} posts")

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
