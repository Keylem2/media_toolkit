import customtkinter as ctk
import os
import webbrowser
from tkinter import filedialog, messagebox, StringVar

try:
    import settings as app_settings
except ImportError:
    app_settings = None


def _default_downloads_path():
    return os.path.join(os.path.expanduser("~"), "Downloads")


class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 4))
        desc = ctk.CTkLabel(
            self, text="Default output folder and app appearance",
            font=ctk.CTkFont(size=13), text_color="gray55",
        )
        desc.grid(row=1, column=0, sticky="w", pady=(0, 24))

        # Default output folder (editable) – always show current value from settings or fallback
        ctk.CTkLabel(self, text="Default output folder", font=ctk.CTkFont(size=13, weight="bold")).grid(row=2, column=0, sticky="w", pady=(0, 4))
        out_frame = ctk.CTkFrame(self, fg_color="transparent")
        out_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        out_frame.grid_columnconfigure(0, weight=1)
        default_out = app_settings.get_default_output_folder() if app_settings else _default_downloads_path()
        self.folder_var = StringVar(value=default_out)
        self.folder_entry = ctk.CTkEntry(out_frame, textvariable=self.folder_var, height=36, font=ctk.CTkFont(size=12))
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        # Force entry to show value (CTkEntry can miss initial StringVar sync when tab is created off-screen)
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, default_out)
        ctk.CTkButton(out_frame, text="Browse", width=90, height=36, command=self._browse).grid(row=0, column=1)

        # Theme
        ctk.CTkLabel(self, text="Theme", font=ctk.CTkFont(size=13, weight="bold")).grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.theme_var = ctk.StringVar(value=app_settings.get_theme().capitalize() if app_settings else "Dark")
        theme_menu = ctk.CTkOptionMenu(
            self, variable=self.theme_var,
            values=["Dark", "Light", "System"],
            height=34, width=160, font=ctk.CTkFont(size=13),
        )
        theme_menu.grid(row=5, column=0, sticky="w", pady=(0, 20))

        # Check for updates
        ctk.CTkButton(self, text="Check for updates", height=40, width=200, command=self._check_updates).grid(row=6, column=0, sticky="w", pady=(0, 8))

        # Save
        self.save_btn = ctk.CTkButton(self, text="Save", height=44, width=140, font=ctk.CTkFont(size=14, weight="bold"), command=self._save)
        self.save_btn.grid(row=7, column=0, sticky="w", pady=(16, 0))

        self.feedback = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="gray55")
        self.feedback.grid(row=8, column=0, sticky="w", pady=(8, 0))

    def on_tab_selected(self):
        """Called when user switches to this tab – refresh folder from settings so we show current value."""
        current = app_settings.get_default_output_folder() if app_settings else _default_downloads_path()
        self.folder_var.set(current)
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, current)

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self.folder_var.get() or None)
        if d:
            self.folder_var.set(d)
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, d)

    def _check_updates(self):
        if not app_settings:
            messagebox.showinfo("Up to date", "Version check not available.", parent=self)
            return
        has_newer, tag = app_settings.check_for_updates()
        if has_newer and tag:
            webbrowser.open("https://github.com/Keylem2/media_toolkit/releases")
            messagebox.showinfo("Update available", f"New version {tag} is available.\nOpening GitHub Releases in your browser.", parent=self)
        else:
            messagebox.showinfo("Up to date", f"You're on the latest version (v{app_settings.APP_VERSION}).", parent=self)

    def _save(self):
        if not app_settings:
            return
        app_settings.set_default_output_folder(self.folder_var.get().strip())
        t = self.theme_var.get().lower()
        app_settings.set_theme(t)
        ctk.set_appearance_mode(t)
        self.feedback.configure(text="Settings saved.")
        self.after(2500, lambda: self.feedback.configure(text=""))
