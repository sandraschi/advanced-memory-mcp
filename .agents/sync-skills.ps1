# Antigravity IDE Skills Sync Script
# Synchronizes skills from Advanced Memory to Antigravity IDE format

param(
    [string]$SourcePath = "skills",
    [string]$TargetPath = ".agents/skills",
    [string]$Format = "anthropic",  # "anthropic" or "antigravity"
    [switch]$Validate,
    [switch]$Backup,
    [string[]]$Categories = @()
)

Write-Host "🔄 Antigravity IDE Skills Sync" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Ensure target directory exists
if (!(Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    Write-Host "✅ Created target directory: $TargetPath" -ForegroundColor Green
}

# Backup existing skills if requested
if ($Backup) {
    $backupPath = "$TargetPath/backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    if (Test-Path $TargetPath) {
        Copy-Item -Path $TargetPath -Destination $backupPath -Recurse -Force
        Write-Host "💾 Backup created: $backupPath" -ForegroundColor Yellow
    }
}

# Export skills from Advanced Memory
Write-Host "📤 Exporting skills from Advanced Memory..." -ForegroundColor Blue

$exportArgs = @("export", "skills", "export_path=$TargetPath", "skills_format=$Format")
if ($Categories.Count -gt 0) {
    $categoriesStr = $Categories -join ","
    $exportArgs += "categories=$categoriesStr"
}

# Call the Advanced Memory export tool
Write-Host "📤 Calling Advanced Memory export tool..." -ForegroundColor Blue
Write-Host "Command: adn_export $($exportArgs -join ' ')" -ForegroundColor Gray

# Note: Replace this with actual API call when available
# $result = Invoke-AdnExport -Operation "skills" -ExportPath $TargetPath -SkillsFormat $Format

# Copy skills from Advanced Memory to Antigravity format
if (Test-Path $SourcePath) {
    $skillDirs = Get-ChildItem -Path $SourcePath -Directory
    foreach ($skillDir in $skillDirs) {
        $sourceSkillPath = Join-Path $SourcePath $skillDir.Name
        $targetSkillPath = Join-Path $TargetPath $skillDir.Name

        if (!(Test-Path $targetSkillPath)) {
            Copy-Item -Path $sourceSkillPath -Destination $targetSkillPath -Recurse -Force
            Write-Host "✅ Copied skill: $($skillDir.Name)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Skill already exists: $($skillDir.Name)" -ForegroundColor Yellow
        }
    }
}

# Validate skills if requested
if ($Validate) {
    Write-Host "`n🔍 Validating skills..." -ForegroundColor Blue

    $skillDirs = Get-ChildItem -Path $TargetPath -Directory
    $validCount = 0
    $invalidCount = 0

    foreach ($skillDir in $skillDirs) {
        $skillPath = Join-Path $TargetPath $skillDir.Name
        $skillMdPath = Join-Path $skillPath "SKILL.md"

        if (Test-Path $skillMdPath) {
            try {
                $content = Get-Content $skillMdPath -Raw
                if ($content -match "^---\s*\n(.*?\n)---\s*\n" -and $Matches[1] -match "name:\s*(\S+)") {
                    $skillName = $Matches[1]
                    Write-Host "✅ Valid: $skillName" -ForegroundColor Green
                    $validCount++
                } else {
                    Write-Host "❌ Invalid frontmatter: $($skillDir.Name)" -ForegroundColor Red
                    $invalidCount++
                }
            } catch {
                Write-Host "❌ Error reading: $($skillDir.Name) - $($_.Exception.Message)" -ForegroundColor Red
                $invalidCount++
            }
        } else {
            Write-Host "❌ Missing SKILL.md: $($skillDir.Name)" -ForegroundColor Red
            $invalidCount++
        }
    }

    Write-Host "`n📊 Validation Results:" -ForegroundColor Cyan
    Write-Host "   Valid skills: $validCount" -ForegroundColor Green
    Write-Host "   Invalid skills: $invalidCount" -ForegroundColor Red
}

Write-Host "`n🎉 Sync complete!" -ForegroundColor Green
Write-Host "Antigravity IDE skills are ready at: $TargetPath" -ForegroundColor Cyan

# Display usage examples
Write-Host "`n📖 Usage Examples:" -ForegroundColor Yellow
Write-Host "   # Sync all skills (Anthropic format)"
Write-Host "   .\sync-skills.ps1"
Write-Host ""
Write-Host "   # Sync all skills (Antigravity format)"
Write-Host "   .\sync-skills.ps1 -Format antigravity"
Write-Host ""
Write-Host "   # Sync with validation"
Write-Host "   .\sync-skills.ps1 -Validate"
Write-Host ""
Write-Host "   # Sync specific categories with backup"
Write-Host "   .\sync-skills.ps1 -Categories technical,creative -Backup -Validate"
