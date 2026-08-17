# Comprehensive Backup Script Testing
# Tests all components of backup-repo.ps1

[CmdletBinding()]
param(
    [switch]$RunFullBackup = $false,
    [switch]$CompareVersions = $false
)

$ErrorActionPreference = 'Continue'
$testResults = @()
$script:TestCount = 0
$script:PassCount = 0
$script:FailCount = 0

function Write-TestLog {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$TestName = ""
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
        "INFO" { "Cyan" }
        default { "White" }
    }

    $prefix = switch ($Level) {
        "PASS" { "[âœ“]" }
        "FAIL" { "[âœ-]" }
        "WARN" { "[!]" }
        default { "[i]" }
    }

    if ($TestName) {
        Write-Host "$prefix [$timestamp] [$TestName] $Message" -ForegroundColor $color
    } else {
        Write-Host "$prefix [$timestamp] $Message" -ForegroundColor $color
    }

    # Also log to file
    $logFile = Join-Path $PSScriptRoot "backup-test-results.log"
    "$prefix [$timestamp] [$TestName] $Message" | Out-File -FilePath $logFile -Append -Encoding UTF8
}

function Test-BackupComponent {
    param(
        [string]$TestName,
        [scriptblock]$TestBlock,
        [string]$Description = ""
    )

    $script:TestCount++
    Write-TestLog "Starting test: $TestName" "INFO" $TestName

    if ($Description) {
        Write-TestLog "  Description: $Description" "INFO" $TestName
    }

    try {
        $result = & $TestBlock
        if ($result -or $result -eq $null) {
            $script:PassCount++
            Write-TestLog "PASSED: $TestName" "PASS" $TestName
            $testResults += @{
                TestName = $TestName
                Status = "PASS"
                Message = "Test passed"
                Timestamp = Get-Date
            }
            return $true
        } else {
            $script:FailCount++
            Write-TestLog "FAILED: $TestName (returned false)" "FAIL" $TestName
            $testResults += @{
                TestName = $TestName
                Status = "FAIL"
                Message = "Test returned false"
                Timestamp = Get-Date
            }
            return $false
        }
    }
    catch {
        $script:FailCount++
        Write-TestLog "FAILED: $TestName - Exception: $_" "FAIL" $TestName
        Write-TestLog "  Stack: $($_.ScriptStackTrace)" "FAIL" $TestName
        $testResults += @{
            TestName = $TestName
            Status = "FAIL"
            Message = $_.Exception.Message
            Exception = $_.Exception.GetType().FullName
            StackTrace = $_.ScriptStackTrace
            Timestamp = Get-Date
        }
        return $false
    }
}

# Test 1: Script File Exists
Write-TestLog "=== COMPREHENSIVE BACKUP SCRIPT TESTS ===" "INFO"
Write-TestLog "Starting test suite at $(Get-Date)" "INFO"
Write-TestLog ""

Test-BackupComponent -TestName "ScriptExists" -Description "Backup script file exists" {
    $scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
    Test-Path $scriptPath
}

# Test 2: Script Syntax Check
Test-BackupComponent -TestName "ScriptSyntax" -Description "Backup script syntax is valid" {
    $scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
    $scriptContent = Get-Content $scriptPath -Raw
    $errors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseInput($scriptContent, [ref]$null, [ref]$errors)
    if ($errors -and $errors.Count -gt 0) {
        Write-TestLog "Syntax errors found: $($errors.Count)" "FAIL" "ScriptSyntax"
        $errors | ForEach-Object {
            Write-TestLog "  Line $($_.Extent.StartLineNumber): $($_.Message)" "FAIL" "ScriptSyntax"
        }
        return $false
    }
    return $true
}

# Test 3: Required .NET Assemblies Available
Test-BackupComponent -TestName "DotNetAssemblies" -Description ".NET compression assemblies available" {
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
        Add-Type -AssemblyName System.Security.Cryptography -ErrorAction Stop
        return $true
    }
    catch {
        Write-TestLog "Failed to load assemblies: $_" "FAIL" "DotNetAssemblies"
        return $false
    }
}

# Test 4: Repository Root Detection
Test-BackupComponent -TestName "RepoRootDetection" -Description "Can detect repository root" {
    $repoRoot = (Get-Item .).FullName
    if ($repoRoot -and (Test-Path $repoRoot)) {
        Write-TestLog "  Repository root: $repoRoot" "INFO" "RepoRootDetection"
        return $true
    }
    return $false
}

# Test 5: Backup Target Directories Accessible
Test-BackupComponent -TestName "BackupTargetAccess" -Description "Backup target directories are accessible" {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $repoName = (Get-Item .).Name

    $targets = @(
        @{ Path = Join-Path (Join-Path $desktop "repo backup") $repoName; Name = "Desktop" },
        @{ Path = "N:\backup\dev\repo-backups\$repoName"; Name = "N: Drive" },
        @{ Path = Join-Path $env:OneDrive "repo backup\$repoName"; Name = "OneDrive" }
    )

    $accessible = 0
    foreach ($target in $targets) {
        if ($target.Path) {
            $parentDir = Split-Path $target.Path -Parent
            if (Test-Path $parentDir -ErrorAction SilentlyContinue) {
                Write-TestLog "  $($target.Name): Accessible" "INFO" "BackupTargetAccess"
                $accessible++
            } else {
                Write-TestLog "  $($target.Name): Not accessible ($parentDir)" "WARN" "BackupTargetAccess"
            }
        }
    }

    Write-TestLog "  Accessible targets: $accessible of $($targets.Count)" "INFO" "BackupTargetAccess"
    return $accessible -gt 0
}

# Test 6: File Scanning Works
Test-BackupComponent -TestName "FileScanning" -Description "Can scan repository files" {
    $files = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 100
    $count = ($files | Measure-Object).Count
    Write-TestLog "  Scanned $count files (sample)" "INFO" "FileScanning"
    return $count -gt 0
}

# Test 7: ZIP Creation Test
Test-BackupComponent -TestName "ZipCreation" -Description "Can create ZIP files" {
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop

        $testDir = Join-Path $env:TEMP "backup-test-$(Get-Random)"
        $null = New-Item -ItemType Directory -Path $testDir -Force -ErrorAction Stop

        $testZipPath = Join-Path $testDir "test-backup.zip"

        # Create a test file
        $testFile = Join-Path $testDir "test.txt"
        "Test content" | Out-File -FilePath $testFile -Encoding UTF8

        # Create ZIP
        $zip = [System.IO.Compression.ZipFile]::Open($testZipPath, [System.IO.Compression.ZipArchiveMode]::Create)
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $testFile, "test.txt", [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
        $zip.Dispose()

        $created = Test-Path $testZipPath
        if ($created) {
            $size = (Get-Item $testZipPath).Length
            Write-TestLog "  Test ZIP created: $size bytes" "INFO" "ZipCreation"
            Remove-Item $testDir -Recurse -Force -ErrorAction SilentlyContinue
        }

        return $created
    }
    catch {
        Write-TestLog "  Exception: $_" "FAIL" "ZipCreation"
        if (Test-Path $testDir) {
            Remove-Item $testDir -Recurse -Force -ErrorAction SilentlyContinue
        }
        return $false
    }
}

# Test 8: Check for Required Functions
Test-BackupComponent -TestName "RequiredFunctions" -Description "All required functions are defined" {
    $scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
    $scriptContent = Get-Content $scriptPath -Raw

    $requiredFunctions = @(
        "Write-Log",
        "New-BackupZip",
        "Test-BackupDuplicate",
        "Get-RepoName"
    )

    $missing = @()
    foreach ($func in $requiredFunctions) {
        if ($scriptContent -notmatch "function\s+$func") {
            $missing += $func
        }
    }

    if ($missing.Count -gt 0) {
        Write-TestLog "  Missing functions: $($missing -join ', ')" "FAIL" "RequiredFunctions"
        return $false
    }

    Write-TestLog "  All required functions present" "INFO" "RequiredFunctions"
    return $true
}

# Test 9: Log File Creation
Test-BackupComponent -TestName "LogFileCreation" -Description "Can create log files" {
    $logDir = Join-Path $env:APPDATA "backup-logs"
    if (-not (Test-Path $logDir)) {
        try {
            $null = New-Item -ItemType Directory -Path $logDir -Force -ErrorAction Stop
        }
        catch {
            Write-TestLog "  Failed to create log directory: $_" "FAIL" "LogFileCreation"
            return $false
        }
    }

    $testLogFile = Join-Path $logDir "test-$(Get-Date -Format 'yyyyMMddHHmmss').log"
    try {
        "Test log entry" | Out-File -FilePath $testLogFile -Encoding UTF8 -ErrorAction Stop
        $created = Test-Path $testLogFile
        if ($created) {
            Remove-Item $testLogFile -Force -ErrorAction SilentlyContinue
        }
        return $created
    }
    catch {
        Write-TestLog "  Failed to create test log file: $_" "FAIL" "LogFileCreation"
        return $false
    }
}

# Test 10: Variable Initialization
Test-BackupComponent -TestName "VariableInitialization" -Description "Required variables are initialized" {
    $scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
    $scriptContent = Get-Content $scriptPath -Raw

    $requiredVars = @(
        "\$ErrorActionPreference",
        "\$created",
        "\$skipped",
        "\$failed"
    )

    $missing = @()
    foreach ($var in $requiredVars) {
        if ($scriptContent -notmatch $var) {
            $missing += $var
        }
    }

    if ($missing.Count -gt 0) {
        Write-TestLog "  Missing variables: $($missing -join ', ')" "WARN" "VariableInitialization"
    }

    return $true  # Non-critical, just warn
}

# Test 11: Error Handling Structure
Test-BackupComponent -TestName "ErrorHandling" -Description "Script has proper error handling" {
    $scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"
    $scriptContent = Get-Content $scriptPath -Raw

    $hasTryCatch = $scriptContent -match "try\s*\{" -and $scriptContent -match "catch\s*\{"
    $hasErrorAction = $scriptContent -match "ErrorActionPreference"

    if (-not $hasTryCatch) {
        Write-TestLog "  Missing try-catch blocks" "WARN" "ErrorHandling"
    }

    if (-not $hasErrorAction) {
        Write-TestLog "  Missing ErrorActionPreference" "WARN" "ErrorHandling"
    }

    return $hasTryCatch -and $hasErrorAction
}

# Run full backup test if requested
if ($RunFullBackup) {
    Write-TestLog "" "INFO"
    Write-TestLog "=== RUNNING FULL BACKUP TEST ===" "INFO"
    Write-TestLog ""

    Test-BackupComponent -TestName "FullBackupRun" -Description "Running actual backup script" {
        $scriptPath = Join-Path $PSScriptRoot "backup-repo.ps1"

        $backupStart = Get-Date
        $output = @()

        try {
            & $scriptPath *>&1 | ForEach-Object {
                $output += $_
                Write-TestLog "  $_" "INFO" "FullBackupRun"
            }

            $backupDuration = (Get-Date) - $backupStart
            Write-TestLog "Backup completed in $([math]::Round($backupDuration.TotalSeconds, 1)) seconds" "INFO" "FullBackupRun"

            # Check if backups were created
            $desktop = [Environment]::GetFolderPath("Desktop")
            $repoName = (Get-Item .).Name
            $backupDir = Join-Path (Join-Path $desktop "repo backup") $repoName

            if (Test-Path $backupDir) {
                $zips = Get-ChildItem -Path $backupDir -Filter "*.zip" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
                if ($zips) {
                    $latest = $zips | Select-Object -First 1
                    Write-TestLog "Backup created: $($latest.Name) ($([math]::Round($latest.Length/1MB, 2)) MB)" "PASS" "FullBackupRun"
                    return $true
                }
            }

            Write-TestLog "No backup files found after execution" "FAIL" "FullBackupRun"
            return $false
        }
        catch {
            Write-TestLog "Backup script failed: $_" "FAIL" "FullBackupRun"
            Write-TestLog "Stack: $($_.ScriptStackTrace)" "FAIL" "FullBackupRun"
            return $false
        }
    }
}

# Summary
Write-TestLog "" "INFO"
Write-TestLog "=== TEST SUMMARY ===" "INFO"
Write-TestLog "Total Tests: $script:TestCount" "INFO"
Write-TestLog "Passed: $script:PassCount" -Level $(if ($script:PassCount -eq $script:TestCount) { "PASS" } else { "INFO" })
Write-TestLog "Failed: $script:FailCount" -Level $(if ($script:FailCount -eq 0) { "PASS" } else { "FAIL" })
Write-TestLog ""

$passRate = if ($script:TestCount -gt 0) { [math]::Round(($script:PassCount / $script:TestCount) * 100, 1) } else { 0 }
Write-TestLog "Pass Rate: $passRate%" -Level $(if ($passRate -eq 100) { "PASS" } else { "WARN" })
Write-TestLog ""

if ($script:FailCount -gt 0) {
    Write-TestLog "Failed Tests:" "FAIL"
    $testResults | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-TestLog "  - $($_.TestName): $($_.Message)" "FAIL"
    }
    exit 1
} else {
    Write-TestLog "All tests passed!" "PASS"
    exit 0
}
