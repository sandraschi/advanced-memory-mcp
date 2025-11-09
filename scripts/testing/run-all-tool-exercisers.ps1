# Runs the tool exerciser Python scripts in sequence with optional skips.
#
# Usage examples:
#   pwsh ./scripts/testing/run-all-tool-exercisers.ps1
#   pwsh ./scripts/testing/run-all-tool-exercisers.ps1 -SkipHeavy
#   pwsh ./scripts/testing/run-all-tool-exercisers.ps1 -SkipNetwork -SkipPackaging

[CmdletBinding()]
param (
    [switch] $SkipHeavy,
    [switch] $SkipNetwork,
    [switch] $SkipPackaging
)

function Invoke-Step {
    param (
        [string] $Name,
        [string[]] $Command
    )

    Write-Host ""
    Write-Host "=== $Name ===" -ForegroundColor Cyan
    Write-Host ("Command: {0}" -f ($Command -join " ")) -ForegroundColor DarkGray

    $executable = $Command[0]
    $arguments = @()
    if ($Command.Length -gt 1) {
        $arguments = $Command[1..($Command.Length - 1)]
    }

    & $executable @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Name (exit code $LASTEXITCODE)"
    }

    Write-Host ("Completed: {0}" -f $Name) -ForegroundColor Green
}

# Core tools exerciser
$coreCommand = @("uv", "run", "python", "scripts/testing/test_core_tools.py")

# Import/export exerciser
$importExportCommand = @("uv", "run", "python", "scripts/testing/test_import_export_tools.py")
if ($SkipHeavy) {
    $importExportCommand += "--skip-heavy"
}

# Skills exerciser
$skillsCommand = @("uv", "run", "python", "scripts/testing/test_skills_tools.py")
if ($SkipNetwork) {
    $skillsCommand += "--skip-network"
}
if ($SkipPackaging) {
    $skillsCommand += "--skip-packaging"
}

# Health/status exerciser
$healthCommand = @("uv", "run", "python", "scripts/testing/test_health_status_tools.py")

try {
    Invoke-Step -Name "Core Tools" -Command $coreCommand
    Invoke-Step -Name "Import/Export" -Command $importExportCommand
    Invoke-Step -Name "Skills" -Command $skillsCommand
    Invoke-Step -Name "Health/Status" -Command $healthCommand

    Write-Host ""
    Write-Host "All tool exercisers completed successfully." -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host $_ -ForegroundColor Red
    exit 1
}

