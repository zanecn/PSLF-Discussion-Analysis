# PSLF Eligibility Classification Dataset for US Residency Training Institutions, 2021–2026

**Version:** 1.0 (R17++ #6 RIGOROUS REVIEW snapshot, 2026-05-17)
**Repository:** GitHub `playwright-sdn-scraper` branch at commit-time-of-deposit
**License:** CC-BY 4.0 (use freely with attribution)
**Citation (after DOI mint):** `[Author(s)] (2026). PSLF Eligibility Classification of US Residency Training Institutions, 2021–2026. [Dryad/Zenodo]. DOI: [TBD].`

---

## What's in this dataset

This dataset characterizes Public Service Loan Forgiveness (PSLF) eligibility of US residency-training institutions across the 2021–2026 NRMP Main Match cycles, using ProPublica IRS Form 990 verification as the primary classification methodology.

**Primary use cases:**
- Replication of Paper 3 (Health Affairs Scholar / Academic Medicine / JGME) cross-sectional fill-rate differential analysis
- Multi-year post-EO (Trump EO 14235, March 2025) workforce trend analysis when 2027+ data become available
- Negative-control specialty analyses (orthopedic surgery, dermatology)
- Cross-walking with CMS Hospital Compare, NIH RePORTER, ACGME accreditation data via stable institution_id

**Suggested NOT-uses:**
- Individual borrower-level PSLF utilization analyses (this is institution-year-level; use NSLDS with appropriate Data User Agreement for borrower-level work)
- Causal attribution of fill-rate to PSLF eligibility (the dataset supports such analyses but is NOT itself causal evidence; see Paper 3 §4.4 for causal-identification limits)

---

## Files

| File | Description |
|---|---|
| `nrmp_program_level_2021_2026.csv` | Primary table: 37,450 program-year rows × 15 columns |
| `nrmp_institution_pslf_classification.csv` | Institution-level PSLF classification table (currently 789 of 872 institutions; 83-institution gap pending resolution per RUN_AUDITS check) |
| `nrmp_institution_pslf_verified.csv` | ProPublica-verified subset |
| `hca_academic_partnership_audit_trail.csv` | 14 HCA-academic partnerships with primary-source URLs |
| `nrmp_field_dictionary.md` | Column-level documentation |
| `paper3_model5_FINAL_results.txt` | Substantive validation evidence (β=−18.07 pp cross-sectional fill-rate differential) |
| `paper3_negative_control_2021_2026_results.txt` | Orthopedic surgery clean null β=+0.54 NS |
| `paper3_negative_control_dermatology_results.txt` | Dermatology mixed null β=−6 to −7 NS |
| `paper3_two_part_nih_results.txt` | NIH RePORTER integration two-part decomposition |
| `paper3_wild_cluster_bootstrap_results.txt` | Webb 6-point B=2,000 wild-cluster bootstrap |
| `CHANGELOG.md` | Version history and corrections log |
| `DATASET_README.md` | This file |

---

## Methods (summary)

**Classification scheme:**
- **PSLF-eligible** (`pslf_friendly`): university-affiliated OR IRS-verified 501(c)(3)
- **Ambiguous** (`ambiguous`): privately-held or LLC structures where eligibility cannot be determined from public records
- **PSLF-hostile** (`pslf_hostile`): for-profit chain-affiliated (HCA Healthcare, Tenet, USHealth, etc.), ProPublica IRS-verified

**Three sensitivity specifications:**
- **S1 (status quo):** all 23 NRMP-listed PSLF-hostile institutions retained
- **S2 (HCA-academic reclassified):** 14 HCA-academic partnerships (USF Morsani × 10, U Miami × 2, U Houston × 1, VCOM × 1) reclassified as ambiguous; reflects W-2-employer uncertainty
- **S3 (HCA-academic dropped):** same 14 institutions dropped from analytical sample entirely

**Data sources:**
- **NRMP Main Match Program Results PDFs**, 2021–2026
- **ProPublica Nonprofit Explorer** (IRS Form 990 verification)
- **CMS Hospital Compare** (city-level quality + ownership classification)
- **NIH RePORTER FY2023** (state-filtered total awards)
- **ACGME Accreditation Data Annual Report 2025**

**Reproducibility provenance:**
- R17 CMS-merge case-collision dedup fix applied across all 10 Model 5 source scripts
- `RUN_AUDITS.ps1` verifies dedup-fix presence + audit-history compliance at HEAD time
- pdfplumber 0.11.9+ used for NRMP PDF extraction
- All scripts pinned to commit-of-deposit at GitHub

---

## Substantive validation (from companion Paper 3)

- Cross-sectional 5-year baseline (2021–2025): PSLF-hostile β = **−18.07 pp** (S1), −16.25 pp (S2), −17.14 pp (S3); wild-cluster bootstrap p<0.0005 / 0.017 / 0.006
- M5+NIH stability: PSLF β shifts by only +0.17 pp adding state-filtered NIH funding
- Negative control orthopedic surgery: β = +0.67 pp NS (clean null at 1.33 pp power floor)
- Secondary negative control dermatology: β = −6 to −7 pp NS (mixed result honestly reported)
- 6-year extended sample (2021–2026): year-by-year gap narrows from −16.5 pp (2022 peak) to −7.0 pp (2026)
- **Trump-EO retraction**: 2026 narrowing consistent with continuation of pre-existing 5-year trend (is_2026 indicator p=0.46 NS; is_post_eo year≥2025 sensitivity p=0.877 NS)

---

## Known limitations (full disclosure)

1. **HCA-academic partnerships have ambiguous W-2 employer structure** that cannot be resolved without individual-borrower data. NSLDS Data User Agreement (DUA) application is pending for separate study (see `NSLDS_DUA_APPLICATION_CHECKLIST.md`).
2. **Reporting unit is institution-year, NOT borrower-year**; classification applies to programs not individuals.
3. **Pre-2020 backfill (2016, 2017, 2020 only — 2018-2019 not available in Wayback archives)** is sparse and reported descriptively only.
4. **Trump-EO 14235 + ED Final Rule July 2026 will reshape classification** post-effective-date; this dataset captures pre-EO baseline (2021–2025) + first post-EO Match cycle (2026) only.
5. **Inter-source agreement rates are not yet computed** for the broadened residency-program dataset (ACGME multi-year + NIH multi-year + VA + AAMC integration is part of the planned R17++ #6 broadening work; current single-source agreement audit is in `RUN_AUDITS.ps1`).
6. **83-institution gap in lookup CSVs**: the institution-level classification CSVs currently cover 789 of 872 institutions. The 83 institutions classified at 2026-extraction time are present in the primary program-level table but not the lookup files. Re-running `scripts/verify_nrmp_pslf_eligibility.py` against the 2026 institution list closes this gap (R17++ #6 P0 BLOCKER pending).

---

## Citation Integrity Note

This dataset is associated with a project that has applied a multi-round citation integrity sweep (R17 + R17++ + R17++ #2-6). **17 fabrications/misattributions caught and corrected** across the citation list; **6 unverifiable citations removed or replaced**. The R17++ Citation Integrity Log (Notion: 35d1b390-1b2f-811d-b70b-e9826f8f7573) documents every correction. All citations in the companion Paper 3 manuscript are author-level WebSearch-verified.

---

## Contact

For dataset questions: see GitHub repository at `https://github.com/zanecn/PSLF-Discussion-Analysis` (issues welcome).

Generated 2026-05-17.
