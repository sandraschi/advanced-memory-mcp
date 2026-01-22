@echo off
echo Killing ADN zombie processes...
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

echo.
echo ADN zombie processes killed!
echo Ports 17770, 8001, 8002, 8003 should now be free.
echo.
