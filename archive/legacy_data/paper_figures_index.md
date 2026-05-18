# Paper Figures Index — Round 9

All 8 figures are paper-ready (300 DPI). File paths relative to `PSLF-Discussion-Analysis/`.

## Substantive paper figures

### Fig S1 — `fig_substantive_1_decoupling_forest.png`
**Headline**: Sentiment-stance decoupling is COHORT-CONDITIONAL AND DIRECTIONALLY OPPOSITE.

Forest plot of OR(pursuing | negative sentiment) by cohort with 95% CIs (log-x axis):
- **Reddit r/PSLF**: OR=7.33 [4.20, 12.78] — **venting-while-committed culture**
- SDN (Medical): OR=0.27 [0.22, 0.34] — analytical decoupling
- Reddit Finance: OR=0.18 [0.11, 0.30] — strongest analytical decoupling
- Other cohorts: NULL

Use as: lead figure for substantive paper. Replaces previous pooled "OR=0.58" claim.

### Fig S2 — `fig_substantive_2_recovery_times.png`
**Headline**: Time-to-recovery shows cohort heterogeneity in temporal persistence (NEW dynamic finding).

Two panels:
- (a) Median recovery days by cohort: r/PSLF 2d, SDN 29d (14× longer), Reddit Medical 77d
- (b) Per-event recovery scatter: Reddit r/PSLF clusters near 0; SDN spreads up to 100d; Reddit Medical mostly censored at 180d

Use as: temporal-dynamics figure showing stake-driven persistence in vocational communities.

### Fig S3 — `fig_substantive_3_rejection_reasons.png`
**Headline**: PSLF rejection has cohort-distinctive AND event-distinctive reasoning patterns.

Two heatmaps:
- (a) Cohort × rejection_reason: SDN-Medical 40% servicer_distrust dominates; Reddit r/StudentLoans 42% no_reason_given (classifier over-eager); Reddit Medical 37% employer_mismatch
- (b) Event × rejection_reason: Trump EO 43% servicer_distrust spike; Payments Restart 57% no_reason_given; Final Trump Rule 38% no_reason_given + 28% servicer_distrust

Use as: substantive findings figure for the rejection-reason finding (NEW Round-9).

### Fig S4 — `fig_substantive_4_topic_3d_heatmap.png`
**Headline**: Different cohorts shift to DIFFERENT topics on the same event (3D cohort×event×topic interaction).

5-panel diverging heatmap (one per cohort), 8 events × 7 topics. Cells show post-window topic % minus pre-window %. Color: green = topic INCREASED, red = topic DECREASED.

Most striking cells:
- SAVE × career_impact: SDN +97pp vs Finance −4pp (101pp range)
- IDR × financial_planning: SDN +62pp vs r/Medical −10pp
- Biden Mass Forg × career_impact: Finance +4pp vs SDN −53pp

Use as: multi-dimensional cohort-heterogeneity supporting figure.

## Methods paper figures

### Fig M1 — `fig_methods_1_op_vs_reply_cohort.png`
**Headline**: TextBlob and VADER show OPPOSITE-DIRECTION sentiment differences within identical posts (n=15,550). Cohort-invariant construct mismatch.

Two-panel forest plot:
- (a) TextBlob: replies MORE positive than OPs in 8/8 cohorts (negative diffs)
- (b) VADER: OPs MORE arousal than replies in 8/8 cohorts (positive diffs, OPPOSITE direction)
- All cohorts cluster-bootstrap p=0 except Teaching/Nursing TB (small n)

Use as: STRONGEST single methods exemplar. Within-thread design eliminates confounds; no published precedent. Lead methods figure.

### Fig M2 — `fig_methods_2_trump_eo_joint.png`
**Headline**: Three sentiment scorers disagree on direction of Trump PSLF EO event (n=1,330) but joint shift IS decisively non-zero.

Per-scorer Hedges' g bar chart:
- TextBlob: g=−0.325 ** (negative direction)
- VADER: g=+0.161 n.s. (positive but individually NS)
- Claude: g=+0.335 ** (positive direction)
- Joint Hotelling T² = 93.0, F=30.95, p=1.11×10⁻¹⁶

Use as: per-event exemplar of construct mismatch. Joint test refutes "instruments measure same thing with noise".

### Fig M3 — `fig_methods_3_alpha_stability.png`
**Headline**: Three-rater Krippendorff's α is sample-stable across 3 corpus expansions (n=4,838 → 6,975 → 9,242). Both canonical (red, ~−0.025) and charitable (green, ~+0.18) estimates remain well below the 0.667 reliability floor.

Single panel: α point estimates with 95% CI by round, with 0.667 reliability floor and 0 reference line.

Use as: sample-stability/robustness figure. Counters "small-n noise" objection.

### Fig M4 — `fig_methods_4_per_event_cohort_forest.png`
**Headline**: Per-event × per-cohort sentiment shifts. Cohort heterogeneity: same event produces different magnitudes (and sometimes opposite signs) across cohorts. ★ = BH FDR q=0.05 significant.

Vertical forest plot of all 38 cohort-event cells with BH-FDR-significant cells highlighted (5 cells star-marked):
- SAVE × SDN +1.69 ***
- Trump EO × SDN −0.45 **
- Trump EO × r/PSLF −0.14 **
- Payments Restart × r/PSLF −0.12 ***
- Payments Restart × r/StudentLoans −0.17 ***

Use as: methods/results figure showing the per-cell cohort heterogeneity with proper multiple-comparison correction.

---

## File summary

| Figure | File | Purpose | Paper |
|---|---|---|---|
| S1 | fig_substantive_1_decoupling_forest.png | Headline: cohort-conditional decoupling | Substantive |
| S2 | fig_substantive_2_recovery_times.png | Time-to-recovery by cohort (NEW) | Substantive |
| S3 | fig_substantive_3_rejection_reasons.png | Rejection reason × cohort × event (NEW) | Substantive |
| S4 | fig_substantive_4_topic_3d_heatmap.png | Topic × cohort × event 3D | Substantive |
| M1 | fig_methods_1_op_vs_reply_cohort.png | OP vs Reply opposite directions (NEW) | Methods |
| M2 | fig_methods_2_trump_eo_joint.png | Trump EO joint Hotelling | Methods |
| M3 | fig_methods_3_alpha_stability.png | α sample-stability | Methods |
| M4 | fig_methods_4_per_event_cohort_forest.png | Per-event cohort heterogeneity (BH-FDR) | Methods/both |

## Companion existing figures (still useful)

| File | Purpose |
|---|---|
| `pslf_master_timeline_3scorer.png` | 4-panel master timeline 2010-2026 (TB, VADER, Claude, volume) |
| `pslf_master_timeline.png` | 2-panel timeline (sentiment + volume) |
| `pslf_event_timecourses.png` | 8-event timecourse grid (TextBlob) |
| `pslf_event_timecourses_vader.png` | 8-event timecourse grid (VADER) |
| `pslf_event_timecourses_combined.png` | 4 key events × 2 scorers side-by-side |
| `pslf_claude_dimensions.png` | 7-panel Claude dimensions overview |
| `pslf_claude_dimensions_by_event.png` | 9-panel pre/post by cohort |
| `volume_artifact_arctic_shift.png` | R/C diagnostic (3 panels) |
| `triangulation_figure7.png` | 3-scorer per-event forest plot (legacy from Round 7) |

## Pending figures (after in-flight data lands)

When the comments collector and test-retest finish, regenerate:
1. **Comments-level cohort heterogeneity** (separate from posts; not yet built as figure)
2. **Reddit test-retest α** added to Fig M3 (currently uses SDN α=+0.958 only)
3. **Comments TB×VADER full-corpus α** (locked at α=+0.298 already; could be a single-number callout)
