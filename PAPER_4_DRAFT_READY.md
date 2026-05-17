# Paper 4 Draft-Ready Template (Path B, *Scientific Data* / Nature)

**Status:** Ready to draft (artifact locked at R17++ #2; structured 5-section Scientific Data format)
**Target:** *Scientific Data* (Nature Publishing Group; primary) / *Data in Brief* (Elsevier; secondary)
**Length:** 2,000–2,500 words + structured Data Records section
**Working title:** *A Public Service Loan Forgiveness eligibility classification of US residency-training institutions, 2021–2026*

**Added:** 2026-05-17 (R17++ #3 — after publishability assessment identified the standalone dataset paper as the single highest-yield Path-B-adjacent addition; see "PSLF 3-Paper Publishability Assessment" agent report 2026-05-16 + subsequent prioritization filter)

---

## Why this paper

The PSLF-eligibility classification of 872 US residency-training institutions across 2021–2026, with three sensitivity specifications addressing HCA-academic partnership ambiguity, is the primary input to Paper 3's substantive results. It is also a reusable infrastructure artifact: every future PSLF-residency study will need either this classification or one substantively equivalent to it. Publishing it as a citable Nature data title with a DOI:

1. **Creates evergreen citation infrastructure.** Trump EO 14235 (March 2025) + ED Final Rule (FR Oct 31, 2025; effective Jul 1, 2026) guarantee growing PSLF-residency research. A standardized institutional classification with documented sensitivity specs becomes the de facto reference.
2. **Compresses Paper 3 methodology section.** With P4 published, P3's classification documentation collapses from ~600 words to one citation, freeing JGME word-count budget for substantive results.
3. **De-risks reviewer #2 critiques.** Reviewer concerns about institutional classification ("how did you handle HCA-academic partnerships? what about VA hospitals? what about university-system mergers?") get addressed in P4's Data Records / Technical Validation sections, not in P3 supplements.

**No conflict with Path B P1/P2/P3.** Reciprocal citation, not competing claims.

---

## Section structure (per Scientific Data format)

### Background & Summary (~400 words)

[INSERT BLOCK: PSLF program background → for-profit chain residency expansion since 2014 (Lassner et al. 2022 ×2, ACGME 2025, HCA Healthcare 2014) → measurement gap: no public, standardized classification of residency-program PSLF eligibility at the institution-year level → this work resolves that gap with ProPublica IRS BMF as the eligibility ground truth + three sensitivity specifications.]

Trump Executive Order 14235 "Restoring Public Service Loan Forgiveness" (March 7, 2025) + ED Final Rule (Federal Register Oct 31, 2025; effective July 1, 2026) make this classification time-sensitive. Pre-EO baseline (2021–2025) and first post-EO Match cycle (2026) provide a natural comparison window.

### Methods (~600 words)

**Data sources:**
- NRMP Main Match Program Results PDFs, 2021–2026 (n=37,450 raw program-year rows from 872 unique institutions across 28 specialties; post Round 17 CMS-merge dedup)
- ProPublica Nonprofit Explorer (IRS Form 990) for 501(c)(3) and university status verification
- CMS Hospital Compare for city-level quality and ownership classification
- NIH RePORTER FY2023 state-filtered awards by organization
- ACGME Accreditation Data 2025

**Classification scheme:**
- PSLF-eligible: university-affiliated OR IRS-verified 501(c)(3)
- Ambiguous: privately-held or LLC structures where eligibility cannot be determined from public records
- PSLF-hostile: for-profit chain–affiliated (HCA Healthcare, Tenet, USHealth, etc.), ProPublica IRS-verified

**Three sensitivity specifications:**
- **S1 (status quo):** all 23 NRMP-listed PSLF-hostile institutions retained; treats HCA-academic partnerships as hostile by parent-company affiliation
- **S2 (HCA-academic reclassified):** 14 HCA-academic partnerships (USF Morsani ×10, U Miami ×2, U Houston ×1, VCOM ×1) reclassified as ambiguous; reflects W-2-employer uncertainty without individual borrower data
- **S3 (HCA-academic dropped):** same 14 institutions dropped from the analytical sample entirely

**Reproducibility provenance:** R17 CMS-merge case-collision dedup fix applied across all 10 Model 5 source scripts. RUN_AUDITS.ps1 verifies dedup presence in all scripts at HEAD time.

[INSERT BLOCK: Cleaning pipeline — institution-name fuzzy matching with manual verification; city/state resolution; ProPublica IRS BMF cross-reference workflow.]

### Data Records (~400 words)

[INSERT BLOCK: tabular description of the released dataset files.]

Primary records:
- **`nrmp_pslf_eligibility_2021_2026.csv`** — 37,450 rows × 28 columns covering NRMP program-year fill-rate + city/state + ProPublica IRS classification + S1/S2/S3 sensitivity labels + CMS quality + NIH funding
- **`institution_classification_master.csv`** — 872 institution-level rows with stable institution_id, parent-organization, IRS status, PSLF eligibility, ACGME accreditation status
- **`hca_academic_partnership_audit_trail.csv`** — explicit documentation of all 14 HCA-academic partnerships with primary-source URLs (institution websites + HCA press releases + ACGME records)
- **`nrmp_field_dictionary.md`** — column-level documentation including units, valid-value ranges, missing-data patterns

Auxiliary records:
- **`source_pdfs/`** — 6 NRMP PDFs (one per Match cycle 2021–2026) for re-extraction
- **`extraction_logs/`** — pdfplumber 0.11.9+ extraction logs with version pin + provenance

### Technical Validation (~400 words)

**Inter-source agreement:**
- ProPublica IRS BMF × ACGME accreditation: agreement rate on parent-organization for 872 institutions = [TO COMPUTE]
- NRMP institution-name × CMS Hospital Compare name (fuzzy-matched): agreement after manual review = [TO COMPUTE]
- S1/S2/S3 sensitivity divergence: 14 of 23 hostile institutions reclassified between S1 and S2; 9 retained across all 3 specs

**Substantive validation (forward-pointing to P3):**
- Cross-sectional 5-year baseline regression with PSLF-hostile classification: β = −18.07 pp (S1) / −16.25 pp (S2) / −17.14 pp (S3); wild-cluster bootstrap p<0.0005 / 0.017 / 0.006
- Stability of headline across confounder adjustment: M5+NIH shifts β by only +0.17 pp
- Negative control (orthopedic surgery, where PSLF financial materiality is weaker): β = +0.67 pp NS (clean null at power floor 1.33 pp 5-yr / 1.06 pp 6-yr)
- Secondary negative control (dermatology): β = −6 to −7 pp NS (mixed result honestly reported; point estimate negative but CIs straddle zero)

**Known limitations (full disclosure):**
- 14 HCA-academic partnerships have ambiguous W-2 employer structure that cannot be resolved without individual-borrower data (NSLDS DUA pending)
- Reporting unit is institution-year, NOT borrower-year; classification applies to programs not individuals
- Pre-2020 backfill (2016, 2017, 2020 only — 2018-2019 not available in Wayback archives) is sparse and reported descriptively only
- Trump-EO 14235 + ED Final Rule July 2026 will reshape classification post-effective-date; this dataset captures pre-EO baseline + first post-EO Match cycle only

### Usage Notes (~300 words)

**Intended applications:**
- Replication and extension of Paper 3's cross-sectional differential analysis
- Multi-year post-EO trend analysis when 2027+ NRMP cycles become available
- Negative-control / placebo-test analyses (orthopedic surgery + dermatology rows included)
- Cross-walking with other institutional datasets (CMS, ACGME, NIH RePORTER) via stable institution_id

**Suggested NOT-uses:**
- Individual borrower-level analyses (this is an institution-year classification; use NSLDS with appropriate DUA for borrower-level work)
- Causal attribution of fill-rate to PSLF eligibility (the dataset SUPPORTS such analyses but is not itself causal evidence; see Paper 3 §4.4 for causal-identification limits)

**Versioning policy:**
- v1.0 (initial release): 2021–2026 with R17++ #2 corrections
- Future versions when 2027+ NRMP cycles release: append-only; v1.0 always preserved as historical record
- All corrections logged in CHANGELOG.md following R17++ citation-integrity-log model

### Code Availability (~100 words)

All extraction, cleaning, classification, and validation scripts are in `scripts/` of the source repository at https://github.com/zanecn/PSLF-Discussion-Analysis (commit-pinned to `db1e955` or later]. Key scripts:
- `extract_nrmp_backfill_2016_2020.py` — pre-2020 NRMP extraction
- `extract_nrmp_cities.py` — city resolution
- `verify_nrmp_pslf_eligibility.py` — ProPublica IRS BMF cross-reference
- `build_institutional_confounders.py` — institution-level confounder build
- `RUN_AUDITS.ps1` — integrity audit pipeline (14 tests including dedup-fix presence in 10 Model 5 scripts)

---

## Pre-submission checklist

- [ ] Deposit dataset to Dryad / Figshare / Zenodo with DOI (Scientific Data requires data deposit before submission)
- [ ] Compute exact inter-source agreement rates (currently `[TO COMPUTE]` in Technical Validation)
- [ ] Generate 1-2 Data Records overview figures (institution count by classification × year; geographic distribution)
- [ ] Write README.md for the deposited dataset (standalone documentation, separate from manuscript)
- [ ] Verify all primary-source URLs in `hca_academic_partnership_audit_trail.csv` are still resolving
- [ ] Confirm CHANGELOG.md is in place at the deposit location

---

## Expected timeline

- **Week 1:** Compute inter-source agreement rates; generate Data Records figures; write README.md for deposit
- **Week 2:** Deposit to Dryad/Zenodo; receive DOI; draft Methods + Data Records sections from existing P3 §2 + extraction scripts
- **Week 3:** Draft Background + Technical Validation + Usage Notes; co-author review; submit

Total: **3 weeks** to submission with focused effort.

---

## Reciprocal citation plan

- **P4 cites:** Lassner et al. 2022 ×2 (PMC9348842 + PMC9380617), ACGME 2025, HCA Healthcare 2014, Cameron-Miller 2015, MacKinnon-Webb 2018, Roodman et al. 2019, Webb 2014, NRMP, ProPublica, CMS, NIH RePORTER. NO citation of P3 (would be a forward reference at submission time).
- **P3 cites P4** in §2.1 Data Sources: "PSLF eligibility classification per [Cite P4]." This collapses 600 words to 1 citation.
- **P4 cited as Methods reference in:** P1 §3 (corpus selection cites P4 for SDN-medical professional identification justification), P2 §3 (cohort definitions reference P4 for PSLF-hostile/PSLF-eligible cohorts).

---

## Source files

- `nrmp_program_level_2021_2026.csv` — primary table
- `paper3_model5_FINAL_results.txt` — substantive validation evidence
- `verify_nrmp_pslf_eligibility.py` — classification pipeline
- `scripts/README.md` — script-to-output mapping
- `MASTER_LOCKED_NUMBERS.md` — canonical numbers (validate consistency on each PSLF-eligibility-classified subset)
- `RUN_AUDITS.ps1` — integrity verifier (must pass at submission time)
