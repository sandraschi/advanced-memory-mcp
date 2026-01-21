@echo off
echo Starting ADN Webapp...
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist node_modules (
    echo Installing dependencies...
    npm install
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

if not exist webapp\node_modules (
    echo Installing webapp dependencies...
    cd webapp
    npm install
    cd ..
    if errorlevel 1 (
        echo Error: Failed to install webapp dependencies
        pause
        exit /b 1
    )
)

echo Starting ADN Auto-Start Service...
start "ADN Auto-Start Service" /min node auto-start-service.js

timeout /t 2 /nobreak >nul

echo Starting ADN Startup Service...
start "ADN Startup Service" /min node startup-service.js

timeout /t 2 /nobreak >nul

echo Starting ADN Webapp...
cd webapp
start "ADN Webapp" /max npm run dev

cd ..
timeout /t 3 /nobreak >nul

echo.
echo ADN Webapp started successfully!
echo Webapp: http://localhost:17770
echo Auto-Start Service: http://localhost:8003
echo Startup Service: http://localhost:8002
echo.
echo The webapp will automatically start all required services.
echo Close this window to stop all services.
echo.
pause
