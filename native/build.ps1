$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$RepoName = Split-Path -Leaf $Root
$Triple = "x86_64-pc-windows-msvc"
$ResourceDir = "$PSScriptRoot\resources"
$DevDir = "$PSScriptRoot\binaries"
New-Item -ItemType Directory -Force -Path $ResourceDir, $DevDir | Out-Null

Write-Host "=== ${RepoName} Tauri Release Build ===" -ForegroundColor Cyan

# Step 1: TypeScript lint gate + frontend build
$frontendDirs = @("web_sota", "webapp/frontend", "webapp")
foreach ($dir in $frontendDirs) {
    $frontend = Join-Path $Root $dir
    if (Test-Path "$frontend\package.json") {
        Write-Host "-> [1/4] Building frontend ($dir)..." -ForegroundColor Yellow
        Push-Location $frontend
        # Production API base: no Vite proxy in dist/, so bake the absolute backend URL
        # (must match BACKEND_PORT in native/src/backend.rs + CSP connect-src).
        $env:VITE_API_URL = "http://127.0.0.1:10705/api/v1"
        npm install --silent 2>$null

        Write-Host "  tsc --noEmit..." -ForegroundColor Gray
        $tscOut = npx tsc --noEmit 2>&1
        $tscExit = $LASTEXITCODE
        if ($tscExit -ne 0) {
            Write-Host "  TypeScript compilation FAILED - fix errors before building NSIS" -ForegroundColor Red
            Write-Host $tscOut
            throw "TypeScript compilation failed - fix all errors before building NSIS installer"
        }

        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
        Pop-Location
        break
    }
}

# Step 2: PyInstaller backend (onefile)
Write-Host "-> [2/4] PyInstaller backend..." -ForegroundColor Yellow
$specFile = "$Root\${RepoName}-backend.spec"
if (Test-Path $specFile) {
    Push-Location $Root
    # NEVER `uv run pyinstaller`: that resolves to the global uv-tool environment,
    # which cannot see the project's venv packages (fastmcp, uvicorn, ...) and
    # silently produces a broken binary. Always the venv exe (fleet pitfall).
    $pyiExe = "$Root\.venv\Scripts\pyinstaller.exe"
    if (-not (Test-Path $pyiExe)) {
        Write-Host "  Installing pyinstaller into project venv..." -ForegroundColor Yellow
        uv add --dev pyinstaller pefile altgraph
        uv sync
    }
    if (-not (Test-Path $pyiExe)) { throw "No pyinstaller at $pyiExe after install" }
    # Pre-clean: a stale locked exe from a previous build breaks the rebuild (WinError 32).
    Get-Process "${RepoName}-backend" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Remove-Item "$Root\dist\${RepoName}-backend.exe" -Force -ErrorAction SilentlyContinue
    # Patch fastmcp to not crash on missing metadata (dist-info stripped below)
    $fm = "$Root\.venv\Lib\site-packages\fastmcp\__init__.py"
    if (Test-Path $fm) {
        $c = Get-Content $fm -Raw
        if ($c -match 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)') {
            $c = $c -replace 'except PackageNotFoundError:\s+    __version__ = _version\("fastmcp"\)', 'except PackageNotFoundError:
    try:
        __version__ = _version("fastmcp")
    except PackageNotFoundError:
        __version__ = "0.0.0"'
            Set-Content $fm -Value $c -Encoding utf8
            Write-Host "  Patched fastmcp metadata fallback" -ForegroundColor Yellow
        }
    }
    & $pyiExe "$specFile" --clean --noconfirm
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
    Pop-Location
} else {
    Write-Host "  WARNING: spec file not found at $specFile - using existing backend exe if present" -ForegroundColor DarkYellow
}

# Gate 0: backend exe must exist and be a real bundle (>= 5MB, not a runt).
$builtExe = "$Root\dist\${RepoName}-backend.exe"
if (-not (Test-Path $builtExe)) { throw "Backend exe missing at $builtExe - PyInstaller step failed" }
$exeMB = (Get-Item $builtExe).Length / 1MB
if ($exeMB -lt 5) { throw "Backend exe is only $([math]::Round($exeMB, 2)) MB - runt build, refusing to bundle" }
Write-Host "  Backend exe size gate OK: $([math]::Round($exeMB, 1)) MB" -ForegroundColor Green

# Phase 2 smoke: run the FROZEN binary, hit /health + a real data route.
Write-Host "-> [2b/4] Frozen sidecar smoke..." -ForegroundColor Yellow
$smokePort = 11999
$smokeErr = "$Root\dist\pyi-smoke-stderr.log"
$smokeProc = Start-Process -FilePath $builtExe -NoNewWindow -PassThru `
    -RedirectStandardError $smokeErr `
    -Environment @{ ADVANCED_MEMORY_MCP_PORT = "$smokePort"; ADVANCED_MEMORY_MCP_HOST = "127.0.0.1"; ADVANCED_MEMORY_MCP_TAURI = "1" }
try {
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        Write-Host "  waiting for frozen backend... ($((($i + 1) * 2))s)" -ForegroundColor DarkGray
        if ($smokeProc.HasExited) { break }
        try {
            $h = Invoke-WebRequest "http://127.0.0.1:$smokePort/api/v1/health" -UseBasicParsing -TimeoutSec 3
            if ($h.StatusCode -eq 200) { $ready = $true; break }
        } catch {}
    }
    if (-not $ready) {
        $errText = Get-Content $smokeErr -Raw -ErrorAction SilentlyContinue
        throw "Frozen backend never became healthy on :$smokePort (exited=$($smokeProc.HasExited)). Stderr:`n$errText"
    }
    $feat = Invoke-WebRequest "http://127.0.0.1:$smokePort/api/v1/projects" -UseBasicParsing -TimeoutSec 10
    if ($feat.StatusCode -ne 200 -or $feat.Content -notmatch "main") { throw "Frozen backend /projects did not return project data" }
    Write-Host "  Frozen smoke OK: /health 200 + /projects has data" -ForegroundColor Green
} finally {
    if (-not $smokeProc.HasExited) { Stop-Process -Id $smokeProc.Id -Force -ErrorAction SilentlyContinue }
}
$smokeErrText = Get-Content $smokeErr -Raw -ErrorAction SilentlyContinue
foreach ($bad in @("cachetools", "isatty", "No module named", "_strptime", "Traceback (most recent call last)", "FileNotFoundError")) {
    if ($smokeErrText -match [regex]::Escape($bad)) { throw "Frozen smoke stderr contains '$bad' - bundle is broken" }
}
Remove-Item $smokeErr -Force -ErrorAction SilentlyContinue

# Step 3: Embed in Tauri resources (+ dev fallback)
Write-Host "-> [3/4] Embedding backend..." -ForegroundColor Yellow
$src = "$Root\dist\${RepoName}-backend.exe"
if (-not (Test-Path $src)) { throw "Backend exe not found at $src - PyInstaller step failed" }
Copy-Item $src "$ResourceDir\${RepoName}-backend.exe" -Force
Copy-Item $src "$DevDir\${RepoName}-backend-$Triple.exe" -Force
Write-Host "  Backend exe: $((Get-Item $src).Length / 1MB) MB"

# Bundle .env.example (NOT .env - dev .env has personal API keys)
$envExample = "$Root\.env.example"
if (Test-Path $envExample) {
    Copy-Item $envExample "$ResourceDir\.env.example" -Force
    Write-Host "  Bundled .env.example OK" -ForegroundColor Green
} else {
    Write-Host "  WARNING: .env.example not found at repo root" -ForegroundColor DarkYellow
}

# Step 4: Single NSIS installer
Write-Host "-> [4/4] Tauri NSIS bundle..." -ForegroundColor Yellow
Push-Location $PSScriptRoot
$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
npx @tauri-apps/cli build --bundles nsis
if ($LASTEXITCODE -ne 0) { throw "Tauri build failed with exit code $LASTEXITCODE" }
Pop-Location

# Stage to repo dist/
$distDir = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$nsisDir = "$PSScriptRoot\target\release\bundle\nsis"
if (Test-Path $nsisDir) { Copy-Item "$nsisDir\*-setup.exe" "$distDir\" -Force }
$strayExe = "$PSScriptRoot\target\release\advanced-memory-mcp-backend.exe"
if (Test-Path $strayExe) { Remove-Item $strayExe -Force; Write-Host "  Cleaned stray: $strayExe" -ForegroundColor DarkGray }

Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "Ship: $nsisDir\*.exe"

