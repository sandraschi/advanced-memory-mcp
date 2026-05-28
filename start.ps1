  EDITED  D:\Dev\repos\advanced-memory-mcp\start.ps1 Param([switch]$Headless)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'
# advanced-memory-mcp Start - Standards-Compliant SOTA
Write-Host 'Starting advanced-memory-mcp...' -ForegroundColor Cyan

uv run advanced-memory mcp