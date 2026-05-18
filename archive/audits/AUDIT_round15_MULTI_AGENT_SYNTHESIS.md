# Audit Round 15 — Multi-Agent Adversarial Synthesis (2026-05-10)

Three parallel adversarial audits, one per paper. Each agent independently read the actual data, scripts, and outline. Each was instructed to be brutally honest. **The findings are substantially worse than my earlier estimates, and they identify real bugs and real overclaims.**

---

## Acceptance probability revisions (the headline)

| Paper | Venue | Original Round-14 estimate | Round-15 honest estimate (current state) | After all critical fixes |
|---|---|---|---|---|
| P1 Methods | EPJ Data Science | 40-50% | **25-35%** | 50-60% |
| P2 Substantive | JCSS | 35-45% | **20-30%** | 35-40% |
| P3 Policy | JAMA Health Forum | 25-35% | **8-15%** | (need to re-route to JGME or AcadMed) |

**Bottom line: All three papers need substantial work before submission. Two have outright bugs or misrepresentations.**

---

## PAPER 1 (Methods, EPJ DS) — 6 critical issues

### C1. **The n=701 multi-LLM intersection contains 0 SDN posts** — BLOCKER

The outline §3.5 claims the n=701 intersection is "weighted by cohort to ensure each of the five cohorts contributes ≥40 posts." The actual file (`zeroshot_reddit_n1000.csv`) contains:
- **0 SDN posts** (the cohort with the strongest construct dissociation in prior rounds)
- **27 r/PSLF posts** (below the claimed ≥40 floor)
- **32 r/StudentLoans posts** (below the floor)

Bulk is profession-subreddit posts. **The "cohort-balanced" claim is a misrepresentation that any reviewer pulling the OSF data will catch in 5 minutes.**

**Fix:** Re-score n=1500-2000 with proper SDN inclusion (~$30, 1 hour).

### C2. **Test-retest 100% exact-match measures API determinism, not test-retest reliability** — HIGH

When the same prompt + temperature=0 + post is sent twice to Claude API, 100% match is the expected null for an idempotent deterministic decoder. The "LLM-stochasticity" objection that matters is: does the classification depend on prompt phrasing, post truncation, examplar order? None of those are tested.

**Fix:** Add paraphrase-robustness test (re-prompt with 2-3 alternative system-prompt phrasings, compute α across phrasings). ~$5.

### C3. **Binning asymmetry hides much worse LLM-vs-lexical agreement** — HIGH

The script uses `pd.qcut` (quintile rank) for TextBlob/VADER → 20% per bin floor. Under canonical fixed thresholds, the actual exact-match values are:
- LLM × VADER: **6.8-9.0%** (script reports 21.8-22.4% under qcut)
- LLM × TextBlob: 40-44% (script reports 20.1-21.7% under qcut)

The outline §4.3 says both will be reported but the headline tables only show qcut.

**Fix:** Report both binning schemes for all pairwise α and exact-match values.

### C4. **3-LLM K-α=+0.7211 is BELOW Krippendorff's 0.80 floor** — "substantial" framing is overclaim

Krippendorff (1980): α≥0.667 = "tentative reliability only"; α≥0.80 = "satisfactory reliability." Landis & Koch (1977): κ=0.57-0.59 is "moderate" not "substantial."

The honest claim is **"LLMs achieve only tentative-reliability levels of agreement among themselves; lexicons agree with LLMs at well below tentative levels."** This is still defensible but weaker than the outline's framing.

### C5. **OP-vs-Reply "no published precedent" claim is WRONG** — likely embarrassing in review

The audit found multiple precedents the outline missed:
- **Tsugawa & Ohsaki (2015)** — Twitter cascades, sentiment in replies
- **Choi et al. (2020) PNAS** — sentiment shifts in Reddit conversational chains
- **Hwang et al. (2017)** — sentiment shifts in social-support forums (OP vs comment)
- **Wang et al. (2023) ICWSM** — sentiment polarity shifts in conversational threads
- **Park, Kim, & Lee (2023, JCS)** — TextBlob-VADER divergence in Reddit comments

Also: TB Δ=−0.017 is essentially zero. The "directionally opposite" framing is technically true but the TB effect is barely distinguishable from noise.

### C6. **Construct labels ("LLM=stance, lexicon=affect") are unvalidated assertions** — HIGH for psychometric reviewers

No human-coded gold standard for stance or affect on this corpus. The Campbell-Fiske multitrait-multimethod framework you invoke requires identified constructs.

**Fix:** Either hand-code n=200-300 posts for stance + sentiment validation set (~1 week of work), OR rephrase throughout as "tentative interpretation; rigorous validation remains for future work" and drop the Campbell-Fiske framework.

### M1 (also concerning): **Claude scored at temp=1 (default), Llama+DeepSeek at temp=0** — asymmetric design

The Claude scoring file (`zeroshot_reddit_n1000.csv`) was likely generated WITHOUT `--temperature 0` (default = 1.0). This biases against Claude and underestimates inter-LLM agreement. Re-scoring at temp=0 would likely raise 3-LLM α from +0.72 to +0.74-0.76.

---

## PAPER 2 (Substantive, JCSS) — 5 critical issues

### C1. **r/PSLF coupling pattern is NOT cross-instrument robust — outline misrepresents the data** — BLOCKER

The l5_cohort_robustness_results.txt artifact says: "Cohorts with CONCORDANT direction across all instrument choices: 1/5" — and only **SDN-Medical** is in that list. r/PSLF gives 4 OR>1 / 1 OR<1 across 5 specifications and is explicitly tagged **"DISCORDANT"**. The outline claims "two robust patterns"; the actual data show "one robust pattern."

**This is the single biggest substantive overclaim across all three papers.**

**Fix:** Reframe as "1 of 5 cohorts shows fully cross-instrument-concordant coupling (SDN-Medical decoupling); 4 of 5 show direction sensitivity to operationalization choice — which is itself the substantive finding."

### C2. **CMV claim for Reddit Finance is mis-framed** — Podsakoff CMV doesn't apply

The Reddit Finance OR=0.18 → 1.10/1.42 sign-flip is **most plausibly a sample-selection artifact**: TB and VADER identify a different subset of posts as "negative" than Claude does. Podsakoff CMV requires shared method variance inflating bivariate correlations between two measures of the same units; here the two measures partition the data differently.

**Fix:** Reframe as "instrument-conditional sample-selection" or "construct misalignment between TB's lexical-affect target and Claude's stance-derived sentiment target." Drop the Podsakoff lineage from lead methodological framing; demote to a "see also" reference.

### C3. **85.6% sentiment-stance decoupling is partly tautological**

The intention_results.txt cross-tab shows 0% rejecting in BOTH positive and very_positive cells (n=2,006 + n=354 = 2,360 posts). This is structurally empty — likely a hard-coded prompt constraint where Claude refuses to call a "positive" post "rejecting." The decoupling claim depends on the off-diagonal cells being substantially populated.

Compounded by base-rate issues: r/PSLF is **92.2% pursuing-or-completed** by Claude — almost any sentiment in r/PSLF is going to overlap with "still pursuing" mathematically.

**Fix:** Compute base-rate-adjusted statistics (deviation from cohort marginal pursuing rate). Investigate the structural empty cells.

### C4. **Within-person Trump EO finding (n=13) is statistically meaningless** — should not be reported as "feasible"

n=13, McNemar p=0.625, 95% CI on Δrejecting = **[−16.7, +50.0]** (67-pp wide).

**Fix:** Drop n≥10 threshold. Reframe ALL eight events as "infeasible by design" — CIs range from 25 pp to 67 pp.

### C5. **"Composition-immune" topic restructuring contradicts floor-effect investigation**

§5.4 claims topic restructuring is composition-immune. floor_effect_investigation.txt shows topic mix shifts WITH poster turnover — pre-rule rejecting authors who posted about career_impact were entirely replaced post-rule by new authors who posted about policy_uncertainty. The topic distribution shift IS a composition shift.

**Fix:** Drop the "composition-immune" claim or run a within-author topic-distribution test (likely infeasible given small returning-author counts).

### M1 (critical): **Comments-scale data CONTRADICTS the cohort heterogeneity story for the lead exemplar**

cohort_heterogeneity_comments_results.txt at comments scale shows Trump PSLF EO **CONCORDANT — all 5 cohorts negative**. The post-level finding of cohort heterogeneity FAILS to replicate at 50× scale for the lead event. The outline's "headline strengthened by 50× scale replication" claim is false.

---

## PAPER 3 (Policy, JAMA HF) — 7 critical issues including 1 BUG

### C1. **Sample-size inflation BUG — n=32,612 > 30,763 NRMP rows is structurally impossible** — BUG

`institutional_confounders.csv` contains 7 institutions with **duplicate rows** (Mayo Clinic appears 3×, identical content; St Vincents, St Francis Med Ctr, others appear 2×). The merge in `run_model5_with_confounders.py:84-89` is many-to-one and silently duplicates Mayo's program-year rows 3× — explains the +1,849 row inflation from M4 (n=29,461) to M5 (n=32,612).

**Fix:** Add `.drop_duplicates(subset='institution')` after the merge in `build_institutional_confounders.py:234`. Re-run M5; expect coefficient to move slightly and t-stat to decrease ~3%.

### C2. **No cluster-robust SEs — t-stat is artificially inflated** — SEVERE

Only 23 unique hostile institutions generate 763 program-years (~33 obs/cluster). HCA Florida JFK + HCA Healthcare KC alone account for 53% of hostile observations. Within-institution fill-rate variance is dramatic (HCA KC 95.3% vs HCA-USF Citrus 21.4%). With ICC ≈ 0.4 and n̄=33, design effect ≈ 13.8 → **effective n_hostile ~ 55, not 763.**

The reported HC3 SE of 1.63 (t=−11.2, p=4.2×10⁻²⁹) **dramatically overstates precision**. Cluster-robust SE would inflate SE by 3-4× → 95% CI more like [−25, −12], p-value many orders of magnitude larger.

**Fix:** Refit with `cov_type="cluster"` clustered on institution. With only 23 hostile clusters, also report wild-cluster bootstrap p-value (Cameron-Miller 2015 recommend for <30 clusters).

### C3. **PSLF-hostile classification is conceptually WRONG for HCA-academic partnerships** — could destroy headline

Of 22 hostile institutions:
- **9 are HCA/USF Morsani partnerships** (USF is a public university, PSLF-eligible)
- **1 HCA-UMiami partnership** (UMiami is 501c3)
- **1 HCA-U Houston partnership**
- **1 HCA-VCOM partnership** (VCOM is 501c3 osteopathic)

PSLF eligibility depends on the **W-2 employer of the resident**, not the parent corporation of the host hospital. At academic-partnered HCA programs, residents are commonly employed by the academic partner (PSLF-eligible). Variance in fill rates across "hostile" institutions corroborates this — HCA-USF Citrus 21.4% vs HCA Healthcare KC 95.3%.

**The "hostile" label conflates fundamentally different employment structures.** A reviewer will ask: "Have the authors verified PSLF eligibility from the actual W-2 employer of residents?" The answer is no.

**Fix options:**
(a) Reclassify HCA-academic partnerships as **ambiguous** rather than hostile, re-run M5
(b) Run analysis only on unambiguous-hostile subset (smaller n)
(c) Acknowledge limitation explicitly

### C4. **Negative control orthopedic surgery is underpowered**

n=21 PSLF-hostile from only 4 unique institutions (3 of which are HCA-academic per C3). SE=0.60, MDE at 80% power ≈ 1.7 pp. The "null" β=+0.67 (95% CI [−0.50, +1.85]) does NOT rule out a uniform-recruitment confound of moderate size; only confounds as large as 18 pp.

The paper claim "this rules out uniform recruitment confound" is overstated.

### C5. **Within-institution DiD is not informative** — addresses adversarial angle #8

n=7 hostile institutions in BOTH eras. Within-institution DiD interpreting "non-significant" as "treatment effect ruled out" with such small n is interpreting failure-to-reject as positive evidence. Power to detect a 10 pp treatment effect is <30% at this n.

### C6. **Robustness ladder is INVERTED — 0.55 pp shrinkage is BAD news, not good** — SEVERE conceptual error

The outline frames "0.55 pp total shrinkage M1 → M5+NIH" as evidence the headline is **robust to confounders**. The audit reads it the opposite way: 0.55 pp shrinkage means **the confounders we measured do not vary across the PSLF-class contrast**.

PSLF-class is defined at the institution level; the confounders are also at the institution level. Hostile institutions are by construction non-university, non-AMC, low-NIH. Once the hostile dummy is in the model, the other institution-level confounders have nothing to explain about the hostile-vs-rest contrast.

**The honest interpretation: Observable measured covariates do not explain the differential. Unobserved institution-level factors that vary at the same level as PSLF classification could still explain it.**

### C7. **University affiliation flag is internally inconsistent** — multiple verified false negatives

The classifier should flag "Loyola Univ Med Ctr" True (contains "univ") but flags it False. Other false negatives: George Washington Univ, Howard Univ Hosp, MedStar Georgetown Univ Hosp, NYP-Columbia Univ Med Ctr, Northwestern McGaw/Lurie Childrens.

**This means the 153 True / 644 False classification has meaningful errors that distort M5 coefficient estimates.**

### C8 (also concerning): **Pre-2020 baseline framing is dodge, not honest**

2016 gap = **−5.92 pp** (hostile filled HIGHER), 2017 gap = +1.27 pp, 2020 gap = +15.63 pp. The pattern is consistent with the differential **emerging around 2020-2021, not a stable structural feature**.

**Fix:** Drop structural-vs-treatment framing entirely. State: "We document a 2020-2025 cross-sectional differential. The mechanism (long-standing structural difference vs treatment effect of PSLF salience increases) cannot be identified with this design and sample."

### C9. **JAMA Health Forum venue fit is BORDERLINE** — desk-reject risk ~25-30%

JAMA HF publishes ACA evaluations, drug pricing, value-based payment, telehealth, COVID workforce — NOT GME match dynamics. Workforce papers focus on hospitalist staffing, NP/PA scope-of-practice, not residency-program-level differential analyses.

**Fix:** Submit to **Journal of Graduate Medical Education** (best fit, 25-35% acceptance) or **Academic Medicine** (better fit, 20-30%) first. JAMA HF should be the second-choice venue.

---

## What this means for Path B

**The 14 prior audit rounds were addressing the wrong objections.** Round 15 is the first that:
- Verified data composition against outline claims (caught Paper 1 SDN-omitted intersection, Paper 2 r/PSLF mis-categorization)
- Verified script outputs against headline (caught Paper 3 sample-size inflation bug)
- Computed alternative binning schemes (caught Paper 1 LLM-VADER 7% vs 22% exact-match)
- Tested the conceptual logic of the audit fixes (caught Paper 3 robustness-ladder inverted interpretation, negative control underpower)
- Searched literature with critical attention (caught Paper 1 "no precedent" claim wrong)

**Concrete impact on Path B timeline:**

| Item | Old plan | Round 15 reality |
|---|---|---|
| Paper 1 ready to draft | Now (after comments) | **2-4 weeks** of fixes (re-scoring with SDN inclusion, paraphrase-robustness, binning report, lit search, validation set, terminology sweep) |
| Paper 2 ready to draft | After comments collector | **3-4 weeks** (cohort-claim rewrite, CMV reframe, base-rate adjustment, drop n=13 framing, resolve composition-immune contradiction) |
| Paper 3 ready to draft | Now (results locked) | **4-6 weeks** (fix duplicate-row bug, cluster-robust SE, HCA-academic reclassification, fix university classifier, drop robustness-ladder framing, switch venue) |

**Realistic submission timeline now:**
- Paper 1: Q4 2026 (was Q3 2026)
- Paper 2: Q1 2027 (was Q4 2026)
- Paper 3: Q1-Q2 2027 (similar; venue change to JGME)

---

## Triage: which fixes are highest-value?

**Highest impact (must do; will determine acceptance):**

1. **Paper 3 C1: Fix the duplicate-row bug.** This is a 30-minute code fix. Should be done immediately. Re-run all M5 specifications.

2. **Paper 3 C2: Cluster-robust SEs.** ~30 minutes. Will move t-stat from −11.2 (suspicious) to ~−4 to −7 (defensible). Report both wild-cluster bootstrap p and HC3 in supplement.

3. **Paper 3 C3: HCA-academic reclassification.** ~2 hours of manual classification + sensitivity rerun. Will likely move headline coefficient from −18.22 pp to somewhere in range −12 to −16 pp depending on choice.

4. **Paper 2 C1: r/PSLF reframe.** Honest reframe of the cohort heterogeneity headline. ~4 hours of outline rewriting.

5. **Paper 1 C1: Re-score with SDN inclusion.** ~$30 + 1 hour. Removes the desk-reject-risk cohort misrepresentation.

**Medium impact (would substantially strengthen):**

6. Paper 1 C5: 6-hour literature search for OP-vs-Reply precedents
7. Paper 1 C6: Hand-code n=200 validation set for construct labels
8. Paper 2 C2: Reframe CMV → construct misalignment (drop Podsakoff)
9. Paper 2 C3: Compute base-rate-adjusted decoupling stats
10. Paper 3 C7: Debug + re-run university affiliation classifier

**Lower impact (polish):**

11. Paper 1 C4: Terminology sweep ("substantial" → "tentative")
12. Paper 1 C2: Paraphrase-robustness test-retest
13. Paper 2 C4: Drop n=13 framing
14. Paper 3 C8: Drop structural-vs-treatment framing
15. Paper 3 C9: Switch venue to JGME or AcadMed

---

## Honest summary for the user

The Round 15 audits found that **all three papers have substantive issues that the prior 14 rounds missed because the prior audits were largely self-audits or one-off agent runs without verifying data against claims**. The new findings include:

- **2 outright errors** (Paper 3 sample-size bug, Paper 1 cohort-balance misrepresentation)
- **1 conceptual inversion** (Paper 3 robustness-ladder framing)
- **3 substantive overclaims** (Paper 2 r/PSLF "robust", Paper 1 "no published precedent", Paper 1 "substantial agreement")
- **2 design weaknesses needing real fixes** (Paper 3 clustering, Paper 1 test-retest design)
- **1 classification noise issue** (Paper 3 university affiliation classifier inconsistencies)

**The papers are not ready to draft as currently structured.** The substantive findings are mostly real (PSLF-hostile differential is large; LLMs do disagree with lexicons; there is cohort heterogeneity for SOME cohorts) but the framing systematically overstates what the data show.

**Recommended next steps:**
1. Fix the duplicate-row bug in Paper 3 immediately (30 min, no-brainer)
2. Add cluster-robust SE to Paper 3 (30 min, removes biggest precision overclaim)
3. Honest rewrite of Paper 2 cohort heterogeneity headline (4 hours)
4. Re-score Paper 1 multi-LLM with SDN inclusion (~$30, 1 hour)
5. Schedule a 2-week revision sprint for Papers 1 and 3 before drafting begins
6. Either accept Paper 2 timeline slipping to Q1 2027, or accept narrower headline

**Path B remains viable but requires honest revision before draft work begins.** Papers that go to peer review with the issues above will get major-revision recommendations at best, reject-and-resubmit at worst.

---

*End of Round 15 multi-agent adversarial synthesis.*
