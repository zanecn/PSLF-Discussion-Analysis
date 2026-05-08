# PSLF Online Discourse Analysis Project

## Overview
Multi-source sentiment analysis of **online discussion** of Public Service Loan Forgiveness (PSLF) across Reddit communities and the Student Doctor Network (SDN) forum. Tracks how **discussant** sentiment varies by profession-self-selected subreddit, platform, and legislative era.

**Scope clarification (round-4 audit fix):** This project studies **online PSLF discourse**, not the PSLF-borrower population. Reddit + SDN users skew young, white, male, more educated than the ~1M+ borrower population, and Bogleheads + allnurses are Cloudflare-blocked. Findings should be interpreted as discourse, not behavior.

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
- **Three-scorer sentiment**: TextBlob polarity + VADER compound + Claude Sonnet 4 zero-shot. Pearson correlations: TB×VA r=0.30, TB×CL r=0.08, VA×CL r=0.13 (all p<0.001). Three-rater Krippendorff's α (ordinal, n=2,002 with all 3 scorers): −0.04 with fixed thresholds, +0.18 with percentile-matched marginals — both well below the 0.667 floor for tentative reliability claims. Marginal distributions diverge sharply (VADER calls 71% of posts very_positive vs Claude's 3.5%).
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
6. **Three-scorer triangulation reveals construct disagreement, not redundant measurement** (round-5, n=2,002 union of zero-shot subsamples). Krippendorff's α for the three-rater ordinal task is +0.18 even with percentile-matched marginals — well below 0.667. Direction concordance on the 8 events is partial: 3/8 events have all three scorers agreeing on sign (IDR Account Adjustment, **Trump PSLF EO**, Final Trump PSLF Rule); 5/8 events have at least one scorer disagreeing on direction. **The Trump PSLF EO is the most defensible single finding**: full-corpus bootstrap-Bonferroni significant *and* sign-concordant across all three scorers. **The SAVE Forbearance positive shift is direction-disputed** — VADER scores it g=−0.29 in the event-stratified subset while TextBlob (+0.16) and Claude (+0.29) agree on a positive shift. Caveat: the event-stratified subset n=50 pre + n=50 post is severely underpowered, and several events flip direction relative to the full-corpus run, so the pre/post head-to-head comparison must be read as descriptive concordance, not effect-size estimation.

### Analytical Caveats (state explicitly in any write-up)
- Pre/post tests are **associational**, not causal: no interrupted-time-series counterfactual.
- Adjacent events (Biden v. Nebraska + Payments Restart, SAVE Block + SAVE Forbearance) have overlapping windows; effects not separately identified.
- TextBlob-VADER correlation r=0.31 indicates weak inter-instrument agreement; **three-scorer triangulation complete (round-5)** confirms this extends to Claude (TB×CL r=0.08, VA×CL r=0.13, three-rater α=+0.18 with percentile-matched marginals). The three sentiment instruments are measuring different latent constructs, not noisy versions of the same construct. See `triangulation_results.txt`.
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
- **PLOS One**: ~2 weeks of revisions (length residuals ✓ done; third-scorer triangulation ✓ done — but α=+0.18 means the paper must be reframed around Trump PSLF EO as the only triple-concordant + bootstrap-Bonferroni-significant event, with sentiment-instrument disagreement as a co-headline finding, not a side caveat; reframing ✓ done)
- **Methods journal** (JCSS / EPJ Data Science): ~1 month of revisions (R/C diagnostic could be standalone methods note)
- **Policy journal**: not without substantial reframing as discourse analysis with topic modeling
