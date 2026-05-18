# run_post_comments_chain.ps1
# =============================
# Single-launcher orchestration script for the post-comments-finish chain.
#
# This script must be run AFTER the comments collector finishes
# (currently at 93%; output: reddit_comments_pslf.csv).
#
# Steps:
#   1) Add VADER to all comments (REQUIRED FIRST — others depend on it)
#   2) In parallel: triangulation + OP-vs-Reply + cohort heterogeneity + per-author panel
#   3) Print consolidated summary of what each script wrote
#
# Total wall-time: ~15-20 min (Step 1 sequential 5-10 min, Step 2 parallel 10 min).
# All free — no API costs.
#
# Usage:
#     cd C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis
#     powershell -ExecutionPolicy Bypass -File ..\scripts\run_post_comments_chain.ps1
#
# Or to skip Step 1 if VADER already added:
#     powershell -ExecutionPolicy Bypass -File ..\scripts\run_post_comments_chain.ps1 -SkipVader

param(
    [switch]$SkipVader = $false
)

$python = "C:\Users\zanen\anaconda3\python.exe"
$proj = "C:\Users\zanen\PSLF_2026\PSLF-Discussion-Analysis"
$scripts = "C:\Users\zanen\PSLF_2026\scripts"

Set-Location $proj

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "POST-COMMENTS-FINISH CHAIN" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Sanity check: comments file exists
if (-not (Test-Path "reddit_comments_pslf.csv")) {
    Write-Host "[ERROR] reddit_comments_pslf.csv not found. Wait for collector to finish." -ForegroundColor Red
    exit 1
}

$startTime = Get-Date
$commentsSize = (Get-Item "reddit_comments_pslf.csv").Length / 1MB
Write-Host "Comments file: reddit_comments_pslf.csv ($([math]::Round($commentsSize, 1)) MB)"
Write-Host ""

# ============================================================
# STEP 1: Add VADER to comments (REQUIRED FIRST)
# ============================================================
if (-not $SkipVader) {
    Write-Host "[STEP 1] Adding VADER to all comments..." -ForegroundColor Yellow
    Write-Host "  Script: compute_vader_on_comments.py"
    Write-Host "  Expected time: 5-10 min (CPU-only, no API)"
    Write-Host ""

    & $python "$scripts\compute_vader_on_comments.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] VADER computation failed. Aborting." -ForegroundColor Red
        exit 1
    }
    Write-Host "[STEP 1 DONE]" -ForegroundColor Green
} else {
    Write-Host "[STEP 1 SKIPPED] (VADER already on comments per --SkipVader flag)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================"
$step1Elapsed = (Get-Date) - $startTime
Write-Host "Step 1 elapsed: $([math]::Round($step1Elapsed.TotalMinutes, 1)) min"
Write-Host "============================================================"
Write-Host ""

# ============================================================
# STEP 2: Run 4 analyses in parallel
# ============================================================
Write-Host "[STEP 2] Launching 4 analyses in parallel..." -ForegroundColor Yellow
Write-Host "  2a. triangulation_with_comments.py    (Paper 1 — TB x VADER alpha at full scale)"
Write-Host "  2b. analyze_op_vs_reply.py            (Paper 1 — OP vs Reply directional mismatch)"
Write-Host "  2c. analyze_cohort_heterogeneity_comments.py  (Paper 2 — cohort heterogeneity at full scale)"
Write-Host "  2d. analyze_per_author_with_comments.py       (Paper 2 — panel feasibility check)"
Write-Host "  Expected parallel time: 10-15 min"
Write-Host ""

$step2Start = Get-Date

$jobs = @()
$jobs += Start-Job -Name "triangulation_comments" -ScriptBlock {
    Set-Location $using:proj
    & $using:python "$using:scripts\triangulation_with_comments.py" 2>&1
} | Add-Member -NotePropertyName "OutputFile" -NotePropertyValue "triangulation_comments_results.txt" -PassThru

$jobs += Start-Job -Name "op_vs_reply" -ScriptBlock {
    Set-Location $using:proj
    & $using:python "$using:scripts\analyze_op_vs_reply.py" 2>&1
} | Add-Member -NotePropertyName "OutputFile" -NotePropertyValue "op_vs_reply_results.txt" -PassThru

$jobs += Start-Job -Name "cohort_heterogeneity" -ScriptBlock {
    Set-Location $using:proj
    & $using:python "$using:scripts\analyze_cohort_heterogeneity_comments.py" 2>&1
} | Add-Member -NotePropertyName "OutputFile" -NotePropertyValue "cohort_heterogeneity_comments_results.txt" -PassThru

$jobs += Start-Job -Name "per_author_panel" -ScriptBlock {
    Set-Location $using:proj
    & $using:python "$using:scripts\analyze_per_author_with_comments.py" 2>&1
} | Add-Member -NotePropertyName "OutputFile" -NotePropertyValue "per_author_with_comments_results.txt" -PassThru

Write-Host "Jobs launched. Waiting for all 4 to complete..."
$jobs | Wait-Job | Out-Null

$step2Elapsed = (Get-Date) - $step2Start
Write-Host ""
Write-Host "Step 2 parallel elapsed: $([math]::Round($step2Elapsed.TotalMinutes, 1)) min"
Write-Host ""

# ============================================================
# Per-job status + first 30 lines of each output file
# ============================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "JOB STATUS + OUTPUT FILE SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

foreach ($job in $jobs) {
    $name = $job.Name
    $state = $job.State
    $outFile = $job.OutputFile
    Write-Host ""
    Write-Host "--- $name : $state ---" -ForegroundColor Magenta

    $jobOutput = Receive-Job -Job $job 2>&1
    $errorLines = $jobOutput | Where-Object { $_ -match "(?i)error|exception|traceback" }
    if ($errorLines) {
        Write-Host "  [WARN] Errors detected in job output:"
        $errorLines | Select-Object -First 5 | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
    }

    if (Test-Path $outFile) {
        $size = (Get-Item $outFile).Length / 1KB
        $modified = (Get-Item $outFile).LastWriteTime
        Write-Host "  Output: $outFile ($([math]::Round($size, 1)) KB; modified $modified)"
        Write-Host "  First 20 lines of output file:"
        Get-Content $outFile -TotalCount 20 | ForEach-Object { Write-Host "    $_" }
    } else {
        Write-Host "  [WARN] Expected output file not found: $outFile" -ForegroundColor Red
    }
    Remove-Job -Job $job
}

# ============================================================
# CONSOLIDATED HEADLINE NUMBERS
# ============================================================
$totalElapsed = (Get-Date) - $startTime
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CONSOLIDATED HEADLINE NUMBERS (post-comments scale)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Total wall-time: $([math]::Round($totalElapsed.TotalMinutes, 1)) min"
Write-Host ""

# Pull key numbers via grep-like patterns
function Get-MatchOrNA($file, $pattern) {
    if (Test-Path $file) {
        $line = Select-String -Path $file -Pattern $pattern -SimpleMatch:$false | Select-Object -First 1
        if ($line) { return $line.Line.Trim() }
    }
    return "(not found)"
}

Write-Host "Paper 1 (Methods, EPJ DS):"
Write-Host "  TB x VADER alpha at comments scale:"
Write-Host "    " (Get-MatchOrNA "triangulation_comments_results.txt" "alpha")
Write-Host "  OP vs Reply Delta:"
Write-Host "    " (Get-MatchOrNA "op_vs_reply_results.txt" "Delta|Delta")
Write-Host ""
Write-Host "Paper 2 (Substantive, JCSS):"
Write-Host "  Cohort heterogeneity at full scale: see cohort_heterogeneity_comments_results.txt"
Write-Host "  Per-author panel feasibility:"
Write-Host "    " (Get-MatchOrNA "per_author_with_comments_results.txt" "events meeting")
Write-Host ""
Write-Host "============================================================"
Write-Host "DONE. Review the output .txt files for full results." -ForegroundColor Green
Write-Host "Compare to current LOCKED numbers in:"
Write-Host "  - PAPER_1_LOCKED_RESULTS_2026-05-10.md"
Write-Host "  - PATH_B_STATUS_DASHBOARD.md"
Write-Host "============================================================"
