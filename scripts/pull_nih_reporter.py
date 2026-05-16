"""
pull_nih_reporter.py
====================
Pull NIH RePORTER total project costs aggregated by organization for
fiscal years 2018–2024, restricted to organizations that match NRMP
institution names.

API: https://api.reporter.nih.gov/  (no authentication; free)

NIH RePORTER does case-insensitive SUBSTRING matching on the org_names
criterion field. So "UNIVERSITY OF MIAMI" matches "UNIVERSITY OF MIAMI
SCHOOL OF MEDICINE" but "BALDWIN" does NOT match "SOUTH BALDWIN
REGIONAL MEDICAL CENTER" unless the latter has been registered under
exactly that string.

Strategy:
  1. Load unique NRMP institution names.
  2. For each institution, generate 1–3 normalized name candidates
     (full normalized name + state-qualifier + token-fallback).
  3. Pull total NIH award amount for each fiscal year.
  4. Save to nih_reporter_by_institution.csv.

For institutions without a match (no NIH funding), record award=0,
matched_name="" — this is the correct interpretation for community
hospitals, for-profit chains, etc.

Output schema:
  institution, state, fy, matched_org_name, total_award_amount, n_projects, match_strategy

Usage:
    python pull_nih_reporter.py --fy-start 2018 --fy-end 2024
"""

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


REPORTER_URL = "https://api.reporter.nih.gov/v2/projects/search"

# Map NRMP abbreviations → expanded names that NIH RePORTER understands
ABBREVIATION_EXPANSIONS = {
    r"\bMed Ctr\b": "MEDICAL CENTER",
    r"\bMem Hosp\b": "MEMORIAL HOSPITAL",
    r"\bMem\b": "MEMORIAL",
    r"\bReg Med Ctr\b": "REGIONAL MEDICAL CENTER",
    r"\bU of\b": "UNIVERSITY OF",
    r"\bU \b": "UNIVERSITY ",
    r"\bUniv\b": "UNIVERSITY",
    r"\bHealth Sci Ctr\b": "HEALTH SCIENCE CENTER",
    r"\bGrad Med Educ\b": "GRADUATE MEDICAL EDUCATION",
    r"\bSchool Of Med\b": "SCHOOL OF MEDICINE",
    r"\bSchool of Med\b": "SCHOOL OF MEDICINE",
    r"\bCollege Of Med\b": "COLLEGE OF MEDICINE",
    r"\bCollege of Med\b": "COLLEGE OF MEDICINE",
    r"\bGME\b": "",
    r"\bAssoc Prog\b": "",
    r"\bCons\b": "",
    r"\bChildrens\b": "CHILDREN'S",
    r"\bWomens\b": "WOMEN'S",
    r"\bSt\b\.?": "SAINT",
    r"\bMt\b\.?": "MOUNT",
    r"\bNYU\b": "NEW YORK UNIVERSITY",
    r"\bUSF\b": "UNIVERSITY OF SOUTH FLORIDA",
    r"\bUC\b": "UNIVERSITY OF CALIFORNIA",
    r"\bMSK\b": "MEMORIAL SLOAN KETTERING",
    r"\bVA\b": "VETERANS AFFAIRS",
}


def normalize_for_query(name: str) -> str:
    """Convert NRMP institution name to a NIH RePORTER-friendly query string."""
    s = str(name)
    for pattern, replacement in ABBREVIATION_EXPANSIONS.items():
        s = re.sub(pattern, replacement, s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip().upper()
    # Strip slashes and parenthetical material
    s = re.sub(r"\(.*?\)", "", s).strip()
    s = s.split("/")[0].strip()
    return s


# Suffixes commonly attached to NRMP institution names but absent from
# NIH RePORTER's official org_name registrations. Stripping these enables
# a parent-institution match.
PARENT_INSTITUTION_SUFFIXES = [
    "SCHOOL OF GRADUATE MEDICAL EDUCATION",
    "SCHOOL OF MEDICINE",
    "COLLEGE OF MEDICINE",
    "MEDICAL CENTER",
    "MEDICAL COLLEGE",
    "GRADUATE MEDICAL EDUCATION",
    "HEALTH SYSTEM",
    "HEALTHCARE SYSTEM",
    "HEALTH NETWORK",
    "HEALTH SCIENCES CENTER",
    "HEALTH SCIENCE CENTER",
    "HOSPITAL",
    "MEMORIAL",
    "REGIONAL",
    "ASSOCIATED",
    "CONSORTIUM",
]


def parent_institution_query(normalized: str) -> str | None:
    """Strip trailing suffixes to get a parent-institution query.
    Returns None if no shortening was possible."""
    s = normalized
    changed = False
    for suffix in PARENT_INSTITUTION_SUFFIXES:
        # Match suffix at end OR followed by another suffix
        pattern = rf"\s+{re.escape(suffix)}.*$"
        new = re.sub(pattern, "", s)
        if new != s:
            s = new
            changed = True
    s = s.strip()
    if changed and len(s) >= 5:
        return s
    return None


def query_total(session: requests.Session, org_query: str, fy: int,
                rate_limit_sec: float = 0.5, state_filter: str = None) -> tuple[float, int, str]:
    """Query NIH RePORTER for total award amount + project count.
    Returns (total_award, n_projects, matched_org_name_sample).

    If state_filter is provided, restricts to matching org_state."""
    payload = {
        "criteria": {"fiscal_years": [fy], "org_names": [org_query]},
        "include_fields": ["ProjectNum", "Organization", "AwardAmount"],
        "limit": 500,
        "offset": 0,
    }
    if state_filter:
        # NIH RePORTER uses 2-letter state codes
        payload["criteria"]["org_states"] = [state_filter.upper()]
    total = 0.0
    n_projects = 0
    matched_org = ""
    while True:
        try:
            r = session.post(REPORTER_URL, json=payload, timeout=30)
        except Exception as e:
            print(f"    [WARN] API error for '{org_query}' FY{fy}: {e}")
            return 0.0, 0, ""
        if r.status_code != 200:
            return 0.0, 0, ""
        data = r.json()
        results = data.get("results", [])
        for proj in results:
            amt = proj.get("award_amount") or 0
            try:
                total += float(amt)
            except (TypeError, ValueError):
                pass
            n_projects += 1
            if not matched_org:
                org = proj.get("organization", {})
                matched_org = org.get("org_name", "") if org else ""
        meta = data.get("meta", {})
        api_total = meta.get("total", 0)
        if n_projects >= api_total or len(results) == 0:
            break
        payload["offset"] = n_projects
        time.sleep(rate_limit_sec)
    return total, n_projects, matched_org


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nrmp-csv", default="C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/nrmp_program_level_2021_2025.csv")
    parser.add_argument("--output", default="C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/nih_reporter_by_institution.csv")
    parser.add_argument("--fy-start", type=int, default=2018)
    parser.add_argument("--fy-end", type=int, default=2024)
    parser.add_argument("--limit-institutions", type=int, default=0,
                        help="Cap institution count for testing (0=all)")
    parser.add_argument("--rate-limit-sec", type=float, default=0.5)
    args = parser.parse_args()

    df = pd.read_csv(args.nrmp_csv)
    inst_state = df.groupby("institution")["state"].first()
    institutions = list(inst_state.index)
    if args.limit_institutions > 0:
        institutions = institutions[:args.limit_institutions]
    fys = list(range(args.fy_start, args.fy_end + 1))
    n_calls = len(institutions) * len(fys)
    print(f"NIH RePORTER pull")
    print(f"  Institutions: {len(institutions)}")
    print(f"  Fiscal years: {fys}")
    print(f"  Estimated API calls: {n_calls}")
    print(f"  Estimated wall-time: {n_calls * args.rate_limit_sec / 60:.1f} min (sequential)")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "PSLF-residency-research/1.0",
        "Content-Type": "application/json",
    })

    rows = []
    for inst in tqdm(institutions, desc="NIH RePORTER"):
        state = inst_state.get(inst, "")
        normalized = normalize_for_query(inst)
        parent = parent_institution_query(normalized)

        for fy in fys:
            # Strategy 1: full normalized name + state filter (most specific)
            total, n, matched = query_total(session, normalized, fy, args.rate_limit_sec,
                                              state_filter=state)
            strategy = "full_normalized_with_state"
            time.sleep(args.rate_limit_sec)

            # Strategy 2: parent institution + state filter
            if total == 0.0 and n == 0 and parent and parent != normalized:
                total2, n2, matched2 = query_total(session, parent, fy, args.rate_limit_sec,
                                                    state_filter=state)
                time.sleep(args.rate_limit_sec)
                if n2 > 0:
                    total, n, matched = total2, n2, matched2
                    strategy = "parent_institution_with_state"

            # Strategy 3: first 3 distinctive tokens + state filter (last-resort)
            if total == 0.0 and n == 0:
                tokens = normalized.split()
                generic = {"OF", "AT", "AND", "THE", "FOR", "MEDICAL", "HOSPITAL",
                           "HEALTH", "CENTER", "CENTRE", "UNIVERSITY", "COLLEGE",
                           "SCHOOL", "SYSTEM", "REGIONAL", "MEMORIAL"}
                distinctive = [t for t in tokens if t not in generic and len(t) >= 4]
                if len(distinctive) >= 2:
                    short = " ".join(distinctive[:3])
                    total3, n3, matched3 = query_total(session, short, fy, args.rate_limit_sec,
                                                        state_filter=state)
                    time.sleep(args.rate_limit_sec)
                    if n3 > 0:
                        total, n, matched = total3, n3, matched3
                        strategy = "distinctive_tokens_with_state"

            rows.append({
                "institution": inst,
                "state": state,
                "fy": fy,
                "normalized_query": normalized,
                "parent_query": parent or "",
                "matched_org_name": matched,
                "total_award_amount": total,
                "n_projects": n,
                "match_strategy": strategy if n > 0 else "no_match",
            })

    out_df = pd.DataFrame(rows)
    out_df.to_csv(args.output, index=False)
    print(f"\nSaved: {args.output}")
    print(f"  Rows: {len(out_df)}")
    inst_match = out_df.groupby('institution')['n_projects'].sum() > 0
    print(f"  Institutions with at least one match: {inst_match.sum()} / {inst_match.shape[0]}")
    print(f"  Total $ matched across all FYs: ${out_df['total_award_amount'].sum() / 1e9:.2f}B")
    print()
    print(f"  Top 10 by FY-aggregate award amount:")
    top = out_df.groupby('institution')['total_award_amount'].sum().nlargest(10)
    for inst, amt in top.items():
        print(f"    {inst[:50]:50} ${amt/1e6:>10.1f}M")


if __name__ == "__main__":
    main()
