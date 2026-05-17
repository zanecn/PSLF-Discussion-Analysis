# Paper 6 Draft-Ready Template — REFRAMED R17++ #6 (multi-policy comparison; PLOS One primary)

**Status:** Ready to scaffold; **R17++ #6 boost: MULTI-POLICY COMPARISON** (expand from PSLF-only to multiple student-loan policy events) + revised venue target
**Target venue (R17++ #6 revised primary):** ***PLOS One*** (broad scope, ~50% acceptance, fast cycle)
**Target venue (R17++ #6 secondary):** ***Cureus*** (high-accept open-access backup; ~70-80%)
**Target venue (R17++ #6 alternative):** *JMIR Formative Research* (only if reframed as digital-health-formative work)
**Length:** 2,000-2,500 words (slightly longer to accommodate multi-policy comparison)
**Working title (REFRAMED):** *Online Discourse as a Real-Time Policy Thermometer: A Multi-Event Pre-Post Analysis of Reddit and SDN Student-Loan Discourse Sentiment, 2023–2026*

## R17++ #6 BOOST STRATEGY (added 2026-05-17 final)

**Why revise:** R17++ #5 targeted *JMIR Formative Research* which was a scope mismatch (JMIR Formative publishes digital-health-intervention formative work, not policy-discourse analysis). Boost strategy: switch primary to PLOS One (better-fit broad-scope venue) + add multi-policy comparison to strengthen the "discourse-as-policy-thermometer" claim.

**Boost: ADD MULTI-POLICY COMPARISON (~3-4 weeks of analysis + ~3-4 weeks of writing; total realistic timeline 8-10 weeks per R17++ #6 review — NOT 2 weeks as earlier outline iterations stated. Per agent review: ITS with autocorrelation correction, overlapping-events sensitivity, placebo test, OSF pre-registration are all non-trivial additions to the 2-week estimate. See `DATA_ACQUISITION_PLAN_R17pp6.md` for data acquisition + `PAPER_TODOS_R17pp6_REVIEW.md` for full P6 critical-path TODO list):**

Add 3-4 additional student-loan policy events beyond Trump EO 14235 + ED Final Rule:
1. **Biden v. Nebraska SCOTUS** (argument Feb 2023; ruling June 2023)
2. **SAVE plan introduction** (July 2023) + **SAVE plan litigation** (2024)
3. **Payments restart** (Oct 2023 effective date)
4. **PSLF reform announcements** (2022 limited waiver expansion + 2023 IDR adjustment)

**New data needed:**
- **Additional Reddit r/StudentLoans Arctic Shift corpus** — Arctic Shift API pull for r/StudentLoans posts spanning 2023-2026; ~1 week of API pulls + scoring with TextBlob/VADER/Claude. Free.
- **Event-window dictionary** — compile dates + descriptions for each event; ~0.5 day.
- **Optional: CFPB Complaints Database** — public download with complaint counts by date/issue type; correlate sentiment shifts with complaint volume changes. ~2-3 days. Strengthens behavior connection.

**Total boost effort:** 8-10 weeks of focused work (per R17++ #6 review correction; earlier "2 weeks" estimate was unrealistic by 4-5×). Breakdown: 1 week OSF pre-registration + 3-4 weeks analysis script + 3-4 weeks writing + revision cycle.

**Framing (R17++ #6 REVIEW REFRAME — earlier "thermometer" framing was at risk of falsification by existing data):** The R17++ #5 outline proposed "discourse-as-policy-thermometer" framing claiming discourse magnitude scales with policy magnitude. **Existing cohort heterogeneity comments data already suggests this framing is at risk of being falsified**: Trump EO produced larger discourse effects (max |g|=0.65 for Nursing) than Biden v. Nebraska SCOTUS ruling (max |g|=0.09), opposite of what magnitude-scaling story predicts. **R17++ #6 honest reframe**: "**Cohort-conditional sentiment dynamics around PSLF policy events**" or "**A pre-registered event-study analysis of five federal student-loan policy interventions in online PSLF discourse, 2023–2026**." The five events are CHARACTERIZED, not assumed to scale predictably. Discourse magnitude vs policy magnitude is the HYPOTHESIS the analysis tests, not the headline assertion.

**Realistic acceptance:** *PLOS One* ~50% with multi-policy framing; *Cureus* ~75% backup (high accept but lower prestige); *JMIR Formative* ~20-35% if framed differently. Combined "in print by ERAS" probability ~80-85%.

---

# Original outline below — to be expanded per R17++ #6 multi-policy boost during drafting

**Status (LEGACY R17++ #5):** Ready to scaffold (data exists; analysis script needs writing; ~2 weeks effort — **REVISED in R17++ #6 REVIEW to 8-10 weeks** after agent identified hidden methodological complexity: autocorrelation correction, overlapping-events sensitivity, multiple-breakpoint identification, placebo test, OSF pre-registration filing before any analysis touch)
**Target venue (LEGACY R17++ #5 primary):** *JMIR Formative Research*
**Target venue (LEGACY R17++ #5 secondary):** *JAMIA Open*
**Target venue (LEGACY R17++ #5 tertiary):** *PLOS One* / *Cureus*
**Length:** 1,500-2,000 words (short report)
**Working title (LEGACY):** *Public Service Loan Forgiveness Discourse Sentiment Around the Trump Executive Order: A Pre-Post Analysis of Reddit and SDN PSLF-Related Posts, 2024–2026*

**Added:** 2026-05-17 (R17++ #5) — small additional short report identified during rigorous validity review as a clean, independent venue contribution that uses existing data without creating salami-slicing concerns with P1/P2.

---

## Why this paper

A small, focused, independent contribution that uses already-collected data without overlapping P1/P2/P3 claims:

- **Clean event-study design:** Trump Executive Order 14235 signed March 7, 2025; ED Final Rule published Oct 31, 2025; effective July 1, 2026. Three discrete events with timestamps create natural pre/post windows.
- **Already-collected discourse data:** 528K Reddit comments + 4,749 SDN posts + 76K Reddit Arctic Shift PSLF posts span 2010–2026; the 2024–2026 window captures pre/post both events with adequate sample.
- **Independent venue:** *JMIR Formative Research* or *JAMIA Open* don't overlap with EPJ DS / JCSS / JGME audiences — no salami-slicing concern.
- **Fast cycle:** *JMIR Formative Research* publishes in ~3 months from submission to in-print; first NS-application-relevant venue with the shortest cycle.
- **Estimated effort:** ~2 weeks of analysis + ~2 weeks of writing during research year.

## Design

**Pre-event windows:**
1. Pre-EO baseline: Jan 1, 2024 – Mar 6, 2025 (~14 months)
2. EO-signed window: Mar 7, 2025 – Oct 30, 2025 (~8 months between EO and Final Rule)
3. Final-Rule-published window: Oct 31, 2025 – present (data through 2026)

**Outcome variables:**
- Mean sentiment score (TextBlob polarity, VADER compound, Claude pslf_sentiment ordinal)
- Volume of PSLF-related posts/comments per week
- Topic distribution shifts (using BERTopic or simple keyword-based categorization)
- Stance distribution shifts (using Claude pslf_stance classifier; pursuing/considering/rejecting/completed/unknown)

**Pre-registration commitment:** This is genuinely PRE-event for the July 2026 effective-date follow-up window. Pre-register at OSF before final analysis (see `OSF_PREREGISTRATION_cross_domain.md` for template).

## Section structure (JMIR Formative Research short-report format)

### Abstract (~250 words; structured)

**Background:** Trump Executive Order 14235 (March 7, 2025) "Restoring Public Service Loan Forgiveness" + the subsequent ED Final Rule (Federal Register Oct 31, 2025; effective July 1, 2026) are the largest federal restructurings of PSLF since the program's 2007 establishment. Whether and how online PSLF discourse responded to these policy shocks has not been quantitatively characterized.

**Objective:** Document sentiment, volume, and stance distribution shifts in Reddit and SDN PSLF-related discourse across three discrete policy windows: (1) pre-EO baseline (Jan 2024 – Mar 6, 2025), (2) EO-signed (Mar 7, 2025 – Oct 30, 2025), (3) Final-Rule-published (Oct 31, 2025 onwards).

**Methods:** Interrupted time series analysis on Reddit Arctic Shift PSLF corpus (n=76,074 posts) + SDN Playwright PSLF corpus (n=4,749 posts) + Reddit comments corpus (n=528,051 comments scored). Sentiment via TextBlob polarity, VADER compound, and Claude Sonnet 4 zero-shot pslf_sentiment (ordinal); stance via Claude pslf_stance. Weekly aggregation; piecewise linear models with breakpoints at each policy event.

**Results:** [TO COMPUTE] expected: significant negative shift in mean sentiment + significant increase in post volume around EO signing; further shift around Final Rule publication; stance distribution shifts toward "rejecting" or "unknown" in post-event windows.

**Conclusions:** [TO COMPUTE] expected: documenting that policy shocks produce measurable downstream sentiment + stance shifts in online PSLF discourse, validating online-discourse-as-policy-indicator framings for future PSLF reform debate.

### Introduction (~300 words)

[INSERT BLOCK: Trump EO 14235 + ED Final Rule policy context; Brookings 2024 + CFPB 2024 PSLF debate context; online discourse as a real-time policy-sentiment indicator (cite Tsugawa & Ohsaki 2015, Choi/Aiello/Varga/Quercia 2020, Park & Conway 2017).]

### Methods (~400 words)

[INSERT BLOCK: corpus description, sentiment scoring methodology (cite Paper 1 for cross-instrument convergence), stance classification methodology (cite Paper 2), interrupted time series analysis approach.]

### Results (~400 words; 2 figures, 1 table)

**Table 1:** Weekly mean sentiment + post volume by policy window (pre-EO baseline / EO-signed / Final-Rule-published) for each platform × instrument combination

**Figure 1:** Time series of weekly mean sentiment with policy-event vertical lines and piecewise-linear model fits overlaid

**Figure 2:** Stance distribution stacked-bar chart by policy window (pursuing / considering / rejecting / completed / unknown)

### Discussion (~300 words)

[INSERT BLOCK: substantive interpretation; comparison to P2 cohort-conditional discourse findings; implications for online-discourse-as-policy-indicator framing.]

**Limitations:** Sentiment shifts measure online-discourse sentiment, not actual borrower decisions; selection bias toward Reddit/SDN users; PSLF discourse may be confounded by other student-loan policy events in the window.

**Future work:** Borrower-level PSLF utilization analysis using NSLDS data (DUA pending — see `NSLDS_DUA_APPLICATION_CHECKLIST.md`); replication when 2027+ data become available; cross-policy comparison with other student-loan policy windows.

---

## Pre-submission checklist

- [ ] Write `analyze_post_eo_sentiment_shift.py` script
- [ ] Generate Figure 1 (time series with breakpoints) + Figure 2 (stance distribution by window)
- [ ] Pre-register analysis plan at OSF BEFORE running the post-Final-Rule analysis (genuine pre-registration)
- [ ] Compute interrupted time series breakpoint statistics
- [ ] Cite Papers 1 + 2 at submission (or "in revision" with proof-stage update)
- [ ] Verify citations at author level (R17++ rule)

## Expected timeline

- **Late Aug 2026 (research year start):** Pre-register at OSF
- **Sep-Oct 2026:** Write analysis script + generate figures (~2 weeks)
- **Oct-Nov 2026:** Draft abstract + Introduction + Methods (~1 week)
- **Nov-Dec 2026:** Draft Results + Discussion + co-author review (~2 weeks)
- **Dec 2026:** Submit to *JMIR Formative Research* (primary)
- **Feb-Mar 2027:** Decision (typically 2-3 months at JMIR Formative)
- **Apr-May 2027:** Revisions
- **Jun-Jul 2027:** In print before ERAS Sept 2027

Total: **~3-4 weeks of effort** spread across Aug-Dec 2026.

## Acceptance probability (R17++ #5 honest estimate)

- *JMIR Formative Research* primary: **~40-50%** (clean event-study design, well-scoped, addresses live policy event)
- *JAMIA Open* secondary: **~30-40%**
- *PLOS One* tertiary: **~50%**
- *Cureus* backup: **~70-80%** (high-acceptance pay-to-publish venue; CV line if needed)

## Strategic value

- **Independent venue, no overlap with P1/P2:** clean addition to publication count without salami-slicing risk
- **Fast cycle:** *JMIR Formative Research* in-print by mid-2027 is achievable with Dec 2026 submission
- **Pre-registration credit:** OSF pre-reg is itself a separate citable artifact + demonstrates methodological rigor
- **Sets up PGY-1 follow-up:** post-2027 follow-up with longer post-effective-date window is natural continuation

## Source files

- `PSLF-Discussion-Analysis/reddit_comments_pslf.csv` — 528K Reddit comments (already scored TB + VADER)
- `PSLF-Discussion-Analysis/reddit_arctic_shift_pslf.csv` — 76K Reddit Arctic Shift PSLF posts
- `PSLF-Discussion-Analysis/forum_pslf_discussions.csv` — 4,749 SDN posts
- `PSLF-Discussion-Analysis/zeroshot_sdn_*.csv` — Claude-scored SDN posts (sentiment + stance + topic)
- `scripts/analyze_post_eo_sentiment_shift.py` — TO BE WRITTEN (interrupted time series)
- `OSF_PREREGISTRATION_cross_domain.md` — pre-registration template (already exists for COVID-vaccine extension; adapt for post-EO PSLF)
- `MASTER_LOCKED_NUMBERS.md` + `MASTER_REFERENCE_LIST.md`
