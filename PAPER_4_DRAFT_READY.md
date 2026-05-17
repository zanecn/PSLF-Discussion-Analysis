# Paper 4 Draft-Ready Template — *Scientific Data* (Nature)

**Status:** Ready to draft (artifact locked; structured Scientific Data format)
**Target:** *Scientific Data* (Nature Publishing Group; primary) / *Data in Brief* (Elsevier; secondary)
**Length:** 2,000-2,500 words + structured Data Records section
**Working title:** *A Public Service Loan Forgiveness eligibility classification of US residency-training institutions, 2021–2026*

**Added:** 2026-05-17 (R17++ #4 — **reinstated** after medical-student context clarification; original R17++ #3 P4 framing reverted same-day; this re-add comes from understanding the user is MS3 ending → NS-match-targeted research year, where publication count matters more than per-paper substantive impact)

---

## Why this paper makes sense for an NS-match medical student

I previously walked you out of this paper on the grounds that realistic 5-year citation count would be 10-25 (low). That argument is correct for a tenure-track academic optimizing for long-term impact. It's wrong for a medical student optimizing for **publication count on ERAS by Sept 2027**. Specifically:

- Neurosurgery match averages **~18 research items** on the ERAS application of matched US-MD seniors; top quartile has 30-50. One more publication on your ERAS list is real marginal value.
- *Scientific Data* is a Nature-family journal title that NS PDs recognize at a glance (they don't need to know it's a "data journal" — they see "Nature Publishing Group").
- Acceptance probability ~50-65% (data documentation quality is the bar, not substantive novelty), and your data is well-documented.
- ~3 weeks of writing during research year, feasible alongside primary NS research.
- "Citation count over 5 years" is irrelevant for residency review which happens in Q4 2027 — well before the citation clock starts ticking.

The paper isn't substantively interesting in the way P3 is, but it's an **easy, fast, additional CV line** during a critical credentialing window. That's the right axis to optimize for, given your situation.

## Section structure (per Scientific Data format)

### Background & Summary (~400 words)

[INSERT BLOCK: PSLF program background → for-profit chain residency expansion since 2014 (Lassner et al. 2022 ×2, ACGME 2025, HCA Healthcare 2014) → measurement gap: no public, standardized classification of residency-program PSLF eligibility at the institution-year level → this work resolves that gap.]

Trump EO 14235 (March 7, 2025) + ED Final Rule (FR Oct 31, 2025; effective July 1, 2026) make the classification time-sensitive. Pre-EO baseline (2021-2025) + first post-EO Match cycle (2026) covers the natural comparison window.

### Methods (~600 words)

**Data sources:** NRMP Main Match Program Results 2021-2026 (37,450 raw program-year rows from 872 institutions across 28 specialties post Round 17 CMS-merge dedup); ProPublica Nonprofit Explorer (IRS Form 990); CMS Hospital Compare; NIH RePORTER FY2023 state-filtered; ACGME Accreditation Data 2025.

**Classification scheme:** PSLF-eligible (university-affiliated OR 501(c)(3)) / ambiguous (privately-held / LLC) / PSLF-hostile (for-profit chain–affiliated, ProPublica IRS-verified).

**Three sensitivity specifications:**
- S1 (status quo): all 23 NRMP-listed PSLF-hostile institutions retained
- S2: 14 HCA-academic partnerships reclassified as ambiguous (W-2 employer uncertainty)
- S3: same 14 institutions dropped from analytical sample

**Reproducibility provenance:** R17 CMS-merge case-collision dedup fix applied across all 10 Model 5 source scripts; `RUN_AUDITS.ps1` verifies at HEAD time.

[INSERT BLOCK: cleaning pipeline detail.]

### Data Records (~400 words)

Primary records:
- `nrmp_pslf_eligibility_2021_2026.csv` (37,450 × 28)
- `institution_classification_master.csv` (872 institutions)
- `hca_academic_partnership_audit_trail.csv` (14 partnerships, primary-source URLs)
- `nrmp_field_dictionary.md` (column-level documentation)

Auxiliary records:
- `source_pdfs/` (6 NRMP PDFs)
- `extraction_logs/` (pdfplumber 0.11.9+ provenance)
- `scripts/extract_*.py` + classification pipeline

All deposited at Dryad (primary) / Zenodo (mirror) with citable DOI before this paper's submission. See `DATASET_DEPOSIT_PLAN.md` for the deposit checklist + file manifest.

### Technical Validation (~400 words)

**Inter-source agreement:**
- ProPublica IRS BMF × ACGME accreditation parent-organization match rate: [TO COMPUTE]
- NRMP institution-name × CMS Hospital Compare fuzzy-match agreement after manual review: [TO COMPUTE]
- S1/S2/S3 sensitivity: 14 of 23 hostile institutions reclassified between S1 and S2; 9 retained across all 3 specs

**Substantive validation (cites P3 at submission):**
- Cross-sectional 5-yr baseline β = −18.07 (S1) / −16.25 (S2) / −17.14 (S3); wild-cluster p<0.0005 / 0.017 / 0.006
- M5+NIH stability: PSLF β shifts only +0.17 pp
- Negative-control ortho clean null (β=+0.67 NS, power floor 1.33 pp)
- Secondary negative-control dermatology mixed (β=−6 to −7 NS, CIs straddle zero)

**Known limitations:**
- HCA-academic partnerships have ambiguous W-2 employer structure (NSLDS DUA pending)
- Institution-year unit, not borrower-year
- Pre-2020 backfill sparse (2016, 2017, 2020 only)
- Trump-EO 14235 + ED Final Rule July 2026 will reshape classification post-effective-date

### Usage Notes (~300 words)

**Intended applications:** replication of P3 cross-sectional analysis; multi-year post-EO trend analysis when 2027+ NRMP cycles release; negative-control / placebo analyses (ortho + dermatology rows); cross-walking with CMS / ACGME / NIH RePORTER via stable `institution_id`.

**Suggested NOT-uses:** individual borrower-level analyses (use NSLDS with DUA); causal attribution (dataset supports but is not itself causal evidence; see P3 §4.4).

**Versioning policy:** v1.0 initial (2021-2026 with R17++ #2 corrections); append-only for future NRMP cycles; CHANGELOG.md follows R17++ citation-integrity-log model.

### Code Availability (~100 words)

All scripts at https://github.com/zanecn/PSLF-Discussion-Analysis (commit `ffe49f2` or later). Key files: `extract_nrmp_backfill_2016_2020.py`, `extract_nrmp_cities.py`, `verify_nrmp_pslf_eligibility.py`, `build_institutional_confounders.py`, `RUN_AUDITS.ps1`.

---

## Pre-submission checklist

- [ ] Deposit dataset to Dryad (primary) / Zenodo (mirror); mint DOI before submission
- [ ] Compute inter-source agreement rates (currently `[TO COMPUTE]` placeholders)
- [ ] Generate 1-2 Data Records overview figures (institution count by classification × year; geographic distribution)
- [ ] Write README.md for the deposited dataset (separate from manuscript)
- [ ] Verify all primary-source URLs in `hca_academic_partnership_audit_trail.csv` still resolve
- [ ] Confirm CHANGELOG.md in deposit location

## Reciprocal citation plan

- **P4 cites:** Lassner et al. 2022 ×2 (PMC9348842 + PMC9380617), ACGME 2025, HCA Healthcare 2014, Cameron-Miller 2015, MacKinnon-Webb 2018, Roodman et al. 2019, Webb 2014, NRMP, ProPublica, CMS, NIH RePORTER. **Cites Paper 3 (JGME)** at submission once P3 is in print.
- **P3 cites P4** in §2.1 Data Sources (compresses ~600 words of classification methodology to ~80 words).
- **P5 (NS spin-off) cites P4** in Methods (cites P4 for the institutional classification methodology used in the NS-specific subset).

## Expected timeline (research year Jul 2026 onwards)

- **Sep-Oct 2026 (~Week 8-12 of research year):** Compute inter-source agreement rates; generate Data Records figures; write README.md for deposit; deposit at Dryad/Zenodo
- **Nov 2026:** Draft Background + Methods + Data Records (1 week)
- **Dec 2026:** Draft Technical Validation + Usage Notes (1 week)
- **Jan 2027:** Co-author review + submit to *Scientific Data*
- **Feb-Apr 2027:** Decision (typically 2-3 months at Scientific Data)
- **May-Jul 2027:** Revisions cycle
- **Aug 2027:** Published online (before ERAS Sept 2027)

Total: ~3 weeks of effective writing during research year, fits alongside primary NS research.

## Source files

- `nrmp_program_level_2021_2026.csv` — primary table
- `paper3_model5_FINAL_results.txt` — substantive validation evidence
- `verify_nrmp_pslf_eligibility.py` — classification pipeline
- `DATASET_DEPOSIT_PLAN.md` — Dryad/Zenodo deposit implementation
- `MASTER_LOCKED_NUMBERS.md` — canonical numbers (validate consistency)
- `RUN_AUDITS.ps1` — integrity verifier (must pass at submission time)
