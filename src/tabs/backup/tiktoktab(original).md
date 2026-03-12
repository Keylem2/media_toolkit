```python
import customtkinter as ctk
import threading
import os
import subprocess
from tkinter import filedialog, messagebox

import yt_dlp


class TikTokTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="TikTok Converter", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        desc = ctk.CTkLabel(self, text="Download TikTok videos without watermark – always H.264 for compatibility", font=ctk.CTkFont(size=13), text_color="gray55")
        desc.grid(row=1, column=0, sticky="w", pady=(0, 18))

        # URL entry
        url_label = ctk.CTkLabel(self, text="TikTok URL", font=ctk.CTkFont(size=13, weight="bold"))
        url_label.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.url_entry = ctk.CTkEntry(
            self, placeholder_text="https://www.tiktok.com/@user/video/123456789...",
            height=40, font=ctk.CTkFont(size=13)
        )
        self.url_entry.grid(row=3, column=0, sticky="ew", pady=(0, 16))

        # Format + Quality row
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.grid(row=4, column=0, sticky="ew", pady=(0, 16))
        options_frame.grid_columnconfigure((0, 1), weight=1)

        # Format
        fmt_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        fmt_container.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(fmt_container, text="Format", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 6))

        self.format_var = ctk.StringVar(value="mp4")
        fmt_btn_frame = ctk.CTkFrame(fmt_container, fg_color="transparent")
        fmt_btn_frame.pack(anchor="w")
        self.mp4_radio = ctk.CTkRadioButton(
            fmt_btn_frame, text="MP4 (Video)", variable=self.format_var,
            value="mp4", command=self._update_quality, font=ctk.CTkFont(size=13),
        )
        self.mp4_radio.pack(side="left", padx=(0, 20))
        self.mp3_radio = ctk.CTkRadioButton(
            fmt_btn_frame, text="MP3 (Audio)", variable=self.format_var,
            value="mp3", command=self._update_quality, font=ctk.CTkFont(size=13),
        )
        self.mp3_radio.pack(side="left")

        # Quality
        qual_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        qual_container.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(qual_container, text="Quality", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 6))

        self.quality_var = ctk.StringVar(value="1080p")
        self.quality_menu = ctk.CTkOptionMenu(
            qual_container, variable=self.quality_var,
            values=["1080p", "720p", "480p", "360p"],
            height=34, font=ctk.CTkFont(size=13),
        )
        self.quality_menu.pack(anchor="w", fill="x")

        # Output folder
        ctk.CTkLabel(self, text="Output Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(row=5, column=0, sticky="w", pady=(0, 4))
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=6, column=0, sticky="ew", pady=(0, 20))
        out_frame.grid_columnconfigure(0, weight=1)

        self.output_var = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.output_entry = ctk.CTkEntry(out_frame, textvariable=self.output_var, height=36, font=ctk.CTkFont(size=12))
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(out_frame, text="Browse", width=90, height=36, command=self._browse).grid(row=0, column=1)

        # Download button
        self.dl_btn = ctk.CTkButton(
            self, text="Download", height=46,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_download,
        )
        self.dl_btn.grid(row=7, column=0, sticky="ew", pady=(0, 12))

        # Progress
        self.progress = ctk.CTkProgressBar(self, height=6)
        self.progress.grid(row=8, column=0, sticky="ew", pady=(0, 6))
        self.progress.set(0)

        self.status = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12), text_color="gray55")
        self.status.grid(row=9, column=0, sticky="w")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _update_quality(self):
        if self.format_var.get() == "mp3":
            vals = ["320 kbps", "256 kbps", "192 kbps", "128 kbps"]
            self.quality_var.set("320 kbps")
        else:
            vals = ["1080p", "720p", "480p", "360p"]
            self.quality_var.set("1080p")
        self.quality_menu.configure(values=vals)

    def _browse(self):
        d = filedialog.askdirectory()
        if d:
            self.output_var.set(d)

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste a TikTok link first.")
            return

        self.dl_btn.configure(state="disabled", text="Downloading...")
        self.progress.set(0)
        self.status.configure(text="Starting download...")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    def _download(self, url):
        try:
            fmt = self.format_var.get()
            quality = self.quality_var.get()
            out_dir = self.output_var.get()
            outtmpl = os.path.join(out_dir, "%(title)s.%(ext)s")

            # Progress hook for yt-dlp
            def hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    done = d.get("downloaded_bytes", 0)
                    if total > 0:
                        pct = done / total
                        self.progress.set(pct)
                        self.status.configure(text=f"Downloading... {pct*100:.1f}%")
                elif d["status"] == "finished":
                    self.progress.set(1.0)
                    self.status.configure(text="Processing...")

            base_opts = {
                "outtmpl": outtmpl,
                "progress_hooks": [hook],
                "quiet": True,
                "no_warnings": True,
            }

            if fmt == "mp3":
                bitrate = quality.split()[0]
                opts = {
                    **base_opts,
                    "format": "ba[has_watermark=false]/ba",  # audio only, prefer no watermark
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate,
                    }],
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
                self.status.configure(text="Download complete!")
                messagebox.showinfo("Success", f"Saved to:\n{out_dir}")
                return

            # --- MP4 download with robust format selection ---
            height = quality.replace("p", "")
            # Format selection chain (tries in order):
            # 1. Best video+audio combined, H.264, no watermark, ≤ height
            # 2. Best video+audio combined, no watermark, ≤ height
            # 3. Best separate video (H.264, no watermark) + best audio (AAC), ≤ height
            # 4. Best separate video (any, no watermark) + best audio, ≤ height
            # 5. Best combined, any codec, no watermark, ≤ height
            # 6. Best combined, H.264, watermark allowed, ≤ height
            # 7. Best combined, any, ≤ height
            format_spec = (
                f"b[height<={height}][vcodec^=avc1][has_watermark=false]/"
                f"b[height<={height}][has_watermark=false]/"
                f"bv*[height<={height}][vcodec^=avc1][has_watermark=false]+ba[acodec^=mp4a]/"
                f"bv*[height<={height}][has_watermark=false]+ba/"
                f"b[height<={height}][vcodec^=avc1]/"
                f"b"
            )
            opts = {
                **base_opts,
                "format": format_spec,
                "merge_output_format": "mp4",
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                # Extract info to get title
                info = ydl.extract_info(url, download=False)
                # Perform download
                ydl.download([url])

            # After download, find the file
            title = info.get('title', 'video')
            # Try to locate downloaded file
            downloaded_file = None
            for f in os.listdir(out_dir):
                if f.startswith(title) and f.endswith('.mp4'):
                    downloaded_file = os.path.join(out_dir, f)
                    break
            if not downloaded_file:
                # fallback to any new mp4 file (crude)
                import glob
                mp4s = glob.glob(os.path.join(out_dir, "*.mp4"))
                if mp4s:
                    downloaded_file = max(mp4s, key=os.path.getctime)

            # If we have a file, ensure it's H.264
            if downloaded_file and os.path.exists(downloaded_file):
                if not self._is_h264(downloaded_file):
                    self.status.configure(text="Converting to H.264 for compatibility...")
                    converted_file = self._convert_to_h264(downloaded_file)
                    if converted_file:
                        # Replace original with converted
                        os.replace(converted_file, downloaded_file)
                    else:
                        self.status.configure(text="Conversion failed, keeping original.")
                else:
                    self.status.configure(text="Already H.264, no conversion needed.")
            else:
                self.status.configure(text="Downloaded file not found, check folder.")

            self.status.configure(text="Download complete!")
            messagebox.showinfo("Success", f"Saved to:\n{out_dir}")

        except Exception as e:
            self.status.configure(text=f"Error: {e}")
            messagebox.showerror("Download Error", str(e))
        finally:
            self.dl_btn.configure(state="normal", text="Download")

    def _is_h264(self, filepath):
        """Check if video uses H.264 codec using ffprobe."""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            codec = result.stdout.strip().lower()
            return codec == "h264"
        except:
            return False  # if ffprobe fails, assume not H.264 to be safe

    def _convert_to_h264(self, filepath):
        """Re-encode video to H.264 using ffmpeg (fast preset)."""
        out_path = filepath.replace(".mp4", "_h264.mp4")
        cmd = [
            "ffmpeg", "-i", filepath,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            "-y", out_path
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return out_path
        except subprocess.CalledProcessError as e:
            print("FFmpeg error:", e.stderr.decode())
            return None
```
