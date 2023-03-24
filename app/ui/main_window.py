"""Main application window: frameless white-glass shell, sidebar navigation, and automation controller."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from app.core.automation_engine import AutomationEngine
from app.core.keyboard_listener import KeyboardApprovalListener
from app.services.app_state import AppState
from app.services.lifecycle_manager import LifecycleManager
from app.services.logger import LoggerService
from app.services.notification_manager import NotificationManager
from app.services.session_manager import SessionManager
from app.services.settings_manager import SettingsManager
from app.ui.pages.about import AboutPage
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.logs import LogsPage
from app.ui.pages.settings import SettingsPage
from app.ui.styles import GLOBAL_STYLESHEET
from app.ui.widgets.notifications import ToastOverlay
from app.ui.widgets.sidebar import SidebarWidget
from app.ui.widgets.title_bar import TitleBar
from app.utils.constants import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    FIRST_MESSAGE_DELAY_MS,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    STATUS_RUNNING,
    STATUS_STOPPED,
)
from app.utils.resources import get_asset_path

PAGE_TITLES = {
    "dashboard": "Dashboard",
    "settings": "Settings",
    "logs": "Logs",
    "about": "About",
}


class MainWindow(QMainWindow):
    """Primary application window and centralized controller."""

    def __init__(self):
        super().__init__()
        self.state = AppState.get_instance()
        self.settings = SettingsManager.get_instance()
        self.logger = LoggerService.get_instance()
        self.sessions = SessionManager.get_instance()
        self.notifier = NotificationManager.get_instance()
        self.lifecycle = LifecycleManager.get_instance()

        self._pending_message: str = ""
        self._pending_target: int = 50
        self._pending_unlimited: bool = False
        self._pending_interval: int = 200

        self._engine = AutomationEngine(self)
        self._listener = KeyboardApprovalListener()

        self.lifecycle.register_engine_and_listener(self._engine, self._listener)

        self._init_window()
        self._init_ui()
        self._bind_signals()

    def _init_window(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

        flags = Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint
        if self.settings.always_on_top:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        icon_path = get_asset_path("app_icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            ico_path = get_asset_path("app_icon.ico")
            if ico_path.exists():
                self.setWindowIcon(QIcon(str(ico_path)))

        self.setStyleSheet(GLOBAL_STYLESHEET)

    def _init_ui(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.root_frame = QFrame(central_widget)
        self.root_frame.setObjectName("rootWindowFrame")
        self.root_frame.setProperty("maximized", "false")
        outer_layout.addWidget(self.root_frame)

        shell_layout = QVBoxLayout(self.root_frame)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)

        # 1. Custom Title Bar
        self.title_bar = TitleBar(self.root_frame)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        shell_layout.addWidget(self.title_bar)

        # 2. Body (Sidebar + Stacked Pages)
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = SidebarWidget(self.root_frame)
        self.sidebar.page_selected.connect(self._on_navigate)
        body_layout.addWidget(self.sidebar)

        self.stacked = QStackedWidget(self.root_frame)
        self.page_dashboard = DashboardPage(self.stacked)
        self.page_settings = SettingsPage(self.stacked)
        self.page_logs = LogsPage(self.stacked)
        self.page_about = AboutPage(self.stacked)

        self.page_index = {
            "dashboard": self.stacked.addWidget(self.page_dashboard),
            "settings": self.stacked.addWidget(self.page_settings),
            "logs": self.stacked.addWidget(self.page_logs),
            "about": self.stacked.addWidget(self.page_about),
        }

        body_layout.addWidget(self.stacked, 1)
        shell_layout.addLayout(body_layout, 1)

        # 3. Toast Notification Overlay
        self.toast_overlay = ToastOverlay(self.root_frame)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self._set_maximized_style(False)
        else:
            self.showMaximized()
            self._set_maximized_style(True)

    def _set_maximized_style(self, is_max: bool):
        val = "true" if is_max else "false"
        self.root_frame.setProperty("maximized", val)
        self.title_bar.setProperty("maximized", val)
        for w in (self.root_frame, self.title_bar):
            w.style().unpolish(w)
            w.style().polish(w)

    def _bind_signals(self):
        self.state.page_changed.connect(self._on_navigate)
        self.state.status_changed.connect(self.sidebar.update_status)

        self.page_dashboard.start_requested.connect(self._on_dashboard_start)
        self.page_dashboard.stop_requested.connect(self._on_dashboard_stop)

        self._listener.approval_hotkey.connect(self.approve_target)
        self._listener.stop_hotkey.connect(self._on_dashboard_stop)

        self._engine.message_sent.connect(self._on_engine_message_sent)
        self._engine.progress_changed.connect(self.state.progress_changed.emit)
        self._engine.status_changed.connect(self.state.set_status)
        self._engine.finished.connect(self._on_engine_finished)
        self._engine.stopped.connect(self._on_engine_stopped)
        self._engine.error.connect(self._on_engine_error)

        self.page_settings.always_on_top_toggled.connect(self._on_always_on_top_toggled)
        self.notifier.toast_requested.connect(self.toast_overlay.show_toast)

    def _on_navigate(self, page_id: str):
        if page_id in self.page_index:
            self.stacked.setCurrentIndex(self.page_index[page_id])
            self.sidebar.set_active_page(page_id)
            self.title_bar.set_page_title(PAGE_TITLES.get(page_id, "Dashboard"))
            self.state.set_current_page(page_id)

    def _on_always_on_top_toggled(self, enabled: bool):
        flags = Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint
        if enabled:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _on_dashboard_start(self, message: str, target_count: int, unlimited: bool, interval_ms: int):
        """START clicked: validates state, enters WAITING FOR APPROVAL and arms listener after safety delay."""
        if self.state.is_running or self.state.waiting_for_approval:
            return

        self._pending_message = message
        self._pending_target = target_count
        self._pending_unlimited = unlimited
        self._pending_interval = interval_ms

        self.state.set_waiting_approval(True)
        self._listener.set_waiting(True)

        QTimer.singleShot(600, self._arm_approval_listener)

        self.logger.info("Waiting for approval.")
        self.notifier.show_info(
            "Waiting for Approval",
            "Select the target field and press Shift + Enter.",
        )

    def _arm_approval_listener(self):
        if self.state.waiting_for_approval:
            self._listener.set_armed(True)

    def approve_target(self):
        """SHIFT + ENTER approval bridge: initiates the real automation session."""
        if not self.state.waiting_for_approval or self._engine.is_running():
            return

        self.state.set_waiting_approval(False)
        self._listener.set_running(True)

        self.state.reset_session_state(
            target_count=self._pending_target,
            unlimited=self._pending_unlimited,
        )
        self.page_dashboard.start_elapsed_timer()

        current_interval = self.settings.interval_ms

        session_id = self.sessions.create_session(
            message=self._pending_message,
            target_count=self._pending_target,
            unlimited=self._pending_unlimited,
            interval_ms=current_interval,
            first_delay_ms=FIRST_MESSAGE_DELAY_MS,
        )
        self.state.set_session_id(session_id)

        self.state.set_status(STATUS_RUNNING)
        self.logger.success("SHIFT + ENTER approval received.")

        self.notifier.show_success(
            "Automation Started",
            f"First message: 1000 ms\nNext messages: {current_interval} ms",
        )

        self._engine.start(
            message=self._pending_message,
            target_count=self._pending_target,
            interval_ms=current_interval,
            unlimited=self._pending_unlimited,
            first_delay_ms=FIRST_MESSAGE_DELAY_MS,
            session_id=session_id,
        )

    def _on_dashboard_stop(self):
        """Handles STOP button or global ESC emergency stop."""
        self._listener.set_waiting(False)
        self._listener.set_running(False)
        self.page_dashboard.stop_elapsed_timer()

        if self._engine.is_running():
            self._engine.stop()
        else:
            if self.state.waiting_for_approval or self.state.is_running:
                self.state.set_status(STATUS_STOPPED)
                self.logger.warning("Automation stopped.")
                self.notifier.show_warning(
                    "Automation Stopped", f"{self.state.sent_count} message(s) were sent."
                )

    def _on_engine_message_sent(self, count: int):
        self.state.set_counts(
            sent=count,
            target=self.state.target_count,
            unlimited=self.state.unlimited,
        )

    def _on_engine_finished(self):
        self._listener.set_waiting(False)
        self._listener.set_running(False)
        self.page_dashboard.stop_elapsed_timer()
        self.notifier.show_success(
            "Automation Completed",
            f"{self.state.sent_count} message(s) sent successfully.",
        )

    def _on_engine_stopped(self):
        self._listener.set_waiting(False)
        self._listener.set_running(False)
        self.page_dashboard.stop_elapsed_timer()
        self.notifier.show_warning(
            "Automation Stopped",
            f"{self.state.sent_count} message(s) were sent.",
        )

    def _on_engine_error(self, err_msg: str):
        self._listener.set_waiting(False)
        self._listener.set_running(False)
        self.page_dashboard.stop_elapsed_timer()
        self.notifier.show_error("Automation Error", f"Typing failed: {err_msg}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.toast_overlay.update_position()

    def closeEvent(self, event):
        self.lifecycle.shutdown()
        event.accept()
