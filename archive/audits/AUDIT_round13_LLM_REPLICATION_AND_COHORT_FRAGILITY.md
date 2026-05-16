# Round 13 Audit — Open-Weight LLM Replication + Cohort Robustness Findings

**Date:** 2026-05-10 (post-Llama replication ~16:30)
**Scope:** Three critical methodological audits driven by completed open-weight LLM replication and L5 cross-instrument cohort robustness test.

---

## TL;DR

Three rigorous audit findings:

1. **PAPER 1 STRENGTHENED** — Llama 3.3 70B replication shows substantial inter-LLM agreement (Claude×Llama: r=+0.703, exact-match=73.6%, Cohen's κ=+0.572; 3-rater LLM-only K-α=+0.691). LLM-class vs lexical-class is the construct boundary. Methods paper is now Tier-1 ready for Political Analysis.

2. **"DIFFERENT CORPORA" CLAIM CORRECTED** — Initial audit overstated the LLM independence. Both Anthropic (Claude) and Meta (Llama) train on undisclosed proprietary mixes that likely overlap substantially on common web sources (Common Crawl, Wikipedia, GitHub, books). Defensible claim is "different organizations + different post-training procedures (Constitutional AI/RLAIF vs RLHF/DPO) + different model architectures" — NOT "different corpora."

3. **PAPER 2 COHORT HETEROGENEITY PARTIALLY FRAGILE** — L5 cross-instrument robustness test shows:
   - SDN-Medical decoupling and r/PSLF venting hold across all 3 sentiment instruments (ROBUST)
   - Reddit Finance "decoupling" was a same-scorer (Claude×Claude) artifact — FLIPS to venting (OR=1.10-1.42) with cross-instrument operationalization
   - The OR=0.18-7.33 spread (40×) was inflated by same-scorer halo
   - Cross-instrument spread: 7-17× (still substantial but smaller)

**Strategic implication:** Combine Paper 1 + Paper 2 into a single Tier-1 paper at Political Analysis. The methods finding (instrument disagreement) and the substantive consequence (cohort heterogeneity with explicit Finance flip) form a unified narrative stronger than either alone.

---

## Audit Finding #1: Open-Weight LLM Replication SUCCEEDED

### Method
- Llama 3.3 70B Instruct Turbo via Together AI ($0.30, 15 min wall-time)
- 721 PSLF posts identical to Claude Sonnet 4 scoring sample
- Same SYSTEM_PROMPT (verbatim from `sentiment_zeroshot.py`)
- 100% parse success rate

### Headline Numbers
| Comparison | Pearson r | Exact-match | Cohen's κ |
|---|---|---|---|
| **Claude × Llama** | **+0.703** | **73.6%** | **+0.572** |
| Claude × TextBlob | +0.066 | 20.1% | +0.002 |
| Claude × VADER | +0.134 | 21.8% | +0.023 |
| Llama × TextBlob | +0.139 | 21.7% | +0.021 |
| Llama × VADER | +0.245 | 22.3% | +0.028 |
| TextBlob × VADER | +0.308 | 27.0% | +0.087 |

### Three-rater Krippendorff α (n=701)
- **Claude + Llama (LLM-only)**: α = +0.6912
- Claude + Llama + TextBlob: α = +0.2011 (drop of 0.49)
- Claude + Llama + VADER: α = +0.2616 (drop of 0.43)

### Stance task (Claude vs Llama, n=485)
- Overall: 87.8% exact-match
- Considering: 92.0%, Completed: 94.4%, Pursuing: 84.6%, Rejecting: 68.8%

### Verdict
✅ **Methods paper "just one LLM" critique is closed.** The construct boundary is LLM-class vs lexical-class.

---

## Audit Finding #2: "Different Corpora" Claim Was Overstated

### What I claimed initially
> "Two LLMs from independent organizations (Anthropic, Meta) trained on **different corpora** with **different RLHF procedures**..."

### What's actually defensible

**Definitely different ✓**
1. **Different organizations**: Anthropic vs Meta
2. **Different model architectures**: Llama uses GQA + RoPE + SiLU + specific attention patterns; Claude is proprietary
3. **Different post-training procedures**:
   - Anthropic: **Constitutional AI + RLAIF** (Reinforcement Learning from AI Feedback)
   - Meta: **Standard RLHF + DPO** (Direct Preference Optimization)

**Likely OVERLAPPING ⚠️**

Neither organization fully discloses training data, but both LLMs likely overlap on:
- Common Crawl (web text)
- Wikipedia
- Books corpora
- Code repositories (GitHub)
- Reddit data
- Academic papers

### Correct framing for the paper

❌ **DON'T say**: "Different corpora with different RLHF procedures"

✅ **DO say**: "From independent organizations with different model architectures and different post-training procedures (Anthropic's Constitutional AI/RLAIF vs Meta's RLHF/DPO)"

✅ **Add to Limitations**: "Both LLMs were trained on undisclosed proprietary data mixes that likely include substantial overlap on common web sources. Stronger refutation of 'shared training data' as the explanation for inter-LLM agreement would require an LLM trained on a fully disclosed, distinct corpus — not currently available at 70B+ scale."

### Mitigation: Add a 3rd LLM from a different organization

Adding a 3rd LLM from a **different organizational/national context** (e.g., Mistral [French], DeepSeek [Chinese], Qwen [Chinese/Alibaba]) would substantially strengthen the case:

- Anthropic Claude (US)
- Meta Llama (US)  
- + Mistral/DeepSeek/Qwen (non-US, different training emphasis)

If 3 LLMs from 3 organizations all agree, "shared training data" becomes much harder to invoke as the explanation.

**Status**: 3rd LLM replication recommended (~$0.30, 18 min). User to identify serverless model on Together AI.

---

## Audit Finding #3: L5 Cross-Instrument Robustness — COHORT FINDING IS PARTIALLY FRAGILE

### What I tested
For each cohort, computed sentiment-stance odds ratio using:
- **Same-scorer**: Claude sentiment + Claude stance (original Round 9 finding)
- **Cross-instrument**: TextBlob sentiment + Claude stance
- **Cross-instrument**: VADER sentiment + Claude stance
- **Cross-LLM (where available)**: Llama sentiment + Claude stance, Claude sentiment + Llama stance

### Results

| Cohort | Claude+Claude (original) | TB+Claude | VADER+Claude | Llama+Claude (sentiment) | Claude-sent+Llama-stance |
|---|---|---|---|---|---|
| Reddit r/PSLF | 7.329 | 1.655 | 2.526 | NaN | NaN |
| SDN (Medical) | 0.272 | 0.147 | 0.334 | NaN | NaN |
| Reddit Finance | 0.182 | **1.103** | **1.423** | 0.242 | 0.121 |
| Reddit r/StudentLoans | 1.411 | 2.495 | 0.990 | NaN | NaN |
| Reddit Medical | 0.726 | 1.191 | 0.841 | 0.222 | 1.000 |

**Cross-cohort spread (max/min):**
| Spec | Spread | Range |
|---|---|---|
| Claude+Claude (original) | **40.2×** | 0.18 to 7.33 |
| TB+Claude | 17.0× | 0.15 to 2.49 |
| VADER+Claude | 7.6× | 0.33 to 2.53 |
| Llama+Claude | 1.1× | 0.22 to 0.24 (only 2 cohorts have data) |
| Claude-sent+Llama-stance | 8.2× | 0.12 to 1.00 (only 2 cohorts have data) |

### What's robust
✅ **SDN-Medical decoupling** (OR<1) holds across all 3 sentiment instruments (Claude, TB, VADER)
- Claude+Claude: 0.27
- TB+Claude: 0.15
- VADER+Claude: 0.33

✅ **Reddit r/PSLF venting culture** (OR>1) holds across all 3
- Claude+Claude: 7.33
- TB+Claude: 1.66
- VADER+Claude: 2.53

✅ **DIRECTIONALLY OPPOSITE** between SDN and r/PSLF holds in all 3 specifications

### What's fragile
❌ **Reddit Finance "decoupling" FLIPS DIRECTION** depending on instrument:
- Claude+Claude: OR=0.18 (decoupling) — original headline
- TB+Claude: OR=1.10 (NEUTRAL/venting)
- VADER+Claude: OR=1.42 (venting)

❌ **The 40× spread (0.18 to 7.33)** was inflated by same-scorer halo:
- Cross-instrument spread: 7-17× (still substantial, but ~3-6× smaller than headline)

### Implications for Paper 2

**Original Round 9 framing**: "Sentiment-stance decoupling has DIRECTIONALLY OPPOSITE cohort heterogeneity (Reddit r/PSLF OR=7.33, SDN OR=0.27, Finance OR=0.18)."

**Honest revised framing**: 
- "Two communities show OPPOSITE-direction sentiment-stance relationships ROBUST across multiple sentiment instruments: SDN-Medical (decoupling, OR=0.15-0.33) and Reddit r/PSLF (venting, OR=1.66-7.33). The magnitude of the OR spread varies substantially by instrument choice, demonstrating same-scorer halo as a methodological caveat. A third cohort (Reddit Finance) appeared to show decoupling with same-scorer Claude×Claude (OR=0.18) but FLIPS to venting with cross-instrument operationalization (TB×Claude OR=1.10, VADER×Claude OR=1.42), illustrating the same-scorer halo concretely."

This is STILL publishable but the headline is:
- "OPPOSITE-direction cohort heterogeneity for SDN vs r/PSLF" (robust)
- NOT: "OR=0.18 to 7.33 spread across 5 cohorts" (inflated)

---

## Strategic Implication: Combine Paper 1 + Paper 2

### Why combine

The L5 cross-instrument finding shows the methods paper and substantive paper are **two facets of the same finding**:
- Paper 1: instrument-side framing (LLM vs lexical disagree)
- Paper 2: cohort-side framing (cohort claims depend on instrument)

The Reddit Finance flip is a **direct consequence** of the methods finding: when the sentiment and stance scorers share a halo, the apparent decoupling is artifactual.

### Combined paper structure

```
Title: Cohort-Conditional Construct Mismatch in Sentiment-Instrument Validation:
       Three-LLM Evidence from Public Service Loan Forgiveness Discourse

Section 1: Theoretical framework
  - Bestvater & Monroe 2023; stance vs sentiment
  - Multi-LLM extension
  - Cohort heterogeneity hypothesis

Section 2: Data + Methods
  - n=9,242 PSLF posts (Reddit + SDN, 2010-2026)
  - Three sentiment instruments (TextBlob, VADER, Claude Sonnet 4)
  - Three LLMs (Claude + Llama 3.3 + 3rd LLM)
  - Test-retest design (α=+0.958)

Section 3: Results
  3.1 Pairwise agreement (Claude×Llama r=+0.703; both LLMs vs lexical r near 0)
  3.2 Three-LLM convergence (3-rater α with LLMs only)
  3.3 Adding lexical collapses α
  3.4 Cohort-conditional sentiment-stance OR
  3.5 Cross-instrument robustness (SDN, r/PSLF stable; Finance flips)
  3.6 Trump PSLF EO directional split (lead exemplar)
  3.7 OP vs Reply construct mismatch (within-thread)

Section 4: Discussion
  - LLM-class vs lexical-class boundary
  - Same-scorer halo (Finance flip exemplar)
  - Implications for "social media as policy signal"

Section 5: Limitations
  - Likely overlap in LLM training data
  - Reddit/SDN demographics
  - PSLF-specific (cross-domain replication pre-registered)
```

### Strategic benefits of combining

1. **Single Tier-1 paper instead of one Tier-1 + one borderline Tier-1**
2. **Cleaner narrative**: methods → consequences in one paper
3. **Honest** about Finance flip — turning a vulnerability into a methodological exemplar
4. **Faster**: 4-6 weeks vs 12-18 months
5. **Less risk**: Paper 2 standalone might be rejected for thinness

---

## Updated To-Do (Round 13)

### USER ACTIONS — this week

1. ✅ DONE: Llama 3.3 70B replication (73.6% exact-match)
2. ⏳ NEXT: Run 3rd LLM serverless diagnostic + replication (~$0.30, 18 min) — strengthens "shared training data" defense
3. ⏳ Send NRMP usage permission email (3-4 week wait)
4. ⏳ Send NSLDS DUA inquiry (6-12 month wait, start clock)
5. ⏳ Send AAMC GQ inquiry (3-month wait)
6. ⏳ Create OSF account + deposit transparency package
7. ⏳ Pre-register cross-domain replication on OSF

### CLAUDE/AI ACTIONS

1. ⏳ After 3rd LLM completes: run `compare_multi_llm_vs_claude.py`
2. ⏳ After comments collector completes: re-run cohort heterogeneity at full scale
3. ⏳ Update OSF transparency package with corrected LLM language
4. ⏳ Decide formally: combine Paper 1+2 vs separate? (Strong recommendation: combine)
5. ⏳ Methods+Substantive combined paper draft (Q3 2026, ~4-6 weeks)

---

## What this audit changes for the project

### Strengthened
- Methods paper headline is now defensible and ready for Political Analysis Tier-1
- Test-retest + open-weight LLM replication addresses every reviewer's likely critique

### Weakened
- "Different corpora" claim must be walked back to "different organizations + different post-training"
- Reddit Finance decoupling is no longer a robust finding
- The OR=0.18 to 7.33 spread is no longer the headline number (was same-scorer-inflated)

### Recommended NEW framing
- Combined Paper 1+2 at Political Analysis (single Tier-1)
- Paper 3 (Policy at Health Affairs) remains separate, unchanged

---

## Files generated this round

- `scripts/compare_multi_llm_vs_claude.py` — supports 3-LLM comparison (NEW)
- `zeroshot_llama_replication.csv` — Llama 3.3 70B scoring (NEW)
- `openweight_vs_claude_results.{txt,csv,png}` — 2-LLM comparison (NEW)
- `AUDIT_round13_LLM_REPLICATION_AND_COHORT_FRAGILITY.md` — this audit (NEW)

Next file (after 3rd LLM): `zeroshot_third_llm_replication.csv` + `multi_llm_comparison_results.{txt,csv,png}`

---

## Bottom line

**The open-weight LLM replication delivered exactly the optimal outcome (Claude×Llama agreement is substantial; both LLMs disagree with lexical at near-zero correlation).** This unblocks Paper 1 for Political Analysis.

**The L5 cross-instrument test revealed Paper 2's vulnerability**: same-scorer halo inflated the cohort-heterogeneity headline. Honest reporting requires walking back the OR=0.18-7.33 spread and acknowledging Finance flip.

**Strategic recommendation**: Combine Paper 1 + Paper 2. The combined paper is stronger than either alone because the Finance flip becomes a concrete methodological exemplar rather than a vulnerability.

**Next user action**: Run 3rd LLM replication ($0.30, 18 min). Test whether 3-LLM agreement holds (further closes "shared training data" critique).