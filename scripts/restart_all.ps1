# Restart All Advanced Memory Services
# 
# This script restarts all Advanced Memory related services:
# - Stops all Python processes related to Advanced Memory
# - Optionally restarts Claude Desktop (which restarts MCP server)
# - Cleans up background processes
#
# Usage: .\scripts\restart_all.ps1 [-SkipClaude] [-Force] [-Timeout 30]

param(
    [switch]$SkipClaude,
    [switch]$Force,
    [int]$Timeout = 30
)

$ErrorActionPreference = "Continue"

# Get script directory and repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Restart All Advanced Memory Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find and stop Advanced Memory Python processes
Write-Host "[1/3] Stopping Advanced Memory Python processes..." -ForegroundColor Yellow

$ProcessesToStop = @()

# Find Python processes that might be running Advanced Memory
$PythonProcesses = Get-Process -Name "python*" -ErrorAction SilentlyContinue | Where-Object {
    $proc = $_
    try {
        $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
        if ($cmdLine) {
            # Check if command line contains advanced_memory or advanced-memory
            return ($cmdLine -match "advanced.memory" -or 
                    $cmdLine -match "advanced-memory" -or
                    $cmdLine -match "tapo.camera.mcp" -or
                    $cmdLine -match "tapo-camera-mcp")
        }
    } catch {
        # Can't get command line, skip
    }
    return $false
}

if ($PythonProcesses) {
    Write-Host "[INFO] Found $($PythonProcesses.Count) Advanced Memory Python process(es)" -ForegroundColor Gray
    
    foreach ($proc in $PythonProcesses) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            Write-Host "  - PID $($proc.Id): $($cmdLine.Substring(0, [Math]::Min(80, $cmdLine.Length)))..." -ForegroundColor Gray
            
            if ($Force) {
                Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                Write-Host "    [OK] Force stopped" -ForegroundColor Green
            } else {
                Stop-Process -Id $proc.Id -ErrorAction Stop
                Write-Host "    [OK] Stopped gracefully" -ForegroundColor Green
            }
            $ProcessesToStop += $proc.Id
        } catch {
            Write-Host "    [WARN] Could not stop PID $($proc.Id): $_" -ForegroundColor Yellow
        }
    }
    
    if ($ProcessesToStop.Count -gt 0) {
        Write-Host "[OK] Stopped $($ProcessesToStop.Count) process(es)" -ForegroundColor Green
        Start-Sleep -Seconds 2
    }
} else {
    Write-Host "[INFO] No Advanced Memory Python processes found" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Stop Claude Desktop (which stops MCP server)
if (-not $SkipClaude) {
    Write-Host "[2/3] Restarting Claude Desktop (restarts MCP server)..." -ForegroundColor Yellow
    
    # Find Claude executable
    $ClaudePath = $null
    $PossiblePaths = @(
        "$env:LOCALAPPDATA\Programs\claude-desktop\Claude.exe",
        "$env:ProgramFiles\Claude\Claude.exe",
        "${env:ProgramFiles(x86)}\Claude\Claude.exe"
    )
    
    foreach ($Path in $PossiblePaths) {
        if (Test-Path $Path) {
            $ClaudePath = $Path
            break
        }
    }
    
    # Try finding via PATH
    if (-not $ClaudePath) {
        try {
            $WhereResult = Get-Command Claude -ErrorAction Stop
            if ($WhereResult) {
                $ClaudePath = $WhereResult.Source
            }
        } catch {
            # Not in PATH
        }
    }
    
    if ($ClaudePath -and (Test-Path $ClaudePath)) {
        # Stop Claude
        $ClaudeProcess = Get-Process -Name "Claude" -ErrorAction SilentlyContinue
        if ($ClaudeProcess) {
            Write-Host "  Stopping Claude Desktop..." -ForegroundColor Gray
            Stop-Process -Name "Claude" -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
            Write-Host "  [OK] Claude Desktop stopped" -ForegroundColor Green
        } else {
            Write-Host "  [INFO] Claude Desktop was not running" -ForegroundColor Gray
        }
        
        # Start Claude
        Write-Host "  Starting Claude Desktop..." -ForegroundColor Gray
        try {
            Start-Process -FilePath $ClaudePath -ErrorAction Stop
            Write-Host "  [OK] Started Claude Desktop from: $ClaudePath" -ForegroundColor Green
            Write-Host "  [INFO] Waiting for Claude to initialize..." -ForegroundColor Gray
            Start-Sleep -Seconds 5
        } catch {
            Write-Host "  [FAIL] Error starting Claude: $_" -ForegroundColor Red
            Write-Host "  [INFO] Try starting Claude manually from: $ClaudePath" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [WARN] Could not find Claude Desktop executable" -ForegroundColor Yellow
        Write-Host "  [INFO] Skipping Claude restart" -ForegroundColor Gray
    }
} else {
    Write-Host "[2/3] Skipping Claude Desktop restart (-SkipClaude specified)" -ForegroundColor Gray
}

Write-Host ""

# Step 3: Summary
Write-Host "[3/3] Summary" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

if ($ProcessesToStop.Count -gt 0) {
    Write-Host "[OK] Stopped $($ProcessesToStop.Count) Advanced Memory process(es)" -ForegroundColor Green
} else {
    Write-Host "[INFO] No Advanced Memory processes were running" -ForegroundColor Gray
}

if (-not $SkipClaude) {
    Write-Host "[OK] Claude Desktop restart attempted" -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] MCP server will restart automatically when Claude Desktop loads" -ForegroundColor Gray
    Write-Host "[INFO] Check logs to verify: Get-Content logs\advanced-memory.log -Tail 30" -ForegroundColor Gray
} else {
    Write-Host "[INFO] Claude Desktop restart skipped" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[SUCCESS] Restart complete!" -ForegroundColor Green
Write-Host ""

