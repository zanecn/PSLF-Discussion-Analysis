# Path B Status Dashboard — Three-Paper Pipeline

**Last updated:** 2026-05-10 (evening)
**Path:** Path B (Tier-2 venues; 35-50% per-paper acceptance)
**Status:** **All three substantive analyses LOCKED. Drafts can begin immediately.** Only user-actions remaining (test-retest run + comments collector finish).

---

## Executive snapshot

| Paper | Venue | Outline | Mandatory fixes | Data acquisition | Submission target |
|---|---|---|---|---|---|
| **P1 Methods** | EPJ Data Science | ✅ done | **3+3 strengtheners (6 ✅ / 0 🔲)** | ✅ done; multi-LLM SDN-included α=+0.76; paraphrase-robust α=+0.90 | Q3 2026 |
| **P2 Substantive** | JCSS | ✅ done | 4 (4 ✅ / 0 🔲) | 🔲 comments collector pending | Q4 2026 |
| **P3 Policy** | JGME (was JAMA HF) | ✅ done | **8+1 strengthener (9 ✅ / 0 🔲)** | ✅ Model 5 + neg-control + wild-cluster bootstrap LOCKED | **Q4 2026** |

**ALL 15 mandatory pre-submission fixes are now COMPLETE (15/15).** Only the comments collector finish remains as a pending dependency (for Paper 2 to update at full scale — but Paper 2 substantive results are already correct at current scale).

**Critical update (2026-05-10):** NRMP DUA / NSLDS DUA / AAMC GQ are NOT needed for Path B. NRMP data is already extracted from publicly-published Match Results PDFs. NSLDS + AAMC are deferred to future work (individual-level data, not needed for program-level Paper 3 design). All Paper 3 confounders are publicly available. **Paper 3 timeline accelerated ~6 months.**

**Critical path:** Paper 1 → Paper 2 → Paper 3 (sequenced; each cites the prior).

---

## Empirical headline numbers (locked, ready to write into drafts)

### Paper 1 (Methods) — multi-LLM convergence

- **n_intersection (5-instrument): 701 posts** (Claude + Llama + DeepSeek + TextBlob + VADER)
- **3-LLM Krippendorff α = +0.7590** [bootstrap 95% CI +0.7241, +0.7868] (Round 16 Strengthener 1: SDN included, n_intersection now 1001 from prior 701; Reddit-subset α=+0.69 boundary, **SDN-subset α=+0.83 above Krippendorff's 0.80 satisfactory-reliability floor**)
- **Paraphrase-robustness K-α = +0.9011** [bootstrap CI +0.8571, +0.9380] across 3 alternative system prompts on n=200 SDN posts (Round 16 Strengthener 2: above pre-specified 0.85 threshold for true test-retest under prompt variation; supersedes the API-determinism-only "100% exact-match" framing)
- **+ TextBlob → 4-rater α = +0.2732** (drop −0.4479)
- **+ VADER → 4-rater α = +0.3298** (drop −0.3913)
- **Pairwise inter-LLM r**: Claude×Llama 0.703 / Claude×DeepSeek 0.723 / Llama×DeepSeek 0.761
- **Pairwise inter-LLM exact-match**: 73.6% / 78.6% / 74.2%
- **Pairwise inter-LLM Cohen's κ**: +0.572 / +0.592 / +0.571 (moderate per Landis & Koch 1977)
- **All LLM-vs-lexical r < 0.30; all LLM-vs-lexical κ ≤ 0.030** (asymmetric construct boundary)
- **Test-retest α (Round 7 exploratory; temp=0 vs temp=1, n=605): +0.958** [+0.938, +0.975]
  - 🔲 Proper temp=0 vs temp=0 design pending (n=200, ~$2)
- **OP-vs-Reply Δ**: TB=−0.017 / VADER=+0.220 (cluster-bootstrap p≈0; same-direction-mismatch in 8/8 cohorts)
- **3-LLM stance task agreement** (companion to sentiment task): Claude×Llama 87.8% / Claude×DeepSeek 87.7% / Llama×DeepSeek 85.8% / **all-three-agree 80.9%** (n=472-485). Stance task convergence is *higher* than sentiment task convergence — strengthens LLM-class construct claim.
- **Test-retest reliability (FINAL, n=615 SDN posts; LOCKED 2026-05-10)**: Two temperature=0 runs, separate API calls — **100.0% exact-match on ALL THREE tasks**:
  - Sentiment (5-level ordinal): exact-match 100%, K-α=+1.0000 (95% CI [+1.0000, +1.0000] B=2,000); κ=+1.0000
  - Stance (5-class nominal): exact-match 100%, κ=+1.0000
  - Topic (7-class nominal): exact-match 100%, κ=+1.0000
- **Claude Sonnet 4 at temperature=0 is empirically deterministic.** Refutes the LLM-stochasticity reviewer objection at the strongest possible level. The 3-LLM cross-instrument disagreement is NOT due to noise; it is substantive construct disagreement.

### Paper 2 (Substantive) — cohort heterogeneity

- **5 cohorts × 3 operationalizations** OR table (Section 5.1)
- **Two robust patterns**:
  - **Reddit r/PSLF coupling**: same-scorer OR=7.33; cross-scorer 1.66/2.53 (still > 1)
  - **SDN-Medical decoupling**: same-scorer OR=0.27; cross-scorer 0.15/0.33 (still < 1)
- **Three null cohorts**: r/StudentLoans, Medical, Teaching (CIs include 1)
- **One same-scorer halo (CMV exemplar)**: Reddit Finance same-scorer OR=0.18 → cross-scorer 1.10/1.42 (CMV-induced sign flip)
- **Per-event topic restructuring**: chi-sq p<10⁻⁴ in 8/8 events (composition-immune)
- **Per-author panel infeasibility**: only 1/8 events meets n≥10 returning-author threshold (Trump EO, n=13)
  - Within-person Δ rejecting = +16.67 pp [−16.7, +50.0], McNemar's p=0.625

### Paper 3 (Policy) — NRMP × PSLF program-year — UPDATED 2026-05-10

- **Sample**: n=32,612 NRMP program-year observations (2021-2025), 789 institutions, 28 specialties
- **PSLF-eligible**: n=17,104; **Ambiguous**: n=11,872; **PSLF-hostile**: n=485
- **Headline (Model 4, with city CMS quality + state FE + specialty FE)**:
  - PSLF-hostile β = **−18.56 pp** (95% CI [−21.0, −16.1]; p<10⁻⁷⁵)
  - PSLF-eligible β = −0.15 pp (NS)
- **Headline (Model 5, with FULL audit-required confounders)** — **NEW 2026-05-10**:
  - PSLF-hostile β = **−18.07 pp** (cluster-robust 95% CI [−24.80, −11.35]; p=1.4×10⁻⁷ — Round 16 corrected with cluster-robust SE on institution; HC3 was overstated)
  - PSLF-friendly β = −0.44 pp (NS)
  - **Shrinkage from M4 to M5: only 0.32 pp.** The audit-required confounders DO NOT explain the differential.
  - **R² = 0.118**; n=32,612
  - Confounders added: university_affiliation, academic_med_center, n_specialties, log(residents), CMS Star Rating, CMS for-profit share
- **Headline (Model 5 + NIH FY2023 funding)** — **NEW 2026-05-10 (FULLY LOCKED)**:
  - PSLF-hostile β across 3 HCA-academic-partnership specifications: S1 (status quo) **−18.07 pp** (wild-cluster p<0.0005), S2 (reclassified as ambiguous) **−16.25 pp** (wild-cluster p=0.017), S3 (dropped) **−17.14 pp** (wild-cluster p=0.006). All cluster-robust CIs exclude zero by wide margins; **all three survive Cameron-Miller wild-cluster bootstrap correction at α=0.05**.
  - log(NIH funding) coefficient: +0.03 pp NS (p=0.21)
  - **Total cumulative shrinkage M1 → M5+NIH: 0.54 pp across 9 confounders + 2 FE.** Result is locked.
- **Negative control (orthopedic surgery)** — **NEW 2026-05-10**:
  - PSLF-hostile β = **+0.67 pp NS** (p=0.26; n=1,119)
  - **Strongly consistent with PSLF financial-incentive mechanism** (vs −18 pp in primary care pooled)
  - Refutes "uniform recruitment confound" alternative explanation
- **Survives across M1-M5+NIH with full cluster-robust SE specifications S1/S2/S3** (range −16 to −18 pp). Honest framing: low coefficient shrinkage means audit-required confounders DO NOT VARY substantially across the PSLF-class contrast (Round 15 conceptual reframe), NOT that the headline is robust to omitted institution-level confounders.
- **Pre-Waiver baseline (Limited PSLF Waiver, Oct 2021)**: insufficient (n_hostile=6 in 2016, n_hostile=8 in 2017; n_hostile=54 in 2020)
- **Pattern stable 2020-2025**: gap +10 to +16 pp every year
- **Within-institution DiD (2016-20 vs 2022-25)**: friendly Δ −0.93 pp, hostile Δ −8.97 pp; DiD = +8.04 pp, p=0.098 (NS)
- **Specialty heterogeneity**: large gaps in primary care (FM, IM, EM, Peds); null in surgical (Surgery, Derm, Psychiatry)
  - Consistent with PSLF financial-incentive mechanism
- **All 8 mandatory pre-submission fixes are COMPLETE or near-complete.**

---

## Mandatory pre-submission fixes — full status

### Paper 1 (Methods, EPJ DS) — 3 fixes

| # | Fix | Status | Owner | Cost / time |
|---|---|---|---|---|
| 1 | Complete proper test-retest design (temp=0 vs temp=0, n=200) | 🔲 pending | User + Claude | ~$2, 30 min × 2 days |
| 2 | Adopt psychometric terminology ("convergent validity failure") | ✅ done in outline | — | — |
| 3 | Cite and distinguish Calderon et al. 2025 | ✅ done in outline | — | — |

### Paper 2 (Substantive, JCSS) — 4 fixes

| # | Fix | Status | Owner | Cost / time |
|---|---|---|---|---|
| 1 | Cite Wang et al. 2025 (composition-bias scoop) | ✅ done in outline | — | — |
| 2 | Reframe same-scorer halo as APPLIED CMV (Podsakoff 2003) | ✅ done in outline | — | — |
| 3 | Drop SDN attending OR=0.024 from headlines (move to Supplement) | ✅ done in outline | — | — |
| 4 | Replace "venting culture" with neutral language | ✅ done in outline | — | — |

### Paper 3 (Policy, JAMA HF) — 8 fixes

| # | Fix | Status | Owner | Cost / time |
|---|---|---|---|---|
| 1 | Switch venue from Health Affairs to JAMA HF | ✅ done | — | — |
| 2 | Add 5+ confounders to NRMP regression | ✅ **DONE 2026-05-10** — Model 5: PSLF-hostile β=−18.24 pp, only 0.32 pp shrinkage from M4 | Claude | done |
| 3 | Replace derm with orthopedic surgery negative control | ✅ **DONE 2026-05-10** — PSLF-hostile β=+0.67 NS in ortho (n=1,119); contrasts with −18 pp in primary care | Claude | done |
| 4 | Drop "structural pre-existing" claim | ✅ done | — | — |
| 5 | Reframe MOHELA as "MOHELA-period convergence" | ✅ done | — | — |
| 6 | Drop circular concern-density framing | ✅ done | — | — |
| 7 | Drop or qualify PSLF Buyback 5.47× ratio | ✅ done | — | — |
| 8 | Reconcile P8 vs P11 on identical denominators | ✅ done | — | — |

**Substantive results LOCKED.** Only NIH funding integration remains (running in background); will likely shift β by <1 pp.

---

## Immediate next actions (this week)

### USER actions (REVISED 2026-05-10 — dropped NSLDS, AAMC, NRMP DUA)

1. 🔲 **Run proper test-retest** (one new run; baseline already exists). ~$3-5, ~10 min:
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-..."
   cd C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis
   C:\Users\zanen\anaconda3\python.exe ..\scripts\sentiment_zeroshot.py `
     --input forum_pslf_discussions.csv `
     --retest-source-csv zeroshot_sdn_temp0_retest.csv `
     --temperature 0 `
     --output zeroshot_sdn_temp0_retest_RUN2.csv
   ```
2. 🔲 Wait for comments collector to finish (was at 88% / 17,888 of 20,366 posts as of 2026-05-09)
3. 🔲 Download NIH RePORTER funding data 2018-2024 (free, ~30 min): https://reporter.nih.gov/exporter
4. 🔲 Acquire ACGME accreditation reports (free, ~30 min): https://www.acgme.org/about/publications-and-resources/data-collection-systems/

**DROPPED from critical path:**
- ~~NRMP usage permission email~~ — already have publicly-extracted Match Results data
- ~~NSLDS DUA~~ — not needed for program-level analysis; defer to future work
- ~~AAMC GQ inquiry~~ — not needed for program-level analysis; defer to future work

### Claude/AI actions (after user kicks off above)

6. 🔲 After user runs test-retest: compute Krippendorff α between two runs, update Paper 1 Section 4.4
7. 🔲 After comments collector finishes: re-run cohort heterogeneity at full scale, update Paper 2 Section 5
8. 🔲 After NRMP data acquired: re-run Model 5 with 5+ confounders, update Paper 3 Section 3.2
9. 🔲 After negative-control re-run: write Paper 3 Section 3.5 with orthopedic surgery results
10. 🔲 Compute bootstrap CIs (B=2,000 stratified by cohort) for all Paper 1 K-α point estimates

---

## Risk register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Test-retest temp=0/temp=0 α < 0.85 | Low (~10%) | Paper 1 LLM-stochasticity defense weakens | Reframe as "temp=0 vs temp=1 α=+0.958 documents low LLM stochasticity even under sampling-variant conditions" |
| Comments collector reveals cohort heterogeneity weakens | Moderate (~30%) | Paper 2 substantive lead weakens | CMV demonstration framing already honest; topic restructuring still composition-immune |
| Model 5 PSLF-hostile β attenuated to <−10 pp | Moderate (~25%) | Paper 3 headline weakens | Honest report of attenuated estimate; reframe headline as "differential persists after extensive confounder adjustment, reduced from −18 pp to −X pp" |
| Negative-control orthopedic surgery shows similar PSLF-hostile β | Low (~15%) | Paper 3 mechanism interpretation collapses | Frame as "PSLF-hostile differential is structural and not specific to PSLF financial mechanism; further work needed to identify mechanism" |
| EPJ DS desk-reject Paper 1 | Low (~15%) | Restart submission cycle | Behavior Research Methods is clean fallback (test-retest framing fits BRM scope) |
| NRMP data acquisition denied | Low (~10%) | Paper 3 cannot proceed | Pivot to ACGME-only data + ProPublica institution-type analysis |
| NSLDS DUA approved within 12 months | Low (~25%) | Major Paper 3 enhancement | If approved early, augment Paper 3 with individual-level loan-history-PSLF-eligibility match |
| Cross-domain replication shows Methods finding doesn't replicate | Low (~10%) | Paper 1 generalizability claim weakens | Frame as "PSLF-specific finding; cross-domain extension is open work" |

---

## Surviving novelty claims (per paper, post-deflation)

### Paper 1 (Methods)
1. ✅ Cross-organization three-LLM cross-validation at scale on policy-discourse text (most prior work uses 1-2 LLMs at smaller scale)
2. ✅ Asymmetric LLM-class vs lexical-class construct boundary (theoretically grounded but not previously quantified at this scale)
3. ✅ OP-vs-Reply within-thread directional mismatch (no published precedent found)
4. ✅ Proper test-retest reliability for LLM scoring at temperature=0 (closes the LLM-stochasticity reviewer objection)
5. ✅ Three-LLM convergence on companion stance task at 80.9% all-three-agree (extends the LLM-class convergence finding beyond a single sentiment task)

### Paper 2 (Substantive)
1. ✅ NO peer-reviewed PSLF Reddit/SDN empirical work exists (real moat)
2. ✅ Cohort-conditional CMV in LLM-scored sentiment-stance is novel quantitative demonstration
3. ✅ Per-event topic restructuring at scale (chi-sq p<10⁻⁴ for all 8 events) — robust to CMV
4. ✅ Per-author panel infeasibility quantified across 8 events — affirmative methodological finding
5. ⚠️ Two community types identified (coupled vs decoupled), only 2 of 5 cohorts; honest framing

### Paper 3 (Policy)
1. ✅ NRMP × PSLF program-year cross-tab is genuinely novel (no peer-reviewed predecessor)
2. ✅ For-profit chain residency fill-rate analysis (n=485 hostile programs) is unoccupied
3. ✅ ProPublica IRS-verified PSLF-eligibility classification methodology is new
4. ⚠️ Specialty heterogeneity consistent with PSLF mechanism (suggestive, not direct evidence)
5. ⚠️ Within-institution DiD null is interpretable as structural-not-treatment (honest framing)

---

## Key file inventory

| File | Role |
|---|---|
| `PATH_B_EXECUTION_PLAN.md` | Master roadmap with venue selection rationale + per-paper timelines |
| `PATH_B_STATUS_DASHBOARD.md` | This file — live status snapshot |
| `PAPER_1_EPJ_DS_methods_only_OUTLINE.md` | Paper 1 full outline (8 sections + 8 supplements) |
| `PAPER_2_JCSS_substantive_OUTLINE.md` | Paper 2 full outline (8 sections + 7 supplements) |
| `PAPER_3_JAMA_HF_policy_OUTLINE.md` | Paper 3 full outline (5 sections + 8 supplements + 8 fix checklist) |
| `PAPER_1_combined_methods_substantive_OUTLINE.md` | Legacy combined outline (Tier-1 Political Analysis target) — superseded by separate Paper 1 + Paper 2 outlines under Path B |
| `AUDIT_round14_ADVERSARIAL_LITERATURE_REVIEW.md` | Adversarial audit synthesis driving Path B selection |
| `AUDIT_round13_LLM_REPLICATION_AND_COHORT_FRAGILITY.md` | Llama replication + L5 cross-instrument robustness |
| `OSF_TRANSPARENCY_PACKAGE.md` | Reproducibility package outline |
| `OSF_PREREGISTRATION_cross_domain.md` | Pre-registration of COVID-vaccine cross-domain replication |
| `cross_domain_replication_design.md` | Cross-domain replication design (optional, ~$50) |
| `NRMP_program_level_data_instructions.md` | User-action: NRMP data request |
| `NSLDS_DUA_application_instructions.md` | User-action: NSLDS DUA application (6-12 months turnaround) |
| `AAMC_GQ_data_request_instructions.md` | User-action: AAMC Graduation Questionnaire data request |

---

## Total Path B timeline (REVISED 2026-05-10)

| Quarter | Milestone |
|---|---|
| **Q3 2026** | Paper 1 (Methods, EPJ DS) drafted, submitted, arXiv pre-print posted |
| **Q3-Q4 2026** | Paper 3 (Policy, JAMA HF) drafted **IN PARALLEL** with Paper 2 (no DUA bottleneck) |
| **Q4 2026** | Paper 2 (Substantive, JCSS) drafted, submitted, SSRN pre-print posted |
| **Q4 2026 / Q1 2027** | Paper 3 submitted, medRxiv pre-print posted |
| Q3 2027 | Paper 1 acceptance/revision (3-6 month peer review at EPJ DS) |
| Q4 2027 | Paper 2 acceptance/revision |
| Q1-Q2 2027 | Paper 3 acceptance/revision |

**First publication target: Q3-Q4 2027 (Paper 1).**
**All-three target: Q4 2027 - Q1 2028 (~6 months earlier than original Path B).**

**Critical change**: Paper 3 was the bottleneck due to NSLDS DUA (6-12 months). Dropping NSLDS shifts Paper 3 to parallel-able with Paper 2. The blocker now is just Paper 1 → Paper 2 sequencing (Paper 2 cites Paper 1 for instrument validation).

---

## Decision points

### After Paper 1 acceptance (or rejection)
- ✅ Accepted at EPJ DS → confirm Paper 2 + 3 strategy
- ❌ Desk-rejected at EPJ DS → submit to Behavior Research Methods (excellent fallback for test-retest framing)
- ❌ Rejected after peer review at EPJ DS → submit to JCSS or PLOS One

### After comments collector finishes
- ✅ Cohort heterogeneity holds at full scale → strengthens Paper 2
- ❌ Cohort heterogeneity weakens with comments → reframe Paper 2 around CMV diagnostic + topic restructuring (composition-immune findings only)

### After NSLDS DUA approved (6-12 months)
- ✅ Approved early → augment Paper 3 with individual-level loan-history-PSLF-eligibility analysis (potentially upgrade venue to Health Affairs)
- 🔲 Denied/delayed → Paper 3 stays at JAMA HF as observational program-level analysis

### After cross-domain replication run (optional, ~$50)
- ✅ COVID-vaccine replicates the methods finding → could attempt Tier-1 Political Analysis for Paper 1 (would push out timeline 6-12 months)
- ❌ COVID-vaccine doesn't replicate → stick with EPJ DS

---

*End of dashboard. Update this file as fixes complete and data lands.*
