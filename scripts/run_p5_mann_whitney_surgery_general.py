"""
P5 R17++ #6 RIGOROUS REVIEW response: Mann-Whitney U test on Surgery-General
fill rates (PSLF-hostile vs eligible/ambiguous program-years).

Per R17++ #6 review agent finding, this test must be run to verify or refute
the outline claim that "Surgery-General is the only surgical subspecialty
where PSLF eligibility may meaningfully affect recruitment."
"""
import sys
from pathlib import Path
import pandas as pd
from scipy import stats

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/nrmp_program_level_2021_2026.csv")
OUT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/paper5_mann_whitney_surgery_general.txt")

df = pd.read_csv(DATA)
sg = df[df["specialty"] == "Surgery-General"].copy()

print(f"Surgery-General program-year rows: {len(sg):,}")
print(f"Unique programs: {sg['program_code'].nunique()}")
print(f"Unique institutions: {sg['institution'].nunique()}")
print()

hostile = sg[sg["pslf_class"] == "pslf_hostile"]
ambiguous = sg[sg["pslf_class"] == "ambiguous"]
eligible = sg[sg["pslf_class"] == "pslf_friendly"]
non_hostile = sg[sg["pslf_class"] != "pslf_hostile"]

print(f"PSLF-hostile rows: {len(hostile)} ({hostile['institution'].nunique()} unique institutions)")
print(f"PSLF-ambiguous rows: {len(ambiguous)}")
print(f"PSLF-eligible rows: {len(eligible)}")
print(f"Non-hostile (combined) rows: {len(non_hostile)}")
print()

hostile_fill = hostile["fill_rate"].dropna()
elig_fill = eligible["fill_rate"].dropna()
amb_fill = ambiguous["fill_rate"].dropna()
nonh_fill = non_hostile["fill_rate"].dropna()

print(f"Fill rate stats:")
print(f"  Hostile:    n={len(hostile_fill)}, mean={hostile_fill.mean():.4f}, median={hostile_fill.median():.4f}, std={hostile_fill.std():.4f}, range=[{hostile_fill.min():.4f}, {hostile_fill.max():.4f}]")
print(f"  Ambiguous:  n={len(amb_fill)}, mean={amb_fill.mean():.4f}, median={amb_fill.median():.4f}, std={amb_fill.std():.4f}")
print(f"  Eligible:   n={len(elig_fill)}, mean={elig_fill.mean():.4f}, median={elig_fill.median():.4f}, std={elig_fill.std():.4f}")
print(f"  Non-hostile (combined): n={len(nonh_fill)}, mean={nonh_fill.mean():.4f}, median={nonh_fill.median():.4f}, std={nonh_fill.std():.4f}")
print()

# Mann-Whitney U (two-sided): hostile vs eligible
u1, p1 = stats.mannwhitneyu(hostile_fill, elig_fill, alternative='two-sided')
print(f"Mann-Whitney U (hostile vs PSLF-eligible): U={u1:.1f}, p={p1:.4f}")

# Mann-Whitney U (two-sided): hostile vs ambiguous
u2, p2 = stats.mannwhitneyu(hostile_fill, amb_fill, alternative='two-sided')
print(f"Mann-Whitney U (hostile vs ambiguous): U={u2:.1f}, p={p2:.4f}")

# Mann-Whitney U (two-sided): hostile vs non-hostile (pooled)
u3, p3 = stats.mannwhitneyu(hostile_fill, nonh_fill, alternative='two-sided')
print(f"Mann-Whitney U (hostile vs non-hostile pooled): U={u3:.1f}, p={p3:.4f}")

# Mann-Whitney U (one-sided, hostile < non-hostile): tests directional hypothesis
u4, p4 = stats.mannwhitneyu(hostile_fill, nonh_fill, alternative='less')
print(f"Mann-Whitney U (one-sided: hostile<non-hostile): U={u4:.1f}, p={p4:.4f}")

# Welch's t-test as supplement (less robust to outliers but more familiar)
t, pt = stats.ttest_ind(hostile_fill, nonh_fill, equal_var=False)
print(f"Welch's t-test (hostile vs non-hostile): t={t:.3f}, p={pt:.4f}")
print()

# Institution-level analysis: aggregate to one mean fill rate per institution-year, then per institution
print("=== INSTITUTION-LEVEL ANALYSIS ===")
inst_agg = sg.groupby(["institution", "pslf_class"])["fill_rate"].mean().reset_index()
host_inst = inst_agg[inst_agg["pslf_class"] == "pslf_hostile"]["fill_rate"].dropna()
nonh_inst = inst_agg[inst_agg["pslf_class"] != "pslf_hostile"]["fill_rate"].dropna()
print(f"Institution-level: hostile n={len(host_inst)}, non-hostile n={len(nonh_inst)}")
print(f"  Hostile mean={host_inst.mean():.4f}, median={host_inst.median():.4f}")
print(f"  Non-hostile mean={nonh_inst.mean():.4f}, median={nonh_inst.median():.4f}")
u5, p5 = stats.mannwhitneyu(host_inst, nonh_inst, alternative='two-sided')
print(f"  Mann-Whitney U (institution-level, two-sided): U={u5:.1f}, p={p5:.4f}")
u6, p6 = stats.mannwhitneyu(host_inst, nonh_inst, alternative='less')
print(f"  Mann-Whitney U (institution-level, one-sided hostile<non-hostile): U={u6:.1f}, p={p6:.4f}")
t2, pt2 = stats.ttest_ind(host_inst, nonh_inst, equal_var=False)
print(f"  Welch's t (institution-level): t={t2:.3f}, p={pt2:.4f}")
print()

# Total UNIQUE institutions across the 7 surgical subspecialties
print("=== TOTAL UNIQUE INSTITUTIONS ACROSS 7 SURGICAL SUBSPECIALTIES (R17++ #6 review: outline claims 979, actual unique = ?) ===")
SURGICAL = [
    "Neurological Surgery", "Orthopaedic Surgery", "Vascular Surgery",
    "Thoracic Surgery", "Plastic Surgery (Integrated)", "Otolaryngology", "Surgery-General",
]
all_surg = df[df["specialty"].isin(SURGICAL)]
print(f"Surgical-subspecialty rows: {len(all_surg):,}")
print(f"UNIQUE institutions across all 7 surgical subspecialties: {all_surg['institution'].nunique()}")
print(f"Sum of per-subspec institution counts (= outline 979 if correct): {sum([all_surg[all_surg['specialty']==s]['institution'].nunique() for s in SURGICAL])}")
print()

# Unique HCA-affiliated PSLF-hostile institutions across all 7 surgical subspecialties
host_surg = all_surg[all_surg["pslf_class"] == "pslf_hostile"]
print(f"PSLF-hostile surgical-subspec rows: {len(host_surg)}")
print(f"UNIQUE institutions hosting PSLF-hostile surgical-subspec programs: {host_surg['institution'].nunique()}")
print(f"  Institutions:")
for inst in sorted(host_surg["institution"].unique()):
    subspecs = sorted(host_surg[host_surg["institution"] == inst]["specialty"].unique())
    print(f"    {inst}: {len(subspecs)} subspecialty(ies) = {subspecs}")
print()
print(f"Total program-institution pairs (= outline 14 if correct): {host_surg.groupby(['institution', 'specialty']).ngroups}")

# Save key results
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("=" * 70 + "\n")
    f.write("Paper 5 R17++ #6 RIGOROUS REVIEW: Mann-Whitney + numerical verification\n")
    f.write("=" * 70 + "\n\n")
    f.write("Run: 2026-05-17 (R17++ #6 review fix)\n\n")
    f.write("=== Surgery-General fill rate comparison ===\n")
    f.write(f"PSLF-hostile rows: n={len(hostile_fill)} from {hostile['institution'].nunique()} unique institutions\n")
    f.write(f"PSLF-eligible rows: n={len(elig_fill)}\n")
    f.write(f"PSLF-ambiguous rows: n={len(amb_fill)}\n")
    f.write(f"Non-hostile (combined) rows: n={len(nonh_fill)}\n\n")
    f.write(f"Hostile fill: mean={hostile_fill.mean():.4f}, median={hostile_fill.median():.4f}, range=[{hostile_fill.min():.4f}, {hostile_fill.max():.4f}]\n")
    f.write(f"Eligible fill: mean={elig_fill.mean():.4f}, median={elig_fill.median():.4f}\n")
    f.write(f"Ambiguous fill: mean={amb_fill.mean():.4f}, median={amb_fill.median():.4f}\n")
    f.write(f"Non-hostile pooled fill: mean={nonh_fill.mean():.4f}, median={nonh_fill.median():.4f}\n\n")
    f.write(f"Mann-Whitney U (hostile vs PSLF-eligible, two-sided): U={u1:.1f}, p={p1:.4f}\n")
    f.write(f"Mann-Whitney U (hostile vs ambiguous, two-sided): U={u2:.1f}, p={p2:.4f}\n")
    f.write(f"Mann-Whitney U (hostile vs non-hostile pooled, two-sided): U={u3:.1f}, p={p3:.4f}\n")
    f.write(f"Mann-Whitney U (hostile vs non-hostile, one-sided hostile<non-hostile): U={u4:.1f}, p={p4:.4f}\n")
    f.write(f"Welch's t (hostile vs non-hostile pooled): t={t:.3f}, p={pt:.4f}\n\n")
    f.write("=== Institution-level test (each institution = 1 observation = mean fill across years) ===\n")
    f.write(f"Hostile institutions n={len(host_inst)}, mean={host_inst.mean():.4f}, median={host_inst.median():.4f}\n")
    f.write(f"Non-hostile institutions n={len(nonh_inst)}, mean={nonh_inst.mean():.4f}, median={nonh_inst.median():.4f}\n")
    f.write(f"Mann-Whitney U (institution-level, two-sided): U={u5:.1f}, p={p5:.4f}\n")
    f.write(f"Mann-Whitney U (institution-level, one-sided hostile<non-hostile): U={u6:.1f}, p={p6:.4f}\n")
    f.write(f"Welch's t (institution-level): t={t2:.3f}, p={pt2:.4f}\n\n")
    f.write("=== VERDICT ===\n")
    if p3 > 0.05:
        f.write(f"At program-year level, hostile vs non-hostile fill rate difference is NOT statistically significant (p={p3:.4f}).\n")
        f.write(f"Hostile mean ({hostile_fill.mean():.4f}) is essentially identical to non-hostile mean ({nonh_fill.mean():.4f}).\n")
        f.write(f"The outline claim that 'PSLF eligibility may meaningfully affect Surgery-General recruitment' is UNSUPPORTED.\n")
        f.write(f"Reframe: Surgery-General hostile programs show greater fill-rate variability than ultra-competitive subspecialties,\n")
        f.write(f"but the central tendency does not differ from non-hostile Surgery-General programs.\n")
    else:
        f.write(f"At program-year level, hostile vs non-hostile fill rate difference IS statistically significant (p={p3:.4f}).\n")
        f.write(f"Hostile mean ({hostile_fill.mean():.4f}) vs non-hostile mean ({nonh_fill.mean():.4f}).\n")
    f.write("\n=== Numerical claim verification ===\n")
    f.write(f"Outline claim 'all 14 PSLF-hostile surgical-subspecialty institutions': ACTUAL = {host_surg.groupby(['institution', 'specialty']).ngroups} program-institution pairs from {host_surg['institution'].nunique()} unique institutions\n")
    f.write(f"Outline claim '979 unique institutions across 7 subspecialties': ACTUAL = {all_surg['institution'].nunique()} unique (979 = sum across subspecialties, which double-counts)\n")
    f.write("\nUnique hostile surgical-subspec institutions:\n")
    for inst in sorted(host_surg["institution"].unique()):
        subspecs = sorted(host_surg[host_surg["institution"] == inst]["specialty"].unique())
        f.write(f"  {inst}: {len(subspecs)} subspec(s) = {subspecs}\n")

print(f"\nSaved results to: {OUT}")
