# PSLF 2026 Project Index — Single Navigation Point

**Last updated:** 2026-05-10 (after Round 17 audit fixes — dedup + state-NIH + Trump-EO retraction + Paper 2 post-level scope)
**Status:** Drafting-ready. All numerical work locked. Round 17 corrections applied across all 3 papers.

---

## TLDR — Where to start

| Goal | Open this file |
|---|---|
| Start drafting Paper 3 immediately (no waiting) | `PAPER_3_DRAFT_READY.md` |
| Start drafting Paper 1 (mostly locked; minor refresh later) | `PAPER_1_DRAFT_READY.md` |
| Look up any number | `MASTER_LOCKED_NUMBERS.md` |
| Look up any citation | `MASTER_REFERENCE_LIST.md` |
| Use a reusable text block | `MASTER_DRAFTING_KIT.md` |
| When comments collector finishes | `POST_COMMENTS_PLUG_AND_PLAY.md` |
| See current state of project | this file |

---

## File structure (drafting-ready, post-cleanup 2026-05-10)

```
C:\Users\zanen\PSLF_2026\
│
├── PROJECT_INDEX.md                                    ← THIS FILE (master nav)
│
├── (CANONICAL DRAFTING KIT)
├── MASTER_LOCKED_NUMBERS.md                            ← All numbers
├── MASTER_REFERENCE_LIST.md                            ← All citations
├── MASTER_DRAFTING_KIT.md                              ← Reusable text blocks
├── POST_COMMENTS_PLUG_AND_PLAY.md                      ← Post-comments workflow (now mostly done)
│
├── (PAPER TEMPLATES)
├── PAPER_1_DRAFT_READY.md                              ← Paper 1 template (EPJ DS)
├── PAPER_2_DRAFT_READY.md                              ← Paper 2 template (JCSS)
├── PAPER_3_DRAFT_READY.md                              ← Paper 3 template (JGME)
│
├── (LOCKED RESULTS — one-page per paper)
├── PAPER_1_LOCKED_RESULTS_FINAL.md
├── PAPER_3_LOCKED_RESULTS_FINAL.md
├── PAPER_3_REFRAMING_ANALYSIS.md                       ← Post-2026 audit doc
│
├── (LATEST AUDIT)
├── AUDIT_round16_POST_STRENGTHENERS_FINAL.md           ← Latest publishability synthesis
│
├── (OSF + cross-domain replication planning)
├── OSF_PREREGISTRATION_cross_domain.md
├── OSF_TRANSPARENCY_PACKAGE.md
├── cross_domain_replication_design.md
│
├── (PROJECT CONFIG)
├── README.md
├── pyproject.toml
├── requirements.txt
│
├── (DATA + ANALYSIS OUTPUTS)
├── PSLF-Discussion-Analysis/
│   ├── *.csv (119 files)                               ← All analysis-ready data
│   ├── *.txt (63 files)                                ← All analysis output text files
│   ├── *.png (48 files)                                ← All figures
│   ├── *.json                                           ← Cache + intermediate
│   ├── nrmp_pdfs/                                       ← Source NRMP PDFs (incl. 2026)
│   ├── logs/                                            ← Run logs (4 files)
│   └── *.xlsx (NHSC + CMS data)
│
├── (CODE)
├── scripts/                                             ← 94 Python scripts
│   ├── collect_*.py                                     ← Data collection
│   ├── sentiment_*.py + compute_*.py                   ← Sentiment scoring
│   ├── analyze_*.py                                     ← All analyses
│   ├── compare_*.py                                     ← Comparison + triangulation
│   ├── run_model5_*.py + wild_cluster_bootstrap_p3.py  ← Paper 3 regressions
│   ├── monitor_and_extract_nrmp_2026.py                ← NRMP 2026 monitor
│   ├── pull_nih_reporter.py                             ← NIH RePORTER puller
│   ├── build_*.py + integrate_*.py                     ← Confounders + integration
│   ├── plot_*.py + gen_*.py                            ← Figure generators
│   ├── pslf_search_terms.py                             ← Shared filter
│   └── run_post_comments_chain.ps1                     ← Comments analysis launcher
│
└── archive/                                             ← Pruned files (84 total)
    ├── README.md                                        ← What's where
    ├── audits/                       (8 files)          ← Prior audit rounds
    ├── legacy_outlines/              (4 files)          ← Pre-DRAFT_READY paper outlines
    ├── legacy_synthesis/             (6 files)          ← Pre-PROJECT_INDEX synthesis docs
    ├── policy_briefs/                (4 files)          ← Early-phase briefs
    ├── legacy_user_actions/          (2 files)          ← Completed user-action docs
    ├── data_acquisition_decisions_not_pursued/  (3 files) ← AAMC/NSLDS/NRMP letter (decided not needed)
    ├── data_backups/                 (9 files)          ← Pre-round CSV backups
    ├── legacy_data/                  (~17 files)        ← Top-level pre-Arctic-Shift data + notebooks
    ├── legacy_figures/               (~10 files)        ← Top-level early figures
    └── scripts_legacy_scrape_attempts/ (16 files)       ← Failed scrape artifacts (PA forum, allnurses, bogleheads)
```

**Counts**: 16 canonical MD docs at top level (was 70+); 94 working scripts; 119 CSVs in data dir; 84 archived files.

---

## Three papers at a glance (P4 *Scientific Data* paper proposal REVERTED 2026-05-17 — see audit history)

| Paper | Title | Venue | Status | Length | Tables | Figures | Suppl |
|---|---|---|---|---|---|---|---|
| **P1 Methods** | Convergent Validity Failure Between Lexical and LLM-Class Sentiment Instruments... | EPJ Data Science | Ready (OP-vs-Reply minor refresh after comments) | 6-8K words | 4 | 3 | 8 |
| **P2 Substantive** | Cohort-Conditional Sentiment-Stance Coupling in Online Policy Discourse... | JCSS | Ready (cohort heterogeneity + panel refresh after comments) | 5-7K words | 5 | 3 | 7 |
| **P3 Policy** | PSLF Eligibility Differential in Residency Match Outcomes... | JGME | Ready NOW | 3-4K words | 5 | 2 | 8 |

**Recommended drafting order: P3 → P1 → P2** (P3 shortest path + locked numbers; P1 highest-impact second submission; P2 in parallel).

**Supplementary infrastructure (NOT a paper):** PSLF-eligibility classification dataset deposited at Dryad/Zenodo as part of P3's submission package. See `DATASET_DEPOSIT_PLAN.md`. Rationale for not pursuing a separate paper: realistic citation count ~10-25 over 5 years (narrow utility — 5-10 active PSLF-residency researchers), low substantive impact (descriptor, not a finding); the deposit captures the citable-DOI infrastructure benefit at ~zero opportunity cost vs the standalone paper's ~3 weeks of writing.

---

## Acceptance probabilities (Round 16 final + R17++ #2 update)

| Paper | Venue | Acceptance % |
|---|---|---|
| P1 Methods | EPJ Data Science | **45-55%** |
| P2 Substantive | JCSS | **30-38%** |
| P3 Policy | JGME (primary) / AcadMed (secondary) | **30-37%** |

---

## What's already done

✅ Data collection (Reddit Arctic Shift + SDN Playwright + comments collector COMPLETE: 528,051 comments)
✅ Three sentiment instruments scored on n=9,242 corpus (TextBlob + VADER + Claude)
✅ Three LLM convergence test on n=1,001 intersection (Claude + Llama + DeepSeek; SDN-included)
✅ Paraphrase-robustness test-retest (3 prompts, K-α=+0.9011 sentiment, 0.93-0.96 stance/topic pairwise) — **independently replicated R17++ #3 at n=399 with identical point estimate α=+0.9011 [+0.8680, +0.9300]; 22% CI tightening; lower-CI headroom above 0.85 widened from +0.007 (n=200) to +0.018 (n=399)**
✅ Per-author longitudinal panel feasibility analysis (8 events; all CIs ≥25 pp wide)
✅ Per-event topic restructuring (8 events × 7 topics, all chi-sq p<10⁻⁴)
✅ Cohort heterogeneity OR table (5 cohorts × 3 operationalizations)
✅ Base-rate-adjusted lift computation (5 cohorts)
✅ NRMP × PSLF program-year regression (5-year baseline n=29,349 + 6-year sample n=35,193; 3-spec sensitivity for HCA-academic partnerships)
✅ Cluster-robust SE + wild-cluster bootstrap for Paper 3 (Webb 6-point, B=2,000)
✅ State-filtered NIH RePORTER integrated into Model 5 (locked β=−18.07 pp p=2.1×10⁻²⁸; funding NS)
✅ Trend-regression test for 2026 EO discontinuity (year_centered p=0.105; is_2026 p=0.46 NS — 2026 continues trend)
✅ All 19 Round 15 mandatory fixes applied
✅ All 3 Round 16 strengtheners run (SDN multi-LLM + paraphrase + wild-cluster)
✅ Round 17 audit fixes (CMS-merge dedup, Trump-EO retraction propagation, Paper 2 post-level scope, P1 §5.5b add, transparency statement)
✅ TB×VADER convergent-validity replicates at 519K-comment scale (α=+0.2892 [+0.287, +0.292])
✅ Internal consistency propagated across abstract / body / locked-results / dashboard
✅ Master locked numbers + reference list + drafting kit + plug-and-play guide created

---

## What's left to do

### Before drafting starts (automated)

⏳ Comments collector finishes (~7% to go; currently running)
⏳ Run `run_post_comments_chain.ps1` (~30 min) → refreshes 4 placeholder numbers
⏳ Update `MASTER_LOCKED_NUMBERS.md` with the refreshed values (~10 min)

**Total: ~45 min wall-time + ~few hours waiting for comments collector**

### Drafting (the actual writing work)

📝 Paper 1: 6-8 weeks of focused writing → arXiv + EPJ DS submission
📝 Paper 2: 6-8 weeks of focused writing → SSRN + JCSS submission
📝 Paper 3: 4-6 weeks of focused writing → medRxiv + JGME submission

**Recommended sequence:**
1. **Now (Day 1-3)**: Draft Paper 3 §1 + §2 (Introduction + Methods); these don't depend on comments
2. **Now-Week 1**: Draft Paper 3 §3 + §4 + §5 (Results + Discussion + Conclusions); all numbers locked
3. **Week 1-2**: Comments collector finishes; run plug-and-play; update master numbers
4. **Week 2-4**: Draft Paper 1 sections in parallel with Paper 3 final review
5. **Week 4-6**: Draft Paper 2 sections
6. **Week 6-8**: Polish + co-author review + arXiv/SSRN/medRxiv pre-prints
7. **Week 8-10**: Submit P1 (EPJ DS) + P3 (JGME); Paper 2 holds pending comments-scale full sample
8. **Week 10-14**: Submit P2 (JCSS)

---

## Key empirical numbers to memorize

### Paper 1 (FINAL, all numbers locked)
- **3-LLM K-α (combined Reddit + SDN, n=1,001) = +0.7590** [+0.7241, +0.7868] — above tentative-reliability floor (0.667)
- **3-LLM K-α (SDN-only, n=300) = +0.8306** [+0.787, +0.866] — above satisfactory-reliability floor (0.80)
- **Paraphrase-robust K-α (3 prompts, n=399 R17++ #3 replication 2026-05-17) = +0.9011** [+0.868, +0.930] — above true-test-retest threshold (0.85) with +0.018 lower-CI headroom (vs +0.007 at n=200 R16). Independent fresh sample from same 615-post SDN-baseline pool; CI half-width tightened 22%; point estimate identical to R16 historical (α=+0.9011 [+0.857, +0.938]).
- **Adding TextBlob drops 4-rater α by 0.42**; **adding VADER drops by 0.52** under FIXED thresholds
- **Stance task: 80.9% all-three-LLM-agree** (n=472)
- **OP-vs-Reply at full ~500K-comment scale**: TB Δ=−0.0146 (p<10⁻⁵⁰), VADER Δ=+0.2387 (p≈0); 8/8 cohorts same-direction-mismatch — REPLICATES post-level finding
- **TB × VADER triangulation at comments scale (n=519,342)**: α=+0.2892 [+0.287, +0.292] — REPLICATES post-level α=+0.34 (within 0.10). Construct boundary holds at 75× sample-size scaling.

### Paper 2 (UPDATED with comments-scale findings)
- **SDN-Medical lift_pp = −16.5** (real decoupling, fully cross-instrument concordant) — POST scale
- **r/PSLF lift_pp = +10.0** (real coupling, 4/5 specs OR>1) — POST scale
- **Reddit Finance lift_pp = −17.6 same-scorer; cross-scorer noisy with CIs spanning 1.0** (construct-misalignment exemplar) — POST scale
- **3 null cohorts** (lifts within ±3 pp): r/StudentLoans, Reddit Medical, Reddit Teaching — POST scale
- **Per-event topic restructuring: chi-sq p<10⁻⁴ for ALL 8 events** — POST scale
- **All 8 events: within-person panel infeasible** (CIs ≥25 pp wide); adding comments-presence raises author-overlap by ~5pp but stance still requires Claude OP in both windows; only Trump EO meets n≥10 (n=13)
- **CAVEAT: At comments scale (n=519,342), Trump PSLF EO event shows MOSTLY CONCORDANT NEGATIVE response across cohorts** (g range −0.01 to −0.65) — post-level cohort heterogeneity may be a property of the curated poster pool, not commenter pool

### Paper 3 (Round 17 dedup-corrected; HONEST framing post-audit)
- **Cross-sectional 2021-2025 (HEADLINE)**: PSLF-hostile β = −18.07 pp (S1) / −16.25 pp (S2) / −17.14 pp (S3) — all cluster-robust 95% CIs exclude zero
- **Wild-cluster bootstrap p**: <0.0005 / 0.017 / 0.006 — all survive α=0.05
- **Model 5 + state-filtered NIH** (n=29,349 OLS sample; 92 of 721 institutions NIH-matched, 87% mass-point at $0): β=−18.07 pp [−21.28, −14.87], p=2.1×10⁻²⁸; log_nih_funding NS — funding doesn't absorb PSLF effect (NIH coefficient is mis-specified due to mass-point but PSLF coefficient is robust)
- **6-year extended sample** (post Round 17 CMS-merge dedup): n=37,450 raw / 35,193 post-OLS-fit, from 872 institutions; pooled β=−16.31 pp (S1) reflecting 2026 narrowing pulling average toward zero
- **Multi-year trend** (2021→2026): Gap narrowed every year since 2022 peak (−16.5 pp → −7.0 pp)
- **2026 (first post-Trump-EO Match) gap = −7.03 pp** (continues pre-existing trend)
- **2026 indicator beyond linear trend: NS** (β=+2.98 pp, p=0.46) — **no evidence of EO-specific discontinuity**
- **AUDIT RETRACTION (preserved)**: Earlier "Trump EO eliminated PSLF differential" framing was OVERSTATED. The 2026 narrowing is statistically indistinguishable from continuation of a pre-existing 5-year trend. Round 17 added retraction banners to 2 P3 supplementary files (paper3_model5_with_2026_results.txt, paper3_model5_pre_post_eo_results.txt) and corrected 5 stale paragraphs in PAPER_3_DRAFT_READY.md.
- **Negative-control orthopedic surgery (Round 17 dedup-corrected)**: 2021–2025 β = +0.67 pp NS (n=1,007, 11 hostile rows from 3 institutions); 2021–2026 β = +0.54 pp NS (n=1,204, 16 hostile rows from 4 institutions); power floor improved 1.33 → 1.06 pp

---

## Common reviewer questions and pre-emptive answers

### "What about Calderon et al. 2025 in Scientific Reports?"
P1 §1.3 + §2.2 cite and differentiate; we extend to (a) longer forum text, (b) cohort stratification (SDN above 0.80 floor), (c) 5-instrument intersection at n=1,001 (vs Calderon's smaller validation sets), (d) paraphrase-robustness as a methodological contribution.

### "Why not just use a fine-tuned BERT?"
P1 §6.4 acknowledges this as a future work item. Our paper is about LLM-class vs lexical-class; BERT-class would be an interesting third class to study.

### "Your test-retest is just API determinism."
P1 §4.4 + §5.4 + L0b: True 100% same-prompt determinism, AND paraphrase-robustness K-α=+0.9011 across 3 alternative prompts. The latter is true psychometric test-retest under prompt variation.

### "Reddit profession subs aren't representative of PSLF discussants."
P1 §3.5 + §7 L0a (now resolved by SDN inclusion): n=1,001 includes SDN-Medical (n=300, the dominant physician PSLF community); cohort heterogeneity in inter-LLM agreement is itself a substantive finding.

### "Your CMV claim isn't really CMV."
P2 §1.2 + §2.3 + §5.3: Acknowledge as initial framing; correct to **construct-misalignment + sample-selection** in §5.3. Cite Bestvater & Monroe 2023 instead of Podsakoff 2003 as our framework.

### "Cohort heterogeneity is just 1/5 cohorts not 2/5."
P2 §5.1 (Round 16 honest framing): we explicitly report only 1/5 cohorts as fully cross-instrument concordant (SDN-Medical). r/PSLF is "coupling under most operationalizations." The "two robust patterns" framing was retracted.

### "You don't have power to detect small uniform-recruitment confound in orthopedic surgery."
P3 §3.5 + §4.4: explicitly state ortho test only rules out uniform confounds > 1.3 pp. Result is suggestive, not conclusive.

### "Your cluster-robust SE assumes large-cluster asymptotics."
P3 §2.5 + §3.2: Wild-cluster bootstrap (Webb 6-point, B=2,000) per Cameron-Miller 2015 confirms all 3 specs at α=0.05. Cluster-robust p-values overstated precision by 7-8 orders of magnitude in S2/S3.

### "HCA-academic partnerships might have PSLF-eligible residents."
P3 §2.3 + §3.2: 3-spec sensitivity (S1/S2/S3) brackets the plausible range. Without W-2 data we cannot determine which is the truth, but headline is robust to the choice (β between −16 and −18 pp).

---

## Audit history (16 rounds)

| Round | Date | Outcome |
|---|---|---|
| R1-R6 | 2026-04 | Initial audits, 46 fixes |
| R7 | 2026-05-08 | Bootstrap rewrite, K-α CI, test-retest design |
| R8 | 2026-05-09 | Arctic Shift expansion (76K Reddit posts) |
| R9 | 2026-05-10 | 4 new analyses, 8 critical statistical fixes |
| R10-R13 | 2026-05-09→10 | Llama 3.3 70B replication, L5 cross-instrument robustness |
| R14 | 2026-05-10 | 3 parallel adversarial agent audits |
| R15 | 2026-05-10 | Multi-agent audit caught 19 critical issues |
| R16 (initial) | 2026-05-10 | All 19 fixes applied |
| R16 (re-audit) | 2026-05-10 | Re-audit found internal consistency issues; full propagation done |
| R16 (strengtheners) | 2026-05-10 | 3 strengtheners run: SDN multi-LLM (P1 +10pp), paraphrase robustness (P1 +3pp), wild-cluster bootstrap (P3 +5pp) |
| **R17 (audit + dedup fix)** | **2026-05-10** | **CMS-merge dedup bug fixed in 7 scripts; all Model 5 scripts re-run (5-year baseline n=29,349 unchanged; 6-year sample n=37,450 raw / 35,193 post-OLS-fit; corrects pre-fix 37,802 → post-fix 35,193 OLS-sample, dedup of 8 case-collision city duplicates); state-filtered NIH integrated (locked β=−18.07 pp, p=2.1×10⁻²⁸); Trump-EO causal interpretation retracted (is_2026 indicator p=0.46 NS confirms 2026 narrowing continues 5-year trend); Paper 2 scoped to post-level (drop §5.3b comments-scale main-text role); Paper 1 reframings (paraphrase as "lexical-format", magnitude framing for OP-vs-Reply, Together AI infrastructure caveat, soften "no precedent" language); P1 §5.5b added for TB×VADER comments-scale finding; transparency statement added to P3 abstract** |
| **R17++ (citation sweep + Notion overhaul)** | **2026-05-11** | 35+ citations re-verified; 8 self-found errors fixed; 5 unverifiable removed; Notion content updated to R17++ canonical |
| **R17++ #2 (publication push)** | **2026-05-16** | 7 publication figures generated (300 DPI); 4 code-required audits completed; OSF venue migration (Political Analysis → EPJ DS); Whitcomb 2014 removed (6th unverifiable); audit infrastructure committed (RUN_AUDITS.ps1 + RUN_ALL.ps1 + QUICKSTART.md + scripts/README.md, 14 integrity tests) |
| **R17++ #3 (paraphrase replication)** | **2026-05-17** | **Paraphrase robustness independently replicated at n=399** (point estimate identical α=+0.9011; CI tightened 22%; lower-CI headroom above 0.85 widened from +0.007 to +0.018; Bessel-expected CI ratio 0.71 matched at observed 0.77 — well-conditioned replication). New artifacts: `paper1_figS_paraphrase_replication.png` (supplementary forest plot), patched `compute_paraphrase_robustness.py` with replication-comparison section, n=200 historical CSV backups preserved at `*_n200_historical.csv` |
| **R17++ #3 revert (P4 honest reassessment)** | **2026-05-17** | After direct user questioning ("is 4 an actual interesting paper" / "is it truly publishable and impactful?"), the *Scientific Data* (Nature) "Paper 4" proposed earlier in R17++ #3 was reverted. Honest impact assessment: ~10-25 realistic citations over 5 years (narrow utility — only 5-10 active PSLF-residency researchers); substantive impact ~zero (descriptor, not finding); the original "50-100 citations / highest yield" framing was overstated. Reverted across QUICKSTART + PROJECT_INDEX + .claude/CLAUDE.md + Notion + memory; `PAPER_4_DRAFT_READY.md` deleted (preserved in git history at `3fceaf8`); replaced with `DATASET_DEPOSIT_PLAN.md` — same dataset deposited at Dryad/Zenodo with a citable DOI cited from P3, ~1 day of metadata work vs ~3 weeks of standalone-paper writing, captures the citable-infrastructure benefit at ~zero opportunity cost. Drafting order reverts to **P3 → P1 → P2** |

---

## Next milestone

**Wait for comments collector → run post-comments chain (~30 min) → start drafting.**

Or: **start drafting Paper 3 now.**

The papers will write themselves from the templates. The empirical work is locked.

---

*This is the single source of truth for the project. All other documents pull from here.*
