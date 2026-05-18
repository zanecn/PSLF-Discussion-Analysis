# PSLF Online Discourse Analysis Project

## ⚠️ CURRENT STATE (Round 17++ — 2026-05-11)

**This file's body below describes Rounds 7-9 historical state. For current state, see PROJECT_INDEX.md and MASTER_LOCKED_NUMBERS.md (R17++ canonical).**

R17++ summary of changes since the R9 framing below:
- Project split into **6 outputs** with **R17++ #6 boost strategy** (2026-05-17 final): (P1) OP-vs-Reply reframe → **ICWSM '26 / CSCW '26 / *IC&S*** primary [was EPJ DS]; (P2) strip to Reddit Finance sign-flip → ***Political Analysis*** primary [was JCSS]; (P3) methods translation + workforce downstream via CMS NPPES → ***Health Affairs Scholar*** primary [was JGME]; (P4) broaden to comprehensive residency-program characterization dataset → *Scientific Data* with Data in Brief firm fallback; (P5) add geographic + workforce-policy analysis → ***Neurosurgery* (WK)** primary [was JAMA Surg]; (P6) multi-policy comparison → ***PLOS One*** primary [was JMIR Formative]. User is MS3 ending → research year next → NS match Sept 2027 ERAS. Recommended drafting order: P3 → P4 → P5 → P6 → P1 → P2. **Critical-path new data acquisition:** CMS NPPES (P3); ACGME + NIH multi-year (P4); HRSA HPSA + USDA RUCA (P5); additional Reddit r/StudentLoans (P6) — all free, ~5-6 weeks engineering — see `DATA_ACQUISITION_PLAN_R17pp6.md`. Conference abstracts pipeline at `CONFERENCE_ABSTRACTS_PLAN.md` (AANS Oct 2026 = critical path). NSLDS DUA application enables PGY-1 follow-up — see `NSLDS_DUA_APPLICATION_CHECKLIST.md`. **Honest realistic ERAS yield with boost strategy: ~3.8-4.5 papers in print + ~4 abstracts = ~8-9 research items from project (NS match avg ~18; contributes ~45-50%; up from R17++ #5's ~5-6).**
- **5-instrument intersection n=1,001** (3 LLMs from 3 organizations: Claude/Llama/DeepSeek + TextBlob + VADER)
- **3-LLM convergence finding (NEW HEADLINE for P1)**: combined α=+0.7590 [+0.7241, +0.7868] above 0.667 floor; cohort-heterogeneous (Reddit-only α=+0.69 boundary, SDN-only α=+0.83 above 0.80 floor)
- TB×VADER comments-scale α=+0.2892 [+0.287, +0.292] on n=519,401 — REPLICATES post-level
- Paraphrase robustness 3-prompt α=+0.9011 [+0.868, +0.930] at n=399 (R17++ #3 replication 2026-05-17); identical point estimate to n=200 R16 historical; CI half-width tightened 22%; lower-CI headroom above 0.85 widened from +0.007 to +0.018. Lexical-format robust, NOT semantic-restructuring.
- Test-retest at temp=0 vs temp=0: 100% exact-match (PERFECT determinism, closes LLM-stochasticity objection)
- **Trump-EO causal interpretation RETRACTED** — trend regression `is_2026` indicator p=0.46 NS; 2026 narrowing continues 5-year pre-existing trend
- **Paper 3 6-year sample** (2021-2026; n=37,450 raw / 35,193 OLS-fit) added; 5-year n=29,349 remains as headline cross-sectional baseline
- CMS-merge dedup bug fixed across 8 scripts (Round 17 critical fix)
- State-filtered NIH RePORTER integrated (M5+NIH locked β=−18.07 pp p=2.1×10⁻²⁸)
- Multiple citation misattributions corrected (Round 17++): 9 hard misattributions + 4 fabricated/unverifiable citations removed/replaced (see MASTER_REFERENCE_LIST.md "Round 17++ audit" notes)
- Paper 2 scoped to **post-level** cohort heterogeneity; comments-scale moved to supplement (Round 17 Option A — but see Agent 5 audit which found this scope statement INVERTS the evidence on 7/8 events; needs further revision)

For full audit history (Rounds 1-17++) and current canonical numbers, read `PROJECT_INDEX.md` then `MASTER_LOCKED_NUMBERS.md`.

---

## Overview (Round 9 update — 2026-05-10) [HISTORICAL]

Round 9 (2026-05-10) added 4 new analyses, 8 of 9 critical statistical fixes (Fix 9 awaits API key), and per-profession breakdowns that **substantially restructure the substantive headlines**. Comments collector grew the comment corpus to 340,965 rows (15,469 unique post-clusters) — Arctic Shift comments still streaming in.

**Round-9 NEW headline (substantive paper)**: Sentiment-stance decoupling has **DIRECTIONALLY OPPOSITE cohort heterogeneity**. The pooled OR=0.58 was averaging across cohorts with literally opposite-direction relationships:
- **Reddit r/PSLF** (n=1,469): negativity → MORE pursuing (OR=7.33, 95% CI [4.20, 12.78], p=6×10⁻¹⁶) — "venting while committed" amplified
- **SDN (Medical)** (n=1,960): negativity → DISengagement (OR=0.27, 95% CI [0.22, 0.34], p=3×10⁻³¹) — strong real decoupling
- **Reddit Finance** (n=999): negativity → DISengagement (OR=0.18, 95% CI [0.11, 0.30], p=2×10⁻¹³) — strongest real decoupling
- **Reddit r/StudentLoans, Medical, Teaching**: null relationship

**The relationship between negative sentiment and behavioral commitment is COHORT-CONDITIONAL AND DIRECTIONALLY OPPOSITE.** "Online sentiment about PSLF" cannot be interpreted without knowing what community it's from. The same negative-sentiment post means different things in different communities.

**Round-9 NEW headline (methods paper)**: OP vs Reply construct mismatch within identical posts — TextBlob and VADER point in OPPOSITE directions on the same OP-vs-reply comparison:
- TB Δ (OP − reply) = −0.017 (95% CI [−0.019, −0.014], cluster boot p=0)
- VADER Δ (OP − reply) = +0.220 (95% CI [+0.212, +0.230], cluster boot p=0)
- **Cohort-invariant**: same direction in 8/8 cohorts. VADER significant in 8/8; TB significant in 6/8.
- **No published precedent found** in 2-hour deep literature search. Strongest single methods exemplar.

**Round-9 LOCKED methods numbers**:
- Three-rater K-α canonical at n=9,242: **−0.0174 (95% CI [−0.031, −0.005])** — stratified bootstrap by source
- Three-rater K-α charitable: **+0.196 (95% CI [+0.183, +0.208])**
- TB×VADER comments α at n=340,965 (15,469 post-clusters): **+0.298 (cluster CI [+0.295, +0.302])** — design effect 1.36
- Trump EO joint Hotelling T² (n=1,330): **F=30.95, p=1.11×10⁻¹⁶** — joint shift decisively non-zero with directionally split components
- Test-retest α at temp=0 vs temp=1: +0.958 (still awaits proper temp=1 vs temp=1 design, Fix 9)

**Round-9 KEY citations to add** (currently NOT in this file):
- **Bestvater & Monroe (2023, Political Analysis 31(2):235-256)** — closest precedent (sentiment ≠ stance r=0.03 on Kavanaugh)
- **arXiv 2410.14626 (2024)** "You Shall Know a Tool by the Traces it Leaves" — closest comparable analysis at scale
- **Freelon et al. (2024, ANNALS Vol 712)** — qualitative R/C precedent

## Overview (Round 8 background — superseded by Round 9 above)

Round 8 (2026-05-09) brought a step-change in data: Arctic Shift (Pushshift successor) recovered **72,262 NEW PSLF posts** the Reddit JSON-API 1000-cap had been suppressing (Reddit corpus expanded ~6.4× to 85,560 PSLF-filtered posts). VADER scored on the new data, plus a 2,281-post stratified Claude scoring sample (~$13) for the new-cell event-window fill. Three substantive findings emerge or strengthen, and the headline reframings stand:

**Primary finding (methodological, sample-stable across rounds 6 → 8):** Three commonly-used sentiment instruments — TextBlob (lexical affect), VADER (expressive arousal, Hutto & Gilbert 2014), and Claude Sonnet 4 zero-shot (stance toward PSLF, per the prompt) — operationalize **substantially different latent constructs** on policy-discourse text. Three-rater Krippendorff's α=−0.018 (canonical fixed thresholds) / +0.196 (charitable upper bound with percentile-matched marginals) on **n=9,242 posts with all three scorers** (round-8 +2,281 from Arctic Shift event-window fill). Both estimates well below the 0.667 floor for tentative reliability claims (Krippendorff 1980). The finding is now sample-stable across THREE corpus expansions: n=4,838 (round-7) → n=6,975 (round-7 fullcorpus) → n=9,242 (round-8 Arctic Shift fill). The construct distinction is theoretically grounded in stance vs sentiment (Mohammad et al. 2016, SemEval-2016 Task 6; **Bestvater & Monroe 2023, Political Analysis 31(2):235-256** — sentiment vs stance r=0.03 on Kavanaugh; **arXiv 2410.14626 2024** — 9 sentiment tools at scale, F1=0.89 for tool identification) but its empirical magnitude on policy discourse with a third LLM-stance dimension has not been previously quantified at this scale.

**Disagreement is NOT LLM stochasticity** (Round-7 critical fix #5; held through round-8). Test-retest α=+0.958 (95% CI [+0.938, +0.975]) on n=605 SDN posts at temperature=0 vs temperature=1; exact-match 95.2%. The cross-instrument α near zero is substantive instrument divergence, not measurement noise.

**Sensitivity check (Round-8 confirmation):** SDN-Medical-excluded canonical α=−0.009 vs full-sample α=−0.018 (delta +0.009, both well below 0.667 floor). The methods finding is robust to SDN-Medical removal at n=6,111 non-SDN posts.

**Lead exemplar (holds at round-8):** The 2025 Trump PSLF Executive Order still produces directionally opposite Hedges' g across the three instruments at n=1,330 posts (Trump EO event-window): TextBlob g=−0.32, VADER g=+0.16, Claude g=+0.33. The TB-vs-Claude direction split is most pronounced in SDN-Medical (g_TB=−0.45, g_Claude positive); in non-SDN cohorts (Reddit r/PSLF g_TB=−0.14) the dissociation is muted. **The construct dissociation is now characterized as cohort-conditional**, not population-uniform — itself a substantive contribution.

**Companion methodological finding (Round-8 quantified):** Reddit's 1000-result API cap creates a year-varying volume-undercount artifact. Arctic Shift baseline (uncapped) shows JSON-API undercounts PSLF Reddit volume by **12× (early years) to 74× (peak 2023)**. Total: 72,262 Arctic Shift PSLF posts vs 3,806 JSON-API PSLF posts on the same 21 subreddits = **19× total undercount**. Previously published "~10× recency bias" was directionally correct but specifically the gap GROWS with annual volume; the cap binds harder when activity is higher. Arctic Shift is the only viable source for longitudinal Reddit research on PSLF. (Cite **Freelon et al. 2024, ANNALS Vol 712** "The Post-API Age of Social Media Data Access" — qualitative framing this paper provides empirical complement to.)

**Round-8 substantive headline (NEW — cohort heterogeneity):** Per-event × per-profession analysis on the post-Arctic-Shift corpus (n=76,074 PSLF-filtered) reveals **SDN-Medical and Reddit-general respond in opposite directions on 5 of 8 events**:
  - **Limited PSLF Waiver**: SDN g=+0.42 *(p=0.02)* vs Reddit r/StudentLoans g=−0.29 *(p=0.07)*. Opposite signs.
  - **Payments Restart**: SDN g=+0.59 *(p=0.03)* vs Reddit r/PSLF g=−0.12 *(p<0.001)*. Both significant, opposite signs.
  - **SAVE Admin Forbearance**: SDN g=+1.69 *(p<0.001, n=97/23)* — the largest single effect in the dataset — vs Reddit r/PSLF g=+0.01 NS. SDN saw "good news, we're protected"; Reddit-general didn't.
  - **Trump PSLF EO**: SDN g=−0.45 *(p=0.003)* vs Reddit r/PSLF g=−0.14 *(p=0.002)*. Same direction, SDN ~3× larger.
  - **Final Trump PSLF Rule**: SDN g=+0.66 *(p=0.04)* vs Reddit r/PSLF g=+0.14 *(p=0.03)*. Same direction, SDN ~5× larger.

Pooled analyses obscure this entirely because the much-larger general-Reddit audience (n_Reddit ≈ 65K vs n_SDN ≈ 4K) averages out the SDN signal. **This is the substantive paper's new lead finding.**

**Pre/post pooled findings (collapsed at round-8 with proper sample size):** Several previously-published pooled headline effects evaporated when Arctic Shift restored the suppressed pre-event sample:
  - SAVE Forbearance: g=+0.51 → g=−0.04 NS (was small + driven by SDN; pooled now NULL)
  - Biden v. Nebraska SCOTUS: g=−0.43 → g=−0.015 NS (was JSON-API artifact)
  - Biden Mass Forgiveness: g=−0.25 → g=−0.004 NS
  - Trump PSLF EO: g=−0.40 → g=−0.137, p_boot=0.0005 (SURVIVES Bonferroni at much larger sample)
  - Payments Restart: g=+0.33 → g=−0.133, p_boot=0.0005 (REVERSED sign + Bonferroni-significant)

**Substantive single-event direction concordance (held through round-8):** At well-powered Claude triangulation (n_event=313–771), still 2/8 events triple-concordant: Biden Mass Forgiveness (all negative) and Biden v. Nebraska SCOTUS (all negative). Trump EO remains TB-negative / VADER+Claude-positive (the lead methods exemplar).

**Scope clarification (round-4):** This project studies **online PSLF discourse**, not the PSLF-borrower population. Reddit + SDN users skew young, white, male, more educated than the ~1M+ borrower population, and Bogleheads + allnurses are Cloudflare-blocked. Findings should be interpreted as discourse construct measurement, not behavior.

## Repository
- Fork: https://github.com/zanecn/PSLF-Discussion-Analysis
- Upstream: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis
- PR #1: https://github.com/margaretcdeleon/PSLF-Discussion-Analysis/pull/1
- Branch: `playwright-sdn-scraper`

## Data (as of 2026-05-09)
- **81,995 PSLF-relevant posts** strict-anchored filter (round-8 Arctic Shift expansion +72,262 to existing ~9,681); **76,074** sentiment-eligible (wc≥20) after dedup + 2009–2026 date trim. Reddit corpus expanded ~6.4×; pre-2018 era (~4,310 posts) recovered from previous near-zero coverage.

### Round-8 corpus composition (post-Arctic-Shift)
  - Reddit r/PSLF: 35,614 (was ~951; **37× growth from JSON-API to Arctic Shift**)
  - Reddit r/StudentLoans: 29,173 (was ~762; **38× growth**)
  - Reddit Finance subs (r/personalfinance + r/financialindependence + general_finance): 5,028 (was ~656)
  - SDN (Medical): 4,053 (unchanged — separate forum, not affected by JSON-API cap)
  - Reddit Medical: 1,195 (was 605)
  - Reddit Teaching: 765 (was 521)
  - Reddit PA: 342 (was 257)
  - Reddit Nursing: 159 (was 127)
  - Other (Law, Pharmacy, OT, SLP, social_work, federal): ~600 combined
  - Reddit medical/teacher (legacy CSVs): 605 + 521 = 1,126
  - Reddit professions: 11,845 raw → 3,806 PSLF-filtered (+ length-residualised)
  - SDN Forum: 45,334 raw → 4,749 PSLF-filtered
  - **23 communities** (21 subreddits + SDN). Round-7 added: r/PAstudent (25 PSLF), r/prephysicianassistant (25 PSLF), r/CRNA (2 PSLF) — total 52 net new posts strengthen the PA + nurse-anesthesia samples.
  - **Cloudflare-blocked sources NOT scraped**: bogleheads.org, allnurses.com, physicianassistantforum.com (all 3 confirmed blocked even via Playwright; PAF blocked at search endpoint with active Turnstile challenge as of 2026-05-08).
- **Three-scorer sentiment**: TextBlob polarity + VADER compound + Claude Sonnet 4 zero-shot. Pearson correlations: TB×VA r=0.30, TB×CL r=0.02, VA×CL r=0.12 (all p<0.001 except TB×CL p=0.09). Three-rater Krippendorff's α (ordinal, **n=4,787 after Path C event-window fill**): −0.03 with fixed thresholds, **+0.17 with percentile-matched marginals** — both well below the 0.667 floor for tentative reliability claims. Marginal distributions diverge sharply (VADER calls 67% of posts very_positive vs Claude's 4.3%).
- **Strict PSLF filter** (`filter_pslf_relevant` in pslf_search_terms.py) — generic 'forgiveness' terms must co-occur with a PSLF-specific anchor (PSLF/MOHELA/qualifying employer/etc.) within 80 chars
- **Length-residualised analysis**: outcome = residuals of polarity ~ log(word_count) + source + profession (round-4 fix; round-5 added QR rank check to drop perfectly-collinear src/profession dummies for SDN)
- **r/AskReddit baseline** (n=177; small, not length-matched in raw form) + **topical-near baseline** (n=7,750 off-PSLF posts in same subs)

## Key Scripts (in scripts/)
- `collect_forum_data.py` — SDN scraper (Playwright headless + requests/BS4)
- `collect_reddit_professions.py` — Reddit JSON API scraper, year-windowed (round-3 fix)
- `collect_reddit_baseline.py` — r/AskReddit + topical-near baselines
- `collect_reddit_comments.py` — Reddit comment trees (needs PRAW API keys)
- `analyze_multi_source.py` — Cross-platform/profession statistical analysis
- `gen_hires_figs.py` — 300 DPI sentiment comparison + word cloud figures
- `gen_legislative_timeline.py` — Policy event timeline + pre/post analysis (raw + residualised) + sensitivity + bootstrap; emits `legislative_timeline_results.{txt,csv}` artifact alongside figures (round-5)
- `gen_volume_artifact_figure.py` — Reddit/CFPB volume ratio diagnostic
- `analyze_admin_data_correlation.py` — CFPB cross-correlation + R/C ratio
- `confound_audit.py` — Profession × year, length × polarity, pre/post word count tests
- `sentiment_vader.py` — VADER scoring (adds vader_compound columns to CSVs)
- `sentiment_zeroshot.py` — Claude API classifier (Sonnet 4); round-5 added preflight auth check + AuthenticationError fail-fast + 5-error circuit breaker (was silently catching auth errors and burning ~715 calls before this fix)
- `sentiment_triangulation.py` — Round-5: three-scorer Krippendorff's α + per-event Claude pre/post + Figure 7 (TB×VA×CL forest plot). Round-7 added: bootstrap CI on α (B=2000), per-event block-permutation, percentile-matched α as charitable bound, test-retest section. Emits `triangulation_results.{txt,csv}` and `triangulation_figure7.png`.
- `pslf_intention_analysis.py` — Round-7 (2026-05-08): analyses Claude `pslf_stance` (pursuing/considering/rejecting/completed) as the BEHAVIORAL INTENTION measure, separate from sentiment. Outputs stance × profession × event cross-tabs, pre/post rejecting-rate shifts with 2-prop z-test + chi-sq, sentiment×stance decoupling cross-tab, topic×stance cross-tab. Headline: 80.8% of "negative"-sentiment posts are still pursuing/considering. Trump EO had only +2.5 pp rejecting-rate shift (NS) despite large negative sentiment shift — "resolute commitment under threat" pattern. Administrative pauses (SAVE Forbearance −16.6 pp, Final Trump Rule −13.5 pp) substantially REDUCE rejection. Emits `intention_results.{txt,csv}`, `intention_trajectory.png`, `intention_event_forest.png`.
- `collect_pa_forum.py` — Round-7: scaffold for physicianassistantforum.com scrape; **Cloudflare-blocked at search endpoint as of 2026-05-08** (Playwright passes homepage but search returns Turnstile challenge). Code preserved as starting point if Cloudflare loosens or with residential proxies.
- `pslf_search_terms.py` — filter_pslf_relevant, anchored regex
- `final_summary.py` — Statistical summary report

## Headline Findings (associational; survive 4 audit rounds)

All effects below are reported as Hedges' g + Glass's Δ_pre (raw) and length-residualised g (round-4 fix). **Block-permutation p-values** (Bickel et al. 1989, B=2000, per-event seed; Round-7 critical fix #1: was moving-block bootstrap WITH replacement, now block PERMUTATION WITHOUT replacement which is the correct two-sample autocorrelation-aware null). Bonferroni α/8 = 0.00625; Holm-Bonferroni step-down also reported. Canonical numbers live in `legislative_timeline_results.txt`.

| Event | g_raw | g_resid | p_boot (corrected) | p_holm | parametric p | survives Bonf/Holm? |
|-------|-------|---------|--------------------|--------|--------------|---------------------|
| **Biden v. Nebraska SCOTUS** (2023-06-30) | −0.43 | −0.39 | **0.0075** | 0.060 | <1e-6 | ✗ neither |
| **Trump PSLF EO** (2025-03-07) | −0.40 | −0.39 | **0.0100** | 0.070 | <1e-7 | ✗ neither |
| **SAVE Admin Forbearance** (2024-08-09) | +0.51 | **+0.58** | 0.0130 | 0.075 | <1e-5 | ✗ neither |
| **Final Trump PSLF Rule** (2025-10-30) | +0.30 | +0.18 | 0.0125 | 0.075 | <1e-4 | ✗ neither |
| **Limited PSLF Waiver** (2021-10-06) | +0.35 | +0.36 | 0.0385 | 0.154 | <1e-5 | ✗ neither |
| Payments Restart (2023-10-01) | +0.33 | +0.34 | 0.0745 | 0.224 | 0.0048 | ✗ neither (window overlaps Biden v. Nebraska) |
| Biden Mass Forgiveness (2022-08-24) | −0.25 | −0.23 | 0.170 | 0.341 | 0.031 | ✗ NS |
| IDR Account Adjustment (2022-04-19) | −0.24 | −0.25 | 0.205 | 0.341 | 0.006 | ✗ NS |

**Round-7 substantive update**: with the corrected bootstrap, **ZERO events survive bootstrap-Bonferroni or Holm-Bonferroni at family-wise α=0.05.** Trump PSLF EO p_boot moved from 0.006 → 0.0100, just outside the α/8=0.00625 threshold. Biden v. Nebraska SCOTUS p_boot moved from 0.0065 → 0.0075, also outside. The parametric p column is known-inflated 30–100× by autocorrelation and should not be the basis for substantive claims. The audit's prediction that "a properly stratified block bootstrap will likely give larger p-values" was confirmed.

**Window-sensitivity flag (Round-7 should-fix #10)**: three events have window-sensitivity SD > 0.20 (IDR Account Adjustment SD=0.233; Payments Restart SD=0.219; SAVE Admin Forbearance SD=0.326), indicating effects are highly window-dependent (likely transient or regression to the mean). Trump PSLF EO is the most window-stable (SD=0.030).

Key descriptive observations (NO causal claims, NO behavioral interpretation):
1. **The 60-day window following the Trump PSLF EO is the only event with a clear bootstrap-Bonferroni-significant shift** (g=−0.40 raw, g=−0.39 residualised; bootstrap p=0.006 < α/8=0.00625). Direction matches the policy mechanism (rule restricts PSLF processing for "illegal-purpose" employers).
2. **The 90-day window following the SAVE administrative forbearance shows the largest positive shift** (g=+0.51 raw → +0.58 length-residualised; bootstrap p=0.017 — passes 0.05 but does NOT clear Bonferroni). g grows under length adjustment, which is unusual: post-period posts are *shorter* on average, so the residualised effect rules out length confound. Adjacent-event contamination (8th Circuit SAVE injunction Jul 2024, Nov election) is not ruled out.
3. **The 90-day window following Biden v. Nebraska shows the largest negative shift in magnitude** (g=−0.43 raw, g=−0.39 residualised, Glass's Δ_pre=−0.48; bootstrap p=0.0065 — just at Bonferroni boundary). Window overlaps with the October 2023 payments restart; effects not separately identified.
4. **Cross-source baseline calibration**: r/AskReddit length-matched baseline polarity = 0.015 (n=177; small sample, sensitivity to n is open). PSLF medical posts polarity = 0.072. PSLF discussion is *slightly more positive* than typical Reddit when length-adjusted — challenges any "PSLF most negative" framing.
5. **CFPB-sentiment cross-correlation null** (all 13 lags p>0.05 after Bonferroni, first-differenced) — online sentiment and formal complaint volume are decoupled signals, NOT a redundant measurement.
6. **Three-scorer triangulation reveals construct disagreement** (round-5 + Path C, n=4,787 union of five zero-shot subsamples with all three scorers; per-event tests are now well-powered at n_pre=166–610 and n_post=109–437). Krippendorff's α for the three-rater ordinal task is +0.17 with percentile-matched marginals — well below 0.667. Direction concordance is sharper than the early underpowered subsample suggested: **only 2/8 events have all three scorers agreeing on sign — Biden Mass Forgiveness and Biden v. Nebraska SCOTUS, both negative**. Six of eight events have at least one scorer disagreeing on direction. **Critical revision (Path C)**: the Trump PSLF EO is *not* triple-concordant in the well-powered triangulation. TextBlob says g=−0.39 (negative shift, p<10⁻⁶) but Claude says g=+0.41 (positive, p<10⁻⁶) and VADER says g=+0.21 (positive, p=0.0007). The earlier "triple-concordant Trump EO" claim was an artifact of the n=50/side eventstrat subsample. **Net result: zero events are simultaneously bootstrap-Bonferroni-significant AND triple-concordant.** Biden Mass Forgiveness is concordant but bootstrap-NS (p=0.155). Trump EO is bootstrap-Bonferroni-significant on TextBlob but direction-split across instruments. The methodological co-headline (sentiment scorers fundamentally disagree on PSLF text) is *strengthened*; the substantive co-headline (a single robust event finding) is *removed*.

7. **Intention shifts are PREDOMINANTLY composition shifts, not within-person stance change** (round-7 floor-effect investigation + per-author longitudinal panel, 2026-05-08; see `floor_effect_investigation.txt`). Two independent analyses converge:
   - **Floor-effect investigation**: SDN-Medical author overlap across the 8 events ranges from 18% (Limited Waiver) to 42% (Trump EO). Most authors do NOT post in both windows. Final Trump PSLF Rule SDN-Medical: 0% author overlap. All 18 pre-rule rejecting authors went silent; 14 entirely new authors populated the post-window discourse. WITHIN the same topic, rejecting still vanishes (career_impact: pre 47% rejecting → post 0%), so the topic-mix-confound hypothesis only partially explains the floor effect. The composition turnover is the dominant driver.
   - **Per-author longitudinal panel** (round-7 follow-up to floor-effect): when filtered to authors with stance-classifiable posts in BOTH pre and post windows (with [deleted]/bot filtering), only **1 of 8 events meets a >=10-returning-authors threshold**. For 7 of 8 events, within-person inference is INFEASIBLE FROM THIS CORPUS. The Trump PSLF EO event (n=12 returning) shows Δ rejecting within-person = +16.67 pp with 95% bootstrap CI [−16.7, +50.0] and McNemar p = 0.625 — statistically indistinguishable from 0 OR from the pooled +2.5 pp NS estimate. Wide CI confirms the n=12 estimator is too noisy for substantive inference.
   - **Conclusion**: The data design itself does not support within-person inference for PSLF-discourse stance dynamics. **Pooled pre/post stance shifts must be interpreted as discussant-pool composition shifts**, not as borrower stance changes. This is a fundamental limitation of forum-based discourse data, not a fixable analysis choice.

8. **Headline intention findings (with revised composition-shift framing)** (n=6,982 unique posts after fullcorpus run; 5,226 with non-unknown stance). Substantive policy patterns via Claude `pslf_stance`:
   - **Sentiment×stance decoupling**: 85.6% of "negative"-sentiment posts are still `pursuing` or `considering` (n=2,243; tighter at larger sample). Affect doesn't determine commitment. **This is the strongest pure-cross-sectional substantive finding** — composition-immune.
   - **IDR Account Adjustment +10.0 pp rejecting (p=0.005)** is the most defensible behavioral pre/post finding: corroborated by topic shift (financial_planning **+49 pp**, the largest in the dataset) AND survives within-topic. Even with composition turnover, the topic-shift signature is composition-immune (post topics depend on event, not poster identity).
   - **Trump PSLF EO +2.5 pp NS**: a NULL result. Original "resolute commitment under threat" framing was overreach (NS is absence of evidence, not evidence of resolute commitment). Honest reframe: "no detectable rejecting-rate shift in 60d window despite negative sentiment shift; we cannot distinguish stance stability from composition turnover toward less-committed posters."
   - **Final Trump PSLF Rule −13.5 pp (p<0.0001)**: real shift in DISCUSSANT POOL but NOT defensibly a borrower-decision finding. The 0% author overlap on the SDN-Medical cell means rejecting authors departed; new authors with different priors arrived. Should be re-cast as "post-rule discourse populated by entirely different posters with materially different stance distributions."
   - **SAVE Admin Forbearance −16.6 pp**: highest window-sensitivity SD (0.326; effect ranges +1.03 → +0.25 across 30/180d windows), 34% author overlap. Composition shift dominant. The "administrative pauses reduce rejection" interpretation is too strong; "pause-period discourse less rejection-coded" is the safer claim.
   - **Limited PSLF Waiver +6.0 pp**: lowest author overlap (18%) — almost entirely composition turnover. The "good-news anxiety" mechanism is even less defensible than the audit suggested.
   - **Profession differences (cumulative stance)**: SDN (Medical) has highest rejecting rate at 13.6% (n=1,960); PA, Nursing, OT, SLP, Pharmacy skew "considering" (50–60%); Medical and Teaching skew "pursuing" (56–58%).
   - **The discourse signature typology** (TB+/CL− = lexical relief masking stance disengagement; all− = genuine bad-news consensus; TB−/CL+ = resolute commitment under threat) is itself a contribution to policy-discourse research, but should be presented as descriptive of WHO POSTS WHEN, not as evidence of within-person dynamics.

8. **Per-event topic-distribution shifts** (round-7 expansion, n=4,838 with valid Claude scoring). All 8 events show highly significant shifts in WHAT people are talking about (chi-sq p<10⁻⁴ for every event). The substantive narratives:
   - **Limited PSLF Waiver**: success_story −31.6pp, financial_planning +13.2pp. Old success stories displaced by waiver-eligibility planning surge.
   - **IDR Account Adjustment**: financial_planning **+49.2pp** (largest shift in the dataset), general_question −30.5pp. Massive recalculation surge — technical complexity drove people to plan, not ask.
   - **Biden Mass Forgiveness**: career_impact −35.8pp, general_question +23.1pp. Career deliberation displaced by basic "what about MY plan?" questions.
   - **Biden v. Nebraska SCOTUS**: policy_uncertainty +23.0pp, financial_planning −21.6pp. Uncertainty surged → planning ceased.
   - **Payments Restart**: policy_uncertainty −24.3pp, financial_planning +14.1pp. Uncertainty RESOLVED → planning resumed. Mirror image of Biden v. Nebraska.
   - **SAVE Admin Forbearance**: financial_planning −29.1pp, career_impact +26.7pp. No need to plan short-term → people debated long-term career decisions.
   - **Trump PSLF EO**: policy_uncertainty −21.7pp (counterintuitive!), financial_planning +12.9pp. Clear bad news REDUCED uncertainty (now everyone knew the threat) and drove planning.
   - **Final Trump PSLF Rule**: policy_uncertainty +16.5pp, general_question −9.0pp. Final rule generated MORE uncertainty (interpretation work) than the EO that preceded it.
   - These topic shifts are MORE STATISTICALLY ROBUST than the per-event sentiment shifts because chi-sq on the full 7-category contingency table is sensitive even to modest mix changes. They tell a coherent narrative about how policy events restructure discussion content even when sentiment direction is contested.

9. **Per-event × per-profession TOPIC shifts** (round-7 expansion). Of 9 (event, profession) cells with n_pre, n_post >= 20 (and profession n>=40), 8 are highly significant (chi-sq p<0.001). Coverage is again SDN (Medical)-dominated, but the SDN findings are substantively richer than the pooled topic shifts because the SDN community is well-powered enough to show topic *consolidation* dynamics:
   - **Trump PSLF EO × SDN (Medical)** (n=494/317): `policy_uncertainty` 63.6% → 36.3% (−27.3pp), `career_impact` 7.5% → 25.6% (+18.1pp, ~3× growth), `financial_planning` 9.1% → 25.6% (+16.4pp, ~3× growth). Medical residents consolidated from abstract anxiety into active "what does this mean for my career" planning. The EO clarified the threat enough to enable concrete decision-making.
   - **IDR Account Adjustment × SDN (Medical)** (n=191/255): `financial_planning` 17.3% → 78.8% (+61.5pp, **biggest single profession-level topic shift in the dataset**), `general_question` 35.6% → 0.4% (−35.2pp). Questions transmuted into detailed planning as the policy's technical complexity drove residents to model their specific eligibility scenarios.
   - **Biden v. Nebraska SCOTUS × SDN (Medical)**: `policy_uncertainty` 9.5% → 42.7% (+33.2pp), `financial_planning` 52.4% → 15.7% (−36.7pp), `career_impact` 31.2% → 3.4% (−27.8pp). Acute uncertainty crowded out everything substantive.
   - **Payments Restart × SDN (Medical)**: `policy_uncertainty` 41.6% → 6.3% (−35.3pp), `financial_planning` 16.2% → 46.0% (+29.8pp). Mirror of Biden v. Nebraska — uncertainty resolved, planning resumed.
   - **Limited PSLF Waiver × SDN (Medical)**: `success_story` 41.1% → 5.6% (−35.5pp), `financial_planning` 25.1% → 39.5% (+14.5pp), `policy_uncertainty` 8.4% → 20.6% (+12.3pp). Old success stories displaced by new-eligibility planning AND uncertainty about the waiver's mechanics.
   - **r/StudentLoans × Final Trump Rule** (n=25/39, only non-SDN cell): chi-sq p=0.58 NS — generic student-loan community didn't restructure topic mix around the PSLF-specific rule.
   - **Coverage limit**: per-event × per-profession topic analysis only meets the n>=20 threshold for SDN (Medical) on every event and r/StudentLoans for one event. Other professions don't have enough per-event posts. This is the principal motivation for full-corpus Claude scoring — would push Medical (Reddit), Teaching, PA, Nursing, Finance into the topic-by-event analysis.

10. **Career stage extracted from text (keyword classifier; ~15% coverage)** — within the subset of posts with explicit career-stage markers (MS1-4, PGY-X, "as a resident", "attending", etc.; n=718 of 4,842 = 14.8%):
    - **Residents are the most polarized career stage**: 44.6% pursuing AND 14.9% rejecting (n=121). Both the highest commitment AND highest rejection. Peak decision moment for PSLF — they're either all-in or actively walking away.
    - **Fellows are most stable**: 65.2% considering, 29.9% pursuing, only 3.4% rejecting (n=204). Career-stage-locked-in.
    - **Attendings have surprisingly high rejection**: 14.8% rejecting (matching residents' rate) with only 19.4% pursuing (n=108). Likely retrospective regret — people who realized PSLF wouldn't work out for their employer or didn't pursue it in time.
    - **Medical students skew pursuing/considering**: 33.3% pursuing, 57.8% considering, 8.9% rejecting (n=45). Early-career enthusiasm before the rules become real.
    - **PA students mostly considering** (80.8%, n=26): pre-decision exploration.
    - These are descriptive findings on the explicit-mentioner subset only; pre/post × career-stage cells largely fail n>=10 threshold (only 3 cells qualify).
    - **Coverage is the bottleneck.** Adding `career_stage` to the Claude prompt during a full-corpus run would push coverage from 15% to ~90%+ and enable per-event × career-stage analysis with adequate power for residents and fellows specifically.

11. **Per-event × per-profession intention + sentiment shifts** (round-7 expansion + PA/NP top-up; n>=10 per cell). Coverage is dominated by SDN (Medical) — the largest medical-PSLF community — but the +51 PA/NP scoring (post r/PAstudent + r/prephysicianassistant + r/CRNA) brought PA into the per-event sentiment table for 4 events. Patterns:
   - **Convergent profession response** to administrative resolution: Final Trump PSLF Rule reduced rejecting-rate by 43.9 pp in SDN (Medical) AND by 32.1 pp in Finance (p=0.030, n_pre=12/n_post=21). The relief signal was not exclusive to medical communities. SAVE Admin Forbearance similarly reduced rejecting across SDN (-41.9 pp, p<0.001), Medical (-10 pp, NS), and Finance (-8 pp, NS).
   - **Divergent profession response to ambiguous policy**: Biden Mass Forgiveness moved SDN (Medical) rejecting -19 pp (NS) but moved Reddit Medical +10 pp (NS) — opposite signs across two medical communities, plausibly a residency-vs-student-cohort split (SDN skews resident/attending; r/medicalschool skews pre-clinical). IDR Account Adjustment shows the same pattern: SDN +12.6 pp (p=0.003) vs Medical -9.0 pp (NS). Caveat: small per-event n's for Reddit Medical (≤20).
   - **PA-specific Claude sentiment cells** (round-7 PA top-up; small n but suggestive): SAVE Forbearance × PA g=+0.74 (n=17/10, p=0.054 marginal) — *opposite* SDN's g=−2.33; Final Trump Rule × PA g=−0.64 (n=15/10, NS) — opposite SDN's g=+0.52; Trump PSLF EO × PA g=−0.44 (n=12/11, NS) — opposite SDN's g=+0.57. PAs may show different stance trajectories than physicians around these specific events. Need more data (Cloudflare-blocked PAF would have helped) before publication-quality claim.
   - **Limited PSLF Waiver SDN-only signal**: +7.0 pp (p=0.019) rejecting-rate INCREASE post-waiver in SDN (Medical) — the "good-news anxiety" pattern at scale. Other professions don't have enough per-event posts to corroborate.
   - Coverage limit: Nursing, Teaching, Law, OT, SLP, Pharmacy, etc. still have insufficient per-event samples (n<10 in pre or post for most events) — profession-stratified per-event analysis here is principally a SDN-Medical-vs-Reddit-Medical-vs-PA comparison plus selected Finance/Teaching cells.

### Analytical Caveats (state explicitly in any write-up)
- Pre/post tests are **associational**, not causal: no interrupted-time-series counterfactual.
- Adjacent events (Biden v. Nebraska + Payments Restart, SAVE Block + SAVE Forbearance) have overlapping windows; effects not separately identified.
- TextBlob-VADER correlation r=0.31 indicates weak inter-instrument agreement; **three-scorer triangulation complete (round-5 + Path C)** confirms this extends to Claude (TB×CL r=0.02 ns, VA×CL r=0.12, three-rater α=+0.17 with percentile-matched marginals). The three sentiment instruments are measuring different latent constructs. With proper power on Path C, the per-event direction-disagreement is sharper than the early subsample showed: 6/8 events are direction-split, including the Trump PSLF EO. See `triangulation_results.txt`.
- Reddit's 1000-result API cap is **partially real / partially confounded with growth** — see Volume-Artifact section.
- Cloudflare-blocked sources (Bogleheads, allnurses, **physicianassistantforum.com** — round-7 attempt 2026-05-08 confirmed even Playwright + cloudscraper + cookie-transfer all blocked at the search endpoint; homepage loads but search returns Cloudflare Turnstile challenge) → financially-sophisticated planners + dominant nursing community + PA forum PSLF discussion all missing.
- Block-bootstrap permutation (Künsch 1989, B=2000) revises 3/8 events to non-significant after autocorrelation correction; the parametric Welch's t had been inflated 30-100×.
- Length confound: 4/8 events have significantly different pre/post word counts. Round-4 length-residualised analysis confirms primary findings survive (and SAVE Forbearance strengthens).
- **Discourse vs borrower scope**: findings concern online PSLF discussants (Reddit + SDN demographics), not the ~1M+ PSLF-eligible borrower population.

### Volume Artifact: Real Growth + API Cap (round-3 quantification)
- **r/PSLF was created 2014-08-21**. 12-year sub history. Sub paginates back exactly 998 posts spanning ~30 days in active periods.
- **CFPB ground truth shows real growth**: PSLF complaints 341 (2016) → 2,223 (2025), ~6.5× increase.
- **Reddit/CFPB ratio over time** (raw counts; `reddit_cfpb_volume_ratio.csv` — note: NOT length-matched, NOT topic-filtered to PSLF on the CFPB side):
  - 2017: 0.12
  - 2020: 0.41
  - 2024: 0.60
  - 2025: 1.63
  - 2026 (Q1-May, partial year — CFPB lags ~3 mo): **8.90**
- The ~74× growth in R/C ratio is too large to be real growth alone. **Mix: ~6-7× real growth, ~10× API-cap recency bias.** The 2026 spike is partly because CFPB data is incomplete for the year — interpret directionally, not as a fixed multiplier.
- The year-windowed Reddit collector (round-3) recovered 3-4× more pre-2020 posts than the original sort-only approach.

## Audit History
- 4 internal audit rounds, plus session-internal multi-agent audits in rounds 2, 4, and 5 (in-conversation, not externally independent).
- Round 1: 46 internal issues fixed.
- Round 2 (4-agent consensus): 5 CRITICAL fixes (filter divergence, wc<20 inconsistency, mislabeled Glass's delta, broken cross-correlation, Bonferroni inconsistency) + ~14 MAJOR. All resolved.
- Round 3: real moving-block bootstrap (replacing iid permutation), R/C ratio diagnostic in code, improved baseline (length-matched + topical-near).
- Round 4 (publication-readiness audit): length-residualised analysis added; ambiguity-aversion framing dropped (was unsupported); reframed as discourse-not-borrower study.
- Round 5 (this session): bootstrap per-event seed + B_actual tracking (was deflating p-values when zero-variance surrogates were skipped); OLS collinearity QR rank check (src_sdn ≡ prof_sdn_medical for SDN posts); sentiment_zeroshot.py auth fail-fast + circuit breaker (after a 715-call burn on auth errors); legislative_timeline_results.txt artifact for traceability; sample-size and R/C-ratio reconciliation; final_summary.py rewritten to canonical 8-event list.
- Path C (event-window Claude fill, ~$15.18, 3,035 posts): scored ALL Reddit + SDN posts in any of the 8 event windows at full corpus depth. Re-ran triangulation at n=4,787. Discovered the underpowered n=50/side eventstrat subsample had given false direction-concordance for Trump EO; with proper power, only Biden Mass Forgiveness and Biden v. Nebraska are triple-concordant. The substantive headline of the paper is meaningfully revised. Also fixed a per_event_tests bug that filtered to a single subsample (was missing the eventfull data even after Path C scoring landed).
- Round 6 / Copilot PR review (2026-05-08): 7 items addressed — UTF-8 stdout wrapper in `confound_audit.py` (mojibake fix); dynamic R/C multiplier in `gen_volume_artifact_figure.py` (was hardcoded 84×); `--stratify-events` help text correction; Trump event label standardisation; dropped misleading "Vectorized" docstring; dynamic subsample count in triangulation artifact; corrected `collect_allnurses` return type.
- Round 7 critical fixes complete (2026-05-08): bootstrap rewrite (block-permutation, Bickel et al. 1989, replacing wrong-null moving-block-with-replacement); K-α bootstrap CI (Hayes & Krippendorff 2007, B=2000); HC3 single-stage adjusted analysis (eliminates generated-regressor problem); Holm-Bonferroni step-down adjustment; per-event block-permutation in triangulation; window-sensitivity SD reporting; APA p-value reporting; Hedges' g J² variance correction; Claude test-retest at temperature=0 (closes LLM-noise reviewer objection: α=+0.958 [+0.938, +0.975] on n=605 SDN posts).
- Round 7 expansion (2026-05-08): added `pslf_intention_analysis.py` separating PSLF behavioral commitment (`pslf_stance`) from sentiment; added 3 new subreddits (PAstudent, prephysicianassistant, CRNA, +52 PSLF posts); attempted PA Forum (physicianassistantforum.com) scrape — Cloudflare-blocked (joins allnurses + Bogleheads on the unscrapable list).
- Round 7 (post-Path-C comprehensive audit, 2026-05-08): 3-agent parallel audit (statistical methodology + triangulation construct validity + literature context). Key outputs:
  - **Reframed headline**: project's primary contribution is now the construct-validity finding (TextBlob = lexical affect, VADER = expressive arousal, Claude-prompted = stance). The α=+0.17 is structural construct mismatch, not noise. Trump EO direction conflict is the lead exemplar, not an embarrassment.
  - **17 statistical-methodology issues identified**, 4 publication-blockers (bootstrap implements wrong null hypothesis; Hedges' g variance missing J² factor; α has no bootstrap CI; percentile-matched α biases upward and is reported without that caveat).
  - **Confound audit logic bug**: `confound_audit.py:99–102` only flags "CONFOUND DETECTED" when stratification *halves* the effect, but the SDN-vs-Reddit case actually shows stratification *grows* the gap (population was suppressing platform effect). Should be |stratified − naive|/|naive| > 0.5 in either direction.
  - **Stale comment in triangulation_results.txt:57** ("~50 pre + ~50 post per event") contradicts the actual n=166–610/109–437 after Path C. Code path is correct; only the frozen comment is stale.
  - **Stochastic Claude scoring**: `sentiment_zeroshot.py:93` does not set `temperature=0`. No test-retest α computed. Need to either re-score 200 posts at temperature=0 or compute test-retest α on a duplicate batch.
  - **Family-wise correction undercounted**: project runs ~72 hypothesis tests across pre/post + window-sensitivity + residualised + triangulation; α/8 = 0.00625 only controls one family. Should switch to Holm-Bonferroni or Benjamini-Hochberg with explicit family declarations.
  - **SAVE Forbearance window-sensitivity range** is +1.03 (30d) → +0.25 (180d), 4× span. Likely transient effect or regression to the mean. Not flagged in the artifact.
  - See `audit_round7_findings.md` (to be created) for full 17-issue list with file:line citations and venue-specific implications.

## Round 7 Critical Fixes (must-do before submission)

These are required before submitting to any methods-aware venue (JCSS / EPJ Data Science / Political Analysis / Behavior Research Methods). They are **substantive code work** and warrant their own PR cycle, not inline patches:

1. **Bootstrap implementation rewrite** (`gen_legislative_timeline.py:386–411`). Current code resamples the *combined* pre+post series in moving blocks and re-cuts at index n1. Replace with **stratified circular block bootstrap within each group** (Politis & Romano 1994) or **block-permutation test** (Bickel et al. 1989). Likely produces *larger* p-values than the current implementation.
2. **Hedges' g variance includes J² factor** (`gen_legislative_timeline.py:484`, `sentiment_triangulation.py:117`). Use Borenstein et al. (2009) eq. 4.24, not Hedges & Olkin (1985) eq. 6.13 (large-sample approximation that omits J²).
3. **Krippendorff's α bootstrap CI** (`sentiment_triangulation.py:208–306`). Add B=10,000 stratified bootstrap CI (Hayes & Krippendorff 2007). The `krippendorff` library does not compute these natively — needs explicit loop.
4. **Acknowledge percentile-matched α as charitable bound, not canonical** (`sentiment_triangulation.py:255–268`). Forcing equal-frequency quintiles aligns marginals between TB and VADER but not with Claude's true asymmetric distribution. Headline number should be the fixed-threshold α (=−0.03) with the percentile-matched α as a sensitivity bound, OR explicitly reframe as "ordinal α with native scorer thresholds gives α=−0.03; an upper-bound estimate that controls for marginal frequency mismatch is α=+0.17; both are well below the 0.667 reliability floor."
5. **Test-retest reliability for Claude** (`sentiment_zeroshot.py`). Re-score 200 posts at `temperature=0` (deterministic) and compute test-retest α. Current Claude scoring uses default temperature=1.0 → per-post output is sampled. Without test-retest, the Claude column has unknown ceiling reliability.
6. **Confound-audit conditional asymmetry bug** (`confound_audit.py:99–102`). Replace the one-sided test with |stratified − naive|/|naive| > 0.5.

## Round 7 Should-Fix (for quality)

7. Replace Bonferroni with Holm-Bonferroni (or BH with explicit family declarations).
8. Add HC3 robust SEs to OLS residualization, or cluster by thread/source/profession/month (generated-regressor problem; Pagan 1984).
9. Add per-event bootstrap to `sentiment_triangulation.py` (currently uses parametric Welch's t with the same autocorrelation issue as the main analysis).
10. Window-sensitivity SD report alongside g (4× span for SAVE Forbearance is currently unflagged).
11. Switch p-value reporting to APA conventions (`p<10⁻⁷` instead of `p=0.000000`).
12. Fix stale `~50 pre + ~50 post` comment in triangulation_results.txt:57.

## Round 7 Reframing for the Paper

The substantive contribution has changed. Drafting around this frame:

**Title (working):** *Stance, Affect, and Arousal: Sentiment Construct Mismatch in Policy-Discourse Text*

**Abstract framing (1 paragraph):** Three commonly-used sentiment instruments — TextBlob (lexicon polarity), VADER (Hutto & Gilbert 2014, social-media-tuned), and Claude Sonnet 4 zero-shot (LLM, prompted for stance toward a policy object) — are routinely treated as interchangeable in policy-discourse research. We demonstrate on a 9,629-post Public Service Loan Forgiveness corpus (Reddit + Student Doctor Network, 2010–2026) that they operationalize substantively different latent constructs: lexical affect, expressive arousal, and stance, respectively. Krippendorff's α=+0.17 (percentile-matched ordinal, n=4,787 with all three scorers) — well below the 0.667 floor for tentative reliability claims (Krippendorff 1980). The 2025 Trump PSLF Executive Order is the lead exemplar: directionally opposite Hedges' g across the three instruments on identical n=1,047 posts (TextBlob g=−0.39, VADER g=+0.21, Claude g=+0.41). The construct distinction is theoretically grounded in stance vs sentiment (Mohammad et al. 2016, SemEval-2016 Task 6) but has not been previously quantified at this scale on policy text. Implication: researchers using off-the-shelf sentiment tools must explicitly choose and defend the construct they are operationalizing; "sentiment" alone is no longer a publishable construct claim. We pair this finding with a quantification of Reddit's 1000-result API cap as a volume artifact (R/C ratio against CFPB Consumer Complaints as ground truth: ~6-7× real growth + ~10× recency-bias artifact 2017–2026).

**Recommended venues:**
- Tier 1 (target first): EPJ Data Science (SentiBench heir), Political Analysis (Heseltine & von Hohenberg 2024 precedent), Sociological Methods & Research (Chae & Davidson 2026 precedent).
- Tier 2: PNAS Nexus, Journal of Computational Social Science, PLOS One, Behavior Research Methods.
- Pre-print: arXiv cs.CL or cs.SI immediately.

**Cannot claim** (in this paper, with this design):
- "PSLF discourse responds to policy events" — substantive headline gone with Path C
- "Trump EO had a robust effect on PSLF sentiment" — direction is contested across 2/3 scorers
- "TextBlob/VADER/Claude are interchangeable" — refuted
- "Online discourse predicts borrower behavior" — no causal design, no representative sample

**Can claim**:
- Three commonly-used sentiment instruments operationalize substantially different constructs on policy discourse
- Construct mismatch is theoretically grounded (stance vs sentiment) and empirically demonstrated at α=+0.17, n=4,787
- Trump PSLF EO is a clean exemplar of the dissociation: TB g=−0.39, VA g=+0.21, CL g=+0.41 on identical n=1,047
- R/C volume artifact: Reddit's 1000-result API cap creates ~10× recency bias when measured against CFPB ground truth

## Round-8 status: what's complete vs pending (2026-05-09)

**Complete this round:**
- Arctic Shift Reddit historical pull (72,262 PSLF posts, 100% strict-filtered)
- VADER scoring on all Arctic Shift posts (free, ~5 min)
- R/C volume artifact diagnostic with proper longitudinal baseline (`gen_volume_artifact_arctic_shift.py`)
- 2,281-post stratified Claude scoring of Arctic Shift event-window cells (~$13)
- Sensitivity analysis excluding SDN-Medical (`sensitivity_excl_sdn_medical.py`) — α robust at n=6,111 non-SDN posts
- Placebo test against topical-near baseline (`placebo_test_topical_near.py`) — 10/16 ADEQUATE_NULL, 5/16 CONFOUNDED
- Per-event × per-profession analysis (`analyze_per_profession_per_event.py`) — cohort heterogeneity headline
- BERTopic full-corpus run (78,143 docs → 364 topics; 5+ servicer_issues sub-clusters surfaced; 5+ missed categories like trophies, FEIE, capitalization, REPAYE subsidy, portal bugs)
- Master timeline figures (`pslf_master_timeline.png`, `pslf_master_timeline_3scorer.png`)
- Event-time timecourse plots (`pslf_event_timecourses_*.png`)
- Claude dimensions multi-panel figure (`pslf_claude_dimensions.png`)
- Pre/post 3-dim heatmap by cohort (`pslf_claude_dimensions_by_event.png`)
- Reddit comments collector partial (~14K comments out of ~80-150K expected)

**Comments triangulation (round-8 partial):** TB×VADER α=+0.29 (95% CI [+0.274, +0.305]) on n=12,601 partial comments vs +0.34 on posts. Disagreement REPLICATES at 50× scale. Will tighten when comments collector finishes (~2-3h remaining as of 2026-05-09).

**Per-author longitudinal panel (Round-8 still infeasible):** Even with Arctic Shift expansion (~6.4× Reddit posts), only 1/8 events meets n>=10 returning-with-stance threshold (Trump EO went from n=12 → n=13 returning authors). Other events: 3-8 returning. The expanded corpus did NOT unlock per-author within-person inference for the substantive paper. **Composition-shift framing remains correct.** Comments collector may add ~5-10× more per-author observations and shift this judgment when it finishes.

**Still pending:**
- Comments collector for Arctic Shift posts (~50h wall-time at 2.5s/post for 70K new posts, ~$0 cost). Decide based on whether per-author panel becomes feasible after current data lands.
- Bogleheads + allnurses + physicianassistantforum.com (Cloudflare-blocked)
- Interrupted time series (ARIMA + control series) — required for causal claims
- OSF deposit + Transparency Statement section (writing task; replaces "pre-registration retrofit" as I previously misnamed it)
- Cross-domain replication of methods finding (COVID-vaccine, climate) — would unlock PNAS Nexus / Political Analysis venue tier

## Publication Status (round-4 audit verdict)
- **Pre-print (arXiv cs.SI / SSRN)**: ready now
- **PLOS One**: ~1–2 weeks of writing. Path C revealed that *no* event is simultaneously bootstrap-Bonferroni-significant AND triple-concordant. The paper must lead with the methodological co-headline (α=+0.17 across three commonly-used sentiment instruments on the same n=4,787 PSLF corpus) and treat the per-event findings as a *case study of instrument disagreement*, not as substantive policy-effect estimates. Trump PSLF EO is now an exemplar of direction-conflict (TB g=−0.39 vs VA g=+0.21 vs CL g=+0.41 on the same n=1,047 posts), not a robust effect.
- **Methods journal** (JCSS / EPJ Data Science): ~1 month of revisions (R/C diagnostic could be standalone methods note)
- **Policy journal**: not without substantial reframing as discourse analysis with topic modeling
