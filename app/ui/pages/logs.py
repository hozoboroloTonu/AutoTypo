"""Logs Page: Polished white-glass activity logs and session history view."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.logger import LoggerService
from app.services.notification_manager import NotificationManager
from app.services.session_manager import SessionManager
from app.ui.styles import apply_card_shadow
from app.ui.widgets.buttons import SecondaryButton
from app.ui.widgets.dialogs import ConfirmationModal
from app.utils.resources import get_asset_path
from app.utils.constants import (
    COLOR_ACCENT,
    COLOR_ERROR,
    COLOR_ERROR_BG,
    COLOR_SUCCESS,
    COLOR_SUCCESS_BG,
    COLOR_TEXT_MUTED,
    COLOR_WARNING,
    COLOR_WARNING_BG,
    LOG_ERROR,
    LOG_INFO,
    LOG_SUCCESS,
    LOG_WARNING,
)


class LogsPage(QWidget):
    """Polished white-glass activity logging and completed sessions view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService.get_instance()
        self.sessions = SessionManager.get_instance()
        self.notifier = NotificationManager.get_instance()

        self._init_ui()
        self._bind_signals()
        self.reload_logs()
        self.reload_sessions()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 28, 40, 28)
        layout.setSpacing(18)

        # 1. Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        lbl_title = QLabel("Logs")
        lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Review activity logs and completed automation sessions.")
        lbl_subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(lbl_subtitle)

        layout.addLayout(header_layout)

        # 2. Segmented Tab Bar (Activity | Sessions)
        tab_bar_row = QHBoxLayout()
        seg_frame = QFrame()
        seg_frame.setObjectName("segmentedTabs")
        seg_frame.setFixedSize(244, 44)
        seg_layout = QHBoxLayout(seg_frame)
        seg_layout.setContentsMargins(4, 4, 4, 4)
        seg_layout.setSpacing(4)

        self.btn_tab_activity = QPushButton("Activity")
        self.btn_tab_activity.setObjectName("segmentTabBtn")
        self.btn_tab_activity.setFixedHeight(36)
        self.btn_tab_activity.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tab_activity.clicked.connect(lambda: self._switch_tab(0))
        seg_layout.addWidget(self.btn_tab_activity, 1)

        self.btn_tab_sessions = QPushButton("Sessions")
        self.btn_tab_sessions.setObjectName("segmentTabBtn")
        self.btn_tab_sessions.setFixedHeight(36)
        self.btn_tab_sessions.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_tab_sessions.clicked.connect(lambda: self._switch_tab(1))
        seg_layout.addWidget(self.btn_tab_sessions, 1)

        tab_bar_row.addWidget(seg_frame)
        tab_bar_row.addStretch()
        layout.addLayout(tab_bar_row)

        # 3. Stacked Content
        self.stack = QStackedWidget()

        # --- TAB 0: Activity Log Card ---
        activity_card = QFrame()
        activity_card.setObjectName("cardFrame")
        apply_card_shadow(activity_card, blur_radius=20, y_offset=8, alpha=12)
        act_layout = QVBoxLayout(activity_card)
        act_layout.setContentsMargins(24, 20, 24, 20)
        act_layout.setSpacing(18)

        tb_layout = QHBoxLayout()
        tb_layout.setSpacing(12)

        self.combo_filter = QComboBox()
        self.combo_filter.setObjectName("filterCombo")
        self.combo_filter.addItems(["All Logs", "INFO", "SUCCESS", "WARNING", "ERROR"])
        self.combo_filter.setFixedSize(176, 40)
        chevron_path = get_asset_path("icons/chevron_down.svg").as_posix()
        self.combo_filter.setStyleSheet(f"""
            QComboBox#filterCombo::down-arrow {{
                image: url("{chevron_path}");
                width: 10px;
                height: 6px;
            }}
        """)
        self.combo_filter.currentIndexChanged.connect(self.reload_logs)
        tb_layout.addWidget(self.combo_filter)

        tb_layout.addStretch()

        btn_refresh_logs = SecondaryButton("Refresh", "refresh.svg")
        btn_refresh_logs.setFixedSize(128, 40)
        btn_refresh_logs.clicked.connect(self.reload_logs)
        tb_layout.addWidget(btn_refresh_logs)

        btn_clear_logs = SecondaryButton("Clear Logs", "trash.svg")
        btn_clear_logs.setFixedSize(148, 40)
        btn_clear_logs.clicked.connect(self._on_clear_logs)
        tb_layout.addWidget(btn_clear_logs)

        act_layout.addLayout(tb_layout)

        self.table_logs = QTableWidget()
        self.table_logs.setObjectName("logsTable")
        self.table_logs.setColumnCount(3)
        self.table_logs.setHorizontalHeaderLabels(["TIME", "LEVEL", "MESSAGE"])
        self.table_logs.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_logs.setColumnWidth(0, 144)
        self.table_logs.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table_logs.setColumnWidth(1, 140)
        self.table_logs.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_logs.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.table_logs.verticalHeader().setVisible(False)
        self.table_logs.verticalHeader().setDefaultSectionSize(30)
        self.table_logs.setAlternatingRowColors(True)
        self.table_logs.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_logs.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_logs.setShowGrid(False)
        self.table_logs.setFocusPolicy(Qt.NoFocus)
        act_layout.addWidget(self.table_logs)

        self.stack.addWidget(activity_card)

        # --- TAB 1: Sessions History Card ---
        sessions_card = QFrame()
        sessions_card.setObjectName("cardFrame")
        apply_card_shadow(sessions_card, blur_radius=20, y_offset=8, alpha=12)
        sess_layout = QVBoxLayout(sessions_card)
        sess_layout.setContentsMargins(24, 20, 24, 20)
        sess_layout.setSpacing(18)

        stb_layout = QHBoxLayout()
        stb_layout.setSpacing(12)
        stb_layout.addStretch()

        btn_refresh_sess = SecondaryButton("Refresh", "refresh.svg")
        btn_refresh_sess.setFixedSize(128, 40)
        btn_refresh_sess.clicked.connect(self.reload_sessions)
        stb_layout.addWidget(btn_refresh_sess)

        btn_clear_sess = SecondaryButton("Clear Sessions", "trash.svg")
        btn_clear_sess.setFixedSize(156, 40)
        btn_clear_sess.clicked.connect(self._on_clear_sessions)
        stb_layout.addWidget(btn_clear_sess)

        sess_layout.addLayout(stb_layout)

        self.sess_scroll = QScrollArea()
        self.sess_scroll.setWidgetResizable(True)
        self.sess_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.sess_container = QWidget()
        self.sess_container_layout = QVBoxLayout(self.sess_container)
        self.sess_container_layout.setContentsMargins(0, 0, 0, 0)
        self.sess_container_layout.setSpacing(12)
        self.sess_scroll.setWidget(self.sess_container)

        sess_layout.addWidget(self.sess_scroll)
        self.stack.addWidget(sessions_card)

        layout.addWidget(self.stack, 1)
        self._switch_tab(0)

    def _switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        self.btn_tab_activity.setProperty("active", "true" if index == 0 else "false")
        self.btn_tab_sessions.setProperty("active", "true" if index == 1 else "false")
        for btn in (self.btn_tab_activity, self.btn_tab_sessions):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _bind_signals(self):
        self.logger.log_added.connect(self._on_log_added)
        self.logger.logs_cleared.connect(self.reload_logs)
        self.sessions.session_added.connect(self._on_session_added)
        self.sessions.sessions_cleared.connect(self.reload_sessions)

    def _on_log_added(self, entry: dict):
        current_filter = self.combo_filter.currentText()
        if current_filter != "All Logs" and entry.get("level") != current_filter:
            return

        row = self.table_logs.rowCount()
        self.table_logs.insertRow(row)
        self._populate_row(row, entry)
        self.table_logs.scrollToBottom()

    def _create_level_badge(self, level: str) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: transparent;")
        w_layout = QHBoxLayout(wrapper)
        w_layout.setContentsMargins(10, 3, 0, 3)
        w_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        bg = "#F0EDF8"
        fg = "#8066B1"
        if level == LOG_SUCCESS:
            bg = COLOR_SUCCESS_BG
            fg = COLOR_SUCCESS
        elif level == LOG_WARNING:
            bg = COLOR_WARNING_BG
            fg = COLOR_WARNING
        elif level == LOG_ERROR:
            bg = COLOR_ERROR_BG
            fg = COLOR_ERROR

        badge = QLabel(f"[{level}]")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(20)
        badge.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                font-size: 11px;
                font-weight: 500;
                border-radius: 6px;
                padding: 0px 10px;
            }}
        """)
        w_layout.addWidget(badge)
        return wrapper

    def _populate_row(self, row: int, entry: dict):
        time_item = QTableWidgetItem(entry.get("timestamp", ""))
        time_item.setForeground(QColor("#747783"))

        level = entry.get("level", LOG_INFO)
        level_item = QTableWidgetItem("")
        msg_item = QTableWidgetItem(entry.get("message", ""))
        msg_item.setForeground(QColor("#343945"))

        self.table_logs.setItem(row, 0, time_item)
        self.table_logs.setItem(row, 1, level_item)
        self.table_logs.setCellWidget(row, 1, self._create_level_badge(level))
        self.table_logs.setItem(row, 2, msg_item)

    def reload_logs(self):
        filter_text = self.combo_filter.currentText()
        logs = self.logger.get_all_logs(filter_text)
        self.table_logs.setRowCount(0)
        self.table_logs.setRowCount(len(logs))
        for row, entry in enumerate(logs):
            self._populate_row(row, entry)
        self.table_logs.scrollToBottom()

    def _on_session_added(self, session: dict):
        self.reload_sessions()

    def reload_sessions(self):
        while self.sess_container_layout.count():
            item = self.sess_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        sessions = self.sessions.get_all_sessions()
        if not sessions:
            lbl_empty = QLabel("No completed automation sessions recorded yet.")
            lbl_empty.setObjectName("helperText")
            lbl_empty.setAlignment(Qt.AlignCenter)
            lbl_empty.setStyleSheet("padding: 48px; font-size: 13px; color: #747783;")
            self.sess_container_layout.addWidget(lbl_empty)
            return

        for sess in sessions:
            card = self._create_session_card(sess)
            self.sess_container_layout.addWidget(card)

        self.sess_container_layout.addStretch()

    def _create_session_card(self, sess: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("innerCardFrame")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        lbl_time = QLabel(sess.get("start_time", ""))
        lbl_time.setStyleSheet("font-size: 13px; font-weight: 600; color: #202633; background: transparent;")
        top_row.addWidget(lbl_time)

        top_row.addStretch()

        status = sess.get("status", "COMPLETED")
        status_color = (
            COLOR_SUCCESS
            if status == "COMPLETED"
            else (COLOR_WARNING if status == "STOPPED" else COLOR_ERROR)
        )
        lbl_status = QLabel(status)
        lbl_status.setStyleSheet(
            f"font-size: 11px; font-weight: 600; color: {status_color}; background: transparent;"
        )
        top_row.addWidget(lbl_status)
        layout.addLayout(top_row)

        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(20)

        unlimited = sess.get("unlimited", False)
        sent = sess.get("sent_count", 0)
        target = sess.get("target", 0)
        sent_str = f"Sent: {sent:,}/Unlimited" if unlimited else f"Sent: {sent:,}/{target:,}"

        lbl_sent = QLabel(sent_str)
        lbl_sent.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLOR_ACCENT}; background: transparent;"
        )
        metrics_row.addWidget(lbl_sent)

        for text in (
            f"Duration: {sess.get('duration_seconds', 0)}s",
            f"Interval: {sess.get('interval_ms', 0)}ms",
            f"First Delay: {sess.get('first_delay_ms', 1000)}ms",
        ):
            lbl = QLabel(text)
            lbl.setObjectName("helperText")
            metrics_row.addWidget(lbl)

        metrics_row.addStretch()
        layout.addLayout(metrics_row)

        preview = sess.get("message_preview", "")
        if preview:
            lbl_preview = QLabel(f'Message: "{preview}"')
            lbl_preview.setStyleSheet(
                f"font-size: 12px; color: {COLOR_TEXT_MUTED}; font-style: italic; background: transparent;"
            )
            layout.addWidget(lbl_preview)

        return card

    def _on_clear_logs(self):
        modal = ConfirmationModal(
            "Clear Activity Logs",
            "Are you sure you want to permanently clear all activity logs?",
            "Clear Logs",
            is_destructive=True,
            parent=self.window(),
        )
        if modal.exec() == ConfirmationModal.Accepted:
            self.logger.clear()
            self.notifier.show_info("Logs Cleared", "Activity logs have been wiped.")

    def _on_clear_sessions(self):
        modal = ConfirmationModal(
            "Clear Session History",
            "Are you sure you want to permanently clear all session history records?",
            "Clear Sessions",
            is_destructive=True,
            parent=self.window(),
        )
        if modal.exec() == ConfirmationModal.Accepted:
            self.sessions.clear()
            self.notifier.show_info("Sessions Cleared", "Session history has been wiped.")
