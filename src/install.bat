@echo off
echo ============================================
echo    Media Toolkit - First Time Setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not on PATH.
    echo         Download it from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [OK] Python found.

:: Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] FFmpeg not found. Attempting install via winget...
    winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [ERROR] Could not install FFmpeg automatically.
        echo         Install manually from https://www.gyan.dev/ffmpeg/builds/
        echo         and add it to your system PATH.
        pause
        exit /b 1
    )
    echo [OK] FFmpeg installed. You may need to restart your terminal for PATH to update.
) else (
    echo [OK] FFmpeg found.
)

:: Install Python packages
echo.
echo Installing Python dependencies...
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python packages.
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Setup complete! Run "run.bat" to start.
echo ============================================
pause
