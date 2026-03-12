import customtkinter as ctk
import threading
import subprocess
import os
import json
from tkinter import filedialog, messagebox


class VideoCompressorTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self.input_path = None
        self.duration = None

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

        # ── Output folder ──
        ctk.CTkLabel(self, text="Output Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(row=7, column=0, sticky="w", pady=(0, 4))
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=8, column=0, sticky="ew", pady=(0, 20))
        out_frame.grid_columnconfigure(0, weight=1)

        self.output_var = ctk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.output_entry = ctk.CTkEntry(out_frame, textvariable=self.output_var, height=36, font=ctk.CTkFont(size=12))
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
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

    # ── helpers ──

    def _get_duration(self, path):
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path],
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

    def _browse(self):
        d = filedialog.askdirectory()
        if d:
            self.output_var.set(d)

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
        threading.Thread(target=self._compress, args=(target_mb,), daemon=True).start()

    def _compress(self, target_mb):
        try:
            duration = self.duration or self._get_duration(self.input_path)
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

            basename = os.path.splitext(os.path.basename(self.input_path))[0]
            output_path = os.path.join(self.output_var.get(), f"{basename}_compressed.mp4")
            passlog = os.path.join(self.output_var.get(), f"{basename}_passlog")

            null_target = "NUL" if os.name == "nt" else "/dev/null"
            cf = subprocess.CREATE_NO_WINDOW

            # Pass 1
            self.status.configure(text="Pass 1 / 2  —  analyzing...")
            self.progress.set(0.15)
            p1 = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", self.input_path,
                    "-c:v", "libx264", "-b:v", str(video_bitrate),
                    "-pass", "1", "-passlogfile", passlog,
                    "-an", "-f", "null", null_target,
                ],
                capture_output=True, text=True, creationflags=cf,
            )
            if p1.returncode != 0:
                raise RuntimeError(f"FFmpeg pass 1 failed:\n{p1.stderr[-800:]}")

            # Pass 2
            self.status.configure(text="Pass 2 / 2  —  encoding...")
            self.progress.set(0.55)
            p2 = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", self.input_path,
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
            self.progress.set(1.0)
            self.status.configure(text=f"Done!  Final size: {final_mb:.2f} MB")
            messagebox.showinfo("Success", f"Compressed to {final_mb:.2f} MB\n\nSaved:\n{output_path}")

        except Exception as e:
            self.status.configure(text=f"Error: {e}")
            messagebox.showerror("Compression Error", str(e))
        finally:
            self.compress_btn.configure(state="normal", text="Compress")
