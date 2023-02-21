"""Application lifecycle, startup bootstrap and graceful shutdown manager."""

import os
from typing import Optional
from PySide6.QtCore import QObject
from app.utils.resources import get_data_dir
from app.services.settings_manager import SettingsManager
from app.services.logger import LoggerService
from app.services.session_manager import SessionManager
from app.services.app_state import AppState
from app.utils.constants import APP_NAME, APP_VERSION

class LifecycleManager(QObject):
    """Coordinates application startup, service initialization, and shutdown."""

    _instance = None

    @classmethod
    def get_instance(cls) -> "LifecycleManager":
        if cls._instance is None:
            cls._instance = LifecycleManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._automation_engine = None
        self._keyboard_listener = None

    def initialize(self):
        """Prepares environment, initializes core services and records boot event."""
        # Ensure data folder exists
        get_data_dir()

        # Initialize singletons
        settings = SettingsManager.get_instance()
        logger = LoggerService.get_instance()
        sessions = SessionManager.get_instance()
        state = AppState.get_instance()

        logger.info(f"{APP_NAME} v{APP_VERSION} initialized successfully.")

    def register_engine_and_listener(self, engine, listener):
        self._automation_engine = engine
        self._keyboard_listener = listener

    def shutdown(self):
        """Performs clean and graceful termination."""
        logger = LoggerService.get_instance()
        logger.info("Application shutting down...")

        if self._automation_engine and self._automation_engine.is_running():
            try:
                self._automation_engine.stop()
                if hasattr(self._automation_engine, "wait"):
                    self._automation_engine.wait(2000)
            except Exception as e:
                print(f"[LifecycleManager] Error stopping engine: {e}")

        if self._keyboard_listener:
            try:
                self._keyboard_listener.stop()
            except Exception as e:
                print(f"[LifecycleManager] Error stopping keyboard listener: {e}")

        # Finalize settings save
        SettingsManager.get_instance().save()
