@echo off
cd /d "%~dp0src"
echo Launching Media Toolkit...
echo (This window will stay open while the app is running)
echo.
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Something went wrong. See the message above.
    pause
) else (
    echo.
    echo Media Toolkit closed.
    timeout /t 2 >nul
)
