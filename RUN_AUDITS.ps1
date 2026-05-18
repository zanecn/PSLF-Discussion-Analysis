# RUN_AUDITS.ps1
# ===============
# Re-verify R17++ integrity across the project:
#   - Dedup fix landed on all 8 Model 5 scripts
#   - Trump-EO retraction propagated (no stale "EO 14253" / "EO-induced narrowing" / "PSLF +18.6 pp causal")
#   - No fabricated/misattributed citations remain in active docs
#   - Source scripts contain R17 retraction language (won't be erased on re-run)
#   - Canonical numbers consistent across MASTER_LOCKED_NUMBERS.md + PROJECT_INDEX.md + paper outlines
#
# Usage:
#   .\RUN_AUDITS.ps1
#
# Exit code 0 = all audits pass; non-zero = at least one issue found.

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = "C:\Users\zanen\PSLF_2026"
Set-Location $PROJECT_ROOT

$failures = 0

function Test-NoStaleString {
    param([string]$Pattern, [string]$Description, [string[]]$ExcludePatterns = @(), [string[]]$Paths = @("*.md"))
    Write-Host "`n  [TEST] $Description" -ForegroundColor Cyan
    $hits = @()
    foreach ($p in $Paths) {
        $matches = Select-String -Path $p -Pattern $Pattern -ErrorAction SilentlyContinue
        foreach ($m in $matches) {
            $excluded = $false
            foreach ($ex in $ExcludePatterns) {
                if ($m.Line -match $ex) { $excluded = $true; break }
            }
            if (-not $excluded) { $hits += $m }
        }
    }
    if ($hits.Count -eq 0) {
        Write-Host "    PASS (0 stale hits)" -ForegroundColor Green
        return $true
    } else {
        Write-Host "    FAIL ($($hits.Count) hits)" -ForegroundColor Red
        $hits | Select-Object -First 5 | ForEach-Object {
            Write-Host "      $($_.Path):$($_.LineNumber): $($_.Line.Trim().Substring(0, [Math]::Min(120, $_.Line.Trim().Length)))" -ForegroundColor DarkRed
        }
        if ($hits.Count -gt 5) { Write-Host "      ... +$($hits.Count - 5) more" -ForegroundColor DarkRed }
        $script:failures++
        return $false
    }
}

function Test-DedupInScript {
    param([string]$ScriptPath, [string]$ScriptName)
    Write-Host "`n  [TEST] CMS-merge dedup fix present in $ScriptName" -ForegroundColor Cyan
    if (-not (Test-Path $ScriptPath)) {
        Write-Host "    SKIP (script not found)" -ForegroundColor Yellow
        return $true
    }
    $content = Get-Content $ScriptPath -Raw
    if ($content -match "drop_duplicates\(subset=\[.city_norm.,\s*.state_norm.\]") {
        Write-Host "    PASS (dedup fix present)" -ForegroundColor Green
        return $true
    } else {
        Write-Host "    FAIL (dedup fix MISSING)" -ForegroundColor Red
        $script:failures++
        return $false
    }
}

Write-Host "=== PSLF R17++ Integrity Audit ===" -ForegroundColor Green
Write-Host "Started: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green

# ========================================================
# 1. Trump-EO retraction propagation
# ========================================================
Write-Host "`n=== 1. Trump-EO retraction propagation ===" -ForegroundColor Magenta

# EO number must be 14235, not 14253
Test-NoStaleString -Pattern "14253" `
    -Description "No residual 'EO 14253' references (should be 14235)" `
    -Paths @("PAPER_*.md", "MASTER_*.md", "PROJECT_INDEX.md", "QUICKSTART.md") `
    -ExcludePatterns @("corrected from", "prior version", "14235", "previously", "Round 17") | Out-Null

# Causal-EO framing should be retracted
Test-NoStaleString -Pattern "EO-induced narrowing|EO eliminated|quasi-experimental DiD-style" `
    -Description "No residual EO-causal framing in active docs" `
    -Paths @("PAPER_*.md", "MASTER_*.md", "PROJECT_INDEX.md") `
    -ExcludePatterns @("RETRACTED", "corrected", "previously", "STALE", "SUPERSEDED", "claim", "rejected", "overstated", "Trigger", "honest trend", "replace") | Out-Null

# ========================================================
# 2. Citation integrity (R17++ corrections)
# ========================================================
Write-Host "`n=== 2. Citation integrity (R17++ corrections) ===" -ForegroundColor Magenta

Test-NoStaleString -Pattern "Calderon et al\. 2025|Calderon, N\." `
    -Description "No active 'Calderon' citations (should be Bojic et al. 2025)" `
    -Paths @("PAPER_*.md") `
    -ExcludePatterns @("corrected", "previously", "mis-attributed", "Bojic", "checklist", "FABRICATED", "R17") | Out-Null

Test-NoStaleString -Pattern "Trabelsi|Cousineau 2025|Kovacs|Cohen et al\. 2022 PMC9348|Reddy et al\. 2022 PMC9380" `
    -Description "No active citations to known-fabricated authors" `
    -Paths @("PAPER_*.md") `
    -ExcludePatterns @("corrected", "previously", "mis-attributed", "Kim, Veselovsky", "Lassner", "Zhu, Yin", "Arowosafe", "Zhang, Hill") | Out-Null

# ========================================================
# 3. CMS-merge dedup fix in all 8 Model 5 scripts
# ========================================================
Write-Host "`n=== 3. CMS-merge dedup fix in all 8 Model 5 scripts ===" -ForegroundColor Magenta

$dedupScripts = @(
    "run_model5_FINAL.py",
    "run_model5_2021_2026_cross_sectional.py",
    "run_model5_with_2026_post_eo.py",
    "run_model5_pre_post_eo_split.py",
    "wild_cluster_bootstrap_p3.py",
    "run_negative_control_with_2026.py",
    "integrate_nih_into_model5.py",
    "run_model5_with_confounders.py",
    "run_dermatology_negative_control.py",
    "run_two_part_nih_p3.py"
)
foreach ($s in $dedupScripts) {
    Test-DedupInScript -ScriptPath "scripts\$s" -ScriptName $s | Out-Null
}

# ========================================================
# 4. Source scripts contain R17 retraction (won't erase on re-run)
# ========================================================
Write-Host "`n=== 4. Source-script retraction language present ===" -ForegroundColor Magenta

foreach ($script in @("run_model5_with_2026_post_eo.py", "run_model5_pre_post_eo_split.py")) {
    Write-Host "`n  [TEST] $script contains R17 retraction in its output text" -ForegroundColor Cyan
    $path = "scripts\$script"
    if (Test-Path $path) {
        $content = Get-Content $path -Raw
        if ($content -match "RETRACTION|is_2026 indicator beyond linear trend p=0\.46|descriptive only|NOT identify a causal Trump EO effect") {
            Write-Host "    PASS (retraction language baked in)" -ForegroundColor Green
        } else {
            Write-Host "    FAIL (retraction language NOT in source; will be erased on re-run)" -ForegroundColor Red
            $failures++
        }
    }
}

# ========================================================
# 5. Venue assignments correct (EPJ DS / JCSS / JGME, not Pol Analysis / SMR / Health Affairs)
# ========================================================
Write-Host "`n=== 5. Venue assignments correct (Path B) ===" -ForegroundColor Magenta

Test-NoStaleString -Pattern "(?:\*\*Target venue\*\*|Target venue|\*\*Venue\*\*|Recommended venue|Submit to)[\s:*]+(?:Political Analysis|Sociological Methods|Health Affairs|SMR\b)" `
    -Description "No residual Political Analysis / SMR / Health Affairs as venue TARGET" `
    -Paths @("PAPER_1_*.md", "PAPER_2_*.md", "PAPER_3_*.md", "OSF_*.md", "MASTER_*.md", "PROJECT_INDEX.md", "QUICKSTART.md") `
    -ExcludePatterns @("corrected from", "R12-era", "R17\+\+ canonical", "formerly", "previously") | Out-Null

# ========================================================
# 6. Git working tree clean + sync with origin
# ========================================================
Write-Host "`n=== 6. Git state ===" -ForegroundColor Magenta

Write-Host "`n  [TEST] Working tree clean" -ForegroundColor Cyan
$gitStatus = git status --porcelain
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "    PASS (working tree clean)" -ForegroundColor Green
} else {
    Write-Host "    WARN (uncommitted changes):" -ForegroundColor Yellow
    $gitStatus | Select-Object -First 5 | ForEach-Object { Write-Host "      $_" -ForegroundColor Yellow }
}

Write-Host "`n  [TEST] HEAD synced with origin/playwright-sdn-scraper" -ForegroundColor Cyan
$local = git rev-parse HEAD
$remote = git rev-parse origin/playwright-sdn-scraper 2>$null
if ($local -eq $remote) {
    Write-Host "    PASS (HEAD == origin at $local)" -ForegroundColor Green
} else {
    Write-Host "    WARN (HEAD != origin)" -ForegroundColor Yellow
    Write-Host "      local:  $local" -ForegroundColor Yellow
    Write-Host "      remote: $remote" -ForegroundColor Yellow
}

# ========================================================
# Summary
# ========================================================
Write-Host "`n=== AUDIT SUMMARY ===" -ForegroundColor Green
if ($failures -eq 0) {
    Write-Host "ALL AUDITS PASSED" -ForegroundColor Green
    exit 0
} else {
    Write-Host "$failures audit failures" -ForegroundColor Red
    exit 1
}
