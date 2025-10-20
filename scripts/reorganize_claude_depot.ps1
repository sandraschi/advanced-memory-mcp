# Claude Depot Reorganization Script
# Helps reorganize the organically-grown claude-depot into a clean structure
#
# SAFE: Creates a reorganization plan, moves files, Advanced Memory auto-syncs

param(
    [switch]$Analyze = $false,
    [switch]$Plan = $false,
    [switch]$Execute = $false,
    [string]$DepotPath = "C:\Users\sandr\Documents\claude-depot"
)

$ErrorActionPreference = "Stop"

Write-Host "=" -ForegroundColor Cyan -NoNewline
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "Claude Depot Reorganization Tool" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# Proposed structure
$ProposedStructure = @{
    "mcp-servers" = @(
        "*mcp*", "avatar*", "blender*", "calibre*", "docker*", "fetch*", 
        "filesystem*", "plex*", "tapo*", "vbox*", "virtual*", "windows*",
        "database*", "gimp*", "hasleo*", "pywin*"
    )
    "projects" = @(
        "01-active-projects", "02-areas", "03-resources"
    )
    "sessions" = @(
        "05-sessions", "session*", "daily*"
    )
    "development" = @(
        "04-development", "dev-*", "fixes", "bugs"
    )
    "archive" = @(
        "06-archive", "*backup*", "*obsolete*", "*archived*", "imported*"
    )
    "reference" = @(
        "cooking", "research", "documentation", "depot"
    )
    "system" = @(
        "system-*", ".advanced-memory", ".trash"
    )
}

function Analyze-Structure {
    param([string]$Path)
    
    Write-Host "Analyzing: $Path" -ForegroundColor Yellow
    Write-Host ""
    
    $folders = Get-ChildItem -Path $Path -Directory | Sort-Object Name
    
    Write-Host "Current Top-Level Folders ($($folders.Count)):" -ForegroundColor Cyan
    Write-Host ""
    
    $categorized = @{}
    $uncategorized = @()
    
    foreach ($folder in $folders) {
        $matched = $false
        
        foreach ($category in $ProposedStructure.Keys) {
            foreach ($pattern in $ProposedStructure[$category]) {
                if ($folder.Name -like $pattern) {
                    if (-not $categorized.ContainsKey($category)) {
                        $categorized[$category] = @()
                    }
                    $categorized[$category] += $folder.Name
                    $matched = $true
                    break
                }
            }
            if ($matched) { break }
        }
        
        if (-not $matched) {
            $uncategorized += $folder.Name
        }
    }
    
    # Display categorized
    foreach ($category in $categorized.Keys | Sort-Object) {
        Write-Host "[$category]" -ForegroundColor Green
        foreach ($folder in $categorized[$category] | Sort-Object) {
            Write-Host "  - $folder" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    if ($uncategorized.Count -gt 0) {
        Write-Host "[UNCATEGORIZED]" -ForegroundColor Yellow
        foreach ($folder in $uncategorized | Sort-Object) {
            Write-Host "  - $folder" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    return @{
        Categorized = $categorized
        Uncategorized = $uncategorized
    }
}

function Create-ReorganizationPlan {
    param(
        [string]$Path,
        [hashtable]$Analysis
    )
    
    Write-Host "=" -ForegroundColor Cyan -NoNewline
    Write-Host ("=" * 69) -ForegroundColor Cyan
    Write-Host "REORGANIZATION PLAN" -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Proposed Structure:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "$Path/" -ForegroundColor Cyan
    Write-Host "├── mcp-servers/           # All MCP server projects" -ForegroundColor Gray
    Write-Host "├── projects/              # Active work projects" -ForegroundColor Gray
    Write-Host "├── sessions/              # Session logs and notes" -ForegroundColor Gray
    Write-Host "├── development/           # Development notes and fixes" -ForegroundColor Gray
    Write-Host "├── archive/               # Old/completed/obsolete content" -ForegroundColor Gray
    Write-Host "├── reference/             # Reference materials (cooking, research)" -ForegroundColor Gray
    Write-Host "└── README.md              # Main index" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Moves Required:" -ForegroundColor Yellow
    Write-Host ""
    
    $moves = @()
    
    foreach ($category in $Analysis.Categorized.Keys | Sort-Object) {
        $targetFolder = $category
        
        foreach ($folderName in $Analysis.Categorized[$category]) {
            # Skip if already in place
            if ($folderName -eq $category) { continue }
            
            $source = Join-Path $Path $folderName
            $dest = Join-Path $Path "$category\$folderName"
            
            $moves += @{
                Source = $source
                Dest = $dest
                Category = $category
                FolderName = $folderName
            }
        }
    }
    
    # Group by category
    foreach ($category in ($moves | Group-Object Category | Sort-Object Name)) {
        Write-Host "→ $($category.Name)/" -ForegroundColor Green
        foreach ($move in $category.Group) {
            Write-Host "  $($move.FolderName)" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    Write-Host "Total moves: $($moves.Count)" -ForegroundColor Cyan
    Write-Host ""
    
    return $moves
}

function Execute-Reorganization {
    param(
        [array]$Moves,
        [string]$Path
    )
    
    Write-Host "=" -ForegroundColor Cyan -NoNewline
    Write-Host ("=" * 69) -ForegroundColor Cyan
    Write-Host "EXECUTING REORGANIZATION" -ForegroundColor Red
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "WARNING: This will move $($Moves.Count) folders!" -ForegroundColor Red
    Write-Host "Advanced Memory will auto-sync after restart." -ForegroundColor Yellow
    Write-Host ""
    
    $confirm = Read-Host "Type 'YES' to proceed"
    if ($confirm -ne "YES") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "Creating category folders..." -ForegroundColor Yellow
    
    # Create category folders
    $categories = $Moves | Select-Object -ExpandProperty Category -Unique
    foreach ($category in $categories) {
        $categoryPath = Join-Path $Path $category
        if (-not (Test-Path $categoryPath)) {
            New-Item -ItemType Directory -Path $categoryPath -Force | Out-Null
            Write-Host "  Created: $category/" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "Moving folders..." -ForegroundColor Yellow
    
    $success = 0
    $failed = 0
    
    foreach ($move in $Moves) {
        try {
            # Create parent directory if needed
            $destParent = Split-Path $move.Dest -Parent
            if (-not (Test-Path $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            
            # Move folder
            Move-Item -Path $move.Source -Destination $move.Dest -Force
            Write-Host "  Moved: $($move.FolderName) → $($move.Category)/" -ForegroundColor Green
            $success++
        }
        catch {
            Write-Host "  FAILED: $($move.FolderName) - $($_.Exception.Message)" -ForegroundColor Red
            $failed++
        }
    }
    
    Write-Host ""
    Write-Host "=" -ForegroundColor Cyan -NoNewline
    Write-Host ("=" * 69) -ForegroundColor Cyan
    Write-Host "COMPLETE" -ForegroundColor Green
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host "Moved: $success" -ForegroundColor Green
    Write-Host "Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
    Write-Host ""
    Write-Host "Next: Restart Claude Desktop to trigger re-sync" -ForegroundColor Yellow
}

# Main logic
if ($Analyze -or (-not $Plan -and -not $Execute)) {
    $analysis = Analyze-Structure -Path $DepotPath
    
    Write-Host "=" -ForegroundColor Cyan -NoNewline
    Write-Host ("=" * 69) -ForegroundColor Cyan
    Write-Host "RECOMMENDATIONS" -ForegroundColor Yellow
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Your depot has grown organically and could benefit from reorganization." -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review the categorization above" -ForegroundColor Gray
    Write-Host "  2. Run with -Plan to see proposed moves" -ForegroundColor Gray
    Write-Host "  3. Run with -Execute to perform reorganization" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Example:" -ForegroundColor Cyan
    Write-Host '  .\scripts\reorganize_claude_depot.ps1 -Plan' -ForegroundColor Gray
}

if ($Plan) {
    $analysis = Analyze-Structure -Path $DepotPath
    $moves = Create-ReorganizationPlan -Path $DepotPath -Analysis $analysis
    
    Write-Host "To execute this plan:" -ForegroundColor Yellow
    Write-Host '  .\scripts\reorganize_claude_depot.ps1 -Execute' -ForegroundColor Gray
}

if ($Execute) {
    $analysis = Analyze-Structure -Path $DepotPath
    $moves = Create-ReorganizationPlan -Path $DepotPath -Analysis $analysis
    Execute-Reorganization -Moves $moves -Path $DepotPath
}




