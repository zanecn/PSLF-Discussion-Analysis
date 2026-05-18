"""
Surgical-subspecialty PSLF feasibility check for R17++ #5 PAPER_5 reframe.

Compares PSLF-eligibility distribution across NS, Orthopaedic Surgery,
Vascular Surgery, Thoracic Surgery, Plastic Surgery, and Surgery-General.
Verifies the cross-subspecialty comparison framing is data-supported.
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

SURGICAL = [
    "Neurological Surgery",
    "Orthopaedic Surgery",
    "Vascular Surgery",
    "Thoracic Surgery",
    "Plastic Surgery (Integrated)",
    "Otolaryngology",  # ENT — sometimes considered surgical
    "Surgery-General",
]

print("=== Surgical-subspecialty PSLF-eligibility comparison (2021-2026) ===\n")

rows = []
for spec in SURGICAL:
    sub = df[df["specialty"] == spec]
    if len(sub) == 0:
        continue
    n_total = len(sub)
    n_programs = sub["program_code"].nunique()
    n_institutions = sub["institution"].nunique()
    n_hostile_rows = (sub["pslf_class"] == "pslf_hostile").sum()
    n_hostile_inst = sub[sub["pslf_class"] == "pslf_hostile"]["institution"].nunique()
    n_ambiguous = (sub["pslf_class"] == "ambiguous").sum()
    n_eligible = (sub["pslf_class"] == "pslf_friendly").sum()
    fill_friendly = sub[sub["pslf_class"] == "pslf_friendly"]["fill_rate"].mean()
    fill_ambiguous = sub[sub["pslf_class"] == "ambiguous"]["fill_rate"].mean()
    fill_hostile = sub[sub["pslf_class"] == "pslf_hostile"]["fill_rate"].mean() if n_hostile_rows > 0 else None
    rows.append({
        "specialty": spec,
        "n_program_years": n_total,
        "n_programs": n_programs,
        "n_institutions": n_institutions,
        "n_hostile_rows": n_hostile_rows,
        "n_hostile_inst": n_hostile_inst,
        "n_ambiguous": n_ambiguous,
        "n_eligible": n_eligible,
        "pct_eligible": 100 * n_eligible / n_total,
        "pct_ambiguous": 100 * n_ambiguous / n_total,
        "pct_hostile": 100 * n_hostile_rows / n_total,
        "fill_eligible": fill_friendly,
        "fill_ambiguous": fill_ambiguous,
        "fill_hostile": fill_hostile,
    })

out = pd.DataFrame(rows)
print(out.to_string(index=False, float_format="%.3f"))

print("\n=== Hostile institutions per surgical subspecialty (detail) ===")
for spec in SURGICAL:
    sub = df[(df["specialty"] == spec) & (df["pslf_class"] == "pslf_hostile")]
    if len(sub) == 0:
        continue
    print(f"\n{spec}: {len(sub)} hostile rows, {sub['institution'].nunique()} unique institutions")
    for inst in sorted(sub["institution"].unique()):
        rows_inst = sub[sub["institution"] == inst]
        years = sorted(rows_inst["year"].unique())
        fill_by_year = rows_inst.groupby("year")["fill_rate"].mean().to_dict()
        print(f"  {inst}: years {years}, fill {fill_by_year}")

print("\n=== FEASIBILITY VERDICT ===")
print("Comparison paper viable across surgical subspecialties:")
for r in rows:
    spec = r["specialty"]
    n_h_inst = r["n_hostile_inst"]
    if n_h_inst == 0:
        verdict = "ZERO hostile — descriptive only"
    elif n_h_inst == 1:
        verdict = "1 hostile institution — descriptive case-study only"
    elif n_h_inst <= 4:
        verdict = f"{n_h_inst} hostile — descriptive + small-n inferential caveat"
    else:
        verdict = f"{n_h_inst} hostile — supports inferential analysis"
    print(f"  {spec:32s}: {verdict}")

print("\n=== HEADLINE for surgical-subspecialty comparison paper ===")
ns = next((r for r in rows if r["specialty"] == "Neurological Surgery"), None)
ortho = next((r for r in rows if r["specialty"] == "Orthopaedic Surgery"), None)
plastics = next((r for r in rows if r["specialty"] == "Plastic Surgery (Integrated)"), None)

print(f"\nPSLF-hostile rates across competitive surgical subspecialties:")
for r in sorted(rows, key=lambda x: -x["pct_hostile"]):
    print(f"  {r['specialty']:32s}: {r['pct_hostile']:5.2f}% hostile  ({r['n_hostile_inst']} institutions)")
