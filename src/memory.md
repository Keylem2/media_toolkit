# Media Toolkit — Project Memory

## What This Project Is
A unified GUI desktop app (Python + CustomTkinter) with 4 media tools:
1. **YouTube Converter** — paste YT link, choose MP3 or MP4, select quality
2. **Background Remover** — local image background removal using rembg/U2Net, outputs PNG
3. **Video Compressor** — compress videos to target file size (24MB / 9MB presets or custom), two-pass x264 encoding with 3% safety margin
4. **Image Compressor** — compress images (JPG, PNG, WEBP) with quality slider (1-100%)

## Folder Structure
```
media_toolkit/
├── memory.md              ← This file (project context for AI sessions)
├── README.txt             ← User-facing guide
├── run.bat                ← Launches app from source (points to src/main.py)
│
├── src/                   ← SOURCE CODE (open this in Cursor to edit)
│   ├── main.py            ← Entry point, sidebar navigation, tab switching
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── youtube_tab.py        ← yt-dlp, prefers H.264+AAC codecs
│   │   ├── bg_remover_tab.py     ← rembg, PIL, side-by-side preview
│   │   ├── video_compressor_tab.py ← FFmpeg two-pass, subprocess
│   │   └── image_compressor_tab.py ← PIL, quality slider + presets
│   ├── requirements.txt
│   ├── run.bat            ← Run from source (needs Python + deps installed)
│   ├── install.bat        ← First-time setup (pip install + FFmpeg via winget)
│   └── build.bat          ← Rebuilds standalone .exe into ../dist/
│
└── dist/
    └── MediaToolkit/      ← STANDALONE APP (no Python needed)
        ├── MediaToolkit.exe
        ├── ffmpeg.exe
        ├── ffprobe.exe
        └── _internal/
```

## Tech Stack
- **Python 3.13** on Windows 11
- **CustomTkinter** — dark-themed modern GUI
- **yt-dlp** — YouTube downloading
- **rembg + onnxruntime** — background removal (U2Net model, ~170MB, downloads on first use)
- **Pillow** — image processing
- **FFmpeg 8.0** — video/audio processing (bundled in dist, installed via winget on dev)
- **PyInstaller** — builds standalone .exe

## Key Decisions & Fixes Applied
1. **YouTube codec fix**: Format string prefers `vcodec^=avc1` (H.264) + `acodec^=mp4a` (AAC) so downloaded MP4s play in Windows Media Player. Falls back to AV1/VP9 only if H.264 unavailable at that resolution. NO re-encoding postprocessor (was causing slow "Processing..." after download).
2. **Video compressor safety margin**: Target size multiplied by 0.97 (3% margin) to guarantee file stays under the limit (e.g., 24MB target → stays under 25MB).
3. **PyInstaller build**: Must include `--collect-all pymatting --copy-metadata pymatting` or the .exe crashes with `PackageNotFoundError: pymatting`. Build also needs `--collect-all customtkinter --collect-all rembg --collect-all onnxruntime`.
4. **FFmpeg must be manually copied** into `dist/MediaToolkit/` after each PyInstaller build (it wipes the dist folder). The `build.bat` attempts to do this automatically.
5. **All long operations** (download, compress, bg removal) run in background threads to keep GUI responsive.

## Build Process
From `src/` folder:
```
python -m PyInstaller --noconfirm --windowed --name "MediaToolkit" --distpath "..\dist" --workpath "..\build" --collect-all customtkinter --collect-all rembg --collect-all onnxruntime --collect-all pymatting --copy-metadata pymatting --hidden-import=PIL --hidden-import=PIL._tkinter_finder --hidden-import=yt_dlp --hidden-import=scipy --hidden-import=skimage --hidden-import=numba main.py
```
Then copy `ffmpeg.exe` and `ffprobe.exe` into `dist/MediaToolkit/`.
Clean up: delete `build/` folder and `.spec` file after build.

## Dependencies (requirements.txt)
```
customtkinter
yt-dlp
rembg[cpu]
Pillow
onnxruntime
```

## Owner Notes
- This is for **personal use only** (not published)
- The dist/MediaToolkit folder is portable — copy to any Windows PC and run without installing anything
- The src/ folder needs Python + `pip install -r requirements.txt` + FFmpeg on PATH to run from source
- Background remover model downloads ~170MB on first use, then works offline
