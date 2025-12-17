# Master Backup Test Runner
# Comprehensive testing and execution with full logging

$ErrorActionPreference = 'Continue'
$script:MasterLog = Join-Path $PSScriptRoot "MASTER-BACKUP-TEST-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-MasterLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry -ForegroundColor $(switch($Level){"ERROR"{"Red"}"SUCCESS"{"Green"}"WARN"{"Yellow"}"INFO"{"Cyan"}default{"White"}})
    $logEntry | Out-File -FilePath $script:MasterLog -Append -Encoding UTF8
}

Write-MasterLog "========================================" "INFO"
Write-MasterLog "MASTER BACKUP TEST RUNNER" "INFO"
Write-MasterLog "Start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
Write-MasterLog "Log file: $script:MasterLog" "INFO"
Write-MasterLog "========================================" "INFO"
Write-MasterLog ""

# Step 1: Backup current version
Write-MasterLog "STEP 1: Backing up current version..." "INFO"
try {
    & "$PSScriptRoot\backup-current-version.ps1" *>&1 | Out-File -FilePath "$PSScriptRoot\backup-version-output.log" -Append -Encoding UTF8
    Write-MasterLog "  Current version backed up" "SUCCESS"
} catch {
    Write-MasterLog "  Failed to backup current version: $_" "ERROR"
}

# Step 2: Run component tests
Write-MasterLog ""
Write-MasterLog "STEP 2: Running component tests..." "INFO"
try {
    & "$PSScriptRoot\test-backup-comprehensive.ps1" *>&1 | Out-File -FilePath "$PSScriptRoot\component-tests-output.log" -Append -Encoding UTF8
    Write-MasterLog "  Component tests completed" "INFO"
} catch {
    Write-MasterLog "  Component tests failed: $_" "WARN"
}

# Step 3: Run the actual backup script
Write-MasterLog ""
Write-MasterLog "STEP 3: Running backup script..." "INFO"
$backupStart = Get-Date
$backupOutputFile = "$PSScriptRoot\backup-run-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

try {
    Write-MasterLog "  Executing: .\scripts\backup-repo.ps1 -Verbose" "INFO"
    cd (Split-Path $PSScriptRoot -Parent)
    $backupOutput = & ".\scripts\backup-repo.ps1" -Verbose *>&1 | Tee-Object -FilePath $backupOutputFile
    $backupDuration = (Get-Date) - $backupStart
    Write-MasterLog "  Backup script executed in $([math]::Round($backupDuration.TotalSeconds, 1)) seconds" "INFO"
    
    # Check for errors in output
    $errors = $backupOutput | Where-Object { $_ -match "ERROR|FAILED|Exception" }
    if ($errors) {
        Write-MasterLog "  Warnings/Errors found: $($errors.Count)" "WARN"
        $errors | Select-Object -First 5 | ForEach-Object {
            Write-MasterLog "    $_" "WARN"
        }
    }
} catch {
    Write-MasterLog "  Backup script exception: $_" "ERROR"
    Write-MasterLog "  Stack: $($_.ScriptStackTrace)" "ERROR"
}

# Step 4: Verify backup files
Write-MasterLog ""
Write-MasterLog "STEP 4: Verifying backup files..." "INFO"
$backupFound = $false
$repoName = (Get-Item (Split-Path $PSScriptRoot -Parent)).Name

$targets = @(
    @{ Name = "Desktop"; Path = Join-Path (Join-Path ([Environment]::GetFolderPath("Desktop")) "repo backup") $repoName },
    @{ Name = "N: Drive"; Path = "N:\backup\dev\repo-backups\$repoName" },
    @{ Name = "OneDrive"; Path = Join-Path $env:OneDrive "repo backup\$repoName" }
)

foreach ($target in $targets) {
    Write-MasterLog "  Checking $($target.Name)..." "INFO"
    if ($target.Path -and (Test-Path (Split-Path $target.Path -Parent) -ErrorAction SilentlyContinue)) {
        if (Test-Path $target.Path -ErrorAction SilentlyContinue) {
            $zips = Get-ChildItem -Path $target.Path -Filter "*.zip" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
            if ($zips) {
                $latest = $zips | Select-Object -First 1
                $age = (Get-Date) - $latest.LastWriteTime
                
                Write-MasterLog "    ✓ Backup found: $($latest.Name)" "SUCCESS"
                Write-MasterLog "      Size: $([math]::Round($latest.Length/1MB, 2)) MB" "INFO"
                Write-MasterLog "      Created: $($latest.LastWriteTime)" "INFO"
                Write-MasterLog "      Age: $([math]::Round($age.TotalMinutes, 1)) minutes" "INFO"
                
                if ($age.TotalMinutes -lt 10) {
                    Write-MasterLog "      ✓ Recently created!" "SUCCESS"
                    $backupFound = $true
                } else {
                    Write-MasterLog "      ⚠ May be old backup" "WARN"
                }
            } else {
                Write-MasterLog "    ✗ No ZIP files found" "WARN"
            }
        } else {
            Write-MasterLog "    ✗ Directory does not exist" "WARN"
        }
    } else {
        Write-MasterLog "    ✗ Target not accessible" "WARN"
    }
}

# Step 5: Summary
Write-MasterLog ""
Write-MasterLog "========================================" "INFO"
Write-MasterLog "FINAL SUMMARY" "INFO"
Write-MasterLog "========================================" "INFO"

if ($backupFound) {
    Write-MasterLog "RESULT: ✓ BACKUP SUCCESSFUL" "SUCCESS"
    Write-MasterLog "  Backup files were created successfully" "SUCCESS"
} else {
    Write-MasterLog "RESULT: ✗ BACKUP FAILED" "ERROR"
    Write-MasterLog "  No backup files were created or found" "ERROR"
    Write-MasterLog ""
    Write-MasterLog "  Next steps:" "INFO"
    Write-MasterLog "  1. Check log file: $backupOutputFile" "INFO"
    Write-MasterLog "  2. Review errors above" "INFO"
    Write-MasterLog "  3. Consider reverting to Nov 29 version" "INFO"
}

Write-MasterLog ""
Write-MasterLog "Master log file: $script:MasterLog" "INFO"
Write-MasterLog "End: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
Write-MasterLog "========================================" "INFO"

exit $(if ($backupFound) { 0 } else { 1 })
