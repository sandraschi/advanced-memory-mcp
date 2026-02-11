@echo off
setlocal
cd /d "%~dp0"

REM Clear reservoir ports 10704, 10733 before start
cd webapp
call npx --yes kill-port 10704 10733 2>nul
cd ..
echo Starting ADN Webapp...
echo This will start all required services automatically.

where node >nul 2>nul
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

for /f "tokens=*" %%v in ('node --version 2^>nul') do set NODEVER=%%v
echo Node.js version: %NODEVER%

if not exist "webapp\node_modules" (
    echo Installing webapp dependencies...
    cd webapp
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install webapp dependencies
        exit /b 1
    )
    cd ..
)

if not exist "node_modules" (
    echo Installing root dependencies...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install root dependencies
        exit /b 1
    )
)

echo Starting ADN Startup Service (port 10733)...
start "ADN Startup Service" node startup-service.js

timeout /t 2 /nobreak >nul

echo Starting ADN Webapp (port 10704)...
echo.
echo ADN Webapp started successfully!
echo Webapp: http://localhost:10704
echo Startup Service: http://localhost:10733
echo.
echo The webapp will automatically start the bridge server when needed.
echo Press Ctrl+C to stop the webapp. Close the "ADN Startup Service" window to stop the backend.
echo.

cd webapp
npm run dev
cd ..

echo Stopping: close the ADN Startup Service window if still open.
endlocal
