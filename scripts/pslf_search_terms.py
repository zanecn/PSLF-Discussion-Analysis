"""
pslf_search_terms.py
====================
Shared PSLF search terms, filter regex, and constants used consistently
across ALL data collection and analysis scripts.

Import this module in any collector to ensure consistency:
    from pslf_search_terms import SEARCH_TERMS, PSLF_FILTER_REGEX, USER_AGENT, BODY_MAX_LEN
"""

# Shared constants
USER_AGENT = "PSLF-Analysis/2.0 (academic research, github.com/zanecn/PSLF-Discussion-Analysis)"
BODY_MAX_LEN = 10000  # max characters to store per post body

# Full search terms — used for forum/site search queries
SEARCH_TERMS = [
    # Core PSLF
    "PSLF",
    "Public Service Loan Forgiveness",
    "loan forgiveness residency",
    "student loan forgiveness",
    "qualifying employer",
    "buyback PSLF",
    # Repayment plans
    "SAVE plan",
    "SAVE injunction",
    "income driven repayment",
    "REPAYE",
    "IBR loan",
    # Policy (2024-2026)
    "OBBBA student loans",
    "one big beautiful bill loans",
    "loan forgiveness executive order",
    # Medical-specific
    "loan forgiveness specialty",
    "PSLF residency",
    "residency loan repayment",
    "student debt specialty choice",
    "nonprofit hospital loan",
    "NHSC loan repayment",
    # Nursing-specific
    "loan forgiveness nursing",
    "loan repayment nurse",
    "NURSE Corps",
    # Social work / law / federal
    "loan forgiveness social worker",
    "loan forgiveness public defender",
    "federal employee loan forgiveness",
    # Servicers
    "MOHELA PSLF",
    "FedLoan PSLF",
]

# Simplified terms for platforms with basic search (Reddit, Nitter)
SEARCH_TERMS_SIMPLE = [
    "PSLF",
    "Public Service Loan Forgiveness",
    "loan forgiveness",
    "student loan forgiveness",
    "SAVE plan student loans",
    "income driven repayment",
    "qualifying employer",
    "MOHELA",
    "FedLoan",
    "NHSC loan repayment",
    "NURSE Corps loan",
]

# BROAD filter: used for initial scraping (cast a wide net)
PSLF_FILTER_REGEX = (
    r"pslf|public service loan forgiveness|loan forgiveness|student loan"
    r"|income.driven|(?<!\w)idr(?!\w)|repayment plan|qualifying payment|save plan"
    r"|repaye|(?<!\w)paye(?!\w)|(?<!\w)ibr(?!\w)|forgiveness|qualifying employer|buyback"
    r"|mohela|fedloan|dept of education|loan repayment"
    r"|nhsc|nurse corps"
)

# STRICT filter: used for analysis — requires explicit PSLF/forgiveness-program terms.
# Excludes generic "student loan" / "loan repayment" which capture off-topic posts.
# (Audit finding: nursing had only 6.1% explicit PSLF mentions with broad filter.)
#
# 2026-04 audit fixes:
#   - Match TEPSLF (Temporary Expanded PSLF) — previously missed by \bpslf\b
#   - Match past-tense "forgiven", "forgive" — previously only "forgiveness" matched
#   - Tighten "save plan" with word boundaries — previously matched "save plan B"
#   - Tighten "buyback" similarly — was matching "auto buyback" etc.
PSLF_STRICT_REGEX = (
    r"\b(te)?pslf\b"                              # PSLF or TEPSLF
    r"|public service loan forgiv"                # forgive / forgiveness / forgiven
    r"|loan forgiv|student loan forgiv"
    r"|teacher loan forgiv"
    # Past tense "loans were forgiven" / "forgive my loans" — anchor near 'loan'
    r"|loans? (were |are |been |was )?forgiv"
    r"|forgiv(e|en|ing) (my |our |the |student |federal |all )?(\w+ )?loans?"
    r"|income.driven repayment|(?<!\w)idr(?!\w)"
    # SAVE plan: anchor with policy/loan keywords to avoid "save plan B"
    r"|(?<!\w)save plan(?=[.,!?:;)]|$|\s+(forbearance|borrowers|injunction|eligible|repayment|enrollees|currently|now))"
    r"|\brepaye\b|(?<!\w)ibr(?!\w)|\bpaye\b"
    r"|qualifying payment|qualifying employer"
    # Buyback: anchor with PSLF/loan/payment context to avoid auto/stock buyback
    r"|\b(pslf )?buyback\b (program|period|payment|process|backlog|eligibl)"
    r"|(pslf|loan|payment).{0,15}\bbuyback\b"
    r"|\bmohela\b|\bfedloan\b"
    r"|\bnhsc\b|\bnurse corps\b"
)
