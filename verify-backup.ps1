# Simple backup verification script
$output = @()

$output += "=== BACKUP VERIFICATION ==="
$output += "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$output += ""

$desktop = [Environment]::GetFolderPath("Desktop")
$paths = @(
    @{ Name = "Desktop"; Path = Join-Path (Join-Path $desktop "repo backup") "advanced-memory-mcp" }
    @{ Name = "N: Drive"; Path = "N:\backup\dev\repo-backups\advanced-memory-mcp" }
    @{ Name = "OneDrive"; Path = Join-Path (Join-Path (Join-Path $env:OneDrive "Backup") "repo-backups") "advanced-memory-mcp" }
)

foreach ($location in $paths) {
    $output += "--- $($location.Name) ---"
    $output += "Path: $($location.Path)"
    
    if (Test-Path $location.Path) {
        $zips = Get-ChildItem -Path $location.Path -Filter "*.zip" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
        $output += "Status: EXISTS"
        $output += "Backup files: $($zips.Count)"
        
        if ($zips.Count -gt 0) {
            $latest = $zips[0]
            $output += "Latest backup:"
            $output += "  File: $($latest.Name)"
            $output += "  Size: $([math]::Round($latest.Length/1MB, 2)) MB"
            $output += "  Date: $($latest.LastWriteTime)"
        }
    } else {
        $output += "Status: NOT FOUND"
    }
    $output += ""
}

$outputFile = "backup-verification.txt"
$output | Out-File -FilePath $outputFile -Encoding utf8
Write-Host "Results written to: $outputFile"
$output
