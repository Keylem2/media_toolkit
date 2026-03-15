# Media Toolkit

Open-source desktop app for downloading and processing media from YouTube, TikTok, and local files. **Windows 10/11.**

---

## Get the app (recommended)

**→ [Download the installer](https://github.com/Keylem2/media_toolkit/releases)** — pick the latest release and grab `MediaToolkit-Setup.exe`.

- **Standalone.** Run the installer and you’re done. No Python, FFmpeg, or anything else to install.
- Launch **Media Toolkit** from the Start Menu or desktop shortcut.

---

## Features

| Tool | What it does |
|------|----------------|
| **YouTube Converter** | Download videos or audio (MP4 / MP3) |
| **TikTok Converter** | Download TikTok videos |
| **Background Remover** | Remove image backgrounds using AI *(first use downloads a model; internet required)* |
| **Video Compressor** | Compress videos for smaller file size |
| **Image Compressor** | Compress images for web or sharing |

All in one modern desktop UI.

---

## Run from source

If you want to hack on the code or run without installing:

1. Install **Python 3.11+** on Windows and ensure `python` is on your PATH.
2. Clone this repo, then:

   ```bash
   cd media_toolkit/src
   pip install -r requirements.txt
   python main.py
   ```

   Or from the project root: run `run.bat`.

---

## Repo contents

- **`src/`** — Source code (main app and tabs)
- **`run.bat`** — Run the app from source on Windows
- **`README.md`** — This file

Installers and releases are published on the [Releases](https://github.com/Keylem2/media_toolkit/releases) page.
