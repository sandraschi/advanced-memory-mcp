# Simple backup test to diagnose the issue
$ErrorActionPreference = 'Stop'

Write-Host "=== SIMPLE BACKUP TEST ===" -ForegroundColor Cyan
Write-Host ""

cd d:\Dev\repos\advanced-memory-mcp

# Check repo name
Write-Host "1. Checking repository..." -ForegroundColor Yellow
if (Test-Path "pyproject.toml") {
    $repoName = (Get-Item .).Name
    Write-Host "   [OK] Repository: $repoName" -ForegroundColor Green
} else {
    Write-Host "   [ERROR] Not in a repository!" -ForegroundColor Red
    exit 1
}

# Check files to backup
Write-Host "2. Checking files..." -ForegroundColor Yellow
try {
    $files = Get-ChildItem -Recurse -File -ErrorAction Stop | Select-Object -First 10
    Write-Host "   [OK] Found files (showing first 10)" -ForegroundColor Green
    $files | ForEach-Object { Write-Host "      - $($_.Name)" -ForegroundColor Gray }
} catch {
    Write-Host "   [ERROR] Failed to scan files: $_" -ForegroundColor Red
    exit 1
}

# Check backup path
Write-Host "3. Checking backup path..." -ForegroundColor Yellow
$desktop = [Environment]::GetFolderPath("Desktop")
$backupDir = Join-Path (Join-Path $desktop "repo backup") $repoName
Write-Host "   Backup directory: $backupDir" -ForegroundColor Gray

if (-not (Test-Path $backupDir)) {
    try {
        New-Item -ItemType Directory -Path $backupDir -Force -ErrorAction Stop | Out-Null
        Write-Host "   [OK] Created directory" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] Failed to create directory: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "   [OK] Directory exists" -ForegroundColor Green
}

# Test ZIP creation
Write-Host "4. Testing ZIP creation..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
    Write-Host "   [OK] ZIP library loaded" -ForegroundColor Green
} catch {
    Write-Host "   [ERROR] Failed to load ZIP library: $_" -ForegroundColor Red
    exit 1
}

$testZipPath = Join-Path $backupDir "test-backup-$(Get-Date -Format 'yyyyMMddHHmmss').zip"
Write-Host "   Test ZIP path: $testZipPath" -ForegroundColor Gray

try {
    $repoRoot = (Get-Item .).FullName
    Write-Host "   Repository root: $repoRoot" -ForegroundColor Gray

    # Get a few files to test with
    $testFiles = Get-ChildItem -File -ErrorAction Stop | Select-Object -First 5

    if ($testFiles.Count -eq 0) {
        Write-Host "   [ERROR] No files found in repository root!" -ForegroundColor Red
        exit 1
    }

    Write-Host "   Testing with $($testFiles.Count) files..." -ForegroundColor Gray

    $zip = [System.IO.Compression.ZipFile]::Open($testZipPath, [System.IO.Compression.ZipArchiveMode]::Create)

    foreach ($file in $testFiles) {
        $relativePath = $file.Name
        Write-Host "      Adding: $relativePath" -ForegroundColor DarkGray
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $relativePath, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }

    $zip.Dispose()

    if (Test-Path $testZipPath) {
        $size = (Get-Item $testZipPath).Length
        Write-Host "   [OK] Test ZIP created: $size bytes" -ForegroundColor Green
        Write-Host "   File: $testZipPath" -ForegroundColor Gray
        Remove-Item $testZipPath -Force
        Write-Host "   [OK] Test ZIP removed" -ForegroundColor Green
    } else {
        Write-Host "   [ERROR] Test ZIP was not created!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   [ERROR] ZIP creation failed: $_" -ForegroundColor Red
    Write-Host "   Exception: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Stack: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== ALL TESTS PASSED ===" -ForegroundColor Green
Write-Host "The backup mechanism should work. Run the full backup script now."
