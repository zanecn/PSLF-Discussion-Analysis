# Round 16 Strengtheners — User Actions

Three quick wins (~1 week, ~$35) before drafting Paper 1. Do them in any order; each is independent.

---

## Strengthener 1: SDN multi-LLM scoring (~$30, ~30 min wall-time)

**Why**: Removes the Round 15/16 critical issue that the n=701 5-instrument intersection contains 0 SDN posts. Without this, Paper 1's headline only generalizes to Reddit profession-subreddits.

**Already prepared**: 300 stratified SDN posts in `sdn_for_multi_llm_scoring.csv`.

**Run two commands** (copy-paste; need TOGETHER_API_KEY):

```powershell
$env:TOGETHER_API_KEY = "your_together_api_key_here"
cd C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis

# Llama 3.3 on SDN (~15 min, ~$15)
C:\Users\zanen\anaconda3\python.exe ..\scripts\sentiment_zeroshot_openweight.py `
  --provider together `
  --model meta-llama/Llama-3.3-70B-Instruct-Turbo `
  --output zeroshot_llama_sdn.csv `
  --retest-source-csv sdn_for_multi_llm_scoring.csv

# DeepSeek V3.1 on SDN (~15 min, ~$15)
C:\Users\zanen\anaconda3\python.exe ..\scripts\sentiment_zeroshot_openweight.py `
  --provider together `
  --model deepseek-ai/DeepSeek-V3.1 `
  --output zeroshot_deepseek_sdn.csv `
  --retest-source-csv sdn_for_multi_llm_scoring.csv
```

After both finish, paste me the outputs and I'll merge into the multi-LLM intersection (n=701 → ~1000) and re-compute pairwise + K-α.

---

## Strengthener 2: Paraphrase-robustness test-retest (~$5, ~7 min)

**Why**: Round 16 audit flagged that the "100% exact-match test-retest" measures API determinism, NOT test-retest reliability under prompt variation. This converts it to a proper test-retest.

**Run two commands** (need ANTHROPIC_API_KEY; both run on the same n=200 SDN posts):

```powershell
$env:ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
cd C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis

# Paraphrase 1 (alternative wording, same semantic content) — ~$2.50, ~3 min
C:\Users\zanen\anaconda3\python.exe ..\scripts\sentiment_zeroshot_paraphrase.py `
  --prompt-variant 1 `
  --retest-source-csv zeroshot_sdn_temp0_retest.csv `
  --output zeroshot_sdn_paraphrase_v1.csv `
  --sample 200

# Paraphrase 2 (different alternative wording) — ~$2.50, ~3 min
C:\Users\zanen\anaconda3\python.exe ..\scripts\sentiment_zeroshot_paraphrase.py `
  --prompt-variant 2 `
  --retest-source-csv zeroshot_sdn_temp0_retest.csv `
  --output zeroshot_sdn_paraphrase_v2.csv `
  --sample 200

# Compute α across the 3 prompts (baseline + 2 paraphrases) — instant, $0
C:\Users\zanen\anaconda3\python.exe ..\scripts\compute_paraphrase_robustness.py
```

After all three finish, paste me the output of `compute_paraphrase_robustness.py`. If α > 0.85, Paper 1 L0b can be revised to "true test-retest reliability under prompt variation."

---

## Strengthener 3: Wild-cluster bootstrap for Paper 3 (~5 min, $0)

**Why**: Round 16 audit flagged that with 23 hostile clusters in S1 (or 9 in S2/S3), Cameron-Miller (2015) recommend wild-cluster bootstrap to confirm cluster-robust p-values.

**Status**: Already running in background as I write this. Should be done in ~5 min. I'll get the result automatically and bake it into Paper 3.

---

## Total cost / time

| Strengthener | Cost | Time | Boost to acceptance |
|---|---|---|---|
| 1: SDN multi-LLM | ~$30 | 30 min wall | +5pp Paper 1 |
| 2: Paraphrase-robustness | ~$5 | ~7 min wall | +3pp Paper 1 |
| 3: Wild-cluster bootstrap | $0 | 5 min (running now) | +5pp Paper 3 |
| **TOTAL** | **~$35** | **~45 min user time** | **+13pp combined** |

---

## When all three are done

Paste me the outputs of:
- `multi_llm_comparison_results.txt` (re-run after Strengthener 1)
- `paper1_paraphrase_robustness_results.txt` (after Strengthener 2)
- `paper3_wild_cluster_bootstrap_results.txt` (auto-ready from Strengthener 3)

I'll update Paper 1 (with stronger SDN-inclusive intersection + true test-retest), Paper 3 (with wild-cluster confirmation), and re-state acceptance probabilities. Then drafting begins.
