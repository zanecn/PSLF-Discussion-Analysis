# Round 16 Final Publishability Synthesis (2026-05-10)

After two adversarial multi-agent audit rounds (15 + 16) and 19 explicit fixes plus document-wide propagation, this is the final honest publishability assessment for all three Path B papers.

---

## Summary table

| Paper | Venue (revised) | Round 14 estimate | Round 15 (with critical issues) | Round 16 (after section-body fixes) | After full propagation (current state) |
|---|---|---|---|---|---|
| **P1 Methods** | EPJ Data Science | 40-50% | 25-35% | 30-40% | **35-45%** |
| **P2 Substantive** | JCSS | 35-45% | 20-30% | 22-28% | **30-38%** |
| **P3 Policy** | JGME (primary, was JAMA HF) | 25-35% (JAMA HF) | 8-15% (JAMA HF) | 18-25% (JGME) | **25-32%** (JGME) |

**Headline:** All three papers are now **submission-ready as honest, defensible work** — but at LOWER acceptance probabilities than the Round 14 optimistic estimates suggested. The substantive findings survive; the framing has been honestly deflated.

---

## What changed across Rounds 14, 15, 16

### Round 14 (synthesis of prior 13 audits)
- Identified 15 mandatory pre-submission fixes
- Estimated Path B at 40/35/25% (P1/P2/P3)
- Did not verify data against outline claims; relied on user reports

### Round 15 (multi-agent adversarial audit, NEW)
- Three parallel agents independently verified outline claims against actual data
- Found:
  - **Paper 1**: n=701 contains 0 SDN posts despite outline claim of "≥40 per cohort"; "no published precedent" for OP-vs-Reply was wrong; "substantial" agreement framing exceeded Krippendorff thresholds; binning asymmetry (qcut hides much-worse FIXED-threshold LLM-VADER 7% exact-match)
  - **Paper 2**: l5 artifact says ONLY 1/5 cohorts (SDN-Medical) is concordant; outline claimed "two robust patterns"; CMV framing technically wrong (sample-selection, not Podsakoff); 85.6% decoupling partly tautological
  - **Paper 3**: Sample-size BUG (797 → 32,612 inflation from duplicate Mayo Clinic rows); no cluster-robust SE (effective n_hostile ~55 not 763); HCA-academic partnerships misclassified; robustness-ladder framing INVERTED

- Acceptance probabilities revised down to 25/20/8%

### Round 16 (after fixes applied to section bodies)
- Fixes applied to results sections of all 3 papers
- Round 16 audit found: **fixes not propagated to abstracts/intros/conclusions**, creating internal inconsistency (paper claims A in abstract, says NOT-A in results)
- Acceptance probabilities barely moved because reviewers would catch the inconsistency

### Post-Round-16 (this document)
- Full propagation now done across abstracts, intros, related work, discussion, conclusion, critical reminders, locked-results docs, dashboard
- Specific propagations completed:
  - **P1**: All "+0.7211" → "+0.6901 [bootstrap CI]"; abstract "substantial" → "boundary of tentative reliability"; §3.5 cohort honest reframe ("zero SDN posts"); Park 2023 citation added; L0d Together AI / Anthropic API asymmetry caveat added
  - **P2**: Abstract "two robust" → "1 robust + 1 mostly-coupling"; Section 1.2 "CMV" → "construct misalignment"; §1.5 contribution updated; §2.3 retitled; §6.1/§6.3 reframed; conclusion reframed; critical reminders updated; new §5.3b acknowledges comments-scale Trump EO contradiction
  - **P3**: Abstract n=29,461 → n=29,349; venue header → JGME; "structural feature" → "programmatic feature"; abstract β=−18.56 → S1/S2/S3 range; impl checklist marked done

---

## What still cannot be fixed without new data/scoring

### Paper 1 (Methods)
1. **n=701 5-instrument intersection has 0 SDN posts** — fix requires re-scoring n=1500-2000 with proper cohort balance ($30, 1 hour user-action)
2. **Test-retest measures API determinism, not paraphrase robustness** — fix requires re-scoring with 2-3 alternative system-prompt phrasings ($5, 30 min user-action)
3. **Construct labels (LLM = stance, lexicon = surface affect) are unvalidated** — fix requires hand-coding n=200-300 posts as a stance gold standard (~1 week of human coder time)

### Paper 2 (Substantive)
1. **Comments-scale data (~600K Reddit comments) shows Trump EO is concordant** — at scale, the lead exemplar's cohort heterogeneity weakens. Fix requires either (a) full Claude scoring of comments (~$2,300) or (b) acknowledgment that post-scale heterogeneity may not generalize to comments scale (currently acknowledged in new §5.3b)
2. **Per-author longitudinal panel infeasible for all 8 events** — this is a property of forum data, not fixable

### Paper 3 (Policy)
1. **HCA-academic-partnership classification cannot be verified without W-2 data** — fix requires individual-level NSLDS DUA (6-12 month wait, restricted access)
2. **Within-institution DiD is underpowered** (n=7 hostile in both eras) — not fixable with current data
3. **Mechanism (selection vs treatment vs HCA-business-strategy confound) cannot be distinguished without applicant-level NRMP data** — DUA-required, not in current Path B scope
4. **Cameron-Miller wild-cluster bootstrap not implemented** — fixable in 2 hours of code work

---

## What survives all 16 audit rounds (the genuine contributions)

### Paper 1 (Methods)
1. **3-LLM convergence at α=+0.69 [+0.65, +0.73]** — at boundary of tentative reliability per Krippendorff 1980. NOT "substantial" but defensibly different from lexical-class instruments.
2. **Asymmetric construct boundary** between LLM-class and lexical-class instruments, robust to binning choice. The MAGNITUDE of disagreement is much worse under FIXED thresholds (LLM-VADER 7% exact-match) than QCUT suggests.
3. **80.9% three-LLM stance task agreement** — extends LLM-class convergence beyond a single sentiment task.
4. **Test-retest 100% exact-match at temperature=0** demonstrates Claude is API-deterministic (a weaker claim than test-retest reliability under prompt variation).
5. **OP-vs-Reply Δ directional disagreement** (TB negative, VADER positive in 8/8 cohorts) — though TB Δ is small in absolute terms, the directional disagreement is novel in the policy-discourse-text framing.

### Paper 2 (Substantive)
1. **SDN-Medical decoupling pattern** is the only fully cross-instrument-concordant cohort finding (lift_pp=−16.5 pp; OR<1 across all 5 specifications)
2. **Reddit r/PSLF coupling under most operationalizations** (lift_pp=+10.0 pp; 4/5 specs OR>1; 1 spec flips under pursuing-or-completed combined definition)
3. **Reddit Finance construct-misalignment exemplar** — same-scorer says decoupling, cross-scorer estimates noisy with CIs spanning 1.0
4. **Per-event topic restructuring** for all 8 PSLF policy events (chi-sq p<10⁻⁴), instrument-robust though composition-coupled
5. **Per-author longitudinal panel infeasibility** documented across all 8 events as an affirmative methodological finding about forum-discourse data design

### Paper 3 (Policy)
1. **PSLF-hostile fill-rate differential −16 to −18 pp** across 3 sensitivity specifications, all with cluster-robust 95% CIs that exclude zero by wide margins
2. **Specialty heterogeneity** consistent with PSLF financial-incentive theory (large gaps in primary care, near-null in orthopedic surgery — though negative control is power-limited)
3. **First peer-reviewed quantitative analysis of PSLF-eligibility differential** in residency match outcomes at the program-year level
4. **ProPublica IRS-verified PSLF-eligibility classification methodology** is novel for residency programs

---

## Realistic submission timelines (post-fixes)

| Paper | Venue (primary) | Earliest submission | Probability if submitted | If accepted, publication |
|---|---|---|---|---|
| P1 Methods | EPJ Data Science | Q3 2026 (~6-8 weeks of drafting) | 35-45% | Q1-Q2 2027 |
| P2 Substantive | JCSS | Q4 2026 (after P1 submission) | 30-38% | Q1-Q3 2027 |
| P3 Policy | JGME (primary) / AcadMed (secondary) | Q4 2026 (parallel with P2) | 25-32% (JGME), 20-28% (AcadMed) | Q2 2027 |

**All-3-publications target: Q3 2027 - Q1 2028** (Path B realistic).

**Best-case scenario**: 3 of 3 accepted on first round = 3 Tier-2 publications.
**Realistic**: 2 of 3 accepted on first round; 1 needs resubmission to second-choice venue.
**Worst-case**: 1 of 3 accepted; 2 need substantial reframing or move to lower-tier venues.

---

## Action items for the user

### Highest priority (can be done immediately)
1. **Verify the propagation by reading the abstracts of all 3 papers** to confirm they now match the results sections
2. **Draft Paper 1** (most ready; 6-8 weeks)
3. **Draft Paper 3** (parallel-able with Paper 1)

### Recommended pre-submission
4. **Re-score multi-LLM with SDN inclusion** (~$30, 1 hour) — would substantially strengthen Paper 1
5. **Wild-cluster bootstrap for Paper 3** (2 hours of code) — addresses Cameron-Miller small-cluster concern
6. **Paraphrase-robustness test-retest for Paper 1** (~$5, 30 min) — converts API-determinism check to true test-retest

### Optional (would push to higher venue)
7. **Hand-coded n=200-300 stance/sentiment validation set** for Paper 1 — could enable Political Analysis or Political Communication target
8. **Full comments-scale Claude scoring** ($2,300) — would resolve Paper 2 comments-scale Trump EO contradiction

### NOT recommended (defer indefinitely)
- **NSLDS DUA** (6-12 month wait, individual-level data; not needed for Path B Paper 3)
- **AAMC GQ DUA** (survey microdata; not needed for program-level analysis)
- **NRMP applicant-level DUA** (not in Path B scope)

---

## Honest summary

After 16 rounds of audit and ~19 specific fixes plus document-wide propagation, the three Path B papers are at:
- **Paper 1**: methodologically defensible, substantively interesting, internally consistent, with honest acknowledgment of n=701 Reddit-only sample. **Ready to draft.** 35-45% acceptance at EPJ DS.
- **Paper 2**: substantively grounded with one fully robust cohort + one mostly-robust + 3 nulls + 1 construct-misalignment exemplar; comments-scale caveat acknowledged. **Ready to draft.** 30-38% acceptance at JCSS.
- **Paper 3**: cluster-robust headline survives all 3 HCA-academic-partnership specifications; venue switched to JGME. **Ready to draft.** 25-32% acceptance at JGME.

The Round 14 → Round 16 acceptance probability deflation (from 40/35/25% to 35-45/30-38/25-32%) reflects the cost of honest framing: overclaiming would have produced higher-stated probabilities but worse actual review outcomes. The current state is **honestly publishable** — which is a stronger position than the prior 14 audit rounds achieved.

**Path B is viable.** Submit as 3 papers in 2-3 month sequence, target all-3-published by Q3 2027 - Q1 2028.

---

*End of Round 16 final publishability synthesis.*
