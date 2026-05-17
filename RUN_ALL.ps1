# RUN_ALL.ps1
# ============
# Regenerate every R17++ canonical result file in dependency order.
#
# Usage (PowerShell):
#   .\RUN_ALL.ps1                    # run all (~15-30 min depending on machine)
#   .\RUN_ALL.ps1 -Stage p3          # run only Paper 3 stage
#   .\RUN_ALL.ps1 -DryRun            # print commands without executing
#
# Wall-time estimates (CPU-bound, no GPU):
#   Paper 1: ~3 min (multi-LLM compare + paraphrase + OP-vs-Reply + cohort bootstrap + cluster bootstrap)
#   Paper 2: ~5 min (cohort heterogeneity + topic + per-author + holm-bonferroni + optional audits)
#   Paper 3: ~10 min (5-yr + 6-yr Model 5 + NIH + wild-cluster + trend + 2 neg-controls + two-part NIH)
#   Figures: ~2 min (7 PNGs at 300 DPI)

param(
    [ValidateSet("all","p1","p2","p3","figures")]
    [string]$Stage = "all",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = "C:\Users\zanen\PSLF_2026"
$PYTHON = "C:\Users\zanen\anaconda3\python.exe"
$SCRIPTS = "$PROJECT_ROOT\scripts"

Set-Location $PROJECT_ROOT

function Run-Script {
    param([string]$ScriptName, [string]$Description)
    Write-Host "`n>>> $Description" -ForegroundColor Cyan
    Write-Host "    Running: $ScriptName" -ForegroundColor Gray
    if ($DryRun) {
        Write-Host "    [DRY-RUN, not executed]" -ForegroundColor Yellow
        return
    }
    & $PYTHON "$SCRIPTS\$ScriptName"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    ERROR: $ScriptName exited with code $LASTEXITCODE" -ForegroundColor Red
        throw "Pipeline halted at $ScriptName"
    }
}

$startTime = Get-Date
Write-Host "=== PSLF R17++ canonical-results regeneration ===" -ForegroundColor Green
Write-Host "Stage: $Stage  |  DryRun: $DryRun  |  Started: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green

# =======================================================
# PAPER 1 (Methods, EPJ DS)
# =======================================================
if ($Stage -eq "all" -or $Stage -eq "p1") {
    Write-Host "`n--- Paper 1 (Methods, EPJ DS) ---" -ForegroundColor Magenta
    Run-Script "compare_multi_llm_with_sdn.py"          "P1: 5-instrument intersection n=1,001 (CANONICAL 3-LLM alpha)"
    Run-Script "compute_paraphrase_robustness.py"       "P1: paraphrase robustness 3-prompt alpha (n=200)"
    Run-Script "analyze_op_vs_reply.py"                 "P1: per-post t-test on OP-vs-Reply Delta"
    Run-Script "run_op_vs_reply_cluster_bootstrap.py"   "P1: PROPER cluster-bootstrap on (post, comment) pairs"
    Run-Script "run_cohort_stratified_bootstrap_p1.py"  "P1: cohort-stratified vs simple bootstrap CI comparison"
    Run-Script "compare_test_retest.py"                 "P1: temp=0 vs temp=0 determinism check"
}

# =======================================================
# PAPER 2 (Substantive, JCSS)
# =======================================================
if ($Stage -eq "all" -or $Stage -eq "p2") {
    Write-Host "`n--- Paper 2 (Substantive, JCSS) ---" -ForegroundColor Magenta
    Run-Script "pslf_intention_analysis.py"             "P2: Claude pslf_stance analysis (intention + topic + sentiment)"
    Run-Script "analyze_l5_cohort_robustness.py"        "P2: 5-spec cross-instrument cohort robustness"
    Run-Script "analyze_topic_per_cohort_per_event.py"  "P2: topic shifts per cohort x event"
    Run-Script "base_rate_adjusted_decoupling.py"       "P2: lift_pp computation"
    Run-Script "run_holm_bonferroni_p2_chi_sq.py"       "P2: Holm-Bonferroni for 5.4 chi-sq family (R17++ Agent 5 M5)"
    Run-Script "run_p2_optional_audits.py"              "P2: pooled-event + BCa + cluster SE (R17++ Agent 5 M1+M4+M6)"
}

# =======================================================
# PAPER 3 (Policy, JGME)
# =======================================================
if ($Stage -eq "all" -or $Stage -eq "p3") {
    Write-Host "`n--- Paper 3 (Policy, JGME) ---" -ForegroundColor Magenta
    Run-Script "run_model5_FINAL.py"                    "P3: 5-year baseline Model 5 (CANONICAL n=29,349)"
    Run-Script "run_model5_2021_2026_cross_sectional.py" "P3: 6-year extended sample"
    Run-Script "integrate_nih_into_model5.py"           "P3: state-filtered NIH integration"
    Run-Script "wild_cluster_bootstrap_p3.py"           "P3: Webb 6-point wild-cluster bootstrap B=2,000"
    Run-Script "run_trend_regression_p3.py"             "P3: trend regression (is_2026 + is_post_eo sensitivity)"
    Run-Script "run_negative_control_with_2026.py"      "P3: orthopedic-surgery negative control"
    Run-Script "run_dermatology_negative_control.py"    "P3: dermatology second negative control (R17++ Agent 2 M5)"
    Run-Script "run_two_part_nih_p3.py"                 "P3: two-part NIH spec (R17++ Agent 2 M2)"
    Run-Script "run_model5_with_2026_post_eo.py"        "P3: 2026 post-EO descriptive (with retraction banner)"
    Run-Script "run_model5_pre_post_eo_split.py"        "P3: pre/post EO descriptive split (with retraction banner)"
}

# =======================================================
# FIGURES
# =======================================================
if ($Stage -eq "all" -or $Stage -eq "figures") {
    Write-Host "`n--- Figures (R17++ canonical, 300 DPI) ---" -ForegroundColor Magenta
    Run-Script "generate_p1_figures.py" "P1 Figures 1+2+3 (correlation matrix + OP-vs-Reply + cohort alpha)"
    Run-Script "generate_p2_figures.py" "P2 Figures 1+2 (cohort OR forest + topic-shift heatmap)"
    Run-Script "generate_p3_figures.py" "P3 Figures 1+2 (year-by-year gap + forest plot)"
}

$endTime = Get-Date
$elapsed = $endTime - $startTime
Write-Host "`n=== Pipeline complete ===" -ForegroundColor Green
Write-Host "Elapsed: $($elapsed.TotalMinutes.ToString('F1')) minutes" -ForegroundColor Green
Write-Host "Outputs at: $PROJECT_ROOT\PSLF-Discussion-Analysis\paper*_results.txt + paper*_fig*.png" -ForegroundColor Green
Write-Host "`nNext: review outputs; then '.\RUN_AUDITS.ps1' to verify R17++ integrity." -ForegroundColor Cyan
