# Advanced Memory MCP - Cursor Startup Diagnostic Script
# This script helps diagnose why the MCP server isn't starting in Cursor

Write-Host "=== Advanced Memory MCP - Cursor Startup Diagnostic ===" -ForegroundColor Cyan
Write-Host ""

# Check 1: Python installation
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
    Write-Host "    Install Python 3.11+ from python.org" -ForegroundColor Red
    exit 1
}

# Check 2: Advanced Memory package installation
Write-Host "[2/6] Checking Advanced Memory installation..." -ForegroundColor Yellow
try {
    $amVersion = python -m advanced_memory --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Advanced Memory installed: $amVersion" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Advanced Memory not installed" -ForegroundColor Red
        Write-Host "    Install with: pip install advanced-memory-mcp" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "  ✗ Advanced Memory not installed" -ForegroundColor Red
    Write-Host "    Install with: pip install advanced-memory-mcp" -ForegroundColor Yellow
    exit 1
}

# Check 3: Test server module import
Write-Host "[3/6] Testing server module import..." -ForegroundColor Yellow
try {
    $importTest = python -c "import advanced_memory.mcp.server; print('OK')" 2>&1
    if ($LASTEXITCODE -eq 0 -and $importTest -eq "OK") {
        Write-Host "  ✓ Server module imports successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Server module import failed" -ForegroundColor Red
        Write-Host "    Error: $importTest" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ✗ Server module import failed" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    exit 1
}

# Check 4: Cursor configuration file location
Write-Host "[4/6] Checking Cursor configuration..." -ForegroundColor Yellow
$cursorConfigPath = "$env:APPDATA\Cursor\User\globalStorage\cursor-storage\mcp_config.json"
if (Test-Path $cursorConfigPath) {
    Write-Host "  ✓ Configuration file found: $cursorConfigPath" -ForegroundColor Green

    # Check if advanced-memory is configured
    $configContent = Get-Content $cursorConfigPath -Raw | ConvertFrom-Json
    if ($configContent.mcpServers.'advanced-memory') {
        Write-Host "  ✓ Advanced Memory configured in mcp_config.json" -ForegroundColor Green
        Write-Host "    Command: $($configContent.mcpServers.'advanced-memory'.command)" -ForegroundColor Cyan
        Write-Host "    Args: $($configContent.mcpServers.'advanced-memory'.args -join ' ')" -ForegroundColor Cyan
    } else {
        Write-Host "  ✗ Advanced Memory not configured in mcp_config.json" -ForegroundColor Red
        Write-Host "    Add configuration (see below)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Configuration file not found: $cursorConfigPath" -ForegroundColor Red
    Write-Host "    Create the file with the configuration below" -ForegroundColor Yellow
}

# Check 5: Test server startup (non-blocking)
Write-Host "[5/6] Testing server startup (5 second timeout)..." -ForegroundColor Yellow
$testProcess = Start-Process -FilePath "python" -ArgumentList "-m", "advanced_memory.mcp.server" -NoNewWindow -PassThru -RedirectStandardOutput "test_output.txt" -RedirectStandardError "test_error.txt"
Start-Sleep -Seconds 2
if (-not $testProcess.HasExited) {
    Write-Host "  ✓ Server started successfully (process running)" -ForegroundColor Green
    Stop-Process -Id $testProcess.Id -Force -ErrorAction SilentlyContinue
    Remove-Item "test_output.txt" -ErrorAction SilentlyContinue
    Remove-Item "test_error.txt" -ErrorAction SilentlyContinue
} else {
    Write-Host "  ✗ Server exited immediately (check errors below)" -ForegroundColor Red
    if (Test-Path "test_error.txt") {
        $errors = Get-Content "test_error.txt"
        Write-Host "    Errors:" -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "      $_" -ForegroundColor Red }
    }
    Remove-Item "test_output.txt" -ErrorAction SilentlyContinue
    Remove-Item "test_error.txt" -ErrorAction SilentlyContinue
}

# Check 6: Cursor logs
Write-Host "[6/6] Checking Cursor logs location..." -ForegroundColor Yellow
$cursorLogPath = "$env:APPDATA\Cursor\logs"
if (Test-Path $cursorLogPath) {
    Write-Host "  ✓ Cursor logs directory found: $cursorLogPath" -ForegroundColor Green
    $latestLog = Get-ChildItem $cursorLogPath -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestLog) {
        Write-Host "    Latest log: $($latestLog.Name)" -ForegroundColor Cyan
        Write-Host "    Check this file for MCP server errors" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Logs directory not found (may not exist until Cursor runs)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Recommended Configuration ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add this to: $cursorConfigPath" -ForegroundColor Yellow
Write-Host ""
Write-Host @"
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"]
    }
  }
}
"@ -ForegroundColor White

Write-Host ""
Write-Host "Or using uvx (if you have uv installed):" -ForegroundColor Yellow
Write-Host ""
Write-Host @"
{
  "mcpServers": {
    "advanced-memory": {
      "command": "uvx",
      "args": ["advanced-memory"]
    }
  }
}
"@ -ForegroundColor White

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Ensure configuration file exists and is valid JSON" -ForegroundColor Yellow
Write-Host "2. Restart Cursor completely (close all windows)" -ForegroundColor Yellow
Write-Host "3. Check Cursor logs for MCP server errors" -ForegroundColor Yellow
Write-Host "4. Verify Python path is correct in configuration" -ForegroundColor Yellow
