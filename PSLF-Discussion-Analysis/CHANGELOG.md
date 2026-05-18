# Changelog — PSLF Eligibility Classification Dataset

All notable changes to this dataset are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to semantic versioning where applicable.

---

## [1.0] — 2026-05-17

### Initial release

This is the first formally-versioned release of the PSLF Eligibility Classification Dataset for US Residency Training Institutions, 2021–2026.

### Added
- 37,450 program-year rows across 872 institutions × 29 specialties × 6 NRMP Match cycles (2021–2026)
- 14 HCA-academic partnership institutions with full audit-trail CSV including primary-source URLs
- Three sensitivity specifications (S1/S2/S3) for HCA-academic-partnership classification ambiguity
- Field dictionary, README, and dataset metadata
- Source-of-truth scripts pinned to GitHub commit (see DATASET_README.md)

### Verified (via R17 + R17++ + R17++ #2 + R17++ #6 RIGOROUS REVIEW)
- 23 PSLF-hostile institutions (S1) — verified via ProPublica IRS Form 990
- 9 unambiguous PSLF-hostile institutions (S2/S3) — verified
- 14 HCA-academic partnerships (S2 reclassified) — verified
- R17 CMS-merge case-collision dedup fix applied across all 10 Model 5 source scripts
- 17 citation fabrications caught and corrected
- 6 unverifiable citations removed or replaced

### Known limitations (full disclosure)
- 83-institution gap in lookup files (`nrmp_institution_pslf_classification.csv` covers 789 of 872 institutions; the 83 missing institutions ARE classified in the primary program-level table but never propagated to lookup files). **Resolution pending: re-run `scripts/verify_nrmp_pslf_eligibility.py` against the 2026 institution list.**
- Inter-source agreement rates not yet computed (requires planned R17++ #6 broadening with ACGME multi-year + NIH multi-year + VA + AAMC integration)

---

## Versioning policy

- **v1.x (current line):** 2021–2026 data with R17 + R17++ corrections
- **v2.x (future):** when 2027+ NRMP cycles release; append-only with v1.x always preserved as historical record
- All future corrections logged here following R17++ citation-integrity-log model

---

## Historical context

- **R12 (2026-05-08):** Initial dataset assembly
- **R17 (2026-05-10):** Critical R17 cycle — CMS-merge case-collision dedup bug fixed across 8 Model 5 scripts; state-filtered NIH integrated; Trump-EO causal interpretation retracted (is_2026 p=0.46 NS)
- **R17++ (2026-05-11):** Citation integrity sweep — 14 fabrications/misattributions corrected, 5 unverifiable removed, Notion overhaul
- **R17++ #2 (2026-05-16):** 7 publication figures generated (300 DPI); 4 code-required audits completed; OSF venue migration (Political Analysis → EPJ DS); Whitcomb 2014 removed (6th unverifiable); audit infrastructure committed (`RUN_AUDITS.ps1` 14 tests)
- **R17++ #3 (2026-05-17):** Paraphrase robustness independently replicated at n=399
- **R17++ #4 (2026-05-17):** NS-match restructure (5-output)
- **R17++ #5 (2026-05-17):** Rigorous validity review — P5 reframed to surgical-subspecialty; P6 added
- **R17++ #6 (2026-05-17):** Boost strategy + revised venues + data acquisition plan
- **R17++ #6 RIGOROUS REVIEW (2026-05-17):** 6 independent peer-review-style agents evaluated story-vs-data consistency; 23 P0 BLOCKERS surfaced; mechanical corrections applied; P1 OP-vs-Reply cluster bootstrap re-run with aligned 4-source loader for exact n=21,453 match (TB Δ=−0.0146 [−0.0164, −0.0127]; VADER Δ=+0.2387 [+0.2306, +0.2460]; magnitude ratio 16.4× corrected from prior wrong 20.5×)
