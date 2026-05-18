"""
score_vader_arctic_shift.py
===========================
One-time VADER scoring of the Arctic Shift PSLF posts. Adds vader_compound,
vader_pos, vader_neg, vader_neu columns in-place. TextBlob polarity is
already in the file (the collector ran TextBlob inline).

Usage:
  python score_vader_arctic_shift.py
"""
from __future__ import annotations

import io
import os
import sys
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import numpy as np
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

INPUT = "reddit_arctic_shift_pslf.csv"
OUTPUT = "reddit_arctic_shift_pslf.csv"  # in-place


def main():
    print(f"Loading {INPUT}...")
    df = pd.read_csv(INPUT)
    print(f"  Rows: {len(df):,}")

    if "vader_compound" in df.columns and df["vader_compound"].notna().sum() > 0:
        print("VADER already scored (vader_compound column present, non-null). Skipping.")
        return

    text_col = ("combined_text" if "combined_text" in df.columns else
                "selftext" if "selftext" in df.columns else "body")
    print(f"Scoring VADER on {text_col}...")
    sia = SentimentIntensityAnalyzer()
    bodies = df[text_col].fillna("").astype(str).tolist()
    n = len(bodies)

    compounds = np.empty(n, dtype=float)
    poses = np.empty(n, dtype=float)
    negs = np.empty(n, dtype=float)
    neus = np.empty(n, dtype=float)
    for i, b in enumerate(bodies):
        if not b:
            compounds[i] = poses[i] = negs[i] = neus[i] = np.nan
        else:
            try:
                s = sia.polarity_scores(b[:5000])
                compounds[i] = s["compound"]
                poses[i] = s["pos"]
                negs[i] = s["neg"]
                neus[i] = s["neu"]
            except Exception:
                compounds[i] = poses[i] = negs[i] = neus[i] = np.nan
        if (i + 1) % 5000 == 0:
            print(f"  {i+1:,}/{n:,} scored")

    df["vader_compound"] = compounds
    df["vader_pos"] = poses
    df["vader_neg"] = negs
    df["vader_neu"] = neus
    print(f"Saving {OUTPUT} ({len(df):,} rows)...")
    df.to_csv(OUTPUT, index=False)
    print(f"Done. {df['vader_compound'].notna().sum():,} posts have valid VADER scores.")


if __name__ == "__main__":
    main()
