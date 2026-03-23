"""Parse raw text extracted from xcancel.com search pages into CSV."""
import csv
import json
import os
import re
import sys
from datetime import datetime
from textblob import TextBlob

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "PSLF-Discussion-Analysis", "twitter_pslf_discussions.csv")

FIELDS = [
    "tweet_id", "author_id", "author_username", "text", "created_at",
    "retweet_count", "like_count", "reply_count", "quote_count",
    "impression_count", "lang", "conversation_id", "is_reply",
    "is_retweet", "is_quote", "hashtags", "query_matched",
    "polarity", "subjectivity", "word_count", "collection_method", "scraped_at",
]

def parse_page_text(raw_text, query):
    """Parse xcancel page text into tweet dicts."""
    tweets = []
    # Split by tweet boundaries - look for @username patterns followed by time
    # Pattern: DisplayName @username TimeAgo
    parts = re.split(r'(?=\S+@\w+\s+(?:(?:\d+[hm])|(?:Mar|Feb|Jan|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+))', raw_text)
    
    for part in parts:
        # Try to extract username
        user_match = re.search(r'@(\w+)\s+((?:\d+[hm])|(?:(?:Mar|Feb|Jan|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+(?:,\s*\d{4})?))', part)
        if not user_match:
            continue
        username = user_match.group(1)
        date_str = user_match.group(2)
        
        # Text is everything after the date until stats or next tweet
        text_start = user_match.end()
        remaining = part[text_start:].strip()
        
        # Remove quoted tweets (lines starting with @)
        # Extract stats from end - look for numbers at the very end
        stat_match = re.findall(r'(\d[\d,]*)\s*$', remaining)
        
        # Clean text - remove URL domains and trailing numbers
        text = re.sub(r'\b\w+\.(com|org|net|io|co)\S*', '', remaining)
        text = re.sub(r'\s+\d+\s*$', '', text).strip()
        text = text[:500]
        
        if len(text) < 10:
            continue
            
        # Sentiment
        try:
            clean = re.sub(r'@\w+', '', re.sub(r'https?://\S+', '', text))
            blob = TextBlob(clean.strip())
            pol = round(blob.sentiment.polarity, 6)
            subj = round(blob.sentiment.subjectivity, 6)
        except:
            pol, subj = 0.0, 0.0
        
        import hashlib
        tid = hashlib.md5(f"{username}:{text[:50]}:{date_str}".encode()).hexdigest()[:16]
        
        tweets.append({
            "tweet_id": tid,
            "author_id": "",
            "author_username": username,
            "text": text,
            "created_at": date_str,
            "retweet_count": 0,
            "like_count": 0,
            "reply_count": 0,
            "quote_count": 0,
            "impression_count": 0,
            "lang": "",
            "conversation_id": "",
            "is_reply": "Replying to" in part,
            "is_retweet": False,
            "is_quote": False,
            "hashtags": ",".join(re.findall(r'#\w+', text)),
            "query_matched": query,
            "polarity": pol,
            "subjectivity": subj,
            "word_count": len(text.split()),
            "collection_method": "nitter_browser",
            "scraped_at": datetime.utcnow().isoformat(),
        })
    return tweets

def main():
    input_file = sys.argv[1]
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_tweets = []
    seen = set()
    for entry in data:
        tweets = parse_page_text(entry['text'], entry['query'])
        for t in tweets:
            if t['tweet_id'] not in seen:
                seen.add(t['tweet_id'])
                all_tweets.append(t)
    
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for t in all_tweets:
            writer.writerow(t)
    
    print(f"Wrote {len(all_tweets)} tweets to {OUTPUT}")

if __name__ == "__main__":
    main()
