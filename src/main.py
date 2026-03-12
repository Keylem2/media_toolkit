import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk

from tabs.youtube_tab import YouTubeTab
from tabs.tiktok_tab import TikTokTab
from tabs.bg_remover_tab import BGRemoverTab
from tabs.video_compressor_tab import VideoCompressorTab
from tabs.image_compressor_tab import ImageCompressorTab


class MediaToolkit(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Media Toolkit")
        self.geometry("1000x660")
        self.minsize(960, 620)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=("gray86", "gray14"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(10, weight=1)

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

        self.tab_defs = [
            ("  YouTube Converter", YouTubeTab),
            ("  TikTok Converter", TikTokTab),
            ("  Background Remover", BGRemoverTab),
            ("  Video Compressor", VideoCompressorTab),
            ("  Image Compressor", ImageCompressorTab),
        ]

        self.nav_buttons = []
        self.tab_frames = []

        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        for i, (label, TabClass) in enumerate(self.tab_defs):
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

            frame = TabClass(self.content)
            self.tab_frames.append(frame)

        version_label = ctk.CTkLabel(
            self.sidebar, text="v1.0  •  FFmpeg powered",
            font=ctk.CTkFont(size=11), text_color="gray45",
        )
        version_label.grid(row=11, column=0, padx=20, pady=(0, 16), sticky="sw")

        self.current_tab_idx = -1
        self.select_tab(0)

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


if __name__ == "__main__":
    app = MediaToolkit()
    app.mainloop()
