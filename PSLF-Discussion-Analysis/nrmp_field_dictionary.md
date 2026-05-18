# NRMP × PSLF Eligibility Field Dictionary

**Dataset:** PSLF eligibility classification of US residency-training institutions, 2021–2026
**Companion to:** `nrmp_program_level_2021_2026.csv` + `nrmp_institution_pslf_classification.csv` + `nrmp_institution_pslf_verified.csv` + `hca_academic_partnership_audit_trail.csv`
**Generated:** 2026-05-17 (R17++ #6 RIGOROUS REVIEW deposit-readiness)
**Methods reference:** `PAPER_4_DRAFT_READY.md` + `DATASET_DEPOSIT_PLAN.md`

---

## File: `nrmp_program_level_2021_2026.csv`

The primary program-year dataset.

| Column | Type | Description | Valid values / range | Missing pattern |
|---|---|---|---|---|
| `institution` | string | NRMP-listed sponsoring institution name (free text) | varies; ~872 unique values | none expected |
| `state` | string | 2-letter US state code | AK..WY; PR for Puerto Rico | none |
| `program_name` | string | NRMP program name | varies; ~7,916 unique program_codes | none |
| `program_code` | string | NRMP program code (institution-specialty-type triplet) | format: `[year]NRMP-[institution]-[specialty]-[type]` | none |
| `specialty_code` | integer | NRMP specialty numeric code | 140 (IM), 165 (FM), 200 (surgery), 400 (psych), 700 (peds), etc. | none |
| `specialty` | string | NRMP specialty name | 29 distinct values including "Internal Medicine", "Family Medicine", "Surgery-General", "Neurological Surgery", etc. | none |
| `program_type_code` | string | Program type code | "C" (Categorical), "P" (Preliminary), "M" (Medicine-Pediatrics), "T" (Transitional), "S" (Specialty) | none |
| `program_type` | string | Program type name | "Categorical", "Preliminary", "Med-Peds", "Transitional", "Specialty" | none |
| `year` | integer | NRMP Match year | 2021, 2022, 2023, 2024, 2025, 2026 | none |
| `quota` | integer | Total positions offered in the program-year | typically 1-200; sum across programs ≈ 38,000/year | none |
| `filled` | integer | Number of positions filled in the Match | 0 ≤ filled ≤ quota | none |
| `fill_rate` | float | filled / quota | 0.000 to 1.000 | none |
| `pslf_class` | string | R17 PSLF eligibility classification | "pslf_friendly", "ambiguous", "pslf_hostile" | none |
| `pslf_evidence` | string | Brief evidence justifying the classification | varies; e.g., "Med Ctr", "VA", "HCA Healthcare for-profit chain" | varies |
| `city` | string | City name (sentence-cased) | post-R17 dedup applied | none |

### Sample size summary (post-dedup, 2026-05-17)
- **Total rows:** 37,450 program-years
- **Unique program_codes:** 7,916
- **Unique institutions:** 872
- **Unique specialties:** 29 (including "Other" and "Unknown" catch-all categories)
- **Years:** 2021–2026 (6 cycles)

### PSLF classification distribution (post-R17 dedup)
- **pslf_friendly:** 57.2% of program-years (high majority; 501(c)(3) and government-affiliated)
- **ambiguous:** 40.3% (private LLC structures where eligibility cannot be determined from public records)
- **pslf_hostile:** 2.5% (for-profit chain-affiliated, ProPublica IRS-verified)

---

## File: `nrmp_institution_pslf_classification.csv`

Institution-level PSLF classification table.

| Column | Type | Description | Valid values |
|---|---|---|---|
| `institution` | string | NRMP-listed institution name | varies |
| `state` | string | 2-letter state code | AK..WY |
| `city` | string | City name | varies |
| `pslf_class` | string | Classification per R17 methodology | "pslf_friendly", "ambiguous", "pslf_hostile" |
| `pslf_evidence` | string | Brief evidence justifying classification | varies |
| `propublica_subseccd` | integer | ProPublica IRS subseccd code | 3 (501(c)(3)), 4 (social welfare), 7 (state instrumentality), null (not 501(c)) |
| `propublica_org_id` | string | ProPublica organization ID | varies |
| `verification_date` | date | When the classification was verified | typically 2026-05-10 (R17 cycle) |

**Coverage:** As of 2026-05-17, this file covers 789 of 872 institutions (90.5%). The 83 institutions missing from this lookup file were classified during the 2026 NRMP extraction step (their `pslf_class` exists in `nrmp_program_level_2021_2026.csv`) but were never propagated to this lookup file. **Re-run `scripts/verify_nrmp_pslf_eligibility.py` to close the gap before final deposit.**

---

## File: `nrmp_institution_pslf_verified.csv`

ProPublica-verified subset of the classification table.

| Column | Type | Description |
|---|---|---|
| (same as classification table above, with additional verification metadata) | | |
| `verification_method` | string | "automatic" (ProPublica subseccd direct match) or "manual" (hand-reviewed) |
| `verification_confidence` | string | "high", "medium", "low" |
| `notes` | string | Manual review notes where applicable |

---

## File: `hca_academic_partnership_audit_trail.csv`

The 14 HCA-academic partnership institutions, with primary-source URLs.

| Column | Type | Description |
|---|---|---|
| `institution_name` | string | Alternative or stable institution name |
| `nrmp_institution_name` | string | Name as appears in NRMP listings (may differ) |
| `parent_organization` | string | "HCA Healthcare" (all 14) |
| `academic_affiliate` | string | University academic partner (USF Morsani, U Miami, U Houston, VCOM) |
| `partnership_type` | string | Description of GME partnership structure |
| `n_programs_2021_2026` | integer | Number of distinct residency programs at this institution |
| `n_program_years_2021_2026` | integer | Total program-years (programs × years) |
| `primary_source_urls` | string | Semicolon-separated URLs to primary sources |
| `verification_notes` | string | Free-text notes on classification rationale |
| `verified_date` | date | Date of audit-trail verification |

### S1/S2/S3 Sensitivity Specifications

| Spec | Classification of these 14 institutions | Use case |
|---|---|---|
| **S1** (status quo) | Treated as `pslf_hostile` based on for-profit parent | Conservative; assumes resident W-2 employer is HCA |
| **S2** | Reclassified as `ambiguous` (W-2 employer uncertain) | Acknowledges that resident may have appointment letter that establishes academic-affiliate employment |
| **S3** | Dropped from analytical sample entirely | Most conservative; uses only 9 pure-HCA/Steward unambiguous-hostile institutions |

---

## Versioning policy

- **v1.0 (initial release):** 2021–2026 with R17++ #2 + R17++ #6 RIGOROUS REVIEW corrections
- **Future versions** when 2027+ NRMP cycles release: append-only; v1.0 always preserved as historical record
- All corrections logged in `CHANGELOG.md` following R17++ citation-integrity-log model
- Deposit DOI to be minted at Dryad or Zenodo before paper submission

## Source-of-truth scripts

- `scripts/verify_nrmp_pslf_eligibility.py` — primary classification pipeline
- `scripts/build_institutional_confounders.py` — confounder integration
- `scripts/integrate_nih_into_model5.py` — NIH RePORTER integration
- `scripts/run_model5_FINAL.py` — primary analysis using this dataset (cross-sectional 2021–2025 baseline; produces canonical β=−18.07 pp)

## Related references

- **ProPublica Nonprofit Explorer**: https://projects.propublica.org/nonprofits/
- **NRMP Main Match Results PDFs (2021–2026)**: https://www.nrmp.org/match-data/
- **ACGME Accreditation Data Annual Reports**: https://www.acgme.org/about/publications-and-resources/annual-data-reports/
- **NIH RePORTER**: https://reporter.nih.gov/
