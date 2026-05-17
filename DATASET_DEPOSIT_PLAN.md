# Dataset Deposit Plan — PSLF-eligibility classification (Dryad/Zenodo)

**Created:** 2026-05-17 (replaces reverted `PAPER_4_DRAFT_READY.md` framing 2026-05-17 a.m.)
**Updated:** 2026-05-17 (P4 *Scientific Data* paper reinstated p.m. after medical-student context clarification; this doc now describes the **Dryad/Zenodo deposit that P4 CITES** rather than a substitute-for-paper)
**Status:** Implementation detail of **Paper 4 (*Scientific Data*) submission** + supplementary citation for **Paper 3 (JGME)** + **Paper 5 (NS Neurosurgery short report)**
**Target repository:** Dryad (`datadryad.org`) primary / Zenodo (`zenodo.org`) mirror
**Effort:** ~1 day of metadata + README polishing (deposit is the artifact; Paper 4 is the descriptor that points readers to the deposit DOI)

---

## How the deposit relates to Paper 4 (*Scientific Data*)

The deposit is the **artifact**: actual CSV files + README + scripts at Dryad/Zenodo with a citable DOI. Paper 4 is the **descriptor**: a peer-reviewed Scientific Data paper that points readers to the deposit and explains methodology + validation + intended use.

For a medical student aiming at NS match, both have value:
- The **deposit** is the citable infrastructure that P3 and P5 cite in their Methods sections
- The **Paper 4 *Scientific Data*** publication is a CV line on ERAS

(The earlier 2026-05-17 a.m. framing that "deposit instead of paper" was advice optimized for tenure-track research impact. For a med-student NS application optimizing for publication count, "deposit AND paper" is the right call. See `PROJECT_INDEX.md` audit history for the back-and-forth.)

---

## Files to deposit

### Primary records
- `nrmp_pslf_eligibility_2021_2026.csv` — 37,450 rows × 28 columns (NRMP program-year fill-rate + city/state + ProPublica IRS classification + S1/S2/S3 sensitivity labels + CMS quality + NIH funding)
- `institution_classification_master.csv` — 872 institution-level rows with stable institution_id, parent-organization, IRS status, PSLF eligibility, ACGME accreditation status
- `hca_academic_partnership_audit_trail.csv` — explicit documentation of all 14 HCA-academic partnerships with primary-source URLs (institution websites + HCA press releases + ACGME records)
- `nrmp_field_dictionary.md` — column-level documentation including units, valid-value ranges, missing-data patterns

### Auxiliary records
- `source_pdfs/` — 6 NRMP PDFs (one per Match cycle 2021–2026) for re-extraction
- `extraction_logs/` — pdfplumber 0.11.9+ extraction logs with version pin + provenance
- `scripts/extract_*.py` + `verify_nrmp_pslf_eligibility.py` + `build_institutional_confounders.py` — full pipeline (also at GitHub `playwright-sdn-scraper` branch commit `3fceaf8` or later)

### Deposit metadata (README.md included in deposit)
- Brief description (~200 words)
- File manifest with checksums
- Methods provenance (link to GitHub commit + paper §2.1)
- Versioning policy (v1.0 initial; append-only for future NRMP cycles)
- Citation format with DOI + suggested-citation block
- License: CC-BY 4.0 (allow downstream use with attribution)
- CHANGELOG.md template

---

## Pre-deposit checklist

- [ ] Compute and document inter-source agreement rates (currently `[TO COMPUTE]` placeholders in `PAPER_3_DRAFT_READY.md`)
- [ ] Verify all primary-source URLs in `hca_academic_partnership_audit_trail.csv` are still resolving (re-check 2026 status of HCA Healthcare press releases + institution program pages)
- [ ] Run `RUN_AUDITS.ps1` to confirm dedup-fix present in all 10 Model 5 scripts (must pass at deposit time)
- [ ] Verify file checksums match the analytical snapshot used in P3
- [ ] Choose primary deposit venue (Dryad: stronger curation, $120 deposit fee, longer review; Zenodo: free, faster, CERN-backed durability)
- [ ] Mint DOI before P3 submission so P3 can cite it in §2.1

---

## How P3 cites the deposit

In P3 §2.1 Data Sources, replace the ~600-word classification-methodology paragraph with:

> Programs were classified as PSLF-eligible (university-affiliated or 501(c)(3)), ambiguous, or PSLF-hostile (for-profit chain–affiliated, ProPublica IRS-verified) per the released classification dataset [PSLF-eligibility classification 2021–2026 dataset, Dryad/Zenodo DOI]. Three sensitivity specifications (S1 status quo, S2 HCA-academic reclassified, S3 HCA-academic dropped) addressed W-2 employer ambiguity at HCA-academic partnership institutions. See dataset README and `hca_academic_partnership_audit_trail.csv` for the full 14-institution audit trail.

This compresses ~600 words to ~80 and gives reviewer-2 a citable artifact to inspect rather than P3 supplements.

---

## Versioning policy

- **v1.0** (initial): 2021–2026 cycles, R17++ #2 dedup-corrected, frozen at GitHub commit `3fceaf8`
- **Future versions** when 2027+ NRMP cycles release: append-only; v1.0 always preserved as historical record
- All corrections logged in deposit's `CHANGELOG.md` following the R17++ citation-integrity-log model

---

## What was reverted on 2026-05-17

The earlier R17++ #3 framing as "Paper 4 — *Scientific Data* (Nature)" was added with the rationale that it would be a high-yield, low-effort publication. After honest re-assessment in response to direct user questioning, the revised assessment is:
- Technically publishable (Scientific Data acceptance ~50-65%; would clear that bar)
- Not substantively impactful (descriptor, not a finding)
- Realistic citations 10-25 over 5 years, not the 50-100 originally claimed
- ~3 weeks of writing yields a CV line + Nature title but ~zero additional research-impact yield over a Dryad/Zenodo deposit

The original `PAPER_4_DRAFT_READY.md` is preserved in git history at commit `3fceaf8` for anyone who later wants the structured 5-section outline (Background → Methods → Data Records → Technical Validation → Usage Notes) — most of that content was reframed into this deposit plan + remains usable in the deposit's README.md if needed.

---

## Source files (unchanged from reverted P4 plan; all still accurate)

- `nrmp_program_level_2021_2026.csv` — primary table
- `paper3_model5_FINAL_results.txt` — substantive validation evidence
- `verify_nrmp_pslf_eligibility.py` — classification pipeline
- `scripts/README.md` — script-to-output mapping
- `MASTER_LOCKED_NUMBERS.md` — canonical numbers
- `RUN_AUDITS.ps1` — integrity verifier (must pass at deposit time)
