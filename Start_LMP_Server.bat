@echo off
echo ============================================
echo  IESO LMP Viewer - Starting Server
echo ============================================
echo.

:: Change to the directory where this bat file lives
cd /d "%~dp0"

:: Check server.py exists
if not exist "server.py" (
    echo [ERROR] server.py not found in %~dp0
    echo         Please run install.bat first.
    pause
    exit /b 1
)

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Check if port 5000 is already in use
netstat -ano | findstr ":5000 " | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Port 5000 is already in use.
    echo        The server may already be running.
    echo        Opening browser anyway...
    timeout /t 2 >nul
    start http://localhost:5000
    exit /b 0
)

echo [INFO] Starting IESO LMP server on port 5000...
echo [INFO] Press Ctrl+C in this window to stop the server.
echo.

:: Open browser after 2 second delay (gives Flask time to start)
start /b cmd /c "timeout /t 2 >nul && start http://localhost:5000"

:: Start Flask server (this window stays open as the server console)
python server.py

:: If Flask exits, pause so user can read any error messages
echo.
echo [INFO] Server stopped.
pause
