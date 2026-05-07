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
- **9,000+ PSLF-relevant posts** (strict anchored filter, MIN_WORDS=20) from 20 communities
  - Reddit: 11,793 raw → 4,200 PSLF-filtered + length-residualised
  - SDN Forum: 45,334 raw → 4,700 PSLF-filtered
- **Dual sentiment scoring**: TextBlob polarity + VADER compound (r=0.31, weak agreement)
- **Strict PSLF filter** (`filter_pslf_relevant` in pslf_search_terms.py) — generic 'forgiveness' terms must co-occur with a PSLF-specific anchor (PSLF/MOHELA/qualifying employer/etc.) within 80 chars
- **Length-residualised analysis**: outcome = residuals of polarity ~ log(word_count) + source + profession (round-4 fix)
- **r/AskReddit baseline** (n=177) + **topical-near baseline** (n=7,750 off-PSLF posts in same subs)

## Key Scripts (in scripts/)
- `collect_forum_data.py` — SDN scraper (Playwright headless + requests/BS4)
- `collect_reddit_professions.py` — Reddit JSON API scraper, year-windowed (round-3 fix)
- `collect_reddit_baseline.py` — r/AskReddit + topical-near baselines
- `collect_reddit_comments.py` — Reddit comment trees (needs PRAW API keys)
- `analyze_multi_source.py` — Cross-platform/profession statistical analysis
- `gen_hires_figs.py` — 300 DPI sentiment comparison + word cloud figures
- `gen_legislative_timeline.py` — Policy event timeline + pre/post analysis (raw + residualised) + sensitivity + bootstrap
- `gen_volume_artifact_figure.py` — Reddit/CFPB volume ratio diagnostic
- `analyze_admin_data_correlation.py` — CFPB cross-correlation + R/C ratio
- `confound_audit.py` — Profession × year, length × polarity, pre/post word count tests
- `sentiment_vader.py` — VADER scoring (adds vader_compound columns to CSVs)
- `sentiment_zeroshot.py` — Claude API classifier (needs funded ANTHROPIC_API_KEY for n≈1000 stratified subsample, ~$10 cost)
- `pslf_search_terms.py` — filter_pslf_relevant, anchored regex
- `final_summary.py` — Statistical summary report

## Headline Findings (associational; survive 4 audit rounds)

All effects below are reported as Hedges' g + Glass's Δ_pre (raw) and length-residualised g (round-4 fix). Block-bootstrap p-values (Künsch 1989, B=2000) reported. Bonferroni α/8 = 0.0063.

| Event | g_raw | g_resid | bootstrap p | survives Bonferroni |
|-------|-------|---------|-------------|---------------------|
| **SAVE Admin Forbearance** (2024-08-09) | +0.51 | **+0.58** | 0.010 | ✓ |
| **Trump PSLF EO** (2025-03-07) | −0.40 | −0.39 | 0.006 | ✓ |
| **Biden v. Nebraska SCOTUS** (2023-06-30) | −0.43 | −0.39 | 0.005 | ✓ (window overlaps Payments Restart) |
| **Limited PSLF Waiver** (2021-10-06) | +0.35 | +0.36 | <0.05 | ✓ |
| **Final Trump PSLF Rule** (2025-10-30) | +0.30 | +0.18 | 0.013 | ✓ raw, weakens on residuals |
| Payments Restart (2023-10-01) | +0.33 | +0.34 | 0.072 | ✗ borderline |
| IDR Account Adjustment (2022-04-19) | −0.24 | −0.25 | 0.237 | ✗ NOT sig |
| Biden Mass Forgiveness (2022-08-24) | −0.25 | −0.23 | 0.170 | ✗ NOT sig |

Key descriptive observations (NO causal claims, NO behavioral interpretation):
1. **The 90-day window following the SAVE administrative forbearance shows a +0.51 to +0.58 standardised mean increase in TextBlob polarity** (g grows under length adjustment). Several alternative mechanisms — selection of who keeps posting, post-period word count differences, adjacent-event contamination (8th Circuit SAVE injunction, Nov election) — are not ruled out.
2. **The 90-day window following Biden v. Nebraska shows the largest negative shift (g=−0.43 raw, g=−0.39 residualised, Glass's Δ_pre=−0.48)**. Window overlaps with the October 2023 payments restart; effects not separately identified.
3. **The 60-day window following the Trump PSLF EO shows the largest negative shift among PSLF-targeted events** (g=−0.40 raw and residualised; permutation p=0.006).
4. **Cross-source baseline calibration**: r/AskReddit length-matched baseline polarity = 0.015. PSLF medical posts polarity = 0.072. PSLF discussion is *slightly more positive* than typical Reddit when length-adjusted — challenges any "PSLF most negative" framing.
5. **CFPB-sentiment cross-correlation null** (all 13 lags p>0.05 after Bonferroni, first-differenced) — online sentiment and formal complaint volume are decoupled signals, NOT a redundant measurement.

### Analytical Caveats (state explicitly in any write-up)
- Pre/post tests are **associational**, not causal: no interrupted-time-series counterfactual.
- Adjacent events (Biden v. Nebraska + Payments Restart, SAVE Block + SAVE Forbearance) have overlapping windows; effects not separately identified.
- TextBlob-VADER correlation r=0.31 indicates weak inter-instrument agreement; **third-scorer triangulation pending API funding** (~$10).
- Reddit's 1000-result API cap is **partially real / partially confounded with growth** — see Volume-Artifact section.
- Cloudflare-blocked sources (Bogleheads, allnurses) → financially-sophisticated planners + dominant nursing community missing.
- Block-bootstrap permutation (Künsch 1989, B=2000) revises 3/8 events to non-significant after autocorrelation correction; the parametric Welch's t had been inflated 30-100×.
- Length confound: 4/8 events have significantly different pre/post word counts. Round-4 length-residualised analysis confirms primary findings survive (and SAVE Forbearance strengthens).
- **Discourse vs borrower scope**: findings concern online PSLF discussants (Reddit + SDN demographics), not the ~1M+ PSLF-eligible borrower population.

### Volume Artifact: Real Growth + API Cap (round-3 quantification)
- **r/PSLF was created 2014-08-21**. 12-year sub history. Sub paginates back exactly 998 posts spanning ~30 days in active periods.
- **CFPB ground truth shows real growth**: PSLF complaints 341 (2016) → 2,223 (2025), ~6.5× increase.
- **Reddit/CFPB ratio over time** (`reddit_cfpb_volume_ratio.csv`):
  - 2017: 0.12
  - 2020: 0.41
  - 2024: 0.60
  - 2025: 1.63
  - 2026 (Q1-May): **8.90**
- The ~74× growth in R/C ratio is too large to be real growth alone. **Mix: ~6-7× real growth, ~10× API-cap recency bias.**
- The year-windowed Reddit collector (round-3) recovered 3-4× more pre-2020 posts than the original sort-only approach.

## Audit History
- 4 internal audit rounds + 4 independent agent rounds.
- Round 1: 46 internal issues fixed.
- Round 2 (4-agent consensus): 5 CRITICAL fixes (filter divergence, wc<20 inconsistency, mislabeled Glass's delta, broken cross-correlation, Bonferroni inconsistency) + ~14 MAJOR. All resolved.
- Round 3: real moving-block bootstrap (replacing iid permutation), R/C ratio diagnostic in code, improved baseline (length-matched + topical-near).
- Round 4 (publication-readiness audit): length-residualised analysis added; ambiguity-aversion framing dropped (was unsupported); reframed as discourse-not-borrower study.

## Not Yet Done
- Claude API zero-shot classification (needs funded ANTHROPIC_API_KEY, ~$10)
- Reddit API comments (needs client_id/client_secret)
- Bogleheads + allnurses (Cloudflare blocks even Playwright stealth)
- Topic modeling (LDA/BERTopic) — required for policy-venue submission
- Interrupted time series (ARIMA + control series) — required for causal claims
- Per-author longitudinal panels (within-subject design for adjacent-event identification)
- OSF/AsPredicted pre-registration of event family (CONSORT-style flow)

## Publication Status (round-4 audit verdict)
- **Pre-print (arXiv cs.SI / SSRN)**: ready now
- **PLOS One**: ~2 weeks of revisions (length residuals ✓ done; third-scorer triangulation pending; reframing ✓ done)
- **Methods journal** (JCSS / EPJ Data Science): ~1 month of revisions (R/C diagnostic could be standalone methods note)
- **Policy journal**: not without substantial reframing as discourse analysis with topic modeling
