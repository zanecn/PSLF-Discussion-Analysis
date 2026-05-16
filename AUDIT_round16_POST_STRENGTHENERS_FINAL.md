# Round 16 Post-Strengtheners — Final Publishability State (2026-05-10)

After three Round 16 strengtheners (SDN multi-LLM scoring, paraphrase-robustness, wild-cluster bootstrap), the three Path B papers are now in their **strongest defensible state**.

---

## Acceptance probability evolution

| Paper | Round 14 | Round 15 (issues) | Round 16 (section fixes) | Round 16 (propagated) | **Round 16 (strengtheners)** |
|---|---|---|---|---|---|
| **P1 Methods** | 40-50% | 25-35% | 30-40% | 35-45% | **45-55%** |
| **P2 Substantive** | 35-45% | 20-30% | 22-28% | 30-38% | **30-38%** (no strengthener) |
| **P3 Policy** | 25-35% | 8-15% | 18-25% | 25-32% | **30-37%** (JGME) |

**Headline:** Paper 1 is now in solid Tier-2 territory; Papers 2-3 in moderate Tier-2 territory.

---

## What the strengtheners delivered

### Strengthener 1: SDN multi-LLM scoring ($30, 30 min)

**n_intersection grew 701 → 1001** (Reddit n=701 + SDN n=300).

| Cohort | 3-LLM K-α | 95% CI | Krippendorff floor classification |
|---|---|---|---|
| **Combined (Reddit + SDN)** | **+0.7590** | [+0.7241, +0.7868] | Above 0.667 tentative-reliability floor |
| Reddit subset only | +0.6901 | [+0.6462, +0.7302] | Boundary of tentative-reliability |
| **SDN subset only** | **+0.8306** | **[+0.7870, +0.8661]** | **Above 0.80 satisfactory-reliability floor** |

**Implications for Paper 1**:
- Generalizes beyond Reddit profession-subreddits to a multi-cohort sample
- SDN-only K-α at "satisfactory" reliability is the strongest single number in the paper
- 4-rater drops with TextBlob/VADER are LARGER on the combined sample (−0.42, −0.52) than on Reddit-only — the construct boundary is reinforced
- Resolves Round 15/16 critical issue L0a (was: SDN-omitted)

### Strengthener 2: Paraphrase-robustness test-retest ($5, 7 min)

3-prompt Krippendorff α (sentiment, ordinal) = **+0.9011** [bootstrap CI +0.8571, +0.9380]
- Above pre-specified 0.85 threshold for "true test-retest under prompt variation"
- Stance task: 92-96% pairwise exact-match
- Topic task: 93-95% pairwise exact-match

**Implications for Paper 1**:
- Resolves Round 15/16 critical issue L0b (was: API-determinism-only)
- The paper can now claim *true psychometric test-retest reliability under prompt variation*, not just API determinism
- Moves the test-retest claim from "weak rebuttal of stochasticity objection" to "strong evidence of prompt-robustness"

### Strengthener 3: Wild-cluster bootstrap for Paper 3 ($0, 5 min)

| Spec | n_hostile_clusters | Cluster-robust p | Wild-cluster bootstrap p | Survives α=0.05? |
|---|---|---|---|---|
| S1 (status quo) | 23 | 1.4×10⁻⁷ | <0.0005 | **YES** |
| S2 (HCA-acad reclassified) | 9 | 4.0×10⁻⁹ | 0.017 | **YES** |
| S3 (HCA-acad dropped) | 9 | 3.1×10⁻¹⁰ | 0.006 | **YES** |

**Implications for Paper 3**:
- Resolves Cameron-Miller (2015) small-cluster concern proactively
- Headline survives the small-sample correction in all 3 specs
- The asymptotic SE was overstated (S2 went from 4×10⁻⁹ to 0.017 — 7 orders of magnitude); the paper now reports the honest p-values
- Defensible at JGME / AcadMed methods review

---

## What still cannot be fixed without new data

### Paper 1
- **Construct labels (LLM = stance, lexicon = surface affect) remain unvalidated** against gold-standard human-coded data. Requires hand-coding n=200-300 posts for stance + sentiment (~1 week of human time). Paper 1 L0c remains.

### Paper 2
- **Comments-scale data (n_partial=14K of ~600K) shows Trump EO is concordant** at scale. Full Claude scoring of comments would resolve (~$2,300). Currently acknowledged as §5.3b caveat.
- **Per-author longitudinal panel infeasibility for all 8 events** — property of forum data, not fixable.

### Paper 3
- **HCA-academic-partnership classification cannot be verified without W-2 data** — requires NSLDS DUA (6-12 months); current 3-spec sensitivity bracketing is the best we can do.
- **Within-institution DiD underpowered** (n=7 hostile in both eras) — not fixable.

---

## Remaining drafting work (no more analysis needed)

| Paper | What to do | Time estimate |
|---|---|---|
| **P1 Methods** | Draft from outline (sections 1-8, supplements S1-S8) | 4-6 weeks |
| **P2 Substantive** | Wait for comments collector finish; refresh §5 numbers; draft from outline | 6-8 weeks (incl. comments wait) |
| **P3 Policy** | Draft from outline (sections 1-5, supplements S1-S8); cover letter for JGME | 4-6 weeks |

---

## Path B realistic timeline (post-strengtheners)

| Quarter | Milestone |
|---|---|
| Q3 2026 | Paper 1 (Methods, EPJ DS) drafted, submitted, arXiv pre-print posted |
| Q3-Q4 2026 | Paper 3 (Policy, JGME) drafted parallel to P1; submitted Q4 |
| Q4 2026 | Paper 2 (Substantive, JCSS) drafted, submitted, SSRN pre-print posted |
| Q1-Q2 2027 | Paper 1 acceptance/revision (3-6 month peer review) |
| Q2-Q3 2027 | Paper 3 acceptance/revision |
| Q3 2027 | Paper 2 acceptance/revision |

**First publication target: Q1-Q2 2027** (Paper 1 at EPJ DS).
**All-3-publications target: Q3 2027 - Q1 2028.**

**Best case** (3/3 accepted on first round): 3 Tier-2 publications by Q1 2028.
**Realistic** (2/3 accepted, 1 resubmits): 3 publications by Q2 2028.

---

## Files produced by the three strengtheners

| File | Purpose |
|---|---|
| `sdn_for_multi_llm_scoring.csv` | Sampled 300 SDN posts |
| `zeroshot_llama_sdn.csv` | Llama 3.3 SDN scoring (300 valid) |
| `zeroshot_deepseek_sdn.csv` | DeepSeek V3.1 SDN scoring (300 valid) |
| `paper1_multi_llm_with_sdn_results.txt` | Re-computed K-α with SDN inclusion |
| `zeroshot_sdn_paraphrase_v1.csv` | Claude alt-prompt 1 (200 posts) |
| `zeroshot_sdn_paraphrase_v2.csv` | Claude alt-prompt 2 (200 posts) |
| `paper1_paraphrase_robustness_results.txt` | 3-prompt K-α = +0.9011 |
| `paper3_wild_cluster_bootstrap_results.txt` | All 3 specs survive at α=0.05 |

---

## Honest summary

After 16 audit rounds and 3 strengtheners:
- **Paper 1**: The strongest of the three. Multi-cohort (n=1001) 3-LLM K-α=+0.76 with cohort heterogeneity (Reddit boundary, SDN satisfactory). Paraphrase-robust α=+0.90. Two reviewer-killing limitations (L0a, L0b) resolved. **45-55% acceptance at EPJ DS**.
- **Paper 2**: Mid-strength. Honest "1 robust + 1 mostly + 3 nulls + 1 misalignment" framing. CMV reframed to construct misalignment. Comments-scale Trump EO discrepancy acknowledged. **30-38% at JCSS**.
- **Paper 3**: Cluster-robust + wild-cluster headline survives all 3 HCA-partnership specs. Venue switched to JGME (best fit). **30-37% at JGME**.

**Path B is publishable.** The substantive findings are real, the framing is honest, the limitations are documented. Time to draft.

---

*End of Round 16 post-strengtheners final synthesis.*
