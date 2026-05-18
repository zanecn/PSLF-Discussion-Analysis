# Discussion-Section Draft Drafts (H + I from Round-9 plan)

These are pre-writing drafts for the substantive paper's Discussion section. Build out from these as needed during paper drafting.

---

## H. Mechanism discussion: Why do cohorts respond differently to PSLF events?

**Four candidate mechanisms, ranked by evidentiary support from this dataset.**

### Mechanism 1 (most defensible): **Career-stake binding**

**Claim**: SDN-Medical posters disproportionately have *time-bounded employer-eligibility constraints* — most are residents (PGY-1 through PGY-7) or attendings within their first 5–10 years of practice. For these posters, the 10-year PSLF clock is a binding constraint during their highest-earning training years. Any policy event that affects clock continuity (forbearance pauses, payment-counting rule changes, employer-qualification rules) materially affects whether they will reach forgiveness on schedule.

The Reddit r/PSLF community, by contrast, draws from the broader PSLF-eligible borrower pool — older borrowers, government employees, nonprofit-sector workers — for whom the clock may be 8 of 10 years complete already, or for whom alternative repayment paths (IDR forgiveness, refinancing) are realistic alternatives.

**Evidence supporting this mechanism in the data**:

1. **SAVE Admin Forbearance × SDN g=+1.69 vs r/PSLF g=+0.01 NS** — administrative protection of the PSLF clock is read by SDN as "good news, my clock continues" but as net-neutral by the broader r/PSLF audience. (n=97/23 for SDN cell — fragile but consistent with mechanism.)

2. **Payments Restart × SDN g=+0.59 vs r/PSLF g=−0.12** — restart of payment obligations is "relief, my clock resumes" for SDN trainees but "stress, more payments" for general borrowers. Both are Bonferroni-significant.

3. **Trump PSLF EO × SDN g=−0.45 vs r/PSLF g=−0.14** — direct threat to clock-validity hits SDN ~3× harder than general r/PSLF. Same direction; magnitude scales with stake.

4. **Time-to-recovery: SDN-Medical median 29 days vs r/PSLF 2 days** — SDN's policy-event sentiment shocks persist ~14× longer, consistent with sustained attention to clock-affecting events.

5. **Topic restructuring**: SDN's post-event topic shifts cluster on `career_impact` (peak +97pp on SAVE Forbearance) and `financial_planning` (+62pp on IDR Adjustment) — the topics most relevant to within-residency career planning. r/PSLF's post-event topics shift toward `financial_planning` (+11pp on Biden v. Nebraska) and `general_question` — the topics relevant to general policy navigation.

**Counter-evidence / scope limits**:

- We cannot validate this directly because we lack survey-linked posters (don't know each poster's PGY, employer, or clock-progress)
- Reddit Medical (r/medicalschool, r/Residency) shows MUCH SMALLER per-event effects than SDN-Medical despite similar nominal demographics. Suggests platform-level selection (people who post in SDN about PSLF are *more committed* PSLF discussants than people who post in r/medicalschool about PSLF) is also operating
- Career-stake binding doesn't explain the direction-REVERSAL of sentiment-stance decoupling (r/PSLF OR=7.33 vs SDN OR=0.27); that's better explained by Mechanism 3 (forum norm) below

### Mechanism 2 (likely operating in addition): **Selection effect on platform**

**Claim**: People who post on SDN about PSLF are a more committed, more deliberative subset of medical trainees than those who happen to mention PSLF on r/medicalschool. SDN is a vocational forum where PSLF discussion is purposeful (career strategy) rather than incidental.

**Evidence**:
- SDN cumulative rejecting rate is 24%, vs Reddit Medical (r/medicalschool) at 7%. Either SDN attracts more rejecters, or its committed users discuss rejection more openly. Both plausible.
- The within-SDN sub-thread consistency check showed SDN's distinctive responses hold across "financial", "residency", "medical_school", and "other" thread types — so it's not driven by specific SDN sub-communities
- This selection-effect story doesn't conflict with career-stake binding — they likely co-occur

### Mechanism 3 (explains direction-REVERSAL): **Forum norm — venting culture vs analytical culture**

**Claim**: Different online communities have different *normative interpretations* of negative sentiment. In help-forums (r/PSLF), expressing negative affect about a policy is a social signal of frustration WITH the program's friction (servicer issues, processing delays, paperwork burden) while *staying in*. In analytical-finance forums (Reddit Finance, SDN-Medical with its strong career-strategy frame), negative affect is more closely tied to *exit reasoning* — articulating WHY one is leaving the program.

**Evidence**:
- Sentiment-stance OR in r/PSLF = 7.33 (negative posters MORE likely to be pursuing)
- Sentiment-stance OR in SDN-Medical = 0.27 (negative posters LESS likely to be pursuing)
- Sentiment-stance OR in Reddit Finance = 0.18 (strongest analytical decoupling)
- Cohort-invariant OP vs Reply pattern: in ALL 8 cohorts, OPs have higher VADER arousal (high emotional affect) than replies. Replies are more measured / supportive. This is the help-forum norm operating universally.
- The forum-norm interpretation is consistent with literature on help-seeking communities (Pariser & DeChoudhury 2017, CSCW; Andalibi et al. 2017)

### Mechanism 4 (weakest evidence): **Information asymmetry**

**Claim**: SDN posters have access to better PSLF information (program officers at academic medical centers, peer networks of residents who have completed PSLF, attending-level mentors who have done the paperwork) than general r/PSLF posters. Their negative sentiment may carry more accurate signal because their priors are better-calibrated.

**Evidence**: Limited direct evidence. Could be tested with content analysis of post sophistication (e.g., references to specific forms, regulations, court cases) but not done in this analysis.

---

## I. Generalizable prediction: Vocational vs general-public forums in other policy domains

The cohort heterogeneity finding has a falsifiable structural prediction: **in any policy domain where vocational/specialist forums and general-public forums coexist, the vocational forums will show systematically larger and often opposite-direction reactions to policy events that affect their specific stakes**.

### Three test cases the field could examine

#### Case 1: Teacher loan forgiveness (Teacher Loan Forgiveness program + Title I changes)

**Predicted pattern**:
- Vocational forum: r/Teachers, r/professors, NEA forums, AFT forums
- General forum: r/StudentLoans, r/personalfinance
- **Prediction**: vocational teacher forums will show larger sentiment shifts on TLF amount changes (currently $5K-17.5K) than general forums. Directional opposition possible: teachers in low-income schools (TLF-eligible) reacting positively to expansion; private-school teachers (ineligible) negative.
- **Stake-binding test**: teachers within their 5-year TLF service requirement should show stronger reactions than tenured teachers past the eligibility window.

#### Case 2: Military GI Bill / VA education benefits

**Predicted pattern**:
- Vocational forum: r/army, r/Marines, r/Veterans, military-specific subreddits
- General forum: r/StudentLoans, r/personalfinance, r/college
- **Prediction**: military forums show larger reactions to GI Bill rule changes than general forums. Directional opposition possible on programs that shift eligibility (Post-9/11 GI Bill changes affecting transfer-of-benefits to family members).
- **Stake-binding test**: active-duty service members within their transfer-eligibility window should show stronger reactions than veterans whose benefits are vested.

#### Case 3: ACA professional eligibility (insurance-broker certification, ACA navigator changes)

**Predicted pattern**:
- Vocational forum: insurance-industry forums (NAIFA, IAIP), broker-specific subreddits
- General forum: r/healthinsurance, r/personalfinance
- **Prediction**: broker forums show larger reactions to commission-rule changes than general health-insurance discussion. Cross-sectional opposition possible: brokers reacting negatively to rule changes that protect consumers but reduce broker income.

### What would falsify this prediction?

- If vocational forums consistently react WITH SAME magnitude as general forums → cohort-invariance, no specific stake-binding mechanism
- If vocational forums react OPPOSITE direction to all events (always positive or always negative regardless of stake direction) → ideological framing, not stake-binding
- If the cohort-heterogeneity holds for PSLF but NOT for any of the three test domains → PSLF-specific finding, not generalizable

### What this predicts about research methodology

Pooled "online reaction" analyses are misleading whenever a policy domain has both vocational and general-public forums in scope. The standard practice of treating "online sentiment" as a single signal is wrong; cohort stratification by community type should be standard.

For computational social science: include forum-type as a primary covariate in any policy-discourse analysis. Report per-cohort effects alongside pooled effects. If they disagree directionally, the pooled mean is misleading.

For health/education policy researchers: be explicit about which community types are in scope when characterizing "online reaction." A study based primarily on r/Teachers will tell a different story than one based primarily on r/StudentLoans, even on the same teacher-loan-forgiveness policy event.

---

## Bottom-line interpretation for the substantive paper

PSLF online discourse is structurally heterogeneous across community types, and the heterogeneity is interpretable through a **career-stake-binding mechanism** (vocational communities with time-bounded eligibility constraints react more strongly and persistently to clock-affecting events) **moderated by community-norm differences** (help-forum venting culture vs analytical-forum exit-reasoning culture).

This generalizes to a falsifiable prediction about vocational vs general-public reactions in other professional-eligibility policy domains. The current paper documents the pattern for PSLF; future research can test the prediction for teacher loan forgiveness, GI Bill, ACA broker rules, and similar professional-policy domains.

The methodological implication is immediate: **policy-discourse research that pools across community types loses cohort-conditional information that may flip direction across reasonable subsets.** Cohort stratification should be standard practice.
