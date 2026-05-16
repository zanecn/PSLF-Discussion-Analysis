"""
extract_nrmp_cities.py
========================
Quick city-extractor from the NRMP 2021-2025 Program Results PDF.

Pattern: institution heading "X-STATE" is followed by line "City Program 2025 2024..."
which gives the city name. Build {institution: city} dict and merge into the
existing nrmp_program_level_2021_2025.csv.

Output: nrmp_program_level_2021_2025.csv (updated with city column populated)
        nrmp_institution_city_lookup.csv
"""
from __future__ import annotations
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import pandas as pd

try:
    import pdfplumber
except ImportError:
    print("[ABORT] pip install pdfplumber"); sys.exit(1)

PDF_PATH = "nrmp_pdfs/2021_2025_program_results.pdf"

STATE_SUFFIXES = set([
    "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH",
    "NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT",
    "VT","VA","WA","WV","WI","WY","PR",
])

RE_INST_HEADING = re.compile(r"^(.*?)-([A-Z]{2})\s*$")
# City line: "<City Name> Program 2025 2024 2023 2022 2021"
RE_CITY = re.compile(r"^([A-Z][a-zA-Z\s\-]{1,40}?)\s+Program\s+2025\s+2024\s+2023\s+2022\s+2021\s*$")


def main():
    print("Extracting NRMP institution -> city lookup...")
    inst_to_city = {}  # (institution, state) -> city

    with pdfplumber.open(PDF_PATH) as pdf:
        current = None
        for pg_idx in range(6, len(pdf.pages)):  # data starts page 7
            text = pdf.pages[pg_idx].extract_text() or ""
            for ln in text.split("\n"):
                ln = ln.strip()
                if not ln: continue
                # Institution heading
                m = RE_INST_HEADING.match(ln)
                if m and m.group(2) in STATE_SUFFIXES:
                    name = m.group(1).strip()
                    state = m.group(2)
                    if len(name) >= 3:
                        current = (name, state)
                        continue
                # City line
                m = RE_CITY.match(ln)
                if m and current:
                    city = m.group(1).strip()
                    inst_to_city[current] = city
                    current = None  # reset after city captured

    print(f"Captured cities for {len(inst_to_city):,} institution-state pairs")

    # Save lookup
    lookup_df = pd.DataFrame([
        {"institution": k[0], "state": k[1], "city": v}
        for k, v in inst_to_city.items()
    ])
    lookup_df.to_csv("nrmp_institution_city_lookup.csv", index=False)
    print(f"Saved: nrmp_institution_city_lookup.csv ({len(lookup_df):,} rows)")

    # Merge into main NRMP CSV
    main_df = pd.read_csv("nrmp_program_level_2021_2025.csv")
    main_df = main_df.drop(columns=["city"], errors="ignore")
    main_df = main_df.merge(lookup_df, on=["institution", "state"], how="left")
    main_df.to_csv("nrmp_program_level_2021_2025.csv", index=False)
    print(f"Updated: nrmp_program_level_2021_2025.csv (city column populated)")
    n_with_city = main_df["city"].notna().sum()
    print(f"  Rows with city: {n_with_city:,} / {len(main_df):,} "
           f"({n_with_city/len(main_df)*100:.1f}%)")


if __name__ == "__main__":
    main()
