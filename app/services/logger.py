"""Structured JSON logger with real-time Qt signal dispatch."""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal
from app.utils.resources import get_data_file
from app.utils.constants import LOG_INFO, LOG_SUCCESS, LOG_WARNING, LOG_ERROR

MAX_PERSISTED_LOGS = 2000

class LoggerService(QObject):
    """Central logging service persisting to data/logs.json."""
    
    log_added = Signal(dict)
    logs_cleared = Signal()

    _instance = None

    @classmethod
    def get_instance(cls) -> "LoggerService":
        if cls._instance is None:
            cls._instance = LoggerService()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._file_path = get_data_file("logs.json")
        self._logs: List[Dict[str, Any]] = []
        self._load_logs()

    def _load_logs(self):
        if self._file_path.exists():
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._logs = data[-MAX_PERSISTED_LOGS:]
            except Exception as e:
                print(f"[LoggerService] Failed to load logs: {e}")
                self._logs = []

    def _save_logs(self):
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._logs[-MAX_PERSISTED_LOGS:], f, indent=2)
        except Exception as e:
            print(f"[LoggerService] Failed to save logs: {e}")

    def log(self, level: str, message: str, details: Optional[str] = None):
        """Records a log entry, persists it, and notifies UI."""
        now = datetime.now()
        entry = {
            "timestamp": now.strftime("%H:%M:%S"),
            "full_timestamp": now.isoformat(),
            "level": level.upper(),
            "message": message,
            "details": details or ""
        }
        self._logs.append(entry)
        if len(self._logs) > MAX_PERSISTED_LOGS:
            self._logs = self._logs[-MAX_PERSISTED_LOGS:]
            
        self._save_logs()
        self.log_added.emit(entry)

    def info(self, message: str, details: Optional[str] = None):
        self.log(LOG_INFO, message, details)

    def success(self, message: str, details: Optional[str] = None):
        self.log(LOG_SUCCESS, message, details)

    def warning(self, message: str, details: Optional[str] = None):
        self.log(LOG_WARNING, message, details)

    def error(self, message: str, details: Optional[str] = None):
        self.log(LOG_ERROR, message, details)

    def get_all_logs(self, level_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns logs, optionally filtered by level."""
        if not level_filter or level_filter.upper() == "ALL" or level_filter == "All Logs":
            return list(self._logs)
        return [entry for entry in self._logs if entry.get("level") == level_filter.upper()]

    def clear(self):
        """Clears logs history."""
        self._logs.clear()
        self._save_logs()
        self.logs_cleared.emit()
