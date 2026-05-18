# OSF Pre-Registration — Cross-Domain Replication Study

**Title:** "Cross-Domain Replication of Cohort-Conditional Sentiment-Instrument
Construct Mismatch: COVID-19 Vaccine Discourse"

**Pre-registered date:** [TO BE FILLED ON OSF]
**OSF URL:** [TO BE CREATED at https://osf.io/registries/osf/new]
**Status:** GENUINE pre-registration — analysis NOT yet performed

**This document constitutes a true pre-registration. The COVID-19 vaccine
data has NOT been collected or scored at the time of registration. The
analyses below will be performed exactly as specified after data
collection.**

---

## 1. Background & Motivation

The PSLF discourse paper (under preparation; OSF: [URL of main project])
documents that three commonly-used sentiment instruments (TextBlob, VADER,
Claude Sonnet 4) operationalize substantively different latent constructs
on policy-discourse text, with cohort-conditional disagreement (Krippendorff's
α=−0.018 canonical / +0.196 charitable upper bound on n=9,242 PSLF posts).

**Open question:** Does this construct-mismatch finding generalize beyond
PSLF discourse to other policy domains? Without cross-domain replication,
the finding can be dismissed as PSLF-specific (e.g., due to PSLF-borrower
demographic skew on Reddit/SDN, or to PSLF's idiosyncratic 10-year
forgiveness contingency structure).

**This pre-registration tests the construct-mismatch finding on COVID-19
vaccine discourse**, a domain that:
- Differs in vocabulary (~5% overlap with PSLF)
- Differs in discourse demographics (broader cross-political audience)
- Differs in policy structure (immediate health decision vs delayed
  forgiveness)
- Has been most extensively validated for VADER (Hutto & Gilbert 2014 was
  trained on tweets, the dominant medium)

If the construct-mismatch finding holds in COVID-vaccine discourse where
VADER should work best, the methods finding generalizes to policy discourse
broadly.

---

## 2. Hypotheses (PRE-SPECIFIED)

### H1 (Replication of primary methods finding)
**Three-rater Krippendorff's α** (TextBlob × VADER × Claude Sonnet 4 on
`vaccine_sentiment` zero-shot) on n≥5,000 COVID-vaccine posts will be
**<0.4** (well below the 0.667 reliability floor; Krippendorff 1980).

### H2 (Lead exemplar finding)
**At least 1 of 5 pre-specified policy events** will produce directionally-
opposite Hedges' g across the three instruments at n≥500 per cell:

| Event | Date |
|---|---|
| FDA EUA Pfizer | 2020-12-11 |
| FDA full approval Pfizer | 2021-08-23 |
| Biden Vaccine Mandate (EO 14043) | 2021-09-09 |
| SCOTUS strikes mandate | 2022-01-13 |
| Bivalent Booster authorization | 2022-08-31 |

### H3 (Cohort heterogeneity replication)
**Direction-split events will be observed in COVID-vaccine discourse across at
least one cohort pair**, mirroring the SDN-Medical vs Reddit r/PSLF
heterogeneity in PSLF.

### H4 (Construct claim — instrument prediction)
The instrument that disagrees most strongly will be **domain-dependent**.
Pre-specified prediction for COVID-vaccine:
- VADER (expressive arousal) will pick up high-arousal anti-vax language
- TextBlob (lexical) will register lower polarity for technical content
- Claude (stance) will code "neutral informational" where the others see
  emotional content

---

## 3. Data Collection Plan (PRE-SPECIFIED)

### Source
- **Platform:** Reddit (Arctic Shift archive)
- **Subreddits:**
  - r/Coronavirus
  - r/CovIDvaccinated
  - r/conspiracy
  - r/Medicine
  - r/Nursing
  - r/news (control)
- **Date range:** 2020-01-01 to 2023-12-31

### PSLF-equivalent COVID-vaccine filter (pre-specified anchored regex)
```
("vaccine" OR "vax" OR "vaccinated" OR "vaccination" OR "booster")
AND ("covid" OR "coronavirus" OR "moderna" OR "pfizer" OR
     "j&j" OR "jnj" OR "astrazeneca" OR "novavax")
```
Co-occurrence within 80 characters required (mirrors `filter_pslf_relevant`
pattern).

### Sampling
**Stratified sample:**
- Strata: cohort × year × quarter
- n=400 per stratum
- 5 cohorts × 4 years × 4 quarters = 80 strata
- Target n: ~10,000 posts (allowing for some strata to be under-populated)

### Inclusion/exclusion criteria
- Inclusion: vaccine-anchored per filter above
- Exclusion: wc<20; deletion-marker posts; duplicate post_id; non-English
- No exclusions added post-data-collection

---

## 4. Scoring Plan (PRE-SPECIFIED)

### Three sentiment instruments
Identical to PSLF protocol:
- TextBlob (v0.18.0, polarity score)
- VADER (v3.3.2, compound score)
- Claude Sonnet 4 (claude-sonnet-4-20250514) at temperature=0 (per Round 7
  fix)

### Claude prompt structure
Adapted from PSLF prompt:

```
You are a sentiment analysis expert specializing in COVID-19 vaccine
discussions.

For each post, classify:

1. vaccine_sentiment: poster's sentiment TOWARD COVID-19 vaccines
   (very_negative, negative, neutral, positive, very_positive)

2. primary_topic:
   - efficacy: discussion of how well vaccines work
   - safety: side effects, adverse events, long-term concerns
   - mandate: vaccine requirements, employer mandates, government action
   - access: distribution, scheduling, eligibility
   - conspiracy: misinformation, conspiracy theories
   - personal_decision: poster's own vaccine decision
   - general_question: basic information-seeking

3. vaccine_stance: uptaking, considering, rejecting, already_received,
   unknown

Respond ONLY with valid JSON: {"vaccine_sentiment": "...",
"primary_topic": "...", "vaccine_stance": "..."}
```

### Test-retest reliability
Re-score n=200 posts at temperature=0 on a separate day to compute Claude
test-retest Krippendorff α (mirrors PSLF Round 7 protocol; expected α>0.85).

---

## 5. Analysis Plan (PRE-SPECIFIED)

### 5.1 Primary test (H1)

Three-rater Krippendorff α on the full n≥5,000 sample:
- Canonical: fixed thresholds (TextBlob/VADER cuts at [−0.5, −0.05, +0.05,
  +0.5] mapped to ordinal {0,1,2,3,4})
- Charitable upper bound: percentile-matched ordinal (forces equal-frequency
  quintiles)

**95% bootstrap CI:** stratified bootstrap by cohort, B=2,000 iterations
(Hayes & Krippendorff 2007 method).

### 5.2 Secondary test (H2)

For each of the 5 pre-specified events × ±60-day window:
- Hedges' g per instrument (TB, VADER, Claude)
- Borenstein et al. (2009) variance with J² correction
- Block-permutation p (Bickel et al. 1989, B=2,000, per-event seed)
- Holm-Bonferroni step-down (family α=0.05 across 5 events)

### 5.3 Cohort heterogeneity (H3)

Per (cohort, event) cell with n≥30 pre AND n≥30 post:
- Direction concordance test (TB sign × VADER sign × Claude sign)
- Direction-split flag if ≥1 instrument disagrees on sign with the others
- Pre-registered threshold: ≥1 direction-split event ⇒ H3 confirmed

### 5.4 Instrument prediction (H4)

Compute per-event Hedges' g per instrument; rank instruments by which has
largest absolute g per event. Pre-registered prediction (H4):
- VADER will have largest |g| in 3 of 5 events (high-arousal anti-vax
  language)
- TextBlob will have smallest |g| in 3 of 5 events (technical content
  flattens polarity)

---

## 6. Stop Rules (PRE-SPECIFIED)

- **If H1 succeeds (α<0.4):** combine PSLF + COVID into single methods
  paper, framed as "construct disagreement on policy discourse — evidence
  from two domains"
- **If H1 fails (α≥0.4):** publish PSLF-only methods paper with COVID
  null-result section, framed as "PSLF-specific construct disagreement
  with explanation for cross-domain non-replication"

---

## 7. Variables We Will Measure

| Variable | Type | Source |
|---|---|---|
| `post_id` | string | Reddit (Arctic Shift) |
| `subreddit` | string | Reddit |
| `created_utc` | datetime | Reddit |
| `body` | string (text) | Reddit |
| `polarity_tb` | float [-1, 1] | TextBlob |
| `compound_vader` | float [-1, 1] | VADER |
| `vaccine_sentiment` | ordinal {0..4} | Claude Sonnet 4 |
| `primary_topic` | categorical | Claude Sonnet 4 |
| `vaccine_stance` | categorical | Claude Sonnet 4 |
| `cohort` | categorical | derived from subreddit |
| `event_window` | string | derived from created_utc |

---

## 8. Sensitivity Analyses (PRE-SPECIFIED)

These will be run regardless of primary results:

1. **Excluding r/conspiracy:** does H1 still hold?
2. **Sample-size robustness:** rerun with random subsamples of n=2K, 5K, 10K
3. **Test-retest robustness:** does Claude give same Krippendorff α at
   temperature=0 vs temperature=1?
4. **Placebo test:** non-vaccine COVID posts (mention COVID but not vaccines)
   should show similar α — if NOT, the instrument disagreement is
   vaccine-specific within COVID

---

## 9. Multiple Comparisons Correction

- Family of tests: 5 events × 3 instruments = 15 effect-size estimates +
  H1, H2, H3, H4 = 4 hypotheses
- **Pre-specified correction:** Holm-Bonferroni step-down at family α=0.05
  for the 5 event-window tests; H1-H4 evaluated independently at α=0.05

---

## 10. Computing Resources & Cost

- Claude scoring: ~10,000 posts × $0.005 = ~$50
- Open-weight LLM replication: ~$5 (Llama 3 via Together AI)
- TextBlob + VADER: free
- Reddit data via Arctic Shift: free
- Computing: local laptop

---

## 11. Personnel & Timeline

- **Pre-registration submitted:** [DATE TBD]
- **Data collection:** Q3 2026 (~2 weeks)
- **Scoring:** Q3 2026 (~3-5 days)
- **Analysis:** Q4 2026 (~1-2 weeks)
- **Manuscript draft:** Q4 2026 (~4 weeks)
- **Total estimated:** 2-3 months from registration to draft

---

## 12. Funding & Conflicts

- Funding: [None / personal / specify]
- Conflicts: None
- Compute: $50 expected

---

## 13. Versioning & Updates

This pre-registration is version 1.0. Material changes will be amended via
OSF amendment process with rationale. Minor changes (e.g., sample-size
adjustments due to data availability) will be documented but not require
amendment.

---

## 14. References

- Bestvater & Monroe (2023), Political Analysis 31(2):235-256
- Hayes & Krippendorff (2007), Communication Methods and Measures 1(1):77-89
- Hutto & Gilbert (2014), ICWSM Proceedings (VADER)
- Krippendorff (1980), Content Analysis: An Introduction to its Methodology
- Mohammad et al. (2016), SemEval-2016 Task 6 (stance task definition)
- Borenstein et al. (2009), Introduction to Meta-Analysis
- Bickel et al. (1989), International Statistical Review (block permutation)

---

## 15. Acknowledgments

Pre-registration template adapted from OSF Standard Pre-Registration
template (https://osf.io/preprints/metaarxiv/9rzfk/).
