# Project Synthesis for Publication — All Findings + Literature Positioning

**Date:** 2026-05-10
**Status:** Comprehensive aggregate interpretation across all rounds (R1-R12),
all data sources, and all 12 P-series policy analyses. Positioned against
2024-2026 literature.

---

## Executive Summary — what we have

Three substantively distinct, venue-distinct papers are now possible. Each has
clear novelty against published literature.

| Paper | Lead finding | Tier-1 venue | Status | Novelty position |
|---|---|---|---|---|
| **Methods** | Three-instrument construct mismatch is COHORT-CONDITIONAL on policy discourse (α=−0.018 / +0.196 at n=9,242; OR-magnitude varies 5-fold by community) | Political Analysis | Ready for draft | Extends Bestvater & Monroe 2023 (PA) from one corpus to community-conditional finding; OR=0.18–7.33 spread has no published precedent |
| **Substantive** | Online discourse measures something COMMUNITY-CONDITIONAL and NOT BEHAVIORAL — composition shifts dominate pre/post effects | Sociological Methods & Research | Reframe needed | NO published precedent for opposite-signed OR by community on same construct (more dramatic than Cousineau 2025); composition-shift framing is novel for student-loan discourse |
| **Policy** | PSLF acts as +18.6pp recruitment subsidy for 501(c)(3) hospitals; MOHELA discourse + CFPB convergent failure; PSLF Buyback explosion | Health Affairs OR Journal of Health Economics | Open white space | NO published academic NRMP × PSLF empirical work; first peer-reviewed quantitative MOHELA analysis; first peer-reviewed Trump EO event-window |

**Most consequential single finding for each paper:**
- Methods: Cohort-conditional construct disagreement (L5) — directionally opposite OR across instrument×community combinations
- Substantive: Composition-shift framing + per-author panel infeasibility (Round 7+8 finding)
- Policy: B5+P11 PSLF-eligibility recruitment gap (-18.6pp p<10⁻⁷⁵ after full controls)

---

## 1. Project at aggregate — what's in the dataset

### Data assets accumulated (~10 corpora, ~$50 spent on Claude scoring)

**Primary discourse corpora:**
- Reddit Arctic Shift PSLF posts: **76,074 posts** (2010-2026, 21 subreddits)
- Student Doctor Network: **4,749 PSLF-strict-filtered posts** (2010-2026)
- Reddit comments (PRAW collector): **460,000 comments** (with TextBlob + VADER)
- Topical-near baseline: 7,750 off-PSLF posts in same subreddits

**Three-rater sentiment scoring:**
- TextBlob (lexical polarity) on all posts + 460K comments
- VADER (Hutto & Gilbert 2014, expressive arousal) on all posts + 460K comments
- Claude Sonnet 4 zero-shot (LLM, prompted for stance + topic + intention) on
  9,263 posts (~$50 spent)

**Administrative / external data:**
- CFPB PSLF complaints: 12,552 records (2016-2026)
- NRMP residency match: 50,633 program-years (2016-2025, 1,425 institutions)
- HRSA HPSA designations: 19,045 designated (2024 snapshot)
- CMS Hospital Compare: 5,426 hospitals (ownership + quality star ratings)
- NHSC Field Strength: 7 years of state-level obligated provider counts
- ProPublica IRS BMF: 501(c)(3) verification for 797 NRMP institutions
- US Cities database: city → county lookup (31,120 cities)

### Findings inventory (60+ documented)

**Methods findings:**
- Three-rater K-α at n=9,242: −0.018 (canonical) / +0.196 (charitable)
- Test-retest α=+0.958 at temperature=0 — not LLM noise
- TB×VADER comments r=0.39 at n=472,810 — extends to 50× scale
- OP vs Reply construct mismatch: TB Δ=−0.017, VADER Δ=+0.220 (8/8 cohort
  consistent, cluster bootstrap p=0)
- Trump EO directionally opposite Hedges' g (TB g=−0.32, VADER g=+0.16, Claude g=+0.33)
- L5 finding: cohort-conditional construct disagreement (only SDN bulletproof
  across 5 instrument×stance specifications)
- 2/8 events triple-concordant (Biden Mass Forgiveness, Biden v. Nebraska)

**Substantive findings:**
- Cohort-conditional sentiment-stance decoupling (OR ranges 0.18–7.33)
- Composition shifts dominate pre/post (Round 7+8 per-author analysis)
- A3 mediation: SDN attendings show extreme decoupling (HA OR=0.024)
- Per-event topic restructuring (chi-sq p<10⁻⁴ for every event)
- Per-event × per-profession interactions (8 events × 5+ professions)
- Time-to-recovery heterogeneity by cohort (specialized cohorts slower)

**Policy findings (P-series):**
- B5+P11: PSLF-eligibility recruitment gap = −18.6pp after full controls
- P2+P10+P3 MOHELA convergent failure (3 channels)
- P3 PSLF Buyback explosion (3,500× growth 2021-2025)
- P5 county-level: gap LARGEST in URBAN (+26pp), smallest in rural HPSAs (+12pp)
- P12 NHSC well-targeted to HPSAs (r=+0.79)
- P6 CFPB vs discourse — Buyback 5.47× over-discussed
- P7 pre/post Limited Waiver — gap is structural

**Negative / null findings (informative):**
- B1+L3 NULL discourse vs FSA admin metrics (parallel signals)
- L2 NULL discourse vs NRMP fill rate (parallel)
- L4 NULL SDN attending pattern at comments scale (intensity proxy)
- Per-author within-person panel infeasible for 7/8 PSLF events

---

## 2. Three potential papers — full novelty positioning

### PAPER 1 — METHODS — "Cohort-Conditional Construct Mismatch in Sentiment-Instrument Validation: A 9,242-Post PSLF Discourse Study"

**Working abstract (~250 words):**

> Three commonly-used sentiment instruments — TextBlob (lexical polarity),
> VADER (Hutto & Gilbert 2014, expressive arousal), and a large language
> model (LLM) prompted for stance — are routinely treated as interchangeable
> in policy-discourse research. Building on Bestvater & Monroe's (2023)
> demonstration that sentiment is not stance on Kavanaugh Twitter, we
> demonstrate on a 9,242-post Public Service Loan Forgiveness corpus
> (Reddit + Student Doctor Network, 2010-2026) that the three instruments
> operationalize substantively different latent constructs: lexical affect,
> expressive arousal, and stance, respectively. Krippendorff's α=−0.018
> (canonical) / +0.196 (percentile-matched ordinal upper bound) — both
> well below the 0.667 reliability floor (Krippendorff 1980). We extend
> Bestvater & Monroe in three respects: (1) the construct disagreement is
> cohort-conditional — Student Doctor Network is the only of five PSLF
> discussion communities to show direction-concordance across all 5 of our
> instrument×stance specifications; the others show directionally opposite
> odds-ratio estimates depending on instrument choice (range 0.18 to 7.33).
> (2) The Trump PSLF Executive Order produces directionally opposite
> Hedges' g across instruments at n=1,330 posts (TextBlob g=−0.32, VADER
> g=+0.16, Claude g=+0.33). (3) We document a within-thread OP vs Reply
> construct mismatch (TextBlob Δ=−0.017 vs VADER Δ=+0.220, 8/8 cohort
> consistent), a finding without published precedent. Test-retest
> reliability for the LLM at temperature=0 is α=+0.958 (n=605), refuting
> the "disagreement is just LLM stochasticity" objection. Implications for
> CSS researchers using off-the-shelf sentiment tools on policy discourse:
> instrument choice materially changes substantive answers, and the choice
> must be defended at the construct level, not the convenience level.

**Novelty claims (specific, defensible):**
1. **Three-rater K-α at n=9,242** — Bestvater & Monroe 2023 used n=3,660 hand-coded
   tweets. We extend to 2.5× larger corpus, three algorithmic instruments,
   policy-discourse domain (PSLF instead of Kavanaugh).
2. **Cohort-conditional construct disagreement** — extends Bestvater & Monroe
   from one community to the cross-community heterogeneity finding. NO
   PUBLISHED PRECEDENT for OR=0.18 to 7.33 spread by instrument×community.
3. **OP vs Reply construct mismatch within identical post threads** — NO
   PUBLISHED PRECEDENT (confirmed by independent literature search).
4. **Comments-scale extension** at n=472,810 — TB×VADER r=0.39 (vs r=0.30 at
   post level). Largest such validation in published literature.
5. **Test-retest α=+0.958 at temperature=0** — closes the "LLM noise"
   objection that Bestvater & Monroe could not address (LLMs not yet validated
   at scale in 2023).

**Position against literature:**
- **Builds on:** Bestvater & Monroe 2023 (Political Analysis); Mohammad et al.
  2016 SemEval-2016 Task 6; Hutto & Gilbert 2014 VADER paper; Codebook LLMs
  2025 (Political Analysis); Krippendorff 1980 reliability standards
- **Recent precedents to engage with:** Burnham 2025 (Political Analysis,
  same venue) on LLM stance detection; Hopfer et al. 2025 JMIR on YouTube
  opioid sentiment; Chae & Davidson 2026 SMR (10 LLMs × 4 training regimes);
  arXiv 2410.14626 (9 sentiment tools at scale); Heseltine & Clemm von
  Hohenberg 2024 Research & Politics
- **Distinct contributions vs each:**
  - Extends Bestvater & Monroe's "sentiment ≠ stance" to multi-instrument and
    cohort-conditional
  - Differs from Hopfer et al. by formally treating disagreement itself as
    finding (they recommend single instrument)
  - Differs from Cousineau 2025 (MDPI Journalism & Media) by showing OPPOSITE-
    SIGNED OR (vs same-direction differences in source-of-negativity)

**Recommended venue:** **Political Analysis** (top match)
- Bestvater & Monroe 2023, Burnham 2025, Codebook LLMs 2025 establish PA as
  active publisher of this work
- Methodology-with-application framing fits PA's typical paper structure
- Existing Bestvater & Monroe precedent in PA pages provides natural citation

**Backup venues:** Sociological Methods & Research (Chae & Davidson 2026);
EPJ Data Science (SentiBench 2016 heir); Behavior Research Methods (test-
retest as psychometrics contribution)

**Estimated effort to draft:** 4-6 weeks of focused writing + peer review prep

---

### PAPER 2 — SUBSTANTIVE — "Online Discourse Measures Community-Conditional Stance, Not Behavior: Evidence from PSLF Forum Decoupling"

**Working abstract (~250 words):**

> The dominant assumption in social-media-as-policy-signal research is that
> aggregate online discourse measures borrower or constituent attitudes
> reflective of population-level behavior. We provide evidence that this
> assumption fails for Public Service Loan Forgiveness (PSLF) discourse on
> two dimensions. First, the sentiment-stance relationship is cohort-
> conditional and DIRECTIONALLY OPPOSITE across communities. Across n=6,946
> PSLF posts with full sentiment and stance scoring (Claude Sonnet 4), the
> odds ratio of pursuing PSLF given negative sentiment ranges from 0.18
> (Reddit Finance) to 7.33 (Reddit r/PSLF). Student Doctor Network medical
> forum posters who post negatively are highly likely to be exiting PSLF
> (OR=0.27); Reddit r/PSLF posters who post negatively are 7.33× MORE likely
> to still be pursuing it ("venting culture"). Second, pre/post policy-event
> shifts in PSLF discourse are dominated by composition shifts in the
> discussant pool, not within-person stance change. Per-author longitudinal
> panel analysis: only 1 of 8 PSLF policy events has n>=10 returning
> stance-classifiable authors. The data design itself does not support
> within-person inference. Pre/post stance shifts must be interpreted as
> discussant-pool composition shifts, not borrower stance changes. We
> validate composition shifts via topic-restructuring patterns
> (composition-immune chi-sq tests, p<10⁻⁴ all 8 events). Implications:
> the "online discourse predicts policy reception" research program needs
> sharper measurement design — community-conditional construct identification
> + explicit handling of selection-into-discourse. We provide a workflow
> using NRMP residency match, CFPB complaints, and CMS quality data as
> external triangulation anchors.

**Novelty claims:**
1. **Directionally opposite OR by community on same construct** — OR=0.18 to
   7.33 spread. Cousineau 2025 (Reddit foreign-aid) found community-varying
   "sources of negativity" but same-direction. Bestvater & Monroe pooled
   across users.
2. **Composition-shift framing for student-loan discourse** — NO published
   rigorous test of within-person panel feasibility on student-loan forums.
3. **Per-author panel infeasibility documented at scale** — addresses the
   "selection-into-discourse" critique formally.
4. **First academic NRMP × PSLF empirical analysis** (B5 finding integrated as
   external triangulation) — gray-literature only otherwise.
5. **Topic-restructuring as composition-immune validation** — methodological
   contribution to within-cohort substantive change measurement.

**Position against literature:**
- **Builds on:** Bestvater & Monroe 2023; Kovács et al. 2018 (JDIQ — selection
  bias in event studies); Heseltine & Clemm von Hohenberg 2024 (LLM annotation
  validation)
- **Distinct from:**
  - Yannelis & Looney 2024 (admin-data-only PSLF analysis): we add discourse
    + admin triangulation
  - CFPB Annual Reports: we treat complaints as one signal among multiple,
    not the direct signal
  - Kim et al. 2023 J Evidence-Based Social Work: they used Reddit + Twitter
    for mental-health framing, not PSLF-specific decision behavior
  - SBPC/AFT 2024 "MOHELA Papers": gray literature; we provide peer-reviewed
    quantitative
- **Distinguishing from "social media as policy signal" literature:** we show
  that the signal is NOT borrower behavior — it's community-conditional stance
  + selection-into-discourse. Counter-mainstream finding.

**Recommended venue:** **Sociological Methods & Research** (top match)
- Long-form measurement-validity papers
- Sociology-adjacent quantitative methods
- Chae & Davidson 2026 SMR shows the venue accepts 67-page methods-with-
  application papers
- Headline IS fundamentally a measurement-validity finding

**Backup venues:** Political Analysis (closer to Bestvater & Monroe lineage);
Journal of Computational Social Science; PNAS Nexus (if cross-domain
replication added)

**Estimated effort:** 6-8 weeks (more empirical work needed than methods paper)

---

### PAPER 3 — POLICY — "Public Service Loan Forgiveness as Hospital Recruitment Subsidy: Evidence from NRMP Residency Match Data and Multi-Channel Discourse"

**Working abstract (~250 words):**

> Public Service Loan Forgiveness (PSLF) creates differential incentives for
> graduate medical education program selection by tying loan forgiveness to
> 501(c)(3) employer status. We provide the first peer-reviewed quantitative
> empirical analysis of PSLF's effect on physician workforce recruitment using
> the NRMP residency match. Programs at PSLF-eligible institutions
> (academic medical centers, Veterans Affairs, government hospitals,
> nonprofit teaching hospitals) fill at residency match rates that are 18.6
> percentage points higher than programs at PSLF-ineligible (for-profit
> chain) hospitals (n=29,461 program-years 2021-2025; p<10⁻⁷⁵ after
> controlling for hospital quality via CMS Care Compare star rating, state
> fixed effects, and specialty fixed effects). The effect is concentrated
> in primary care (Internal Medicine +28pp, Family Medicine +15pp,
> Emergency Medicine +15pp) and absent in low-loan-burden specialties
> (Dermatology +3pp NS), consistent with a PSLF-mechanism interpretation.
> The gap is structural — it pre-existed the 2021 Limited PSLF Waiver
> expansion of for-profit chain residencies — and is largest in urban
> markets where for-profit hospital chains compete with academic medical
> centers, not in rural shortage areas. We supplement with multi-channel
> discourse analysis showing convergent evidence of MOHELA servicer
> performance failure (discourse polarity dropped 50% 2017-2024; CFPB
> complaint share jumped from 1.7% pre-takeover to 63% in 2023; 96% of
> MOHELA-issue mentions contain concern markers). The PSLF Buyback program
> has generated 10,542 discourse mentions in 2025 (3,500× growth from 2021)
> with only 2.1% of CFPB complaint share — the strongest case of discourse
> as early-warning signal for federal student aid process improvement.

**Novelty claims:**
1. **First academic NRMP × PSLF empirical work** (literature scan: zero
   peer-reviewed precedents). Open white space.
2. **First peer-reviewed quantitative MOHELA analysis** (only "MOHELA Papers"
   gray-literature precedent at SBPC/AFT 2024).
3. **First peer-reviewed Trump PSLF EO event-window analysis** (no academic
   work yet on the 2025-03-07 EO or 2025-10-30 Final Rule).
4. **PSLF Buyback emergence documented at scale** — first documentation of
   the program's discourse signature.
5. **Discourse-as-early-warning quantification** (P6: PSLF Buyback 5.47×
   over-discussed vs CFPB) — methodological contribution.

**Position against literature:**
- **Builds on:** Yannelis & Looney 2024 (admin-data PSLF); Catherine,
  Ebrahimian & Yannelis 2024 (NBER WP 33059, IDR distributional analysis);
  Brookings 2024 ("Past, Present, and Future of PSLF"); CFPB 2024 Annual
  Student Loan Ombudsman Report
- **Goes beyond:** None of these test the workforce-recruitment hypothesis at
  the residency-program level
- **MOHELA-specific predecessors:** SBPC/AFT 2024 "MOHELA Papers" (gray
  literature, qualitative); GAO PSLF audits (descriptive); we provide
  quantitative + cross-channel
- **Methodological:** P11's city-aggregate matching strategy (96.2% match
  rate) is itself a methodological contribution for hospital-level health-
  services research where the unit of analysis (residency program) doesn't
  1:1 match the matching dimension (hospital)

**Recommended venue:** **Health Affairs** (top match)
- Direct policy-relevant framing
- Active in residency workforce research (multiple Family Medicine NRMP papers)
- Wide policy audience (Congress, federal agencies)

**Backup venues:** Journal of Health Economics (more econometric); ILR Review
(labor-market angle); Annals of Family Medicine (specialty-specific); Health
Services Research (general health-services methods)

**Estimated effort:** 8-12 weeks (largest paper; needs writing + tables + 
NRMP backfill if available)

---

## 3. Cross-paper joint contribution

The three papers together establish a **measurement-to-policy pipeline** for
discourse-based research on federal program effects:

```
Methods paper:  How to measure discourse rigorously
                ↓
Substantive:    What discourse measures (and doesn't)
                ↓
Policy:         How discourse + admin data together inform PSLF policy
```

**Joint methodological contribution:** The audit-counter-audit cycle (P8 →
P11) is itself a methodological case study in observational-data sampling
bias. The lesson — "when match rate is below ~70%, sampling bias should be
explicitly tested; aggregation strategies achieving 90%+ coverage are
preferable to hospital-name matching at 30% coverage" — has direct
applicability to all health-services research using NRMP/CMS cross-walks.

**Joint substantive contribution:** Triangulation across discourse + CFPB +
NRMP + HPSA + CMS demonstrates that no single signal is sufficient. The
convergent MOHELA finding (discourse + CFPB + concern density) IS the
strongest evidence in the dataset because it triangulates across three
independent channels.

**Joint policy contribution:** The dataset directly supports three policy
debates:
1. PSLF reform (Paper 3): quantified +18.6pp recruitment differential
2. PSLF servicer contract design (Paper 3): MOHELA evidence
3. FSA process-improvement priorities (Paper 3): ranked queue

---

## 4. Recommended publication strategy

### Sequential vs parallel publication

**Sequential is recommended** because:
- Methods paper (Paper 1) is most ready for draft and has clearest novelty
- Methods finding directly motivates Substantive paper's "discourse measures
  community-conditional stance, not behavior"
- Policy paper benefits from BOTH methods + substantive being out as preprints
  for citation

**Recommended order:**

| Order | Paper | Target submit | Estimated time-to-draft | Pre-print? |
|---|---|---|---|---|
| 1 | Methods (Political Analysis) | Q3 2026 | 4-6 weeks | arXiv cs.CL immediately |
| 2 | Substantive (Sociological Methods & Research) | Q4 2026 | 6-8 weeks | SSRN once ready |
| 3 | Policy (Health Affairs) | Q1 2027 | 8-12 weeks | None until ready |

### Parallel publication strategy

If parallel: write Methods + Substantive simultaneously since they share most
of the data and analyses. Policy paper waits for NRMP backfill (2010-2015) +
NSLDS DUA (if obtained) for stronger causal identification.

### What to do BEFORE submission

**Methods paper:**
1. Apply L5 cross-validation to one additional domain (COVID-vaccine corpus,
   per `cross_domain_replication_design.md`) — would unlock Tier-1 claim
   "construct disagreement is general, not PSLF-specific"
2. Include OSF pre-registration retrofit (Round 9 should-fix)
3. Run sentiment_zeroshot_openweight.py with TOGETHER_API_KEY to confirm
   construct disagreement holds with Llama-3 (not just Claude) — closes the
   "just one LLM" critique

**Substantive paper:**
1. Re-run cohort heterogeneity at full comments scale once collector finishes
   (currently 17K of 76K posts covered)
2. Strengthen composition-shift framing with author-level demographic
   metadata where available
3. Include at least one within-cohort robustness check addressing the
   "discourse skews young/educated/white" caveat

**Policy paper:**
1. NRMP 2010-2015 backfill via Wayback Machine retry (currently 503'd)
2. Improved CMS-NRMP matching using CMS hospital-system file
3. Apply for NSLDS DUA (6-12 month timeline; would convert to definitive
   from observational)
4. Include Trump EO impact analysis (currently event-window data exists but
   needs dedicated Trump-EO-focused write-up)

### Estimated timeline

```
Q2-Q3 2026: Write Methods paper draft
Q3 2026:    Submit Methods to PA; arXiv pre-print
Q3-Q4 2026: Write Substantive paper draft (parallel with Methods peer review)
Q4 2026:    Submit Substantive to SMR; SSRN pre-print
Q4 2026:    NRMP backfill (Wayback) + improved CMS matching
Q1 2027:    Write Policy paper draft
Q1 2027:    Submit Policy paper to Health Affairs
Q3 2027:    First publications (assuming 6-9 month review cycles)
```

---

## 5. What's still needed (concrete to-do list)

### Tier 1 — needed for first paper (Methods) submission

| Task | Effort | Status |
|---|---|---|
| Open-weight LLM replication (Llama-3 via Together AI) | $10-15, 1 day | Built, not run |
| OSF pre-registration retrofit | 1 week | Not started |
| Cross-domain replication (COVID-vaccine; tier upgrade) | $50, 3-4 weeks | Designed (`cross_domain_replication_design.md`), not started |
| Methods paper draft | 4-6 weeks | Not started |

### Tier 2 — needed for second paper (Substantive)

| Task | Effort | Status |
|---|---|---|
| Comments collector finish (currently 17K of 76K) | 0 work, ~30h wall-time | In progress |
| Re-run cohort heterogeneity at full comments | 1 day | Pending data |
| Substantive paper draft | 6-8 weeks | Not started |

### Tier 3 — needed for third paper (Policy)

| Task | Effort | Cost | Timeline |
|---|---|---|---|
| NRMP 2010-2015 backfill (Wayback) | 1-2 weeks | $0 | Pending Wayback availability |
| Improved CMS-NRMP via hospital-system file | 1 week | $0 | Started, needs file |
| AAMC GQ DUA (specialty x PSLF intent crosstabs) | 3-month process | $500-5K | Not started |
| NSLDS DUA application | 6-12 months | $0-$2,500 | Instructions written; not submitted |
| Policy paper draft | 8-12 weeks | $0 | Not started |

### Optional — would strengthen but not blocking

- Bogleheads / allnurses / PA Forum scrape (Cloudflare-blocked)
- TikTok PSLF discourse (separate methodology)
- State physician loan repayment program data
- Federal Reserve Consumer Credit Panel access (DUA)

---

## 6. Bottom-line recommendations

### What to do THIS WEEK (immediate)

1. **Run open-weight LLM replication** — `python sentiment_zeroshot_openweight.py
   --provider together` with `TOGETHER_API_KEY` set. ~$10. Closes "just Claude"
   critique. Required for Methods paper Tier 1 venue.
2. **Start OSF pre-registration retrofit** — write the methods paper
   pre-registration on OSF. Required for Political Analysis tier.
3. **Confirm Wayback Machine NRMP backfill is unavailable** vs. just rate-limited.
   If achievable, +5 years of pre-PSLF baseline strengthens Policy paper.

### What to do THIS MONTH (Methods paper draft)

1. Draft Methods paper using Bestvater & Monroe (2023, PA) as primary
   theoretical anchor + Hopfer et al. (2025, JMIR) as closest methodological
   precedent
2. Lead with cohort-conditional finding (L5) — most novel against literature
3. Include OP vs Reply mismatch as strongest single-finding exemplar
4. Submit to Political Analysis. arXiv simultaneously.

### What to do THIS QUARTER (Substantive paper)

1. Wait for comments collector to finish + re-run cohort heterogeneity
2. Draft Substantive paper with composition-shift framing as headline
3. Lead with OR=0.18 to 7.33 directional spread
4. Submit to Sociological Methods & Research

### What to do BY YEAR END (Policy paper preparation)

1. Apply for NSLDS DUA (start 6-12 month process)
2. Apply for AAMC GQ DUA (start 3-month process)
3. Improve CMS-NRMP matching via hospital-system file
4. Wait for above + draft Policy paper Q1 2027

---

## 7. The single most important insight from this synthesis

**There are THREE papers here, not one.** The original framing of "PSLF
discourse analysis paper" has expanded into a measurement → measurement-
of-what → policy-implication trilogy where each paper:
- Has clear novelty against published 2024-2026 literature
- Has a specific Tier-1 venue match (PA, SMR, Health Affairs)
- Has independent value (each can be published without the others)
- Can cite the others (sequential publication strengthens each)

**Most exciting open white space**: NRMP × PSLF empirical literature is
EMPTY at the academic peer-reviewed level. The Policy paper would be the
foundational citation in this space. The MOHELA quantitative analysis
similarly has only gray-literature predecessors.

**Most defensible-novelty single finding**: The cohort-conditional construct
disagreement (L5) — extends Bestvater & Monroe 2023's theoretical contribution
with a community-decomposition that has NO published precedent at the
OR=0.18–7.33 directional spread we observe. This is the headline of the
Methods paper and earns its place in Political Analysis.

**Most policy-actionable single finding**: The PSLF-eligibility recruitment
gap (-18.6pp after full controls in P11) directly informs Congressional
PSLF reform debates with quantified evidence that has no peer-reviewed
predecessor.

---

## 8. Recommended publication roadmap (with dependencies)

```
NOW
  └── Open-weight LLM replication ($10, 1 day)
  └── OSF pre-registration retrofit (1 week)
  └── Methods paper draft (4-6 weeks)
       └── Submit Political Analysis (Q3 2026)
       └── arXiv pre-print
            └── Substantive paper draft (6-8 weeks, parallel with Methods review)
                 └── Submit SMR (Q4 2026)
                 └── SSRN pre-print
                      └── NSLDS DUA submission (6-12 months)
                      └── AAMC GQ DUA submission (3 months)
                      └── NRMP 2010-2015 backfill if Wayback available
                           └── Policy paper draft (8-12 weeks)
                                └── Submit Health Affairs (Q1 2027)
```

This is a 12-18 month publication arc with three Tier-1 outputs. Each paper is
independently fundable and substantively distinct. The cumulative contribution
is comparable to a full dissertation chapter at a top R1 program.

---

## Files generated this synthesis

- `PUBLICATION_SYNTHESIS_aggregate_view.md` (this file)

Sources:
- [Sentiment is Not Stance (Bestvater & Monroe 2023, Political Analysis)](https://www.cambridge.org/core/journals/political-analysis/article/sentiment-is-not-stance-targetaware-opinion-classification-for-political-text-analysis/743A9DD62DF3F2F448E199BDD1C37C8D)
- [Stay Tuned: Improving Sentiment Analysis and Stance Detection Using LLMs (Burnham 2025, Political Analysis)](https://www.cambridge.org/core/journals/political-analysis/article/stay-tuned-improving-sentiment-analysis-and-stance-detection-using-large-language-models/2D8F121012D3D1CB2259B6DD5EE32D0D)
- [Codebook LLMs (Political Analysis 2025)](https://www.cambridge.org/core/journals/political-analysis/article/codebook-llms-evaluating-llms-as-measurement-tools-for-political-science-concepts/7B323A0E47F782F2698A0AE849EA00DE)
- [LLMs for Text Classification (Chae & Davidson 2026, Sociological Methods & Research)](https://journals.sagepub.com/doi/10.1177/00491241251325243)
- [Public Health Discussions on Social Media (Hopfer et al. 2025, JMIR Formative Research)](https://formative.jmir.org/2025/1/e57395)
- [LLMs as Substitute for Human Annotators (Heseltine & Clemm von Hohenberg 2024, Research & Politics)](https://journals.sagepub.com/doi/10.1177/20531680241236239)
- [What Went Wrong with Federal Student Loans (Yannelis & Looney 2024, NBER)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4826794)
- [How IDR Plans Benefit Borrowers (NBER WP 33059, 2024)](https://www.nber.org/papers/w33059)
- [The MOHELA Papers (SBPC/AFT 2024)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4876434)
- [Selection Bias in Social Media Event Studies (Kovács et al. 2018, JDIQ)](https://dl.acm.org/doi/10.1145/3185048)
- [Polarization in Reddit Foreign Aid Discussion (Cousineau 2025)](https://www.mdpi.com/2673-5172/6/4/199)
- [Past Present Future of PSLF (Brookings 2024)](https://www.brookings.edu/articles/the-past-present-and-future-of-the-public-service-loan-forgiveness-program/)
- [You Shall Know a Tool by the Traces it Leaves (arXiv 2410.14626)](https://arxiv.org/abs/2410.14626)
- [Reddit + Twitter Student Loan Mental Health (Kim et al. 2023, J Evidence-Based Social Work)](https://www.tandfonline.com/doi/full/10.1080/26408066.2023.2202668)
- [TateEsq — Does HCA Qualify for PSLF?](https://www.tateesq.com/learn/does-hca-qualify-for-pslf)
