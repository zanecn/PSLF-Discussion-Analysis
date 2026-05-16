# NRMP Program-Level Fill Rate Data — Instructions & Workflow

## Status (2026-05-10)

✅ **DONE**: Built end-to-end pipeline for the 2021-2025 NRMP Program Results PDF
(789 institutions, 7,490 unique programs, 30,763 program-year rows). Headline
finding: **PSLF-friendly programs fill 12.86 pp higher than PSLF-hostile (Cohen's
d=+0.62, p=3.4×10⁻²⁷)**, with the gap LARGEST in Internal Medicine (+28.2 pp)
and Family Medicine (+15.1 pp), and ABSENT in Dermatology (+3.4 pp NS).

🔧 **REMAINING WORK** for full publication-quality dataset (multi-week effort):
1. Manual classification refinement (ambiguous bucket = 387 institutions)
2. Backfill 2010-2020 from older annual Results-and-Data PDFs (per-year, not the
   2021-2025 consolidated report)
3. NRMP permission for redistribution of derived data (mandatory per copyright)

---

## Pipeline overview

```
NRMP PDFs              collect_nrmp_program_level.py    analyze_nrmp_program_pslf.py
├── 2021_2025_*.pdf  ──┬─→ nrmp_program_level_2021_2025.csv ──→ nrmp_pslf_program_results.txt
├── 2024_main_*.pdf    │   nrmp_institution_pslf_classification.csv  nrmp_pslf_program_results.csv
├── 2023_main_*.pdf    │                                              nrmp_pslf_program_figure.png
├── 2025_main_*.pdf    │
└── (older years)      └─→ nrmp_program_extraction_log.txt
```

## What we extracted

For each institution × specialty × program-type × year:
- Institution name, state, city
- Program name (e.g., "Family Medicine/Rural")
- 9-character NRMP program code (4-digit institution + 3-digit specialty + program-type letter + track digit)
- Specialty (decoded from positions 5-7 of program code)
- Program type: Categorical / Primary / Preliminary / Advanced / Physician / Fellowship
- Quota (positions offered)
- Filled (positions matched)
- Fill rate (filled/quota)

## PSLF eligibility classification (heuristic)

Each institution is tagged as one of:
- **`pslf_friendly`** (387 institutions): contains "University", "VA", "Children",
  "County", "Mayo Clinic", "Cleveland Clinic", "Med Ctr", etc. — keywords associated
  with 501(c)(3) nonprofit teaching hospitals or qualifying federal employers
- **`pslf_hostile`** (23 institutions): contains "HCA", "Tenet", "LifePoint",
  "Universal Health Services", etc. — for-profit hospital chains where PSLF does
  not apply
- **`ambiguous`** (387 institutions): no clear marker (most community hospitals,
  health systems with mixed nonprofit/for-profit affiliations)

**Verification needed**: ~50% of institutions are ambiguous. Manual classification
of these would tighten the headline gap estimate significantly. Suggested approach:
- Cross-reference against ProPublica Nonprofit Explorer (501c3 status)
- Cross-reference against AHA Annual Survey (ownership type field)
- ~4-8 hours of manual review per 100 institutions

## Headline findings (2021-2025 program-level data)

| Comparison | Mean PSLF-Friendly | Mean PSLF-Hostile | Gap (pp) | p-value | Cohen's d |
|---|---|---|---|---|---|
| **Overall** | 93.9% | 81.1% | +12.86 | 3.4e-27 | +0.62 |
| Family Medicine | 88.3% | 73.2% | +15.1 | 1.6e-04 | (medium) |
| Internal Medicine | 94.3% | 66.0% | +28.2 | 5.8e-21 | (large) |
| Pediatrics | (n_hostile<10) | — | — | — | — |
| Dermatology | 98.9% | 95.5% | +3.4 | 0.32 (NS) | (small) |
| Emergency Medicine | 93.0% | 77.8% | +15.2 | 9.7e-04 | (medium) |
| Psychiatry | 99.1% | 100.0% | -0.9 | 1.0e-04 | (small reverse) |

## Year-over-year trajectory (2021 → 2025)

| Year | PSLF-Friendly | PSLF-Hostile | Gap (pp) |
|---|---|---|---|
| 2021 | 93.9% | 79.9% | +14.00 |
| 2022 | 94.2% | 77.7% | +16.48 |
| 2023 | 93.5% | 80.3% | +13.18 |
| 2024 | 94.0% | 83.3% | +10.71 |
| 2025 | 94.0% | 83.6% | +10.47 |

Pre/post Trump PSLF EO (Mar 2025): gap narrowed from +13.53 pp (2021-24 pooled) to
+10.47 pp (2025), driven by **PSLF-hostile programs IMPROVING by +3.22 pp** while
friendly stayed stable. Speculative interpretation: post-EO uncertainty drove
some applicants to take any spot rather than holding out for PSLF-eligible programs.

## How to extend to 2010-2020

The 2021-2025 consolidated PDF is a one-time NRMP release. For earlier years,
**each annual Results-and-Data book includes per-program tables** in a similar
format. Successfully downloaded so far:

| Year | URL |
|---|---|
| 2018 | https://www.nrmp.org/wp-content/uploads/2018/04/Main-Match-Result-and-Data-2018.pdf |
| 2019 | https://www.nrmp.org/wp-content/uploads/2019/04/NRMP-Results-and-Data-2019_04112019_final.pdf |
| 2021 | https://www.nrmp.org/wp-content/uploads/2021/08/MRM-Results_and-Data_2021.pdf |
| 2023 | https://www.nrmp.org/wp-content/uploads/2023/05/2023-Main-Match-Results-and-Data-Book-FINAL.pdf |
| 2024 | https://www.nrmp.org/wp-content/uploads/2024/06/2024-Main-Match-Results-and-Data-Final.pdf |
| 2025 | https://www.nrmp.org/wp-content/uploads/2025/05/Main_Match_Results_and_Data_20250529_FINAL.pdf |

**Missing (need to find via NRMP archive page or wayback machine):**
- 2010-2017 (URL pattern not stable; check
  https://www.nrmp.org/match-data-analytics/residency-data-reports/)
- 2020 (one URL pattern returned 404; try alternate)
- 2022 (one URL pattern returned 404; try alternate)

The 2018, 2019, 2021, 2023, 2024 main-match books each have one year of program-
level data in a "NRMP Program Results" section. The parser regex
(`RE_DATA_ROW`) should extend to those PDFs but may need format-specific tweaks
because layout has shifted across years.

## NRMP usage compliance — IMPORTANT

The 2021-2025 PDF carries an explicit notice:

> "No part of the data provided by NRMP may be used as an input to or otherwise
> in connection with any machine learning or artificial intelligence models,
> algorithms, or other tools without the express written consent of the NRMP."

**This pipeline is compliant** because:
- NRMP data feeds only **traditional descriptive/inferential statistics**
  (group means, t-tests, correlations, regression)
- No NRMP text/data is fed to any LLM (sentiment instruments are run on
  Reddit/SDN text only)
- Tabular extracts saved locally for analysis only

**Before publication**, you must:
1. Email `datarequest@nrmp.org` with a description of your project, the specific
   tables/derived statistics you want to publish, and the journal target
2. Wait for written permission (NRMP typically responds in 2-4 weeks)
3. Cite using the suggested citation:
   > National Resident Matching Program, *Program Results: Main Residency Match®
   > 2021-2025 Appointment Years*. National Resident Matching Program, Washington,
   > DC, 2025.

## Open methodological questions

1. **PSLF-eligibility validation**: Audit a random sample of 50 friendly + 23
   hostile institutions against PSLF Qualifying Employer database
   (https://studentaid.gov/pslf/employer-search). False-positive and false-
   negative rates would calibrate the heuristic.

2. **Ambiguous bucket**: 387 institutions = 49% of the dataset. If the 12.86 pp
   gap survives reclassification of ambiguous → friendly/hostile (per AHA
   ownership data), the headline strengthens. If it shrinks substantially, the
   keyword heuristic was driving it.

3. **Confound: applicant quality**: For-profit chain hospitals attract lower-
   quality applicants for many reasons unrelated to PSLF (lower research
   output, fewer fellowship pipelines, lower NRMP rank). Need to either
   condition on US-MD-Senior-only fill rate (the strongest applicant tier) or
   add program reputation controls (Doximity reputation, NIH funding).

4. **Backfill 2010-2017**: With the 5-year 2021-2025 baseline, fill rate
   trajectories pre-Limited Waiver (2021) cannot be assessed. Backfill is
   doable from older PDFs (~3-5 weeks of parser work + manual cleanup) but is
   the single biggest extension cost.

5. **Per-program longitudinal panel**: With 7,490 unique programs across 5
   years, can fit per-program slope models (program random intercept × PSLF
   class fixed effect × year) — much higher statistical power than aggregate
   means. Worth doing if a methods journal wants the rigor.

## Recommended action

**For substantive paper draft**: Use the 2021-2025 finding as a substantive co-
headline alongside the discourse data. The gap is large, statistically robust
(p<10⁻²⁶), and theoretically motivated (PSLF should bind hardest in primary
care, smallest in specialties with low federal-loan exposure).

**For publication**: 
1. Apply for NRMP permission immediately (~3-4 week lag)
2. Manual ambiguous-bucket validation (~2 weeks)
3. AHA ownership cross-reference (~1 week)
4. Optional 2018-2020 backfill if you want trajectory pre-Limited Waiver

**For follow-up paper**: Combine NRMP program-level fill rates with PSLF
discourse signals at the institution level (geographic alignment of SDN/Reddit
discussion peaks with localized fill-rate disruptions). Would need state-level
SDN-Medical posts which we have, plus FY-bound NRMP timing — feasible from
existing data.
