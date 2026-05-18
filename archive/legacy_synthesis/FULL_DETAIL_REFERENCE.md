# PSLF Project — Full Detail Reference

**Date:** 2026-05-10 (Round 12 final)
**Coverage:** Every script, every data corpus, every analysis, every finding, every figure across R1-R12.

---

# SECTION A: PRIMARY DATA CORPORA

## A.1 Reddit Arctic Shift (R8 expansion — primary corpus)

**File:** `reddit_arctic_shift_pslf.csv`
**n posts:** 72,262 PSLF-strict-filtered (from ~120K raw)
**Date range:** 2010-01-01 to 2025-12-31
**Source:** Arctic Shift archive (Pushshift successor; uncapped Reddit historical)
**Filter:** `filter_pslf_relevant` from `pslf_search_terms.py` (anchored regex requiring PSLF-specific term within 80 chars of generic "loan forgiveness")
**Columns:** `id`, `subreddit`, `created_utc`, `created_datetime`, `title`, `selftext`, `combined_text`, `author`, `score`, `num_comments`, `polarity` (TextBlob), `vader_compound`, `word_count`, `profession`
**Subreddits covered:** 21 (PSLF, StudentLoans, personalfinance, financialindependence, medicalschool, medicine, Residency, physicianassistant, PAstudent, prephysicianassistant, nursing, CRNA, Teachers, lawschool, pharmacy, OccupationalTherapy, slp, fednews, govfire, socialwork, StudentNurse)
**Collector:** `scripts/collect_reddit_arctic_shift.py`

## A.2 Reddit Professions PSLF (original corpus)

**File:** `reddit_professions_pslf.csv`
**n posts:** 11,793 raw → 3,754 PSLF-filtered → 11,451 with wc≥20
**Date range:** 2011-01-07 to 2026-05-07
**Source:** Reddit JSON API year-windowed scraping
**Limitation:** Reddit's 1000-result API cap creates volume distortion (R3 finding; 6-7× real growth + 10× recency bias)
**Backups:** `reddit_professions_pslf_pre_round2.csv`, `_pre_round3.csv`, `_pre_round7expand.csv`, `_20260422_backup.csv`, `_20260424_backup.csv`
**Collector:** `scripts/collect_reddit_professions.py`

## A.3 Reddit New Subs PSLF (R7 expansion)

**File:** `reddit_new_subs_pslf.csv`
**n posts:** 470 PSLF-filtered (from r/PAstudent, r/prephysicianassistant, r/CRNA — 52 net new)
**Date range:** 2018-2026
**Purpose:** R7 expansion to address PA + nurse-anesthesia sample gaps

## A.4 Student Doctor Network (SDN)

**File:** `forum_pslf_discussions.csv`
**n posts:** 45,334 raw → 4,749 PSLF-strict-filtered
**Date range:** 2004-11-25 to 2026-05-06
**Source:** SDN forum scrape via Playwright headless Chromium
**Threads scraped:** 200+ threads across medical-discussion sub-forums
**Backups:** `forum_pslf_discussions_pre_round3.csv`, `_20260422_backup.csv`, `_20260424_backup.csv`
**Collector:** `scripts/collect_forum_data.py`

## A.5 Reddit Comments (R8 collector)

**File:** `reddit_comments_pslf.csv`
**n comments:** 459,789 (with TextBlob)
**File:** `reddit_comments_pslf_with_vader.csv` (459,789 + VADER added; 460 MB)
**Date range:** 2018-2026
**Source:** PRAW Reddit API + no-auth JSON API
**Coverage:** ~17,686 of 76,074 PSLF posts have comments collected (~23% coverage; collector ongoing ~3-50h wall-time remaining)
**Columns:** `comment_id`, `post_id`, `post_subreddit`, `parent_id`, `author`, `body`, `score`, `created_utc`, `created_datetime`, `depth`, `is_top_level`, `profession`, `polarity`, `subjectivity`, `word_count`, `vader_compound`
**Collectors:** `scripts/collect_reddit_comments.py` (PRAW), `scripts/collect_reddit_comments_no_auth.py` (no-auth)

## A.6 Comprehensive Medical/Teacher PSLF (legacy corpora)

**Files:** `comprehensive_medical_pslf_discussions.csv` (1,126 posts), `comprehensive_teacher_pslf_discussions.csv` (subset)
**Date range:** 2016-2025
**Source:** Original medical and teacher subreddit posts
**Purpose:** Supplement primary Reddit corpus

## A.7 Topical-near baseline

**File:** `reddit_baseline_topical_near.csv`
**n posts:** 7,750 off-PSLF posts in same subreddits
**Purpose:** Calibration baseline (same population, off-topic)
**Collector:** `scripts/collect_reddit_baseline.py`

## A.8 r/AskReddit baseline

**File:** `reddit_baseline_askreddit.csv`
**n posts:** 177
**Purpose:** Generic Reddit polarity baseline (relevance + new sort, drops viral 'top' bias)
**Caveat:** Small sample (n=177); not length-matched in raw form

## A.9 Bogleheads (Cloudflare-blocked attempt)

**File:** `bogleheads_pslf_discussions.csv` (essentially empty)
**Status:** Cloudflare-blocked even via Playwright
**Documented in:** `scripts/collect_bogleheads.py`

## A.10 Other failed scrape attempts

- **allnurses.com:** Cloudflare-blocked (`scripts/collect_allnurses.py`)
- **physicianassistantforum.com:** Cloudflare-blocked at search endpoint with Turnstile challenge (`scripts/collect_pa_forum.py`)
- **YouTube comments:** Collector built but not run (requires YOUTUBE_API_KEY) — `scripts/collect_youtube_pslf.py`

---

# SECTION B: CLAUDE SENTIMENT SCORING SUBSAMPLES

## B.1 Reddit cross-source baseline

**File:** `zeroshot_reddit_n1000.csv`
**n posts:** 721 (originally 1000 sampled, 721 valid after parse_error filter)
**Source:** Sample of `reddit_professions_pslf.csv`
**Cost:** ~$2

## B.2 SDN cross-platform baseline

**File:** `zeroshot_sdn_n1000.csv`
**n posts:** 605
**Source:** Sample of `forum_pslf_discussions.csv`
**Cost:** ~$2

## B.3 Event-stratified Reddit

**File:** `zeroshot_reddit_eventstrat.csv`
**n posts:** 696
**Sample design:** 100 per (8 events × pre/post) = 1,600 target
**Source:** Year-windowed Reddit posts in 8 PSLF event windows
**Cost:** ~$2

## B.4 Event-window Reddit fill (Path C)

**File:** `zeroshot_reddit_eventfull.csv`
**n posts:** 458
**Purpose:** Path C event-window fill at full corpus depth
**Cost:** ~$2.40

## B.5 Event-window SDN fill (Path C)

**File:** `zeroshot_sdn_eventfull.csv`
**n posts:** 2,528
**Purpose:** Path C event-window fill on SDN
**Cost:** ~$13 (1.2% error rate)

## B.6 PA + nurse practitioner expansion

**File:** `zeroshot_pa_np_expansion.csv`
**n posts:** 51
**Purpose:** R7 expansion top-up for PA cells

## B.7 Full corpus Reddit fill (R7)

**File:** `zeroshot_reddit_fullcorpus.csv`
**n posts:** 2,140
**Purpose:** Round 7 full-corpus expansion

## B.8 Arctic Shift event-window fill (R8)

**File:** `zeroshot_reddit_arctic_shift_fill.csv`
**n posts:** 2,281
**Purpose:** Round 8 Arctic Shift expansion event-window fill
**Cost:** ~$13 (March 2026 stratified scoring run)

## B.9 Test-retest sample (R7 fix #5)

**Files:** `zeroshot_sdn_temp0_retest.csv` (n=605 SDN, temperature=0), `zeroshot_reddit_temp1_retest.csv`
**Test-retest α:** +0.958 (95% CI [+0.938, +0.975]), exact-match 95.2%
**Purpose:** Closes the "LLM stochasticity" objection

## TOTAL CLAUDE SCORING

- **9,263 posts** total across all subsamples
- **9,242 unique posts** with all three scorers (after deduplication)
- **~$50 spent** total

---

# SECTION C: ADMINISTRATIVE / EXTERNAL DATA

## C.1 CFPB Consumer Complaints (PSLF subset)

**File:** `admin_data_pslf_complaints.csv`
**n records:** 12,552 (2016-2026)
**Source:** CFPB Consumer Complaints API + PSLF/student-loan filter
**Columns:** `complaint_id`, `product`, `complaint_what_happened`, `date_received`, `date_sent_to_company`, `issue`, `sub_product`, `sub_issue`, `zip_code`, `state`, `tags`, `company`, `company_response`, `consumer_consent_provided`, `submitted_via`, `consumer_disputed`, `company_public_response`, `timely`, `query_matched`, `date`
**Used for:** P6 (CFPB vs discourse topic comparison), P10 (CFPB by company timeline)
**Year-by-year volume:**
- 2016: 341
- 2017: 1,391
- 2018: 1,053
- 2019: 1,007
- 2020: 511
- 2021: 519
- 2022: 1,278
- 2023: 1,885
- 2024: 2,116
- 2025: 2,223
- 2026 (Q1-May): 228

## C.2 NRMP Program-Level Match Data

**File:** `nrmp_program_level_2021_2025.csv`
**n records:** 30,763 program-years
**n institutions:** 789 (with city populated for 99.8%)
**Date range:** 2021-2025 (5 years)
**Source:** NRMP "Program Results: Main Residency Match 2021-2025 Appointment Years" PDF (downloaded via `nrmp_pdfs/2021_2025_program_results.pdf`)
**Extracted via:** `scripts/collect_nrmp_program_level.py` (PDF parser)
**Columns:** `institution`, `state`, `city`, `program_name`, `program_code`, `specialty_code`, `specialty`, `program_type_code`, `program_type`, `year`, `quota`, `filled`, `fill_rate`, `pslf_class`, `pslf_evidence`
**City population:** `extract_nrmp_cities.py` populated city for 99.8% of rows

**File:** `nrmp_program_level_2016_2020_backfill.csv`
**n records:** 19,870 program-years
**n institutions:** 1,425 unique
**Date range:** 2016-2020
**Source:** NRMP main match books 2016, 2017, 2018, 2019, 2020 (5 separate PDFs)
**Extractor:** `scripts/extract_nrmp_backfill_2016_2020.py`

## C.3 NRMP PSLF Eligibility Verification

**File:** `nrmp_institution_pslf_classification.csv` (heuristic)
**File:** `nrmp_institution_pslf_verified.csv` (ProPublica-verified)
**n institutions:** 797 unique institution-state pairs
**Source:** ProPublica Nonprofit Explorer API (IRS BMF lookups)
**Verifier:** `scripts/verify_nrmp_pslf_eligibility.py`
**Result distribution:**
- pslf_eligible_501c3: 431
- no_propublica_match: 331
- pslf_ineligible_for_profit: 22
- pslf_unclear_other_subsec: 8
- pslf_eligible_gov: 5

## C.4 HRSA HPSA Designations

**File:** `hrsa_hpsa_primary_care.csv`
**n records:** 77,818 raw → 19,045 designated primary-care HPSAs
**Date:** 2024 snapshot
**Source:** HRSA HPSA primary-care download (45 MB)
**URL pattern:** https://data.hrsa.gov/DataDownload/DD_Files/BCD_HPSA_FCT_DET_PC.csv
**Columns:** `HPSA Name`, `HPSA ID`, `Designation Type`, `HPSA Discipline Class`, `HPSA Score`, `PC MCTA Score`, `Primary State Abbreviation`, `HPSA Status`, `HPSA Designation Date`, plus 50+ more (lat/lon, county, FIPS, etc.)
**Used for:** P4, P5

## C.5 CMS Hospital Compare

**File:** `cms_hospital_general.csv`
**n hospitals:** 5,426
**Source:** CMS Provider Data Catalog API (Hospital General Information dataset)
**Dataset ID:** xubh-q36u
**Columns:** `Facility ID`, `Facility Name`, `Address`, `City/Town`, `State`, `ZIP Code`, `County/Parish`, `Hospital Type`, `Hospital Ownership`, `Hospital overall rating` (1-5 stars), MORT/Safety/READM/Pt-Exp/TE measures
**CMS ownership distribution:**
- Voluntary non-profit - Private: 2,304 (PSLF-eligible)
- Proprietary: 1,069 (PSLF-INELIGIBLE)
- Government - Hospital District/Authority: 519
- Government - Local: 401
- Voluntary non-profit - Other: 355
- Voluntary non-profit - Church: 271
- Government - State: 209
- Veterans Health Administration: 132
- Physician (independent): 76
- Government - Federal: 43
- Department of Defense: 32
- Tribal: 15
**Used for:** P8, P11

## C.6 NHSC Field Strength

**Files:** `nhsc_field_strength_FY2019.xlsx` through `nhsc_field_strength_FY2025.xlsx` (7 files)
**Source:** HRSA NHSC Field Strength annual reports
**URL pattern:** https://data.hrsa.gov/DataDownload/StaticDocuments/FY%20[YEAR]%20NHSC%20Field%20Strength.xlsx
**National total trajectory:**
- 2019: 13,306
- 2020: 16,562
- 2021: 20,448
- 2022: 20,697 (peak)
- 2023: 18,703
- 2024: 17,706
- 2025: 18,846
**Sheets per file:** 2024 NHSC Field Strength, Primary Care FS, Oral Health FS, Mental Health FS, Rural FS, Non-Rural FS
**Used for:** P12

## C.7 US Cities Database (city → county lookup)

**File:** `uscities.csv`
**n cities:** 31,120
**Source:** SimpleMaps US Cities free CSV (1.86 MB)
**Columns:** `city`, `city_ascii`, `state_id`, `state_name`, `county_fips`, `county_name`, `lat`, `lng`, `population`, `density`
**Used for:** P5, P11 (NRMP city → HPSA county matching)

## C.8 FSA PSLF Admin Data (B1)

**File:** `fsa_pslf_admin_data.csv`
**Source:** Hand-curated milestone timeline (FSA quarterly reports)
**Status:** Quarterly format limitations; used hand-curated milestone fallback
**Used for:** B1 (NULL correlation finding)
**Result:** r=−0.20 to +0.04 across 4 specifications (all p>0.49)

## C.9 NRMP PDFs downloaded

`nrmp_pdfs/` directory contains:
- `2016_main_match.pdf` (520 KB)
- `2017_main_match.pdf` (760 KB)
- `2018_main_match.pdf` (789 KB)
- `2019_main_match.pdf` (867 KB)
- `2020_main_match.pdf` (772 KB)
- `2020_alt.pdf` (772 KB, alternate)
- `2021_main_match.pdf` (839 KB)
- `2022_main_match.pdf` (957 KB)
- `2023_main_match.pdf` (909 KB)
- `2024_main_match.pdf` (1,235 KB)
- `2024_state_specialty.pdf` (258 KB)
- `2025_main_match.pdf` (2,640 KB)
- `2021_2025_program_results.pdf` (2,457 KB) — primary source for B5

**Missing (Wayback Machine retry pending):** 2010-2015

---

# SECTION D: ALL SCRIPTS (82 total, organized by category)

## D.1 Data Collectors (12 scripts)

| Script | Purpose | Status |
|---|---|---|
| `collect_reddit_arctic_shift.py` | Arctic Shift API; 72,262 PSLF posts | ✅ Run R8 |
| `collect_reddit_professions.py` | Reddit JSON API year-windowed | ✅ Run R3 |
| `collect_reddit_baseline.py` | r/AskReddit + topical-near | ✅ Run R3 |
| `collect_reddit_comments.py` | PRAW comment trees | 🟡 Partial (~17K of 76K coverage) |
| `collect_reddit_comments_no_auth.py` | No-auth JSON comments | 🟡 Partial |
| `collect_forum_data.py` | SDN Playwright + requests/BS4 | ✅ Run |
| `collect_fsa_pslf_admin_data.py` | FSA cumulative approvals | ✅ Run B1 |
| `collect_nrmp_program_level.py` | NRMP PDF parser (2021-2025) | ✅ Run R10 |
| `collect_youtube_pslf.py` | YouTube comments via Data API v3 | 🟢 Built (needs API key) |
| `collect_bogleheads.py` | Bogleheads scraper | ❌ Cloudflare-blocked |
| `collect_allnurses.py` | allnurses scraper | ❌ Cloudflare-blocked |
| `collect_pa_forum.py` | PA Forum scraper | ❌ Cloudflare-blocked |

## D.2 Data Extractors (3 scripts)

| Script | Purpose |
|---|---|
| `extract_nrmp_cities.py` | Re-parse NRMP PDF for city info (99.8% coverage) |
| `extract_nrmp_backfill_2016_2020.py` | 5-year NRMP backfill (19,870 rows) |
| `extract_rejection_reasons.py` | Coded PSLF rejection reasons from text |

## D.3 Sentiment Scorers (5 scripts)

| Script | Purpose |
|---|---|
| `sentiment_vader.py` | VADER compound on all posts |
| `sentiment_zeroshot.py` | Claude Sonnet 4 zero-shot (R7 fix: temperature=0 + circuit breaker) |
| `sentiment_zeroshot_openweight.py` | Together AI Llama 3 / OpenAI GPT-4o (built, awaiting user run) |
| `score_vader_arctic_shift.py` | VADER on Arctic Shift posts |
| `compute_vader_on_comments.py` | VADER on 460K comments |

## D.4 Sample Selection (1 script)

| Script | Purpose |
|---|---|
| `select_arctic_shift_for_claude.py` | Stratified sampling for R8 Claude scoring |

## D.5 Methods Analyses (10 scripts)

| Script | Purpose | Output |
|---|---|---|
| `sentiment_triangulation.py` | Three-rater Krippendorff α + per-event tests + Figure 7 | `triangulation_results.{txt,csv}` |
| `triangulation_with_comments.py` | Comments-scale TB×VADER α | `triangulation_comments_results.txt` |
| `analyze_specification_curve.py` | 360-spec curve (A2) | `spec_curve_results.{txt,csv,png}` |
| `analyze_a2_spec_curve_decomposition.py` | r/PSLF flip decomposition | `spec_curve_decomposition.{txt,csv}` |
| `analyze_a3_firth_correction.py` | Firth/HA OR for sparse cells | `a3_firth_corrected_results.{txt,csv}` |
| `analyze_l5_cohort_robustness.py` | 5-spec cohort robustness | `l5_cohort_robustness_results.{txt,csv}` |
| `analyze_op_vs_reply.py` | OP vs Reply construct mismatch | `op_vs_reply_results.{txt,csv}` |
| `analyze_op_reply_per_event.py` | OP vs Reply per-event | `op_reply_per_event_results.{txt,csv}` |
| `compare_openweight_vs_claude.py` | OW vs Claude inter-LLM agreement | `openweight_vs_claude_results.{txt,csv,png}` |
| `confound_audit.py` | Platform×profession, length×polarity tests | `confound_audit_results.txt` |

## D.6 Substantive Analyses (10 scripts)

| Script | Purpose | Output |
|---|---|---|
| `analyze_multi_source.py` | Cross-platform/profession statistical analysis | base findings |
| `pslf_intention_analysis.py` | Claude `pslf_stance` analysis (R7) | `intention_results.{txt,csv}`, intention_*.png |
| `analyze_mediation_career_stage.py` | A3 career-stage mediation | `mediation_career_stage_results.{txt,csv}` |
| `analyze_per_profession_breakdowns.py` | Per-profession decoupling | `per_profession_breakdowns.txt` |
| `analyze_per_profession_per_event.py` | Per-event × per-profession (R8) | `per_profession_per_event_results.txt` |
| `analyze_topic_per_cohort_per_event.py` | Topic shifts per cohort × event | `topic_per_cohort_per_event_results.txt` |
| `analyze_cohort_heterogeneity_comments.py` | C1 cohort heterogeneity at comments scale | `cohort_heterogeneity_comments_results_*.csv` |
| `analyze_comment_cohort_heterogeneity.py` | Comment-level cohort heterogeneity | `comment_cohort_heterogeneity_results.csv` |
| `analyze_per_author_with_comments.py` | Per-author longitudinal panel | `per_author_with_comments_results.csv` |
| `analyze_time_to_recovery.py` | Time-to-recovery per cohort | `time_to_recovery_results.{txt,csv}` |

## D.7 Sub-Analyses (5 scripts)

| Script | Purpose |
|---|---|
| `analyze_rejection_reasons.py` | PSLF rejection reasons coding |
| `analyze_sdn_subthread_consistency.py` | SDN subthread consistency check |
| `analyze_l4_sdn_attending_comments.py` | L4 SDN attending in comments |
| `topic_model_bertopic.py` | BERTopic topic modeling on full corpus |
| `placebo_test_topical_near.py` | Placebo test against topical-near baseline |

## D.8 Linking Analyses (4 scripts)

| Script | Purpose |
|---|---|
| `verify_nrmp_pslf_eligibility.py` | L1 ProPublica IRS verification |
| `analyze_l2_discourse_to_nrmp_specialty.py` | L2 discourse → NRMP fill |
| `analyze_l3_topic_fsa_responsiveness.py` | L3 topic-level FSA responsiveness |
| `analyze_c1_threshold_sensitivity.py` | C1 time-to-recovery threshold sensitivity |

## D.9 Policy Analyses (12 P-series + 1 base = 13 scripts)

| Script | Purpose | P # |
|---|---|---|
| `analyze_nrmp_program_pslf.py` | B5 base NRMP × PSLF analysis | (B5) |
| `analyze_policy_state_heatmap.py` | State-level discourse heatmap | P1 |
| `analyze_policy_servicer_specific.py` | MOHELA/FedLoan/etc. discourse | P2 |
| `analyze_policy_process_issues.py` | Process-issue prevalence | P3 |
| `analyze_policy_hrsa_hpsa_nrmp.py` | HPSA state-level | P4 |
| `analyze_policy_p5_county_hrsa_nrmp.py` | HPSA county-level | P5 |
| `analyze_policy_p6_cfpb_topic_comparison.py` | CFPB vs discourse topics | P6 |
| `analyze_policy_p7_nrmp_pre_post_waiver.py` | Pre/post Limited Waiver | P7 |
| `analyze_policy_p8_cms_quality.py` | CMS quality cross-check | P8 (superseded) |
| `analyze_policy_p9_within_institution_pre_post.py` | Within-institution DiD | P9 |
| `analyze_policy_p10_cfpb_company_timeline.py` | CFPB by company timeline | P10 |
| `analyze_policy_p11_improved_cms_matching.py` | Improved CMS-NRMP matching | P11 |
| `analyze_policy_p12_nhsc_vs_pslf.py` | NHSC vs PSLF comparison | P12 |

## D.10 Sensitivity Tests (2 scripts)

| Script | Purpose |
|---|---|
| `sensitivity_excl_sdn_medical.py` | Sensitivity excluding SDN-Medical |
| `placebo_test_topical_near.py` | Placebo against off-PSLF baseline |

## D.11 Figure Generators (10 scripts)

| Script | Purpose | Figures |
|---|---|---|
| `gen_legislative_timeline.py` | Legislative timeline + pre/post + sensitivity | `pslf_sentiment_legislative_timeline.png`, `pslf_pre_post_events.png`, `pslf_profession_timecourse.png` |
| `gen_hires_figs.py` | Multi-source comparison + word clouds | `multi_source_sentiment_comparison.png`, `pslf_wordcloud_timecourse.png` |
| `gen_volume_artifact_figure.py` | R/C ratio diagnostic (3 panels) | `pslf_volume_artifact.png` |
| `gen_volume_artifact_arctic_shift.py` | Arctic Shift R/C diagnostic | `volume_artifact_arctic_shift.png` |
| `plot_master_timeline.py` | Master timeline (single scorer) | `pslf_master_timeline.png` |
| `plot_master_timeline_3scorer.py` | Master timeline (3 scorers) | `pslf_master_timeline_3scorer.png` |
| `plot_event_timecourses.py` | Per-event sentiment timecourses | `pslf_event_timecourses.png`, `_combined.png`, `_vader.png` |
| `plot_claude_dimensions.py` | Claude 3-dim multi-panel | `pslf_claude_dimensions.png` |
| `plot_claude_dimensions_by_event.py` | Claude 3-dim by event | `pslf_claude_dimensions_by_event.png` |
| `plot_sdn_nrmp_alignment.py` | SDN-NRMP timeline alignment | `fig_substantive_5_sdn_nrmp_alignment.png` |
| `generate_paper_figures.py` | All publication-ready figures | `fig_methods_*.png`, `fig_substantive_*.png` |

## D.12 Utilities (5 scripts)

| Script | Purpose |
|---|---|
| `pslf_search_terms.py` | Anchored PSLF filter regex (`filter_pslf_relevant`) — 17/17 unit tests |
| `final_summary.py` | Statistical summary report (R5: canonical 8-event list) |
| `build_master_numbers_table.py` | Build master numbers table |
| `critical_fixes.py` | R7 critical fixes implementation |
| `debug_sdn.py` | SDN scrape debugging |
| `save_pages.py` | HTML page saving utility |

---

# SECTION E: AUDIT ROUNDS R1-R12 (DETAILED)

## R1: Internal Audits (April 2026)

**46 issues fixed across 4 internal audit passes.** Basic methodology cleanup.

## R2: 4-Agent Independent Consensus (April 2026)

**5 CRITICAL fixes:**
1. Filter divergence (`gen_hires_figs.py` was using broad regex while all other scripts used strict)
2. `wc<20` nullification inconsistency across scripts
3. Mislabeled "Glass's delta" formula → replaced with **Hedges' g** + **Glass's Δ_pre** both reported
4. Cross-correlation broken (positional shift on irregular index, no detrending) → **first-differenced + reindexed (Box-Jenkins 1970)**
5. Bonferroni correction applied to one place but not others → **uniform application**

**~14 MAJOR fixes** including:
- Strict regex tightened with PSLF-anchor co-occurrence rule
- Subreddit count reconciled (18 entries)
- CLAUDE.md reframed as associational, not causal

## R3: Methodological Depth (April 2026)

- **Real moving-block bootstrap (Künsch 1989, B=2000)** — replaced previous IID permutation
- **R/C ratio diagnostic** added to `analyze_admin_data_correlation.py`
- **Improved baseline**: drop sort=top, n=1000 target, length-matched, plus topical-near baseline
- **Year-windowed Reddit collector**: t=year/all/month/week × sort modes; recovered 3-4× more pre-2020 posts

## R4: Publication-Readiness Audit (April 2026)

- **Length-residualised analysis** added (residuals of polarity ~ log(word_count) + source + profession)
- **Knight/Ellsberg "ambiguity-aversion" framing dropped** — was unsupported by the design
- **Reframed throughout**: "online discussants" not "borrowers"

## R5: Audit Fixes (May 7, 2026)

- **Bootstrap reproducibility & validity**: per-event seeds + B_actual tracking
- **OLS collinearity fix**: QR rank check on design matrix drops perfectly-collinear dummies (`src_sdn` ≡ `prof_sdn_medical` for SDN posts)
- **`sentiment_zeroshot.py` hardening**: preflight auth check + AuthenticationError fail-fast + 5-error circuit breaker (after 715-call burn on auth errors)
- **Traceability artifact**: `legislative_timeline_results.txt` + `.csv` emitted alongside figures
- **`final_summary.py` rewrite**: aligned with canonical 8-event list, added length-residualised + Glass's delta, dynamic date stamp
- **Sample-size & R/C language reconciliation**: 9,629 strict-filtered / 8,788 sentiment-eligible / 7,918 in legislative-timeline analysis
- **Bonferroni interpretation correction**: only Trump EO clearly passes bootstrap-Bonferroni; Biden v. Nebraska is at the boundary

## R6: Copilot PR Review (May 8, 2026)

7 items addressed:
- UTF-8 stdout wrapper in `confound_audit.py` (mojibake fix)
- Dynamic R/C multiplier in `gen_volume_artifact_figure.py` (was hardcoded 84×)
- `--stratify-events` help text correction
- Trump event label standardisation
- Dropped misleading "Vectorized" docstring
- Dynamic subsample count in triangulation artifact
- Corrected `collect_allnurses` return type

## R7: Critical Methodological Fixes (May 8, 2026)

**6 Tier-1 critical fixes:**

1. **Bootstrap rewrite** (`gen_legislative_timeline.py:386-411`): Bickel et al. 1989 block-permutation WITHOUT replacement, replacing wrong-null moving-block-with-replacement
2. **Hedges' g variance with J² correction** (`gen_legislative_timeline.py:484`, `sentiment_triangulation.py:117`): Borenstein et al. 2009 eq. 4.24
3. **Krippendorff α bootstrap CI** (`sentiment_triangulation.py:208-306`): Hayes & Krippendorff 2007, B=2,000 stratified bootstrap
4. **Acknowledge percentile-matched α as charitable upper bound, not canonical** (`sentiment_triangulation.py:255-268`)
5. **Test-retest reliability for Claude** (`sentiment_zeroshot.py`): re-score 200 posts at temperature=0, compute test-retest α. Result: **α=+0.958 (95% CI [+0.938, +0.975]) on n=605 SDN posts. Closes LLM-noise objection.**
6. **Confound-audit asymmetry bug** (`confound_audit.py:99-102`): replaced one-sided test with `|stratified − naive|/|naive| > 0.5`

**6 Should-Fix items** (also addressed):
7. Holm-Bonferroni step-down adjustment
8. HC3 robust SEs in OLS
9. Per-event block permutation
10. Window-sensitivity SD reporting
11. APA p-value reporting (`p<10⁻⁷` instead of `p=0.000000`)
12. Stale `~50 pre + ~50 post` comment in `triangulation_results.txt:57`

**R7 expansion** (May 8):
- Added `pslf_intention_analysis.py` separating PSLF behavioral commitment (`pslf_stance`) from sentiment
- Added 3 new subreddits (PAstudent, prephysicianassistant, CRNA, +52 PSLF posts)
- Floor-effect investigation: SDN-Medical author overlap across 8 events ranges 18-42%; per-author longitudinal infeasible for 7/8 events

## R8: Arctic Shift Expansion (May 9, 2026)

- **+72,262 new PSLF posts** from Arctic Shift archive
- Reddit corpus expanded ~6.4× (from 11,793 → 76,074 PSLF-strict-filtered)
- VADER scored on all Arctic Shift posts (free, ~5 min)
- 2,281-post stratified Claude scoring of Arctic Shift event-window cells (~$13)
- **n=9,242 with all three scorers** (sample-stable: α=−0.018 to −0.020 across n=4,838 → 9,242 expansions)
- SDN-Medical-excluded sensitivity: α=−0.009 (delta only +0.009)
- Per-event × per-profession analysis newly possible at scale

**Key R8 substantive finding:** Cohort heterogeneity in event response. SDN-Medical and Reddit-general respond OPPOSITE directions on 5/8 events.

## R9: Cohort Heterogeneity Headline (May 10, 2026)

**Substantive paper's new lead finding.** Sentiment-stance decoupling has DIRECTIONALLY OPPOSITE cohort heterogeneity:
- Reddit r/PSLF (n=1,469): OR=7.33 (95% CI [4.20, 12.78], p=6×10⁻¹⁶)
- SDN-Medical (n=1,960): OR=0.27 (95% CI [0.22, 0.34], p=3×10⁻³¹)
- Reddit Finance (n=999): OR=0.18 (95% CI [0.11, 0.30], p=2×10⁻¹³)
- Reddit r/StudentLoans, Medical, Teaching: null

**Methods paper update:** OP vs Reply construct mismatch within identical posts:
- TB Δ (OP − reply) = −0.017 (95% CI [−0.019, −0.014], cluster bootstrap p=0)
- VADER Δ (OP − reply) = +0.220 (95% CI [+0.212, +0.230], cluster bootstrap p=0)
- Cohort-invariant: same direction in 8/8 cohorts

## R10: Policy P-Series + Initial Audits (May 10, 2026)

12 P-series policy analyses:
- P1: state-level discourse heat map
- P2: MOHELA discourse polarity dropped 50%
- P3: PSLF Buyback exploded 3500×
- P4: HPSA state-level interaction
- P5: HPSA county-level (gap LARGEST in URBAN, +26pp)
- P6: CFPB vs discourse — Buyback 5.47× over-discussed
- P7: Pre/post Limited Waiver — gap is structural
- P8: CMS quality cross-check (CRITICAL — superseded by R12)
- P9: Within-institution pre/post
- P10: CFPB by company timeline (MOHELA 1.7% → 63% in 1 year)

Plus L-series linking:
- L1: ProPublica IRS BMF verification of NRMP institutions
- L2: Discourse → NRMP fill rate (NULL)
- L3: Topic-level FSA responsiveness (NULL)
- L4: SDN attending pattern at comments scale (NULL — no Claude on comments)
- L5: Cohort heterogeneity robustness across 5 instrument×stance specs

## R11: P8 Audit Caveat (May 10, 2026, ~14:30)

**P8 CMS hospital-name matching at 31.5% match rate.** After controlling for hospital quality + state FE in this matched subset, the PSLF-eligibility coefficient drops to **−1.58pp NS (p=0.09)**.

This APPEARED to refute the B5 +12.86pp gap finding.

Round 11 audit document (`AUDIT_round11_P8_CMS_correction.md`) updated all policy claims with CMS quality caveat. **Now superseded.**

## R12: P11 REVERSAL — Current State (May 10, 2026, ~15:25)

**P11 city-aggregate matching at 96.2% match rate REFUTES P8.**

| Model | PSLF-hostile coefficient | p-value |
|---|---|---|
| 1 (PSLF only) | −18.76 pp | < 10⁻⁸⁴ |
| 2 (+ city CMS quality) | −17.90 pp | < 10⁻⁷⁶ |
| 3 (+ state FE) | −19.00 pp | < 10⁻⁷³ |
| 4 (+ specialty FE) | **−18.56 pp** | **< 10⁻⁷⁵** |

**The PSLF mechanism dominates the quality effect by ~4×.** B5 stands.

**Why P8 gave the wrong answer:** 31.5% match rate was sampling-biased toward academic medical centers (where institution name = CMS hospital name). For-profit chain residencies (where GME consortium ≠ host hospital) didn't match. P11 city-aggregation captures both because they share cities.

**Lesson learned:** When match rate is below ~70%, sampling bias should be explicitly tested. Aggregation strategies achieving 90%+ coverage are preferable to hospital-name matching at 30% coverage.

---

# SECTION F: METHODS PAPER FINDINGS (DETAILED)

## F.1 Three-rater Krippendorff α (canonical headline)

**n=9,242** posts with all three scorers
- **Canonical α = −0.018** (95% CI [−0.031, −0.005]) — stratified bootstrap by source, B=2,000
- **Charitable α = +0.196** (95% CI [+0.183, +0.208]) — percentile-matched ordinal upper bound

Both well below the 0.667 floor for tentative reliability claims (Krippendorff 1980).

**Sample stability:** α essentially unchanged across expansion:
- n=4,838 (R7 baseline): α = −0.020
- n=6,975 (R7 fullcorpus): α = −0.018
- **n=9,242 (R8 Arctic Shift): α = −0.018** (canonical)

**Sensitivity exclusions:**
- SDN-Medical excluded (n=6,111 non-SDN posts): α = −0.009 (delta +0.009; robust)

## F.2 Test-retest reliability (R7 fix #5)

**n=605 SDN posts re-scored at temperature=0 vs temperature=1**
- α = +0.958 (95% CI [+0.938, +0.975])
- Exact-match rate: 95.2%

**Closes the "disagreement is just LLM stochasticity" objection.**

## F.3 Per-instrument pairwise correlations (n=4,787 → 9,242)

- TextBlob × VADER: r = 0.30 (Pearson)
- TextBlob × Claude: r = 0.02 (Pearson, p=0.09)
- VADER × Claude: r = 0.12 (Pearson)

**Marginal class distributions diverge sharply:**
- VADER calls 67% of posts very_positive
- Claude calls 4.3% very_positive
- Claude calls 47.6% neutral
- VADER calls 2.5% neutral

**The three instruments are measuring different latent constructs.**

## F.4 Comments-scale extension

**File:** `triangulation_comments_results.csv`
- TB×VADER α at n=460,000 PSLF comments: **+0.298** (cluster CI [+0.295, +0.302])
- Design effect 1.36

**Extends the methods finding from posts (n=9,242) to comments scale (50× larger).**

## F.5 Trump PSLF EO joint Hotelling T² (R8 finding)

**n=1,330** posts in Trump EO event window
- Joint Hotelling T² (TB, VADER, Claude joint shift): F=30.95, p=1.11×10⁻¹⁶
- Joint shift decisively non-zero
- **Components are directionally split:**
  - TextBlob g = −0.32 (95% CI tight; p<10⁻⁶)
  - VADER g = +0.16 (p=0.0007)
  - Claude g = +0.33 (p<10⁻⁶)

**Lead methods exemplar.**

## F.6 OP vs Reply construct mismatch (R9 finding)

**Within identical post threads:**
- TB Δ (OP − reply) = −0.017 (95% CI [−0.019, −0.014], cluster bootstrap p=0)
- VADER Δ (OP − reply) = +0.220 (95% CI [+0.212, +0.230], cluster bootstrap p=0)
- **Cohort-invariant**: same direction in 8/8 cohorts
- VADER significant in 8/8; TB significant in 6/8

**No published precedent in 2-hour deep literature search.** Strongest single methods exemplar.

## F.7 Per-event direction concordance

**At Path C well-powered triangulation (n_event=313-771):**

Only 2/8 events triple-concordant:
- Biden Mass Forgiveness: TB g=−0.245, VADER g=−0.358, Claude g=−0.363 (all negative)
- Biden v. Nebraska SCOTUS: TB g=−0.436, VADER g=−0.303, Claude g=−0.049 (Claude essentially null)

6/8 events have at least one scorer disagreeing on direction.

## F.8 L5 Cohort robustness (R10 finding)

For each cohort, 5 OR specifications:

| Cohort | Specs OR>1 | Specs OR<1 | Verdict |
|---|---|---|---|
| **SDN (Medical)** | 0 | 5 | **CONCORDANT — bulletproof** |
| Reddit r/PSLF | 4 | 1 | DISCORDANT (1 spec flips: pur+completed) |
| Reddit Finance | 2 | 3 | **DISCORDANT (TB and VADER give OR>1!)** |
| Reddit r/StudentLoans | 3 | 2 | DISCORDANT |
| Reddit Medical | 2 | 3 | DISCORDANT |

**Detailed L5 OR table:**

| Cohort | Spec | n | OR | 95% CI |
|---|---|---|---|---|
| Reddit r/PSLF | Claude-neg × Claude-pur (original) | 1,469 | 7.329 | [4.20, 12.78] |
| Reddit r/PSLF | TB-neg × Claude-pur | 1,469 | 1.655 | [0.97, 2.83] |
| Reddit r/PSLF | VADER-neg × Claude-pur | 1,469 | 2.526 | [1.53, 4.18] |
| Reddit r/PSLF | Claude-neg × Claude-pur-only | 1,469 | 5.207 | [3.54, 7.65] |
| Reddit r/PSLF | Claude-neg × Claude-pur-or-completed | 1,469 | 0.194 | [0.04, 1.01] |
| SDN (Medical) | Claude-neg × Claude-pur (original) | 1,960 | 0.272 | [0.22, 0.34] |
| SDN (Medical) | TB-neg × Claude-pur | 1,960 | 0.147 | [0.10, 0.22] |
| SDN (Medical) | VADER-neg × Claude-pur | 1,960 | 0.334 | [0.26, 0.43] |
| SDN (Medical) | Claude-neg × Claude-pur-only | 1,960 | 0.361 | [0.29, 0.46] |
| SDN (Medical) | Claude-neg × Claude-pur-or-completed | 1,960 | 0.056 | [0.04, 0.08] |
| Reddit Finance | Claude-neg × Claude-pur (original) | 999 | 0.182 | [0.11, 0.30] |
| Reddit Finance | TB-neg × Claude-pur | 999 | 1.103 | [0.33, 3.66] |
| Reddit Finance | VADER-neg × Claude-pur | 999 | 1.423 | [0.72, 2.82] |
| Reddit Finance | Claude-neg × Claude-pur-only | 999 | 0.369 | [0.25, 0.54] |
| Reddit Finance | Claude-neg × Claude-pur-or-completed | 999 | 0.104 | [0.06, 0.18] |

## F.9 A2 Specification curve (360 specs)

For each cohort × analytic specification combination:

- **SDN (Medical)**: 100% of 72 specs OR<1, 100% sig — BULLETPROOF
- **Reddit Finance**: 94% OR<1, 83% sig — VERY ROBUST
- **Reddit r/PSLF**: 67% OR>1, 67% sig — FRAGILE (33% of specs flip direction)

A2 decomposition: r/PSLF flip is driven entirely by **`pur_def`** (whether "completed" PSLF posters count as "pursuing"):
- `pursuing_considering_completed`: 100% OR<1
- `pursuing_only`: 100% OR>1
- `pursuing_or_considering`: 100% OR>1

Other dimensions (`neg_def`, `excl_arctic`, `excl_sdn`, `min_n`) inert.

---

# SECTION G: SUBSTANTIVE PAPER FINDINGS (DETAILED)

## G.1 Cohort-conditional sentiment-stance decoupling (R9 headline)

(See Section F.8 for full table)

**Same negative-sentiment post means different things in different communities.**

## G.2 Composition shifts (R7 floor-effect investigation + R8)

Per-author longitudinal panel feasibility test:
- Required threshold: n>=10 returning-with-stance authors per event
- **Met for only 1 of 8 events** (Trump PSLF EO with n=12-13 returning, McNemar p=0.625)
- Other events: 3-8 returning authors

**SDN-Medical author overlap by event:**
- Limited Waiver: 18% (lowest)
- Trump EO: 42% (highest)
- Final Trump Rule: 0% (zero overlap)

**Pre/post stance shifts must be interpreted as discussant-pool composition shifts, not borrower stance changes.**

## G.3 A3 mediation by career stage

**SDN attending:** HA-corrected OR=0.024 (naive 0.016), p=8e-08, n=88
- a (neg+pur)=12, b (neg+not_pur)=12, c (not_neg+pur)=63, d (not_neg+not_pur)=1
- The d=1 cell drives the naive estimate, but HA correction confirms extreme decoupling

**SDN fellow:** OR=0.085 (naive), 0.118 (HA), p=0.017, n=152
**SDN resident:** OR=0.943 (naive), 0.913 (HA), NS, n=66

**Pure-career-stage OR (cohort-pooled):**
- attending: OR=0.07, p=1.4e-07, n=137
- medical_student: OR=0.10, p=0.033, n=68
- resident: OR=1.16, NS, n=209
- fellow: OR=0.65, NS, n=292

**Mechanism revision:** SDN's decoupling is *seniority-driven, not stake-driven*. Senior physicians (attendings, fellows) who post negatively have made credible decisions to walk away.

## G.4 Per-event topic restructuring

All 8 events show highly significant topic shifts (chi-sq p<10⁻⁴):

| Event | Largest topic shifts |
|---|---|
| Limited Waiver | success_story −31.6pp, financial_planning +13.2pp |
| **IDR Account Adjustment** | **financial_planning +49.2pp** (largest in dataset), general_question −30.5pp |
| Biden Mass Forgive | career_impact −35.8pp, general_question +23.1pp |
| Biden v. Nebraska | policy_uncertainty +23.0pp, financial_planning −21.6pp |
| Payments Restart | policy_uncertainty −24.3pp, financial_planning +14.1pp |
| SAVE Forbearance | financial_planning −29.1pp, career_impact +26.7pp |
| Trump PSLF EO | policy_uncertainty −21.7pp (counterintuitive), financial_planning +12.9pp |
| Final Trump Rule | policy_uncertainty +16.5pp, general_question −9.0pp |

**These topic shifts are MORE STATISTICALLY ROBUST than per-event sentiment shifts.**

## G.5 Per-event × per-profession topic shifts

Of 9 (event, profession) cells with n_pre, n_post >= 20: **8 highly significant** (chi-sq p<0.001).

Most striking findings:
- **IDR Adjustment × SDN-Medical**: financial_planning 17.3% → **78.8% (+61.5pp)** — biggest single profession-level topic shift
- **Trump PSLF EO × SDN-Medical**: policy_uncertainty 63.6% → 36.3% (−27.3pp); career_impact 7.5% → 25.6% (+18.1pp); financial_planning 9.1% → 25.6% (+16.4pp)
- **Biden v. Nebraska × SDN-Medical**: policy_uncertainty 9.5% → 42.7% (+33.2pp)

## G.6 Per-event × per-profession sentiment shifts

Coverage dominated by SDN-Medical. Patterns:
- **Convergent profession response to administrative resolution**: Final Trump PSLF Rule reduced rejecting-rate by 43.9pp in SDN-Medical AND 32.1pp in Finance (p=0.030)
- **Divergent profession response to ambiguous policy**: Biden Mass Forgiveness moved SDN-Medical rejecting −19pp NS but Reddit Medical +10pp NS (opposite signs across two medical communities)
- **PA-specific Claude sentiment cells** (R7 PA top-up): SAVE Forbearance × PA g=+0.74 (n=17/10, p=0.054 marginal) — opposite SDN's g=−2.33

## G.7 Career stage extracted from text (~15% coverage)

n=718 of 4,842 posts with explicit career-stage markers (14.8% coverage):
- **Residents most polarized**: 44.6% pursuing AND 14.9% rejecting (n=121)
- **Fellows most stable**: 65.2% considering, 29.9% pursuing, 3.4% rejecting (n=204)
- **Attendings high rejection**: 14.8% rejecting, 19.4% pursuing (n=108)
- **Medical students skew pursuing/considering**: 33.3% pursuing, 57.8% considering, 8.9% rejecting (n=45)

## G.8 Time-to-recovery per cohort (Trump EO exemplar)

**±0.02 threshold of pre-event mean (7-day rolling):**
- Reddit r/PSLF: 2 days
- Reddit r/StudentLoans: 2 days
- Reddit Medical: 2 days
- Reddit Finance: NO recovery in 90 days
- Reddit PA: NO recovery in 90 days

**Threshold sensitivity (C1):**

| Cohort | ±0.005 | ±0.01 | ±0.02 | ±0.05 | ±0.10 |
|---|---|---|---|---|---|
| Reddit r/PSLF | 9d | 3d | 2d | 2d | 2d |
| Reddit r/StudentLoans | 5d | 2d | 2d | 2d | 2d |
| Reddit Finance | >90d | >90d | >90d | 33d | 33d |
| Reddit Medical | 53d | 52d | 2d | 2d | 2d |
| Reddit PA | >90d | >90d | >90d | 74d | 26d |

Pattern direction is robust; magnitude is threshold-sensitive.

---

# SECTION H: POLICY PAPER FINDINGS (DETAILED — P-SERIES + B5 + L1-L5)

## H.1 B5 + L1 + P11: PSLF recruitment gap (HEADLINE)

### B5 baseline (R10)
- **PSLF-eligible programs (heuristic)**: n=17,596 program-years, mean fill **93.9%**
- **PSLF-ineligible programs**: n=763, mean fill **81.1%**
- **Gap: +12.86 pp** (p=3.4×10⁻²⁷, Cohen's d=+0.62)

### Specialty pattern (B5)

| Specialty | Mean PSLF-friendly | Mean PSLF-hostile | Gap (pp) | p-value |
|---|---|---|---|---|
| Internal Medicine | 94.3% | 66.0% | **+28.2** | 5.8e-21 |
| Family Medicine | 88.3% | 73.2% | +15.1 | 1.6e-04 |
| Emergency Medicine | 93.0% | 77.8% | +15.2 | 9.7e-04 |
| Pediatrics | n_hostile<10 | — | — | — |
| Dermatology | 98.9% | 95.5% | **+3.4** | **0.32 NS** (negative control) |
| Psychiatry | 99.1% | 100.0% | −0.9 | 1.0e-04 (small reverse) |

### L1 verification (R10)
ProPublica IRS BMF lookup confirmed all 22 HCA institutions are for-profit. Per Tate Esq. authoritative source, **HCA residents are NOT PSLF-eligible regardless of academic-partner branding** (e.g., HCA/USF Morsani GME, HCA Florida JFK Hosp-U Miami).

### P11 final (R12 — REVERSES P8)

City-aggregate matching at 96.2% match rate (vs P8's hospital-name matching at 31.5%):

| Model | PSLF-hostile coefficient | p-value | R² |
|---|---|---|---|
| 1 (PSLF only) | −18.76 pp | < 10⁻⁸⁴ | 0.015 |
| 2 (+ city CMS quality) | −17.90 pp | < 10⁻⁷⁶ | 0.017 |
| 3 (+ state FE) | −19.00 pp | < 10⁻⁷³ | 0.029 |
| 4 (+ specialty FE) | **−18.56 pp** | **< 10⁻⁷⁵** | 0.116 |

City quality coefficient: +1.10 pp/star (small, but significant)
**PSLF effect dominates quality effect by ~4×.**

City-aggregate validation:
- PSLF-friendly cities: 20.2% for-profit hospitals on average
- PSLF-hostile cities: **77.0%** for-profit hospitals (heuristic correctly identified for-profit-chain hosts)

### P7 pre/post Limited Waiver (structural finding)

| Year | n_friendly | n_hostile | Gap (pp) | p |
|---|---|---|---|---|
| 2016 | 2,190 | 6 | −5.92 | 1.78e-41 |
| 2017 | 2,437 | 8 | +1.27 | 0.87 |
| 2018 | 2,231 | 4 | (insufficient) | — |
| 2019 | 2,201 | 4 | (insufficient) | — |
| 2020 | 2,269 | 54 | **+15.63** | 0.002 |
| 2021 | 3,353 | 129 | +14.00 | 6.4e-06 |
| 2022 | 3,451 | 149 | +16.48 | 2.4e-08 |
| 2023 | 3,518 | 159 | +13.18 | 5.7e-07 |
| 2024 | 3,597 | 159 | +10.71 | 4.9e-06 |
| 2025 | 3,677 | 167 | +10.47 | 1.3e-05 |

**Pre-Waiver mean (2016, 2017, 2020): +3.66 pp**
**Post-Waiver mean (2021-2025): +12.97 pp**
**Δ: +9.31 pp** (T-test p=0.28 NS due to small year sample)

Note: For-profit chain residency expansion only reached scale in 2020 (n_hostile jumped 4 → 54).

## H.2 P1: State-level discourse heatmap

**After regex fix** (initially had bogus "in"/"or"/"me" matches):
- Total state-mention rows: 9,397 (after regex fix)

**Top states by volume** (n>=100):
- PA (986), CA (938), VA (716), OR (603), MD (559), TX (458), MO (369), NY (348), FL (308), IN (306), WA (298), OK (280), MA (260), MS (229), ID (215)

**PSLF distress hotspots** (high volume + below-median polarity, median = +0.0925):
- Missouri: +0.05 polarity, 17.1% negative (n=369) — TOP HOTSPOT
- South Carolina: +0.06, 11.3% (n=106)
- Idaho: +0.07, 10.2% (n=215)
- Maine: +0.08, 10.2% (n=108)

**Trump PSLF EO impact 2024 vs 2025:**
- Largest negative: OK (−0.043), PA (−0.017), MD (−0.013), OR (−0.007), CA (−0.004), IN (−0.002)
- Improved: TX (+0.027), MO (+0.020), VA (+0.010)

## H.3 P2: Servicer-specific discourse

**File:** `policy_servicer_results.csv`
**n total mentions:** 106,090 across 8 servicers

| Servicer | n | Mean polarity | Sd | %neg | %pos |
|---|---|---|---|---|---|
| MOHELA | 64,812 | +0.056 | 0.177 | 18.17% | 45.32% |
| FedLoan/PHEAA | 16,327 | +0.071 | 0.164 | 14.48% | 51.50% |
| Nelnet | 8,743 | +0.067 | 0.163 | 14.46% | 50.31% |
| Aidvantage | 5,387 | +0.063 | 0.150 | 14.09% | 49.01% |
| Navient | 4,608 | +0.071 | 0.157 | 13.80% | 52.97% |
| EdFinancial | 2,768 | +0.053 | 0.158 | 15.64% | 46.93% |
| Great Lakes | 2,173 | +0.251 | 0.206 | 1.15% | 90.80% |
| Sallie Mae | 1,272 | +0.064 | 0.150 | 11.95% | 54.87% |

**MOHELA year-over-year decline:**
- 2017: +0.079
- 2018: +0.097
- 2019: +0.074
- 2020: +0.076
- 2021: +0.085
- 2022: +0.073 (MOHELA assumes PSLF in July)
- 2023: +0.063
- **2024: +0.040** (lowest)
- 2025: +0.041

**Pre-takeover vs post-takeover:**
- Pre-2022 (n=784): +0.0794
- Post-2022 (n=64,028): +0.0555
- **Δ: −0.0239**

## H.4 P3: Process-issue prevalence

**File:** `policy_process_issues_results.csv`
**Total mentions:** 142,689

| Process | n | Mean polarity | %concern | %neg |
|---|---|---|---|---|
| Loan_Consolidation | 49,919 | +0.071 | 16.84% | 12.06% |
| Payment_Count_Dispute | 21,134 | +0.068 | 22.60% | 12.96% |
| IDR_Recertification | 19,615 | +0.060 | 18.43% | 13.78% |
| Employment_Certification | 17,284 | +0.067 | 21.15% | 13.78% |
| **PSLF_Buyback** | 16,458 | +0.059 | 18.19% | 15.18% |
| Form_Processing_Delay | 5,717 | +0.049 | **32.88%** | 17.79% |
| IDR_Adjustment | 3,176 | +0.068 | 17.29% | 13.38% |
| Employer_Determination | 2,794 | +0.070 | 24.77% | 11.06% |
| **MOHELA_Specific_Issue** | 2,788 | +0.005 | **96.38%** | 27.87% |
| Limited_Waiver | 1,970 | +0.046 | 21.62% | 15.84% |
| PSLF_Help_Tool | 1,834 | +0.073 | 22.08% | 11.78% |

**PSLF Buyback explosive growth:**
- 2019: 0
- 2020: 2
- 2021: 3
- 2022: 16
- 2023: 464
- 2024: 2,957
- **2025: 10,542**
- 2026 (Q1): 2,473

## H.5 P4: HRSA HPSA × PSLF (state-level)

**File:** `policy_hrsa_hpsa_results.csv`
**HPSA records:** 19,045 designated primary-care HPSAs (after Designated filter from 77,818 raw)
**NRMP-HPSA matched:** 48 states

State HPSA tier (by n_hpsas):
- High (top tertile): PSLF gap = **+12.52 pp** (p=2.3e-25, n=12,301 friendly / 722 hostile)
- Medium (middle tertile): PSLF gap = **+24.26 pp** (p=2.8e-04, n=4,409 friendly / 41 hostile)
- (Low tier had insufficient hostile sample)

**State-level Pearson r (HPSA count vs mean fill rate):** +0.227 (p=0.12 NS, n=48)

## H.6 P5: HRSA HPSA × PSLF (county-level — superseded P4)

**File:** `policy_p5_county_hrsa_results.csv`
**Counties matched:** 25,795 NRMP rows of 30,763 (96.2% match via SimpleMaps city → county)

| HPSA-severity tier | n_friendly | n_hostile | Friendly fill | Hostile fill | Gap (pp) | p |
|---|---|---|---|---|---|---|
| Low (urban, well-served) | 4,491 | 192 | 0.9193 | 0.6576 | **+26.17** | 1.3e-18 |
| Medium | 4,216 | 265 | 0.9496 | 0.7924 | +15.72 | 6.6e-14 |
| High (rural, underserved) | 5,626 | 56 | 0.9475 | 0.8244 | +12.31 | 0.002 |

**The PSLF eligibility gap is LARGEST in LOW-shortage (urban) counties** — counter to PSLF's stated workforce-targeting goal.

## H.7 P6: CFPB vs discourse topic comparison

**File:** `policy_p6_cfpb_comparison_results.csv`
**CFPB total:** 12,552; **Discourse total (P3):** 142,689

| Process | CFPB n | CFPB share | Discourse n | Discourse share | Ratio |
|---|---|---|---|---|---|
| **PSLF_Buyback** | 207 | 2.1% | 16,458 | 11.5% | **5.47×** |
| **PSLF_Help_Tool** | 35 | 0.4% | 1,834 | 1.3% | **3.61×** |
| **Employment_Certification** | 493 | 5.0% | 17,284 | 12.1% | **2.41×** |
| Loan_Consolidation | 2,543 | 25.9% | 49,919 | 35.0% | 1.35× |
| Limited_Waiver | 129 | 1.3% | 1,970 | 1.4% | 1.05× |
| Payment_Count_Dispute | 1,990 | 20.3% | 21,134 | 14.8% | 0.73× |
| Employer_Determination | 340 | 3.5% | 2,794 | 2.0% | 0.57× |
| Form_Processing_Delay | 779 | 7.9% | 5,717 | 4.0% | 0.50× |
| IDR_Recertification | 2,871 | 29.2% | 19,615 | 13.7% | **0.47×** |
| MOHELA_Specific_Issue | 431 | 4.4% | 2,788 | 2.0% | **0.45×** |

## H.8 P7: Pre/post Limited Waiver

(See H.1 for B5 finding context with pre/post table.)

## H.9 P8: CMS quality cross-check (R11 — SUPERSEDED by P11)

**Match rate:** 31.5% (251 of 797 institutions)
**Concordance with heuristic:** 45% (113 of 251)

| Stars | n_e | n_i | E_mean | I_mean | Gap (pp) | p |
|---|---|---|---|---|---|---|
| 1.0 | 870 | 123 | 0.9153 | 0.9923 | **−7.69** | 5.1e-18 |
| 2.0 | 1,478 | 475 | 0.9005 | 0.9040 | −0.35 | 0.79 |
| 3.0 | 2,353 | 921 | 0.9306 | 0.9454 | −1.48 | 0.05 |
| 4.0 | 1,365 | 59 | 0.9417 | 0.9137 | +2.80 | 0.29 |
| 5.0 | 1,103 | 5 | 0.9650 | 1.0000 | −3.50 | 2.6e-13 |

**OLS coefficient:** PSLF_eligible = −0.0158 (NS, p=0.09); Star = +0.013 per star (p<10⁻⁶)

**P8 conclusion (now reversed):** PSLF gap appeared quality-confounded.

## H.10 P9: Within-institution pre/post

**File:** `policy_p9_within_institution_results.csv`
**Institutions in BOTH pre (2016-2020) AND post (2022-2025) eras:** 468 (453 with computable means)

Within-institution Δ fill rate by class:
- pslf_friendly: n=224, mean Δ=−0.93pp, median=−0.27pp, sd=10.94pp
- ambiguous: n=222, mean Δ=−0.56pp, median=0.00pp, sd=13.48pp
- pslf_hostile: n=7, mean Δ=−8.97pp

**DiD (friendly vs hostile):** +8.04 pp (t=+1.94, p=0.098 marginally NS)

## H.11 P10: CFPB by company timeline

**File:** `policy_p10_cfpb_company_results.csv`
**Total complaints:** 12,552 across 11+ companies

**MOHELA CFPB share trajectory:**
- 2016: 1.76% (n=6)
- 2017: 1.22% (n=17)
- 2018: 1.04% (n=11)
- 2019: 0.10% (n=1)
- 2020: 0.20% (n=1)
- 2021: 0.39% (n=2)
- 2022: **18.31%** (n=234) — MOHELA assumes PSLF July 2022
- 2023: **63.13%** (n=1,190)
- 2024: **62.81%** (n=1,329)
- 2025: **56.28%** (n=1,251)
- 2026 (Q1): 52.19% (n=119)

**FedLoan/AES/PHEAA share (predecessor PSLF servicer):**
- 2021: 64.4% (peak)
- 2022: 35.2%
- 2023: 1.6% (after PSLF transition)
- 2024-2026: <1%

**Top MOHELA issue types:**
- "Dealing with your lender or servicer": 3,464 (83% of MOHELA complaints)
- "Struggling to repay your loan": 607
- "Incorrect information on your report": 50

## H.12 P12: NHSC vs PSLF comparative analysis

**NHSC field strength growth:**
- 2019: 13,306
- 2022: 20,697 (peak)
- 2025: 18,846

**NHSC vs HPSA correlation (state-level):**
- Pearson r(HPSA count, NHSC total) = **+0.789** (p=3.2e-13, n=57)
- Spearman ρ = +0.797 (p=1.2e-13)

**Top efficient NHSC targeting (per HPSA):**
1. RI: 13.8 NHSC per HPSA
2. DC: 13.2
3. CT: 11.0
4. MP: 10.5
5. MD: 8.6
6. VT: 6.0
7. NY: 6.0
8. DE: 5.2
9. MA: 4.7
10. HI: 3.7

**NHSC PC vs NRMP PC fill (state-level):** r=+0.063 NS — NHSC presence does NOT predict NRMP PC fill rates.

**PSLF gap by NHSC tier (primary care only):**
- Low NHSC: PSLF gap = **+33.81 pp** (p=1e-08)
- Medium NHSC: PSLF gap = +6.91 pp (p=0.023)
- High NHSC: PSLF gap = **+37.44 pp** (p=4.5e-20)

## H.13 L1: NRMP institutions verified via ProPublica IRS BMF

**File:** `nrmp_institution_pslf_verified.csv`
**Result distribution:**
- pslf_eligible_501c3: 431
- no_propublica_match: 331
- pslf_ineligible_for_profit: 22
- pslf_unclear_other_subsec: 8
- pslf_eligible_gov: 5

**Original heuristic vs CMS-verified concordance:**
| Heuristic | ambiguous | pslf_eligible | pslf_ineligible | Total |
|---|---|---|---|---|
| ambiguous | 0 | 102 | 15 | 117 |
| pslf_friendly | 3 | 113 | 17 | 133 |
| pslf_hostile | 0 | 1 | 0 | 1 |
| Total | 3 | 216 | 32 | 251 |

## H.14 L2: Discourse → NRMP fill rates

**Specialty-year cells:** 35 with n_sdn>=10
**Tests:**
- Contemporaneous Pearson r = +0.029 (p=0.87, n=35)
- Lagged (year-1 sentiment → year fill) r = −0.313 (p=0.11, n=27)
- Δ-Δ first-difference r = −0.075 (p=0.73, n=24)

**All NULL** — discourse does NOT predict NRMP fill rate (parallel signals).

## H.15 L3: Servicer-issues topic prevalence vs FSA events

**Months with n>=20:** 51

Operational events (servicer_issues prevalence pre/post):
- Payments Restart 60d: pre=21.9%, post=24.6%, Δ=+2.66pp (NaN p)
- Payments Restart 90d: +6.28pp, p=0.45
- MOHELA Transition 90d: +6.10pp, p=0.14
- SAVE Forbearance 90d: −8.48pp, p=0.24
- PSLF Form Online 90d: +0.76pp, p=0.94

Policy events (controls):
- Limited Waiver 60d: +10.00pp, p=0.11
- Biden Mass Forgive 60d: +10.82pp, p=0.40
- Biden v Nebraska 90d: +0.31pp, p=0.96
- Trump PSLF EO 90d: −6.31pp, p=0.32

**All NULL at p<0.05.** Power-limited at monthly aggregation.

## H.16 L4: SDN attending pattern at comments scale

**Reddit comments analyzed:** 413,756 (after wc>=5)
**Medical-subreddit comments:** 8,778

| Career stage | n (medical subs) | Mean polarity | %neg |
|---|---|---|---|
| Resident | 389 | +0.105 | 9.3% |
| Attending | 158 | +0.091 | 11.4% |
| Fellow | 179 | +0.124 | 7.8% |
| Medical student | 159 | +0.083 | 12.6% |

**Attending vs Resident pairwise:** d=−0.082, p=0.35 NS

**Comments cannot test stance-decoupling (no Claude on comments).** A3 finding cannot be replicated at this scale without Claude scoring (~$2,300 estimated).

## H.17 L5: Cohort robustness

(See Section F.8 above — listed in Methods findings since it's the primary methods finding.)

## H.18 B1: FSA admin data NULL correlation

**File:** `fsa_pslf_discourse_correlation.csv`
**4 specifications tested:** All NULL (r=−0.20 to +0.04, all p>0.49).

Caveats noted:
- Stock-vs-flow mismatch (cumulative approvals is monotonically increasing; discourse polarity is stationary)
- Hand-curated milestone fallback (n is small)
- Should test FLOW (monthly NEW approvals), not stock — methodology limitation

---

# SECTION I: ALL RESULT ARTIFACTS (CSV + TXT)

## I.1 Master tables

- `legislative_timeline_results.{txt,csv}` — canonical 8-event pre/post table with all metrics (R5)
- `triangulation_results.{txt,csv}` — three-rater K-α + per-event tests (R7)
- `triangulation_comments_results.{txt,csv}` — comments-scale TB×VADER α
- `paper_numbers_table.csv` — master numbers for paper drafts
- `intention_results.{txt,csv}` — Claude pslf_stance analysis (R7)

## I.2 Methods analyses

- `op_vs_reply_results.{txt,csv}` — OP vs Reply construct mismatch
- `op_reply_per_event_results.{txt,csv}` — OP vs Reply per-event
- `spec_curve_results.{txt,csv}` — A2 specification curve (360 specs)
- `spec_curve_decomposition.{txt,csv}` — A2 decomposition by spec dimension
- `a3_firth_corrected_results.{txt,csv}` — A3 Firth/HA corrected ORs
- `l5_cohort_robustness_results.{txt,csv}` — L5 cohort-conditional robustness

## I.3 Substantive analyses

- `mediation_career_stage_results.{txt,csv}` — A3 career-stage mediation
- `decoupling_by_cohort.csv` — Per-cohort decoupling OR table
- `per_profession_breakdowns.txt` — Per-profession decoupling
- `per_profession_per_event_results.{txt,csv}` — Per-event × per-profession
- `topic_per_cohort_per_event_results.{txt,csv}` — Topic shifts per cohort × event
- `cohort_heterogeneity_comments_results_*.csv` (5 files: intensity, events, direction, depth, recovery)
- `comment_cohort_heterogeneity_results.csv` — Comment-level cohort heterogeneity
- `per_author_with_comments_results.csv` — Per-author longitudinal panel
- `time_to_recovery_results.{txt,csv}` — Time-to-recovery per cohort
- `c1_threshold_sensitivity.{txt,csv}` — C1 time-to-recovery threshold sensitivity
- `floor_effect_investigation.txt` — R7 floor-effect investigation

## I.4 Linking analyses

- `l2_discourse_nrmp_results.{txt,csv}` — L2 discourse → NRMP
- `l3_topic_fsa_results.{txt,csv}` — L3 topic-FSA responsiveness
- `l4_sdn_attending_comments_results.{txt,csv}` — L4 SDN attending in comments

## I.5 Policy artifacts (P1-P12 + B5)

- `nrmp_pslf_program_results.{txt,csv}` — B5 base
- `policy_state_discourse.{txt,csv}` (P1)
- `policy_servicer_results.{txt,csv}` (P2)
- `policy_process_issues_results.{txt,csv}` (P3)
- `policy_hrsa_hpsa_results.{txt,csv}` + `_gap.csv` (P4)
- `policy_p5_county_hrsa_results.{txt,csv}` + `_counties.csv` (P5)
- `policy_p6_cfpb_comparison_results.{txt,csv}` (P6)
- `policy_p7_pre_post_waiver_results.{txt,csv}` + `_by_specialty.csv` (P7)
- `policy_p8_cms_quality_results.{txt,csv}` (P8 — superseded)
- `policy_p9_within_institution_results.{txt,csv}` + `_by_specialty.csv` + `_per_institution.csv` (P9)
- `policy_p10_cfpb_company_results.{txt,csv}` + `_company_year_table.csv` (P10)
- `policy_p11_improved_cms_matching.{txt,csv}` (P11 — supersedes P8)
- `policy_p12_nhsc_vs_pslf_results.{txt,csv}` (P12)

## I.6 Other artifacts

- `confound_audit_results.txt` — Platform×profession, length×polarity tests
- `critical_fixes_results.txt` — R7 critical fixes implementation log
- `final_summary_report.txt` — R5 statistical summary report
- `sensitivity_results.txt` — Sensitivity analyses
- `placebo_results.txt` (`.csv`) — Placebo test against topical-near baseline
- `topic_model_results.{txt,csv,bertopic.txt,bertopic.csv}` — BERTopic full corpus
- `topic_model_topics.csv` + `_bertopic.csv` — Topic descriptions
- `topic_model_crosstab.csv` + `_bertopic.csv` — Topic crosstabs
- `rejection_reason_analysis_results.{txt,csv}` — PSLF rejection reasons coding
- `rejection_reasons.csv` — Coded rejection reasons
- `volume_artifact_arctic_shift.{txt,csv}` — R/C ratio against Arctic Shift baseline
- `nrmp_program_extraction_log.txt` — Parser diagnostics
- `nrmp_institution_city_lookup.csv` — City extraction (R10)
- `sdn_subthread_consistency.{txt,csv}` — SDN subthread consistency check
- `admin_correlation_results.txt` — Original CFPB cross-correlation analysis
- `admin_data_pslf_complaints.csv` (CFPB extract)
- `reddit_cfpb_volume_ratio.csv` — R/C ratio per year

---

# SECTION J: ALL FIGURES (47 PNGs at 300 DPI)

## J.1 Methods Paper figures (5)

1. **`fig_methods_1_op_vs_reply_cohort.png`** (416 KB) — OP vs Reply construct mismatch, 8/8 cohort consistent
2. **`fig_methods_2_trump_eo_joint.png`** (288 KB) — Trump PSLF EO directional disagreement
3. **`fig_methods_3_alpha_stability.png`** (331 KB) — Krippendorff α stability across sample sizes
4. **`fig_methods_4_per_event_cohort_forest.png`** (912 KB) — Per-event × cohort forest
5. **`triangulation_figure7.png`** (522 KB) — Three-rater triangulation forest

## J.2 Substantive Paper figures (5)

1. **`fig_substantive_1_decoupling_forest.png`** (313 KB) — Cohort heterogeneity OR forest
2. **`fig_substantive_2_recovery_times.png`** (496 KB) — Time-to-recovery per cohort
3. **`fig_substantive_3_rejection_reasons.png`** (709 KB) — PSLF rejection reasons
4. **`fig_substantive_4_topic_3d_heatmap.png`** (483 KB) — Topic restructuring 3D heatmap
5. **`fig_substantive_5_sdn_nrmp_alignment.png`** (956 KB) — SDN-NRMP timeline alignment

## J.3 Policy Paper figures (12)

1. **`policy_p11_improved_cms_matching.png`** (146 KB) — Coefficient stability across nested models (THE money chart)
2. **`policy_p12_nhsc_vs_pslf_results.png`** (190 KB) — NHSC × PSLF comparison
3. **`policy_p10_cfpb_company_results.png`** (329 KB) — MOHELA CFPB share jump
4. **`policy_p9_within_institution_results.png`** (85 KB) — Within-institution DiD
5. **`policy_p8_cms_quality_results.png`** (120 KB) — CMS quality (P8 — superseded)
6. **`policy_p7_pre_post_waiver_results.png`** (187 KB) — Pre/post Limited Waiver
7. **`policy_p6_cfpb_comparison_results.png`** (119 KB) — Discourse vs CFPB topic comparison
8. **`policy_p5_county_hrsa_results.png`** (165 KB) — County-level HPSA × PSLF
9. **`policy_state_discourse.png`** (157 KB) — State-level distress hotspots (P1)
10. **`policy_servicer_results.png`** (506 KB) — MOHELA discourse trajectory (P2)
11. **`policy_process_issues_results.png`** (208 KB) — Process-issue priority ranking (P3)
12. **`nrmp_pslf_program_figure.png`** (172 KB) — B5 baseline gap by specialty

## J.4 Substantive intention/stance figures (6)

13. **`intention_event_forest.png`** (355 KB)
14. **`intention_profession_event_heatmap.png`** (348 KB)
15. **`intention_topic_event_shifts.png`** (532 KB)
16. **`intention_topic_profession_event_heatmap.png`** (406 KB)
17. **`intention_trajectory.png`** (711 KB)
18. **`intention_within_vs_between_decomposition.png`** (170 KB)

## J.5 Project overview / methods support (10)

19. **`pslf_master_timeline.png`** (1.2 MB) — Master timeline
20. **`pslf_master_timeline_3scorer.png`** (2.0 MB) — Master timeline 3-scorer
21. **`pslf_event_timecourses.png`** (2.0 MB) — Event timecourses (per-event)
22. **`pslf_event_timecourses_combined.png`** (2.1 MB) — Combined event timecourses
23. **`pslf_event_timecourses_vader.png`** (2.0 MB) — VADER-specific event timecourses
24. **`pslf_pre_post_events.png`** (2.0 MB) — 8 violin plots + forest of effect sizes
25. **`pslf_profession_timecourse.png`** (1.8 MB) — Quarterly polarity by profession (13 lines)
26. **`pslf_sentiment_legislative_timeline.png`** (2.2 MB) — 21-event timeline (3 panels)
27. **`pslf_volume_artifact.png`** (504 KB) — R/C ratio diagnostic
28. **`volume_artifact_arctic_shift.png`** (499 KB) — Arctic Shift R/C diagnostic

## J.6 Cross-paper figures (5)

29. **`multi_source_sentiment_comparison.png`** (1.6 MB) — Reddit vs SDN multi-panel
30. **`pslf_wordcloud_timecourse.png`** (7.5 MB) — 8 word clouds (4 eras × 2 platforms)
31. **`spec_curve_results.png`** (347 KB) — A2 specification curve (360 specs)
32. **`pslf_claude_dimensions.png`** (1.2 MB) — Claude 3-dim multi-panel
33. **`pslf_claude_dimensions_by_event.png`** (1.7 MB) — Claude 3-dim by event

## J.7 Linking & sub-analyses (4)

34. **`l2_discourse_nrmp_figure.png`** (219 KB) — L2 discourse → NRMP (NULL)
35. **`l3_topic_fsa_figure.png`** (235 KB) — L3 topic-FSA (NULL)
36. **`admin_sentiment_correlation.png`** (1.2 MB) — Original CFPB cross-correlation function
37. **`cohort_heterogeneity_comments_figure.png`** (319 KB) — Comments-scale cohort heterogeneity (C1)

---

# SECTION K: STATISTICAL METHODOLOGY (DETAILED)

## K.1 Inter-rater reliability

**Krippendorff α** (`sentiment_triangulation.py`):
- Library: `krippendorff` Python package (point estimate)
- 95% CI: hand-coded stratified bootstrap (B=2,000), stratification by source — Hayes & Krippendorff 2007
- Two reported:
  - **Canonical**: fixed thresholds (TextBlob/VADER cuts at [−0.5, −0.05, +0.05, +0.5])
  - **Charitable upper bound**: percentile-matched ordinal (forces equal-frequency quintiles)

## K.2 Effect sizes

**Hedges' g** with **J² small-sample correction** (Borenstein et al. 2009 eq. 4.24):
- J = 1 − 3/(4(n) − 9)
- g = d × J
- NOT Hedges & Olkin (1985) eq. 6.13 (large-sample approximation that omits J²)

**Glass's Δ_pre** alongside (uses pre-period SD as reference)

## K.3 Permutation/bootstrap tests

**Block permutation** (`gen_legislative_timeline.py`):
- Bickel et al. (1989) WITHOUT replacement (R7 fix; was wrong-null moving-block-with-replacement)
- Block size: 14 days (autocorrelation length scale on PSLF discourse)
- B=2,000, per-event seed (R5 fix)
- B_actual tracking (R5 fix; was deflating p-values when zero-variance surrogates were skipped)

**Cluster bootstrap** (for OP vs Reply):
- Cluster by post_id
- B=2,000

## K.4 Multiple comparisons correction

**Holm-Bonferroni step-down** (R7 should-fix #7):
- Family α = 0.05 across the 8 events
- Replaces uniform Bonferroni α/8 = 0.00625

## K.5 OLS specifications

- **HC3 robust SEs** (White heteroskedasticity-consistent) — R7 should-fix #8
- **Length residualization**: outcome = polarity − OLS predicted from log(word_count) + source + profession dummies (R4 fix)
- **Collinearity check**: QR-rank check to drop perfectly-collinear src/profession dummies (R5 fix)

## K.6 Hotelling T² (joint multivariate test)

For Trump EO joint shift across 3 instruments:
- F = 30.95, p = 1.11×10⁻¹⁶ (n=1,330)
- Three-instrument joint shift decisively non-zero with directionally split components

## K.7 Test-retest reliability for Claude (R7 fix #5)

- Re-score n=200 SDN posts at temperature=0
- Compute test-retest Krippendorff α
- Threshold: α > 0.85 = LLM-noise objection refuted
- Achieved: α = +0.958 (95% CI [+0.938, +0.975]), exact-match 95.2%

## K.8 BH FDR (alternative for some tests)

For per-event topic shift chi-sq tests:
- Benjamini-Hochberg FDR α=0.05 across 8 events × 7 topics

## K.9 Firth penalized logistic regression / Haldane-Anscombe

For sparse 2×2 cells (A3 SDN-attending OR=0.02):
- `firthlogist` library failed to install for Python 3.11+
- Used Haldane-Anscombe correction: add 0.5 to each cell
- Result: HA OR=0.024 vs naive 0.016 — only 50% bias, same order of magnitude
- d=1 cell drives the magnitude but doesn't drive the direction

## K.10 Specification curve (Steegen et al. 2016)

A2 implementation: 360 specifications across:
- 3 negative definitions × 3 pursuing definitions × 2 exclude_arctic × 2 exclude_sdn × 4 min_cell_n × 5 cohorts

## K.11 Per-cohort odds ratio (sentiment-stance decoupling)

For each cohort:
- a = (negative AND pursuing/considering)
- b = (negative AND NOT pursuing)
- c = (NOT negative AND pursuing/considering)
- d = (NOT negative AND NOT pursuing)
- OR = (a×d) / (b×c)
- log_OR ± 1.96×SE for 95% CI

---

# SECTION L: SOFTWARE STACK & DEPENDENCIES

## L.1 Core stack

- **Python 3.11.x** (Anaconda at `C:\Users\zanen\anaconda3\`)
- **Operating system**: Windows 10/11

## L.2 Data manipulation

- pandas 2.x
- numpy 1.26.x
- scipy 1.13+ (`scipy.stats`)

## L.3 Statistics

- statsmodels 0.14+ (OLS, FE models, HC3 SEs)
- scikit-learn 1.5+ (classification, regression baselines)
- krippendorff 0.5+ (Krippendorff α)

## L.4 Sentiment analysis

- TextBlob 0.18.0+
- vaderSentiment 3.3.2+ (VADER)
- anthropic 0.40+ (Claude API)
- together 2.12+ (Together AI for open-weight LLMs)
- openai 1.x+ (OpenAI GPT-4o alternative)

## L.5 Web scraping

- requests
- beautifulsoup4
- playwright 1.x (headless Chromium)
- google-api-python-client (YouTube collector)

## L.6 PDF processing

- pdfplumber 0.11.9+ (NRMP PDFs)
- xlrd, openpyxl (NHSC Excel files)

## L.7 NLP

- NLTK 3.x (English stopwords, WordNet lemmatizer)
- BERTopic (full-corpus topic modeling)
- TfidfVectorizer (sklearn)

## L.8 Visualization

- matplotlib 3.8+
- wordcloud 1.x

## L.9 Optional / failed installs

- firthlogist (requires Python 3.8-3.10; not available for 3.11+)
  - Workaround: Haldane-Anscombe correction implemented manually

## L.10 Hardware

- Local laptop computation only
- No GPU required (LLM scoring via cloud APIs)
- Anthropic API: ~$50 spent on Claude scoring across all subsamples
- Together AI: ~$0.29 estimated for open-weight replication (pending user run)

---

# SECTION M: REPRODUCIBILITY

## M.1 Code repository

- **Working directory**: `C:\Users\zanen\PSLF_2026\`
- **GitHub fork**: https://github.com/zanecn/PSLF-Discussion-Analysis
- **GitHub upstream**: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis
- **Branch**: `playwright-sdn-scraper`

## M.2 OSF deposit (planned)

Per `OSF_TRANSPARENCY_PACKAGE.md`:
- Aggregated three-rater results (n=9,242 with sentiment_int per scorer) — CC0
- Cohort heterogeneity OR table (per L5) — CC0
- All `*_results.csv` files — CC0
- All figures (PNG) — CC0
- Raw post text NOT redistributed (per Reddit ToS)
- NRMP per-program data NOT redistributed (per NRMP usage agreement)

## M.3 Pre-registration (genuine, for cross-domain replication)

Per `OSF_PREREGISTRATION_cross_domain.md`:
- COVID-19 vaccine discourse replication
- Pre-specified hypotheses, design, analysis plan, stop rules
- Status: not yet executed; pre-registration constitutes commitment

---

# SECTION N: KEY DOCUMENTATION FILES

## N.1 Audit documents
- `AUDIT_round10_findings.md` — initial round-10 audit
- `AUDIT_round10_LINKING_RESULTS.md` — L1-L5 linking results
- `AUDIT_round11_P8_CMS_correction.md` — superseded
- `AUDIT_round12_P11_REVERSAL.md` — current (B5 stands at +18.56pp)

## N.2 Policy briefs
- `POLICY_BRIEF_round10.md` — initial 7 findings
- `POLICY_BRIEF_v2_full.md` — incorporates P5, P6, P7
- `POLICY_BRIEF_v3_FINAL.md` — initial v3
- `POLICY_BRIEF_v4_DEFINITIVE.md` — final (incorporates P11 reversal + P12)

## N.3 Publication strategy
- `PUBLICATION_SYNTHESIS_aggregate_view.md` — full publication synthesis with literature positioning
- `CONSOLIDATED_MAIN_STORY.md` — one-page consolidated story

## N.4 OSF / pre-registration
- `OSF_TRANSPARENCY_PACKAGE.md` — for the OSF deposit (post-hoc transparency)
- `OSF_PREREGISTRATION_cross_domain.md` — for genuine cross-domain pre-registration

## N.5 Data acquisition instructions
- `NRMP_program_level_data_instructions.md` — NRMP usage compliance + workflow
- `AAMC_GQ_data_request_instructions.md` — AAMC GQ DUA process
- `NSLDS_DUA_application_instructions.md` — NSLDS DUA process

## N.6 Cross-domain replication
- `cross_domain_replication_design.md` — COVID-vaccine replication design

## N.7 User actions
- `USER_ACTION_open_weight_LLM.md` — open-weight LLM replication setup + run

---

# SECTION O: HEADLINE STATISTICS QUICK-REFERENCE TABLE

| Metric | Value | Source |
|---|---|---|
| Total PSLF-strict-filtered Reddit posts | 76,074 | Arctic Shift R8 |
| Total SDN PSLF posts | 4,749 | SDN Playwright scrape |
| Total Reddit comments | 460,000 | PRAW collector |
| Claude-scored posts (3-rater intersection) | **9,242** | All zeroshot subsamples |
| Test-retest α at temperature=0 | **+0.958** | n=605 SDN posts |
| Three-rater K-α (canonical) | **−0.018** | n=9,242 |
| Three-rater K-α (charitable) | **+0.196** | n=9,242 |
| TB×VADER comments α | +0.298 | n=460,000 |
| Reddit r/PSLF decoupling OR | **7.33** | n=1,469 |
| SDN-Medical decoupling OR | **0.27** | n=1,960 |
| Reddit Finance decoupling OR | **0.18** | n=999 |
| OP vs Reply TB Δ | −0.017 | cluster bootstrap |
| OP vs Reply VADER Δ | +0.220 | cluster bootstrap |
| Trump EO TB g | −0.32 | n=1,330 |
| Trump EO VADER g | +0.16 | n=1,330 |
| Trump EO Claude g | +0.33 | n=1,330 |
| PSLF recruitment gap (B5 raw) | +12.86 pp | n=789 institutions |
| PSLF recruitment gap (P11 with controls) | **−18.56 pp** | n=29,461 program-years |
| MOHELA CFPB share 2017 | 1.22% | CFPB |
| MOHELA CFPB share 2023 | **63.13%** | CFPB |
| PSLF Buyback discourse 2021 | 3 | P3 |
| PSLF Buyback discourse 2025 | **10,542** | P3 |
| NHSC HPSA correlation | r=+0.789 | P12, n=57 states |

---

*This document is the comprehensive reference for the PSLF Project at Round 12. For executive summary, see `CONSOLIDATED_MAIN_STORY.md`. For publication strategy, see `PUBLICATION_SYNTHESIS_aggregate_view.md`. For paper drafts, see Notion paper child pages.*