# Minimal test to see what's happening with backup
cd d:\Dev\repos\advanced-memory-mcp

Write-Host "=== MINIMAL BACKUP TEST ===" -ForegroundColor Cyan
Write-Host ""

# Test .NET ZIP libraries
Write-Host "Testing .NET compression libraries..." -ForegroundColor Yellow
try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction Stop
    Write-Host "  [OK] System.IO.Compression.FileSystem loaded" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed to load: $_" -ForegroundColor Red
    exit 1
}

# Test repository root
Write-Host "Testing repository root..." -ForegroundColor Yellow
try {
    $repoRoot = (Get-Item .).FullName
    Write-Host "  [OK] Repository root: $repoRoot" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Failed: $_" -ForegroundColor Red
    exit 1
}

# Test backup path
Write-Host "Testing backup path..." -ForegroundColor Yellow
$desktop = [Environment]::GetFolderPath("Desktop")
$backupDir = Join-Path (Join-Path $desktop "repo backup") "advanced-memory-mcp"
Write-Host "  Backup directory: $backupDir" -ForegroundColor Gray

if (-not (Test-Path $backupDir)) {
    try {
        New-Item -ItemType Directory -Path $backupDir -Force -ErrorAction Stop | Out-Null
        Write-Host "  [OK] Created directory" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Failed to create directory: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  [OK] Directory exists" -ForegroundColor Green
}

# Test file access
Write-Host "Testing file access..." -ForegroundColor Yellow
try {
    $testFile = Join-Path $backupDir "test-write.tmp"
    "test" | Out-File -FilePath $testFile -Encoding utf8 -ErrorAction Stop
    Remove-Item $testFile -Force -ErrorAction Stop
    Write-Host "  [OK] Write access confirmed" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Write access failed: $_" -ForegroundColor Red
    exit 1
}

# Test file scanning
Write-Host "Testing file scanning..." -ForegroundColor Yellow
try {
    $allFiles = Get-ChildItem -Recurse -File -ErrorAction Stop
    Write-Host "  [OK] Found $($allFiles.Count) files" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] File scan failed: $_" -ForegroundColor Red
    exit 1
}

# Test ZIP creation with a single file
Write-Host "Testing ZIP creation..." -ForegroundColor Yellow
try {
    $testZipPath = Join-Path $backupDir "test-backup.zip"
    if (Test-Path $testZipPath) {
        Remove-Item $testZipPath -Force -ErrorAction Stop
    }

    $zip = [System.IO.Compression.ZipFile]::Open($testZipPath, [System.IO.Compression.ZipArchiveMode]::Create)

    # Add one test file
    $testContentFile = Join-Path $repoRoot "README.md"
    if (Test-Path $testContentFile) {
        $relativePath = "README.md"
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $testContentFile, $relativePath, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
        Write-Host "  [OK] Added file to ZIP" -ForegroundColor Green
    }

    $zip.Dispose()

    if (Test-Path $testZipPath) {
        $size = (Get-Item $testZipPath).Length
        Write-Host "  [OK] ZIP created: $size bytes" -ForegroundColor Green
        Write-Host "  Test ZIP: $testZipPath" -ForegroundColor Gray
        Remove-Item $testZipPath -Force
    } else {
        Write-Host "  [ERROR] ZIP file not created!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  [ERROR] ZIP creation failed: $_" -ForegroundColor Red
    Write-Host "  Exception: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== ALL TESTS PASSED ===" -ForegroundColor Green
Write-Host "The backup mechanism should work. Check the full script for other issues."
