# PSLF Project — QUICKSTART

**For a new session, read this first.** PROJECT_INDEX.md is the comprehensive index; this is the 5-minute onboarding.

## What is this project?

Three peer-review papers on Public Service Loan Forgiveness (PSLF) discourse + residency-match outcomes, targeting Tier-2 venues, plus a supplementary dataset deposit (Dryad/Zenodo with citable DOI; **not** a separate paper):

| Paper | Venue | Status | Headline |
|---|---|---|---|
| **P1 Methods** | EPJ Data Science | Ready to draft | 3-LLM Krippendorff α = +0.7590 on n=1,001 above 0.667 floor; LLM-class vs lexical-class construct boundary |
| **P2 Substantive** | JCSS | Ready to draft (post-level scope per R17 Option A) | Cohort-conditional sentiment-stance coupling; SDN-Medical OR=0.27, r/PSLF OR=7.33, Finance OR=0.18 |
| **P3 Policy** | JGME | Ready to draft NOW (shortest path) | PSLF-hostile cross-sectional fill-rate differential −18.07 pp (S1) at n=29,349; Trump-EO causal interpretation RETRACTED |

**Recommended drafting order: P3 → P1 → P2.** P3 is the shortest path (3-4 weeks of focused writing) and most-ready substantive paper. P1 (EPJ DS) and P2 (JCSS) follow.

**Supplementary infrastructure (NOT a paper):** PSLF-eligibility classification dataset (872 institutions × 2021–2026 × S1/S2/S3 sensitivity specs) deposited at Dryad or Zenodo with a citable DOI as part of P3's submission package. See `DATASET_DEPOSIT_PLAN.md` for the deposit checklist. The earlier "P4 *Scientific Data* paper" framing (2026-05-17) was reverted after an honest assessment: the dataset has narrow utility (5-10 active researchers), realistic citation count 10-25 over 5 years, and the separate paper would be procedurally easy but substantively low-impact. The deposit captures the citable-infrastructure benefit at ~zero additional writing cost vs the standalone paper's ~3 weeks.

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
