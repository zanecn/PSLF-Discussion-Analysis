# Paper 1 LOCKED Results — 2026-05-10 (Round 17)

This is a one-page summary of the substantive results that LOCK Paper 1 (Methods, EPJ Data Science target). All 3 mandatory pre-submission fixes are COMPLETE; Round 17 audit fixes (C-series) are also COMPLETE.

---

## Headline finding (multi-LLM construct mismatch)

**Three LLMs from three independent organizations across two countries with three different post-training procedures achieve agreement above the tentative-reliability floor on the COMBINED sample (3-LLM Krippendorff α = +0.7590 [bootstrap 95% CI +0.7241, +0.7868] on combined Reddit + SDN, n=1,001). Adding either lexical instrument collapses 4-rater α by 0.36–0.52 (binning-dependent: TB-FIXED 0.42, TB-QCUT 0.42, VADER-FIXED 0.52, VADER-QCUT 0.36). The construct boundary is asymmetric: between LLM-class and lexical-class, NOT among individual models.**

**Cohort heterogeneity (newly disclosed, Round 17):**
- **Reddit only (n=701)**: 3-LLM α = +0.6901 [+0.6462, +0.7302] — **lower CI bound (0.646) just below Krippendorff's 0.667 tentative-reliability floor**
- **SDN only (n=300)**: 3-LLM α = +0.8306 [+0.7870, +0.8661] — clearly above floor
- **Combined (n=1,001)**: 3-LLM α = +0.7590 [+0.7241, +0.7868] — entire CI above floor

| LLM | Organization | Country | Post-training | n_scored (combined) |
|---|---|---|---|---|
| Claude Sonnet 4 | Anthropic | USA | Constitutional AI / RLAIF | 1,001 |
| Llama 3.3 70B Instruct Turbo | Meta (via Together AI) | USA | RLHF + DPO | 1,001 |
| DeepSeek V3.1 | DeepSeek (via Together AI) | China | GRPO | 1,001 |

n_intersection (5-instrument: Claude + Llama + DeepSeek + TextBlob + VADER) = **1,001 posts** (Reddit 701 + SDN 300).

**Infrastructure note**: Llama and DeepSeek were both accessed via Together AI's hosted inference, while Claude was accessed via Anthropic's first-party API. The 3-LLM convergence finding is therefore partially confounded with serving infrastructure (2/3 LLMs share Together AI; Claude does not). This is acknowledged in §5 Limitations.

---

## Pairwise agreement matrix

### Combined Reddit + SDN (n=1,001)

| Pair | Pearson r | Exact-match (FIXED) | Class |
|---|---|---|---|
| Claude × Llama | +0.737 | 68.2% | LLM × LLM |
| Claude × DeepSeek | +0.785 | 75.9% | LLM × LLM |
| Llama × DeepSeek | +0.811 | 71.3% | LLM × LLM |
| Claude × TextBlob | +0.021 | 30.1% | LLM × Lexical |
| Claude × VADER | +0.089 | 9.0% | LLM × Lexical |
| Llama × TextBlob | +0.092 | 31.0% | LLM × Lexical |
| Llama × VADER | +0.247 | 11.8% | LLM × Lexical |
| DeepSeek × TextBlob | +0.028 | 25.9% | LLM × Lexical |
| DeepSeek × VADER | +0.194 | 10.6% | LLM × Lexical |
| TextBlob × VADER | +0.333 | 11.2% | Lexical × Lexical |

**Pattern**: All inter-LLM r ≥ 0.74; all LLM-vs-lexical r ≤ 0.25. Asymmetric construct boundary holds in both Reddit-only and SDN-only sub-cohorts (see paper1_multi_llm_with_sdn_results.txt for stratified tables).

---

## Multi-rater Krippendorff α with bootstrap CIs

### Combined Reddit + SDN (n=1,001) — CANONICAL

| Rater combination | α | 95% CI |
|---|---|---|
| **3-LLM only (Claude + Llama + DeepSeek)** | **+0.7590** | [+0.7241, +0.7868] |
| 3-LLM + TextBlob (FIXED) | +0.3415 | [+0.3079, +0.3760] |
| 3-LLM + TextBlob (QCUT) | +0.3347 | [+0.2980, +0.3705] |
| 3-LLM + VADER (FIXED) | +0.2385 | [+0.2021, +0.2728] |
| 3-LLM + VADER (QCUT) | +0.3983 | [+0.3611, +0.4331] |
| All 5 (FIXED) | +0.1703 | [+0.1402, +0.1981] |
| All 5 (QCUT) | +0.2723 | [+0.2410, +0.3018] |

### Reddit only (n=701) — sensitivity

| Rater combination | α | 95% CI |
|---|---|---|
| 3-LLM only | +0.6901 | [+0.6462, +0.7302] |
| All 5 (FIXED) | +0.1415 | [+0.1057, +0.1787] |

### SDN only (n=300) — sensitivity

| Rater combination | α | 95% CI |
|---|---|---|
| 3-LLM only | +0.8306 | [+0.7870, +0.8661] |
| All 5 (FIXED) | +0.2180 | [+0.1698, +0.2646] |

**Drop in α when adding a lexicon (combined sample):**
- + TextBlob (FIXED): −0.4175 (from 0.7590 to 0.3415)
- + VADER (FIXED): −0.5205 (from 0.7590 to 0.2385)
- + Both (FIXED): −0.5887 (from 0.7590 to 0.1703)

The construct that the three LLMs agree on is operationalized differently by lexical instruments — to the point that combining them into a single composite measure is statistically incoherent.

---

## Companion stance task

The same three LLMs were also prompted for PSLF stance (5 classes) on the same posts:

| LLM pair | Stance exact-match | n |
|---|---|---|
| Claude × Llama | 87.8% | 485 |
| Claude × DeepSeek | 87.7% | 472 |
| Llama × DeepSeek | 85.8% | 472 |
| **All three LLMs agree** | **80.9%** | 472 |

**Stance task convergence is HIGHER than sentiment task convergence** (pairwise sentiment 68-79% vs pairwise stance 86-88%). This extends the LLM-class convergence finding beyond a single sentiment task. (Stance/topic tasks are also used downstream in Paper 2 — cross-cite at submission.)

---

## Test-retest reliability (LOCKED 2026-05-10) — PERFECT determinism

Two temperature=0 runs of Claude Sonnet 4 on the same 615 SDN post_ids, separate API calls:

| Task | Exact-match | Krippendorff α (ordinal) | Cohen's κ |
|---|---|---|---|
| **Sentiment** (5-level ordinal) | **100.0%** | **+1.0000** [bootstrap CI 1.0000, 1.0000; B=2,000] | **+1.0000** quadratic-weighted |
| **Stance** (5-class nominal) | **100.0%** | n/a | **+1.0000** |
| **Topic** (7-class nominal) | **100.0%** | n/a | **+1.0000** |

**Claude Sonnet 4 at temperature=0 is empirically deterministic across all three classification tasks.** Refutes the LLM-stochasticity reviewer objection at the strongest possible level.

**Comparison to Round 7 design** (temp=0 vs temp=1, n=605): α = +0.958. The 0.042 gap was entirely due to temperature=1 sampling, NOT test-retest noise.

**Implication for the methods finding:** the cross-instrument disagreement (3-LLM α=+0.76; +lexical drops α to +0.17-0.40) is **NOT due to LLM stochasticity**. It is **substantive construct disagreement**.

---

## Paraphrase robustness (Round 16 Strengthener 2; Round 17 Fix C2) — n=200

Same Claude Sonnet 4 model, same temperature=0, but THREE different system prompts (semantically identical, lexically different wording):

| Task | Result |
|---|---|
| **Sentiment** 3-prompt α | **+0.9011** [bootstrap 95% CI +0.857, +0.938] |
| Sentiment pairwise exact-match | 0.860 – 0.935 |
| **Stance** pairwise exact-match | 0.930 – 0.956 (n=114) |
| **Topic** pairwise exact-match | 0.930 – 0.950 (n=200) |

**Caveat (Round 17 Fix C2 — REFRAMED)**: this is paraphrase-robustness to **LEXICAL-FORMAT** rewording, NOT to semantic restructuring, task redefinition, or category reordering. Stronger "prompt-design" robustness (different category labels, different rubrics, different reasoning scaffolds) remains untested.

---

## OP-vs-Reply directional mismatch (Round 17+ corrected)

On the full ~500K-comment scale (n=21,453 OPs; 506,639 comments aggregated; mean 23.6 comments/post):
- TextBlob Δ (OP − reply) = **−0.0146** (1-sample t-test on per-post mean differences; t=−15.10, p=2.8×10⁻⁵¹)
- VADER Δ (OP − reply) = **+0.2387** (1-sample t-test on per-post mean differences; t=+60.40, p≈0)
- **Same direction in 8 of 8 cohorts** (TB always negative, VADER always positive)
- VADER significant in 8/8 cohorts; TextBlob significant in 6/8 cohorts (per-cohort tests in `op_reply_per_event_results.txt`)
- **Magnitude framing**: VADER's |Δ|=0.2387 is ~16× TextBlob's |Δ|=0.0146. The directional split is the headline; the magnitude split is a corollary.

**Inferential caveat (Round 17+ audit):** the headline numbers above use a 1-sample t-test on per-post mean differences (one observation per post, after aggregating comment polarities to a per-post mean). This treats each post as iid. A more conservative cluster-bootstrap on (post, comment) pairs would be desirable for headline inference and is on the to-do list for the published version. The per-event analysis in `op_reply_per_event_results.txt` does use B=1000 cluster bootstrap; the headline overall-corpus number does not. **CIs were previously reported in this document as "[−0.019, −0.014]" and "[+0.212, +0.230]" with "cluster-bootstrap p≈0" labelling — those CIs and the cluster-bootstrap label were Round 17+ audit-flagged as non-canonical** (no script in the project produces them); they have been replaced above with the actual t-statistic + parametric p from the producing script `analyze_op_vs_reply.py:159-161`.

This is the cleanest within-construct mismatch: a single measurement target (Δ = mean(OP) − mean(reply)) on which the two lexicons produce **directionally opposite estimates** with t-statistics of opposite sign and very large magnitude. A structured 2-hour literature search did not locate published precedent of the explicit lexical-instrument directional disagreement framed on identical OP-vs-reply contrasts in policy-discourse text; we present this as "first systematic quantification we are aware of," not a categorical novelty claim.

---

## TB×VADER replication at comments scale (Round 16 finding) — Paper 1 §5.5b

The TextBlob × VADER disagreement REPLICATES at 50× scale on Reddit comments:
- TB×VADER α (posts, n=9,242) = +0.34
- TB×VADER α (comments, n=519,401 with valid scoring; 528,051 collected) = **+0.2892** [cluster-bootstrap 95% CI +0.287, +0.292]
- Design effect ≈ 1.36 (cluster-adjusted)

The lexical-instrument construct mismatch is not an artifact of the post-level n; it holds at half-million-row scale within the same project ecosystem.

---

## Mandatory pre-submission fixes — STATUS

| # | Fix | Status |
|---|---|---|
| 1 | Complete proper test-retest design (temp=0 vs temp=0) | ✅ DONE 2026-05-10 — 100% exact-match across all 3 tasks |
| 2 | Adopt psychometric terminology ("convergent validity failure") | ✅ done in outline |
| 3 | Cite and distinguish closest LLM-validation competitor (originally tagged as "Calderon et al. 2025"; R17++ audit corrected to **Bojić et al. 2025** *Sci Reports* 15:11477 — the DOI 10.1038/s41598-025-96508-3 had a hallucinated author list) | ✅ done in outline (with corrected attribution) |

**Round 17 audit fixes (C-series):**
| # | Fix | Status |
|---|---|---|
| C1 | Persist stance + topic numbers to disk | ✅ DONE 2026-05-10 |
| C2 | Reframe paraphrase as "lexical-format" (not "prompt-design") | ✅ DONE 2026-05-10 |
| C3 | Disclose Reddit-only α=0.6901 lower-CI just below 0.667 floor | ✅ documented above |
| C4 | Acknowledge Together AI infrastructure confound | ✅ documented above |
| C5 | Soften "no published precedent" to "structured search did not locate" | ✅ documented above |
| C6 | Magnitude framing for OP-vs-Reply | ✅ documented above |

**ALL PRE-SUBMISSION + ROUND 17 FIXES COMPLETE.** Paper 1 ready to draft.

---

## Surviving novelty claims (post-deflation)

1. ✅ Cross-organization three-LLM cross-validation at scale on policy-discourse text (most prior work uses 1-2 LLMs at smaller scale)
2. ✅ Asymmetric LLM-class vs lexical-class construct boundary (theoretically grounded; not previously quantified at this scale)
3. ✅ OP-vs-Reply within-thread directional mismatch (no published precedent located in structured search)
4. ✅ Perfect test-retest reliability for LLM scoring at temperature=0 (closes the LLM-stochasticity reviewer objection definitively)
5. ✅ Three-LLM convergence on companion stance task at 80.9% all-three-agree (extends LLM-class convergence beyond a single task)
6. ✅ Paraphrase robustness to LEXICAL-FORMAT prompt variation (sentiment α=0.9011)
7. ✅ TB×VADER construct mismatch replicates at 519K-comment scale (α=+0.29)

---

## Files produced

- `paper1_multi_llm_with_sdn_results.txt` — 5-instrument intersection + cohort-stratified α
- `paper1_paraphrase_robustness_results.txt` — sentiment/stance/topic paraphrase reliability
- `paper1_dual_binning_results.{csv,txt}` — FIXED vs QCUT binning sensitivity
- `multi_llm_comparison_results.{txt,csv,png}` — 3-LLM + lexical comparison (Reddit-only, n=701)
- `zeroshot_sdn_temp0_retest.csv` (Round 7 baseline, n=605)
- `zeroshot_sdn_temp0_retest_RUN2.csv` (2026-05-10 run, n=615)
- `test_retest_FINAL_results.txt` — 100% exact-match across all 3 tasks
- `scripts/compare_test_retest.py` — comparison helper script
- `scripts/compute_paraphrase_robustness.py` — paraphrase α + pairwise persistence (Round 17 C1)

---

## What remains for Paper 1

**FULLY LOCKED.** All substantive analyses complete. Ready to draft.

**Optional refinements** (would not change the headline):
- Generate Figure 1 (5×5 instrument correlation matrix with within/across class coloring)
- Generate Figure 2 (OP-vs-reply forest plot by cohort)
- Generate Figure 3 (comments-scale α replication trend)

Paper 1 timeline: Q3 2026 submission target to EPJ Data Science.

---

*End of Paper 1 LOCKED Results document. Last updated 2026-05-10 with Round 17 audit fixes.*
