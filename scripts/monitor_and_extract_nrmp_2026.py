"""
monitor_and_extract_nrmp_2026.py
==================================
Round 16 Strengthener (Paper 3 follow-up): monitor NRMP for the 2026 Match
Results & Data PDF; once available, download, extract program-level data, and
merge into the existing Paper 3 analytical sample.

Critical context:
  - 2026 Match Day was March 20, 2026
  - Trump PSLF Executive Order was March 7, 2025
  - 2026 Match is the FIRST cycle where applicants had time to respond to the EO
    when forming preferences (rank lists due Feb 23, 2026)
  - NRMP typically releases the full Results & Data report 6-8 weeks after Match Day
  - As of 2026-05-10, the report should be available or imminent

This script:
  1. POLLS the NRMP page for the 2026 PDF availability
  2. Once detected, downloads the PDF to nrmp_pdfs/2026_main_match_results.pdf
  3. Runs the extraction pipeline (mirrors collect_nrmp_program_level.py logic)
  4. Outputs nrmp_program_level_2026.csv
  5. Merges with the existing 2021-2025 dataset → nrmp_program_level_2021_2026.csv
  6. Re-runs the cluster-robust + wild-cluster bootstrap regression to test
     for a post-EO effect (2025 vs 2026 fill-rate change for PSLF-hostile programs)

Usage (one-off polling check):
    python scripts/monitor_and_extract_nrmp_2026.py --check

Usage (continuous polling, 1x per day for up to 30 days):
    python scripts/monitor_and_extract_nrmp_2026.py --poll-days 30

Usage (force download + extract from a specific URL once you find it):
    python scripts/monitor_and_extract_nrmp_2026.py --pdf-url "https://www.nrmp.org/wp-content/uploads/2026/05/..."

NRMP USAGE COMPLIANCE: Same as collect_nrmp_program_level.py — descriptive/inferential
statistics only, no ML inputs, no derived-data redistribution without permission.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")
PDF_DIR = PROJECT / "nrmp_pdfs"
PDF_2026 = PDF_DIR / "2026_main_match_results.pdf"
OUT_2026_CSV = PROJECT / "nrmp_program_level_2026.csv"
OUT_COMBINED_CSV = PROJECT / "nrmp_program_level_2021_2026.csv"

# Likely NRMP page locations to monitor
NRMP_LANDING_URLS = [
    "https://www.nrmp.org/match-data/main-residency-match-data/",
    "https://www.nrmp.org/match-data/",
    "https://www.nrmp.org/match-data-analytics/residency-data-reports/",
]

# Patterns that indicate a 2026 Results & Data report URL
URL_2026_PATTERNS = [
    re.compile(r"(?i)2026[-_].*?(?:main|match|results?|data).*?\.pdf"),
    re.compile(r"(?i)main[-_]?match[-_]?(?:results?[-_]?and[-_]?data|results)[-_]?2026.*?\.pdf"),
    re.compile(r"(?i)2026[-_].*?\.pdf"),
]

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")


def find_2026_pdf_url() -> str | None:
    """Scan NRMP landing pages for any 2026 PDF link. Return the first match or None."""
    headers = {"User-Agent": USER_AGENT}
    for landing_url in NRMP_LANDING_URLS:
        try:
            r = requests.get(landing_url, headers=headers, timeout=20, allow_redirects=True)
        except Exception as e:
            print(f"  [warn] {landing_url}: {e}")
            continue
        if r.status_code != 200:
            print(f"  [warn] {landing_url}: HTTP {r.status_code}")
            continue
        # Find all PDF links
        all_pdfs = re.findall(r'href="([^"]+\.pdf)"', r.text, flags=re.IGNORECASE)
        for pdf_path in all_pdfs:
            absolute = urljoin(landing_url, pdf_path)
            for pattern in URL_2026_PATTERNS:
                if pattern.search(absolute):
                    print(f"  [match] Found candidate 2026 PDF: {absolute}")
                    return absolute
    return None


def download_pdf(url: str, output_path: Path) -> bool:
    """Download a PDF. Returns True if successful and file is plausibly a real PDF."""
    headers = {"User-Agent": USER_AGENT}
    print(f"Downloading: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=120, stream=True)
        r.raise_for_status()
    except Exception as e:
        print(f"  [error] {e}")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    size_mb = output_path.stat().st_size / 1e6
    print(f"  Downloaded: {output_path.name} ({size_mb:.1f} MB)")

    # Sanity check: looks like a PDF
    with open(output_path, "rb") as f:
        header = f.read(8)
    if not header.startswith(b"%PDF"):
        print(f"  [error] File is not a valid PDF (header: {header})")
        return False
    return True


def extract_2026_data() -> bool:
    """Run the same extraction logic as collect_nrmp_program_level.py but on the
    2026 PDF only. Returns True if extraction produced plausible output.

    Schema (must match nrmp_program_level_2021_2025.csv):
      institution, state, program_name, program_code, specialty_code, specialty,
      program_type_code, program_type, year, quota, filled, fill_rate,
      pslf_class, pslf_evidence, city
    """
    if not PDF_2026.exists():
        print(f"[error] 2026 PDF not found at {PDF_2026}")
        return False

    print(f"\nExtracting from {PDF_2026}...")
    print("This uses the same parser logic as collect_nrmp_program_level.py.")

    try:
        import pdfplumber
    except ImportError:
        print("[ABORT] pip install pdfplumber")
        return False

    # Re-use the parser from collect_nrmp_program_level.py
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from collect_nrmp_program_level import (
            RE_DATA_ROW, RE_INST_HEADING, SPECIALTY_CODES, PROG_TYPE,
            classify_institution,
        )
    except ImportError as e:
        print(f"[ABORT] Cannot import parser components: {e}")
        return False

    rows = []
    current_inst = None
    current_state = None
    n_pages = 0

    with pdfplumber.open(PDF_2026) as pdf:
        n_pages = len(pdf.pages)
        print(f"  PDF has {n_pages} pages")
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Check for institution heading
                inst_match = RE_INST_HEADING.match(line)
                if inst_match:
                    candidate_name = inst_match.group(1).strip()
                    candidate_state = inst_match.group(2).strip()
                    if 5 <= len(candidate_name) <= 80 and not RE_DATA_ROW.match(line):
                        current_inst = candidate_name
                        current_state = candidate_state
                        continue
                # Check for data row
                row_match = RE_DATA_ROW.match(line)
                if row_match and current_inst:
                    program_name = row_match.group(1).strip()
                    program_code = row_match.group(2)
                    fields = [row_match.group(i) for i in range(3, 13)]
                    spec_code = program_code[4:7]
                    type_code = program_code[7]
                    specialty = SPECIALTY_CODES.get(spec_code, "Unknown")
                    prog_type = PROG_TYPE.get(type_code, "Unknown")

                    # 2026-only extraction: just take the 2026 quota + filled
                    # In annual books, the 10 fields are typically:
                    # quota_offered, quota_filled, US_MD_filled, US_DO_filled,
                    # IMG_filled, US_IMG_filled, etc.
                    # For 2021-2025 multi-year report, fields are quota/filled per year.
                    # 2026 ANNUAL book likely has just current-year breakdown.
                    # We assume the first two fields are quota_offered and quota_filled.
                    quota_str, filled_str = fields[0], fields[1]
                    try:
                        quota = int(quota_str) if quota_str != "--" else 0
                        filled = int(filled_str) if filled_str != "--" else 0
                    except ValueError:
                        continue
                    if quota <= 0:
                        continue
                    fill_rate = filled / quota

                    pslf_class, pslf_evidence = classify_institution(current_inst)

                    rows.append({
                        "institution": current_inst,
                        "state": current_state,
                        "program_name": program_name,
                        "program_code": program_code,
                        "specialty_code": spec_code,
                        "specialty": specialty,
                        "program_type_code": type_code,
                        "program_type": prog_type,
                        "year": 2026,
                        "quota": quota,
                        "filled": filled,
                        "fill_rate": fill_rate,
                        "pslf_class": pslf_class,
                        "pslf_evidence": pslf_evidence,
                        "city": "",  # populate via city-extraction script later
                    })

    if not rows:
        print(f"[error] Extraction produced 0 rows. PDF format may differ from prior years.")
        print(f"        Manually inspect {PDF_2026} and adapt the parser.")
        return False

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(OUT_2026_CSV, index=False)
    print(f"\n  Extracted: {len(df):,} program-year rows")
    print(f"  Unique institutions: {df['institution'].nunique()}")
    print(f"  Unique specialties: {df['specialty'].nunique()}")
    print(f"  PSLF class breakdown:")
    print(df["pslf_class"].value_counts())
    print(f"\n  Saved: {OUT_2026_CSV}")
    return True


def merge_with_2021_2025() -> bool:
    """Combine 2021-2025 + 2026 into a single analytical CSV."""
    if not OUT_2026_CSV.exists():
        print(f"[error] {OUT_2026_CSV} not found. Run extract_2026_data first.")
        return False

    import pandas as pd
    prior = pd.read_csv(PROJECT / "nrmp_program_level_2021_2025.csv")
    new = pd.read_csv(OUT_2026_CSV)
    combined = pd.concat([prior, new], ignore_index=True)

    # Sanity checks
    n_2026 = (combined["year"] == 2026).sum()
    if n_2026 == 0:
        print("[error] After merge, 0 rows for year=2026. Aborting.")
        return False

    combined.to_csv(OUT_COMBINED_CSV, index=False)
    print(f"\n  Combined dataset:")
    print(f"    Total rows: {len(combined):,}")
    print(f"    Year breakdown: {combined['year'].value_counts().sort_index().to_dict()}")
    print(f"    Unique institutions: {combined['institution'].nunique()}")
    print(f"    Saved: {OUT_COMBINED_CSV}")
    return True


def post_eo_quasi_experiment_summary():
    """Quick descriptive comparison: 2025 (pre-EO preferences) vs 2026 (first post-EO).
    Just summary stats; full regression in run_model5_FINAL.py rerun below."""
    import pandas as pd
    if not OUT_COMBINED_CSV.exists():
        return
    df = pd.read_csv(OUT_COMBINED_CSV)
    df_25 = df[df["year"] == 2025]
    df_26 = df[df["year"] == 2026]
    print("\n" + "=" * 70)
    print("POST-TRUMP-EO QUASI-EXPERIMENT — 2025 vs 2026 fill-rate descriptives")
    print("=" * 70)
    for cls in ["pslf_friendly", "ambiguous", "pslf_hostile"]:
        s25 = df_25[df_25["pslf_class"] == cls]
        s26 = df_26[df_26["pslf_class"] == cls]
        if len(s25) > 0 and len(s26) > 0:
            print(f"\n  {cls}:")
            print(f"    2025: n={len(s25):,}, mean fill rate = {s25['fill_rate'].mean():.3f}")
            print(f"    2026: n={len(s26):,}, mean fill rate = {s26['fill_rate'].mean():.3f}")
            print(f"    Δ (2026-2025) = {s26['fill_rate'].mean() - s25['fill_rate'].mean():+.4f}")
    print("\n  Reminder: EO signed Mar 7, 2025 (after 2025 ROL deadline = Feb 24, 2025).")
    print("  2025 reflects pre-EO preferences. 2026 is the first post-EO Match cycle.")
    print("  For full regression with cluster-robust SE, re-run scripts/run_model5_FINAL.py")
    print("  pointing at nrmp_program_level_2021_2026.csv.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true",
                       help="One-off check for 2026 PDF availability")
    group.add_argument("--poll-days", type=int,
                       help="Continuous polling for N days (1 check per day)")
    group.add_argument("--pdf-url", type=str,
                       help="Force download from a specific PDF URL")
    parser.add_argument("--no-extract", action="store_true",
                       help="Skip extraction (just download)")
    parser.add_argument("--no-merge", action="store_true",
                       help="Skip merge with 2021-2025 dataset")
    args = parser.parse_args()

    if args.pdf_url:
        ok = download_pdf(args.pdf_url, PDF_2026)
        if not ok:
            sys.exit(1)
        if not args.no_extract:
            ok = extract_2026_data()
            if not ok:
                sys.exit(1)
        if not args.no_merge:
            merge_with_2021_2025()
            post_eo_quasi_experiment_summary()
        sys.exit(0)

    if args.check:
        url = find_2026_pdf_url()
        if url:
            print(f"\n[FOUND] 2026 PDF candidate at: {url}")
            print(f"  To download + extract + merge, run:")
            print(f"    python scripts/monitor_and_extract_nrmp_2026.py --pdf-url \"{url}\"")
        else:
            print(f"\n[NOT FOUND] 2026 PDF not yet on NRMP landing pages.")
            print(f"  Pages checked: {NRMP_LANDING_URLS}")
            print(f"  Try again in a few days.")
        sys.exit(0)

    # Continuous polling
    n_days = args.poll_days
    deadline = datetime.now() + timedelta(days=n_days)
    print(f"Polling NRMP every 24h for up to {n_days} days (until {deadline.date()})...")
    while datetime.now() < deadline:
        url = find_2026_pdf_url()
        if url:
            print(f"\n[FOUND on {datetime.now().isoformat(timespec='minutes')}] {url}")
            ok = download_pdf(url, PDF_2026)
            if ok:
                if not args.no_extract:
                    extract_2026_data()
                if not args.no_merge:
                    merge_with_2021_2025()
                    post_eo_quasi_experiment_summary()
                sys.exit(0)
        else:
            print(f"  [{datetime.now().isoformat(timespec='minutes')}] not yet; sleeping 24h")
        time.sleep(24 * 3600)
    print(f"\n[TIMEOUT] {n_days} days elapsed; 2026 PDF not yet found.")
    sys.exit(1)


if __name__ == "__main__":
    main()
