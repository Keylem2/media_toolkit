"""App settings: default output folder, theme, and check for updates."""
import os
import sys
import json
import re

APP_VERSION = "1.1.0"  # Bump this with each release
CONFIG_FILENAME = "settings.json"


def _config_dir():
    if getattr(sys, "frozen", False):
        base = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        folder = os.path.join(base, "Media Toolkit")
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
    try:
        os.makedirs(folder, exist_ok=True)
    except Exception:
        folder = os.path.dirname(os.path.abspath(__file__))
    return folder


def _config_path():
    return os.path.join(_config_dir(), CONFIG_FILENAME)


def _load():
    path = _config_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    try:
        with open(_config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_default_output_folder():
    """Default folder for downloads/compressed output. Uses settings or user Downloads."""
    data = _load()
    folder = data.get("default_output_folder", "").strip()
    if folder and os.path.isdir(folder):
        return folder
    return os.path.join(os.path.expanduser("~"), "Downloads")


def set_default_output_folder(path):
    data = _load()
    data["default_output_folder"] = path
    _save(data)


def get_theme():
    """Returns 'dark', 'light', or 'system'."""
    data = _load()
    t = data.get("theme", "dark").lower()
    if t in ("dark", "light", "system"):
        return t
    return "dark"


def set_theme(theme):
    data = _load()
    data["theme"] = theme
    _save(data)


def check_for_updates():
    """
    Returns (has_newer: bool, latest_tag: str or None).
    Fetches latest release tag from GitHub and compares to APP_VERSION.
    """
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api.github.com/repos/Keylem2/media_toolkit/releases/latest",
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        tag = data.get("tag_name", "")  # e.g. "v1.0.2" or "v.1.0.2"
        if not tag:
            return False, None

        def _parse_version_tuple(version_str):
            """
            Parse loose version strings like:
            - 1.1.0
            - v1.1.0
            - v.1.1.0
            Returns a 3-part tuple: (major, minor, patch), or None.
            """
            nums = re.findall(r"\d+", str(version_str))
            if not nums:
                return None
            parts = [int(x) for x in nums[:3]]
            while len(parts) < 3:
                parts.append(0)
            return tuple(parts)

        remote_v = _parse_version_tuple(tag)
        local_v = _parse_version_tuple(APP_VERSION)
        if not remote_v or not local_v:
            # Unknown format: don't force update, but still return tag for info.
            return False, tag

        if remote_v > local_v:
            return True, tag
        return False, tag
    except Exception:
        return False, None
