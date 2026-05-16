"""
collect_nrmp_program_level.py
==============================
B5: Extract NRMP program-level fill data from "Program Results: Main Residency
Match 2021-2025 Appointment Years" PDF and earlier annual Results-and-Data PDFs.

What this gives us that specialty-level NRMP data does not:
  - Per-institution (sponsoring institution) fill rates
  - Program-type classification (academic vs community vs private/for-profit)
  - PSLF-eligibility heuristic (academic medical center / VA / military / nonprofit
    teaching hospital -> PSLF-friendly; for-profit / private practice -> not)
  - Year-over-year fill trajectory per program

Why this matters for the substantive paper:
  - The existing fig_substantive_5_sdn_nrmp_alignment.png uses hand-curated
    SPECIALTY-level fill rates (FM, peds, derm, IM)
  - Program-level data lets us test whether PSLF-friendly programs (e.g. county
    hospital FM, VA IM) hold their fill rates while PSLF-hostile programs (e.g.
    private-practice derm, for-profit hospital programs) do not
  - This is a much sharper test of the "PSLF tax" mechanism the discourse data
    suggests

NRMP USAGE COMPLIANCE NOTE:
  The 2021-2025 Program Results PDF includes:
    "No part of the data provided by NRMP may be used as an input to or
     otherwise in connection with any machine learning or artificial
     intelligence models, algorithms, or other tools without the express
     written consent of the NRMP."
  This pipeline:
    - Uses NRMP data ONLY for traditional descriptive/inferential statistics
      (regressions, t-tests, time-series correlations)
    - Does NOT feed NRMP data into any ML/AI model (sentiment instruments are
      run on Reddit/SDN text, not NRMP text)
    - Tabular extracts are saved locally for analysis only; do NOT redistribute
      derived data without NRMP permission
    - For publication, request explicit NRMP permission via datarequest@nrmp.org

PDF sources (free, public):
  - 2021-2025 Program Results:
    https://www.nrmp.org/wp-content/uploads/2025/03/Main_Match_Program_Results_2021-2025.pdf
  - 2024 Results and Data (Main Match):
    https://www.nrmp.org/wp-content/uploads/2024/06/2024-Main-Match-Results-and-Data-Final.pdf
  - 2023 Results and Data:
    https://www.nrmp.org/wp-content/uploads/2023/05/2023-Main-Match-Results-and-Data-Book-FINAL.pdf
  - 2025 Results and Data:
    https://www.nrmp.org/wp-content/uploads/2025/05/Main_Match_Results_and_Data_20250529_FINAL.pdf
  - Older annual books accessible via NRMP archive page

Outputs:
  - nrmp_program_level_2021_2025.csv  (long-format: institution, state, program,
                                       code, year, quota, filled)
  - nrmp_institution_pslf_classification.csv  (institution -> PSLF-eligibility tag)
  - nrmp_program_extraction_log.txt  (parser diagnostics)
"""
from __future__ import annotations
import csv, io, os, re, sys
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

try:
    import pdfplumber
except ImportError:
    print("[ABORT] pip install pdfplumber")
    sys.exit(1)

PDF_2021_2025 = "nrmp_pdfs/2021_2025_program_results.pdf"
OUT_LONG_CSV = "nrmp_program_level_2021_2025.csv"
OUT_CLASS_CSV = "nrmp_institution_pslf_classification.csv"
OUT_LOG = "nrmp_program_extraction_log.txt"

# State two-letter codes used as institution-name suffixes ("-AL", "-FL", etc.)
STATE_SUFFIXES = set([
    "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH",
    "NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT",
    "VT","VA","WA","WV","WI","WY","PR",
])

# Each program code is 9 chars: 4-digit institution + 3-digit specialty +
# 1-letter program type (C/M/P/A/R/F) + 1 char track (0-9).
RE_PROGRAM_CODE = re.compile(r"\b(\d{4})(\d{3})([CMPARF])(\d)\b")

# A data row is: <program name> <9-char code: 7 digits + letter + digit> <10 fields>
# Each field is either a 1-3 digit integer or "--".
RE_CODE = r"\d{7}[CMPARF]\d"
RE_FIELD = r"(?:\d{1,3}|--)"
RE_DATA_ROW = re.compile(
    r"^(.+?)\s+(" + RE_CODE + r")\s+"
    + r"\s+".join([f"({RE_FIELD})"] * 10)
    + r"\s*$"
)

# Institution heading line ends with "-XX" where XX is a US state code.
RE_INST_HEADING = re.compile(r"^(.*?)-([A-Z]{2})\s*$")

# Specialty codes (from PDF page 5)
SPECIALTY_CODES = {
    "040": "Anesthesiology",
    "080": "Dermatology",
    "110": "Emergency Medicine",
    "120": "Family Medicine",
    "140": "Internal Medicine",
    "160": "Neurological Surgery",
    "180": "Neurology",
    "185": "Child Neurology",
    "186": "Neurodevelopmental Disabilities",
    "200": "Nuclear Medicine",
    "220": "Obstetrics-Gynecology",
    "260": "Orthopaedic Surgery",
    "275": "Osteopathic NMM",
    "280": "Otolaryngology",
    "300": "Pathology",
    "320": "Pediatrics",
    "340": "Phys Medicine & Rehab",
    "362": "Plastic Surgery (Integrated)",
    "380": "Preventive Medicine",
    "400": "Psychiatry",
    "416": "Interventional Radiology",
    "420": "Radiology-Diagnostic",
    "430": "Radiation Oncology",
    "440": "Surgery-General",
    "451": "Vascular Surgery",
    "461": "Thoracic Surgery",
    "999": "Transitional",
}

PROG_TYPE = {
    "C": "Categorical",
    "M": "Primary care",
    "P": "Preliminary",
    "A": "Advanced",
    "R": "Physician (PGY-2 entry)",
    "F": "Fellowship",
}

# PSLF eligibility heuristic by institution-name keywords
PSLF_FRIENDLY_KEYWORDS = [
    # Federal/military/VA (all qualifying public service)
    "VA ", "Veterans", "Veteran", "Walter Reed", "Naval", "Army", "Air Force",
    "Bethesda", "Tripler", "Madigan", "Wilford Hall",
    # Universities (overwhelmingly 501(c)(3) nonprofit teaching hospitals)
    "University", "U Alabama", "U Arizona", "U California", "U Colorado",
    "U Connecticut", "U Florida", "U Georgia", "U Hawaii", "U Illinois",
    "U Iowa", "U Kansas", "U Kentucky", "U Louisville", "U Maryland",
    "U Massachusetts", "U Michigan", "U Minnesota", "U Mississippi",
    "U Missouri", "U Nebraska", "U Nevada", "U New Mexico", "U North Carolina",
    "U Oklahoma", "U Oregon", "U South Carolina", "U South Dakota",
    "U Tennessee", "U Utah", "U Vermont", "U Virginia", "U Washington",
    "U Wisconsin", "Univ ", "School of Medicine", "Medical School",
    "Med School", "SOM", " UMass",
    # Children's / teaching / county hospitals (overwhelmingly 501c3)
    "Children", "County", "Public Health", "State Hospital", "Indian Health",
    "Health Service", "Federal", "Health Center",
    # Major nonprofit academic systems
    "Mayo Clinic", "Cleveland Clinic", "Johns Hopkins", "Massachusetts General",
    "Brigham", "Harvard", "Yale", "Stanford", "Duke", "Vanderbilt", "Emory",
    "Northwestern", "Mount Sinai", "Columbia", "Cornell", "NYU", "Penn",
    "Hopkins", "UCSF", "UCLA", "USC Med", "UT Sou", "Baylor", "Wash U",
    "Beth Israel", "BIDMC", "Brigham", "Dana-Farber",
    # Generic academic markers
    "Med Ctr", "Medical Ctr", "Medical Center", "Health System", "Healthcare",
    "Hospitals", "Institute", "Memorial",
]

PSLF_HOSTILE_KEYWORDS = [
    # For-profit / investor-owned chains
    "HCA ", "HCA-", "Tenet", "Community Health Systems", "CHS ",
    "Universal Health Services", "Steward", "LifePoint", "Encompass",
    "Ardent Health", "Surgery Partners", "RegionalCare",
    # Private practice indicators
    "Private Practice", " LLC", " LLP", " LP ", " PC ",
]


def classify_institution(name: str) -> tuple[str, str]:
    """Return (pslf_class, evidence_keyword)."""
    name_lower = name.lower()
    # Hostile takes precedence (HCA hospitals are clearly for-profit even if "Hospital")
    for kw in PSLF_HOSTILE_KEYWORDS:
        if kw.lower() in name_lower:
            return "pslf_hostile", kw.strip()
    for kw in PSLF_FRIENDLY_KEYWORDS:
        if kw.lower() in name_lower:
            return "pslf_friendly", kw.strip()
    # Default: ambiguous (most non-academic community hospitals)
    return "ambiguous", ""


def parse_field(s: str) -> int | None:
    """Parse '--' as None, else int."""
    s = s.strip()
    if s == "--" or s == "":
        return None
    try:
        return int(s)
    except ValueError:
        return None


def extract_program_results(pdf_path: str) -> tuple[list[dict], list[str]]:
    """Walk the PDF page-by-page, detect institution headers and data rows,
    return long-format (institution, state, program_name, code, year, quota,
    filled) tuples + log lines."""
    rows = []
    log = []
    current_institution = None
    current_state = None
    current_city = None  # heuristic — line after institution often contains city
    inst_count = 0

    with pdfplumber.open(pdf_path) as pdf:
        n_pages = len(pdf.pages)
        log.append(f"PDF has {n_pages} pages")
        # Data starts around page 7 based on inspection
        data_start = 7
        for pg_idx in range(data_start - 1, n_pages):
            page = pdf.pages[pg_idx]
            text = page.extract_text() or ""
            lines = [ln.rstrip() for ln in text.split("\n") if ln.strip()]
            for ln in lines:
                # Skip page header
                if ln.startswith("Program Results: Main Residency Match"):
                    continue
                # Skip column header lines
                if ln.startswith("Code Quota Filled") or "Code Quota Filled" in ln[:20]:
                    continue
                if ln.startswith("Program 2025") or " Program 2025 " in ln:
                    continue

                # Check for institution heading: text ending in "-XX " (state code)
                m_inst = RE_INST_HEADING.match(ln)
                if m_inst and m_inst.group(2) in STATE_SUFFIXES:
                    inst_name = m_inst.group(1).strip()
                    state = m_inst.group(2)
                    if len(inst_name) >= 3 and not RE_PROGRAM_CODE.search(ln):
                        current_institution = inst_name
                        current_state = state
                        current_city = None
                        inst_count += 1
                        continue

                # Check for data row
                m_data = RE_DATA_ROW.match(ln)
                if m_data and current_institution:
                    program_name = m_data.group(1).strip()
                    code = m_data.group(2)
                    fields = [parse_field(m_data.group(i)) for i in range(3, 13)]
                    # Fields are: 2025_Q, 2025_F, 2024_Q, 2024_F, 2023_Q, 2023_F,
                    #             2022_Q, 2022_F, 2021_Q, 2021_F
                    years = [2025, 2024, 2023, 2022, 2021]
                    for i, year in enumerate(years):
                        quota = fields[i*2]
                        filled = fields[i*2 + 1]
                        if quota is None and filled is None:
                            continue
                        # Specialty code is positions 5-7 of the program code
                        specialty_code = code[4:7]
                        prog_type_char = code[7]
                        rows.append({
                            "institution": current_institution,
                            "state": current_state,
                            "city": current_city or "",
                            "program_name": program_name,
                            "program_code": code,
                            "specialty_code": specialty_code,
                            "specialty": SPECIALTY_CODES.get(specialty_code, "Other"),
                            "program_type_code": prog_type_char,
                            "program_type": PROG_TYPE.get(prog_type_char, "Other"),
                            "year": year,
                            "quota": quota,
                            "filled": filled,
                            "fill_rate": (filled / quota) if (quota and quota > 0
                                                              and filled is not None) else None,
                        })
                    continue

                # Heuristic: a non-matched line right after institution heading
                # might be the city + " Program" header. Capture city.
                if (current_institution and current_city is None
                        and ln.endswith(" Program")):
                    current_city = ln.replace(" Program", "").strip()

            if (pg_idx + 1) % 25 == 0:
                log.append(f"  page {pg_idx+1}: {len(rows)} rows so far, "
                            f"{inst_count} institutions")

    log.append(f"Total: {len(rows)} program-year rows from {inst_count} institutions")
    return rows, log


def main():
    print("=" * 80)
    print("NRMP Program-Level Extraction (2021-2025)")
    print("=" * 80)

    if not os.path.exists(PDF_2021_2025):
        print(f"[ABORT] PDF not found: {PDF_2021_2025}")
        print("        Download from:")
        print("        https://www.nrmp.org/wp-content/uploads/2025/03/"
              "Main_Match_Program_Results_2021-2025.pdf")
        sys.exit(1)

    print(f"\nParsing {PDF_2021_2025}...")
    rows, log = extract_program_results(PDF_2021_2025)

    if not rows:
        print("[ABORT] No data rows extracted; check PDF format")
        sys.exit(1)

    df = pd.DataFrame(rows)
    print(f"\n  Parsed: {len(df):,} program-year rows")
    print(f"  Unique institutions: {df['institution'].nunique():,}")
    print(f"  States covered: {df['state'].nunique()}")
    print(f"  Years: {sorted(df['year'].unique().tolist())}")

    # Classify institutions
    print("\nClassifying institutions by PSLF eligibility...")
    inst_df = df[["institution", "state"]].drop_duplicates().reset_index(drop=True)
    inst_df[["pslf_class", "pslf_evidence"]] = inst_df["institution"].apply(
        lambda n: pd.Series(classify_institution(n)))
    print(inst_df["pslf_class"].value_counts().to_string())

    df = df.merge(inst_df[["institution", "state", "pslf_class", "pslf_evidence"]],
                   on=["institution", "state"], how="left")

    # Save
    df.to_csv(OUT_LONG_CSV, index=False)
    inst_df.to_csv(OUT_CLASS_CSV, index=False)

    with open(OUT_LOG, "w", encoding="utf-8") as f:
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
        for ln in log:
            f.write(ln + "\n")
        f.write(f"\nClassification breakdown:\n")
        for k, v in inst_df["pslf_class"].value_counts().to_dict().items():
            f.write(f"  {k}: {v} institutions\n")

    print(f"\nSaved: {OUT_LONG_CSV} ({len(df):,} rows)")
    print(f"Saved: {OUT_CLASS_CSV} ({len(inst_df):,} institutions)")
    print(f"Saved: {OUT_LOG}")

    # Quick descriptive — fill rate trajectory by class
    print("\n" + "=" * 80)
    print("PRELIMINARY: Mean fill rate by year x PSLF class")
    print("=" * 80)
    summary = df.dropna(subset=["fill_rate"]).groupby(
        ["year", "pslf_class"])["fill_rate"].agg(["mean", "count"]).reset_index()
    pivot = summary.pivot_table(index="year", columns="pslf_class",
                                  values="mean").round(4)
    print(pivot.to_string())

    # Per-specialty fill rate by class (FM, peds, derm — match existing figure)
    print("\n" + "=" * 80)
    print("PRELIMINARY: FM/Peds/Derm/IM fill rate by year x PSLF class")
    print("=" * 80)
    for sp in ["Family Medicine", "Pediatrics", "Dermatology", "Internal Medicine"]:
        sub = df[df["specialty"] == sp].dropna(subset=["fill_rate"])
        if sub.empty:
            continue
        print(f"\n  {sp}:")
        p = sub.groupby(["year", "pslf_class"])["fill_rate"].agg(
            ["mean", "count"]).reset_index().pivot_table(
                index="year", columns="pslf_class", values="mean").round(4)
        print(p.to_string())


if __name__ == "__main__":
    main()
