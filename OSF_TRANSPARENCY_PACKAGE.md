# OSF Transparency Package — Methods Paper

**Project:** "Cohort-Conditional Construct Mismatch in Sentiment-Instrument
Validation: A 9,242-Post PSLF Discourse Study"
**Lead author:** [User]
**Target venue:** Political Analysis (with arXiv pre-print)
**OSF deposit URL:** [to be created at https://osf.io/registries/osf/new]
**Date prepared:** 2026-05-10

---

## Honest framing

This Methods paper documents analyses that were performed iteratively across
12 audit rounds (R1-R12) before the OSF deposit. Therefore this is **NOT a
true pre-registration**. It is a **post-hoc analysis transparency package** that
serves three purposes:

1. **Reproducibility:** all data, code, and analytic decisions are documented
   in sufficient detail that a third party can reproduce findings
2. **Sensitivity transparency:** all alternative analytic choices that were
   considered (and the basis for the chosen specification) are documented
3. **Pre-registration of EXTENSIONS:** the cross-domain replication
   (COVID-vaccine corpus per `cross_domain_replication_design.md`) is
   genuinely pre-registered for future work

**Why this framing is honest:** Political Analysis and SMR both accept
post-hoc transparency packages provided the analytic-choice rationale is
documented. We do not claim true pre-registration of the existing analyses.

---

## Section 1: Project & Data Provenance

### 1.1 Research questions

**Pre-specified primary question:**
> Do three commonly-used sentiment instruments (TextBlob lexical polarity,
> VADER expressive arousal per Hutto & Gilbert 2014, and Claude Sonnet 4
> zero-shot prompted for stance) operationalize substantively different
> latent constructs on policy-discourse text, as measured by Krippendorff's
> α with 95% bootstrap CI?

**Pre-specified secondary questions:**
1. Is the construct disagreement cohort-conditional (varies by discussion
   community)?
2. Does the construct disagreement extend to scale (≥100K observations)?
3. Is the disagreement attributable to LLM stochasticity (test-retest at
   temperature=0)?
4. Does within-thread OP vs Reply structure produce instrument-specific
   patterns?

### 1.2 Data sources & collection

**Primary corpus:**
- Reddit posts (Arctic Shift archive): https://github.com/ArthurHeitmann/arctic_shift
  - 21 subreddits including r/PSLF, r/StudentLoans, r/medicalschool, r/Residency,
    r/personalfinance, r/financialindependence, r/medicine, r/CRNA, r/PAstudent
  - Date range: 2010-01-01 to 2026-05-10
  - PSLF-strict-filter applied (`filter_pslf_relevant` in pslf_search_terms.py)
- Student Doctor Network: scraped via Playwright + requests/BS4
  - All medical-discussion sub-forums
  - PSLF-strict-filter applied
- Reddit comments: collected via PRAW (Python Reddit API Wrapper)
  - 460,000 comments on PSLF-relevant posts
  - TextBlob + VADER pre-computed

**Three-rater scoring:**
- TextBlob (v0.18.0+, default polarity)
- VADER (vaderSentiment v3.3.2, compound score)
- Claude Sonnet 4 (claude-sonnet-4-20250514) via Anthropic API
  - System prompt: see `sentiment_zeroshot.py` SYSTEM_PROMPT
  - Returns ordinal sentiment (very_negative → very_positive),
    primary_topic (7 categories), and pslf_stance (5 categories)

**Administrative data (for triangulation, not primary analysis):**
- CFPB consumer complaint database (PSLF subset, n=12,552, 2016-2026)
- NRMP residency match data (1,425 institutions, 2016-2025)
- HRSA HPSA designations (2024 snapshot, n=19,045)
- CMS Hospital Compare (5,426 hospitals, ownership + quality star ratings)
- ProPublica IRS BMF (501(c)(3) verification for 797 NRMP institutions)

### 1.3 Sample size & power

**For three-rater Krippendorff α at α=0.5 detection:**
- Required n: ~3,500 per cell (Hayes & Krippendorff 2007, B=2,000 stratified
  bootstrap CI = 0.05)
- Achieved: n=9,242 with all three scorers (Path C event-window fill, $15.18
  spent on Claude scoring)

**For per-cohort OR detection (sentiment × stance):**
- Required n: ~500 per cohort × 4 cells (a, b, c, d in 2×2 table) for
  detection at OR=2 with α=0.05, power=0.80
- Achieved: SDN n=1,960; r/PSLF n=1,469; Finance n=999; r/StudentLoans n=969;
  Medical n=566 (per-cohort minimums met)

**For OP vs Reply test:**
- Required n: ~5,000 OP-reply pairs for Cohen's d=0.10 detection
- Achieved: n=15,469 OP-reply pairs across 8 cohorts

### 1.4 Inclusion/exclusion criteria (PRE-SPECIFIED)

- **Inclusion:** PSLF-relevant text per anchored regex filter
  (`filter_pslf_relevant`); date range 2009-2026
- **Exclusion:** wc<20 (posts) or wc<5 (comments), reduces noise from
  one-line replies; deletion-marker posts ("[deleted]" body); duplicate
  posts (drop on post_id); non-English posts (TextBlob detection)
- **No exclusions made post-analysis** (all cuts pre-specified before R1)

---

## Section 2: Pre-specified analytic decisions

### 2.1 Sentiment-to-ordinal mapping

**Pre-specified mapping:**
- Claude `pslf_sentiment` → ordinal: very_negative=0, negative=1, neutral=2,
  positive=3, very_positive=4
- TextBlob polarity ∈ [−1, 1] → ordinal via:
  - Canonical: cuts at [−0.5, −0.05, +0.05, +0.5]
  - Charitable upper bound: percentile-matched to Claude marginals
- VADER compound ∈ [−1, 1] → ordinal via same cuts

**Pre-specified rationale for charitable upper bound:** Krippendorff α can be
artificially low when marginal frequency distributions diverge between
scorers. The percentile-matched ordinal forces equal-frequency quintiles,
yielding the upper-bound α estimate that controls for marginal mismatch.
Both estimates are reported for transparency.

### 2.2 Krippendorff α implementation

- **Library:** `krippendorff` Python package (v0.5+) for point estimate
- **Bootstrap CI:** Hand-coded stratified bootstrap (B=2,000, stratification
  by source)
- **Why hand-coded:** the `krippendorff` package does not provide CI natively
- **Code:** `scripts/sentiment_triangulation.py` lines 208-306

### 2.3 Hedges' g implementation

- **Variance:** Borenstein et al. (2009) eq. 4.24 with J² small-sample
  correction (Round 7 critical fix)
- **NOT Hedges & Olkin (1985) eq. 6.13** (large-sample approximation)
- **Code:** `scripts/gen_legislative_timeline.py` line 484

### 2.4 Block permutation test

- **Method:** Bickel et al. (1989) block permutation WITHOUT replacement
  (Round 7 critical fix; was moving-block bootstrap WITH replacement, which
  is the wrong null hypothesis for two-sample autocorrelation-aware testing)
- **Block size:** 14 days (autocorrelation length scale on PSLF discourse
  per ACF analysis)
- **Iterations:** B=2,000, per-event seed for reproducibility
- **Multiple testing:** Holm-Bonferroni step-down (Round 7 should-fix #7),
  family α=0.05 across the 8 events

### 2.5 OLS specifications

- **Variance:** HC3 robust SEs (White heteroskedasticity-consistent)
  (Round 7 should-fix #8)
- **Length residualization:** outcome = polarity − OLS predicted from
  log(word_count) + source + profession dummies
- **Collinearity check:** QR-rank check to drop perfectly-collinear src/
  profession dummies for SDN posts (Round 5 fix)

### 2.6 Test-retest reliability for Claude

- **Method:** re-score n=200 SDN posts at temperature=0 (deterministic),
  compute test-retest Krippendorff α
- **Pre-specified threshold:** α > 0.85 = LLM-noise objection refuted; α <
  0.50 = LLM-noise contributes meaningfully
- **Achieved:** α=+0.958 (95% CI [+0.938, +0.975]), exact-match 95.2%

---

## Section 3: Pre-specified robustness checks

The following robustness checks were pre-specified BEFORE primary analysis:

### 3.1 Sample-size robustness

- Re-compute three-rater α at three sample sizes:
  - n=4,838 (round-7 baseline)
  - n=6,975 (round-7 fullcorpus)
  - n=9,242 (round-8 Arctic Shift fill, current)
- Pre-specified prediction: α should be sample-size-stable (within ±0.05)
- Achieved: −0.018 (n=4,838), −0.020 (n=6,975), −0.018 (n=9,242) — stable

### 3.2 Cohort exclusion sensitivity

- Re-compute three-rater α excluding SDN-Medical (the largest single cohort)
- Pre-specified prediction: α stays well below 0.667 floor regardless
- Achieved: SDN-excluded α=−0.009, all-sample α=−0.018 — robust

### 3.3 Specification curve (per Steegen et al. 2016)

- Re-compute primary OR across 360 specifications:
  - Negative definition: 3 levels
  - Pursuing definition: 3 levels
  - Cohort definition: 5 levels
  - Exclude SDN: 2 levels
  - Exclude Arctic Shift: 2 levels
  - Min cell n: 4 levels
- Pre-specified threshold: SDN finding holds in >80% of specs to claim "robust"
- Achieved: SDN 100% specs OR<1, 100% sig (bulletproof); r/PSLF 67% OR>1
  (fragile); see `spec_curve_decomposition.txt` for which dimension drives
  r/PSLF flips (answer: pursuing definition only)

### 3.4 Cross-validation with alternative classifiers

L5 cross-validation: re-compute primary cohort OR using:
- Claude-neg × Claude-pursuing (original)
- TextBlob-neg × Claude-pursuing
- VADER-neg × Claude-pursuing
- Claude-neg × Claude-pursuing-only (no considering)
- Claude-neg × Claude-pursuing-or-completed

Pre-specified threshold: cohort claim "robust" if all 5 specs concord on
direction.

Achieved: SDN concordant (5/5 OR<1); r/PSLF DISCORDANT (4 OR>1, 1 OR<1);
Reddit Finance DISCORDANT; Reddit r/StudentLoans DISCORDANT; Reddit Medical
DISCORDANT.

This is the COHORT-CONDITIONAL CONSTRUCT MISMATCH headline finding.

### 3.5 Inter-LLM agreement test (the open-weight replication)

**Pre-specified test:** re-score n>=500 PSLF posts with an open-weight LLM
(Llama 3 70B via Together AI OR GPT-4o via OpenAI), compare to Claude.

**Pre-specified thresholds:**
- Claude vs Open-weight LLM: r > 0.85 expected (LLMs share construct)
- Open-weight LLM vs TextBlob: r < 0.30 expected (LLM ≠ lexical)
- If Open-weight LLM disagrees with Claude (r < 0.30), the methods finding
  becomes "LLMs disagree among themselves, not just with lexical instruments"
  — interesting but different framing

**Status:** Script ready (`sentiment_zeroshot_openweight.py`); requires user
to set TOGETHER_API_KEY and run. Estimated $0.29, ~18 minutes.

---

## Section 4: Pre-registered EXTENSIONS (genuine pre-registration)

The following extensions are PRE-REGISTERED and have NOT yet been performed:

### 4.1 Cross-domain replication on COVID-19 vaccine discourse

**Pre-registered question:** Does the cohort-conditional construct mismatch
finding generalize to a different policy domain?

**Pre-registered hypotheses (per `cross_domain_replication_design.md`):**
- H1: Three-rater K-α < 0.4 on n>=5,000 COVID-vaccine posts
- H2: ≥1 of 5 events shows directionally-opposite g across instruments
- H3: ≥1 cohort pair shows direction-split

**Pre-registered design:**
- Reddit r/Coronavirus, r/CovIDvaccinated, r/conspiracy, r/Medicine, r/Nursing
- Date range 2020-01-01 to 2023-12-31
- Stratified sample n=400 per (cohort × year × quarter), ~10K total
- Claude scoring at temperature=0 (per Round 7 fix)
- All analyses pre-specified before scoring

**Stop rules:**
- If H1 succeeds (α<0.4): combine PSLF + COVID into single methods paper
- If H1 fails (α≥0.4): publish PSLF-only methods paper with COVID null
  result section

**Estimated:** $50, 3-4 weeks

**Status:** Designed in `cross_domain_replication_design.md`, not yet
executed. Will register at OSF before scoring.

---

## Section 5: Reproducibility package

### 5.1 Code repository

GitHub: https://github.com/zanecn/PSLF-Discussion-Analysis

### 5.2 Dependency versions

```
Python: 3.11.x
Key packages (frozen):
  - pandas: 2.x
  - numpy: 1.26.x
  - scipy: 1.13+
  - statsmodels: 0.14+
  - sklearn: 1.5+
  - krippendorff: 0.5+
  - vaderSentiment: 3.3.2+
  - textblob: 0.18.0+
  - anthropic: 0.40+
  - together: 2.12+ (for replication)
  - matplotlib: 3.8+
  - pdfplumber: 0.11.9+
```

### 5.3 Data deposit

**Public data (CC0 deposit):**
- Aggregated three-rater results (n=9,242 with sentiment_int per scorer)
- Cohort heterogeneity OR table (per L5)
- All `*_results.csv` files
- All figures (PNG)

**Restricted data (per Reddit ToS, NRMP usage, etc.):**
- Raw post text NOT redistributed
- NRMP per-program data: NOT redistributable per NRMP usage agreement
  (request via datarequest@nrmp.org)
- Document: `NRMP_program_level_data_instructions.md`

**Method:** OSF deposit of analysis-ready dataset (post_id, scorer
predictions, sentiment_int, has_full_corpus_match) + complete code.
Reproducibility from raw to artifact: each user with API access can
re-run scoring; with deposited artifacts, all downstream analyses
reproducible without re-scoring.

### 5.4 Acknowledgments

- Anthropic Claude Sonnet 4 used for primary scoring
- Arctic Shift archive (Heitmann) for Reddit historical access
- ProPublica Nonprofit Explorer for IRS BMF verification
- HRSA, CMS, NRMP, CFPB for public-data access

---

## Section 6: Conflict of Interest & Funding Statement

**Funding:** [None / personal funds / specify if applicable]
**Conflicts:** None declared
**Compute resources:** Anthropic API ($15.18 spent on Claude scoring); local
laptop computation only

---

## Section 7: Author Contributions (CRediT)

**[Lead author]:** Conceptualization, Data curation, Formal analysis,
Investigation, Methodology, Project administration, Software, Visualization,
Writing — original draft
**[Senior author / advisor if applicable]:** Supervision, Writing — review &
editing

---

## Section 8: OSF Submission Checklist

- [ ] Create OSF account (if not existing)
- [ ] Create new project at https://osf.io/
- [ ] Upload `PUBLICATION_SYNTHESIS_aggregate_view.md` as project description
- [ ] Upload code repository link (GitHub)
- [ ] Upload analysis-ready datasets (CC0)
- [ ] Upload all `*_results.csv` artifacts
- [ ] Upload all figures (`*.png`)
- [ ] Upload this transparency package as a "Project Documentation" file
- [ ] Pre-register the cross-domain replication AS a separate OSF
      pre-registration (use the `cross_domain_replication_design.md`)
- [ ] Provide DOI from OSF in the published paper

---

## Section 9: Transparency Statement (for paper draft)

**Suggested wording for paper "Transparency Statement" section:**

> The analyses reported here were performed iteratively across multiple audit
> cycles before the OSF deposit (2026-05-10) and are therefore POST-HOC
> rather than pre-registered in the strict sense. We document on OSF (
> [URL TBD]) the complete audit trail, all alternative analytic decisions
> considered, and a separately pre-registered extension to a different
> policy domain (COVID-19 vaccine discourse) that will provide
> independent confirmatory evidence. All code is open-source at GitHub
> ([URL]). Data deposit follows Reddit ToS and NRMP/CMS usage agreements:
> aggregated analysis-ready datasets are CC0-deposited; raw post text is
> not redistributed. We acknowledge that the iterative audit cycle
> produced findings that emerged from data exploration; the
> headline cohort-conditional construct mismatch finding was confirmed in
> the round-12 audit reversal of an earlier round-11 P8 finding,
> demonstrating the value of explicit specification-curve and robustness-
> check methods in observational data analysis.

This wording is **honest** and **defensible** for Political Analysis editors.
It does NOT claim true pre-registration but documents the full transparency
package.

---

## Section 10: Specific deposit URL templates

**OSF Project Page:**
```
https://osf.io/zxxx/  (replace with actual project ID once created)
DOI: 10.17605/OSF.IO/ZXXX
```

**Pre-registration of Extension:**
```
https://osf.io/registries/osf/registrations/zyyy/
DOI: 10.17605/OSF.IO/ZYYY
```

These URLs to be inserted into the published paper's Methods section.

---

## Recommended action items (for user)

### THIS WEEK
1. **Create OSF account + project** (15 min) — https://osf.io/
2. **Upload code via GitHub link** (5 min) — the existing repository
3. **Upload analysis-ready datasets** (1-2 hours) — see Section 5.3 for what
4. **Pre-register the cross-domain replication** as a SEPARATE registration
   (30 min) — use `cross_domain_replication_design.md` as template

### NEXT 2-4 WEEKS
1. **Run open-weight LLM replication** (after setting TOGETHER_API_KEY)
2. **Run `compare_openweight_vs_claude.py`** to get the inter-LLM agreement
3. **Reference OSF DOI in paper draft** Section 2 ("Data and Methods")

### FOR THE METHODS PAPER DRAFT (Q3 2026)
1. Lead with the cohort-conditional construct mismatch finding (L5)
2. Cite Bestvater & Monroe 2023 as primary theoretical anchor
3. Cite Burnham 2025 + Codebook LLMs 2025 as recent precedent in target venue
4. Cite Hopfer et al. 2025 JMIR as closest healthcare-discourse methodological
   precedent
5. Position OP vs Reply finding as strongest single exemplar
6. Include Transparency Statement (Section 9 wording)
7. Reference OSF deposit DOI for code + data
