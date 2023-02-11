"""Configuration helper module."""

from app.services.settings_manager import SettingsManager

class ConfigManager:
    """Convenience access to application configuration."""

    @staticmethod
    def get_settings() -> SettingsManager:
        return SettingsManager.get_instance()

    @staticmethod
    def get_interval_ms() -> int:
        return SettingsManager.get_instance().interval_ms

    @staticmethod
    def get_first_delay_ms() -> int:
        return SettingsManager.get_instance().first_delay_ms

    @staticmethod
    def should_show_notifications() -> bool:
        return SettingsManager.get_instance().show_notifications

    @staticmethod
    def is_always_on_top() -> bool:
        return SettingsManager.get_instance().always_on_top

    @staticmethod
    def should_stop_on_error() -> bool:
        return SettingsManager.get_instance().stop_on_error
