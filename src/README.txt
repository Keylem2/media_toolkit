================================================================
  MEDIA TOOLKIT - Source Code
================================================================
Open THIS folder in Cursor / your editor to work on the app.

FILES:
  main.py                        - App entry point + sidebar layout
  tabs/youtube_tab.py            - YouTube Converter feature
  tabs/tiktok_tab.py             - TikTok Converter feature
  tabs/bg_remover_tab.py         - Background Remover feature
  tabs/video_compressor_tab.py   - Video Compressor feature
  tabs/image_compressor_tab.py   - Image Compressor feature
  requirements.txt               - Python dependencies

SCRIPTS (for devs):
  install.bat    - First-time setup (checks Python/FFmpeg, installs deps)
  run.bat        - Run the app from source (needs Python)
  build.bat      - Rebuild the standalone .exe (outputs to ..\dist\MediaToolkit)

Typical dev workflow:
  1) Double-click install.bat  (one time per machine)
  2) Double-click run.bat      (during development)
  3) When ready to ship, run build.bat, then rebuild the installer.

----------------------------------------------------------------
  HOW TO BUILD THE STANDALONE APP (STEP BY STEP)
----------------------------------------------------------------

STEP 1 - Before you build
  • Close Media Toolkit if it's running (so dist folder isn't locked).
  • Don't have dist\MediaToolkit open in File Explorer while building.

STEP 2 - Build the .exe
  • Open a terminal in this folder (src), or double-click build.bat.
  • Run:  build.bat
  • Wait until you see "Build complete!" (can take several minutes).
  • Result: app is in  ..\dist\MediaToolkit\  (MediaToolkit.exe + _internal + FFmpeg files).

STEP 3 - Create the installer (optional)
  • Install Inno Setup if you haven't: https://jrsoftware.org/isinfo.php
  • Open  MediaToolkitInstaller.iss  from the project root (one folder up from src).
  • In Inno Setup: Build → Compile (or press Ctrl+F9).
  • Installer is created in  Output\MediaToolkit-Setup.exe.
  • Use that .exe to install on your PC or share with others.

STEP 4 - Test
  • Run  ..\dist\MediaToolkit\MediaToolkit.exe  to test before making the installer.
  • After compiling in Inno, run the new MediaToolkit-Setup.exe and test the installed app.

================================================================
