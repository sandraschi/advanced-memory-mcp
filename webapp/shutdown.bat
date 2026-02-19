@echo off
REM ADN Webapp - Unified Shutdown Script
REM Kills all ADN webapp processes and frees ports

echo ========================================
echo   ADN Webapp Shutdown
echo ========================================
echo.

REM Try graceful shutdown via bridge API
echo Attempting graceful shutdown via bridge API...
curl -s -X POST http://localhost:10705/api/v1/system/graceful-exit -H "Content-Type: application/json" -d "{\"reason\":\"Manual shutdown\",\"force\":false}" >nul 2>&1
timeout /t 2 /nobreak >nul

REM Kill processes on webapp ports (current + legacy)
for %%p in (10704 10705 10733 10735 17770 8001 8002 8003) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p 2^>nul') do (
        echo Killing PID %%a on port %%p
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Kill ADN-titled windows
taskkill /FI "WINDOWTITLE eq ADN*" /F >nul 2>&1

timeout /t 1 /nobreak >nul

echo.
echo All ADN webapp processes stopped.
echo.
pause
