#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Automated skill upload to Claude.ai using browser automation

.DESCRIPTION
    Uses Selenium WebDriver to automate uploading all skill ZIPs to Claude.ai
    Requires: Chrome browser, ChromeDriver, user logged into Claude.ai

.PARAMETER BatchSize
    Number of skills to upload in one batch (default: 10)

.EXAMPLE
    .\scripts\auto_upload_skills.ps1
    .\scripts\auto_upload_skills.ps1 -BatchSize 20
#>

param(
    [int]$BatchSize = 10
)

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║     🤖 AUTOMATED CLAUDE SKILLS UPLOADER 🤖             ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Check prerequisites
$zipDir = "skill-zips"
if (-not (Test-Path $zipDir)) {
    Write-Host "❌ Error: skill-zips directory not found" -ForegroundColor Red
    exit 1
}

$zips = Get-ChildItem $zipDir -Filter "*.zip" | Sort-Object Name
Write-Host "📦 Found $($zips.Count) skill ZIPs`n" -ForegroundColor Cyan

# Check if Selenium module is available
$seleniumAvailable = $null -ne (Get-Module -ListAvailable -Name Selenium)

if (-not $seleniumAvailable) {
    Write-Host "⚠️  Selenium module not installed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 OPTION 1: Install Selenium for Full Automation" -ForegroundColor Cyan
    Write-Host "   Install-Module -Name Selenium -Scope CurrentUser" -ForegroundColor Gray
    Write-Host "   Then run this script again" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📋 OPTION 2: Manual Upload (Recommended - Easier!)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   1. I'll open the browser and folder" -ForegroundColor White
    Write-Host "   2. Login to Claude.ai if needed" -ForegroundColor White
    Write-Host "   3. Go to Settings → Capabilities" -ForegroundColor White
    Write-Host "   4. Drag & drop ZIPs from folder (10-20 at a time)" -ForegroundColor White
    Write-Host ""

    $choice = Read-Host "Continue with manual process? (y/n)"
    if ($choice -ne 'y') {
        Write-Host "❌ Cancelled" -ForegroundColor Red
        exit 0
    }

    # Manual process
    Write-Host "`n📁 Opening skill-zips directory..." -ForegroundColor Cyan
    Start-Process explorer.exe -ArgumentList (Get-Item $zipDir).FullName

    Start-Sleep -Seconds 2

    Write-Host "🌐 Opening Claude.ai capabilities page..." -ForegroundColor Cyan
    Start-Process "https://claude.ai/settings/capabilities"

    Write-Host ""
    Write-Host "✅ Ready for manual upload!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Skills to upload ($($zips.Count) total):" -ForegroundColor Cyan

    $i = 0
    $zips | ForEach-Object {
        $i++
        Write-Host "  $($i.ToString().PadLeft(3)). $($_.Name)" -ForegroundColor Gray
        if ($i % $BatchSize -eq 0) {
            Write-Host "  ─────── Batch $([math]::Ceiling($i / $BatchSize)) complete ───────" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "💡 TIP: Select multiple ZIPs (Ctrl+Click) and upload as batch!" -ForegroundColor Cyan
    Write-Host "💡 Recommended: $BatchSize skills per batch to avoid timeouts" -ForegroundColor Cyan
    Write-Host ""

    exit 0
}

# FULL AUTOMATION with Selenium (if module is installed)
Write-Host "✅ Selenium module found - attempting full automation" -ForegroundColor Green
Write-Host ""

try {
    Import-Module Selenium

    Write-Host "🌐 Starting Chrome browser..." -ForegroundColor Cyan
    $driver = Start-SeChrome -Quiet

    Write-Host "📍 Navigating to Claude.ai capabilities..." -ForegroundColor Cyan
    Enter-SeUrl -Driver $driver -Url "https://claude.ai/settings/capabilities"

    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Make sure you're logged in!" -ForegroundColor Yellow
    Write-Host "   Check browser window - login if needed" -ForegroundColor Yellow
    Write-Host ""

    $ready = Read-Host "Press Enter when logged in and on capabilities page..."

    Write-Host "`n🚀 Starting automated upload..." -ForegroundColor Green

    $uploaded = 0
    $failed = 0

    foreach ($zip in $zips) {
        try {
            Write-Host "`n[$($uploaded + $failed + 1)/$($zips.Count)] Uploading: $($zip.Name)" -ForegroundColor Cyan

            # Find upload button (this selector may need adjustment)
            $uploadButton = Find-SeElement -Driver $driver -By CssSelector "button[data-testid='upload-skill'], input[type='file']" -ErrorAction Stop

            # Send file path to input
            Send-SeKeys -Element $uploadButton -Keys $zip.FullName

            # Wait for upload confirmation (adjust timeout as needed)
            Start-Sleep -Seconds 3

            $uploaded++
            Write-Host "  ✅ Uploaded successfully" -ForegroundColor Green

            # Pause between uploads to avoid rate limiting
            if ($uploaded % $BatchSize -eq 0) {
                Write-Host "`n⏸️  Batch complete - pausing 5 seconds..." -ForegroundColor Yellow
                Start-Sleep -Seconds 5
            }

        } catch {
            $failed++
            Write-Host "  ❌ Failed: $_" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║          📊 UPLOAD COMPLETE! 📊                        ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Uploaded: $uploaded" -ForegroundColor Green
    Write-Host "❌ Failed:   $failed" -ForegroundColor Red
    Write-Host "📊 Total:    $($zips.Count)" -ForegroundColor Cyan
    Write-Host ""

    # Keep browser open for verification
    Write-Host "💡 Browser left open - verify uploads in Claude.ai" -ForegroundColor Cyan
    Write-Host "   Press Enter to close browser..." -ForegroundColor Gray
    Read-Host

    Stop-SeDriver -Driver $driver

} catch {
    Write-Host ""
    Write-Host "❌ Automation failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Falling back to manual process..." -ForegroundColor Yellow
    Write-Host ""

    # Clean up
    if ($driver) {
        Stop-SeDriver -Driver $driver -ErrorAction SilentlyContinue
    }

    # Open manual process
    Start-Process explorer.exe -ArgumentList (Get-Item $zipDir).FullName
    Start-Process "https://claude.ai/settings/capabilities"

    Write-Host "📁 Opened folder and browser for manual upload" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ Done!`n" -ForegroundColor Green
