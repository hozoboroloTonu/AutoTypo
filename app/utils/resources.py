"""Resource resolution helper for standalone and bundled execution."""

import os
import sys
from pathlib import Path

def get_base_dir() -> Path:
    """Returns the base application directory (source directory or PyInstaller bundle/exe directory)."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        # sys.executable is the .exe location
        return Path(sys.executable).resolve().parent
    else:
        # Running from source (root of workspace)
        return Path(__file__).resolve().parent.parent.parent

def get_bundle_dir() -> Path:
    """Returns the internal sys._MEIPASS directory if frozen, else source root."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return get_base_dir()

def get_data_dir() -> Path:
    """Returns the data folder for user persistence (always beside the executable/source)."""
    data_dir = get_base_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_asset_path(filename: str) -> Path:
    """Returns path to an asset file in assets/ directory."""
    # First check bundle dir (for embedded assets)
    bundle_path = get_bundle_dir() / "assets" / filename
    if bundle_path.exists():
        return bundle_path
    # Otherwise check base dir
    base_path = get_base_dir() / "assets" / filename
    return base_path

def get_data_file(filename: str) -> Path:
    """Returns path to a file inside the persistent data directory."""
    return get_data_dir() / filename
