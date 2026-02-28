@echo off
setlocal

echo Starting Cyber Security Learning Platform...
echo.

:: Check if virtual environment exists and is healthy
set "VENV_HEALTHY=0"
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if not errorlevel 1 set VENV_HEALTHY=1
)

if "%VENV_HEALTHY%"=="0" (
    echo [INFO] Virtual environment not found or broken. Re-creating...
    if exist venv rmdir /s /q venv
    call setup.bat --no-pause
    if errorlevel 1 (
        echo [ERROR] Setup failed!
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo Server starting at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python backend\app.py
