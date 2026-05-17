# Scripts README — Script-to-Output Mapping

**107 Python + 1 PowerShell scripts.** This file maps each script to its purpose, inputs, and outputs so a new collaborator can navigate quickly.

## Quick-reference: which script produces which output?

| Output file | Producing script |
|---|---|
| **Paper 1 (EPJ DS)** |
| `paper1_multi_llm_with_sdn_results.txt` | `compare_multi_llm_with_sdn.py` |
| `paper1_paraphrase_robustness_results.txt` | `compute_paraphrase_robustness.py` |
| `paper1_dual_binning_results.{txt,csv}` | `p1_dual_binning_with_bootstrap.py` |
| `paper1_cohort_stratified_bootstrap_results.txt` | `run_cohort_stratified_bootstrap_p1.py` |
| `paper1_op_vs_reply_cluster_bootstrap_results.txt` | `run_op_vs_reply_cluster_bootstrap.py` |
| `paper1_fig{1,2,3}*.png` | `generate_p1_figures.py` |
| `test_retest_FINAL_results.txt` | `compare_test_retest.py` |
| `op_vs_reply_results.{txt,csv}` | `analyze_op_vs_reply.py` |
| `op_reply_per_event_results.{txt,csv}` | `analyze_op_reply_per_event.py` |
| `triangulation_results.{txt,csv}` | `sentiment_triangulation.py` |
| `triangulation_comments_results.{txt,csv}` | `triangulation_with_comments.py` |
| `multi_llm_comparison_results.{txt,csv,png}` | `compare_multi_llm_vs_claude.py` (Reddit-only, n=701; superseded by `compare_multi_llm_with_sdn.py`) |
| `openweight_vs_claude_results.txt` | `compare_openweight_vs_claude.py` |
| **Paper 2 (JCSS)** |
| `paper2_holm_bonferroni_p2_chi_sq_results.txt` | `run_holm_bonferroni_p2_chi_sq.py` |
| `paper2_optional_audits_results.txt` | `run_p2_optional_audits.py` (pooled-event + BCa + cluster SE) |
| `paper2_base_rate_adjusted_decoupling.csv` | `base_rate_adjusted_decoupling.py` |
| `paper2_fig{1,2}*.png` | `generate_p2_figures.py` |
| `decoupling_by_cohort.csv` | `analyze_multi_source.py` |
| `l5_cohort_robustness_results.{txt,csv}` | `analyze_l5_cohort_robustness.py` |
| `intention_results.{txt,csv}` + `intention_*.png` | `pslf_intention_analysis.py` |
| `topic_per_cohort_per_event_results.{txt,csv}` | `analyze_topic_per_cohort_per_event.py` |
| `per_author_with_comments_results.{txt,csv}` | `analyze_per_author_with_comments.py` |
| `cohort_heterogeneity_comments_results*.{txt,csv,png}` | `analyze_cohort_heterogeneity_comments.py` |
| **Paper 3 (JGME)** |
| `paper3_model5_FINAL_results.txt` | `run_model5_FINAL.py` (5-yr baseline; CANONICAL) |
| `paper3_model5_2021_2026_cross_sectional_results.txt` | `run_model5_2021_2026_cross_sectional.py` (6-yr) |
| `paper3_model5_with_NIH_results.txt` | `integrate_nih_into_model5.py` (state-NIH integrated) |
| `paper3_model5_with_2026_results.txt` | `run_model5_with_2026_post_eo.py` (descriptive 6-yr; **R17 retraction banner**) |
| `paper3_model5_pre_post_eo_results.txt` | `run_model5_pre_post_eo_split.py` (descriptive split; **R17 retraction banner**) |
| `paper3_wild_cluster_bootstrap_results.txt` | `wild_cluster_bootstrap_p3.py` (Webb 6-point, B=2,000) |
| `paper3_trend_regression_results.txt` | `run_trend_regression_p3.py` (is_2026 + is_post_eo sensitivity) |
| `paper3_negative_control_2021_2026_results.txt` | `run_negative_control_with_2026.py` (orthopedic surgery) |
| `paper3_negative_control_dermatology_results.txt` | `run_dermatology_negative_control.py` (R17++ Agent 2 M5) |
| `paper3_two_part_nih_results.txt` | `run_two_part_nih_p3.py` (R17++ Agent 2 M2) |
| `paper3_fig{1,2}*.png` | `generate_p3_figures.py` |
| `paper3_model5_results.txt` ⚠️ | `run_model5_with_confounders.py` (legacy; superseded by `run_model5_FINAL.py`) |
| **Master / shared** |
| `MASTER_LOCKED_NUMBERS.md` | hand-maintained from above result files |
| `MASTER_REFERENCE_LIST.md` | hand-maintained; R17++ corrected |

## Script categories

### Data collection (in collection-time order)
- `collect_reddit_arctic_shift.py` — R8 Arctic Shift PSLF pull (72K posts)
- `collect_reddit_professions.py` — original Reddit JSON-API collector
- `collect_forum_data.py` — SDN Playwright scraper
- `collect_reddit_comments_no_auth.py` — comments collector (COMPLETE: 528,051 collected)
- `collect_nrmp_program_level.py` — NRMP PDF parser
- `extract_nrmp_backfill_2016_2020.py` — pre-2020 NRMP backfill
- `extract_nrmp_cities.py` — city resolution
- `monitor_and_extract_nrmp_2026.py` — 2026 cycle monitor
- `pull_nih_reporter.py` — NIH RePORTER state-filtered pull
- `build_institutional_confounders.py` — institution-level confounder build

### Sentiment scoring
- `sentiment_zeroshot.py` — Claude Sonnet 4 at temp=0 (CANONICAL)
- `sentiment_zeroshot_paraphrase.py` — 3-prompt paraphrase test-retest
- `sentiment_zeroshot_openweight.py` — Together AI (Llama + DeepSeek)
- `score_vader_arctic_shift.py` — VADER on Arctic Shift posts
- `compute_vader_on_comments.py` — VADER on 528K comments
- `select_arctic_shift_for_claude.py` — Claude scoring sample selection

### Paper 1 analyses (Methods)
- `compare_multi_llm_with_sdn.py` — 5-instrument intersection n=1,001 (CANONICAL)
- `compare_multi_llm_vs_claude.py` — Reddit-only n=701 (predecessor; superseded)
- `compare_openweight_vs_claude.py` — open-weight LLM cross-check
- `compute_paraphrase_robustness.py` — 3-prompt paraphrase α (sentiment/stance/topic)
- `compare_test_retest.py` — temp=0 vs temp=0 determinism check
- `sentiment_triangulation.py` — 3-rater K-α (predecessor framework)
- `triangulation_with_comments.py` — comments-scale TB×VADER α
- `analyze_op_vs_reply.py` — per-post Δ t-test
- `analyze_op_reply_per_event.py` — per-event OP-vs-Reply
- `run_cohort_stratified_bootstrap_p1.py` — R17++ Agent 1 C4
- `run_op_vs_reply_cluster_bootstrap.py` — R17++ Agent 1 C1 (real CIs)
- `p1_dual_binning_with_bootstrap.py` — FIXED vs QCUT binning sensitivity
- `generate_p1_figures.py` — Figures 1+2+3

### Paper 2 analyses (Substantive)
- `analyze_multi_source.py` — main cohort heterogeneity OR table
- `analyze_l5_cohort_robustness.py` — 5-spec cross-instrument robustness
- `pslf_intention_analysis.py` — Claude pslf_stance analysis
- `base_rate_adjusted_decoupling.py` — lift_pp computation
- `analyze_per_profession_breakdowns.py` — per-profession decoupling
- `analyze_per_profession_per_event.py` — per-event × per-profession
- `analyze_topic_per_cohort_per_event.py` — topic shifts
- `analyze_per_author_with_comments.py` — per-author longitudinal panel
- `analyze_cohort_heterogeneity_comments.py` — comments-scale (Supplement S5)
- `analyze_comment_cohort_heterogeneity.py` — comment-level
- `run_holm_bonferroni_p2_chi_sq.py` — R17++ Agent 5 M5
- `run_p2_optional_audits.py` — R17++ Agent 5 M1+M4+M6 (pooled + BCa + cluster SE)
- `generate_p2_figures.py` — Figures 1+2

### Paper 3 analyses (Policy)
- `run_model5_FINAL.py` — 5-year baseline (CANONICAL n=29,349)
- `run_model5_2021_2026_cross_sectional.py` — 6-year sample
- `run_model5_with_2026_post_eo.py` — 2026 post-EO descriptive (with retraction banner)
- `run_model5_pre_post_eo_split.py` — pre/post EO descriptive split (with retraction banner)
- `run_model5_with_confounders.py` — legacy generic baseline (superseded)
- `wild_cluster_bootstrap_p3.py` — Webb 6-point bootstrap
- `run_trend_regression_p3.py` — is_2026 + is_post_eo sensitivity
- `integrate_nih_into_model5.py` — state-filtered NIH integration
- `run_two_part_nih_p3.py` — R17++ Agent 2 M2 (binary + intensive margin)
- `run_negative_control_with_2026.py` — orthopedic surgery
- `run_dermatology_negative_control.py` — R17++ Agent 2 M5 (dermatology)
- `verify_nrmp_pslf_eligibility.py` — ProPublica IRS BMF check
- `analyze_nrmp_program_pslf.py` — B5 baseline (legacy)
- `analyze_policy_p11_improved_cms_matching.py` — P11 (descriptive only post R17)
- `generate_p3_figures.py` — Figures 1+2
- `placebo_test_topical_near.py` — placebo test
- `sensitivity_excl_sdn_medical.py` — SDN-Medical-excluded sensitivity

### LEGACY policy P-series (P-series partially dropped from Path B P3 per R17 re-scoping)
- `analyze_policy_state_heatmap.py` (P1 — dropped)
- `analyze_policy_servicer_specific.py` (P2 MOHELA — DROPPED from Path B)
- `analyze_policy_process_issues.py` (P3 — dropped)
- `analyze_policy_hrsa_hpsa_nrmp.py` (P4 — dropped)
- `analyze_policy_p5_county_hrsa_nrmp.py` (P5 — dropped)
- `analyze_policy_p6_cfpb_topic_comparison.py` (P6 — dropped)
- `analyze_policy_p7_nrmp_pre_post_waiver.py` (P7 — dropped)
- `analyze_policy_p8_cms_quality.py` (P8 — superseded by P11)
- `analyze_policy_p9_within_institution_pre_post.py` (P9 — dropped)
- `analyze_policy_p10_cfpb_company_timeline.py` (P10 MOHELA CFPB share — DROPPED from Path B)
- `analyze_policy_p12_nhsc_vs_pslf.py` (P12 — dropped)
- These were all R10-R12 analyses; their outputs `policy_p*.{txt,csv,png}` are legacy
- Recommendation: archive these scripts + outputs since Path B P3 no longer includes them

### Audit + validation
- `confound_audit.py` — platform × profession + length × polarity checks
- `critical_fixes.py` — R7 critical fixes implementation log
- `analyze_specification_curve.py` — A2 specification curve (360 specs)
- `analyze_l4_sdn_attending_comments.py` — A3 SDN attending check at comments scale
- `analyze_mediation_career_stage.py` — A3 career-stage mediation

### Figure generators
- `generate_p1_figures.py`, `generate_p2_figures.py`, `generate_p3_figures.py` — R17++ canonical paper figures
- `generate_paper_figures.py` — legacy R12 fig_methods_* / fig_substantive_* generator (superseded)
- `plot_master_timeline.py`, `plot_master_timeline_3scorer.py` — timeline plots
- `plot_event_timecourses.py` — per-event timecourses
- `plot_claude_dimensions.py`, `plot_claude_dimensions_by_event.py` — Claude 3-dim plots
- `plot_sdn_nrmp_alignment.py` — SDN-NRMP alignment
- `gen_hires_figs.py`, `gen_legislative_timeline.py`, `gen_volume_artifact_*.py` — high-res helpers

### Utilities
- `pslf_search_terms.py` — anchored PSLF filter (`filter_pslf_relevant`)
- `topic_model_bertopic.py` — BERTopic full-corpus run
- `build_master_numbers_table.py` — master numbers compilation
- `final_summary.py` — R5 statistical summary
- `extract_rejection_reasons.py` — PSLF rejection-reason coding
- `analyze_sdn_subthread_consistency.py` — SDN subthread check
- `analyze_rejection_reasons.py` — rejection-reason analysis
- `analyze_time_to_recovery.py` — per-cohort recovery time
- `probe_acgme_reports.py` — ACGME report scraper
- `run_post_comments_chain.ps1` — comments analysis launcher (PowerShell)

## How to run the canonical results pipeline

See `RUN_ALL.ps1` (TODO) for a one-shot regeneration of all canonical results. Until then, the dependency order is roughly:

1. Data collection (already done; `*.csv` files in `PSLF-Discussion-Analysis/`)
2. Sentiment scoring (already done; `zeroshot_*.csv` files)
3. Paper-1 analyses: `compare_multi_llm_with_sdn.py` → `compute_paraphrase_robustness.py` → `analyze_op_vs_reply.py` → `run_op_vs_reply_cluster_bootstrap.py`
4. Paper-2 analyses: `pslf_intention_analysis.py` → `analyze_l5_cohort_robustness.py` → `analyze_topic_per_cohort_per_event.py` → `run_holm_bonferroni_p2_chi_sq.py` → `run_p2_optional_audits.py`
5. Paper-3 analyses (in order; later ones depend on earlier outputs):
   - `run_model5_FINAL.py` (5-yr baseline)
   - `run_model5_2021_2026_cross_sectional.py` (6-yr)
   - `integrate_nih_into_model5.py` (state-NIH)
   - `wild_cluster_bootstrap_p3.py` (Webb)
   - `run_trend_regression_p3.py` (is_2026 + is_post_eo)
   - `run_negative_control_with_2026.py` (orthopedic)
   - `run_dermatology_negative_control.py` (R17++ second neg-ctl)
   - `run_two_part_nih_p3.py` (R17++ Agent 2 M2)
   - `run_model5_with_2026_post_eo.py` + `run_model5_pre_post_eo_split.py` (descriptive)
6. Figures: `generate_p1_figures.py` + `generate_p2_figures.py` + `generate_p3_figures.py`

---

*Last updated 2026-05-11 (R17++). Update this README when adding/removing scripts.*
