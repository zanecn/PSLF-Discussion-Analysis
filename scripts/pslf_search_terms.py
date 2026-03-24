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

# Regex for post-hoc filtering of scraped content to PSLF-relevant posts
# Use word boundaries (\b) instead of trailing spaces so terms match at
# end-of-string and before punctuation (audit fix: trailing-space bug).
PSLF_FILTER_REGEX = (
    r"pslf|public service loan forgiveness|loan forgiveness|student loan"
    r"|income.driven|(?<!\w)idr(?!\w)|repayment plan|qualifying payment|save plan"
    r"|repaye|(?<!\w)paye(?!\w)|(?<!\w)ibr(?!\w)|forgiveness|qualifying employer|buyback"
    r"|mohela|fedloan|dept of education|loan repayment"
    r"|nhsc|nurse corps"
)
