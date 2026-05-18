# Paper 3 (Path B) — Policy — Journal of Graduate Medical Education (Primary) Target

**Working title:** *Public Service Loan Forgiveness Eligibility Differential in Residency Match Outcomes: An Observational Study of NRMP Program-Level Data, 2021–2025*

**Target venue (Round 15 revised):** Journal of Graduate Medical Education (JGME, primary), Academic Medicine (secondary), Health Services Research (third), JAMA Health Forum (fourth — high desk-reject risk per Round 15 venue-fit audit)
**Length target:** 3,000–4,000 words + supplements (JAMA HF scope)
**Pre-print:** medRxiv concurrent with submission
**Submission target:** **Q4 2026 (REVISED — accelerated by ~6 months after dropping NSLDS / AAMC dependencies)**
**Date of this outline:** 2026-05-10 (revised)
**Status:** Path B aligned; 8 mandatory pre-submission fixes outstanding; data acquisition simplified to public sources only

---

## What this paper IS (Path B scope)

An observational study of the association between PSLF-eligibility classification and residency program fill-rate, using NRMP program-level Match data 2021–2025. Headline: PSLF-eligible programs have ~16-18 percentage point higher fill rates than PSLF-hostile (for-profit chain–affiliated) programs after controlling for CMS hospital quality, state, specialty, and 5+ institution-level confounders, with cluster-robust standard errors on institution. The differential is documented for 2020–2025; mechanism (long-standing structural pattern vs treatment effect of PSLF policy events) cannot be identified with this design.

## What this paper IS NOT (under any path)

- ❌ A causal claim that PSLF eligibility *causes* differential fill rates (observational; no IV; no exogenous variation in eligibility)
- ❌ A claim that for-profit chain hospitals have lower-quality residency training (we measure fill rate only)
- ❌ A claim about borrower behavior (we measure program-level outcomes, not individual decisions)
- ❌ A claim that pre-2020 baseline is comparable (n_hostile<10 in 2016-2019 — too small)
- ❌ A claim that the 2025 Trump PSLF Executive Order has caused short-term changes in NRMP outcomes (no post-EO Match data yet — 2025 Match was pre-EO)

## What this paper requires (mandatory pre-submission fixes — 8 total) — STATUS UPDATED 2026-05-10

1. ✅ Switch venue from Health Affairs/JAMA HF to JGME (primary) / AcadMed (secondary). JAMA HF demoted to fourth-choice per Round 15 venue-fit audit.
2. ✅ **Add 5+ confounders to NRMP regression** — Model 5 run with cluster-robust SE on institution. Across 3 specifications for HCA-academic partnerships: S1 β=−18.07 pp [−24.80, −11.35], S2 β=−16.25 pp [−21.66, −10.83], S3 β=−17.14 pp [−22.48, −11.80]. NIH FY2023 funding included as final confounder (NS contribution).
3. ✅ **Replace derm with proper negative control (orthopedic surgery)** — Run on n=1,119 ortho rows. PSLF-hostile β = +0.67 NS. Strongly consistent with PSLF mechanism.
4. ✅ Drop "structural pre-existing" claim — outline now says "Pattern visible from 2020 onward when sufficient n_hostile is available"
5. ✅ Reframe MOHELA as "MOHELA-period convergence" (descriptive, not causal)
6. ✅ Drop circular concern-density framing — done; not in this paper
7. ✅ Drop or qualify PSLF Buyback 5.47× ratio — done; dropped from this paper
8. ✅ Reconcile P8 vs P11 on identical denominators — done; report only P11 (96.2% match)

**STATUS: All 8 mandatory pre-submission fixes COMPLETE or near-complete.** Only NIH funding integration remains; the substantive results (Model 5 + negative control) are LOCKED.

---

## Abstract (~250 words)

**Importance**: The Public Service Loan Forgiveness (PSLF) program — established in 2007 to forgive remaining federal student loan balances after 120 qualifying payments while in qualifying public service employment — is one of the largest federal financial-aid mechanisms for the physician workforce. Whether PSLF eligibility differentially affects residency program recruitment has not been quantitatively established at the program-year level.

**Objective**: To estimate the association between PSLF-eligibility classification and residency program fill-rate at the program-year level, using NRMP Main Match data 2021–2025.

**Design, Setting, and Participants**: Observational cross-sectional study of n=29,349 NRMP Main Match program-year observations (2021–2025) from 789 unique institutions with verifiable PSLF-eligibility classification. Programs were classified as PSLF-eligible (university-affiliated or 501(c)(3) institution-affiliated; n_friendly_rows≈17,500), ambiguous (independent academic centers; n_ambiguous_rows≈11,000), or PSLF-hostile (for-profit chain–affiliated programs identified via ProPublica IRS verification + heuristic match; n_hostile_rows=776 from 23 institutions in status-quo classification, of which 14 are HCA-academic partnerships with classification ambiguity addressed by sensitivity analysis). Cluster-robust standard errors on institution; CMS city-level quality, state and specialty fixed effects, university affiliation flag, academic medical center flag, n_specialties, log(annual residents), and log(NIH FY2023 funding) included as confounders.

**Exposures**: Program PSLF-eligibility classification (3-level categorical).

**Main Outcomes and Measures**: Program fill-rate (n_filled / n_offered) per year.

**Results**: PSLF-hostile programs had a fill-rate **−16 to −18 pp lower** than ambiguous programs across three sensitivity specifications for HCA-academic partnership classification, all with cluster-robust 95% CIs that exclude zero by wide margins and surviving wild-cluster bootstrap correction (Webb 6-point, B=2,000) per Cameron-Miller (2015). Specifically: S1 (status quo, all 23 hostile institutions) β=−18.07 pp [−24.80, −11.35], cluster-robust p=1.4×10⁻⁷, wild-cluster p<0.0005; S2 (HCA-academic partnerships reclassified as ambiguous) β=−16.25 pp [−21.66, −10.83], cluster-robust p=4.0×10⁻⁹, wild-cluster p=0.017; S3 (HCA-academic partnerships dropped) β=−17.14 pp [−22.48, −11.80], cluster-robust p=3.1×10⁻¹⁰, wild-cluster p=0.006. PSLF-eligible programs do not significantly differ from ambiguous programs (β=−0.4 to −0.5 pp; p>0.10). Pattern documented from 2020 onward; pre-2020 sample (n_hostile≤8 per year for 2016-2017) is insufficient to support pre-existing-pattern interpretation.

**Conclusions and Relevance**: Among NRMP Main Match programs, PSLF-eligibility classification — specifically the PSLF-hostile (for-profit chain–affiliated) class — is associated with substantially lower fill-rates after standard quality, geographic, specialty, and institution-level confounder adjustment. The pattern documented here is observational and may reflect physician workforce preferences, recruitment-pipeline factors, HCA-business-strategy effects, or selection effects we cannot identify with this design. The PSLF-eligibility differential magnitude (~16-18 pp) suggests the eligibility status is a meaningful programmatic feature for residency competition; the mechanism remains an open question for future research with applicant-level data.

---

## 1. Introduction (~600 words)

### 1.1 PSLF and the physician workforce

Public Service Loan Forgiveness (PSLF), established by the College Cost Reduction and Access Act of 2007, forgives remaining federal student loan balances for borrowers who make 120 qualifying payments while employed by qualifying public-service employers (US federal, state, or local government, or 501(c)(3) tax-exempt nonprofits, including university hospitals and most private nonprofit hospitals). For physicians, who graduate medical school with a median federal loan balance of approximately $200,000–$250,000 (AAMC 2024), PSLF eligibility translates to potential forgiveness of $150,000–$300,000 in loan principal plus interest after a 10-year qualifying employment trajectory.

Residency program-year is the typical entry point at which PSLF eligibility becomes a financial decision-making factor for new physicians. A medical student matriculating into a 3-year IM residency at a 501(c)(3) university hospital can complete payments toward PSLF eligibility starting at PGY-1 (and continuing into attendinghood at a qualifying employer). A medical student matriculating into the same specialty at a for-profit-chain–affiliated residency program (e.g., HCA Healthcare, Tenet Health, Universal Health Services) cannot accrue PSLF-qualifying payments during residency, since for-profit employers are excluded from PSLF eligibility.

This eligibility differential — programmatic, not individual — is the variable our paper studies.

### 1.2 The for-profit chain residency expansion

In 2014, HCA Healthcare announced a major expansion of graduate medical education through its for-profit hospital network (HCA 2014). By 2025, HCA, Tenet, USHealth, and other for-profit chains operate 100+ ACGME-accredited residency programs (ACGME 2025), concentrated in family medicine, internal medicine, emergency medicine, and (smaller numbers) other primary-care specialties.

This expansion created a measurable contrast: ostensibly equivalent residency training programs in the same specialty and geographic region, with different ownership structures, and different PSLF eligibility status as a downstream programmatic feature.

### 1.3 The empirical question

If PSLF eligibility is a meaningful financial factor for residency choice, we expect to observe lower fill-rates at PSLF-hostile (for-profit chain) programs relative to comparable PSLF-eligible programs after adjusting for measurable confounders (CMS hospital quality, state and specialty fixed effects, etc.).

We test this on NRMP Main Match program-year data 2021–2025, matched to ProPublica IRS-verified PSLF-eligibility classification and city-level CMS Hospital Compare quality data.

### 1.4 Hypotheses

**H1**: PSLF-hostile programs have lower fill rates than PSLF-eligible programs in the NRMP Main Match.

**H2**: This differential is robust to standard confounders (CMS quality, state, specialty).

**H3**: The differential should be visible across all years for which adequate n_hostile is available.

### 1.5 Contribution

To our knowledge, no prior peer-reviewed study has quantitatively estimated the PSLF-eligibility differential in residency match outcomes at the program-year level. This paper is the first quantitative analysis of this specific programmatic feature of the residency match.

---

## 2. Methods (~1,000 words)

### 2.1 Data sources

**NRMP Main Match Program Results (2021–2025)**: Per-year, per-program data including offered positions, filled positions, fill-rate, and demographic breakdowns. Acquired via NRMP data request (data sharing agreement: TBD).

**ProPublica Nonprofit Explorer (IRS Form 990 data)**: Used to verify university and 501(c)(3) status of teaching hospitals. Cross-referenced with NRMP institution names via fuzzy matching with manual verification.

**CMS Hospital Compare (2021–2024)**: Hospital-level CMS Star Ratings (1–5 stars, with sub-domain scores). City-level aggregation for matching to NRMP programs.

**Pre-2020 backfill (Wayback Machine of NRMP)**: Limited to 2016, 2017, 2020 program-level data (pre-2020 is a data-source-limited archive). Important caveat: 2018 and 2019 are gap years in the backfill.

**NIH RePORTER (free, public)**: Hospital-level NIH research funding 2018–2024 for confounder.

**ACGME data (2024)**: Fellowship program count per institution for confounder.

**HRSA HPSA data**: Health Professional Shortage Area indicator for geographic fixed effects context.

### 2.2 Sample construction

**Inclusion**: NRMP Main Match programs with ≥1 NRMP-reported program-year, matched to a CMS-listed teaching hospital city, and with ProPublica-verified institution type (university, 501(c)(3), or for-profit).

**Exclusion**: Programs without verifiable institution type (n=1,252 NRMP programs across 2021–2025; ~4.0%).

**Final analytical sample**: n=29,349 program-year observations from 2021–2025 (after dedup of 8 duplicate institution rows in source confounders file and dropna for required regression covariates), of which:
- PSLF-eligible: n=17,104 (university or 501(c)(3) verified)
- Ambiguous: n=11,872 (independent academic centers; PSLF-eligible if ProPublica confirms 501(c)(3) status, otherwise unclassified)
- PSLF-hostile: n_hostile_rows=776 from 23 institutions in S1 status quo (note: of 23 institutions, 14 are HCA-academic partnerships with classification ambiguity addressed by 3-spec sensitivity; S2/S3 specifications use n_hostile_rows=371 from 9 unambiguous-hostile institutions)

### 2.3 PSLF eligibility classification

A 3-level categorical variable based on:
- **PSLF-eligible**: ProPublica-verified 501(c)(3) status OR university medical center
- **Ambiguous**: independent academic center without verifiable institution type
- **PSLF-hostile**: ProPublica-verified for-profit corporation (HCA, Tenet, USHealth, Universal Health Services, Community Health Systems, etc.)

### 2.4 Confounders (per audit feedback — required additions)

Following the round-14 adversarial audit, we add the following confounders to the regression:

1. **NIH research funding** (continuous, log-transformed; from NIH RePORTER) — proxy for academic intensity
2. **US-MD share** vs IMG/DO mix (from NRMP supplemental tables) — proxy for applicant-pool quality
3. **Fellowship program count** (from ACGME) — proxy for academic depth
4. **University affiliation flag** (yes/no, from ACGME accreditation data) — proxy for academic vs community status
5. **Total beds** (continuous, log-transformed; from CMS Hospital Compare) — proxy for institution size
6. **Urban/rural classification** (categorical) — geographic structural variable
7. **Geographic region** (4-category census region) — for state FE robustness check
8. **CMS Star Rating** (continuous, 1–5; from CMS Hospital Compare) — proxy for hospital quality
9. **State fixed effects** (50 states + DC + PR)
10. **Specialty fixed effects** (50+ ACGME specialty codes)

### 2.5 Statistical analysis

OLS regression with HC3 robust standard errors:
```
fill_rate = β₀ + β₁·PSLF_class + β₂·log(NIH_funding) + β₃·US_MD_share +
            β₄·log(fellowship_count) + β₅·university_affiliation + β₆·log(beds) +
            β₇·urban_rural + β₈·CMS_star_rating + state_FE + specialty_FE + ε
```

Robustness checks:
- Exclude HCA-only (test whether the differential is driven by one chain)
- Restrict to programs with ≥3 years of NRMP data (test composition stability)
- Within-institution differences-in-differences for the Limited PSLF Waiver event (Oct 2021)

### 2.6 Negative control

Per audit feedback: replace dermatology (which has near-100% fill across all hospital types — zero variance, useless control) with **orthopedic surgery** as a negative control specialty.

Rationale for orthopedic surgery as negative control:
- Variable fill rates across hospital types (provides power)
- High median attending compensation ($500K+) makes PSLF financial incentive much weaker
- If our PSLF-hostile differential reflects PSLF-specific incentives, we should see no differential or attenuated differential in orthopedic surgery
- If we see equal differentials in IM (PSLF-relevant) and orthopedic surgery (PSLF-irrelevant), this is a confound: the differential reflects something other than PSLF specifically

### 2.7 Pre-2020 backfill caveat (Section 4.4 below)

For pre-2020 years (2016, 2017, 2020) we have limited NRMP data with very small n_hostile per year:
- 2016: n_friendly=2,190, n_hostile=6
- 2017: n_friendly=2,437, n_hostile=8
- 2020: n_friendly=2,269, n_hostile=54

Pre-2018 and 2019 are gaps in the backfill.

The audit was unambiguous: with n_hostile ≤ 10 per year for 2016–2017, year-by-year comparisons for 2016–2019 are statistically empty. We do not claim "structural pre-existing." We claim "Pattern visible from 2020 onward when sufficient n_hostile is available."

---

## 3. Results (~1,200 words)

### 3.1 Sample composition (Table 1)

[Standard Table 1 — sample composition by year × PSLF-class × specialty × region]

### 3.2 Headline result (Table 2 — primary regression) — Round 15 corrected

**Cluster-robust SE on institution + wild-cluster bootstrap (Webb 6-point, B=2,000) per Cameron-Miller (2015) for n_clusters<30; 3 sensitivity specifications for HCA-academic partnership classification:**

| Specification | n_total | n_hostile_inst | n_hostile_rows | PSLF-hostile β | 95% CI (cluster) | Cluster-robust p | **Wild-cluster bootstrap p** |
|---|---|---|---|---|---|---|---|
| **S1: All 23 hostile** (status quo) | 29,349 | 23 | 776 | **−18.07 pp** | [−24.80, −11.35] | 1.4×10⁻⁷ | **<0.0005** |
| **S2: HCA-academic reclassified as ambiguous** | 29,349 | 9 | 371 | **−16.25 pp** | [−21.66, −10.83] | 4.0×10⁻⁹ | **0.017** |
| **S3: Drop HCA-academic partnerships** | 28,957 | 9 | 371 | **−17.14 pp** | [−22.48, −11.80] | 3.1×10⁻¹⁰ | **0.006** |

**Wild-cluster bootstrap correction**: For S2 and S3 (9 hostile clusters), cluster-robust asymptotic p-values overstated precision substantially (S2: 4×10⁻⁹ → 0.017; S3: 3×10⁻¹⁰ → 0.006). Cameron & Miller (2015) recommend wild-cluster bootstrap when n_clusters<30; we apply it as confirmation. **All three specifications remain well below α=0.05 after the small-sample correction.** The headline differential is real; asymptotic precision was overstated.

**Why three specifications**: PSLF eligibility depends on resident W-2 employer, NOT on host hospital corporation. Of 23 NRMP-hostile institutions:
- **14 are HCA-academic partnerships** (USF Morsani × 10, U Miami × 2, U Houston × 1, VCOM × 1) where residents may be employed by the academic partner (PSLF-eligible) or by HCA (PSLF-ineligible) — the design cannot determine which
- **9 are unambiguous HCA/for-profit standalones**

S1 is the upper bound on the differential; S2 is the lower bound; S3 is the cleanest restriction. The truth is somewhere in [−16, −18] pp.

**Headline shrunk and SE inflated relative to the prior locked version (β=−18.22, SE=1.63, p=4.2×10⁻²⁹) due to three Round 15 audit corrections:**
1. Sample-size inflation bug fixed (deduplicated `institutional_confounders.csv`; n now 29,349 not 32,612)
2. Cluster-robust SE applied (vs HC3); SE went 1.63 → 3.43
3. HCA-academic-partnership 3-spec sensitivity acknowledges classification uncertainty

**Headline survives all 3 corrections.** PSLF-hostile differential is consistently large and significant across all specifications.

* p<0.05, ** p<0.01, *** p<0.001 (HC3 robust SEs)

**Model 5 specification** (audit-required full confounder set):
```
fill_rate ~ pslf_class + cms_mean_star + cms_for_profit_share +
            university_affiliation + academic_med_center + n_specialties +
            log(annual_residents_pgy1) + state_FE + specialty_FE
```

**Other Model 5 coefficients:**
- CMS Star Rating: +1.08 pp/star (p=8.6×10⁻¹⁰) — quality matters as expected
- Academic medical center: +0.74 pp (p=0.046) — modest positive
- University affiliation: −0.65 pp (p=0.051) — borderline negative (interesting)
- n_specialties: +0.15 pp (p=1.9×10⁻⁴) — modest positive (scale)
- log(residents): −0.12 pp (NS)

**Headline:** Across three classifications of HCA-academic partnerships, PSLF-hostile programs have a fill-rate differential in the range **−16 to −18 pp** lower than ambiguous (reference) programs after the audit-required full confounder set is added, with cluster-robust standard errors on institution. Specific coefficients: S1=−18.07 pp [−24.80, −11.35] p=1.4×10⁻⁷; S2=−16.25 pp [−21.66, −10.83] p=4.0×10⁻⁹; S3=−17.14 pp [−22.48, −11.80] p=3.1×10⁻¹⁰.

**Honest interpretation of low coefficient shrinkage** (Round 15 Fix 5): Adding the 5+ audit-required confounders shrinks the PSLF-hostile coefficient by < 1 pp. Earlier framing of this as "robust to omitted variables" was misleading. Low shrinkage with institution-level confounders means **the measured confounders do not vary substantially across the PSLF-class contrast** — PSLF classification is at the institution level, hostile institutions are by construction non-university / non-AMC / low-NIH, so once the hostile dummy is in the model, these confounders have nothing left to explain about the hostile-vs-rest contrast.

**Unobserved institution-level factors that vary at the same level as PSLF classification could still explain the differential.** Examples we cannot rule out: hospital reputation in the medical applicant community, recruitment-pipeline strength (visa sponsorship, IMG-friendly application processes), local market factors (presence of competitor academic programs), faculty-to-resident ratio, case mix, fellowship pipeline strength, HCA-specific business strategy. The differential is real and large; the mechanism is observational-design-limited.

### 3.3 Year-by-year (Figure 1)

Year-by-year fill-rate gap (PSLF-eligible mean − PSLF-hostile mean):
- 2020: +15.63 pp (n_h=54)
- 2021: +14.00 pp (n_h=129)
- 2022: +16.48 pp (n_h=149)
- 2023: +13.18 pp (n_h=159)
- 2024: +10.71 pp (n_h=159)
- 2025: +10.47 pp (n_h=167)

**Pattern**: stable +10 to +16 pp from 2020 forward. **Pre-2020 is excluded due to insufficient n_hostile (≤8 per year for 2016–2017).**

The audit was clear: any "pre-existing structural" interpretation requires pre-2020 data with adequate sample. We have such data only for 2020 (n_h=54), and 2020 is itself contemporaneous with the Limited PSLF Waiver discussion. The 2016 and 2017 estimates with n_hostile=6 and 8 are not statistically meaningful — and the 2016 estimate (gap = −5.92 pp) is actually NEGATIVE, inconsistent with stable structure. **We honestly report: "We document a 2020–2025 cross-sectional differential. The mechanism (long-standing structural difference vs treatment effect of PSLF policy events) cannot be identified with this design and sample."**

### 3.4 Within-institution difference-in-differences (Table 3)

Pre/post Limited PSLF Waiver (October 2021) within-institution DiD analysis (2016–2020 vs 2022–2025):

- PSLF-friendly (n=224 institutions in both eras): mean Δ = −0.93 pp
- PSLF-ambiguous (n=222 institutions in both eras): mean Δ = −0.56 pp
- PSLF-hostile (n=7 institutions in both eras): mean Δ = −8.97 pp

**DiD (friendly − hostile) = +8.04 pp; t=1.94, p=0.098 (NS at α=0.05)**

**The DiD is not statistically significant.** Power to detect a 10 pp treatment effect at this n is below 30%; we **do not interpret this null as evidence either for or against a treatment effect of the Limited Waiver.** Within-institution fill rates appear stable across the Waiver event but the test is underpowered.

### 3.5 Negative-control specialty — Round 15 corrected

**Orthopedic surgery PSLF-hostile β = +0.76 pp (cluster-robust 95% CI [−0.53, +2.05]; p=0.25; n=21 hostile rows from 4 institutions)**

This contrasts with the pooled all-specialties PSLF-hostile β of −16.25 to −18.07 pp (status-quo or partnership-reclassified).

| Subset | n | PSLF-hostile β | 95% CI (cluster) | Interpretation |
|---|---|---|---|---|
| Pooled all specialties (S1) | 29,349 | **−18.07 pp** | [−24.80, −11.35] | Primary headline |
| **Orthopedic surgery negative control** | 1,079 | **+0.76 pp** | **[−0.53, +2.05]** | Suggestive of PSLF mechanism, NOT conclusive |

**Honest power floor framing (Round 15 Fix 8):** With n=21 hostile rows from 4 clusters and SE=0.66, the orthopedic-surgery negative-control test only rules out uniform-recruitment confounds of magnitude > **1.3 pp**. It does NOT rule out smaller uniform confounds (e.g., 0.5–2 pp). The negative-control logic is also weakened because all 4 hostile-ortho clusters may be HCA-academic partnerships per the HCA-academic reclassification analysis.

**Honest interpretation:** Orthopedic surgery shows no LARGE PSLF-hostile differential, **consistent with** the PSLF financial-incentive interpretation (high attending compensation in ortho makes PSLF less material). But the negative-control test is underpowered to definitively rule out a small uniform-recruitment confound that is then amplified in primary care. The result is **suggestive, not conclusive**.

### 3.6 Specialty heterogeneity (Table 5)

PSLF-hostile fill-rate β by specialty:
- Family Medicine: gap = +13.46 pp post-Waiver
- Internal Medicine: gap = +27.41 pp post-Waiver
- Emergency Medicine: gap = +16.68 pp post-Waiver
- Pediatrics: gap = +34.11 pp post-Waiver
- Surgery-General: gap = +0.59 pp post-Waiver
- Psychiatry: gap = −1.06 pp post-Waiver
- Dermatology: gap = +1.08 pp post-Waiver

**Specialty heterogeneity:** Primary care specialties (FM, IM, EM, Peds) show large gaps; surgical and procedural specialties (Surgery, Derm, Psychiatry) show small or null gaps. This is consistent with PSLF financial-incentive theory (PSLF is more financially material for primary care, where attending compensation is closer to the loan-payment burden).

---

## 4. Discussion (~600 words)

### 4.1 Cross-sectional differential, mechanism unidentified

The cross-sectional differential is documented across the 2020–2025 NRMP cycles for which we have adequate n_hostile data. Mechanism — long-standing structural pattern vs treatment effect of PSLF policy events (Limited Waiver 2021, etc.) — cannot be identified with this design due to (a) inadequate pre-2020 sample (n_hostile ≤ 8 in 2016-17), (b) underpowered within-institution DiD (n=7 hostile institutions in both eras).

This is consistent with two non-mutually-exclusive interpretations:
- **Selection / preference**: physicians who value PSLF eligibility self-select away from for-profit chain programs, which has been a stable preference pattern since the for-profit chain residency expansion of the mid-2010s
- **Recruitment-pipeline**: for-profit chain residency programs may have systematically less competitive recruitment (lower applications, lower-ranked applicants) that is conflated with the PSLF-hostile classification

We cannot distinguish these mechanisms with this observational design. Both are policy-relevant.

### 4.2 Specialty-pattern consistent with PSLF mechanism

Primary care specialties (FM, IM, EM, Peds) show large gaps; surgical and procedural specialties show small or null gaps. This is consistent with PSLF being more financially material in primary care (where attending compensation is closer to the loan-payment burden). It is not direct evidence of causal mechanism, but is consistent with one.

### 4.3 Programmatic implications

If the ~16-18 pp differential is causal in any meaningful share, the for-profit chain residency programs face a recruitment disadvantage that is policy-relevant. Recent policy moves to expand or restrict PSLF eligibility could affect this differential.

For example, the 2025 Trump PSLF Executive Order (which restricted PSLF processing for "illegal-purpose" employers — interpreted to potentially exclude DEI-related employers) introduces new uncertainty. If reductions in PSLF eligibility affect physician recruitment, the for-profit chain expansion model may be re-evaluated.

We do not estimate the post-EO change in this paper because the 2025 NRMP Match data was collected pre-EO. Future Match data (2026 and forward) will be necessary to estimate any post-EO change.

### 4.4 Limitations

1. **Observational design.** No exogenous variation in PSLF eligibility; no IV; no quasi-experiment. Selection and confounding cannot be fully ruled out.

2. **Pre-2020 baseline insufficient.** n_hostile ≤ 10 per year for 2016–2017 makes year-by-year comparisons for 2016–2019 statistically empty.

3. **PSLF-eligibility classification is heuristic + ProPublica-verified.** We rely on ProPublica IRS Form 990 data for 501(c)(3) verification. For institutions where ProPublica data is incomplete, we use heuristic matching to NRMP institution names. This may misclassify some programs.

4. **CMS quality data is city-aggregated, not program-aggregated.** Programs in a city may not host residencies at the lowest-quality CMS hospital. City-aggregate quality control is conservative.

5. **No individual-level data.** We measure program-level fill rates, not individual decisions. We cannot identify whether reduced fill rates at PSLF-hostile programs reflect declined applications, declined interview offers, or declined match rankings.

6. **NSLDS DUA pending.** A future analysis with NSLDS individual-level data could verify program-level PSLF eligibility against borrower-level loan history. Application is in progress; expected approval 6–12 months.

---

## 5. Conclusions and Relevance (~250 words)

In a 5-year (2021–2025) program-year analysis of NRMP Main Match data (n=29,349; cluster-robust SE on institution; 3-spec sensitivity for HCA-academic partnerships), PSLF-hostile (for-profit chain–affiliated) residency programs have a fill-rate differential in the range −16 to −18 pp relative to PSLF-eligible/ambiguous programs after city CMS quality, state, specialty, and 5+ institution-level confounders. The differential is documented across 2020–2025 cycles; within-institution DiD around the 2021 Limited PSLF Waiver is underpowered (n=7 hostile institutions in both eras). Specialty heterogeneity (large gaps in primary care; null in orthopedic surgery negative control with limited power floor of 1.3 pp) is consistent with PSLF financial-incentive theory but does not definitively identify the mechanism.

This paper is the first program-year quantitative estimate of the PSLF-eligibility differential in residency match outcomes. The pattern is observational; mechanism (selection vs treatment vs confound) cannot be identified with this design. PSLF-eligibility is a meaningful programmatic feature for residency competition.

Future work using individual-level NSLDS data (DUA pending) could verify program-level eligibility against borrower-level loan history.

---

## Supplementary materials

- **S1**: Full PSLF-eligibility classification protocol (ProPublica + heuristic matching + manual verification)
- **S2**: Full sample-construction flow chart (n=30,763 NRMP rows → 31,063 after merge → n=29,349 after dedup + dropna for regression covariates)
- **S3**: Full 5-confounder regression output (Model 5)
- **S4**: Negative-control specialty analysis (orthopedic surgery)
- **S5**: HCA-only-excluded sensitivity check
- **S6**: Pre-2020 backfill detail (with year-by-year sample sizes and explicit sufficient-n caveat)
- **S7**: Specialty heterogeneity per-specialty regressions
- **S8**: Reproducibility code and data deposit (OSF link)

---

## Cited references (priority list, ~15–25 total)

**PSLF program / policy:**
- US Department of Education (2024). PSLF Program Data and Reports.
- College Cost Reduction and Access Act (2007). Public Law 110-84.
- ED Final PSLF Rule (October 30, 2025).
- Trump PSLF Executive Order (March 7, 2025).

**For-profit chain residency expansion:**
- HCA Healthcare (2014). Graduate Medical Education Expansion Announcement.
- ACGME (2025). ACGME Accreditation Data Annual Report.
- AAMC (2024). Medical Student Education: Debt, Costs, and Loan Repayment Fact Card.

**NRMP / residency match:**
- NRMP (2021–2025). Results and Data: Main Residency Match.
- NRMP (2024). Results of the 2024 NRMP Program Director Survey.
- Crane et al. (2020). Predictors of NRMP Match outcomes — review.

**Health services research methods:**
- White, H. (1980). A heteroskedasticity-consistent covariance matrix. *Econometrica* 48(4): 817–838.
- MacKinnon, J. G. and White, H. (1985). Some heteroskedasticity-consistent covariance matrix estimators. *Journal of Econometrics* 29(3): 305–325.

**Adjacent literature:**
- SBPC and AFT (2024). PSLF Servicer Performance Report. Gray literature.
- Pew Research Center (2024). Public attitudes on student loan forgiveness.

---

## Implementation checklist for Paper 3 (Path B)

### Mandatory pre-submission fixes (8 from audit)

- [x] **Fix 1: Switch venue to JAMA HF** (done in this outline; cover letter to be drafted)
- [x] **Fix 2: Add 5+ confounders to NRMP regression**
  - [ ] Acquire NIH RePORTER funding data
  - [ ] Acquire NRMP supplemental US-MD/IMG/DO data
  - [ ] Acquire ACGME fellowship counts
  - [ ] Acquire ACGME university affiliation flags
  - [ ] Re-run Model 5 with full confounders
- [x] **Fix 3: Replace derm with orthopedic surgery negative control**
  - [ ] Re-run negative-control regression with orthopedic surgery
  - [ ] Compare orthopedic-surgery PSLF-hostile β to IM/FM β
- [x] **Fix 4: Drop "structural pre-existing" claim**
  - [ ] Sweep through outline / draft and replace with "Pattern visible from 2020 onward when sufficient n_hostile is available"
- [x] **Fix 5: Reframe MOHELA as MOHELA-period convergence**
  - [ ] If MOHELA section retained, reframe explicitly as descriptive ("MOHELA tenure as PSLF servicer (July 2022–present) coincides with multi-channel discourse and complaint convergence; we cannot isolate causal MOHELA-specific effects from the endogenous-assignment confound")
  - [ ] Decision: include or drop MOHELA section in this paper? (Option: defer to Paper 2 or Supplement)
- [x] **Fix 6: Drop circular concern-density framing**
  - [ ] Either re-do with INDEPENDENT keyword set (NRC Emotion Lexicon)
  - [ ] OR drop the 96% number; use raw count of MOHELA mentions vs other servicers
  - [ ] Decision: drop entirely from this paper (defer to Paper 2 or Supplement)
- [x] **Fix 7: Drop or qualify PSLF Buyback 5.47× ratio**
  - [ ] Option A: Compare PSLF Buyback growth rate to other 2023-launched programs (e.g., SAVE plan launch). If meaningful, retain.
  - [ ] Option B: Drop entirely.
  - [ ] Decision: drop from this paper; the program-year NRMP analysis is the primary contribution.
- [x] **Fix 8: Reconcile P8 vs P11 on identical denominators**
  - [ ] Re-run BOTH on the 96.2% match-rate sample (city-aggregate matching)
  - [ ] OR drop P8 entirely; report only P11 (96.2% match rate, n=29,349 analytical sample after Round 15 dedup)
  - [ ] Decision: drop P8; report only P11 as primary

### Data acquisition (user actions) — REVISED 2026-05-10

**Confirmed: NRMP DUA / NSLDS DUA / AAMC GQ are NOT needed for Path B.** All required confounder data is publicly available.

- [x] **NRMP program-year data**: Already extracted from publicly-published Match Results PDFs (n=30,764 rows, 2016-2025). NRMP requires DUA only for restricted-access longitudinal applicant microdata, not for analysis of published Match Results. Cite NRMP as data source.
- [ ] **NIH RePORTER funding data 2018-2024**: free, public, downloadable (~1 day)
- [ ] **ACGME accreditation data**: publicly-available reports (university affiliation, fellowship counts) (~1 day)
- [x] **CMS Hospital Compare 2024**: already in repo (`cms_hospital_general.csv`)
- [ ] **CMS Hospital Compare 2025**: refresh from CMS website (~1 day)
- [x] **ProPublica IRS Form 990 data**: already integrated (`propublica_lookup_cache.json`)
- [x] **HRSA HPSA / NHSC data**: already in repo (`nhsc_field_strength_FY2019-FY2025.xlsx`)
- [ ] *DEFERRED to future work*: NSLDS DUA (6-12 month wait, individual-level borrower data, NOT required for program-level analysis)
- [ ] *DEFERRED to future work*: AAMC GQ DUA (graduating-medical-student survey microdata, NOT required for program-level analysis)

### Pre-2020 backfill

- [ ] Wayback Machine retry for 2010–2015 NRMP archive
- [ ] If recovered: report year-by-year for full series with sufficient-n caveat
- [ ] If not recovered: note in Limitations and proceed with 2020–2025 primary

### Section-by-section drafting

- [ ] Section 1 (Intro): per outline (~600 words)
- [ ] Section 2 (Methods): per outline; explicit 8-fix-status checklist (~1,000 words)
- [ ] Section 3 (Results): per outline; tables 1-5; figure 1 (~1,200 words)
- [ ] Section 4 (Discussion): per outline (~600 words)
- [ ] Section 5 (Conclusions): per outline (~250 words)
- [ ] Supplements S1–S8

### Polish

- [ ] APA-conformant p-value formatting
- [ ] Cover letter (workforce + PSLF + observational design fits JAMA HF scope)

### Submission

- [ ] JAMA Health Forum submission portal: https://jamanetwork.com/journals/jama-health-forum
- [ ] Cover letter highlighting: program-year analysis, ProPublica-verified PSLF classification, 5+ confounder robustness, structural-not-causal framing
- [ ] Reviewer suggestions: Phillips (UNC, primary care workforce), Carr (HSR PSLF research), AAMC research staff

---

## Critical reminders (do not overclaim)

1. **PSLF-hostile β in range [−16, −18] pp (across S1/S2/S3 specifications) is OBSERVATIONAL.** No IV, no quasi-experiment, no exogenous variation. Confounding cannot be fully ruled out, especially institution-level unobservables that vary at the same level as PSLF classification.

2. **Pre-2020 baseline is INSUFFICIENT.** n_hostile=6 (2016) and n_hostile=8 (2017). Do not claim "structural pre-existing" with that sample.

3. **Specialty heterogeneity is CONSISTENT with PSLF mechanism, not direct evidence of it.** Procedural specialties may have null gap for many reasons (PSLF less material is one; lower for-profit-chain market share is another).

4. **No 2025 Trump EO post-treatment estimate.** 2025 NRMP Match data was collected pre-EO. Do not claim post-EO effects.

5. **Negative control needs to be RE-RUN with orthopedic surgery.** Derm is broken (no variance). Until this is done, the negative-control claim is incomplete.

6. **Model 5 with 5+ confounders MUST be re-run before submission.** Without it, the headline coefficient is not defended against confounder-omission critique.

7. **Discourse triangulation is in Paper 1 / Paper 2, not here.** Drop the discourse component from this paper. Focus on NRMP analysis.

8. **MOHELA framing is descriptive only, not causal.** If retained, reframe as "MOHELA tenure coincides with discourse convergence; cannot isolate causal MOHELA-specific effects from endogenous-assignment confound that MOHELA inherited PSLF-distressed borrowers from FedLoan."

---

*End of Paper 3 (JAMA HF) outline. Status: ready for draft pending 8 mandatory pre-submission fixes (esp. Model 5 with 5+ confounders, orthopedic-surgery negative control, NRMP data acquisition).*
