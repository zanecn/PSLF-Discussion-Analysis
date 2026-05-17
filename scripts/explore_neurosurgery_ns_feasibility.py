"""
Quick feasibility check: is there enough neurosurgery-specific data in the
NRMP program-level dataset to support a Paper 5 spin-off targeting NS venues?

Decision criteria:
- N_ns_programs >= 80 (US has ~115-120 NS programs)
- n_hostile_ns >= 5 for meaningful regression; else descriptive paper only
- Multi-year coverage (2021-2026) consistent across the dataset
"""
import sys
from pathlib import Path
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/nrmp_program_level_2021_2026.csv")
df = pd.read_csv(DATA)
print(f"Total rows: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(f"Years: {sorted(df['year'].unique())}")
print(f"Specialties (count): {df['specialty'].nunique()}")
print(f"Programs (unique program_code): {df['program_code'].nunique()}")
print(f"Institutions (unique): {df['institution'].nunique()}")

print("\n=== Search for neurosurgery ===")
# Specialty may be spelled in various ways
ns_patterns = ["neurosurg", "neurological surgery", "neuro surgery"]
ns_mask = df["specialty"].str.lower().str.contains("|".join(ns_patterns), na=False, regex=True)
ns = df[ns_mask].copy()
print(f"NS rows: {len(ns):,}")
print(f"NS specialties found: {sorted(ns['specialty'].unique())}")
print(f"NS unique programs: {ns['program_code'].nunique()}")
print(f"NS unique institutions: {ns['institution'].nunique()}")

print("\n=== NS by year ===")
print(ns.groupby("year").size().to_string())

print("\n=== NS by PSLF class ===")
print(ns["pslf_class"].value_counts().to_string())

print("\n=== NS PSLF class by year ===")
print(ns.groupby(["year", "pslf_class"]).size().unstack(fill_value=0).to_string())

print("\n=== NS hostile programs (if any) ===")
hostile = ns[ns["pslf_class"] == "pslf_hostile"]
if len(hostile) > 0:
    print(f"  n hostile rows: {len(hostile)}")
    print(f"  n unique hostile programs: {hostile['program_code'].nunique()}")
    print(f"  n unique hostile institutions: {hostile['institution'].nunique()}")
    print(f"  Hostile institutions:")
    for inst in sorted(hostile["institution"].unique()):
        years = sorted(hostile[hostile["institution"] == inst]["year"].unique())
        rates = hostile[hostile["institution"] == inst].groupby("year")["fill_rate"].mean()
        print(f"    {inst}: years {years}, fill_rate {rates.to_dict()}")
else:
    print("  ZERO PSLF-hostile NS programs in dataset")

print("\n=== NS fill-rate summary by PSLF class ===")
print(ns.groupby("pslf_class")["fill_rate"].describe()[["count", "mean", "std", "min", "max"]].to_string())

print("\n=== NS fill-rate by year by PSLF class ===")
print(ns.groupby(["year", "pslf_class"])["fill_rate"].mean().unstack(fill_value=None).to_string())

print("\n=== Comparison: NS vs other specialties, PSLF class distribution ===")
ns_only = ns["pslf_class"].value_counts(normalize=True) * 100
other = df[~ns_mask]["pslf_class"].value_counts(normalize=True) * 100
comp = pd.DataFrame({"ns_%": ns_only, "other_specialties_%": other}).fillna(0).round(2)
print(comp.to_string())

print("\n=== Specialty list (top 30 by row count) ===")
print(df["specialty"].value_counts().head(30).to_string())

print("\n=== FEASIBILITY VERDICT ===")
n_ns_programs = ns["program_code"].nunique()
n_hostile_ns_inst = ns[ns["pslf_class"] == "pslf_hostile"]["institution"].nunique()
print(f"  N unique NS programs: {n_ns_programs}")
print(f"  N unique NS hostile institutions: {n_hostile_ns_inst}")
if n_ns_programs >= 80:
    print(f"  ✓ Adequate NS program count for descriptive paper")
else:
    print(f"  ⚠ Low NS program count — descriptive paper plausible but smaller scope")
if n_hostile_ns_inst >= 5:
    print(f"  ✓ Adequate hostile NS for regression-style analysis")
elif n_hostile_ns_inst >= 1:
    print(f"  ⚠ Few hostile NS — case-study + descriptive paper only")
else:
    print(f"  ⚠ Zero hostile NS — descriptive 'PSLF eligibility universal among NS programs' paper only")
