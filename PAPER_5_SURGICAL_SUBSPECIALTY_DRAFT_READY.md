# Paper 5 Draft-Ready Template — Surgical-subspecialty PSLF comparison (R17++ #6 revised venue + geographic boost)

**Status:** Ready to draft; **R17++ #6 boost: ADD GEOGRAPHIC + WORKFORCE-POLICY CONTEXT (HRSA HPSA + USDA RUCA + state Medicaid)** + revised venue target
**Target venue (R17++ #6 revised primary):** ***Neurosurgery* (Wolters Kluwer)** — flagship NS journal; has Health Policy section; realistic ~30-40% acceptance with NS as lead subspecialty
**Target venue (R17++ #6 secondary):** ***World Neurosurgery*** (~40-50% acceptance backup)
**Target venue (R17++ #6 reach):** *JAMA Surgery* (~15-25% if attempted as primary — too ambitious as primary but acceptable as reach for one attempt)
**Length:** 2,000-2,500 words (short report)
**Working title:** *Public Service Loan Forgiveness Eligibility Across US Surgical Subspecialty Residency Programs, 2021–2026: Institutional Concentration of Hostile Programs at HCA Healthcare-Affiliated Facilities* (with subtitle "Geographic and Workforce-Policy Context" added if Option C boost is applied)

## R17++ #6 BOOST STRATEGY (added 2026-05-17 final)

**Why revise:** R17++ #5 targeted *JAMA Surgery* primary which was too ambitious for a non-causal descriptive paper. *JAMA Surgery* desk-rejects 60-70% of submissions; without a strong clinical implication, the HCA-concentration finding is interesting but not enough. Boost strategy: (a) downgrade primary to *Neurosurgery* (Wolters Kluwer) for realistic acceptance + NS-match strategic visibility; (b) add geographic + workforce-policy analysis to strengthen the policy framing.

**Boost: ADD GEOGRAPHIC ANALYSIS (~3-5 days; all free TIER 1 data per `DATA_ACQUISITION_PLAN_R17pp6.md`):**

1. **HRSA Health Professional Shortage Area (HPSA) designation** — by county/state. Free CSV at https://data.hrsa.gov/topics/health-workforce/shortage-areas. ~1 day merge with institution geocoordinates. Are HCA-affiliated PSLF-hostile surgical programs concentrated in HPSAs or non-HPSAs?
2. **USDA Rural-Urban Commuting Area (RUCA) codes** — county-level urbanicity. Free at https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/. ~1 day. Where geographically are the HCA-Kansas-City-style multi-subspecialty concentrations?
3. **KFF Medicaid Expansion Status tracker** — state-level health-policy variable. Free at https://www.kff.org/medicaid/. ~0.5 day. Are PSLF-hostile programs concentrated in non-Medicaid-expansion states?
4. **U.S. Census Bureau county demographics** — socioeconomic context. Free Census API. ~1 day.

**Total boost effort:** 3-5 days of data engineering + ~3 weeks of paper writing.

**New section in paper:** §5.2 "Geographic and Workforce-Policy Context of PSLF-Hostile Surgical-Subspecialty Training" — maps HCA-Healthcare-affiliated institutions against HPSA, RUCA, and Medicaid-expansion-state variables. Strengthens the "for-profit chain consolidation of surgical training has workforce-policy implications" framing.

**Realistic acceptance:** *Neurosurgery* (WK) primary ~30-40%; *World Neurosurgery* secondary ~40-50%; *JAMA Surgery* ~15-25% if attempted as reach. Combined "in print by ERAS" probability ~70-75%.

---

# Original outline below — to be expanded per R17++ #6 geographic boost during drafting

**Status (LEGACY R17++ #5):** Ready to draft (data feasibility verified 2026-05-17 for both NS-only and surgical-subspecialty comparison framings; **reframed from NS-only descriptive to surgical-subspecialty comparison after rigorous validity review** — see PROJECT_INDEX.md R17++ #5 audit history row)
**Target venue (LEGACY R17++ #5 primary):** *JAMA Surgery* (cross-surgical-subspecialty scope fits the venue)
**Target venue (LEGACY R17++ #5 secondary):** *Annals of Surgery* (broader surgical audience)
**Target venue (LEGACY R17++ #5 tertiary):** *Neurosurgery* (Wolters Kluwer; if framed with NS as primary subspecialty)
**Target venue (LEGACY R17++ #5 backup):** *World Neurosurgery* / *Journal of Surgical Education*
**Length:** 2,000-2,500 words (short report)
**Working title:** *Public Service Loan Forgiveness Eligibility Across US Surgical Subspecialty Residency Programs, 2021–2026: Institutional Concentration of Hostile Programs at HCA Healthcare-Affiliated Facilities*

**Added:** 2026-05-17 (R17++ #4) — original NS-only descriptive framing. **Reframed 2026-05-17 (R17++ #5)** after rigorous validity review surfaced that the NS-only "99.2% PSLF-eligible" headline is borderline trivial to NS audiences; surgical-subspecialty comparison creates a stronger novel finding.

---

## Why this paper (reframed)

The R17++ #4 original framing ("99.2% of US NS programs are PSLF-eligible") would have been a descriptively accurate but substantively unsurprising paper. NS faculty already know that NS training is academic-medical-center based; reviewers at *Neurosurgery* / *JAMA Surgery* would ask "what's the news here?"

The **surgical-subspecialty comparison framing** (R17++ #5 reframe) is substantively stronger:

1. **Genuinely novel sub-finding**: **All 14 PSLF-hostile surgical-subspecialty residency programs are HCA Healthcare-affiliated.** HCA Healthcare Kansas City alone hosts 4 different surgical subspecialty residencies (NS, Plastic Surgery, Otolaryngology, Orthopedic Surgery) plus Surgery-General — making it the most concentrated multi-subspecialty PSLF-hostile training site in the US.

2. **Workforce-policy implication**: For the ultra-competitive surgical subspecialties (Vascular, Thoracic, Plastics, NS, ENT) hostile-program fill rate is 100% every year — suggesting PSLF eligibility does NOT deter applicants for ultra-competitive specialties. Surgery-General shows variable fill rates (0.5-1.0) at the 7 hostile institutions — the only surgical subspecialty where PSLF eligibility may actually matter for recruitment.

3. **Trump-EO-relevant**: Post-EO workforce planning at the surgical-subspecialty level requires institution-level PSLF eligibility classification. This paper provides it for the surgical-subspecialty universe.

4. **NS-match strategic value preserved**: NS is the lead subspecialty in the comparison; the paper is co-authored by NS faculty mentor; reviewers will see NS-specific content.

## The data-verified headline (2026-05-17 surgical-subspecialty feasibility script)

| Surgical subspecialty | n program-years | n institutions | PSLF-hostile rate | n hostile institutions | Hostile-program fill rate |
|---|---|---|---|---|---|
| **Surgery-General** | 3,607 | 322 | **3.05%** | 7 (all HCA-affiliated) | variable 0.5–1.0 |
| **Orthopaedic Surgery** | 1,288 | 193 | **2.02%** | 4 (all HCA-affiliated) | 100% |
| **Plastic Surgery (Integrated)** | 539 | 93 | **1.11%** | 1 (HCA Kansas City) | 100% |
| **Neurological Surgery** | 701 | 121 | **0.86%** | 1 (HCA Kansas City) | 100% |
| **Otolaryngology** | 818 | 130 | **0.73%** | 1 (HCA Kansas City) | 100% |
| **Vascular Surgery** | 445 | 83 | **0.00%** | 0 | N/A |
| **Thoracic Surgery** | 216 | 37 | **0.00%** | 0 | N/A |

**Single most concentrated finding:** HCA Healthcare Kansas City hosts 4 surgical subspecialty residencies (Neurological Surgery, Plastic Surgery (Integrated), Otolaryngology, Orthopedic Surgery) plus Surgery-General — all PSLF-hostile, all at 100% fill every year 2021–2026. This is the most institutionally concentrated multi-subspecialty PSLF-hostile training site in the US.

## Section structure (JAMA Surgery short-report format)

### Abstract (~250 words; structured)

**Importance:** Public Service Loan Forgiveness affects ~$200K-$400K of typical surgical-subspecialty resident debt. Whether competitive surgical subspecialty training is structurally PSLF-eligible — and how PSLF-hostile programs are distributed across subspecialties — has not been quantitatively characterized.

**Objective:** Characterize PSLF eligibility of US surgical-subspecialty residency programs across 2021–2026; identify institutional concentration of PSLF-hostile programs.

**Design:** Cross-sectional analysis of NRMP Main Match Program Results 2021–2026 (n=7,614 surgical-subspecialty program-years from 7 subspecialties across 979 unique institutions). PSLF eligibility classified using ProPublica IRS Form 990 verification (PSLF-eligible if 501(c)(3) or government; ambiguous if private/LLC; PSLF-hostile if for-profit chain-affiliated).

**Main Outcomes and Measures:** Subspecialty-stratified PSLF-eligibility rates; fill rates at PSLF-hostile institutions; institutional concentration of PSLF-hostile multi-subspecialty training sites.

**Results:** Surgical-subspecialty PSLF-hostile rates ranged from 0% (Vascular, Thoracic) to 3.05% (Surgery-General); **all 14 PSLF-hostile surgical-subspecialty institutions are HCA Healthcare-affiliated**. HCA Healthcare Kansas City alone hosts 5 surgical training programs (NS, Plastics, ENT, Ortho, Surgery-General), all PSLF-hostile, all at 100% fill every year. For ultra-competitive subspecialties (Vascular, Thoracic, Plastics, NS, ENT) PSLF-hostile programs maintain 100% fill, suggesting PSLF eligibility does not deter applicants. Surgery-General hostile programs show variable fill rates (0.5–1.0 range), the only surgical subspecialty where PSLF eligibility may meaningfully affect recruitment.

**Conclusions:** Surgical-subspecialty training is overwhelmingly PSLF-eligible; rare exceptions are concentrated at HCA Healthcare-affiliated facilities. The single multi-subspecialty PSLF-hostile training cluster at HCA Kansas City warrants attention from surgical-workforce policymakers post-Trump EO 14235.

### Introduction (~300 words)

[INSERT BLOCK: surgical-subspecialty debt context; Trump EO 14235 + ED Final Rule; for-profit chain expansion since 2014 (Lassner et al. 2022 ×2, ACGME 2025, HCA Healthcare 2014); gap in institution-level PSLF eligibility classification for surgical subspecialties.]

### Methods (~400 words)

**Data:** NRMP 2021–2026 (n=7,614 surgical-subspecialty program-years from 7 subspecialties); ProPublica IRS Form 990 PSLF eligibility classification per `DATASET_DEPOSIT_PLAN.md` (Dryad/Zenodo DOI to cite at submission). Three sensitivity specifications (S1/S2/S3) for HCA-academic partnerships — note: 0 surgical-subspecialty hostile programs are HCA-academic partnerships, so S1/S2/S3 identical for this analysis.

**Statistical analyses:** Descriptive cross-subspecialty comparison of PSLF-eligibility rates + fill rates by PSLF class. For Surgery-General (only subspecialty with n_hostile≥5 institutions): simple fill-rate comparison test (Mann-Whitney U) between hostile and eligible/ambiguous program-years. No formal regression given small n_hostile in most subspecialties.

**Reproducibility:** R17 CMS-merge dedup applied; `RUN_AUDITS.ps1` verifies dedup-fix presence in all 10 Model 5 source scripts.

### Results (~600 words; 2 tables, 2 figures)

**Table 1:** Surgical-subspecialty PSLF-eligibility distribution 2021–2026 (the data-verified table above)

**Table 2:** HCA Healthcare facility-level concentration of PSLF-hostile surgical-subspecialty training (institution × subspecialty matrix with fill rates)

**Figure 1:** Bar chart of PSLF-hostile rate × subspecialty, sorted descending; HCA-affiliation labels

**Figure 2:** US choropleth of surgical-subspecialty hostile-institution density by state; highlighting HCA Kansas City as the multi-subspecialty concentration

[INSERT BLOCK: Narrative interpretation of cross-subspecialty pattern.]

### Discussion (~500 words)

**Three main implications:**

1. **Surgical-subspecialty training is structurally PSLF-eligible** (96.95% to 100% across subspecialties). Surgical-subspecialty residents at the vast majority of US training programs can plan PSLF strategy with high confidence in qualifying-employer status. The post-EO landscape does not fundamentally alter this for the surgical subspecialties.

2. **HCA Healthcare as the single source of PSLF-hostile surgical-subspecialty training:** All 14 PSLF-hostile surgical-subspecialty residency institutions across our 6-year window are HCA Healthcare-affiliated. HCA Kansas City hosts the most concentrated multi-subspecialty PSLF-hostile training site (5 programs including NS, Plastics, ENT, Ortho, Surgery-General). The institutional concentration of for-profit-chain surgical-subspecialty training warrants attention from surgical-workforce policymakers and ACGME-accreditation reviewers.

3. **PSLF eligibility does not deter applicants for ultra-competitive subspecialties** (Vascular, Thoracic, Plastics, NS, ENT all show 100% fill at hostile programs every year). Surgery-General is the exception — its hostile programs show variable fill rates (0.5–1.0 range), consistent with a recruitment-relevant PSLF eligibility effect at lower-prestige surgical training. This pattern aligns with the broader cross-specialty −18 pp PSLF-hostile fill-rate differential in Paper 3 (companion publication, JGME), where the cross-specialty average is dominated by Internal Medicine + Family Medicine + Emergency Medicine recruitment dynamics.

**Limitations:** Cross-sectional + descriptive; insufficient n_hostile for surgical subspecialty-stratified regression except for Surgery-General. Pre-2020 backfill sparse. NSLDS-linked borrower-level analysis pending (DUA application; see `NSLDS_DUA_APPLICATION_CHECKLIST.md`).

**Future work:** (1) Specialty-by-specialty PSLF utilization rates among trainees, using NSLDS borrower-level data; (2) Post-EO follow-up at 2027+ NRMP cycles to detect any fill-rate response to Trump EO 14235 + ED Final Rule (effective July 2026); (3) Qualitative analysis of HCA Kansas City multi-subspecialty PSLF-hostile training cluster (case study).

### References (~25 citations, all R17++ verified)

Same R17++ verified citation set as Paper 3 plus surgical-subspecialty-specific references. See `MASTER_REFERENCE_LIST.md` for full list.

---

## Strategic value (medical student NS match — REFRAMED)

**Original NS-only framing:** weak — "99.2% PSLF-eligible" was descriptively trivial to NS audiences.

**Surgical-subspecialty comparison framing (R17++ #5):**
- **Stronger novel finding:** HCA-affiliated institutional concentration of PSLF-hostile surgical training across multiple subspecialties (NS + Plastics + ENT + Ortho + Surgery-General all at one HCA facility)
- **NS-specialty-relevance preserved:** NS is included in the cross-subspecialty comparison; can be co-authored by NS faculty mentor
- **Broader venue eligibility:** *JAMA Surgery* primary (vs the NS-only paper that wouldn't have cleared the *JAMA Surgery* bar) — substantially higher prestige + visibility for NS PDs at top programs
- **Acceptance probability roughly doubles** at premier venues (JAMA Surg / Annals of Surgery): from ~15-25% (NS-only descriptive) to ~25-40% (cross-subspecialty comparison with novel HCA concentration finding)
- **Conference abstract continuity preserved:** the AANS Annual Meeting abstract (Oct 2026 deadline) remains the same NS-relevant slice extracted from this broader paper

## Pre-submission checklist

- [ ] Re-run analysis with explicit Surgery-General PSLF-hostile vs eligible/ambiguous fill-rate comparison test (Mann-Whitney U or Welch's t-test)
- [ ] Generate Figure 1 (bar chart) + Figure 2 (US choropleth showing HCA-affiliated concentration)
- [ ] Compute institution-level descriptives for HCA Kansas City multi-subspecialty cluster
- [ ] Confirm faculty co-author (NS faculty during research year + PSLF-project senior author)
- [ ] Cite deposited classification dataset DOI in Methods (after Dryad/Zenodo submission)
- [ ] Cite Paper 3 (JGME) at submission once accepted
- [ ] Verify all 25+ citations at author level (R17++ rule)

## Expected timeline (research year July 2026 onwards)

- **Aug 2026 (Week 1-2 of research year):** Re-run cross-subspecialty analysis with formal Mann-Whitney comparison for Surgery-General; generate figures (~1 week)
- **Sep 2026:** Draft Background + Methods + Results (~2 weeks)
- **Oct 2026:** Draft Discussion + co-author review (~2 weeks)
- **Nov 2026:** Submit to *JAMA Surgery* (primary)
- **Jan-Mar 2027:** Decision (typically 2-4 months at JAMA Surgery)
- **Apr-Jun 2027:** Revisions
- **Jul-Aug 2027:** In print before ERAS Sept 2027

Total: **~3 weeks of effective writing** plus normal review/revision cycle.

## Acceptance probability (R17++ #5 revised, honest)

- *JAMA Surgery* primary: **25-35%** (cross-subspecialty + novel HCA concentration finding)
- *Annals of Surgery* secondary: **20-30%**
- *Neurosurgery* (Wolters Kluwer): **30-40%** (with NS as the lead subspecialty in the narrative)
- *World Neurosurgery* backup: **40-50%**

## Source files

- `nrmp_program_level_2021_2026.csv` — primary data (filter to surgical subspecialties)
- `scripts/explore_surgical_subspecialty_feasibility.py` — feasibility verification script
- `PSLF-Discussion-Analysis/paper5_surgical_subspecialty_feasibility_results.txt` — saved output
- `scripts/explore_neurosurgery_ns_feasibility.py` + `paper5_neurosurgery_feasibility_results.txt` — original NS-only feasibility (preserved for transparency; this is the data the R17++ #4 NS-only framing was based on)
- `nrmp_institution_pslf_classification.csv` + `nrmp_institution_pslf_verified.csv` — PSLF classification
- `PAPER_3_DRAFT_READY.md` — parent methodology (cross-specialty fill-rate differential)
- `DATASET_DEPOSIT_PLAN.md` — citable dataset DOI plan
- `NSLDS_DUA_APPLICATION_CHECKLIST.md` — long-horizon PGY-1 follow-up enabler
- `MASTER_LOCKED_NUMBERS.md` + `MASTER_REFERENCE_LIST.md`
