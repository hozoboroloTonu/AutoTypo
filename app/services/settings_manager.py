"""Persistent application settings manager."""

import json
import os
from typing import Any, Dict
from PySide6.QtCore import QObject, Signal
from app.utils.resources import get_data_file
from app.utils.constants import (
    DEFAULT_INTERVAL_MS,
    DEFAULT_TARGET_COUNT,
    FIRST_MESSAGE_DELAY_MS,
    APPROVAL_HOTKEY
)

DEFAULT_SETTINGS: Dict[str, Any] = {
    "interval_ms": 200,
    "first_delay_ms": FIRST_MESSAGE_DELAY_MS,
    "approval_hotkey": "SHIFT+ENTER",
    "show_notifications": True,
    "always_on_top": False,
    "minimize_to_tray": False,
    "stop_on_error": True,
    "last_message": "Hello from Auto Typo!",
    "last_target_count": DEFAULT_TARGET_COUNT,
    "last_unlimited": False
}

class SettingsManager(QObject):
    """Manages persistent application settings in data/settings.json."""

    settings_changed = Signal(dict)
    
    _instance = None

    @classmethod
    def get_instance(cls) -> "SettingsManager":
        if cls._instance is None:
            cls._instance = SettingsManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._file_path = get_data_file("settings.json")
        self._settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self) -> Dict[str, Any]:
        """Loads settings from file or creates with defaults."""
        if self._file_path.exists():
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._settings.update(data)
            except Exception as e:
                print(f"[SettingsManager] Error loading settings: {e}")
        
        # Enforce locked settings
        self._settings["first_delay_ms"] = FIRST_MESSAGE_DELAY_MS
        self._settings["approval_hotkey"] = "SHIFT+ENTER"
        
        self.save()
        return self._settings

    def save(self) -> bool:
        """Saves current settings to file."""
        try:
            # Enforce locked invariants
            self._settings["first_delay_ms"] = FIRST_MESSAGE_DELAY_MS
            self._settings["approval_hotkey"] = "SHIFT+ENTER"
            
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
            self.settings_changed.emit(self._settings)
            return True
        except Exception as e:
            print(f"[SettingsManager] Error saving settings: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key: str, value: Any, auto_save: bool = True):
        if key == "first_delay_ms":
            value = FIRST_MESSAGE_DELAY_MS
        elif key == "approval_hotkey":
            value = "SHIFT+ENTER"
            
        self._settings[key] = value
        if auto_save:
            self.save()

    def update_all(self, new_settings: Dict[str, Any]):
        for k, v in new_settings.items():
            if k == "first_delay_ms":
                self._settings[k] = FIRST_MESSAGE_DELAY_MS
            elif k == "approval_hotkey":
                self._settings[k] = "SHIFT+ENTER"
            else:
                self._settings[k] = v
        self.save()

    def reset_to_defaults(self):
        self._settings = DEFAULT_SETTINGS.copy()
        self.save()

    @property
    def interval_ms(self) -> int:
        return int(self.get("interval_ms", DEFAULT_INTERVAL_MS))

    @property
    def first_delay_ms(self) -> int:
        return FIRST_MESSAGE_DELAY_MS

    @property
    def show_notifications(self) -> bool:
        return bool(self.get("show_notifications", True))

    @property
    def always_on_top(self) -> bool:
        return bool(self.get("always_on_top", False))

    @property
    def stop_on_error(self) -> bool:
        return bool(self.get("stop_on_error", True))
