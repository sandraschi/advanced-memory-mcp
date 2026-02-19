@echo off
REM ADN Webapp - Unified Start Script (Batch)
REM Starts backend (bridge-server + startup-service) and frontend (Vite dev server)
REM Ports: 10704 (webapp), 10705 (bridge), 10733 (startup service)

echo ========================================
echo   ADN Webapp Startup
echo ========================================
echo.

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL] Node.js not found. Install from https://nodejs.org/
    pause
    exit /b 1
)

REM Kill processes on our ports
echo Clearing ports...
call npx --yes kill-port 10704 10705 10733 >nul 2>&1

REM Install backend dependencies if needed
if not exist "%~dp0backend\node_modules" (
    echo Installing backend dependencies...
    pushd "%~dp0backend"
    call npm install
    popd
)

REM Install frontend dependencies if needed
if not exist "%~dp0frontend\node_modules" (
    echo Installing frontend dependencies...
    pushd "%~dp0frontend"
    call npm install
    popd
)

echo.
echo Starting bridge server (port 10705)...
start "ADN-Bridge-Server" /D "%~dp0backend" node bridge-server.js

timeout /t 2 /nobreak >nul

echo Starting startup service (port 10733)...
start "ADN-Startup-Service" /D "%~dp0backend" node startup-service.js

timeout /t 1 /nobreak >nul

echo Starting frontend (Vite dev server, port 10704)...
start "ADN-Webapp" /D "%~dp0frontend" cmd /c "npm run dev"

echo.
echo ========================================
echo   ADN Webapp Running
echo ========================================
echo   Frontend:  http://localhost:10704
echo   Bridge:    http://localhost:10705
echo   Startup:   http://localhost:10733
echo.
echo Close the terminal windows to stop services.
pause
