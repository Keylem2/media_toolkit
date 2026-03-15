# Media Toolkit

Open-source desktop app for downloading and processing media from YouTube, TikTok, and local files. **Windows 10/11.**

**Current version: v1.0.1**

---

## Get the app (recommended)

**→ [Download the installer](https://github.com/Keylem2/media_toolkit/releases)** — pick the latest release and grab the setup .exe (e.g. `MediaToolkit-Setup-1.0.1.exe`).

- **Standalone.** Run the installer and you’re done. No Python, FFmpeg, or anything else to install.
- Launch **Media Toolkit** from the Start Menu or desktop shortcut.

---

## Features

| Tool | What it does |
|------|----------------|
| **YouTube Converter** | Download videos or audio (MP4 / MP3), choose quality |
| **TikTok Converter** | Download TikTok videos (always best quality, H.264) or MP3 (320 kbps) |
| **Background Remover** | Remove image backgrounds using AI *(first use downloads a model; internet required)* — Clear to reset and load another image |
| **Video Compressor** | Compress videos to a target file size (two-pass encoding for accurate size) |
| **Image Compressor** | Compress images with adjustable quality |
| **Settings** | Default output folder (editable + Browse), theme (Dark / Light / System), Check for updates, Save |

---

## Run from source

If you want to hack on the code or run without installing:

1. Install **Python 3.11+** and **[FFmpeg](https://www.gyan.dev/ffmpeg/builds/)** on Windows; ensure both `python` and `ffmpeg` are on your PATH. *(The app needs FFmpeg for YouTube/TikTok downloads and video compression.)*
2. Clone this repo and open a terminal in the **`src`** folder (where `requirements.txt` and `main.py` live).
3. Install dependencies (first time only):

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   - From **`src`**: `python main.py`
   - Or from the **project root**: double‑click `run.bat` (Windows).

   **Windows shortcut:** Double‑click `src/install.bat` once to check Python/FFmpeg and run `pip install -r requirements.txt` for you, then use `run.bat` to start the app.

---

## Repo contents

- **`src/`** — Source code (main app, tabs, and settings). The app creates `settings.json` in `src/` when run from source (or in AppData when installed) when you save Settings; it is not required in the repo.
- **`run.bat`** — Run the app from source on Windows
- **`README.md`** — This file

Installers and releases are published on the [Releases](https://github.com/Keylem2/media_toolkit/releases) page.

---

**Like Media Toolkit?** If you find it useful, you can support the project: [PayPal.Me](https://paypal.me/keylem). Totally optional — the app is free either way.
