"""Dashboard Page: Polished white-glass automation control center."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.services.app_state import AppState
from app.services.notification_manager import NotificationManager
from app.services.settings_manager import SettingsManager
from app.ui.styles import apply_card_shadow
from app.ui.widgets.buttons import (
    DestructiveButton,
    PrimaryButton,
    ToggleSwitch,
    load_svg_pixmap,
)
from app.ui.widgets.counters import LiveCharacterCounter, OverviewMetricsBar
from app.utils.constants import (
    COLOR_ACCENT,
    COLOR_SUCCESS,
    COLOR_TEXT_PRIMARY,
    DEFAULT_INTERVAL_MS,
    DEFAULT_TARGET_COUNT,
    FIRST_MESSAGE_DELAY_MS,
    STATUS_COMPLETED,
    STATUS_ERROR,
    STATUS_READY,
    STATUS_RUNNING,
    STATUS_STOPPED,
    STATUS_WAITING,
)


class DashboardPage(QWidget):
    """Polished white-glass dashboard view for configuring and running automation."""

    start_requested = Signal(str, int, bool, int)  # message, target_count, unlimited, interval_ms
    stop_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = AppState.get_instance()
        self.settings = SettingsManager.get_instance()
        self.notifier = NotificationManager.get_instance()

        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.setInterval(1000)
        self._elapsed_timer.timeout.connect(self._on_elapsed_tick)
        self._elapsed_seconds = 0

        self._init_ui()
        self._bind_state()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 28, 40, 32)
        layout.setSpacing(20)

        # 1. Page Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        lbl_title = QLabel("Dashboard")
        lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Configure your message automation and start instantly.")
        lbl_subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(lbl_subtitle)

        layout.addLayout(header_layout)

        # 2. Approval Banner Card (Hidden unless waiting for approval)
        self.approval_banner = QFrame()
        self.approval_banner.setObjectName("approvalBanner")
        banner_layout = QVBoxLayout(self.approval_banner)
        banner_layout.setContentsMargins(20, 14, 20, 14)
        banner_layout.setSpacing(4)

        lbl_appr_title = QLabel("WAITING FOR APPROVAL")
        lbl_appr_title.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {COLOR_ACCENT}; letter-spacing: 0.8px; background: transparent;"
        )
        banner_layout.addWidget(lbl_appr_title)

        lbl_appr_desc = QLabel(
            "Select the target text field in your target application and press Shift + Enter."
        )
        lbl_appr_desc.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; background: transparent;"
        )
        banner_layout.addWidget(lbl_appr_desc)

        self.lbl_appr_hint = QLabel("Ready - press Shift + Enter to begin.")
        self.lbl_appr_hint.setStyleSheet(
            f"font-size: 12px; font-weight: 600; color: {COLOR_SUCCESS}; background: transparent;"
        )
        banner_layout.addWidget(self.lbl_appr_hint)

        self.approval_banner.hide()
        layout.addWidget(self.approval_banner)

        # 3. Unified Overview Metrics Bar
        self.metrics_bar = OverviewMetricsBar()
        layout.addWidget(self.metrics_bar)

        # 4. Main Two-Column Content Area
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(24)

        # --- LEFT COLUMN (Message Editor + Session Progress) ---
        left_col = QVBoxLayout()
        left_col.setSpacing(24)

        # Card A: Message to type
        msg_card = QFrame()
        msg_card.setObjectName("cardFrame")
        apply_card_shadow(msg_card, blur_radius=20, y_offset=8, alpha=12)
        msg_layout = QVBoxLayout(msg_card)
        msg_layout.setContentsMargins(24, 22, 24, 24)
        msg_layout.setSpacing(14)

        msg_header = QHBoxLayout()
        msg_header.setSpacing(10)

        lbl_msg_icon = QLabel()
        lbl_msg_icon.setFixedSize(20, 20)
        lbl_msg_icon.setStyleSheet("background: transparent;")
        lbl_msg_icon.setPixmap(load_svg_pixmap("card_message.svg", QSize(20, 20)))
        msg_header.addWidget(lbl_msg_icon)

        lbl_msg_title = QLabel("Message to type")
        lbl_msg_title.setObjectName("cardHeading")
        msg_header.addWidget(lbl_msg_title)
        msg_header.addStretch()

        self.char_counter = LiveCharacterCounter()
        msg_header.addWidget(self.char_counter)
        msg_layout.addLayout(msg_header)

        lbl_msg_sub = QLabel("Enter the exact message the automation should type.")
        lbl_msg_sub.setObjectName("helperText")
        msg_layout.addWidget(lbl_msg_sub)

        # Editor Frame with Plain text footer & resize grip
        editor_box = QFrame()
        editor_box.setObjectName("messageEditorBox")
        editor_box.setMinimumHeight(166)
        editor_layout = QVBoxLayout(editor_box)
        editor_layout.setContentsMargins(16, 14, 14, 10)
        editor_layout.setSpacing(6)

        self.txt_message = QPlainTextEdit()
        self.txt_message.setObjectName("messagePlainEdit")
        self.txt_message.setPlaceholderText("Type your message here...")
        self.txt_message.setMinimumHeight(110)
        default_msg = self.settings.get("last_message", "Hello from Auto Typo!")
        self.txt_message.setPlainText(default_msg)
        self.txt_message.textChanged.connect(self._on_message_text_changed)
        editor_layout.addWidget(self.txt_message, 1)

        editor_footer = QHBoxLayout()
        editor_footer.setContentsMargins(2, 0, 0, 0)
        lbl_plain = QLabel("Plain text")
        lbl_plain.setStyleSheet("font-size: 10px; color: #747783; background: transparent;")
        editor_footer.addWidget(lbl_plain)
        editor_footer.addStretch()

        lbl_grip = QLabel()
        lbl_grip.setFixedSize(12, 12)
        lbl_grip.setStyleSheet("background: transparent;")
        lbl_grip.setPixmap(load_svg_pixmap("resize_grip.svg", QSize(12, 12)))
        editor_footer.addWidget(lbl_grip)
        editor_layout.addLayout(editor_footer)

        msg_layout.addWidget(editor_box)
        self.char_counter.update_count(len(self.txt_message.toPlainText()))
        left_col.addWidget(msg_card)

        # Card B: Session progress
        prog_card = QFrame()
        prog_card.setObjectName("cardFrame")
        apply_card_shadow(prog_card, blur_radius=20, y_offset=8, alpha=12)
        prog_layout = QVBoxLayout(prog_card)
        prog_layout.setContentsMargins(24, 22, 24, 22)
        prog_layout.setSpacing(14)

        prog_header = QHBoxLayout()
        prog_header.setSpacing(10)

        lbl_prog_icon = QLabel()
        lbl_prog_icon.setFixedSize(20, 20)
        lbl_prog_icon.setStyleSheet("background: transparent;")
        lbl_prog_icon.setPixmap(load_svg_pixmap("card_progress.svg", QSize(20, 20)))
        prog_header.addWidget(lbl_prog_icon)

        lbl_prog_title = QLabel("Session progress")
        lbl_prog_title.setObjectName("cardHeading")
        prog_header.addWidget(lbl_prog_title)
        prog_header.addStretch()

        self.lbl_prog_pct = QLabel("0%")
        self.lbl_prog_pct.setStyleSheet(
            f"font-size: 18px; font-weight: 600; color: {COLOR_ACCENT}; background: transparent;"
        )
        prog_header.addWidget(self.lbl_prog_pct)
        prog_layout.addLayout(prog_header)

        initial_target = self.settings.get("last_target_count", DEFAULT_TARGET_COUNT)
        self.lbl_prog_sub = QLabel(f"0 of {initial_target:,} messages sent")
        self.lbl_prog_sub.setObjectName("helperText")
        prog_layout.addWidget(self.lbl_prog_sub)

        prog_layout.addSpacing(8)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self._progress_anim = QPropertyAnimation(self.progress_bar, b"value", self)
        self._progress_anim.setDuration(240)
        self._progress_anim.setEasingCurve(QEasingCurve.OutCubic)
        prog_layout.addWidget(self.progress_bar)

        prog_layout.addSpacing(10)

        prog_div = QFrame()
        prog_div.setObjectName("subtleDivider")
        prog_layout.addWidget(prog_div)

        # Metadata footer: Elapsed 00:00 | Next sent 200 ms
        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)

        lbl_clock = QLabel()
        lbl_clock.setFixedSize(16, 16)
        lbl_clock.setStyleSheet("background: transparent;")
        lbl_clock.setPixmap(load_svg_pixmap("elapsed_clock.svg", QSize(16, 16)))
        meta_row.addWidget(lbl_clock)

        lbl_elapsed_cap = QLabel("Elapsed")
        lbl_elapsed_cap.setStyleSheet("font-size: 11px; color: #747783; background: transparent;")
        meta_row.addWidget(lbl_elapsed_cap)

        self.lbl_elapsed_val = QLabel("00:00")
        self.lbl_elapsed_val.setStyleSheet(
            "font-size: 13px; font-weight: 500; color: #515D70; background: transparent;"
        )
        meta_row.addWidget(self.lbl_elapsed_val)

        meta_row.addSpacing(12)
        meta_sep = QFrame()
        meta_sep.setFixedSize(1, 14)
        meta_sep.setStyleSheet("background-color: #E5E8F0; border: none;")
        meta_row.addWidget(meta_sep)
        meta_row.addSpacing(12)

        self.lbl_next_cap = QLabel("Next sent")
        self.lbl_next_cap.setStyleSheet("font-size: 11px; color: #747783; background: transparent;")
        meta_row.addWidget(self.lbl_next_cap)

        self.lbl_next_val = QLabel(f"{self.settings.interval_ms} ms")
        self.lbl_next_val.setStyleSheet(
            "font-size: 13px; font-weight: 500; color: #515D70; background: transparent;"
        )
        meta_row.addWidget(self.lbl_next_val)

        meta_row.addStretch()
        prog_layout.addLayout(meta_row)

        left_col.addWidget(prog_card)
        left_col.addStretch()
        columns_layout.addLayout(left_col, 61)

        # --- RIGHT COLUMN (Automation settings) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(0)

        settings_card = QFrame()
        settings_card.setObjectName("cardFrame")
        apply_card_shadow(settings_card, blur_radius=20, y_offset=8, alpha=12)
        sc_layout = QVBoxLayout(settings_card)
        sc_layout.setContentsMargins(24, 22, 24, 24)
        sc_layout.setSpacing(16)

        # Card Header
        sc_header_block = QVBoxLayout()
        sc_header_block.setSpacing(6)

        sc_header = QHBoxLayout()
        sc_header.setSpacing(10)
        lbl_sc_icon = QLabel()
        lbl_sc_icon.setFixedSize(20, 20)
        lbl_sc_icon.setStyleSheet("background: transparent;")
        lbl_sc_icon.setPixmap(load_svg_pixmap("card_settings.svg", QSize(20, 20)))
        sc_header.addWidget(lbl_sc_icon)

        lbl_sc_title = QLabel("Automation settings")
        lbl_sc_title.setObjectName("cardHeading")
        sc_header.addWidget(lbl_sc_title)
        sc_header.addStretch()
        sc_header_block.addLayout(sc_header)

        lbl_sc_sub = QLabel("Fine-tune every keystroke.")
        lbl_sc_sub.setObjectName("helperText")
        sc_header_block.addWidget(lbl_sc_sub)
        sc_layout.addLayout(sc_header_block)

        div1 = QFrame()
        div1.setObjectName("subtleDivider")
        sc_layout.addWidget(div1)

        # How many messages?
        count_block = QVBoxLayout()
        count_block.setSpacing(8)
        lbl_count = QLabel("How many messages?")
        lbl_count.setObjectName("fieldLabel")
        count_block.addWidget(lbl_count)

        count_input_wrap = QFrame()
        count_input_wrap.setObjectName("inputContainer")
        count_input_wrap.setFixedHeight(44)
        count_input_row = QHBoxLayout(count_input_wrap)
        count_input_row.setContentsMargins(14, 0, 14, 0)

        self.spin_count = QSpinBox()
        self.spin_count.setObjectName("cleanSpinBox")
        self.spin_count.setRange(1, 1000000)
        self.spin_count.setValue(initial_target)
        self.spin_count.valueChanged.connect(self._on_target_count_changed)
        count_input_row.addWidget(self.spin_count, 1)

        lbl_msg_unit = QLabel("messages")
        lbl_msg_unit.setStyleSheet("font-size: 11px; color: #747783; background: transparent;")
        count_input_row.addWidget(lbl_msg_unit)
        count_block.addWidget(count_input_wrap)
        sc_layout.addLayout(count_block)

        # Unlimited messages toggle row
        unlim_row = QHBoxLayout()
        lbl_unlim = QLabel("Unlimited messages")
        lbl_unlim.setStyleSheet("font-size: 12px; color: #5A6577; background: transparent;")
        unlim_row.addWidget(lbl_unlim)
        unlim_row.addStretch()

        self.chk_unlimited = ToggleSwitch(width=38, height=22)
        self.chk_unlimited.setChecked(self.settings.get("last_unlimited", False))
        self.chk_unlimited.toggled.connect(self._on_unlimited_toggled)
        unlim_row.addWidget(self.chk_unlimited)
        sc_layout.addLayout(unlim_row)

        div2 = QFrame()
        div2.setObjectName("subtleDivider")
        sc_layout.addWidget(div2)

        # Message interval & First message delay (side-by-side)
        timing_row = QHBoxLayout()
        timing_row.setSpacing(16)

        # Left: Message interval
        int_col = QVBoxLayout()
        int_col.setSpacing(8)
        lbl_int = QLabel("Message interval")
        lbl_int.setObjectName("fieldLabel")
        int_col.addWidget(lbl_int)

        int_wrap = QFrame()
        int_wrap.setObjectName("inputContainer")
        int_wrap.setFixedHeight(44)
        int_inner = QHBoxLayout(int_wrap)
        int_inner.setContentsMargins(14, 0, 14, 0)

        self.spin_interval = QSpinBox()
        self.spin_interval.setObjectName("cleanSpinBox")
        self.spin_interval.setRange(10, 60000)
        self.spin_interval.setValue(self.settings.interval_ms)
        self.spin_interval.valueChanged.connect(self._on_interval_changed)
        int_inner.addWidget(self.spin_interval, 1)

        lbl_int_ms = QLabel("ms")
        lbl_int_ms.setStyleSheet("font-size: 11px; color: #747783; background: transparent;")
        int_inner.addWidget(lbl_int_ms)
        int_col.addWidget(int_wrap)
        timing_row.addLayout(int_col, 1)

        # Right: First message delay
        fmd_col = QVBoxLayout()
        fmd_col.setSpacing(8)
        lbl_fmd = QLabel("First message delay")
        lbl_fmd.setObjectName("fieldLabel")
        fmd_col.addWidget(lbl_fmd)

        fmd_wrap = QFrame()
        fmd_wrap.setObjectName("readOnlyContainer")
        fmd_wrap.setFixedHeight(44)
        fmd_inner = QHBoxLayout(fmd_wrap)
        fmd_inner.setContentsMargins(14, 0, 14, 0)

        lbl_fmd_val = QLabel(str(FIRST_MESSAGE_DELAY_MS))
        lbl_fmd_val.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #202633; background: transparent;"
        )
        fmd_inner.addWidget(lbl_fmd_val)
        fmd_inner.addStretch()

        lbl_fmd_ms = QLabel("ms")
        lbl_fmd_ms.setStyleSheet("font-size: 11px; color: #747783; background: transparent;")
        fmd_inner.addWidget(lbl_fmd_ms)
        fmd_col.addWidget(fmd_wrap)
        timing_row.addLayout(fmd_col, 1)

        sc_layout.addLayout(timing_row)

        # Approval shortcut
        sc_block = QVBoxLayout()
        sc_block.setSpacing(8)
        lbl_sc_field = QLabel("Approval shortcut")
        lbl_sc_field.setObjectName("fieldLabel")
        sc_block.addWidget(lbl_sc_field)

        sc_wrap = QFrame()
        sc_wrap.setObjectName("inputContainer")
        sc_wrap.setFixedHeight(44)
        sc_inner = QHBoxLayout(sc_wrap)
        sc_inner.setContentsMargins(14, 0, 14, 0)
        sc_inner.setSpacing(10)

        lbl_kb = QLabel()
        lbl_kb.setFixedSize(18, 18)
        lbl_kb.setStyleSheet("background: transparent;")
        lbl_kb.setPixmap(load_svg_pixmap("shortcut_keyboard.svg", QSize(18, 18)))
        sc_inner.addWidget(lbl_kb)

        lbl_shift = QLabel("Shift")
        lbl_shift.setStyleSheet(
            "font-size: 12px; font-weight: 500; color: #657084; background: transparent;"
        )
        sc_inner.addWidget(lbl_shift)

        lbl_plus = QLabel("+")
        lbl_plus.setStyleSheet("font-size: 12px; color: #747783; background: transparent;")
        sc_inner.addWidget(lbl_plus)

        lbl_enter = QLabel("Enter")
        lbl_enter.setStyleSheet(
            "font-size: 12px; font-weight: 500; color: #657084; background: transparent;"
        )
        sc_inner.addWidget(lbl_enter)
        sc_inner.addStretch()

        sc_block.addWidget(sc_wrap)
        sc_layout.addLayout(sc_block)

        sc_layout.addSpacing(8)

        # Controls: Start automation + Stop
        btn_row = QHBoxLayout()
        btn_row.setSpacing(14)

        self.btn_start = PrimaryButton("Start automation", "play.svg")
        self.btn_start.setFixedHeight(54)
        self.btn_start.clicked.connect(self._on_start_clicked)
        btn_row.addWidget(self.btn_start, 2)

        self.btn_stop = DestructiveButton("Stop", "stop.svg")
        self.btn_stop.setFixedHeight(54)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._on_stop_clicked)
        btn_row.addWidget(self.btn_stop, 1)

        sc_layout.addLayout(btn_row)

        right_col.addWidget(settings_card)
        right_col.addStretch()
        columns_layout.addLayout(right_col, 39)

        layout.addLayout(columns_layout)
        layout.addStretch()

        scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

        self._on_unlimited_toggled(self.chk_unlimited.isChecked())

    def _bind_state(self):
        self.state.status_changed.connect(self._on_state_status_changed)
        self.state.counts_changed.connect(self._on_state_counts_changed)
        self.state.progress_changed.connect(self._on_state_progress_changed)
        self.state.approval_state_changed.connect(self._on_approval_state_changed)
        self.settings.settings_changed.connect(self._on_settings_external_update)

    def _on_message_text_changed(self):
        text = self.txt_message.toPlainText()
        self.char_counter.update_count(len(text))
        self.settings.set("last_message", text, auto_save=False)

    def _on_target_count_changed(self, val: int):
        if not self.chk_unlimited.isChecked():
            self.metrics_bar.slot_target.set_value(f"{val:,}")
            self.lbl_prog_sub.setText(f"{self.state.sent_count:,} of {val:,} messages sent")
            self.settings.set("last_target_count", val, auto_save=False)

    def _on_unlimited_toggled(self, checked: bool):
        is_idle = self.state.status in (STATUS_READY, STATUS_COMPLETED, STATUS_STOPPED, STATUS_ERROR)
        self.spin_count.setEnabled(not checked and is_idle)
        self.settings.set("last_unlimited", checked, auto_save=False)

        if checked:
            self.metrics_bar.slot_target.set_value("∞")
            self.metrics_bar.slot_progress.set_value("∞")
            self.lbl_prog_pct.setText("∞")
            self.lbl_prog_sub.setText(f"{self.state.sent_count:,} messages sent (Unlimited)")
        else:
            target_val = self.spin_count.value()
            self.metrics_bar.slot_target.set_value(f"{target_val:,}")
            self.metrics_bar.slot_progress.set_value(f"{self.state.progress}%")
            self.lbl_prog_pct.setText(f"{self.state.progress}%")
            self.lbl_prog_sub.setText(f"{self.state.sent_count:,} of {target_val:,} messages sent")

    def _on_interval_changed(self, val: int):
        self.settings.set("interval_ms", val, auto_save=True)
        if self.state.status != STATUS_WAITING:
            self.lbl_next_cap.setText("Next sent")
            self.lbl_next_val.setText(f"{val} ms")

    def _on_settings_external_update(self, settings_dict: dict):
        new_interval = settings_dict.get("interval_ms", DEFAULT_INTERVAL_MS)
        if self.spin_interval.value() != new_interval:
            self.spin_interval.blockSignals(True)
            self.spin_interval.setValue(new_interval)
            self.spin_interval.blockSignals(False)
            if self.state.status != STATUS_WAITING:
                self.lbl_next_cap.setText("Next sent")
                self.lbl_next_val.setText(f"{new_interval} ms")

    def _on_start_clicked(self):
        msg = self.txt_message.toPlainText()
        if not msg or not msg.strip():
            self.notifier.show_warning(
                "Empty Message", "Please enter the message you want to automate before starting."
            )
            return

        target = self.spin_count.value()
        unlimited = self.chk_unlimited.isChecked()
        if not unlimited and target <= 0:
            self.notifier.show_warning(
                "Invalid Message Target", "Target message count must be at least 1."
            )
            return

        interval = self.spin_interval.value()

        self.settings.set("last_message", msg, auto_save=False)
        self.settings.set("last_target_count", target, auto_save=False)
        self.settings.set("last_unlimited", unlimited, auto_save=True)

        self._elapsed_seconds = 0
        self.lbl_elapsed_val.setText("00:00")
        self.lbl_next_cap.setText("First send")
        self.lbl_next_val.setText(f"{FIRST_MESSAGE_DELAY_MS} ms")
        self.lbl_appr_hint.setText("Ready - press Shift + Enter to begin.")

        self.start_requested.emit(msg, target, unlimited, interval)

    def _on_stop_clicked(self):
        self._elapsed_timer.stop()
        self.stop_requested.emit()

    def start_elapsed_timer(self):
        """Starts the active duration stopwatch."""
        self._elapsed_seconds = 0
        self.lbl_elapsed_val.setText("00:00")
        self._elapsed_timer.start()

    def stop_elapsed_timer(self):
        """Stops the active duration stopwatch."""
        self._elapsed_timer.stop()

    def _on_elapsed_tick(self):
        self._elapsed_seconds += 1
        mins = self._elapsed_seconds // 60
        secs = self._elapsed_seconds % 60
        self.lbl_elapsed_val.setText(f"{mins:02d}:{secs:02d}")
        self.state.set_elapsed(self._elapsed_seconds)

    def _on_approval_state_changed(self, waiting: bool):
        self.approval_banner.setVisible(waiting)

    def _on_state_status_changed(self, status: str):
        self.metrics_bar.slot_status.set_value(status)

        if status == STATUS_RUNNING:
            self._set_inputs_enabled(False)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        elif status == STATUS_WAITING:
            self.lbl_next_cap.setText("First send")
            self.lbl_next_val.setText(f"{FIRST_MESSAGE_DELAY_MS} ms")
            self._set_inputs_enabled(False)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            self._elapsed_timer.stop()
            self._set_inputs_enabled(True)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
            self.lbl_next_cap.setText("Next sent")
            self.lbl_next_val.setText(f"{self.spin_interval.value()} ms")

    def _set_inputs_enabled(self, enabled: bool):
        self.txt_message.setEnabled(enabled)
        self.chk_unlimited.setEnabled(enabled)
        if enabled:
            self.spin_count.setEnabled(not self.chk_unlimited.isChecked())
        else:
            self.spin_count.setEnabled(False)
        self.spin_interval.setEnabled(enabled)

    def _on_state_counts_changed(self, sent: int, target: int, unlimited: bool):
        self.metrics_bar.slot_sent.set_value(f"{sent:,}")
        if unlimited:
            self.metrics_bar.slot_target.set_value("∞")
            self.lbl_prog_sub.setText(f"{sent:,} messages sent (Unlimited)")
        else:
            self.metrics_bar.slot_target.set_value(f"{target:,}")
            self.lbl_prog_sub.setText(f"{sent:,} of {target:,} messages sent")

        if sent >= 1:
            self.lbl_next_cap.setText("Next sent")
            self.lbl_next_val.setText(f"{self.spin_interval.value()} ms")

    def _on_state_progress_changed(self, pct: int):
        if self.chk_unlimited.isChecked():
            self.metrics_bar.slot_progress.set_value("∞")
            self.lbl_prog_pct.setText("∞")
            self._animate_progress(100)
        else:
            self.metrics_bar.slot_progress.set_value(f"{pct}%")
            self.lbl_prog_pct.setText(f"{pct}%")
            self._animate_progress(pct)

    def _animate_progress(self, target: int):
        self._progress_anim.stop()
        self._progress_anim.setStartValue(self.progress_bar.value())
        self._progress_anim.setEndValue(target)
        self._progress_anim.start()
