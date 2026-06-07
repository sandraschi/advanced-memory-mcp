param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$WebPort = 10704
$BackendPort = 10705
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
$FleetStart = Initialize-FleetStartMode @PSBoundParameters
Enter-FleetHeadlessConsole -Headless:$Headless -BackendOnly:$BackendOnly
Stop-FleetPortSquatters -Ports @($WebPort, $BackendPort) -Label "advanced-memory-mcp"

# 2. Setup (frontend has package.json)
Set-Location $PSScriptRoot
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Set-Location $frontendPath
    npm install
    Set-Location $PSScriptRoot
}

# 3. Start the Python backend (Background). uv --project finds package; CWD stays webapp.
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$PSScriptRoot'; uv run --project '$ProjectRoot' uvicorn advanced_memory.server:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 3b. Wait for HTTP health (TCP listen alone is not enough for the fleet probe)
$healthUrl = "http://127.0.0.1:$BackendPort/api/v1/health"
$maxAttempts = 30
$attempt = 0
$backendUp = $false
while ($attempt -lt $maxAttempts) {
    try {
        $null = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        $backendUp = $true
        break
    } catch {
        Start-Sleep -Seconds 2
        $attempt++
    }
}
if ($backendUp) {
    Write-Host "Backend (port $BackendPort) answered GET /api/v1/health." -ForegroundColor Green
} else {
    Write-Host "Backend (port $BackendPort) did not return HTTP 200 from /api/v1/health; check the backend window." -ForegroundColor Yellow
}

if (-not $FleetStart.RunFrontend) { return }

# 4. Run Vite dev from frontend
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
Set-Location $frontendPath

# 4b. Launch background task to open browser once frontend is ready (Auto-opened by Antigravity)
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
if (-not $FleetStart.RunFrontend) { return }
npm run dev -- --port $WebPort --host






