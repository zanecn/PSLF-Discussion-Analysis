"""
Build twitter_pslf_discussions.csv from raw text extracted via browser.
Parses xcancel.com page text into structured tweet records.
"""
import csv
import hashlib
import re
import sys
from datetime import datetime
from textblob import TextBlob

OUTPUT = "C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis/twitter_pslf_discussions.csv"

FIELDS = [
    "tweet_id", "author_id", "author_username", "text", "created_at",
    "retweet_count", "like_count", "reply_count", "quote_count",
    "impression_count", "lang", "conversation_id", "is_reply",
    "is_retweet", "is_quote", "hashtags", "query_matched",
    "polarity", "subjectivity", "word_count", "collection_method", "scraped_at",
]


def analyze_sentiment(text):
    try:
        clean = re.sub(r'@\w+', '', re.sub(r'https?://\S+', '', text))
        blob = TextBlob(clean.strip())
        return round(blob.sentiment.polarity, 6), round(blob.sentiment.subjectivity, 6)
    except Exception:
        return 0.0, 0.0


def parse_xcancel_text(raw_text, query):
    """Parse xcancel page text into tweet records."""
    tweets = []

    # Split on the pattern: username@handle timestamp
    # e.g. "PeopleJoy Inc.@getpeoplejoy 10h" or "funyun princess@willactuallycry Mar 22"
    pattern = r'(?:^|\n)(.+?)@(\w+)\s+((?:\d+[hm])|(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+(?:,?\s*\d{4})?)|(?:\d+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}))\s+'

    matches = list(re.finditer(pattern, raw_text))

    for i, match in enumerate(matches):
        username = match.group(2)
        date_str = match.group(3).strip()

        # Text goes from end of this match to start of next match (or end)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_text)
        text_block = raw_text[start:end].strip()

        # Remove "Load more" footer
        text_block = re.sub(r'\s*Load more\s*$', '', text_block)

        # Remove trailing stat numbers (likes, RTs etc) - last line of numbers
        lines = text_block.split('\n')
        # Try to extract stats from the last few tokens
        stat_nums = []
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^[\d,\s]+$', line):
                clean_lines.append(line)
            elif re.match(r'^[\d,\s]+$', line):
                for n in re.findall(r'[\d,]+', line):
                    stat_nums.append(int(n.replace(',', '')))

        text = ' '.join(clean_lines).strip()
        # Remove embedded URLs (domain patterns)
        text = re.sub(r'\b\w+\.(com|org|net|io|co|gov|edu)\S*', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 15:
            continue

        # Check if reply
        is_reply = text.startswith('Replying to')

        # Extract hashtags
        hashtags = ','.join(re.findall(r'#\w+', text))

        # Sentiment
        pol, subj = analyze_sentiment(text)

        # Generate tweet ID
        tid = hashlib.md5(f"{username}:{text[:80]}:{date_str}".encode()).hexdigest()[:16]

        tweets.append({
            "tweet_id": tid,
            "author_id": "",
            "author_username": username,
            "text": text[:1000],
            "created_at": date_str,
            "retweet_count": stat_nums[1] if len(stat_nums) > 1 else 0,
            "like_count": stat_nums[-1] if stat_nums else 0,
            "reply_count": stat_nums[0] if stat_nums else 0,
            "quote_count": stat_nums[2] if len(stat_nums) > 2 else 0,
            "impression_count": stat_nums[3] if len(stat_nums) > 3 else 0,
            "lang": "en",
            "conversation_id": "",
            "is_reply": is_reply,
            "is_retweet": False,
            "is_quote": False,
            "hashtags": hashtags,
            "query_matched": query,
            "polarity": pol,
            "subjectivity": subj,
            "word_count": len(text.split()),
            "collection_method": "nitter_browser",
            "scraped_at": datetime.utcnow().isoformat(),
        })

    return tweets


# Raw text data from each query page (collected via browser)
PAGES = {}  # Will be populated below

def main():
    import json

    # Load from file
    with open("C:/Users/zanen/PSLF_2026/scripts/xcancel_pages.json", "r", encoding="utf-8") as f:
        pages = json.load(f)

    all_tweets = []
    seen_ids = set()

    for query, text in pages.items():
        tweets = parse_xcancel_text(text, query)
        for t in tweets:
            if t["tweet_id"] not in seen_ids:
                seen_ids.add(t["tweet_id"])
                all_tweets.append(t)
        print(f"  {query}: {len(tweets)} tweets parsed")

    # Write CSV
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for t in all_tweets:
            writer.writerow(t)

    print(f"\nTotal unique tweets: {len(all_tweets)}")
    print(f"Output: {OUTPUT}")

    # Quick stats
    pols = [t["polarity"] for t in all_tweets]
    replies = sum(1 for t in all_tweets if t["is_reply"])
    print(f"Mean polarity: {sum(pols)/len(pols):.4f}")
    print(f"Replies: {replies} ({replies/len(all_tweets)*100:.0f}%)")


if __name__ == "__main__":
    main()
