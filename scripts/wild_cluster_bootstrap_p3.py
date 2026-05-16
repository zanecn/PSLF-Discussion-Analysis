"""
wild_cluster_bootstrap_p3.py
=============================
Wild-cluster bootstrap p-values for Paper 3 Model 5 (Round 16 strengthener).

Cameron, Gelbach, & Miller (2008, REStat) and Cameron & Miller (2015, JHR)
recommend wild-cluster bootstrap when the number of clusters is small (<30).
Our Paper 3 has 23 hostile clusters in S1 and 9 in S2/S3 — well below the
asymptotic-cluster-robust threshold.

Implementation: Webb (6-point) wild bootstrap weights, B=2,000.

For each specification (S1, S2, S3):
  1. Fit the original Model 5 regression with cluster-robust SE
  2. Generate B wild-bootstrap residuals (cluster-level weights from {-1, +1})
  3. Re-fit the model on bootstrap residuals; record t-statistic for PSLF-hostile
  4. p-value = 2 × min(P(t* < t_obs), P(t* > t_obs))

Output: paper3_wild_cluster_bootstrap_results.txt
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT = Path("C:/Users/zanen/PSLF_2026/PSLF-Discussion-Analysis")

HCA_ACADEMIC_PARTNERSHIPS = [
    "HCA Healthcare/USF Morsani GME-Blake",
    "HCA Healthcare/USF Morsani GME-Brandon",
    "HCA Healthcare/USF Morsani GME-Citrus",
    "HCA Healthcare/USF Morsani GME-Largo",
    "HCA Healthcare/USF Morsani GME-Oak Hill",
    "HCA Healthcare/USF Morsani GME-Sarasota",
    "HCA Healthcare/USF Morsani GME-St Pete",
    "HCA Healthcare/USF Morsani GME-Trinity",
    "HCA Healthcare/USF Morsani-Bayonet Pt",
    "HCA Healthcare/USF Morsani-Northside",
    "HCA Florida JFK Hosp-U Miami",
    "HCA Healthcare/JFK Med Center-UMiami",
    "HCA Houston Healthcare/U Houston",
    "HCA Healthcare LGH-Montgomery/VCOM",
]


def load_and_merge():
    nrmp = pd.read_csv(PROJECT / "nrmp_program_level_2021_2025.csv")
    confounders = pd.read_csv(PROJECT / "institutional_confounders.csv")
    cms = pd.read_csv(PROJECT / "cms_hospital_general.csv")

    cms = cms.rename(columns={"Hospital Ownership": "ownership", "City/Town": "city",
                                "State": "state", "Hospital overall rating": "star",
                                "Hospital Type": "hospital_type"})
    cms["star_num"] = pd.to_numeric(cms["star"], errors="coerce")
    cms["is_for_profit"] = (cms["ownership"] == "Proprietary").astype(int)
    cms_city = cms.groupby(["city", "state"]).agg(
        cms_mean_star=("star_num", "mean"),
        cms_for_profit_share=("is_for_profit", "mean"),
        cms_n_hospitals=("Facility ID", "count"),
    ).reset_index()
    cms_city["city_norm"] = cms_city["city"].str.strip().str.upper()
    cms_city["state_norm"] = cms_city["state"].str.strip().str.upper()
    # Round 17 fix: dedup case-collision duplicates (e.g., "Boston" vs "BOSTON")
    cms_city = cms_city.drop_duplicates(subset=["city_norm", "state_norm"], keep="first")
    nrmp["city_norm"] = nrmp["city"].fillna("").str.strip().str.upper()
    nrmp["state_norm"] = nrmp["state"].fillna("").str.strip().str.upper()

    df = nrmp.merge(
        cms_city[["city_norm", "state_norm", "cms_mean_star",
                   "cms_for_profit_share", "cms_n_hospitals"]],
        on=["city_norm", "state_norm"], how="left",
    )
    df = df.merge(
        confounders[["institution", "n_unique_programs", "n_specialties",
                      "annual_residents_pgy1", "university_affiliation",
                      "academic_med_center"]],
        on="institution", how="left",
    )

    nih_path = PROJECT / "nih_reporter_FY2023_state.csv"
    if nih_path.exists():
        nih = pd.read_csv(nih_path)
        nih_inst = nih.groupby("institution").agg(
            nih_total_award=("total_award_amount", "sum"),
        ).reset_index()
        df = df.merge(nih_inst, on="institution", how="left")
        df["nih_total_award"] = df["nih_total_award"].fillna(0)
    else:
        df["nih_total_award"] = 0
    df["log_nih_funding"] = np.log1p(df["nih_total_award"])
    df["log_residents"] = np.log1p(df["annual_residents_pgy1"].fillna(0))
    return df.dropna(subset=["fill_rate", "pslf_class"]).copy()


def wild_cluster_bootstrap(df, formula, target_coef, n_boot=2000, seed=42):
    """
    Webb (2014) 6-point wild-cluster bootstrap.

    Returns:
        - point_t: original t-statistic
        - boot_t: bootstrap distribution of t* (under null that target_coef=0)
        - p_value: 2 × min tail probability
    """
    import statsmodels.formula.api as smf
    from patsy import dmatrices

    rng = np.random.default_rng(seed)

    # Drop rows with NA in any regression variable
    needed = ["fill_rate", "pslf_class", "cms_mean_star", "cms_for_profit_share",
              "university_affiliation", "academic_med_center", "n_specialties",
              "log_residents", "log_nih_funding", "state", "specialty", "institution"]
    d = df.dropna(subset=needed).copy().reset_index(drop=True)

    # Fit original model with cluster-robust SE
    cluster_groups = d["institution"].astype("category").cat.codes.values
    full_model = smf.ols(formula, data=d).fit(
        cov_type="cluster", cov_kwds={"groups": cluster_groups})

    # Original t-statistic for target coefficient
    if target_coef not in full_model.params.index:
        return None
    point_t = full_model.tvalues[target_coef]
    point_beta = full_model.params[target_coef]

    # ====== Wild-cluster bootstrap under null ======
    # Restricted model: fit WITHOUT the target coefficient (i.e., impose H0: β_target = 0)
    # Then add back the target coefficient's contribution as if it were zero
    # Get residuals under the restricted model

    # Build the design matrix manually to extract restricted residuals
    y, X_full = dmatrices(formula, data=d, return_type="dataframe")
    y_arr = y.values.flatten()

    if target_coef not in X_full.columns:
        return None
    target_idx = list(X_full.columns).index(target_coef)

    # Restricted X (drop target column)
    X_restricted = X_full.drop(columns=[target_coef])
    beta_restricted, residuals_restricted, _, _ = np.linalg.lstsq(
        X_restricted.values, y_arr, rcond=None)
    y_hat_restricted = X_restricted.values @ beta_restricted
    e_restricted = y_arr - y_hat_restricted  # residuals under H0

    # Webb 6-point weights
    webb_values = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])

    # Bootstrap loop
    unique_clusters = np.unique(cluster_groups)
    n_clusters = len(unique_clusters)
    cluster_to_idx = {c: np.where(cluster_groups == c)[0] for c in unique_clusters}

    boot_t = []
    fail_count = 0
    for b in range(n_boot):
        # Sample one weight per cluster
        cluster_weights = rng.choice(webb_values, size=n_clusters)
        # Apply weights to residuals
        weights_per_obs = np.zeros(len(d))
        for i, c in enumerate(unique_clusters):
            weights_per_obs[cluster_to_idx[c]] = cluster_weights[i]

        # Generate bootstrap y: y* = X_restricted @ beta_restricted + w * e_restricted
        y_boot = y_hat_restricted + weights_per_obs * e_restricted

        # Re-fit FULL model with bootstrap y, get t-stat for target coef
        try:
            beta_boot, _, _, _ = np.linalg.lstsq(X_full.values, y_boot, rcond=None)
            y_hat_boot = X_full.values @ beta_boot
            resid_boot = y_boot - y_hat_boot

            # Compute cluster-robust SE for the target coefficient under bootstrap
            # Using the meat estimator: sum_c (X_c' resid_c)(X_c' resid_c)'
            X_arr = X_full.values
            XtX_inv = np.linalg.inv(X_arr.T @ X_arr)
            meat = np.zeros((X_arr.shape[1], X_arr.shape[1]))
            for c in unique_clusters:
                idx_c = cluster_to_idx[c]
                X_c = X_arr[idx_c]
                e_c = resid_boot[idx_c]
                Xe_c = X_c.T @ e_c
                meat += np.outer(Xe_c, Xe_c)
            vcov = XtX_inv @ meat @ XtX_inv
            # Small-cluster correction (G/(G-1) * (n-1)/(n-k))
            G = n_clusters
            n_obs = len(d)
            k = X_arr.shape[1]
            adj = (G / (G - 1)) * ((n_obs - 1) / (n_obs - k))
            vcov *= adj
            se_target = np.sqrt(vcov[target_idx, target_idx])

            # t-statistic
            t_boot = beta_boot[target_idx] / se_target
            boot_t.append(t_boot)
        except Exception:
            fail_count += 1

    boot_t = np.array(boot_t)
    if len(boot_t) < 100:
        print(f"    WARN: only {len(boot_t)} successful bootstraps (fail={fail_count})")
        return {"point_t": point_t, "point_beta": point_beta, "boot_t": boot_t,
                "p_value": np.nan, "n_boot_success": len(boot_t)}

    # Two-sided p-value
    p_value = 2 * min((boot_t >= abs(point_t)).mean(), (boot_t <= -abs(point_t)).mean())
    p_value = min(p_value, 1.0)

    return {
        "point_t": point_t, "point_beta": point_beta, "boot_t": boot_t,
        "p_value": p_value, "n_boot_success": len(boot_t),
    }


def main():
    df_base = load_and_merge()
    print(f"Loaded analytical dataset: n={len(df_base):,}")

    formula = ("fill_rate ~ C(pslf_class, Treatment(reference='ambiguous'))"
               " + cms_mean_star + cms_for_profit_share"
               " + C(university_affiliation) + C(academic_med_center)"
               " + n_specialties + log_residents + log_nih_funding"
               " + C(state) + C(specialty)")

    target_coef = "C(pslf_class, Treatment(reference='ambiguous'))[T.pslf_hostile]"

    out_lines = []
    out_lines.append("=" * 90)
    out_lines.append("PAPER 3 WILD-CLUSTER BOOTSTRAP P-VALUES (Round 16 strengthener)")
    out_lines.append("=" * 90)
    out_lines.append("")
    out_lines.append("Method: Webb (2014) 6-point wild bootstrap; B=2,000")
    out_lines.append("Reference: Cameron, Gelbach & Miller (2008) REStat; Cameron & Miller (2015) JHR")
    out_lines.append("Recommended for cluster-robust inference when n_clusters < 30")
    out_lines.append("")

    for spec_name, df_modify in [
        ("S1: Status quo (all 23 hostile)", lambda d: d),
        ("S2: HCA-academic reclassified as ambiguous", lambda d: d.assign(
            pslf_class=d["pslf_class"].where(
                ~d["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS), "ambiguous"))),
        ("S3: Drop HCA-academic partnerships", lambda d: d[
            ~d["institution"].isin(HCA_ACADEMIC_PARTNERSHIPS)]),
    ]:
        df = df_modify(df_base.copy())
        df["pslf_class"] = df["pslf_class"].astype("category")
        df["pslf_class"] = df["pslf_class"].cat.set_categories(
            ["ambiguous", "pslf_friendly", "pslf_hostile"], ordered=False)
        n_clusters = df["institution"].nunique()
        n_h_inst = df[df["pslf_class"] == "pslf_hostile"]["institution"].nunique()
        print(f"\n[{spec_name}] n={len(df):,}, n_clusters={n_clusters}, n_hostile_inst={n_h_inst}")
        print(f"  Running wild-cluster bootstrap (B=2,000) — this takes ~1-2 min...")

        result = wild_cluster_bootstrap(df, formula, target_coef, n_boot=2000)
        if result is None:
            out_lines.append(f"  [{spec_name}] FAILED")
            continue
        out_lines.append(f"")
        out_lines.append(f"{spec_name}")
        out_lines.append(f"  n_clusters: {n_clusters}, n_hostile_inst: {n_h_inst}")
        out_lines.append(f"  Point β (PSLF-hostile): {result['point_beta']*100:+.2f} pp")
        out_lines.append(f"  Cluster-robust t-statistic: {result['point_t']:+.3f}")
        out_lines.append(f"  Wild-cluster bootstrap p-value (B={result['n_boot_success']}): {result['p_value']:.4e}")
        print(f"  β={result['point_beta']*100:+.2f} pp | t={result['point_t']:+.3f} | wild-cluster p={result['p_value']:.4e}")

    out_lines.append("")
    out_lines.append("INTERPRETATION:")
    out_lines.append("-" * 90)
    out_lines.append("")
    out_lines.append("The Cameron-Miller (2015) recommendation for n_clusters < 30 is to confirm")
    out_lines.append("cluster-robust asymptotic p-values with wild-cluster bootstrap. If wild-cluster")
    out_lines.append("p-values agree with the asymptotic p-values from cluster-robust SE, the")
    out_lines.append("inference is robust to the small-cluster concern.")
    out_lines.append("")
    out_lines.append("For Paper 3:")
    out_lines.append("  - S1 has 23 hostile clusters → small-sample correction matters")
    out_lines.append("  - S2/S3 have 9 hostile clusters → small-sample correction matters MORE")
    out_lines.append("")
    out_lines.append("If wild-cluster bootstrap p-values are similar to cluster-robust p-values,")
    out_lines.append("the headline survives the small-cluster concern. If wild-cluster p-values are")
    out_lines.append("substantially larger, the cluster-robust SE was overstating precision.")

    out_text = "\n".join(out_lines)
    print()
    print(out_text)
    out_path = PROJECT / "paper3_wild_cluster_bootstrap_results.txt"
    out_path.write_text(out_text, encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
