"""
verify_nrmp_pslf_eligibility.py
================================
L1: Verify NRMP institution PSLF eligibility against IRS 501(c)(3) status
via ProPublica Nonprofit Explorer API.

Method:
  1. For each unique NRMP institution name, search ProPublica IRS Business Master
     File (BMF) for the closest 501(c)(3) match
  2. Classify based on:
     - subseccd=3 (501c3 public charity) -> PSLF-eligible
     - subseccd=4 (501c4 social welfare) -> probably NOT PSLF-eligible
     - subseccd=7 (state instrumentality) -> PSLF-eligible (government)
     - For-profit known names (HCA, Tenet, Universal Health Services) -> NOT eligible
     - No match found -> ambiguous

Caveat: The "sponsoring institution" in NRMP may differ from the legal employer
of record for residents. For HCA-with-university programs, residents may be
employed by the academic GME consortium (501c3) or by HCA (for-profit). This
script approximates by looking up the strongest 501c3 match for the institution
name; for institutions like "HCA Florida JFK Hosp-U Miami", we additionally
look up "U Miami" and assign PSLF-eligible if the academic affiliate is 501c3.

Output: nrmp_institution_pslf_verified.csv (revised classification per institution)
"""
from __future__ import annotations
import csv, io, json, os, re, sys, time
import urllib.request, urllib.parse
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

OUT_CSV = "nrmp_institution_pslf_verified.csv"
CACHE_FILE = "propublica_lookup_cache.json"

# Known for-profit / non-PSLF-eligible operating chains
FOR_PROFIT_CHAINS = [
    "HCA Healthcare", "HCA Inc", "Tenet Healthcare", "Community Health Systems",
    "Universal Health Services", "LifePoint Health", "Steward Health Care",
    "Encompass Health", "Ardent Health Services", "Surgery Partners",
    "RegionalCare", "ScionHealth", "Prime Healthcare",
]
FOR_PROFIT_KEYWORDS = ["HCA ", "HCA-", "HCA/", "Tenet", "LifePoint", "Universal Health Services",
                        "Steward", "Encompass", "Ardent Health", "Prime Healthcare"]

# Known PSLF-friendly markers (federal / military / VA / Indian Health)
GOV_KEYWORDS = ["VA Med", "VA Hosp", "Veterans", "Walter Reed", "Naval Med",
                 "Naval Hosp", "Army Med", "Air Force", "Bethesda", "Tripler",
                 "Madigan", "Wilford Hall", "Indian Health"]


def cache_load():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f: return json.load(f)
        except Exception: return {}
    return {}


def cache_save(c):
    with open(CACHE_FILE, "w") as f: json.dump(c, f)


def propublica_search(query: str, cache: dict, max_results: int = 5) -> list[dict]:
    """Search ProPublica Nonprofit Explorer. Returns list of org dicts."""
    if query in cache: return cache[query]
    url = ("https://projects.propublica.org/nonprofits/api/v2/search.json?q="
           + urllib.parse.quote_plus(query))
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "research-pslf-eligibility-verification (academic)"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        orgs = data.get("organizations", [])[:max_results]
        cache[query] = orgs
        return orgs
    except Exception as e:
        print(f"    ProPublica error '{query}': {str(e)[:120]}")
        cache[query] = []
        return []


def normalize_for_search(name: str) -> str:
    """Strip common suffixes/markers to improve match."""
    n = name
    # Remove state suffix already gone
    # Remove "-XXXXX City" etc.
    n = re.sub(r"\s+(GME|Healthcare|Health Care|Health System|Hospitals?|Hosp|"
                r"Med Ctr|Medical Center|Med Center)\b", " ", n, flags=re.IGNORECASE)
    # Common abbreviations to expand
    n = re.sub(r"\bU ", "University ", n)
    n = re.sub(r"\bUniv ", "University ", n)
    n = re.sub(r"\bSOM\b", "School of Medicine", n)
    n = re.sub(r"\bGen\b", "General", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def is_for_profit_name(name: str) -> bool:
    return any(kw.lower() in name.lower() for kw in FOR_PROFIT_KEYWORDS)


def classify(name: str, cache: dict) -> dict:
    """Returns dict: {pslf_class, evidence, ein, propublica_match, subsec, ...}"""
    out = {"institution": name,
            "pslf_class": "unknown",
            "evidence": "",
            "ein": "",
            "propublica_match": "",
            "subsec_code": None,
            "ntee_code": ""}

    # Government markers (always PSLF-eligible)
    for kw in GOV_KEYWORDS:
        if kw.lower() in name.lower():
            out["pslf_class"] = "pslf_eligible_gov"
            out["evidence"] = f"keyword: {kw}"
            return out

    # For-profit chains: lookup parent first
    is_fp = is_for_profit_name(name)

    # Strategy 1: try direct lookup (will hit if name is a 501c3 itself)
    norm = normalize_for_search(name)
    orgs = propublica_search(norm, cache)

    # Find strongest 501c3 match — name match score
    best = None
    for o in orgs:
        if o.get("subseccd") == 3:  # 501c3 public charity
            best = o
            break
    if best is None and orgs:
        # No 501c3, but found something
        best = orgs[0]

    # Strategy 2: for HCA/etc with university partner in name, lookup the partner
    academic_partner = ""
    if is_fp:
        # Extract university name from "HCA-Foo/UMiami" patterns
        m = re.search(r"[/\-]?(USF Morsani|U[\s-]?Miami|UMiami|U Houston|"
                       r"U[\s-]?Texas|VCOM|U[\s-]?Florida|Vanderbilt|"
                       r"University[^/]+)$", name)
        if m:
            academic_partner = m.group(1).strip()
            partner_orgs = propublica_search(academic_partner, cache)
            for o in partner_orgs:
                if o.get("subseccd") == 3 and "university" in o.get("name", "").lower():
                    # Found 501c3 university partner
                    out["pslf_class"] = "pslf_eligible_via_academic_partner"
                    out["evidence"] = f"academic partner: {academic_partner} -> {o.get('name')}"
                    out["ein"] = o.get("ein", "")
                    out["propublica_match"] = o.get("name", "")[:80]
                    out["subsec_code"] = o.get("subseccd")
                    out["ntee_code"] = o.get("ntee_code", "")
                    return out

        # Pure for-profit (no academic partner)
        out["pslf_class"] = "pslf_ineligible_for_profit"
        out["evidence"] = f"for-profit chain: matches {[k for k in FOR_PROFIT_KEYWORDS if k.lower() in name.lower()]}"
        return out

    # Non-FP institution: classify by ProPublica result
    if best is not None:
        out["ein"] = best.get("ein", "")
        out["propublica_match"] = best.get("name", "")[:80]
        out["subsec_code"] = best.get("subseccd")
        out["ntee_code"] = best.get("ntee_code", "")
        if best.get("subseccd") == 3:
            out["pslf_class"] = "pslf_eligible_501c3"
            out["evidence"] = f"ProPublica match: {best.get('name')[:60]} (501c3)"
        elif best.get("subseccd") == 7:
            out["pslf_class"] = "pslf_eligible_gov"
            out["evidence"] = f"ProPublica: state instrumentality"
        else:
            out["pslf_class"] = "pslf_unclear_other_subsec"
            out["evidence"] = f"ProPublica: subsec={best.get('subseccd')}"
    else:
        out["pslf_class"] = "no_propublica_match"
        out["evidence"] = "no ProPublica result"

    return out


def main():
    print("=" * 80)
    print("L1: Verify NRMP institutions against IRS BMF (ProPublica)")
    print("=" * 80)

    if not os.path.exists("nrmp_institution_pslf_classification.csv"):
        print("[ABORT] Run collect_nrmp_program_level.py first")
        sys.exit(1)

    inst_df = pd.read_csv("nrmp_institution_pslf_classification.csv")
    print(f"\nUnique institutions to verify: {len(inst_df):,}")

    cache = cache_load()
    print(f"Cache hits available: {len(cache):,}")

    results = []
    for i, row in enumerate(inst_df.itertuples()):
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(inst_df)}] processed; cache size {len(cache)}")
            cache_save(cache)
        try:
            r = classify(row.institution, cache)
            r["state"] = row.state
            r["original_class"] = row.pslf_class
            results.append(r)
        except Exception as e:
            print(f"    ERROR on {row.institution}: {e}")
        if i % 5 == 0:
            time.sleep(0.3)  # be polite to ProPublica

    cache_save(cache)
    out = pd.DataFrame(results)
    out.to_csv(OUT_CSV, index=False)
    print(f"\nSaved: {OUT_CSV}")

    print("\n" + "=" * 80)
    print("VERIFIED CLASSIFICATION DISTRIBUTION")
    print("=" * 80)
    print(out["pslf_class"].value_counts().to_string())

    print("\n" + "=" * 80)
    print("ORIGINAL vs VERIFIED — confusion matrix")
    print("=" * 80)
    crosstab = pd.crosstab(out["original_class"], out["pslf_class"])
    print(crosstab.to_string())

    # Specifically: how many "pslf_hostile" orig become eligible after verification?
    print("\n" + "=" * 80)
    print("KEY: Original 'pslf_hostile' reclassification")
    print("=" * 80)
    orig_hostile = out[out["original_class"] == "pslf_hostile"]
    for cls, sub in orig_hostile.groupby("pslf_class"):
        print(f"\n  -> {cls} ({len(sub)} institutions):")
        for _, r in sub.iterrows():
            print(f"      {r['institution']:<55s} {r['evidence'][:80]}")


if __name__ == "__main__":
    main()
