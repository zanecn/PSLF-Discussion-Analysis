# Master Drafting Kit — Reusable Text Blocks

**Purpose:** Pre-written prose blocks that appear in multiple papers. Drop into the paper drafts verbatim and edit only as needed for venue voice.

---

## Block A — PSLF program context (1 paragraph; for any paper Methods or Background)

**Text (~110 words):**

The Public Service Loan Forgiveness (PSLF) program, established by the College Cost Reduction and Access Act of 2007, forgives remaining federal student loan balances for borrowers who make 120 qualifying monthly payments while employed full-time by qualifying public-service employers (US federal, state, or local government, or 501(c)(3) tax-exempt nonprofits, including most university hospitals and most private nonprofit hospitals). For physicians — who graduate medical school with a median federal loan balance of approximately $200,000–$250,000 (AAMC 2024) — PSLF eligibility translates to potential forgiveness of $150,000–$300,000 in loan principal plus interest after a 10-year qualifying employment trajectory. The program is administered by the US Department of Education with loan servicing performed by contracted servicers (currently MOHELA).

**Citations:** AAMC (2024); College Cost Reduction and Access Act (2007); US Department of Education (2024).

**Used in:** P1 §3.2, P2 §3.2, P3 §1.1.

---

## Block B — PSLF policy events 2021-2025 (1 paragraph + bullet list)

**Text (~150 words):**

We identify eight major PSLF-related federal policy events spanning 2021–2025: (1) the Limited PSLF Waiver (October 2021), which retroactively counted previously-disqualified payments toward forgiveness; (2) the IDR Account Adjustment (April 2022), expanding income-driven repayment recognition; (3) the Biden Mass Forgiveness Plan announcement (August 2022); (4) the Supreme Court's Biden v. Nebraska ruling (June 2023) striking down the mass forgiveness plan; (5) the resumption of payment requirements (October 2023) after the COVID-19 pause; (6) the SAVE Plan administrative forbearance (August 2024) following the 8th Circuit injunction; (7) the Trump PSLF Executive Order (March 2025) restricting PSLF eligibility for "illegal-purpose" employers; and (8) the Final Trump PSLF Rule (October 2025) implementing the EO. We use 60-day pre-event and 60-day post-event windows around each event date for analyses requiring temporal comparison.

**Used in:** P1 §3.2 (brief), P2 §1.4, P3 §1.4 (event #7 + #8 only for Paper 3 contextual mention).

---

## Block C — Discourse-vs-borrower scope clarification (essential limitation)

**Text (~85 words):**

This study analyzes online PSLF discourse on Reddit and Student Doctor Network. The user populations of these platforms skew young, white, male, and more educated than the broader ~1M-person PSLF-borrower population (per AAMC and Pew demographic surveys, 2024). Key forums for some PSLF-relevant audiences — Bogleheads.org, allnurses.com, and physicianassistantforum.com — are blocked by Cloudflare and could not be scraped. Findings should be interpreted as **discourse construct measurement on these specific online communities**, not as direct measurement of borrower attitudes or behavior across the PSLF-borrower population.

**Used in:** P1 §7 limitation 1, P2 §7 limitation 1, P3 (NOT used; P3 is program-level, not discourse).

---

## Block D — Three sentiment instruments (Methods boilerplate)

**Text (~150 words):**

We score each post on three sentiment instruments: (i) **TextBlob 0.18.0+** lexical polarity, a Naive Bayes scorer using the Pattern.en lexicon (~2,900 hand-coded adjectives), producing a continuous score in [−1, +1]; (ii) **VADER 3.3.2+** compound score (Hutto & Gilbert 2014), a rule-based scorer tuned on social-media text using a 7,500-word lexicon plus rules for negation, intensifiers, punctuation, and capitalization, producing a continuous score in [−1, +1]; and (iii) **Claude Sonnet 4** (claude-sonnet-4-20250514) at temperature=0 via the Anthropic API, prompted to classify each post on a 5-level ordinal sentiment scale (very_negative / negative / neutral / positive / very_positive) along with primary topic and PSLF stance. Continuous polarities are binned into 5 ordinal levels using either fixed thresholds {−0.5, −0.05, +0.05, +0.5} (canonical, VADER convention) or quintile rank (qcut, charitable upper bound that controls for marginal-frequency mismatch). We report results under both binnings.

**Citations:** Hutto & Gilbert (2014); Loria (2018); De Smedt & Daelemans (2012).

**Used in:** P1 §3, P2 §3.4 (cite Paper 1 instead of duplicating).

---

## Block E — Three LLMs (Paper 1 Methods only)

**Text (~110 words):**

We score the same posts with three LLMs from three independent organizations: **Claude Sonnet 4** (Anthropic, USA, post-trained via Constitutional AI / RLAIF, proprietary dense architecture); **Llama 3.3 70B Instruct Turbo** (Meta, USA, post-trained via RLHF + DPO, Llama-3 dense architecture with GQA, RoPE, SiLU); and **DeepSeek V3.1** (DeepSeek, China, post-trained via GRPO, MoE 671B parameters with 37B active). All three are queried at temperature=0. We acknowledge in §6 that training corpora for all three are undisclosed proprietary mixes that likely overlap on common web sources (Common Crawl, Wikipedia, GitHub, books); the cross-organization and cross-country diversity provides a partial — not complete — refutation of "shared training data" as the explanation for inter-LLM agreement.

**Used in:** P1 §3.2.

---

## Block F — Krippendorff α with bootstrap CI (Methods)

**Text (~95 words):**

Inter-rater reliability is computed as Krippendorff's α (ordinal level of measurement; Hayes & Krippendorff 2007) using the `krippendorff` Python package (Castro 2020). 95% confidence intervals are computed via stratified bootstrap (B=2,000 resamples, stratified by source/cohort), as the package does not provide native CIs. We interpret α point estimates against Krippendorff's (1980, 2018) standard reliability floors: α ≥ 0.667 = "tentative reliability" only; α ≥ 0.800 = "satisfactory reliability." We report Cohen's κ pairwise alongside Krippendorff α, interpreted against Landis & Koch (1977) thresholds (≤0.20 slight; 0.21–0.40 fair; 0.41–0.60 moderate; 0.61–0.80 substantial; 0.81–1.00 almost perfect).

**Citations:** Hayes & Krippendorff (2007); Krippendorff (2018); Castro (2020); Landis & Koch (1977).

**Used in:** P1 §3.3, §4.2.

---

## Block G — PSLF-relevance filter (Methods)

**Text (~75 words):**

PSLF-relevant posts are identified using an anchored regular-expression filter (`filter_pslf_relevant` in `pslf_search_terms.py`, 17 unit tests pass). The rule: generic loan-forgiveness terms (e.g., "loan forgiveness," "debt forgiveness") must co-occur with a PSLF-specific anchor (PSLF, MOHELA, FedLoan, qualifying employer, IBR/ICR/REPAYE, etc.) within 80 characters in the same post. Posts shorter than 20 words after PSLF filtering are excluded (TextBlob is unreliable on short posts; threshold applied uniformly across instruments to prevent length-effect confounds).

**Used in:** P1 §3.3, P2 §3.3.

---

## Block H — Cohort definitions (5 communities; for Paper 2 Methods)

**Text (~90 words):**

We define five PSLF-discussing communities for cohort-stratified analysis: (1) **Reddit r/PSLF** (n=1,469 with Claude scoring), the dedicated PSLF subreddit; (2) **Student Doctor Network Medical** (n=1,960), the dominant physician/medical-trainee online forum (studentdoctor.net); (3) **Reddit Finance** (n=999), pooling r/personalfinance and r/financialindependence; (4) **Reddit r/StudentLoans** (n=969), the general student-loan subreddit; and (5) **Reddit Medical** (n=566), pooling r/medicalschool, r/medicine, and r/Residency. Cohorts were chosen for: (a) ≥400 posts with all three sentiment instruments AND Claude stance scoring; (b) discrete community boundaries (separate subreddits or platforms); (c) coverage of the major PSLF-discussant demographics.

**Used in:** P2 §3.2.

---

## Block I — Honest reliability framing (replaces "substantial agreement")

**Text (~100 words):**

We characterize the inter-rater reliability of our three LLMs against Krippendorff's standard floors. Three-LLM α=+0.7590 [bootstrap 95% CI +0.7241, +0.7868] on the combined Reddit + SDN sample (n=1,001) places the LLM-class instruments above the 0.667 tentative-reliability floor; the SDN-only sub-sample (n=300) achieves α=+0.8306 [+0.7870, +0.8661], exceeding the 0.80 satisfactory-reliability floor. The Reddit-only sub-sample (n=701) sits at the boundary of tentative reliability (α=+0.6901, lower CI bound +0.65). Pairwise Cohen's κ values among the three LLMs (+0.57 to +0.59) are "moderate" by Landis & Koch (1977), not "substantial." We adopt this strict terminology throughout.

**Used in:** P1 §5.2, P1 conclusion, P2 §3.4 (citing Paper 1).

---

## Block J — Construct-misalignment framing (replaces CMV)

**Text (~120 words):**

When sentiment and stance are scored by the same LLM from identical text, the resulting bivariate analysis is subject to **construct-misalignment + sample-selection bias** rather than Common Method Variance in the Podsakoff (2003) sense. Podsakoff CMV requires that two measures of the SAME units share method variance that inflates their bivariate correlation. In our design, TextBlob/VADER and Claude do not score the SAME posts as "negative" — TB and VADER pick up lexical-affect negativity (e.g., venting about MOHELA), while Claude picks up stance-relevant policy-dissatisfaction (e.g., exit-decided posters). The two operationalizations identify partially-disjoint subsamples, and the OR computed on different subsamples can differ in magnitude and direction. The Reddit Finance cohort (Section 5.3) is the cleanest empirical demonstration of this in our dataset.

**Citations:** Bestvater & Monroe (2023); arXiv:2410.14626 (2024).

**Used in:** P2 §1.2, §2.3, §5.3.

---

## Block K — Wild-cluster bootstrap framing (Paper 3)

**Text (~95 words):**

Cluster-robust standard errors clustered on institution are reported as our primary inferential framework. Because the number of hostile clusters is small (n=23 in S1; n=9 in S2/S3), Cameron & Miller (2015) recommend confirmation via wild-cluster bootstrap. We apply the Webb (2014) 6-point wild-cluster bootstrap with B=2,000 iterations to compute small-sample-adjusted p-values for the PSLF-hostile coefficient. The asymptotic cluster-robust p-values overstate precision substantially in S2 and S3 (where only 9 hostile clusters identify the coefficient); we report wild-cluster p-values as the defensible inferences. All three specifications survive at α=0.05 after wild-cluster correction.

**Citations:** Cameron, Gelbach & Miller (2008); Cameron & Miller (2015); Webb (2014).

**Used in:** P3 §2.5.

---

## Block L — Standard limitations boilerplate (for any paper)

**Text (~150 words):**

This study has the following limitations: (1) **Discourse demographics**: online forum users (Reddit + SDN) are not representative of the ~1M PSLF-borrower population; findings concern discourse construct measurement on specific online communities, not direct borrower attitudes. (2) **Cloudflare-blocked sources**: Bogleheads.org, allnurses.com, and physicianassistantforum.com are blocked from scraping; the financially-sophisticated planner cohort, the dominant nursing community, and the PA-specific forum are missing. (3) **Single-domain**: PSLF-specific corpus; cross-domain generalizability (e.g., COVID-19 vaccine discourse, climate policy) is pre-registered but not yet completed. (4) **Observational design**: no exogenous variation in policy events or PSLF eligibility; causal claims about policy effects are not made. (5) **Cohort-conditional findings**: where applicable, findings stratify by community; some patterns observed in one community may not generalize to others. (6) **Single-period scoring**: no longitudinal LLM re-scoring across model versions; results may differ if scoring is replicated with future LLM versions.

**Used in:** P1 §7, P2 §7, P3 §4.4 (modified for program-level scope).

---

## Block M — Standard methods software footer

**Text:**

All analyses were conducted in Python 3.11 with pandas 2.x, scipy.stats 1.x, statsmodels 0.14+, and sklearn.metrics. Krippendorff α was computed with the `krippendorff` Python package (Castro 2020). Figures were produced with matplotlib 3.x. Claude scoring used the Anthropic API (claude-sonnet-4-20250514) at temperature=0. Llama 3.3 70B Instruct Turbo and DeepSeek V3.1 scoring used the Together AI API at temperature=0. All code, data, and analysis-ready intermediate datasets are deposited at OSF (DOI: TBD; CC-BY 4.0).

**Used in:** P1 §3 footer, P2 §3 footer, P3 §2.6 footer.

---

## Block N — Standard "what we cannot claim" disclaimer

**Text (~70 words):**

This study makes the following limitations explicit: we do NOT claim that (a) any sentiment instrument is "correct" — different instruments measure different constructs; (b) policy events causally shift borrower attitudes — we observe associations only; (c) the patterns documented here generalize to PSLF-borrowers outside the studied online communities; (d) our findings predict individual borrower decisions or future PSLF program enrollment. The patterns are descriptive of community-level discourse, with explicit construct-validity caveats per Paper 1.

**Used in:** Conclusion sections of all three papers.

---

## Block O — OSF + reproducibility

**Text (~50 words):**

All analyses are fully reproducible. Code, data, and intermediate analytical outputs are deposited at OSF (DOI: TBD), licensed CC-BY 4.0. The analytical pipelines for sentiment scoring, multi-LLM convergence, base-rate-adjusted decoupling, per-event topic restructuring, per-author panel feasibility, NRMP confounder construction, and cluster-robust regression with wild-cluster bootstrap are all available as Python scripts.

**Used in:** Methods footers + supplements of all three papers.

---

## How to use this kit

1. Copy the relevant block into the appropriate paper section
2. Edit lightly to match the paper's voice (e.g., "We" → "The authors" for some venues)
3. Update placeholders (TBD, [N], etc.) with current values from `MASTER_LOCKED_NUMBERS.md`
4. Cite from `MASTER_REFERENCE_LIST.md` (don't re-derive citations)

This eliminates ~40% of the prose-writing work for each paper.
