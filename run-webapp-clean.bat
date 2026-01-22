@echo off
echo Starting ADN Webapp (with zombie cleanup)...
echo.

REM Kill any existing processes on port 17770 (webapp)
echo Killing any existing webapp processes on port 17770...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :17770') do (
    echo Killing process %%a on port 17770
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any existing processes on port 8001 (bridge server)
echo Killing any existing bridge server processes on port 8001...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Killing process %%a on port 8001
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any existing processes on port 8002 (startup service)
echo Killing any existing startup service processes on port 8002...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo Killing process %%a on port 8002
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any existing processes on port 8003 (auto-start service)
echo Killing any existing auto-start service processes on port 8003...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do (
    echo Killing process %%a on port 8003
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill any remaining Node.js processes that might be ADN-related
echo Killing any remaining ADN-related Node.js processes...
taskkill /FI "WINDOWTITLE eq ADN*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq node.exe" /FI "WINDOWTITLE eq ADN*" /F >nul 2>&1

REM Give processes time to die
timeout /t 2 /nobreak >nul

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

echo Starting ADN Webapp on port 17770 (strict port, no hopping)...
cd webapp
start "ADN Webapp" /max npm run dev

cd ..
timeout /t 3 /nobreak >nul

echo.
echo ADN Webapp started successfully!
echo Webapp: http://localhost:17770 (STRICT PORT - no hopping allowed)
echo Auto-Start Service: http://localhost:8003
echo Startup Service: http://localhost:8002
echo.
echo Zombie processes have been killed before startup.
echo Close this window to stop all services.
echo.
pause
