# Run backup script with comprehensive logging and error capture

$ErrorActionPreference = 'Continue'

$script:LogFile = Join-Path $PSScriptRoot "backup-execution-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$script:ErrorLog = Join-Path $PSScriptRoot "backup-errors-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

function Write-ExecutionLog {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $logEntry = "[$timestamp] [$Level] $Message"

    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        default { "White" }
    }

    Write-Host $logEntry -ForegroundColor $color
    $logEntry | Out-File -FilePath $script:LogFile -Append -Encoding UTF8

    if ($Level -eq "ERROR") {
        $logEntry | Out-File -FilePath $script:ErrorLog -Append -Encoding UTF8
    }
}

Write-ExecutionLog "=== BACKUP SCRIPT EXECUTION WITH LOGGING ===" "INFO"
Write-ExecutionLog "Start time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"
Write-ExecutionLog "Log file: $script:LogFile" "INFO"
Write-ExecutionLog "Error log: $script:ErrorLog" "INFO"
Write-ExecutionLog ""

# Check pre-conditions
Write-ExecutionLog "Checking pre-conditions..." "INFO"

$scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
if (-not (Test-Path $scriptPath)) {
    Write-ExecutionLog "ERROR: Backup script not found at $scriptPath" "ERROR"
    exit 1
}
Write-ExecutionLog "  âœ“ Backup script found: $scriptPath" "SUCCESS"

# Check .NET assemblies
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
    Add-Type -AssemblyName System.Security.Cryptography -ErrorAction Stop
    Write-ExecutionLog "  âœ“ .NET assemblies loaded" "SUCCESS"
}
catch {
    Write-ExecutionLog "  âœ- Failed to load .NET assemblies: $_" "ERROR"
    exit 1
}

# Check backup targets
$desktop = [Environment]::GetFolderPath("Desktop")
$repoName = (Get-Item .).Name

$targets = @(
    @{ Path = Join-Path (Join-Path $desktop "repo backup") $repoName; Name = "Desktop" },
    @{ Path = "N:\backup\dev\repo-backups\$repoName"; Name = "N: Drive" },
    @{ Path = Join-Path $env:OneDrive "repo backup\$repoName"; Name = "OneDrive" }
)

Write-ExecutionLog "Checking backup targets..." "INFO"
$accessible = 0
foreach ($target in $targets) {
    if ($target.Path) {
        $parentDir = Split-Path $target.Path -Parent
        if (Test-Path $parentDir -ErrorAction SilentlyContinue) {
            Write-ExecutionLog "  âœ“ $($target.Name): Accessible" "SUCCESS"
            $accessible++
        } else {
            Write-ExecutionLog "  âœ- $($target.Name): Not accessible ($parentDir)" "WARN"
        }
    }
}
Write-ExecutionLog "  Accessible targets: $accessible of $($targets.Count)" "INFO"
Write-ExecutionLog ""

# Run the backup script
Write-ExecutionLog "=== EXECUTING BACKUP SCRIPT ===" "INFO"
Write-ExecutionLog ""

$backupStart = Get-Date
$outputLines = @()
$errorLines = @()
$exitCode = 0

try {
    # Capture all output
    $job = Start-Job -ScriptBlock {
        param($ScriptPath)
        Set-Location (Split-Path $ScriptPath -Parent | Split-Path -Parent)
        & $ScriptPath *>&1
    } -ArgumentList $scriptPath

    $timeout = 600 # 10 minutes
    $completed = Wait-Job $job -Timeout $timeout

    if (-not $completed) {
        Write-ExecutionLog "ERROR: Backup script timed out after $timeout seconds" "ERROR"
        Stop-Job $job
        Remove-Job $job
        exit 1
    }

    $output = Receive-Job $job
    Remove-Job $job

    foreach ($line in $output) {
        $outputLines += $line
        Write-ExecutionLog "$line" "INFO"

        if ($line -match "ERROR|FAILED|Exception") {
            $errorLines += $line
        }
    }

    $backupDuration = (Get-Date) - $backupStart
    Write-ExecutionLog ""
    Write-ExecutionLog "Backup execution completed in $([math]::Round($backupDuration.TotalSeconds, 1)) seconds" "INFO"

    if ($errorLines.Count -gt 0) {
        Write-ExecutionLog "  Warnings/Errors captured: $($errorLines.Count)" "WARN"
    }
}
catch {
    Write-ExecutionLog "EXCEPTION during backup execution: $_" "ERROR"
    Write-ExecutionLog "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    $exitCode = 1
}

Write-ExecutionLog ""
Write-ExecutionLog "=== VERIFYING BACKUP FILES ===" "INFO"
Write-ExecutionLog ""

$backupFound = $false
foreach ($target in $targets) {
    if ($target.Path -and (Test-Path (Split-Path $target.Path -Parent) -ErrorAction SilentlyContinue)) {
        Write-ExecutionLog "Checking $($target.Name)..." "INFO"

        if (Test-Path $target.Path -ErrorAction SilentlyContinue) {
            $zips = Get-ChildItem -Path $target.Path -Filter "*.zip" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

            if ($zips) {
                $latest = $zips | Select-Object -First 1
                $backupFound = $true

                Write-ExecutionLog "  âœ“ Backup found: $($latest.Name)" "SUCCESS"
                Write-ExecutionLog "    Size: $([math]::Round($latest.Length/1MB, 2)) MB" "INFO"
                Write-ExecutionLog "    Date: $($latest.LastWriteTime)" "INFO"

                # Check if created in last 5 minutes
                $ageMinutes = ((Get-Date) - $latest.LastWriteTime).TotalMinutes
                if ($ageMinutes -lt 5) {
                    Write-ExecutionLog "    âœ“ Created recently ($([math]::Round($ageMinutes, 1)) minutes ago)" "SUCCESS"
                } else {
                    Write-ExecutionLog "    âš  Created $([math]::Round($ageMinutes, 1)) minutes ago (may be old)" "WARN"
                }
            } else {
                Write-ExecutionLog "  âœ- No ZIP files found" "WARN"
            }
        } else {
            Write-ExecutionLog "  âœ- Backup directory does not exist" "WARN"
        }
        Write-ExecutionLog ""
    }
}

Write-ExecutionLog ""
Write-ExecutionLog "=== SUMMARY ===" "INFO"
if ($backupFound) {
    Write-ExecutionLog "âœ“ BACKUP SUCCESSFUL - Files created" "SUCCESS"
} else {
    Write-ExecutionLog "âœ- BACKUP FAILED - No files created" "ERROR"
    Write-ExecutionLog "Check error log: $script:ErrorLog" "ERROR"
    $exitCode = 1
}

Write-ExecutionLog "Execution log: $script:LogFile" "INFO"
Write-ExecutionLog "End time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "INFO"

exit $exitCode
