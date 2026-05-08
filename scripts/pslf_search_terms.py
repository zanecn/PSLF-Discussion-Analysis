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
# 2026-04 round 1 audit fixes:
#   - Match TEPSLF (Temporary Expanded PSLF) — previously missed by \bpslf\b
#   - Match past-tense "forgiven", "forgive" — previously only "forgiveness" matched
#   - Tighten "save plan" with word boundaries — previously matched "save plan B"
#   - Tighten "buyback" similarly — was matching "auto buyback" etc.
#
# 2026-04 round 2 audit fix:
#   - Generic "loan forgiveness" was over-including: matched the 2022 Biden $10K-20K
#     mass-forgiveness EO (different program), Biden v. Nebraska SCOTUS (struck down
#     mass forgiveness, not PSLF), and generic forgiveness debates.
#   - Now generic-forgiveness terms must co-occur with a PSLF-specific anchor
#     (PSLF, public service, qualifying employer/payment, MOHELA, FedLoan, NHSC,
#     teacher loan, nonprofit, residency) within ~80 chars in either direction.
PSLF_STRICT_REGEX = (
    # Tier 1 — explicit, unambiguous PSLF terms (no anchoring needed)
    r"\b(te)?pslf\b"                              # PSLF or TEPSLF
    r"|public service loan forgiv"                # explicit program name
    r"|teacher loan forgiv"                       # explicit alt program
    r"|qualifying payment|qualifying employer"    # PSLF-specific terminology
    r"|\b(pslf )?buyback\b (program|period|payment|process|backlog|eligibl)"
    r"|(pslf|loan|payment).{0,15}\bbuyback\b"
    r"|\bmohela\b|\bfedloan\b"                    # PSLF servicers
    r"|\bnhsc\b|\bnurse corps\b"                  # explicit alt programs
    # Tier 2 — IDR plans, but only when relevant to PSLF (these are also non-PSLF
    # repayment plans, so we keep them as soft signals — high recall, lower precision)
    r"|\brepaye\b|(?<!\w)ibr(?!\w)|\bpaye\b"
    r"|income.driven repayment|(?<!\w)idr(?!\w)"
    r"|(?<!\w)save plan(?=[.,!?:;)]|$|\s+(forbearance|borrowers|injunction|eligible|repayment|enrollees|currently|now))"
)

# PSLF-specific anchor terms (used to validate generic-forgiveness matches).
# A post matching ONLY generic "loan forgiveness" terms must ALSO contain one of
# these anchors within 80 chars to be classified as PSLF-relevant.
_PSLF_ANCHORS = (
    r"\bpslf\b|\btepslf\b|public service loan|qualifying employer|qualifying payment"
    r"|\bmohela\b|\bfedloan\b|\bnhsc\b|nurse corps|teacher loan forgiv"
    r"|nonprofit (employer|hospital|job|work)|government employer|federal employer"
    r"|residen(t|cy)|\battending\b"  # medical career stages (proxy for PSLF context)
)

# Generic forgiveness terms that REQUIRE a PSLF anchor nearby.
_GENERIC_FORGIVENESS = (
    r"\bloan forgiv|student loan forgiv"
    r"|loans? (were |are |been |was )?forgiv"
    r"|forgiv(e|en|ing) (my |our |the |student |federal |all )?(\w+ )?loans?"
)


def filter_pslf_relevant(series) -> "pd.Series":
    """Apply has_pslf_relevance over a pandas Series, returning a boolean mask.

    Implementation note: this is a per-row apply (NOT vectorized) because the
    anchor-window check is order-sensitive within each text. Acceptable for
    the project's corpus sizes (<50K rows); a fully vectorized rewrite would
    use str.contains for the strict path and only fall back to apply for the
    generic-with-anchor path.

    Use as drop-in replacement for:
        df["text"].str.lower().str.contains(PSLF_STRICT_REGEX, na=False)
    """
    import re as _re
    pattern = _re.compile(PSLF_STRICT_REGEX)
    generic = _re.compile(_GENERIC_FORGIVENESS)
    anchors = _re.compile(_PSLF_ANCHORS)

    def _check(text):
        if not isinstance(text, str) or not text:
            return False
        t = text.lower()
        if pattern.search(t):
            return True
        for m in generic.finditer(t):
            start, end = max(0, m.start() - 80), min(len(t), m.end() + 80)
            if anchors.search(t[start:end]):
                return True
        return False

    return series.fillna("").apply(_check)


def has_pslf_relevance(text: str) -> bool:
    """True if text matches PSLF_STRICT_REGEX OR has generic-forgiveness terms
    co-occurring with a PSLF anchor within 80 characters.

    Two-stage filter (round 2 audit fix):
      1. If text matches the strict regex (Tier 1 + Tier 2), return True.
      2. If text only matches generic forgiveness, require an anchor within 80 chars.

    This rejects mass-forgiveness-only posts (Biden EO, SCOTUS) while keeping
    PSLF-specific forgiveness discussions.
    """
    import re as _re
    if not text:
        return False
    t = text.lower()
    if _re.search(PSLF_STRICT_REGEX, t):
        return True
    # Fall back: generic forgiveness ONLY if a PSLF anchor is nearby
    for m in _re.finditer(_GENERIC_FORGIVENESS, t):
        start, end = max(0, m.start() - 80), min(len(t), m.end() + 80)
        window = t[start:end]
        if _re.search(_PSLF_ANCHORS, window):
            return True
    return False
