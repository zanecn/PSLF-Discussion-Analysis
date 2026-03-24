"""
pslf_search_terms.py
====================
Shared PSLF search terms used consistently across ALL data collection scripts.

Import this module in any collector to ensure term consistency:
    from pslf_search_terms import SEARCH_TERMS, PSLF_FILTER_REGEX
"""

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
PSLF_FILTER_REGEX = (
    r"pslf|public service loan forgiveness|loan forgiveness|student loan"
    r"|income driven|idr |repayment plan|qualifying payment|save plan"
    r"|repaye|paye |ibr |forgiveness|qualifying employer|buyback"
    r"|mohela|fedloan|dept of education|loan repayment"
    r"|nhsc|nurse corps"
)
