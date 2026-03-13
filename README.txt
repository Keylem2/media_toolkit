================================================================
  MEDIA TOOLKIT
================================================================

Open‑source desktop app for downloading and processing media
from YouTube, TikTok and local files (Windows 10/11).

CONTENTS (IN THIS REPO)
----------------------------------------------------------------

  src/        <- Source code (edit and run from here)
  run.bat     <- Helper script to run from source on Windows
  README.txt  <- This file

----------------------------------------------------------------
FEATURES
----------------------------------------------------------------

  - YouTube Converter: download videos or audio (MP4 / MP3)
  - TikTok Converter: download TikTok videos
  - Background Remover: remove image backgrounds using AI
  - Video Compressor: compress videos for smaller file sizes
  - Image Compressor: compress images for web/sharing

All tools are wrapped in a single modern desktop UI.

----------------------------------------------------------------
INSTALL (RECOMMENDED FOR MOST USERS)
----------------------------------------------------------------

1. Download `MediaToolkit-Setup.exe` from the latest GitHub release.
2. Run it and follow the installer steps.
3. Launch **Media Toolkit** from the Start Menu or desktop shortcut.

The installer is standalone and does NOT require Python, pip or any
other tools to be installed.

----------------------------------------------------------------
RUN FROM SOURCE
----------------------------------------------------------------

1. Install Python 3.11+ on Windows and ensure "python" is on PATH.
2. Clone this repo, then in a terminal:

     cd media_toolkit/src
     pip install -r requirements.txt
     run python main.py

3. Or from the project root you can use:

     run.bat