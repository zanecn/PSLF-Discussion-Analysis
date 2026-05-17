# PSLF Project Tasks

**Last updated:** 2026-05-17 (R17++ #6 RIGOROUS REVIEW)
**See:** `PAPER_TODOS_R17pp6_REVIEW.md` for detailed per-paper TODO list with priorities + effort estimates.

---

## Active — P0 BLOCKERS (must fix before any submission)

Mechanical edits (~6 hours total) — do these FIRST:

- [ ] **P1**: Resolve OP-vs-Reply sample discrepancy (n=21,453 t-test vs n=14,153 cluster bootstrap pair mismatch). File: `scripts/run_op_vs_reply_cluster_bootstrap.py`. 30 min code + 10 min run.
- [ ] **P1**: Verify Park & Conway 2017 JMIR citation is real (WebSearch DOI 10.2196/jmir.6826). 15 min.
- [ ] **P1**: Reconcile n=519,401 vs n=519,342 for comments TB×VADER across docs. 30 min.
- [ ] **P2**: Investigate + document Reddit Medical n=566 vs n=398 discrepancy. 1 hour.
- [ ] **P2**: Correct "4/5 coupling" → "4/5 coupling, 1/5 underpowered" for r/PSLF. 15 min.
- [ ] **P2**: Reframe Reddit Finance "sign-flip" as "2 of 5 specs (cross-scorer LEXICAL) flip with wide CIs." 30 min.
- [ ] **P4**: Re-run `verify_nrmp_pslf_eligibility.py` for 2026 institution list (close 83-institution gap). 2-4 hours.
- [ ] **P5**: Correct "14 unique institutions" → "14 program-rows, 8 unique HCA institutions" throughout. 15 min.
- [ ] **P5**: Correct "979 unique institutions" → "358 unique" in Methods. 5 min.
- [ ] **P5**: Add Methods caveat that all-HCA result is conditional on surgical-subspec slice (2 non-HCA hostiles exist outside this slice). 30 min.
- [ ] **P5**: REPLACE §3 implication #3 with honest Mann-Whitney p=0.84 NS result. 1 hour.
- [ ] **P6**: Update outline timeline (2 weeks → 8-10 weeks). 5 min.
- [ ] **P6**: Reframe headline from "discourse-as-thermometer" to defensible alternative. 1 hour.

## Active — P0 LARGER BLOCKERS

- [ ] **P3 (HAS path)**: Pilot CMS NPPES match on 3-4 HCA institutions (1 week). Decide HAS vs JGME based on match rate.
- [ ] **P3**: Add randomization inference for S2/S3 small-cluster gray zone (1 day).
- [ ] **P3**: Translate methods to JGME/HAS-readable language + plain-English Trump-EO retraction paragraph (1 day).
- [ ] **P4 (Sci Data path)**: Create `hca_academic_partnership_audit_trail.csv` with primary-source URLs (1 day).
- [ ] **P4**: Draft `nrmp_field_dictionary.md` (0.5 day).
- [ ] **P4**: Compute inter-source agreement rates (`[TO COMPUTE]` placeholder in outline; 2-3 days).
- [ ] **P4**: Mint Dryad or Zenodo DOI + README + CHANGELOG + checksums (1 day).
- [ ] **P6**: File OSF pre-registration BEFORE touching post-Final-Rule analytical data (1 week). Adapt `OSF_PREREGISTRATION_cross_domain.md`.

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
