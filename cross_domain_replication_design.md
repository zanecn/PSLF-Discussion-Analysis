# Cross-Domain Methods Replication Design

**Purpose**: Defend the methods paper's lead finding (TextBlob ≠ VADER ≠ Claude
on policy-discourse text; Krippendorff's α ≈ 0) against the "PSLF-specific
quirks" critique by replicating in a second policy domain.

**Why required**: Round-7 audit + reviewer-anticipation panel flagged that
the construct-mismatch finding could be dismissed as a quirk of:
- PSLF-borrower discourse demographics (Reddit / SDN skew young, white, male, educated)
- The PSLF policy's idiosyncratic structure (10-year forgiveness contingent on serving
  a "qualifying" employer — invites stance-affect dissociation that may not generalize)
- Word frequency patterns specific to student-debt vocabulary

**Goal**: Replicate the construct dissociation in a second policy domain where:
- Discourse demographics differ
- Policy structure is different (immediate vs delayed; binary vs conditional; etc.)
- Vocabulary is largely non-overlapping with PSLF

If α ≈ 0 holds in the replication, the finding is general to policy discourse.
If α ≥ 0.4 in the replication, it's PSLF-specific and the methods paper must
be reframed as a domain-specific case study.

---

## Candidate Domains (ranked)

### #1: COVID-19 vaccine discourse (RECOMMENDED)
**Why best:**
- Largest available policy-discourse corpus (~50M+ tweets pre-Musk; ~5M Reddit posts)
- Multiple cleanly-dated events: FDA EUA (2020-12-11), full FDA approval (2021-08-23),
  vaccine mandates (Biden EO 2021-09-09), SCOTUS strikes mandate (2022-01-13),
  bivalent booster authorization (2022-08-31)
- VADER has the STRONGEST claim of validity on tweets (Hutto & Gilbert 2014 trained
  on tweets); the construct-mismatch finding is most defensible if it holds where
  VADER should work best
- Cohort heterogeneity available (left-coded vs right-coded subreddits; r/Coronavirus
  vs r/conspiracy; medical professionals via r/Medicine, r/Residency)
- Vocabulary overlap with PSLF: ~5% (mostly sentiment-bearing words like "scam",
  "fraud", "broken")
- Existing scored corpora available (Müller et al. 2020 COVID-Twitter-BERT gives
  comparison ground truth — third anchor)

**Source data:**
- Reddit r/Coronavirus, r/CovIDvaccinated, r/conspiracy, r/Medicine, r/Nursing
  via Arctic Shift (matches our PSLF Reddit data pull infrastructure)
- Twitter: COVID-19 Twitter datasets via Banda et al. 2021 (DOI:10.5281/zenodo.3723940)
  — ~1.4B tweet IDs, hydrate via Hydrator/Twarc
- Pre-existing labeled corpus: COVID-19-Sentiment-Analysis-Dataset (Kaggle) —
  validation against human-labeled gold standard

**Expected effort:**
- Data acquisition: 1-2 weeks (Arctic Shift + Twitter hydration)
- Preprocessing + filter: 3-5 days
- Three-scorer (TB/VADER/Claude): ~$20 Claude on a 10K stratified sample
- Analysis: 1 week (mirror existing PSLF infrastructure)
- Total: ~3-4 weeks

**Estimated total cost:** $20-50

### #2: Inflation Reduction Act / climate discourse
**Why second:**
- Clean event: IRA signed 2022-08-16
- Policy is non-personal (no individual eligibility) — different stake structure
- Discourse is more politically polarized (left/right axis dominates)
- Smaller corpus (~500K-2M relevant Reddit posts)
- VADER less validated here

**Effort:** ~3 weeks
**Cost:** ~$15-30

### #3: SAVE Plan / income-driven repayment
**Why third (SUPPLEMENTARY, not standalone):**
- Same Reddit subs as PSLF (r/StudentLoans, r/personalfinance) — overlapping discourse
- Different policy mechanism (IDR vs forgiveness)
- Useful as a SUPPLEMENT to PSLF (within-author panel feasible) but not a true
  cross-domain replication because of corpus overlap

### #4: Affordable Care Act subsidies / open enrollment
**Why fourth:**
- Annual cycles (cleaner counterfactual)
- Smaller online discourse (~100K relevant posts)
- Personal eligibility makes it similar to PSLF
- Lower power for direction-split detection

---

## Pre-registered design (COVID-vaccine replication)

### Hypotheses

**H1 (replication)**: Three-rater Krippendorff's α (TextBlob × VADER × Claude
Sonnet 4 on `vaccine_sentiment` zero-shot) on n≥5,000 COVID-vaccine posts will be
**< 0.4** (well below the 0.667 reliability floor), replicating the PSLF finding
of α=−0.018 (canonical) / +0.196 (charitable).

**H2 (lead exemplar)**: At least ONE policy event will produce directionally-opposite
Hedges' g across the three instruments at n≥500 per cell, mirroring the Trump PSLF EO
finding (TB g=−0.32, VA g=+0.16, Claude g=+0.33).

**H3 (cohort heterogeneity replication)**: Direction-split events will be observed
in COVID-vaccine discourse across at least one cohort pair (e.g., r/Coronavirus
vs r/conspiracy), mirroring the SDN-Medical vs Reddit r/PSLF heterogeneity in PSLF.

**H4 (construct claim)**: The instrument that disagrees most strongly will be
domain-dependent. PSLF: Claude (stance) ≠ TB (lexical). Prediction for COVID:
VADER (expressive arousal) > TB (lexical) > Claude (stance) — VADER will pick
up high-arousal anti-vax language that TB misses and Claude codes as "neutral
informational."

### Design choices (parallel to PSLF infrastructure)

1. **Data source**: Reddit Arctic Shift for r/Coronavirus, r/CovIDvaccinated,
   r/conspiracy, r/Medicine, r/Nursing, r/news (control). Date range 2020-01-01
   to 2023-12-31.

2. **Filter**: Anchored COVID-vaccine relevance via term list (vaccine + (covid|
   coronavirus|moderna|pfizer|booster|jab|shot|j&j|jnj|astrazeneca)). Mirrors
   `pslf_search_terms.py` pattern.

3. **Sampling**: Stratified sample by (cohort, year, quarter) with n=400 per cell
   for full-corpus Claude scoring (~10K total → ~$50). Matches Path C protocol.

4. **Sentiment prompts**:
   - TextBlob: same `polarity` extraction as PSLF
   - VADER: same `compound` score as PSLF
   - Claude Sonnet 4 zero-shot: 3-dim prompt
     `vaccine_sentiment` (very_negative...very_positive)
     `primary_topic` (efficacy/safety/mandate/access/conspiracy/personal)
     `vaccine_stance` (uptaking/considering/rejecting/already_received/unknown)

5. **Triangulation analysis**: Re-use `sentiment_triangulation.py` with
   COVID-specific adapters (`load_zeroshot()` already supports new subsamples).
   Compute Krippendorff's α with B=2,000 stratified bootstrap CI.

6. **Per-event tests**: 5 events listed above, ±60-day windows, block-permutation
   p-values. Direct port of `gen_legislative_timeline.py`.

7. **Pre-registration**: OSF preregistration BEFORE Claude scoring (so the
   $50 spend is committed to the design, not data-dredged).

### Statistical tests + decision rules

| Test | Threshold | If fails | Action |
|------|-----------|----------|--------|
| H1: α < 0.4 (canonical) | TRUE replicates | Methods finding generalizes | publish methods paper as general |
| H1: α ≥ 0.4 | FALSE replicates | PSLF-specific quirk | reframe methods paper as domain study |
| H2: ≥1 event direction-split | ≥1 of 5 | Lead exemplar generalizes | lead with cross-domain exemplars |
| H3: cohort heterogeneity | ≥1 cohort pair direction-split | Substantive paper generalizes | unlock cross-domain substantive paper |
| H4: instrument-dominant disagreement | varies | Theoretical refinement | discuss in mechanism section |

### Power analysis

- For α detection at n=10K, B=2,000 bootstrap: SE(α) ≈ 0.015. Powered to detect
  α difference of 0.05.
- For per-event Hedges' g at n=500 per cell: 80% power to detect |g|=0.18 at
  α=0.05/5=0.01 (Bonferroni).
- For direction-split detection across 6 cohort pairs: requires ≥1 cohort pair
  with |g_diff|≥0.30 at n_per_cohort≥250. This is the binding constraint.

### Pre-registered deviations / robustness checks

- Test-retest α at temperature=0 on 200 COVID posts (mirrors PSLF round-7 fix)
- Sensitivity excl. r/conspiracy (mirror PSLF SDN-Medical sensitivity)
- Placebo: scoring on a topical-near baseline (COVID non-vaccine posts)
- HC3 robust SEs on length-residualized analysis

---

## Deliverable structure

If replication succeeds (H1: α < 0.4 in COVID), the methods paper restructures:

**Title (revised):** *Stance, Affect, and Arousal: Sentiment Construct Mismatch
in Policy Discourse — Evidence from PSLF and COVID-19 Vaccine Discussions*

**Section 4 (NEW):** Cross-domain replication
  - 4.1 COVID-vaccine corpus
  - 4.2 Triangulation results (α and 95% CI)
  - 4.3 Comparison: which scorer dissociates most?
  - 4.4 Cohort heterogeneity replication (r/Coronavirus vs r/conspiracy)
  - 4.5 Joint test: cross-domain α<0.4 sustained across BOTH corpora

**Venue tier upgrade:**
- Single-domain: PLOS One, EPJ Data Science, Behavior Research Methods (target Tier 2)
- Two-domain: Political Analysis, PNAS Nexus, Sociological Methods & Research (Tier 1)

---

## Recommendation

**Pre-register the COVID-vaccine replication on OSF this week.** Total estimated
cost ~$50, total estimated effort ~3-4 weeks. The cross-domain finding is the
single highest-leverage upgrade for venue tier (single → top-tier methods journals).

If pursuing both PSLF substantive AND methods papers: the methods paper benefits
from this replication; the substantive paper does not require it.

If only pursuing the methods paper: this is now the most important next step
(higher leverage than open-weight LLM replication, which only addresses the
"not just Claude" critique within PSLF).

---

## Pre-registration template (OSF)

```
Title: Cross-domain replication of sentiment construct mismatch in policy discourse

Hypotheses:
  H1: K-α(TB, VADER, Claude) < 0.4 on n≥5,000 COVID-vaccine posts
  H2: ≥1/5 events shows directionally-opposite g across instruments
  H3: ≥1 cohort pair shows direction-split

Design:
  - Pre-existing 9,242-post PSLF corpus = anchor
  - New 10,000-post COVID-vaccine corpus = replication target
  - Identical scoring pipeline (sentiment_zeroshot.py + sentiment_triangulation.py)
  - All analyses pre-specified before scoring

Sample:
  - Stratified by (cohort × year × quarter), n=400 per cell
  - Cohorts: r/Coronavirus, r/CovIDvaccinated, r/conspiracy, r/Medicine, r/Nursing
  - Date range: 2020-01-01 to 2023-12-31
  - Filter: COVID-vaccine anchored term list

Analysis:
  - Three-rater Krippendorff's α (ordinal, percentile-matched)
  - 95% bootstrap CI (B=2,000 stratified)
  - Per-event pre/post Hedges' g (5 events × 5 cohorts)
  - Block-permutation p-values (Bickel et al. 1989)
  - Bonferroni and Holm-Bonferroni step-down adjustments

Stop rules:
  - If H1 succeeds (α<0.4): combine PSLF + COVID into single methods paper
  - If H1 fails (α≥0.4): publish PSLF-only methods paper with COVID null-result section

Confounds to address:
  - Sample composition (Reddit demographics)
  - Event timing (COVID events span pandemic phases — control with quarter FE)
  - Topic mix (efficacy vs safety vs mandate vs conspiracy)
```
