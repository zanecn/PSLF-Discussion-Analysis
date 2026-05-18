# User Action Required: Open-Weight LLM Replication

**Time:** ~20 minutes (5 min setup + 15 min compute)
**Cost:** ~$0.29 (Together AI) OR ~$3.60 (OpenAI GPT-4o)
**Importance:** Required for Political Analysis Tier-1 venue (closes "just one LLM" critique)

---

## What this does

Re-scores the same 721 Reddit PSLF posts that Claude already scored, using
either Together AI's Llama 3.1 70B Instruct OR OpenAI's GPT-4o. Then
auto-compares the open-weight LLM's scoring to Claude's scoring to test
whether the construct-mismatch finding generalizes beyond Claude.

**Pre-registered hypotheses** (per `OSF_TRANSPARENCY_PACKAGE.md`):
- Claude vs Open-weight LLM: r > 0.85 expected (LLMs share construct)
- Open-weight LLM vs TextBlob: r < 0.30 expected (LLM ≠ lexical)

If the prediction holds → methods finding generalizes from "Claude says X" to
"LLMs say X". This is the critical evidence for the venue tier upgrade.

---

## Setup (5 minutes)

### Option A: Together AI (RECOMMENDED — $0.29)

1. Get API key: https://api.together.xyz/settings/api-keys
   (sign up if needed; no credit card required for $1 free credit)
2. Set environment variable:

   **Windows PowerShell (current shell):**
   ```powershell
   $env:TOGETHER_API_KEY = "your-key-here"
   ```

   **Windows persistent (recommended):**
   ```powershell
   [Environment]::SetEnvironmentVariable("TOGETHER_API_KEY", "your-key-here", "User")
   ```

3. Verify:
   ```powershell
   echo $env:TOGETHER_API_KEY
   ```

### Option B: OpenAI GPT-4o ($3.60, requires existing OpenAI account)

1. Get API key: https://platform.openai.com/api-keys
2. Set environment variable:
   ```powershell
   $env:OPENAI_API_KEY = "your-key-here"
   ```

---

## Run (15 minutes)

```powershell
cd C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis

# Option A (Together AI):
python ../scripts/sentiment_zeroshot_openweight.py --provider together

# Option B (OpenAI):
python ../scripts/sentiment_zeroshot_openweight.py --provider openai
```

The script will:
1. Pre-flight test on a single PSLF post (verifies API key works)
2. Score 721 posts with the open-weight LLM (~15 min)
3. Auto-compute exact-match rate vs Claude
4. Save: `zeroshot_together_replication.csv` (or `zeroshot_openai_replication.csv`)

---

## Auto-comparison analysis

Once scoring completes, run the comparison:

```powershell
python ../scripts/compare_openweight_vs_claude.py
```

This computes:
- Pairwise sentiment Pearson correlation: Claude vs OW, Claude vs TB,
  Claude vs VADER, OW vs TB, OW vs VADER, TB vs VADER
- Three-rater Krippendorff α: Claude+OW+TB, Claude+OW+VADER, Claude+OW (just LLMs)
- Stance exact-match rate: Claude vs OW
- Per-stance agreement breakdown

Output: `openweight_vs_claude_results.{txt,csv,png}`

---

## Expected results & interpretation

### If predictions hold (most likely):
- Claude vs OW: r=0.7-0.9, exact match 60-80%
- OW vs TB: r=0.05-0.30 (low — LLM ≠ lexical)
- OW vs VADER: r=0.10-0.40 (low — LLM ≠ arousal)

**Verdict:** The construct mismatch is LLM-vs-lexical, not Claude-specific.
Methods paper's headline generalizes. **Required for Political Analysis tier.**

### If Claude vs OW disagrees (less likely):
- Claude vs OW: r<0.50

**Verdict:** Even LLMs disagree among themselves. This is a different but
still publishable finding — "LLM-as-annotator has inter-LLM construct
disagreement on policy discourse" — but reframes the methods paper.

---

## Reporting in Methods paper

Add to Section 3 (Methods):

> "We replicated the construct disagreement test using Llama 3.1 70B Instruct
> via Together AI on the same n=721 posts that Claude Sonnet 4 scored.
> Inter-LLM agreement: Claude vs Llama-3 r=[X], exact match [Y]%. LLM vs
> TextBlob: r=[X]. LLM vs VADER: r=[X]. The construct disagreement we
> document for Claude vs lexical instruments holds for Llama 3 vs lexical
> instruments [confirmed / not confirmed]. This generalizes the methods
> finding from a single proprietary LLM (Claude) to LLM-class (Claude +
> Llama) versus lexical instruments (TextBlob + VADER)."

---

## Pre-registration linkage

Per `OSF_TRANSPARENCY_PACKAGE.md` Section 3.5, this test is pre-specified
with thresholds:
- Inter-LLM r > 0.6 = LLM-class shares construct
- LLM vs lexical r < 0.30 = LLM-class ≠ lexical
- Both passed → construct mismatch finding generalizes

After running, document in OSF with the actual results vs the pre-specified
thresholds.

---

## Troubleshooting

**"TOGETHER_API_KEY not set"**: Verify with `echo $env:TOGETHER_API_KEY`. If
blank, re-run the setx command. May need to restart shell.

**Pre-flight test fails (parse_error)**: API key invalid or rate-limited.
Try the OpenAI fallback.

**Script hangs**: Ctrl+C and check if API service is up at
https://status.together.ai/ or https://status.openai.com/

**Cost overrun**: The script defaults to 721 posts (~$0.29). Use
`--max-posts 100` to test with smaller sample first (~$0.04).
