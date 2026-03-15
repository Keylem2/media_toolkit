import customtkinter as ctk
import queue
import threading
import os
import io
from tkinter import filedialog, messagebox

from PIL import Image
from rembg import remove


class BGRemoverTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.input_path = None
        self.result_image = None

        title = ctk.CTkLabel(self, text="Background Remover", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        desc = ctk.CTkLabel(
            self,
            text="Remove image backgrounds locally (outputs PNG)\n⚠ INTERNET REQUIRED: First use downloads AI model (~170 MB)",
            font=ctk.CTkFont(size=13), text_color="orange"
        )
        desc.grid(row=1, column=0, sticky="w", pady=(0, 18))

        # ── Buttons ──
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.select_btn = ctk.CTkButton(btn_frame, text="Select Image", height=40, width=140, command=self._select)
        self.select_btn.pack(side="left", padx=(0, 8))

        self.remove_btn = ctk.CTkButton(
            btn_frame, text="Remove Background", height=40, width=180,
            command=self._start_removal, state="disabled",
            fg_color="#e74c3c", hover_color="#c0392b",
        )
        self.remove_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = ctk.CTkButton(
            btn_frame, text="Clear", height=40, width=80,
            command=self._clear, fg_color=("gray75", "gray28"),
            hover_color=("gray65", "gray35"),
        )
        self.clear_btn.pack(side="left", padx=(0, 8))

        self.save_btn = ctk.CTkButton(
            btn_frame, text="Save PNG", height=40, width=120,
            command=self._save, state="disabled",
            fg_color="#27ae60", hover_color="#1e8449",
        )
        self.save_btn.pack(side="left")

        self.file_label = ctk.CTkLabel(self, text="No image selected", font=ctk.CTkFont(size=12), text_color="gray55")
        self.file_label.grid(row=3, column=0, sticky="w", pady=(0, 10))

        # ── Preview area ──
        preview_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray17"), corner_radius=10)
        preview_frame.grid(row=5, column=0, sticky="nsew")
        preview_frame.grid_columnconfigure((0, 1), weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(preview_frame, text="Original", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, pady=(12, 4))
        ctk.CTkLabel(preview_frame, text="Result", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=1, pady=(12, 4))

        self.orig_preview = ctk.CTkLabel(preview_frame, text="", width=320, height=320)
        self.orig_preview.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="nsew")

        self.result_preview = ctk.CTkLabel(preview_frame, text="", width=320, height=320)
        self.result_preview.grid(row=1, column=1, padx=12, pady=(0, 12), sticky="nsew")

        # ── Status ──
        self.status = ctk.CTkLabel(self, text="Ready", font=ctk.CTkFont(size=12), text_color="gray55")
        self.status.grid(row=6, column=0, sticky="w", pady=(8, 0))

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

    def _show_preview(self, source, label, max_px=320):
        img = Image.open(source) if isinstance(source, str) else source.copy()
        img.thumbnail((max_px, max_px), Image.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        label.configure(image=ctk_img, text="")
        label._ctk_img = ctk_img

    def _clear(self):
        """Clear input and result so user can load a new image."""
        self.input_path = None
        self.result_image = None
        self.file_label.configure(text="No image selected")
        self.remove_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.status.configure(text="Ready")
        self.orig_preview.configure(image=None, text="")
        self.result_preview.configure(image=None, text="")
        if hasattr(self.orig_preview, "_ctk_img"):
            self.orig_preview._ctk_img = None
        if hasattr(self.result_preview, "_ctk_img"):
            self.result_preview._ctk_img = None

    def _select(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")])
        if not path:
            return
        self.input_path = path
        size_kb = os.path.getsize(path) / 1024
        size_str = f"{size_kb / 1024:.1f} MB" if size_kb >= 1024 else f"{size_kb:.0f} KB"
        self.file_label.configure(text=f"{os.path.basename(path)}  ({size_str})")
        self.remove_btn.configure(state="normal")
        self.save_btn.configure(state="disabled")
        self.result_image = None
        self._show_preview(path, self.orig_preview)
        self.result_preview.configure(image=None, text="")

    def _start_removal(self):
        self.remove_btn.configure(state="disabled", text="Processing...")
        self.status.configure(text="Removing background... (first run downloads model ~170 MB)")
        input_path = self.input_path
        threading.Thread(target=self._remove, args=(input_path,), daemon=True).start()

    def _remove(self, input_path):
        try:
            with open(input_path, "rb") as f:
                data = f.read()

            def set_status(t):
                self._ui_queue.put((lambda: self.status.configure(text=t), (), {}))

            set_status("Loading AI model... (~170 MB on first run)")
            try:
                out = remove(data)
            except Exception as model_error:
                error_msg = str(model_error).lower()
                if "download" in error_msg or "url" in error_msg or "network" in error_msg or "connection" in error_msg:
                    raise RuntimeError(
                        "Failed to download AI model (170 MB). "
                        "Please ensure internet connection for first-time setup.\n"
                        f"Error: {model_error}"
                    )
                raise

            if out is None:
                raise RuntimeError(
                    "Background removal returned empty result. "
                    "This may be due to missing AI model or incompatible image format."
                )

            result_image = Image.open(io.BytesIO(out)).convert("RGBA")

            def on_success():
                self.result_image = result_image
                self._show_preview(result_image, self.result_preview)
                self.save_btn.configure(state="normal")
                self.status.configure(text="Background removed!")
            self._ui_queue.put((on_success, (), {}))
        except Exception as e:
            err_msg = str(e)

            def on_error():
                self.status.configure(text=f"Error: {err_msg}")
                messagebox.showerror("Background Removal Error", err_msg, parent=self.winfo_toplevel())
            self._ui_queue.put((on_error, (), {}))
        finally:
            def on_finish():
                self.remove_btn.configure(state="normal", text="Remove Background")
            self._ui_queue.put((on_finish, (), {}))

    def _save(self):
        if self.result_image is None:
            return
        base = os.path.splitext(os.path.basename(self.input_path))[0]
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile=f"{base}_nobg.png",
        )
        if path:
            self.result_image.save(path, "PNG")
            self.status.configure(text=f"Saved to {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Saved to:\n{path}")
