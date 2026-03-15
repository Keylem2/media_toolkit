import customtkinter as ctk
import threading
import os
import subprocess
import sys
import tempfile
from tkinter import filedialog, messagebox

import yt_dlp

try:
    import settings as app_settings
except ImportError:
    app_settings = None


class TikTokTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        # Locate ffmpeg/ffprobe once during initialization
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
        if not self.ffmpeg_path or not self.ffprobe_path:
            missing = []
            if not self.ffmpeg_path:
                missing.append("FFmpeg")
            if not self.ffprobe_path:
                missing.append("FFprobe")
            msg = f"{' and '.join(missing)} not found. H.264 conversion will not work.\n" \
                  "Download from https://ffmpeg.org and add to PATH or place next to the executable."
            print(f"Warning: {msg}")
            self.after(100, lambda: messagebox.showwarning("FFmpeg Missing", msg))

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

        # Format (TikTok always downloads highest quality; no quality selector)
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.grid(row=4, column=0, sticky="ew", pady=(0, 16))
        options_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(options_frame, text="Format", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(0, 6))
        fmt_btn_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        fmt_btn_frame.pack(anchor="w")
        self.format_var = ctk.StringVar(value="mp4")
        self.mp4_radio = ctk.CTkRadioButton(
            fmt_btn_frame, text="MP4 (Video) – best quality", variable=self.format_var,
            value="mp4", font=ctk.CTkFont(size=13),
        )
        self.mp4_radio.pack(side="left", padx=(0, 20))
        self.mp3_radio = ctk.CTkRadioButton(
            fmt_btn_frame, text="MP3 (Audio) – 320 kbps", variable=self.format_var,
            value="mp3", font=ctk.CTkFont(size=13),
        )
        self.mp3_radio.pack(side="left")

        # Output folder (read-only display, change via Browse only)
        ctk.CTkLabel(self, text="Output Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(row=5, column=0, sticky="w", pady=(0, 4))
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=6, column=0, sticky="ew", pady=(0, 20))
        out_frame.grid_columnconfigure(0, weight=1)
        default_out = app_settings.get_default_output_folder() if app_settings else os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_var = ctk.StringVar(value=default_out)
        self.output_label = ctk.CTkLabel(out_frame, text=self._truncate_path(default_out), height=36, font=ctk.CTkFont(size=12), anchor="w")
        self.output_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))
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
    # FFmpeg / FFprobe location helpers (for PyInstaller bundles)
    # ------------------------------------------------------------------
    def _find_ffmpeg(self):
        """Locate ffmpeg executable: first next to executable, then PATH."""
        return self._find_executable("ffmpeg")

    def _find_ffprobe(self):
        """Locate ffprobe executable: first next to executable, then PATH."""
        return self._find_executable("ffprobe")

    def _find_executable(self, name):
        """Search for executable in bundle locations and PATH."""
        candidates = []

        # If running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            # Directory of the executable
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, f"{name}.exe"))
            candidates.append(os.path.join(exe_dir, f"{name}.bat"))
            # Common PyInstaller _internal subfolder
            candidates.append(os.path.join(exe_dir, "_internal", f"{name}.exe"))
            candidates.append(os.path.join(exe_dir, "_internal", f"{name}.bat"))
            # _MEIPASS temp dir (for one-file bundles)
            if hasattr(sys, '_MEIPASS'):
                meipass_dir = sys._MEIPASS
                candidates.append(os.path.join(meipass_dir, f"{name}.exe"))
                candidates.append(os.path.join(meipass_dir, f"{name}.bat"))
                # Some bundles place _internal inside _MEIPASS
                candidates.append(os.path.join(meipass_dir, "_internal", f"{name}.exe"))
                candidates.append(os.path.join(meipass_dir, "_internal", f"{name}.bat"))
                # Or alongside _MEIPASS (parent dir)
                candidates.append(os.path.join(os.path.dirname(meipass_dir), "_internal", f"{name}.exe"))
                candidates.append(os.path.join(os.path.dirname(meipass_dir), "_internal", f"{name}.bat"))
        else:
            # Not frozen: check current script dir
            script_dir = os.path.dirname(os.path.abspath(__file__))
            candidates.append(os.path.join(script_dir, f"{name}.exe"))
            candidates.append(os.path.join(script_dir, f"{name}.bat"))

        for cand in candidates:
            if os.path.isfile(cand):
                return cand

        # Fall back to PATH
        import shutil
        return shutil.which(name)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _truncate_path(path, max_len=48):
        if len(path) <= max_len:
            return path
        return path[: max_len - 3] + "..."

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.output_var.get())
        if d:
            self.output_var.set(d)
            self.output_label.configure(text=self._truncate_path(d))

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste a TikTok link first.")
            return

        # Reset progress bar to determinate mode and zero
        self.progress.configure(mode="determinate")
        self.progress.set(0)
        self.status.configure(text="Starting download...")

        # Disable button and start thread
        self.dl_btn.configure(state="disabled", text="Downloading...")
        threading.Thread(target=self._download, args=(url,), daemon=True).start()

    # --- Thread-safe UI updates ---
    def _update_progress(self, value, text=None):
        self.after(0, lambda: self.progress.set(value))
        if text is not None:
            self.after(0, lambda: self.status.configure(text=text))

    def _start_indeterminate(self, text):
        self.after(0, lambda: self.progress.configure(mode="indeterminate"))
        self.after(0, lambda: self.progress.start())
        if text is not None:
            self.after(0, lambda: self.status.configure(text=text))

    def _stop_indeterminate(self):
        self.after(0, lambda: self.progress.stop())
        self.after(0, lambda: self.progress.configure(mode="determinate"))

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
            out_dir = self.output_var.get()
            # Use a temporary filename with a placeholder to avoid collisions
            temp_template = os.path.join(out_dir, "%(title)s_%(id)s.%(ext)s")

            # Progress hook for yt-dlp (thread-safe updates)
            def hook(d):
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                    done = d.get("downloaded_bytes", 0)
                    if total > 0:
                        pct = done / total
                        self._update_progress(pct, f"Downloading... {pct*100:.1f}%")
                elif d["status"] == "finished":
                    self._update_progress(1.0, "Processing...")

            # Pass ffmpeg location to yt-dlp if we found it (for merging/audio extraction)
            ffmpeg_location = self.ffmpeg_path
            base_opts = {
                "outtmpl": temp_template,
                "progress_hooks": [hook],
                "quiet": True,
                "no_warnings": True,
            }
            if ffmpeg_location:
                base_opts["ffmpeg_location"] = ffmpeg_location

            if fmt == "mp3":
                opts = {
                    **base_opts,
                    "format": "ba[has_watermark=false]/ba",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "320",
                    }],
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    # Get info to find filename
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'video')
                    video_id = info.get('id', '')
                    safe_title = "".join(c for c in title if c.isalnum() or c in " ._-").rstrip()
                    expected_file = os.path.join(out_dir, f"{safe_title}_{video_id}.mp3")
                    final_file = unique_filename(expected_file)
                    
                    ydl.download([url])
                    
                    # Rename if needed
                    if final_file != expected_file and os.path.exists(expected_file):
                        os.rename(expected_file, final_file)
                
                self._show_success(f"Saved to:\n{os.path.dirname(final_file)}")
                # No early finish call - let finally handle it
                return

            # --- MP4 download: always best quality, H.264 for compatibility ---
            # Prefer up to 2160p (4K) H.264, no watermark
            format_spec = (
                "bv*[height<=2160][vcodec^=avc1][has_watermark=false]+ba[acodec^=mp4a]/"
                "b[height<=2160][vcodec^=avc1][has_watermark=false]/"
                "b[height<=2160][has_watermark=false]/"
                "bv*[height<=2160][vcodec^=avc1]+ba/"
                "b[height<=2160][vcodec^=avc1]/"
                "b[height<=2160]/"
                "b"
            )
            opts = {
                **base_opts,
                "format": format_spec,
                "merge_output_format": "mp4",
            }

            # Helper to generate unique filename if already exists
            def unique_filename(path):
                if not os.path.exists(path):
                    return path
                base, ext = os.path.splitext(path)
                counter = 1
                while os.path.exists(f"{base} ({counter}){ext}"):
                    counter += 1
                return f"{base} ({counter}){ext}"
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Extract info to get the final filename
                info = ydl.extract_info(url, download=True)

            # Extract video_id early (needed for fallback search)
            video_id = info.get('id', '')

            # Determine downloaded file path
            if 'requested_downloads' in info and info['requested_downloads']:
                downloaded_file = info['requested_downloads'][0]['filepath']
            else:
                # Fallback: construct from template
                title = info.get('title', 'video')
                safe_title = "".join(c for c in title if c.isalnum() or c in " ._-").rstrip()
                filename = f"{safe_title}_{video_id}.mp4"
                downloaded_file = os.path.join(out_dir, filename)
            
            # Handle duplicate filenames - rename if already exists with different path
            if downloaded_file and os.path.exists(downloaded_file):
                unique_path = unique_filename(downloaded_file)
                if unique_path != downloaded_file:
                    os.rename(downloaded_file, unique_path)
                    downloaded_file = unique_path

            # Verify file exists, else try to find by video_id
            if not os.path.exists(downloaded_file):
                candidates = [f for f in os.listdir(out_dir) if f.endswith('.mp4') and video_id in f]
                if candidates:
                    downloaded_file = os.path.join(out_dir, candidates[0])
                else:
                    raise FileNotFoundError("Could not locate downloaded file.")

            # Ensure H.264 (only if we have ffmpeg and ffprobe)
            if self.ffmpeg_path and self.ffprobe_path:
                if not self._is_h264(downloaded_file):
                    self._start_indeterminate("Converting to H.264...")
                    try:
                        converted = self._convert_to_h264_safe(downloaded_file)
                    finally:
                        self._stop_indeterminate()
                    if converted:
                        # Replace original with converted, clean up temp on failure
                        try:
                            os.replace(converted, downloaded_file)
                        except Exception as e:
                            # Try to delete the temp file if replace failed
                            try:
                                os.unlink(converted)
                            except:
                                pass
                            raise  # Re-raise to outer handler
                        self._update_progress(1.0, "Conversion complete.")
                    else:
                        self._update_progress(1.0, "Conversion failed, keeping original (may be HEVC).")
                else:
                    self._update_progress(1.0, "Already H.264.")
            else:
                self._update_progress(1.0, "FFmpeg not available, skipping conversion.")

            self._show_success(f"Saved to:\n{downloaded_file}")

        except Exception as e:
            self._show_error(str(e))
        finally:
            self._finish_download()

    def _is_h264(self, filepath):
        """Check if video uses H.264 codec using ffprobe."""
        try:
            cmd = [
                self.ffprobe_path, "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                filepath
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
            codec = result.stdout.strip().lower()
            return codec == "h264"
        except (subprocess.CalledProcessError, FileNotFoundError, TypeError):
            # If ffprobe not available, we can't check
            return False

    def _convert_to_h264_safe(self, filepath):
        """Re-encode video to H.264 using a temporary file to avoid collisions."""
        # Create a temporary file in the same directory
        temp_dir = os.path.dirname(filepath)
        with tempfile.NamedTemporaryFile(dir=temp_dir, suffix=".mp4", delete=False) as tmp:
            temp_path = tmp.name
        cmd = [
            self.ffmpeg_path, "-i", filepath,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            "-y", temp_path
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return temp_path
        except (subprocess.CalledProcessError, FileNotFoundError, TypeError):
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return None