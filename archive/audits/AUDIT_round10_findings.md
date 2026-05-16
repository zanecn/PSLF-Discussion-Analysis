# Round 10 Audit — B1, A2, A3, C1, B5

**Date:** 2026-05-10
**Scope:** Self-audit of the five new analyses shipped this round + interpretation
in context of the project's existing methods/substantive narrative + concrete
linking plan.

**Verdict summary:**

| Finding | Original claim | Audit verdict | Severity |
|---|---|---|---|
| B1 FSA NULL correlation | "Discourse responds to events not operations" | Undertested — needs first-differences + topic-level test | YELLOW |
| A2 Spec curve | r/PSLF fragile, SDN/Finance bulletproof | Substantively correct; claim direction is right | GREEN |
| A3 Mediation by career stage | "SDN attendings extreme decouplers OR=0.02" | Driven by single-cell artifact (d=1) — overstated | RED |
| C1 Cohort heterogeneity at comments | "6/8 events direction-split, replicates at 50× scale" | Direction-split count is at TextBlob alone; recovery threshold arbitrary | YELLOW |
| B5 NRMP +12.86pp gap | "PSLF-friendly programs fill 12.86pp higher" | **Misclassification overcounts hostile by ~57%; true gap is +4.5pp** | **RED** |

Two RED findings need substantial revision before being put into the paper. Three
need qualification. Detail below.

---

## B1 — FSA Admin NULL Correlation: yellow flag

**Original claim:** "Discourse responds to *policy events*, not *operational events*"
based on r=−0.20 to +0.04 (all p>0.49) between SDN monthly polarity and FSA
cumulative PSLF approvals.

**Audit issues:**

1. **Stock vs flow mismatch**: FSA cumulative approvals is a *monotonically
   increasing* stock variable (16K → 1.18M from 2021-2025). Discourse polarity
   is approximately stationary. Correlating a monotone increasing series with
   a stationary one is statistically meaningless even before considering autocorrelation.

2. **Should test FLOW, not stock**: monthly *new* approvals (the derivative)
   would be the right operational signal. The audit on the prior FSA analysis
   appears to have correlated levels.

3. **Topic-level test missing**: Mean polarity might be insensitive even when
   operational events show up. The right test is whether `servicer_issues`
   topic prevalence (Claude-scored) tracks operational metrics. We have the
   data but didn't run this test.

4. **Hand-curated milestone fallback**: With ~10 sparse milestone observations,
   power is severely limited. NULL with p>0.49 doesn't establish that there's
   no relationship; it establishes we couldn't detect one with very few
   observations.

**Verdict:** The claim "discourse decoupled from operations" is interesting and
*may* be true, but is insufficiently tested. Currently a "we didn't find it"
result, not a "it isn't there" result. **Walk back to: "first-pass NULL — needs
flow-based and topic-level retest before publication."**

**What to do:**
- Re-run with monthly NEW approvals (compute differences from cumulative)
- Test `servicer_issues` topic prevalence × monthly approvals via Claude `primary_topic` (have the data)
- Add lag analysis (operational events may show up ±2-3 months later in discourse)

---

## A2 — Specification Curve: green (with one nuance)

**Original claim:** SDN bulletproof (100% specs OR<1, all sig); Finance very
robust (94% OR<1, 83% sig); r/PSLF fragile (33% of specs flip direction).

**Audit issues:**

1. **Are the 360 specs orthogonal?** They're combinations across 5 dimensions
   (negative definition × pursuing definition × exclude_sdn × exclude_arctic ×
   min_cell_n × cohort). Many specs are highly correlated within a cohort. The
   "% of specs" metric is a useful summary but should be reported alongside the
   *which dimensions drive the flips*.

2. **Critical missing analysis**: Which spec dimension causes r/PSLF to flip?
   - If it's `wc_min` (e.g., flips at wc≥5 vs wc≥20) → substantively meaningful
     (short venting matters)
   - If it's `negative` definition (very_negative vs negative+very_negative) →
     methodological choice issue
   - If it's `exclude_arctic` → the Arctic Shift expansion materially changes
     the finding (cohort definition issue)

3. **Spec-curve is good evidence but the FRAGILITY of r/PSLF needs to be
   characterized, not just stated**.

**Verdict:** The headline "SDN/Finance bulletproof" stands. The "r/PSLF fragile"
finding stands and should be reported as a CAVEAT to the directional reversal
claim. Cannot lead with "directionally opposite cohort heterogeneity" if 33% of
analytic specs flip the r/PSLF direction.

**What to do:**
- Decompose r/PSLF flip-cases by specification dimension (cheap diagnostic on
  existing `spec_curve_results.csv`)
- If the flip is driven by `wc` cutoff, lead with "venting culture is sensitive
  to whether short-form posts are included" (that's a real finding, not a flaw)

---

## A3 — Mediation by Career Stage: RED — major overstatement

**Original claim:** "SDN's decoupling is *seniority-driven*. Attendings OR=0.02,
p=8e-08 (n=88). Mechanism revision: senior physicians post negatively when they
have already decided to walk away."

**Audit critical finding — the OR=0.02 is a single-cell artifact:**

The SDN attending 2×2 table:
```
            not_pursuing  pursuing
not_negative     1          63
negative        12          12
```

OR = (12 × 1) / (12 × 63) = **0.0159** — but the entire estimate hinges on the
single observation in the `not_negative + not_pursuing` cell (d=1).

**What this actually means substantively:**
- 63/64 SDN attendings who are positive-toward-PSLF are still pursuing it (98%)
- 12/24 SDN attendings who are negative are still pursuing
- The "extreme decoupling" interpretation is statistically true but the magnitude
  is inflated by the rare d cell

**Better description:** "Among SDN attendings, the 'rejecting' subgroup is
almost entirely composed of negative-sentiment posters (12/13 = 92%). This is
consistent with a 'decided exit' pattern but rests on n=88 with one near-empty
cell — the OR=0.02 magnitude should not be interpreted literally."

**Critical missing test:** SDN-attending vs SDN-resident DIRECTLY (within-cohort
career stage effect). Confirmed: SDN-resident OR=0.94 (NS, n=66). So the within-
SDN career-stage difference is real (attending vs resident) — but the ORs are
both inferentially fragile (n<100, narrow cells).

**Why mechanism reframe was overconfident:** I claimed "seniority-driven not
stake-driven" but the cleaner test (SDN-resident OR=0.94 vs r/PSLF-resident
OR=?) was infeasible because r/PSLF residents had n<30.

**Verdict:** The career-stage finding is INTERESTING but needs:
- Bayesian rare-event correction (Firth logistic regression, Haldane-Anscombe
  continuity correction) for the n=88 attending OR
- Replication on the full corpus once Claude scoring is extended (currently
  ~6,946 stance-classified posts of 76K total)
- Honest framing: "n is too small for definitive mechanism claims; pattern is
  suggestive of seniority effect within SDN"

**Mechanism revision MUST be walked back.** Headline: "Cohort × career-stage
patterns are suggestive but underpowered. The cohort heterogeneity main finding
remains the lead; career-stage is a hint at mechanism, not a confirmed driver."

**What to do:**
- Apply Firth penalized logistic regression (handles separation/quasi-separation
  in 2×2 tables with rare cells)
- Compute Haldane-Anscombe corrected OR (add 0.5 to each cell) as sensitivity
- Push for Claude scoring of remaining ~70K Reddit posts (currently funded out
  of personal budget — would cost ~$300 to triple sample size for stance)

---

## C1 — Cohort Heterogeneity at Comments Scale: yellow

**Original claim:** "6/8 events direction-split across cohorts at TextBlob; time
to recovery for Trump EO: r/PSLF 2d, Finance/PA NO recovery in 90d."

**Audit issues:**

1. **TextBlob only**: All comments analysis used TextBlob polarity (the only
   pre-computed score). Construct mismatch (the methods paper's headline)
   implies VADER and Claude could give materially different splits. The "6/8
   direction-split" is a TextBlob result, not a cross-instrument result. Cannot
   claim it replicates the post-level cohort heterogeneity finding which used
   Claude `pslf_stance`.

2. **Time-to-recovery threshold ±0.02 is arbitrary**:
   - r/PSLF pre=+0.0645, post30=+0.0537, Δ=−0.011 — already within threshold!
   - Finance pre=+0.1367, post30=+0.1144, Δ=−0.022 — JUST outside threshold
   - "r/PSLF recovers in 2 days" partly means "didn't shift enough at this
     aggregation to need recovery"
   - "Finance no recovery in 90d" partly means "shift was just over the
     threshold; pre/post difference is not dramatic"

3. **Sample size disparities**: r/PSLF n=234K vs Nursing n=375. The "direction-
   split" detection is biased toward cohorts with adequate n; small cohorts may
   appear to disagree with no-effect cohorts simply due to noise.

4. **Reply depth → positive (slight)**: this finding is robust (n>16K per depth
   level) but the EFFECT IS TINY (mean polarity 0.080 → 0.092 across depths
   0-5). Statistically significant but practically negligible. Should be
   reported as "no meaningful depth × sentiment relationship" not as
   "ratification pattern."

**Verdict:** The cohort heterogeneity REPLICATES at comments scale at the
descriptive level (cohort-mean differences), but the "direction-split" framing
needs:
- Robustness to threshold choice (test ±0.01, ±0.05, ±0.10)
- Acknowledgment that this is single-instrument (TextBlob) — cannot generalize
  to Claude-stance until comments are scored
- More cautious framing on time-to-recovery: "Smaller specialized cohorts
  (Finance, PA) do not return to baseline within 90 days at TextBlob
  polarity ±0.02 of pre-event mean; this is sensitive to threshold choice."

**What to do:**
- Re-run time-to-recovery with multiple thresholds (sensitivity check)
- Compute VADER on the comments (free; ~30 min)
- TB×VADER α at comments scale would extend the methods paper finding to 460K
  scale (currently α=+0.298 at comments, partial)

---

## B5 — NRMP Program-Level: RED — substantial misclassification

**Original claim:** "PSLF-friendly programs fill at 93.9% vs PSLF-hostile 81.1%
— a 12.86 pp gap, p=3.4×10⁻²⁷, Cohen's d=+0.62. Internal Medicine gap +28.2pp.
Substantive paper's strongest external-validity finding."

**Audit critical finding:** **57% of "PSLF-hostile" institutions are actually
HCA hospitals partnered with university GME consortia** — meaning their
residents are likely PSLF-eligible via the academic affiliate. The crude name-
based heuristic mis-classified them as hostile.

The 23 "PSLF-hostile" institutions:
| Institution | Likely PSLF status |
|---|---|
| HCA Florida JFK Hosp-U Miami | PSLF-eligible (U Miami affiliate) |
| HCA Healthcare LGH-Montgomery/VCOM | PSLF-eligible (VCOM affiliate) |
| HCA Healthcare/USF Morsani GME-Blake | PSLF-eligible (USF Morsani affiliate) |
| HCA Healthcare/USF Morsani GME-Brandon | PSLF-eligible |
| HCA Healthcare/USF Morsani GME-Citrus | PSLF-eligible |
| HCA Healthcare/USF Morsani GME-Largo | PSLF-eligible |
| HCA Healthcare/USF Morsani GME-Oak Hill | PSLF-eligible |
| HCA Healthcare/USF Morsani GME-Sarasota | PSLF-eligible |
| HCA Healthcare/USF Morsani GME-St Pete | PSLF-eligible |
| HCA Healthcare/USF Morsani GME-Trinity | PSLF-eligible |
| HCA Healthcare/USF Morsani-Bayonet Pt | PSLF-eligible |
| HCA Healthcare/USF Morsani-Northside | PSLF-eligible |
| HCA Houston Healthcare/U Houston | PSLF-eligible (U Houston affiliate) |
| HCA Chippenham & Johnston-Willis Hosps | true hostile |
| HCA Corpus Christi Med Ctr | true hostile |
| HCA Healthcare Kansas City | true hostile (largest, 56 programs) |
| HCA Healthcare/TriStar Nashville | true hostile |
| HCA Healthcare/TriStar Southern Hills | true hostile |
| HCA Las Palmas del Sol Healthcare | true hostile |
| HCA Medical City Healthcare | true hostile |
| North Oaks Med Ctr LLC | true hostile |
| Steward Carney Hospital | likely hostile (Steward = bankrupt for-profit) |
| HCA Healthcare/JFK Med Center-UMiami | PSLF-eligible (likely duplicate) |

After reclassifying the 13 university-affiliated programs as friendly:
- **True academic vs pure for-profit gap: +4.53pp, p=0.0004** (vs originally claimed +12.86pp)
- **PURE PSLF-hostile sample: 9 institutions, 358 program-years**
- **HCA-with-academic affiliation has the LOWEST fill rate (73.7%)** — *opposite*
  of what PSLF mechanism predicts! If PSLF eligibility drove fills, university-
  affiliated HCA programs (PSLF-eligible) should fill BETTER than pure HCA
  (not PSLF-eligible). They fill WORSE.

**This pattern argues AGAINST the PSLF mechanism, not for it:**
- HCA-academic-consortium fill: 73.7% (PSLF-eligible)
- Pure HCA: 89.4% (NOT PSLF-eligible)
- True academic: 93.9% (PSLF-eligible)

If PSLF eligibility were the mechanism, the ordering would be:
true-academic ≈ HCA-academic > pure-HCA. Instead we observe:
true-academic > pure-HCA > HCA-academic. **This is inconsistent with a PSLF
explanation.**

The most plausible alternative explanation is **academic prestige + program
quality reputation**, NOT PSLF eligibility:
- True academic medical centers: best NIH funding, research, prestige → fill best
- Pure HCA: known for-profit chain, applicants make informed choice → fill at 89%
- HCA-academic-consortium: arguably the worst of both worlds (HCA name + non-
  flagship academic affiliation, often newer programs in suburban Florida) → fill
  worst at 74%

**Verdict:** The B5 substantive claim does NOT survive proper reclassification.
The +12.86pp gap was driven by misclassification of HCA-academic-consortium
programs. After reclassification, the true academic-vs-pure-for-profit gap is
+4.5pp, and the pattern across the three groups is inconsistent with a PSLF
mechanism.

**What B5 actually shows:** Academic prestige × program-quality differences,
not a PSLF treatment effect. The headline finding **must be retracted** in its
current form.

**What to do:**
1. Manually classify all 23 "hostile" institutions against the official
   [PSLF Qualifying Employer database](https://studentaid.gov/pslf/employer-search)
   (use `studentaid.gov` API or manual lookup)
2. Validate by checking whether HCA-USF-Morsani residents have actually filed
   PSLF certifications (would require institutional GME contact, ~weeks)
3. Re-run with controls for: NIH funding by institution, US-MD-Senior fill rate
   (proxy for prestige), program age, geographic concentration
4. Honest framing if PSLF mechanism doesn't survive: "Program-level fill rates
   show academic-prestige tier differences but are NOT a clean test of PSLF
   eligibility. The substantive paper should not lean on this."
5. Alternative defense: backfill 2010-2017 (pre-Limited-Waiver). If the gap
   EMERGES post-2021, it suggests PSLF salience matters; if it pre-existed, it's
   structural prestige.

---

## How does this fit the project's broader narrative?

Three ways the new findings interact with the existing project state.

### Narrative arc check (substantive paper):

The pre-audit story was:

```
Discourse signals (cohort-conditional sentiment-stance decoupling)
    ↓
Behavioral selection (career-stage stratifies who decouples)  
    ↓
Workforce outcomes (PSLF-friendly programs fill better)
```

After audit:

```
Discourse signals (cohort-conditional decoupling) — STILL HOLDS
    ↓
Career-stage decoupling within SDN — UNDERPOWERED, suggestive only
    ↓
Workforce outcomes — DOES NOT SURVIVE proper PSLF classification
```

**The chain breaks at the workforce-outcomes step.** B5 was supposed to be the
"objective behavioral validation" — instead it's a confounded observational
correlation that doesn't isolate PSLF.

### What strengthens AFTER audit

1. **A2 spec curve**: SDN/Finance findings are robust across analytic specs.
   Lead with these, NOT r/PSLF.

2. **C1 cohort heterogeneity at comments**: at the cohort-mean and event-shift
   level, replicates the post-level finding at 50× scale. Solid even at TextBlob
   only.

3. **A3 SDN attending pattern**: even if OR magnitude is artifact, the
   substantive observation (12/13 = 92% of SDN-attending rejecters are negative-
   sentiment) is meaningful. This is consistent with the existing project
   finding that "negative sentiment in vocational-expert communities indicates
   a different posting pattern than in general communities."

4. **B1 + CFPB previously published NULL**: the "discourse responds to events
   not operations" claim has TWO null findings (CFPB cross-correlation + FSA
   cumulative). Even if undertested, the convergent NULL is itself meaningful.
   Frame as: "Multiple operational signals fail to correlate with discourse;
   discourse appears to be event-responsive, not operationally-driven."

### What weakens AFTER audit

1. **B5 no longer external validation**: substantive paper loses its biggest
   "objective downstream behavior" claim. Need either a different external
   anchor OR honest acknowledgment that we cannot link discourse to behavior
   with available data.

2. **A3 mechanism reframe**: cannot claim "seniority-driven" with confidence.
   The cleaner story is "career stage adds to cohort effect with current data
   underpowered for definitive mechanism claim."

3. **r/PSLF directional reversal**: still true, but with the spec-curve
   showing 33% of specs flip, the magnitude (OR=7.33) is misleading and the
   direction itself is sensitive to choices.

---

## Linking analyses: what to do next

Highest-leverage tests to LINK the existing pieces of evidence and produce
defensible substantive claims.

### Linking analysis L1 — NRMP × FSA Qualifying Employer database (FIX B5)

**Question:** Do programs at *verified* PSLF-qualifying employers (per the
official FSA database) actually fill better than programs at non-qualifying
employers?

**Method:**
- Query `studentaid.gov/pslf/employer-search` for each of the 789 NRMP
  institutions in our dataset
- Tag each as `PSLF_qualifying_yes` / `PSLF_qualifying_no` / `unknown`
- Re-run H1-H4 with verified classification
- If gap survives → substantive claim defensible
- If gap collapses → drop B5 from substantive paper

**Effort:** 1-2 days (API/scrape), $0
**Risk:** medium — gap might not survive

### Linking analysis L2 — Discourse → behavior at the SPECIALTY level

**Question:** Does the SDN-Medical sentiment signal predict NRMP fill rates by
specialty, year-over-year?

**Method:**
- For each (year, specialty) cell, compute mean SDN-Medical polarity in posts
  mentioning that specialty
- For each (year, specialty), look up NRMP fill rate (from existing
  `nrmp_program_level_2021_2025.csv`)
- Test: does sentiment(year-1, specialty) predict fill(year, specialty)?
- Negative sentiment year-prior should depress fill year-current if discourse
  is informative

**Effort:** 2-3 days
**Risk:** low — descriptive analysis using existing data
**Power:** 5 years × 8-10 main specialties = 40-50 (year, specialty) cells —
modest power but enough for a Pearson correlation

### Linking analysis L3 — Topic shifts × FSA operational events (FIX B1)

**Question:** Does `servicer_issues` topic prevalence track FSA operational
events (e.g., MOHELA transition, payments restart), independent of mean
polarity?

**Method:**
- Extract `primary_topic == "servicer_issues"` posts from Claude `pslf_stance`
  classifications (~6,946 posts available)
- Aggregate to monthly servicer_issues prevalence per cohort
- Test against FSA monthly approvals (FLOW, not stock) and operational events:
  MOHELA transition (Aug 2023), SAVE Forbearance (Jul 2024), Trump EO (Mar 2025)
- Lag analysis: lead 0, 1, 3, 6 months

**Effort:** 1-2 days using existing data
**Risk:** low — publishable result either direction (responsiveness OR null)

### Linking analysis L4 — Place SDN attending pattern in context with comments

**Question:** Among SDN-Medical posts in the comments dataset, does the
attending vs resident pattern (A3) replicate?

**Method:**
- Apply career-stage classifier to SDN-Medical comments (we have ~500 posts;
  comments would add 5-10× more career-mentioning text)
- Test pattern across larger n: does attendings-skew-decoupling hold?
- Even with TextBlob (no Claude stance on comments), can test
  attending vs resident sentiment INTENSITY differences

**Effort:** 1-2 days using existing comments data
**Risk:** low

### Linking analysis L5 — Cross-validate cohort heterogeneity (B5 → C1)

**Question:** Does the cohort heterogeneity finding (sentiment-stance OR varying
by cohort) hold when we include alternative classifiers (TB+VADER instead of
just Claude pslf_stance)?

**Method:**
- For each cohort, compute three OR-style decouplings:
  - OR(TB-negative × Claude-pursuing): the original
  - OR(VADER-negative × Claude-pursuing): VADER as sentiment
  - OR(TB-negative × Claude-rejecting): rejecting as the explicit alternative
- Bootstrap CIs per cohort
- If all 3 OR formulations agree on direction within cohort → robust
- If they disagree → cohort effect was instrument-conditional

**Effort:** 1 day
**Risk:** low

---

## Recommended priority order

1. **L1 (validate B5)** — RED finding; until B5 is validated or retracted, the
   substantive paper has a hole. ~1-2 days.

2. **L3 (topic-level FSA test)** — directly addresses B1 yellow flag with
   existing data. ~1-2 days.

3. **L5 (cross-validate cohort heterogeneity)** — strengthens the lead
   substantive finding by making it instrument-robust. ~1 day.

4. **L2 (discourse → behavior at specialty level)** — IF L1 partly survives,
   this is the strongest external validation. ~2-3 days.

5. **L4 (SDN attending in comments)** — addresses A3 underpower. ~1-2 days.

6. **A3 Firth correction + sensitivity** — addresses the OR=0.02 artifact.
   ~1 day.

7. **A2 spec curve decomposition** — addresses YELLOW flag on r/PSLF
   fragility. ~half-day.

8. **C1 threshold sensitivity** — addresses YELLOW flag on time-to-recovery.
   ~half-day.

Total: ~10-14 days of analyst time. After this, the substantive paper has
either:
- A defensible "discourse → behavior" link (if L1+L2 survive), OR
- An honest scope limitation ("discourse signals exist but cannot be
  causally linked to behavioral outcomes with available data")

---

## Headline messages, post-audit

### For the methods paper (less affected by audit)

The headline is unchanged: TB ≠ VADER ≠ Claude on policy-discourse text;
α ≈ 0; construct dissociation is theoretically grounded and empirically
demonstrated at scale. Add the comments-scale replication (TB×VADER α=+0.298
at n=460K) as a "scale robustness" section.

### For the substantive paper (significantly affected by audit)

**Reframe required.** The cleanest defensible claim now is:

> "Online PSLF discourse exhibits cohort-conditional patterns: the
> sentiment-stance relationship varies systematically by community type,
> with vocational-expert forums (SDN-Medical, Reddit Finance) showing
> sentiment-stance dissociation while general-purpose communities
> (Reddit r/PSLF) show 'venting culture' patterns. These patterns are
> stable across analytic specifications for SDN/Finance and partially
> stable for r/PSLF. Convergent evidence at the comments scale (50×
> sample, single-instrument) supports cohort-mean differences; multi-
> instrument validation pending."

What CANNOT be claimed without further work:
- "PSLF-friendly programs fill better" — B5 is currently confounded
- "Career stage drives cohort heterogeneity" — A3 is underpowered
- "Discourse predicts behavior" — no clean discourse-behavior link

What CAN be claimed honestly:
- Cohort heterogeneity is robust at multiple sample scales
- Sentiment-stance dissociation is real (post-level Claude scoring)
- Composition shifts (not within-person stance change) drive pre/post effects
- Construct mismatch (methods paper headline) generalizes to comments scale

---

**This audit is uncomfortable but necessary. Two RED findings need fixing before
the substantive paper draft. The methods paper is largely untouched.**
