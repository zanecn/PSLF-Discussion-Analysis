# PSLF Discussion Analysis Project

## Overview
Multi-source sentiment analysis of Public Service Loan Forgiveness (PSLF) discussions across online communities. Tracks how sentiment toward PSLF varies by profession, platform, and legislative era.

## Repository
- Fork: https://github.com/zanecn/PSLF-Discussion-Analysis
- Upstream: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis
- PR #1: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis/pull/1
- Branch: `playwright-sdn-scraper`

## Data (as of 2026-03-24)
- **9,446 PSLF-relevant posts** (strict filter) from 20 communities
  - Reddit: 4,167 posts from 18 subreddits (r/PSLF, r/StudentLoans, r/Residency, r/medicalschool, r/nursing, r/StudentNurse, r/nursepractitioner, r/Teachers, r/LawSchool, r/socialwork, r/fednews, r/govfire, r/pharmacy, r/physicianassistant, r/OccupationalTherapy, r/slp, r/personalfinance, r/financialindependence)
  - SDN Forum: 5,279 posts (Playwright headless scraper, 200 threads)
  - Original medical/teacher CSVs: 1,126 posts
- **Dual sentiment scoring**: TextBlob polarity + VADER compound
- **Strict PSLF filter** (`PSLF_STRICT_REGEX` in pslf_search_terms.py) — requires explicit PSLF/forgiveness/IDR terms
- **Min 20 words** for sentiment scoring (TextBlob unreliable on short posts)

## Key Scripts (in scripts/)
- `collect_forum_data.py` — SDN scraper (Playwright headless + requests/BS4)
- `collect_reddit_professions.py` — Reddit JSON API scraper (no auth needed)
- `collect_reddit_comments.py` — Reddit comment trees (needs PRAW API keys)
- `analyze_multi_source.py` — Cross-platform/profession statistical analysis
- `gen_hires_figs.py` — 300 DPI sentiment comparison + word cloud figures
- `gen_legislative_timeline.py` — Policy event timeline + pre/post analysis + profession timecourse
- `sentiment_vader.py` — VADER scoring (adds vader_compound columns to CSVs)
- `sentiment_zeroshot.py` — Claude API classifier (needs ANTHROPIC_API_KEY with billing)
- `pslf_search_terms.py` — Shared search terms, filter regexes, constants
- `final_summary.py` — Generates full statistical summary report

## Pipeline Entry Points (added 2026-05-07)
- `run_pipeline.sh` — full scrape + analyze orchestrator. Flags: `--analyze-only`, `--scrape-only`, `--with-comments`, `--with-zeroshot`. Honors `REDDIT_CLIENT_ID/SECRET` + `ANTHROPIC_API_KEY` env vars.
- `.github/workflows/rescrape.yml` — same pipeline on GH Actions runners (full outbound network); `workflow_dispatch` + monthly cron; uploads artifacts and commits CSVs back to `playwright-sdn-scraper`.
- Important: the Claude Code web sandbox **blocks reddit.com / forums.studentdoctor.net / consumerfinance.gov / huggingface.co** by egress allowlist. A rescrape must run from a laptop session or GH Actions, not from claude.ai/code.

## Key Findings (associational; pre/post tests are NOT interrupted time series)
1. **Medical-professional posts are most negative** in associational comparison (22.3% neg, pol=0.070) — debt-to-income concerns
2. **r/PSLF has highest negativity rate** (23.9%) — frustration with servicers/process
3. **Social work (10.3% neg) and OT (11.0% neg) least negative** — near-automatic PSLF eligibility
4. **Sentiment dropped 90 days after Trump PSLF EO (Mar 2025)** — pol -0.046, p<0.0001, Hedges' g=-0.30. NOT causally identified.
5. **Sentiment rose 90 days after Limited Waiver (Oct 2021)** — pol +0.036, p<0.0001, Hedges' g=+0.33. NOT causally identified.
6. **Sentiment dropped 90 days after Biden v. Nebraska SCOTUS (Jun 2023)** — Hedges' g=-0.43, the LARGEST shift. Window overlaps 2023-10-01 payment restart, so confounded.
7. **Present day (2026-04) shows lower polarity** vs pre-COVID baseline (2018-2019).
8. **SDN posts more positive than Reddit** in unadjusted comparison (0.113 vs 0.086, p<0.000001) — but confounded with population (medical-only on SDN) and post length.

### Analytical Caveats (from 2026-04 independent audit consensus)
- Pre/post tests are associational, not causal: there is no interrupted-time-series counterfactual.
- Adjacent events (e.g., Biden v. Nebraska + Payments Restart, SAVE Block + SAVE Forbearance) have overlapping 90-day windows; their effects are not separately identified.
- TextBlob-VADER correlation r=0.33 indicates the two scorers measure different constructs; headline numbers use TextBlob (limitation noted in all reports).
- Reddit's 1000-result API cap is **partially real / partially confounded with growth** — see Volume-Artifact section below.
- Cloudflare-blocked sources (Bogleheads, allnurses) → financially-sophisticated planners and dominant nursing community are missing.
- r/AskReddit baseline: pol=0.050, %neg=26.4% (n=330). PSLF medical (pol=0.070, %neg=22.3%) is actually slightly MORE positive than Reddit baseline — challenges 'PSLF most negative' framing.
- Permutation p-values (B=200) ~0.005 vs parametric p<0.0001 confirms autocorrelation inflated t-statistics 1-2 orders of magnitude. True effects are still significant after correction but with much wider uncertainty.

### Volume Artifact: Real Growth + API Cap (mixed; 2026-04 round-3 investigation)
- **r/PSLF was created 2014-08-21** (CLAUDE.md previously said 2017 — corrected). 12-year sub history.
- **Reddit's 1000-result hard cap is confirmed**: paginating /new backwards terminates at exactly 998 posts, spanning only ~30 days of recent activity in r/PSLF.
- **CFPB ground truth shows real growth**: PSLF complaints went from 341 (2016) → 2,223 (2025) — about 6.5× increase.
- **Reddit/CFPB ratio over time**:
  | Year | CFPB | Reddit (scraped) | R/C ratio |
  |------|------|------------------|-----------|
  | 2017 | 1,391 | 80 | 0.058 |
  | 2020 | 511 | 125 | 0.245 |
  | 2024 | 2,116 | 414 | 0.196 |
  | 2025 | 2,223 | 659 | 0.296 |
  | 2026 (Q1) | 228 | 1,102 | **4.83** |
- The 84× growth in R/C ratio from 2017 to 2026 is too large to be real growth alone. It's a **mix**: ~5-10× real PSLF growth (waiver, SAVE crisis, EO drove discussion), and ~10× API-cap recency bias.
- **Recent-3-months pattern is starkest**: Mar 2026 R/C = 80, Apr 2026 R/C = ∞ (CFPB lags). Confirms the API-cap retrieves a recent-30d window in active subs.
- **Implication**: Reddit volume increase is BOTH real AND inflated. Don't use the volume curve as evidence of "discussion intensity" without normalizing to CFPB or another non-capped source.

## Audit History
- 4 internal audit rounds (initial → audit 4): 46 issues fixed.
- 2026-04 independent four-agent consensus audit: identified 5 CRITICAL fixes (filter divergence, wc<20 inconsistency, mislabeled Glass's delta, broken cross-correlation, Bonferroni inconsistency) + ~14 MAJOR.
- All 5 CRITICALs resolved (commit will land soon). MAJORs partially resolved.

## Not Yet Done
- Reddit API comments (needs client_id/client_secret from user)
- Claude API zero-shot classification (needs funded ANTHROPIC_API_KEY)
- Bogleheads forum (Cloudflare blocks even Playwright stealth)
- allnurses.com (Cloudflare blocks headless browsers)
- Topic modeling (LDA/BERTopic)
- Interrupted time series (ARIMA) for causal inference
