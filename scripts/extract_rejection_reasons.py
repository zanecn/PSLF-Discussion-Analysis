"""
extract_rejection_reasons.py
=============================
Re-prompts Claude on posts with pslf_stance="rejecting" to extract a
structured rejection_reason category. Currently the project's stance
classifier collapses all rejection reasons into one bucket; this expands
it into 7 substantive categories so we can characterize WHY borrowers are
rejecting PSLF.

Categories (mutually exclusive; pick best fit):
  - cost_complexity        : "PSLF is too complex / requirements unclear"
  - employer_mismatch      : "My employer doesn't qualify / left qualifying employer"
  - job_change             : "Changing jobs and new one isn't qualifying"
  - forbearance_fatigue    : "Tired of forbearance/limbo, just want it done"
  - timeline_too_long      : "10 years too long; better to refinance/pay off"
  - servicer_distrust      : "Servicer screwed it up / I don't trust them"
  - alternative_strategy   : "Refinancing/IDR forgiveness is better for me"

Cost: ~3,000 rejecting posts × $0.005 = ~$15
Wall-time: ~2 hours

Requires: ANTHROPIC_API_KEY environment variable

Usage:
  $env:ANTHROPIC_API_KEY = "sk-ant-..."  # PowerShell
  python extract_rejection_reasons.py
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

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

import pandas as pd
import numpy as np
from tqdm import tqdm

ZEROSHOT_CSVS = [
    "zeroshot_reddit_n1000.csv",
    "zeroshot_sdn_n1000.csv",
    "zeroshot_reddit_eventstrat.csv",
    "zeroshot_reddit_eventfull.csv",
    "zeroshot_sdn_eventfull.csv",
    "zeroshot_pa_np_expansion.csv",
    "zeroshot_reddit_fullcorpus.csv",
    "zeroshot_reddit_arctic_shift_fill.csv",
]

SYSTEM_PROMPT = """You are an expert in classifying reasons people give for rejecting Public Service Loan Forgiveness (PSLF).

For each post that the original analysis classified as `pslf_stance="rejecting"`, extract the PRIMARY reason cited (or implied) for rejecting PSLF, from this taxonomy:

  - cost_complexity        : "PSLF is too complex / requirements unclear / paperwork burden"
  - employer_mismatch      : "My employer doesn't qualify / I left a qualifying employer / can't find qualifying job"
  - job_change             : "Changing jobs and new one isn't qualifying / career path doesn't fit PSLF"
  - forbearance_fatigue    : "Tired of forbearance/limbo/uncertainty, just want it done"
  - timeline_too_long      : "10 years too long / better to refinance and pay off / not worth the wait"
  - servicer_distrust      : "Servicer screwed it up / can't trust them / processing failures"
  - alternative_strategy   : "Refinancing / IDR forgiveness / PAYE bomb is better for my situation"
  - other                  : doesn't fit any category cleanly

If the post doesn't actually express a rejection reason (e.g., the original classifier was wrong), return "no_reason_given".

Respond ONLY with valid JSON, no markdown:
{"rejection_reason": "...", "confidence": "high"|"medium"|"low"}"""


def get_rejecting_posts() -> pd.DataFrame:
    """Get all posts where stance was classified as 'rejecting'."""
    frames = []
    for f in ZEROSHOT_CSVS:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        d = d[d["pslf_stance"] == "rejecting"].copy()
        if "post_id" not in d.columns:
            continue
        keep = ["post_id", "pslf_sentiment", "pslf_stance", "primary_topic"]
        if "profession" in d.columns:
            keep.append("profession")
        if "source" in d.columns:
            keep.append("source")
        frames.append(d[keep])
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True).drop_duplicates("post_id")
    return out


def attach_text(rejecting_df: pd.DataFrame) -> pd.DataFrame:
    """Merge in body/text from source CSVs."""
    text_frames = []
    for fpath, text_col, title_col in [
        ("reddit_professions_pslf.csv", "combined_text", "title"),
        ("comprehensive_medical_pslf_discussions.csv", "combined_text", "title"),
        ("comprehensive_teacher_pslf_discussions.csv", "combined_text", "title"),
        ("reddit_arctic_shift_pslf.csv", "combined_text", "title"),
        ("reddit_new_subs_pslf.csv", "combined_text", "title"),
    ]:
        if not os.path.exists(fpath):
            continue
        d = pd.read_csv(fpath)
        if "id" in d.columns:
            d = d.rename(columns={"id": "post_id"})
        if text_col not in d.columns:
            continue
        d["text"] = (d[title_col].fillna("").astype(str) + "\n" +
                      d[text_col].fillna("").astype(str)).str.strip()
        text_frames.append(d[["post_id", "text"]])
    # SDN
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        d["text"] = (d["thread_title"].fillna("").astype(str) + "\n" +
                      d["body"].fillna("").astype(str)).str.strip()
        text_frames.append(d[["post_id", "text"]])
    texts = pd.concat(text_frames, ignore_index=True).drop_duplicates("post_id")
    rejecting_df["post_id"] = rejecting_df["post_id"].astype(str)
    texts["post_id"] = texts["post_id"].astype(str)
    return rejecting_df.merge(texts, on="post_id", how="left")


def classify_reason(client, text: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Single-post Claude classification of rejection reason."""
    if not text or len(text) < 30:
        return {"rejection_reason": "no_reason_given", "confidence": "low"}
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=80,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text[:4000]}],
        )
        out = resp.content[0].text.strip()
        if out.startswith("```"):
            out = out.split("```")[1].lstrip("json\n").rstrip("`").strip()
        return json.loads(out)
    except Exception as e:
        return {"rejection_reason": "parse_error", "confidence": "low",
                "error": str(e)[:200]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="rejection_reasons.csv")
    parser.add_argument("--max-posts", type=int, default=None,
                        help="Cap for testing")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--model", default="claude-sonnet-4-20250514")
    args = parser.parse_args()

    if not HAS_ANTHROPIC:
        print("[ERROR] pip install anthropic")
        sys.exit(1)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[ERROR] Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    print("Loading rejecting posts...")
    rej = get_rejecting_posts()
    print(f"  Rejecting posts: {len(rej):,}")
    if len(rej) == 0:
        print("[ABORT] No rejecting posts found.")
        sys.exit(1)

    print("Attaching text from source CSVs...")
    rej = attach_text(rej)
    rej = rej[rej["text"].notna() & (rej["text"].str.len() > 30)]
    print(f"  Posts with text >30 chars: {len(rej):,}")

    if args.max_posts:
        rej = rej.head(args.max_posts).copy()
        print(f"  --max-posts: limiting to {len(rej):,}")

    # Resume support
    done = set()
    mode = "w"
    if args.resume and os.path.exists(args.output):
        prev = pd.read_csv(args.output)
        done = set(prev["post_id"].astype(str))
        rej = rej[~rej["post_id"].astype(str).isin(done)]
        print(f"  --resume: skipping {len(done):,} already-done; "
              f"remaining {len(rej):,}")
        mode = "a"

    estimated = len(rej) * 0.005
    print(f"\nEstimated cost (~$0.005/post): ${estimated:.2f}")
    print(f"Estimated wall-time (~1.5 sec/post): {len(rej) * 1.5 / 60:.0f} min")

    print("\nPre-flight test...")
    client = anthropic.Anthropic(api_key=api_key)
    test = classify_reason(client, "I'm rejecting PSLF because servicer keeps losing my paperwork")
    print(f"  Pre-flight: {test}")
    if test.get("rejection_reason") in ("parse_error",):
        print(f"[ABORT] Pre-flight failed: {test.get('error', '')}")
        sys.exit(1)

    print(f"\nClassifying {len(rej):,} rejecting posts...")
    fields = ["post_id", "rejection_reason", "confidence", "error"]
    with open(args.output, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if mode == "w":
            writer.writeheader()
        for _, row in tqdm(rej.iterrows(), total=len(rej), desc="Classifying"):
            result = classify_reason(client, row["text"], model=args.model)
            result["post_id"] = row["post_id"]
            writer.writerow(result)

    print(f"\nSaved: {args.output}")

    # Quick summary
    out = pd.read_csv(args.output)
    print("\nRejection reason distribution:")
    print(out["rejection_reason"].value_counts().to_string())


if __name__ == "__main__":
    main()
