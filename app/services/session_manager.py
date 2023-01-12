"""Session history manager with persistent JSON storage."""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal
from app.utils.resources import get_data_file
from app.utils.constants import STATUS_COMPLETED, STATUS_STOPPED, STATUS_ERROR

MAX_PERSISTED_SESSIONS = 500

class SessionManager(QObject):
    """Manages automation session history in data/sessions.json."""

    session_added = Signal(dict)
    sessions_cleared = Signal()

    _instance = None

    @classmethod
    def get_instance(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = SessionManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._file_path = get_data_file("sessions.json")
        self._sessions: List[Dict[str, Any]] = []
        self._active_session: Optional[Dict[str, Any]] = None
        self._load_sessions()

    def _load_sessions(self):
        if self._file_path.exists():
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._sessions = data[-MAX_PERSISTED_SESSIONS:]
            except Exception as e:
                print(f"[SessionManager] Failed to load sessions: {e}")
                self._sessions = []

    def _save_sessions(self):
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._sessions[-MAX_PERSISTED_SESSIONS:], f, indent=2)
        except Exception as e:
            print(f"[SessionManager] Failed to save sessions: {e}")

    def create_session(
        self,
        message: str,
        target_count: int,
        unlimited: bool,
        interval_ms: int,
        first_delay_ms: int
    ) -> str:
        """Starts tracking a new session."""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        preview = message[:50] + "..." if len(message) > 50 else message
        
        self._active_session = {
            "session_id": session_id,
            "started_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "start_iso": now.isoformat(),
            "ended_at": "",
            "end_time": "",
            "status": "RUNNING",
            "message_preview": preview,
            "message_length": len(message),
            "target_count": target_count,
            "target": target_count,
            "unlimited": unlimited,
            "interval_ms": interval_ms,
            "first_delay_ms": first_delay_ms,
            "sent_count": 0,
            "duration_seconds": 0,
            "error": ""
        }
        return session_id

    def update_active_sent(self, sent: int):
        if self._active_session:
            self._active_session["sent_count"] = sent

    def finish_session(
        self,
        status: str,
        sent_count: int,
        duration_seconds: int,
        error_msg: str = ""
    ) -> Optional[Dict[str, Any]]:
        """Completes and records the active session."""
        if not self._active_session:
            return None

        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self._active_session["ended_at"] = timestamp_str
        self._active_session["end_time"] = timestamp_str
        self._active_session["status"] = status
        self._active_session["sent_count"] = sent_count
        self._active_session["duration_seconds"] = duration_seconds
        self._active_session["error"] = error_msg

        completed_session = self._active_session
        self._sessions.insert(0, completed_session)  # Newest first
        
        if len(self._sessions) > MAX_PERSISTED_SESSIONS:
            self._sessions = self._sessions[:MAX_PERSISTED_SESSIONS]

        self._save_sessions()
        self._active_session = None
        self.session_added.emit(completed_session)
        return completed_session

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        return list(self._sessions)

    def clear(self):
        self._sessions.clear()
        self._save_sessions()
        self.sessions_cleared.emit()
