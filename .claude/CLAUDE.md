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

## Key Findings
1. **Medical professionals are most negative** about PSLF (22.3% neg, pol=0.070) — debt-to-income concerns
2. **r/PSLF has highest negativity** (23.9%) — frustration with servicers/process
3. **Social work (10.3% neg) and OT (11.0% neg) most positive** — near-automatic eligibility
4. **Trump EO (Mar 2025) caused sharpest negative shift**: pol dropped 0.046, p<0.0001
5. **PSLF Waiver (Oct 2021) caused biggest positive shift**: pol up 0.036, p<0.0001
6. **Present day (Mar 2026)**: pol=0.071, 21.4% neg — significantly worse than 2024 H2 baseline
7. **SDN forum more positive than Reddit** (0.113 vs 0.086, p<0.000001) — longer-form discussion

## Audit History
- 4 full audit rounds, 46 issues found and fixed (3 critical, 19 major, 24 minor)
- Content audit revealed broad filter was capturing off-topic posts (nursing had only 6.1% explicit PSLF mentions) — fixed with PSLF_STRICT_REGEX
- TextBlob vs VADER correlation only r=0.33 — measuring different things

## Not Yet Done
- Reddit API comments (needs client_id/client_secret from user)
- Claude API zero-shot classification (needs funded ANTHROPIC_API_KEY)
- Bogleheads forum (Cloudflare blocks even Playwright stealth)
- allnurses.com (Cloudflare blocks headless browsers)
- Topic modeling (LDA/BERTopic)
- Interrupted time series (ARIMA) for causal inference
