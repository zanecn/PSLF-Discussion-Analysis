# Master Locked Numbers — All 3 Papers (Path B)

**Last updated:** 2026-05-10 (post-Round-17 audit + dedup-fix re-runs)
**Status:** All numbers locked. Round 17 corrections applied: CMS-merge dedup fix (8 case-collision city duplicates removed) propagated to all Model 5 scripts; state-filtered NIH integrated; Trump-EO causal interpretation retracted (replaced with multi-year trend documentation); Paper 2 scoped to post-level cohort heterogeneity.

This document is the canonical numerical reference for drafting. **If a number appears here and in a paper outline, this document wins.**

---

## Corpus

| Quantity | Value | Source |
|---|---|---|
| PSLF-strict-filtered Reddit posts | 76,074 | Arctic Shift archive |
| PSLF-strict-filtered SDN posts | 4,749 | Playwright scrape |
| Reddit comments (collected) | ⏳ ~600K (final TBD when collector finishes) | PRAW collector |
| Three-rater intersection (TB+VADER+Claude) | n=9,242 | Claude scoring across all sources |
| Five-instrument intersection (3 LLMs + TB + VADER) | **n=1,001** (Reddit n=701 + SDN n=300) | Round 16 Strengthener 1 |
| Subreddits sampled | 21 | r/PSLF, r/StudentLoans, r/personalfinance, r/financialindependence, r/medicalschool, r/medicine, r/Residency, r/PAstudent, r/prephysicianassistant, r/CRNA, r/medicine, r/nursing, r/Teachers, r/teaching, etc. |
| SDN forum sub-forums | 1 (Medical/Pre-Med Allopathic) | studentdoctor.net |
| Date range | 2010–2025 | All sources |

---

## PSLF policy events (8)

| Event | Date | Pre window | Post window |
|---|---|---|---|
| Limited PSLF Waiver | 2021-10-06 | 60d | 60d |
| IDR Account Adjustment | 2022-04-19 | 60d | 60d |
| Biden Mass Forgiveness Plan | 2022-08-24 | 60d | 60d |
| Biden v. Nebraska SCOTUS | 2023-06-30 | 60d | 60d |
| Payments Restart | 2023-10-01 | 60d | 60d |
| SAVE Plan Administrative Forbearance | 2024-08-09 | 60d | 60d |
| Trump PSLF Executive Order | 2025-03-07 | 60d | 60d |
| Final Trump PSLF Rule | 2025-10-30 | 60d | 60d |

---

## Paper 1 (Methods) — locked numbers

### Sample

- 5-instrument intersection: **n=1,001** (Reddit n=701, SDN n=300)
- Test-retest sample: n=605 (SDN, two temp=0 runs)
- Paraphrase-robustness sample: **n=200** (SDN, baseline + 2 alt prompts)
- Stance-task sample: n=485 (Claude × Llama), n=472 (Claude × DeepSeek, Llama × DeepSeek), n=472 (all-three-agree)

### Multi-LLM convergence (Strengthener 1 expanded sample)

| Quantity | Value | Source file |
|---|---|---|
| **3-LLM K-α (combined)** | **+0.7590** [bootstrap CI +0.7241, +0.7868] | `paper1_multi_llm_with_sdn_results.txt` |
| 3-LLM K-α (Reddit subset) | +0.6901 [+0.6462, +0.7302] | same |
| **3-LLM K-α (SDN subset)** | **+0.8306** [+0.7870, +0.8661] | same |
| 3-LLM + TextBlob (FIXED, combined) | +0.3415 [+0.3079, +0.3760] | same |
| 3-LLM + TextBlob (QCUT, combined) | +0.3347 [+0.2980, +0.3705] | same |
| 3-LLM + VADER (FIXED, combined) | +0.2385 [+0.2021, +0.2728] | same |
| 3-LLM + VADER (QCUT, combined) | +0.3983 [+0.3611, +0.4331] | same |
| All 5 (FIXED, combined) | +0.1703 [+0.1402, +0.1981] | same |
| All 5 (QCUT, combined) | +0.2723 [+0.2410, +0.3018] | same |

### Pairwise instrument agreement (combined n=1001)

| Pair | Pearson r | Exact-match (FIXED) | Exact-match (QCUT) |
|---|---|---|---|
| Claude × Llama | +0.737 | 68.2% | 68.2% |
| Claude × DeepSeek | +0.785 | 75.9% | 75.9% |
| Llama × DeepSeek | +0.811 | 71.3% | 71.3% |
| Claude × TextBlob | +0.021 | 30.1% | 21.7% |
| Claude × VADER | +0.089 | **9.0%** | 19.6% |
| Llama × TextBlob | (TBD from sourcefile) | (FIXED) | (QCUT) |
| Llama × VADER | (similar pattern) | (~10%) | (~22%) |
| DeepSeek × TextBlob | (TBD) | (similar) | (similar) |
| DeepSeek × VADER | (TBD) | (~10%) | (~22%) |
| TextBlob × VADER | +0.339 | 8.4% | 26.2% |

### Stance task (3-LLM)

| Pair | Exact-match | n |
|---|---|---|
| Claude × Llama | 87.8% | 485 |
| Claude × DeepSeek | 87.7% | 472 |
| Llama × DeepSeek | 85.8% | 472 |
| **All-three-agree** | **80.9%** | 472 |

### Test-retest (Strengthener 2)

| Quantity | Value | Source |
|---|---|---|
| **Sentiment 3-prompt K-α (CURRENT, n=399 R17++ #3 replication)** | **+0.9011** [+0.8680, +0.9300] | `paper1_paraphrase_robustness_results.txt` |
| Sentiment 3-prompt K-α (n=200 R16 historical, locked) | +0.9011 [+0.8571, +0.9380] | `zeroshot_sdn_paraphrase_v1_n200_historical.csv` + `..._v2_n200_historical.csv` |
| Sentiment baseline-vs-paraphrase-1 exact-match (n=399) | 89.22% (was 89.5% at n=200) | same |
| Sentiment baseline-vs-paraphrase-2 exact-match (n=399) | 85.46% (was 86.0% at n=200) | same |
| Sentiment paraphrase-1-vs-2 exact-match (n=399) | 94.24% (was 93.5% at n=200) | same |
| Stance 3-prompt pairwise exact-match (n=231 valid) | 93.07%–96.10% (was 92.98%–95.61% at n=114 R16) | same |
| Topic 3-prompt pairwise exact-match (n=399 valid) | 92.23%–94.24% (was 93.00%–95.00% at n=200 R16) | same |
| Lower-CI headroom above 0.85 threshold | n=200: +0.007 · **n=399: +0.018** (2.5× more headroom) | same |
| CI half-width tightening ratio (n=399 vs n=200) | 0.766 (Bessel-expected 0.71 at 2× sample) | same |
| API determinism (temp=0 vs temp=0, same prompt) | 100.00% | `test_retest_FINAL_results.txt` |
| Round 7 noise check (temp=0 vs temp=1) | α=+0.958 [+0.938, +0.975] | (legacy) |

### OP-vs-Reply within-thread (LOCKED at full comments scale, 2026-05-10)

Full-scale analysis: n=21,453 OPs, 506,639 comments aggregated, mean 23.6 comments/post.

| Quantity | Value |
|---|---|
| **TextBlob Δ (OP − reply) overall** | **−0.0146** (n=21,453; t=−15.10, p=2.8×10⁻⁵¹; **cluster-bootstrap CI [−0.0164, −0.0127], B=2,000, boot p=0; R17++ #6 RIGOROUS REVIEW re-run 2026-05-17 with aligned 4-source loader for exact t-test parity**) |
| **VADER Δ (OP − reply) overall** | **+0.2387** (n=21,453; t=60.40, p≈0; **cluster-bootstrap CI [+0.2306, +0.2460], B=2,000, boot p=0**) |
| **Magnitude ratio |VADER|/|TB|** | **16.4×** (R17++ #6 correction; prior wrong value 20.5× was from a different n=14,153 `_with_vader` subset) |
| Mean OP polarity | +0.0751 |
| Mean reply polarity | +0.0897 |
| Mean OP VADER | +0.5206 |
| Mean reply VADER | +0.2820 |

**Per-cohort table (all 8 cohorts; same-direction-mismatch confirmed at full scale):**

| Cohort | n_posts | TB Δ (OP−reply) | VADER Δ (OP−reply) |
|---|---|---|---|
| Reddit r/PSLF | 10,645 | −0.0121 | +0.2214 |
| Reddit r/StudentLoans | 6,965 | −0.0144 | +0.2499 |
| Reddit Finance | 1,968 | −0.0247 | +0.3021 |
| Reddit Medical | 668 | −0.0255 | +0.2061 |
| Other | 608 | −0.0148 | +0.2040 |
| Reddit PA | 268 | −0.0241 | +0.3170 |
| Reddit Teaching | 211 | −0.0067 | +0.2384 |
| Reddit Nursing | 120 | −0.0081 | +0.2581 |

**REPLICATES at full ~500K-comment scale**: all 8 cohorts show TextBlob Δ negative, VADER Δ positive (directionally opposite). The TB Δ magnitude is small in absolute terms (−0.007 to −0.026) but the directional disagreement with VADER is consistent across cohorts.

H2 depth-escalation: top-level vs deep replies, TB Δ=−0.0105 (t=−9.73, p=2.5×10⁻²²). Top-level replies slightly more negative than deeper replies.

### TB × VADER triangulation at comments scale (LOCKED 2026-05-10)

n = 519,342 comments with both TextBlob polarity and VADER compound scored.

| Metric | Posts (n=6,975) | **Comments (n=519,342)** | Status |
|---|---|---|---|
| TB × VADER Krippendorff α (ordinal) | +0.34 | **+0.2892** [bootstrap CI +0.2869, +0.2917] | **REPLICATES** (within 0.10 of post-level) |
| Pearson r | +0.30 | +0.3640 | Replicates |
| Spearman ρ | (TBD) | +0.3732 | (new) |

**Verdict**: The TB × VADER instrument-disagreement pattern is NOT specific to top-level posts. The construct boundary holds across the larger and stylistically-different comment corpus. This is the strengthener for Paper 1 §5 — the asymmetric construct boundary survives a 75× sample-size scaling.

---

## Paper 2 (Substantive) — locked numbers

### Sample

- Cohort heterogeneity sample (post-level): **n=9,242** (TB + VADER + Claude)
- Cohort heterogeneity sample (comments-scale): ⏳ TBD when collector finishes (~600K total comments; ~250K-350K with valid post_id linkage)
- Per-author longitudinal panel: 8 events evaluated; only 1 (Trump EO, n=13 returning) formally meets n≥10 threshold
- Per-event topic restructuring: 8 events × 7 topics × 5 cohorts where adequate sample

### Cohort definitions

| Cohort | n_with_Claude_scoring |
|---|---|
| Reddit r/PSLF | 1,469 |
| Student Doctor Network Medical | 1,960 |
| Reddit Finance | 999 |
| Reddit r/StudentLoans | 969 |
| Reddit Medical | 566 |

**Note (Round 17 reconciliation)**: Some prior tables had Reddit r/PSLF as n=1,470 and Reddit Finance as n=998. The single-row differences in those tables were spurious (likely a one-row missing-data filter difference). Canonical values are r/PSLF=1,469 and Finance=999 across all Paper 2 sections.

### Sentiment-stance OR table (5 cohorts × 3 operationalizations)

From `decoupling_by_cohort.csv` and `l5_cohort_robustness_results.txt`:

| Cohort | Same-scorer (Claude×Claude) | TB-neg×Claude-pur | VADER-neg×Claude-pur | Cross-instrument concordant? |
|---|---|---|---|---|
| **SDN-Medical** | OR=0.272 [0.22, 0.34] | OR=0.147 [0.10, 0.22] | OR=0.334 [0.26, 0.43] | **YES (5/5 specs OR<1)** |
| Reddit r/PSLF | OR=7.329 [4.20, 12.78] | OR=1.655 [0.97, 2.83] | OR=2.526 [1.53, 4.18] | **NO (4/5 OR>1, 1 spec [pur-or-completed] flips to OR=0.194)** |
| Reddit Finance | OR=0.182 [0.11, 0.30] | OR=1.103 [0.33, 3.66] | OR=1.423 [0.72, 2.82] | **NO (cross-scorer CIs span 1.0; construct-misalignment exemplar)** |
| Reddit r/StudentLoans | OR=1.411 [0.85, 2.34] | OR=2.495 [0.99, 6.28] | OR=0.990 [0.56, 1.74] | NO (3 OR>1, 2 OR<1) |
| Reddit Medical | OR=0.726 [0.33, 1.61] | OR=1.191 [0.40, 3.54] | OR=0.841 [0.35, 2.03] | NO (2 OR>1, 3 OR<1; all CIs include 1) |

### Base-rate-adjusted decoupling lift (Strengthener-equivalent)

From `paper2_base_rate_adjusted_decoupling.csv`:

| Cohort | n | P(pursue) baseline | P(pursue|neg) | **Lift_pp** |
|---|---|---|---|---|
| Reddit r/PSLF | 1,469 | 87.1% | 97.1% | **+10.0 pp** (coupling) |
| SDN-Medical | 1,960 | 78.9% | 62.4% | **−16.5 pp** (decoupling) |
| Reddit Finance | 999 | 91.4% | 73.8% | **−17.6 pp** (decoupling, same-scorer only) |
| Reddit Medical | 565 | 91.2% | 89.7% | −1.4 pp (null) |
| Reddit Teaching | 270 | 86.7% | 89.5% | +2.8 pp (null) |
| Other | 1,681 | 90.9% | 89.0% | −1.9 pp (null) |

### Per-event topic restructuring (post-scale; chi-sq p<10⁻⁴ for ALL 8)

From `topic_per_cohort_per_event_results.txt`:

| Event | n_pre | n_post | Cramér's V | Top topic shifts |
|---|---|---|---|---|
| Limited PSLF Waiver | 422 | 314 | 0.31 | success_story −31.6 pp; financial_planning +13.2 pp |
| IDR Account Adjustment | 234 | 179 | 0.42 | financial_planning +49.2 pp; general_question −30.5 pp |
| Biden Mass Forgiveness | 198 | 305 | 0.28 | career_impact −35.8 pp; general_question +23.1 pp |
| Biden v. Nebraska SCOTUS | 466 | 417 | 0.24 | policy_uncertainty +23.0 pp; financial_planning −21.6 pp |
| Payments Restart | 376 | 391 | 0.22 | policy_uncertainty −24.3 pp; financial_planning +14.1 pp |
| SAVE Forbearance | 203 | 168 | 0.27 | financial_planning −29.1 pp; career_impact +26.7 pp |
| Trump PSLF EO | 661 | 524 | 0.21 | policy_uncertainty −21.7 pp; financial_planning +12.9 pp |
| Final Trump PSLF Rule | 152 | 218 | 0.18 | policy_uncertainty +16.5 pp; general_question −9.0 pp |

### Per-author longitudinal panel feasibility

From `per_author_with_comments_results.txt`:

| Event | Pre authors | Post authors | Returning | Trump EO Δ rejecting (within-person) |
|---|---|---|---|---|
| Limited PSLF Waiver | 384 | 287 | 8 | n/a |
| IDR Account Adjustment | 209 | 165 | 6 | n/a |
| Biden Mass Forgiveness | 183 | 282 | 5 | n/a |
| Biden v. Nebraska SCOTUS | 421 | 376 | 7 | n/a |
| Payments Restart | 339 | 354 | 8 | n/a |
| SAVE Forbearance | 184 | 152 | 4 | n/a |
| Trump PSLF EO | 579 | 478 | **13** | +16.67 pp [bootstrap CI −16.7, +50.0]; McNemar p=0.625 |
| Final Trump PSLF Rule | 137 | 196 | 3 | n/a |

**All 8 events: CIs ≥25 pp wide → infeasible by design for within-person inference.**

### Comments-scale (LOCKED 2026-05-10)

n_total_comments = 519,342 across 21,960 unique posts.

**Per-cohort sentiment intensity at comments scale (TextBlob polarity):**

| Cohort | n_comments | mean polarity | %neg | %pos |
|---|---|---|---|---|
| Reddit r/PSLF | 234,133 | +0.0785 | 16.6% | 43.5% |
| Reddit r/StudentLoans | 207,353 | +0.0779 | 16.4% | 47.2% |
| Reddit Finance | 44,096 | +0.1131 | 11.8% | 60.3% |
| Reddit Medical | 12,541 | +0.0898 | 15.5% | 50.8% |
| Reddit Teaching | 3,458 | +0.0917 | 16.7% | 49.1% |
| Reddit PA | 4,587 | +0.1226 | 12.2% | 57.9% |
| Reddit Nursing | 921 | +0.0734 | 18.5% | 48.4% |

**Per-event Hedges' g at comments scale (selected events; n_pre, n_post ≥ 30):**

| Event | Cohort | n_pre | n_post | g | p |
|---|---|---|---|---|---|
| Trump PSLF EO | Reddit r/PSLF | 15,015 | 10,579 | −0.054 | 2.4×10⁻⁵ |
| Trump PSLF EO | Reddit r/StudentLoans | 13,239 | 11,539 | −0.014 | 0.27 |
| Trump PSLF EO | Reddit Finance | 318 | 448 | **−0.287** | 0.0001 |
| Trump PSLF EO | Reddit Medical | 1,609 | 670 | −0.011 | 0.81 |
| Trump PSLF EO | Reddit PA | 216 | 193 | −0.158 | 0.11 |
| Trump PSLF EO | Reddit Nursing | 30 | 191 | **−0.653** | 0.014 |

**Important comments-scale finding (Round 16 caveat)**: For the Trump PSLF EO event (Paper 2's lead exemplar), at comments scale all cohorts trend negative (no sign disagreements observed). This is **MORE concordant than the post-level analysis suggested**. Post-level cohort heterogeneity may reflect the more curated poster pool; at comments scale, larger less-selected commenter pool converges. Paper 2 should explicitly flag this as a caveat (§5.3b in the outline already does).

### Per-author panel (LOCKED 2026-05-10, with comments-presence)

Adding comments to author-presence universe raises author-overlap by ~5pp across most events, but stance inference still requires Claude OP in both windows. **Result unchanged from post-only**: only 1 of 8 events meets n≥10 returning-with-stance threshold (Trump EO, n=13).

| Event | Author overlap (post-only %) | Author overlap (post+comment %) | n_returning_with_stance | Verdict |
|---|---|---|---|---|
| Limited PSLF Waiver | 4.1% | 9.1% | 3 | INFEASIBLE |
| IDR Account Adjustment | 8.6% | 13.7% | 4 | INFEASIBLE |
| Biden Mass Forgiveness | 10.4% | 14.0% | 3 | INFEASIBLE |
| Biden v. Nebraska SCOTUS | 5.4% | 10.7% | 4 | INFEASIBLE |
| Payments Restart | 7.2% | 12.4% | 8 | INFEASIBLE |
| SAVE Admin Forbearance | 6.4% | 13.0% | 4 | INFEASIBLE |
| **Trump PSLF EO** | **6.9%** | **14.0%** | **13** | **FEASIBLE (n≥10)** |
| Final Trump PSLF Rule | 4.6% | 9.5% | 4 | INFEASIBLE |

Trump EO within-person stance shift (n=13 returning):
- Pre-EO rejecting%: 7.7%
- Post-EO rejecting%: 23.1%
- Δ within-person: +15.4 pp (3 to_rej, 1 from_rej, 9 stable)
- McNemar p = 0.6250 (NS due to small n)

Adding comments-presence does NOT unlock additional events for within-person inference (stance still requires Claude OP in both windows). Per-author panel infeasibility for 7/8 events stands.

---

## Paper 3 (Policy) — locked numbers

### Sample

- **5-year pre-EO baseline (2021–2025)**: n=29,349 program-year observations (after Round 15 dedup + Round 17 CMS dedup + dropna). Unique institutions: 789. Specialties: 28. Hostile institutions: 23 (S1 status quo); 9 (S2/S3 sensitivity).
- **6-year extended sample (2021–2026)**: n=37,450 raw program-year observations; n=35,193 after OLS-regression dropna. Unique institutions: 872 (post Round 17 CMS-dedup of 8 case-collision city duplicates such as "Boston" vs "BOSTON"). Hostile institutions: 23 (S1).
- **NIH-integrated 5-year + state-NIH sample**: n=29,349 OLS regression sample (state-filtered NIH RePORTER FY2023; 92 of 721 institutions NIH-matched (12.8%); 629 institutions (87.2%) coded as $0 NIH funding via log(1+0)=0 — see paper3_model5_with_NIH_results.txt for the Round 17++ NIH mass-point disclosure; $8.81B total funding aggregated). The "30,763" figure that appeared in earlier Round 17 documents was a pre-OLS-NA-drop count.

### Model 5 with cluster-robust SE + wild-cluster bootstrap

**5-year pre-EO baseline (HEADLINE, from `paper3_model5_FINAL_results.txt` + `paper3_wild_cluster_bootstrap_results.txt`):**

| Specification | n_total | n_hostile_inst | n_hostile_rows | PSLF-hostile β | 95% CI (cluster) | Cluster-robust p | **Wild-cluster bootstrap p** |
|---|---|---|---|---|---|---|---|
| **S1: Status quo (all 23 hostile)** | 29,349 | 23 | 763 | **−18.07 pp** | [−24.80, −11.35] | 1.4×10⁻⁷ | **<0.0005** |
| **S2: HCA-academic reclassified as ambiguous** | 29,349 | 9 | 358 | **−16.25 pp** | [−21.66, −10.83] | 4.0×10⁻⁹ | **0.017** |
| **S3: Drop HCA-academic partnerships** | 28,957 | 9 | 358 | **−17.14 pp** | [−22.48, −11.80] | 3.1×10⁻¹⁰ | **0.006** |

**6-year extended sample (DESCRIPTIVE TRAJECTORY, from `paper3_model5_2021_2026_cross_sectional_results.txt`):**

| Specification | n_total | n_hostile_rows | PSLF-hostile β (6-year pooled) | 95% CI |
|---|---|---|---|---|
| S1 (all 23 hostile) | 35,193 | 645 | −16.31 pp | [−22.49, −10.14] |
| S2 (HCA-academic reclassified) | 35,193 | 165 | −13.68 pp | [−18.36, −9.01] |
| S3 (HCA-academic dropped) | 34,713 | 165 | −14.50 pp | [−19.15, −9.84] |

The 6-year pooled β is smaller in absolute value than the 5-year because the 2026 narrowing pulls the average toward zero. We report 5-year as the headline cross-sectional estimate and 6-year for trajectory.

**NIH-integrated headline (from `paper3_model5_with_NIH_results.txt`, state-filtered NIH):**

| Specification | n_total | PSLF-hostile β | 95% CI | p | Notes |
|---|---|---|---|---|---|
| Model 5 + NIH (S1) | 29,349 | **−18.07 pp** | [−21.28, −14.87] | 2.1×10⁻²⁸ | log_nih_funding β=+0.02 NS (mass-point at 0 for 87% of institutions — see paper3_model5_with_NIH_results.txt); PSLF coefficient unchanged from non-NIH M5 |

### Other Model 5 coefficients (S1 status quo)

| Coefficient | β | Cluster-robust p |
|---|---|---|
| PSLF-eligible (vs ambiguous) | −0.45 pp | NS (p≈0.10) |
| CMS Star Rating | +1.05 pp/star | <10⁻⁹ |
| University affiliation flag | −0.65 pp | borderline (p≈0.05) |
| Academic medical center flag | +0.73 pp | borderline (p≈0.05) |
| n_specialties | +0.14 pp/specialty | <10⁻³ |
| log(annual residents) | NS | — |
| log(NIH FY2023 funding) | NS | — |

### Negative control: orthopedic surgery

From `paper3_negative_control_2021_2026_results.txt` (Round 17 dedup-corrected):

| Sample | n_total | n_hostile_rows | n_hostile_inst | PSLF-hostile β | 95% CI | p | Power floor |
|---|---|---|---|---|---|---|---|
| **2021–2025** (replication baseline) | 1,007 | 11 | 3 | **+0.67 pp** | [−0.66, +2.00] | 0.33 (NS) | ~1.33 pp |
| **2021–2026** (Round 17 update) | 1,204 | 16 | 4 | **+0.54 pp** | [−0.53, +1.60] | 0.32 (NS) | **~1.06 pp** |
| 2026 ortho descriptive | 223 | 5 | — | n/a | n/a | n/a | n/a |

**Verdict**: Negative-control test consistent across 5-year and 6-year samples; both null. Power floor improved from 1.33 pp → 1.06 pp with 2026 data. Note: previously-locked number (β=+0.76, n=1,079) reflected a slightly different inclusion filter; the Round 17 re-run uses the canonical Model 5 covariate set and yields β=+0.67 NS for the 5-year sample.

### Dermatology (R17++ Agent 2 M5 second negative control)

From `paper3_negative_control_dermatology_results.txt`:

| Sample | n_total | n_hostile_rows | n_hostile_inst | β | 95% CI | p | Power floor |
|---|---|---|---|---|---|---|---|
| 2021–2025 | 791 | 27 | 5 | **−7.20 pp** | [−16.92, +2.52] | 0.147 NS | ~9.7 pp |
| 2021–2026 | 953 | 33 | 6 | **−6.28 pp** | [−14.57, +2.01] | 0.138 NS | ~8.3 pp |

**Verdict (HONEST FRAMING)**: Dermatology is NOT a clean null like orthopedic surgery. Point estimates are notably negative (−6 to −7 pp), CIs straddle zero with much wider lower bound (−15 to −17 pp) than upper bound (only +2 pp). NS at α=0.05 but power-limited; admits both null AND substantial PSLF-hostile differential. Reported as SECONDARY negative control with this caveat. Orthopedic surgery remains the cleaner negative-control case.

### Trend-regression `is_post_eo` sensitivity (R17++ Agent 2 M4)

| Specification | β (year_centered) | β (EO-indicator) | EO-indicator p |
|---|---|---|---|
| Headline: `is_2026` | +1.595 pp/year (p=0.105) | +2.984 pp [−4.96, +10.92] | **p=0.46 NS** |
| Sensitivity: `is_post_eo` (year≥2025) | +1.827 pp/year (p=0.114) | +0.538 pp [−6.28, +7.36] | **p=0.877 NS** |

**Both specifications NS** — robustness check confirms no detectable EO-specific discontinuity beyond pre-existing trend, regardless of whether EO impact is modeled as 2026-only or 2025+.

### Year-by-year fill rates (UPDATED with 2026 data, March 2026 release)

| Year | n_friendly | n_hostile | Hostile fill | Friendly fill | Gap (pp) |
|---|---|---|---|---|---|
| 2016 | 2,190 | **6** | 0.7900 | 0.9408 | −5.92 (insufficient n) |
| 2017 | 2,437 | **8** | 0.9250 | 0.9377 | +1.27 (insufficient n) |
| 2020 | 2,269 | 54 | 0.7793 | 0.9355 | +15.63 |
| 2021 | 3,353 | 129 | 0.7994 | 0.9394 | **−14.00** |
| 2022 | 3,451 | 149 | 0.7767 | 0.9415 | **−16.48** (peak gap) |
| 2023 | 3,518 | 159 | 0.8028 | 0.9346 | −13.18 |
| 2024 | 3,597 | 159 | 0.8326 | 0.9397 | −10.71 |
| 2025 | 3,677 | 167 | 0.8356 | 0.9404 | −10.47 |
| **2026** | **3,887** | **171** | **0.8645** | **0.9348** | **−7.03** |

**TREND**: Gap has narrowed every year since 2022 peak. Linear time trend on PSLF-hostile programs alone (cluster-robust SE, state+specialty FE): +1.595 pp/year (SE=0.985, p=0.105). 2026 indicator beyond linear trend = +2.984 pp (SE=4.05, **p=0.46, NS**) — 2026 narrowing is statistically indistinguishable from continuation of pre-existing trend.

**RETRACTED claim** (per Round 16 audit, 2026-05-10): Earlier framing of "Trump PSLF EO eliminated the differential" was overstated. The 2026 narrowing continues a multi-year trend that began in 2022, well before the March 2025 EO. We cannot specifically attribute the 2026 narrowing to the EO with this design.

### Within-institution DiD (underpowered, do not interpret)

- Pre-Waiver (2016-20) vs Post-Waiver (2022-25)
- Friendly Δ: −0.93 pp (n=224 institutions)
- Ambiguous Δ: −0.56 pp (n=222)
- **Hostile Δ: −8.97 pp (n=7)**
- DiD: +8.04 pp; t=1.94; p=0.098 (NS) — **uninformative due to small n**

### HCA-academic partnerships (Round 15 critical context)

14 of 23 NRMP-hostile institutions are HCA-academic partnerships:
- USF Morsani × 10 (HCA Healthcare/USF Morsani GME-{Blake, Brandon, Citrus, Largo, Oak Hill, Sarasota, St Pete, Trinity, Bayonet Pt, Northside})
- U Miami × 2 (HCA Florida JFK Hosp-U Miami; HCA Healthcare/JFK Med Center-UMiami)
- U Houston × 1 (HCA Houston Healthcare/U Houston)
- VCOM × 1 (HCA Healthcare LGH-Montgomery/VCOM)

9 of 23 are unambiguous HCA/for-profit standalones:
- HCA Chippenham & Johnston-Willis Hosps
- HCA Corpus Christi Med Ctr
- HCA Healthcare Kansas City
- HCA Healthcare/TriStar Nashville
- HCA Healthcare/TriStar Southern Hills
- HCA Las Palmas del Sol Healthcare
- HCA Medical City Healthcare
- North Oaks Med Ctr LLC
- Steward Carney Hospital

---

## Cross-paper dependency map (when something changes, what updates?)

| Source data | Affects | If updated, refresh |
|---|---|---|
| Comments collector finish | Paper 1 §5.5 OP-vs-Reply, Paper 2 §5.1 cohort heterogeneity, Paper 2 §5.5 panel feasibility | Run `run_post_comments_chain.ps1`; substitute outputs into placeholders flagged ⏳ |
| New SDN scoring | Paper 1 §5 multi-LLM K-α | Re-run `compare_multi_llm_with_sdn.py` |
| New paraphrase variant | Paper 1 §5.4 | Re-run `compute_paraphrase_robustness.py` |
| New NRMP year | Paper 3 §3.3 + §3.6 | Re-run `run_model5_FINAL.py` + `wild_cluster_bootstrap_p3.py` |
| ProPublica re-classification | Paper 3 confounders + headline | Re-run `build_institutional_confounders.py` + `run_model5_FINAL.py` |

---

## Round-by-round summary (audit history)

| Round | Date | Key outcome |
|---|---|---|
| R1-R6 | 2026-04 | Initial audits, 46 fixes, sentiment triangulation |
| R7 | 2026-05-08 | Bootstrap rewrite, K-α CI, test-retest design |
| R8 | 2026-05-09 | Arctic Shift expansion (76K Reddit posts) |
| R9 | 2026-05-10 (early) | 4 new analyses, 8 critical statistical fixes |
| R10-R13 | 2026-05-09→10 | Llama 3.3 70B replication, L5 cross-instrument robustness |
| R14 | 2026-05-10 | 3 parallel adversarial agent audits |
| R15 | 2026-05-10 | Multi-agent audit caught 19 critical issues |
| R16 (initial) | 2026-05-10 | All 19 fixes applied |
| R16 (re-audit) | 2026-05-10 | Re-audit found internal consistency issues; full propagation done |
| **R16 (strengtheners)** | **2026-05-10** | **3 strengtheners run: SDN multi-LLM (P1 +10pp), paraphrase robustness (P1 +3pp), wild-cluster bootstrap (P3 +5pp)** |
| **R17 (audit + dedup fix)** | **2026-05-10** | **CMS-merge dedup bug found + fixed in 7 scripts; all Model 5 scripts re-run; state-filtered NIH integrated (final locked β=−18.07 pp); Trump-EO causal interpretation retracted (trend regression: is_2026 indicator p=0.46 NS); Paper 2 scoped to post-level (drop §5.3b comments-scale); Paper 1 reframings (paraphrase as "lexical-format", magnitude framing for OP-vs-Reply, Together AI infrastructure caveat, soften "no precedent" language); 5 stale P3 paragraphs corrected; 2 P3 supplementary files received retraction banners; transparency statement added to P3 abstract** |

---

*This document is the source of truth. Update once when comments-scale numbers land; all paper drafts pull from here.*
