"""
build_master_numbers_table.py
===============================
Aggregates every quotable number from the project's analysis artifacts into
ONE master CSV. Each row = one publication-ready statistic with point
estimate, CI, p-value, n, source artifact, and which paper section it
belongs in.

Output: paper_numbers_table.csv
"""
from __future__ import annotations
import io, os, sys, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

OUT = "paper_numbers_table.csv"

# Manually curated from artifacts. Each row: paper section + claim + numbers.
NUMBERS = [
    # ============================================================
    # METHODS PAPER — construct mismatch
    # ============================================================
    {"paper": "methods", "section": "abstract", "claim": "Three-rater K-α canonical at n=9,242, sample-stable across 3 expansions",
     "value": -0.0174, "ci_lo": -0.0306, "ci_hi": -0.0049, "p": None,
     "n": 9242, "source": "critical_fixes_results.txt (Fix 1)",
     "notes": "stratified bootstrap by source, B=2000"},
    {"paper": "methods", "section": "abstract", "claim": "Three-rater K-α charitable upper bound (percentile-matched)",
     "value": 0.196, "ci_lo": 0.183, "ci_hi": 0.208, "p": None,
     "n": 9242, "source": "critical_fixes_results.txt (Fix 1)",
     "notes": "Both estimates well below 0.667 floor"},
    {"paper": "methods", "section": "results — comments scale",
     "claim": "TB×VADER α on comments at 50× scale (cluster-bootstrap by post_id)",
     "value": 0.298, "ci_lo": 0.295, "ci_hi": 0.302, "p": None,
     "n": 340965, "source": "critical_fixes_results.txt (Fix 2)",
     "notes": "n_post_clusters=15,469; design effect=1.36; comments show MORE disagreement than posts (was +0.34)"},
    {"paper": "methods", "section": "results — test-retest",
     "claim": "Test-retest α (NEW Round-9 strict design, temp=1 vs temp=1)",
     "value": 0.934, "ci_lo": 0.910, "ci_hi": 0.956, "p": None,
     "n": 680, "source": "triangulation_results.txt",
     "notes": "Reddit posts. Pure stochastic re-scoring noise; isolates within-temperature variance. Methods paper headline number for noise control."},
    {"paper": "methods", "section": "results — test-retest",
     "claim": "Test-retest α (cross-temp design, temp=0 vs temp=1, supporting)",
     "value": 0.958, "ci_lo": 0.938, "ci_hi": 0.975, "p": None,
     "n": 605, "source": "triangulation_results.txt",
     "notes": "SDN posts. Slightly higher than temp=1 vs temp=1 because temp=0 is deterministic. Use as ceiling for what re-scoring at any temp could achieve."},
    {"paper": "methods", "section": "results — test-retest",
     "claim": "Exact-match rate at temp=1 vs temp=1",
     "value": 0.946, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 680, "source": "triangulation_results.txt",
     "notes": "94.6% of n=680 Reddit posts get identical 5-level sentiment label across two temp=1 scoring passes"},
    {"paper": "methods", "section": "results — Trump EO joint",
     "claim": "Trump PSLF EO joint Hotelling T² across 3 scorers (n=1,330)",
     "value": 92.996, "ci_lo": None, "ci_hi": None, "p": 1.11e-16,
     "n": 1330, "source": "critical_fixes_results.txt (Fix 4)",
     "notes": "F=30.95, df1=3, df2=1326. Joint shift decisively non-zero with directionally split components"},
    {"paper": "methods", "section": "results — Trump EO per scorer",
     "claim": "Trump EO TextBlob g (negative shift)",
     "value": -0.325, "ci_lo": None, "ci_hi": None, "p": 0.007,
     "n": 1330, "source": "critical_fixes_results.txt (Fix 4)",
     "notes": "block-permutation p"},
    {"paper": "methods", "section": "results — Trump EO per scorer",
     "claim": "Trump EO VADER g (positive, NS individually)",
     "value": 0.161, "ci_lo": None, "ci_hi": None, "p": 0.174,
     "n": 1330, "source": "critical_fixes_results.txt (Fix 4)",
     "notes": "individually NS but contributes to joint signal"},
    {"paper": "methods", "section": "results — Trump EO per scorer",
     "claim": "Trump EO Claude g (positive shift)",
     "value": 0.335, "ci_lo": None, "ci_hi": None, "p": 0.005,
     "n": 1330, "source": "critical_fixes_results.txt (Fix 4)",
     "notes": "block-permutation p"},
    {"paper": "methods", "section": "results — OP vs Reply",
     "claim": "OP vs Reply TextBlob diff (cluster bootstrap by post)",
     "value": -0.0167, "ci_lo": -0.019, "ci_hi": -0.014, "p": 0.0,
     "n": 15550, "source": "critical_fixes_results.txt (Fix 3)",
     "notes": "bootstrap p=0 (zero of 2,000 iterations crossed null). Replies more positive than OPs."},
    {"paper": "methods", "section": "results — OP vs Reply",
     "claim": "OP vs Reply VADER diff (cluster bootstrap by post)",
     "value": 0.220, "ci_lo": 0.212, "ci_hi": 0.230, "p": 0.0,
     "n": 15550, "source": "critical_fixes_results.txt (Fix 3)",
     "notes": "bootstrap p=0. OPs higher arousal than replies. OPPOSITE direction from TB."},
    # Per-cohort OP-Reply (cohort-invariance demonstration)
    {"paper": "methods", "section": "results — OP-Reply by cohort",
     "claim": "OP-Reply VADER diff in 8/8 cohorts same direction (+)",
     "value": None, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 8, "source": "per_profession_breakdowns.txt",
     "notes": "8/8 cohorts: r/PSLF +0.221, r/StudentLoans +0.246, Finance +0.305, Medical +0.199, PA +0.341, Teaching +0.269, Nursing +0.227, Other +0.215"},
    # ============================================================
    # SUBSTANTIVE PAPER — cohort heterogeneity + decoupling
    # ============================================================
    {"paper": "substantive", "section": "abstract — main headline",
     "claim": "Sentiment-stance OR in r/PSLF (REVERSE decoupling — venting culture)",
     "value": 7.33, "ci_lo": 4.20, "ci_hi": 12.78, "p": 6e-16,
     "n": 1469, "source": "per_profession_breakdowns.txt",
     "notes": "Negative-sentiment posters in r/PSLF are 7.3× more likely to be pursuing than non-pursuing"},
    {"paper": "substantive", "section": "abstract — main headline",
     "claim": "Sentiment-stance OR in SDN-Medical (analytical decoupling)",
     "value": 0.27, "ci_lo": 0.22, "ci_hi": 0.34, "p": 3e-31,
     "n": 1960, "source": "per_profession_breakdowns.txt",
     "notes": "Negative-sentiment posters in SDN are 73% LESS likely to be pursuing"},
    {"paper": "substantive", "section": "abstract — main headline",
     "claim": "Sentiment-stance OR in Reddit Finance (analytical decoupling)",
     "value": 0.18, "ci_lo": 0.11, "ci_hi": 0.30, "p": 2e-13,
     "n": 999, "source": "per_profession_breakdowns.txt",
     "notes": "Strongest analytical decoupling. Finance treats negativity as exit signal."},
    {"paper": "substantive", "section": "results — cohort heterogeneity per event",
     "claim": "Payments Restart × Reddit r/PSLF (BH-FDR significant)",
     "value": -0.124, "ci_lo": None, "ci_hi": None, "p": 0.001,
     "n": 5443, "source": "per_profession_per_event_results.csv",
     "notes": "n_pre=3,084, n_post=2,359. Cleanest opposite-sign cell vs SDN."},
    {"paper": "substantive", "section": "results — cohort heterogeneity per event",
     "claim": "Payments Restart × Reddit r/StudentLoans (BH-FDR significant)",
     "value": -0.169, "ci_lo": None, "ci_hi": None, "p": 0.001,
     "n": 6588, "source": "per_profession_per_event_results.csv",
     "notes": "n_pre=4,037, n_post=2,551. Same direction as r/PSLF, opposite SDN."},
    {"paper": "substantive", "section": "results — cohort heterogeneity per event",
     "claim": "Payments Restart × SDN-Medical (opposite-sign vs Reddit)",
     "value": 0.586, "ci_lo": None, "ci_hi": None, "p": 0.031,
     "n": 238, "source": "per_profession_per_event_results.csv",
     "notes": "n_pre=174, n_post=64. POSITIVE shift in SDN, NEGATIVE in r/PSLF + r/StudentLoans (both Bonf-sig)"},
    {"paper": "substantive", "section": "results — cohort heterogeneity per event",
     "claim": "Trump EO × Reddit r/PSLF (BH-FDR significant)",
     "value": -0.139, "ci_lo": None, "ci_hi": None, "p": 0.002,
     "n": 2666, "source": "per_profession_per_event_results.csv",
     "notes": "n_pre=1,659, n_post=1,007"},
    {"paper": "substantive", "section": "results — cohort heterogeneity per event",
     "claim": "Trump EO × SDN-Medical (BH-FDR significant; SDN amplifies r/PSLF 3×)",
     "value": -0.454, "ci_lo": None, "ci_hi": None, "p": 0.003,
     "n": 828, "source": "per_profession_per_event_results.csv",
     "notes": "n_pre=497, n_post=331. Same direction, ~3× larger than r/PSLF."},
    # Comment-level replication
    {"paper": "substantive", "section": "results — comment-level replication",
     "claim": "Cohort heterogeneity REPLICATES at comment level",
     "value": None, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 14, "source": "comment_cohort_heterogeneity_results.txt",
     "notes": "8/14 post-level cohort-event cells REPLICATE at comment level, 0 REVERSED. Strongest cell: Limited Waiver × SDN g=+0.42→+0.58 (STRENGTHENS)"},
    # Time-to-recovery (NEW Round-9 dynamic finding)
    {"paper": "substantive", "section": "results — temporal dynamics (NEW)",
     "claim": "SDN-Medical median recovery time post-event",
     "value": 29, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 8, "source": "time_to_recovery_results.txt",
     "notes": "8/8 events recovered. SDN takes ~14× longer than Reddit r/PSLF (2 days)."},
    {"paper": "substantive", "section": "results — temporal dynamics (NEW)",
     "claim": "Reddit r/PSLF median recovery time post-event",
     "value": 2, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 8, "source": "time_to_recovery_results.txt",
     "notes": "8/8 events recovered. Transient response. Stake-driven persistence hypothesis confirmed."},
    # Topic restructuring per cohort (NEW Round-9 multi-dim finding)
    {"paper": "substantive", "section": "results — multi-dim cohort heterogeneity (NEW)",
     "claim": "SAVE Forbearance × career_impact: SDN +97pp vs Finance −4pp",
     "value": 100.8, "ci_lo": None, "ci_hi": None, "p": None,
     "n": None, "source": "topic_per_cohort_per_event_results.txt",
     "notes": "101pp range across cohorts on the same topic. SDN treats SAVE as career-decision moment; Finance doesn't."},
    {"paper": "substantive", "section": "results — multi-dim cohort heterogeneity (NEW)",
     "claim": "IDR Adjustment × financial_planning: SDN +62pp vs r/Medical −10pp",
     "value": 71.2, "ci_lo": None, "ci_hi": None, "p": None,
     "n": None, "source": "topic_per_cohort_per_event_results.txt",
     "notes": "Largest single profession-level topic shift in dataset. Technical complexity drove SDN to plan."},
    {"paper": "substantive", "section": "results — pre/post sentiment shifts (HONEST CORRECTION)",
     "claim": "Trump PSLF EO pooled g (proper sample, Bonf-significant)",
     "value": -0.137, "ci_lo": None, "ci_hi": None, "p": 0.0005,
     "n": 6997, "source": "legislative_timeline_results.txt",
     "notes": "Was published as g=-0.40 with n=4K JSON-API; corrected to -0.137 with proper Arctic Shift sample"},
    {"paper": "substantive", "section": "results — pre/post sentiment shifts (HONEST CORRECTION)",
     "claim": "SAVE Admin Forbearance pooled g — DIED at proper sample size",
     "value": -0.039, "ci_lo": None, "ci_hi": None, "p": 0.188,
     "n": 6219, "source": "legislative_timeline_results.txt",
     "notes": "Was published as g=+0.51; collapsed to NULL with Arctic Shift sample. Was JSON-API artifact."},
    {"paper": "substantive", "section": "results — pre/post sentiment shifts (HONEST CORRECTION)",
     "claim": "Biden v. Nebraska SCOTUS pooled g — DIED at proper sample size",
     "value": -0.015, "ci_lo": None, "ci_hi": None, "p": 0.535,
     "n": 10375, "source": "legislative_timeline_results.txt",
     "notes": "Was published as g=-0.43; collapsed to NULL"},
    {"paper": "substantive", "section": "results — pre/post sentiment shifts (HONEST CORRECTION)",
     "claim": "Payments Restart pooled g — REVERSED sign + Bonf-significant",
     "value": -0.133, "ci_lo": None, "ci_hi": None, "p": 0.0005,
     "n": 12866, "source": "legislative_timeline_results.txt",
     "notes": "Was published as g=+0.33; reversed to -0.133. Vindicated within-method (not Simpson's paradox)."},
    # Per-author longitudinal infeasibility
    {"paper": "both", "section": "limitations / structural insight",
     "claim": "Per-author longitudinal panel infeasible at 6.4× corpus expansion",
     "value": 1, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 8, "source": "per_author_with_comments_results.txt",
     "notes": "Only 1/8 events meets n>=10 returning-with-stance threshold. Comments don't help. Structural data-design insight."},
    # Topic restructuring (composition-immune, all 8 events)
    {"paper": "substantive", "section": "results — topic restructuring",
     "claim": "IDR Account Adjustment financial_planning shift (composition-immune)",
     "value": 49.2, "ci_lo": None, "ci_hi": None, "p": 1e-4,
     "n": None, "source": "intention_results.txt",
     "notes": "Largest single per-event topic signature. Cramer's V medium-large. Composition-immune."},
    # R/C volume artifact (R/C methods note)
    {"paper": "rc_note", "section": "abstract",
     "claim": "Reddit JSON-API undercounts PSLF volume vs Arctic Shift baseline (total)",
     "value": 19, "ci_lo": None, "ci_hi": None, "p": None,
     "n": 76068, "source": "volume_artifact_arctic_shift.txt",
     "notes": "72,262 Arctic Shift PSLF posts vs 3,806 JSON-API on same 21 subs"},
    {"paper": "rc_note", "section": "abstract",
     "claim": "JSON-API undercount per year (range)",
     "value": None, "ci_lo": 12, "ci_hi": 74, "p": None,
     "n": 14, "source": "volume_artifact_arctic_shift.txt",
     "notes": "12× early years (2014-2018) → 74× peak 2023. The cap binds harder when annual volume is bigger."},
]


def main():
    df = pd.DataFrame(NUMBERS)
    df.to_csv(OUT, index=False)
    print(f"Saved: {OUT}")
    print(f"  Total publication-ready numbers: {len(df)}")
    print(f"  By paper:")
    print(df["paper"].value_counts().to_string())
    print(f"\n  By section:")
    print(df["section"].value_counts().to_string())


if __name__ == "__main__":
    main()
