# Paper 3 Reframing Analysis (Post-2026-NRMP, Post-Audit)

**Date**: 2026-05-10 (post-audit)
**Trigger**: Round 16 audit found my "Trump-EO eliminated PSLF differential" claim was overstated. 2026 narrowing continues a 5-year pre-existing trend; "extra 2026 effect" beyond trend is statistically indistinguishable from zero (p=0.46).

---

## The honest empirical picture

| Year | n_hostile | Hostile fill | Friendly fill | Gap (pp) | Δ from prior |
|---|---|---|---|---|---|
| 2021 | 129 | 0.7994 | 0.9394 | **−14.00** | (baseline) |
| 2022 | 149 | 0.7767 | 0.9415 | **−16.48** | −2.48 |
| 2023 | 159 | 0.8028 | 0.9346 | **−13.18** | +3.30 |
| 2024 | 159 | 0.8326 | 0.9397 | **−10.71** | +2.47 |
| 2025 | 167 | 0.8356 | 0.9404 | **−10.47** | +0.24 |
| **2026** | **171** | **0.8645** | **0.9348** | **−7.03** | **+3.44** |

**Key facts:**
- Gap has narrowed every year since 2022 (~+1.5 pp/year average)
- Trump EO signed Mar 2025; 2025 ROL deadline was Feb 2025 (pre-EO)
- 2026 narrowing of +3.44 pp is the largest single-year change since 2022→2023
- Linear trend (2021-2025) predicts 2026 gap of −9.12 pp; actual is −7.03 pp; deviation is +2.09 pp (within noise)
- Formal regression: 2026 indicator beyond linear year trend = +2.98 pp, SE=4.05, **p=0.46 (NS)**

---

## Three candidate framings

### Option A: Multi-year trend documentation (CLEANEST)

**Headline**: *"PSLF-Hostile Residency Programs Have Been Closing the Recruitment Gap: A 6-Year (2021-2026) NRMP Program-Year Analysis"*

**Story**:
- For-profit chain residency programs (PSLF-hostile by definition) had ~−14 to −16 pp lower fill rates than university/501(c)(3) programs in 2021-2022
- This gap has narrowed continuously every year since 2022, reaching −7 pp in 2026
- The 2026 narrowing of +3.44 pp is the first post-Trump-EO Match cycle but is statistically indistinguishable from continuation of the pre-existing trend
- Mechanism is unclear: HCA program maturation (5-10 year tenure now), applicant supply-side shifts, secular GME workforce changes, marginal Trump EO contribution all plausible

**Strengths**:
- Honest about what the data show
- Multi-year trend is itself novel and quantitatively documented for the first time
- Doesn't overclaim about Trump EO

**Weaknesses**:
- Less exciting than a "policy-effect" story
- Still requires explaining away the cross-sectional differential (which we cannot identify mechanism for)

**Venue fit**: JGME (best), Academic Medicine (good), JGIM (moderate)
**Acceptance probability**: 35-42% at JGME

### Option B: Cross-sectional headline + 2026 trend continuation as descriptive followup

**Headline**: *"Public Service Loan Forgiveness Eligibility Differential in Residency Match Outcomes: An Observational Study of NRMP Program-Year Data, 2021-2026, with Multi-Year Trend Documentation"*

**Story** (what I had before, with 2026 added as descriptive):
- 2021-2025 pooled: PSLF-hostile fill rate is −16 to −18 pp lower (depending on HCA-academic classification spec), cluster-robust SE, wild-cluster bootstrap confirmed
- 2026 (first post-EO cycle): differential narrowed to ~−7 pp; consistent with a multi-year trend; cannot be specifically attributed to EO
- Specialty heterogeneity: primary care has larger gaps; surgical specialties have null gaps; consistent with PSLF financial-incentive theory but underpowered to definitively rule out alternatives
- Negative-control orthopedic surgery: NS (β=+0.76 pp); rules out only large uniform-recruitment confounds (>1.3 pp)

**Strengths**:
- Combines the substantive cross-sectional finding (which is real) with the multi-year trend
- Honestly frames 2026 as descriptive continuation
- Most defensible scientific framing
- Wider venue compatibility

**Weaknesses**:
- Less of a "headline-grabbing" finding
- Still has the underlying causal-identification limitation

**Venue fit**: JGME (best), Academic Medicine (good), HSR (moderate methods-focused)
**Acceptance probability**: 35-42% at JGME

### Option C: Maturation hypothesis (HCA-program-vintage as primary mechanism)

**Headline**: *"Residency Program Maturation in For-Profit Chain Hospitals: Six-Year Recruitment Trends 2021-2026"*

**Story** (reframe entirely as a "for-profit chain residency" study, with PSLF as one of multiple mechanisms):
- HCA / Tenet / etc. began rapidly expanding residency programs in 2014
- Their initial programs (2014-2019) had low fill rates because they were unknown quantities
- As programs mature (5-10 years), they gain reputation, applicant familiarity, and recruitment competitiveness
- The 2021→2026 narrowing trend documents this maturation empirically
- PSLF eligibility is one of several mechanisms (financial materiality, prestige, clinical training quality, applicant-pool composition)
- 2026 (first post-EO Match) is consistent with continuation of maturation; we cannot isolate EO contribution

**Strengths**:
- Coherent mechanism explanation
- PSLF becomes one of several factors, not the sole focus
- Gives proper credit to HCA program-quality improvements over time

**Weaknesses**:
- More speculative on mechanism
- Departure from the original PSLF-focused project framing
- Loses the "PSLF policy implications" angle
- Reviewer at AcadMed/JGME might say "you don't have direct data on program maturation; you're inferring"

**Venue fit**: Academic Medicine (good fit for GME maturation framing), JGME (also good)
**Acceptance probability**: 30-40% at AcadMed; reviewers may want more direct maturation evidence

---

## Recommendation: OPTION B (combined cross-sectional + trend, honest)

**Why**:
1. Preserves the locked, defensible cross-sectional finding (−16 to −18 pp pre-EO with cluster-robust + wild-cluster bootstrap)
2. Adds 2026 as honest descriptive continuation (not as a quasi-experimental break)
3. Documents the multi-year trend as novel quantitative finding
4. Maintains PSLF-policy framing (relevant to JGME/AcadMed audiences)
5. Doesn't overclaim about Trump EO causation

**Reframing checklist**:

| Section | Change |
|---|---|
| Title | Add "2021-2026" and emphasize "Observational Study" |
| Abstract | Lead with cross-sectional finding; add "narrowing trend" as secondary; flag 2026 as descriptive |
| §1 Introduction | Add hypothesis about trend (H4: gap narrows over time as HCA programs mature) |
| §2 Methods | Add 2026 to data sources; describe trend analysis (linear year trend + 2026 indicator) |
| §3 Results | Add §3.7 "Six-year trend (2021-2026)" with year-by-year table + linear trend regression. Modify abstract numbers to include 2026 |
| §4 Discussion | Replace any "Trump EO" causal framing with "consistent with multi-year trend" honest framing |
| §5 Conclusions | Soft conclusion: differential exists, has been narrowing since 2022, mechanism remains open question |
| Cover letter | Lead with novelty: first quantitative analysis at program-year level; multi-year trend documented |

---

## Updated acceptance probabilities

| Venue | Pre-2026 | Post-2026 (with my OVERSTATED framing) | Post-2026 (with HONEST framing) |
|---|---|---|---|
| JGME | 30-37% | 40-50% (overstated) | **35-42%** |
| Academic Medicine | 25-32% | 35-45% (overstated) | **32-40%** |
| HSR | 12-22% | 25-35% (overstated) | **18-28%** |
| JAMA HF | 5-15% | 25-35% (overstated, was promoted) | **8-18%** (back to fourth-choice) |
| Health Affairs | 8-15% | 15-25% (overstated, was promoted) | **8-12%** (still wrong scope) |

**Honest take**: 2026 data adds maybe +5pp to acceptance probability vs the original 5-year-only paper. It does NOT change the venue ladder substantially. JGME remains the right primary target.

---

## What changes in the deliverables

1. **`MASTER_LOCKED_NUMBERS.md`**: add 2026 row to year-by-year fill-rate table; replace "Trump EO eliminated differential" claim with honest trend documentation
2. **`PAPER_3_DRAFT_READY.md`**: add §3.7 trend analysis section; rewrite abstract; update §1 hypothesis section
3. **`PAPER_3_LOCKED_RESULTS_2026-05-10.md`**: rename to `_FINAL.md` with corrected framing
4. **`PROJECT_INDEX.md`**: update Paper 3 "headline" line
5. **`POST_COMMENTS_PLUG_AND_PLAY.md`**: no change (not affected)
6. **NEW**: `PAPER_3_LOCKED_RESULTS_2026-05-10_corrected.md` documenting the audit + retraction + reframing

---

## Lessons learned for Paper 1 + Paper 2

The same overclaim risk exists in Papers 1 and 2:

**Paper 1**: I should NOT claim "LLMs converge above satisfactory-reliability floor" without checking that the SDN-only n=300 result isn't itself part of a longer trend / cohort-specific artifact. (It probably isn't — the SDN posts are a stratified sample; bootstrap CIs are tight — but worth verifying.)

**Paper 2**: I should NOT claim "construct misalignment causes the Reddit Finance flip" without showing the underlying overlap matrix between the three negative-sentiment subsets. The current outline already flags this in §5.3 as "we hypothesize."

The overclaim pattern: I see an exciting result, frame it as causal/mechanistic, and forget to check the simpler "trend continuation" or "selection effects" alternative explanations. Going forward: BEFORE claiming a clean quasi-experiment or mechanism, check the year-by-year (or whatever the relevant baseline is) trend.
