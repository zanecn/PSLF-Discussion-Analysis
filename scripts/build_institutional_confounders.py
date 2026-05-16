"""
build_institutional_confounders.py
===================================
Build per-institution confounders from data we ALREADY HAVE for Paper 3.

Inputs:
  - nrmp_program_level_2021_2025.csv (NRMP data with program counts)
  - nrmp_institution_pslf_verified.csv (ProPublica IRS verification)
  - propublica_lookup_cache.json (full ProPublica metadata including NTEE codes)
  - cms_hospital_general.csv (CMS Hospital Compare)

Outputs:
  - institutional_confounders.csv with columns:
      institution, state, city, n_programs, n_specialties,
      pslf_class_propublica, ntee_code, ntee_top_level,
      university_affiliation, academic_med_center,
      n_residents_total (sum of quotas across years/specialties),
      cms_avg_star_rating

Usage:
    python build_institutional_confounders.py
"""

import json
import re
from pathlib import Path

import pandas as pd

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")


def get_ntee_top_level(ntee: str) -> str:
    """NTEE top level: B (Education), E (Health), F (Mental Health), G (Disease/Disorders)."""
    if not isinstance(ntee, str) or not ntee:
        return ""
    return ntee[0].upper()


def classify_university_affiliation(institution_name: str, ntee_code: str,
                                     propublica_subname: str) -> bool:
    """Heuristic for university affiliation flag.

    True if any of:
    - Institution name contains explicit university markers
    - Institution name matches known university-affiliated abbreviations
    - NTEE code starts with 'B' (education sector)
    - ProPublica subname contains university markers
    """
    name_lc = str(institution_name).lower()
    sub_lc = str(propublica_subname).lower()
    # Explicit name markers
    name_markers = [
        "university", "univ", "college of med", "school of med", "school of grad med",
        "school of grad. med", "medical college", "coll med", "college med",
        "college of phys", "academic med", "school of medicine",
        "grad med educ", "graduate med", "med school", "medical school",
        "icahn school", "weill cornell", "geisel school", "lewis katz",
        "perelman", "feinberg",
    ]
    if any(m in name_lc or m in sub_lc for m in name_markers):
        return True
    # NTEE B = Education sector
    if str(ntee_code).startswith("B"):
        return True
    # Specific abbreviation prefixes for university hospital systems
    abbrev_markers = [
        "upmc",        # Univ Pittsburgh Medical Center
        "uc davis", "uc san diego", "uc san francisco", "uc irvine",
        "ucsd", "ucsf", "ucla", "uchicago",
        "ismms",       # Icahn School of Medicine at Mount Sinai
        "msk ",        # Memorial Sloan Kettering
        "nyu ",        # NYU
        "chop",        # Children's Hospital Philadelphia
        "uw med",      # University of Washington Medicine
        "uw medicine",
        "usc ",        # University of Southern California
        "vcu ",        # Virginia Commonwealth University
        "vumc",        # Vanderbilt Medical Center
        "duke univ",
        "tufts",
        "case western",
        "case wstrn",
        "ohsu",        # Oregon Health & Science University
        "thomas jefferson", "jefferson",
        "loma linda",
        "uci ",        # UC Irvine
        "ut southwestern", "ut health",
        "wfubmc",      # Wake Forest Univ Baptist
        "wfu",
        "louisiana state",
        "lsu",
        "drexel",
        "rutgers",
        "boston univ", "bu ",
        "georgetown",
        "yale",
        "harvard",
        "columbia",
        "stanford",
        "emory",
        "vanderbilt",
        "northwestern",
        "cornell",
        "penn med", "u penn",
        "univ of",
        "michigan med",
        "u mich",
        "wash u", "wustl",
        "barnes-jewish",
        "u tex", "ut ",
        "u ark", "u ariz", "u colo", "u conn", "u del", "u fla",
        "u georgia", "u hawaii", "u idaho", "u ill", "u iowa", "u kan",
        "u ky", "u md", "u mass", "u minn", "u miss", "u mo",
        "u neb", "u nev", "u nh", "u nm", "u nc", "u nd", "u oh", "u okla",
        "u ore", "u pa", "u ri", "u sc", "u sd", "u tenn", "u tx", "u ut",
        "u va", "u vt", "u wa", "u wash", "u wisc", "u wyo",
    ]
    for ab in abbrev_markers:
        if name_lc.startswith(ab) or f" {ab}" in name_lc or f"/{ab}" in name_lc:
            return True
    return False


def classify_academic_med_center(institution_name: str, ntee_code: str,
                                   n_specialties: int) -> bool:
    """Heuristic for academic medical center status.

    True if both:
    - University-affiliated (per above) OR has 8+ specialty programs
    - Not a small standalone hospital
    """
    name_lc = str(institution_name).lower()
    # Major academic medical center markers
    if any(m in name_lc for m in ["mayo clinic", "johns hopkins", "cleveland clinic",
                                    "mass general", "mount sinai", "brigham", "cedars-sinai",
                                    "stanford", "ucsf", "uchicago", "yale-new haven",
                                    "duke univ", "nyu", "penn med", "northwestern mem",
                                    "vanderbilt", "emory univ", "ucla", "uc san diego",
                                    "memorial sloan", "cleveland clinic", "barnes-jewish",
                                    "rush univ", "chop", "boston childrens"]):
        return True
    if n_specialties >= 8 and (str(ntee_code).startswith("B") or
                                "university" in name_lc or
                                "academic" in name_lc):
        return True
    return False


def main():
    # Load NRMP program data — sums per institution
    nrmp = pd.read_csv(PROJECT / "nrmp_program_level_2021_2025.csv")
    print(f"NRMP rows loaded: {len(nrmp):,}")

    # Per-institution aggregates (over the 5 years 2021-2025)
    inst_agg = nrmp.groupby("institution").agg(
        state=("state", "first"),
        city=("city", "first"),
        n_program_rows=("program_code", "count"),
        n_unique_programs=("program_code", "nunique"),
        n_specialties=("specialty", "nunique"),
        total_quota_5y=("quota", "sum"),
        total_filled_5y=("filled", "sum"),
        avg_fill_rate=("fill_rate", "mean"),
    ).reset_index()
    print(f"Unique institutions in NRMP: {len(inst_agg):,}")

    # Approximate annual residents = total_quota / 5 years (PGY-1 only)
    inst_agg["annual_residents_pgy1"] = inst_agg["total_quota_5y"] / 5.0

    # Load ProPublica IRS verification
    pslf_v = pd.read_csv(PROJECT / "nrmp_institution_pslf_verified.csv")
    print(f"ProPublica verified rows: {len(pslf_v):,}")

    # Load ProPublica cache for NTEE codes
    with open(PROJECT / "propublica_lookup_cache.json") as f:
        pp_cache = json.load(f)

    # Build a per-institution NTEE code lookup
    # The cache key is a normalized institution name; the value is a list of matches
    # We use the top-scored match (first item)
    ntee_lookup = {}
    sub_name_lookup = {}
    for inst_key, matches in pp_cache.items():
        if matches and isinstance(matches, list) and len(matches) > 0:
            top = matches[0]
            ntee_lookup[inst_key] = top.get("ntee_code", "") or ""
            sub_name_lookup[inst_key] = top.get("sub_name", "") or top.get("name", "") or ""

    # Match ProPublica cache keys (which are partial names) back to NRMP institutions
    # We'll do best-substring match
    def get_propublica_meta(nrmp_inst: str) -> tuple[str, str]:
        """Return (ntee_code, sub_name) for the best ProPublica cache match."""
        nrmp_lc = nrmp_inst.lower()
        best = (None, 0)
        for cache_key in ntee_lookup:
            ck_lc = cache_key.lower()
            if ck_lc in nrmp_lc or nrmp_lc.startswith(ck_lc):
                # Score by length of shared prefix / cache_key
                score = len(ck_lc) if ck_lc in nrmp_lc else 0
                if score > best[1]:
                    best = (cache_key, score)
        if best[0]:
            return ntee_lookup[best[0]], sub_name_lookup[best[0]]
        return "", ""

    print("Building per-institution metadata...")
    rows = []
    for _, r in inst_agg.iterrows():
        inst = r["institution"]
        ntee, sub = get_propublica_meta(inst)
        ntee_top = get_ntee_top_level(ntee)
        univ_aff = classify_university_affiliation(inst, ntee, sub)
        amc = classify_academic_med_center(inst, ntee, r["n_specialties"])
        rows.append({
            "institution": inst,
            "state": r["state"],
            "city": r["city"],
            "n_unique_programs": r["n_unique_programs"],
            "n_specialties": r["n_specialties"],
            "total_quota_5y": r["total_quota_5y"],
            "annual_residents_pgy1": r["annual_residents_pgy1"],
            "avg_fill_rate": r["avg_fill_rate"],
            "ntee_code": ntee,
            "ntee_top_level": ntee_top,
            "propublica_sub_name": sub,
            "university_affiliation": univ_aff,
            "academic_med_center": amc,
        })

    # Merge in PSLF class.
    # FIX (Round 15 Audit): pslf_v has duplicate rows for institutions that appear
    # in NRMP under the same name across multiple states or campuses (e.g.,
    # 'Mayo Clinic School of Grad Med Educ' appears 3x in pslf_v for Mayo's
    # Rochester / Arizona / Florida campuses). These duplicates cascaded into
    # the merge and silently 3x-inflated downstream Model 5 sample. Dedup before merge.
    out = pd.DataFrame(rows)
    pslf_v_min = pslf_v[["institution", "pslf_class", "subsec_code"]].copy()
    pslf_v_min_n_before = len(pslf_v_min)
    pslf_v_min = pslf_v_min.drop_duplicates(subset="institution", keep="first")
    n_dropped = pslf_v_min_n_before - len(pslf_v_min)
    if n_dropped > 0:
        print(f"  [dedup] Dropped {n_dropped} duplicate institution rows from pslf_v before merge")
    out = out.merge(pslf_v_min, on="institution", how="left")
    out.rename(columns={"pslf_class": "pslf_class_propublica"}, inplace=True)

    # Final sanity dedup (catches any other stray duplicates from intermediate steps)
    n_before = len(out)
    out = out.drop_duplicates(subset="institution", keep="first").reset_index(drop=True)
    if n_before != len(out):
        print(f"  [final dedup] Dropped {n_before - len(out)} duplicate institution rows from output")

    # Save
    out_path = PROJECT / "institutional_confounders.csv"
    out.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    print(f"  Rows: {len(out)}")
    print(f"  Unique institutions: {out['institution'].nunique()}")
    assert len(out) == out["institution"].nunique(), "ERROR: duplicates remain in output"

    # Summary
    print(f"\n{'='*60}")
    print("CONFOUNDER SUMMARY")
    print('='*60)
    print(f"\nUniversity affiliation flag:")
    print(out["university_affiliation"].value_counts())
    print(f"\nAcademic medical center flag:")
    print(out["academic_med_center"].value_counts())
    print(f"\nNTEE top level distribution:")
    print(out["ntee_top_level"].value_counts())
    print(f"\nPSLF class (from ProPublica):")
    print(out["pslf_class_propublica"].value_counts())
    print(f"\nUniversity-affiliated × academic-medical-center crosstab:")
    print(pd.crosstab(out["university_affiliation"], out["academic_med_center"]))

    # Cross-tab with PSLF class
    print(f"\nUniversity affiliation by PSLF class:")
    ct = pd.crosstab(out["pslf_class_propublica"], out["university_affiliation"], margins=True)
    print(ct)


if __name__ == "__main__":
    main()
