#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated repository backup excluding build artifacts, caches, and virtual environments
    
.DESCRIPTION
    Creates a compressed backup of the Advanced Memory MCP repository excluding:
    - .venv/ (220 MB)
    - .mypy_cache/ (69 MB)
    - htmlcov/ (11 MB) 
    - __pycache__/ directories
    - .ruff_cache/
    - .pytest_cache/
    - node_modules/ (if any)
    - dist/ (optional - can include if needed)
    
    Final backup: ~30-40 MB vs 200+ MB
    
.PARAMETER OutputPath
    Where to save the backup (default: parent directory)
    
.PARAMETER IncludeDist
    Include dist/ folder with built packages (default: false)
    
.PARAMETER UseWinRAR
    Use WinRAR instead of 7-Zip (default: auto-detect)
    
.EXAMPLE
    .\backup-repo.ps1
    # Creates backup in parent directory using 7-Zip or WinRAR
    
.EXAMPLE
    .\backup-repo.ps1 -OutputPath "D:\Backups" -IncludeDist
    # Creates backup in D:\Backups including dist/ folder
#>

param(
    [string]$OutputPath = "..",
    [switch]$IncludeDist = $false,
    [switch]$UseWinRAR = $false
)

# Color output functions
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║     📦 Advanced Memory MCP - Repository Backup 📦      ║" -ForegroundColor Magenta
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Check if we're in the repo root
if (-not (Test-Path "pyproject.toml")) {
    Write-Error "❌ Error: Must run from repository root directory"
    exit 1
}

# Get repo name and timestamp
$repoName = (Get-Item .).Name
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "${repoName}_backup_${timestamp}.7z"

# Resolve output path
$OutputPath = Resolve-Path $OutputPath
$backupPath = Join-Path $OutputPath $backupName

Write-Info "📋 Backup Configuration:"
Write-Host "  Repository: $repoName" -ForegroundColor White
Write-Host "  Timestamp:  $timestamp" -ForegroundColor White
Write-Host "  Output:     $backupPath" -ForegroundColor White
Write-Host "  Include dist/: $(if($IncludeDist){'Yes'}else{'No'})" -ForegroundColor White
Write-Host ""

# Detect compression tool
$compressorPath = $null
$compressorName = ""

if ($UseWinRAR) {
    # Check for WinRAR
    $winrarPaths = @(
        "C:\Program Files\WinRAR\WinRAR.exe",
        "C:\Program Files (x86)\WinRAR\WinRAR.exe",
        "$env:ProgramFiles\WinRAR\WinRAR.exe",
        "$env:ProgramFiles(x86)\WinRAR\WinRAR.exe"
    )
    
    foreach ($path in $winrarPaths) {
        if (Test-Path $path) {
            $compressorPath = $path
            $compressorName = "WinRAR"
            break
        }
    }
} else {
    # Check for 7-Zip first (preferred)
    $sevenZipPaths = @(
        "C:\Program Files\7-Zip\7z.exe",
        "C:\Program Files (x86)\7-Zip\7z.exe",
        "$env:ProgramFiles\7-Zip\7z.exe",
        "$env:ProgramFiles(x86)\7-Zip\7z.exe"
    )
    
    foreach ($path in $sevenZipPaths) {
        if (Test-Path $path) {
            $compressorPath = $path
            $compressorName = "7-Zip"
            break
        }
    }
    
    # Fall back to WinRAR if 7-Zip not found
    if (-not $compressorPath) {
        $winrarPaths = @(
            "C:\Program Files\WinRAR\WinRAR.exe",
            "C:\Program Files (x86)\WinRAR\WinRAR.exe"
        )
        
        foreach ($path in $winrarPaths) {
            if (Test-Path $path) {
                $compressorPath = $path
                $compressorName = "WinRAR"
                break
            }
        }
    }
}

if (-not $compressorPath) {
    Write-Error "❌ Error: Neither 7-Zip nor WinRAR found!"
    Write-Host "   Install one of:" -ForegroundColor Yellow
    Write-Host "   - 7-Zip: https://www.7-zip.org/" -ForegroundColor Yellow
    Write-Host "   - WinRAR: https://www.win-rar.com/" -ForegroundColor Yellow
    exit 1
}

Write-Success "✓ Found: $compressorName at $compressorPath`n"

# Define exclusions
$exclusions = @(
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "htmlcov",
    "node_modules",
    ".git",
    ".trash",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".DS_Store",
    "Thumbs.db",
    ".windsurf",
    ".claude"
)

if (-not $IncludeDist) {
    $exclusions += "dist"
}

Write-Info "🚫 Excluding:"
foreach ($excl in $exclusions) {
    Write-Host "  - $excl" -ForegroundColor Gray
}
Write-Host ""

# Calculate sizes
Write-Info "📊 Analyzing repository size..."

$totalSize = (Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | 
    Measure-Object -Property Length -Sum).Sum / 1MB

$excludedSize = 0
foreach ($excl in $exclusions) {
    if ($excl -match '^\*') { continue } # Skip wildcards
    if (Test-Path $excl) {
        $size = (Get-ChildItem $excl -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum / 1MB
        $excludedSize += $size
    }
}

$backupSize = $totalSize - $excludedSize

Write-Host "  Total size:    $([math]::Round($totalSize, 2)) MB" -ForegroundColor White
Write-Host "  Excluded:      $([math]::Round($excludedSize, 2)) MB" -ForegroundColor Red
Write-Host "  Backup size:   $([math]::Round($backupSize, 2)) MB" -ForegroundColor Green
Write-Host "  Reduction:     $([math]::Round(($excludedSize / $totalSize) * 100, 1))%`n" -ForegroundColor Cyan

# Create backup
Write-Info "🔄 Creating backup..."

if ($compressorName -eq "7-Zip") {
    # Build 7-Zip exclusion arguments
    $excludeArgs = @()
    foreach ($excl in $exclusions) {
        $excludeArgs += "-xr!$excl"
    }
    
    # Create command
    $arguments = @(
        "a",                    # Add to archive
        "-t7z",                 # 7z format
        "-mx=9",                # Maximum compression
        "-mmt=on",              # Multi-threading
        "$backupPath",          # Output file
        ".",                    # Current directory
        "-r"                    # Recursive
    ) + $excludeArgs
    
    # Execute
    try {
        $process = Start-Process -FilePath $compressorPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Success "`n✅ Backup created successfully!"
        } else {
            Write-Error "❌ Backup failed with exit code: $($process.ExitCode)"
            exit $process.ExitCode
        }
    } catch {
        Write-Error "❌ Error creating backup: $_"
        exit 1
    }
    
} elseif ($compressorName -eq "WinRAR") {
    # Build WinRAR exclusion arguments
    $excludeArgs = @()
    foreach ($excl in $exclusions) {
        $excludeArgs += "-x$excl"
    }
    
    # Create command
    $arguments = @(
        "a",                    # Add to archive
        "-afrar",               # RAR format (or use "-afzip" for ZIP)
        "-m5",                  # Maximum compression
        "-mt1",                 # Multi-threading
        "-r",                   # Recursive
        "$backupPath",          # Output file
        "."                     # Current directory
    ) + $excludeArgs
    
    # Execute
    try {
        $process = Start-Process -FilePath $compressorPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Success "`n✅ Backup created successfully!"
        } else {
            Write-Error "❌ Backup failed with exit code: $($process.ExitCode)"
            exit $process.ExitCode
        }
    } catch {
        Write-Error "❌ Error creating backup: $_"
        exit 1
    }
}

# Get final backup file info
if (Test-Path $backupPath) {
    $finalSize = (Get-Item $backupPath).Length / 1MB
    $compressionRatio = ($finalSize / $backupSize) * 100
    
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║              📦 Backup Complete! 📦                     ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Info "📊 Backup Statistics:"
    Write-Host "  File:           $(Split-Path -Leaf $backupPath)" -ForegroundColor White
    Write-Host "  Location:       $OutputPath" -ForegroundColor White
    Write-Host "  Size:           $([math]::Round($finalSize, 2)) MB" -ForegroundColor Cyan
    Write-Host "  Original:       $([math]::Round($backupSize, 2)) MB" -ForegroundColor Gray
    Write-Host "  Compression:    $([math]::Round($compressionRatio, 1))%" -ForegroundColor Green
    Write-Host "  Space saved:    $([math]::Round($totalSize - $finalSize, 2)) MB" -ForegroundColor Green
    Write-Host ""
    
    # Quick restore instructions
    Write-Info "💡 To restore:"
    if ($compressorName -eq "7-Zip") {
        Write-Host "  7z x `"$backupPath`" -o`"destination-folder`"" -ForegroundColor Gray
    } else {
        Write-Host "  WinRAR x `"$backupPath`" `"destination-folder`"" -ForegroundColor Gray
    }
    Write-Host ""
    
} else {
    Write-Error "❌ Error: Backup file not found at $backupPath"
    exit 1
}

# Optional: Open backup location
$openLocation = Read-Host "Open backup location? (y/n)"
if ($openLocation -eq 'y') {
    explorer.exe $OutputPath
}

Write-Success "✅ Done!`n"

