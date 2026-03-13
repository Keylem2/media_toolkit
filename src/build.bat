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
    --icon "media_toolkit.ico" ^
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

:: Copy FFmpeg and ALL its DLLs into the dist folder
echo Bundling FFmpeg (exe + DLLs)...
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('where ffmpeg') do (
        echo Found ffmpeg at: %%i
        for %%D in ("%%~dpi.") do (
            echo Copying all files from: %%~fD
            copy /Y "%%~fD\*.exe" "..\dist\MediaToolkit\" >nul
            copy /Y "%%~fD\*.dll" "..\dist\MediaToolkit\" >nul
        )
    )
) else (
    echo [WARNING] FFmpeg not found on PATH. Video merging/compression will not work.
)

echo.
echo ============================================
echo    Build complete!
echo    Your app is in: ..\dist\MediaToolkit\
echo    Run: ..\dist\MediaToolkit\MediaToolkit.exe
echo ============================================
pause
