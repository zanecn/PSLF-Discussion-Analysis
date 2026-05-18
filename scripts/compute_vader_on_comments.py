"""
compute_vader_on_comments.py
==============================
C1 / methods extension: compute VADER compound on the 460K-comment dataset
to extend the construct-mismatch finding to comments scale.

Currently comments only have TextBlob polarity. Adding VADER lets us compute
TB×VADER α at comments scale — the partial finding showed α=+0.298 at n=12,601.
This brings the finding to ~460K.

Output: appends `vader_compound` column to reddit_comments_pslf.csv
        prints partial summary
"""
from __future__ import annotations
import io, os, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import pandas as pd
from tqdm import tqdm

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print("[ABORT] pip install vaderSentiment")
    sys.exit(1)


def main():
    print("=" * 80)
    print("Compute VADER compound on Reddit comments")
    print("=" * 80)

    src = "reddit_comments_pslf.csv"
    out = "reddit_comments_pslf_with_vader.csv"

    if os.path.exists(out) and os.path.getsize(out) > 100_000_000:
        print(f"  Already exists: {out} ({os.path.getsize(out)/1024/1024:.0f} MB)")
        return

    print(f"\nLoading {src}...")
    t0 = time.time()
    df = pd.read_csv(src, low_memory=False)
    print(f"  Loaded {len(df):,} rows in {time.time()-t0:.0f}s")

    if "vader_compound" in df.columns:
        print("  Already has vader_compound column")
    else:
        sia = SentimentIntensityAnalyzer()
        print("  Computing VADER compound on body text...")
        t0 = time.time()
        # Vectorize via list comprehension for speed
        bodies = df["body"].fillna("").astype(str).str.slice(0, 5000).tolist()
        compound = []
        for i in tqdm(range(0, len(bodies), 5000)):
            batch = bodies[i:i+5000]
            for b in batch:
                compound.append(sia.polarity_scores(b)["compound"])
        df["vader_compound"] = compound
        print(f"  Done in {time.time()-t0:.0f}s")

    print(f"\nSaving {out}...")
    df.to_csv(out, index=False)
    print(f"  Saved")

    # Quick correlation summary
    print("\nTextBlob polarity vs VADER compound (Pearson):")
    sub = df.dropna(subset=["polarity", "vader_compound"])
    print(f"  n={len(sub):,}, r={sub['polarity'].corr(sub['vader_compound']):.4f}")

    # Per-cohort
    sub = sub[sub.get("word_count", pd.Series(0, index=sub.index)) >= 5]
    if "post_subreddit" in sub.columns:
        for sr in ["PSLF", "StudentLoans", "personalfinance"]:
            ss = sub[sub["post_subreddit"] == sr]
            if len(ss) > 100:
                r = ss["polarity"].corr(ss["vader_compound"])
                print(f"  {sr:<22s} n={len(ss):>6,} r={r:.4f}")


if __name__ == "__main__":
    main()
