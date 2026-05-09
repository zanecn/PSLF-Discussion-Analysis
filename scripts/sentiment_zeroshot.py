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


def classify_batch(client, posts: list[dict], model: str = "claude-sonnet-4-20250514",
                   max_consecutive_errors: int = 5,
                   temperature: float | None = None) -> list[dict]:
    """Classify a batch of posts using Claude API.

    Round-5 audit fixes:
      - Fail-fast on AuthenticationError / PermissionDeniedError (never transient)
      - Circuit breaker after `max_consecutive_errors` consecutive failures
      - Zero-guard on summary stats (handled in main() not here)
      - max_tokens raised from 150 -> 250 (was truncating ~2.6% of responses)
      - locals() instead of dir() for the parse-error raw_response capture
    Round-7 critical fix #5:
      - `temperature` argument (None = API default = 1.0; pass 0 for
        deterministic re-scoring used in test-retest reliability runs).
    """
    import anthropic as _anth

    results = []
    consecutive_errors = 0

    for i, post in enumerate(tqdm(posts, desc="Classifying")):
        text = post.get("text", "")[:2000]  # Cap for token efficiency
        title = post.get("title", "")[:200]

        prompt = f"Post title: {title}\n\nPost text: {text}"
        content = ""  # Initialize so JSONDecodeError handler can reference it safely

        try:
            kwargs = dict(
                model=model,
                max_tokens=250,  # Round-5: was 150, truncating ~2.6% of responses
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            if temperature is not None:
                kwargs["temperature"] = temperature
            response = client.messages.create(**kwargs)

            content = response.content[0].text.strip()
            parsed = json.loads(content)
            parsed["post_id"] = post.get("post_id", post.get("id", ""))
            parsed["source"] = post.get("source", "")
            parsed["profession"] = post.get("profession", "")
            results.append(parsed)
            consecutive_errors = 0  # reset on success

        except (_anth.AuthenticationError, _anth.PermissionDeniedError) as e:
            # Never transient — abort immediately to save the user money
            print(f"\n[FATAL] Authentication failed at post {i+1}/{len(posts)}: {str(e)[:150]}")
            print(f"[FATAL] Aborting to avoid burning API credits. Check $env:ANTHROPIC_API_KEY.")
            return results  # return what we have so far (likely 0 rows)

        except json.JSONDecodeError:
            results.append({
                "post_id": post.get("post_id", post.get("id", "")),
                "pslf_sentiment": "parse_error",
                "primary_topic": "parse_error",
                "pslf_stance": "unknown",
                "raw_response": content[:200] if content else "",
            })
            consecutive_errors += 1

        except Exception as e:
            results.append({
                "post_id": post.get("post_id", post.get("id", "")),
                "pslf_sentiment": "api_error",
                "primary_topic": "api_error",
                "pslf_stance": "unknown",
                "error": str(e)[:200],
            })
            consecutive_errors += 1

        # Circuit breaker: abort if too many consecutive failures
        if consecutive_errors >= max_consecutive_errors:
            print(f"\n[ABORT] {consecutive_errors} consecutive errors at post {i+1}/{len(posts)}.")
            print(f"[ABORT] Returning partial results. Check API status, key validity, rate limits.")
            return results

        # Rate limit: ~50 req/min for Sonnet
        time.sleep(0.5)

    return results


def preflight_check(client, model: str) -> tuple[bool, str]:
    """One-shot test call before iterating. Catches auth errors instantly."""
    import anthropic as _anth
    try:
        response = client.messages.create(
            model=model,
            max_tokens=20,
            system="Reply with one word.",
            messages=[{"role": "user", "content": "Say OK."}],
        )
        return True, response.content[0].text.strip()
    except _anth.AuthenticationError as e:
        return False, f"AuthenticationError: {str(e)[:200]}"
    except _anth.PermissionDeniedError as e:
        return False, f"PermissionDeniedError: {str(e)[:200]}"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:200]}"


def main():
    parser = argparse.ArgumentParser(description="Zero-shot PSLF sentiment with Claude API")
    parser.add_argument("--input", required=True, nargs="+",
                        help="Input CSV file(s). Multiple files are concatenated (Reddit medical + teacher + professions).")
    parser.add_argument("--output", default="zeroshot_sentiment.csv", help="Output CSV")
    parser.add_argument("--sample", type=int, default=200, help="Number of posts to classify (0=all)")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument("--stratify-events", action="store_true",
                        help="Sample N posts per event (pre + post window) instead of overall random sample. "
                             "Combine with --per-event to control posts per event (default 100). "
                             "Yields per-event triangulation power. NOTE: --sample is ignored in this mode.")
    parser.add_argument("--per-event", type=int, default=100,
                        help="When --stratify-events is set, posts per event (pre+post combined; "
                             "split as N/2 pre, N/2 post)")
    parser.add_argument("--event-windows-full", action="store_true",
                        help="Score ALL posts in the 8 event windows (pre+post) at full corpus depth, "
                             "no subsampling. Path C in the round-5 triangulation strategy.")
    parser.add_argument("--exclude-scored-csv", nargs="*", default=[],
                        help="Path(s) to existing zeroshot CSV(s); their post_ids will be skipped to avoid "
                             "re-scoring posts already classified.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Filter + dedup as usual, then print sample size and exit (no API calls).")
    parser.add_argument("--temperature", type=float, default=None,
                        help="Override Claude temperature (default uses API default = 1.0). "
                             "Set --temperature 0 for deterministic re-scoring "
                             "(use this for test-retest reliability runs, Round 7 critical fix #5).")
    parser.add_argument("--retest-source-csv", default=None,
                        help="Path to an existing zeroshot CSV. When set, the script will RE-SCORE "
                             "the same post_ids that appear in this CSV (instead of filtering anew). "
                             "Use with --temperature 0 to compute test-retest reliability against "
                             "the original (sampled-temperature) Claude scores.")
    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("[ERROR] pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERROR] Set ANTHROPIC_API_KEY environment variable")
        print("  Get a key at https://console.anthropic.com/settings/keys")
        sys.exit(1)

    # Load and filter data (supports multiple input files for Reddit's split CSVs)
    frames = []
    for inp in args.input:
        d = pd.read_csv(inp)
        d["_input_file"] = inp
        frames.append(d)
        print(f"Loaded {len(d):,} posts from {inp}")
    df = pd.concat(frames, ignore_index=True, sort=False)
    if len(args.input) > 1:
        print(f"Combined: {len(df):,} posts from {len(args.input)} files")
        # Dedup by post id (Reddit medical/teacher CSVs overlap with reddit_professions_pslf.csv)
        id_col = "post_id" if "post_id" in df.columns else ("id" if "id" in df.columns else None)
        if id_col is not None:
            before = len(df)
            df = df.drop_duplicates(subset=[id_col], keep="first").reset_index(drop=True)
            if len(df) < before:
                print(f"After in-file dedup by {id_col}: {len(df):,} unique posts (removed {before - len(df):,})")

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

    # Test-retest source mode (Round-7 critical fix #5): instead of filtering
    # anew, restrict to post_ids that appear in an existing zeroshot CSV. Used
    # with --temperature 0 to compute test-retest reliability against the
    # original (default-temperature) Claude scoring.
    if args.retest_source_csv:
        if not os.path.exists(args.retest_source_csv):
            print(f"[ERROR] --retest-source-csv path does not exist: {args.retest_source_csv}")
            sys.exit(1)
        retest_ids = set(pd.read_csv(args.retest_source_csv,
                                      usecols=["post_id"])["post_id"].astype(str))
        id_col = "post_id" if "post_id" in df.columns else ("id" if "id" in df.columns else None)
        if id_col is None:
            print("[ERROR] No post_id/id column to filter by; cannot run --retest-source-csv mode")
            sys.exit(1)
        before = len(df)
        df = df[df[id_col].astype(str).isin(retest_ids)].copy()
        print(f"[retest mode] Restricted to {len(df):,} posts that appear in "
              f"{args.retest_source_csv} (from {before:,})")
        if len(df) < len(retest_ids):
            missing = len(retest_ids) - len(df)
            print(f"[retest mode] WARNING: {missing} of {len(retest_ids)} source-CSV "
                  f"post_ids are missing from the input CSV. Test-retest alpha will "
                  f"be computed on the {len(df):,}-post intersection only.")

    # Event-windows-full: score ALL posts in any of the 8 event windows (Path C, round-5)
    if args.event_windows_full:
        EVENTS_FULL = [
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
            print("[ERROR] Cannot find date column for event-windows-full mode")
            sys.exit(1)
        in_window = pd.Series(False, index=df.index)
        per_event_counts = []
        for ev_name, ev_date, win in EVENTS_FULL:
            dt = pd.Timestamp(ev_date)
            mask = ((df["_dt"] >= dt - pd.Timedelta(days=win)) &
                    (df["_dt"] <= dt + pd.Timedelta(days=win)))
            per_event_counts.append((ev_name, int(mask.sum())))
            in_window |= mask
        df = df[in_window].drop(columns=["_dt"]).copy()
        print(f"Event-windows-full filter: {len(df):,} posts in any of the 8 event windows")
        print(f"  {'Event':<35s} {'in-window':>10s}")
        for n, c in per_event_counts:
            print(f"  {n:<35s} {c:>10d}")

    # Dedup against already-scored CSVs (saves money on re-scoring)
    if args.exclude_scored_csv:
        scored_ids = set()
        for csv_path in args.exclude_scored_csv:
            if os.path.exists(csv_path):
                d = pd.read_csv(csv_path, usecols=["post_id"])
                scored_ids |= set(d["post_id"].astype(str))
                print(f"Loaded {len(d):,} already-scored ids from {csv_path}")
        if scored_ids:
            id_col = "post_id" if "post_id" in df.columns else ("id" if "id" in df.columns else None)
            if id_col is None:
                print("[WARN] No post_id/id column to dedup against; skipping --exclude-scored-csv")
            else:
                before = len(df)
                df = df[~df[id_col].astype(str).isin(scored_ids)].copy()
                print(f"After dedup against {len(scored_ids):,} prior ids: {len(df):,} posts (was {before:,})")

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
    elif (not args.event_windows_full) and (not args.retest_source_csv) and args.sample > 0 and len(df) > args.sample:
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

    if args.dry_run:
        # Round-trip cost estimate at observed Sonnet 4 rate (~$0.005/post including
        # input + output tokens); rate is ~50 req/min with the 0.5s sleep below.
        est_cost = len(posts) * 0.005
        est_minutes = len(posts) * 0.5 / 60 + len(posts) * 2.0 / 60  # api latency + sleep
        print(f"\n[DRY RUN] {len(posts):,} posts would be scored.")
        print(f"  Estimated cost:     ~${est_cost:.2f}")
        print(f"  Estimated wall-time: ~{est_minutes:.0f} min")
        return

    # Classify
    client = anthropic.Anthropic(api_key=api_key)

    # Round-5 audit fix: pre-flight test to catch auth errors before iterating
    print(f"\nPre-flight check (1 test call to validate API key)...")
    ok, msg = preflight_check(client, args.model)
    if not ok:
        print(f"[FATAL] Pre-flight failed: {msg}")
        print(f"[FATAL] Aborting before iterating {len(posts)} posts.")
        print(f"[FATAL] Verify $env:ANTHROPIC_API_KEY is set in THIS PowerShell window.")
        sys.exit(1)
    print(f"  Pre-flight OK (Claude replied: {msg!r})")

    temp_str = f" (temperature={args.temperature})" if args.temperature is not None else ""
    print(f"\nClassifying {len(posts)} posts with {args.model}{temp_str}...")
    results = classify_batch(client, posts, model=args.model,
                              temperature=args.temperature)

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

    # Summary (round-5 audit: zero-guard on all distributions)
    sentiments = [r.get("pslf_sentiment", "") for r in results
                  if r.get("pslf_sentiment") not in ("parse_error", "api_error")]
    topics = [r.get("primary_topic", "") for r in results
              if r.get("primary_topic") not in ("parse_error", "api_error")]
    stances = [r.get("pslf_stance", "") for r in results
               if r.get("pslf_stance") not in ("unknown",)]
    n_errors = sum(1 for r in results if r.get("pslf_sentiment") in ("parse_error", "api_error"))

    from collections import Counter

    print(f"\n{'='*60}")
    print(f"Zero-shot classification complete!")
    print(f"  Classified: {len(results)}")
    print(f"  Errors: {n_errors} ({n_errors/max(len(results),1)*100:.1f}%)")
    print(f"  Output: {args.output}")

    if not sentiments:
        print(f"\n  [WARNING] No valid sentiment classifications. ALL classifications failed.")
        print(f"  Check {args.output} 'error' column for details.")
    else:
        print(f"\n  Sentiment distribution (n={len(sentiments)}):")
        for s, c in Counter(sentiments).most_common():
            print(f"    {s:20s}: {c:4d} ({c/len(sentiments)*100:.1f}%)")

    if not topics:
        print(f"\n  [WARNING] No valid topic classifications.")
    else:
        print(f"\n  Topic distribution (n={len(topics)}):")
        for t, c in Counter(topics).most_common():
            print(f"    {t:25s}: {c:4d} ({c/len(topics)*100:.1f}%)")

    if not stances:
        print(f"\n  [WARNING] No valid stance classifications.")
    else:
        print(f"\n  PSLF stance (n={len(stances)}):")
        for s, c in Counter(stances).most_common():
            print(f"    {s:15s}: {c:4d} ({c/len(stances)*100:.1f}%)")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
