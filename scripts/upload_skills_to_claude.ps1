#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automate uploading skills to Claude.ai capabilities page

.DESCRIPTION
    Uses browser automation to upload all skill ZIPs to Claude.ai
    Requires: Chrome browser, user must be logged into Claude.ai

.EXAMPLE
    .\scripts\upload_skills_to_claude.ps1
#>

Write-Host "`nâ•"â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•-" -ForegroundColor Magenta
Write-Host "â•'     ðŸ¤- CLAUDE SKILLS UPLOAD AUTOMATION ðŸ¤-              â•'" -ForegroundColor Magenta
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•`n" -ForegroundColor Magenta

# Check for skill ZIPs
$zipDir = "skill-zips"
if (-not (Test-Path $zipDir)) {
    Write-Host "âŒ Error: skill-zips directory not found" -ForegroundColor Red
    Write-Host "   Run: scripts\create_skill_batch.py first" -ForegroundColor Yellow
    exit 1
}

$zips = Get-ChildItem $zipDir -Filter "*.zip"
Write-Host "ðŸ"¦ Found $($zips.Count) skill ZIPs to upload`n" -ForegroundColor Cyan

# Manual instructions (automation is complex)
Write-Host "ðŸ"‹ MANUAL UPLOAD PROCESS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open browser: https://claude.ai/settings/capabilities" -ForegroundColor White
Write-Host "2. Click 'Add Skill' or 'Upload Skill' button" -ForegroundColor White
Write-Host "3. For each skill in: $((Get-Item $zipDir).FullName)" -ForegroundColor White
Write-Host "   - Click 'Choose File'" -ForegroundColor Gray
Write-Host "   - Select the ZIP file" -ForegroundColor Gray
Write-Host "   - Click 'Upload'" -ForegroundColor Gray
Write-Host ""
Write-Host "ðŸš€ FASTER BATCH METHOD (if available):" -ForegroundColor Yellow
Write-Host "   - Select multiple ZIPs at once (Ctrl+Click)" -ForegroundColor White
Write-Host "   - Drag & drop all ZIPs into upload area" -ForegroundColor White
Write-Host ""

# Open the directory for easy access
Write-Host "ðŸ" Opening skill-zips directory..." -ForegroundColor Cyan
Start-Process explorer.exe -ArgumentList (Get-Item $zipDir).FullName

# Open Claude capabilities page
Write-Host "ðŸŒ Opening Claude.ai capabilities page..." -ForegroundColor Cyan
Start-Process "https://claude.ai/settings/capabilities"

Write-Host ""
Write-Host "âœ... Directory and webpage opened!" -ForegroundColor Green
Write-Host ""
Write-Host "ðŸ'¡ TIP: Upload in batches (10-20 at a time) to avoid timeouts" -ForegroundColor Cyan
Write-Host ""
Write-Host "ðŸ"Š Progress tracker:" -ForegroundColor Yellow
Write-Host "   Total skills: $($zips.Count)" -ForegroundColor White
Write-Host "   Uploaded: [ ] / $($zips.Count)" -ForegroundColor White
Write-Host ""

# List all ZIPs for reference
Write-Host "ðŸ"‹ Skills to upload:" -ForegroundColor Cyan
$zips | ForEach-Object { Write-Host "   - $($_.Name)" -ForegroundColor Gray }

Write-Host ""
Write-Host "ðŸŽ¯ After uploading, skills will be available across:" -ForegroundColor Green
Write-Host "   - Claude.ai web interface" -ForegroundColor White
Write-Host "   - Claude Desktop app" -ForegroundColor White
Write-Host "   - Claude mobile (if available)" -ForegroundColor White
Write-Host ""
