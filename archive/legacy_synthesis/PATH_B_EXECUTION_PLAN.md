# Path B Execution Plan — 3 Tier-2 Publications in 12-18 Months

**Selected:** Path B (Tier-2 realism, 35-50% per-paper acceptance)
**Date:** 2026-05-10
**Target:** 2-3 publications by Q4 2027

---

## The three papers (Path B venues)

| # | Paper | Venue | Acceptance prob | Timeline |
|---|---|---|---|---|
| 1 | Methods: cohort-conditional construct mismatch (3 LLMs vs 2 lexical) | **EPJ Data Science** OR **Behavior Research Methods** | 40-50% | Q3 2026 |
| 2 | Substantive: PSLF discourse cohort heterogeneity + composition shifts | **Journal of Computational Social Science (JCSS)** | 35-45% | Q4 2026 |
| 3 | Policy: NRMP × PSLF program-level analysis | **JAMA Health Forum** OR **Health Services Research** | 25-35% | Q1-Q2 2027 |

**Expected outcomes:**
- Best case: 3 of 3 accepted = 3 Tier-2 publications
- Realistic: 2 of 3 accepted = 2 Tier-2 publications + 1 resubmission
- Worst case: 1 of 3 accepted on first round, 2 resubmits to lower-tier venues

---

# PAPER 1 — METHODS PAPER

## Target venue: EPJ Data Science (primary) OR Behavior Research Methods (alt)

**Why EPJ DS:**
- SentiBench 2016 venue — natural home for sentiment-instrument work
- Open-access, established for CSS methodological work
- Less domain-restrictive than Political Analysis (no "political" requirement)
- Calderon et al. 2025 published in adjacent venue (Scientific Reports), they'd be reviewers

**Why BRM as alternative:**
- Test-retest reliability has psychometric appeal
- Replication-and-validation papers welcomed
- LLM-as-instrument framing fits

## Working title (revised)

**"Convergent Validity Failure Between Lexical and LLM-Class Sentiment Instruments on Public Service Loan Forgiveness Discourse: A Three-LLM Cross-Validation"**

Note the title shift:
- "Convergent validity failure" instead of "construct mismatch" (psychometric standard)
- "Three-LLM cross-validation" foregrounds the multi-LLM design
- Empirical case (PSLF) in title positions as case study

## Headline numbers (post-3-LLM, FINAL — 2026-05-10)

n_intersection = 701 posts with all 5 instruments scored (3 LLMs + TB + VADER)

| Pairwise comparison | Pearson r | Exact-match | Cohen's κ |
|---|---|---|---|
| **Claude × Llama** | +0.703 | 73.6% | +0.572 |
| **Claude × DeepSeek** | +0.723 | 78.6% | +0.592 |
| **Llama × DeepSeek** | +0.761 | 74.2% | +0.571 |
| Claude × TextBlob | +0.066 | 20.1% | +0.002 |
| Claude × VADER | +0.134 | 21.8% | +0.023 |
| Llama × TextBlob | +0.139 | 21.7% | +0.021 |
| Llama × VADER | +0.245 | 22.3% | +0.028 |
| DeepSeek × TextBlob | +0.060 | 20.4% | +0.005 |
| DeepSeek × VADER | +0.180 | 22.4% | +0.030 |
| TextBlob × VADER | +0.308 | 27.0% | +0.087 |

**3-rater K-α (LLM-only, n=701): +0.7211** (substantial agreement; just below the 0.80 conventional reliability floor)
Adding TextBlob → 4-rater α = **+0.2732** (drop of −0.4479)
Adding VADER → 4-rater α = **+0.3298** (drop of −0.3913)

**HEADLINE FRAMING:** The construct boundary is asymmetric: it falls between LLM-class and lexical-class, NOT among individual LLMs. Three LLMs from three independent organizations across two countries (Anthropic [US] / Meta [US] / DeepSeek [China]) with three different post-training procedures (Constitutional AI/RLAIF / RLHF+DPO / GRPO) achieve substantial inter-LLM agreement. Adding either lexical instrument collapses 4-rater α by 0.39-0.45. This rules out "single-LLM idiosyncrasy" or "shared training data on a single corpus" as the explanation, since cross-organization + cross-country + cross-post-training convergence persists.

**Companion stance-task agreement (same 3 LLMs, same posts):**
- Claude × Llama: 87.8% exact-match (n=485)
- Claude × DeepSeek: 87.7% exact-match (n=472)
- Llama × DeepSeek: 85.8% exact-match (n=472)
- **All three LLMs agree: 80.9%**

Stance-task convergence is *higher* than sentiment-task convergence (pairwise sentiment exact-match 73.6-78.6% vs pairwise stance 85.8-87.8%). The 5-category stance classification — a more constrained classification problem with surface markers like "I'm pursuing PSLF", "I've decided not to apply" — shows even stronger LLM-class agreement. This extends the LLM-class convergence finding beyond a single task and strengthens the construct claim.

## Mandatory pre-submission fixes (3)

### Fix #1: Complete proper test-retest design — ✅ COMPLETE 2026-05-10

**Problem (resolved):** Round 7 "Fix 9" was marked done but only ran temp=0 vs temp=1, which measures sampling-noise-vs-no-sampling, NOT test-retest reliability.

**Action taken (2026-05-10):**
```powershell
# One run already existed (Round 7): zeroshot_sdn_temp0_retest.csv (n=605)
# New run at temp=0 produced: zeroshot_sdn_temp0_retest_RUN2.csv (n=615)
# Comparison via compare_test_retest.py
```

**FINAL RESULT (perfect determinism):**
- **Sentiment task** (5-level ordinal): exact-match **100.0%**, K-α = **+1.0000** (95% CI [+1.0000, +1.0000] B=2,000), Cohen's κ = **+1.0000**
- **Stance task** (5-class nominal): exact-match **100.0%**, κ = **+1.0000**
- **Topic task** (7-class nominal): exact-match **100.0%**, κ = **+1.0000**

**Claude Sonnet 4 at temperature=0 is empirically deterministic.** This is the strongest possible test-retest result — refutes the LLM-stochasticity reviewer objection completely.

**Comparison to Round 7 design**: temp=0 vs temp=1 had α=+0.958. The 0.042 gap below perfect agreement was entirely due to temperature=1 sampling, not test-retest noise.

**Cost: $5; Time: ~21 min. DONE.**

### Fix #2: Adopt psychometric terminology
**Problem:** "Construct mismatch" is non-standard. Reviewers will demand "convergent validity failure."

**Action:** Sweep through paper draft replacing:
- "construct mismatch" → "convergent validity failure"
- "sentiment instruments operationalize different constructs" → "instruments fail convergent validity tests"
- "measure different latent constructs" → "show insufficient convergent validity per Krippendorff's α threshold"

### Fix #3: Cite and distinguish Calderon et al. 2025
**Problem:** Calderon et al. (2025, Scientific Reports) tested 8 LLMs with K-α + bootstrap on sentiment + political leaning. Direct competitor.

**Action:** Add to introduction:
> "Calderon et al. (2025, Scientific Reports) recently tested eight LLMs against human annotators on sentiment, political leaning, emotional intensity, and sarcasm classification, finding LLMs achieve human-level reliability on sentiment and surpass humans on political leaning. Our work extends this in three respects: (1) we focus on the asymmetric construct boundary between LLM-class and lexical-class instruments rather than LLM-vs-human comparison; (2) we operate at scale (n=9,242 posts vs Calderon et al.'s smaller validation sets); (3) we include three LLMs from three independent organizations across two countries (Anthropic, Meta, DeepSeek) to test the 'shared training data' explanation for inter-LLM agreement."

## Surviving novelty claims

After honest deflation, Paper 1's surviving novelty:
1. ✅ **Three-LLM convergence with explicit shared-training-data limitation acknowledgment** (most novel work has 1-2 LLMs)
2. ✅ **OP vs Reply within-thread directional mismatch (TB vs VADER)** — operationalization is novel even if "post-comment differs" is documented
3. ✅ **At scale (n=9,242)** — Calderon et al. and adjacent work operate at smaller scales
4. ✅ **Full cross-validation panel** with 5 instruments (3 LLMs + TB + VADER) is more comprehensive than typical

## Things to CUT from this paper
- ❌ Cohort heterogeneity findings (move to Paper 2)
- ❌ Same-scorer halo Reddit Finance flip (move to Paper 2)
- ❌ Trump PSLF EO directional split (move to Paper 2 or supplement)
- ❌ Per-event topic restructuring (move to Paper 2)

## Section structure (~6-8K words for EPJ DS)

```
1. Introduction (~1,000 words)
2. Related work (~800 words) — explicit Calderon et al. distinction
3. Data: PSLF discourse (n=9,242 posts) (~600 words)
4. Methods (~1,500 words)
   4.1 Five instruments (TB, VADER, 3 LLMs)
   4.2 Krippendorff's α with bootstrap CI
   4.3 Test-retest design (proper temp=0 vs temp=0)
4.4 OP vs Reply within-thread
5. Results (~2,000 words)
   5.1 Pairwise agreement matrix
   5.2 3-LLM K-α and lexical drop
   5.3 Test-retest α
   5.4 OP vs Reply directional mismatch
6. Discussion (~1,000 words)
7. Limitations (~500 words) — explicit corpus-overlap acknowledgment
8. Supplementary
```

## Path B Paper 1 Timeline

| Week | Action |
|---|---|
| W1 | Complete proper test-retest run (temp=0 vs temp=0) |
| W1 | Run multi-LLM comparison (compare_multi_llm_vs_claude.py) |
| W2-3 | Draft sections 1-4 |
| W4-5 | Draft sections 5-7 |
| W6 | Polish + figures |
| W7 | Co-author/colleague review |
| W8 | Submit EPJ Data Science + arXiv |

**Submission target: Q3 2026**

---

# PAPER 2 — SUBSTANTIVE PAPER

## Target venue: Journal of Computational Social Science (JCSS)

**Why JCSS:**
- Open to "discourse-as-signal critique" framing
- Methodologically rigorous but accepts case studies
- 35-45% acceptance probability per audit
- Faster turnaround than top-tier venues
- Cohort heterogeneity findings fit CSS methodology venue

## Working title (revised)

**"Cohort-Conditional Sentiment-Stance Coupling in Online Policy Discourse: Evidence from Public Service Loan Forgiveness Communities, with Construct-Validity Diagnostics"**

Note shifts from earlier framing:
- "Coupling" not "decoupling" (more neutral)
- "Communities" not "cohorts" (sociological standard)
- "Construct-validity diagnostics" foregrounds methodological rigor

## Headline numbers

**Two REAL community types:**
- Reddit r/PSLF: OR=7.33 (sentiment-stance "coupled" — negative posts often pursuing)
- SDN-Medical: OR=0.27 (sentiment-stance "decoupled" — negative posts often exiting)

**Three null communities:**
- Reddit r/StudentLoans, Medical, Teaching

**One same-scorer artifact (CMV exemplar):**
- Reddit Finance: OR=0.18 (Claude×Claude) → OR=1.10 (TB×Claude) → OR=1.42 (VADER×Claude)

## Mandatory pre-submission fixes (4)

### Fix #1: Cite Wang et al. 2025 (arXiv 2509.16831) "Survivors, Complainers, Borderliners"
**Problem:** Composition-shift framing is partially scooped.

**Action:** Add to introduction:
> "Wang et al. (2025) recently demonstrated upward bias from selective posting in Reddit/Zhihu conference-review discussions, establishing that who-posts ≠ population for forum-based research. Our work extends this in policy discourse: we quantify per-author longitudinal panel infeasibility across 8 PSLF policy events, finding only 1 of 8 events meets a n>=10 returning-author threshold for within-person inference. We further demonstrate that the consequence is community-conditional: cohort-level sentiment-stance odds ratios are robust across instruments for two communities (SDN-Medical decoupling, Reddit r/PSLF coupling) but flip direction for one community (Reddit Finance) under cross-instrument operationalization."

### Fix #2: Reframe same-scorer halo as APPLIED CMV (Podsakoff 2003)
**Problem:** Reviewers will say this is textbook Common Method Variance, not novel.

**Action:**
> "We provide a clean empirical demonstration of Common Method Variance (Podsakoff et al. 2003) operating between sentiment-scoring and stance-scoring when both are LLM-derived from identical text. Reddit Finance's apparent decoupling (OR=0.18 with same-scorer Claude×Claude) reverses to OR=1.10-1.42 with cross-instrument operationalization. While CMV is well-established in survey methodology, its quantification in LLM-derived discourse measures is, to our knowledge, novel. Our result implies that LLM-scored cohort claims should report cross-instrument robustness as standard practice."

### Fix #3: Drop SDN attending OR=0.024 from headlines
**Problem:** n=88 with d=1 cell — "reject on sight" by senior reviewer.

**Action:** Move to supplement only. Headline should be cohort-level (n>=400 per cohort), not career-stage subgroup.

### Fix #4: Replace "venting culture" with neutral language
**Problem:** No literature precedent. Sounds editorial.

**Action:**
- "venting culture" → "expressive negativity decoupled from behavioral intention"
- Or: "sentiment-stance coupled pattern" (where negative sentiment co-occurs with continued pursuing)

## Surviving novelty claims

After honest deflation, Paper 2's surviving novelty:
1. ✅ **NO peer-reviewed PSLF Reddit/SDN empirical work exists** (real moat)
2. ✅ **Cohort-conditional CMV in LLM-scored sentiment-stance is novel quantitative demonstration**
3. ✅ **Per-event topic restructuring at scale** (chi-sq p<10⁻⁴ for all 8 events) — robust to CMV
4. ✅ **Per-author panel infeasibility quantified across 8 events** — affirmative methodological finding
5. ✅ **Two community types identified** (coupled vs decoupled) — even if 2 of 5 cohorts

## Things to CUT
- ❌ "Venting culture" terminology (replace with neutral)
- ❌ Same-scorer halo as "novel discovery" (reframe as APPLIED CMV)
- ❌ SDN attending OR=0.024 as headline (move to supplement)
- ❌ "Cohort heterogeneity is REAL across all instruments" (honest: SDN+r/PSLF robust, Finance flips, 3 nulls)

## Section structure (~5-7K words for JCSS)

```
1. Introduction (~800 words)
2. Related work (~600 words) — Wang et al. 2025, Bestvater & Monroe 2023, CMV literature
3. Data: PSLF discourse (n=9,242 posts) (~500 words)
4. Methods (~1,000 words)
   4.1 Sentiment + stance scoring (cite Paper 1 for instrument validation)
   4.2 Cross-instrument robustness design
   4.3 Per-author longitudinal panel feasibility test
5. Results (~2,000 words)
   5.1 Cohort-level OR table (5 communities × 3 instrument operationalizations)
   5.2 Two robust patterns (SDN, r/PSLF)
   5.3 Reddit Finance CMV exemplar (flip with instrument)
   5.4 Per-event topic restructuring (8 events, all p<10⁻⁴)
   5.5 Per-author panel infeasibility (only 1/8 events meets threshold)
6. Discussion (~800 words)
7. Limitations (~400 words)
```

## Path B Paper 2 Timeline

| Week | Action |
|---|---|
| W1 | Wait for comments collector finish + re-run cohort heterogeneity at full scale |
| W2 | Update analyses with Path B framing |
| W3-4 | Draft sections 1-4 |
| W5-6 | Draft sections 5-7 |
| W7 | Polish |
| W8 | Submit JCSS + SSRN pre-print |

**Submission target: Q4 2026**

---

# PAPER 3 — POLICY PAPER

## Target venue: JAMA Health Forum (primary) OR Health Services Research (alt)

**Why JAMA Health Forum:**
- Workforce + policy + observational design fits scope (per their 2025 Year in Review)
- 25-35% acceptance probability per audit
- Faster review than Health Affairs
- Health-policy audience

**Why HSR as alternative:**
- Strong fit for NRMP × PSLF observational design
- 30-40% acceptance probability
- Established health-services-research audience

## Working title (revised)

**"Public Service Loan Forgiveness Eligibility Differential in Residency Match Outcomes: An Observational Study of NRMP Program-Level Data, 2021-2025"**

Note shifts:
- "Eligibility differential" not "recruitment subsidy" (descriptive, not causal)
- "Observational study" foregrounds limitation
- Drop the discourse triangulation from main paper (move to Paper 1 or 2 or supplement)

## Mandatory pre-submission fixes (8)

### Fix #1: Switch venue to JAMA Health Forum (or HSR)
Health Affairs is wrong scope. Submit to JAMA HF where workforce+policy fits.

### Fix #2: Add 5+ confounders to NRMP regression
**Required confounders:**
- NIH research funding (NIH RePORTER, free)
- US-MD share vs IMG/DO mix (NRMP supplements)
- Doximity reputation rank (where available)
- Fellowship program count (ACGME data)
- University affiliation flag (yes/no)
- Urban/rural × population density
- Total beds (CMS Hospital Compare)
- Geographic region

**Cost:** $0 (all public data); ~2 weeks of data work

**New regression:**
```
fill_rate ~ pslf_eligible + cms_star_rating + nih_funding_quartile +
            us_md_share + fellowship_count + university_affiliation +
            log(total_beds) + population_density + state_FE + specialty_FE
```

### Fix #3: Replace derm with proper negative control
**Problem:** Derm has near-100% fill across all hospital types. Zero variance = useless control.

**Better negative control:** Orthopedic surgery (variable fill across hospital types but PSLF prediction is weak because orthopedic salaries are high enough to make PSLF less material).

### Fix #4: Drop "structural pre-existing" claim
**Problem:** n_hostile=4-8 in 2016-2019 is statistically empty.

**Action:** Replace with: "Pattern visible from 2020 onward (n_hostile=54). Earlier years have insufficient sample for valid comparison."

### Fix #5: Reframe MOHELA as "MOHELA-period convergence"
**Problem:** Endogenous-assignment confound — MOHELA inherited the most-distressed PSLF book.

**Action:** Replace "MOHELA caused failure" with:
> "The MOHELA tenure as PSLF servicer (July 2022-present) coincides with multi-channel discourse and complaint convergence. We cannot isolate causal MOHELA-specific performance effects from the endogenous-assignment confound that MOHELA inherited PSLF-distressed borrowers from FedLoan. The descriptive pattern replicates SBPC/AFT (2024) gray-literature observations at quantitative scale."

### Fix #6: Drop circular concern-density framing
**Problem:** 96% concern density was computed on posts pre-filtered for concern markers. Circular.

**Action:** Either:
- Re-do with INDEPENDENT keyword set (e.g., NRC Emotion Lexicon) for concern detection
- OR drop the 96% number entirely; use raw count of MOHELA mentions vs other servicers

### Fix #7: Drop PSLF Buyback 5.47× ratio (or qualify heavily)
**Problem:** 5.47× discourse:CFPB ratio is tautological for new programs. Need growth-rate baseline.

**Action:** Compare PSLF Buyback growth rate to other 2023-launched programs (e.g., SAVE plan launch). If Buyback grows faster than comparable programs, the ratio is meaningful. If similar, drop the claim.

### Fix #8: Reconcile P8 vs P11 on identical denominators
**Problem:** P8 (31.5% match) and P11 (96.2% match) used different sample subsets.

**Action:** Either:
- Re-run BOTH on the same denominator (96.2% match using direct hospital-name matching wherever possible, city-aggregate elsewhere)
- OR drop the P8-vs-P11 comparison from the paper (just report P11 as the primary analysis)

## Surviving novelty claims (after deflation)

After honest deflation, Paper 3's surviving novelty:
1. ✅ **NRMP × PSLF cross-tab is genuinely novel** (no peer-reviewed predecessor)
2. ✅ **For-profit chain residency fill-rate analysis** is unoccupied
3. ✅ **PSLF Buyback documentation** (with proper baseline framing) is unoccupied
4. ✅ **Trump PSLF EO empirical effects** are unoccupied
5. ⚠️ MOHELA convergence (descriptive only, not causal)
6. ⚠️ NHSC HPSA correlation is established background, not novel

## Things to CUT or RELOCATE
- ❌ Discourse triangulation (76K Reddit + 4.7K SDN posts) — DROP from main paper, move to supplement or Paper 1/2
- ❌ MOHELA "caused failure" framing (drop causal language)
- ❌ Buyback 5.47× ratio without baseline comparison (drop or qualify heavily)
- ❌ Derm as negative control (replace)
- ❌ "Structural pre-existing" claim (drop)
- ❌ P8 vs P11 different-denominator comparison (drop)

## Section structure (~3-5K words for JAMA Health Forum)

```
1. Introduction (~600 words) — PSLF context + workforce question + hypothesis
2. Methods (~1,000 words)
   2.1 NRMP data 2021-2025 (program-year level)
   2.2 PSLF eligibility classification (heuristic + ProPublica IRS verification)
   2.3 Confounders (NIH funding, US-MD share, fellowships, university affiliation, etc.)
   2.4 OLS with state FE + specialty FE + HC3 robust SEs
2.5 Pre-2020 backfill (with explicit n_hostile<10 caveat)
3. Results (~1,500 words)
   3.1 Headline: PSLF-eligible fill rate by employer type (with full controls)
   3.2 Specialty pattern (IM, FM, EM positive; new negative control specialty)
   3.3 Pre/post 2020 (with explicit baseline-insufficient caveat)
   3.4 Geographic (HPSA × PSLF interaction; honest "doesn't preferentially target")
4. Discussion (~600 words)
5. Limitations (~400 words) — observational, no W-2 verification, NSLDS DUA pending
```

## Path B Paper 3 Timeline

| Week | Action |
|---|---|
| W1-2 | Send NRMP usage permission email + apply for NSLDS DUA |
| W1-2 | Add 5+ confounders to regression (NIH funding, IMG share, fellowships, etc.) |
| W3 | Re-run P11 with full confounders |
| W4 | Replace derm negative control with orthopedic surgery |
| W5-6 | NRMP backfill check (Wayback Machine retry for 2010-2015) |
| W7-10 | Draft sections 1-5 |
| W11 | Polish |
| W12 | Submit JAMA Health Forum |

**Submission target: Q1-Q2 2027**

---

# IMMEDIATE NEXT ACTIONS (this week)

## User actions
1. ⏳ Run multi-LLM comparison: `compare_multi_llm_vs_claude.py` — paste output to me
2. ⏳ Send NRMP usage permission email (datarequest@nrmp.org)
3. ⏳ Send NSLDS DUA inquiry (RUDDS@ed.gov)
4. ⏳ Send AAMC GQ inquiry (gq@aamc.org)
5. ⏳ Run proper test-retest (temp=0 vs temp=0, n=200, ~$2)

## Claude/AI actions
6. ⏳ After multi-LLM comparison: update Methods Paper page with 3-LLM headline numbers
7. ⏳ After comments collector finishes: re-run cohort heterogeneity at full scale
8. ⏳ Update Notion pages with Path B venue framing (EPJ DS / JCSS / JAMA HF)
9. ⏳ Begin Paper 1 outline draft (Q3 2026 target)

---

# Total Path B Timeline

| Quarter | Milestones |
|---|---|
| Q3 2026 | Paper 1 (Methods, EPJ DS) drafted + submitted + arXiv |
| Q4 2026 | Paper 2 (Substantive, JCSS) drafted + submitted + SSRN |
| Q1-Q2 2027 | Paper 3 (Policy, JAMA HF) drafted + submitted |
| Q3 2027 | Paper 1 acceptance/revision (peer review takes 3-6 months at EPJ DS) |
| Q4 2027 | Paper 2 acceptance/revision |
| Q1-Q2 2028 | Paper 3 acceptance/revision |

**Total time to first publication: ~12 months (Paper 1 published Q3 2027)**
**Total time to all 3 publications: ~18-24 months (all published by Q2 2028)**

---

# Decision points along the way

## After Paper 1 acceptance (or rejection)
- **If accepted**: confirm Paper 2 + Paper 3 strategy
- **If rejected at EPJ DS**: try Behavior Research Methods, then JCSS, then PLOS One
- **If rejected at all 3 Tier-2 venues**: substantial reframing needed

## After comments collector finishes
- **If cohort heterogeneity holds at full scale**: strengthens Paper 2
- **If cohort heterogeneity weakens**: Paper 2 needs reframing

## After NSLDS DUA approved (6-12 months)
- **If approved**: dramatically strengthens Paper 3 — could even attempt Health Affairs Tier-1
- **If denied/delayed**: Paper 3 stays at JAMA HF as observational

## After cross-domain replication run (optional, $50)
- **If COVID-vaccine replicates the methods finding**: could attempt Political Analysis for Paper 1
- **If COVID-vaccine doesn't replicate**: stick with EPJ DS

---

# Key risks and mitigations

| Risk | Probability | Mitigation |
|---|---|---|
| Multi-LLM comparison shows 3-LLM K-α < 0.5 | Low (~10%) | Reframe as "LLMs disagree among themselves" — still publishable |
| Comments collector reveals cohort heterogeneity weakens | Moderate (~30%) | Paper 2 framing already honest about CMV |
| Paper 1 desk-rejected at EPJ DS | Low (~15%) | Behavior Research Methods is excellent fallback |
| Paper 3 desk-rejected at JAMA HF | Moderate (~30%) | Health Services Research is excellent fallback |
| NSLDS DUA denied | Low (~20%) | Paper 3 stays observational at JAMA HF |
| NRMP usage permission denied | Very low (~5%) | Re-derive analyses from public summaries only |

---

## Bottom line for Path B

**Realistic expected outcome (12-18 months):**
- 2 Tier-2 publications minimum
- Possibly 3 Tier-2 publications
- Cumulative impact comparable to 1 Tier-1 publication
- Lower variance, faster timeline, more sustainable narrative

**The next 30 minutes:**
1. Run `compare_multi_llm_vs_claude.py` (paste output to me)
2. Send 3 emails (NRMP, NSLDS, AAMC GQ) — ~15 min total

**The next 2 weeks:**
1. Run proper test-retest design (temp=0 vs temp=0, $2)
2. Wait for comments collector to finish (auto)
3. Re-run cohort heterogeneity at full scale (auto when comments done)

**The next 4 weeks:**
1. Draft Paper 1 outline → full draft (4-6 weeks of focused writing)
2. Update Notion pages with Path B framing