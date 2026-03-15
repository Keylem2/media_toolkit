import customtkinter as ctk
import queue
import threading
import subprocess
import os
import sys
import json
import shutil
from tkinter import filedialog, messagebox

try:
    import settings as app_settings
except ImportError:
    app_settings = None


class VideoCompressorTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self.input_path = None
        self.duration = None

        self.ffmpeg_path = self._find_executable("ffmpeg") or "ffmpeg"
        self.ffprobe_path = self._find_executable("ffprobe") or "ffprobe"

        title = ctk.CTkLabel(self, text="Video Compressor", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        desc = ctk.CTkLabel(
            self, text="Compress videos to a target file size using two-pass encoding",
            font=ctk.CTkFont(size=13), text_color="gray55",
        )
        desc.grid(row=1, column=0, sticky="w", pady=(0, 18))

        # ── File selection ──
        self.select_btn = ctk.CTkButton(self, text="Select Video", height=40, width=150, command=self._select)
        self.select_btn.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.file_label = ctk.CTkLabel(self, text="No video selected", font=ctk.CTkFont(size=12), text_color="gray55")
        self.file_label.grid(row=3, column=0, sticky="w", pady=(0, 2))

        self.info_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="gray55")
        self.info_label.grid(row=4, column=0, sticky="w", pady=(0, 16))

        # ── Target size ──
        ctk.CTkLabel(self, text="Target Size", font=ctk.CTkFont(size=13, weight="bold")).grid(row=5, column=0, sticky="w", pady=(0, 6))

        size_frame = ctk.CTkFrame(self, fg_color="transparent")
        size_frame.grid(row=6, column=0, sticky="ew", pady=(0, 16))

        self.size_var = ctk.StringVar(value="24")

        self.btn_24 = ctk.CTkRadioButton(size_frame, text="24 MB  (under 25 MB)", variable=self.size_var, value="24", font=ctk.CTkFont(size=13))
        self.btn_24.pack(side="left", padx=(0, 24))

        self.btn_9 = ctk.CTkRadioButton(size_frame, text="9 MB  (under 10 MB)", variable=self.size_var, value="9", font=ctk.CTkFont(size=13))
        self.btn_9.pack(side="left", padx=(0, 24))

        self.btn_custom = ctk.CTkRadioButton(size_frame, text="Custom:", variable=self.size_var, value="custom", font=ctk.CTkFont(size=13))
        self.btn_custom.pack(side="left", padx=(0, 6))

        self.custom_entry = ctk.CTkEntry(size_frame, width=70, height=32, placeholder_text="MB")
        self.custom_entry.pack(side="left", padx=(0, 4))

        ctk.CTkLabel(size_frame, text="MB", font=ctk.CTkFont(size=12), text_color="gray55").pack(side="left")

        # ── Output folder (read-only display, change via Browse only) ──
        ctk.CTkLabel(self, text="Output Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(row=7, column=0, sticky="w", pady=(0, 4))
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=8, column=0, sticky="ew", pady=(0, 20))
        out_frame.grid_columnconfigure(0, weight=1)
        default_out = app_settings.get_default_output_folder() if app_settings else os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_var = ctk.StringVar(value=default_out)
        self.output_label = ctk.CTkLabel(out_frame, text=self._truncate_path(default_out), height=36, font=ctk.CTkFont(size=12), anchor="w")
        self.output_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(out_frame, text="Browse", width=90, height=36, command=self._browse).grid(row=0, column=1)

        # ── Compress button ──
        self.compress_btn = ctk.CTkButton(
            self, text="Compress", height=46,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start, state="disabled",
        )
        self.compress_btn.grid(row=9, column=0, sticky="ew", pady=(0, 12))

        # ── Progress ──
        self.progress = ctk.CTkProgressBar(self, height=6)
        self.progress.grid(row=10, column=0, sticky="ew", pady=(0, 6))
        self.progress.set(0)

        self.status = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12), text_color="gray55")
        self.status.grid(row=11, column=0, sticky="w")

        self._ui_queue = queue.Queue()
        self.after(100, self._process_ui_queue)

    def _process_ui_queue(self):
        try:
            while True:
                cb, args, kwargs = self._ui_queue.get_nowait()
                try:
                    cb(*args, **kwargs)
                except Exception:
                    pass
        except queue.Empty:
            pass
        if self.winfo_exists():
            self.after(100, self._process_ui_queue)

    # ── helpers ──

    def _find_executable(self, name):
        candidates = []
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            candidates.append(os.path.join(exe_dir, f"{name}.exe"))
            candidates.append(os.path.join(exe_dir, "_internal", f"{name}.exe"))
            if hasattr(sys, '_MEIPASS'):
                meipass_dir = sys._MEIPASS
                candidates.append(os.path.join(meipass_dir, f"{name}.exe"))
                candidates.append(os.path.join(os.path.dirname(meipass_dir), "_internal", f"{name}.exe"))
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            candidates.append(os.path.join(script_dir, f"{name}.exe"))
        for cand in candidates:
            if os.path.isfile(cand):
                return cand
        return shutil.which(name)

    def _get_duration(self, path):
        try:
            r = subprocess.run(
                [self.ffprobe_path, "-v", "quiet", "-print_format", "json", "-show_format", path],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return float(json.loads(r.stdout)["format"]["duration"])
        except Exception:
            return None

    def _select(self):
        path = filedialog.askopenfilename(
            filetypes=[("Videos", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.mpg *.mpeg *.ts")]
        )
        if not path:
            return
        self.input_path = path
        size_mb = os.path.getsize(path) / (1024 * 1024)
        self.file_label.configure(text=os.path.basename(path))

        self.duration = self._get_duration(path)
        dur_str = f"  |  Duration: {self.duration:.1f}s" if self.duration else ""
        self.info_label.configure(text=f"Size: {size_mb:.1f} MB{dur_str}")
        self.compress_btn.configure(state="normal")

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

    def _start(self):
        if not self.input_path:
            return

        size_val = self.size_var.get()
        if size_val == "custom":
            try:
                target_mb = float(self.custom_entry.get())
            except ValueError:
                messagebox.showwarning("Invalid size", "Enter a valid number in MB.")
                return
        else:
            target_mb = float(size_val)

        self.compress_btn.configure(state="disabled", text="Compressing...")
        self.progress.set(0)
        self.status.configure(text="Preparing...")
        input_path = self.input_path
        duration = self.duration or self._get_duration(input_path)
        out_dir = self.output_var.get()
        ffmpeg_path = self.ffmpeg_path
        threading.Thread(
            target=self._compress,
            args=(target_mb, input_path, duration, out_dir, ffmpeg_path),
            daemon=True,
        ).start()

    def _compress(self, target_mb, input_path, duration, out_dir, ffmpeg_path):
        try:
            duration = duration or self._get_duration(input_path)
            if not duration:
                raise RuntimeError("Cannot determine video duration.")

            # 3% safety margin so the file stays under the limit
            effective_mb = target_mb * 0.97
            target_bits = effective_mb * 8 * 1024 * 1024
            audio_bitrate = 128 * 1024
            video_bitrate = int((target_bits / duration) - audio_bitrate)

            if video_bitrate <= 0:
                raise RuntimeError(
                    f"Target size ({target_mb} MB) is too small for a {duration:.0f}s video. "
                    "Try a larger target or trim the video."
                )

            basename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(out_dir, f"{basename}_compressed.mp4")
            passlog = os.path.join(out_dir, f"{basename}_passlog")

            null_target = "NUL" if os.name == "nt" else "/dev/null"
            cf = subprocess.CREATE_NO_WINDOW

            def ui_status(text, progress=None):
                def do():
                    self.status.configure(text=text)
                    if progress is not None:
                        self.progress.set(progress)
                self._ui_queue.put((do, (), {}))

            # Pass 1
            ui_status("Pass 1 / 2  —  analyzing...", 0.15)
            p1 = subprocess.run(
                [
                    ffmpeg_path, "-y", "-i", input_path,
                    "-c:v", "libx264", "-b:v", str(video_bitrate),
                    "-pass", "1", "-passlogfile", passlog,
                    "-an", "-f", "null", null_target,
                ],
                capture_output=True, text=True, creationflags=cf,
            )
            if p1.returncode != 0:
                raise RuntimeError(f"FFmpeg pass 1 failed:\n{p1.stderr[-800:]}")

            # Pass 2
            ui_status("Pass 2 / 2  —  encoding...", 0.55)
            p2 = subprocess.run(
                [
                    ffmpeg_path, "-y", "-i", input_path,
                    "-c:v", "libx264", "-b:v", str(video_bitrate),
                    "-pass", "2", "-passlogfile", passlog,
                    "-c:a", "aac", "-b:a", "128k",
                    output_path,
                ],
                capture_output=True, text=True, creationflags=cf,
            )
            if p2.returncode != 0:
                raise RuntimeError(f"FFmpeg pass 2 failed:\n{p2.stderr[-800:]}")

            # Cleanup pass log files
            for ext in ("", ".mbtree"):
                log = f"{passlog}-0.log{ext}"
                if os.path.exists(log):
                    os.remove(log)

            final_mb = os.path.getsize(output_path) / (1024 * 1024)

            def on_success():
                self.progress.set(1.0)
                self.status.configure(text=f"Done!  Final size: {final_mb:.2f} MB")
                messagebox.showinfo("Success", f"Compressed to {final_mb:.2f} MB\n\nSaved:\n{output_path}", parent=self.winfo_toplevel())
            self._ui_queue.put((on_success, (), {}))

        except Exception as e:
            err_msg = str(e)

            def on_error():
                self.status.configure(text=f"Error: {err_msg}")
                messagebox.showerror("Compression Error", err_msg, parent=self.winfo_toplevel())
            self._ui_queue.put((on_error, (), {}))
        finally:
            def on_finish():
                self.compress_btn.configure(state="normal", text="Compress")
            self._ui_queue.put((on_finish, (), {}))
