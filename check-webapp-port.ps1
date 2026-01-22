# Check webapp port usage and zombie processes
Write-Host "Checking ADN Webapp port 17770..." -ForegroundColor Cyan

# Check if port 17770 is in use
$port17770 = netstat -ano | findstr ":17770"
if ($port17770) {
    Write-Host "Port 17770 is in use:" -ForegroundColor Yellow
    $port17770 | ForEach-Object {
        $line = $_ -split '\s+'
        $processId = $line[-1]
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "  PID $processId : $($process.Name) - $($process.Description)" -ForegroundColor Red
        } else {
            Write-Host "  PID $processId : Unknown process" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Port 17770 is free" -ForegroundColor Green
}

# Check for ADN-related processes
Write-Host "`nChecking for ADN-related processes..." -ForegroundColor Cyan
$adnProcesses = Get-Process | Where-Object {
    $_.Name -like "*node*" -or
    $_.Name -like "*npm*" -or
    $_.Name -like "*vite*" -or
    $_.MainWindowTitle -like "*ADN*"
}

if ($adnProcesses) {
    Write-Host "Found ADN-related processes:" -ForegroundColor Yellow
    $adnProcesses | ForEach-Object {
        Write-Host "  $($_.Name) (PID: $($_.Id)) - $($_.MainWindowTitle)" -ForegroundColor Red
    }
} else {
    Write-Host "No ADN-related processes found" -ForegroundColor Green
}

# Check all Node.js processes
Write-Host "`nAll Node.js processes:" -ForegroundColor Cyan
$nodeProcesses = Get-Process node -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    $nodeProcesses | ForEach-Object {
        Write-Host "  $($_.Name) (PID: $($_.Id)) - $($_.MainWindowTitle)" -ForegroundColor Magenta
    }
} else {
    Write-Host "No Node.js processes running" -ForegroundColor Green
}

Write-Host "`nTo kill all ADN processes, run: .\run-webapp-clean.bat" -ForegroundColor Cyan
