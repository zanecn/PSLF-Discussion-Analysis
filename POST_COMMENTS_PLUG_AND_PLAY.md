# Post-Comments Plug-and-Play Guide

**When the comments collector finishes (currently at ~93%), follow these 3 steps in order. Total time: ~30-45 min. No drafting required during this phase — fully automated.**

---

## Step 1: Verify comments collector is done

Open PowerShell, navigate to project:
```powershell
cd C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis
```

Check the file:
```powershell
ls reddit_comments_pslf.csv
```

If the file size is no longer growing AND the comments collector process has exited, proceed to Step 2.

---

## Step 2: Run the post-comments analysis chain

Single command — the launcher does Step 1 (VADER) sequentially, then Steps 2a-2d in parallel:

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\run_post_comments_chain.ps1
```

**What this does (~15-25 min total):**

1. **VADER on comments** (~5-10 min, sequential): adds `vader_compound` to all ~600K comments
2. **Triangulation with comments** (~10 min, parallel): TB×VADER α at full scale (was α=+0.298 at n=12,601 partial)
3. **OP-vs-Reply** (~5 min, parallel): refresh OP-vs-Reply Δ at full scale
4. **Cohort heterogeneity comments** (~10 min, parallel): refresh 5-cohort × 3-operationalization OR table at full scale
5. **Per-author panel feasibility** (~5 min, parallel): does adding comment-presence unlock more events for within-person panel?

**Outputs produced (paste these into the locked-numbers placeholders):**

| Output file | Goes into |
|---|---|
| `triangulation_comments_results.txt` | Paper 1 §5.5 (TB×VADER α at full scale) |
| `op_vs_reply_results.txt` | Paper 1 §5.5 (TB Δ, VADER Δ at full scale) |
| `cohort_heterogeneity_comments_results.txt` | Paper 2 §5.1 OR table at full scale |
| `per_author_with_comments_results.txt` | Paper 2 §5.5 panel feasibility refresh |

---

## Step 3: Update the master locked numbers

Open `C:\Users\zanen\PSLF_2026\MASTER_LOCKED_NUMBERS.md` and find the rows tagged with ⏳ (TBD). Replace with the new values from the output files.

Specifically:

### Paper 1 §5.5 OP-vs-Reply (in `MASTER_LOCKED_NUMBERS.md` ⏳ section)

Replace:
- TextBlob Δ (OP − reply) = ⏳ → use the actual value from `op_vs_reply_results.txt`
- VADER Δ (OP − reply) = ⏳ → use the actual value
- Same-direction cohorts = ⏳ → from results file

### Paper 2 §5 cohort heterogeneity comments-scale

Open `cohort_heterogeneity_comments_results.txt` and copy the comments-scale OR table into the Paper 2 outline §5.3b (currently has placeholder text about Trump EO concordance at comments scale).

### Paper 2 §5.5 panel feasibility

Open `per_author_with_comments_results.txt`. If MORE events now meet the n≥10 returning-author threshold (currently only Trump EO at n=13 with comments-presence inclusion), update Paper 2 §5.5 table.

---

## After Step 3: drafting can begin

All numbers are now final. Three paper drafts can begin simultaneously:

1. **PAPER_1_DRAFT_READY.md** — open and start writing prose. Reference `MASTER_LOCKED_NUMBERS.md` for any number, `MASTER_REFERENCE_LIST.md` for any citation, `MASTER_DRAFTING_KIT.md` for reusable text blocks.

2. **PAPER_2_DRAFT_READY.md** — same workflow.

3. **PAPER_3_DRAFT_READY.md** — same workflow. Note: Paper 3 has NO comments dependency; it could have started before this step.

---

## Quick sanity check after Step 2

After running the launcher, verify all four output files exist:

```powershell
ls triangulation_comments_results.txt, op_vs_reply_results.txt, cohort_heterogeneity_comments_results.txt, per_author_with_comments_results.txt
```

If any are missing, check the launcher's per-job summary output for that job's error.

---

## Edge cases / troubleshooting

**Q: What if comments collector finishes with errors (some posts not collected)?**
A: That's fine. The analysis pipelines tolerate partial data. Note the actual N in the output files; the qualitative findings should be stable.

**Q: What if cohort heterogeneity at comments scale CONTRADICTS post-scale findings (Round 16 audit flagged this for Trump EO)?**
A: Paper 2 §5.3b already acknowledges this caveat ("post-scale phenomenon may not generalize to comments scale"). Update the §5.3b language with the actual comments-scale numbers.

**Q: What if the per-author panel suddenly unlocks 3-4 events at n≥10 with comments inclusion?**
A: That's a substantial improvement. Update Paper 2 §5.5 table to reflect, and consider adding a sentence in §6 noting that comments-presence enables broader within-person inference than OP-only.

**Q: What if I want to skip the post-comments chain and just draft Paper 1 + Paper 3 first?**
A: Yes, do that. Paper 3 has zero comments dependency. Paper 1 mostly depends on the multi-LLM + paraphrase results which are already locked. Only Paper 1 §5.5 OP-vs-Reply numbers will be slightly stale (current values are partial).

---

## Wall-time summary

| Phase | Time | Cost |
|---|---|---|
| Wait for comments collector (last 7%) | ~few hours? | $0 |
| Step 2: Post-comments chain | ~15-25 min | $0 |
| Step 3: Update master numbers | ~10 min | $0 |
| **Total** | **~30-45 min once collector finishes** | **$0** |

Then drafting begins. The drafting work is 4-8 weeks per paper.

---

*Plug-and-play. After comments finish: 3 commands, 3 file edits, then write.*
