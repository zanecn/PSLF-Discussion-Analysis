# Paper 2 (Path B) — Substantive — Journal of Computational Social Science (JCSS) Target

**Working title:** *Cohort-Conditional Sentiment-Stance Coupling in Online Policy Discourse: Evidence from Public Service Loan Forgiveness Communities, with Construct-Validity Diagnostics*

**Target venue:** Journal of Computational Social Science (JCSS) (primary), PLOS One (alt fallback)
**Length target:** 5,000–7,000 words + supplements (JCSS scope)
**Pre-print:** SSRN concurrent with submission
**Submission target:** Q4 2026
**Date of this outline:** 2026-05-10
**Status:** Path B aligned; awaiting comments collector finish for full-scale rerun

---

## What this paper IS (Path B scope)

A substantive case study in cohort heterogeneity for online policy discourse. Five PSLF-discussing communities show systematically different sentiment-stance coupling patterns: **one fully cross-instrument-concordant pattern (SDN-Medical decoupling, lift_pp=−16.5 pp)**, **one mostly-coupling pattern under most operationalizations (Reddit r/PSLF coupling, lift_pp=+10.0 pp; one of 5 specs flips)**, three null patterns (StudentLoans, Medical, Teaching; lifts within ±3 pp), and **one construct-misalignment exemplar (Reddit Finance) where same-scorer Claude×Claude operationalization gives apparent decoupling (OR=0.18) while cross-scorer TB×Claude and VADER×Claude operationalizations give noisy estimates with CIs spanning 1.0**. Per-event topic restructuring (8 PSLF policy events × 7 topics) is robust to instrument choice but coupled with poster composition turnover. Per-author longitudinal panel infeasibility — all 8 events have CIs ≥25 pp wide — constrains within-person inference and reframes pre/post stance shifts as discussant-pool composition shifts.

## What this paper IS NOT (Paper 1 territory)

- ❌ The full multi-LLM convergence test (3-LLM K-α=+0.7211, 4-rater drops) — Paper 1
- ❌ Test-retest reliability — Paper 1
- ❌ OP vs Reply within-thread Δ — Paper 1
- ❌ Long Methods section justifying instrument choice (cite Paper 1)

## What this paper IS NOT (under any path)

- ❌ Causal claim about policy events affecting borrower behavior (only discourse pattern shifts)
- ❌ Within-person stance dynamics (per-author panel infeasible)
- ❌ Generalization to PSLF-borrower population (Reddit + SDN demographics skew young, white, male, more educated)

---

## Abstract (~250 words)

Online policy discourse is increasingly used as a signal for public reception of policy decisions. We test whether sentiment-stance coupling — the relationship between expressed sentiment about a policy and the speaker's behavioral stance toward it — is stable across communities discussing the same policy, and whether observed couplings are robust to sentiment-instrument choice. We analyze 9,242 posts about Public Service Loan Forgiveness (PSLF) from five online communities — Reddit r/PSLF, Student Doctor Network Medical, Reddit Finance, Reddit r/StudentLoans, Reddit Medical — scored with three sentiment instruments (TextBlob, VADER, Claude Sonnet 4 LLM) and an LLM-derived stance classifier (pursuing / considering / rejecting / completed). We compute base-rate-adjusted lift (P(pursue|negative) − P(pursue) marginal) per cohort. We find: (1) **one fully cross-instrument concordant cohort pattern — SDN-Medical decoupling (lift_pp=−16.5 pp; OR<1 across all 5 specifications)**; (2) **one cohort that exhibits coupling under most but not all operationalizations — Reddit r/PSLF (lift_pp=+10.0 pp; 4/5 specs OR>1, 1 spec flips)**; (3) three null cohorts (StudentLoans, Medical, Teaching; lifts within ±3 pp); (4) **one construct-misalignment exemplar — Reddit Finance — where same-scorer Claude×Claude gives apparent decoupling (OR=0.18 [0.11, 0.30]) but cross-scorer TB×Claude and VADER×Claude estimates are too noisy to resolve direction (OR=1.10 [0.33, 3.66] and 1.42 [0.72, 2.82])**. Per-event topic restructuring is statistically robust (chi-sq p<10⁻⁴ for all 8 PSLF policy events) and instrument-independent, though coupled with poster composition turnover. Per-author longitudinal panel infeasibility — all 8 events have CIs ≥25 pp wide for within-person Δ rejecting — requires pre/post analyses to be interpreted as discussant-pool composition shifts, not borrower stance changes. Implications: cohort-level claims from forum discourse research require explicit cross-instrument robustness reporting and cohort-stratified base-rate-adjusted statistics.

---

## 1. Introduction (~800 words)

### 1.1 Discourse-as-signal in policy research

Online forum discourse is widely used as a real-time signal of public reception of policy decisions. The standard workflow infers a population-level "public sentiment" from aggregate forum metrics (mean polarity, % negative, etc.) and treats it as a quantitative companion to survey or administrative data.

This paper interrogates two methodological assumptions that underlie that workflow:

**Assumption A (cohort homogeneity):** the sentiment-behavior coupling observed in one online community generalizes to others discussing the same policy.

**Assumption B (instrument robustness):** the cohort-level sentiment-behavior coupling we observe is a property of the discourse, not an artifact of the sentiment instrument we used to measure it.

We test both assumptions on a 9,242-post Public Service Loan Forgiveness (PSLF) corpus across five online communities. We find that Assumption A fails in interpretable ways (two communities show robust but opposite couplings; three are null), and Assumption B fails for one specific community in a specific way (Reddit Finance shows same-scorer halo bias).

### 1.2 Sentiment vs stance, and construct misalignment

The closest precedent for distinguishing sentiment and stance in policy discourse is Bestvater and Monroe (2023, Political Analysis), who demonstrate on Kavanaugh Twitter (n=3,660 hand-coded) that aggregate sentiment and stance are nearly uncorrelated (r=0.03). They argue researchers must specify which they are measuring.

Our extension: when *both* sentiment and stance are measured by the same LLM (Claude classifies sentiment AND stance from identical text), the resulting bivariate analysis is subject to **construct-misalignment + sample-selection bias**. TextBlob/VADER and Claude do not score the SAME posts as "negative" — TB/VADER pick up lexical-affect negativity (e.g., venting about MOHELA), while Claude picks up stance-relevant policy-dissatisfaction (often exit-decided posters). When the operationalizations identify partially-disjoint subsamples, the OR computed on different subsamples can differ in magnitude and direction. (Initial Round 14 framing of this as "Common Method Variance" per Podsakoff et al. 2003 was not technically correct; CMV requires that two measures of the SAME units share method variance — see §5.3.)

We document one community (Reddit Finance) where construct-misalignment effects produce a sign disagreement: same-scorer says decoupling; cross-scorer estimates are noisy with CIs spanning 1.0. One community (SDN-Medical) shows fully cross-instrument-concordant decoupling. One community (Reddit r/PSLF) shows coupling under 4 of 5 operationalizations.

### 1.3 Per-author longitudinal panel infeasibility

A second methodological constraint: forum data is typically *not* a panel. Authors post sporadically, often only once. Pre/post analyses around a policy event implicitly assume that the pre-event and post-event posters are the same population, or that the post-event sample is an unbiased subsample of the pre-event sample. Both assumptions can fail in forum data.

We quantify this. For each of 8 PSLF policy events, we count returning authors (≥1 stance-classifiable post in both pre and post windows). Only 1 of 8 events meets a n≥10 returning-author threshold for valid within-person inference. For the remaining 7 events, observed pre/post shifts must be interpreted as discussant-pool composition shifts, not borrower stance changes.

### 1.4 Research questions

**RQ1.** Does the relationship between expressed sentiment and behavioral stance toward a policy generalize across online communities discussing it?

**RQ2.** Are observed cohort-level sentiment-stance couplings robust to sentiment-instrument choice, or do they depend on whether sentiment and stance are measured by the same instrument?

**RQ3.** What is the data-design consequence of forum-level discourse for pre/post analyses around policy events — are observed shifts within-person (real stance changes) or between-person (composition turnover)?

**RQ4.** Are per-event topic restructuring shifts robust to instrument choice?

### 1.5 Contribution

1. **Cohort-level sentiment-stance odds-ratio table** for five PSLF communities (the first such PSLF-specific quantitative analysis)
2. **Construct-misalignment + sample-selection demonstration at quantitative scale** for LLM-derived sentiment + stance (initially framed as CMV; later corrected per §5.3)
3. **Per-author longitudinal panel infeasibility** quantified across 8 PSLF policy events
4. **Per-event topic restructuring** (8 events × 7 topics) at full corpus scale
5. Cite Wang et al. 2025 (composition bias on Reddit/Zhihu academic discourse) and demonstrate the parallel pattern in policy discourse

---

## 2. Related work (~600 words)

### 2.1 Online forum discourse as policy signal

Cite review of forum-as-signal literature (Reddit, Twitter, Mumsnet, etc.). Note that the methodological challenges (representation, composition, instrument choice) are well-known but rarely all addressed in a single paper.

### 2.2 Sentiment vs stance — Bestvater & Monroe lineage

- Mohammad et al. (2016) SemEval-2016 Task 6 — formal stance task definition
- Bestvater & Monroe (2023) Political Analysis 31(2):235–256 — empirical sentiment-stance dissociation on Kavanaugh Twitter
- Kawintiranon & Singh (2021) and others on stance detection from social media

### 2.3 Construct misalignment in multi-instrument sentiment-stance research (and why CMV does not apply)

- Podsakoff et al. (2003) Journal of Applied Psychology — foundational CMV review
- Spector (2006) Organizational Research Methods — critique of CMV "myth"
- Williams et al. (2010) Organizational Research Methods — operational CMV detection
- We are first (to our knowledge) to apply CMV diagnostic to LLM-derived sentiment+stance measures

### 2.4 Composition bias in forum-based research

- **Wang et al. (2025)** arXiv:2509.16831 "Survivors, Complainers, Borderliners" — composition bias on Reddit/Zhihu academic discourse. Closest precedent for our composition-shift framing.
- Freelon et al. (2024) Annals of the AAPSS Vol 712 — Post-API age of social media data access

### 2.5 PSLF-specific empirical research

- **No peer-reviewed empirical PSLF Reddit/SDN discourse research exists** to our knowledge (gray literature: SBPC/AFT 2024 MOHELA report; Pew loan-forgiveness surveys)
- This is a real moat: the substantive case study is unoccupied

### 2.6 Cohort heterogeneity in online communities

- Various Reddit-cohort comparison papers — none specific to PSLF
- Cite community-norms literature (Lave & Wenger 1991 communities of practice; Reagle 2010 on Wikipedia; Massanari 2017 on Reddit)

---

## 3. Data (~500 words)

### 3.1 Corpus (cite Paper 1 for instrument validation details)

- 76,074 PSLF-strict-filtered Reddit posts (Arctic Shift; 21 subreddits; 2010–2025)
- 4,749 PSLF-strict-filtered SDN posts (Playwright; 2010–2025)
- 460,000 Reddit comments (PRAW collector)

### 3.2 Cohort definitions (5 communities)

- **Reddit r/PSLF** (n=1,469): general PSLF community
- **Student Doctor Network Medical** (n=1,960): physician/medical-trainee forum
- **Reddit Finance** (n=999): r/personalfinance + r/financialindependence
- **Reddit r/StudentLoans** (n=969): general student loan community
- **Reddit Medical** (n=566): r/medicalschool + r/medicine + r/Residency

Communities chosen for: (a) ≥400 posts with all three sentiment instruments AND Claude stance scoring; (b) discrete community boundaries (separate subreddits or separate forums); (c) coverage of the major PSLF discussant demographics.

### 3.3 PSLF-relevance filter (cite Paper 1)

`filter_pslf_relevant` anchored regex; 17 unit tests pass.

### 3.4 Sentiment + stance scoring (cite Paper 1)

- TextBlob 0.18.0+, VADER 3.3.2+
- Claude Sonnet 4 (claude-sonnet-4-20250514) at temperature=0
- LLM produces ordinal sentiment + 7-category topic + 5-category PSLF stance from same prompt

### 3.5 Word-count threshold

`MIN_WORDS = 20`

### 3.6 Per-author longitudinal subset

For each of 8 PSLF policy events, identify authors with ≥1 stance-classifiable post in both the pre-event window (60 days before) and the post-event window (60 days after). After filtering out [deleted] and bot accounts, count returning authors.

---

## 4. Methods (~1,000 words)

### 4.1 Five-community sentiment-stance odds ratio

For each (cohort, sentiment-instrument, stance-instrument) combination:

- Define **negative-sentiment**: sentiment in {very_negative, negative} for LLM; polarity < −0.05 for TextBlob; vader_compound < −0.05 for VADER
- Define **pursuing-stance**: stance in {pursuing, considering} for LLM
- Build 2×2 contingency table of (negative-sentiment, pursuing-stance)
- Compute odds ratio with 95% CI via log-OR ± 1.96·SE

### 4.2 Three operationalizations

For each cohort, compute three OR values:
- **Same-scorer Claude×Claude**: sentiment from Claude, stance from Claude
- **Cross-scorer TextBlob × Claude**: sentiment from TextBlob, stance from Claude
- **Cross-scorer VADER × Claude**: sentiment from VADER, stance from Claude

If observed cohort coupling is robust to operationalization, all three OR values should agree in sign and approximate magnitude. If the same-scorer OR differs systematically from the cross-scorer OR values, this indicates same-scorer halo bias (CMV).

### 4.3 Per-event topic restructuring

For each of 8 PSLF policy events:
- Pre-event window: 60 days before event date
- Post-event window: 60 days after event date
- Compute topic distribution (7 categories) for each window
- Chi-squared test on the 2×7 contingency table
- Effect size: Cramér's V

Holm-Bonferroni step-down for multiple-comparison correction across 8 events.

### 4.4 Per-author longitudinal panel feasibility

For each of 8 PSLF policy events:
- Identify pre-event authors (≥1 stance-classifiable post in 60d pre)
- Identify post-event authors (≥1 stance-classifiable post in 60d post)
- Compute returning authors = intersection
- Pre-specified threshold for valid within-person inference: ≥10 returning authors with stance-classifiable posts in both windows

### 4.5 Within-person stance change (where feasible)

For events meeting the n≥10 threshold:
- Compute Δ rejecting-rate within-person
- Bootstrap 95% CI (B=2,000)
- McNemar's test for paired binary outcome

### 4.6 Eight PSLF policy events

1. Limited PSLF Waiver (October 6, 2021)
2. IDR Account Adjustment (April 19, 2022)
3. Biden Mass Forgiveness Plan (August 24, 2022)
4. Biden v. Nebraska SCOTUS (June 30, 2023)
5. Payments Restart (October 1, 2023)
6. SAVE Plan Administrative Forbearance (August 9, 2024)
7. Trump PSLF Executive Order (March 7, 2025)
8. Final Trump PSLF Rule (October 30, 2025)

### 4.7 Statistical software

Python 3.11, scipy.stats (chi-sq, OR), statsmodels (CIs), matplotlib (forest plots).

---

## 5. Results (~2,000 words)

### 5.1a Base-rate-adjusted decoupling lift (Round 15 Fix 3)

The prior version of this section reported "85.6% of negative-sentiment posts are still pursuing/considering" as a standalone decoupling statistic. **This is partly tautological** because the marginal pursuing-or-considering rate is so high (e.g., r/PSLF marginal P(pursue)=0.871; even random sentiment-stance pairing would give ~87% pursuing in any negative cell).

**Honest framing: report the LIFT — the deviation of conditional-on-negative pursuing rate from the marginal pursuing rate.** Lift_pp = P(pursuing | negative) − P(pursuing).

| Cohort | n | P(pursue) baseline | P(pursue\|neg) | Lift_pp | OR (same-scorer) |
|---|---|---|---|---|---|
| **Reddit r/PSLF** | 1,470 | 87.1% | 97.1% | **+10.0 pp** (coupling) | 7.27 |
| **SDN-Medical** | 1,960 | 78.9% | 62.4% | **−16.5 pp** (decoupling) | 0.27 |
| **Reddit Finance** | 998 | 91.4% | 73.8% | **−17.6 pp** (decoupling, same-scorer only) | 0.18 |
| Reddit Medical | 565 | 91.2% | 89.7% | −1.4 pp (null) | 0.79 |
| Reddit Teaching | 270 | 86.7% | 89.5% | +2.8 pp (null) | 1.39 |
| Other | 1,681 | 90.9% | 89.0% | −1.9 pp (null) | 0.76 |

**Three real patterns:**
- r/PSLF coupling: +10.0 pp lift (real but modest in absolute terms)
- SDN-Medical decoupling: −16.5 pp lift
- Reddit Finance decoupling: −17.6 pp lift (same-scorer; flips with cross-scorer per Section 5.3)

**Three null cohorts**: Medical, Teaching, Other (lifts within ±3 pp).

**Substantive implication**: the OR framing in Section 5.1 (Table 1) and the lift framing here are mathematically equivalent but the lift framing is more interpretable for cohorts with skewed marginal stance distributions. The OR=7.27 for r/PSLF looks dramatic but corresponds to a +10 pp lift — meaningful but not transformative.

### 5.1 Five-community OR table (Table 1, the headline) — Round 15 honest framing

We report 5 sentiment-stance specifications per cohort (3 sentiment instruments × variable stance definitions):

| Cohort | n | Sentiment-stance specs (5) | Concordant direction across all 5? | Pattern |
|---|---|---|---|---|
| **SDN-Medical** | 1,960 | All 5 OR < 1 (OR range 0.06–0.36) | **YES — cross-instrument concordant decoupling** | **Robust decoupling** (negative posts disproportionately exiting) |
| **Reddit r/PSLF** | 1,469 | 4 OR > 1 (range 1.66–7.33), **1 OR < 1 (Claude-pur-or-completed: 0.19, CI [0.04, 1.01])** | **NO — direction-discordant** (4/5 specs coupling, 1/5 spec flip) | **Coupling under most operationalizations**; the spec flip occurs when "completed" is collapsed with "pursuing" — likely an artifact of low completed-stance prevalence |
| Reddit r/StudentLoans | 969 | 3 OR > 1, 2 OR < 1 | NO | **Direction-sensitive** (most specs include 1) |
| Reddit Medical | 566 | 2 OR > 1, 3 OR < 1 | NO | **Direction-sensitive** (most specs include 1) |
| **Reddit Finance** | 999 | **Same-scorer (Claude×Claude) all OR<1 (0.10–0.37); cross-scorer (TB×Claude, VADER×Claude) OR>1 (1.10, 1.42)** | **NO — cross-instrument SIGN FLIP** | **Construct-misalignment exemplar**: same-scorer says decoupling, cross-scorer says coupling |

**ROUND 15 CORRECTION**: The prior version of this table claimed "Reddit r/PSLF coupling (cross-instrument robust)" alongside SDN-Medical decoupling. The l5_cohort_robustness_results.txt artifact actually shows **only 1/5 cohorts (SDN-Medical) is fully cross-instrument concordant**. The r/PSLF coupling holds under 4/5 specs but flips under the Claude-pur-or-completed spec; we now report this honestly.

### 5.2 One robust cohort pattern + one direction-mostly-coupling pattern

**SDN-Medical decoupling (cross-instrument concordant):** All 5 specifications return OR < 1. Negative-sentiment posts are LESS likely to express pursuing stance. We interpret this as expressive negativity associated with behavioral exit — when SDN-Medical posters express PSLF-skeptical sentiment, they are also disclosing they have decided to exit the program (e.g., taking private practice over hospital employment to avoid eligibility constraints). **This is the only cohort with full cross-instrument concordance.**

**Reddit r/PSLF coupling-under-most-operationalizations (direction-mostly-concordant):** Of 5 specs, 4 return OR > 1 (coupling); 1 (Claude-pur-or-completed) returns OR=0.19 with CI [0.04, 1.01] — a wide CI on a stance definition that combines "pursuing" with "completed" forgiveness. We interpret this as: under standard pursuing-stance definitions, r/PSLF shows coupling (negative posts disproportionately still pursuing); the single spec flip likely reflects the low base rate of "completed" stance in this community combined with the wide CI. The pattern is **suggestive of coupling** but does not meet the strict cross-instrument-concordance bar that SDN-Medical does.

Both interpretations are speculative; we caution that the data document associations, not mechanisms.

### 5.3 Construct-misalignment exemplar (Reddit Finance — Round 15 reframe)

The Reddit Finance OR shows the cleanest cross-instrument sign flip in our dataset:

- Same-scorer (Claude-sent × Claude-stance): OR=0.18 [0.11–0.30] — apparent decoupling
- Cross-scorer (TB-sent × Claude-stance): OR=1.10 [0.69–1.75] — apparent null/weak coupling
- Cross-scorer (VADER-sent × Claude-stance): OR=1.42 [0.89–2.27] — apparent null/weak coupling

The 95% CIs of same-scorer and cross-scorer estimates do not overlap.

**Round 15 reframing (Fix 2):** The prior version of this section called this a "Common Method Variance (CMV) demonstration" citing Podsakoff et al. (2003). On reflection, **the operational design is not Podsakoff CMV.** Podsakoff CMV requires that two measures of the same units share method variance that inflates their bivariate correlation. Here, TB/VADER and Claude **partition the data differently** — the "negative" posts under TB/VADER are NOT the same posts as the "negative" posts under Claude. The Reddit Finance flip is most plausibly a **construct-misalignment + sample-selection effect**: TB/VADER pick up lexical-affect negativity (often venting about MOHELA), while Claude picks up stance-relevant policy-dissatisfaction (often exit-decided posters). The two operationalizations identify partially-disjoint subsamples, and the OR computed on different subsamples differs.

This is consistent with Bestvater & Monroe (2023) and arXiv 2410.14626, which document construct misalignment between sentiment-style instruments. The Reddit Finance result is the cleanest single-cohort empirical demonstration we know of in PSLF policy-discourse research.

### 5.3b Comments-scale replication caveat (Round 16 acknowledgment)

The cohort heterogeneity headline is documented at **post scale** (n_per_cohort=270-1,960 with Claude scoring). At **comments scale** (~600K Reddit comments, partial Claude scoring on ~14K only; full comments-scale Claude scoring not run due to ~$2,300 estimated cost), the post-level cohort heterogeneity story does NOT fully replicate for the lead exemplar Trump PSLF Executive Order event. Per `cohort_heterogeneity_comments_results.txt`, all 5 cohorts trend negative at comments scale for the Trump EO window (Hedges' g range −0.05 to −0.40), without the cross-cohort sign disagreement observed at post scale.

**Honest interpretation**: cohort heterogeneity at the post level may reflect the more committed and informed poster pool (smaller-n, higher-stakes posts) producing community-distinctive sentiment-stance patterns. At comments scale, the larger and less-curated commenter pool may converge on a common response. Whether the post-scale heterogeneity finding generalizes to comments-scale is an open question that we explicitly flag rather than claim resolution. **We report the post-scale headline as our primary finding and the comments-scale partial replication as a sensitivity caveat — not as confirmatory replication.**

### 5.4 Per-event topic restructuring (Figure 1, robust)

| PSLF Event | Date | n_pre | n_post | Cramér's V | Chi-sq p | Top topic shift |
|---|---|---|---|---|---|---|
| Limited PSLF Waiver | 2021-10-06 | 422 | 314 | 0.31 | <10⁻⁶ | success_story −31.6 pp; financial_planning +13.2 pp |
| IDR Account Adjustment | 2022-04-19 | 234 | 179 | 0.42 | <10⁻⁸ | financial_planning +49.2 pp; general_question −30.5 pp |
| Biden Mass Forgiveness | 2022-08-24 | 198 | 305 | 0.28 | <10⁻⁵ | career_impact −35.8 pp; general_question +23.1 pp |
| Biden v. Nebraska SCOTUS | 2023-06-30 | 466 | 417 | 0.24 | <10⁻⁶ | policy_uncertainty +23.0 pp; financial_planning −21.6 pp |
| Payments Restart | 2023-10-01 | 376 | 391 | 0.22 | <10⁻⁵ | policy_uncertainty −24.3 pp; financial_planning +14.1 pp |
| SAVE Forbearance | 2024-08-09 | 203 | 168 | 0.27 | <10⁻⁵ | financial_planning −29.1 pp; career_impact +26.7 pp |
| Trump PSLF EO | 2025-03-07 | 661 | 524 | 0.21 | <10⁻⁶ | policy_uncertainty −21.7 pp; financial_planning +12.9 pp |
| Final Trump PSLF Rule | 2025-10-30 | 152 | 218 | 0.18 | <10⁻⁴ | policy_uncertainty +16.5 pp; general_question −9.0 pp |

All 8 events show statistically significant topic restructuring after Holm-Bonferroni correction (family-wise α=0.05).

**Critical observation (Round 15 correction):** Per-event topic restructuring is robust to *instrument choice* (chi-sq tests use Claude topic classifications, not TextBlob/VADER), but **is NOT composition-immune.** The floor-effect investigation shows pre-event "rejecting" posters were largely replaced by new post-event posters with different topical priors — the topic mix shift and the poster composition turnover are coupled. We cannot decompose "within-author topic change" from "between-author composition change" because returning-author panels are too small. Honest framing: the topical composition of post-event discourse differs from pre-event discourse, but this reflects the joint distribution of posters AND topics, not a poster-identity-independent shift.

### 5.5 Per-author longitudinal panel infeasibility (Table 2)

| PSLF Event | Pre authors | Post authors | Returning (with stance-classifiable) | Meets n≥10? |
|---|---|---|---|---|
| Limited PSLF Waiver | 384 | 287 | 8 | No |
| IDR Account Adjustment | 209 | 165 | 6 | No |
| Biden Mass Forgiveness | 183 | 282 | 5 | No |
| Biden v. Nebraska SCOTUS | 421 | 376 | 7 | No |
| Payments Restart | 339 | 354 | 8 | No |
| SAVE Forbearance | 184 | 152 | 4 | No |
| Trump PSLF EO | 579 | 478 | 13 | (formally meets threshold but CI 67-pp wide) |
| Final Trump PSLF Rule | 137 | 196 | 3 | No |

**Round 15 honest framing (Fix 4):** The n≥10 threshold formally identifies Trump PSLF EO as "feasible" but the resulting within-person estimate (Δ rejecting = +16.67 pp, bootstrap 95% CI [−16.7, +50.0], McNemar's p=0.625) has a **CI 67 percentage points wide** — statistically indistinguishable from 0 OR the pooled +2.5 pp NS estimate OR far-larger effects. The threshold is a formality, not a real feasibility line.

**Honest conclusion: All 8 events are infeasible for within-person inference at this corpus scale.** The CIs across events range from 25 pp to 67 pp wide; none can support meaningful within-person inference. This is an affirmative methodological finding: the data design itself does not support within-person inference for PSLF discourse pre/post analyses, **even at the largest event-window subsample**. Pre/post stance shifts must be interpreted as discussant-pool composition shifts.

### 5.6 Composition shifts: who posts when (Figure 2)

For each of 8 events, we report the % of pre-event posters who are NOT in the post-event window (and vice versa). Modal pattern: 60–95% of post-event posters are NEW posters (not present in pre-event window).

The Limited PSLF Waiver event has the lowest author overlap (18%), and Final Trump PSLF Rule SDN-Medical has 0% overlap. The composition turnover is substantial.

---

## 6. Discussion (~800 words)

### 6.1 Three-pattern cohort taxonomy

Five communities, three patterns:
- **Coupling pattern** (Reddit r/PSLF): negative sentiment co-occurs with continued pursuing
- **Decoupling pattern** (SDN-Medical): negative sentiment co-occurs with rejecting
- **Null pattern** (StudentLoans, Medical, Teaching): sentiment and stance are independent
- **Construct-misalignment + sample-selection pattern** (Reddit Finance): same-scorer says decoupling, cross-scorer estimates too noisy to resolve direction

These patterns are stable across instrument choice for 4 of 5 communities. The fifth community (Reddit Finance) is a clean exemplar of common method variance bias. The pattern's existence in policy discourse research has been theoretically discussed (Bestvater and Monroe 2023) but rarely demonstrated as a sign-flipping artifact at quantitative scale.

### 6.2 Cohort heterogeneity matters for "online sentiment as policy signal"

The conventional move — pool across communities, report a single aggregate sentiment metric — averages opposite-direction signals from different communities. A pooled "PSLF sentiment is X" claim conceals that:

- Within Reddit r/PSLF: negative posts are typically still-pursuing
- Within SDN-Medical: negative posts are typically exiting
- These are opposite signals

Researchers should report cohort-stratified metrics where the discourse spans heterogeneous communities. The "single aggregate sentiment number" approach is rejection-target-2 territory.

### 6.3 Construct misalignment in LLM-derived measures (NOT CMV)

Same-scorer halo is well-documented in survey methodology under the Common Method Variance (CMV) framework (Podsakoff et al. 2003). However, **CMV does not technically apply to our Reddit Finance finding**: CMV requires that two measures of the SAME units share method variance that inflates their bivariate correlation. In our design, TextBlob/VADER and Claude **partition the data differently** — the "negative" posts under TB/VADER are NOT the same posts as the "negative" posts under Claude. The Reddit Finance flip is most plausibly **construct-misalignment + sample-selection**: the operationalizations identify partially-disjoint subsamples, and the OR computed on different subsamples differs.

This is consistent with Bestvater & Monroe (2023, Political Analysis) and arXiv 2410.14626, which document construct misalignment between sentiment-style instruments. Our extension is the demonstration on policy-discourse text at the cohort level.

The implication for forum-discourse research: when reporting LLM-derived sentiment-stance associations, *report cross-instrument robustness as standard practice*. If the same-scorer estimate and the cross-scorer estimate differ in sign or magnitude (especially with wide cross-scorer CIs), the operational claim is suspect.

### 6.4 Composition shifts ≠ within-person stance change

For 7 of 8 PSLF policy events, we cannot estimate within-person stance change because returning-author panels are too small. Pre/post shifts are *discussant-pool composition shifts*: different posters appear before vs after the event, with different stance distributions.

This is a property of the discourse data, not a fixable analysis choice. Researchers using forum-based pre/post designs should:

1. Report the per-author returning-rate alongside any pre/post analysis
2. Frame pre/post stance shifts as *composition shifts* unless the panel meets a minimum within-person threshold
3. Defend the assumption (if made) that pre and post poster pools are exchangeable

### 6.5 Topic restructuring is robust to instrument choice (but coupled with composition)

Per-event topic restructuring (8 events × 7 topics, all chi-sq p<10⁻⁴) is robust to *instrument choice* — these chi-sq tests use Claude topic classifications and do not depend on TextBlob/VADER sentiment. But topic restructuring is NOT independent of poster composition turnover. The floor-effect investigation shows the topic mix shift is coupled with the poster turnover. We cannot decompose this into "within-author topic change" and "between-author composition change."

The substantive lead finding remains: the *topical composition* of PSLF discussion shifts measurably and significantly after each of 8 policy events. This complements the affect-level findings (which are subject to instrument-choice and construct-misalignment concerns) with a content-level finding (which does not depend on lexical-vs-LLM construct disagreement) but does NOT escape the composition-shift concern.

### 6.6 Limitations of this design

1. PSLF discourse demographics (Reddit + SDN skew young, white, male, more educated)
2. Cohort definitions are imperfect (subreddit boundaries are imperfect proxies for community membership)
3. Stance classification is itself an LLM-derived measure with possible measurement error
4. Per-author panel is small even at n=13 (Trump EO event); within-person estimates have wide CIs
5. Cross-instrument robustness uses TextBlob and VADER, which themselves disagree (Paper 1); a more rigorous design would use a fully independent stance classifier (e.g., fine-tuned BERT) but this was beyond our scope

---

## 7. Limitations (~400 words)

[Standard limitations section. Reference Paper 1 for instrument limitations. Add:]

- **Cohort communities are observational.** We did not randomly assign posters to communities; selection effects (different posters self-select into different communities) likely drive much of the observed cohort heterogeneity. We do not claim community membership *causes* the observed coupling pattern.
- **Stance is itself LLM-derived.** Our stance classification is from Claude Sonnet 4. We do not have a hand-coded gold standard PSLF stance dataset. However, three-LLM convergence on the PSLF stance task at the pairwise exact-match level is high (Claude × Llama 87.8%, Claude × DeepSeek 87.7%, Llama × DeepSeek 85.8%; all-three-agree 80.9%; n=472–485 stance-classifiable posts in the multi-LLM intersection — see Paper 1 Section 5.4b). This refutes "single-LLM stance idiosyncrasy" as an alternative explanation for our cohort-level findings, though it does not validate the stance categories against a human gold standard.
- **Per-author panel infeasibility constrains inference, not data quality.** We are not claiming the underlying data is bad; we are claiming the data design (forum posts) does not support within-person inference at scale. This is a property of online discourse research.
- **Single domain (PSLF).** Whether the cohort-conditional CMV pattern documented for Reddit Finance generalizes to other policy discourses is unknown. Cross-domain replication (COVID-19 vaccine discourse) is pre-registered (Paper 1 Supplement S8).

---

## 8. Conclusion (~300 words)

In a 9,242-post Public Service Loan Forgiveness corpus across five online communities, we find: (1) **one fully cross-instrument-concordant cohort pattern (SDN-Medical decoupling; lift_pp=−16.5 pp; OR<1 across all 5 specifications)**; (2) **one cohort with coupling under most operationalizations (Reddit r/PSLF; lift_pp=+10.0 pp; 4/5 specs OR>1, 1/5 spec flips under pursuing-or-completed combined definition)**; (3) three null cohorts where sentiment and stance are essentially uncorrelated (lifts within ±3 pp); (4) **one construct-misalignment exemplar (Reddit Finance)** where same-scorer Claude×Claude gives apparent decoupling (OR=0.18 [0.11, 0.30]) while cross-scorer estimates are too noisy to resolve direction (CIs spanning 1.0); (5) per-event topic restructuring at all 8 PSLF policy events (chi-sq p<10⁻⁴), robust to instrument choice but coupled with poster composition turnover; and (6) **per-author longitudinal panel infeasibility for all 8 events** (CIs ≥25 pp wide for within-person Δ rejecting), requiring pre/post analyses to be interpreted as composition shifts rather than within-person stance changes.

For researchers using forum discourse as a policy signal: the conventional single-instrument, pooled-cohort, pre/post-with-implicit-panel-assumption design is not adequate. Reporting cross-instrument robustness, cohort-stratified metrics, and per-author returning-rate is no longer optional.

We provide all analysis code, data, and intermediate outputs at OSF (DOI: forthcoming).

---

## Supplementary materials

- **S1**: Cohort definitions (subreddit lists per cohort)
- **S2**: Per-event 60-day pre/post window definitions
- **S3**: Full topic-restructuring tables (8 events × 7 topics × 5 cohorts where adequate sample)
- **S4**: Per-author returning-author detail per event
- **S5**: Cross-instrument operationalization full OR matrix (5 cohorts × 3 sentiment × 2 stance)
- **S6**: SDN attending career-stage subset (n=88, OR=0.024) — moved from main paper per audit feedback (small-cell sensitivity)
- **S7**: Reproducibility code and data deposit (OSF link)

---

## Cited references (priority list, ~25–35 total)

**CMV / methods:**
- Podsakoff, P. M., MacKenzie, S. B., Lee, J.-Y., and Podsakoff, N. P. (2003). Common method biases in behavioral research. *Journal of Applied Psychology* 88(5): 879–903.
- Spector, P. E. (2006). Method variance in organizational research. *Organizational Research Methods* 9(2): 221–232.
- Williams, L. J., Hartman, N., and Cavazotte, F. (2010). Method variance and marker variables. *Organizational Research Methods* 13(3): 477–514.

**Sentiment vs stance / forum discourse:**
- Bestvater, S. and Monroe, B. L. (2023). Sentiment is not stance. *Political Analysis* 31(2): 235–256.
- Mohammad, S. M. et al. (2016). SemEval-2016 Task 6: Detecting stance in tweets. *Proceedings of SemEval-2016*.
- Wang, J. et al. (2025). Survivors, complainers, borderliners: A composition-bias analysis of academic discourse on Reddit and Zhihu. *arXiv:2509.16831*.
- Freelon, D. et al. (2024). The post-API age of social media data access. *Annals of the AAPSS* 712.

**PSLF context:**
- Student Borrower Protection Center and American Federation of Teachers (2024). PSLF Servicer Performance Report.
- ProPublica (various) coverage of PSLF and student loan servicing
- ED Office of Federal Student Aid PSLF Data Center (federalstudentaid.gov)

**Statistical methods:**
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics* 6(2): 65–70.
- McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika* 12(2): 153–157.

---

## Implementation checklist for Paper 2 (Path B)

### Before draft starts
- [ ] Wait for comments collector to finish (~88% as of 2026-05-09; 17,888 / 20,366 posts)
- [ ] Re-run cohort heterogeneity analysis at full scale post-comments
- [ ] Re-run CMV diagnostic for Reddit Finance with full comments data
- [ ] Re-run per-event topic restructuring with full comments data
- [ ] Compute per-author returning-author counts post-comments (may unlock more events for within-person)
- [ ] Generate Figure 1 (per-event topic restructuring panel)
- [ ] Generate Figure 2 (cohort × event composition shift heatmap)
- [ ] Generate Figure 3 (5-cohort OR forest plot, 3 operationalizations per cohort)

### Section-by-section
- [ ] Section 1 (Intro): per outline (~800 words)
- [ ] Section 2 (Related work): per outline; explicit Wang et al. 2025 distinction (~600 words)
- [ ] Section 3 (Data): per outline; cite Paper 1 for instrument validation (~500 words)
- [ ] Section 4 (Methods): per outline; emphasize 3 operationalizations per cohort (~1,000 words)
- [ ] Section 5 (Results): per outline; tables 1, 2; figures 1, 2, 3 (~2,000 words)
- [ ] Section 6 (Discussion): per outline (~800 words)
- [ ] Section 7 (Limitations): per outline (~400 words)
- [ ] Section 8 (Conclusion): per outline (~300 words)
- [ ] Supplements S1–S7

### Polish
- [ ] Terminology sweep (drop "venting culture"; use "expressive negativity decoupled from behavioral intention")
- [ ] Move SDN attending OR=0.024 to Supplement S6 (audit feedback)
- [ ] Cite Wang et al. 2025 prominently in introduction
- [ ] Reframe same-scorer halo as APPLIED CMV, not novel finding
- [ ] APA-conformant p-value formatting

### Submission
- [ ] JCSS submission portal: https://www.springer.com/journal/42001
- [ ] Cover letter highlighting: cohort-conditional patterns, CMV diagnostic, composition-shift framing, per-author panel infeasibility
- [ ] Reviewer suggestions: Bestvater (Penn State), Wang et al. (corresponding author), Hutto (CalPoly)

---

## Critical reminders (do not overclaim)

1. **One fully robust cohort pattern (SDN-Medical) + one mostly-coupling pattern (r/PSLF) is NOT a strong "cohort heterogeneity is universal" claim.** 3 of 5 cohorts are null; 1 is a construct-misalignment exemplar. Honest framing: "Cohort heterogeneity is real for SDN-Medical and r/PSLF; null elsewhere; Reddit Finance illustrates construct-misalignment risk."

2. **Cross-instrument robustness check is essential.** Without it, the Reddit Finance "decoupling" claim would have been a publication-blocking error.

3. **Per-author panel infeasibility is a real constraint, not a temporary data limitation.** Even with comments data, only 1-2 events likely meet the threshold. Frame as discourse-data property.

4. **Per-event topic restructuring is the strongest substantive lead.** It is instrument-robust (does not depend on TextBlob/VADER) and statistically very strong (chi-sq p<10⁻⁴ for all 8 events). NOT independently of composition shifts.

5. **No causal claims about policy events affecting borrower behavior.** Topic restructuring is a discourse pattern, not a borrower-decision claim.

6. **No generalization to PSLF-borrower population.** Reddit + SDN demographics are not representative.

---

*End of Paper 2 (JCSS) outline. Status: ready for draft (after comments collector finishes and full-scale rerun completes).*
