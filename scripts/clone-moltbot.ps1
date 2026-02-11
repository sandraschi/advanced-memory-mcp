# Clone Moltbot (ClawdBot/OpenClaw) into D:\Dev\repos\<root>\moltbot
# Usage: .\clone-moltbot.ps1 [root]   e.g. .\clone-moltbot.ps1 external
# Run from PowerShell. Requires: git. Optional: Node 22+, pnpm for local dev.
# If partial clones left locked .git dirs, delete <root>\moltbot manually first.
#
# SECURITY: Feb 2026 PII exfiltration incident. Run security assessment before build.
# Standalone clone (no script): cd D:\Dev\repos\external; git clone --depth 1 https://github.com/moltbot/moltbot.git moltbot; git clone --depth 1 https://github.com/openclaw/openclaw.git openclaw

$ErrorActionPreference = "Stop"
$rootName = if ($args[0]) { $args[0] } else { "external" }
$root = "D:\Dev\repos\$rootName"
$repo = "moltbot"
$url = "https://github.com/moltbot/moltbot.git"
$dir = Join-Path $root $repo

if (Test-Path $dir) {
    Write-Host "Remove existing $dir first (e.g. partial clone). Run: Remove-Item -Recurse -Force '$dir'"
    exit 1
}

New-Item -ItemType Directory -Force -Path $root | Out-Null
Push-Location $root
try {
    git -c core.longpaths=true clone --depth 1 $url $repo
    Write-Host "Cloned to $dir"
    Write-Host "SECURITY: Run assessment before build. Then: cd $dir; pnpm install; pnpm build; moltbot onboard --install-daemon"
} finally {
    Pop-Location
}
