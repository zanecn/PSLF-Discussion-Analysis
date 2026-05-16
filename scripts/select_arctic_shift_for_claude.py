"""
select_arctic_shift_for_claude.py
==================================
Picks a stratified subset of Arctic Shift PSLF posts for Claude scoring,
optimized for analytical value per dollar.

Strategy:
  1. Restrict to posts within +/-90d of any of the 8 canonical events
  2. For each (event x profession) cell, count existing Claude coverage
     across all zeroshot_*.csv files
  3. Sample Arctic Shift posts to bring each cell up to TARGET_N (default 100)
     Claude-scored total. Cells already at target are skipped.
  4. Cap total at MAX_TOTAL (default 5,000) to control spend (~$25 at $0.005/post)
  5. Write a CSV in the input format `sentiment_zeroshot.py` expects.

Usage:
  python select_arctic_shift_for_claude.py
  python select_arctic_shift_for_claude.py --target-n 200 --max-total 10000
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

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

ZEROSHOT_CSVS = [
    "zeroshot_reddit_n1000.csv",
    "zeroshot_sdn_n1000.csv",
    "zeroshot_reddit_eventstrat.csv",
    "zeroshot_reddit_eventfull.csv",
    "zeroshot_sdn_eventfull.csv",
    "zeroshot_pa_np_expansion.csv",
    "zeroshot_reddit_fullcorpus.csv",
]


def load_existing_coverage() -> pd.DataFrame:
    """Load all existing Claude-scored posts and tag with (event, profession).
    A post is in an event window if its date is within +/-window_days of the event.
    """
    frames = []
    for f in ZEROSHOT_CSVS:
        if not os.path.exists(f):
            continue
        d = pd.read_csv(f)
        if "post_id" not in d.columns or "profession" not in d.columns:
            continue
        d = d[~d["pslf_sentiment"].isin(["parse_error", "api_error"])][
            ["post_id", "profession"]].copy()
        d["zeroshot_csv"] = f
        frames.append(d)
    if not frames:
        return pd.DataFrame(columns=["post_id", "profession", "event"])

    existing = pd.concat(frames, ignore_index=True).drop_duplicates("post_id")
    print(f"  Loaded {len(existing):,} unique already-scored posts across "
          f"{len(frames)} zeroshot CSVs")

    # We need dates to assign event windows. Pull from source CSVs.
    # Reddit:
    src = []
    for fpath in ["reddit_professions_pslf.csv",
                   "comprehensive_medical_pslf_discussions.csv",
                   "comprehensive_teacher_pslf_discussions.csv",
                   "reddit_new_subs_pslf.csv",
                   "reddit_arctic_shift_pslf.csv"]:
        if os.path.exists(fpath):
            d = pd.read_csv(fpath, usecols=lambda c: c in ("id", "created_utc"))
            d = d.rename(columns={"id": "post_id"})
            d["date"] = pd.to_datetime(pd.to_numeric(d["created_utc"], errors="coerce"),
                                       unit="s")
            src.append(d[["post_id", "date"]])
    # SDN:
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv",
                         usecols=lambda c: c in ("post_id", "date_posted"))
        d["date"] = pd.to_datetime(d["date_posted"], errors="coerce", utc=True).dt.tz_localize(None)
        src.append(d[["post_id", "date"]])
    src_dates = pd.concat(src, ignore_index=True).drop_duplicates("post_id")
    existing = existing.merge(src_dates, on="post_id", how="left")

    # Assign event window membership (a post can be in multiple event windows)
    rows = []
    for _, r in existing.iterrows():
        if pd.isna(r["date"]):
            rows.append({"post_id": r["post_id"], "profession": r["profession"], "event": "OUT_OF_WINDOW"})
            continue
        in_any = False
        for ev_name, ev_date, win in EVENTS:
            dt = pd.Timestamp(ev_date)
            if dt - pd.Timedelta(days=win) <= r["date"] <= dt + pd.Timedelta(days=win):
                rows.append({"post_id": r["post_id"], "profession": r["profession"], "event": ev_name})
                in_any = True
        if not in_any:
            rows.append({"post_id": r["post_id"], "profession": r["profession"], "event": "OUT_OF_WINDOW"})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--target-n", type=int, default=100,
                        help="Target Claude-scored posts per (event, profession) cell")
    parser.add_argument("--max-total", type=int, default=5000,
                        help="Max total posts to select (cost cap)")
    parser.add_argument("--output", default="arctic_shift_for_claude.csv",
                        help="Output CSV in sentiment_zeroshot.py input format")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("=" * 80)
    print("Selecting stratified Arctic Shift sample for Claude scoring")
    print("=" * 80)

    print("\nStep 1: Loading existing Claude coverage...")
    existing = load_existing_coverage()
    coverage_in_window = (existing[existing["event"] != "OUT_OF_WINDOW"]
                          .groupby(["event", "profession"]).size()
                          .reset_index(name="claude_n"))

    print("\nExisting Claude coverage by (event, profession):")
    print(coverage_in_window.pivot_table(index="profession", columns="event",
                                          values="claude_n", fill_value=0).to_string())

    print("\nStep 2: Loading Arctic Shift posts and tagging by event window...")
    ar = pd.read_csv("reddit_arctic_shift_pslf.csv")
    ar["date"] = pd.to_datetime(pd.to_numeric(ar["created_utc"], errors="coerce"), unit="s")
    # Already-scored Arctic Shift post_ids to exclude
    already = set(existing["post_id"].astype(str))
    ar = ar[~ar["id"].astype(str).isin(already)].copy()
    print(f"  Arctic Shift candidates (excluding already-scored): {len(ar):,}")

    # Tag each Arctic Shift post by which event windows it falls in (can be multiple)
    ar_event_rows = []
    for _, r in ar.iterrows():
        if pd.isna(r["date"]):
            continue
        for ev_name, ev_date, win in EVENTS:
            dt = pd.Timestamp(ev_date)
            if dt - pd.Timedelta(days=win) <= r["date"] <= dt + pd.Timedelta(days=win):
                ar_event_rows.append({
                    "id": r["id"],
                    "subreddit": r.get("subreddit", ""),
                    "profession": r.get("profession", ""),
                    "title": r.get("title", ""),
                    "combined_text": r.get("combined_text", r.get("selftext", "")),
                    "created_utc": r["created_utc"],
                    "date": r["date"],
                    "event": ev_name,
                    "word_count": r.get("word_count", 0),
                })
    arw = pd.DataFrame(ar_event_rows)
    print(f"  Arctic Shift posts in any event window: "
          f"{arw['id'].nunique():,} unique posts ({len(arw):,} (post, event) rows)")

    print("\nStep 3: Computing per-cell deficits (target_n - existing_n)...")
    coverage_dict = {}
    for _, r in coverage_in_window.iterrows():
        coverage_dict[(r["event"], r["profession"])] = r["claude_n"]

    cells = []
    for ev_name, _, _ in EVENTS:
        for prof in arw["profession"].dropna().unique():
            existing_n = coverage_dict.get((ev_name, prof), 0)
            deficit = max(args.target_n - existing_n, 0)
            cells.append({
                "event": ev_name,
                "profession": prof,
                "existing": existing_n,
                "deficit": deficit,
            })
    deficits = pd.DataFrame(cells).sort_values("deficit", ascending=False)
    print(deficits.head(20).to_string(index=False))

    print(f"\nStep 4: Sampling Arctic Shift posts to fill deficits "
          f"(cap {args.max_total:,} total)...")
    rng = np.random.default_rng(args.seed)
    selected_ids = set()
    per_cell_picks = []
    # Process cells in order of largest deficit first (so under-served cells get filled)
    for _, c in deficits.iterrows():
        if len(selected_ids) >= args.max_total:
            break
        if c["deficit"] <= 0:
            continue
        # Candidates: Arctic Shift posts in this (event, profession) cell that
        # haven't already been selected
        cand = arw[(arw["event"] == c["event"]) & (arw["profession"] == c["profession"]) &
                   (~arw["id"].isin(selected_ids))]
        cand_unique = cand.drop_duplicates("id")
        n_take = min(c["deficit"], len(cand_unique),
                     args.max_total - len(selected_ids))
        if n_take <= 0:
            continue
        take_idx = rng.choice(cand_unique.index, size=n_take, replace=False)
        take_ids = cand_unique.loc[take_idx, "id"].tolist()
        selected_ids.update(take_ids)
        per_cell_picks.append({
            "event": c["event"], "profession": c["profession"],
            "existing": c["existing"], "deficit": c["deficit"],
            "available": len(cand_unique), "picked": n_take,
            "ending_total": c["existing"] + n_take,
        })

    picks = pd.DataFrame(per_cell_picks)
    print("\nPer-cell picks (sorted by ending total Claude n):")
    print(picks.sort_values("ending_total", ascending=False).head(40).to_string(index=False))

    print(f"\nTotal Arctic Shift posts selected: {len(selected_ids):,}")
    print(f"Estimated Claude cost (~$0.005/post): ${len(selected_ids)*0.005:.2f}")

    # Write output CSV in the format sentiment_zeroshot.py expects
    sel = arw[arw["id"].isin(selected_ids)].drop_duplicates("id").copy()
    out_cols = ["id", "subreddit", "profession", "title", "combined_text",
                "created_utc", "word_count"]
    sel[out_cols].to_csv(args.output, index=False)
    print(f"\nSaved: {args.output}")
    print(f"Now run: python sentiment_zeroshot.py "
          f"--input {args.output} --output zeroshot_reddit_arctic_shift_fill.csv")


if __name__ == "__main__":
    main()
