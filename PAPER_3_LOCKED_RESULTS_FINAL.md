# Paper 3 LOCKED Results — POST-2026-NRMP, POST-AUDIT (2026-05-10 final)

This is the corrected and finalized one-page summary of Paper 3 substantive results, after:
1. Round 16 strengthener (cluster-robust SE + wild-cluster bootstrap on 2021-2025 data)
2. 2026 NRMP data integration (released March 2026)
3. Round 16 audit (rejected my dramatic "Trump-EO eliminated PSLF differential" claim)
4. Honest reframing as multi-year trend documentation

**This document supersedes `PAPER_3_LOCKED_RESULTS_2026-05-10.md`.**

---

## Headline finding (POST-AUDIT honest framing)

**Cross-sectional differential** (pooled 2021-2025, pre-Trump-EO):
- PSLF-hostile programs have a fill-rate **−16 to −18 pp lower** than ambiguous (reference) programs, robust across HCA-academic-partnership classification specifications, with cluster-robust SE on institution and wild-cluster bootstrap (Webb 6-point, B=2,000) confirmation per Cameron-Miller (2015).

**Multi-year trend** (2021-2026):
- The PSLF-hostile fill-rate gap has been narrowing every year since 2022:
  - 2021: −14.00 pp
  - 2022: −16.48 pp (peak)
  - 2023: −13.18 pp
  - 2024: −10.71 pp
  - 2025: −10.47 pp
  - **2026: −7.03 pp**
- Linear time trend on PSLF-hostile programs: +1.6 pp/year improvement (SE=1.0; p=0.11)
- 2026 narrowing of +3.44 pp continues this trajectory

**Trump-EO causal interpretation: NOT SUPPORTED**
- 2026 indicator beyond linear time trend = +2.98 pp (SE=4.05; **p=0.46, NS**)
- The 2026 narrowing is statistically indistinguishable from continuation of the pre-existing trend
- Plausible mechanisms (HCA program maturation, applicant supply-side changes, secular workforce shifts, marginal Trump-EO contribution) cannot be distinguished with this design

---

## Cross-sectional regression (2021-2025 pooled, status-quo specification)

**Sample: n=29,349 program-year rows; 789 institutions; 28 specialties**

| Specification | n_hostile_inst | n_hostile_rows | PSLF-hostile β | 95% CI (cluster) | Wild-cluster bootstrap p |
|---|---|---|---|---|---|
| **S1: Status quo (all 23 hostile)** | 23 | 763 | **−18.07 pp** | [−24.80, −11.35] | **<0.0005** |
| **S2: HCA-academic reclassified as ambiguous** | 9 | 358 | **−16.25 pp** | [−21.66, −10.83] | **0.017** |
| **S3: Drop HCA-academic partnerships** | 9 | 358 | **−17.14 pp** | [−22.48, −11.80] | **0.006** |

**HCA-academic partnership ambiguity**: 14 of 23 hostile institutions are HCA-academic partnerships (10 with USF Morsani, 2 with U Miami, 1 with U Houston, 1 with VCOM). Resident W-2 employer determines actual PSLF eligibility but cannot be determined from this design. Three sensitivity specifications bracket the plausible range.

---

## Multi-year trend analysis (NEW post-2026-data)

### Year-by-year fill rates

| Year | n_hostile | Hostile fill | Friendly fill | Gap (pp) |
|---|---|---|---|---|
| 2021 | 129 | 0.7994 | 0.9394 | −14.00 |
| 2022 | 149 | 0.7767 | 0.9415 | −16.48 |
| 2023 | 159 | 0.8028 | 0.9346 | −13.18 |
| 2024 | 159 | 0.8326 | 0.9397 | −10.71 |
| 2025 | 167 | 0.8356 | 0.9404 | −10.47 |
| **2026** | **171** | **0.8645** | **0.9348** | **−7.03** |

### Formal trend regression (PSLF-hostile programs only)

Outcome: fill rate (pp); cluster-robust SE on institution; controls for state FE + specialty FE.

| Coefficient | β | SE | p |
|---|---|---|---|
| year_centered (2021=0, ..., 2026=5) | +1.595 pp/year | 0.985 | **0.105** (marginal) |
| 2026 indicator (beyond linear trend) | +2.984 pp | 4.051 | **0.461 (NS)** |

**Interpretation**: The 2026 narrowing is consistent with continuation of a pre-existing trend (~+1.5 pp/year). There is no detectable discontinuity in 2026 specifically.

### Pre-EO vs first-post-EO regression (2021-2025 vs 2026, separate fits)

| Specification | Pre-EO (2021-2025) β | Post-EO (2026 only) β |
|---|---|---|
| S1 status quo | −18.07 pp [−24.80, −11.35] (p=1.4×10⁻⁷) | −8.43 pp [−13.54, −3.33] (p=0.001) |
| S2 reclassified | −16.25 pp [−21.66, −10.83] (p=4.0×10⁻⁹) | +0.62 pp [−7.17, +8.42] (p=0.88, NS) |
| S3 dropped | −17.14 pp [−22.48, −11.80] (p=3.1×10⁻¹⁰) | +0.19 pp [−7.71, +8.10] (p=0.96, NS) |

**Honest framing**: The 2026-only post-EO regression has wide CIs because the post-EO sample is only 1 year (n_hostile rows ~72-160 depending on spec). The "post-EO β shrunk to near-zero" reading is misleading — it reflects (a) reduced sample size, (b) continuation of the multi-year trend, NOT a Trump-EO-specific discontinuity. The proper test is the linear-trend-with-2026-indicator regression above (p=0.46, NS).

---

## Negative-control specialties (R17 + R17++ canonical)

### Orthopedic surgery (primary negative control)

**5-year baseline (2021–2025, dedup-corrected):** PSLF-hostile β = **+0.67 pp** (cluster-robust 95% CI [−0.66, +2.00]; p=0.33; n=1,007 program-year rows; n_hostile=11 from 3 institutions)

**6-year extended (2021–2026, dedup-corrected):** PSLF-hostile β = **+0.54 pp** (cluster-robust 95% CI [−0.53, +1.60]; p=0.32; n=1,204 program-year rows; n_hostile=16 from 4 institutions)

**Power floor**: 5-year rules out uniform confounds > 1.33 pp; 6-year rules out > 1.06 pp.

**SUPERSEDED**: Earlier circulating drafts cited n=1,079 / β=+0.76 pp / p=0.25 (n=21 hostile rows from 4 clusters) — those numbers reflect a pre-Round-17 covariate-filter; the canonical numbers are above (per `paper3_negative_control_2021_2026_results.txt`).

### Dermatology (R17++ Agent 2 M5 second negative control)

**5-year (2021–2025):** PSLF-hostile β = **−7.20 pp** (cluster-robust 95% CI [−16.92, +2.52]; p=0.147 NS; n=791 program-year rows; n_hostile=27 from 5 institutions)

**6-year (2021–2026):** PSLF-hostile β = **−6.28 pp** (cluster-robust 95% CI [−14.57, +2.01]; p=0.138 NS; n=953 program-year rows; n_hostile=33 from 6 institutions)

**Power floor**: ~8–10 pp (much wider CIs than ortho due to fewer hostile-derm institutions and higher within-cohort variance).

**HONEST FRAMING (R17++)**: Dermatology is **NOT a clean null** like orthopedic surgery — point estimate is notably negative (−6 to −7 pp), and CIs are much less constrained on the negative side than positive (lower bound −15 to −17 pp; upper bound only +2 pp). p-values are non-significant at α=0.05 but the test is power-limited and admits both the null AND a substantial PSLF-hostile differential. We report dermatology as a SECONDARY negative control with this caveat (see `paper3_negative_control_dermatology_results.txt`). Orthopedic surgery remains the cleaner negative-control case.

This finding STRENGTHENS the rigor of the paper: we ran a pre-specified second negative control that did NOT confirm cleanly, and we report this honestly rather than dropping it.

## Trend regression sensitivity (R17++ Agent 2 M4)

The headline trend test `fill_pp ~ year_centered + is_2026 + state_FE + specialty_FE` on PSLF-hostile programs (n=934) gives is_2026 = +2.984 pp (SE=4.05, p=0.46 NS).

**R17++ sensitivity** with `is_post_eo = (year≥2025)` instead of `is_2026` (catches any 2025-cycle anticipation effect):
- year_centered (with is_post_eo control): +1.827 pp/year (SE=1.16, p=0.114)
- is_post_eo: **+0.538 pp** (SE=3.48, **p=0.877 NS**, 95% CI [−6.28, +7.36] pp)

**Both `is_2026` and `is_post_eo` specifications NS** — there is no detectable EO-specific discontinuity beyond the pre-existing 5-year trend, in either operationalization. The retraction of the Trump-EO causal interpretation is robust to the sensitivity choice.

---

## What changed from the prior LOCKED RESULTS doc (2026-05-10 morning + Round 17+ updates)

1. **Added 2026 NRMP data**: n_total 29,349 (5-year 2021–2025) → 37,802 raw 6-year → **after Round 17 CMS-merge dedup of 8 case-collision city duplicates: 37,450 raw / 35,193 OLS-fit (6-year sample)**. The 5-year baseline n=29,349 was unaffected by the dedup fix because the case-collision cities (San Diego, Jacksonville, El Paso, Bethesda, etc.) had been correctly handled in `run_model5_FINAL.py` already; the bug was in `run_model5_with_confounders.py` and `run_model5_2021_2026_cross_sectional.py` and emitted 31,063 / 37,802 inflated counts respectively.
2. **Added year-by-year fill-rate table** showing the multi-year narrowing trajectory
3. **Added linear-trend test** showing 2026 is consistent with continuation of pre-existing trend (is_2026 indicator beyond linear trend β=+2.98 pp, SE=4.05, p=0.46 NS). **Power caveat (Round 17+ audit):** the 95% CI on the is_2026 coefficient is approximately [−4.96, +10.92] pp — the test cannot rule out a substantial post-EO discontinuity up to ~+11 pp; "p=0.46 NS" should be read as "this design lacks power to distinguish trend continuation from a meaningful EO contribution," NOT as positive evidence for a null EO effect.
4. **RETRACTED the dramatic "Trump EO eliminated PSLF differential" framing** (was based on comparing 2026-only vs 2021-2025-pooled, which conflated trend continuation with EO discontinuity)
5. **Reframed as multi-year trend documentation + cross-sectional differential persistence**, with explicit "mechanism cannot be identified" framing
6. **Updated negative-control numbers (Round 17+ audit)**: prior n=1,079 / β=+0.76 pp / p=0.25 reflected a pre-Round-17 covariate filter; canonical 5-year is n=1,007 / β=+0.67 pp / p=0.33; 6-year (with 2026) is n=1,204 / β=+0.54 pp / p=0.32 (power floor 1.06 pp).
7. **Updated hostile-row counts (Round 17+ audit)**: S1=763 (was 776), S2/S3=358 (was 371) — reflects the canonical `paper3_model5_FINAL_results.txt` line 21.

---

## Updated venue strategy

**Primary**: Journal of Graduate Medical Education (JGME) — best fit for GME-focused descriptive trend paper. Acceptance probability: **35-42%** (was 30-37% pre-2026; the 2026 trend addition modestly strengthens the paper as the longest year-by-year program-level analysis available).

**Secondary**: Academic Medicine — same fit; slightly more methods-aware reviewers. Acceptance probability: **32-40%**.

**Tertiary**: Health Services Research — methods-heavy; would welcome the cluster-robust + wild-cluster bootstrap framing. Acceptance probability: **18-28%**.

**Demoted**: JAMA Health Forum (back to fourth-choice). Without a defensible Trump-EO causal claim, the venue fit drops back to ~10-15% (high desk-reject risk per Round 15 venue-fit audit).

**Not viable**: Health Affairs. Without causal identification + clean policy-effect story, no realistic path.

---

## What this means for drafting

The honest reframe makes Paper 3:
- **More defensible** at peer review (no overclaim risk)
- **Slightly less exciting** (no headline Trump-EO finding)
- **Substantively novel** still — first peer-reviewed quantitative analysis at program-year level + multi-year trend documentation
- **Same venue strategy** as before 2026-data integration
- **Same drafting timeline** (~4-6 weeks)

**Net acceptance probability change vs original 2021-2025-only paper**: +5pp (from 30-37% → 35-42% at JGME). The 2026 data adds a year + a trend story; it does NOT enable a quasi-experimental headline.

---

## Audit lessons

The same overclaim risk exists for Paper 2 (cohort heterogeneity at comments scale: Trump EO appears more concordant across cohorts than the post-level data suggested) and Paper 1 (cohort heterogeneity in inter-LLM agreement: SDN-only K-α=+0.83 vs Reddit-only +0.69 may reflect sample composition rather than instrument-cohort interaction). Going forward: **before claiming a clean quasi-experiment or mechanism, check the year-by-year (or whatever the relevant baseline is) trend**.

---

*This document supersedes the prior `PAPER_3_LOCKED_RESULTS_2026-05-10.md`. Use this as the source of truth for Paper 3 numbers + framing.*
