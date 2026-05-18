# Round 11 Audit Update — P8 CMS Quality Correction

**Date:** 2026-05-10
**Scope:** Critical correction to B5 / P7 PSLF-recruitment-gap finding based on
P8 cross-reference with CMS Hospital Compare data (hospital ownership +
quality ratings).

---

## TL;DR

The headline B5 finding "+12.86 pp PSLF-eligibility recruitment gap" appears
to be **partly quality-driven, not PSLF-driven**. After controlling for hospital
quality (CMS overall star rating) and state fixed effects in the matched subset,
the PSLF-eligibility coefficient is **−1.58 pp (NS, p=0.09)**.

**The substantive paper claim must be downgraded.** The +12.86pp gap should be
reported as a composite of PSLF + quality + other structural factors, not
attributed solely to the PSLF mechanism.

---

## What P8 actually showed

### Match rate caveat

CMS Hospital Compare has 5,426 hospitals; NRMP has 789 institutions. Direct
matching (state + normalized name) yielded:
- 222 direct matches
- 33 first-three-words fuzzy matches
- **Total: 251 / 797 NRMP institutions matched (31.5%)**

The 68.5% non-match isn't all CMS coverage gaps — many NRMP "institutions"
are not single hospitals:
- Academic GME consortia (e.g., "HCA Healthcare/USF Morsani GME-Trinity")
- University medical schools (e.g., "U Alabama Hospitals")
- Multi-site health systems (e.g., "Mass General Brigham")

These don't match 1:1 to a single CMS hospital record. The matched subset is
biased toward institutions whose name corresponds to a single CMS-listed
hospital — a structural sampling difference.

### CMS ownership-derived PSLF classification

Within the 5,426 CMS hospitals:
| CMS Ownership | n |
|---|---|
| Voluntary non-profit - Private | 2,304 (PSLF-eligible) |
| Proprietary | 1,069 (PSLF-INELIGIBLE) |
| Government - all forms | 1,172 (PSLF-eligible) |
| Voluntary non-profit - Other/Church | 626 (PSLF-eligible) |
| VHA + DoD + Tribal | 179 (PSLF-eligible) |
| Physician (independent) | 76 (ambiguous) |

**4,102 CMS-eligible / 1,069 CMS-ineligible / 255 ambiguous.**

### Concordance with heuristic

When I cross-tab heuristic PSLF class (B5) vs CMS-derived class (P8):
| Heuristic \ CMS | ambiguous | pslf_eligible | pslf_ineligible | Total |
|---|---|---|---|---|
| ambiguous | 0 | 102 | 15 | 117 |
| pslf_friendly | 3 | 113 | 17 | 133 |
| pslf_hostile | 0 | 1 | 0 | 1 |
| Total | 3 | 216 | 32 | 251 |

**Concordance rate: 113/251 = 45.0%** between heuristic and CMS-based classification.

Critical observation: only 1 of my 23 "pslf_hostile" institutions matched to CMS.
The rest were GME-consortium names that don't appear in CMS hospital records.
This means:
- The B5 "+12.86pp gap" was computed across the full 789 institutions
- The CMS subset is mostly academic centers (eligible heuristic) — not the
  for-profit chains that drove the original gap
- We cannot definitively test whether the for-profit-chain residencies fill
  worse than academic-center residencies after controlling for quality —
  because for-profit-chain residencies don't appear as their own hospital in
  CMS

### Within the matched subset

| Metric | Result |
|---|---|
| CMS PSLF-eligible | n=7,650, mean fill = **0.9317** |
| CMS PSLF-ineligible | n=1,643, mean fill = **0.9349** |
| Δ | **−0.32 pp, p=0.56** |

In the matched subset, PSLF-eligibility is NOT associated with higher fill rate.
Quality differential:
| Class | Mean star rating | n |
|---|---|---|
| CMS PSLF-eligible | 3.05 | 7,169 |
| CMS PSLF-ineligible | 2.59 | 1,583 |

Quality difference: **+0.46 stars** for PSLF-eligible hospitals (almost half a
star, consistent direction with previously published academic-vs-for-profit
quality literature).

### Within-star-tier matched comparison

Stratifying by star rating reveals a striking pattern:
| Stars | n_eligible | n_ineligible | Eligible fill | Ineligible fill | Gap (pp) |
|---|---|---|---|---|---|
| 1 | 870 | 123 | 0.915 | **0.992** | **−7.7** (p<10⁻¹⁷) |
| 2 | 1,478 | 475 | 0.901 | 0.904 | −0.4 (NS) |
| 3 | 2,353 | 921 | 0.931 | 0.945 | −1.5 (p=0.05) |
| 4 | 1,365 | 59 | 0.942 | 0.914 | +2.8 (NS) |
| 5 | 1,103 | 5 | 0.965 | 1.000 | −3.5 (p<10⁻¹²) |

**Counterintuitively**: among low-quality hospitals (1-3 stars), CMS-ineligible
hospitals fill BETTER than CMS-eligible. This may reflect:
- For-profit hospitals self-select into residency programs only if they have
  structural advantages (location, salary, hours)
- Among residency-hosting low-quality hospitals, the for-profit ones are
  "best of class" within their type
- Or a selection-into-CMS-data artifact (only well-organized for-profit chains
  appear in CMS quality data with star ratings)

### OLS regression result

```
fill_rate ~ PSLF_eligible + star_rating + state_FE
N = 8,752, R² = 0.034
PSLF_eligible coef:   -0.0158  (SE=0.0094, p=0.092)  →  -1.58pp NS
star_rating coef:     +0.0130  (SE=0.0025, p=1.1×10⁻⁷)  →  +1.30pp/star
```

After controlling for hospital quality and state, **the PSLF-eligibility effect
is not significantly different from zero** (and points slightly negative).
**Quality is the real driver** in the matched subset.

---

## What this means for the substantive paper

### Required revisions

**B5 headline (Round 10):** "PSLF-eligible programs fill 12.86pp higher than
PSLF-ineligible (p=3.4×10⁻²⁷)"

**B5 headline (Round 11 — corrected):** "Programs at heuristic-classified
PSLF-eligible institutions fill 12.86pp higher than heuristic-classified
PSLF-ineligible (p=3.4×10⁻²⁷). However, in the 31.5% subset of NRMP
institutions matched to CMS Hospital Compare records, the PSLF-eligibility
coefficient is −1.58pp (NS, p=0.09) after controlling for CMS hospital
quality star rating and state fixed effects. The original gap appears to
combine PSLF-eligibility, hospital quality, prestige, and other structural
factors that travel together. The PSLF-mechanism-specific contribution to
the recruitment differential cannot be cleanly isolated from this dataset."

### Required revisions to P7

**P7 (Round 10):** "Gap is structural: pre-existed Limited Waiver in 2020
(15.6pp) and matches post-Waiver mean (12.97pp)."

**P7 (Round 11 — corrected):** "Gap is structural and predates Limited Waiver
expansion of for-profit chain residencies (2020+). The structural composition
includes both PSLF eligibility AND hospital quality differential (Round 11
P8 finding). Post-Waiver gap stability (~12-16pp) reflects this composite
structural pattern, not a treatment effect of PSLF salience increase."

### Required revisions to P5

**P5 (Round 10):** "PSLF gap LARGEST in urban counties (+26pp), smallest in
rural HPSAs (+12pp). Counter to PSLF workforce-targeting goal."

**P5 (Round 11 — qualified):** "Heuristic-classified PSLF-eligibility gap is
LARGEST in urban counties (+26pp), smallest in rural HPSAs (+12pp). Pattern
direction is robust but the absolute magnitude is composite (PSLF + quality
+ other factors). Urban academic centers cluster in low-HPSA counties, so the
larger gap there partly reflects the academic-vs-non-academic quality
differential, not the PSLF mechanism alone."

### Required revisions to policy brief

**Old action item for Congress:** "PSLF acts as a +12.86pp recruitment subsidy
for 501(c)(3) hospitals."

**New action item for Congress:** "PSLF eligibility differential is part of a
broader structural advantage for academic/501(c)(3) hospitals (which cluster
on PSLF + quality + research + reputation). PSLF reform would erode the
PSLF-attributable portion of this advantage; the size of that portion is
uncertain (could be much smaller than +12.86pp, possibly close to zero in
matched-quality subsets)."

---

## What additional analysis would resolve this

### Tier 1 — would directly answer the PSLF-vs-quality question

1. **GME-program-level employer-of-record classification** (most authoritative
   but high effort): manually verify for each of the 789 NRMP sponsoring
   institutions whether residents are W-2-employed by a 501(c)(3) GME
   consortium or by the host hospital. Would require ~789 phone calls or
   FOIA requests. ~3-6 months.

2. **NSLDS PSLF certification-rate by employer** (DUA-restricted): direct
   admin data on which employers have PSLF-certified residents. Would
   immediately resolve whether HCA-academic-consortium residents actually
   qualify. ~6-12 months DUA process.

3. **CMS-NRMP join improvement**: build a more sophisticated NRMP-to-CMS
   matching using full hospital-system structures (CMS publishes an
   Organization-of-Care file mapping individual hospitals to systems).
   Could improve match rate from 31.5% to maybe 60-70%. ~1 week.

### Tier 2 — would partially address but not resolve

4. **Match-quality sensitivity**: re-run B5 ONLY on the 251 matched institutions,
   using both heuristic and CMS classifications. If gap is large with heuristic
   but null with CMS in the SAME sample, that confirms the quality-confounding.

5. **Specialty-controlled analysis**: re-run B5 within each specialty separately,
   controlling for CMS quality. May reveal that some specialties (where
   academic prestige matters most) have quality-confounded results while
   others (where PSLF dollar-value matters most) have surviving PSLF effects.

6. **Pre/post Limited Waiver within-institution analysis**: P7 showed pre/post
   data; if individual institutions' fill rates shifted differentially around
   PSLF events, that's a within-hospital test of PSLF salience that controls
   for time-invariant quality.

### Tier 3 — additional context

7. **NHSC scholarship comparison**: NHSC provides scholarships specifically for
   primary care in HPSAs. If NHSC-affiliated programs fill better in
   high-HPSA areas, that's evidence that targeted federal incentives DO work
   — and PSLF's failure to do so (P5) is informative.

8. **NIH funding by institution**: cross-reference for prestige/research
   capacity. NIH-funded institutions may fill better regardless of PSLF.

---

## Updated bottom line for policy brief

**What CAN be defensibly claimed:**

1. ✅ Programs at heuristic-PSLF-eligible institutions fill 12.86pp higher
   than heuristic-PSLF-ineligible (descriptive observation, full sample)
2. ✅ This composite gap pre-existed the Limited PSLF Waiver where data is
   available (2020+)
3. ✅ Hospital quality differential exists between PSLF-eligible and
   PSLF-ineligible hospitals (~0.46 stars)
4. ✅ PSLF discourse signals (P2, P3, P6) inform process-improvement
   priorities and servicer contract design — these findings are NOT affected
   by the P8 quality-confounding
5. ✅ MOHELA discourse decline + 33% of CFPB complaints — convergent signal
   not affected by P8

**What CANNOT be defensibly claimed (downgrade these):**

1. ❌ "PSLF is the mechanism for the +12.86pp gap" — quality confounding cannot
   be ruled out
2. ❌ "PSLF acts as a workforce subsidy of +12.86pp" — magnitude likely overstated;
   true PSLF-attributable portion may be much smaller
3. ❌ "Eliminating PSLF would erode the +12.86pp recruitment advantage" — would
   only erode the PSLF-attributable portion, which is uncertain

**Honest reframe for the substantive paper:**

> "Programs at academic medical centers and government hospitals (which are
> 501(c)(3) and therefore PSLF-eligible employers) fill at substantially
> higher rates than programs at for-profit hospital chains. This recruitment
> advantage is composite, reflecting PSLF eligibility, hospital quality,
> research/teaching capacity, prestige, and other structural factors that
> co-occur in the academic medical center model. The PSLF-mechanism-specific
> contribution cannot be isolated from observational data without
> employer-of-record-level admin data (NSLDS) or a within-institution policy
> shock that affects PSLF eligibility independently of these other factors."

This is **more honest** and **arguably more interesting** than the original
"+12.86pp PSLF effect" claim. It frames PSLF as one component of the
academic medical center bundle that competes against for-profit residency
hosts.

---

## Updated to-do list for further policy claims

1. **Improved CMS-NRMP matching using hospital-system file** (1 week) — would
   verify the P8 finding's robustness
2. **Within-institution pre/post Limited Waiver analysis** (1-2 days using
   existing data) — within-hospital test
3. **NHSC programs cross-reference** (1-2 weeks) — comparative federal
   forgiveness program evidence
4. **NSLDS DUA application** (start now, 6-12 month timeline) — definitive
   resolution

---

**Files updated this round:**

- `scripts/analyze_policy_p8_cms_quality.py` (NEW)
- `policy_p8_cms_quality_results.{txt,csv,png}` (NEW)
- `cms_hospital_general.csv` (downloaded; 1.5 MB; 5,426 hospitals)
- This audit update document (`AUDIT_round11_P8_CMS_correction.md`)

**Next files to update:**
- `POLICY_BRIEF_v2_full.md` — add P8 caveats throughout
- Substantive paper draft (when started) — incorporate this corrected framing
