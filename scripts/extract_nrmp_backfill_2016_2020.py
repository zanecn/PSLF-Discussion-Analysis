"""
extract_nrmp_backfill_2016_2020.py
=====================================
Backfill NRMP program-level data for 2016-2020 (years before Limited PSLF Waiver
2021-10-06).

The 2016, 2017, 2018, 2019, 2020 main-match books each have a "NRMP Program
Results" section with the same structure as 2021-2025. Parser is reused.

Output: nrmp_program_level_2016_2020_backfill.csv
"""
from __future__ import annotations
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

try: import pdfplumber
except ImportError: print("[ABORT] pip install pdfplumber"); sys.exit(1)

PDFS = [
    ("nrmp_pdfs/2016_main_match.pdf", 2016),
    ("nrmp_pdfs/2017_main_match.pdf", 2017),
    ("nrmp_pdfs/2018_main_match.pdf", 2018),
    ("nrmp_pdfs/2019_main_match.pdf", 2019),
    ("nrmp_pdfs/2020_main_match.pdf", 2020),
]
OUT_CSV = "nrmp_program_level_2016_2020_backfill.csv"

STATE_SUFFIXES = set([
    "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH",
    "NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT",
    "VT","VA","WA","WV","WI","WY","PR",
])

# Single-year format: <program name> <code> <quota> <filled>
RE_CODE = r"\d{7}[CMPARF]\d"
RE_FIELD = r"(?:\d{1,3}|--)"
RE_DATA_ROW_SINGLE = re.compile(
    r"^(.+?)\s+(" + RE_CODE + r")\s+(" + RE_FIELD + r")\s+(" + RE_FIELD + r")\s*$"
)
RE_INST_HEADING = re.compile(r"^(.*?)-([A-Z]{2})\s*$")
RE_CITY = re.compile(r"^([A-Z][a-zA-Z\s\-]{1,40}?)\s+Program\s+(?:Code\s+)?Quota\s+Filled\s*$")

SPECIALTY_CODES = {
    "040":"Anesthesiology","080":"Dermatology","110":"Emergency Medicine",
    "120":"Family Medicine","140":"Internal Medicine","160":"Neurological Surgery",
    "180":"Neurology","185":"Child Neurology","186":"Neurodevelopmental Disabilities",
    "200":"Nuclear Medicine","220":"Obstetrics-Gynecology","260":"Orthopaedic Surgery",
    "275":"Osteopathic NMM","280":"Otolaryngology","300":"Pathology","320":"Pediatrics",
    "340":"Phys Medicine & Rehab","362":"Plastic Surgery (Integrated)",
    "380":"Preventive Medicine","400":"Psychiatry","416":"Interventional Radiology",
    "420":"Radiology-Diagnostic","430":"Radiation Oncology","440":"Surgery-General",
    "451":"Vascular Surgery","461":"Thoracic Surgery","999":"Transitional",
}
PROG_TYPE = {"C":"Categorical","M":"Primary care","P":"Preliminary","A":"Advanced",
              "R":"Physician (PGY-2 entry)","F":"Fellowship"}


def parse_field(s: str) -> int | None:
    s = s.strip()
    if s in ("--", ""): return None
    try: return int(s)
    except: return None


def find_data_pages(pdf):
    """Return (start_page, end_page) range that contains program-level data."""
    # Search for the "NRMP Program Results" section header
    start = None
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").lower()
        if "nrmp program results" in text and i > 50:
            start = i
            break
    if start is None: return (None, None)
    # End is until last page or until "Acknowledg" / "Index"
    end = len(pdf.pages)
    return (start, end)


def parse_single_year_pdf(pdf_path, year):
    rows = []
    current_inst = None
    current_state = None
    current_city = None
    n_inst = 0

    with pdfplumber.open(pdf_path) as pdf:
        start, end = find_data_pages(pdf)
        if start is None:
            print(f"  WARNING: no Program Results section in {pdf_path}")
            return rows
        print(f"  {pdf_path}: data pages {start+1}-{end}")
        for pg_idx in range(start, end):
            text = pdf.pages[pg_idx].extract_text() or ""
            for ln in [l.rstrip() for l in text.split("\n") if l.strip()]:
                # Skip page headers
                if "NRMP Program Results" in ln and "Match" in ln: continue
                if ln.startswith("Code Quota Filled"): continue

                # Institution heading
                m = RE_INST_HEADING.match(ln)
                if m and m.group(2) in STATE_SUFFIXES:
                    name = m.group(1).strip()
                    if len(name) >= 3 and not RE_DATA_ROW_SINGLE.match(ln):
                        current_inst = name
                        current_state = m.group(2)
                        current_city = None
                        n_inst += 1
                        continue

                # City line ("Mobile Program Code Quota Filled")
                m_city = RE_CITY.match(ln)
                if m_city and current_inst:
                    current_city = m_city.group(1).strip()
                    continue

                # Data row (single year format)
                m = RE_DATA_ROW_SINGLE.match(ln)
                if m and current_inst:
                    program_name = m.group(1).strip()
                    code = m.group(2)
                    quota = parse_field(m.group(3))
                    filled = parse_field(m.group(4))
                    if quota is None and filled is None: continue
                    sp_code = code[4:7]
                    pt_char = code[7]
                    rows.append({
                        "institution": current_inst, "state": current_state,
                        "city": current_city or "",
                        "program_name": program_name,
                        "program_code": code, "specialty_code": sp_code,
                        "specialty": SPECIALTY_CODES.get(sp_code, "Other"),
                        "program_type_code": pt_char,
                        "program_type": PROG_TYPE.get(pt_char, "Other"),
                        "year": year,
                        "quota": quota, "filled": filled,
                        "fill_rate": (filled / quota) if (quota and quota > 0
                                                          and filled is not None) else None,
                    })
    print(f"  {pdf_path}: parsed {len(rows):,} rows, {n_inst} institutions")
    return rows


def main():
    print("=" * 80)
    print("NRMP backfill 2016-2020 extraction")
    print("=" * 80)

    all_rows = []
    for path, year in PDFS:
        if not os.path.exists(path):
            print(f"  SKIP: {path} not found")
            continue
        print(f"\nProcessing {year} ({path})...")
        rows = parse_single_year_pdf(path, year)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    print(f"\nTotal rows extracted: {len(df):,}")
    print(f"Years: {sorted(df['year'].unique().tolist()) if len(df) else []}")
    print(f"Unique institutions: {df['institution'].nunique() if len(df) else 0}")

    if len(df):
        df.to_csv(OUT_CSV, index=False)
        print(f"\nSaved: {OUT_CSV}")
        print(f"\nPer-year summary:")
        print(df.groupby("year").agg(
            n_rows=("program_code", "count"),
            n_institutions=("institution", "nunique"),
            mean_fill=("fill_rate", "mean"),
        ).round(3).to_string())


if __name__ == "__main__":
    main()
