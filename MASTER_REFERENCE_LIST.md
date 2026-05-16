# Master Reference List — All 3 Papers (Path B)

**Last updated:** 2026-05-10
**Status:** Drafting-ready; full bibliographic entries with publication URLs/DOIs.

Citations grouped by topic. Each entry tagged with paper(s) that use it. Use this as the single source for BibTeX or citation-management import.

---

## Construct validity / multitrait-multimethod / sentiment vs stance

**Bestvater, S. & Monroe, B. L. (2023).** Sentiment is not stance: Target-aware opinion classification for political text analysis. *Political Analysis*, 31(2), 235–256. doi:10.1017/pan.2022.10
- **Used in:** P1 §1.3, §2.3, §6.2; P2 §1.2, §2.2, §5.3
- **Why:** Foundational sentiment-stance distinction; n=3,660 Kavanaugh hand-coded; r=0.03 between sentiment and stance. Closest precedent for our framing.

**Mohammad, S., Kiritchenko, S., Sobhani, P., Zhu, X., & Cherry, C. (2016).** SemEval-2016 Task 6: Detecting Stance in Tweets. In *Proceedings of the 10th International Workshop on Semantic Evaluation (SemEval-2016)*, 31–41. ACL Anthology S16-1003. https://aclanthology.org/S16-1003/
- **Used in:** P1 §1.3, §2.3; P2 §1.2, §2.2
- **Why:** Formal stance task definition (3-label: favour/neutral/against; 5 target topics: abortion, atheism, climate change, feminism, Hillary Clinton); theoretical anchor for "target-aware position." Round 17++ audit corrected author list (was 3 authors; actual is 5: Mohammad, Kiritchenko, Sobhani, Zhu, Cherry).

**Campbell, D. T. & Fiske, D. W. (1959).** Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin*, 56(2), 81–105.
- **Used in:** P1 §1.3, §6.2 (with caveat in L0c that constructs are unvalidated)
- **Why:** Classical psychometric framework for multi-instrument convergent validity.

---

## LLM-as-classifier validation

**Bojić, L., Zagovora, O., Zelenkauskaite, A., Vuković, V., Čabarkapa, M., Veseljević Jerković, S., & Jovančević, A. (2025).** Comparing Large Language Models and Human Annotators in Latent Content Analysis of Sentiment, Political Leaning, Emotional Intensity and Sarcasm. *Scientific Reports*, 15, Article 11477. doi:10.1038/s41598-025-96508-3. PMC11968858. arXiv preprint: 2501.02532 ("Evaluating Large Language Models Against Human Annotators in Latent Content Analysis...")
- **Used in:** P1 §1.3, §2.2; abstract
- **Why:** Direct competitor / closest prior work — tested 8 LLM variants (GPT-3.5-turbo-16k, GPT-4, GPT-4o, GPT-4o-mini, Gemini 1.5 Pro, Llama-3.1-70B, Mixtral 8x7B, Hard Prompt GPT-4o) against 33 human annotators on 100 curated textual items (3,300 human + 19,200 LLM annotations across 4 dimensions: sentiment, political leaning, emotional intensity, sarcasm). Our extension: cross-organization 3-LLM (Claude + Llama + DeepSeek) at n=1,001 forum-text intersection with cross-organizational diversity Bojić's panel does not include (no Anthropic Claude, no DeepSeek).
- **Round 17++ CRITICAL CORRECTION (2026-05-11)**: a prior version of this entry was attributed to "Calderon, N., Caspi, R., Friedman-Avraham, A., et al." That author list was FABRICATED — there are no Calderon, Caspi, or Friedman-Avraham authors on the paper at this DOI. The actual first author is Ljubiša Bojić. **All inline references to "Calderon et al. 2025" in paper outlines must be re-attributed to "Bojić et al. 2025."** This was caught by the second-pass verification audit; the prior audit cycle had matched the substance of the paper but the author list was hallucinated.

**Heseltine, M. & Clemm von Hohenberg, B. (2024).** Large language models as a substitute for human experts in annotating political text. *Research & Politics*, 11(1).
- **Used in:** P1 §1.3, §2.2

**Burnham, M. (2025).** Stance detection: a practical guide to classifying political beliefs in text. *Political Science Research and Methods*, 13(3), 611–628. doi:10.1017/psrm.2024.35
- **Used in:** P1 §1.3, §2.2
- **Why:** LLM stance-detection methodological reference. Round 17 audit corrected venue from "Political Analysis" → "Political Science Research and Methods".

**Halterman, A. & Keith, K. (2025).** Codebook LLMs: Evaluating LLMs as measurement tools for political science concepts. *Political Analysis*. doi:10.1017/pan.2025.10017
- **Used in:** P1 §2.2
- **Why:** LLM-with-codebook reproducing human inter-rater reliability for stance + topic classification. Round 17 audit added author names (previously "full author list pending").

**Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024).** Synthetic Replacements for Human Survey Data? The Perils of Large Language Models. *Political Analysis*, 32, 401–416. doi:10.1017/pan.2024.5
- **Used in:** P1 §2.2 (counterweight), §6.4 limitation
- **Why:** LLM stochasticity / paraphrase-sensitivity skepticism on synthetic-survey use; calibrates our paraphrase-robustness contribution. Round 17++ audit added definitive volume/page/DOI (was previously "(forthcoming)").

**[REPLACED — Round 17++ audit, 2026-05-11]** A prior entry "Spirling, A. (2024). Why open-source LLMs are necessary for political science. *Political Analysis*, 32(2)" CANNOT be verified at that title/venue/issue via WebSearch. The closest verified Spirling work is **Spirling, A. (2023).** Why open-source generative AI models are an ethical way forward for science. *Nature*, 616(7957), 413. doi:10.1038/d41586-023-01295-4 — which is the standard "open-source LLMs in scholarship" citation. Use this verified Nature 2023 reference instead. Other 2024 Spirling work is co-authored (Palmer, Smith & Spirling 2024; Barrie, Palmer & Spirling 2024) and on different topics.

**Spirling, A. (2023).** Why open-source generative AI models are an ethical way forward for science. *Nature*, 616(7957), 413. doi:10.1038/d41586-023-01295-4
- **Used in:** P1 §2.2 (counterweight), §6.4
- **Why:** Open-source-LLM advocacy paper — the standard "reproducibility argument for OSS LLMs in social-science research" citation. Substituted by Round 17++ audit for unverifiable "Spirling 2024 Political Analysis."

**Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024).** Can Large Language Models Transform Computational Social Science? *Computational Linguistics*, 50(1), 237–291. https://aclanthology.org/2024.cl-1.8/
- **Used in:** P1 §2.2
- **Why:** Round 17++ audit added page range (was missing). Author list (6 authors) verified correct.

**Gilardi, F., Alizadeh, M., & Kubli, M. (2023).** ChatGPT outperforms crowd-workers for text-annotation tasks. *PNAS*, 120(30), e2305016120.
- **Used in:** P1 §2.2 (foundational LLM-as-annotator)

**Tornberg, P. (2023).** ChatGPT-4 outperforms experts and crowd workers in annotating political Twitter messages with zero-shot learning. *arXiv:2304.06588*.
- **Used in:** P1 §2.2

---

## Lexical sentiment instruments

**Hutto, C. J. & Gilbert, E. (2014).** VADER: A parsimonious rule-based model for sentiment analysis of social media text. In *Proceedings of ICWSM*, 216–225.
- **Used in:** P1 §1, §2.1, §3.1; P2 §3.4
- **Why:** VADER methodology paper.

**Loria, S. (2018).** TextBlob documentation. Release 0.18.0. https://textblob.readthedocs.io/
- **Used in:** P1 §2.1, §3.1; P2 §3.4

**De Smedt, T. & Daelemans, W. (2012).** Pattern for Python. *Journal of Machine Learning Research*, 13, 2063–2067.
- **Used in:** P1 §2.1 (Pattern.en is TextBlob's underlying engine)

**Ribeiro, F. N., Araújo, M., Gonçalves, P., Gonçalves, M. A., & Benevenuto, F. (2016).** SentiBench — a benchmark comparison of state-of-practice sentiment analysis methods. *EPJ Data Science*, 5(23).
- **Used in:** P1 §2.1, §6.4 (cite as the canonical EPJ DS sentiment-comparison paper; differentiate our contribution)

**van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021).** The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. *Communication Methods and Measures*, 15(2), 121–140.
- **Used in:** P1 §2.1, §2.4 (validity methodology framing)

**Boukes, M., van de Velde, B., Araujo, T., & Vliegenthart, R. (2020).** What's the tone? Easy doesn't do it. *Communication Methods and Measures*, 14(2), 83–104.
- **Used in:** P1 §2.1 (TB/VADER/SentiStrength comparison precedent)

**Reagan, A. J., Mitchell, L., Kiley, D., Danforth, C. M., & Dodds, P. S. (2016).** The emotional arcs of stories are dominated by six basic shapes. *EPJ Data Science*, 5(31). doi:10.1140/epjds/s13688-016-0093-1
- **Used in:** P1 §2.1 (lexicon disagreement precedent at EPJ DS)
- **Why:** Round 17++ audit corrected year from 2017 to 2016 (verified via Springer DOI).

---

## Inter-rater reliability methodology

**Hayes, A. F. & Krippendorff, K. (2007).** Answering the call for a standard reliability measure for coding data. *Communication Methods and Measures*, 1(1), 77–89.
- **Used in:** P1 §3.3, §4.2; P2 §4.1
- **Why:** Krippendorff α + bootstrap CI methodology.

**Krippendorff, K. (2018).** *Content Analysis: An Introduction to Its Methodology* (4th ed.). Sage.
- **Used in:** P1 §1.3, §5.2 (cite for the 0.667 tentative-reliability and 0.80 satisfactory-reliability floors)

**Landis, J. R. & Koch, G. G. (1977).** The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174.
- **Used in:** P1 §5.1 (Cohen's κ thresholds: ≤0.20 = slight; 0.21–0.40 = fair; 0.41–0.60 = moderate; 0.61–0.80 = substantial; 0.81–1.00 = almost perfect)

**Castro, S. (2020).** krippendorff Python package, v0.6+. https://github.com/pln-fing-udelar/fast-krippendorff
- **Used in:** P1 §3.3 software

---

## Within-thread / OP-vs-reply sentiment dynamics

**Choi, M., Aiello, L. M., Varga, K., & Quercia, D. (2020).** Ten Social Dimensions of Conversations and Relationships. In *Proceedings of The Web Conference 2020 (WWW '20)*, 1514–1525. ACM. doi:10.1145/3366423.3380224
- **Used in:** P1 §1.4, §5.5, §8 (within-thread sentiment dynamics; cite as adjacent precedent)
- **Why:** Round 17 audit corrected venue from misattributed "PNAS 117(31)" (which does not exist for these authors) to the actual WWW '20 publication, and corrected the author list (Aiello/Varga/Quercia, not Joo/Yi/Tan).

**Tsugawa, S. & Ohsaki, H. (2015).** Negative messages spread rapidly and widely on social media. In *Proceedings of the 2015 ACM Conference on Online Social Networks (COSN '15)*, 151–160. doi:10.1145/2817946.2817962
- **Used in:** P1 §5.5
- **Why:** Round 17 audit corrected venue from "ACM Web Science Conference" → "COSN '15".

**[REMOVED — Round 17++ audit, 2026-05-11]** A prior entry "Hwang, K. O., Lee, M., & Park, J. (2017). Sentiment shifts in social-support forums. *JMIR* 19(4)" CANNOT be verified via WebSearch. Closest match found is Park & Conway (2017) "Longitudinal Changes in Psychological States in Online Health Community Members" *JMIR* 19(3) — but author list and topic differ. The "Hwang, Lee, Park 2017 JMIR" citation has been excised because we cannot confirm it exists with these author/title/issue details. Verified alternative for "online support forum sentiment dynamics over time" if needed: **Park, A. & Conway, M. (2017).** Longitudinal Changes in Psychological States in Online Health Community Members. *Journal of Medical Internet Research*, 19(3), e71. https://www.jmir.org/2017/3/e71/

- **NOTE (Round 17 + Round 17++ audit, two passes)**: THREE prior citations REMOVED from the within-thread / OP-vs-reply section because Round 17 + Round 17++ WebSearches failed to verify their existence:
  (a) "Wang, Mei et al. (2023) Sentiment polarity shifts in conversational threads, ICWSM" — no record at ICWSM 2023.
  (b) "Park, Kim & Lee (2023) TextBlob-VADER divergence in Reddit comment sentiment, JCSS 6(2)" — no record found.
  (c) "Hwang, K. O., Lee, M., & Park, J. (2017). Sentiment shifts in social-support forums. JMIR 19(4)" — could not verify; closest match has different authors and topic.
  All three citations may have been generated as plausible-sounding placeholders in earlier draft rounds. They have been excised. Any paper outline reference to (a), (b), or (c) must be removed or replaced with a VERIFIED alternative. Verified alternatives that DO exist for these topics: Boukes 2020 CMM (TB/VADER comparison); Baumartz et al. 2024 arXiv:2410.14626 (instrument-class separability); Park & Conway 2017 JMIR 19(3) e71 (longitudinal sentiment in online health community).

---

## Common Method Variance (CMV) and methodological alternatives

**Podsakoff, P. M., MacKenzie, S. B., Lee, J.-Y., & Podsakoff, N. P. (2003).** Common method biases in behavioral research. *Journal of Applied Psychology*, 88(5), 879–903.
- **Used in:** P2 §1.2 (acknowledge as initial framing), §2.3 (cite as background, NOT as our framework — we explicitly do not apply Podsakoff CMV per Round 16 fix)

**Spector, P. E. (2006).** Method variance in organizational research. *Organizational Research Methods*, 9(2), 221–232.
- **Used in:** P2 §2.3

**Williams, L. J., Hartman, N., & Cavazotte, F. (2010).** Method variance and marker variables. *Organizational Research Methods*, 13(3), 477–514.
- **Used in:** P2 §2.3

---

## Composition bias / forum data limitations / Reddit-specific methodology

**Zhu, H., Yin, Y., & Zhang, Y. (2025).** Survivors, Complainers, and Borderliners: Upward Bias in Online Discussions of Academic Conference Reviews. *arXiv:2509.16831*. https://arxiv.org/abs/2509.16831
- **Used in:** P2 §1.3, §2.4 (closest composition-shift precedent; explicit differentiation in §2.4)
- **Why:** Documents three composition-bias mechanisms (survivors, complainers, borderliners) on Reddit + Zhihu academic-conference-review discussions vs full submission populations. Round 17++ audit corrected attribution from a prior incorrect "Wang, J. et al." authorship and corrected the title (was "A composition-bias analysis of academic discourse on Reddit and Zhihu" — actual title is "Survivors, Complainers, and Borderliners: Upward Bias in Online Discussions of Academic Conference Reviews").

**Kim, R., Veselovsky, V., & Anderson, A. (2025).** Capturing Dynamics in Online Public Discourse: A Case Study of Universal Basic Income Discussions on Reddit. *Proceedings of the International AAAI Conference on Web and Social Media (ICWSM)*, Vol. 19. arXiv:2312.09611. https://ojs.aaai.org/index.php/ICWSM/article/view/35858
- **Used in:** P2 §1.3, §2.6 (DIRECT precedent for cohort-heterogeneous sentiment-in-policy-discourse: explicitly analyzes "shifts within different user cohorts" on UBI Reddit and finds "newer cohorts are more negative about UBI than older cohorts" with cohort-specific stance dynamics, classifying users by year-of-first-comment "cohort." P2's cohort-heterogeneity novelty claim must cite + differentiate from this work.)
- **NOTE (Round 17++ audit)**: A prior version of this entry (introduced earlier in this session) mis-attributed the paper to "Trabelsi, A., Zhu, X., Yin, X., & Zhang, Y. (2024)" with a 2024 ICWSM date. **Both the author list and year were WRONG.** Verified via WebSearch 2026-05-11: actual authors are Kim, Veselovsky, and Anderson (University of Toronto); actual venue is ICWSM Vol 19 (2025); arXiv preprint dated 2023 (arXiv:2312.09611) but final-publication ICWSM Vol 19 = 2025.

**Freelon, D., Monzer, C., Jeon, G., Moy, C., & Williams, N. (2024).** The Post-API Age of Social Media Data Access: Past, Present, and Future. *Annals of the American Academy of Political and Social Science*, 715(1), 16–37. doi:10.1177/00027162251372557
- **Used in:** P2 §1.3, §2.4 (forum-data limitations); P1 §2.2 (companion to Pushshift methodological context)
- **Why:** Round 17 audit corrected author list (Marwick + Kreiss are NOT authors; actual co-authors are Monzer, Jeon, Moy, Williams) and volume (Vol 715, not 712).

**Baumgartner, J., Zannettou, S., Keegan, B., Squire, M., & Blackburn, J. (2020).** The Pushshift Reddit dataset. In *Proceedings of ICWSM*, 830–839.
- **Used in:** P1 §3.1; P2 §3.1 (Arctic Shift is Pushshift successor)

---

## Statistical methods (bootstrap, multiple comparisons, etc.)

**Bickel, P. J., Götze, F., & van Zwet, W. R. (1997).** Resampling fewer than n observations: Gains, losses, and remedies for losses. *Statistica Sinica*, 7, 1–31.
- **Used in:** P1 §3.6 (block-permutation test for autocorrelation)

**Politis, D. N. & Romano, J. P. (1994).** The stationary bootstrap. *Journal of the American Statistical Association*, 89(428), 1303–1313.
- **Used in:** P1 §3.6 (block bootstrap)

**Holm, S. (1979).** A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70.
- **Used in:** P1 §3.7; P2 §4.4

**Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008).** Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414–427.
- **Used in:** P3 §2.5 (cluster-robust SE)

**Cameron, A. C. & Miller, D. L. (2015).** A practitioner's guide to cluster-robust inference. *Journal of Human Resources*, 50(2), 317–372.
- **Used in:** P3 §2.5 (small-cluster wild-cluster bootstrap recommendation)

**Webb, M. D. (2014).** Reworking Wild Bootstrap Based Inference for Clustered Errors. *Queen's Economics Department Working Paper No. 1315*. http://qed.econ.queensu.ca/working_papers/papers/qed_wp_1315.pdf (Eventually published as Webb, M. D. (2023). Reworking wild bootstrap‐based inference for clustered errors. *Canadian Journal of Economics*, 56(3), 839–858.)
- **Used in:** P3 §2.5 (Webb 6-point weights)
- **Why:** Round 17++ audit verified the working paper exists at Queen's Economics Dept WP 1315; Round 17++ also added the 2023 CJE published-version reference for citations preferring published-vs-WP. Either is acceptable to cite.

**MacKinnon, J. G. & Webb, M. D. (2018).** The wild bootstrap for few (treated) clusters. *Econometrics Journal*, 21(2), 114–135. doi:10.1111/ectj.12107
- **Used in:** P3 §2.5 (Round 17 audit add — KEY citation for Paper 3's design with G=9–23 hostile clusters; MacKinnon-Webb 2018 is the specifically-applicable methodological reference for wild-cluster inference with few treated clusters, complementing the more general Cameron-Miller 2015)

**Roodman, D., MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D. (2019).** Fast and wild: Bootstrap inference in Stata using boottest. *Stata Journal*, 19(1), 4–60. doi:10.1177/1536867X19830877
- **Used in:** P3 §2.5 (Round 17 audit add — most-cited modern wild-cluster bootstrap implementation reference; cite alongside Cameron-Miller 2015 and MacKinnon-Webb 2018)

**MacKinnon, J. G. & White, H. (1985).** Some heteroskedasticity-consistent covariance matrix estimators. *Journal of Econometrics*, 29(3), 305–325.
- **Used in:** P3 §2.5 (HC3, supplement)

**Borenstein, M., Hedges, L. V., Higgins, J. P. T., & Rothstein, H. R. (2009).** *Introduction to Meta-Analysis*. Wiley.
- **Used in:** P1 §3 (Hedges' g variance with J² correction; equation 4.24)

**McNemar, Q. (1947).** Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika*, 12(2), 153–157.
- **Used in:** P2 §4.5 (within-person Δ test)

---

## PSLF policy / federal student loan context

**US Department of Education (2024).** PSLF Program Data and Reports. https://studentaid.gov/data-center/student/loan-forgiveness/pslf-data
- **Used in:** P1 §3.2; P2 §3.2; P3 §1.1

**Consumer Financial Protection Bureau (2024).** Annual Report of the CFPB Student Loan Ombudsman (November 2024). https://files.consumerfinance.gov/f/documents/cfpb_2024-annual-student-loan-ombudsmans-report_2024-11.pdf ; https://www.consumerfinance.gov/data-research/research-reports/annual-report-of-the-cfpb-student-loan-ombudsman-2024/
- **Used in:** P3 background (PSLF servicing failures + 14,000 federal student loan complaints in 2024); also legacy R12 P3 framing context
- **Verified Round 17++ (2026-05-11)**: Round 17++ audit confirmed via direct CFPB URL.

**Itzkowitz, M. & Akers, B. (2024).** The past, present, and future of the Public Service Loan Forgiveness program. *Brookings*. https://www.brookings.edu/articles/the-past-present-and-future-of-the-public-service-loan-forgiveness-program/
- **Used in:** P3 background context
- **Verified Round 17++ (2026-05-11)**: Brookings article confirmed at this exact URL. (Note: lowercase "past, present, and future" with commas in actual title — earlier WebSearch with capitalized-quoted phrasing failed due to that.)

**Student Borrower Protection Center & American Federation of Teachers (2024).** The MOHELA Papers: The Rise of a Student Loan Servicing Giant and the Fall of the Student Loan System. February 2024. https://www.mohelapapers.org/ ; SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4876434
- **Used in:** P2 §2.5 (legacy gray-literature MOHELA reference; **note: MOHELA was DROPPED from current Path B P3 — this cite is no longer load-bearing for the substantive arc, but documented here for completeness**)
- **Verified Round 17++ (2026-05-11)**: Real report. Released February 2024. SSRN abstract 4876434 confirms institutional authorship.

**Tate, S.** Does HCA Qualify for PSLF? *TateEsq.com — Student Loan Lawyer*. https://www.tateesq.com/learn/does-hca-qualify-for-pslf
- **Used in:** P3 §2.3 (HCA-academic eligibility ambiguity context — gray-literature legal commentary)
- **Why:** Stanley Tate is a real student-loan attorney; substantive claim that HCA is for-profit and HCA-employed residents are not PSLF-eligible regardless of academic affiliation is supported. **Caveat (Round 17++)**: this is a blog/commentary source, NOT peer-reviewed. The current P3 §2.3 HCA-academic ambiguity is addressed via the S1/S2/S3 sensitivity analysis (W-2 employer ambiguity); Tate Esq. can be cited as gray-literature support but should not be the primary basis for the classification.

## Round 17++ second-pass verifications added 2026-05-11 (community norms + composition bias)

**Lave, J. & Wenger, E. (1991).** *Situated Learning: Legitimate Peripheral Participation*. Cambridge University Press.
- **Used in:** P2 §2.6 (community-norms background; cited with caveat that Reddit/SDN posters are not "communities of practice" in the strict Lave-Wenger sense)
- **Verified Round 17++**: real Cambridge UP textbook; widely cited.

**Massanari, A. (2017).** #Gamergate and The Fappening: How Reddit's algorithm, governance, and culture support toxic technocultures. *New Media & Society*, 19(3), 329–346. doi:10.1177/1461444815608807
- **Used in:** P2 §2.6 (Reddit cultural/normative dynamics)
- **Verified Round 17++**: real paper; verified via Sage publisher page and Semantic Scholar.

**Chandrasekharan, E., Samory, M., Jhaver, S., Charvat, H., Bruckman, A., Lampe, C., Eisenstein, J., & Gilbert, E. (2018).** The Internet's Hidden Rules: An Empirical Study of Reddit Norm Violations at Micro, Meso, and Macro Scales. *Proceedings of the ACM on Human-Computer Interaction* 2(CSCW), Article 32. doi:10.1145/3274301
- **Used in:** P2 §2.6 (Reddit norm-violation detection; macro/meso/micro norms)
- **Verified Round 17++**: real CSCW 2018 paper; 8-author list verified via ACM DL.

**Reagle, J. M. Jr. (2010).** *Good Faith Collaboration: The Culture of Wikipedia*. MIT Press. ISBN 978-0-262-01447-2 (hardcover) / 0-262-51820-1 (paperback).
- **Used in:** P2 §2.6 (online community culture background)
- **Verified Round 17++**: real MIT Press book by Joseph M. Reagle Jr.; verified via Wikipedia + MIT Press.

## Round 17++ FABRICATIONS / MISATTRIBUTIONS found in legacy R12 Notion content (2026-05-11)

The following citations were in the prior R12 Notion content but **could NOT be verified** at the attributed author/venue. All are no longer load-bearing for Path B but are documented here so they are not reintroduced:

- **Yannelis & Looney 2024 NBER WP 33059** — INCORRECT. WP 33059 is actually **Catherine, Ebrahimian & Yannelis 2024** "How Do Income-Driven Repayment Plans Benefit Student Debt Borrowers?" NBER WP 33059. The real Looney & Yannelis 2024 work is **"What Went Wrong with Federal Student Loans?"** NBER WP 32469 (also published in *Journal of Economic Perspectives* Summer 2024).
- **Cousineau 2025 MDPI Journalism & Media** — INCORRECT. No paper by "Cousineau" found at this venue. The closest matching paper is **Arowosafe, S. & Makata, E. (2025).** "Polarization and Sentiment Shifts in Reddit Discussion on the US Foreign Aid Freeze." *Journalism and Media* 6(4):199.
- **Kovács et al. 2018 JDIQ "selection bias in social-media event studies"** — INCORRECT. The matching paper is **Zhang, H., Hill, S., & Rothschild, D. (2018).** "Addressing Selection Bias in Event Studies with General-Purpose Social Media Panels." *Journal of Data and Information Quality* (JDIQ). doi:10.1145/3185048. No author named Kovács.

**College Cost Reduction and Access Act (2007).** Public Law 110-84.
- **Used in:** P1 §3.2; P2 §3.2; P3 §1.1

**U.S. Department of Education (2025).** Final Rule on Public Service Loan Forgiveness. Announced October 30, 2025; published in the Federal Register October 31, 2025; effective July 1, 2026. (FR doc 2025-19729; ED press release "U.S. Department of Education Announces Final Rule on Public Service Loan Forgiveness to Protect American Taxpayers" https://www.ed.gov/about/news/press-release/us-department-of-education-announces-final-rule-public-service-loan-forgiveness-protect-american-taxpayers)
- **Used in:** P3 §1.4
- **Why:** Round 17++ audit corrected date precision: announcement was Oct 30; FR publication was Oct 31 (canonical date for Federal Register citation). Both dates are now disclosed.

**Trump, D. J. (2025).** Executive Order 14235 — Restoring Public Service Loan Forgiveness. Signed March 7, 2025. White House. govinfo: DCPD-202500340. https://www.govinfo.gov/app/details/DCPD-202500340 ; https://www.whitehouse.gov/presidential-actions/2025/03/restoring-public-service-loan-forgiveness/
- **Used in:** P3 §4.3; P2 §4.6 (event #7)
- **Why:** Round 17++ audit corrected EO number from 14253 (which is a DIFFERENT EO) to **14235** (the actual Restoring Public Service Loan Forgiveness EO). Verified via American Presidency Project + govinfo + H.R.4727 (119th Congress, 2025-2026) which references EO 14235 by number.

**Khoury, M. K., Jones, R. E., Gee, K. M., Taveras, L. R., Boniakowski, A. M., Coleman, D. M., Abdelfattah, K. R., Rectenwald, J. E., & Minter, R. M. (2021).** Trainee Reliance on Public Service Loan Forgiveness. *Journal of Surgical Education*, 78(6). PMC8648921. (Round 17 audit replaces a previous misattribution to "Marcu et al. Federal Reserve Bank of Atlanta Discussion Paper" — that paper does not exist at that title/venue; the underlying PMC8648921 is Khoury et al. in J Surg Educ. The Marcu authors did write "Borrow or Serve? An Economic Analysis of Options for Financing a Medical School Education" PMC5483978, 2017 — see separate entry below if relevant.)
- **Used in:** P3 §1.1
- **Why:** Survey of US surgical trainees (n=934, 44.5% using PSLF; 20% report PSLF impacts career decisions). Direct precedent for P3's behavioral-mechanism framing.

**Marcu, M. I., Kellermann, A. L., Hunter, C., Curtis, J., Rice, C., & Wilensky, G. R. (2017).** Borrow or Serve? An Economic Analysis of Options for Financing a Medical School Education. *Academic Medicine*, 92(7), 966–975. PMC5483978. https://pmc.ncbi.nlm.nih.gov/articles/PMC5483978/
- **Used in:** P3 §1.1 (financing-decision economic analysis — distinct from PSLF-reliance survey above)
- **Why:** Round 17++ audit fixed author list (Crecelius & Lieberman are NOT authors; actual co-authors are Rice & Wilensky). Added volume/issue/page numbers (92(7):966-975) and DOI confirmation.

**Student Borrower Protection Center & American Federation of Teachers (2024).** PSLF Servicer Performance Report.
- **Used in:** P2 §2.5; P3 (background only; not central)

**Pew Research Center (2024).** Public attitudes on student loan forgiveness.
- **Used in:** P2 §2.5

---

## NRMP / residency match

**NRMP (2021–2025).** Results and Data: Main Residency Match. https://www.nrmp.org/match-data/
- **Used in:** P3 §2.1, §3.1

**NRMP (2024).** Results of the 2024 NRMP Program Director Survey.
- **Used in:** P3 §2.1

**Roth, A. E. & Peranson, E. (1999).** The Redesign of the Matching Market for American Physicians. *American Economic Review*, 89(4), 748–780.
- **Used in:** P3 §2.5 (mechanism design context)

**Agarwal, N. (2015).** An Empirical Model of the Medical Match. *American Economic Review*, 105(7), 1939–1978.
- **Used in:** P3 §2.5 (canonical residency-match modeling reference)

**Gottlieb, J. D., Polyakova, M., Rinz, K., Shiplett, H., & Udalova, V. (2025).** The Earnings and Labor Supply of U.S. Physicians. *Quarterly Journal of Economics*, 140(2), 1243–1298. (Round 17 audit add — foundational econometric framework for physician labor supply; should be cited as background even though not PSLF-specific. Round 17++ audit corrected page range to 1243-1298 — earlier note said 1243-1294 which was a typo.)
- **Used in:** P3 §1.1, §1.2

---

## For-profit chain residency expansion

**HCA Healthcare (2014).** Graduate Medical Education Expansion Announcement.
- **Used in:** P3 §1.2

**[REPLACED — Round 17++ audit, 2026-05-11]** A prior entry "Salsberg, E. (2017). The For-Profit Path to Graduate Medical Education. *Health Affairs Forefront*" CANNOT be verified at this title/year via WebSearch. Real Salsberg work in Health Affairs exists but is dated 2014 (the IOM report commentary "The 2014 GME Residency Match Results: Is There Really A 'GME Squeeze'?"), and I could not confirm a Salsberg 2017 piece on for-profit GME. The substantive claim (HCA / for-profit GME expansion since 2014) is verifiable elsewhere — substitute with these confirmed peer-reviewed sources:

**Lassner, J. W., Ahn, J., Singh, A., & Kukulski, P. (2022).** Growth of for-profit involvement in emergency medicine graduate medical education and association between for-profit affiliation and resident salary. *AEM Education and Training*, 6(4), e10786. doi:10.1002/aet2.10786. PMC9348842. PMID 35936813. https://pmc.ncbi.nlm.nih.gov/articles/PMC9348842/
- **Used in:** P3 §1.2 (substituted for unverifiable "Salsberg 2017"; documents EM-residency-program growth from 117 to 276 (2001–2021), with for-profit-affiliated rising 1 → 29; for-profit affiliation predicted lower 2021–2022 PGY1 salary controlling for program characteristics)
- **Why:** Directly supports the for-profit-GME-expansion framing P3 needs in the EM specialty.

**Lassner, J. W., Ahn, J., Martin, S., McQueen, A., & Kukulski, P. (2022).** Quantifying For-Profit Outcomes in GME: A Multispecialty Analysis of Board Certifying Examination Pass Rates in For-Profit Affiliated Residency Programs. *Journal of Graduate Medical Education*, 14(4), 431–438. doi:10.4300/JGME-D-21-01097.1. PMC9380617. PMID 35991103. https://meridian.allenpress.com/jgme/article/14/4/431/484922/
- **Used in:** P3 §1.2 (multispecialty for-profit residency outcome analysis — closer venue and recent enough)
- **Why:** Verified peer-reviewed alternative for the for-profit-GME context, in P3's primary target venue (JGME).

**Round 17++ CRITICAL CORRECTION (2026-05-11)**: prior versions of these two entries were attributed to "Cohen, D. M. et al. (2022)" and "Reddy, S. R. et al. (2022)." Those author surnames were FABRICATED — both PMC IDs (PMC9348842 + PMC9380617) are actually authored by **Lassner et al. 2022** (with overlapping author lists; J. W. Lassner is the first author on both, and Paul Kukulski is the senior author on both). **All inline references to "Cohen et al. 2022" or "Reddy et al. 2022" in paper outlines must be re-attributed to "Lassner et al. 2022."** This was caught by the second-pass verification audit.

**Whitcomb, M. E. (2014).** Toward a Common Set of Standards for Graduate Medical Education. *Academic Medicine*, 89(10). [VERIFY BEFORE SUBMISSION — Round 17++ audit could not confirm this exact title/volume/issue via WebSearch. Whitcomb is a real author with multiple Acad Med pieces, and the year/venue are plausible, but I could not match the specific title. Either confirm via direct journal-website lookup, or substitute with a verifiable alternative on GME standards (e.g., Englander et al. 2013 *Acad Med* on competency taxonomy; or one of the IOM 2014 GME reports cited via Salsberg's 2014 Health Affairs Forefront commentary).]
- **Used in:** P3 §1.2

**ACGME (2025).** ACGME Accreditation Data Annual Report. https://www.acgme.org/about/publications-and-resources/annual-data-reports/
- **Used in:** P3 §1.2, §2.1

**AAMC (2024).** Medical Student Education: Debt, Costs, and Loan Repayment Fact Card. https://www.aamc.org/data-reports/students-residents/data/aamc-debt-fact-cards
- **Used in:** P3 §1.1

---

## CMS / hospital quality

**Centers for Medicare & Medicaid Services.** CMS Hospital Compare Database. https://data.cms.gov/provider-data/
- **Used in:** P3 §2.1, §2.4 (city-level CMS aggregates)

---

## Workforce / HPSA / NHSC

**Pathman, D. E. & Konrad, T. R. (multiple years).** NHSC and HPSA workforce literature. (specific citations TBD)
- **Used in:** P3 §1.2 (background)

**HRSA.** Health Professional Shortage Areas (HPSA) data. https://data.hrsa.gov/
- **Used in:** P3 §3.4 (geographic confounder)

---

## Software / tools

**Python 3.11**: programming language used throughout
**pandas 2.x**: DataFrames
**scipy.stats 1.x**: Pearson r, Welch's t
**statsmodels 0.14+**: OLS with cluster-robust SE
**sklearn.metrics**: cohen_kappa_score
**matplotlib 3.x**: figures
**Anthropic API (claude-sonnet-4-20250514)**: Claude scoring at temperature=0
**Together AI API (Llama 3.3 70B Instruct Turbo, DeepSeek V3.1)**: open-weight LLM scoring
**Custom scripts**: deposited at OSF (DOI TBD)

---

## Data deposit (for OSF Supplements)

All code and analysis-ready intermediate datasets to be deposited at OSF:
- DOI: TBD
- License: CC-BY 4.0
- Includes: scoring scripts, cleaning pipelines, statistical analysis scripts, figures

---

*This list is the master bibliography. Add to this when introducing new citations; remove from individual papers.*
