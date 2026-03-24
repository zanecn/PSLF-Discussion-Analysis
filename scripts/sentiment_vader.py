"""
sentiment_vader.py
==================
Adds VADER sentiment scores to existing CSV files as new columns.

VADER (Valence Aware Dictionary and sEntiment Reasoner) is purpose-built
for social media text — handles caps, punctuation, emoji, slang, negation.

Adds columns: vader_compound, vader_pos, vader_neg, vader_neu

Usage:
    python sentiment_vader.py --input reddit_professions_pslf.csv
    python sentiment_vader.py --input forum_pslf_discussions.csv
    python sentiment_vader.py --input comprehensive_medical_pslf_discussions.csv
"""

import argparse
import os
import sys

import pandas as pd
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def add_vader_scores(df: pd.DataFrame, text_col: str) -> pd.DataFrame:
    """Add VADER sentiment columns to DataFrame."""
    analyzer = SentimentIntensityAnalyzer()

    compounds = []
    positives = []
    negatives = []
    neutrals = []

    for text in tqdm(df[text_col].fillna(""), desc="VADER scoring"):
        if not text.strip():
            compounds.append(float("nan"))
            positives.append(float("nan"))
            negatives.append(float("nan"))
            neutrals.append(float("nan"))
            continue

        # VADER works best on shorter texts; cap at 5000 chars
        scores = analyzer.polarity_scores(text[:5000])
        compounds.append(scores["compound"])
        positives.append(scores["pos"])
        negatives.append(scores["neg"])
        neutrals.append(scores["neu"])

    df["vader_compound"] = compounds
    df["vader_pos"] = positives
    df["vader_neg"] = negatives
    df["vader_neu"] = neutrals

    return df


def main():
    parser = argparse.ArgumentParser(description="Add VADER sentiment to CSV")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", default="", help="Output CSV (default: overwrite input)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] File not found: {args.input}")
        sys.exit(1)

    df = pd.read_csv(args.input)
    print(f"Loaded {len(df):,} rows from {args.input}")

    # Detect text column
    if "combined_text" in df.columns:
        text_col = "combined_text"
    elif "body" in df.columns:
        text_col = "body"
    elif "text" in df.columns:
        text_col = "text"
    else:
        print("[ERROR] No text column found")
        sys.exit(1)

    print(f"Using text column: {text_col}")

    # Check if already scored
    if "vader_compound" in df.columns:
        existing = df["vader_compound"].notna().sum()
        print(f"  Already has {existing:,} VADER scores — re-scoring all")

    df = add_vader_scores(df, text_col)

    # Summary
    valid = df["vader_compound"].dropna()
    print(f"\n{'='*60}")
    print(f"VADER Scoring Complete")
    print(f"  Scored: {len(valid):,}/{len(df):,}")
    print(f"  Mean compound: {valid.mean():.4f}")
    print(f"  % Negative (compound < -0.05): {(valid < -0.05).mean()*100:.1f}%")
    print(f"  % Neutral (-0.05 to 0.05): {((valid >= -0.05) & (valid <= 0.05)).mean()*100:.1f}%")
    print(f"  % Positive (compound > 0.05): {(valid > 0.05).mean()*100:.1f}%")

    # Compare with TextBlob if available
    if "polarity" in df.columns:
        both = df[["polarity", "vader_compound"]].dropna()
        if len(both) > 10:
            corr = both["polarity"].corr(both["vader_compound"])
            print(f"\n  TextBlob vs VADER correlation: r={corr:.3f}")

    # Save
    output = args.output or args.input
    df.to_csv(output, index=False)
    print(f"  Saved: {output}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
