"""Auto Typo: Main Application Entry Point."""

import sys
import os
from pathlib import Path

# Ensure application root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont

from app.utils.constants import APP_NAME, APP_COMPANY, APP_VERSION
from app.utils.resources import get_asset_path
from app.services.lifecycle_manager import LifecycleManager
from app.ui.main_window import MainWindow

def main():
    # Configure High-DPI and Rendering attributes
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(APP_COMPANY)
    app.setApplicationVersion(APP_VERSION)

    # Set default modern UI font
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # Set default taskbar application icon
    icon_path = get_asset_path("app_icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        ico_path = get_asset_path("app_icon.ico")
        if ico_path.exists():
            app.setWindowIcon(QIcon(str(ico_path)))

    # Bootstrap services
    lifecycle = LifecycleManager.get_instance()
    lifecycle.initialize()

    # Launch UI
    window = MainWindow()
    window.show()

    # Run application main loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
