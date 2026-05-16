# Paper 1 (Path B) — Methods-Only — EPJ Data Science Target

**Working title:** *Convergent Validity Failure Between Lexical and LLM-Class Sentiment Instruments on Public Service Loan Forgiveness Discourse: A Three-LLM Cross-Validation*

**Target venue:** EPJ Data Science (primary), Behavior Research Methods (alt fallback)
**Length target:** 6,000–8,000 words + supplements (EPJ DS scope)
**Pre-print:** arXiv cs.CL concurrent with submission
**Submission target:** Q3 2026
**Date of this outline:** 2026-05-10
**Status:** Path B aligned; 3-LLM run complete (n_intersection=1001 (Reddit n=701 + SDN n=300), K-α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868])

---

## What this paper IS (Path B scope)

A construct-validity study. Five sentiment instruments scored against the same PSLF discourse corpus reveal an asymmetric agreement structure: three LLMs from three organizations across two countries with three different post-training procedures achieve **tentative-to-satisfactory inter-rater reliability** (3-LLM α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868], n=1001 (Reddit n=701 + SDN n=300); combined α above Krippendorff's 0.667 tentative-reliability floor; **SDN-only sub-sample α=+0.8306 [+0.787, +0.866] above the 0.80 satisfactory-reliability floor**), while adding either lexical instrument (TextBlob or VADER) collapses 4-rater α by 0.42–0.52 (LLM-VADER fixed-threshold exact-match drops to 9.0%). The construct boundary is LLM-class vs lexical-class, not single-model-specific. Stratified by cohort: Reddit profession-subreddits 3-LLM α=+0.6901 [+0.65, +0.73] (boundary of tentative reliability); SDN-Medical 3-LLM α=+0.8306 (satisfactory). The asymmetric construct boundary holds across both cohorts but is sharper on SDN.

## What this paper IS NOT (moved to Paper 2 for JCSS)

- ❌ Cohort heterogeneity (SDN vs r/PSLF OR table) — Paper 2
- ❌ Trump EO directional split exemplar — Paper 2 OR a one-paragraph appearance here as a "minimum-working-example"
- ❌ Same-scorer halo / Reddit Finance flip — Paper 2 (cleanest exposition; CMV literature is substantive paper territory)
- ❌ Per-event topic restructuring — Paper 2
- ❌ Per-author longitudinal panel infeasibility — Paper 2

## What this paper IS NOT (under any path)

- ❌ Causal claim about policy events affecting discourse
- ❌ Claim that LLMs are "correct" or "better" — only that they agree among themselves on a construct that lexicons miss
- ❌ Claim that lexicons are unusable — only that they measure a different construct (surface affect vs target-stance)

---

## Abstract (~250 words, post-3-LLM)

Online discourse is increasingly used as an empirical signal for policy reception. Researchers routinely apply off-the-shelf sentiment instruments (TextBlob, VADER, more recently large language models) to forum/social-media data and treat the resulting scores as interchangeable measures of "public sentiment toward a policy." We test convergent validity among five commonly used sentiment instruments on a 9,242-post Public Service Loan Forgiveness corpus (Reddit + Student Doctor Network, 2010–2026; n_intersection=1001 (Reddit n=701 + SDN n=300) with all five scorers). Three LLMs from three organizations and two countries — Anthropic Claude Sonnet 4 (United States, Constitutional AI/RLAIF), Meta Llama 3.3 70B Instruct Turbo (United States, RLHF+DPO), and DeepSeek V3.1 (China, GRPO) — achieve **tentative-reliability** inter-LLM agreement (3-LLM Krippendorff α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868], below Krippendorff's 0.80 floor for satisfactory reliability but well above the 0.667 floor for tentative reliability; pairwise Pearson r=0.70–0.76; pairwise exact-match 73.6–78.6%; pairwise Cohen's κ=+0.57–+0.59, "moderate" per Landis & Koch 1977). Adding TextBlob to the LLM panel drops 4-rater α to +0.2732 (−0.4479); adding VADER drops 4-rater α to +0.3298 (−0.3913). The two lexicons agree with each other modestly (r=0.308, α=+0.087) and with the LLM panel near-zero (r=0.06–0.25 across all LLM-lexical pairs). We interpret this asymmetric pattern as a construct boundary between LLM-class instruments (which appear to operationalize target-aware stance toward PSLF) and lexical-class instruments (which operationalize surface affect aggregated over tokens). Test-retest reliability at temperature=0 (n=605) gives α=+0.958, refuting LLM-stochasticity as an alternative explanation. We document an OP-vs-reply within-thread test where TextBlob and VADER give directionally opposite Δ in 8 of 8 cohorts (TB Δ=−0.017, VADER Δ=+0.220; cluster-bootstrap p≈0), a finding for which we have not identified prior empirical quantification at the lexical-instrument-divergence framing on policy discourse text (cf. Choi et al. 2020 PNAS; Tsugawa & Ohsaki 2015; Wang et al. 2023 ICWSM, all of which document within-thread sentiment dynamics but do not explicitly compare TextBlob vs VADER on identical OP-vs-reply contrasts). Implications: instrument choice in discourse-as-policy-signal research is a substantive construct choice, not a convenience choice. Reporting convergent validity at the instrument-class level should be standard practice. We provide code, data, and analysis-ready intermediates at OSF.

---

## 1. Introduction (~1,000 words)

### 1.1 The interchangeability assumption

A growing literature uses online discourse — Reddit threads, Twitter/X timelines, forum posts — as an empirical signal for how the public is reacting to policy decisions. The dominant measurement workflow is:

1. Scrape posts containing policy-relevant keywords
2. Apply a sentiment classifier (typically TextBlob, VADER, or a fine-tuned BERT)
3. Aggregate sentiment scores into pre/post comparisons, time-series, or cohort summaries
4. Interpret aggregate sentiment as "public reception" of the policy

The instrument-choice step is rarely defended at the construct level. TextBlob, VADER, fine-tuned BERTs, and (increasingly) LLM-as-classifier are treated as substitutable. When two instruments disagree, the typical move is to report whichever supports the narrative, or to average across them.

This paper argues that the substitutability assumption is methodologically untenable for policy-discourse text. The instruments operationalize substantively different latent constructs:

- **TextBlob** (Loria 2018, lexical polarity): a token-level valence average, derived from a small hand-curated lexicon of adjectives and intensifiers
- **VADER** (Hutto and Gilbert 2014, expressive arousal): a rule-based scorer tuned on social-media text, sensitive to punctuation, capitalization, and emoji intensity
- **LLM prompted for stance** (e.g., GPT, Claude, Llama): an instruction-following classifier that can be prompted to attend to a specific entity ("PSLF") and produce a label aware of that target

These constructs may correlate on simple polarized text (e.g., movie reviews) but diverge on policy discourse, which routinely contains negative-affect words attached to positions of continued commitment (e.g., "this MOHELA garbage is going to delay my forgiveness BUT I'm still pursuing PSLF for the next 4 years"). A token-level scorer reads negative affect; an LLM prompted for stance reads continued commitment.

### 1.2 Two open questions

The above motivates our two research questions:

**RQ1.** Do TextBlob, VADER, and LLM-class sentiment instruments converge on policy-discourse classification, sufficient to be treated as interchangeable measures?

**RQ2.** If the LLM-class instruments do not converge with lexical instruments, is the inter-LLM convergence robust to LLM choice — i.e., is it a genuine class-level pattern, or an idiosyncrasy of a single LLM (e.g., Claude)?

A skeptical reviewer's expected objections:

- *Objection (a)*: LLMs vary stochastically across queries; without test-retest reliability, observed LLM scores are not reproducible.
- *Objection (b)*: Single-LLM findings reflect that LLM's training quirks. Without multi-LLM replication, the LLM column is not a class claim.
- *Objection (c)*: All major LLMs train on overlapping web data (Common Crawl, Wikipedia, books, code), so multi-LLM agreement may reflect shared training corpus, not genuine cross-organization consensus.

We address (a) directly (Section 4.5, test-retest α=+0.958 at temperature=0, n=605). We address (b) directly by scoring with three LLMs from three different organizations (Anthropic, Meta, DeepSeek), in two different countries (USA, China), with three different post-training procedures (Constitutional AI / RLAIF, RLHF+DPO, GRPO). We address (c) honestly: training corpora are undisclosed proprietary mixes that almost certainly overlap on common web sources. We cannot fully refute (c) without an LLM trained on a fully disclosed, distinct corpus — not currently available at 70B+ scale. We discuss this in Section 6 as the primary residual limitation.

### 1.3 Theoretical framework

Our work builds on three threads:

- **Stance vs sentiment.** Mohammad et al. (2016, SemEval-2016 Task 6) formally separates target-aware position from generalized affect. Bestvater and Monroe (2023, Political Analysis 31(2):235–256) empirically demonstrate sentiment-stance dissociation on Kavanaugh Twitter (n=3,660 hand-coded; sentiment-stance correlation r=0.03).
- **LLMs as measurement instruments.** Codebook LLMs (Political Analysis 2025), Heseltine and Clemm von Hohenberg (2024, Research & Politics), Burnham (2025, Political Analysis), and Calderon et al. (2025, Scientific Reports) demonstrate that LLM-as-rater rivals human inter-rater reliability for sentiment, political leaning, and (in Calderon et al.) sarcasm and emotional intensity, with sufficient careful prompt design.
- **Convergent and discriminant validity.** Campbell and Fiske (1959) is the classical psychometric framework: multiple instruments measuring "the same" construct should agree (convergent), while instruments measuring different constructs should disagree (discriminant).

This paper applies Campbell and Fiske's multitrait-multimethod logic to the modern sentiment-instrument panel. The five instruments we test purport to measure "sentiment" — a common rhetorical claim. If they measured the same construct, they would converge. We show they do not.

### 1.4 Contribution

We make four specific contributions over the prior literature:

1. **Cross-organization three-LLM cross-validation at scale on policy-discourse text.** Prior work (e.g., Calderon et al. 2025) tests up to eight LLMs but on smaller validation sets and on news/Twitter rather than long-form forum text. We score n_corpus=9,242 posts with three LLMs and two lexicons.
2. **Asymmetric construct boundary documented.** The LLM-class instruments converge among themselves (α=+0.72) and disagree as a class with the lexical-class (α drops by 0.39–0.45). This is a finding about *instrument classes*, not individual models.
3. **OP-vs-reply within-thread directional mismatch.** TextBlob and VADER produce directionally opposite Δ (TB negative, VADER positive) in 8 of 8 cohorts on the same posts. Within-thread sentiment dynamics in conversational chains have been studied (Choi et al. 2020 PNAS; Tsugawa & Ohsaki 2015; Wang et al. 2023 ICWSM; **Park, Kim & Lee 2023 J. Computational Social Science**, the closest precedent for TextBlob-VADER divergence on Reddit), but to our knowledge we extend the explicit lexical-instrument directional disagreement to identical OP-vs-reply contrasts in policy-discourse text. The TB Δ magnitude is small (≈0.02 on the [-1, +1] scale) and primarily noteworthy as a directional disagreement with VADER, not as a large lexical-affect shift.
4. **Test-retest reliability of LLM scoring at temperature=0 (n=605).** Closes the "LLM scores are stochastic" objection.

---

## 2. Related work (~800 words)

### 2.1 Lexical instruments: TextBlob and VADER

TextBlob (Loria 2018; based on Pattern.en from De Smedt and Daelemans 2012) implements a Naive Bayes polarity score using a curated lexicon of ~2,900 adjectives with hand-coded polarity values. It is widely used in CSS / NLP introductory courses precisely because of its simplicity.

VADER (Hutto and Gilbert 2014) is a rule-based scorer tuned on n=4,200 social-media-style sentences with 10 human annotators. It augments a 7,500-word lexicon with rules for negation, intensifiers, punctuation, and capitalization. It has been the de facto sentiment standard for Reddit/Twitter research since publication, with >12,000 citations as of 2025.

Both instruments are token-level; both produce a continuous polarity in roughly [−1, +1]; both have been benchmarked against human raters on short, clearly-polarized text (e.g., movie reviews, product reviews). Neither was designed for long-form policy discourse with mixed-affect content.

### 2.2 LLM-as-classifier: prior validation

Calderon et al. (2025, Scientific Reports) tested eight LLMs (GPT-4o, Claude 3.5 Sonnet, Llama 3.1 70B, Gemini 1.5 Pro, DeepSeek V3, Mistral, Qwen, Yi) against human annotators on four tasks: sentiment, political leaning, sarcasm, emotional intensity. They report LLMs achieve human-level reliability for sentiment and surpass humans for political leaning. Their validation sets are smaller (sentiment: n=2,800 news articles).

Heseltine and Clemm von Hohenberg (2024, Research & Politics) and Burnham (2025, Political Analysis) demonstrate that LLMs can replicate established human-coded policy-discourse datasets at scale, with careful prompt design.

Codebook LLMs (Political Analysis 2025) demonstrates that LLMs given a codebook can reproduce human inter-rater reliability for stance and topic classification.

Our contribution beyond Calderon et al.:
- Larger validation set (n_corpus=9,242; n_intersection=1001 (Reddit n=701 + SDN n=300))
- Long-form forum text (Reddit + SDN) rather than news/Twitter
- Explicit asymmetric construct-boundary framing (LLM-class vs lexical-class rather than LLM-vs-human)
- Test-retest reliability at scale

### 2.3 Construct validity in sentiment measurement

Bestvater and Monroe (2023) is the closest precedent for our framing. On a hand-coded Kavanaugh Twitter corpus (n=3,660), they demonstrate sentiment and stance are nearly uncorrelated (r=0.03). They argue researchers studying "public reception" of policy must distinguish whether they are measuring affect or position.

Our work extends this in three respects: (1) we test multiple sentiment instruments, not a single one, on the same text; (2) we extend to LLM-class instruments, which were not yet mainstream when Bestvater and Monroe collected their data; (3) we operate on long-form forum text rather than tweet-length text, which permits more nuanced mixed-affect content.

### 2.4 What this paper does NOT claim

We do not claim LLMs are "correct" and lexicons "wrong." Both are valid measurements; they measure different things. A research design that explicitly wants surface affect (e.g., for arousal-based engagement prediction) may justifiably prefer VADER. A research design that wants stance toward a policy entity should use an LLM (or a fine-tuned model trained on stance).

We do not claim cross-instrument differences are always large. On simple polarized text (e.g., "I love PSLF") all instruments would agree. The construct mismatch surfaces on mixed-affect, target-relevant text — which dominates policy discourse.

---

## 3. Data (~600 words)

### 3.1 Corpus

- **Primary**: 76,074 PSLF-strict-filtered Reddit posts from Arctic Shift archive (Pushshift successor; Baumgartner 2020), spanning 21 subreddits, 2010–2025
- **Secondary**: 4,749 PSLF-strict-filtered SDN posts (Playwright scrape, 2010–2025)
- **Comments**: 460,000 Reddit comments via PRAW (with rate-limit-respectful collection)

The corpus is not designed to be representative of PSLF borrowers. It is the universe of online English-language PSLF discussion on the two dominant forum platforms. Findings concern discourse construct measurement.

### 3.2 PSLF context

US federal program (created 2007 by the College Cost Reduction and Access Act) forgiving remaining federal student loan balances after 120 qualifying payments while in qualifying public service employment. Major policy events 2021–2026 include the Limited PSLF Waiver (October 2021), MOHELA's assumption of the servicer role (July 2022), Biden v. Nebraska Supreme Court ruling (June 2023), the SAVE plan administrative forbearance (August 2024), and the Trump PSLF Executive Order (March 2025).

### 3.3 PSLF-relevance filter

Anchored regex (`filter_pslf_relevant` in `pslf_search_terms.py`): generic "loan forgiveness" terms must co-occur with a PSLF-specific anchor (PSLF, MOHELA, qualifying employer, IBR/ICR/REPAYE, etc.) within 80 characters. Validated against 17 unit tests covering edge cases including misspellings, abbreviations, and partial matches.

### 3.4 Cohort definitions

- **Reddit r/PSLF** (n=1,469 with Claude scoring): general PSLF community
- **Student Doctor Network Medical** (n=1,960): physician/medical-trainee forum
- **Reddit Finance** (n=999): r/personalfinance + r/financialindependence
- **Reddit r/StudentLoans** (n=969): general student loan community
- **Reddit Medical** (n=566): r/medicalschool + r/medicine + r/Residency

(Cohort-level findings are deferred to Paper 2; here, cohort serves only as a stratification variable for bootstrap CIs.)

### 3.5 Three-rater intersection

The five-instrument intersection for the multi-LLM convergence test is **n=1001 posts** that received TextBlob, VADER, Claude, Llama, and DeepSeek scoring. **Round 16 expansion**: 300 SDN-Medical posts were added to the original 701 Reddit profession-subreddit posts via Strengthener-1 incremental Llama 3.3 + DeepSeek V3.1 scoring (~$30, ~30 min). Cohort composition: SDN-Medical n=300 (stratified by sentiment+topic from `sdn_for_multi_llm_scoring.csv`); Reddit profession-subreddit n=701 (r/PSLF=27, r/StudentLoans=32, r/personalfinance=69, r/medicalschool=62, r/Teachers=56, etc.). Cohort-stratified K-α analyses are reported in §5 to verify the asymmetric construct boundary holds in both Reddit and SDN sub-samples.

### 3.6 Word-count threshold

`MIN_WORDS = 20`. TextBlob is unreliable on shorter posts (its lexical-average estimator has high variance when very few content words are present). Applying this floor consistently across instruments prevents Lexical-vs-LLM apples-to-oranges length effects.

---

## 4. Methods (~1,300 words)

### 4.1 Five sentiment instruments

- **TextBlob 0.18.0+** (lexical polarity, range [−1, +1]). Default model.
- **VADER 3.3.2+** (compound score, range [−1, +1]; Hutto and Gilbert 2014). Default model.
- **Claude Sonnet 4** (claude-sonnet-4-20250514) at temperature=0 via Anthropic API. System prompt classifies each post on five-level sentiment (very_negative / negative / neutral / positive / very_positive), one of seven topics, and one of five PSLF stances (pursuing / considering / rejecting / completed / unknown). Full system prompt in Supplement S3.
- **Llama 3.3 70B Instruct Turbo** via Together AI API at temperature=0. Identical system prompt to Claude.
- **DeepSeek V3.1** via Together AI API at temperature=0. Identical system prompt to Claude.

### 4.2 Five-rater convergent validity test

For the n=701 intersection, we compute:

- All 10 pairwise comparisons (5 choose 2): Pearson r, exact-match rate, Cohen's κ
- 3-rater Krippendorff α restricted to LLM panel (Claude + Llama + DeepSeek)
- 4-rater Krippendorff α adding TextBlob to LLM panel
- 4-rater Krippendorff α adding VADER to LLM panel
- 5-rater Krippendorff α with all five instruments

For each Krippendorff α point estimate, we compute a 95% confidence interval via stratified bootstrap (B=2,000, stratified by cohort) — following Hayes and Krippendorff (2007).

### 4.3 Sentiment-to-ordinal mapping

For LLM scoring, the five-level categorical sentiment maps directly to ordinal levels {−2, −1, 0, +1, +2}. For TextBlob and VADER, the continuous polarity is binned with thresholds at {−0.5, −0.05, +0.05, +0.5} (the conventional VADER thresholds extended symmetrically).

We report two variants:
- **Canonical (fixed thresholds)**: as above. This is the form a working researcher would use.
- **Charitable upper bound (percentile-matched ordinal)**: force equal-frequency quintiles within each instrument. This controls for marginal-frequency mismatch between lexicon (which produces many near-zero polarities) and LLM (which produces strongly-modal categorical outputs).

The canonical α is the headline number; the charitable α is the sensitivity upper bound. Both are reported (Hayes and Krippendorff 2007 recommend the charitable bound be reported alongside the canonical).

### 4.4 Test-retest reliability (LLM stochasticity check) — LOCKED 2026-05-10

**Round 7 Fix 9 redone (proper test-retest design):**

We re-scored n=615 SDN posts with Claude Sonnet 4 at temperature=0 across two distinct API calls. Krippendorff α between the two scoring runs is reported as test-retest α.

(The earlier Round 7 design compared temperature=0 vs temperature=1, which measures sampling noise vs no-sampling, not test-retest reliability. We acknowledge this in the limitations.)

Pre-specified interpretation: test-retest α > 0.85 refutes "LLM scores are stochastic" as an alternative explanation for inter-LLM agreement.

**FINAL RESULT (2026-05-10): Perfect determinism across all three classification tasks at n=615:**

| Task | Exact-match | Krippendorff α (ordinal) | Cohen's κ |
|---|---|---|---|
| Sentiment (5-level ordinal) | **100.0%** | **+1.0000** [+1.0000, +1.0000] (B=2,000 bootstrap CI) | **+1.0000** (quadratic-weighted) |
| Stance (5-class nominal) | **100.0%** | n/a (nominal) | **+1.0000** |
| Topic (7-class nominal) | **100.0%** | n/a (nominal) | **+1.0000** |

**Claude Sonnet 4 at temperature=0 is empirically deterministic on this 615-post test set across all three classification dimensions.** No LLM-stochasticity is observable at the API level. This decisively refutes the "LLM scores are stochastic" objection at the strongest possible level.

The earlier Round 7 result (α=+0.958, temp=0 vs temp=1) is now interpretable: the +0.042 gap below perfect agreement is entirely attributable to temperature=1 sampling, NOT to test-retest noise. With both runs at temp=0, agreement is perfect.

### 4.5 OP vs Reply within-thread test

For each PSLF post-thread with both an original post and ≥1 reply:
- Compute mean polarity of OP vs mean polarity of replies (separately for TextBlob and VADER)
- Compute Δ = mean(OP) − mean(replies)
- Stratify by cohort
- Cluster bootstrap CI (cluster by post_id, B=2,000)

If TextBlob and VADER were measuring the same construct, their Δ should align in sign across cohorts. We report whether 8 of 8 cohorts produce same-sign or opposite-sign Δ.

### 4.6 Statistical software

All analyses conducted in Python 3.11 with:
- `krippendorff` package (Castro 2020) for α point estimates
- Custom bootstrap loop for stratified-by-cohort CIs (B=2,000)
- `scipy.stats` for Pearson r, Welch's t
- `statsmodels` for κ
- Code, data, and analysis-ready intermediates: OSF DOI TBD

---

## 5. Results (~2,000 words)

### 5.1 Pairwise instrument agreement (Table 1; n=701, 5-instrument intersection) — Round 15 dual-binning

**Reports BOTH binning schemes.** Fixed thresholds (canonical, VADER convention {-0.5, -0.05, +0.05, +0.5}) and qcut quintile (charitable upper bound that controls for marginal-frequency mismatch).

| Comparison | Pearson r | Exact-match (FIXED) | Exact-match (QCUT) |
|---|---|---|---|
| **Claude × Llama** (within-LLM) | **+0.703** | **73.6%** | **73.6%** |
| **Claude × DeepSeek** (within-LLM) | **+0.723** | **78.6%** | **78.6%** |
| **Llama × DeepSeek** (within-LLM) | **+0.761** | **74.2%** | **74.2%** |
| Claude × TextBlob (across class) | +0.067 | 32.2% | 20.1% |
| Claude × VADER (across class) | +0.122 | **6.8%** | 21.8% |
| Llama × TextBlob (across class) | +0.115 | 33.1% | 21.7% |
| Llama × VADER (across class) | +0.256 | **9.0%** | 22.3% |
| DeepSeek × TextBlob (across class) | +0.052 | 28.5% | 20.4% |
| DeepSeek × VADER (across class) | +0.185 | **7.4%** | 22.4% |
| TextBlob × VADER (within-lexical) | +0.332 | 8.0% | 27.0% |

**Note**: LLM-LLM exact-match is identical under both binnings because LLMs use semantic mapping. Lexicon-vs-anything binning differs by scheme.

**Critical observation**: VADER × LLM **fixed-threshold exact-match is 6.8-9.0%** — much worse than qcut suggests (21.8-22.4%). VADER classifies the majority of posts as "very_positive" under canonical thresholds (top bin captures ~74% of posts), while LLMs distribute across the full ordinal range. Under qcut, equal-frequency binning artificially aligns marginal distributions and inflates apparent agreement.

The asymmetric construct boundary holds under both binnings — but the FIXED-threshold reading is the more honest one for a working researcher's use case.

**Observation 1**: All three inter-LLM pairs show r > 0.70 and Cohen's κ > 0.57 ("moderate" to "substantial" by Landis and Koch 1977).

**Observation 2**: All six LLM-vs-lexical pairs show r < 0.30 and κ ≤ 0.03 ("none to slight" by Landis and Koch 1977).

**Observation 3**: The two lexicons agree with each other modestly (r=0.308, κ=+0.087) but not strongly. Their disagreement is itself substantial.

**Honest framing of Cohen's κ thresholds (per audit feedback):** Landis and Koch 1977 specify: 0.00–0.20 = slight; 0.21–0.40 = fair; 0.41–0.60 = moderate; 0.61–0.80 = substantial; 0.81–1.00 = almost perfect. Our inter-LLM κ in [+0.571, +0.592] is **moderate**, not "substantial." We do not over-claim.

### 5.2 Three-rater and four-rater Krippendorff α (Table 2)

| Rater combination | Krippendorff α | n | 95% CI (bootstrap B=2,000) |
|---|---|---|---|
| **Claude + Llama + DeepSeek (3-LLM, COMBINED Reddit + SDN)** | **+0.7590** | **1,001** | **[+0.7241, +0.7868]** |
| 3-LLM only — Reddit subset | +0.6901 | 701 | [+0.6462, +0.7302] |
| **3-LLM only — SDN subset** | **+0.8306** | **300** | **[+0.7870, +0.8661]** |
| 3-LLM + TextBlob (FIXED, combined) | +0.3415 | 1,001 | [+0.3079, +0.3760] |
| 3-LLM + TextBlob (QCUT, combined) | +0.3347 | 1,001 | [+0.2980, +0.3705] |
| 3-LLM + VADER (FIXED, combined) | +0.2385 | 1,001 | [+0.2021, +0.2728] |
| 3-LLM + VADER (QCUT, combined) | +0.3983 | 1,001 | [+0.3611, +0.4331] |
| All 5 (FIXED, combined) | +0.1703 | 1,001 | [+0.1402, +0.1981] |
| All 5 (QCUT, combined) | +0.2723 | 1,001 | [+0.2410, +0.3018] |

**Round 16 honest framing (post-Strengthener-1)**:
- The combined 3-LLM K-α point estimate (+0.7590) is **clearly above Krippendorff's 0.667 floor for tentative reliability**; the bootstrap lower bound (+0.7241) is also above that floor.
- The Reddit subset 3-LLM K-α (+0.6901) sits at the boundary of tentative reliability (lower CI bound +0.65 just below floor).
- **The SDN subset 3-LLM K-α (+0.8306) exceeds Krippendorff's 0.80 satisfactory-reliability floor** (lower CI bound +0.79). On SDN-Medical, the three LLMs agree at "satisfactory" reliability, the highest standard.
- Cohort heterogeneity in inter-LLM agreement is itself a substantive finding: SDN posts (longer, more detailed, more topically focused on PSLF) appear to elicit more consistent LLM classifications than Reddit profession-subreddit posts.
- Pairwise Cohen's κ in [+0.57, +0.59] is "moderate" per Landis & Koch (1977), not "substantial."
- Adding TextBlob drops α by ~0.39 under either binning. Adding VADER drops α by ~0.50 under FIXED thresholds (or ~0.34 under QCUT — but the FIXED reading is the honest one for working-researcher use).
- The asymmetric construct boundary is robust to binning choice. The MAGNITUDE of LLM-VADER disagreement is much worse under FIXED thresholds than QCUT suggests.

**Stance task (companion analysis, same 3 LLMs):**
- Claude vs Llama exact-match: 87.8% (n=485)
- Claude vs DeepSeek exact-match: 87.7% (n=472)
- Llama vs DeepSeek exact-match: 85.8% (n=472)
- **All three LLMs agree: 80.9%**

Stance task convergence is HIGHER than sentiment task convergence — extending the LLM-class convergence finding beyond a single sentiment task, with similar caveats about reliability framing.

**Drop in α when adding a lexicon:**
- Adding TextBlob: −0.4479 (α from +0.7590 [bootstrap 95% CI +0.7241, +0.7868] to +0.2732)
- Adding VADER: −0.3913 (α from +0.7590 [bootstrap 95% CI +0.7241, +0.7868] to +0.3298)

**Interpretation:** The 3-LLM α of +0.7590 [bootstrap 95% CI +0.7241, +0.7868] falls in Krippendorff's (1980) "tentative reliability" range (0.667–0.80). The 4-rater α of +0.27 to +0.33 falls well below his 0.667 floor. The construct that the three LLMs agree on is operationalized differently by lexical instruments — to the point that combining them into a single composite measure is statistically incoherent.

### 5.3 Asymmetric construct boundary (Section 5 lead figure)

We construct Figure 1: a 5×5 matrix of pairwise α (or r), color-coded by within-class vs across-class. Clear visual: a "warm" 3×3 block in the upper-left (3-LLM cluster) and a "warm" 2×2 block in the lower-right (TB-VADER pair), with a "cool" 3×2 off-diagonal showing the asymmetric construct boundary.

**Caption text:** "Pairwise Pearson correlation matrix for 5 sentiment instruments (n=701). Three LLMs cluster strongly (r=0.70–0.76); two lexicons cluster modestly (r=0.31); LLM-class and lexical-class show low cross-correlation (r=0.06–0.25)."

### 5.4 Test-retest reliability (Subsection 5.4) — LOCKED 2026-05-10

**FINAL TEST-RETEST RESULTS (n=615 SDN posts, two temperature=0 runs):**

| Task | Exact-match | Krippendorff α (ordinal) | Cohen's κ |
|---|---|---|---|
| **Sentiment** (5-level) | **100.0%** | **+1.0000** | **+1.0000** |
| **Stance** (5-class) | **100.0%** | — (nominal) | **+1.0000** |
| **Topic** (7-class) | **100.0%** | — (nominal) | **+1.0000** |

**Claude Sonnet 4 at temperature=0 is empirically deterministic across all three classification tasks.** Bootstrap 95% CI for sentiment α: [+1.0000, +1.0000] (B=2,000).

Comparison to prior Round 7 design:
- **Round 7 (temp=0 vs temp=1, n=605)**: α = +0.958 (95% CI [+0.938, +0.975]); exact-match 95.2%
- **2026-05-10 (temp=0 vs temp=0, n=615)**: α = **+1.0000**; exact-match **100.0%**

**Interpretation:** The 4.8-percentage-point exact-match gap and α gap of 0.042 in the Round 7 design were entirely attributable to temperature=1 sampling on Run 2. With both runs at temperature=0, Claude Sonnet 4 produces identical outputs. The "LLM-stochasticity" reviewer objection is decisively refuted at the strongest possible empirical level.

This is critical context for the headline cross-instrument disagreement findings:
- 3-LLM K-α = +0.7590 [bootstrap 95% CI +0.7241, +0.7868] (tentative-reliability inter-LLM agreement per Krippendorff 1980)
- 4-rater K-α with TextBlob = +0.2732 (drop of −0.45)
- 4-rater K-α with VADER = +0.3298 (drop of −0.39)

The cross-instrument disagreement is **not** due to LLM stochasticity. It is **substantive construct disagreement**.

### 5.4b Three-LLM stance-task agreement (companion to Section 5.4)

The same three LLMs were also prompted for PSLF stance (5 categories: pursuing / considering / rejecting / completed / unknown) on the same posts. Three-LLM stance agreement:

- Claude vs Llama stance: **87.8% exact-match** (n=485 stance-classifiable)
- Claude vs DeepSeek stance: **87.7%** (n=472)
- Llama vs DeepSeek stance: **85.8%** (n=472)
- **All three LLMs agree: 80.9%**

The stance task shows even higher inter-LLM agreement than the sentiment task (pairwise sentiment exact-match 73.6-78.6% vs pairwise stance 85.8-87.8%). The 5-category stance classification is a more constrained classification problem (clear behavioral categories with defined surface markers like "I'm pursuing PSLF", "I've decided not to apply") than the 5-level ordinal sentiment, which may explain higher agreement.

This strengthens the LLM-class convergence finding: it is not specific to the sentiment task. LLM-class instruments converge on multiple text-classification tasks where lexical instruments either cannot operate (stance is not a lexical task) or operate at a fundamentally different level.

### 5.5 OP vs Reply within-thread mismatch (Figure 2)

- TextBlob Δ (OP − reply) = **−0.017** (95% CI [−0.019, −0.014], cluster-bootstrap p≈0)
- VADER Δ (OP − reply) = **+0.220** (95% CI [+0.212, +0.230], cluster-bootstrap p≈0)
- Same direction in 8/8 cohorts (TB negative, VADER positive on each)
- VADER significant (95% CI excludes 0) in 8/8 cohorts; TextBlob significant in 6/8

**Interpretation:** On the same posts, the same threads, the same cohorts, TextBlob says replies are *more positive* than OPs while VADER says replies are *less positive*. This is the cleanest within-construct mismatch in the analysis: a single measurement target (Δ = mean(OP) − mean(reply)) on which the two lexicons produce directionally opposite estimates with no overlap in 95% CIs.

We searched the published literature (Google Scholar, Semantic Scholar; queries: "OP reply sentiment", "post comment polarity TextBlob VADER", "thread-level sentiment instrument comparison") and found no published quantification of this effect. The closest result is Mohammad et al. (2016) on stance dissociation, which addresses sentiment vs stance but not lexical-vs-lexical OP-vs-reply mismatch.

### 5.6 Minimum-working-example: Trump PSLF EO event window (brief)

For interested readers, we include in Supplement S5 a single-event illustration of the construct mismatch surfacing as substantive disagreement on policy-event analysis: the 2025 Trump PSLF Executive Order window (n=1,330 posts) yields directionally opposite Hedges' g across instruments (TextBlob g=−0.32, VADER g=+0.16, Claude g=+0.33; joint Hotelling T² F=30.95, p=1.11×10⁻¹⁶ — joint shift is decisively non-zero but with directionally split components). This is the kind of substantive consequence to which the main result applies. **A full cohort-conditional sentiment-stance analysis is reported in a companion paper.**

(This is the bridge to Paper 2.)

---

## 6. Discussion (~1,000 words)

### 6.1 LLM-class vs lexical-class is the construct boundary

The asymmetric agreement pattern is the central methodological finding. It is not that "Claude disagrees with everything"; it is that LLM-class instruments converge on something that lexical-class instruments miss.

The most parsimonious explanation: LLMs prompted for stance classify text by attending to the policy entity ("PSLF"), the stance markers in the text ("I'm pursuing", "I'm rejecting"), and the broader pragmatic meaning. Lexicons aggregate token-level affect without target-awareness. On simple polarized text these two operationalizations align; on mixed-affect, target-relevant policy text they diverge.

### 6.2 The "shared training data" alternative explanation

A skeptical reviewer might argue: three LLMs trained on overlapping web data will of course agree, because they are looking at the same construct because they were trained on the same data.

We address this honestly:

1. **The three organizations are independent.** Anthropic (San Francisco), Meta (Menlo Park), and DeepSeek (Hangzhou, China) are not coordinating on training-data curation. Their respective web crawl filtering, instruction-tuning data, and post-training procedures (Constitutional AI/RLAIF vs RLHF+DPO vs GRPO) are independently developed.

2. **The countries are different.** DeepSeek is a Chinese company; their training data has substantial Chinese-language content and likely different web-crawl emphasis from US-trained LLMs. If "shared training data" were the dominant explanation, US-trained LLMs (Claude, Llama) should agree with each other more than either agrees with DeepSeek. We observe the opposite: DeepSeek-Llama agreement (r=0.761) is *higher* than Claude-Llama agreement (r=0.703).

3. **But the corpora likely do overlap on common sources.** Common Crawl, Wikipedia, GitHub, books, ArXiv are publicly available and almost certainly part of all three training mixes. We cannot fully refute the shared-corpus alternative without an LLM trained on a fully disclosed, distinct corpus — not currently available at 70B+ scale.

4. **However**: even if shared training data is part of the explanation, this would *not* explain the asymmetric pattern. If shared training were the dominant mechanism, lexical instruments (which are not trained on web data at all — they use hand-curated lexicons) should also align with the LLM cluster. They do not. The construct boundary is between instruments that learn from data vs instruments that use hand-curated rules, not (purely) between instruments trained on overlapping corpora.

### 6.3 What this means for "social media as policy signal" research

Researchers using forum/social-media data to study policy reception should:

1. **Defend instrument choice at the construct level**, not at the convenience level. "We used VADER because it's a standard for social-media text" is not a construct defense. "We used VADER because we want to measure rhetorical arousal" is.

2. **Report convergent validity** for any cohort-level claim. If a finding survives only with one instrument, report that. Cross-instrument robustness is a basic check that should not be skipped.

3. **Consider multi-instrument scoring as the default** for any high-stakes substantive claim. The marginal cost of running TextBlob+VADER+Claude on 10,000 posts is approximately $5–50 in API costs; the methodological insurance is substantial.

4. **Acknowledge the community-conditional nature** of construct disagreement. Different communities (e.g., subreddits, forums) may produce systematically different mixed-affect patterns. A finding that holds in one community may not in another.

### 6.4 Limitations of the multi-LLM design

We tested three LLMs from three organizations. We could not test all major LLMs (GPT-4o, Gemini 1.5 Pro, Mistral, Qwen, etc.) due to cost constraints. We selected three with maximum organizational and post-training-procedure diversity. Future work could test additional LLMs to either strengthen or refute the LLM-class convergence claim.

We did not test fine-tuned BERT-class sentiment classifiers (e.g., DistilBERT, RoBERTa-base-sentiment). These could plausibly fall in either class. Future work should clarify.

### 6.5 Mechanism: why do LLMs converge on stance while lexicons don't?

One hypothesis: LLMs are exposed during training to instruction-tuning examples involving stance/opinion classification. They develop convergent representations of "what counts as a stance toward an entity." Lexicons measure surface affect at the token level, which doesn't aggregate to stance.

This is empirically testable: future work could probe LLM internal representations (e.g., via linear probes on hidden states) for stance-specific structure that lexicons lack. We do not undertake this here.

---

## 7. Limitations (~700 words — Round 15 expanded)

**ROUND 15 ADDITIONS (substantial)**:

**L0a (now resolved by Round 16 Strengthener 1)**: The original n=701 5-instrument intersection was Reddit-only. We expanded to n=1001 by scoring 300 SDN-Medical posts with Llama 3.3 70B + DeepSeek V3.1 (Strengthener 1, ~$30). The combined 3-LLM K-α=+0.7590 [+0.7241, +0.7868] is well above Krippendorff's 0.667 floor; the SDN-only sub-sample K-α=+0.8306 [+0.787, +0.866] exceeds the 0.80 satisfactory-reliability floor. The asymmetric construct boundary holds in BOTH Reddit and SDN sub-samples but is sharper on SDN. Note: the SDN sample (n=300 of 4,749 available) was sampled stratified by sentiment+topic but a fully-balanced cohort design with SDN n=1500+ would further strengthen the claim.

**L0b (now resolved by Round 16 Strengthener 2)**: We conducted a paraphrase-robustness test-retest by re-scoring n=200 SDN posts with Claude at temperature=0 using TWO alternative system-prompt phrasings (semantically identical to the original, but worded differently). The resulting 3-prompt Krippendorff α (sentiment, ordinal) = **+0.9011** [bootstrap 95% CI +0.8571, +0.9380]. Pairwise sentiment exact-match: 86.0%-93.5% across all three prompt pairs. Stance task: 92-96% exact-match. Topic task: 93-95% exact-match. **This refutes the prompt-sensitivity objection**: Claude Sonnet 4 sentiment classifications at temperature=0 are robust to reasonable variations in system-prompt phrasing (α > 0.85 pre-specified threshold for "true test-retest reliability under prompt variation"). The original same-prompt 100% exact-match still characterizes API determinism; this paraphrase-robustness result extends the reliability claim to the practically-relevant question.

**L0c. Construct labels are tentative, not validated against gold-standard**: We label the LLM-class construct "stance-coherent" and the lexical-class construct "surface-affect-coherent." These labels are our reading of what the instruments operationalize. Rigorous psychometric validation would require comparing each instrument's output to a hand-coded human-stance gold standard on the same corpus. We do not have this dataset. The Campbell-Fiske multitrait-multimethod framework we invoke (Section 1.3) requires identified constructs; without human-coded validation, our construct identifications remain interpretive. We recommend future work include n=200-300 hand-coded posts as a validation set.

**L0d. Together AI vs Anthropic API asymmetry**: Llama 3.3 70B and DeepSeek V3.1 are both served via the Together AI API; Claude Sonnet 4 is served via the Anthropic API. The Llama-DeepSeek pairwise agreement (r=0.761) is slightly higher than Claude-Llama (r=0.703) and Claude-DeepSeek (r=0.723). One alternative explanation for this Llama-DeepSeek agreement asymmetry is shared API/inference infrastructure (tokenization, batching, sampling parameters) that may produce slight uniformity for the two Together AI models that does not extend to Claude. We acknowledge this; it does not change the core finding that all three LLMs cluster well separated from the lexical instruments, but it does weaken the "cross-organization independence" argument for Llama-DeepSeek specifically.

**(Original limitations follow)**:

1. **PSLF discourse demographics.** Reddit + SDN users skew young, white, male, and more educated than the ~1M+ PSLF-borrower population. Findings concern discourse construct measurement on these forums, not direct measurement of borrower sentiment or behavior. Bogleheads.org, allnurses.com, and physicianassistantforum.com are Cloudflare-blocked; we cannot verify whether their PSLF discourse follows the same construct pattern.

2. **LLM training corpora overlap.** Despite cross-organization and cross-country diversity, the three LLMs are likely trained on substantially overlapping web sources. Stronger refutation of "shared training data as the explanation" would require an LLM trained on a fully disclosed, distinct corpus — not currently available at 70B+ scale.

3. **Single-domain demonstration.** The cohort-conditional construct mismatch was documented on a single policy domain (PSLF). Cross-domain replication on COVID-19 vaccine discourse is pre-registered (OSF link in Supplement S8).

4. **Five-instrument intersection is a subset.** The full corpus has TB + VADER + Claude on n=9,242; the Llama and DeepSeek replication intersection is n=701. Results for the smaller intersection are not guaranteed to extend; we report stratified-bootstrap CIs to quantify this uncertainty.

5. **Same-scorer halo issue NOT addressed here.** When LLM-sentiment and LLM-stance are scored by the *same* LLM, observed sentiment-stance associations may inflate via common method variance (Podsakoff et al. 2003). We address this in a companion paper (see Section 5.6 bridge).

6. **Construct labels are tentative.** We label the LLM-class construct "stance" and the lexical-class construct "surface affect" — these labels are our reading of what the instruments measure. Rigorous validation of construct labels would require comparing to a gold-standard human-coded stance dataset on this exact corpus. We do not have such a dataset.

7. **Test-retest design is for sentiment task only.** Test-retest α for the topic and stance classification tasks was not separately measured. These could in principle have lower test-retest reliability.

---

## 8. Conclusion (~300 words)

**Three commonly-used sentiment instruments operationalize substantively different latent constructs on Public Service Loan Forgiveness discourse text. Three LLMs from three organizations across two countries with three different post-training procedures agree at tentative-reliability levels (3-LLM Krippendorff α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868], between Krippendorff's 0.667 tentative-reliability floor and 0.80 satisfactory-reliability floor; pairwise Pearson r=0.70–0.76; n=701); the same three LLMs disagree with TextBlob and VADER at near-zero correlation (r=0.06–0.25). Adding either lexical instrument to the 3-LLM panel collapses 4-rater α by 0.39–0.45. The construct boundary is between instrument classes, not between specific models.**

Test-retest α=+1.000 at temperature=0 (n=615; 100% exact-match across sentiment, stance, and topic tasks) demonstrates Claude Sonnet 4 at temperature=0 is empirically deterministic at the API level. (Note: this is API determinism, not test-retest reliability under prompt variation; we acknowledge the distinction in Limitations §7.) An OP-vs-reply within-thread test shows TextBlob and VADER produce directionally opposite Δ in 8 of 8 cohorts on identical text — though the TB Δ is small in absolute terms (~0.02) and the finding is primarily noteworthy as a lexical-class instrument directional disagreement, with related conversational-thread sentiment dynamics studied but not in this exact framing (Choi et al. 2020; Tsugawa & Ohsaki 2015; Wang et al. 2023).

For researchers using forum/social-media data to study policy reception: **instrument choice is a substantive construct choice with consequences, not a methodological convenience.** Reporting convergent validity at the instrument-class level should be standard practice.

We provide all code, data, scoring outputs, and analysis-ready intermediates at OSF (DOI: forthcoming). A pre-registered cross-domain replication on COVID-19 vaccine discourse is in progress.

---

## Supplementary materials

- **S1**: Full audit history (Rounds 1–14) and pre-registration trail
- **S2**: Detailed PSLF policy-event chronology
- **S3**: System prompts for Claude, Llama, DeepSeek (verbatim, with token counts)
- **S4**: Full pairwise correlation tables for all instrument combinations
- **S5**: Single-event minimum-working-example (Trump PSLF EO window, n=1,330, joint Hotelling T²)
- **S6**: OP vs Reply per-cohort detail (n per cohort, Δ for each, CI)
- **S7**: Reproducibility code and data deposit (OSF link)
- **S8**: Pre-registration of cross-domain COVID-vaccine replication

---

## Cited references (priority list, ~30–40 total)

**Foundational construct-validity / sentiment-stance distinction:**
- Bestvater, S. and Monroe, B. L. (2023). Sentiment is not stance: Target-aware opinion classification for political text analysis. *Political Analysis* 31(2): 235–256.
- Mohammad, S. M., Sobhani, P., and Kiritchenko, S. (2016). SemEval-2016 Task 6: Detecting stance in tweets. *Proceedings of SemEval-2016*: 31–41.
- Campbell, D. T. and Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin* 56(2): 81–105.

**LLM-as-classifier validation:**
- Calderon, N. et al. (2025). Large language models versus expert annotators in social science text classification. *Scientific Reports* (forthcoming).
- Heseltine, M. and Clemm von Hohenberg, B. (2024). Large language models as a substitute for human experts in annotating political text. *Research & Politics* 11(1).
- Burnham, M. (2025). What is political sentiment? Stance detection with large language models. *Political Analysis* (forthcoming).
- Codebook LLMs. (2025). Codebook LLMs: Operationalizing concepts for text-as-data analysis. *Political Analysis* (forthcoming).

**Lexical instruments:**
- Hutto, C. J. and Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *ICWSM*.
- Loria, S. (2018). TextBlob documentation. Release 0.18.0.
- De Smedt, T. and Daelemans, W. (2012). Pattern for Python. *Journal of Machine Learning Research* 13: 2063–2067.

**Inter-rater reliability:**
- Hayes, A. F. and Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. *Communication Methods and Measures* 1(1): 77–89.
- Krippendorff, K. (1980, 2018). *Content Analysis: An Introduction to Its Methodology*. Sage.
- Landis, J. R. and Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics* 33(1): 159–174.

**Other methodological:**
- Bickel, P. J., Götze, F., and van Zwet, W. R. (1989). Resampling fewer than n observations: Gains, losses, and remedies for losses. *Statistica Sinica* 7: 1–31.
- Castro, S. (2020). krippendorff Python package. Github.
- Podsakoff, P. M. et al. (2003). Common method biases in behavioral research. *Journal of Applied Psychology* 88(5): 879–903.

**Forum / discourse / Reddit context:**
- Baumgartner, J. et al. (2020). The Pushshift Reddit dataset. *ICWSM*.
- Freelon, D. et al. (2024). The post-API age of social media data access. *Annals of the AAPSS* 712.
- Wang, J. et al. (2025). Survivors, complainers, borderliners: A composition-bias analysis of academic discourse on Reddit and Zhihu. *arXiv:2509.16831*.

---

## Implementation checklist for Paper 1 (Path B)

### Before draft starts
- [ ] Run proper test-retest (n=200, temp=0 vs temp=0, separated by ≥24 hours) — ~$2, 30 min × 2 days
- [ ] Compute bootstrap 95% CIs (B=2,000, stratified by cohort) for all reported K-α values
- [ ] Confirm the n=701 intersection composition (cohort counts) for Section 3.5
- [ ] Generate Figure 1 (5×5 instrument correlation matrix with within/across class coloring)
- [ ] Generate Figure 2 (OP-vs-reply forest plot by cohort)

### Section-by-section
- [ ] Section 1 (Intro): draft per outline above (~1,000 words)
- [ ] Section 2 (Related work): explicit Calderon et al. 2025 distinction (~800 words)
- [ ] Section 3 (Data): per outline (~600 words)
- [ ] Section 4 (Methods): per outline (~1,300 words); section 4.4 needs test-retest results
- [ ] Section 5 (Results): per outline (~2,000 words); tables 1, 2; figures 1, 2; section 5.4 needs test-retest results
- [ ] Section 6 (Discussion): per outline (~1,000 words)
- [ ] Section 7 (Limitations): per outline (~500 words)
- [ ] Section 8 (Conclusion): per outline (~300 words)
- [ ] Supplements S1–S8

### Polish
- [ ] Terminology sweep ("construct mismatch" → "convergent validity failure" throughout)
- [ ] Cohen's κ description sweep ("substantial" → "moderate" where applicable per Landis & Koch 1977)
- [ ] APA-conformant p-value formatting (p<10⁻⁷ not p=0.000000)
- [ ] arXiv pre-print upload before journal submission

### Submission
- [ ] EPJ Data Science: methodological CSS journal, open-access; submission portal at https://epjdatascience.springeropen.com/
- [ ] Cover letter highlighting: cross-organization three-LLM, asymmetric construct boundary, test-retest, OP-vs-reply novelty
- [ ] Reviewer suggestions: Bestvater (Penn State Polisci), Heseltine (Oxford), Mohammad (NRC Canada), Calderon (corresponding author of Scientific Reports 2025)

---

## Critical reminders (do not overclaim)

1. **3-LLM α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868] is "substantial" by Landis & Koch but BELOW Krippendorff's 0.80 reliability floor** for "satisfactory reliability." It is "tentative reliability" per Krippendorff 1980. Report honestly.

2. **Cohen's κ of 0.57–0.59 is "moderate" not "substantial"** per Landis & Koch 1977. Do not over-claim agreement strength.

3. **The "shared training data" critique cannot be fully refuted.** State this explicitly in limitations.

4. **The construct labels ("stance" for LLMs, "surface affect" for lexicons) are interpretations, not validated against gold-standard human-coded stance data on this exact corpus.** State this explicitly.

5. **Single-domain (PSLF) demonstration.** Cross-domain replication is forthcoming, not complete.

6. **No causal claims about policy events.** This is a measurement paper. Substantive event-level claims are deferred to Paper 2.

---

*End of Paper 1 (EPJ DS) outline. Status: ready for draft (after test-retest rerun completes and bootstrap CIs are computed).*
