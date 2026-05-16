# Round 14 Audit — Adversarial Literature Review (BRUTAL)

**Date:** 2026-05-10 (post-DeepSeek scoring run)
**Method:** 3 parallel adversarial literature audits commissioned with explicit instruction to find rejection grounds, not validation
**Scope:** Comprehensive publishability audit for all three planned papers

---

## TL;DR — My earlier optimism was substantially miscalibrated

Three rigorous adversarial audits revealed:

1. **Acceptance probabilities are 50pp lower than I estimated** at Tier-1 venues
2. **Several novelty claims are partially scooped** by 2025-2026 work I missed
3. **Test-retest design is FLAWED** (temp=0 vs temp=1 measures sampling noise, not retest reliability)
4. **Venue choice is wrong** for the policy paper (Health Affairs is poor fit; should be JAMA Health Forum or HSR)
5. **Multiple methodological vulnerabilities** require substantial pre-submission work

**Brutal verdict: Path A (3 Tier-1 papers in 12-18 months) has 12-25% per-paper acceptance probability — UNREALISTIC.** Path B (Tier-2 venues with current data) is realistic. Path C (additional rigor work) preserves Tier-1 ambition with longer timeline.

---

## Three audits, three verdicts

### Methods Paper (Combined Methods+Substantive at PA)
- **Acceptance probability: 12-25%** (was estimated 70-75%)
- Critical issues: Calderon et al. 2025 direct competitor missed; test-retest design flawed; PSLF venue fit weak; Cohen's κ language overclaimed; SDN sample imbalance; "construct mismatch" non-standard terminology
- **If rejected**: Research & Politics (~70%), PSRM, SMR (Chae-Davidson precedent), EPJ Data Science, JCSS

### Substantive (cohort heterogeneity)
- **Acceptance probability at Political Analysis: 15-25%**
- Critical issues: Wang et al. 2025 (arXiv 2509.16831) partial scoop on composition shifts; same-scorer halo is textbook CMV (Podsakoff 2003) not novel; SDN attendings n=88 OR=0.024 is "reject on sight" with d=1 cell; "venting culture" terminology has no precedent; OR magnitudes are 2 outliers vs 3 nulls statistically
- **Best alternative venue**: JCSS (~35-45%) after dropping SDN attending claim and reframing terminology

### Policy (NRMP × PSLF at Health Affairs)
- **Acceptance probability at Health Affairs: 5-10%** (DESK-REJECT RISK HIGH)
- Critical issues: Wrong venue (HA doesn't publish residency match papers); 8+ unmodeled confounders in NRMP regression; derm negative control broken (no variance); pre-2020 baseline empty; MOHELA finding is endogenous-assignment; concern-density filter is circular; CFPB share is denominator artifact; Buyback growth is tautological; P8 vs P11 different denominators
- **Better venues**: JAMA Health Forum (25-35%), Health Services Research (30-40%), Academic Medicine (35-45%)

---

## Literature I missed (must cite)

### Methods paper additions
- **Calderon et al. (2025, Scientific Reports)** — 8 LLMs comparing sentiment/political-leaning/sarcasm with K-α and bootstrap. **Direct competitor in higher-impact venue.**
- **arXiv 2512.20352 (Dec 2025)** — Multi-LLM thematic analysis with Gemini+GPT+Claude, six independent runs
- **Iglesias et al. (2025, JMIR Formative Research e57395)** — VADER + LIWC + T2D + ChatGPT comparison on YouTube opioid comments
- **EMNLP 2025 "Rating Roulette: Self-Inconsistency in LLM-As-A-Judge"** — undermines test-retest claims industry-wide
- **Wang & Culotta (2020); ICLR 2025 spurious correlations paper** — for same-scorer halo framing

### Substantive paper additions
- **Wang et al. (2025, arXiv 2509.16831) "Survivors, Complainers, Borderliners"** — composition-shift framing in Reddit/Zhihu (different domain, same logic)
- **Sobhani et al. (WASSA 2024)** — multi-target stance discovery
- **Podsakoff et al. (2003); Tehseen et al. (2021); Annual Reviews 2024** — CMV literature for same-scorer halo

### Policy paper additions
- **Marcu et al. (2021, PMC8648921)** — survey-based PSLF trainee reliance work
- **Agarwal (2015, AER)** "An Empirical Model of the Medical Match" — canonical match economics paper
- **Pattar et al. (2025, JAMA Network Open)** — residency program characteristics analyses
- **Pathman, Konrad et al.** — long history of NHSC/HPSA workforce papers (NHSC HPSA correlation finding is 30-year-old background, not novel)

---

## 15 Mandatory Pre-Submission Fixes

### Methods paper (3)
1. **Complete proper test-retest design** (temp=0 vs temp=0 on different days, n>=200) — fixes Round 7 "Fix 9" that was marked done but only ran temp=0 vs temp=1
2. **Adopt psychometric terminology** — "convergent validity failure" instead of "construct mismatch"
3. **Cite Calderon et al. 2025 Scientific Reports** — distinguish your work explicitly

### Substantive findings (4)
4. **Cite Wang et al. 2025 (arXiv 2509.16831)** — "Survivors, Complainers, Borderliners"
5. **Reframe same-scorer halo as APPLIED CMV** (Podsakoff 2003), not novel discovery
6. **Drop SDN attending OR=0.024 from headlines** (n=88 with d=1 cell)
7. **Replace "venting culture" with neutral language** ("expressive negativity decoupled from behavioral intention")

### Policy paper (8)
8. **Switch venue from Health Affairs to JAMA Health Forum or HSR**
9. **Add 5+ confounders to NRMP regression** (NIH funding, IMG share, Doximity, fellowships, university affiliation)
10. **Replace derm with proper negative control** (orthopedic surgery in for-profit-heavy markets, or another high-variance specialty)
11. **Drop "structural pre-existing" claim** (n_hostile=4-8 is empty); claim "pattern visible from 2020 onward"
12. **Reframe MOHELA as "MOHELA-period convergence"** not "MOHELA caused failure"
13. **Drop circular concern-density framing** OR re-do with independent keyword set
14. **Drop or qualify PSLF Buyback 5.47× ratio** (tautological without growth-rate baseline comparison to other 2023-launched programs)
15. **Reconcile P8 vs P11 on identical denominators** OR drop the comparison

---

## Three honest publication paths

### Path A — Tier-1 ambition with current data (12-25% per paper)
- Combined Methods+Substantive at Political Analysis: 15-25%
- Policy paper at Health Affairs: 5-10%
- **Realistic outcome**: 1 of 3 attempts succeeds; rest go to Tier-2 after rejection
- **Total time to publication**: 2-3 years (revisions + rejections + resubmissions)
- **Risk**: high; demoralizing; rejected papers may not get re-targeted optimally

### Path B — Tier-2 realism (35-50% per paper) — RECOMMENDED
- Methods paper alone at **EPJ Data Science** or **Behavior Research Methods**: 40-50%
- Substantive cohort heterogeneity at **JCSS**: 35-45% (after dropping SDN attending claim)
- Policy NRMP × PSLF at **JAMA Health Forum**: 25-35% (after addressing 8+ confounders)
- **Realistic outcome**: 2-3 of 3 acceptances
- **Total time to publication**: 12-18 months
- **Strategy**: 3 Tier-2 publications > 1 Tier-1 + 2 Tier-3

### Path C — Maximum rigor before Tier-1 submission (35-50% per paper)
Do additional work BEFORE submitting:
1. Complete proper test-retest design (temp=0 vs temp=0)
2. Cross-domain replication (COVID-vaccine, immigration, abortion)
3. Get NSLDS DUA (6-12 month wait)
4. Add 5+ confounders to NRMP regression
5. Use proper negative-control specialty
6. Then submit Methods+Substantive combined to PA + Policy to JAMA Health Forum
- **Total time to publication**: 18-30 months
- **Acceptance probability**: 35-50% Tier-1
- **Strategy**: Higher prestige, longer wait

---

## Strategic recommendation: Path B

**Be honest about where the data lands you.**

Three Tier-2 publications:
- EPJ Data Science (methods)
- JCSS (substantive)
- JAMA Health Forum (policy)

= ~2-3 publications in 12-18 months at moderate-prestige venues.

Versus Path A:
- 0-1 Tier-1 publications + likely 0-2 Tier-2 publications after rejection
= 1-3 publications in 24-36 months at mixed prestige.

Path B is better expected value AND lower variance.

If you have grant pressure / tenure clock requiring Tier-1, do Path C (longer timeline, more rigor).

---

## What this means for the combined paper plan

The "combined Methods+Substantive at Political Analysis" plan I championed has **15-25% acceptance**. The audit identified 3 specific reasons:
1. Combined paper risks looking like "one finding restated two ways"
2. PSLF is borderline-political (PA editors prefer voting/elections/parliamentary)
3. Substantive headline (cohort heterogeneity) is partially CMV demonstration, not novel discovery

**Revised recommendation**: Either:
- **Keep separate** at Tier-2 venues (Path B) — best expected value
- **Strengthen integration** with explicit "methods explains why substantive finding is real not artifact" argument PLUS add second policy domain (Path C) — preserves Tier-1 ambition

---

## Specific findings that survived the audit

Some claims are STRONGER than I thought:

**Methods paper:**
- ✅ Three-rater K-α at n=9,242 is real and at scale
- ✅ Inter-LLM agreement (Claude×Llama r=+0.703, κ=+0.572) is solid
- ✅ Multi-LLM with DeepSeek (in progress) genuinely strengthens
- ✅ OP vs Reply *operationalization* is novel (TB vs VADER directional disagreement on identical threads is novel even if "post-comment differs" is documented)

**Substantive:**
- ✅ NO PSLF-Reddit/SDN peer-reviewed empirical work exists (real moat)
- ✅ Per-event topic restructuring (chi-sq p<10⁻⁴) is robust and unrelated to CMV
- ✅ SDN-Medical decoupling + r/PSLF venting are real (just be honest they're 2 of 5)

**Policy:**
- ✅ NRMP × PSLF cross-tab is genuinely novel
- ✅ For-profit chain residency fill rates not in any peer-reviewed venue
- ✅ Trump PSLF EO empirical analysis is unoccupied
- ✅ PSLF Buyback documentation is unoccupied (just need non-zero baseline framing)

**These are the publishable contributions.** The rest is overclaim that needs walking back.

---

## Updated to-do (Round 14)

### USER MUST DECIDE FIRST
1. Path A (Tier-1 ambition, 12-25% per paper)
2. **Path B (Tier-2 realism, 35-50% per paper) — RECOMMENDED**
3. Path C (More rigor, longer timeline, 35-50% Tier-1)

### Regardless of path
1. ⏳ Complete proper test-retest design (temp=0 vs temp=0, n>=200, ~$2)
2. ⏳ Update all paper drafts with revised terminology and added citations
3. ⏳ Walk back overclaims (SDN attending, "venting culture", "structural pre-existing")
4. ⏳ Run multi-LLM comparison after DeepSeek finishes
5. ⏳ Comments collector finishes (~1h 15m remaining)

### If Path C selected (RECOMMENDED if grant pressure)
6. ⏳ Cross-domain replication (COVID-vaccine, ~$50, 3-4 weeks)
7. ⏳ NRMP confounders (NIH funding via NIH RePORTER, IMG share via NRMP supplements)
8. ⏳ NSLDS DUA application (6-12 month wait)
9. ⏳ AAMC GQ DUA application (3-month wait)

### Notion updates needed
10. Update Methods Paper page with realistic 12-25% acceptance estimate + 3 mandatory fixes
11. Update Substantive Paper page with realistic 15-45% range + 4 mandatory fixes
12. Update Policy Paper page with realistic 5-45% range + 8 mandatory fixes + venue change

---

## Bottom line

**The data is real. Some findings are publishable.** But:
- Tier-1 acceptance probabilities are MUCH lower than I estimated
- The "combined Methods+Substantive at PA" strategy is risky
- Health Affairs is wrong venue for the Policy paper
- Multiple methodological corrections are required
- Test-retest design fix is non-optional (Round 7 "Fix 9" was incomplete)

**Realistic strategy: Path B (Tier-2 venues) yields 2-3 publications in 12-18 months. Path A (Tier-1 ambition) yields 0-1 publications in 24-36 months with high rejection risk.**

User must decide: prestige vs probability. The data supports Path B. Path C is defensible if institutional pressure requires Tier-1.

---

## Sources cited in audits

- [Codebook LLMs (Halterman & Keith, Political Analysis 2025)](https://www.cambridge.org/core/journals/political-analysis/article/codebook-llms-evaluating-llms-as-measurement-tools-for-political-science-concepts/7B323A0E47F782F2698A0AE849EA00DE)
- [Calderon et al. 2025 - LLM-human latent content analysis comparison, Nature Scientific Reports](https://www.nature.com/articles/s41598-025-96508-3)
- [Iglesias et al. 2025 - VADER+LIWC+ChatGPT comparison, JMIR Formative Research](https://formative.jmir.org/2025/1/e57395)
- [Multi-LLM Thematic Analysis with Dual Reliability Metrics, arXiv 2512.20352 (Dec 2025)](https://arxiv.org/abs/2512.20352)
- [Rating Roulette: Self-Inconsistency in LLM-As-A-Judge, EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.1361.pdf)
- [Bestvater & Monroe 2023, Sentiment is Not Stance, Political Analysis](https://www.cambridge.org/core/journals/political-analysis/article/sentiment-is-not-stance-targetaware-opinion-classification-for-political-text-analysis/743A9DD62DF3F2F448E199BDD1C37C8D)
- [Survivors, Complainers, Borderliners (arXiv 2509.16831, Wang et al. 2025)](https://arxiv.org/pdf/2509.16831)
- [Common Method Bias Annual Review 2024](https://www.annualreviews.org/content/journals/10.1146/annurev-orgpsych-110721-040030)
- [Trainee Reliance on PSLF (PMC8648921, 2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8648921/)
- [The MOHELA Papers (SBPC, 2024)](https://protectborrowers.org/wp-content/uploads/2024/02/MOHELA-Papers-Report.pdf)
- [Senate Banking MOHELA Hearing 2024](https://www.banking.senate.gov/hearings/mohelas-performance-as-a-student-loan-servicer)
- [Agarwal 2015, AER, "An Empirical Model of the Medical Match"](https://economics.mit.edu/sites/default/files/publications/aer_agarwal2015.pdf)
- [Pattar et al. 2025, JAMA Network Open](https://jamanetwork.com/journals/jamanetworkopen/articlepdf/2836552/pattar_2025_oi_250642_1752166550.63188.pdf)
- [Health Affairs Brief: Graduate Medical Education](https://www.healthaffairs.org/content/briefs/graduate-medical-education) - shows HA scope is GME funding/governance, NOT match dynamics
- [JAMA Health Forum 2025 Year in Review](https://jamanetwork.com/journals/jama-health-forum/fullarticle/2846549)
- [Stay Tuned: LLMs for Sentiment & Stance, Political Analysis](https://www.cambridge.org/core/journals/political-analysis/article/stay-tuned-improving-sentiment-analysis-and-stance-detection-using-large-language-models/2D8F121012D3D1CB2259B6DD5EE32D0D)
- [Heseltine & von Hohenberg 2024 - Research & Politics](https://journals.sagepub.com/doi/10.1177/20531680241236239) (NOT Political Analysis - this matters for venue framing)
- [Polarization & Sentiment in Reddit Foreign Aid Freeze (MDPI 2025)](https://www.mdpi.com/2673-5172/6/4/199)
- [Multi-Target User Stance Discovery (WASSA 2024)](https://aclanthology.org/2024.wassa-1.16.pdf)
- [LLM Validity: From Prompts to Constructs, arXiv 2506.16697](https://arxiv.org/pdf/2506.16697)
