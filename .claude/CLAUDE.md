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
