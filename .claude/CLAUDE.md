# PSLF Online Discourse Analysis Project

## Overview (Round 7 reframing — 2026-05-08)

This project began as a multi-source sentiment analysis of online PSLF discussion. After Path C event-window Claude scoring (n=4,787 posts with all three scorers) and a Round-7 comprehensive audit, **the substantive headline has been replaced by a methodological one**:

**Primary finding (methodological):** Three commonly-used sentiment instruments — TextBlob (lexical affect), VADER (expressive arousal, Hutto & Gilbert 2014), and Claude Sonnet 4 zero-shot (stance toward PSLF, per the prompt) — operationalize **substantially different latent constructs** on policy-discourse text. Krippendorff's α=+0.17 (percentile-matched ordinal, n=4,787) — well below the 0.667 floor for tentative reliability claims. Pearson r: TB×VADER +0.30, TB×Claude +0.02 (ns), VADER×Claude +0.12. The construct distinction is theoretically grounded in stance vs sentiment (Mohammad et al. 2016, SemEval-2016 Task 6) but its empirical magnitude on policy discourse has not been previously quantified.

**Lead exemplar:** The 2025 Trump PSLF Executive Order produces directionally opposite Hedges' g across the three instruments on the same n=1,047 posts: TextBlob g=−0.39 (more negative-valence vocabulary), VADER g=+0.21 (more affective intensity), Claude g=+0.41 (more stance-positive engagement, "still pursuing PSLF"). This is *not* measurement noise — it is consistent construct dissociation visible across all 8 PSLF policy events.

**Companion methodological finding:** Reddit's 1000-result API cap creates a quantifiable volume-growth artifact when measured against CFPB Consumer Complaints (no cap) as ground truth. R/C ratio grew ~74× from 2017 to 2026 (Q1-May, partial year); CFPB grew ~6.5× — implying ~6-7× real growth + ~10× recency-bias artifact.

**Substantive single-event findings (formerly headline, now demoted):** Pre/post tests show Trump PSLF EO bootstrap-Bonferroni-significant on TextBlob alone (g=−0.39, p_boot=0.006). After Path C: NO event simultaneously survives bootstrap-Bonferroni AND has three-scorer direction concordance. Biden Mass Forgiveness and Biden v. Nebraska SCOTUS are triple-concordant negative but bootstrap-NS or window-confounded.

**Scope clarification (round-4):** This project studies **online PSLF discourse**, not the PSLF-borrower population. Reddit + SDN users skew young, white, male, more educated than the ~1M+ borrower population, and Bogleheads + allnurses are Cloudflare-blocked. Findings should be interpreted as discourse construct measurement, not behavior.

## Repository
- Fork: https://github.com/zanecn/PSLF-Discussion-Analysis
- Upstream: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis
- PR #1: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis/pull/1
- Branch: `playwright-sdn-scraper`

## Data (as of 2026-05-07)
- **9,629 PSLF-relevant posts** strict-anchored filter; **8,788** of those are sentiment-eligible (MIN_WORDS≥20); **7,918** in the legislative-timeline analysis (after the 2009-01-01 to 2026-04-01 date trim).
  - Reddit medical/teacher (legacy CSVs): 605 + 521 = 1,126
  - Reddit professions: 11,793 raw → 3,754 PSLF-filtered (+ length-residualised)
  - SDN Forum: 45,334 raw → 4,749 PSLF-filtered
  - 20 communities (18 subreddits + SDN)
- **Three-scorer sentiment**: TextBlob polarity + VADER compound + Claude Sonnet 4 zero-shot. Pearson correlations: TB×VA r=0.30, TB×CL r=0.02, VA×CL r=0.12 (all p<0.001 except TB×CL p=0.09). Three-rater Krippendorff's α (ordinal, **n=4,787 after Path C event-window fill**): −0.03 with fixed thresholds, **+0.17 with percentile-matched marginals** — both well below the 0.667 floor for tentative reliability claims. Marginal distributions diverge sharply (VADER calls 67% of posts very_positive vs Claude's 4.3%).
- **Strict PSLF filter** (`filter_pslf_relevant` in pslf_search_terms.py) — generic 'forgiveness' terms must co-occur with a PSLF-specific anchor (PSLF/MOHELA/qualifying employer/etc.) within 80 chars
- **Length-residualised analysis**: outcome = residuals of polarity ~ log(word_count) + source + profession (round-4 fix; round-5 added QR rank check to drop perfectly-collinear src/profession dummies for SDN)
- **r/AskReddit baseline** (n=177; small, not length-matched in raw form) + **topical-near baseline** (n=7,750 off-PSLF posts in same subs)

## Key Scripts (in scripts/)
- `collect_forum_data.py` — SDN scraper (Playwright headless + requests/BS4)
- `collect_reddit_professions.py` — Reddit JSON API scraper, year-windowed (round-3 fix)
- `collect_reddit_baseline.py` — r/AskReddit + topical-near baselines
- `collect_reddit_comments.py` — Reddit comment trees (needs PRAW API keys)
- `analyze_multi_source.py` — Cross-platform/profession statistical analysis
- `gen_hires_figs.py` — 300 DPI sentiment comparison + word cloud figures
- `gen_legislative_timeline.py` — Policy event timeline + pre/post analysis (raw + residualised) + sensitivity + bootstrap; emits `legislative_timeline_results.{txt,csv}` artifact alongside figures (round-5)
- `gen_volume_artifact_figure.py` — Reddit/CFPB volume ratio diagnostic
- `analyze_admin_data_correlation.py` — CFPB cross-correlation + R/C ratio
- `confound_audit.py` — Profession × year, length × polarity, pre/post word count tests
- `sentiment_vader.py` — VADER scoring (adds vader_compound columns to CSVs)
- `sentiment_zeroshot.py` — Claude API classifier (Sonnet 4); round-5 added preflight auth check + AuthenticationError fail-fast + 5-error circuit breaker (was silently catching auth errors and burning ~715 calls before this fix)
- `sentiment_triangulation.py` — Round-5: three-scorer Krippendorff's α + per-event Claude pre/post + Figure 7 (TB×VA×CL forest plot). Emits `triangulation_results.{txt,csv}` and `triangulation_figure7.png`.
- `pslf_search_terms.py` — filter_pslf_relevant, anchored regex
- `final_summary.py` — Statistical summary report

## Headline Findings (associational; survive 4 audit rounds)

All effects below are reported as Hedges' g + Glass's Δ_pre (raw) and length-residualised g (round-4 fix). Block-bootstrap p-values (Künsch 1989, B=2000, per-event seed — round-5 fix) reported. Bonferroni α/8 = 0.00625. Canonical numbers live in `legislative_timeline_results.txt`.

| Event | g_raw | g_resid | bootstrap p | parametric p | survives Bonferroni? |
|-------|-------|---------|-------------|--------------|----------------------|
| **Trump PSLF EO** (2025-03-07) | −0.40 | −0.39 | 0.0060 | <0.0001 | ✓ on bootstrap and parametric |
| **Biden v. Nebraska SCOTUS** (2023-06-30) | −0.43 | −0.39 | 0.0065 | <0.0001 | borderline bootstrap (just over 0.00625), ✓ parametric. Window overlaps 2023-10-01 Payments Restart. |
| **SAVE Admin Forbearance** (2024-08-09) | +0.51 | **+0.58** | 0.017 | <0.0001 | ✗ on bootstrap (passes 0.05, fails 0.00625), ✓ parametric |
| **Final Trump PSLF Rule** (2025-10-30) | +0.30 | +0.18 | 0.011 | <0.0001 | ✗ on bootstrap, ✓ parametric. g_resid weakens. |
| **Limited PSLF Waiver** (2021-10-06) | +0.35 | +0.36 | 0.032 | <0.0001 | ✗ on bootstrap, ✓ parametric |
| Payments Restart (2023-10-01) | +0.33 | +0.34 | 0.072 | 0.005 | ✗ borderline. Window overlaps Biden v. Nebraska. |
| IDR Account Adjustment (2022-04-19) | −0.24 | −0.25 | 0.211 | 0.006 | ✗ NS on bootstrap |
| Biden Mass Forgiveness (2022-08-24) | −0.25 | −0.23 | 0.155 | 0.031 | ✗ NS |

**Key correction (round-5)**: prior versions of this table claimed 5 events "survive Bonferroni" by conflating p<0.05 with the Bonferroni threshold. With α/8 = 0.00625 applied strictly to the autocorrelation-corrected bootstrap p, only Trump PSLF EO clearly passes. Biden v. Nebraska is at the boundary. The parametric p column inflates significance because Welch's t ignores within-window autocorrelation; bootstrap is the more honest test.

Key descriptive observations (NO causal claims, NO behavioral interpretation):
1. **The 60-day window following the Trump PSLF EO is the only event with a clear bootstrap-Bonferroni-significant shift** (g=−0.40 raw, g=−0.39 residualised; bootstrap p=0.006 < α/8=0.00625). Direction matches the policy mechanism (rule restricts PSLF processing for "illegal-purpose" employers).
2. **The 90-day window following the SAVE administrative forbearance shows the largest positive shift** (g=+0.51 raw → +0.58 length-residualised; bootstrap p=0.017 — passes 0.05 but does NOT clear Bonferroni). g grows under length adjustment, which is unusual: post-period posts are *shorter* on average, so the residualised effect rules out length confound. Adjacent-event contamination (8th Circuit SAVE injunction Jul 2024, Nov election) is not ruled out.
3. **The 90-day window following Biden v. Nebraska shows the largest negative shift in magnitude** (g=−0.43 raw, g=−0.39 residualised, Glass's Δ_pre=−0.48; bootstrap p=0.0065 — just at Bonferroni boundary). Window overlaps with the October 2023 payments restart; effects not separately identified.
4. **Cross-source baseline calibration**: r/AskReddit length-matched baseline polarity = 0.015 (n=177; small sample, sensitivity to n is open). PSLF medical posts polarity = 0.072. PSLF discussion is *slightly more positive* than typical Reddit when length-adjusted — challenges any "PSLF most negative" framing.
5. **CFPB-sentiment cross-correlation null** (all 13 lags p>0.05 after Bonferroni, first-differenced) — online sentiment and formal complaint volume are decoupled signals, NOT a redundant measurement.
6. **Three-scorer triangulation reveals construct disagreement** (round-5 + Path C, n=4,787 union of five zero-shot subsamples with all three scorers; per-event tests are now well-powered at n_pre=166–610 and n_post=109–437). Krippendorff's α for the three-rater ordinal task is +0.17 with percentile-matched marginals — well below 0.667. Direction concordance is sharper than the early underpowered subsample suggested: **only 2/8 events have all three scorers agreeing on sign — Biden Mass Forgiveness and Biden v. Nebraska SCOTUS, both negative**. Six of eight events have at least one scorer disagreeing on direction. **Critical revision (Path C)**: the Trump PSLF EO is *not* triple-concordant in the well-powered triangulation. TextBlob says g=−0.39 (negative shift, p<10⁻⁶) but Claude says g=+0.41 (positive, p<10⁻⁶) and VADER says g=+0.21 (positive, p=0.0007). The earlier "triple-concordant Trump EO" claim was an artifact of the n=50/side eventstrat subsample. **Net result: zero events are simultaneously bootstrap-Bonferroni-significant AND triple-concordant.** Biden Mass Forgiveness is concordant but bootstrap-NS (p=0.155). Trump EO is bootstrap-Bonferroni-significant on TextBlob but direction-split across instruments. The methodological co-headline (sentiment scorers fundamentally disagree on PSLF text) is *strengthened*; the substantive co-headline (a single robust event finding) is *removed*.

### Analytical Caveats (state explicitly in any write-up)
- Pre/post tests are **associational**, not causal: no interrupted-time-series counterfactual.
- Adjacent events (Biden v. Nebraska + Payments Restart, SAVE Block + SAVE Forbearance) have overlapping windows; effects not separately identified.
- TextBlob-VADER correlation r=0.31 indicates weak inter-instrument agreement; **three-scorer triangulation complete (round-5 + Path C)** confirms this extends to Claude (TB×CL r=0.02 ns, VA×CL r=0.12, three-rater α=+0.17 with percentile-matched marginals). The three sentiment instruments are measuring different latent constructs. With proper power on Path C, the per-event direction-disagreement is sharper than the early subsample showed: 6/8 events are direction-split, including the Trump PSLF EO. See `triangulation_results.txt`.
- Reddit's 1000-result API cap is **partially real / partially confounded with growth** — see Volume-Artifact section.
- Cloudflare-blocked sources (Bogleheads, allnurses) → financially-sophisticated planners + dominant nursing community missing.
- Block-bootstrap permutation (Künsch 1989, B=2000) revises 3/8 events to non-significant after autocorrelation correction; the parametric Welch's t had been inflated 30-100×.
- Length confound: 4/8 events have significantly different pre/post word counts. Round-4 length-residualised analysis confirms primary findings survive (and SAVE Forbearance strengthens).
- **Discourse vs borrower scope**: findings concern online PSLF discussants (Reddit + SDN demographics), not the ~1M+ PSLF-eligible borrower population.

### Volume Artifact: Real Growth + API Cap (round-3 quantification)
- **r/PSLF was created 2014-08-21**. 12-year sub history. Sub paginates back exactly 998 posts spanning ~30 days in active periods.
- **CFPB ground truth shows real growth**: PSLF complaints 341 (2016) → 2,223 (2025), ~6.5× increase.
- **Reddit/CFPB ratio over time** (raw counts; `reddit_cfpb_volume_ratio.csv` — note: NOT length-matched, NOT topic-filtered to PSLF on the CFPB side):
  - 2017: 0.12
  - 2020: 0.41
  - 2024: 0.60
  - 2025: 1.63
  - 2026 (Q1-May, partial year — CFPB lags ~3 mo): **8.90**
- The ~74× growth in R/C ratio is too large to be real growth alone. **Mix: ~6-7× real growth, ~10× API-cap recency bias.** The 2026 spike is partly because CFPB data is incomplete for the year — interpret directionally, not as a fixed multiplier.
- The year-windowed Reddit collector (round-3) recovered 3-4× more pre-2020 posts than the original sort-only approach.

## Audit History
- 4 internal audit rounds, plus session-internal multi-agent audits in rounds 2, 4, and 5 (in-conversation, not externally independent).
- Round 1: 46 internal issues fixed.
- Round 2 (4-agent consensus): 5 CRITICAL fixes (filter divergence, wc<20 inconsistency, mislabeled Glass's delta, broken cross-correlation, Bonferroni inconsistency) + ~14 MAJOR. All resolved.
- Round 3: real moving-block bootstrap (replacing iid permutation), R/C ratio diagnostic in code, improved baseline (length-matched + topical-near).
- Round 4 (publication-readiness audit): length-residualised analysis added; ambiguity-aversion framing dropped (was unsupported); reframed as discourse-not-borrower study.
- Round 5 (this session): bootstrap per-event seed + B_actual tracking (was deflating p-values when zero-variance surrogates were skipped); OLS collinearity QR rank check (src_sdn ≡ prof_sdn_medical for SDN posts); sentiment_zeroshot.py auth fail-fast + circuit breaker (after a 715-call burn on auth errors); legislative_timeline_results.txt artifact for traceability; sample-size and R/C-ratio reconciliation; final_summary.py rewritten to canonical 8-event list.
- Path C (event-window Claude fill, ~$15.18, 3,035 posts): scored ALL Reddit + SDN posts in any of the 8 event windows at full corpus depth. Re-ran triangulation at n=4,787. Discovered the underpowered n=50/side eventstrat subsample had given false direction-concordance for Trump EO; with proper power, only Biden Mass Forgiveness and Biden v. Nebraska are triple-concordant. The substantive headline of the paper is meaningfully revised. Also fixed a per_event_tests bug that filtered to a single subsample (was missing the eventfull data even after Path C scoring landed).
- Round 6 / Copilot PR review (2026-05-08): 7 items addressed — UTF-8 stdout wrapper in `confound_audit.py` (mojibake fix); dynamic R/C multiplier in `gen_volume_artifact_figure.py` (was hardcoded 84×); `--stratify-events` help text correction; Trump event label standardisation; dropped misleading "Vectorized" docstring; dynamic subsample count in triangulation artifact; corrected `collect_allnurses` return type.
- Round 7 (post-Path-C comprehensive audit, 2026-05-08): 3-agent parallel audit (statistical methodology + triangulation construct validity + literature context). Key outputs:
  - **Reframed headline**: project's primary contribution is now the construct-validity finding (TextBlob = lexical affect, VADER = expressive arousal, Claude-prompted = stance). The α=+0.17 is structural construct mismatch, not noise. Trump EO direction conflict is the lead exemplar, not an embarrassment.
  - **17 statistical-methodology issues identified**, 4 publication-blockers (bootstrap implements wrong null hypothesis; Hedges' g variance missing J² factor; α has no bootstrap CI; percentile-matched α biases upward and is reported without that caveat).
  - **Confound audit logic bug**: `confound_audit.py:99–102` only flags "CONFOUND DETECTED" when stratification *halves* the effect, but the SDN-vs-Reddit case actually shows stratification *grows* the gap (population was suppressing platform effect). Should be |stratified − naive|/|naive| > 0.5 in either direction.
  - **Stale comment in triangulation_results.txt:57** ("~50 pre + ~50 post per event") contradicts the actual n=166–610/109–437 after Path C. Code path is correct; only the frozen comment is stale.
  - **Stochastic Claude scoring**: `sentiment_zeroshot.py:93` does not set `temperature=0`. No test-retest α computed. Need to either re-score 200 posts at temperature=0 or compute test-retest α on a duplicate batch.
  - **Family-wise correction undercounted**: project runs ~72 hypothesis tests across pre/post + window-sensitivity + residualised + triangulation; α/8 = 0.00625 only controls one family. Should switch to Holm-Bonferroni or Benjamini-Hochberg with explicit family declarations.
  - **SAVE Forbearance window-sensitivity range** is +1.03 (30d) → +0.25 (180d), 4× span. Likely transient effect or regression to the mean. Not flagged in the artifact.
  - See `audit_round7_findings.md` (to be created) for full 17-issue list with file:line citations and venue-specific implications.

## Round 7 Critical Fixes (must-do before submission)

These are required before submitting to any methods-aware venue (JCSS / EPJ Data Science / Political Analysis / Behavior Research Methods). They are **substantive code work** and warrant their own PR cycle, not inline patches:

1. **Bootstrap implementation rewrite** (`gen_legislative_timeline.py:386–411`). Current code resamples the *combined* pre+post series in moving blocks and re-cuts at index n1. Replace with **stratified circular block bootstrap within each group** (Politis & Romano 1994) or **block-permutation test** (Bickel et al. 1989). Likely produces *larger* p-values than the current implementation.
2. **Hedges' g variance includes J² factor** (`gen_legislative_timeline.py:484`, `sentiment_triangulation.py:117`). Use Borenstein et al. (2009) eq. 4.24, not Hedges & Olkin (1985) eq. 6.13 (large-sample approximation that omits J²).
3. **Krippendorff's α bootstrap CI** (`sentiment_triangulation.py:208–306`). Add B=10,000 stratified bootstrap CI (Hayes & Krippendorff 2007). The `krippendorff` library does not compute these natively — needs explicit loop.
4. **Acknowledge percentile-matched α as charitable bound, not canonical** (`sentiment_triangulation.py:255–268`). Forcing equal-frequency quintiles aligns marginals between TB and VADER but not with Claude's true asymmetric distribution. Headline number should be the fixed-threshold α (=−0.03) with the percentile-matched α as a sensitivity bound, OR explicitly reframe as "ordinal α with native scorer thresholds gives α=−0.03; an upper-bound estimate that controls for marginal frequency mismatch is α=+0.17; both are well below the 0.667 reliability floor."
5. **Test-retest reliability for Claude** (`sentiment_zeroshot.py`). Re-score 200 posts at `temperature=0` (deterministic) and compute test-retest α. Current Claude scoring uses default temperature=1.0 → per-post output is sampled. Without test-retest, the Claude column has unknown ceiling reliability.
6. **Confound-audit conditional asymmetry bug** (`confound_audit.py:99–102`). Replace the one-sided test with |stratified − naive|/|naive| > 0.5.

## Round 7 Should-Fix (for quality)

7. Replace Bonferroni with Holm-Bonferroni (or BH with explicit family declarations).
8. Add HC3 robust SEs to OLS residualization, or cluster by thread/source/profession/month (generated-regressor problem; Pagan 1984).
9. Add per-event bootstrap to `sentiment_triangulation.py` (currently uses parametric Welch's t with the same autocorrelation issue as the main analysis).
10. Window-sensitivity SD report alongside g (4× span for SAVE Forbearance is currently unflagged).
11. Switch p-value reporting to APA conventions (`p<10⁻⁷` instead of `p=0.000000`).
12. Fix stale `~50 pre + ~50 post` comment in triangulation_results.txt:57.

## Round 7 Reframing for the Paper

The substantive contribution has changed. Drafting around this frame:

**Title (working):** *Stance, Affect, and Arousal: Sentiment Construct Mismatch in Policy-Discourse Text*

**Abstract framing (1 paragraph):** Three commonly-used sentiment instruments — TextBlob (lexicon polarity), VADER (Hutto & Gilbert 2014, social-media-tuned), and Claude Sonnet 4 zero-shot (LLM, prompted for stance toward a policy object) — are routinely treated as interchangeable in policy-discourse research. We demonstrate on a 9,629-post Public Service Loan Forgiveness corpus (Reddit + Student Doctor Network, 2010–2026) that they operationalize substantively different latent constructs: lexical affect, expressive arousal, and stance, respectively. Krippendorff's α=+0.17 (percentile-matched ordinal, n=4,787 with all three scorers) — well below the 0.667 floor for tentative reliability claims (Krippendorff 1980). The 2025 Trump PSLF Executive Order is the lead exemplar: directionally opposite Hedges' g across the three instruments on identical n=1,047 posts (TextBlob g=−0.39, VADER g=+0.21, Claude g=+0.41). The construct distinction is theoretically grounded in stance vs sentiment (Mohammad et al. 2016, SemEval-2016 Task 6) but has not been previously quantified at this scale on policy text. Implication: researchers using off-the-shelf sentiment tools must explicitly choose and defend the construct they are operationalizing; "sentiment" alone is no longer a publishable construct claim. We pair this finding with a quantification of Reddit's 1000-result API cap as a volume artifact (R/C ratio against CFPB Consumer Complaints as ground truth: ~6-7× real growth + ~10× recency-bias artifact 2017–2026).

**Recommended venues:**
- Tier 1 (target first): EPJ Data Science (SentiBench heir), Political Analysis (Heseltine & von Hohenberg 2024 precedent), Sociological Methods & Research (Chae & Davidson 2026 precedent).
- Tier 2: PNAS Nexus, Journal of Computational Social Science, PLOS One, Behavior Research Methods.
- Pre-print: arXiv cs.CL or cs.SI immediately.

**Cannot claim** (in this paper, with this design):
- "PSLF discourse responds to policy events" — substantive headline gone with Path C
- "Trump EO had a robust effect on PSLF sentiment" — direction is contested across 2/3 scorers
- "TextBlob/VADER/Claude are interchangeable" — refuted
- "Online discourse predicts borrower behavior" — no causal design, no representative sample

**Can claim**:
- Three commonly-used sentiment instruments operationalize substantially different constructs on policy discourse
- Construct mismatch is theoretically grounded (stance vs sentiment) and empirically demonstrated at α=+0.17, n=4,787
- Trump PSLF EO is a clean exemplar of the dissociation: TB g=−0.39, VA g=+0.21, CL g=+0.41 on identical n=1,047
- R/C volume artifact: Reddit's 1000-result API cap creates ~10× recency bias when measured against CFPB ground truth

## Not Yet Done
- Claude API zero-shot classification: **complete** — `zeroshot_reddit_n1000.csv` (n=721), `zeroshot_sdn_n1000.csv` (n=615), `zeroshot_reddit_eventstrat.csv` (n=715, ~50 pre + ~50 post per event).
- Krippendorff's α + per-event Claude pre/post triangulation + Figure 7: **complete** — see `triangulation_results.txt` and `triangulation_figure7.png`.
- Reddit API comments (needs client_id/client_secret)
- Bogleheads + allnurses (Cloudflare blocks even Playwright stealth)
- Topic modeling (LDA/BERTopic) — required for policy-venue submission
- Interrupted time series (ARIMA + control series) — required for causal claims
- Per-author longitudinal panels (within-subject design for adjacent-event identification)
- OSF/AsPredicted pre-registration of event family (CONSORT-style flow)

## Publication Status (round-4 audit verdict)
- **Pre-print (arXiv cs.SI / SSRN)**: ready now
- **PLOS One**: ~1–2 weeks of writing. Path C revealed that *no* event is simultaneously bootstrap-Bonferroni-significant AND triple-concordant. The paper must lead with the methodological co-headline (α=+0.17 across three commonly-used sentiment instruments on the same n=4,787 PSLF corpus) and treat the per-event findings as a *case study of instrument disagreement*, not as substantive policy-effect estimates. Trump PSLF EO is now an exemplar of direction-conflict (TB g=−0.39 vs VA g=+0.21 vs CL g=+0.41 on the same n=1,047 posts), not a robust effect.
- **Methods journal** (JCSS / EPJ Data Science): ~1 month of revisions (R/C diagnostic could be standalone methods note)
- **Policy journal**: not without substantial reframing as discourse analysis with topic modeling
