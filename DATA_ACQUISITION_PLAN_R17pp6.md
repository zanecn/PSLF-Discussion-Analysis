# Data Acquisition Plan (R17++ #6)

**Created:** 2026-05-17 (R17++ #6 — boost strategy implementation)
**Purpose:** identify all additional data needs for the 6-paper boost strategy + flag feasibility/cost/timing for each acquisition; establish critical path

---

## Summary: data needs by paper

| Paper | Boost strategy | New data needed | Source | Cost | Time | Feasibility |
|---|---|---|---|---|---|---|
| **P1 (OP-vs-Reply reframe)** | Reframe headline; minimal new data | ~~none required~~ thread-structure metadata (optional) | already in Reddit Arctic Shift JSON | $0 | 1-2 days | TIER 1 (immediate) |
| **P2 (Reddit Finance strip)** | Strip to single finding; no new data | ~~none required~~ | n/a | $0 | 0 days | TIER 1 (immediate) |
| **P3 (workforce downstream)** | Where do residents practice after training? | CMS NPPES + AAMC GraduateMedicalEd OR AMA Masterfile | CMS NPPES free / AMA $$$$ | $0 (NPPES) - $5K (AMA) | 1-3 weeks | TIER 2 (NPPES) / TIER 4 (AMA) |
| **P4 (comprehensive reframe)** | Broaden to multi-source residency dataset | ACGME multi-year, NIH RePORTER multi-year, VA designation | ACGME public reports / NIH RePORTER public / VA facility directory | $0 | 1-2 weeks | TIER 1 (all free) |
| **P5 (geographic analysis)** | Add HPSA/RUCA/state-policy context to surgical-subspecialty PSLF | HRSA HPSA + USDA RUCA + state Medicaid expansion status | HRSA public + USDA public + KFF tracker | $0 | 3-5 days | TIER 1 (all free) |
| **P6 (multi-policy comparison)** | Add non-PSLF student-loan policy events | Event dates + Reddit data spanning events (mostly already collected) | News archives + already-collected Reddit | $0 | 1-2 weeks | TIER 1 (immediate) |
| **P7 (PGY-1 NSLDS follow-up)** | NSLDS DUA-enabled borrower-level analysis | Borrower-level federal loan records | DOE NSLDS via DUA | $0-500 fees | 6-12 month review | TIER 3 (long-horizon) |

**Feasibility tiers:**
- **TIER 1**: free, public data, immediately accessible
- **TIER 2**: free public data but significant data-engineering work
- **TIER 3**: requires DUA / IRB / institutional process; 6+ month timeline
- **TIER 4**: requires commercial license or institutional purchase

---

## Per-paper data acquisition detail

### P1 — OP-vs-Reply reframe (TIER 1; ~1-2 days)

**Current data state:** OP-vs-Reply directional finding is locked at the 519K-comment scale (TextBlob Δ=−0.0146 [−0.0164, −0.0127], VADER Δ=+0.2387 [+0.2306, +0.2460] in 8/8 cohorts; magnitude split 16.4×; n=21,453 OPs with both polarity and ≥1 comment). The cluster-bootstrap CIs were re-run in R17++ #6 RIGOROUS REVIEW (with aligned 4-source loader to match t-test sample exactly); prior R17++ #2 CIs used a different n=14,153 subset and have been superseded.

**Optional supplements to strengthen for ICWSM/CSCW '26:**

1. **Thread-structure metadata** — Reddit Arctic Shift JSON already contains `parent_id` for every comment. Currently we analyze OP-vs-Reply (depth 0 vs depth 1+). Could extend to:
   - Depth 1 vs depth 2 vs depth 3+ sentiment trajectories
   - Within-thread sentiment evolution
   - Conversation graph topology (chains vs trees)
   - **Effort: 1-2 days of analysis on already-collected data**
   - **Cost: $0**

2. **SDN comment-level data** for cross-platform replication of the directional finding
   - Currently P1 uses SDN post-level only (n=300); SDN comments would extend to thread-level
   - Could re-scrape SDN with depth metadata via existing Playwright script
   - **Effort: 1 week of scraping + re-scoring**
   - **Cost: $50-100 in Claude API for re-scoring**
   - **Risk: SDN scraping is rate-limited; Cloudflare partially blocks**

**Recommended:** Option 1 (thread-structure analysis on already-collected Reddit data). Skip Option 2 unless reviewers specifically ask.

### P2 — Reddit Finance cross-scorer finding strip (TIER 1; 0 days)

**Current data state:** The Reddit Finance OR=0.18 → 1.10-1.42 cross-scorer sign-flip is locked in `paper2_l5_cohort_robustness_results.txt`. The analytical lift for elevation is purely conceptual/theoretical (framing as "construct misalignment exemplar" + theoretical scaffold).

**No new data needed.** The boost is reframing + theoretical scaffolding. If reviewers request:
- Cross-scorer combinations beyond TextBlob/VADER/Claude (e.g., Llama × VADER, DeepSeek × TextBlob) — these can be computed from already-scored CSVs in `PSLF-Discussion-Analysis/` with ~1 day of additional analysis
- Simulation study showing when sign-flips occur — would require ~1 week of new code but uses no new data

### P3 — Workforce downstream (TIER 2 for NPPES, TIER 4 for AMA Masterfile; 1-3 weeks NPPES)

**Goal of boost:** link PSLF-hostile training programs to downstream physician practice locations. "Where do residents from for-profit chain programs practice after graduation?"

**Data needed:**

1. **CMS NPPES (National Plan and Provider Enumeration System)** — FREE public data
   - Every U.S. physician with NPI registration
   - Practice address (current)
   - Specialty taxonomy
   - Limitation: NPPES does NOT contain training program history; need to infer via fuzzy matching on specialty + estimated graduation year + name
   - URL: https://npiregistry.cms.hhs.gov/api-page (free API; bulk download available)
   - **Effort: 1-2 weeks of data engineering for NPI matching pipeline**
   - **Cost: $0**

2. **AAMC GraduateMedicalEd (GME) Track** — alternative; institutional license required
   - Has training program × current practice linkage
   - Requires AAMC membership or institutional subscription
   - **Effort: 1 week if access available; otherwise blocked**
   - **Cost: institutional license (check with your medical school's GME office)**

3. **AMA Physician Masterfile** — gold standard but commercial
   - Complete training history + current practice
   - $5K-15K commercial purchase; sometimes available via institutional license
   - **Effort: 1 week with data; access is the bottleneck**
   - **Cost: $5K-15K commercial; $0 if institution has license**

4. **HRSA Health Workforce data** — supplementary
   - Aggregate workforce by specialty + geography
   - Free at https://data.hrsa.gov/
   - **Effort: 2-3 days**

**Recommended path:** **Start with CMS NPPES** (free, public, immediately accessible). If your institution has AAMC GME Track or AMA Masterfile access, escalate.

**Alternative if data linkage proves too hard:** Drop the workforce downstream boost; rely on Option 1 (methods translation) alone for P3. Keeps JGME primary at current acceptance probability without requiring new data.

### P4 — Comprehensive residency program characterization (TIER 1; 1-2 weeks)

**Goal of boost:** broaden P4 from "PSLF eligibility classification" to "comprehensive residency program characterization dataset 2021-2026" to pass *Scientific Data*'s "broad utility" bar.

**Data needed (all free, all public):**

1. **ACGME Annual Data Reports** — accreditation status, program age, complement size, fellowship status
   - URL: https://www.acgme.org/about/publications-and-resources/annual-data-reports/
   - Multi-year (2018-2025) PDFs + spreadsheets
   - **Effort: 1 week to extract and harmonize**

2. **NIH RePORTER multi-year** — currently FY2023 only; expand to FY2018-2024
   - URL: https://reporter.nih.gov/
   - Public API + bulk download
   - **Effort: 2-3 days**

3. **VA Facility Directory** — flag VA-affiliated training programs
   - URL: https://www.va.gov/directory/guide/home.asp
   - **Effort: 1-2 days**

4. **AAMC Institutional Characteristics** — undergraduate enrollment, medical-school faculty count, residency program count
   - Public via AAMC databases
   - **Effort: 2-3 days**

5. **CMS Hospital Compare multi-year** — currently 2023 only; expand to 2018-2024
   - Free via https://data.cms.gov/
   - **Effort: 1 week**

**Total effort:** 2-3 weeks of data engineering for the broadened dataset; $0 cost.

**Recommended:** Yes, execute this. Modest effort + significantly stronger Scientific Data fit.

### P5 — Geographic + workforce-policy context (TIER 1; 3-5 days)

**Goal of boost:** add geographic and state-policy context to the HCA-Healthcare institutional concentration finding. Makes it a workforce-policy paper, not just a descriptive HCA list.

**Data needed (all free, all public):**

1. **HRSA Health Professional Shortage Area (HPSA) designation** — by county/state
   - URL: https://data.hrsa.gov/topics/health-workforce/shortage-areas
   - Free CSV download
   - **Effort: 1 day to merge with institution geocoordinates**

2. **USDA Rural-Urban Commuting Area (RUCA) codes** — county-level urbanicity classification
   - URL: https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/
   - Free Excel download
   - **Effort: 1 day**

3. **KFF Medicaid Expansion Status tracker** — state-level health-policy variable
   - URL: https://www.kff.org/medicaid/issue-brief/status-of-state-medicaid-expansion-decisions-interactive-map/
   - Free table (small)
   - **Effort: 0.5 day**

4. **U.S. Census Bureau county demographics** — for socioeconomic context
   - Free via Census API
   - **Effort: 1 day**

**Total effort:** 3-5 days; $0 cost.

**Recommended:** Yes, execute this. Cheap and meaningfully strengthens the workforce-policy framing.

### P6 — Multi-policy comparison (TIER 1; 1-2 weeks)

**Goal of boost:** expand from PSLF-only event analysis to multi-policy comparison (Biden v. Nebraska, SAVE plan litigation, payments restart, etc.) to make P6 a "discourse-as-policy-thermometer" paper.

**Data needed:**

1. **Other student-loan policy event dates** — public historical record
   - Biden v. Nebraska SCOTUS argument + ruling (Feb 2023, June 2023)
   - SAVE plan introduction + litigation (2023, 2024)
   - Payments restart announcement + effective date (2023)
   - Already documented in `MASTER_LOCKED_NUMBERS.md` per R17 events
   - **Effort: 0.5 day to compile event window dictionary**

2. **Reddit r/StudentLoans corpus** (not just r/PSLF) — already partially collected
   - Currently have r/PSLF posts + comments
   - Need to extend Reddit Arctic Shift query to r/StudentLoans + r/Bogleheads (note: Bogleheads is Cloudflare-blocked) + r/personalfinance student-loan subset
   - **Effort: 1 week for additional Reddit Arctic Shift pulls**
   - **Cost: free (Arctic Shift)**

3. **CFPB Complaints Database** — supplementary for behavioral outcomes
   - Free public download
   - Has complaint counts by date + issue type
   - Could correlate with sentiment shifts
   - **Effort: 2-3 days**
   - **Optional but strengthens behavior connection**

**Total effort:** 1-2 weeks; $0 cost.

**Recommended:** Yes, execute the additional Reddit pulls + event dictionary. CFPB Complaints Database is optional supplement.

### P7 — NSLDS PGY-1 follow-up (TIER 3; 6-12 month review)

See `NSLDS_DUA_APPLICATION_CHECKLIST.md` for full process detail.

**Critical action: start the DUA application NOW.** Even though P7 won't be in print by ERAS Sept 2027, the active DUA pipeline can be listed as "Research in Progress" on ERAS.

---

## Cross-paper integration

Several data sources serve multiple papers:

| Data source | Used in | Acquisition action |
|---|---|---|
| CMS NPPES | P3 (workforce downstream) | Pull once; cross-walk to NRMP institutions |
| ACGME Annual Data Reports | P4 (broadened dataset) | Pull multi-year PDFs; harmonize |
| NIH RePORTER multi-year | P4 (broadened dataset) | API pull FY2018-2024 |
| HRSA HPSA | P5 (geographic) | Merge with institution geocoordinates |
| USDA RUCA | P5 (geographic) | County-level merge |
| Reddit r/StudentLoans corpus | P6 (multi-policy) | Arctic Shift pull |
| NSLDS borrower-level | P7 (PGY-1 follow-up) | DUA application |

**Consolidated build script (recommended):** `build_extended_residency_dataset.py` that integrates all the TIER 1 acquisitions into a single combined dataset. ~1 week effort; serves P3 + P4 + P5 simultaneously.

---

## Critical path timeline

Assuming research year starts July 2026:

| Window | Data acquisition action |
|---|---|
| **Aug 2026** | Start NSLDS DUA application (TIER 3 long-horizon); pull HRSA HPSA + USDA RUCA + KFF Medicaid for P5 (3-5 days); pull ACGME multi-year + NIH RePORTER multi-year for P4 (1-2 weeks) |
| **Sep 2026** | Pull CMS NPPES + build NPI matching pipeline for P3 workforce (1-2 weeks); pull additional Reddit r/StudentLoans for P6 (1 week) |
| **Oct 2026** | Build `build_extended_residency_dataset.py` consolidating P3+P4+P5 data sources (1 week); compile P6 event-window dictionary (0.5 day) |
| **Nov 2026** | Begin P3 + P5 paper writing using new data |
| **Dec 2026 - Jan 2027** | P4 + P6 paper writing |
| **Feb 2027** | All papers in submission cycle |
| **Mar-Jun 2027** | Revisions cycle; data acquisition continues for NSLDS if approved |
| **Jul-Aug 2027** | Final preparations before ERAS Sept 2027 |

**Critical-path data acquisition:** P3 workforce downstream (CMS NPPES matching pipeline) is the longest single data-engineering task (~2 weeks). Start this in early September 2026 to allow time for P3 writing.

---

## What's NOT recommended for acquisition

These would be high-value but are out of realistic scope for a medical student:

- **AMA Physician Masterfile** ($5K-15K commercial) — too expensive unless institutional license exists
- **AAMC ERAS application data** — restricted-use; multi-month DUA process
- **State medical board licensure data** — patchwork access; state-by-state variation; high effort
- **Doximity full-provider scraping** — gray area legally; against ToS
- **Twitter/X academic API** — has been restricted since 2023; mostly inaccessible
- **Twitter/X commercial firehose** — $$$$$, way out of scope

---

## Cost summary

- **TIER 1 acquisitions (P1, P2 supplemental + P4 + P5 + P6):** $0
- **TIER 2 acquisitions (P3 CMS NPPES):** $0 + 2 weeks data engineering
- **TIER 3 acquisitions (P7 NSLDS):** $0-500 in fees; 6-12 month review
- **Optional Tier 4 (P3 AMA Masterfile):** $5K-15K if institution doesn't have license

**Total realistic cost:** $0 if institutional access to NPPES + ACGME + NIH RePORTER + HRSA + USDA is available (it is — all public).

**Total realistic time:** ~5-6 weeks of data engineering across the boost strategies, executable during research year alongside paper writing.

---

## Source files

- `PAPER_{1,2,3,4,5,6}_DRAFT_READY.md` + the renamed `PAPER_5_SURGICAL_SUBSPECIALTY_DRAFT_READY.md`
- `NSLDS_DUA_APPLICATION_CHECKLIST.md`
- `MASTER_LOCKED_NUMBERS.md` + `MASTER_REFERENCE_LIST.md`
- `scripts/` — extending with `build_extended_residency_dataset.py` and per-paper analytical scripts
- This file (DATA_ACQUISITION_PLAN_R17pp6.md) is the single source of truth for new-data needs
