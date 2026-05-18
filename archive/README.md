# Archive Directory

This directory contains all files that were superseded, completed, or never pursued, but preserved for historical reference. Nothing here is required for current drafting work; all canonical files live at the project root.

**Pruned:** 2026-05-10

---

## Subdirectory contents

### `audits/` (8 files)
Prior audit-round documents. Latest audit (`AUDIT_round16_POST_STRENGTHENERS_FINAL.md`) remains at top level.
- `AUDIT_round10_LINKING_RESULTS.md`
- `AUDIT_round10_findings.md`
- `AUDIT_round11_P8_CMS_correction.md`
- `AUDIT_round12_P11_REVERSAL.md`
- `AUDIT_round13_LLM_REPLICATION_AND_COHORT_FRAGILITY.md`
- `AUDIT_round14_ADVERSARIAL_LITERATURE_REVIEW.md`
- `AUDIT_round15_MULTI_AGENT_SYNTHESIS.md`
- `AUDIT_round16_FINAL_PUBLISHABILITY_SYNTHESIS.md` (intermediate; superseded by `_POST_STRENGTHENERS_FINAL.md`)

### `legacy_outlines/` (4 files)
Paper outlines superseded by the `PAPER_*_DRAFT_READY.md` templates.
- `PAPER_1_combined_methods_substantive_OUTLINE.md` (very early, pre-Path-B)
- `PAPER_1_EPJ_DS_methods_only_OUTLINE.md` (Path-B initial)
- `PAPER_2_JCSS_substantive_OUTLINE.md` (Path-B initial)
- `PAPER_3_JAMA_HF_policy_OUTLINE.md` (Path-B initial; venue later changed to JGME)

### `legacy_synthesis/` (6 files)
Earlier synthesis docs and intermediate planning artifacts.
- `PATH_B_EXECUTION_PLAN.md` (superseded by drafting kit + PROJECT_INDEX)
- `PATH_B_STATUS_DASHBOARD.md` (superseded by PROJECT_INDEX)
- `CONSOLIDATED_MAIN_STORY.md` (very early)
- `FULL_DETAIL_REFERENCE.md` (superseded by MASTER_LOCKED_NUMBERS + REFERENCE_LIST)
- `PUBLICATION_SYNTHESIS_aggregate_view.md` (very early)
- `PAPER_3_LOCKED_RESULTS_2026-05-10.md` (superseded by `_FINAL.md`)

### `policy_briefs/` (4 files)
Policy-brief drafts from an earlier project phase. Not part of current paper-publication pipeline.

### `legacy_user_actions/` (2 files)
User-action documents for completed work.
- `USER_ACTIONS_round16_strengtheners.md` (all 3 strengtheners completed)
- `USER_ACTION_open_weight_LLM.md` (Llama + DeepSeek scoring done)

### `data_acquisition_decisions_not_pursued/` (3 files)
Instruction docs for data acquisitions we decided NOT to pursue (per Round 16 dashboard decision).
- `AAMC_GQ_data_request_instructions.md` — AAMC Graduation Questionnaire microdata; not needed
- `NSLDS_DUA_application_instructions.md` — NSLDS individual-level loan data; 6-12 month wait; not needed
- `NRMP_program_level_data_instructions.md` — NRMP DUA; we use publicly-published Match Results data instead

### `data_backups/` (9 files)
Pre-round backups of data CSVs. The main current data files in `PSLF-Discussion-Analysis/` supersede these.

### `legacy_data/` (~16 files)
Top-level CSV/notebook files from early project phase (pre-Arctic-Shift expansion). Current data lives in `PSLF-Discussion-Analysis/`.
- `combined_pslf_discussions.csv`
- `comprehensive_*.csv`
- `enhanced_*.csv`
- `reddit_*_pslf_*.csv`
- `sdn_pslf_discussions.csv`
- `files.zip`
- `medical.ipynb`, `teaching.ipynb`
- `paper_discussion_drafts.md`
- `paper_figures_index.md`

### `legacy_figures/` (~10 files)
Top-level figure*.png from early project phase. Current figures live in `PSLF-Discussion-Analysis/`.

### `scripts_legacy_scrape_attempts/` (16 files)
Failed or unused scraping attempts.
- `paf_*.html` + `paf_cookies.txt` — Cloudflare-blocked PA forum (physicianassistantforum.com)
- `xcancel_*.json` — unrelated to current project
- `collect_pa_forum.py` — Cloudflare-blocked
- `collect_youtube_pslf.py` — never used
- `collect_bogleheads.py` — Cloudflare-blocked
- `collect_allnurses.py` — Cloudflare-blocked
- `debug_sdn.py`, `save_pages.py` — debug/utility scripts no longer needed

---

## Restoring archived files

If anything in here is needed for drafting:
```powershell
Move-Item C:\Users\zanen\PSLF_2026\archive\<subdir>\<filename> C:\Users\zanen\PSLF_2026\
```

Nothing has been deleted; everything is preserved for reference.
