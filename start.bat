@echo off
chcp 65001 >nul 2>&1
title Shuti System
cd /d "%~dp0"

echo ====================================
echo   Starting...
echo ====================================
echo.

rem ============ Backend ============
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend already running
    goto start_frontend
)

echo [..] Starting backend...
start "shuti-backend" /D "%~dp0backend" cmd /c "venv\Scripts\python app.py"

:wait_backend
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% neq 0 goto wait_backend
echo [OK] Backend started

rem ============ Frontend ============
:start_frontend
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend already running
    goto open_browser
)

echo [..] Starting frontend...
start "shuti-frontend" /D "%~dp0frontend" cmd /c "npx vite --host"

:wait_frontend
timeout /t 1 /nobreak >nul
powershell -Command "try { Invoke-WebRequest http://localhost:5173 -UseBasicParsing -TimeoutSec 1 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 goto wait_frontend
echo [OK] Frontend started

rem ============ Open Browser ============
:open_browser
echo.
echo ====================================
echo   Done! Opening browser...
echo ====================================
timeout /t 1 /nobreak >nul
start "" http://localhost:5173
echo.
echo   You can close this window now.
echo.
pause
