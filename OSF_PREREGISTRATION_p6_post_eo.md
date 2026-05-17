# OSF Pre-Registration — Paper 6: Post-Trump-EO PSLF Discourse Sentiment

**Title:** *Cohort-conditional sentiment dynamics around PSLF policy events: A pre-registered event-study analysis of five federal student-loan policy interventions in online PSLF discourse, 2023–2026*

**Pre-registered date:** [TO BE FILLED ON OSF — must be on or before any analysis of post-October-31-2025 (Final Rule) data]
**OSF URL:** [TO BE CREATED at https://osf.io/registries/osf/new]
**Status:** GENUINE pre-registration — analysis NOT yet performed for the Final-Rule and post-Final-Rule windows
**Lead author:** [User]
**Created:** 2026-05-17 (R17++ #6 RIGOROUS REVIEW deliverable)

**This document constitutes a true pre-registration for the post-Final-Rule analysis window (October 31, 2025 onwards). The analyses below will be performed exactly as specified after pre-registration is filed at OSF.**

---

## 1. Background & Motivation

The Public Service Loan Forgiveness (PSLF) program has been the subject of substantial federal policy activity in 2023–2026:

| Event | Date | Type |
|---|---|---|
| Biden v. Nebraska SCOTUS oral argument | 2023-02-28 | SCOTUS signal event |
| Biden v. Nebraska SCOTUS ruling | 2023-06-30 | SCOTUS outcome event (struck down $400B forgiveness) |
| SAVE plan introduction | 2023-07-10 | New federal program rollout |
| Federal student-loan payment restart effective date | 2023-10-01 | End of 3.5-year payment pause |
| SAVE plan litigation begins | 2024-03-29 | Adverse court action |
| Trump Executive Order 14235 signed | 2025-03-07 | Executive action (PSLF eligibility revision) |
| ED Final Rule announced | 2025-10-30 | Regulatory finalization |
| ED Final Rule published in Federal Register | 2025-10-31 | Regulatory publication |
| ED Final Rule effective date | 2026-07-01 | Operative date |

This window provides a rare opportunity to study **how online PSLF discourse responds to multiple discrete federal policy interventions** in a relatively short timeframe.

**Open question:** Do discourse-level sentiment shifts in online PSLF communities track policy events in a measurable and pre-specifiable way? Specifically: (a) Are sentiment shifts detectable at the discourse level around the Trump EO 14235 and ED Final Rule events? (b) Do shifts vary by cohort (Reddit r/PSLF vs SDN-Medical vs Reddit Finance vs Reddit r/StudentLoans vs Reddit Medical)? (c) Does the magnitude of discourse response correlate with the magnitude of the policy event?

**Companion papers:** This pre-registration extends the methodology established in Papers 1 (sentiment instrument convergence on PSLF text) and 2 (cohort-conditional sentiment-stance coupling). The R17++ #6 RIGOROUS REVIEW noted that existing cohort heterogeneity comments data already suggests "discourse-as-thermometer" framing may be at risk of falsification (Trump EO produces larger effects than Biden v. Nebraska). This pre-registration **characterizes the events without assuming magnitude scaling**.

---

## 2. Hypotheses (PRE-SPECIFIED)

### H1 (Detectability)
For **at least 2 of 5 policy events**, Hedges' g comparing pre-event (60-day window) to post-event (60-day window) sentiment will exceed |g| = 0.10 in at least one of the 5 cohorts × 3 instruments combinations.

**Pre-specified events:**
- E1: Trump EO 14235 signed (2025-03-07)
- E2: ED Final Rule published in Federal Register (2025-10-31)
- E3: Biden v. Nebraska SCOTUS ruling (2023-06-30)
- E4: Federal payment restart (2023-10-01)
- E5: SAVE plan litigation (2024-03-29)

### H2 (Cohort heterogeneity)
At least 1 of 5 events will produce **directionally-opposite Hedges' g across the 5 cohorts**. (Replicates the cohort-conditional pattern documented in Paper 2 at the post level; tests whether it generalizes to the discourse-event timescale.)

### H3 (Magnitude scaling — TESTED, NOT ASSUMED)
The R17++ #6 RIGOROUS REVIEW noted that existing cohort heterogeneity comments data already suggests Trump EO > Biden v. Nebraska in effect size, opposite of what a simple magnitude-scaling story predicts. **H3 is therefore a test, not an assertion**: regression of |g_event_cohort_instrument| on log(estimated affected borrowers) for each event will yield a slope coefficient that may be positive, negative, or null. **H3 will be reported descriptively, not used as the headline.**

### H4 (Cross-instrument robustness)
For events with |g| > 0.10, the directional sign (positive vs negative shift) will agree across at least 2 of 3 instruments (TextBlob, VADER, Claude Sonnet 4) in at least 1 cohort. If instrument disagreement is widespread, this is a **negative result** that further substantiates Paper 1's cross-instrument construct disagreement finding.

---

## 3. Data Sources (PRE-SPECIFIED)

### 3a. Reddit posts

- **Reddit Arctic Shift PSLF corpus**: ~76,074 PSLF-anchored posts spanning 2010–present
- **Reddit r/StudentLoans expansion**: ~207,353 r/StudentLoans comments (already partially collected per the cohort heterogeneity comments output); additional Arctic Shift pull to extend post-level if needed
- Cohorts: Reddit r/PSLF, Reddit Finance, Reddit r/StudentLoans, Reddit Medical, Reddit PA, Reddit Teaching, Reddit Nursing, Other

### 3b. SDN posts

- **SDN Playwright PSLF corpus**: ~4,749 PSLF-anchored posts
- Cohorts: SDN-Medical (Pre-Allopathic Forum, Medical Student Forum, Resident Forum)

### 3c. Reddit comments

- **Reddit comments corpus**: 528,051 collected, 519,342 with valid TB+VADER scoring

### 3d. Sentiment scoring

Three instruments per post/comment (already computed):
1. TextBlob polarity (-1 to +1)
2. VADER compound (-1 to +1)
3. Claude Sonnet 4 (claude-sonnet-4-20250514) at temperature=0 zero-shot pslf_sentiment (5-level ordinal: very_negative, negative, neutral, positive, very_positive)

### 3e. Stance scoring

Claude Sonnet 4 pslf_stance (5-class nominal: pursuing, considering, rejecting, completed, unknown)

### 3f. Event-date dictionary

See Section 1 table. Final lock date: **filing date of this pre-registration on OSF**.

---

## 4. Statistical Methods (PRE-SPECIFIED)

### 4a. Event-window definition

- **Pre-event window:** 60 days before event date (e.g., for Trump EO 2025-03-07: 2025-01-06 to 2025-03-06)
- **Post-event window:** 60 days after event date (e.g., for Trump EO: 2025-03-08 to 2025-05-07)
- **No-overlap requirement:** events that fall within another event's window are flagged; overlap-aware sensitivity analysis runs each event analysis dropping potentially-overlapping events

### 4b. Primary analysis: Hedges' g per cohort × instrument × event

For each event × cohort × instrument cell:
- Compute mean sentiment in pre-event window
- Compute mean sentiment in post-event window  
- Compute Hedges' g (pooled-SD effect size with small-sample correction)
- Compute cluster-bootstrap 95% CI (B=2,000) on the per-post (Reddit/SDN) means

### 4c. Secondary analysis: Interrupted time series with autocorrelation correction

For each cohort × instrument:
- Weekly aggregation of sentiment scores
- Prais-Winsten ITS with AR(1) errors (or Newey-West with HAC if Prais-Winsten fails to converge)
- Piecewise linear model with breakpoints at the 5 event dates
- Cluster bootstrap (B=2,000) for breakpoint significance

### 4d. Multiple-comparison correction

- 5 events × 5 cohorts × 3 instruments = 75 cells
- **Holm-Bonferroni adjustment** across the 75-cell family for significance claims at α=0.05
- Raw p-values reported alongside adjusted

### 4e. Placebo test (pre-specified falsification)

- **Placebo window:** April 1, 2024 to May 31, 2024 (2 months; no known PSLF policy event in this window)
- Apply the same analysis pipeline as above to the placebo window
- Expected: |g| < 0.10 for all cells under H0 (no event = no shift)
- If placebo window shows significant g, the methodology produces false positives and primary results require qualification

### 4f. Overlap-aware sensitivity

- For each of 5 events, drop the events with overlapping windows and refit
- Report whether the directional conclusion changes

---

## 5. Stop rules + decision criteria (PRE-SPECIFIED)

### 5a. Sufficient data thresholds

For each event × cohort × instrument cell:
- **Minimum n in pre-event window: 30 posts or 100 comments**
- **Minimum n in post-event window: 30 posts or 100 comments**
- Cells failing these thresholds are flagged as **UNDERPOWERED** and excluded from headline H1/H2 claims

### 5b. Falsification triggers

- If placebo test (Section 4e) shows |g| > 0.10 in >25% of cells, the methodology is too sensitive — pre-registered primary results require methods-level disclosure paragraph
- If post-Final-Rule data (Oct 31, 2025+) covers <60 days at the time of analysis lock, the Final-Rule event analysis is reported as **PRELIMINARY** with explicit power-limited language

### 5c. What if H1 is fully null?

A null H1 (no event detectable) is itself an informative finding about discourse sentiment as a policy thermometer. The paper will be submitted with the null result if H1 is falsified, accompanied by explicit discussion of (a) statistical power, (b) instrument choice, (c) cohort selection, (d) borrower-vs-discussant selection bias.

---

## 6. Pre-specified secondary analyses (NOT counted in H1-H4 family)

- Topic distribution shifts (BERTopic on the event-windowed comments) per cohort × event
- Stance distribution shifts (Claude pslf_stance) per cohort × event
- Volume time-series (posts/week, comments/week) per cohort
- CFPB Complaints Database correlation (OPTIONAL — depends on CFPB data availability at analysis time): correlate weekly CFPB complaint volume with weekly discourse sentiment

---

## 7. Reporting (PRE-SPECIFIED)

- Effect sizes (Hedges' g) with cluster-bootstrap 95% CIs reported regardless of significance
- Raw + Holm-Bonferroni adjusted p-values both reported
- Visual: time-series plot of weekly sentiment per cohort × instrument with vertical lines at event dates
- Visual: forest plot of g per cohort per event
- All event × cohort × instrument cell counts reported in a supplementary table

---

## 8. Citation Integrity Commitment

Following the R17 + R17++ + R17++ #2 + R17++ #6 RIGOROUS REVIEW citation integrity protocols of the parent project: every citation in the final manuscript will be independently WebSearch-verified at author level. The R17++ Citation Integrity Log (Notion: 35d1b390-1b2f-811d-b70b-e9826f8f7573) is the project's record-of-truth.

---

## 9. Data Availability + Code Availability

- All data deposited at Dryad/Zenodo with citable DOI (companion to Paper 4 dataset deposit)
- All scripts deposited at GitHub: `https://github.com/zanecn/PSLF-Discussion-Analysis` (commit-pinned)
- Analysis script (TO BE WRITTEN BEFORE FILING THIS PRE-REGISTRATION): `scripts/analyze_post_eo_sentiment_shift.py`

---

## 10. Conflict of Interest + Funding

- [Author affiliations + COI statement TBD]
- [Funding sources TBD]

---

## 11. References (R17++ verified)

- Bernal-Cummins-Gasparrini (2017). Interrupted time series regression for the evaluation of public health interventions: a tutorial. *International Journal of Epidemiology* 46(1):348–355. doi:10.1093/ije/dyw098 — standard ITS methodology reference
- Wagner et al. (2002). Segmented regression analysis of interrupted time series studies in medication use research. *Journal of Clinical Pharmacy and Therapeutics* 27(4):299–309 — ITS pre-period stability guidance
- Hedges (1981). Distribution theory for Glass's estimator of effect size and related estimators. *Journal of Educational Statistics* 6(2):107–128 — effect size methodology
- Cameron, Gelbach & Miller (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics* 90(3):414–427 — cluster bootstrap
- MacKinnon & Webb (2018). The wild bootstrap for few (treated) clusters. *Econometrics Journal* 21(2):114–135 — small-cluster inference
- Hutto & Gilbert (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. *ICWSM* — VADER reference
- Park & Conway (2017). Longitudinal Changes in Psychological States in Online Health Community Members. *JMIR* 19(3):e71. doi:10.2196/jmir.6826 — Reddit longitudinal sentiment methodology
- Companion papers (this project): Paper 1 (Methods, ICWSM/CSCW); Paper 2 (Substantive, Political Analysis primary); Paper 3 (Policy, Health Affairs Scholar / JGME)

---

## 12. Pre-registration filing checklist

- [ ] Author-level verify all references in Section 11
- [ ] Confirm final event-date dictionary (Section 1) is locked
- [ ] Confirm pre-event/post-event window lengths (Section 4a) are locked
- [ ] Confirm Hedges' g + cluster bootstrap pipeline is implemented in `scripts/analyze_post_eo_sentiment_shift.py`
- [ ] Confirm placebo window (Section 4e) is locked
- [ ] Confirm stop rules (Section 5) are locked
- [ ] Upload PDF version of this pre-registration to OSF Registry (https://osf.io/registries/osf/new)
- [ ] Receive OSF DOI; add to this document at top
- [ ] Update Notion P6 page with OSF DOI link
- [ ] **Only after OSF DOI is obtained:** begin post-Final-Rule analytical work

---

*This pre-registration is a deliverable of the R17++ #6 RIGOROUS REVIEW process. Filing this pre-registration BEFORE running the post-Final-Rule analysis is the gating block for Paper 6. Without pre-registration filed before analysis, the pre-registration credit that adds methodological rigor signal is forfeited.*
