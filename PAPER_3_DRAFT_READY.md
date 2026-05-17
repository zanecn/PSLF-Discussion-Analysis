# Paper 3 Draft-Ready Template — REFRAMED R17++ #6 (Health Affairs Scholar target)

**Status:** READY TO DRAFT; **R17++ #6 boost: METHODS TRANSLATION + WORKFORCE-DOWNSTREAM ADDITION via CMS NPPES**
**Target (R17++ #6 revised):** ***Health Affairs Scholar*** primary / ***Academic Medicine*** secondary / Journal of Graduate Medical Education (JGME) backup
**Length:** 3,500–4,500 words + supplements (slightly longer to accommodate workforce-downstream section)
**Working title (REFRAMED):** *Public Service Loan Forgiveness Eligibility, Residency Match Outcomes, and Downstream Physician Practice Patterns: A 2021–2026 Multi-Source Analysis of For-Profit Chain Residency Training in the United States*

## R17++ #6 BOOST STRATEGY (added 2026-05-17 final)

**Why elevate:** Original R17++ #5 plan targeted JGME with cross-sectional descriptive only. R17++ #5 rigorous review surfaced that JGME may struggle with the methods-heavy 28-specialty wild-cluster bootstrap, AND the descriptive nature limits policy-stakes claim. Boost strategy: translate methods for non-econometrician audience + ADD workforce-downstream analysis to convert from "institutional-level descriptive" to "institutional-level differential WITH downstream workforce implications" — better fit at *Health Affairs Scholar*.

**Two-part boost:**

1. **Methods translation (1 week)** — translate wild-cluster bootstrap + cluster-robust SE into JGME/HAS-readable language; add intuitive event-study-style figures; tone down methodological jargon. Doesn't change findings. Reduces reviewer methods barrier.

2. **Workforce downstream addition (~2-3 weeks; new data acquisition)** — link PSLF-hostile training programs to physician practice locations via CMS NPPES. "Where do residents from for-profit chain residency programs practice after graduation?" Strengthens policy claim significantly. **New data: CMS NPPES NPI pull (free public API at https://npiregistry.cms.hhs.gov/api-page) + fuzzy matching pipeline to NRMP institutions + specialty + estimated graduation year.**

**Per `DATA_ACQUISITION_PLAN_R17pp6.md`:** CMS NPPES is TIER 2 (free public data; significant data-engineering work). Total ~2 weeks of pipeline development + matching + analysis. **Fallback if matching proves too hard:** Drop the workforce-downstream boost; rely on methods translation alone for P3. Keeps JGME primary at current acceptance.

**Realistic acceptance:** *Health Affairs Scholar* ~15-25%; *Academic Medicine* ~25-30%; JGME ~30-37% (backup with methods translation).

---

# Original outline below — to be expanded per R17++ #6 boost during drafting

**Status (LEGACY R17++ #5):** READY TO DRAFT NOW. Includes 2026 NRMP data (released March 2026). Per Round 16 audit (2026-05-10), the post-Trump-EO causal interpretation is NOT supported; reframed as multi-year trend documentation.
**Target (LEGACY R17++ #5):** Journal of Graduate Medical Education (primary) / Academic Medicine (secondary)
**Length:** 3,000–4,000 words + supplements
**Working title (LEGACY):** *Public Service Loan Forgiveness Eligibility Differential in Residency Match Outcomes: A Six-Year (2021–2026) Observational Study of NRMP Program-Level Data*

---

## How to use this template

Each section below has:
- Word target
- Pre-written prose blocks with **placeholder numbers** [N=PLACEHOLDER] — substitute from `MASTER_LOCKED_NUMBERS.md`
- Citations as **(Author Year)** — full entries in `MASTER_REFERENCE_LIST.md`
- Cross-references to figures/tables that will be in the supplement

**Drafting workflow:** Open this file, expand each section's prose into the full paper. ~80% of the prose work is structural; you just fill in numbers and add transitional sentences.

---

# Title page

**Title:** Public Service Loan Forgiveness Eligibility Differential in Residency Match Outcomes: An Observational Study of NRMP Program-Level Data, 2021–2026

**Authors:** [Author 1 et al.]

**Corresponding author:** [N=PLACEHOLDER]

**Word count:** [N=PLACEHOLDER, target 3500]
**Tables:** 5
**Figures:** 2

**Funding/conflict of interest:** [N=PLACEHOLDER]

---

# Abstract (~250 words; structured per JGME)

**Background**: The Public Service Loan Forgiveness (PSLF) program is one of the largest federal financial-aid mechanisms for the physician workforce. For-profit chain hospital residency programs (PSLF-hostile by definition) have expanded since ~2014. Whether PSLF eligibility differentially affects residency program recruitment, and whether this differential has changed over time, has not been quantitatively established at the program-year level.

**Objective**: (1) To estimate the cross-sectional association between PSLF-eligibility classification and residency program fill-rate at the program-year level, using six years of NRMP Main Match data (2021–2026). (2) To document the year-by-year trajectory of the PSLF-eligibility recruitment differential.

**Methods**: Observational cross-sectional + trend study of NRMP Main Match program-year data (2021–2026) covering n=37,450 raw program-year observations from 872 unique institutions across 28 specialties. Headline cross-sectional analyses use the 5-year pre-EO subsample (2021–2025; n=29,349 program-year observations after regression dropna). Trend trajectory uses the full 6-year sample (2021–2026; n=35,193 after dropna). Programs classified as PSLF-eligible (university-affiliated or 501(c)(3)), ambiguous, or PSLF-hostile (for-profit chain–affiliated, ProPublica IRS-verified). Three sensitivity specifications addressed HCA-academic partnership classification ambiguity. Cluster-robust standard errors on institution; CMS city-level quality, state and specialty fixed effects, plus institution-level confounders (academic affiliation, scale, NIH funding) included. Wild-cluster bootstrap (Webb 6-point, B=2,000; Cameron & Miller 2015) confirmed cluster-robust inference for the small-cluster setting. Negative-control specialty (orthopedic surgery) and a linear time trend with 2026 indicator served as design checks.

**Results**: **Cross-sectional headline (2021–2025 pre-EO baseline)**: PSLF-hostile programs had a fill-rate **−16 to −18 pp lower** than ambiguous programs across all three specifications (S1 status quo: β=−18.07 pp [95% CI −24.80, −11.35], wild-cluster p<0.0005; S2 HCA-academic reclassified: β=−16.25 pp [−21.66, −10.83], wild-cluster p=0.017; S3 HCA-academic dropped: β=−17.14 pp [−22.48, −11.80], wild-cluster p=0.006). Adding NIH-funding control (state-filtered FY2023 NIH RePORTER) shifted the headline by only +0.17 pp (M5+NIH: β=−18.07 pp [−21.28, −14.87], p=2.1×10⁻²⁸). The PSLF-hostile fill-rate gap has narrowed continuously from −16.5 pp (2022) to −7.0 pp (2026). Linear trend on PSLF-hostile programs alone: +1.6 pp/year improvement (SE=1.0; p=0.105). The 2026 indicator beyond the linear trend was +3.0 pp (SE=4.1; p=0.46, NS, 95% CI [−4.96, +10.92] pp). **R17++ Agent 2 M4 sensitivity**: a complementary `is_post_eo = (year≥2025)` specification — which catches any 2025-cycle anticipation effect that the binary `is_2026` spec might miss — gives β=+0.54 pp (SE=3.48, p=0.877 NS, 95% CI [−6.28, +7.36] pp). **Both specs NS** strengthens the framing: there is no detectable EO-specific discontinuity beyond the pre-existing trend in either operationalization. We interpret this as: **the 2026 narrowing is consistent with continuation of the pre-existing trajectory** AND with up to a ~+11 pp post-EO discontinuity; this design lacks power to distinguish trend continuation from a meaningful EO contribution. The null result on the EO indicators should NOT be read as positive evidence of zero EO effect. **Negative controls**: orthopedic surgery shows clean null (2021–2025: β=+0.67 pp [−0.66, +2.00], p=0.33; 2021–2026: β=+0.54 pp [−0.53, +1.60], p=0.32 — power floor 1.06–1.33 pp). **R17++ Agent 2 M5 second negative control**: dermatology shows β=−6 to −7 pp (NS; 2021–2025 p=0.147, 2021–2026 p=0.138) — point estimate notably negative but CIs straddle zero with wide upper bound; NOT a clean null like ortho. Reported honestly as a secondary negative control with mixed result.

**Conclusions**: A substantial cross-sectional fill-rate differential separates PSLF-hostile from PSLF-eligible/ambiguous residency programs, robust to extensive confounder adjustment and small-cluster correction. The differential has been narrowing since 2022; the 2026 narrowing — the first post-Trump-EO Match cycle — is consistent with continuation of a pre-existing trend and cannot be specifically attributed to the Executive Order with this design. Plausible mechanisms (program maturation, applicant supply-side shifts, secular workforce changes, marginal EO contribution) cannot be distinguished. Future work with applicant-level data (NSLDS-linked) would help identify mechanism.

**Transparency statement**: All NRMP, ProPublica, CMS, NIH RePORTER, and ACGME source data used in this study are publicly available. Analysis code and a frozen analytical dataset will be deposited at the Open Science Framework (OSF) prior to publication. We conducted three pre-specified sensitivity specifications for the central PSLF-hostile classification (S1/S2/S3), one negative-control specialty (orthopedic surgery), one linear-trend test against a 2026-indicator alternative, and one CMS-merge dedup audit (Round 17, 2026-05-10). All analyses were run on a single corpus snapshot dated 2026-05-10. No analyses were excluded post hoc. The 2026-only post-EO causal interpretation that appeared in earlier circulating drafts is retracted (see §4.3).

---

# 1. Introduction (~600 words)

## 1.1 PSLF and the physician workforce

[INSERT BLOCK A from MASTER_DRAFTING_KIT.md] (~110 words)

## 1.2 The for-profit chain residency expansion

In 2014, HCA Healthcare announced a major expansion of graduate medical education through its for-profit hospital network (HCA Healthcare 2014). The growth has been substantial: **Lassner, Ahn, Martin, McQueen & Kukulski (2022, *J Grad Med Educ* 14(4):431–438, PMC9380617)** document the for-profit-affiliated residency program landscape across multiple specialties, and **Lassner, Ahn, Singh & Kukulski (2022, *AEM Educ Train* 6(4):e10786, PMC9348842)** report that emergency-medicine residency programs grew from 117 to 276 over 2001–2021, with for-profit-affiliated EM programs rising from 1 to 29 (85.7% of new for-profit programs accredited 2016–2021). For-profit affiliation predicted lower 2021–2022 PGY1 salary controlling for program characteristics. By 2025, HCA Healthcare, Tenet Health, USHealth, and other for-profit chains operate over 100 ACGME-accredited residency programs (ACGME 2025), concentrated in family medicine, internal medicine, emergency medicine, pediatrics, and (in smaller numbers) other primary-care specialties.

**Round 17++ correction**: prior drafts of this paragraph cited "Reddy et al. 2022" and "Cohen et al. 2022" — those author surnames were FABRICATED. Both PMC9380617 and PMC9348842 are authored by Lassner et al. (with overlapping author lists; J. W. Lassner first author on both, P. Kukulski senior author on both). All inline mentions of these papers have been re-attributed.

This expansion creates a measurable contrast: ostensibly equivalent residency training programs in the same specialty and geographic region, with different ownership structures, and **different PSLF eligibility status as a downstream programmatic feature**. This eligibility differential — programmatic, not individual — is the variable our paper studies.

## 1.3 The empirical question

If PSLF eligibility is a meaningful financial factor for residency choice, we expect to observe lower fill-rates at PSLF-hostile (for-profit chain) programs relative to comparable PSLF-eligible programs after adjusting for measurable confounders (CMS hospital quality, state and specialty fixed effects, university affiliation, academic medical center status, institution scale, NIH research funding). We test this on NRMP Main Match program-year data 2021–2025, matched to ProPublica IRS-verified PSLF-eligibility classification and city-level CMS Hospital Compare quality data.

## 1.4 Hypotheses

**H1:** PSLF-hostile programs have lower fill rates than PSLF-eligible programs in the NRMP Main Match.
**H2:** This differential is robust to standard confounders (CMS quality, state, specialty, institution scale, academic affiliation, NIH funding).
**H3:** The differential should be visible across all years for which adequate n_hostile is available.
**H4 (negative control):** The differential should be smaller in specialties where PSLF financial materiality is weaker (orthopedic surgery, where high attending compensation makes PSLF less material).

## 1.5 Contribution

To our knowledge, no prior peer-reviewed study has quantitatively estimated the PSLF-eligibility differential in residency match outcomes at the program-year level. This paper is the first quantitative analysis of this specific programmatic feature of the residency match.

---

# 2. Methods (~1,000 words)

## 2.1 Data sources

**NRMP Main Match Program Results (2021–2026)**: Per-year, per-program data including offered positions (quota), filled positions, and fill-rate. Data extracted from NRMP-published annual *Results and Data: Main Residency Match* PDFs (NRMP 2021–2026; the 2026 cycle was added from the *Program Results 2022-2026* PDF released March 2026), available publicly. Total: **37,450 raw program-year rows from 872 institutions across 28 specialties** (post Round 17 CMS-merge dedup; 6-year sample). Headline cross-sectional analyses use the 5-year pre-EO subsample (2021-2025; n=29,349 after regression dropna and HCA-academic sensitivity); 6-year sample (2021-2026; n=35,193 after dropna) is used for the year-by-year trajectory and 2026-indicator trend regression.

**Pre-2020 backfill (Wayback Machine)**: Limited NRMP archive data for 2016, 2017, and 2020 (intermediate years 2018–2019 not available in archives). Pre-2020 sample is sparse and reported descriptively only.

**ProPublica Nonprofit Explorer**: IRS Form 990 data for verifying 501(c)(3) and university status of teaching hospitals. Cross-referenced with NRMP institution names via fuzzy matching with manual verification.

**CMS Hospital Compare**: Hospital-level CMS Star Ratings (1–5 stars) and ownership classification (proprietary, voluntary nonprofit, government, etc.). City-level aggregation matched to NRMP programs.

**NIH RePORTER**: FY2023 total awards by organization, state-filtered to match NRMP institution names. Used as continuous research-intensity proxy.

**ACGME accreditation data**: University affiliation, fellowship program counts (publicly-available reports).

## 2.2 Sample construction

**Inclusion**: NRMP Main Match programs with ≥1 NRMP-reported program-year, matched to a CMS-listed teaching hospital city, and with ProPublica-verified institution type.

**Exclusion**: Programs without verifiable institution type (~4% of NRMP programs). Programs with missing CMS quality or geographic data dropped at the regression step (1,714 rows of 31,063 = 5.5%).

**Final analytical samples**:
- **5-year pre-EO baseline (2021–2025)**: n=29,349 program-year observations, after Round 15 dedup of 8 duplicate institution rows and dropna for required regression covariates. **PSLF-hostile**: 763 program-year rows from 23 institutions (S1 status-quo; 14 are HCA-academic partnerships addressed by sensitivity analysis).
- **6-year extended sample (2021–2026)**: n=35,193 program-year observations after Round 17 CMS-merge dedup (dropping 8 case-collision city duplicates such as "Boston" vs "BOSTON") and dropna. **PSLF-hostile**: 645 program-year rows from 23 institutions (S1).
- PSLF-eligible: ~17-21k program-year rows (university or 501(c)(3) verified, depending on year span)
- Ambiguous: ~11-13k program-year rows (independent academic centers)

A CONSORT-style flow diagram is provided in Supplement S2.

## 2.3 PSLF-eligibility classification (3 specifications for sensitivity)

A 3-level categorical variable based on:
- **PSLF-eligible**: ProPublica-verified 501(c)(3) status OR university medical center.
- **Ambiguous**: Independent academic center without verifiable institution type.
- **PSLF-hostile**: ProPublica-verified for-profit corporation (HCA, Tenet, USHealth, Universal Health Services, Steward Health Care, etc.).

**Critical classification ambiguity**: PSLF eligibility is determined by the **W-2 employer of the resident**, not by the parent corporation of the host hospital. At academic-partnered HCA programs (HCA/USF Morsani × 10, HCA/UMiami × 2, HCA/U Houston × 1, HCA/VCOM × 1 = 14 of 23 hostile institutions), residents may be employed by the academic partner (PSLF-eligible) under affiliation agreements. Without individual W-2 data, we cannot determine which.

To address this, we report **three sensitivity specifications**:
- **S1 (status quo)**: All 23 NRMP-hostile institutions classified as hostile. Upper bound on the PSLF-hostile differential.
- **S2 (reclassified)**: 14 HCA-academic partnerships moved to ambiguous; 9 unambiguous standalones remain hostile. Lower bound on the differential.
- **S3 (dropped)**: 14 HCA-academic partnerships removed entirely; 9 unambiguous standalones remain hostile. Cleanest restriction.

## 2.4 Confounders

[INSERT BLOCK D from drafting kit if want to combine sentiment + this; otherwise continue]

We adjust for:
1. **City-level CMS Star Rating** (mean across hospitals in the program's city; 1–5 scale)
2. **City-level CMS for-profit hospital share** (proportion proprietary)
3. **University affiliation flag** (binary, from name patterns + ProPublica NTEE codes; covers UPMC, UCSF, Stanford, Baylor, Mayo, etc.)
4. **Academic medical center flag** (binary, from name patterns; covers major-AMC institutions)
5. **n_specialties at institution** (continuous; institution scale proxy)
6. **log(annual residents PGY-1 quota)** (continuous; institution scale)
7. **log(NIH FY2023 funding)** (continuous; academic intensity)
8. **State fixed effects** (50 states + DC)
9. **Specialty fixed effects** (28 specialties)

## 2.5 Statistical analysis

OLS regression with **cluster-robust standard errors clustered on institution** as the primary inferential framework:
```
fill_rate ~ pslf_class + cms_mean_star + cms_for_profit_share +
            university_affiliation + academic_med_center +
            n_specialties + log(annual_residents_pgy1) + log(NIH_FY2023) +
            state_FE + specialty_FE
```

[INSERT BLOCK K from drafting kit] (Cameron-Miller wild-cluster bootstrap explanation, ~95 words)

**Wild-cluster bootstrap with few treated clusters (Round 17+ audit add):** Our PSLF-hostile contrast involves G=23 hostile clusters in S1 and G=9 in S2/S3. With G_treated < 30, MacKinnon & Webb (2018, *Econometrics Journal* 21(2):114–135) document that conventional cluster-robust inference and standard wild-cluster bootstrap variants can have substantially mis-sized rejection rates. We use the Webb 6-point wild bootstrap (Webb 2014; CGM 2008) imposing the null β_hostile = 0 in the restricted residuals (the WCR-1 variant), which MacKinnon-Webb (2018) and Roodman, MacKinnon, Nielsen & Webb (2019, *Stata Journal* 19(1):4–60) recommend as the most defensible single-test variant in the few-treated-cluster regime. Reported wild-cluster p-values (S1 p<0.0005; S2 p=0.017; S3 p=0.006) should be interpreted as the most-defensible currently-available point estimates with the caveat that their finite-sample coverage at G=9 (S2/S3) sits in the gray zone of the MacKinnon-Webb 2018 simulations; randomization inference (permuting hostile vs ambiguous within strata) would be the natural complement to confirm.

Robustness checks include negative-control specialty (orthopedic surgery; high attending compensation makes PSLF less financially material), within-institution differences-in-differences for the Limited PSLF Waiver event (October 2021), year-by-year fill-rate gap reporting, and per-specialty PSLF-hostile β.

## 2.6 Software

[INSERT BLOCK M from drafting kit] (Methods software footer, ~80 words)

---

# 3. Results (~1,200 words)

## 3.1 Sample composition (Table 1)

**Table 1**: Sample composition by year × PSLF-class × specialty × geographic region. [Generate from `nrmp_program_level_2021_2025.csv` + `institutional_confounders.csv`.]

## 3.2 Headline result (Table 2)

**Table 2 — Robustness ladder (M1 → M5+NIH with cluster-robust SE):**

[Substitute from `paper3_model5_FINAL_results.txt` and `paper3_wild_cluster_bootstrap_results.txt`. Use the exact 3-spec sensitivity table from `MASTER_LOCKED_NUMBERS.md` Paper 3 section.]

| Specification | n_hostile_inst | n_hostile_rows | PSLF-hostile β | 95% CI (cluster) | Cluster-robust p | Wild-cluster bootstrap p |
|---|---|---|---|---|---|---|
| S1 (all 23 hostile) | 23 | 763 | **−18.07 pp** | [−24.80, −11.35] | 1.4×10⁻⁷ | <0.0005 |
| S2 (HCA-acad reclassified) | 9 | 358 | **−16.25 pp** | [−21.66, −10.83] | 4.0×10⁻⁹ | 0.017 |
| S3 (HCA-acad dropped) | 9 | 358 | **−17.14 pp** | [−22.48, −11.80] | 3.1×10⁻¹⁰ | 0.006 |

**Interpretation paragraph (~150 words):** The PSLF-hostile differential is large and statistically significant across all three specifications. Both cluster-robust and wild-cluster bootstrap inferences support a fill-rate gap of approximately 16-18 percentage points relative to ambiguous programs. The wild-cluster bootstrap correction substantially attenuates the asymptotic precision (S2 went from p=4×10⁻⁹ to p=0.017 — 7 orders of magnitude); we report the wild-cluster values as the defensible inferences. The headline survives the small-cluster correction in all three specifications.

[INSERT honest robustness-ladder framing from MASTER_LOCKED_NUMBERS.md or §3.2 of current outline — low coefficient shrinkage M1→M5 means measured confounders don't vary across the contrast, NOT that the headline is robust to omitted variables.]

## 3.3 Year-by-year fill-rate trajectory (Figure 1) — UPDATED with 2026 data

**Figure 1**: Year-by-year PSLF-eligible vs PSLF-hostile fill-rate gap, 2016–2026. With explicit annotation: 2016–2017 sample sizes inadequate (n_hostile ≤ 8); 2020 onward report sufficient n. **Visual emphasizes the multi-year narrowing trend 2022→2026.**

| Year | n_friendly | n_hostile | Hostile fill | Friendly fill | Gap (pp) |
|---|---|---|---|---|---|
| 2016 | 2,190 | 6 | 0.7900 | 0.9408 | −5.92 (insufficient n) |
| 2017 | 2,437 | 8 | 0.9250 | 0.9377 | +1.27 (insufficient n) |
| 2020 | 2,269 | 54 | 0.7793 | 0.9355 | +15.63 |
| 2021 | 3,353 | 129 | 0.7994 | 0.9394 | **−14.00** |
| 2022 | 3,451 | 149 | 0.7767 | 0.9415 | **−16.48** |
| 2023 | 3,518 | 159 | 0.8028 | 0.9346 | **−13.18** |
| 2024 | 3,597 | 159 | 0.8326 | 0.9397 | **−10.71** |
| 2025 | 3,677 | 167 | 0.8356 | 0.9404 | **−10.47** |
| **2026** | **3,887** | **171** | **0.8645** | **0.9348** | **−7.03** |

**Interpretation paragraph (~120 words):** The PSLF-hostile fill-rate gap has been narrowing every year since 2022 (−16.48 pp → −13.18 pp → −10.71 pp → −10.47 pp → −7.03 pp). The 2026 narrowing of +3.44 pp continues this multi-year trajectory. Linear time trend regression on PSLF-hostile programs alone (n=934 program-year rows; cluster-robust SE on institution; controls for state and specialty fixed effects): year coefficient = +1.595 pp/year (SE=0.985, p=0.105). Adding a 2026 indicator beyond this linear trend yields a non-significant +2.984 pp (SE=4.05, p=0.46), indicating **the 2026 narrowing is statistically indistinguishable from continuation of the pre-existing trend**. We cannot specifically attribute the 2026 narrowing to the Trump PSLF Executive Order. Plausible mechanisms — HCA program maturation, secular workforce changes, applicant-pool composition shifts, marginal EO contribution — cannot be distinguished with this design.

## 3.4 Within-institution DiD (Table 3, with caveat)

**Table 3:** Within-institution differences-in-differences (pre-2020 vs post-2022). Pre-Waiver (2016-20) vs Post-Waiver (2022-25):
- PSLF-friendly (n=224 institutions): Δ = −0.93 pp
- Ambiguous (n=222): Δ = −0.56 pp
- **PSLF-hostile (n=7)**: Δ = −8.97 pp
- DiD: +8.04 pp; t=1.94; **p=0.098 (NS)**

**Interpretation paragraph (~80 words):** With only 7 hostile institutions present in both pre- and post-Waiver eras, power to detect a 10-pp treatment effect is below 30%. The DiD is non-significant; we **do not interpret this null as evidence either for or against a treatment effect of the Limited PSLF Waiver**. Within-institution fill rates appear stable across the Waiver event but the test is underpowered to definitively resolve the question.

## 3.5 Negative-control specialty (Table 4)

**Table 4:** Orthopedic surgery PSLF-hostile β (Round 17 dedup-corrected; both 5-year and 6-year samples).

| Subset | n_total | n_hostile | n_inst | PSLF-hostile β | 95% CI | p-value | Power floor (1.96·SE) |
|---|---|---|---|---|---|---|---|
| Pooled all specialties (S1, 5-year) | 29,349 | 763 | 23 | −18.07 pp | [−24.80, −11.35] | <0.0005 (wild-cluster) | n/a |
| Orthopedic surgery (5-year, 2021–2025) | 1,007 | 11 | 3 | **+0.67 pp** | [−0.66, +2.00] | 0.33 (NS) | 1.33 pp |
| Orthopedic surgery (6-year, 2021–2026) | 1,204 | 16 | 4 | **+0.54 pp** | [−0.53, +1.60] | 0.32 (NS) | 1.06 pp |

**Interpretation paragraph (~140 words; Round 17+ revised):** The negative-control specialty (orthopedic surgery) shows no PSLF-hostile differential at either the 5-year or 6-year sample, in contrast to the −18 pp pooled finding. This is consistent with the PSLF financial-incentive interpretation: high attending compensation in orthopedic surgery makes PSLF less material, so the differential should be smaller or null in this specialty. **However, the negative-control test is power-limited.** With n=11 hostile rows from 3 institutions (5-year) or n=16 from 4 institutions (6-year), the orthopedic-surgery test only rules out uniform-recruitment confounds of magnitude > 1.06–1.33 pp. It does NOT rule out smaller uniform confounds (e.g., 0.5–1 pp). The negative-control logic is also weakened because the 3-4 hostile-ortho clusters may be HCA-academic partnerships (with classification ambiguity addressed in S2/S3 sensitivity above). The result is suggestive, not conclusive. (Earlier circulating drafts cited n=1,079, β=+0.76 pp, p=0.25, n_hostile=21 from 4 clusters; those numbers reflect a pre-Round-17 covariate filter and are superseded.)

## 3.6 Specialty heterogeneity (Table 5)

**Table 5:** PSLF-hostile β by specialty (post-Waiver):
| Specialty | Gap (pp) | Direction consistent with PSLF mechanism? |
|---|---|---|
| Pediatrics | +34.11 | YES (primary care, low compensation) |
| Internal Medicine | +27.41 | YES |
| Emergency Medicine | +16.68 | YES |
| Family Medicine | +13.46 | YES |
| Dermatology | +1.08 | (high compensation; null as expected) |
| Surgery-General | +0.59 | (high compensation; null as expected) |
| Psychiatry | −1.06 | (slight inversion; not interpreted) |

**Interpretation paragraph (~120 words):** Specialty heterogeneity is consistent with the PSLF financial-incentive theory: the differential is concentrated in primary care (Internal Medicine, Family Medicine, Emergency Medicine, Pediatrics) where attending compensation is closer to the loan-payment burden and PSLF is more financially material. Procedural and surgical specialties (Surgery, Dermatology, Psychiatry) show small or null differentials, where attending compensation is high enough that PSLF is less material. **However**, this pattern is also confounded by HCA-business-strategy: HCA's residency expansion focused on primary care and emergency medicine, so PSLF-hostile representation in surgical specialties is partly driven by where HCA chose to enter the market, not by where PSLF eligibility matters. We frame specialty heterogeneity as descriptive — concentrated in primary care — rather than mechanism-confirming.

---

# 4. Discussion (~600 words)

## 4.1 Cross-sectional differential, mechanism unidentified

The cross-sectional fill-rate differential between PSLF-hostile and PSLF-eligible/ambiguous residency programs is approximately 16-18 percentage points and is documented across the 2020–2025 NRMP cycles for which we have adequate hostile-institution sample. Mechanism — long-standing structural pattern vs treatment effect of PSLF policy events (Limited Waiver 2021, etc.) — cannot be identified with this design due to (a) inadequate pre-2020 sample (n_hostile ≤ 8 in 2016-17), (b) underpowered within-institution DiD (n=7 hostile institutions in both eras).

## 4.2 Specialty-pattern consistent with PSLF mechanism

Primary care specialties (FM, IM, EM, Peds) show large gaps; surgical and procedural specialties show small or null gaps. This is consistent with PSLF being more financially material in primary care, where attending compensation is closer to the loan-payment burden. We caveat that the pattern is also consistent with HCA-business-strategy + applicant-pool-composition confounds we cannot directly measure.

## 4.3 Programmatic implications

If the 16-18 pp differential is causal in any meaningful share, for-profit chain residency programs face a recruitment disadvantage that is policy-relevant. Recent policy moves to expand or restrict PSLF eligibility (e.g., the March 2025 Trump PSLF Executive Order restricting PSLF for "illegal-purpose" employers) introduce new uncertainty. The 2026 Match cycle — the first in which applicants had ~12 months to respond to the EO when forming preferences — shows continued narrowing of the PSLF-hostile fill-rate gap (−10.47 pp in 2025 → −7.03 pp in 2026, a +3.44 pp narrowing). However, this narrowing is statistically indistinguishable from continuation of the 2022–2025 trajectory (+1.6 pp/year linear trend, p=0.105; is_2026 indicator beyond linear trend p=0.46 NS); we cannot specifically attribute the 2026 narrowing to the EO with this design. Multi-year follow-up (2027 and forward) and applicant-level data would be needed to identify EO-specific impact.

## 4.4 Limitations

1. **Observational design.** No exogenous variation in PSLF eligibility; no IV; no quasi-experiment. Selection and confounding cannot be fully ruled out.

2. **PSLF-eligibility classification depends on host hospital institution type, not resident W-2 employer**. We address this with three sensitivity specifications (S1/S2/S3) that bracket the plausible range. Without individual W-2 data (NSLDS DUA-required, not in our scope), we cannot determine which specification reflects the true classification.

3. **Pre-2020 baseline insufficient**. n_hostile ≤ 8 per year for 2016–2017 makes year-by-year comparisons for 2016–2019 statistically empty.

4. **Specialty heterogeneity is consistent with PSLF mechanism, not direct evidence of it**. Compensation, applicant-pool-quality, and HCA-business-strategy confounds cannot be directly measured.

5. **Negative-control orthopedic surgery is power-limited** to ruling out uniform confounds of magnitude > 1.3 pp.

6. **No individual-level data**. We measure program-level fill rates, not individual decisions.

7. **2026 Match data is one post-EO cycle only.** The 2025 NRMP Match was pre-EO (ROL deadline Feb 24, 2025; EO signed Mar 7, 2025). 2026 is the first post-EO Match cycle. The 2026 narrowing of the PSLF-hostile fill-rate gap (+3.44 pp DiD descriptive; +8.46 pp post-EO Δ regression coefficient in S1) cannot be statistically distinguished from continuation of the pre-existing 5-year trend (linear-trend year coefficient +1.6 pp/year, p=0.105; is_2026 indicator beyond linear trend p=0.46 NS). Multi-year post-EO follow-up is necessary to identify EO-specific causal impact.

8. **NSLDS DUA pending**. A future analysis with NSLDS individual-level data could verify program-level PSLF eligibility against borrower-level loan history. Application is not currently in progress; estimated 6–12 months for approval.

---

# 5. Conclusions and Relevance (~250 words)

In a six-year (2021–2026) program-year analysis of NRMP Main Match data (5-year pre-EO subsample n=29,349 for headline cross-sectional inference; full 6-year n=35,193 for trajectory and 2026 indicator; cluster-robust SE on institution; Cameron-Miller wild-cluster bootstrap confirmation; 3-spec sensitivity for HCA-academic partnerships), PSLF-hostile (for-profit chain–affiliated) residency programs have a fill-rate differential in the range −16 to −18 pp relative to PSLF-eligible/ambiguous programs after extensive confounder adjustment. The PSLF-hostile fill-rate gap has narrowed continuously from −16.5 pp (2022) to −7.0 pp (2026); year-by-year linear trend on hostile-only programs is +1.6 pp/year (p=0.105). The 2026 narrowing — the first post–Trump-EO Match cycle — is consistent with continuation of the pre-existing trend (is_2026 indicator beyond linear trend β=+3.0 pp, p=0.46 NS) and cannot be specifically attributed to the EO with this design. Specialty heterogeneity (large gaps in primary care; null/inconsistent in surgical specialties) is consistent with PSLF financial-incentive theory, though direct mechanism identification is limited by the observational design and by classification ambiguity for HCA-academic-partnership institutions.

This paper is the first peer-reviewed quantitative estimate of the PSLF-eligibility differential in residency match outcomes at the program-year level. The pattern is observational; mechanism (selection vs treatment vs confound) cannot be identified. PSLF-eligibility is a meaningful programmatic feature for residency competition; the mechanism remains an open question for future research with applicant-level (NSLDS-linked) data.

[INSERT BLOCK N (what we cannot claim) and BLOCK O (OSF) from drafting kit]

---

# Tables (5 total)

- Table 1: Sample composition by year × PSLF-class × specialty × region
- Table 2: Robustness ladder (M1 → S3) with wild-cluster bootstrap
- Table 3: Within-institution DiD (with power caveat)
- Table 4: Negative-control specialty (orthopedic surgery)
- Table 5: Specialty heterogeneity

# Figures (2 total)

- Figure 1: Year-by-year fill-rate gap 2016-2026 with sample-size annotations
- Figure 2: Forest plot of PSLF-hostile β across 3 specifications + negative control

---

# Supplements (8 total)

[See `PAPER_3_JAMA_HF_policy_OUTLINE.md` for S1-S8 list.]

---

## DRAFTING NOTES FOR PAPER 3

- Voice: medical-journal formal (JGME / AcadMed style)
- Avoid editorializing
- Lead with cluster-robust + wild-cluster bootstrap as primary inference
- Frame mechanism as "open question" not "supports PSLF interpretation"
- Specialty heterogeneity as "descriptive" not "mechanism-confirming"
- Cover letter should highlight: program-year analysis, ProPublica-verified PSLF classification, S1/S2/S3 sensitivity, wild-cluster bootstrap robustness, novel quantitative analysis
- Suggested reviewers: Phillips (UNC, primary care workforce), Carr (HSR PSLF research), AAMC research staff, Mullan (GME policy)

**Estimated drafting time: 4-6 weeks of focused writing.**
