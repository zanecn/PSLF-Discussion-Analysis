# Per-Paper TODO List — R17++ #6 Rigorous Review (2026-05-17)

**Source:** Independent peer-review-style evaluation by 6 parallel agents (one per paper). Each agent read paper outlines + locked results + scripts + reference list + verified claims against data.

**Critical integrity findings up front:** 5 of 6 papers have at least one numerical-consistency issue that would damage credibility at peer review if not fixed. P3 is the cleanest. **Address all P0 BLOCKER items before any submission attempt.**

---

## Cross-paper critical findings (read first)

| Paper | Most-severe issue | Status |
|---|---|---|
| **P1** | **OP-vs-Reply sample-size discrepancy**: outline reports CIs [−0.0129, −0.0079] / [+0.2048, +0.2238] (from n=14,153 cluster bootstrap) paired with point estimates −0.0146 / +0.2387 (from n=21,453 t-test). **Mirrors the R17++ Agent 1 C1 fabricated-CI pattern.** | P0 BLOCKER |
| **P2** | **Reddit Medical n discrepancy**: 566 vs 398 across two source files (~30% sample reduction). Lift_pp / OR / l5 robustness use different n's. | P0 BLOCKER |
| **P3** | None at integrity level — methods + retraction + locked numbers all verified clean | none |
| **P4** | **789-vs-872 institution mismatch**: classification CSVs cover 789 institutions; primary table has 872. 83 institutions classified at 2026-extraction time but never propagated to lookup files. | P0 BLOCKER |
| **P5** | **"14 unique institutions" is wrong**: actually 14 program-rows across **8 unique HCA-affiliated institutions**. The "979 unique institutions" claim is also wrong (= 358 unique; 979 double-counts). | P0 BLOCKER |
| **P5** | **Mann-Whitney on Surgery-General fill rates returns p=0.84 NS** (mean hostile 0.806 vs non-hostile 0.814) — the "PSLF may matter for Surgery-General recruitment" interpretation is **UNSUPPORTED** by the data | P0 BLOCKER |
| **P6** | **No analysis script exists** (0% of analytical work done). Plus: existing data already suggests "discourse-as-policy-thermometer" hypothesis may be falsified (Trump EO > Biden v. Nebraska in effect size — opposite of what the magnitude-scaling story predicts) | P0 + P1 |

---

# Paper 1 (P1) — Methods (OP-vs-Reply reframe)

**Target:** ICWSM '26 / CSCW '26 / IC&S primary; BRM fallback
**Realistic acceptance estimate:** 20-25% at ICWSM (was 25-30% in outline — slightly optimistic)

## P0 BLOCKERS (must fix before any submission)

1. **[P0]** **✅ RESOLVED 2026-05-17 (R17++ #6 RIGOROUS REVIEW)**. Cluster bootstrap re-run with aligned 4-source OP loader + raw comments file + on-the-fly VADER. **NEW EXACT MATCH n=21,453**: TB Δ=−0.0146 cluster-bootstrap CI [−0.0164, −0.0127] boot p=0 (matches t-test t=−15.10 p=2.83e−51 exactly); VADER Δ=+0.2387 CI [+0.2306, +0.2460] boot p=0; magnitude ratio 16.4× (vs prior wrong 20.5× from n=14,153 subset). All P1/locked/data-acquisition docs updated.
2. **[P0]** **Verify Park & Conway 2017 JMIR citation** is real. Memory note says it was excised in R17++ audit; outline still cites it at §1.4 and §250. WebSearch DOI 10.2196/jmir.6826 to confirm. Remove if fabricated. Effort: 15 min.
3. **[P0]** **Reconcile n=519,401 vs n=519,342** for comments TB×VADER analysis across MASTER_LOCKED_NUMBERS.md (line 105: 519,342) vs outline §5.5b (519,401). Pick one canonical, propagate. Effort: 30 min.

## P1 HIGH PRIORITY (strengthens substantially)

4. **[P1]** **Generate Figures 1, 2, 3** — none currently exist except Figure S1 (paraphrase replication). Figure 1 = 5×5 instrument correlation matrix; Figure 2 = OP-vs-reply forest plot by 8 cohorts with cluster-bootstrap CIs; Figure 3 = cohort-stratified 3-LLM α with Krippendorff floors. Effort: 2 hours.
5. **[P1]** **Add per-cohort cluster bootstrap for OP-vs-Reply.** New script `scripts/run_op_vs_reply_cluster_bootstrap_by_cohort.py`. Per-event cluster bootstrap exists; per-cohort does not. Reviewers will ask. Effort: 1 hour.
6. **[P1]** **Reorder §5 to put OP-vs-Reply first** per R17++ #6 reframe. Currently §5.1-5.4 are 3-LLM convergence; §5.5 is the new headline. Move OP-vs-Reply to §5.1. Update §1.1, §1.4, abstract. Effort: 4 hours.
7. **[P1]** **Run RoBERTa-base-sentiment as 4th instrument family on n=1,001 intersection.** ~30 min compute via HuggingFace. Would strengthen LLM-class boundary claim. Effort: 1-2 hours.

## P2 MEDIUM PRIORITY

8. **[P2]** **Hand-code 100 random posts from n=1,001 as sentiment gold standard.** Pre-empts the "but which scorer is right?" reviewer question (the single highest-impact critique per agent). Effort: 4 hours.
9. **[P2]** **Add MIN_WORDS=20 selection-bias disclosure** to §3.6 and §7. TextBlob's known unreliability on short text drives the threshold, which systematically excludes emotionally-charged short posts (where VADER excels). Effort: 20 min.
10. **[P2]** **Tighten SDN-only "above 0.80 floor" framing.** Point estimate is +0.83 but lower CI bound is +0.787 (below 0.80). Currently §5.2 + §8 + locked doc line 13 claim "exceeds the 0.80 satisfactory floor" without the lower-bound caveat. Effort: 15 min.

## P3 LOW PRIORITY

11. **[P3]** Add Hayes & Krippendorff 2007 citation for cohort-stratified bootstrap justification.
12. **[P3]** Footnote Reddit Finance as sharpest help-seeking → help-giving structural asymmetry (largest VADER Δ).
13. **[P3]** Verify Halterman & Keith 2025 PA DOI format (10.1017/pan.2025.10017 — unusually large index for 2025).

---

# Paper 2 (P2) — Substantive (Reddit Finance cross-scorer)

**Target:** Political Analysis primary; SMR secondary; JCSS / PLOS One backup
**Realistic acceptance estimate:** PA 15-20% (with mitigating analyses); 25-35% at JCSS

## P0 BLOCKERS

1. **[P0]** **Reconcile Reddit Medical n discrepancy** (566 in decoupling/base_rate CSV vs 398 in l5_robustness file). Determine why l5 filters lose 168 rows (likely `pslf_stance != "unknown"` filter per script line 81-82). Add explanatory footnote in §3.3 and §4.1. Effort: 1 hour to investigate + document.
2. **[P0]** **Correct "5/5 specs cross-instrument concordant" claim** for SDN-Medical — verified TRUE in data (all 5 specs OR<1, all CIs below 1.0). But **correct "4/5 coupling" claim for r/PSLF** — actual: 4 OR>1, 1 underpowered NS (OR=0.194 [0.04, **1.01**] — upper bound just touches 1.0). Reword to "4/5 coupling, 1/5 underpowered to discriminate." Effort: 15 min.
3. **[P0]** **Correct "cohort-conditional sign-flip" framing.** Of Reddit Finance's 5 specs: 3 still return OR<1; only TB×Claude and VADER×Claude (the cross-scorer LEXICAL specs) flip. Reframe: "two of five specs (the cross-scorer lexical specifications) flip direction with wide CIs spanning 1.0." Effort: 30 min.

## P1 HIGH PRIORITY

4. **[P1]** **Add symmetric cross-scorer matrix** with TB/VADER-proxy stance for Reddit Finance specifically. The current design varies sentiment but fixes stance at Claude — cannot rule out Claude-stance-specific artifact. Effort: 1 day Python work.
5. **[P1]** **Run Llama × Claude and DeepSeek × Claude OR for Reddit Finance** to rule out Claude-sentiment-specific artifact (3-LLM data exists). Add as §5.3b or supplement S5. Effort: 1 day.
6. **[P1]** **Restore 5-cohort heterogeneity table as CO-HEADLINE in §5.1** — R17++ #6 strip-to-Reddit-Finance reframe was too aggressive. Better framing: "construct misalignment manifests in 1 of 5 cohorts" is a stronger story than "case study of Reddit Finance." Effort: 2 hours rewrite.
7. **[P1]** **Apply Holm-Bonferroni to per-event × per-cohort × per-topic family** (script flagged but never run). Effort: 1 hour.
8. **[P1]** **Re-fit cohort ORs with author cluster-robust SE** per Agent 5 M1 todo. Will widen CIs by 10-20%; r/PSLF OR=0.194 [0.04, 1.01] may flip to clearly NS. Effort: 1 day.

## P2 MEDIUM PRIORITY

9. **[P2]** **Pre-registration disclosure.** State explicitly whether 5 specifications were pre-registered or exploratory. If exploratory, reframe as "specification curve" rather than hypothesis tests. Effort: 30 min.
10. **[P2]** **Add Reddit r/StudentLoans as secondary construct-misalignment exemplar** in §5.3 (parallel pattern: 3 OR>1, 2 OR<1, all CIs spanning 1.0; weaker effect than Finance but same diagnostic). Effort: 1 hour.
11. **[P2]** **Add base-rate sensitivity supplement**: re-compute OR after excluding cohorts with <30 non-pursuing posts; specify behavior of OR under marginal-pursue >90% (Reddit Finance is at 91.4% pursuing baseline). Effort: 2 hours.

## P3 LOW PRIORITY

12. **[P3]** Add dichotomization-sensitivity paragraph (e.g., very_negative-only threshold vs current {very_negative, negative} grouping). Effort: 1 hour.

---

# Paper 3 (P3) — Policy (PSLF residency fill-rate differential)

**Target:** Health Affairs Scholar primary (with CMS NPPES workforce-downstream boost) OR JGME (without boost)
**Realistic acceptance estimate:** HAS 15-25% with boost; 8-15% without boost; JGME 35-42% backup

**Status: cleanest of the 6 papers. Numbers all verified; retraction handled rigorously; integrity audit infrastructure functional. R17++ #6 elevation depends on CMS NPPES workforce-downstream addition.**

## P0 BLOCKERS for HAS elevation (decide first; submit to JGME if you skip these)

1. **[P0]** **Pilot CMS NPPES match on 3-4 HCA institutions** (~1 week). If match rate ≥70%, commit to full 2-3 week build for workforce-downstream. If <70%, drop the boost and submit to JGME.
2. **[P0]** **Add randomization inference** for S2/S3 small-cluster gray-zone (B=5,000 permutations of hostile-vs-ambiguous within state×specialty strata). With G=9 hostile clusters in S2/S3, wild-cluster bootstrap is in MacKinnon-Webb (2018) §5 gray zone. Effort: 1 day.
3. **[P0]** **Translate methods to JGME/HAS-readable language.** Current §2.5 reads as econometrics prose. Add plain-English Trump-EO retraction paragraph in §3.3 + simplified methods paragraph. Effort: 1 day.

## P1 HIGH PRIORITY

4. **[P1]** **Add CR2 (Pustejovsky-Tipton 2018) variance estimator** as parallel small-cluster check alongside CR1 + wild-cluster bootstrap. `clubSandwich` R package or Python equivalent. Effort: 1 day.
5. **[P1]** **Generate event-study-style Figure 3** — year-by-year β with CI from year-by-year regressions, vertical line at March 2025 EO. Visualizes the retraction directly. Effort: 1 day.
6. **[P1]** **Oster (2019) δ-bounds on M1→M5 coefficient stability** to bound selection-on-unobservables. Effort: 1 day.
7. **[P1]** **Diagnose two-part NIH Part 2 result**: β=+0.00 / p=5×10⁻⁶ suggests near-perfect collinearity — likely n_hostile in positive-NIH subsample is ~0. Report n_hostile_rows on Part 2 sample and explain. Effort: 1 hour.
8. **[P1]** **Pre-empt dermatology asymmetry critique** in §3.5 — add 3 candidate explanations (small G, ceiling-effect competition, hostile-derm market concentration) from locked-results doc to manuscript. Effort: 30 min.

## P2 MEDIUM PRIORITY

9. **[P2]** **Inverse-hyperbolic-sine (asinh) NIH spec** as third NIH check alongside single-equation log + two-part. Handles zeros without mass-point bias. Effort: 30 min.
10. **[P2]** **Back-of-envelope welfare/cost calculation** in §4.3 (~160 unfilled hostile positions/year × $ federal residency support = $Y foregone subsidy). Effort: 1 day.
11. **[P2]** **OSF pre-registration of 6-year sample analysis** before submission. Effort: 1 day.
12. **[P2]** **Specialty heterogeneity Figure** (Table 5 as visualization with HCA-business-strategy confound caveat ribbon). Effort: 30 min.
13. **[P2]** **Power calculation** for multi-year follow-up — how many post-EO years needed to detect 5 pp EO discontinuity with 80% power? Effort: 30 min.

## P3 LOW PRIORITY

14. **[P3]** NSLDS DUA application (defer to PGY-1; not blocking ERAS).
15. **[P3]** AMA Masterfile institutional license inquiry (only if NPPES pilot succeeds).

---

# Paper 4 (P4) — Data (Comprehensive Residency Program Characterization)

**Target:** *Scientific Data* with broadened framing OR Data in Brief (more honest given current state)
**Realistic acceptance estimate:** Sci Data 25-30% (with broadening); Data in Brief 70-80%
**Agent recommendation: for medical student, switch primary to Data in Brief** — venue prestige delta is negligible for NS PDs, acceptance is 2× higher, no broadening cost.

## P0 BLOCKERS (~1 week before any submission)

1. **[P0]** **Re-run `verify_nrmp_pslf_eligibility.py` against 2026 institution list** to close 83-institution gap (current: 789 in classification CSV vs 872 in primary table). Effort: 2-4 hours including ProPublica API calls.
2. **[P0]** **Create `hca_academic_partnership_audit_trail.csv`** with primary-source URLs for all 14 partnerships (HCA press releases + ACGME records + USF/U Miami/U Houston/VCOM program pages). Currently missing. Effort: 1 day.
3. **[P0]** **Draft `nrmp_field_dictionary.md`** with column-level documentation (units, valid ranges, missingness patterns). Currently missing. Effort: 0.5 day.
4. **[P0]** **Compute inter-source agreement rates** (currently `[TO COMPUTE]` in outline). Scientific Data submission blocker. Effort: 2-3 days if broadening data already pulled; cannot do ProPublica × ACGME without the broadening.
5. **[P0]** **Mint Dryad or Zenodo DOI** (Zenodo recommended: free, faster, CERN durability). Currently no deposit exists.
6. **[P0]** **Write README.md for deposit + CHANGELOG.md + SHA-256 checksums.** Effort: 1 day.
7. **[P0]** **Verify `RUN_AUDITS.ps1` passes at deposit-anchor commit.**

## P1 HIGH PRIORITY (only if pursuing Scientific Data with broadening, ~2-3 weeks)

8. **[P1]** Pull ACGME Annual Data Reports 2018-2025; harmonize to single multi-year table. Effort: 1 week.
9. **[P1]** Pull NIH RePORTER FY2018-2024 (currently FY2023 only). Effort: 2-3 days.
10. **[P1]** Pull VA Facility Directory; flag VA-affiliated programs. Effort: 1-2 days.
11. **[P1]** Pull CMS Hospital Compare 2018-2024 (currently 2023 only). Effort: 1 week.
12. **[P1]** Pull AAMC Institutional Characteristics (faculty count, UME enrollment). Effort: 2-3 days.
13. **[P1]** Build `build_extended_residency_dataset.py` to merge all sources; document merge keys + match rates. Effort: 1 week.
14. **[P1]** Recompute inter-source agreement rates with broadened data.

## P2 MEDIUM PRIORITY

15. **[P2]** Generate 2 Data Records figures (institution count × year facet panel; US choropleth with HCA-academic highlights). Effort: 1 day.
16. **[P2]** Add `requirements.txt` / `environment.yml`; freeze pdfplumber + pandas + statsmodels versions; freeze ProPublica cache snapshot. Effort: 0.5 day.
17. **[P2]** Rename primary table from `nrmp_program_level_2021_2026.csv` to `nrmp_pslf_eligibility_2021_2026.csv` to match outline.

**Strategic recommendation:** Drop the broadening; submit single-source dataset to Data in Brief. Saves 2-3 weeks; venue still appears as Elsevier-recognized CV line; acceptance ~75%. The R17++ #6 case for Scientific Data is sound for tenure-track but the marginal CV value for a med student is small relative to opportunity cost.

---

# Paper 5 (P5) — Surgical-subspecialty (HCA institutional concentration)

**Target:** *Neurosurgery* (Wolters Kluwer) primary OR *World Neurosurgery* backup
**Realistic acceptance estimate:** *Neurosurgery* 20-30% (5-10pp lower than outline's 30-40%); *World Neurosurgery* 35-45%

## P0 BLOCKERS (mechanical edits but critical for integrity)

1. **[P0]** **Correct "14 unique hostile institutions" → "14 program-rows, 8 unique HCA-affiliated institutions"** throughout abstract, §1, §3 implication #2, Results Table 2. The outline currently double-counts (HCA KC ×5, HCA Medical City ×2, HCA JFK ×2). Effort: 15 min mechanical edit.
2. **[P0]** **Correct "979 unique institutions" → "358 unique institutions (979 sums per-subspec counts; double-counts HCA-affiliated multi-subspec facilities)"** in Methods. Effort: 5 min.
3. **[P0]** **Add Methods caveat that all-HCA result is conditional on the surgical-subspec slice.** The full hostile pool of 23 institutions across all specialties includes 2 non-HCA institutions (North Oaks Med Ctr LLC, Steward Carney Hospital) that happen not to host surgical-subspec programs. Failure to include this invites selection-on-outcome critique. Effort: 30 min.
4. **[P0]** **REPLACE §3 implication #3** with honest Mann-Whitney result. Agent pre-ran the test: hostile (n=110 program-years from 7 institutions) vs eligible (n=2,087), **U=117,137.5, p=0.6414 NS**. Mean fill hostile=0.806 vs non-hostile=0.814 — essentially identical. Current claim "the only surgical subspecialty where PSLF eligibility may actually matter for recruitment" is **UNSUPPORTED**. Reframe: "Surgery-General hostile programs show greater variability in fill rates than ultra-competitive subspecialties, but central tendency does not differ from non-hostile programs (Mann-Whitney p=0.84). This null result is itself informative for workforce-policy." Effort: 1 hour rewrite.

## P1 HIGH PRIORITY

5. **[P1]** **Add explicit reference to Lassner 2022 *JGME* multispecialty BCBE paper** in Methods §6 as closest multispecialty for-profit-GME precedent. PSLF outcome positioned as novel extension. Prevents reviewer "you re-ran Lassner with different outcome" critique. Effort: 1 hour.
6. **[P1]** **Generate Figure 1** (bar chart of subspec × PSLF-hostile rate, sorted descending). Effort: 1 hour.
7. **[P1]** **Generate Figure 2** (US choropleth with HCA KC + 7 other HCA institutions highlighted). Requires geocoding ~8 institutions. Effort: 1 day.
8. **[P1]** **Pull HRSA HPSA + USDA RUCA + KFF Medicaid** for the 8 hostile institutions. Add one Methods paragraph + supplementary table on geographic context. Skip Census Bureau (adds nothing beyond RUCA at n=8). Effort: 3 days.

## P2 MEDIUM PRIORITY

9. **[P2]** Add "HCA Kansas City hosts 21 distinct specialties (not just 5 surgical)" footnote to Discussion citing Lassner 2022 EM paper for broader for-profit-chain GME expansion pattern. Effort: 30 min.
10. **[P2]** Pre-register 2027 follow-up analysis explicitly as Future Work to detect post-EO-14235 fill-rate shifts. Effort: 30 min.
11. **[P2]** **Pre-emptively draft brief contact letter to HCA Healthcare's GME office** noting institution-naming analysis underway (some clinical journals now require this). Effort: 1 hour.

## P3 LOW PRIORITY

12. **[P3]** Census Bureau county demographics pull — skip (low marginal value at n=8).
13. **[P3]** Formal regression on Surgery-General fill rate — skip (n=7 hostile institutions below defensible-regression threshold; Mann-Whitney already settles).

---

# Paper 6 (P6) — Post-EO sentiment (multi-policy comparison)

**Target:** *PLOS One* primary; *Cureus* high-accept backup
**Realistic acceptance estimate:** PLOS One **30-40% (with proper ITS + pre-reg + placebo)**, lower than outline's ~50%; Cureus ~80%

**Status: LEAST-DEVELOPED of 6 papers. NO analysis script written. Outline framing at risk of being falsified by existing data.**

## P0 BLOCKERS (entire analytical foundation)

1. **[P0]** **STOP CALLING THIS A 2-WEEK PROJECT.** Realistic effort: 8-10 weeks of focused work (data + analysis + writing). Update outline timeline. Effort: 5 min.
2. **[P0]** **HONEST REFRAMING of headline.** Replace "discourse as real-time policy thermometer" with framing the data can defend. Existing cohort_heterogeneity_comments output already shows Trump EO > Biden v. Nebraska in effect size — OPPOSITE of what the magnitude-scaling story predicts. Suggested replacement: "Cohort-conditional sentiment dynamics around PSLF policy events" or "A pre-registered event-study analysis of five federal student-loan policy interventions in online PSLF discourse, 2023–2026." Effort: 1 hour.
3. **[P0]** **FILE OSF PRE-REGISTRATION BEFORE TOUCHING POST-FINAL-RULE DATA.** Adapt `OSF_PREREGISTRATION_cross_domain.md` to PSLF post-EO (~2 days). Lock: pre-EO baseline period, event windows (60d default), primary instrument (Claude pslf_sentiment recommended given P1 construct findings), ITS specification (Newey-West vs Prais-Winsten vs AR(1)), Holm-Bonferroni for 5×3 instrument-event family, placebo test design, stop rules. **Without pre-registration BEFORE analysis, you forfeit pre-reg credit.** Effort: 1 week.

## P1 HIGH PRIORITY

4. **[P1]** **Write `analyze_post_eo_sentiment_shift.py`** with proper methodology:
   - Weekly aggregation per cohort × instrument
   - **Newey-West or Prais-Winsten ITS** with autocorrelation correction (CRITICAL — OLS will overstate significance)
   - **Overlap-aware sensitivity** (drop each potentially-overlapping event, refit)
   - Cluster bootstrap for breakpoint inference (B=2,000)
   - **Holm-Bonferroni** across the 5×3 instrument-event family
   - **Placebo test** using a no-event period (e.g., spring 2024 before SAVE litigation)
   - Effort: 3-4 weeks (NOT 2 weeks as outline claims)
5. **[P1]** **Cite Bernal-Cummins-Gasparrini (2017) IJE 46(1):348–355** as standard methodology for ITS with multiple interventions. Cite Wagner et al. 2002 J Clin Pharm Ther for ITS guidance.
6. **[P1]** **Compile event dictionary** with both signal events (announcements, arguments) and outcome events (rulings, effective dates). Effort: 0.5 day.
7. **[P1]** **Verify additional Reddit r/StudentLoans Arctic Shift pull is complete** — partial data exists per cohort_heterogeneity_comments (n=207,353 comments) but post-level may be incomplete. Verify `collect_reddit_arctic_shift.py` covered r/StudentLoans, not just PSLF-anchored. Effort: 1 day to verify + 1 week pull if needed.

## P2 MEDIUM PRIORITY

8. **[P2]** **Cite Papers 1 and 2** with construct disagreement caveat — mandatory honesty given P1 findings. Do NOT report TB/VADER convergence claims without P1 disclaimer.
9. **[P2]** **Author-level verification of cited papers** (R17++ rule). Check Tsugawa & Ohsaki 2015 COSN '15, Choi/Aiello/Varga/Quercia 2020 WWW '20, Park & Conway 2017 JMIR 19(3)e71.
10. **[P2]** **Generate Figures 1 and 2** (ITS time series with breakpoints + stance distribution by window). Depends on analysis. Effort: 3-5 days.

## P3 LOW PRIORITY

11. **[P3]** Comparison to non-PSLF student-loan policy as negative control (e.g., forbearance extension for non-PSLF borrowers) — would strengthen but not critical.

**TIME-SENSITIVITY: HIGH.** Trump PSLF EO is generating active research RIGHT NOW (Brookings, CFPB, AERA, CSS labs). Realistic timeline to submission: 12-16 weeks from today. If pursuing P6, **prioritize over P1 and P2** to claim citation primacy. Otherwise, expect to get scooped.

---

# Summary table — TODOs by priority

| Paper | P0 BLOCKERS | P1 HIGH | P2 MED | P3 LOW |
|---|---|---|---|---|
| P1 | 3 | 4 | 3 | 3 |
| P2 | 3 | 5 | 3 | 1 |
| P3 | 3 | 5 | 5 | 2 |
| P4 | 7 | 7 | 3 | 0 |
| P5 | 4 | 4 | 3 | 2 |
| P6 | 3 | 4 | 3 | 1 |
| **TOTAL** | **23 P0 BLOCKERS** | **29 P1 HIGH** | **20 P2 MED** | **9 P3 LOW** |

**Combined critical path (recommended sequencing, given time-sensitivity + dependency):**

**Week 1-2 (immediate):**
- Fix all P0 mechanical edits across all 6 papers (~6 hours total: P1 sample fix, P2 n reconciliation, P4 institution re-run, P5 "14 → 8" + Mann-Whitney rewrite, P6 reframe)
- File P6 OSF pre-registration FIRST (1 week; gating block for any post-Final-Rule analysis)

**Week 3-6:**
- P6 analysis script writing (3-4 weeks; race against external competition)
- In parallel: P3 CMS NPPES pilot (1 week, then decide HAS vs JGME)
- In parallel: P5 geographic data pull (3-5 days)

**Week 7-12:**
- P3 writing (HAS or JGME path)
- P1 writing with OP-vs-Reply headline
- P5 writing with reframed §3 + figures

**Week 13-18:**
- P2 writing with restored 5-cohort co-headline + new symmetric cross-scorer + Llama/DeepSeek replication
- P4 deposit + Data in Brief submission (or broadened Sci Data submission if pursued)

**Submission targets:**
- **Aug-Sep 2026**: P6 (urgent — race for citation primacy)
- **Oct-Nov 2026**: P3, P5, P4
- **Dec 2026**: P1, P2
- **All in print by ERAS Sept 2027** (assuming ~3-6 month venue review cycles)

---

## Honest meta-assessment

**Most rigorous paper:** P3. Numbers all locked + verified, retraction handled exemplarily, integrity audits passing. Submit-ready with minor methods translation.

**Highest risk:** P6 (entire analytical core unwritten + time-sensitive competition + headline risks falsification by existing data).

**Most strategically valuable for NS match:** P5 (NS specialty-relevant, IF the P0 corrections land cleanly).

**Numbers-still-need-rebuilding:** P1 (sample mismatch), P2 (n discrepancy), P4 (institution gap), P5 (double-counting). None are fatal; all are fixable in <1 day each but ALL must be fixed.

**The R17++ #6 reframe is broadly defensible** but introduced new issues in P2 (over-aggressive strip) and P5 (Mann-Whitney result contradicts new framing). The P3 elevation to HAS is contingent on the NPPES pilot succeeding.

**Realistic expected ERAS yield with the reviews applied:**
- P3: 35-42% at JGME OR 15-25% at HAS (if NPPES boost lands) = ~35% expected acceptance
- P4: 75% at Data in Brief (recommended pivot) OR 25-30% at Sci Data (if broadening done)
- P5: 30-40% at *Neurosurgery* with P0 fixes
- P6: 30-40% at PLOS One with proper ITS + pre-reg + placebo
- P1: 20-25% at ICWSM with OP-vs-Reply reframe + fixes
- P2: 25-35% at JCSS OR 15-20% at PA (with sensitivity additions)

**Expected papers in print by ERAS:** ~3-3.5 (slightly lower than R17++ #6's optimistic 3.8-4.5 due to true acceptance probability constraints, but achievable with honest execution of the P0 fixes).

---

*Last updated 2026-05-17 (R17++ #6 RIGOROUS REVIEW). Source: 6 parallel independent peer-review-style agents, each reading paper outline + locked results + scripts + reference list + verifying claims against data files.*
