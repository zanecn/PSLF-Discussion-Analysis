"""
topic_model_bertopic.py
=======================
Bottom-up topic discovery on the PSLF corpus, complementing Claude's 7
prompt-defined topic categories.

The Claude `primary_topic` field has 7 categories (policy_uncertainty,
financial_planning, career_impact, success_story, general_question,
employer_concern, idr_concern). These were chosen from PSLF domain knowledge.
The reviewer question at any policy / methods venue will be:

  "Why these 7 categories? What about topics that don't fit into them?"

This script answers by running an unsupervised topic model and comparing
its discovered topics to the 7 prompt-defined ones. Findings to look for:

  1. Coverage: do prompt topics map cleanly to one or more discovered topics?
     (If yes -> prompt topics are a reasonable summarization of the latent
      structure)
  2. Missed topics: are there discovered topics with NO prompt-topic home?
     Most likely candidates: spousal-income / family-planning,
     IDR-recertification mechanics, employer-verification disputes
  3. Composite topics: prompt topics that fragment into multiple discovered
     ones (suggests they bundle distinct issues)

Two backends:
  --backend lda     scikit-learn LDA (default; no extra install needed)
  --backend bertopic BERTopic (requires sentence-transformers + UMAP + HDBSCAN;
                     ~3GB install: pip install bertopic)

Inputs:
  Reads from the same merged corpus the triangulation script uses (Reddit
  + SDN PSLF-filtered posts), preferring posts with a Claude primary_topic
  label so the comparison can be made.

Outputs:
  - topic_model_results.txt        - canonical artifact
  - topic_model_results.csv        - per-topic summary
  - topic_model_crosstab.csv       - prompt_topic x discovered_topic counts
  - topic_model_topics.csv         - top words per discovered topic

Usage:
  python topic_model_bertopic.py
  python topic_model_bertopic.py --backend bertopic --n-topics 30
  python topic_model_bertopic.py --include-comments  # adds comment corpus
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

try:
    from pslf_search_terms import filter_pslf_relevant
    HAS_PSLF_FILTER = True
except ImportError:
    HAS_PSLF_FILTER = False


def out_paths(backend: str) -> dict:
    """Backend-tagged output filenames so LDA and BERTopic runs coexist."""
    return {
        "txt":      f"topic_model_results_{backend}.txt",
        "csv":      f"topic_model_results_{backend}.csv",
        "crosstab": f"topic_model_crosstab_{backend}.csv",
        "topics":   f"topic_model_topics_{backend}.csv",
    }

# Curated PSLF stopwords (in addition to standard English) - high-frequency
# words that swamp every topic in domain text.
PSLF_STOPWORDS = [
    "pslf", "loan", "loans", "forgiveness", "forgive", "forgiven",
    "payment", "payments", "pay", "paid", "paying", "year", "years",
    "month", "months", "time", "way", "thing", "things", "people",
    "would", "could", "get", "got", "make", "made", "go", "going",
    "think", "know", "see", "want", "say", "said", "really", "still",
    "even", "also", "well", "much", "like", "just", "back", "lot",
    "10", "ten", "120", "qualifying", "qualify", "qualified",
    "https", "http", "www", "com", "edu", "gov", "amp",
]


def load_corpus(include_comments: bool = False, max_posts: int = None,
                include_arctic_shift: bool = True) -> pd.DataFrame:
    """Load PSLF-filtered posts + (optionally) comments. Applies the project's
    strict PSLF anchored regex (filter_pslf_relevant from pslf_search_terms.py)
    to drop non-PSLF posts. The CSVs on disk (reddit_professions_pslf.csv etc.)
    are NOT pre-filtered despite the filename - they hold the raw scrape.
    """
    if not HAS_PSLF_FILTER:
        print("[WARN] pslf_search_terms not importable; loading WITHOUT strict filter.\n"
              "       Topics will be polluted by non-PSLF content.")
    frames = []

    def _apply_pslf_filter(df: pd.DataFrame, text_col: str, title_col: str = None) -> pd.DataFrame:
        if not HAS_PSLF_FILTER:
            return df
        text_mask = filter_pslf_relevant(df[text_col].fillna(""))
        if title_col and title_col in df.columns:
            title_mask = filter_pslf_relevant(df[title_col].fillna(""))
            return df[text_mask | title_mask].copy()
        return df[text_mask].copy()

    # Reddit posts (raw -> PSLF-filtered)
    if os.path.exists("reddit_professions_pslf.csv"):
        d = pd.read_csv("reddit_professions_pslf.csv")
        n_raw = len(d)
        d = _apply_pslf_filter(
            d,
            text_col="combined_text" if "combined_text" in d.columns else "selftext",
            title_col="title" if "title" in d.columns else None)
        print(f"  reddit_professions_pslf.csv:           {n_raw:,} raw -> {len(d):,} PSLF-filtered")
        d["text"] = (d.get("title", "").fillna("") + " "
                     + d.get("selftext", d.get("combined_text", "")).fillna(""))
        d["doc_id"] = d["id"]
        d["doc_source"] = "reddit_post"
        d["doc_subreddit"] = d.get("subreddit", "")
        frames.append(d[["doc_id", "text", "doc_source", "doc_subreddit"]])

    # Round-7 PA/NP additions (raw -> PSLF-filtered)
    if os.path.exists("reddit_new_subs_pslf.csv"):
        d = pd.read_csv("reddit_new_subs_pslf.csv")
        n_raw = len(d)
        d = _apply_pslf_filter(
            d,
            text_col="combined_text" if "combined_text" in d.columns else "selftext",
            title_col="title" if "title" in d.columns else None)
        if len(d):
            print(f"  reddit_new_subs_pslf.csv:              {n_raw:,} raw -> {len(d):,} PSLF-filtered")
            d["text"] = (d.get("title", "").fillna("") + " "
                         + d.get("selftext", d.get("combined_text", "")).fillna(""))
            d["doc_id"] = d["id"]
            d["doc_source"] = "reddit_post"
            d["doc_subreddit"] = d.get("subreddit", "")
            frames.append(d[["doc_id", "text", "doc_source", "doc_subreddit"]])

    # Arctic Shift historical pull (raw -> PSLF-filtered)
    if include_arctic_shift and os.path.exists("reddit_arctic_shift_pslf.csv"):
        d = pd.read_csv("reddit_arctic_shift_pslf.csv")
        n_raw = len(d)
        d = _apply_pslf_filter(
            d,
            text_col="combined_text" if "combined_text" in d.columns else (
                "selftext" if "selftext" in d.columns else "body"),
            title_col="title" if "title" in d.columns else None)
        if len(d):
            print(f"  reddit_arctic_shift_pslf.csv:          {n_raw:,} raw -> {len(d):,} PSLF-filtered")
            text_col = ("combined_text" if "combined_text" in d.columns
                        else "selftext" if "selftext" in d.columns else "body")
            d["text"] = (d.get("title", "").fillna("") + " "
                         + d.get(text_col, "").fillna(""))
            d["doc_id"] = d.get("id", d.get("post_id", ""))
            d["doc_source"] = "reddit_arctic_shift_post"
            d["doc_subreddit"] = d.get("subreddit", "")
            frames.append(d[["doc_id", "text", "doc_source", "doc_subreddit"]])

    # SDN posts (raw -> PSLF-filtered)
    if os.path.exists("forum_pslf_discussions.csv"):
        d = pd.read_csv("forum_pslf_discussions.csv")
        n_raw = len(d)
        d = _apply_pslf_filter(d, text_col="body", title_col="thread_title")
        print(f"  forum_pslf_discussions.csv (SDN):      {n_raw:,} raw -> {len(d):,} PSLF-filtered")
        d["text"] = d["body"].fillna("")
        d["doc_id"] = d["post_id"]
        d["doc_source"] = "sdn_post"
        d["doc_subreddit"] = "sdn"
        frames.append(d[["doc_id", "text", "doc_source", "doc_subreddit"]])

    if include_comments and os.path.exists("reddit_comments_pslf.csv"):
        d = pd.read_csv("reddit_comments_pslf.csv")
        n_raw = len(d)
        d = _apply_pslf_filter(d, text_col="body")
        print(f"  reddit_comments_pslf.csv:              {n_raw:,} raw -> {len(d):,} PSLF-filtered")
        d["text"] = d["body"].fillna("")
        d["doc_id"] = d["comment_id"]
        d["doc_source"] = "reddit_comment"
        d["doc_subreddit"] = d.get("post_subreddit", "")
        frames.append(d[["doc_id", "text", "doc_source", "doc_subreddit"]])

    big = pd.concat(frames, ignore_index=True)
    n_pre_wc = len(big)
    big = big[big["text"].str.split().str.len() >= 20].copy()
    big = big.drop_duplicates("doc_id").reset_index(drop=True)
    print(f"  After word_count >= 20 + dedup:        {n_pre_wc:,} -> {len(big):,}")

    # Attach Claude prompt topics from any zeroshot CSV
    claude_topics = []
    for f in ["zeroshot_reddit_n1000.csv", "zeroshot_sdn_n1000.csv",
              "zeroshot_reddit_eventstrat.csv",
              "zeroshot_reddit_eventfull.csv", "zeroshot_sdn_eventfull.csv",
              "zeroshot_pa_np_expansion.csv", "zeroshot_reddit_fullcorpus.csv"]:
        if os.path.exists(f):
            d = pd.read_csv(f)
            if "primary_topic" in d.columns:
                claude_topics.append(d[["post_id", "primary_topic"]].drop_duplicates("post_id"))
    if claude_topics:
        ct = pd.concat(claude_topics, ignore_index=True).drop_duplicates("post_id")
        big = big.merge(ct.rename(columns={"post_id": "doc_id"}),
                        on="doc_id", how="left")
    else:
        big["primary_topic"] = pd.NA

    # Sample if max_posts requested
    if max_posts and len(big) > max_posts:
        big = big.sample(n=max_posts, random_state=42).reset_index(drop=True)

    return big


def fit_lda(docs: list[str], n_topics: int = 20, random_state: int = 42,
            max_features: int = 5000, min_df: int = 5, max_df: float = 0.5):
    """Fit scikit-learn LatentDirichletAllocation. Returns (model, vectorizer, topic_assignments)."""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    import nltk
    from nltk.corpus import stopwords as nltk_stopwords
    try:
        sw = set(nltk_stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        sw = set(nltk_stopwords.words("english"))
    sw.update(PSLF_STOPWORDS)

    vec = CountVectorizer(stop_words=list(sw), max_features=max_features,
                          min_df=min_df, max_df=max_df,
                          token_pattern=r"\b[a-z]{3,}\b")
    X = vec.fit_transform(docs)
    print(f"  Vocab size: {len(vec.vocabulary_)}")

    lda = LatentDirichletAllocation(
        n_components=n_topics, random_state=random_state,
        learning_method="online", batch_size=512,
        max_iter=20, n_jobs=1)
    print(f"  Fitting LDA (n_topics={n_topics})...")
    doc_topic_dist = lda.fit_transform(X)
    topic_assignments = doc_topic_dist.argmax(axis=1)
    return lda, vec, topic_assignments


def top_words_per_topic_lda(lda, vec, n_top: int = 12) -> list[list[str]]:
    """Return top-N words per LDA topic."""
    feature_names = np.array(vec.get_feature_names_out())
    out = []
    for k in range(lda.n_components):
        top_idx = lda.components_[k].argsort()[::-1][:n_top]
        out.append(feature_names[top_idx].tolist())
    return out


def fit_bertopic(docs: list[str], n_topics: int = "auto"):
    """Fit BERTopic with sensible defaults for PSLF discourse. Lazy-imports."""
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        print(f"\n[ABORT] BERTopic backend not installed: {e}")
        print("  Install:  pip install bertopic sentence-transformers")
        print("  Then re-run with --backend bertopic")
        sys.exit(1)
    print("  Loading sentence-transformer (this may download ~80 MB on first run)...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    print("  Encoding documents...")
    embeddings = embed_model.encode(docs, show_progress_bar=True)
    print(f"  Fitting BERTopic (nr_topics={n_topics})...")
    bt = BERTopic(language="english", nr_topics=n_topics,
                  calculate_probabilities=False, verbose=True)
    topics, _ = bt.fit_transform(docs, embeddings)
    return bt, np.asarray(topics)


def top_words_per_topic_bertopic(bt) -> list[list[str]]:
    out = []
    for tid in sorted(bt.get_topics().keys()):
        if tid == -1:
            continue
        out.append([w for w, _ in bt.get_topic(tid)[:12]])
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--backend", choices=["lda", "bertopic"], default="lda",
                        help="Topic-model backend (default lda; bertopic requires extra install)")
    parser.add_argument("--n-topics", default="20",
                        help="Number of topics (lda: int; bertopic: int or 'auto')")
    parser.add_argument("--max-posts", type=int, default=None,
                        help="Cap docs (for fast iteration; default = all)")
    parser.add_argument("--include-comments", action="store_true",
                        help="Include reddit_comments_pslf.csv in the corpus")
    parser.add_argument("--exclude-arctic-shift", action="store_true",
                        help="Exclude Arctic Shift historical posts (default: include)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print("=" * 78)
    print(f"PSLF Topic Modeling - {args.backend.upper()}")
    print("=" * 78)

    print("\nLoading corpus (applying strict PSLF filter at load)...")
    corpus = load_corpus(include_comments=args.include_comments,
                          max_posts=args.max_posts,
                          include_arctic_shift=not args.exclude_arctic_shift)
    print(f"  Total docs:                  {len(corpus):,}")
    print(f"  Sources:")
    print(corpus["doc_source"].value_counts().to_string().replace("\n", "\n    "))
    n_with_topic = corpus["primary_topic"].notna().sum()
    print(f"  Docs with Claude topic:      {n_with_topic:,} "
          f"({100*n_with_topic/max(len(corpus),1):.1f}%)")

    docs = corpus["text"].tolist()

    # === Fit topic model ===
    print(f"\nFitting {args.backend} topic model...")
    if args.backend == "lda":
        n_topics = int(args.n_topics) if args.n_topics != "auto" else 20
        model, vec, assignments = fit_lda(docs, n_topics=n_topics,
                                          random_state=args.seed)
        top_words = top_words_per_topic_lda(model, vec)
        topic_ids = list(range(n_topics))
    else:
        n_topics = args.n_topics if args.n_topics == "auto" else int(args.n_topics)
        model, assignments = fit_bertopic(docs, n_topics=n_topics)
        top_words = top_words_per_topic_bertopic(model)
        topic_ids = sorted(set(assignments) - {-1})

    corpus["discovered_topic"] = assignments

    # === Compare to Claude prompt topics ===
    print("\nBuilding prompt-vs-discovered crosstab...")
    sub = corpus.dropna(subset=["primary_topic", "discovered_topic"]).copy()
    sub["primary_topic"] = sub["primary_topic"].astype(str)
    sub["discovered_topic"] = sub["discovered_topic"].astype(int)

    crosstab = pd.crosstab(sub["primary_topic"], sub["discovered_topic"],
                           margins=True, margins_name="TOTAL")

    # Per-discovered-topic dominant prompt topic + coverage
    summary_rows = []
    for tid in range(len(top_words)):
        mask = corpus["discovered_topic"] == tid
        n_docs = int(mask.sum())
        if n_docs == 0:
            continue
        prompt_dist = sub[sub["discovered_topic"] == tid]["primary_topic"].value_counts()
        if len(prompt_dist) == 0:
            dominant = "no_claude_label"
            dom_pct = 0.0
        else:
            dominant = prompt_dist.idxmax()
            dom_pct = 100 * prompt_dist.iloc[0] / prompt_dist.sum()
        # Source mix
        src_mix = corpus[mask]["doc_source"].value_counts(normalize=True).to_dict()
        src_str = ", ".join(f"{k}:{100*v:.0f}%" for k, v in sorted(src_mix.items()))
        summary_rows.append({
            "discovered_topic_id": tid,
            "n_docs": n_docs,
            "top_words": ", ".join(top_words[tid][:8]),
            "dominant_prompt_topic": dominant,
            "dominant_prompt_topic_pct": round(dom_pct, 1),
            "source_mix": src_str,
        })
    summary = pd.DataFrame(summary_rows)

    # === Identify potentially-missed topics ===
    # Discovered topics where dominant prompt-topic share is < 35%
    # (i.e. high entropy across prompt topics) suggest the discovered topic
    # spans multiple prompt categories OR is a category the prompt missed.
    flagged = summary[(summary["dominant_prompt_topic_pct"] < 35) &
                      (summary["n_docs"] >= 30)].copy()
    flagged = flagged.sort_values("n_docs", ascending=False)

    # === Write artifact ===
    paths = out_paths(args.backend)
    crosstab.to_csv(paths["crosstab"])  # rewrite to backend-tagged filename
    summary.to_csv(paths["topics"], index=False)
    print(f"\nWriting {paths['txt']}...")
    with open(paths["txt"], "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"PSLF Bottom-Up Topic Modeling ({args.backend.upper()})\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write("Source: scripts/topic_model_bertopic.py\n")
        f.write("=" * 80 + "\n\n")

        f.write("PURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("Tests whether Claude's 7 prompt-defined `primary_topic` categories provide\n")
        f.write("an adequate summarization of the latent topic structure in the PSLF corpus.\n")
        f.write("Bottom-up topic discovery surfaces:\n")
        f.write("  - Validation: prompt topics that cleanly map to discovered topics\n")
        f.write("  - Composites: prompt topics that fragment into multiple discovered ones\n")
        f.write("  - Gaps: discovered topics with no clear prompt-topic home (potentially\n")
        f.write("    missed categories - the strongest reviewer-defense finding)\n\n")

        f.write("SAMPLE\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Total docs:                  {len(corpus):,}\n")
        f.write(f"  Docs with Claude label:      {n_with_topic:,}\n")
        f.write(f"  Backend:                     {args.backend}\n")
        f.write(f"  Topics fit:                  {len(summary)}\n\n")

        f.write("DISCOVERED TOPICS (by sample size)\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'tid':>3s} {'n_docs':>7s} {'dominant_claude_topic':<28s} {'%':>5s}  top_words\n")
        for _, r in summary.sort_values("n_docs", ascending=False).iterrows():
            f.write(f"{int(r['discovered_topic_id']):>3d} "
                    f"{int(r['n_docs']):>7d} "
                    f"{r['dominant_prompt_topic']:<28s} "
                    f"{r['dominant_prompt_topic_pct']:>5.1f}  "
                    f"{r['top_words']}\n")

        f.write("\nPROMPT-vs-DISCOVERED CROSSTAB (rows=prompt topic, cols=discovered topic id)\n")
        f.write("-" * 80 + "\n")
        f.write("Read each row: of the docs with Claude prompt-topic X, which discovered\n")
        f.write("topics absorb them?\n\n")
        # Truncated readable view (drop margins for compactness)
        ct_view = crosstab.drop("TOTAL", errors="ignore").drop("TOTAL", axis=1, errors="ignore")
        f.write(ct_view.to_string())
        f.write("\n\n(Full crosstab in topic_model_crosstab.csv)\n")

        f.write("\nPOTENTIAL MISSED CATEGORIES (dominant Claude-topic share < 35%, n>=30)\n")
        f.write("-" * 80 + "\n")
        if flagged.empty:
            f.write("  (none) - prompt categories absorb all discovered topics cleanly.\n")
            f.write("  This is a strong validity result for the prompt-defined taxonomy.\n")
        else:
            f.write(f"{len(flagged)} discovered topic(s) flagged. Inspect top_words to see\n")
            f.write("if the topic is a coherent missed category (write up as a finding) or\n")
            f.write("noise/multi-prompt-category mixture (write up as a limitation):\n\n")
            for _, r in flagged.iterrows():
                f.write(f"  tid={int(r['discovered_topic_id'])}, "
                        f"n={int(r['n_docs'])}, "
                        f"dominant_claude={r['dominant_prompt_topic']} "
                        f"({r['dominant_prompt_topic_pct']:.1f}%)\n")
                f.write(f"    top_words: {r['top_words']}\n")
                f.write(f"    sources:   {r['source_mix']}\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF ARTIFACT\n")
        f.write("=" * 80 + "\n")

    summary.to_csv(paths["csv"], index=False)
    for k, p in paths.items():
        print(f"Saved: {p}")
    print()
    print("Top discovered topics (by n_docs):")
    print(summary.sort_values("n_docs", ascending=False).head(10)[
        ["discovered_topic_id", "n_docs", "dominant_prompt_topic",
         "dominant_prompt_topic_pct", "top_words"]].to_string(index=False))


if __name__ == "__main__":
    main()
