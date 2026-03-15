"""App settings: default output folder, theme, and check for updates."""
import os
import sys
import json

APP_VERSION = "1.0.1"  # Bump this with each release
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
        tag = data.get("tag_name", "")  # e.g. "v1.0.2"
        if not tag:
            return False, None
        # Normalize: strip 'v' and compare
        remote = tag.lstrip("v").strip()
        local = APP_VERSION.strip()
        if remote == local:
            return False, tag
        # Simple compare: split by . and compare numbers
        try:
            r_parts = [int(x) for x in remote.split(".")[:3]]
            l_parts = [int(x) for x in local.split(".")[:3]]
            while len(r_parts) < 3:
                r_parts.append(0)
            while len(l_parts) < 3:
                l_parts.append(0)
            if r_parts > l_parts:
                return True, tag
        except (ValueError, IndexError):
            pass
        return False, tag
    except Exception:
        return False, None
