#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated repository backup with complete error handling and logging

.DESCRIPTION
    Creates a compressed ZIP backup of the repository and saves to multiple locations:
    1. Desktop\repo backup\
    2. N:\backup\dev\repo-backups\
    3. OneDrive\repo backup\

    Features:
    - Complete error handling with detailed logging
    - Triple-location backups with individual error handling
    - Duplicate detection using SHA256 hashing
    - Intelligent file exclusions
    - Progress reporting and statistics
    - Dry-run mode (-WhatIf)
    - Backup history viewer (-List)
    - JSON output support (-OutputFormat json)

.PARAMETER IncludeBuild
    Include dist/ and build/ folders (default: false)

.PARAMETER List
    List backup history and statistics

.PARAMETER OutputFormat
    Output format: 'text' (default) or 'json'

.EXAMPLE
    .\scripts\backup-repo.ps1
    # Creates backup in all three locations

.EXAMPLE
    .\scripts\backup-repo.ps1 -IncludeBuild -Verbose
    # Creates backup including build artifacts with detailed progress

.EXAMPLE
    .\scripts\backup-repo.ps1 -WhatIf
    # Preview what would be backed up

.EXAMPLE
    .\scripts\backup-repo.ps1 -List
    # Show backup history
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$IncludeBuild = $false,
    [switch]$List = $false,
    [ValidateSet('text', 'json')]
    [string]$OutputFormat = 'text'
)

# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

$ErrorActionPreference = 'Stop'
$script:ErrorCount = 0
$script:WarningCount = 0
$script:StartTime = Get-Date
$script:LogFile = $null
$script:LogDir = $null

# Get verbosity settings
$Verbose = $VerbosePreference -eq 'Continue'
$WhatIf = $WhatIfPreference

# ============================================================================
# LOGGING SYSTEM
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Color = "White",
        [switch]$IsError = $false,
        [switch]$IsWarning = $false,
        [switch]$NoNewline = $false
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $prefix = ""
    
    if ($IsError) {
        $prefix = "[ERROR]"
        $Color = "Red"
        $script:ErrorCount++
        [Console]::Error.WriteLine("$timestamp $prefix $Message")
    }
    elseif ($IsWarning) {
        $prefix = "[WARN]"
        $Color = "Yellow"
        $script:WarningCount++
    }
    
    $logMessage = "$timestamp $prefix $Message"
    
    # Write to console
    if ($NoNewline) {
        Write-Host $logMessage -ForegroundColor $Color -NoNewline
    }
    else {
        Write-Host $logMessage -ForegroundColor $Color
    }
    
    # Write to log file
    if ($script:LogFile) {
        try {
            $logMessage | Out-File -FilePath $script:LogFile -Append -Encoding UTF8 -ErrorAction SilentlyContinue
        }
        catch {
            # If log write fails, just continue - don't fail the script
        }
    }
}

function Initialize-Logging {
    try {
        $script:LogDir = Join-Path $env:APPDATA "backup-logs"
        
        if (-not (Test-Path $script:LogDir)) {
            $null = New-Item -ItemType Directory -Path $script:LogDir -Force -ErrorAction Stop
            Write-Log "Created log directory: $script:LogDir" "Cyan"
        }
        
        $logFileName = "backup-$(Get-Date -Format 'yyyy-MM-dd').log"
        $script:LogFile = Join-Path $script:LogDir $logFileName
        
        Write-Log "========================================" "Cyan"
        Write-Log "Backup script started" "Cyan"
        Write-Log "Log file: $script:LogFile" "Cyan"
        Write-Log "========================================" "Cyan"
        Write-Log ""
        
        return $true
    }
    catch {
        Write-Host "CRITICAL: Failed to initialize logging: $_" -ForegroundColor Red
        [Console]::Error.WriteLine("CRITICAL: Failed to initialize logging: $_")
        return $false
    }
}

# ============================================================================
# ERROR HANDLING
# ============================================================================

function Write-ErrorDetails {
    param(
        [System.Exception]$Exception,
        [string]$Context = "Unknown"
    )
    
    Write-Log "  Context: $Context" "Red" -IsError
    Write-Log "  Exception Type: $($Exception.GetType().FullName)" "Red" -IsError
    Write-Log "  Exception Message: $($Exception.Message)" "Red" -IsError
    
    if ($Exception.InnerException) {
        Write-Log "  Inner Exception: $($Exception.InnerException.Message)" "Red" -IsError
    }
    
    if ($Exception.StackTrace) {
        Write-Log "  Stack Trace:" "Red" -IsError
        $Exception.StackTrace -split "`n" | ForEach-Object {
            Write-Log "    $_" "Red" -IsError
        }
    }
    
    [Console]::Error.WriteLine("ERROR in $Context : $($Exception.Message)")
}

function Exit-WithError {
    param(
        [string]$Message,
        [int]$ExitCode = 1
    )
    
    Write-Log "" "White"
    Write-Log "========================================" "Red"
    Write-Log "BACKUP FAILED" "Red" -IsError
    Write-Log "========================================" "Red"
    Write-Log "$Message" "Red" -IsError
    Write-Log "Total errors: $script:ErrorCount" "Red" -IsError
    Write-Log "Total warnings: $script:WarningCount" "Yellow" -IsWarning
    Write-Log ""
    
    if ($script:LogFile) {
        Write-Log "Full log available at: $script:LogFile" "Cyan"
    }
    
    exit $ExitCode
}

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize logging first
if (-not (Initialize-Logging)) {
    Exit-WithError "Failed to initialize logging system"
}

# Get repository name
$repoName = "unknown"
try {
    $currentDir = Get-Location
    if ((Test-Path "pyproject.toml") -or (Test-Path ".git") -or (Test-Path "package.json")) {
        $repoName = (Get-Item $currentDir).Name
    }
    else {
        Write-Log "Warning: Repository markers not found, using directory name" "Yellow" -IsWarning
        $repoName = (Get-Item $currentDir).Name
    }
}
catch {
    Write-ErrorDetails -Exception $_ -Context "Repository name detection"
    Exit-WithError "Failed to determine repository name"
}

Write-Log "Repository: $repoName" "Cyan"
Write-Log "Working directory: $currentDir" "Gray"

# ============================================================================
# BACKUP HISTORY (List mode)
# ============================================================================

if ($List) {
    Write-Log "Showing backup history for: $repoName" "Cyan"
    Write-Log ""
    
    try {
        $desktop = [Environment]::GetFolderPath("Desktop")
        $desktopBackup = Join-Path (Join-Path $desktop "repo backup") $repoName
        $nDriveBackup = "N:\backup\dev\repo-backups\$repoName"
        $oneDriveBackup = Join-Path (Join-Path $env:OneDrive "repo backup") $repoName
        
        $backupDirs = @(
            @{ Name = "Desktop"; Path = $desktopBackup },
            @{ Name = "N: Drive"; Path = $nDriveBackup },
            @{ Name = "OneDrive"; Path = $oneDriveBackup }
        )
        
        foreach ($backupDir in $backupDirs) {
            Write-Log "Location: $($backupDir.Name)" "Cyan"
            
            if ($backupDir.Path -and (Test-Path (Split-Path $backupDir.Path -Parent) -ErrorAction SilentlyContinue)) {
                if (Test-Path $backupDir.Path -ErrorAction SilentlyContinue) {
                    $backups = Get-ChildItem -Path $backupDir.Path -Filter "*.zip" -File -ErrorAction SilentlyContinue | 
                               Sort-Object LastWriteTime -Descending | 
                               Select-Object -First 10
                    
                    if ($backups) {
                        Write-Log "  Found $($backups.Count) backup(s):" "Green"
                        foreach ($backup in $backups) {
                            $size = [math]::Round($backup.Length / 1MB, 2)
                            Write-Log "    - $($backup.Name)" "Yellow"
                            Write-Log "      Size: $size MB, Date: $($backup.LastWriteTime)" "Gray"
                        }
                    }
                    else {
                        Write-Log "  No backups found" "Yellow" -IsWarning
                    }
                }
                else {
                    Write-Log "  Directory does not exist" "Yellow" -IsWarning
                }
            }
            else {
                Write-Log "  Location not accessible" "Yellow" -IsWarning
            }
            Write-Log ""
        }
        
        exit 0
    }
    catch {
        Write-ErrorDetails -Exception $_ -Context "Backup history listing"
        Exit-WithError "Failed to list backup history"
    }
}

# ============================================================================
# .NET ASSEMBLY LOADING
# ============================================================================

Write-Log "Loading .NET compression libraries..." "Cyan"

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
    Add-Type -AssemblyName System.Security.Cryptography -ErrorAction Stop
    Write-Log "  .NET libraries loaded successfully" "Green"
}
catch {
    Write-ErrorDetails -Exception $_ -Context ".NET assembly loading"
    Exit-WithError "Failed to load required .NET assemblies"
}

# ============================================================================
# FILE SCANNING AND FILTERING
# ============================================================================

Write-Log "Scanning repository files..." "Cyan"

try {
    $repoRoot = (Get-Item .).FullName
    Write-Log "  Repository root: $repoRoot" "Gray"
    
    # Get all files
    $allFiles = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue
    
    Write-Log "  Total files found: $($allFiles.Count)" "Gray"
    
    # Exclusion patterns
    $exclusions = @(
        '\.venv\\',
        '\\venv\\',
        '\\env\\',
        '\\__pycache__\\',
        '\\.ruff_cache\\',
        '\\.mypy_cache\\',
        '\\.pytest_cache\\',
        '\\node_modules\\',
        '\\.git\\objects\\',
        '\\.git\\refs\\',
        '\\\\.windsurf\\\\',
        '\\\\.cursor\\\\',
        '\\.backup-output\\.txt$',
        'backup-test-results\\.log$'
    )
    
    # Additional exclusions based on IncludeBuild flag
    if (-not $IncludeBuild) {
        $exclusions += @('\\dist\\', '\\build\\', '\\.eggs\\', '\\.tox\\')
    }
    
    # File type exclusions
    $fileExclusions = @('\.vdi$', '\.vmdk$', '\.vbox$', '\.log$')
    
    # Filter files
    $backupFiles = $allFiles | Where-Object {
        $file = $_
        $relativePath = $file.FullName.Substring($repoRoot.Length + 1)
        
        # Check exclusion patterns
        $excluded = $false
        foreach ($pattern in $exclusions) {
            if ($relativePath -match $pattern) {
                $excluded = $true
                break
            }
        }
        
        if (-not $excluded) {
            foreach ($pattern in $fileExclusions) {
                if ($file.Name -match $pattern) {
                    $excluded = $true
                    break
                }
            }
        }
        
        -not $excluded
    }
    
    $backupCount = ($backupFiles | Measure-Object).Count
    $totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB
    $backupSize = ($backupFiles | Measure-Object -Property Length -Sum).Sum / 1MB
    $excludedSize = $totalSize - $backupSize
    
    Write-Log "  Files to backup: $backupCount" "Green"
    Write-Log "  Total size: $([math]::Round($totalSize, 2)) MB" "Gray"
    Write-Log "  Excluded size: $([math]::Round($excludedSize, 2)) MB" "Gray"
    Write-Log "  Backup size: $([math]::Round($backupSize, 2)) MB" "Green"
    Write-Log ""
    
    if ($backupCount -eq 0) {
        Exit-WithError "No files found to backup"
    }
}
catch {
    Write-ErrorDetails -Exception $_ -Context "File scanning"
    Exit-WithError "Failed to scan repository files"
}

# Exit early if WhatIf
if ($WhatIf) {
    Write-Log "DRY-RUN MODE: No files will be created" "Yellow" -IsWarning
    Write-Log "Files that would be backed up: $backupCount files ($([math]::Round($backupSize, 2)) MB)" "Cyan"
    Write-Log ""
    exit 0
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Get-FileHashSHA256 {
    param(
        [string]$FilePath,
        [switch]$ShowProgress
    )
    
    try {
        $hash = [System.Security.Cryptography.SHA256]::Create()
        $fileStream = [System.IO.File]::OpenRead($FilePath)
        
        try {
            $hashBytes = $hash.ComputeHash($fileStream)
            return [System.BitConverter]::ToString($hashBytes) -replace '-', ''
        }
        finally {
            $fileStream.Close()
            $hash.Dispose()
        }
    }
    catch {
        Write-Log "  Warning: Failed to compute hash for $FilePath : $_" "Yellow" -IsWarning
        return $null
    }
}

function Test-BackupDuplicate {
    param(
        [string]$NewBackupPath,
        [string]$BackupDir,
        [switch]$Verbose
    )
    
    try {
        if (-not (Test-Path $NewBackupPath)) {
            return $false
        }
        
        if (-not (Test-Path $BackupDir)) {
            return $false
        }
        
        # Get previous backup
        $previousBackups = Get-ChildItem -Path $BackupDir -Filter "*.zip" -File -ErrorAction SilentlyContinue | 
                          Sort-Object LastWriteTime -Descending
        
        if ($previousBackups.Count -eq 0) {
            return $false
        }
        
        $previousBackup = $previousBackups[0]
        
        if ($Verbose) {
            Write-Log "    Comparing with: $($previousBackup.Name)" "Gray"
        }
        
        # Compare file sizes first (fast check)
        $newSize = (Get-Item $NewBackupPath).Length
        $oldSize = $previousBackup.Length
        
        if ($newSize -ne $oldSize) {
            return $false
        }
        
        # Compare hashes
        Write-Log "    Computing hash of new backup..." "Gray"
        $newHash = Get-FileHashSHA256 -FilePath $NewBackupPath
        
        Write-Log "    Computing hash of previous backup..." "Gray"
        $oldHash = Get-FileHashSHA256 -FilePath $previousBackup.FullName
        
        if ($newHash -and $oldHash -and $newHash -eq $oldHash) {
            Write-Log "    Hashes match - backup is duplicate" "Yellow" -IsWarning
            return $true
        }
        
        return $false
    }
    catch {
        Write-Log "  Warning: Duplicate check failed: $_" "Yellow" -IsWarning
        return $false
    }
}

function New-BackupZip {
    param(
        [string]$ZipPath,
        [array]$Files,
        [string]$LocationName,
        [string]$RepoRoot,
        [switch]$Verbose
    )
    
    $zipStart = Get-Date
    $fileCount = 0
    $errorCount = 0
    $zip = $null
    
    try {
        Write-Log "  Creating ZIP archive: $ZipPath" "Cyan"
        
        # Create parent directory if needed
        $zipDir = Split-Path $ZipPath -Parent
        if (-not (Test-Path $zipDir)) {
            $null = New-Item -ItemType Directory -Path $zipDir -Force -ErrorAction Stop
            Write-Log "    Created directory: $zipDir" "Gray"
        }
        
        # Remove existing file if present
        if (Test-Path $ZipPath) {
            Remove-Item $ZipPath -Force -ErrorAction Stop
            Write-Log "    Removed existing file" "Gray"
        }
        
        # Create ZIP archive
        $zip = [System.IO.Compression.ZipFile]::Open($ZipPath, [System.IO.Compression.ZipArchiveMode]::Create)
        
        foreach ($file in $Files) {
            try {
                if (-not (Test-Path $file.FullName)) {
                    $errorCount++
                    continue
                }
                
                if (-not $file.FullName.StartsWith($RepoRoot)) {
                    $errorCount++
                    continue
                }
                
                # Calculate relative path
                $relativePath = $file.FullName.Substring($RepoRoot.Length + 1)
                $zipEntryPath = $relativePath -replace '\\', '/'
                
                # Add file to ZIP
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $zip,
                    $file.FullName,
                    $zipEntryPath,
                    [System.IO.Compression.CompressionLevel]::Optimal
                ) | Out-Null
                
                $fileCount++
                
                # Progress reporting
                if ($Verbose -and ($fileCount % 100 -eq 0)) {
                    $percent = [math]::Round(($fileCount / $Files.Count) * 100, 1)
                    Write-Log "    Progress: $fileCount/$($Files.Count) files ($percent%)" "Gray"
                }
            }
            catch {
                $errorCount++
                Write-Log "    Warning: Failed to add file $($file.Name) : $_" "Yellow" -IsWarning
            }
        }
        
        # Close ZIP
        if ($zip) {
            $zip.Dispose()
            $zip = $null
        }
        
        # Validate
        if ($fileCount -eq 0) {
            throw "No files were added to ZIP archive"
        }
        
        if (-not (Test-Path $ZipPath)) {
            throw "ZIP file was not created"
        }
        
        $zipDuration = (Get-Date) - $zipStart
        $zipSize = (Get-Item $ZipPath).Length / 1MB
        
        Write-Log "  ZIP created successfully" "Green"
        Write-Log "    Files: $fileCount" "Gray"
        Write-Log "    Size: $([math]::Round($zipSize, 2)) MB" "Gray"
        Write-Log "    Duration: $([math]::Round($zipDuration.TotalSeconds, 1))s" "Gray"
        
        if ($errorCount -gt 0) {
            Write-Log "    Warnings: $errorCount files failed to add" "Yellow" -IsWarning
        }
        
        return $true
    }
    catch {
        Write-ErrorDetails -Exception $_ -Context "ZIP creation for $LocationName"
        
        # Cleanup on failure
        if ($zip) {
            try {
                $zip.Dispose()
            }
            catch {
                # Ignore disposal errors
            }
        }
        
        if (Test-Path $ZipPath) {
            try {
                Remove-Item $ZipPath -Force -ErrorAction SilentlyContinue
            }
            catch {
                # Ignore cleanup errors
            }
        }
        
        throw
    }
}

function Test-BackupTarget {
    param(
        [string]$TargetPath,
        [string]$TargetName
    )
    
    try {
        $parentDir = Split-Path $TargetPath -Parent
        
        if (-not (Test-Path $parentDir)) {
            return @{
                Success = $false
                Error = "Parent directory does not exist: $parentDir"
            }
        }
        
        # Test write access
        $testFile = Join-Path $parentDir ".backup-test-$(Get-Date -Format 'yyyyMMddHHmmss').tmp"
        
        try {
            "test" | Out-File -FilePath $testFile -Encoding UTF8 -ErrorAction Stop
            Remove-Item $testFile -Force -ErrorAction Stop
            
            return @{
                Success = $true
                Error = $null
            }
        }
        catch {
            return @{
                Success = $false
                Error = "Cannot write to directory: $_"
            }
        }
    }
    catch {
        return @{
            Success = $false
            Error = "Failed to test target: $_"
        }
    }
}

# ============================================================================
# BACKUP TARGET SETUP
# ============================================================================

Write-Log "Setting up backup targets..." "Cyan"

try {
    $desktop = [Environment]::GetFolderPath("Desktop")
    $desktopBackup = Join-Path (Join-Path $desktop "repo backup") $repoName
    $nDriveBackup = "N:\backup\dev\repo-backups\$repoName"
    $oneDriveBackup = Join-Path (Join-Path $env:OneDrive "repo backup") $repoName
    
    Write-Log "  Desktop: $desktopBackup" "Gray"
    Write-Log "  N: Drive: $nDriveBackup" "Gray"
    Write-Log "  OneDrive: $oneDriveBackup" "Gray"
    Write-Log ""
}
catch {
    Write-ErrorDetails -Exception $_ -Context "Backup target setup"
    Exit-WithError "Failed to set up backup targets"
}

# Test backup targets
Write-Log "Testing backup target accessibility..." "Cyan"

$desktopTest = Test-BackupTarget -TargetPath $desktopBackup -TargetName "Desktop"
$nDriveTest = Test-BackupTarget -TargetPath $nDriveBackup -TargetName "N: Drive"
$oneDriveTest = Test-BackupTarget -TargetPath $oneDriveBackup -TargetName "OneDrive"

if ($desktopTest.Success) {
    Write-Log "  Desktop: Accessible" "Green"
}
else {
    Write-Log "  Desktop: NOT ACCESSIBLE - $($desktopTest.Error)" "Red" -IsError
    Exit-WithError "Required backup target (Desktop) is not accessible"
}

if ($nDriveTest.Success) {
    Write-Log "  N: Drive: Accessible" "Green"
}
else {
    Write-Log "  N: Drive: NOT ACCESSIBLE - $($nDriveTest.Error)" "Yellow" -IsWarning
}

if ($oneDriveTest.Success) {
    Write-Log "  OneDrive: Accessible" "Green"
}
else {
    Write-Log "  OneDrive: NOT ACCESSIBLE - $($oneDriveTest.Error)" "Yellow" -IsWarning
}

Write-Log ""

# ============================================================================
# CREATE BACKUPS
# ============================================================================

$backupStartTime = Get-Date
$created = @()
$skipped = @()
$failed = @()

$backupFileName = "$repoName-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"

# Backup 1: Desktop
if ($desktopTest.Success) {
    Write-Log "Creating Desktop backup..." "Cyan"
    
    try {
        $backupPath1 = Join-Path $desktopBackup $backupFileName
        
        New-BackupZip -ZipPath $backupPath1 -Files $backupFiles -LocationName "Desktop" -RepoRoot $repoRoot -Verbose:$Verbose
        
        # Check for duplicates
        Write-Log "  Checking for duplicates..." "Gray"
        if (Test-BackupDuplicate -NewBackupPath $backupPath1 -BackupDir $desktopBackup -Verbose:$Verbose) {
            Write-Log "  Backup is duplicate of previous - removing" "Yellow" -IsWarning
            Remove-Item $backupPath1 -Force -ErrorAction SilentlyContinue
            $backupPath1 = $null
            $skipped += "Desktop"
        }
        else {
            $created += "Desktop"
            Write-Log "  Desktop backup complete" "Green"
        }
    }
    catch {
        Write-ErrorDetails -Exception $_ -Context "Desktop backup"
        $failed += "Desktop"
        $script:backup1Failed = $true
    }
    
    Write-Log ""
}

# Backup 2: N: Drive
if ($nDriveTest.Success) {
    Write-Log "Creating N: Drive backup..." "Cyan"
    
    try {
        $backupPath2 = Join-Path $nDriveBackup $backupFileName
        
        New-BackupZip -ZipPath $backupPath2 -Files $backupFiles -LocationName "N: Drive" -RepoRoot $repoRoot -Verbose:$Verbose
        
        # Check for duplicates
        Write-Log "  Checking for duplicates..." "Gray"
        if (Test-BackupDuplicate -NewBackupPath $backupPath2 -BackupDir $nDriveBackup -Verbose:$Verbose) {
            Write-Log "  Backup is duplicate of previous - removing" "Yellow" -IsWarning
            Remove-Item $backupPath2 -Force -ErrorAction SilentlyContinue
            $backupPath2 = $null
            $skipped += "N: Drive"
        }
        else {
            $created += "N: Drive"
            Write-Log "  N: Drive backup complete" "Green"
        }
    }
    catch {
        Write-ErrorDetails -Exception $_ -Context "N: Drive backup"
        $failed += "N: Drive"
        $script:backup2Failed = $true
    }
    
    Write-Log ""
}

# Backup 3: OneDrive
if ($oneDriveTest.Success) {
    Write-Log "Creating OneDrive backup..." "Cyan"
    
    try {
        $backupPath3 = Join-Path $oneDriveBackup $backupFileName
        
        New-BackupZip -ZipPath $backupPath3 -Files $backupFiles -LocationName "OneDrive" -RepoRoot $repoRoot -Verbose:$Verbose
        
        # Check for duplicates
        Write-Log "  Checking for duplicates..." "Gray"
        if (Test-BackupDuplicate -NewBackupPath $backupPath3 -BackupDir $oneDriveBackup -Verbose:$Verbose) {
            Write-Log "  Backup is duplicate of previous - removing" "Yellow" -IsWarning
            Remove-Item $backupPath3 -Force -ErrorAction SilentlyContinue
            $backupPath3 = $null
            $skipped += "OneDrive"
        }
        else {
            $created += "OneDrive"
            Write-Log "  OneDrive backup complete" "Green"
        }
    }
    catch {
        Write-ErrorDetails -Exception $_ -Context "OneDrive backup"
        $failed += "OneDrive"
        $script:backup3Failed = $true
    }
    
    Write-Log ""
}

# ============================================================================
# SUMMARY
# ============================================================================

$backupDuration = (Get-Date) - $backupStartTime
$totalDuration = (Get-Date) - $script:StartTime

Write-Log "========================================" "Cyan"
Write-Log "BACKUP SUMMARY" "Cyan"
Write-Log "========================================" "Cyan"
Write-Log "Total time: $([math]::Round($totalDuration.TotalSeconds, 1)) seconds" "Gray"
Write-Log "Backup time: $([math]::Round($backupDuration.TotalSeconds, 1)) seconds" "Gray"
Write-Log ""

if ($created.Count -gt 0) {
    Write-Log "Created: $($created -join ', ')" "Green"
}

if ($skipped.Count -gt 0) {
    Write-Log "Skipped (duplicate): $($skipped -join ', ')" "Yellow" -IsWarning
}

if ($failed.Count -gt 0) {
    Write-Log "Failed: $($failed -join ', ')" "Red" -IsError
}

Write-Log ""
Write-Log "Total errors: $script:ErrorCount" $(if ($script:ErrorCount -gt 0) { "Red" } else { "Gray" }) -IsError:($script:ErrorCount -gt 0)
Write-Log "Total warnings: $script:WarningCount" $(if ($script:WarningCount -gt 0) { "Yellow" } else { "Gray" }) -IsWarning:($script:WarningCount -gt 0)
Write-Log ""

if ($created.Count -eq 0 -and $failed.Count -gt 0) {
    Exit-WithError "All backups failed"
}

if ($created.Count -gt 0) {
    Write-Log "========================================" "Green"
    Write-Log "BACKUP COMPLETED SUCCESSFULLY" "Green"
    Write-Log "========================================" "Green"
}

if ($script:LogFile) {
    Write-Log "Full log: $script:LogFile" "Cyan"
}

Write-Log ""

exit 0
