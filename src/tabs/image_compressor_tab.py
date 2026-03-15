import customtkinter as ctk
import threading
import os
from tkinter import filedialog, messagebox

from PIL import Image

try:
    import settings as app_settings
except ImportError:
    app_settings = None


class ImageCompressorTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        self.input_path = None

        title = ctk.CTkLabel(self, text="Image Compressor", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        desc = ctk.CTkLabel(self, text="Compress images with adjustable quality", font=ctk.CTkFont(size=13), text_color="gray55")
        desc.grid(row=1, column=0, sticky="w", pady=(0, 18))

        # ── File selection ──
        self.select_btn = ctk.CTkButton(self, text="Select Image", height=40, width=150, command=self._select)
        self.select_btn.grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.file_label = ctk.CTkLabel(self, text="No image selected", font=ctk.CTkFont(size=12), text_color="gray55")
        self.file_label.grid(row=3, column=0, sticky="w", pady=(0, 16))

        # ── Quality slider ──
        ctk.CTkLabel(self, text="Quality", font=ctk.CTkFont(size=13, weight="bold")).grid(row=4, column=0, sticky="w", pady=(0, 4))

        slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        slider_frame.grid(row=5, column=0, sticky="ew", pady=(0, 6))
        slider_frame.grid_columnconfigure(0, weight=1)

        self.quality_var = ctk.IntVar(value=80)
        self.slider = ctk.CTkSlider(slider_frame, from_=1, to=100, variable=self.quality_var, command=self._on_slide)
        self.slider.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.quality_label = ctk.CTkLabel(slider_frame, text="80 %", font=ctk.CTkFont(size=15, weight="bold"), width=55)
        self.quality_label.grid(row=0, column=1)

        # Quick-pick quality buttons
        presets_frame = ctk.CTkFrame(self, fg_color="transparent")
        presets_frame.grid(row=6, column=0, sticky="w", pady=(0, 16))
        for val, label in [(25, "Low"), (50, "Medium"), (75, "High"), (90, "Very High"), (100, "Max")]:
            ctk.CTkButton(
                presets_frame, text=f"{label}\n{val}%", width=80, height=44,
                font=ctk.CTkFont(size=11), fg_color=("gray78", "gray28"),
                hover_color=("gray68", "gray38"), text_color=("gray10", "gray90"),
                command=lambda v=val: self._set_quality(v),
            ).pack(side="left", padx=(0, 6))

        # ── Output format ──
        ctk.CTkLabel(self, text="Output Format", font=ctk.CTkFont(size=13, weight="bold")).grid(row=7, column=0, sticky="w", pady=(0, 4))
        self.fmt_var = ctk.StringVar(value="Same as input")
        self.fmt_menu = ctk.CTkOptionMenu(
            self, variable=self.fmt_var,
            values=["Same as input", "JPEG", "PNG", "WEBP"],
            height=34, font=ctk.CTkFont(size=13),
        )
        self.fmt_menu.grid(row=8, column=0, sticky="ew", pady=(0, 16))

        # ── Output folder (read-only display, change via Browse only) ──
        ctk.CTkLabel(self, text="Output Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(row=9, column=0, sticky="w", pady=(0, 4))
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=10, column=0, sticky="ew", pady=(0, 20))
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
        self.compress_btn.grid(row=11, column=0, sticky="ew", pady=(0, 12))

        # ── Status ──
        self.status = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12), text_color="gray55")
        self.status.grid(row=12, column=0, sticky="w")

    # ── helpers ──

    def _on_slide(self, value):
        self.quality_label.configure(text=f"{int(value)} %")

    def _set_quality(self, val):
        self.quality_var.set(val)
        self.slider.set(val)
        self.quality_label.configure(text=f"{val} %")

    def _select(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif")]
        )
        if not path:
            return
        self.input_path = path
        size_kb = os.path.getsize(path) / 1024
        size_str = f"{size_kb / 1024:.1f} MB" if size_kb >= 1024 else f"{size_kb:.0f} KB"
        self.file_label.configure(text=f"{os.path.basename(path)}  ({size_str})")
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
        self.compress_btn.configure(state="disabled", text="Compressing...")
        threading.Thread(target=self._compress, daemon=True).start()

    def _compress(self):
        try:
            quality = self.quality_var.get()
            fmt = self.fmt_var.get()
            img = Image.open(self.input_path)

            basename = os.path.splitext(os.path.basename(self.input_path))[0]
            input_ext = os.path.splitext(self.input_path)[1].lower()

            ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
            ext = ext_map.get(fmt, input_ext) if fmt != "Same as input" else input_ext

            output_path = os.path.join(self.output_var.get(), f"{basename}_compressed{ext}")

            if ext in (".jpg", ".jpeg"):
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            elif ext == ".png":
                compress_level = max(0, min(9, int((100 - quality) / 11)))
                img.save(output_path, "PNG", optimize=True, compress_level=compress_level)
            elif ext == ".webp":
                img.save(output_path, "WEBP", quality=quality)
            else:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(output_path, quality=quality, optimize=True)

            orig_kb = os.path.getsize(self.input_path) / 1024
            final_kb = os.path.getsize(output_path) / 1024
            final_str = f"{final_kb / 1024:.1f} MB" if final_kb >= 1024 else f"{final_kb:.0f} KB"
            reduction = ((orig_kb - final_kb) / orig_kb) * 100 if orig_kb > 0 else 0

            self.status.configure(text=f"Done!  {final_str}  ({reduction:.0f}% smaller)")
            messagebox.showinfo(
                "Success",
                f"Compressed to {final_str}  ({reduction:.0f}% reduction)\n\nSaved:\n{output_path}",
            )
        except Exception as e:
            self.status.configure(text=f"Error: {e}")
            messagebox.showerror("Compression Error", str(e))
        finally:
            self.compress_btn.configure(state="normal", text="Compress")
