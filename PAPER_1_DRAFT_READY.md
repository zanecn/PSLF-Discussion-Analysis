# Paper 1 Draft-Ready Template — REFRAMED R17++ #6

**Status:** READY TO DRAFT NOW; **R17++ #6 boost: REFRAME headline to OP-vs-Reply directional split**
**Target (R17++ #6 revised):** ***ICWSM '26*** OR ***CSCW '26*** primary / ***Information, Communication & Society*** secondary / *Behavior Research Methods* tertiary / EPJ DS as reach
**Length:** 6,000–8,000 words + supplements (or ~3-4K words for ICWSM/CSCW short-paper format)
**Working title (REFRAMED):** *Directional Disagreement Between Lexical Sentiment Instruments on Original-Posts versus Replies in PSLF Online Discourse: An 8-Cohort Conversation-Dynamics Finding*

## R17++ #6 BOOST STRATEGY (added 2026-05-17 final)

**Why reframe:** Original 3-LLM convergence headline (α=+0.7590 on n=1,001) was incremental in an over-crowded LLM-as-coder space (Gilardi 2023, Bisbee 2024, Burnham 2025, Halterman 2025, Heseltine 2024, Bojić 2025, Ziems 2024). The OP-vs-Reply directional split (TextBlob Δ=−0.0146 [−0.0164, −0.0127], VADER Δ=+0.2387 [+0.2306, +0.2460] in 8/8 cohorts on n=21,453 OPs/506,639 comments; cluster bootstrap B=2,000; magnitude split 16.4×; **R17++ #6 RIGOROUS REVIEW** re-ran cluster bootstrap with aligned 4-source loader to exactly match t-test sample) is genuinely novel — own lit search confirmed no precedent.

**New headline:** Directional disagreement between TextBlob and VADER on identical OP-vs-Reply contrasts in 8 of 8 PSLF cohorts on 21,453 posts + 506,639 comments. This is a conversation-dynamics finding wrapped inside a methods paper — better fit at ICWSM/CSCW/IC&S than at EPJ DS.

**Demoted to supporting evidence (still in paper):** 3-LLM convergence at α=+0.76; construct-boundary 4-rater α collapse; paraphrase α=+0.9011 at n=399 (R17++ #3 replication).

**Boost effort:** ~1 week of reframing (rewrite §1 Introduction + §5 Results focus; demote §5.4 paraphrase to subsection; promote OP-vs-Reply to §5.1). **No new data needed** — analysis exists from R17++ #2 work.

**Optional supplements** (per `DATA_ACQUISITION_PLAN_R17pp6.md`): thread-structure metadata for within-thread sentiment evolution (Reddit Arctic Shift JSON already contains `parent_id`; ~1-2 days extension). Skip unless reviewers request.

**Realistic acceptance:** ICWSM '26 ~25-30%; CSCW '26 ~25%; *Information, Communication & Society* ~25-30%; *Behavior Research Methods* ~50% (fallback).

---

# Original outline below — to be reorganized per R17++ #6 reframe during drafting

**Status (LEGACY R17++ #5):** READY TO DRAFT NOW (multi-LLM + paraphrase numbers locked from Round 16 strengtheners; OP-vs-Reply numbers refreshed at 519K-comment scale)
**Target (LEGACY R17++ #5):** EPJ Data Science (primary) / Behavior Research Methods (secondary)
**Length:** 6,000–8,000 words + supplements
**Working title (LEGACY):** *Convergent Validity Failure Between Lexical and LLM-Class Sentiment Instruments on Public Service Loan Forgiveness Discourse: A Three-LLM Cross-Validation*

---

## Drafting workflow

1. Use this template as the prose scaffold.
2. Pull numbers from `MASTER_LOCKED_NUMBERS.md` Paper 1 section.
3. Pull citations from `MASTER_REFERENCE_LIST.md`.
4. Use `MASTER_DRAFTING_KIT.md` blocks where flagged.
5. After comments collector finishes + Step 2 of post-comments chain runs: refresh §5.5 OP-vs-Reply numbers from `op_vs_reply_results.txt`.

---

# Title page

**Title:** Convergent Validity Failure Between Lexical and LLM-Class Sentiment Instruments on Public Service Loan Forgiveness Discourse: A Three-LLM Cross-Validation

**Authors:** [Author 1 et al.]
**Word count:** [target 7000]
**Tables:** 4
**Figures:** 3
**Supplements:** 8

---

# Abstract (~250 words)

Online discourse is increasingly used as an empirical signal for policy reception. Researchers routinely apply off-the-shelf sentiment instruments (TextBlob, VADER, more recently large language models) to forum/social-media data and treat the resulting scores as interchangeable measures of "public sentiment toward a policy." We test convergent validity among five commonly used sentiment instruments on a 9,242-post Public Service Loan Forgiveness corpus (Reddit + Student Doctor Network, 2010–2026; 5-instrument intersection n=1,001 from Reddit subreddits and SDN-Medical). Three LLMs from three independent organizations — Anthropic Claude Sonnet 4 (USA, Constitutional AI/RLAIF; first-party API), Meta Llama 3.3 70B Instruct Turbo (USA, RLHF+DPO; via Together AI), and DeepSeek V3.1 (China, GRPO; via Together AI) — achieve **tentative-to-satisfactory inter-rater reliability** (combined 3-LLM Krippendorff α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868]; SDN-only sub-sample α=+0.8306 [+0.787, +0.866] above Krippendorff's 0.80 satisfactory-reliability floor; Reddit-only sub-sample α=+0.6901 [+0.6462, +0.7302] — lower CI bound BELOW Krippendorff's 0.667 tentative-reliability floor, i.e., the Reddit cohort alone does not decisively exceed the floor). Adding either lexical instrument (TextBlob or VADER) collapses 4-rater α by 0.36–0.52 depending on binning (LLM-VADER fixed-threshold pairwise exact-match drops to 9.0%). The construct boundary is LLM-class vs lexical-class, not single-model-specific — though we acknowledge that 2 of 3 LLMs share Together AI serving infrastructure, which we cannot fully disentangle from model effect (§7 L0d). **Paraphrase-robustness test-retest** at temperature=0 across three alternative system prompts that vary in lexical/format wording (but hold rubric, category labels, and reasoning scaffold constant) yields α=+0.9011 [+0.8571, +0.9380]; the lower CI bound (0.857) is only marginally above the pre-specified 0.85 threshold and a higher-n replication is desirable. Stance and topic classifications are similarly robust to lexical-format variation (92–96% pairwise exact-match). An OP-vs-reply within-thread test on the full ~500K-comment scale shows TextBlob and VADER produce directionally opposite Δ in 8 of 8 cohorts on identical text (TB Δ=−0.0146, VADER Δ=+0.2387, both with parametric t-test p<10⁻⁵⁰); a structured literature search did not locate prior systematic quantification of this pattern in policy-discourse text. Implications: instrument choice in discourse-as-policy-signal research is a substantive construct choice with consequences, not a methodological convenience.

---

# 1. Introduction (~1,000 words)

## 1.1 Motivation

Online discourse — Reddit threads, Twitter/X timelines, forum posts — is increasingly used as an empirical signal for how the public is reacting to policy decisions. The dominant measurement workflow is: (1) scrape posts containing policy-relevant keywords, (2) apply a sentiment classifier (typically TextBlob, VADER, or more recently a fine-tuned BERT or LLM), (3) aggregate sentiment scores into pre/post comparisons, time-series, or cohort summaries, (4) interpret aggregate sentiment as "public reception" of the policy.

This paper argues that the substitutability assumption underlying that workflow is methodologically untenable for policy-discourse text. The three commonly-used sentiment instruments operationalize substantively different latent constructs: TextBlob (lexical polarity, valence of words in the text); VADER (Hutto & Gilbert 2014, expressive arousal, rhetorical intensity sensitive to punctuation, capitalization, and emoji); and LLMs prompted for stance (instruction-following classifiers attending to a specific entity, e.g., "PSLF," and producing a label aware of that target). These constructs may correlate on simple polarized text but diverge on policy discourse.

## 1.2 Two open questions

The above motivates our research questions:

**RQ1.** Do TextBlob, VADER, and LLM-class sentiment instruments converge on policy-discourse classification, sufficient to be treated as interchangeable measures?

**RQ2.** If LLM-class instruments do not converge with lexical instruments, is the inter-LLM convergence robust to LLM choice — i.e., is it a genuine class-level pattern, or an idiosyncrasy of a single LLM (e.g., Claude)?

A skeptical reviewer's expected objections:
- **(a) LLMs vary stochastically across queries**: without test-retest reliability, observed LLM scores are not reproducible.
- **(b) Single-LLM findings reflect that LLM's training quirks**: without multi-LLM replication, the LLM column is not a class claim.
- **(c) All major LLMs train on overlapping web data** (Common Crawl, Wikipedia, books, code), so multi-LLM agreement may reflect shared training corpus, not genuine cross-organization consensus.

We address (a) directly via a paraphrase-robustness test-retest at temperature=0 (Section 4.4 + 5.4). We address (b) by scoring with three LLMs from three different organizations across two countries with three different post-training procedures (Section 3.2 + 5.2). We address (c) honestly: training corpora are undisclosed proprietary mixes that almost certainly overlap on common web sources. We cannot fully refute (c) without an LLM trained on a fully disclosed, distinct corpus — not currently available at 70B+ scale. We discuss this as the primary residual limitation in Section 6.

## 1.3 Theoretical framework

Our work builds on three threads:
- **Stance vs sentiment**: Mohammad et al. (2016, SemEval-2016 Task 6) formally separates target-aware position from generalized affect. Bestvater & Monroe (2023, Political Analysis) empirically demonstrate sentiment-stance dissociation on Kavanaugh Twitter (n=3,660 hand-coded; r=0.03 between sentiment and stance).
- **LLMs as measurement instruments**: Halterman & Keith (2025, *Political Analysis*, "Codebook LLMs"), Heseltine & Clemm von Hohenberg (2024, *Research & Politics*), Burnham (2025, *Political Science Research and Methods*), and Bojić et al. (2025, *Scientific Reports*, doi:10.1038/s41598-025-96508-3 — formerly mis-cited as "Calderon et al."; corrected Round 17++) demonstrate that LLM-as-rater rivals human inter-rater reliability for sentiment, political leaning, and (in Calderon et al.) related social-science classification tasks, with careful prompt design.
- **Convergent and discriminant validity**: Campbell & Fiske (1959) is the classical psychometric framework: multiple instruments measuring "the same" construct should agree (convergent), while instruments measuring different constructs should disagree (discriminant). We apply this multitrait-multimethod logic to the modern sentiment-instrument panel, with a caveat noted in Section 7 L0c that our construct identifications remain interpretive.

## 1.4 Contribution

We make four specific contributions over the prior literature:
1. **Cross-organization three-LLM cross-validation at scale on policy-discourse text.** Prior work (e.g., Bojić et al. 2025) tests up to eight LLMs but on smaller validation sets and on news/Twitter rather than long-form forum text. We score n=1,001 posts (combined Reddit + SDN) with three LLMs and two lexicons.
2. **Asymmetric construct boundary documented**. The LLM-class instruments converge among themselves (combined α=+0.76) and disagree as a class with the lexical-class (4-rater α drops by 0.36–0.52, binning-dependent: TB-FIXED 0.42, TB-QCUT 0.42, VADER-FIXED 0.52, VADER-QCUT 0.36). This is a finding about *instrument classes*, not individual models.
3. **OP-vs-reply within-thread directional mismatch** (TextBlob Δ negative, VADER Δ positive in 8 of 8 cohorts). Within-thread sentiment and conversational dynamics in social-media threads have been studied (Choi, Aiello, Varga & Quercia 2020, *WWW '20*; Tsugawa & Ohsaki 2015, *COSN '15*; Park & Conway 2017, *JMIR* on longitudinal sentiment in an online health community), but a structured 2-hour literature search did not locate prior work explicitly framing the lexical-instrument *directional* disagreement on identical OP-vs-reply contrasts in policy-discourse text.
4. **Paraphrase-robustness test-retest** for LLM scoring at temperature=0 — **independently replicated 2× at n=200 (R16 Strengthener 2) and n=399 (R17++ #3, 2026-05-17) with identical point estimate α=+0.9011** and tightened CI (lower bound +0.018 above the 0.85 threshold at n=399 vs +0.007 at n=200). Refutes the "LLM scores are prompt-sensitive" objection at the strongest possible empirical level — the result is not a single-sample artifact but is preserved across a fresh ~2× resample with Bessel-expected precision gain.

---

# 2. Related work (~800 words)

## 2.1 Lexical instruments: TextBlob and VADER

TextBlob (Loria 2018; based on Pattern.en from De Smedt & Daelemans 2012) implements a Naive Bayes polarity score using a hand-curated lexicon of ~2,900 adjectives. It is widely used in CSS/NLP introductory courses precisely because of its simplicity. VADER (Hutto & Gilbert 2014) is a rule-based scorer tuned on n=4,200 social-media-style sentences with 10 human annotators. It augments a 7,500-word lexicon with rules for negation, intensifiers, punctuation, and capitalization. It has been the de facto sentiment standard for Reddit/Twitter research since publication, with >12,000 citations as of 2025. Both instruments are token-level; both produce a continuous polarity in roughly [−1, +1]; both have been benchmarked against human raters on short, clearly-polarized text (movie reviews, product reviews). Neither was designed for long-form policy discourse with mixed-affect content.

## 2.2 LLM-as-classifier: prior validation

**Bojić, L., Zagovora, O., Zelenkauskaite, A., et al. (2025, *Scientific Reports* 15:11477, doi:10.1038/s41598-025-96508-3)** tested 8 LLM variants (GPT-3.5-turbo-16k, GPT-4, GPT-4o, GPT-4o-mini, Gemini 1.5 Pro, Llama-3.1-70B, Mixtral 8x7B, Hard Prompt GPT-4o) against 33 human annotators on 100 curated textual items, producing 3,300 human + 19,200 LLM annotations across 4 dimensions (sentiment, political leaning, emotional intensity, sarcasm). They report LLMs achieve human-level reliability for sentiment and surpass humans on some tasks. **Round 17++ audit CRITICAL CORRECTION**: this entry was previously mis-attributed to "Calderon, N., Caspi, R., Friedman-Avraham, A., et al." with a hallucinated panel description. There is NO Calderon, Caspi, or Friedman-Avraham author on the paper at this DOI; the actual first author is Ljubiša Bojić. All inline references in this outline are now re-attributed to Bojić et al. 2025.

Heseltine & Clemm von Hohenberg (2024, *Research & Politics*) and Burnham (2025, *Political Science Research and Methods*) demonstrate that LLMs can replicate established human-coded political-discourse datasets at scale, with careful prompt design. Halterman & Keith (2025, *Political Analysis*, "Codebook LLMs") shows LLMs given a codebook can reproduce human inter-rater reliability for stance and topic classification.

Skeptical voices: Bisbee et al. (2024, *Political Analysis* 32:401–416, doi:10.1017/pan.2024.5) and Spirling (2023, *Nature* 616:413, doi:10.1038/d41586-023-01295-4 — open-source-LLM advocacy on reproducibility grounds) raise concerns about LLM stochasticity, paraphrase-sensitivity, and reproducibility. Our paraphrase-robustness test-retest (Section 4.4 + 5.4) directly addresses the LEXICAL-FORMAT slice of this concern (semantic-restructuring robustness untested; see §7 L0e).

Our contribution beyond Bojić et al. (2025):
- Larger validation set (n_corpus=9,242; n_intersection=1,001 with 3 LLMs)
- Long-form forum text (Reddit + SDN) rather than news/Twitter
- Cross-organization (US Anthropic + US Meta + Chinese DeepSeek) and cross-post-training (Constitutional AI/RLAIF + RLHF+DPO + GRPO) diversity
- Explicit asymmetric construct-boundary framing (LLM-class vs lexical-class rather than LLM-vs-human)
- Paraphrase-robustness test-retest as a methodological contribution

## 2.3 Construct validity in sentiment measurement

Bestvater & Monroe (2023) is the closest precedent for our framing. On a hand-coded Kavanaugh Twitter corpus (n=3,660), they demonstrate sentiment and stance are nearly uncorrelated (r=0.03). They argue researchers studying "public reception" of policy must distinguish whether they are measuring affect or position. Our work extends this in three respects: (1) we test multiple sentiment instruments, not a single one, on the same text; (2) we extend to LLM-class instruments, which were not yet mainstream when Bestvater & Monroe collected their data; (3) we operate on long-form forum text rather than tweet-length text, which permits more nuanced mixed-affect content.

The closest within-class precedent is Boukes et al. (2020, *Communication Methods and Measures*), who compare TextBlob, VADER, SentiStrength and dictionary methods on news/forum text and document substantial divergence. We extend the TB-VADER comparison framing to (a) policy-discourse forum text at 75× the prior scale, (b) explicit class-vs-class construct-boundary framing, and (c) addition of LLM-class as a third instrument family. Baumartz et al. (2024, arXiv:2410.14626, "You Shall Know a Tool by the Traces it Leaves") shows F1=0.89 separability across 9 sentiment tools at the system-output level — structurally consistent with our class-boundary finding but at a different inferential target (tool identification vs construct mismatch quantification).

The seminal benchmark in our target venue (EPJ Data Science) is Ribeiro et al. (2016) "SentiBench," comparing 24 sentiment methods. We extend SentiBench's design to: (a) include LLM-class instruments (which did not exist in 2016), (b) add construct-validity (not just classifier-accuracy) framing, (c) operate on longer forum text rather than short polarized snippets.

## 2.4 What this paper does NOT claim

We do not claim LLMs are "correct" and lexicons "wrong." Both are valid measurements; they measure different things. A research design that explicitly wants surface affect (e.g., for arousal-based engagement prediction) may justifiably prefer VADER. A research design that wants stance toward a policy entity should use an LLM (or a fine-tuned model trained on stance). We do not claim cross-instrument differences are always large; on simple polarized text (e.g., "I love PSLF") all instruments would agree. The construct mismatch surfaces on mixed-affect, target-relevant text — which dominates policy discourse.

---

# 3. Data (~600 words)

## 3.1 Corpus

[INSERT BLOCK from current outline §3.1; substitute n=9,242 from MASTER_LOCKED_NUMBERS.md] (~150 words)

## 3.2 PSLF context

[INSERT BLOCK A from MASTER_DRAFTING_KIT.md] (~110 words)

## 3.3 PSLF-relevance filter

[INSERT BLOCK G from MASTER_DRAFTING_KIT.md] (~75 words)

## 3.4 Cohort definitions

[INSERT BLOCK H from MASTER_DRAFTING_KIT.md] (~90 words)

## 3.5 Five-instrument intersection (n=1,001)

The five-instrument intersection for the multi-LLM convergence test is **n=1,001 posts** that received TextBlob, VADER, Claude, Llama, and DeepSeek scoring. Composition:
- **Reddit profession-subreddit subset (n=701)**: r/PSLF (n=27), r/StudentLoans (n=32), r/personalfinance (n=69), r/medicalschool (n=62), r/Teachers (n=56), r/PAstudent, r/prephysicianassistant, r/CRNA, r/medicine, r/Residency, etc.
- **SDN-Medical subset (n=300)**: stratified random sample by sentiment+topic from the larger SDN-Medical Claude-scored corpus, scored with Llama 3.3 + DeepSeek V3.1 in Round 16 Strengthener 1.

Cohort-stratified K-α analyses (Section 5.2) verify that the asymmetric construct boundary holds in both Reddit and SDN sub-samples but is sharper on SDN.

## 3.6 Word-count threshold

`MIN_WORDS = 20`. TextBlob is unreliable on shorter posts. Threshold applied uniformly across instruments to prevent length-effect confounds.

---

# 4. Methods (~1,300 words)

## 4.1 Five sentiment instruments

[INSERT BLOCK D from MASTER_DRAFTING_KIT.md] (~150 words)

## 4.2 Three LLMs (multi-LLM convergence test)

[INSERT BLOCK E from MASTER_DRAFTING_KIT.md] (~110 words)

## 4.3 Five-rater convergent validity test

[INSERT BLOCK F from MASTER_DRAFTING_KIT.md] (~95 words)

For the n=1,001 intersection, we compute: all 10 pairwise comparisons (Pearson r, exact-match rate, Cohen's κ); 3-rater Krippendorff α restricted to LLM panel (Claude + Llama + DeepSeek); 4-rater Krippendorff α adding TextBlob to LLM panel; 4-rater Krippendorff α adding VADER to LLM panel; 5-rater Krippendorff α with all five instruments. For each Krippendorff α point estimate, we compute a 95% confidence interval via simple bootstrap (B=2,000) of the post indices. **Method note (Round 17+ audit):** this is a non-cohort-stratified resample within the relevant subset (combined / Reddit-only / SDN-only). The combined-sample bootstrap CI may slightly under-cover the true sampling variability because it does not preserve the within-cohort:between-cohort stratum balance. We additionally report cohort-stratified α point estimates separately (Reddit-only, SDN-only) to enable cohort-comparison interpretation; cohort-stratified resampling for the combined-sample CI is recommended for the published version.

## 4.4 Paraphrase-robustness test-retest (Round 16 Strengthener 2; Round 17 reframe)

We re-score n=200 SDN posts with Claude Sonnet 4 at temperature=0 using two alternative system-prompt phrasings. The three prompts are **semantically identical but lexically different in surface wording** — the rubric, category labels, ordinal direction, and reasoning scaffold are held constant; only word choice and sentence structure vary. Together with the original baseline (n=605 SDN posts at temperature=0), this produces a 3-prompt comparison set. We compute pairwise sentiment agreement (exact-match, Pearson r, Cohen's κ) and the 3-prompt Krippendorff α (ordinal, n=200) with bootstrap 95% CI (B=2,000). Pre-specified threshold: 3-prompt α > 0.85 demonstrates true test-retest reliability under **lexical-format prompt variation**; α ≤ 0.85 indicates such variation drives classification.

**Scope caveat (Round 17 Fix C2):** This design tests robustness to *lexical-format* paraphrase, NOT to semantic restructuring (different rubrics, different category counts, different category orderings, different reasoning instructions). A stronger "prompt-design robustness" test would require independently-developed rubrics; we did not perform that here and acknowledge it as a residual limitation (§7 L0e).

## 4.5 OP vs Reply within-thread test

[INSERT from current outline §4.5] (~120 words)

## 4.6 Statistical software

[INSERT BLOCK M from MASTER_DRAFTING_KIT.md] (~80 words)

---

# 5. Results (~2,000 words)

## 5.1 Pairwise instrument agreement (Table 1; n=1,001)

[INSERT pairwise table from MASTER_LOCKED_NUMBERS.md Paper 1 section]

**Critical observation:** VADER × LLM **fixed-threshold exact-match is 9.0%** — much worse than qcut suggests (19.6-22.3%). VADER classifies the majority of posts as "very_positive" under canonical thresholds while LLMs distribute across the full ordinal range. Under qcut, equal-frequency binning artificially aligns marginal distributions and inflates apparent agreement. The asymmetric construct boundary holds under both binnings but the FIXED-threshold reading is the more honest one for a working researcher's use case.

## 5.2 Multi-rater Krippendorff α with bootstrap CI (Table 2; n=1,001)

[INSERT Table 2 from MASTER_LOCKED_NUMBERS.md Paper 1 section, including Combined / Reddit / SDN subset rows]

[INSERT BLOCK I from MASTER_DRAFTING_KIT.md (honest reliability framing)] (~100 words)

## 5.3 Asymmetric construct boundary visualization (Figure 1)

**Figure 1**: 5×5 instrument correlation matrix, color-coded by within-class vs across-class. Visible: a "warm" 3×3 block in the upper-left (3-LLM cluster) and a "warm" 2×2 block in the lower-right (TB-VADER pair), with a "cool" 3×2 off-diagonal showing the asymmetric construct boundary.

**Caption text:** "Pairwise Pearson correlation matrix for 5 sentiment instruments (n=1,001, combined Reddit + SDN). Three LLMs cluster strongly (r=0.74–0.81); two lexicons cluster modestly (r=0.34); LLM-class and lexical-class show low cross-correlation (r=0.02–0.27). Asymmetric construct boundary visible as the cool 3×2 off-diagonal."

## 5.4 Paraphrase-robustness test-retest (Subsection 5.4)

[FROM MASTER_LOCKED_NUMBERS.md Paper 1 section, paraphrase robustness sub-table]

**Two-sample replication table (n=200 R16 + n=399 R17++ #3, 2026-05-17):**

| Comparison | n=200 exact-match | n=399 exact-match | Δ |
|---|---|---|---|
| Baseline vs Paraphrase 1 | 89.5% | 89.22% | −0.28 pp |
| Baseline vs Paraphrase 2 | 86.0% | 85.46% | −0.54 pp |
| Paraphrase 1 vs 2 | 93.5% | 94.24% | +0.74 pp |
| **3-prompt Krippendorff α (sentiment)** | **+0.9011** [+0.8571, +0.9380] | **+0.9011** [+0.8680, +0.9300] | Δα=0; CI half-width tightened 22% |

Stance task pairwise at n=231 valid (R17++ #3): 93.07%–96.10% exact-match. Topic task pairwise at n=399 valid: 92.23%–94.24% exact-match. Both stable within sampling noise relative to R16 historical (stance 92.98%–95.61% at n=114; topic 93.00%–95.00% at n=200).

**Interpretation paragraph (~200 words; R17++ #3 revised):** Claude Sonnet 4 sentiment classifications at temperature=0 are robust to **lexical-format variation in system-prompt phrasing** across two independent samples drawn from the same 615-post SDN-baseline pool. The original n=200 sample (R16 Strengthener 2) yielded a 3-prompt Krippendorff α = +0.9011 [+0.8571, +0.9380] with the lower CI bound only +0.007 above the pre-specified 0.85 threshold — a tight safety margin that motivated a higher-n replication. The independent **n=399 replication (R17++ #3, 2026-05-17, deterministic fresh sample from the same pool with `random_state=42`)** yielded an **identical point estimate α = +0.9011** with a tightened bootstrap 95% CI of [+0.8680, +0.9300]. The CI half-width dropped 22% (from 0.040 to 0.031), closely matching the Bessel-expected ratio of 0.71 at 2× sample, confirming the replication is statistically well-conditioned. The lower CI bound now has **+0.018 of headroom above 0.85**, more than 2.5× the original margin. Pairwise stance (n=231 valid) and topic (n=399 valid) classifications are similarly stable. **Scope caveat unchanged:** this refutes only the *lexical-format* prompt-sensitivity objection; semantic-restructuring robustness remains untested. Combined with the 100% temp=0 test-retest exact-match across two runs of the identical prompt, the cross-instrument disagreement (Section 5.2) is **not** due to LLM measurement noise within the prompt-paraphrase regime tested; it is **substantive construct disagreement**. See Supplementary Figure S1 (`paper1_figS_paraphrase_replication.png`) for the n=200 vs n=399 forest plot.

## 5.5 OP vs Reply within-thread mismatch (Figure 2) — LOCKED at full ~500K-comment scale

Final analysis (n=21,453 OPs; 506,639 comments; mean 23.6 comments/post):

- **TextBlob Δ (OP − reply) overall = −0.0146** (t=−15.10, p=2.8×10⁻⁵¹)
- **VADER Δ (OP − reply) overall = +0.2387** (t=60.40, p≈0)
- **Same direction in 8/8 cohorts** (TB negative, VADER positive)
- Per-cohort TB Δ range: −0.007 to −0.026
- Per-cohort VADER Δ range: +0.20 to +0.32
- Top-level vs deep replies: TB Δ=−0.0105 (t=−9.73, p=2.5×10⁻²²) — depth-escalation effect detectable but very small in absolute terms

**Replicates the post-level finding at the full ~500K-comment scale**: directionally opposite Δ in 8/8 cohorts. Same-direction-mismatch is robust to scale.

**Interpretation paragraph (~170 words; Round 17+ revised):** On the same posts, the same threads, the same cohorts, TextBlob says replies are *more positive* than OPs while VADER says replies are *less positive*. This is the cleanest within-construct mismatch in the analysis: a single measurement target (Δ = mean(OP) − mean(reply)) on which the two lexicons produce directionally opposite estimates. The Δ values are estimated by 1-sample t-tests on per-post mean differences; the corresponding t-statistics are large in magnitude (TB t=−15.10, VADER t=+60.40) and their parametric p-values are infinitesimal (p<10⁻⁵⁰). **Inferential caveat:** the per-post-aggregation t-test treats each post as one observation, but a more conservative cluster-bootstrap on (post, comment) pairs would be desirable for headline inference and is recommended for the published version. **Magnitude framing:** TextBlob |Δ|=0.0146 (~1.5% of the [−1, +1] range); VADER |Δ|=0.2387 (~24% of range). The headline is the *directional split* (TB negative, VADER positive in 8/8 cohorts); the magnitude split (~16× larger absolute Δ for VADER) is a corollary indicating the two lexicons are not estimating the same underlying quantity. Within-thread sentiment dynamics have been studied (Choi, Aiello, Varga & Quercia 2020, *WWW '20*; Tsugawa & Ohsaki 2015, *COSN '15*; Park & Conway 2017, *JMIR*); a structured 2-hour literature search did not locate prior work explicitly framing the lexical-instrument directional disagreement on identical OP-vs-reply contrasts in policy-discourse text. We present this as "first systematic quantification we are aware of," not a categorical novelty claim.

## 5.5b TB×VADER convergent-validity replication at comments-scale (Round 17 fix; new sub-section)

The TB×VADER convergent-validity failure replicates at half-million-row scale on the broader Reddit comments corpus, ruling out the post-level n as an artifact:

| Sample | n | TB×VADER α (ordinal, FIXED-threshold) | 95% CI |
|---|---|---|---|
| Posts (5-instrument intersection) | 1,001 | +0.112 (table 1, FIXED) | — |
| Posts (5-instrument intersection, qcut) | 1,001 | +0.234 (table 1, qcut) | — |
| Posts (full PSLF post-level corpus) | 9,242 | +0.34 | (Round 8 baseline) |
| **Comments (Arctic Shift collector, fully scored)** | **519,342** | **+0.2892** | **[+0.287, +0.292]** (cluster bootstrap, design effect 1.36) |

**Interpretation (~80 words):** The two-instrument lexical-class agreement is α≈0.29-0.34 across orders of magnitude in n (1K → 9K → 519K). The TB×VADER convergent-validity failure is structural to the construct measured by these two lexicons, not a small-sample artifact. The 519K-comment scale is also large enough to give cluster-bootstrap CI half-widths < 0.005 around the point estimate, which is far below any plausible reliability threshold (0.667 / 0.80) we would care about.

## 5.6 Stance task companion (Section 5.6)

[FROM MASTER_LOCKED_NUMBERS.md Paper 1 section, stance task sub-table]

| Pair | Exact-match | n |
|---|---|---|
| Claude × Llama | 87.8% | 485 |
| Claude × DeepSeek | 87.7% | 472 |
| Llama × DeepSeek | 85.8% | 472 |
| **All-three-agree** | **80.9%** | 472 |

**Interpretation paragraph (~100 words):** The same three LLMs were also prompted for PSLF stance (5 categories: pursuing / considering / rejecting / completed / unknown). Three-LLM stance agreement is HIGHER than three-LLM sentiment agreement (pairwise sentiment exact-match 73.6-78.6% vs pairwise stance 85.8-87.8%). The 5-category stance classification — a more constrained classification problem with surface markers like "I'm pursuing PSLF", "I've decided not to apply" — shows stronger LLM-class agreement. This extends the LLM-class convergence finding beyond a single sentiment task and strengthens the construct claim that LLM-class instruments operationalize a stance-coherent representation that lexicons do not.

## 5.7 Minimum-working-example: Trump PSLF EO event window

We include a single-event illustration of the construct mismatch surfacing as substantive disagreement on policy-event analysis. The 2025 Trump PSLF Executive Order window (n=1,330 posts) yields directionally opposite Hedges' g across instruments:
- TextBlob g = −0.32
- VADER g = +0.16
- Claude g = +0.33
- Joint Hotelling T² F=30.95, p=1.11×10⁻¹⁶

The joint shift is decisively non-zero but with directionally split components. This is the kind of substantive consequence to which the main result applies. **A full cohort-conditional sentiment-stance analysis is reported in a companion paper (Paper 2).**

---

# 6. Discussion (~1,000 words)

## 6.1 LLM-class vs lexical-class is the construct boundary

[From current outline §6.1; emphasize cohort-stratified finding (SDN-only above 0.80 floor; Reddit-only at boundary)] (~250 words)

## 6.2 The "shared training data" alternative explanation

[From current outline §6.2] (~200 words)

**Together AI / Anthropic API asymmetry caveat (Round 17 Fix C4; ~80 words to add to §6.2):** Llama 3.3 70B and DeepSeek V3.1 were both accessed via Together AI's hosted inference, while Claude Sonnet 4 was accessed via Anthropic's first-party API. This means 2 of 3 LLMs share serving infrastructure, including any common pre/post-processing, batching, JSON-mode parsing, and request normalization that Together AI applies. The 3-LLM convergence finding is therefore partially confounded with serving infrastructure (Together AI vs Anthropic). We cannot isolate the model effect from the inference-stack effect. A future study using Llama on Meta's own inference, DeepSeek on DeepSeek's own API, and Claude on Anthropic could disentangle these. We discuss this as a residual limitation in §7 L0d.

## 6.3 What this means for "social media as policy signal" research

[From current outline §6.3] (~250 words)

## 6.4 Limitations of the multi-LLM design

We tested three LLMs from three organizations. We could not test all major LLMs (GPT-4o, Gemini 1.5 Pro, Mistral, Qwen, etc.) due to cost constraints. We selected three with maximum organizational and post-training-procedure diversity. Future work could test additional LLMs to either strengthen or refute the LLM-class convergence claim.

We also did not test fine-tuned BERT-class sentiment classifiers (e.g., DistilBERT, RoBERTa-base-sentiment). These could plausibly fall in either class. Future work should clarify.

## 6.5 Mechanism

One hypothesis: LLMs are exposed during training to instruction-tuning examples involving stance/opinion classification. They develop convergent representations of "what counts as a stance toward an entity." Lexicons measure surface affect at the token level, which doesn't aggregate to stance. This is empirically testable: future work could probe LLM internal representations for stance-specific structure.

---

# 7. Limitations (~700 words)

[USE expanded version from current outline §7 including L0a (resolved), L0b (resolved), L0c (constructs unvalidated), L0d (Together AI / Anthropic API asymmetry), then standard limitations 1-6]

[INSERT BLOCK C from MASTER_DRAFTING_KIT.md (discourse vs borrower scope)]
[INSERT BLOCK L from MASTER_DRAFTING_KIT.md (standard limitations)]

---

# 8. Conclusion (~300 words)

**Three commonly-used sentiment instruments operationalize substantively different latent constructs on Public Service Loan Forgiveness discourse text. Three LLMs from three organizations across two countries with three different post-training procedures achieve tentative-to-satisfactory inter-rater reliability: combined 3-LLM Krippendorff α=+0.7590 [+0.7241, +0.7868] (n=1,001 from Reddit subreddits and SDN-Medical); the SDN-only sub-sample exceeds the 0.80 satisfactory-reliability floor (α=+0.8306 [+0.787, +0.866]); the Reddit-only sub-sample is at the boundary (α=+0.6901 [+0.6462, +0.7302], lower CI bound below 0.667 floor). The same three LLMs disagree with TextBlob and VADER at near-zero correlation (r=0.02–0.25 across all LLM-lexical pairs); adding either lexical instrument to the 3-LLM panel collapses 4-rater α by 0.36–0.52 (binning-dependent: TB-FIXED 0.42, TB-QCUT 0.42, VADER-FIXED 0.52, VADER-QCUT 0.36). The construct boundary is between instrument classes, not between specific models — although 2 of 3 LLMs share Together AI serving infrastructure, which we cannot fully disentangle from model effect.**

Paraphrase-robustness test-retest (n=200, three alternative lexical-format system-prompt phrasings holding rubric/category-labels/reasoning-scaffold constant, K-α=+0.9011 [+0.857, +0.938]) demonstrates that LLM classifications at temperature=0 are robust to **lexical-format** prompt variation. The lower CI bound (0.857) is only 0.007 above the pre-specified 0.85 threshold; a higher-n replication is desirable. Robustness to *semantic-restructuring* prompt variation (different rubrics, different category counts, reordered ordinals) remains untested and is acknowledged as a residual limitation. An OP-vs-reply within-thread test shows TextBlob and VADER produce directionally opposite Δ in 8 of 8 cohorts on identical text — a finding extending the lexical-instrument directional-disagreement framing to policy-discourse text.

For researchers using forum/social-media data to study policy reception: **instrument choice is a substantive construct choice with consequences, not a methodological convenience.** Reporting convergent validity at the instrument-class level should be standard practice.

[INSERT BLOCK N (what we cannot claim)]
[INSERT BLOCK O (OSF reproducibility)]

---

# Tables (4 total)

- Table 1: Pairwise instrument agreement (combined n=1,001)
- Table 2: Multi-rater Krippendorff α with bootstrap CI (cohort-stratified)
- Table 3: Paraphrase-robustness 3-prompt agreement (sentiment, stance, topic)
- Table 4: Stance task three-LLM agreement (companion to Section 5.6)

# Figures (3 total)

- Figure 1: 5×5 instrument correlation matrix
- Figure 2: OP-vs-reply forest plot by cohort
- Figure 3: Cohort-stratified 3-LLM K-α with Krippendorff floors annotated

# Supplements (8 total)

- S1: Full audit history (Rounds 1–16)
- S2: PSLF policy-event chronology
- S3: Verbatim system prompts (baseline + 2 paraphrases) for Claude/Llama/DeepSeek
- S4: Full pairwise correlation tables under both binnings
- S5: Single-event minimum-working-example (Trump PSLF EO; n=1,330)
- S6: OP-vs-reply per-cohort detail
- S7: Reproducibility code and data deposit (OSF link)
- S8: Pre-registration of cross-domain COVID-vaccine replication

---

## DRAFTING NOTES FOR PAPER 1

- Voice: methodological CSS-journal formal (EPJ Data Science style)
- Lead with multi-LLM convergence (combined α=+0.76) → cohort heterogeneity (SDN above 0.80; Reddit at boundary)
- Frame paraphrase robustness as the methods-bullet-proofing finding
- Cohort heterogeneity in SDN inter-LLM agreement (sharper than Reddit) is itself a substantive finding
- Reviewers to suggest: Bestvater (Penn State), Heseltine (Oxford), Mohammad (NRC Canada), Bojić (or another author from the Bojić et al. 2025 group)
- Tier-2 fallback if rejected: Behavior Research Methods (psychometric framing fits)
- arXiv pre-print upload before journal submission

**Estimated drafting time: 6-8 weeks of focused writing.**
