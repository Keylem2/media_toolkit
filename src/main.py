import sys
import os
import time
import webbrowser
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Messages shown on splash (same duration each, for show — first launch only)
_SPLASH_MESSAGES = [
    "Loading...",
    "Loading interface...",
    "Loading YouTube...",
    "Loading TikTok...",
    "Loading Background Remover...",
    "Loading Video Compressor...",
    "Loading Image Compressor...",
    "Loading Settings...",
    "Preparing interface...",
    "Preparing YouTube...",
    "Preparing TikTok...",
    "Preparing Background Remover...",
    "Preparing Video Compressor...",
    "Preparing Image Compressor...",
    "Preparing Settings...",
    "Almost ready...",
]
_SPLASH_MSG_DURATION = 1.2  # seconds per message (first launch only)


def _first_run_file():
    """Path to a sentinel file that marks 'first run done' (so 2nd+ launch is fast)."""
    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        folder = os.path.join(base, "Media Toolkit")
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, ".first_run_done")


def _is_first_launch():
    return not os.path.isfile(_first_run_file())


def _mark_first_run_done():
    try:
        with open(_first_run_file(), "w"):
            pass
    except Exception:
        pass


# Show splash screen immediately before heavy imports
_splash = None
_splash_status = None
_splash_subtitle = None  # "First launch may take a moment" — only on first run

def _show_splash(first_launch):
    global _splash, _splash_status, _splash_subtitle
    try:
        splash = tk.Tk()
        splash.overrideredirect(True)
        splash.attributes('-topmost', True)
        
        # Center on screen
        w, h = 400, 220
        sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        splash.geometry(f"{w}x{h}+{x}+{y}")
        
        # Dark theme matching app
        splash.configure(bg='#2b2b2b')
        
        tk.Label(splash, text="Media Toolkit", font=('Segoe UI', 24, 'bold'), 
                bg='#2b2b2b', fg='white').pack(expand=True, pady=(20, 5))
        status_lbl = tk.Label(splash, text="Loading...", 
                font=('Segoe UI', 12), bg='#2b2b2b', fg='gray70')
        status_lbl.pack(expand=True)
        _splash_status = status_lbl
        sub_text = "First launch may take a moment" if first_launch else ""
        sub_lbl = tk.Label(splash, text=sub_text, 
                font=('Segoe UI', 9), bg='#2b2b2b', fg='gray50')
        sub_lbl.pack(expand=True, pady=(0, 20))
        _splash_subtitle = sub_lbl
        
        splash.update()
        _splash = splash
    except Exception:
        pass
    return _splash

def _set_splash_status(msg):
    """Update the splash status text so the user sees progress."""
    global _splash, _splash_status
    try:
        if _splash_status is not None:
            _splash_status.config(text=msg)
        if _splash is not None:
            _splash.update()
    except Exception:
        pass


# First launch = show "First launch may take a moment" and fixed delays; 2nd+ = fast, no delays
_first_launch = _is_first_launch()
_splash = _show_splash(_first_launch)
_msg_idx = [0]

def _next_msg():
    i = _msg_idx[0] % len(_SPLASH_MESSAGES)
    _msg_idx[0] += 1
    return _SPLASH_MESSAGES[i]

def _splash_delay():
    """Only wait on first launch; 2nd+ launch stays fast."""
    if _first_launch:
        time.sleep(_SPLASH_MSG_DURATION)

# Heavy imports: on first launch show each message for fixed time; on 2nd+ just update and go
_set_splash_status(_next_msg())
_splash_delay()
_set_splash_status(_next_msg())
_splash_delay()
import customtkinter as ctk

_set_splash_status(_next_msg())
_splash_delay()
from tabs.youtube_tab import YouTubeTab

_set_splash_status(_next_msg())
_splash_delay()
from tabs.tiktok_tab import TikTokTab

_set_splash_status(_next_msg())
_splash_delay()
from tabs.bg_remover_tab import BGRemoverTab

_set_splash_status(_next_msg())
_splash_delay()
from tabs.video_compressor_tab import VideoCompressorTab

_set_splash_status(_next_msg())
_splash_delay()
from tabs.image_compressor_tab import ImageCompressorTab
from tabs.settings_tab import SettingsTab
import settings as app_settings


def _icon_path():
    """Path to the app icon (works when run from source or from PyInstaller bundle)."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "media_toolkit.ico")


class MediaToolkit(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Toolkit")
        self.geometry("1000x660")
        self.minsize(960, 620)

        self._set_window_icon()

        ctk.set_default_color_theme("blue")
        try:
            ctk.set_appearance_mode(app_settings.get_theme())
        except Exception:
            ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar (minimal right border via separator) ──
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=("gray86", "gray14"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(9, weight=1)

        title_label = ctk.CTkLabel(
            self.sidebar, text="  Media Toolkit",
            font=ctk.CTkFont(size=21, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=(28, 8), sticky="w")

        subtitle = ctk.CTkLabel(
            self.sidebar, text="All-in-one media tools",
            font=ctk.CTkFont(size=12), text_color="gray50",
        )
        subtitle.grid(row=1, column=0, padx=22, pady=(0, 28), sticky="w")

        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color="gray30")
        sep.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Tab definitions - all loaded at startup (splash screen covers the wait)
        self.tab_defs = [
            ("  YouTube Converter", lambda: YouTubeTab(self.content)),
            ("  TikTok Converter", lambda: TikTokTab(self.content)),
            ("  Background Remover", lambda: BGRemoverTab(self.content)),
            ("  Video Compressor", lambda: VideoCompressorTab(self.content)),
            ("  Image Compressor", lambda: ImageCompressorTab(self.content)),
            ("  Settings", lambda: SettingsTab(self.content)),
        ]

        self.nav_buttons = []
        self.tab_frames = [None] * len(self.tab_defs)

        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        for i, (label, factory) in enumerate(self.tab_defs):
            btn = ctk.CTkButton(
                self.sidebar, text=label, height=42,
                font=ctk.CTkFont(size=14),
                anchor="w",
                command=lambda idx=i: self.select_tab(idx),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray78", "gray25"),
                corner_radius=8,
            )
            btn.grid(row=3 + i, column=0, padx=12, pady=3, sticky="ew")
            self.nav_buttons.append(btn)

        # Create all tabs: on first launch show each message for same duration; 2nd+ just go
        for i, (label, factory) in enumerate(self.tab_defs):
            _set_splash_status(_next_msg())
            if _first_launch:
                time.sleep(_SPLASH_MSG_DURATION)
            self.tab_frames[i] = factory()

        version_label = ctk.CTkLabel(
            self.sidebar, text="v1.1.0  •  FFmpeg powered",
            font=ctk.CTkFont(size=11), text_color="gray45",
        )
        version_label.grid(row=10, column=0, padx=20, pady=(0, 4), sticky="sw")

        donation_url = "https://paypal.me/keylem"
        ctk.CTkLabel(
            self.sidebar, text="If you find this useful, you can support the project:",
            font=ctk.CTkFont(size=10), text_color="gray50", wraplength=190,
        ).grid(row=11, column=0, padx=20, pady=(0, 2), sticky="sw")
        ctk.CTkButton(
            self.sidebar, text="PayPal.Me", font=ctk.CTkFont(size=10),
            fg_color="transparent", text_color=("gray40", "gray60"),
            hover_color=("gray75", "gray30"), cursor="hand2",
            command=lambda: webbrowser.open(donation_url),
        ).grid(row=12, column=0, padx=20, pady=(0, 16), sticky="sw")

        self.current_tab_idx = -1
        self.select_tab(0)

    def _set_window_icon(self):
        """Set the window title bar icon (taskbar uses .exe icon; title bar needs this)."""
        try:
            path = _icon_path()
            if not os.path.isfile(path):
                return
            self._do_set_icon(path)
            # CustomTkinter can overwrite icon after init; re-apply after a short delay
            self.after(250, self._apply_icon)
        except Exception:
            pass

    def _do_set_icon(self, path):
        """Set icon using iconbitmap or raw wm command (CTk can break iconbitmap on some setups)."""
        try:
            self.iconbitmap(path)
        except Exception:
            try:
                self.tk.call("wm", "iconbitmap", self._w, path)
            except Exception:
                pass

    def _apply_icon(self):
        """Re-apply icon after CTk may have set its default."""
        try:
            path = _icon_path()
            if os.path.isfile(path):
                self._do_set_icon(path)
        except Exception:
            pass

    def select_tab(self, index):
        if index == self.current_tab_idx:
            return

        if self.current_tab_idx >= 0:
            self.tab_frames[self.current_tab_idx].grid_forget()
            self.nav_buttons[self.current_tab_idx].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90"),
            )

        self.tab_frames[index].grid(row=0, column=0, sticky="nsew", padx=28, pady=24)
        self.nav_buttons[index].configure(
            fg_color=("gray78", "gray25"),
            text_color=("gray10", "white"),
        )
        self.current_tab_idx = index
        # Let tab refresh its content when shown (e.g. Settings tab loads current output folder)
        tab = self.tab_frames[index]
        if hasattr(tab, "on_tab_selected"):
            tab.on_tab_selected()


if __name__ == "__main__":
    app = MediaToolkit()
    
    _set_splash_status("Opening Media Toolkit...")
    if _first_launch:
        _mark_first_run_done()  # next launch will be fast
    # Close splash screen when app is ready
    if '_splash' in globals() and _splash is not None:
        try:
            _splash.destroy()
        except Exception:
            pass
    
    app.mainloop()
