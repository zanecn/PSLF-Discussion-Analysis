# PSLF Project — QUICKSTART

**For a new session, read this first.** PROJECT_INDEX.md is the comprehensive index; this is the 5-minute onboarding.

## What is this project?

**Five outputs targeting both substantive impact and publication count for medical-student NS-match application** (MS3 ending → research year next → ERAS Sept 2027; neurosurgery match averages ~18 ERAS research items, top quartile 30-50):

| Paper | Venue | Status | Headline |
|---|---|---|---|
| **P1 Methods** | EPJ Data Science | Ready to draft | 3-LLM Krippendorff α = +0.7590 on n=1,001 above 0.667 floor; paraphrase α=+0.9011 replicated at n=399 (R17++ #3) |
| **P2 Substantive** | JCSS (primary) / **PLOS One** (backup if speed needed) | Ready to draft (post-level scope per R17 Option A) | Cohort-conditional sentiment-stance coupling; SDN-Medical OR=0.27, r/PSLF OR=7.33, Reddit Finance OR=0.18 cross-scorer sign-flip |
| **P3 Policy** | JGME | Ready to draft NOW (shortest path; ~3-4 weeks) | PSLF-hostile cross-sectional fill-rate differential −18.07 pp (S1) at n=29,349; Trump-EO causal interpretation RETRACTED |
| **P4 Data** | *Scientific Data* (Nature) | Ready to draft (artifact locked; ~3 weeks) | 872-institution PSLF-eligibility classification 2021–2026, ProPublica IRS-verified, S1/S2/S3 HCA-academic sensitivity specs; CV line + Nature-family title; cites the Dryad/Zenodo deposit DOI |
| **P5 NS spin-off** | *Neurosurgery* (Wolters Kluwer) / *JAMA Surgery* / *World Neurosurgery* | Ready to draft (~2-3 weeks; data feasibility verified 2026-05-17) | 124 of 125 (99.2%) US neurosurgery residency programs are PSLF-eligible/ambiguous 2021–2026; sole hostile (HCA Kansas City) at 100% fill; specialty-relevant publication for NS match |

**Recommended drafting order: P3 → P4 → P5 → P1 → P2** (P3 first because shortest + highest substantive impact; P4 second to mint the Dryad/Zenodo DOI that P3 cites; P5 third because NS-specialty-relevant and short; P1 + P2 last with longer review cycles).

**Conference abstracts pipeline:** 5 concrete abstract submissions planned per `CONFERENCE_ABSTRACTS_PLAN.md` targeting AANS Annual Meeting (Apr/May 2027; **abstract deadline ~Oct 2026 — CRITICAL PATH**), CSNS Annual Meeting, AAMC Health Workforce Research Conference, AcademyHealth ARM, AAMC RIME. Realistic yield: 2-4 conference presentations on ERAS (50-70% typical abstract accept rates) = 2-4 additional research items.

**Supplementary infrastructure:** PSLF-eligibility classification dataset deposited at Dryad (primary) / Zenodo (mirror) with citable DOI, cited from P3, P4, and P5 Methods sections. See `DATASET_DEPOSIT_PLAN.md` for deposit checklist. (The earlier 2026-05-17 a.m. revert of P4 was made under wrong assumption that user was tenure-track academic optimizing for research impact; med-student NS-match context changes the calculus.)

## 5-minute resume-where-you-left-off

```powershell
# 1. Verify clean state
cd C:/Users/zanen/PSLF_2026
git pull && git status

# 2. Read in this order (5–10 min)
# - QUICKSTART.md (this file)
# - PROJECT_INDEX.md (comprehensive)
# - MASTER_LOCKED_NUMBERS.md (every number, R17++ corrected)

# 3. Pick a paper to work on and read its outline + locked one-pager
# - PAPER_3_DRAFT_READY.md + PAPER_3_LOCKED_RESULTS_FINAL.md  (start here — shortest)
# - PAPER_1_DRAFT_READY.md + PAPER_1_LOCKED_RESULTS_FINAL.md
# - PAPER_2_DRAFT_READY.md (no locked one-pager; numbers in MASTER)
```

## Critical things to NOT forget

1. **Trump PSLF EO causal interpretation is RETRACTED** (R17 audit). The 2026 narrowing of the PSLF-hostile fill-rate gap is consistent with continuation of a 5-year pre-existing trend, NOT an EO discontinuity. `is_2026` indicator p=0.46 NS; `is_post_eo` (year≥2025) sensitivity p=0.877 NS. Design lacks power to identify EO-specific impact.

2. **ZERO TOLERANCE for fabricated/misattributed citations** (R17++ rule). Every cited paper must be independently WebSearch-verified at AUTHOR LEVEL (not just substance). The R17++ second-pass audit caught 3 fabrications where substance matched but author surnames were hallucinated (Calderon→Bojić, Cohen+Reddy→Lassner, EO 14253→14235). See `📝 Citation Integrity Log` Notion page.

3. **Trump EO is EO 14235** (NOT EO 14253). Signed March 7, 2025. ED Final Rule announced Oct 30, 2025; FR published Oct 31, 2025; effective Jul 1, 2026.

4. **5-instrument intersection n=1,001** (Reddit 701 + SDN 300) is the P1 canonical sample. Claude Sonnet 4 + Llama 3.3 70B Instruct Turbo (via Together AI) + DeepSeek V3.1 (via Together AI) + TextBlob + VADER. Together AI infrastructure caveat: 2/3 LLMs share serving.

5. **OP-vs-Reply cluster-bootstrap CIs are computed** (`paper1_op_vs_reply_cluster_bootstrap_results.txt`) — REPLACES the fabricated CIs in earlier drafts. TB: [−0.013, −0.008] boot p=0; VADER: [+0.205, +0.224] boot p=0; magnitude ratio 20.5×.

6. **Paper 2 scope = POST-LEVEL only** (R17 Option A). Comments-scale (n=519K) used only for P1 cross-citation (TB×VADER convergent-validity replication) + Supplement S5 descriptive.

7. **6 of 8 events significant** after Holm-Bonferroni (NOT the earlier "all 8 events p<10⁻⁴" claim). Biden v. Nebraska p=0.44 NS; Payments Restart p=0.37 NS.

## Highest-leverage next action

**Draft Paper 3 (JGME) §1 Introduction.** All numbers locked, citations corrected, 2 figures generated. Outline at `PAPER_3_DRAFT_READY.md` is detailed enough to write directly from. ~4–6 weeks of focused writing for the full paper.

## Where everything lives

```
C:/Users/zanen/PSLF_2026/
├── QUICKSTART.md                       ← this file
├── PROJECT_INDEX.md                    ← comprehensive index
├── MASTER_LOCKED_NUMBERS.md            ← every canonical number
├── MASTER_REFERENCE_LIST.md            ← every citation (R17++ corrected)
├── MASTER_DRAFTING_KIT.md              ← reusable prose blocks
├── PAPER_{1,2,3}_DRAFT_READY.md        ← per-paper outlines
├── PAPER_{1,3}_LOCKED_RESULTS_FINAL.md ← per-paper one-page locked summaries
├── scripts/                            ← 107 Python scripts (see scripts/README.md)
│   └── README.md                       ← script-to-output mapping
├── PSLF-Discussion-Analysis/           ← all data + results
│   ├── *.txt                           ← analysis output text files (numbers)
│   ├── *.png                           ← publication-ready figures
│   ├── *.csv                           ← analysis-ready CSVs (raw + intermediate)
│   ├── nrmp_pdfs/                      ← NRMP source PDFs
│   └── nih_reporter_FY2023_state.csv   ← NIH RePORTER state-filtered
└── archive/                            ← legacy/superseded content (84+ files)
```

Raw CSVs > 100 MB (e.g., `reddit_comments_pslf.csv` 222 MB) are NOT in git per `.gitignore`. Regeneratable from collector scripts.

## Notion mirror

The Notion workspace mirrors this project. Top-level page: **🎓 PSLF Discourse Analysis Project (R17++)**. Six R17++ pages: project reference, P1/P2/P3 per-paper, Citation Integrity Log, plus 5 legacy R12 pages with "superseded" banners.

## When stuck

- For a number: `grep "the number" MASTER_LOCKED_NUMBERS.md` or read PROJECT_INDEX.md
- For a citation: `grep "Author" MASTER_REFERENCE_LIST.md`
- For a methods detail: read the relevant paper's `_DRAFT_READY.md` + check `scripts/README.md` for the source script
- For audit history: `PROJECT_INDEX.md` § "Audit history (R1 → R17++)"
- For a result file: `scripts/README.md` maps each `*_results.txt` to its producing script

---

*Last updated 2026-05-11. If this file goes stale, update it before doing anything else.*
