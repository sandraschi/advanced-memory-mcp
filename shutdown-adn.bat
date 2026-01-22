@echo off
echo Shutting down ADN system gracefully...
echo.

REM Default reason
set "REASON=Remote shutdown request"
set "FORCE=false"

REM Parse command line arguments
if "%~1"=="" goto :shutdown
set "REASON=%~1"

if "%~2"=="-force" (
    set "FORCE=true"
    echo Force shutdown requested
)

:shutdown
echo Reason: %REASON%
echo Force: %FORCE%
echo.

REM Try to make the API call using curl (if available)
curl -X POST http://localhost:8001/api/v1/system/graceful-exit ^
  -H "Content-Type: application/json" ^
  -d "{\"reason\":\"%REASON%\",\"force\":%FORCE%}" ^
  2>nul

if %errorlevel% equ 0 (
    echo.
    echo Graceful shutdown request sent successfully!
    echo ADN system should shut down within a few seconds.
) else (
    echo.
    echo Failed to connect to ADN bridge server.
    echo Make sure the ADN system is running.
    echo Start it with: .\run-webapp-clean.bat
)

echo.
pause
