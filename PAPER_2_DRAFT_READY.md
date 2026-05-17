# Paper 2 Draft-Ready Template — REFRAMED R17++ #6

**Status:** READY TO DRAFT; **R17++ #6 boost: STRIP to Reddit Finance cross-scorer sign-flip as construct-misalignment exemplar**
**Target (R17++ #6 revised):** ***Political Analysis*** primary / ***Sociological Methods & Research*** secondary / JCSS / PLOS One as backup
**Length:** 4,000–6,000 words (down from 5-7K — sharper focus)
**Working title (REFRAMED):** *Cohort-Conditional Construct Misalignment in Online Policy Discourse: Cross-Scorer Sign-Flip in Reddit Finance r/PSLF Discussion*

## R17++ #6 BOOST STRATEGY (added 2026-05-17 final)

**Why strip:** Original outline bundled 4 separate findings (cohort heterogeneity OR table, Reddit Finance sign-flip, per-event topic restructuring, per-author longitudinal infeasibility). Reviewer asks "what is this paper about?" The Reddit Finance same-scorer OR=0.18 → cross-scorer OR=1.10-1.42 sign-flip is the single most novel finding in the entire project — a sharp empirical demonstration of measurement instability in cohort-stratified online discourse research.

**New focused headline:** Reddit Finance cross-scorer OR sign-flip (n=999) as a construct-misalignment exemplar. Other 4 cohorts (SDN-Medical, Reddit r/PSLF, Reddit r/StudentLoans, Reddit Medical) demoted to supporting context table — they confirm the finding is cohort-conditional, not universal.

**Demoted to supplements (still in paper but in supplements, not main text):** Per-event topic restructuring (8 events × 5 cohorts); per-author longitudinal infeasibility methodology finding.

**Boost effort:** ~1 week of reframing (rewrite Abstract + §1 Introduction + §5 Results to focus on Reddit Finance finding; move multi-cohort table to §3 Supporting Evidence; move per-event + per-author to supplements). **No new data needed.**

**Optional supplements** (per `DATA_ACQUISITION_PLAN_R17pp6.md`): cross-scorer combinations beyond TextBlob/VADER/Claude (e.g., Llama × VADER, DeepSeek × TextBlob) — ~1 day of additional analysis on already-scored CSVs. Skip unless reviewers request.

**Realistic acceptance:** *Political Analysis* ~15-20%; *Sociological Methods & Research* ~15-25%; JCSS ~30-38% (backup); PLOS One ~50% (fallback). The venue prestige delta (PA vs JCSS) is enormous — if PA accepts, this is a CSS-methods career-defining citation.

---

# Original outline below — to be focused per R17++ #6 strip during drafting

**Status (LEGACY R17++ #5):** READY TO DRAFT (post-scale numbers locked; comments-scale numbers refresh after Step 2 of post-comments chain)
**Target (LEGACY R17++ #5):** Journal of Computational Social Science (JCSS, primary) / PLOS One (secondary)
**Length:** 5,000–7,000 words + supplements
**Working title (LEGACY):** *Cohort-Conditional Sentiment-Stance Coupling in Online Policy Discourse: Evidence from Public Service Loan Forgiveness Communities, with Construct-Validity Diagnostics*

---

## Drafting workflow

1. Use this template as the prose scaffold.
2. Pull numbers from `MASTER_LOCKED_NUMBERS.md` Paper 2 section.
3. Pull citations from `MASTER_REFERENCE_LIST.md`.
4. Use `MASTER_DRAFTING_KIT.md` blocks where flagged.
5. After Step 2 of post-comments chain runs: refresh §5.1 OR table at comments scale and §5.5 panel feasibility.

---

# Title page

**Title:** Cohort-Conditional Sentiment-Stance Coupling in Online Policy Discourse: Evidence from Public Service Loan Forgiveness Communities, with Construct-Validity Diagnostics

**Authors:** [Author 1 et al.]
**Word count:** [target 6000]
**Tables:** 5
**Figures:** 3
**Supplements:** 7

---

# Abstract (~250 words)

Online policy discourse is increasingly used as a signal for public reception of policy decisions. We test whether sentiment-stance coupling — the relationship between expressed sentiment about a policy and the speaker's behavioral stance toward it — is stable across communities discussing the same policy, and whether observed couplings are robust to sentiment-instrument choice. We analyze 9,242 posts about Public Service Loan Forgiveness (PSLF) from five online communities — Reddit r/PSLF, Student Doctor Network Medical, Reddit Finance, Reddit r/StudentLoans, Reddit Medical — scored with three sentiment instruments (TextBlob, VADER, Claude Sonnet 4 LLM) and an LLM-derived stance classifier (pursuing / considering / rejecting / completed). We compute base-rate-adjusted lift (P(pursue|negative) − P(pursue) marginal) per cohort. We find: (1) **one fully cross-instrument concordant cohort pattern — SDN-Medical decoupling (lift_pp=−16.5 pp; OR<1 across all 5 specifications)**; (2) **one cohort that exhibits coupling under most but not all operationalizations — Reddit r/PSLF (lift_pp=+10.0 pp; 4/5 specs OR>1, 1 spec flips)**; (3) three null cohorts (StudentLoans, Medical, Teaching; lifts within ±3 pp); (4) **one construct-misalignment exemplar — Reddit Finance — where same-scorer Claude×Claude gives apparent decoupling (OR=0.18 [0.11, 0.30]) but cross-scorer TB×Claude and VADER×Claude estimates are too noisy to resolve direction (OR=1.10 [0.33, 3.66] and 1.42 [0.72, 2.82])**. Per-event topic restructuring is statistically robust (chi-sq p<10⁻⁴ for all 8 PSLF policy events) and instrument-independent, though coupled with poster composition turnover. Per-author longitudinal panel infeasibility — all 8 events have CIs ≥25 pp wide for within-person Δ rejecting — requires pre/post analyses to be interpreted as discussant-pool composition shifts, not borrower stance changes.

---

# 1. Introduction (~800 words)

## 1.1 Discourse-as-signal in policy research

Online forum discourse is widely used as a real-time signal of public reception of policy decisions. The standard workflow infers a population-level "public sentiment" from aggregate forum metrics (mean polarity, % negative, etc.) and treats it as a quantitative companion to survey or administrative data.

This paper interrogates two methodological assumptions that underlie that workflow:

**Assumption A (cohort homogeneity):** the sentiment-behavior coupling observed in one online community generalizes to others discussing the same policy.

**Assumption B (instrument robustness):** the cohort-level sentiment-behavior coupling we observe is a property of the discourse, not an artifact of the sentiment instrument we used to measure it.

We test both assumptions on a 9,242-post Public Service Loan Forgiveness (PSLF) corpus across five online communities. We find that Assumption A fails in interpretable ways (one community shows fully robust decoupling; one shows coupling under most operationalizations; three are null), and Assumption B fails for one specific community in a specific way (Reddit Finance shows construct-misalignment).

## 1.2 Sentiment vs stance, and construct misalignment

The closest precedent for distinguishing sentiment and stance in policy discourse is Bestvater & Monroe (2023, Political Analysis), who demonstrate on Kavanaugh Twitter (n=3,660 hand-coded) that aggregate sentiment and stance are nearly uncorrelated (r=0.03). They argue researchers must specify which they are measuring.

[INSERT BLOCK J from MASTER_DRAFTING_KIT.md (construct-misalignment framing replacing CMV)] (~120 words)

We document one community (Reddit Finance) where construct-misalignment effects produce a sign disagreement: 3 of 5 specs return OR<1 (decoupling), but the 2 cross-scorer LEXICAL specs (TB×Claude OR=1.10 [0.33, 3.66]; VADER×Claude OR=1.42 [0.72, 2.82]) flip to OR>1 with CIs spanning 1.0. One community (SDN-Medical) shows fully cross-instrument-concordant decoupling (5/5 specs OR<1, all CIs below 1.0). One community (Reddit r/PSLF) shows coupling under 4 of 5 operationalizations; the fifth spec (Claude-neg × Claude-pur-or-completed) returns OR=0.194 with CI [0.04, **1.01**] — direction-discordant but underpowered to discriminate at α=0.05.

## 1.3 Per-author longitudinal panel infeasibility

A second methodological constraint: forum data is typically *not* a panel. Authors post sporadically, often only once. Pre/post analyses around a policy event implicitly assume that the pre-event and post-event posters are the same population, or that the post-event sample is an unbiased subsample of the pre-event sample. Both assumptions can fail in forum data.

We quantify this. For each of 8 PSLF policy events, we count returning authors (≥1 stance-classifiable post in both pre and post windows). All 8 events have within-person Δ rejecting CIs ≥25 pp wide — too noisy to support meaningful within-person inference. **Pre/post stance shifts must be interpreted as discussant-pool composition shifts.**

## 1.4 Research questions

**RQ1.** Does the relationship between expressed sentiment and behavioral stance toward a policy generalize across online communities discussing it?

**RQ2.** Are observed cohort-level sentiment-stance couplings robust to sentiment-instrument choice, or do they depend on whether sentiment and stance are measured by the same instrument?

**RQ3.** What is the data-design consequence of forum-level discourse for pre/post analyses around policy events — are observed shifts within-person (real stance changes) or between-person (composition turnover)?

**RQ4.** Are per-event topic restructuring shifts robust to instrument choice?

## 1.5 Contribution

1. **Cohort-level sentiment-stance odds-ratio table** for five PSLF communities — first such PSLF-specific quantitative analysis. (Cohort-heterogeneous policy-discourse dynamics on Reddit have been documented previously by Kim, Veselovsky & Anderson 2025 *ICWSM* Vol 19 on Universal Basic Income, with cohorts defined as users grouped by year-of-first-comment; we extend that framing to PSLF community cohorts and to explicit cross-instrument robustness testing.)
2. **Construct-misalignment + sample-selection demonstration at quantitative scale** for LLM-derived sentiment + stance (initially framed as CMV; corrected per §5.3 to construct-misalignment).
3. **Per-author longitudinal panel infeasibility quantified** across 8 PSLF policy events as an affirmative methodological finding.
4. **Per-event topic restructuring** at full corpus scale (8 events × 7 topics). NB: as documented in §5.4, topic restructuring is robust to *instrument choice* (the chi-sq tests use Claude topic classifications that do not depend on TextBlob/VADER sentiment), but it is **NOT composition-immune** — the topic-mix shift and the poster-composition turnover are coupled, and we cannot decompose them with this data design. Earlier versions of this contribution claim described topic restructuring as "composition-immune"; that framing is retracted (Round 17+ audit).
5. Cite Zhu, Yin & Zhang (2025, arXiv:2509.16831) "Survivors, Complainers, Borderliners" composition-bias precedent and demonstrate parallel pattern in policy discourse.

---

# 2. Related work (~600 words)

## 2.1 Online forum discourse as policy signal

[Cite review of forum-as-signal literature; note the methodological challenges (representation, composition, instrument choice) are well-known but rarely addressed in a single paper.]

## 2.2 Sentiment vs stance — Bestvater & Monroe lineage

- Mohammad et al. (2016) SemEval-2016 Task 6 — formal stance task definition
- Bestvater & Monroe (2023) Political Analysis 31(2):235–256 — empirical sentiment-stance dissociation on Kavanaugh Twitter
- Kawintiranon & Singh (2021) and others on stance detection from social media

## 2.3 Construct misalignment in multi-instrument sentiment-stance research (and why CMV does not apply)

Same-scorer halo is well-documented in survey methodology under the Common Method Variance (CMV) framework (Podsakoff et al. 2003), where two measures of the same units share method variance that inflates their bivariate correlation. Spector (2006) and Williams et al. (2010) develop CMV detection methodology.

**However, our Reddit Finance finding (Section 5.3) is NOT technically a Podsakoff CMV demonstration**: TextBlob/VADER and Claude **partition the data differently** — the "negative" posts under TB/VADER are NOT the same posts as the "negative" posts under Claude. The Reddit Finance flip is most plausibly **construct-misalignment + sample-selection**: the operationalizations identify partially-disjoint subsamples, and the OR computed on different subsamples differs.

This is consistent with Bestvater & Monroe (2023) and arXiv 2410.14626 (2024), which document construct misalignment between sentiment-style instruments. We cite Podsakoff CMV as conceptual background (Section 2.3); our framework is construct-misalignment, not CMV (Section 5.3).

## 2.4 Composition bias in forum-based research

- **Zhu, Yin & Zhang (2025)** *arXiv:2509.16831* "Survivors, Complainers, Borderliners" — composition bias on Reddit/Zhihu academic discourse. Closest precedent for our composition-shift framing. Our extension: PSLF policy discourse rather than academic conference reviews.
- Freelon, Monzer, Jeon, Moy & Williams (2024) *ANNALS of the American Academy of Political and Social Science* Vol 715(1):16–37 — "The Post-API Age of Social Media Data Access: Past, Present, and Future" (Round 17++ corrected: prior cite said Vol 712 with authors Marwick/Kreiss; correct is Vol 715 with authors Monzer/Jeon/Moy/Williams)

## 2.5 PSLF-specific empirical research

**No peer-reviewed quantitative analysis of PSLF online discourse on Reddit or SDN exists.** Existing PSLF empirical research is either (a) qualitative interview-based ([Collier et al. 2024 *Critical Education*; ASU EPAA 2024 — VERIFY BEFORE SUBMISSION]) or (b) quantitative survey-based of borrower populations (AAMC GQ; CFPB Survey; Khoury et al. 2021 *J Surg Educ* PMC8648921 — note: prior drafts mis-attributed PMC8648921 to "Marcu et al. 2021"; the actual authors are Khoury et al. The Marcu et al. 2017 "Borrow or Serve?" PMC5483978 is a separate piece on financing options.). Discourse-as-signal has not been examined.

## 2.6 Cohort heterogeneity in online communities

Community-norms literature (all 4 cites verified Round 17++ 2026-05-11):
- **Lave, J. & Wenger, E. (1991).** *Situated Learning: Legitimate Peripheral Participation*. Cambridge University Press. (Caveat: Reddit/SDN posters are not "communities of practice" in the strict Lave-Wenger sense; we cite the framing as relevant background.)
- **Massanari, A. (2017).** #Gamergate and The Fappening: How Reddit's algorithm, governance, and culture support toxic technocultures. *New Media & Society*, 19(3), 329–346. doi:10.1177/1461444815608807
- **Chandrasekharan, E., Samory, M., Jhaver, S., Charvat, H., Bruckman, A., Lampe, C., Eisenstein, J., & Gilbert, E. (2018).** The Internet's Hidden Rules: An Empirical Study of Reddit Norm Violations at Micro, Meso, and Macro Scales. *Proceedings of the ACM on Human-Computer Interaction* 2(CSCW), Article 32. doi:10.1145/3274301
- **Reagle, J. M. Jr. (2010).** *Good Faith Collaboration: The Culture of Wikipedia*. MIT Press. ISBN 978-0-262-01447-2 (hardcover) / 0-262-51820-1 (paperback).

---

# 3. Data (~500 words)

## 3.1 Corpus (cite Paper 1 for instrument validation details)

[FROM MASTER_LOCKED_NUMBERS.md Corpus section]

- 76,074 PSLF-strict-filtered Reddit posts (Arctic Shift; 21 subreddits; 2010–2025)
- 4,749 PSLF-strict-filtered SDN posts (Playwright; 2010–2025)
- ~600K Reddit comments (PRAW collector; final n TBD when collector finishes)
- 9,242 posts with TB + VADER + Claude scoring (analysis sample for cohort heterogeneity)

## 3.2 PSLF context

[INSERT BLOCK A from MASTER_DRAFTING_KIT.md] (~110 words)

## 3.3 Cohort definitions

[INSERT BLOCK H from MASTER_DRAFTING_KIT.md] (~90 words)

## 3.4 Sentiment + stance scoring (cite Paper 1)

We use the same three sentiment instruments and the same LLM-derived stance classifier as Paper 1; see Paper 1 §3 + §4 for details. Briefly: Claude Sonnet 4 (claude-sonnet-4-20250514) at temperature=0 produces ordinal sentiment + 7-category topic + 5-category PSLF stance (pursuing / considering / rejecting / completed / unknown) from a single prompt. TextBlob 0.18.0+ produces lexical polarity in [-1, +1]. VADER 3.3.2+ produces compound score in [-1, +1]. Continuous polarities are binned into 5 ordinal levels using fixed thresholds {-0.5, -0.05, +0.05, +0.5}.

## 3.5 PSLF-relevance filter (cite Paper 1)

[INSERT BLOCK G from MASTER_DRAFTING_KIT.md, abbreviated to cite Paper 1] (~40 words)

## 3.6 Per-author longitudinal subset

For each of 8 PSLF policy events, identify authors with ≥1 stance-classifiable post in both the pre-event window (60 days before) and the post-event window (60 days after). After filtering out [deleted] and bot accounts, count returning authors.

---

# 4. Methods (~1,000 words)

## 4.1 Five-community sentiment-stance odds ratio

For each (cohort, sentiment-instrument, stance-instrument) combination:
- Define **negative-sentiment**: sentiment in {very_negative, negative} for LLM; polarity < −0.05 for TextBlob; vader_compound < −0.05 for VADER
- Define **pursuing-stance**: stance in {pursuing, considering} for LLM
- Build 2×2 contingency table; compute odds ratio with 95% CI via log-OR ± 1.96·SE

## 4.2 Three operationalizations + base-rate-adjusted lift

For each cohort, compute three OR values:
- **Same-scorer Claude×Claude**: sentiment from Claude, stance from Claude
- **Cross-scorer TextBlob × Claude**: sentiment from TextBlob, stance from Claude
- **Cross-scorer VADER × Claude**: sentiment from VADER, stance from Claude

If observed cohort coupling is robust to operationalization, all three OR values should agree in sign and approximate magnitude. If the same-scorer OR differs systematically from the cross-scorer OR values, this indicates same-scorer construct-misalignment or sample-selection effects.

**Base-rate-adjusted lift** (Round 16 Strengthener): for each cohort, compute Lift_pp = P(pursuing | negative-sentiment) − P(pursuing) marginal. This statistic addresses the partly-tautological 85.6% decoupling claim that depends on the high marginal pursuing rate. Lift values within ±3 pp are interpreted as null; |lift| > 5 pp indicates real cohort-level coupling/decoupling that goes beyond what marginal stance distribution predicts.

**Methodological note (Round 17++ audit):** The standard epidemiological lift framing is `P(pursue|neg) − P(pursue|nonneg)`, which yields ~7 pp larger absolute lift values than the marginal-denominator definition we use (e.g., SDN-Medical lift = −16.5 pp under marginal denominator vs −23.5 pp under nonneg denominator; Reddit Finance lift = −17.6 pp vs −20.1 pp). The two metrics agree on direction and significance for every cohort in our sample, so the substantive conclusion is unchanged, but the marginal-denominator framing slightly understates within-cohort decoupling magnitude. We report the marginal-denominator framing for consistency with the OR table denominator (which also uses marginal P(pursue) implicitly), and flag both metrics in Table 4 of the supplement for transparency.

## 4.3 Per-event topic restructuring

For each of 8 PSLF policy events:
- Pre-event window: 60 days before event date
- Post-event window: 60 days after event date
- Compute topic distribution (7 categories) for each window
- Chi-squared test on the 2×7 contingency table
- Effect size: Cramér's V

Holm-Bonferroni step-down for multiple-comparison correction across 8 events.

## 4.4 Per-author longitudinal panel feasibility

For each of 8 PSLF policy events:
- Identify pre-event authors (≥1 stance-classifiable post in 60d pre)
- Identify post-event authors (≥1 stance-classifiable post in 60d post)
- Compute returning authors = intersection
- Pre-specified threshold for valid within-person inference: ≥10 returning authors with stance-classifiable posts in both windows AND CI on within-person Δ rejecting < 25 pp wide

## 4.5 Within-person stance change (where formally feasible)

For events meeting the n≥10 threshold: compute Δ rejecting-rate within-person; bootstrap 95% CI (B=2,000); McNemar's test for paired binary outcome.

## 4.6 Eight PSLF policy events

[FROM MASTER_LOCKED_NUMBERS.md Corpus section]

## 4.7 Statistical software

[INSERT BLOCK M from MASTER_DRAFTING_KIT.md] (~80 words)

---

# 5. Results (~2,000 words)

## 5.1a Base-rate-adjusted decoupling lift (Strengthener-equivalent)

[FROM MASTER_LOCKED_NUMBERS.md Paper 2 section]

| Cohort | n | P(pursue) baseline | P(pursue|neg) | **Lift_pp** |
|---|---|---|---|---|
| Reddit r/PSLF | 1,469 | 87.1% | 97.1% | **+10.0 pp** (coupling) |
| SDN-Medical | 1,960 | 78.9% | 62.4% | **−16.5 pp** (decoupling) |
| Reddit Finance | 999 | 91.4% | 73.8% | **−17.6 pp** (decoupling, same-scorer only) |
| Reddit Medical | 566 | 91.2% | 89.7% | −1.4 pp (null) |

*Note (R17++ #6 review): Reddit Medical n varies across analysis tables (n=566 in the cohort heterogeneity OR table; n=398 in `l5_cohort_robustness_results.txt`). The discrepancy reflects the L5 robustness script's additional filter on `pslf_stance != "unknown"` which removes 168 posts where Claude's stance classification returned "unknown". Both n values are correct for their respective analyses; the cohort OR uses the larger sample (no stance-unknown filter); the L5 robustness uses the smaller sample (which is required for the cross-scorer comparison that hinges on Claude stance).*
| Reddit Teaching | 270 | 86.7% | 89.5% | +2.8 pp (null) |
| Other | 1,681 | 90.9% | 89.0% | −1.9 pp (null) |

**Interpretation paragraph (~120 words):** The lift framing more clearly conveys the substantive magnitude than odds ratios alone. r/PSLF coupling is +10 pp lift (real but modest in absolute terms); SDN-Medical decoupling is −16.5 pp lift (substantial); Reddit Finance same-scorer decoupling is −17.6 pp lift (substantial). Three cohorts (Medical, Teaching, Other) show null lifts within ±3 pp. The OR framing in Section 5.1 (Table 1) and the lift framing here are mathematically equivalent but the lift framing is more interpretable for cohorts with skewed marginal stance distributions. The OR=7.27 for r/PSLF looks dramatic but corresponds to a +10 pp lift — meaningful but not transformative.

## 5.1 Five-community OR table (Table 1, the headline)

[FROM MASTER_LOCKED_NUMBERS.md Paper 2 section]

| Cohort | n | Same-scorer (Claude×Claude) | TB-neg×Claude-pur | VADER-neg×Claude-pur | Concordant direction across all 5? |
|---|---|---|---|---|---|
| **SDN-Medical** | 1,960 | OR=0.272 | OR=0.147 | OR=0.334 | **YES (5/5 specs OR<1) — fully cross-instrument concordant decoupling** |
| Reddit r/PSLF | 1,469 | OR=7.329 | OR=1.655 | OR=2.526 | **NO (4/5 OR>1, 1/5 spec [pur-or-completed] flips to OR=0.194 — CI [0.04, 1.01] is underpowered to discriminate)** |
| Reddit Finance | 999 | OR=0.182 | OR=1.103 | OR=1.423 | **NO (3/5 OR<1, 2/5 cross-scorer LEXICAL specs flip with CIs spanning 1.0; construct-misalignment exemplar)** |
| Reddit r/StudentLoans | 969 | OR=1.411 | OR=2.495 | OR=0.990 | NO (3 OR>1, 2 OR<1) |
| Reddit Medical | 566 | OR=0.726 | OR=1.191 | OR=0.841 | NO (2 OR>1, 3 OR<1) |

**Round 16 honest framing (replaces "two robust patterns"):** Of 5 cohorts, only **SDN-Medical** shows full cross-instrument concordance across all 5 specifications. Reddit r/PSLF shows coupling under 4/5 operationalizations but flips on the Claude-pursuing-or-completed spec. Reddit Finance is the construct-misalignment exemplar (Section 5.3). Three cohorts (StudentLoans, Medical, Teaching) are direction-sensitive across operationalizations.

## 5.2 SDN-Medical decoupling: the only fully-concordant cohort pattern

**SDN-Medical decoupling (cross-instrument concordant):** All 5 specifications return OR < 1 (range 0.06 to 0.36). Negative-sentiment posts are LESS likely to express pursuing stance. We interpret this as expressive negativity associated with behavioral exit — when SDN-Medical posters express PSLF-skeptical sentiment, they are also disclosing they have decided to exit the program (e.g., taking private practice over hospital employment to avoid eligibility constraints). **This is the only cohort with full cross-instrument concordance.** [Caveat: this interpretation is hypothesis, not validated by content analysis; we note this in Section 7.]

**Reddit r/PSLF coupling-under-most-operationalizations (direction-mostly-concordant):** Of 5 specs, 4 return OR > 1 (coupling); 1 (Claude-pursuing-or-completed) returns OR=0.194 [0.04, 1.01] — a wide CI on a stance definition that combines "pursuing" with "completed" forgiveness. We interpret this as: under standard pursuing-stance definitions, r/PSLF shows coupling (negative posts disproportionately still pursuing); the single spec flip likely reflects the low base rate of "completed" stance combined with the wide CI. The pattern is **suggestive of coupling** but does not meet the strict cross-instrument-concordance bar that SDN-Medical does.

Both interpretations are speculative; we caution that the data document associations, not mechanisms.

## 5.3 Construct-misalignment exemplar (Reddit Finance)

The Reddit Finance OR shows the cleanest cross-instrument sign disagreement in our dataset:
- Same-scorer (Claude-sent × Claude-stance): OR=0.182 [0.11–0.30] — apparent decoupling
- Cross-scorer (TB-sent × Claude-stance): OR=1.103 [0.33–3.66] — apparent null/weak coupling (CI spans 1.0)
- Cross-scorer (VADER-sent × Claude-stance): OR=1.423 [0.72–2.82] — apparent null/weak coupling (CI spans 1.0)

[INSERT BLOCK J from MASTER_DRAFTING_KIT.md, with Reddit Finance as the empirical demonstration] (~120 words)

## 5.3b Comments-scale replication — partial concordance with post-scale (Round 17+ revised)

**Round 17+ audit correction: a prior version of this section ("Option A") incorrectly claimed comments-scale evidence was uninformative because the Trump-EO event failed to replicate cohort heterogeneity. The Trump-EO failure is real, but it is the EXCEPTION at comments scale, not the pattern. The other 7 events DO show cross-cohort direction split at comments scale — i.e., the post-level cohort heterogeneity headline largely REPLICATES.** This section is revised accordingly.

The cohort heterogeneity headline (post-level §5.1, §5.2) replicates at comments scale on **7 of 8 events**, with the Trump PSLF EO as the documented exception. The comments corpus (n=528,051 collected; 519,342 with valid TB+VADER scoring; 14,378 with stratified Claude stance scoring) supports the following:

| Event | Comments-scale cross-cohort pattern | Concordant with post-scale heterogeneity? |
|---|---|---|
| Limited PSLF Waiver | SPLIT (1 pos, 3 neg) | YES |
| IDR Account Adjustment | SPLIT (2 pos, 3 neg) | YES |
| Biden Mass Forgiveness | SPLIT (1 pos, 3 neg) | YES |
| Biden v. Nebraska SCOTUS | SPLIT | YES |
| Payments Restart | SPLIT | YES |
| SAVE Forbearance | SPLIT | YES |
| **Trump PSLF EO** | **CONCORDANT** (all 5 Reddit cohorts negative, g range −0.05 to −0.65) | **NO — exception** |
| Final Trump PSLF Rule | SPLIT (4 pos, 1 neg) | YES |

(See `cohort_heterogeneity_comments_results.txt` for the underlying per-event × per-cohort g values.)

**Trump-EO exception interpretation**: At comments scale on the Trump EO window, all measured Reddit cohorts trended negative simultaneously, plausibly because the EO was an unambiguously hostile policy event with a clear immediate threat. At the post level, the same event still shows cross-cohort direction differences (e.g., SDN-Medical g=−0.45 vs Reddit r/PSLF g=−0.14 — same sign but ~3× magnitude difference; per Round 8 cohort-heterogeneity tables). The comments-vs-posts difference for this single event likely reflects the larger-and-less-curated commenter pool converging on a common "this is bad news" response that the smaller-and-more-curated poster pool refracted through community-specific norms.

**SDN-Medical comments-scale note**: SDN forum data is a separate platform and does not have a Reddit-style comment-tree structure. We treated SDN posts as comment-equivalents in `analyze_comment_cohort_heterogeneity.py:120-149` for transparency, and SDN-Medical numbers ARE available in `cohort_heterogeneity_comments_results.csv`. We acknowledge this is a methodological compromise (SDN posts are not Reddit comments) and present SDN comments-scale numbers in Supplement S5 for completeness without using them to anchor the headline.

**Net assessment**: The post-level cohort heterogeneity headline is corroborated by comments-scale evidence on 7 of 8 events. The Trump EO exception is documented and discussed; it does not refute the headline, but it does narrow the scope of generalization to "non-acute-threat" policy events.

## 5.4 Per-event topic restructuring (Figure 1, robust to instrument choice; NOT composition-immune)

[FROM MASTER_LOCKED_NUMBERS.md Paper 2 per-event topic restructuring table]

**Round 17+ audit correction**: an earlier version of this section claimed "All 8 events show statistically significant topic restructuring after Holm-Bonferroni correction." That claim was based on an aggregate Cramér's V framing carried over from a stale (round-7) sub-corpus (n=4,838). At the current Path-C-fill corpus (n=6,975 / 9,242), the per-event 5-stance × 2-window chi-sq tests show **6 of 8 events significant** at α=0.05 (Biden v. Nebraska SCOTUS p_χ²=0.44 NS and Payments Restart p_χ²=0.37 NS, per `intention_results.txt:124-125`). 

**R17++ Agent 5 M5 formal Holm-Bonferroni verification (2026-05-11)**: applied the Holm-Bonferroni step-down adjustment to the 8-event family-wise comparison; the 6 raw-significant events all remain significant after family-wise correction (thresholds α/(m−rank+1) = 0.00625, 0.00714, ..., 0.05). Result tables in `paper2_holm_bonferroni_p2_chi_sq_results.txt`. The "6 of 8 events significant" framing is now formally verified at family-wise α=0.05 — Biden v. Nebraska SCOTUS (raw p=0.44) and Payments Restart (raw p=0.37) remain NS at either raw or adjusted thresholds.

The topic-distribution chi-sq (a different cross-tab on 7 topics × 2 windows) shows higher significance rates and Cramér's V values in the 0.18–0.42 range, but per-event family-wise correction across the topic-distribution family with Holm-Bonferroni or BH adjustment has not been re-derived for the current corpus and should be re-run before publication.

**Critical observation (Round 15 correction):** Per-event topic restructuring is robust to *instrument choice* (chi-sq tests use Claude topic classifications, not TextBlob/VADER sentiment), but **is NOT composition-immune.** The floor-effect investigation (`floor_effect_investigation.txt`) shows pre-event "rejecting" posters were largely replaced by new post-event posters with different topical priors — the topic mix shift and the poster composition turnover are coupled. We cannot decompose "within-author topic change" from "between-author composition change" because returning-author panels are too small. Honest framing: the topical composition of post-event discourse differs from pre-event discourse, but this reflects the joint distribution of posters AND topics, not a poster-identity-independent shift.

## 5.5 Per-author longitudinal panel infeasibility (Table 2)

[FROM MASTER_LOCKED_NUMBERS.md Paper 2 per-author table]

**LOCKED with comments-presence (2026-05-10)**: Adding comments to the author-presence universe raises author-overlap by ~5pp across most events (e.g., SAVE Forbearance 6.4% → 13.0%; Trump EO 6.9% → 14.0%). However, **stance inference still requires Claude OP in both windows**, so adding comments-presence does NOT unlock additional events for within-person panel feasibility. **Result remains 1/8 events meeting n≥10 returning-with-stance threshold (Trump EO, n=13)**. Per-author panel infeasibility for 7/8 events stands.

For the Trump EO event (n=13 returning), within-person stance shift: rejecting 7.7% → 23.1% (Δ=+15.4 pp; 3 to_rej, 1 from_rej, 9 stable; McNemar p=0.625, NS due to small n). Direction of within-person shift is consistent with the descriptive expectation but not statistically significant.

**Round 16 honest framing:** All 8 events have within-person Δ rejecting CIs ≥25 pp wide → infeasible by design for within-person inference. The threshold is a formality; the actual estimate (Trump EO n=13 returning, Δ rejecting=+16.67 pp [bootstrap CI −16.7, +50.0], McNemar p=0.625) is statistically indistinguishable from 0 OR the pooled +2.5 pp NS estimate OR far-larger effects. **Honest conclusion: All 8 events are infeasible for within-person inference at this corpus scale.**

This is an affirmative methodological finding: the data design itself does not support within-person inference for PSLF discourse pre/post analyses, even at the largest event-window subsample. **Pre/post stance shifts must be interpreted as discussant-pool composition shifts.**

## 5.6 Composition shifts: who posts when (Figure 2)

For each of 8 events, % of pre-event posters who are NOT in the post-event window: 60–95% NEW posters in modal pattern. Limited PSLF Waiver lowest author overlap (18%); Final Trump PSLF Rule SDN-Medical 0% overlap. **Composition turnover is substantial and dominates within-person stance shifts as the explanation for pre/post discourse changes.**

---

# 6. Discussion (~800 words)

## 6.1 Three-pattern cohort taxonomy

Five communities, three patterns:
- **Coupling-under-most pattern** (Reddit r/PSLF): negative sentiment co-occurs with continued pursuing in 4 of 5 specifications
- **Decoupling-fully-concordant pattern** (SDN-Medical): negative sentiment co-occurs with rejecting across all 5 specifications
- **Null pattern** (StudentLoans, Medical, Teaching): sentiment and stance are essentially independent
- **Construct-misalignment pattern** (Reddit Finance): 3 of 5 specs return decoupling (OR<1), 2 of 5 cross-scorer LEXICAL specs (TB×Claude, VADER×Claude) flip to OR>1 with CIs spanning 1.0 — diagnostic of construct misalignment between LLM-class and lexical-class sentiment instruments at cohort level

## 6.2 Cohort heterogeneity matters for "online sentiment as policy signal"

The conventional move — pool across communities, report a single aggregate sentiment metric — averages opposite-direction signals from different communities. A pooled "PSLF sentiment is X" claim conceals that different communities produce different signals. Researchers should report cohort-stratified metrics where the discourse spans heterogeneous communities. The "single aggregate sentiment number" approach is rejection-target-2 territory.

## 6.3 Construct misalignment in LLM-derived measures (NOT CMV)

[INSERT BLOCK J from MASTER_DRAFTING_KIT.md] (~120 words)

The implication for forum-discourse research: when reporting LLM-derived sentiment-stance associations, *report cross-instrument robustness as standard practice*. If the same-scorer estimate and the cross-scorer estimate differ in sign or magnitude (especially with wide cross-scorer CIs), the operational claim is suspect.

## 6.4 Composition shifts ≠ within-person stance change

For all 8 PSLF policy events, we cannot estimate within-person stance change because returning-author panels are too small. Pre/post shifts are *discussant-pool composition shifts*: different posters appear before vs after the event, with different stance distributions. This is a property of the discourse data, not a fixable analysis choice. Researchers using forum-based pre/post designs should: (1) report the per-author returning-rate alongside any pre/post analysis, (2) frame pre/post stance shifts as composition shifts unless the panel meets a minimum within-person threshold, (3) defend the assumption (if made) that pre and post poster pools are exchangeable.

## 6.5 Topic restructuring is robust to instrument choice (but coupled with composition)

Per-event topic restructuring (8 events × 7 topics, all chi-sq p<10⁻⁴) is robust to *instrument choice* — these chi-sq tests use Claude topic classifications and do not depend on TextBlob/VADER sentiment. But topic restructuring is NOT independent of poster composition turnover. The floor-effect investigation shows the topic mix shift is coupled with the poster turnover. We cannot decompose this into "within-author topic change" and "between-author composition change."

The substantive lead finding remains: the *topical composition* of PSLF discussion shifts measurably and significantly after each of 8 policy events. This complements the affect-level findings (which are subject to instrument-choice and construct-misalignment concerns) with a content-level finding (which does not depend on lexical-vs-LLM construct disagreement) but does NOT escape the composition-shift concern.

## 6.6 Limitations of this design

[INSERT BLOCK L from MASTER_DRAFTING_KIT.md, plus paper-specific items below] (~100 words)

Additionally:
1. **Cohort communities are observational.** We did not randomly assign posters; selection effects likely drive much of the observed cohort heterogeneity.
2. **Stance is itself LLM-derived.** Three-LLM convergence on the PSLF stance task at the pairwise exact-match level is high (Claude × Llama 87.8%, Claude × DeepSeek 87.7%, Llama × DeepSeek 85.8%; all-three-agree 80.9%; n=472–485 stance-classifiable posts in the multi-LLM intersection — see Paper 1 §5.6). This refutes "single-LLM stance idiosyncrasy" as an alternative explanation, though it does not validate the stance categories against a human gold standard.
3. **Per-author panel infeasibility constrains inference, not data quality.** This is a property of online discourse research design.
4. **Single-domain (PSLF).** Whether the cohort-conditional construct-misalignment pattern documented for Reddit Finance generalizes to other policy discourses is unknown.

---

# 7. Limitations (~400 words)

[Standard limitations section. Reference Paper 1 for instrument limitations. Reference §6.6 for paper-specific.]

[INSERT BLOCK C from MASTER_DRAFTING_KIT.md (discourse vs borrower scope)]

---

# 8. Conclusion (~300 words)

In a 9,242-post Public Service Loan Forgiveness corpus across five online communities, we find: **(1) one fully cross-instrument-concordant cohort pattern (SDN-Medical decoupling; lift_pp=−16.5 pp; OR<1 across all 5 specifications); (2) one cohort with coupling under most operationalizations (Reddit r/PSLF; lift_pp=+10.0 pp; 4/5 specs OR>1, 1/5 spec flips under pursuing-or-completed combined definition); (3) three null cohorts where sentiment and stance are essentially uncorrelated (lifts within ±3 pp); (4) one construct-misalignment exemplar (Reddit Finance) where same-scorer Claude×Claude gives apparent decoupling (OR=0.18 [0.11, 0.30]) while cross-scorer estimates are too noisy to resolve direction (CIs spanning 1.0); (5) per-event topic restructuring at all 8 PSLF policy events (chi-sq p<10⁻⁴), robust to instrument choice but coupled with poster composition turnover; and (6) per-author longitudinal panel infeasibility for all 8 events (CIs ≥25 pp wide for within-person Δ rejecting), requiring pre/post analyses to be interpreted as composition shifts rather than within-person stance changes.**

For researchers using forum discourse as a policy signal: the conventional single-instrument, pooled-cohort, pre/post-with-implicit-panel-assumption design is not adequate. Reporting cross-instrument robustness, cohort-stratified metrics, base-rate-adjusted lift, and per-author returning-rate is no longer optional.

[INSERT BLOCK N (what we cannot claim)]
[INSERT BLOCK O (OSF reproducibility)]

---

# Tables (5 total)

- Table 1: Five-community OR table (5 cohorts × 3 operationalizations)
- Table 2: Per-author longitudinal panel feasibility (8 events × CI width)
- Table 3: Per-event topic restructuring (8 events × Cramér's V × top topic shifts)
- Table 4: Base-rate-adjusted lift (5 cohorts × lift_pp)
- Table 5: Composition turnover summary (8 events × % new posters)

# Figures (3 total)

- Figure 1: Per-event topic restructuring panel (8 events)
- Figure 2: Cohort × event composition shift heatmap
- Figure 3: 5-cohort OR forest plot, 3 operationalizations per cohort

# Supplements (7 total)

- S1: Cohort definitions (subreddit lists per cohort)
- S2: Per-event 60-day pre/post window definitions
- S3: Full topic-restructuring tables (8 events × 7 topics × 5 cohorts)
- S4: Per-author returning-author detail per event
- S5: Cross-instrument operationalization full OR matrix
- S6: SDN attending career-stage subset (small-cell analysis)
- S7: Reproducibility code and data deposit (OSF link)

---

## DRAFTING NOTES FOR PAPER 2

- Voice: CSS-journal formal (JCSS / PLOS One style)
- Lead with **construct-misalignment + base-rate-adjusted lift** framing (NOT CMV/Podsakoff)
- Cite Zhu, Yin & Zhang 2025 prominently in introduction as composition-bias precedent
- Acknowledge comments-scale partial replication caveat in §5.3b (do NOT overclaim that comments confirm posts)
- Submit pre-print to SSRN concurrent with JCSS submission
- Reviewers to suggest: Bestvater (Penn State Polisci), Wang et al. (corresponding author), Hutto (CalPoly), Mohammad (NRC Canada)

**Estimated drafting time: 6-8 weeks of focused writing.**
