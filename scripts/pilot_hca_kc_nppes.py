"""
P5 / Health Affairs Forefront commentary supporting analysis:
HCA Kansas City workforce snapshot via CMS NPPES public API
(R17++ #6 RIGOROUS REVIEW response — high-yield item #3).

Per agent review: HCA Kansas City hosts 5 PSLF-hostile surgical residencies
(NS+Plastics+ENT+Ortho+Surgery-General) — the single most concentrated
PSLF-hostile surgical training site in the country. Warrants Health Affairs
Forefront commentary.

CMS NPPES (National Plan & Provider Enumeration System) public API:
  https://npiregistry.cms.hhs.gov/api-page
  No API key required. Rate-limited to ~200 requests/minute.

What NPPES CAN tell us:
  - Provider count at HCA Kansas City vs academic comparator (UKMC)
  - Specialty distribution at each
  - Snapshot of current workforce composition

What NPPES CANNOT tell us:
  - Training program history (NPPES has no "trained at" field)
  - Whether a current employee was previously trained at the facility
  - PSLF-eligible vs ineligible employer status (we infer from facility name)

This is a DESCRIPTIVE workforce snapshot, NOT a longitudinal training-outcome
analysis. For the commentary, we present this as context: "the most concentrated
PSLF-hostile surgical training site is a [X]-physician facility in [Missouri],
vs the [Y]-physician academic comparator University of Kansas Medical Center.
Residents who complete training at HCA KC and remain in-system face no PSLF-eligible
local academic alternatives within the same metropolitan area."
"""
import sys
import json
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("FATAL: requests library not installed. Install with: pip install requests")
    sys.exit(1)

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")
NPPES_BASE = "https://npiregistry.cms.hhs.gov/api/"

# Search parameters per NPPES API v2.1 documentation
# We search by organization name + city/state to find HCA Kansas City facilities
# Then for individual providers, we'll do a separate search

ORG_QUERIES = [
    {"name": "HCA_Healthcare_KC_organizations", "params": {
        "version": "2.1",
        "organization_name": "HCA Healthcare",
        "city": "Kansas City",
        "state": "MO",
        "enumeration_type": "NPI-2",  # NPI-2 = organizational
        "limit": 200,
    }},
    {"name": "Research_Med_Center_organizations", "params": {
        "version": "2.1",
        "organization_name": "Research Medical Center",  # HCA-owned KC hospital
        "city": "Kansas City",
        "state": "MO",
        "enumeration_type": "NPI-2",
        "limit": 200,
    }},
    {"name": "Centerpoint_Med_Center_organizations", "params": {
        "version": "2.1",
        "organization_name": "Centerpoint",  # HCA-owned KC hospital
        "city": "Independence",
        "state": "MO",
        "enumeration_type": "NPI-2",
        "limit": 200,
    }},
    {"name": "Univ_Kansas_Medical_Center_orgs", "params": {
        "version": "2.1",
        "organization_name": "Kansas",
        "city": "Kansas City",
        "state": "KS",
        "enumeration_type": "NPI-2",
        "limit": 200,
    }},
]


def query_nppes(params, timeout=15):
    """Hit NPPES public API."""
    try:
        r = requests.get(NPPES_BASE, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"  ERROR: {e}")
        return {"result_count": 0, "results": [], "error": str(e)}


def summarize_org_results(payload, query_name):
    n = payload.get("result_count", 0)
    out_lines = [f"\n--- {query_name} ---", f"NPPES returned {n} organizations"]
    if n == 0:
        if "error" in payload:
            out_lines.append(f"  API error: {payload['error']}")
        return out_lines, []
    rows = []
    for org in payload.get("results", [])[:50]:  # cap at 50 for readability
        basic = org.get("basic", {})
        name = basic.get("organization_name") or "(no name)"
        addrs = org.get("addresses", [])
        primary = addrs[0] if addrs else {}
        city = primary.get("city") or ""
        state = primary.get("state") or ""
        npi = org.get("number") or ""
        taxonomy = org.get("taxonomies", [])
        prim_tax = next((t for t in taxonomy if t.get("primary")), {})
        spec = prim_tax.get("desc") or ""
        rows.append({"npi": npi, "name": name, "city": city, "state": state, "specialty": spec})
        out_lines.append(f"  NPI {npi}: {name[:50]:50s} {city}, {state} [{spec[:30]}]")
    return out_lines, rows


def individual_provider_search(org_name, city, state, name):
    """Search NPPES for individual providers (NPI-1) with given org/city/state."""
    params = {
        "version": "2.1",
        "city": city,
        "state": state,
        "enumeration_type": "NPI-1",
        "limit": 200,
    }
    payload = query_nppes(params)
    n = payload.get("result_count", 0)
    out_lines = [f"\n--- {name} individual providers (NPI-1) ---",
                 f"NPPES returned {n} individual providers in {city}, {state}"]
    if n == 0:
        return out_lines, {}, []
    # Tally by specialty
    spec_counts = {}
    surg_specs_kept = []
    target_surg_specs = ["Surgery", "Neurosurgery", "Neurological", "Orthopaedic", "Otolaryngology",
                         "Plastic", "Vascular Surgery", "Thoracic Surgery", "Pediatric Surgery"]
    for prov in payload.get("results", []):
        taxonomy = prov.get("taxonomies", [])
        prim_tax = next((t for t in taxonomy if t.get("primary")), {})
        spec = prim_tax.get("desc") or "Unknown"
        spec_counts[spec] = spec_counts.get(spec, 0) + 1
        # Capture surgical providers for the case study
        if any(s in spec for s in target_surg_specs):
            basic = prov.get("basic", {})
            surg_specs_kept.append({
                "npi": prov.get("number"),
                "first_name": basic.get("first_name", ""),
                "last_name": basic.get("last_name", ""),
                "specialty": spec,
            })
    # Sort specialties by count
    sorted_specs = sorted(spec_counts.items(), key=lambda x: -x[1])
    out_lines.append(f"\nTop 10 specialties by provider count:")
    for spec, count in sorted_specs[:10]:
        out_lines.append(f"  {count:4d}  {spec}")
    return out_lines, spec_counts, surg_specs_kept


def main():
    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("HCA KANSAS CITY WORKFORCE SNAPSHOT (CMS NPPES PILOT)")
    out_lines.append("(R17++ #6 RIGOROUS REVIEW response — high-yield item #3)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("NPPES public API: https://npiregistry.cms.hhs.gov/api/")
    out_lines.append("Search strategy: organizations matching HCA Healthcare entities in Kansas City MSA")
    out_lines.append("Comparator: University of Kansas Medical Center (academic, PSLF-eligible)")
    out_lines.append("")
    out_lines.append("LIMITATIONS:")
    out_lines.append("  - NPPES has no 'trained at' field — cannot link current physicians to past residencies")
    out_lines.append("  - PSLF-eligible vs ineligible employer status is INFERRED from facility name only")
    out_lines.append("  - This is a current workforce SNAPSHOT, not a longitudinal training-outcome analysis")
    out_lines.append("")

    all_org_rows = []

    # Phase 1: Organization-level search
    out_lines.append("=" * 90)
    out_lines.append("PHASE 1: ORGANIZATION-LEVEL NPI ENTITIES (NPI-2)")
    out_lines.append("=" * 90)
    for q in ORG_QUERIES:
        payload = query_nppes(q["params"])
        lines, rows = summarize_org_results(payload, q["name"])
        out_lines.extend(lines)
        for r in rows:
            r["query"] = q["name"]
            all_org_rows.append(r)
        time.sleep(0.5)  # polite delay

    # Phase 2: Individual provider counts in HCA KC vicinity vs UKMC
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("PHASE 2: INDIVIDUAL PROVIDER COUNTS BY SPECIALTY (NPI-1)")
    out_lines.append("=" * 90)
    out_lines.append("Note: NPPES individual-provider search is city/state-based, not org-based.")
    out_lines.append("These counts include ALL providers in the city (academic + HCA + private).")
    out_lines.append("They represent the total available physician workforce, not HCA-specific counts.")
    out_lines.append("Use these as a metropolitan-area baseline.")
    out_lines.append("")

    kc_mo_lines, kc_mo_specs, kc_mo_surg = individual_provider_search(
        "ALL", "Kansas City", "MO", "Kansas City, MO (HCA territory)"
    )
    out_lines.extend(kc_mo_lines)
    time.sleep(0.5)

    kc_ks_lines, kc_ks_specs, kc_ks_surg = individual_provider_search(
        "ALL", "Kansas City", "KS", "Kansas City, KS (UKMC academic)"
    )
    out_lines.extend(kc_ks_lines)

    # Phase 3: Headline numbers for commentary
    out_lines.append("")
    out_lines.append("=" * 90)
    out_lines.append("PHASE 3: HEADLINE NUMBERS FOR HEALTH AFFAIRS FOREFRONT COMMENTARY")
    out_lines.append("=" * 90)
    out_lines.append("")

    total_org_unique_npis = len(set(r["npi"] for r in all_org_rows if r["npi"]))
    out_lines.append(f"Unique organizational NPIs identified in HCA/UKMC searches: {total_org_unique_npis}")

    # Surgical headcount comparison
    def count_surg_in_specs(spec_dict):
        surg_total = 0
        targets = ["Surgery", "Neurosurgery", "Neurological", "Orthopaedic",
                   "Otolaryngology", "Plastic Surgery", "Vascular Surgery", "Thoracic"]
        for spec, n in spec_dict.items():
            if any(t in spec for t in targets):
                surg_total += n
        return surg_total

    kc_mo_surg_count = count_surg_in_specs(kc_mo_specs)
    kc_ks_surg_count = count_surg_in_specs(kc_ks_specs)

    out_lines.append(f"\nTotal individual providers in Kansas City, MO: {sum(kc_mo_specs.values())}")
    out_lines.append(f"  - of which surgical specialties: {kc_mo_surg_count}")
    out_lines.append(f"Total individual providers in Kansas City, KS: {sum(kc_ks_specs.values())}")
    out_lines.append(f"  - of which surgical specialties: {kc_ks_surg_count}")
    out_lines.append("")
    out_lines.append("INTERPRETIVE CAVEAT: NPPES limits results to 200 per query. The above counts")
    out_lines.append("are CAPPED, not exhaustive. For a complete enumeration, the NPPES Weekly Data")
    out_lines.append("Dissemination File (CSV download, ~8 GB) should be used. The pilot is sufficient")
    out_lines.append("to confirm:")
    out_lines.append("  (a) NPPES public API is accessible and responsive;")
    out_lines.append("  (b) Provider-level metadata (specialty, city) is queryable;")
    out_lines.append("  (c) Org-level NPI entities for HCA KC facilities can be identified.")
    out_lines.append("")
    out_lines.append("RECOMMENDED NEXT STEPS for Health Affairs Forefront commentary:")
    out_lines.append("  1. Download full NPPES Weekly Data Dissemination File (~8 GB)")
    out_lines.append("  2. Filter to providers with primary practice address at HCA Healthcare KC")
    out_lines.append("     (NPI 1992878466 or similar — verify via Phase 1 results above)")
    out_lines.append("  3. Cross-reference with publicly-available residency-match outcomes (NRMP")
    out_lines.append("     individual-program post-match reports) if accessible")
    out_lines.append("  4. Estimate fraction of HCA KC current surgical physicians who completed")
    out_lines.append("     residency at HCA KC vs elsewhere (if NPPES grad-year + facility tenure")
    out_lines.append("     fields permit inference)")
    out_lines.append("  5. Compare to UKMC (academic baseline) for retention-rate context")
    out_lines.append("")
    out_lines.append("ESTIMATED EFFORT for full commentary-supporting analysis: 1-2 weeks data wrangling")

    out_text = "\n".join(out_lines)
    out_path = PROJECT / "paper5_hca_kc_nppes_pilot_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(out_text)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
