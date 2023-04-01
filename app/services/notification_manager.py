"""In-app toast notification dispatcher."""

from PySide6.QtCore import QObject, Signal
from app.services.settings_manager import SettingsManager
from app.utils.constants import LOG_INFO, LOG_SUCCESS, LOG_WARNING, LOG_ERROR

class NotificationManager(QObject):
    """Dispatches toast notifications if enabled in user settings."""

    # Signal: (title, message, level_type)
    toast_requested = Signal(str, str, str)

    _instance = None

    @classmethod
    def get_instance(cls) -> "NotificationManager":
        if cls._instance is None:
            cls._instance = NotificationManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._settings = SettingsManager.get_instance()

    def show(self, title: str, message: str, level: str = LOG_INFO):
        """Shows notification if notifications are enabled."""
        if not self._settings.show_notifications:
            return
        self.toast_requested.emit(title, message, level)

    def show_info(self, title: str, message: str):
        self.show(title, message, LOG_INFO)

    def show_success(self, title: str, message: str):
        self.show(title, message, LOG_SUCCESS)

    def show_warning(self, title: str, message: str):
        self.show(title, message, LOG_WARNING)

    def show_error(self, title: str, message: str):
        self.show(title, message, LOG_ERROR)
