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
- Reddit's 1000-result API cap is unmitigated → pre-2020 corpus is sparse.
- Cloudflare-blocked sources (Bogleheads, allnurses) → financially-sophisticated planners and dominant nursing community are missing.

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
