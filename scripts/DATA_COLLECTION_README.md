# PSLF Multi-Source Data Collection

## Overview

These scripts expand the PSLF Discussion Analysis beyond Reddit posts to include:
- **Reddit comments** — nested replies on existing posts (same platform, deeper signal)
- **SDN + WCI forums** — professional physician communities (separate file)
- **X/Twitter** — real-time policy discourse (separate file)

Each produces a **separate CSV** to keep data provenance clean. The unified analysis script (`analyze_multi_source.py`) reads all sources and generates cross-platform comparisons.

## Output Files

| Script | Output | Data Source |
|--------|--------|-------------|
| `collect_reddit_comments.py` | `reddit_comments_pslf.csv` | Reddit comment trees |
| `collect_forum_data.py` | `forum_pslf_discussions.csv` | SDN + WCI forums |
| `collect_twitter_data.py` | `twitter_pslf_discussions.csv` | X/Twitter |
| `analyze_multi_source.py` | `multi_source_sentiment_comparison.png` | All of the above |

## Setup

```bash
# Install all dependencies
pip install praw tweepy requests beautifulsoup4 textblob tqdm lxml scipy matplotlib pandas numpy scikit-learn

# Download NLTK data (needed by TextBlob)
python -c "import nltk; nltk.download('punkt')"
```

## 1. Reddit Comments

Requires a Reddit API application (free, instant): https://www.reddit.com/prefs/apps/

```bash
python collect_reddit_comments.py \
    --client_id YOUR_CLIENT_ID \
    --client_secret YOUR_CLIENT_SECRET \
    --user_agent "PSLF-Analysis/2.0 by u/YOUR_USERNAME"
```

**What it does:** Iterates through all 1,126 posts in the existing medical + teacher CSVs, pulls the full comment tree (up to depth 5), computes TextBlob polarity/subjectivity per comment, and saves with `post_id` as the join key.

**Expected yield:** ~5,000–15,000 comments depending on thread activity.

**Resume support:** Use `--resume` to pick up where you left off if interrupted.

**Rate limiting:** 1 second between posts. Full collection takes ~20–30 minutes.

## 2. Forums (SDN + WCI)

No API key needed — uses web scraping with polite rate limits.

```bash
# Scrape both forums
python collect_forum_data.py --source all

# Or individually
python collect_forum_data.py --source sdn
python collect_forum_data.py --source wci
```

**What it does:** Searches each forum for PSLF-related threads using 12 search queries, then scrapes all posts within each discovered thread. Posts from both forums go into a single file with a `source` column (`sdn` or `wci`).

**Expected yield:** 200–800 forum posts across 50–150 threads.

**Note:** Forum HTML structures can change. If scraping fails, the selectors in `SDNScraper` and `WCIScraper` may need updating. The script handles errors gracefully and continues.

## 3. X/Twitter

Two methods available:

### API method (recommended)
Requires X API access: https://developer.x.com/en/portal/dashboard

```bash
# Set bearer token
export X_BEARER_TOKEN="your_token_here"

# Run collection
python collect_twitter_data.py \
    --method api \
    --bearer_token $X_BEARER_TOKEN \
    --start_date 2021-01-01 \
    --end_date 2026-03-23 \
    --max_per_query 500
```

API tiers:
- **Basic ($100/month):** 10,000 tweets/month, recent search only (7 days)
- **Pro ($5,000/month):** 1M tweets/month, full-archive search
- **Academic Research (free, apply):** full-archive, best for this project

### Nitter fallback (no API key)
```bash
python collect_twitter_data.py --method nitter
```

Nitter instances are unreliable and may go down. Less structured data but zero cost.

**Expected yield:** 1,000–10,000 tweets depending on API tier.

## 4. Unified Analysis

After collecting data from any combination of sources:

```bash
python analyze_multi_source.py
```

Produces:
- Cross-source sentiment comparison (statistical tests)
- Temporal sentiment trajectories by platform
- Volume comparison across sources
- Reddit post vs. comment sentiment analysis
- Forum vs. Reddit discourse characteristics
- 4-panel comparison visualization

## Data Schema

### Reddit Comments (`reddit_comments_pslf.csv`)
- `comment_id`, `post_id` (join key), `parent_id`
- `author`, `body`, `score`, `depth`
- `polarity`, `subjectivity`, `word_count`
- `profession` (inherited from parent post)

### Forum Data (`forum_pslf_discussions.csv`)
- `source` (`sdn` or `wci`), `thread_id`, `thread_title`
- `post_number`, `author`, `body`, `date_posted`
- `is_thread_start`, `polarity`, `subjectivity`

### Twitter Data (`twitter_pslf_discussions.csv`)
- `tweet_id`, `author_username`, `text`, `created_at`
- `like_count`, `retweet_count`, `reply_count`
- `is_reply`, `is_retweet`, `is_quote`
- `query_matched`, `polarity`, `subjectivity`

## Ethical Considerations

- All data is publicly available and collected via official APIs or public web pages
- Rate limits are respected (1-2s between requests)
- No private/DM data is collected
- Usernames are collected for deduplication but should be anonymized before publication
- Follows Reddit API Terms, X Developer Agreement, and robots.txt conventions
