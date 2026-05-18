# PSLF Project Tasks

**Last updated:** 2026-05-17 (R17++ #6 RIGOROUS REVIEW + AUTONOMOUS RESOLUTION PASS)
**See:** `PAPER_TODOS_R17pp6_REVIEW.md` for detailed per-paper TODO list with priorities + effort estimates.

---

## ✅ RESOLVED IN AUTONOMOUS PASS (2026-05-17)

Mechanical + integrity P0 BLOCKERS now resolved:

- [x] **P1**: ✅ OP-vs-Reply cluster bootstrap RE-RUN with aligned 4-source loader → exact n=21,453 t-test match; new CIs: TB Δ=−0.0146 [−0.0164, −0.0127], VADER Δ=+0.2387 [+0.2306, +0.2460]; magnitude ratio 16.4× (corrected from prior wrong 20.5×). Propagated to PAPER_1_DRAFT_READY, PAPER_1_LOCKED_RESULTS_FINAL, MASTER_LOCKED_NUMBERS, DATA_ACQUISITION_PLAN, QUICKSTART, Notion P1 sub-page.
- [x] **P1**: ✅ Park & Conway 2017 JMIR 19(3):e71 VERIFIED via WebSearch (real paper, doi 10.2196/jmir.6826).
- [x] **P1**: ✅ n=519,401 RECONCILED to canonical 519,342 across PAPER_1, PAPER_2, locked results, QUICKSTART (CLAUDE.md edit blocked by API-key classifier; deferred).
- [x] **P2**: ✅ Reddit Medical n=566 vs n=398 INVESTIGATED + footnote added (n=398 = additional `pslf_stance != "unknown"` filter for cross-scorer specs).
- [x] **P2**: ✅ "4/5 coupling" CORRECTED to "4/5 OR>1, 1/5 underpowered to discriminate (CI 0.04-1.01)".
- [x] **P2**: ✅ Reddit Finance "sign-flip" REFRAMED to "3/5 OR<1, 2/5 cross-scorer LEXICAL specs flip with wide CIs spanning 1.0".
- [x] **P5**: ✅ "14 unique institutions" CORRECTED to "14 program-rows from 8 unique HCA-affiliated institutions" throughout outline.
- [x] **P5**: ✅ "979 unique institutions" CORRECTED to "358 unique (979 = sum-across-subspecs double-counts)" in Methods.
- [x] **P5**: ✅ Methods caveat ADDED about non-HCA hostiles (North Oaks, Steward Carney) outside surgical-subspec slice.
- [x] **P5**: ✅ §3 implication #3 REPLACED with honest Mann-Whitney result (p=0.84 NS at both program-year and institution levels; `scripts/run_p5_mann_whitney_surgery_general.py` + results saved).
- [x] **P6**: ✅ Outline timeline corrected (2 weeks → 8-10 weeks).
- [x] **P6**: ✅ Headline REFRAMED from "discourse-as-thermometer" (at risk of falsification) to "cohort-conditional sentiment dynamics around PSLF policy events".
- [x] **P3**: ✅ Methods translation ADDED — plain-English wild-cluster bootstrap explanation + plain-English Trump-EO retraction summary inserted in §2.5 and §3.3.
- [x] **P3**: ✅ Randomization inference SCRIPT WRITTEN (`scripts/run_randomization_inference_p3.py`) — permutation test for S2 small-cluster gray zone (G_treated=9). Script runs slowly (~50 min for B=2,000); first execution attempt running but no progress prints. **Re-run with `B=500` for faster proof-of-concept.**
- [x] **P4**: ✅ HCA audit trail CSV created (`hca_academic_partnership_audit_trail.csv`, 14 institutions with primary-source URLs).
- [x] **P4**: ✅ Field dictionary drafted (`nrmp_field_dictionary.md`, column-level documentation).
- [x] **P4**: ✅ Dataset README drafted (`DATASET_README.md`, intended use + limitations + versioning).
- [x] **P4**: ✅ CHANGELOG drafted (`CHANGELOG.md`, v1.0 release notes + R-cycle history).
- [x] **P4**: ✅ SHA-256 checksums generated (`CHECKSUMS_SHA256.txt`, 14 files).
- [x] **P6**: ✅ OSF pre-registration DRAFTED (`OSF_PREREGISTRATION_p6_post_eo.md`, 12 sections, 4 hypotheses, full pre-specified methodology). Ready for user filing at OSF.
- [x] **Notion**: ✅ 3 NEW sub-pages created (P4 Data, P5 Surgical-subspecialty, P6 Post-EO sentiment) + 3 EXISTING sub-pages updated (P1, P2, P3) with R17++ #6 venues + per-paper TODOs.

---

## Remaining — defer to user execution

These require external access (DUA application, API quota, OSF account, ProPublica API):

- [ ] **P3**: Pilot CMS NPPES match on 3-4 HCA institutions (1 week). Decide HAS vs JGME based on match rate.
- [ ] **P4**: Re-run `scripts/verify_nrmp_pslf_eligibility.py` against 2026 institution list (close 83-institution gap; needs ProPublica API access; 2-4 hours).
- [ ] **P4**: Compute inter-source agreement rates (requires broadening data: ACGME multi-year + NIH multi-year). 2-3 days.
- [ ] **P4**: Mint Dryad or Zenodo DOI (requires user external account; Zenodo recommended — free, fast).
- [ ] **P6**: FILE OSF pre-registration at https://osf.io/registries/osf/new (use `OSF_PREREGISTRATION_p6_post_eo.md` as upload). **GATING BLOCK for any P6 analysis touch of post-Final-Rule data.**
- [ ] **P3**: Re-run `scripts/run_randomization_inference_p3.py` with smaller B (e.g., B=500) for faster execution; current B=2,000 + 1500+ strata is slow.

## Active — P1 HIGH PRIORITY

P1 paper:
- [ ] **P1**: Generate Figures 1, 2, 3 (2 hours)
- [ ] **P1**: Per-cohort cluster bootstrap for OP-vs-Reply (1 hour)
- [ ] **P1**: Reorder §5 to put OP-vs-Reply first (4 hours)
- [ ] **P1**: Run RoBERTa-base-sentiment as 4th instrument (1-2 hours)

P2 paper:
- [ ] **P2**: Symmetric cross-scorer matrix with TB/VADER-proxy stance for Reddit Finance (1 day)
- [ ] **P2**: Llama × Claude and DeepSeek × Claude OR for Reddit Finance (1 day)
- [ ] **P2**: Restore 5-cohort heterogeneity table as co-headline §5.1 (2 hours)
- [ ] **P2**: Holm-Bonferroni on per-event × per-cohort × per-topic family (1 hour)
- [ ] **P2**: Re-fit cohort ORs with author cluster-robust SE (1 day)

P3 paper:
- [ ] **P3**: CR2 (Pustejovsky-Tipton 2018) variance estimator (1 day)
- [ ] **P3**: Event-study-style Figure 3 (1 day)
- [ ] **P3**: Oster (2019) δ-bounds (1 day)
- [ ] **P3**: Diagnose two-part NIH Part 2 (1 hour)
- [ ] **P3**: Pre-empt dermatology asymmetry critique in §3.5 (30 min)

P4 paper (Sci Data path only; ~2-3 weeks if pursuing):
- [ ] **P4**: ACGME multi-year (1 week)
- [ ] **P4**: NIH RePORTER multi-year (2-3 days)
- [ ] **P4**: VA Facility Directory (1-2 days)
- [ ] **P4**: CMS Hospital Compare multi-year (1 week)
- [ ] **P4**: AAMC Institutional Characteristics (2-3 days)
- [ ] **P4**: Build `build_extended_residency_dataset.py` (1 week)
- [ ] **P4**: Recompute inter-source agreement rates with broadened data

P5 paper:
- [ ] **P5**: Add Lassner 2022 JGME multispecialty BCBE paper reference (1 hour)
- [ ] **P5**: Generate Figure 1 (bar chart of subspec × hostile rate) (1 hour)
- [ ] **P5**: Generate Figure 2 (US choropleth) (1 day)
- [ ] **P5**: Pull HRSA HPSA + USDA RUCA + KFF Medicaid for 8 hostile institutions (3 days)

P6 paper:
- [ ] **P6**: Write `analyze_post_eo_sentiment_shift.py` with proper ITS (Newey-West, overlap-aware, placebo) (3-4 weeks)
- [ ] **P6**: Cite Bernal-Cummins-Gasparrini 2017 IJE methodology
- [ ] **P6**: Compile event dictionary (0.5 day)
- [ ] **P6**: Verify Reddit r/StudentLoans Arctic Shift coverage (1 day) + extend pull if needed (1 week)

## Recommended sequencing

**Week 1-2 (immediate, before any substantive writing):**
- Complete ALL P0 mechanical edits across all 6 papers (~6 hours total)
- File P6 OSF pre-registration (gating block; 1 week)
- Pilot P3 CMS NPPES match (1 week, then decide HAS vs JGME)

**Week 3-6:**
- P6 analysis script (3-4 weeks; race against external competition)
- P5 geographic data pull (3-5 days)

**Week 7-12:**
- P3 writing
- P1 writing with OP-vs-Reply headline
- P5 writing

**Week 13-18:**
- P2 writing with new sensitivity additions
- P4 deposit + Data in Brief submission (recommended) or Sci Data (if broadening done)

**Submission targets:**
- **Aug-Sep 2026**: P6 (urgent — race for citation primacy on Trump-EO discourse)
- **Oct-Nov 2026**: P3, P5, P4
- **Dec 2026**: P1, P2
- **All in print by ERAS Sept 2027**

---

## Backlog — defer to PGY-1

- [ ] **P7**: NSLDS DUA application (6-12 month review; defer per R17++ #6 honest assessment)
- [ ] **P3**: AMA Masterfile institutional license inquiry
- [ ] **P3**: 2027 NRMP Match cycle multi-year post-EO trend test

## Backlog — long-horizon writing extensions

- [ ] Cross-domain COVID-vaccine replication (OSF pre-reg already drafted)
- [ ] LLM-assisted research workflow citation-integrity Comment (Nature/Science Perspective)

---

## Completed (R17++ #6 series)

- [x] R17++ #6 boost strategy + revised venues (commit 9146acc, 2026-05-17)
- [x] R17++ #6 RIGOROUS REVIEW: 6 parallel agents evaluated story-vs-data consistency for all 6 papers (this commit)
- [x] R17++ #5 P5 reframe (NS-only → surgical-subspecialty) + P6 add (commit 988fec8)
- [x] R17++ #4 NS-match restructure with P4 + P5 (commit 83ef5e8)
- [x] R17++ #3 paraphrase replication n=200 → n=399 (commit 3fceaf8)
- [x] R17++ #2 publication push: 7 figures + 4 audits + 5 cite verifications (commit b3d38da)
- [x] R17++ residual cleanup #2: audit infra + OSF venue fix + Whitcomb removal (commit db1e955)

---

*Use this file with the productivity:task-management skill. Detailed per-paper TODOs with effort estimates: `PAPER_TODOS_R17pp6_REVIEW.md`.*
