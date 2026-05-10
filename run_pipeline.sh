#!/usr/bin/env bash
# PSLF rescrape + analysis pipeline.
# Designed to be runnable from a laptop (Claude Code or plain shell)
# with full outbound network access. Will fail gracefully if a target
# blocks the request (Cloudflare on Bogleheads/allnurses, etc.).
#
# Usage:
#   bash run_pipeline.sh                   # full: scrape + analyze
#   bash run_pipeline.sh --analyze-only    # skip scraping, reuse CSVs
#   bash run_pipeline.sh --scrape-only     # scrape, no analysis
#   bash run_pipeline.sh --with-comments   # also collect Reddit comment trees (needs PRAW creds)
#   bash run_pipeline.sh --with-zeroshot   # also run Claude zero-shot scorer (needs ANTHROPIC_API_KEY)
#
# Environment variables (optional):
#   REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET   Reddit PRAW (only needed for comments)
#   ANTHROPIC_API_KEY                        Anthropic key (only needed for zero-shot)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$ROOT/PSLF-Discussion-Analysis"
SCRIPTS="$ROOT/scripts"

DO_SCRAPE=1
DO_ANALYZE=1
WITH_COMMENTS=0
WITH_ZEROSHOT=0

for arg in "$@"; do
  case "$arg" in
    --analyze-only)   DO_SCRAPE=0 ;;
    --scrape-only)    DO_ANALYZE=0 ;;
    --with-comments)  WITH_COMMENTS=1 ;;
    --with-zeroshot)  WITH_ZEROSHOT=1 ;;
    -h|--help)
      sed -n '1,20p' "$0"; exit 0 ;;
    *) echo "Unknown arg: $arg" >&2; exit 2 ;;
  esac
done

mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo "==> [1/9] Installing Python dependencies"
python3 -m pip install --quiet -r "$ROOT/requirements.txt"

echo "==> [2/9] Installing Playwright Chromium (skipped if already present)"
python3 -m playwright install chromium 2>&1 | tail -3 || {
  echo "  [WARN] Playwright install failed — SDN scrape will be skipped"
}

echo "==> [3/9] Downloading NLTK data (wordnet, omw-1.4)"
python3 -c "import nltk; nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)"

if [[ "$DO_SCRAPE" == 1 ]]; then
  echo "==> [4/9] Scraping Reddit profession subreddits"
  python3 "$SCRIPTS/collect_reddit_professions.py" || echo "  [WARN] Reddit professions failed"

  echo "==> [5/9] Scraping Reddit r/AskReddit baseline (n target ~1000)"
  python3 "$SCRIPTS/collect_reddit_baseline.py" || echo "  [WARN] Reddit baseline failed"

  echo "==> [6/9] Scraping SDN forum (Playwright)"
  python3 "$SCRIPTS/collect_forum_data.py" || echo "  [WARN] SDN forum scrape failed"

  if [[ "$WITH_COMMENTS" == 1 ]]; then
    if [[ -z "${REDDIT_CLIENT_ID:-}" || -z "${REDDIT_CLIENT_SECRET:-}" ]]; then
      echo "  [SKIP] Comment collection requires REDDIT_CLIENT_ID + REDDIT_CLIENT_SECRET"
    else
      python3 "$SCRIPTS/collect_reddit_comments.py" || echo "  [WARN] Reddit comments failed"
    fi
  fi
else
  echo "==> [4-6/9] Scraping skipped (--analyze-only)"
fi

if [[ "$DO_ANALYZE" == 1 ]]; then
  echo "==> [7/9] Applying VADER sentiment"
  for csv in reddit_professions_pslf.csv forum_pslf_discussions.csv reddit_baseline_askreddit.csv comprehensive_medical_pslf_discussions.csv comprehensive_teacher_pslf_discussions.csv; do
    [[ -f "$csv" ]] && python3 "$SCRIPTS/sentiment_vader.py" --input "$csv" || echo "  [SKIP] $csv missing"
  done

  if [[ "$WITH_ZEROSHOT" == 1 ]]; then
    if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
      echo "  [SKIP] Zero-shot needs ANTHROPIC_API_KEY"
    else
      python3 "$SCRIPTS/sentiment_zeroshot.py" || echo "  [WARN] Zero-shot failed"
    fi
  fi

  echo "==> [8/9] Running analyses"
  python3 "$SCRIPTS/analyze_multi_source.py"               | tee analysis_multi_source.log
  python3 "$SCRIPTS/gen_legislative_timeline.py"           | tee analysis_legislative.log
  python3 "$SCRIPTS/analyze_admin_data_correlation.py"     | tee analysis_admin.log || \
    python3 "$SCRIPTS/analyze_admin_data_correlation.py" --no-fetch | tee analysis_admin.log
  python3 "$SCRIPTS/gen_volume_artifact_figure.py"         | tee analysis_volume_artifact.log
  python3 "$SCRIPTS/gen_hires_figs.py"                     | tee analysis_hires_figs.log

  echo "==> [9/9] Final summary"
  python3 "$SCRIPTS/final_summary.py" | tee analysis_final_summary.log
else
  echo "==> [7-9/9] Analysis skipped (--scrape-only)"
fi

echo
echo "Done. Outputs in: $DATA_DIR"
ls -lh "$DATA_DIR"/*.png "$DATA_DIR"/*.log 2>/dev/null | tail -20 || true
