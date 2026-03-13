import customtkinter as ctk
import threading
import os
import sys
import time
import traceback
from tkinter import filedialog, messagebox

import yt_dlp


class YouTubeTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        # Locate ffmpeg (ffprobe not needed for this tab)
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            msg = ("FFmpeg not found. Merging video & audio or extracting MP3 will not work.\n"
                   "Download from https://ffmpeg.org and add to PATH or place next to the executable.")
            print(f"Warning: {msg}")
            self.after(100, lambda: messagebox.showwarning("FFmpeg Missing", msg))

        title = ctk.CTkLabel(self, text="YouTube Converter", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        desc = ctk.CTkLabel(self, text="Download YouTube videos as MP4 or MP3", font=ctk.CTkFont(size=13), text_color="gray55")
        desc.grid(row=1, column=0, sticky="w", pady=(0, 18))

        # URL
        url_label = ctk.CTkLabel(self, text="YouTube URL", font=ctk.CTkFont(size=13, weight="bold"))
        url_label.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.url_entry = ctk.CTkEntry(
            self, placeholder_text="https://www.youtube.com/watch?v=...",
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
            value="mp4", command=self._on_format_change, font=ctk.CTkFont(size=13),
        )
        self.mp4_radio.pack(side="left", padx=(0, 20))
        self.mp3_radio = ctk.CTkRadioButton(
            fmt_btn_frame, text="MP3 (Audio)", variable=self.format_var,
            value="mp3", command=self._on_format_change, font=ctk.CTkFont(size=13),
        )
        self.mp3_radio.pack(side="left")

        # Quality
        qual_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        qual_container.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(qual_container, text="Quality", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 6))

        self.quality_var = ctk.StringVar(value="1080p")
        self.quality_menu = ctk.CTkOptionMenu(
            qual_container, variable=self.quality_var,
            values=["2160p (4K)", "1440p", "1080p", "720p", "480p", "360p"],
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

        # Throttle progress/status updates (except "finished" which must always show)
        self._last_progress_update = 0
        self._progress_throttle = 0.1  # seconds

        # Initial state
        self._on_format_change()

    # ------------------------------------------------------------------
    # FFmpeg location helper
    # ------------------------------------------------------------------
    def _find_ffmpeg(self):
        return self._find_executable("ffmpeg")

    def _find_executable(self, name):
        candidates = []

        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, f"{name}.exe"))
            candidates.append(os.path.join(exe_dir, f"{name}.bat"))
            candidates.append(os.path.join(exe_dir, "_internal", f"{name}.exe"))
            candidates.append(os.path.join(exe_dir, "_internal", f"{name}.bat"))
            if hasattr(sys, '_MEIPASS'):
                meipass_dir = sys._MEIPASS
                candidates.append(os.path.join(meipass_dir, f"{name}.exe"))
                candidates.append(os.path.join(meipass_dir, f"{name}.bat"))
                candidates.append(os.path.join(meipass_dir, "_internal", f"{name}.exe"))
                candidates.append(os.path.join(meipass_dir, "_internal", f"{name}.bat"))
                candidates.append(os.path.join(os.path.dirname(meipass_dir), "_internal", f"{name}.exe"))
                candidates.append(os.path.join(os.path.dirname(meipass_dir), "_internal", f"{name}.bat"))
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            candidates.append(os.path.join(script_dir, f"{name}.exe"))
            candidates.append(os.path.join(script_dir, f"{name}.bat"))

        for cand in candidates:
            if os.path.isfile(cand):
                return cand

        import shutil
        return shutil.which(name)

    # ------------------------------------------------------------------
    # UI update handlers
    # ------------------------------------------------------------------
    def _on_format_change(self):
        """Update quality dropdown values."""
        if self.format_var.get() == "mp3":
            vals = ["320 kbps", "256 kbps", "192 kbps", "128 kbps"]
            self.quality_var.set("320 kbps")
        else:
            vals = ["2160p (4K)", "1440p", "1080p", "720p", "480p", "360p"]
            self.quality_var.set("1080p")
        self.quality_menu.configure(values=vals, state="normal")

    def _browse(self):
        d = filedialog.askdirectory()
        if d:
            self.output_var.set(d)

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste a YouTube link first.")
            return

        # Ensure output directory exists
        out_dir = self.output_var.get()
        os.makedirs(out_dir, exist_ok=True)

        # Reset UI and throttle timer
        self.dl_btn.configure(state="disabled", text="Downloading...")
        self.progress.set(0)
        self.status.configure(text="Starting download...")
        self._last_progress_update = 0  # ensure first hook update isn't throttled

        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    # --- Thread-safe UI updates with throttling ---
    def _update_progress(self, value=None, text=None, force=False):
        """
        Thread‑safe progress/status update with throttling.
        If value is None, the progress bar is not changed.
        If force=True, bypass throttle.
        """
        if force:
            if value is not None:
                self.after(0, lambda: self.progress.set(value))
            if text is not None:
                self.after(0, lambda: self.status.configure(text=text))
            return

        now = time.time()
        if now - self._last_progress_update > self._progress_throttle:
            self._last_progress_update = now
            if value is not None:
                self.after(0, lambda: self.progress.set(value))
            if text is not None:
                self.after(0, lambda: self.status.configure(text=text))

    def _show_error(self, msg):
        self.after(0, lambda: messagebox.showerror("Error", msg))
        self.after(0, lambda: self.status.configure(text=f"Error: {msg}"))

    def _show_success(self, msg):
        self.after(0, lambda: messagebox.showinfo("Success", msg))
        self.after(0, lambda: self.status.configure(text="Download complete!"))

    def _finish_download(self):
        self.after(0, lambda: self.dl_btn.configure(state="normal", text="Download"))

    # --- Core download logic ---
    def _download(self, url):
        try:
            fmt = self.format_var.get()
            quality = self.quality_var.get()
            out_dir = self.output_var.get()

            # Use template with video ID to avoid overwrites
            outtmpl = os.path.join(out_dir, "%(title)s_%(id)s.%(ext)s")

            # Progress hook (thread-safe, throttled)
            def hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    done = d.get("downloaded_bytes", 0)
                    if total > 0:
                        pct = done / total
                        self._update_progress(pct, f"Downloading... {pct*100:.1f}%")
                    else:
                        # Total size unknown – only update status text
                        self._update_progress(text="Downloading...")
                elif d["status"] == "finished":
                    # Force this update to ensure "Processing..." shows immediately
                    self._update_progress(1.0, "Processing...", force=True)

            # Base options – default yt-dlp options for this tab
            base_opts = {
                "outtmpl": outtmpl,
                "progress_hooks": [hook],
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,  # Prevent playlist downloads
            }

            # Tell yt-dlp where ffmpeg is (so it can merge high-quality streams)
            if self.ffmpeg_path:
                if os.path.isabs(self.ffmpeg_path):
                    base_opts["ffmpeg_location"] = os.path.dirname(self.ffmpeg_path)
                else:
                    base_opts["ffmpeg_location"] = self.ffmpeg_path

            if fmt == "mp3":
                bitrate = quality.split()[0]
                opts = {
                    **base_opts,
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": bitrate,
                    }],
                }
            else:
                res_map = {"2160p (4K)": "2160", "1440p": "1440", "1080p": "1080",
                           "720p": "720", "480p": "480", "360p": "360"}
                res = res_map.get(quality, "1080")
                # Force H.264 (avc1) for maximum compatibility with Windows Movies & TV
                opts = {
                    **base_opts,
                    "format": (
                        f"bestvideo[height<={res}][vcodec^=avc1][protocol!=m3u8][protocol!=http_dash_segments]+"
                        f"bestaudio[acodec^=mp4a][protocol!=m3u8][protocol!=http_dash_segments]/"
                        f"bestvideo[height<={res}][vcodec^=avc1]+bestaudio/"
                        f"bestvideo[height<={res}][vcodec^=avc1]/"
                        f"best[height<={res}]"
                    ),
                    "merge_output_format": "mp4",
                }

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            self._show_success(f"Saved to:\n{out_dir}")

        except Exception as e:
            # Log full error details for debugging
            try:
                here = os.path.abspath(__file__)
                app_root = os.path.dirname(os.path.dirname(here))       # .../src
                proj_root = os.path.dirname(app_root)                   # project root
                log_candidates = [
                    os.path.join(app_root, "media_toolkit_log.txt"),
                    os.path.join(proj_root, "media_toolkit_log.txt"),
                ]
                log_path = log_candidates[0]
                for cand in log_candidates:
                    # Prefer a path that is writable; fall back to first if checks fail
                    try:
                        with open(cand, "a", encoding="utf-8") as _f:
                            log_path = cand
                        break
                    except Exception:
                        continue

                with open(log_path, "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 60 + "\n")
                    f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Format: {fmt}\n")
                    f.write(f"Quality: {quality}\n")
                    f.write(f"Output dir: {out_dir}\n")
                    f.write("Exception:\n")
                    f.write("".join(traceback.format_exception(type(e), e, e.__traceback__)))
            except Exception:
                # If logging fails, don't break the UI
                pass

            self._show_error(str(e))
        finally:
            self._finish_download()