# NSLDS PSLF Data — DUA Application Instructions

**Last updated:** 2026-05-10
**Purpose:** Step-by-step instructions for applying for restricted-use NSLDS
(National Student Loan Data System) PSLF certification and approval data via
the Department of Education's data-request process.

---

## Why this data matters

NSLDS is the federal student loan administrative database. For PSLF research,
the key restricted-use elements are:

1. **PSLF certification submission counts** by employer (EIN) and year
2. **PSLF certification approval/denial rates** by employer
3. **PSLF forgiveness completions** by employer, year, specialty
4. **Cumulative qualifying payment counts** by borrower
5. **Borrower-level loan amount + IDR plan choice + employment dates**

**This is the SINGLE most important external dataset for the substantive paper.**
Without it, we cannot:
- Definitively distinguish PSLF-mechanism effect from quality-confound (P8/P11
  audit cycle)
- Validate forum discourse signals against actual borrower behavior
- Estimate dollar-value of PSLF reform per employer type
- Test whether HCA-residents-with-academic-affiliates actually file PSLF
  certifications (per the L1 question)

With NSLDS data, the substantive paper would shift from observational to
quasi-experimental. Without it, the paper is observational with caveats.

---

## Eligibility for NSLDS access

DOE allows researcher access via:
1. **NCES Restricted-Use License** (preferred for academic researchers)
2. **HRSA / DOE Data Sharing Agreement** (if affiliated with a federal agency)
3. **GAO contract** (if working on a Congressional audit)
4. **Direct DOE contracted research** (rare; usually agency-initiated)

**For independent academic researchers:** The NCES Restricted-Use License
is the standard path.

---

## Step-by-step application process (NCES Restricted-Use License path)

### Step 1: Verify your institutional eligibility (1 week)

**Requirements:**
- Affiliated with a U.S. accredited institution of higher education OR a
  recognized research organization (501(c)(3))
- Applicant has a Ph.D., M.D., or equivalent terminal degree (or is a faculty
  member working with a doctoral-trained researcher as Senior Project Officer)
- Institution can sign the formal license agreement
- IRB approval for the proposed research (or formal Exempt determination)

**Documentation to collect:**
- Letter from your institution's IRB confirming approval/exemption
- Senior Project Officer's CV
- Institutional Research Integrity Office point of contact

### Step 2: Submit IRB application (4-8 weeks)

The IRB application should include:
- Research questions (specific to PSLF — example below)
- Data security plan (which NCES requires for the license)
- Data destruction plan
- Personnel list (only those with NCES-cleared computers can access data)
- Publications plan

**Sample research questions to include in IRB:**
1. Do PSLF certification rates differ between for-profit and 501(c)(3)
   employers within the same residency-program type?
2. Does the +12.86pp NRMP fill-rate gap (Round 11 finding) correspond to a
   parallel gap in PSLF certification rates by employer?
3. Do PSLF-eligible-employer borrowers complete forgiveness at higher rates
   than projected based on debt levels and IDR plan choices?

### Step 3: Submit NCES license application (Form 6 weeks)

**Apply via:** https://nces.ed.gov/statprog/instruct.asp
**Specific application form:** "Restricted-Use Data Procedures Manual" (CRDC-NCES)

**Application checklist:**
- [ ] Project Officer information (Ph.D. or equivalent)
- [ ] Senior Project Officer (institutional commitment)
- [ ] Institution Designee (signs license)
- [ ] Statement of research purpose
- [ ] Specific NCES datasets requested (list NSLDS-PSLF specific tables)
- [ ] Data security plan (encryption, computer access, transit security)
- [ ] List of all personnel with data access
- [ ] IRB approval letter
- [ ] Affidavit of nondisclosure for each personnel

### Step 4: NCES technical review (4-8 weeks)

NCES reviews applications case-by-case. They may:
- Request modifications to research design
- Require additional data security measures
- Approve, conditionally approve, or deny

If approved, NCES issues a license with specific restrictions:
- Data must be stored on a specific computer (cannot be on shared servers)
- All output reviewed by NCES before publication
- Specific requirement: cell sizes < 30 must be suppressed
- Data destruction date specified

### Step 5: Data delivery + analysis (ongoing)

- NCES sends data on encrypted physical media
- Data must be loaded onto designated secure computer
- All analysis happens in this secure environment
- Output (tables, regression results) submitted to NCES for review before
  publication

**NCES review of output:** Takes 2-6 weeks per submission.

### Step 6: Publication

- Each manuscript citing NSLDS data must include the standard NCES citation
- Tables/figures with cell sizes < 30 must be suppressed (replaced with "*")
- NCES staff must be co-authors or acknowledged

---

## Estimated total timeline

| Phase | Time |
|---|---|
| IRB approval | 4-8 weeks |
| NCES application | 6-12 weeks |
| NCES review | 4-8 weeks |
| Data setup | 2-4 weeks |
| **Total to data access** | **~16-32 weeks** |

**Conservative estimate:** 6-12 months from application to data access.

---

## Cost

| Item | Estimated cost |
|---|---|
| NCES license fee | $0 (free for academic) |
| IRB fee | $0-$500 (institution-dependent) |
| Secure computer setup | $500-$2,000 (encrypted, network-isolated) |
| Personnel time | Variable |

**Total cost: ~$0-$2,500** for the formal application process. Personnel time
is the major investment.

---

## Specific NSLDS data elements to request

For PSLF substantive paper:
- **PSLF Employment Certification Forms (ECF)** by year, employer EIN, employer
  name, borrower employment dates
- **PSLF Approved Forgiveness Records** by year, employer EIN, borrower
- **Borrower demographic** (age, race, geographic state, MD/DO/PhD designation)
- **Loan history**: origination, balances, IDR plan choice, payment counts
- **Borrower-level PSLF certification status**: not-applied, approved, denied,
  pending
- **Federal employer identifiers** for cross-referencing with NRMP institutions

For methods paper:
- Subset of above sufficient to validate sentiment-derived patterns against
  admin reality

---

## What this would unlock for the substantive paper

**With NSLDS approved:**
1. Convert B5 finding from "+12.86pp NRMP fill-rate gap" to "+X% PSLF
   certification gap" — direct admin-data evidence
2. Resolve the P8/P11 audit cycle definitively (PSLF mechanism vs quality
   confound)
3. Validate forum discourse signals (P3, P10) against actual borrower behavior
4. Test "discourse predicts behavior" hypothesis with cleanly-linked data
5. Estimate dollar-value of PSLF reform on physician workforce composition
6. Distinguish HCA-academic-consortium (residents employed by HCA, NOT
   PSLF-eligible per L1) from true academic medical centers

**Tier-1 publishable claim with NSLDS data:**
> "Direct administrative data from NSLDS show that PSLF certifications
> by primary-care residents at PSLF-eligible employers exceed those at
> PSLF-ineligible employers by [X%] (p<...), confirming the workforce
> composition effect documented in NRMP fill-rate analysis."

---

## Alternative: GAO partnership for faster access

If a Congressional audit on PSLF were occurring, working with GAO could provide
faster access to NSLDS data. GAO has standing data-sharing agreements with DOE.

**To explore:** Contact GAO researchers studying PSLF (multiple GAO reports
exist — 2018, 2019, 2024). Faster path if your research aligns with their
audit questions.

---

## Recommended action

**Start the application process NOW.** The 6-12 month timeline means even if
the substantive paper is submitted with observational evidence first, NSLDS
data could be incorporated into:
- Revisions during peer review
- A v2/follow-up paper
- A definitive policy brief

**Action items:**
1. Contact your institution's IRB office this week
2. Identify a Senior Project Officer (Ph.D./M.D. faculty)
3. Draft the IRB application using the research questions above
4. Begin drafting the NCES license application in parallel
5. Set a data destruction date that allows for 18-24 months of analysis

---

## Files referenced

- `POLICY_BRIEF_v3_FINAL.md` — describes findings that would benefit from NSLDS
- `AUDIT_round11_P8_CMS_correction.md` — P8 audit (now superseded by P11)
- `AUDIT_round12_P11_REVERSAL.md` — P11 reversal of P8

---

## Contact information

- **NCES restricted-use:** RUDDS@ed.gov
- **NCES website:** https://nces.ed.gov/statprog/instruct.asp
- **DOE PSLF program:** https://studentaid.gov/manage-loans/forgiveness-cancellation/public-service
- **PSLF Help Tool API (does not provide research access):**
  https://studentaid.gov/help-center/answers/article/can-i-access-pslf-help-tool-api
