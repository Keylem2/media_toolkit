@echo off
echo ============================================
echo    Building Media Toolkit .exe
echo    This may take several minutes...
echo ============================================
echo.

cd /d "%~dp0"

python -m PyInstaller ^
    --noconfirm ^
    --windowed ^
    --name "MediaToolkit" ^
    --distpath "..\dist" ^
    --workpath "..\build" ^
    --collect-all customtkinter ^
    --collect-all rembg ^
    --collect-all onnxruntime ^
    --collect-all pymatting ^
    --copy-metadata pymatting ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=yt_dlp ^
    --hidden-import=scipy ^
    --hidden-import=skimage ^
    --hidden-import=numba ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. Check the output above for details.
    pause
    exit /b 1
)

:: Copy FFmpeg into the dist folder
echo Bundling FFmpeg...
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    copy /Y "$(where ffmpeg)" "..\dist\MediaToolkit\" >nul 2>&1
    copy /Y "$(where ffprobe)" "..\dist\MediaToolkit\" >nul 2>&1
    for /f "tokens=*" %%i in ('where ffmpeg') do copy /Y "%%i" "..\dist\MediaToolkit\" >nul
    for /f "tokens=*" %%i in ('where ffprobe') do copy /Y "%%i" "..\dist\MediaToolkit\" >nul
)

echo.
echo ============================================
echo    Build complete!
echo    Your app is in: ..\dist\MediaToolkit\
echo    Run: ..\dist\MediaToolkit\MediaToolkit.exe
echo ============================================
pause
