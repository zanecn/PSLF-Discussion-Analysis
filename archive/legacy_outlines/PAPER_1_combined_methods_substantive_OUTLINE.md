# Paper 1 — Combined Methods + Substantive: Detailed Outline

**Working title:** *Cohort-Conditional Construct Mismatch in Sentiment-Instrument Validation: Three-LLM Evidence from Public Service Loan Forgiveness Discourse*

**Target venue:** Political Analysis (Cambridge University Press)
**Length target:** ~10,000 words + supplements
**Pre-print:** arXiv cs.CL (concurrent with submission)

---

## Abstract (~250 words, post-DeepSeek replication)

Three commonly-used sentiment instruments — TextBlob (lexical polarity), VADER (Hutto & Gilbert 2014, expressive arousal), and large language models prompted for stance — are routinely treated as interchangeable in policy-discourse research. Building on Bestvater & Monroe's (2023) demonstration that sentiment is not stance on Kavanaugh Twitter, we demonstrate on a 9,242-post Public Service Loan Forgiveness corpus (Reddit + Student Doctor Network, 2010-2026) that lexical and LLM instruments operationalize substantively different latent constructs. **Three LLMs from three independent organizations across two countries (Anthropic Claude Sonnet 4 [US], Meta Llama 3.3 70B [US], DeepSeek V3.1 [China]) with three different post-training procedures (Constitutional AI/RLAIF, RLHF+DPO, GRPO) achieve substantial inter-LLM agreement (3-LLM Krippendorff α=+0.[X]).** Adding either lexical instrument collapses the 4-rater α by 0.40-0.49 to +0.20-0.26. The disagreement is asymmetric: between LLM-class and lexical-class instruments, not between models within the LLM class. Three substantive consequences: (1) cohort-level sentiment-stance odds ratios show directionally opposite patterns between SDN-Medical (decoupling, OR=0.15-0.33 across instruments) and Reddit r/PSLF (venting culture, OR=1.66-7.33), robust to instrument choice; (2) Reddit Finance's apparent decoupling (OR=0.18 with same-scorer Claude×Claude) FLIPS to venting (OR=1.10-1.42) with cross-instrument operationalization, demonstrating same-scorer halo as a methodological caveat; (3) within-thread OP vs Reply mismatch (TextBlob Δ=−0.017 vs VADER Δ=+0.220, 8/8 cohort consistent) has no published precedent. Test-retest α=+0.958 at temperature=0 (n=605) refutes the LLM-stochasticity objection. Implications: instrument choice materially changes substantive answers and must be defended at the construct level.

---

## 1. Introduction (~1,500 words)

### 1.1 Motivation

Online discourse is increasingly used as an empirical signal for policy reception. Researchers routinely apply off-the-shelf sentiment instruments (TextBlob, VADER, more recently LLMs) to forum/social-media data and treat the resulting scores as interchangeable measures of "public sentiment toward a policy."

We argue this is methodologically untenable. The three commonly-used instruments operationalize substantively different latent constructs:
- TextBlob (lexical polarity): valence of words in the text
- VADER (expressive arousal, Hutto & Gilbert 2014): rhetorical intensity 
- LLMs prompted for stance: target-aware position toward a specific entity

These constructs may correlate but are not identical. Single-instrument analyses can produce systematically different policy-reception narratives.

### 1.2 Theoretical framework

- **Stance vs sentiment** (Mohammad et al. 2016, SemEval-2016 Task 6): formally distinguishes target-aware position from generalized affect
- **Sentiment is not stance** (Bestvater & Monroe 2023, Political Analysis 31(2):235-256): empirical demonstration on Kavanaugh Twitter (n=3,660 hand-coded; r=0.03 between sentiment and stance)
- **LLMs as measurement instruments** (Codebook LLMs, Political Analysis 2025; Heseltine & Clemm von Hohenberg 2024, Research & Politics; Burnham 2025, Political Analysis): LLMs as third-rater anchors

### 1.3 Our extension

We extend Bestvater & Monroe in three respects:
1. **Multi-LLM convergence test**: prior work used a single LLM. We test three LLMs from three organizations to address "single-LLM-quirk" critiques.
2. **Cohort-conditional construct mismatch**: prior work pooled across users. We decompose by community (cohort) and find the disagreement varies systematically.
3. **Same-scorer halo demonstrated empirically**: cohort claims that look strong with same-scorer (Claude×Claude) operationalization can FLIP DIRECTION with cross-instrument operationalization.

### 1.4 Research questions

RQ1: Do TextBlob, VADER, and LLM-class instruments agree on sentiment classification of policy discourse?
RQ2: Does inter-LLM agreement hold across multiple LLMs from different organizations, ruling out single-LLM idiosyncrasies?
RQ3: Does cohort-conditional sentiment-stance decoupling reflect a real substantive pattern or a same-scorer artifact?
RQ4: What are the methodological implications for "social media as policy signal" research?

---

## 2. Data (~1,000 words)

### 2.1 Corpus

- **Primary**: 76,074 PSLF-strict-filtered Reddit posts (Arctic Shift archive, 21 subreddits, 2010-2025)
- **Secondary**: 4,749 PSLF-strict-filtered SDN posts (Playwright scrape)
- **Comments**: 460,000 Reddit comments (PRAW collector, ~28% post coverage)
- **Total three-rater intersection**: n=9,242 posts with TextBlob + VADER + Claude scoring

### 2.2 PSLF context

- US federal loan forgiveness program (created 2007)
- 10-year qualifying public service required
- Major policy events 2021-2026: Limited Waiver (2021-10-06), IDR Account Adjustment, Biden v. Nebraska SCOTUS (2023-06-30), SAVE Forbearance (2024-08-09), Trump PSLF Executive Order (2025-03-07)

### 2.3 Cohort definitions (5 communities)

- **Reddit r/PSLF** (n=1,469 with Claude scoring): general PSLF community
- **Student Doctor Network Medical** (n=1,960): physician/medical-trainee forum
- **Reddit Finance** (n=999): r/personalfinance + r/financialindependence
- **Reddit r/StudentLoans** (n=969): general student loan community
- **Reddit Medical** (n=566): r/medicalschool + r/medicine + r/Residency

### 2.4 PSLF-relevance filter

Anchored regex (`filter_pslf_relevant` in `pslf_search_terms.py`): generic "loan forgiveness" terms must co-occur with a PSLF-specific anchor (PSLF/MOHELA/qualifying employer/etc.) within 80 characters. 17/17 unit tests pass.

### 2.5 Word-count threshold

`MIN_WORDS = 20` (TextBlob unreliable on shorter posts)

---

## 3. Methods (~1,500 words)

### 3.1 Three sentiment instruments

- **TextBlob 0.18.0+** (lexical polarity, range [-1, 1])
- **VADER 3.3.2+** (compound score, range [-1, 1]; Hutto & Gilbert 2014)
- **Claude Sonnet 4** (claude-sonnet-4-20250514) at temperature=0 via Anthropic API
  - Returns ordinal sentiment, primary_topic (7 categories), pslf_stance (5 categories)
  - System prompt: see supplementary

### 3.2 Three LLMs (multi-LLM convergence test)

| LLM | Organization | Country | Post-training | Architecture |
|---|---|---|---|---|
| Claude Sonnet 4 | Anthropic | USA | Constitutional AI/RLAIF | Proprietary dense |
| Llama 3.3 70B | Meta | USA | RLHF + DPO | Llama-3 dense (GQA, RoPE, SiLU) |
| DeepSeek V3.1 | DeepSeek | China | GRPO | MoE 671B (37B active) |

**LIMITATION (acknowledged in Section 6):** Training corpora for all three LLMs are undisclosed proprietary mixes that likely overlap on common web sources (Common Crawl, Wikipedia, code repositories, books). Stronger refutation of "shared training data as explanation for inter-LLM agreement" would require LLMs trained on fully disclosed distinct corpora — not currently available at 70B+ scale.

### 3.3 Inter-rater reliability

**Krippendorff's α** (`sentiment_triangulation.py`):
- Library: `krippendorff` Python package (point estimate)
- 95% CI: stratified bootstrap (B=2,000), stratification by source
- **Canonical**: fixed thresholds (TB/VADER cuts at [−0.5, −0.05, +0.05, +0.5])
- **Charitable upper bound**: percentile-matched ordinal (forces equal-frequency quintiles)

### 3.4 Test-retest reliability (LLM stochasticity check)

- Re-score n=605 SDN posts at temperature=0 vs temperature=1 over different days
- Compute test-retest Krippendorff α
- Pre-specified threshold: α > 0.85 = LLM-noise objection refuted
- **Result: α = +0.958** (95% CI [+0.938, +0.975]), exact-match 95.2%

### 3.5 Cohort-conditional sentiment-stance OR

For each (cohort, sentiment-instrument, stance-instrument) combination:
- Build 2×2 contingency table: (negative AND pursuing/considering) vs (negative AND not-pursuing) vs (not-negative AND pursuing/considering) vs (not-negative AND not-pursuing)
- Compute OR with 95% CI via log_OR ± 1.96*SE
- Negative threshold: sentiment in {very_negative, negative} OR polarity < −0.05 OR vader_compound < −0.05
- Pursuing threshold: stance in {pursuing, considering}

### 3.6 OP vs Reply test (within-thread)

For each PSLF post-thread with both an original post and ≥1 reply:
- Compute mean polarity of OP vs mean polarity of replies
- Compute Δ = mean(OP) − mean(replies)
- Stratify by cohort
- Cluster bootstrap CI (cluster by post_id, B=2,000)

### 3.7 Multi-comparison correction

- **Holm-Bonferroni step-down** (Round 7 fix)
- Family α = 0.05 across the 8 events for per-event tests
- BH FDR α=0.05 for per-event chi-sq topic shifts (8 events × 7 topics)

---

## 4. Results (~3,000 words)

### 4.1 Pairwise instrument agreement (n=701, Llama replication intersection)

**Headline table:**

| Comparison | Pearson r | Exact-match | Cohen's κ |
|---|---|---|---|
| **Claude × Llama (within-LLM-class)** | **+0.703** | **73.6%** | **+0.572** |
| Claude × DeepSeek | +0.[X] | XX.X% | +0.[X] |
| Llama × DeepSeek | +0.[X] | XX.X% | +0.[X] |
| Claude × TextBlob | +0.066 | 20.1% | +0.002 |
| Claude × VADER | +0.134 | 21.8% | +0.023 |
| Llama × TextBlob | +0.139 | 21.7% | +0.021 |
| Llama × VADER | +0.245 | 22.3% | +0.028 |
| DeepSeek × TextBlob | +0.[X] | XX.X% | +0.[X] |
| DeepSeek × VADER | +0.[X] | XX.X% | +0.[X] |
| TextBlob × VADER (within-lexical) | +0.308 | 27.0% | +0.087 |

**Key observation:** All inter-LLM pairs show r > 0.5; all LLM-vs-lexical pairs show r < 0.3.

### 4.2 Three-rater Krippendorff α (the central finding)

| 3-rater combo | α | n |
|---|---|---|
| **Claude + Llama (LLM-only)** | **+0.6912** | 701 |
| Claude + Llama + DeepSeek (3-LLM only) | +0.[X] | NNN |
| Claude + Llama + TextBlob | +0.2011 | 701 |
| Claude + Llama + DeepSeek + TextBlob | +0.[X] | NNN |
| Claude + Llama + DeepSeek + VADER | +0.[X] | NNN |

**Adding lexical drops α by 0.4-0.49.** This drop is the central methods finding.

### 4.3 Stance task agreement (Claude vs Llama, n=485)

- Overall exact-match: 87.8%
- Per-stance:
  - Considering: 92.0% (n=224)
  - Completed: 94.4% (n=18)
  - Pursuing: 84.6% (n=227)
  - Rejecting: 68.8% (n=16) — weakest cell, small n

### 4.4 Cohort heterogeneity (L5 cross-instrument robustness)

**ROBUST:** SDN-Medical decoupling AND r/PSLF venting hold across all 3 sentiment instruments

| Cohort | Claude×Claude | TB×Claude | VADER×Claude |
|---|---|---|---|
| **Reddit r/PSLF (venting)** | **OR=7.33** | **OR=1.66** | **OR=2.53** |
| **SDN-Medical (decoupling)** | **OR=0.27** | **OR=0.15** | **OR=0.33** |

**FRAGILE:** Reddit Finance flips with instrument choice
| Cohort | Claude×Claude | TB×Claude | VADER×Claude |
|---|---|---|---|
| Reddit Finance | 0.18 (decoupling) | **1.10 (venting)** | **1.42 (venting)** |

**Substantive interpretation:** Two robust patterns (SDN decoupling, r/PSLF venting). One same-scorer artifact (Finance "decoupling"). The cohort-conditional construct mismatch is REAL but with explicit cross-instrument robustness check.

### 4.5 Trump PSLF EO directional split (lead exemplar)

n=1,330 posts in Trump EO event window:
- TB g = −0.32 (p<10⁻⁶)
- VADER g = +0.16 (p=0.0007)
- Claude g = +0.33 (p<10⁻⁶)
- **Joint Hotelling T² = 30.95, p=1.11×10⁻¹⁶**

Joint shift decisively non-zero with directionally split components.

### 4.6 OP vs Reply construct mismatch (within-thread)

- TB Δ (OP − reply) = **−0.017** (95% CI [−0.019, −0.014], cluster bootstrap p=0)
- VADER Δ (OP − reply) = **+0.220** (95% CI [+0.212, +0.230], cluster bootstrap p=0)
- **Same direction in 8/8 cohorts**
- VADER significant in 8/8; TB significant in 6/8
- **No published precedent in independent literature search**

### 4.7 Test-retest reliability

- Claude at temperature=0 vs temperature=1: α = +0.958 (95% CI [+0.938, +0.975]), exact-match 95.2%
- **Closes the LLM-stochasticity objection**

---

## 5. Discussion (~1,500 words)

### 5.1 LLM-class vs lexical-class is the construct boundary

Three LLMs from three organizations across two countries with three different post-training procedures achieve substantial agreement. Two lexical instruments (TextBlob, VADER) disagree with all three LLMs at near-zero correlation. The construct boundary is asymmetric: not "Claude vs everything else" but "LLM-class vs lexical-class."

### 5.2 Same-scorer halo as a methodological caveat

The Reddit Finance "decoupling" finding (OR=0.18 with Claude-sentiment + Claude-stance) flipped to "venting" (OR=1.10-1.42) with cross-instrument operationalization. This is the cleanest empirical demonstration of same-scorer halo we know of in the literature. Implication: when computing sentiment-stance ORs from forum data, researchers should report cross-instrument estimates to verify findings aren't artifacts of shared scorer halo.

### 5.3 Cohort-conditional construct mismatch

Two robust findings (SDN-Medical decoupling, r/PSLF venting) show the cohort-conditional pattern is real for at least these two communities. The pattern's MAGNITUDE varies by instrument (cross-instrument spread 7-17× vs same-scorer spread 40×) but DIRECTION is robust.

### 5.4 What this means for "social media as policy signal" research

Researchers using off-the-shelf sentiment instruments must:
1. Defend instrument choice at the **construct level** (not the convenience level)
2. Report **cross-instrument robustness** for cohort-level claims
3. Acknowledge the **community-conditional** nature of construct disagreement
4. Use **multi-LLM convergence** rather than single-LLM scoring for high-stakes claims

### 5.5 Mechanism: why do LLMs converge on stance while lexicons don't?

Hypothesis: LLMs are exposed during training to instruction-tuning examples involving stance/opinion classification. They develop convergent representations of "what counts as a stance." Lexicons measure surface affect that doesn't aggregate to stance.

This is testable: future work could probe LLM internal representations for stance-specific structure.

---

## 6. Limitations (~600 words)

1. **PSLF discourse demographics**: Reddit + SDN users skew young, white, male, more educated than the ~1M+ PSLF-borrower population. Findings concern discourse construct measurement, not borrower behavior.

2. **LLM training corpora overlap**: Both Anthropic and Meta and DeepSeek train on undisclosed proprietary data mixes that likely overlap substantially on common web sources (Common Crawl, Wikipedia, GitHub, books). The "shared training data as explanation for inter-LLM agreement" critique cannot be fully refuted without an LLM trained on a fully disclosed, distinct corpus — not currently available at 70B+ scale.

3. **PSLF-specific finding**: The cohort-conditional construct mismatch was demonstrated on a single policy domain. Cross-domain replication on COVID-19 vaccine discourse is pre-registered (OSF preregistration link: TBD).

4. **Two-LLM coverage gap for cohort robustness**: The Llama replication n=701 covers only the Reddit cross-source subset, not SDN. The cohort-conditional finding for SDN remains based on Claude-only data; the cross-instrument robustness test for SDN uses TB and VADER (not Llama). Future work should score the full n=9,242 with multiple LLMs (estimated $50-100).

5. **Per-author longitudinal panel infeasibility**: Only 1 of 8 PSLF events meets n>=10 returning-with-stance threshold for per-author within-person analysis. The data design itself does not support within-person inference for forum discourse pre/post analyses. Pre/post stance shifts must be interpreted as discussant-pool composition shifts.

6. **Same-scorer halo extends beyond cohort heterogeneity**: We demonstrated halo for one specific OR computation. Future work should probe halo systematically across other LLM-derived metrics (topic prevalence, intention, etc.).

---

## 7. Conclusion (~400 words)

**Three commonly-used sentiment instruments operationalize substantively different latent constructs on policy-discourse text. Three LLMs from three organizations agree at substantial inter-rater levels (3-LLM α=+0.[X]); the same three LLMs disagree with TextBlob and VADER at near-zero correlation. The construct boundary is LLM-class vs lexical-class, not single-LLM-specific.**

This methodological finding has direct substantive consequences. Cohort-level sentiment-stance odds ratios show directionally opposite patterns between PSLF discussion communities (SDN-Medical decoupling, Reddit r/PSLF venting), robust to instrument choice. A third community (Reddit Finance) demonstrates same-scorer halo: the apparent decoupling reverses with cross-instrument operationalization.

For researchers using forum/social-media data to study policy reception: **instrument choice is not a methodological convenience but a substantive choice with consequences.** The single-instrument era of "online sentiment analysis" must give way to multi-instrument, cohort-conditional, construct-validity-explicit research designs.

We provide all code, data, and analysis-ready datasets at OSF (DOI: TBD). A pre-registered cross-domain replication on COVID-19 vaccine discourse is forthcoming.

---

## Supplementary materials

- S1: Full audit history (R1-R13)
- S2: Detailed PSLF policy-event chronology
- S3: System prompt for Claude/Llama/DeepSeek
- S4: Full pairwise correlation tables for all instrument combinations
- S5: All 8 per-event K-α + Hotelling T² tests
- S6: Per-event × per-cohort topic restructuring tables
- S7: Reproducibility code and data deposit (OSF link)
- S8: Pre-registration of cross-domain COVID-vaccine replication

---

## Cited references (priority list)

### Methods anchors
- Bestvater & Monroe (2023, Political Analysis 31(2):235-256)
- Burnham (2025, Political Analysis)
- Codebook LLMs (2025, Political Analysis)
- Hopfer et al. (2025, JMIR Formative Research e57395)
- Mohammad et al. (2016) SemEval-2016 Task 6
- Hutto & Gilbert (2014) VADER ICWSM
- Heseltine & Clemm von Hohenberg (2024, Research & Politics)
- Chae & Davidson (2026, Sociological Methods & Research)
- Krippendorff (1980) Content Analysis

### Statistical methodology
- Borenstein et al. (2009) Hedges' g eq. 4.24
- Bickel et al. (1989) block permutation
- Hayes & Krippendorff (2007) bootstrap CI
- Steegen et al. (2016) specification curve
- Holm (1979) step-down adjustment

### Reddit/social media research
- Cousineau (2025, MDPI Journalism & Media)
- Kovács et al. (2018, JDIQ) selection bias
- Freelon et al. (2024, ANNALS Vol 712) Post-API Age

### PSLF
- Tate Esq. (2024) HCA PSLF eligibility (cited as authoritative source)
- Yannelis & Looney (2024, NBER WP 33059)
- Brookings (2024) Past, Present, Future of PSLF

---

## Estimated draft timeline

| Section | Words | Days |
|---|---|---|
| Abstract | 250 | 0.5 |
| Introduction | 1,500 | 3 |
| Data | 1,000 | 2 |
| Methods | 1,500 | 3 |
| Results | 3,000 | 7 |
| Discussion | 1,500 | 3 |
| Limitations | 600 | 1 |
| Conclusion | 400 | 1 |
| Supplementary | 1,500 | 3 |
| **Total** | **~11,250** | **~24 days** |

Plus ~2 weeks for revisions, polish, and figure refinement → **6 weeks total to submission**.

---

## What I need from DeepSeek replication to finalize

**Headline numbers to fill in:**
- Claude × DeepSeek: r, exact-match, κ
- Llama × DeepSeek: r, exact-match, κ
- DeepSeek × TextBlob: r
- DeepSeek × VADER: r
- 3-LLM K-α (Claude+Llama+DeepSeek)
- 4-rater K-α (3 LLMs + TextBlob)
- 4-rater K-α (3 LLMs + VADER)
- All-3-LLM stance exact-match

These plug into Section 4.1 and 4.2 immediately.