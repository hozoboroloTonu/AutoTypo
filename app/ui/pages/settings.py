"""Settings Page: Polished white-glass configuration and preferences view."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.services.notification_manager import NotificationManager
from app.services.settings_manager import SettingsManager
from app.ui.styles import apply_card_shadow
from app.ui.widgets.buttons import PrimaryButton, SecondaryButton, ToggleSwitch
from app.ui.widgets.dialogs import ConfirmationModal
from app.utils.constants import FIRST_MESSAGE_DELAY_MS


class SettingsPage(QWidget):
    """Polished white-glass settings view for customization."""

    always_on_top_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = SettingsManager.get_instance()
        self.notifier = NotificationManager.get_instance()
        self._init_ui()
        self._load_values()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 28, 40, 32)
        layout.setSpacing(24)

        # 1. Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        lbl_title = QLabel("Settings")
        lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Customize the behavior of Auto Typo.")
        lbl_subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(lbl_subtitle)

        layout.addLayout(header_layout)

        # 2. Typing Behavior Card
        card_typing = QFrame()
        card_typing.setObjectName("cardFrame")
        apply_card_shadow(card_typing, blur_radius=20, y_offset=8, alpha=12)
        t_layout = QVBoxLayout(card_typing)
        t_layout.setContentsMargins(24, 22, 24, 24)
        t_layout.setSpacing(18)

        lbl_sec1 = QLabel("Typing behavior")
        lbl_sec1.setObjectName("cardHeading")
        t_layout.addWidget(lbl_sec1)

        div1 = QFrame()
        div1.setObjectName("sectionDivider")
        t_layout.addWidget(div1)

        # Row 1: Message Interval
        row_int = QHBoxLayout()
        row_int.setSpacing(20)
        int_text = QVBoxLayout()
        int_text.setSpacing(4)
        lbl_int_title = QLabel("Message Interval")
        lbl_int_title.setObjectName("settingTitle")
        int_text.addWidget(lbl_int_title)
        lbl_int_desc = QLabel("Used between messages after the first send.")
        lbl_int_desc.setObjectName("helperText")
        int_text.addWidget(lbl_int_desc)
        row_int.addLayout(int_text)
        row_int.addStretch()

        int_box = QFrame()
        int_box.setObjectName("inputContainer")
        int_box.setFixedSize(380, 46)
        int_box_layout = QHBoxLayout(int_box)
        int_box_layout.setContentsMargins(16, 0, 16, 0)

        self.spin_interval = QSpinBox()
        self.spin_interval.setObjectName("cleanSpinBox")
        self.spin_interval.setRange(10, 60000)
        int_box_layout.addWidget(self.spin_interval, 1)

        lbl_ms1 = QLabel("ms")
        lbl_ms1.setStyleSheet("font-size: 12px; color: #747783; background: transparent;")
        int_box_layout.addWidget(lbl_ms1)
        row_int.addWidget(int_box)
        t_layout.addLayout(row_int)

        # Row 2: First Message Delay
        row_fmd = QHBoxLayout()
        row_fmd.setSpacing(20)
        fmd_text = QVBoxLayout()
        fmd_text.setSpacing(4)
        lbl_fmd_title = QLabel("First Message Delay")
        lbl_fmd_title.setObjectName("settingTitle")
        fmd_text.addWidget(lbl_fmd_title)
        lbl_fmd_desc = QLabel("Fixed at 1 second for target field readiness.")
        lbl_fmd_desc.setObjectName("helperText")
        fmd_text.addWidget(lbl_fmd_desc)
        row_fmd.addLayout(fmd_text)
        row_fmd.addStretch()

        fmd_box = QFrame()
        fmd_box.setObjectName("readOnlyContainer")
        fmd_box.setFixedSize(380, 46)
        fmd_box_layout = QHBoxLayout(fmd_box)
        fmd_box_layout.setContentsMargins(16, 0, 16, 0)

        lbl_fmd_val = QLabel(str(FIRST_MESSAGE_DELAY_MS))
        lbl_fmd_val.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #8B8E9C; background: transparent;"
        )
        fmd_box_layout.addWidget(lbl_fmd_val)
        fmd_box_layout.addStretch()

        lbl_ms2 = QLabel("ms")
        lbl_ms2.setStyleSheet("font-size: 12px; color: #747783; background: transparent;")
        fmd_box_layout.addWidget(lbl_ms2)
        row_fmd.addWidget(fmd_box)
        t_layout.addLayout(row_fmd)

        # Row 3: Approval Shortcut
        row_sc = QHBoxLayout()
        row_sc.setSpacing(20)
        sc_text = QVBoxLayout()
        sc_text.setSpacing(4)
        lbl_sc_title = QLabel("Approval Shortcut")
        lbl_sc_title.setObjectName("settingTitle")
        sc_text.addWidget(lbl_sc_title)
        lbl_sc_desc = QLabel("Used to approve the selected target.")
        lbl_sc_desc.setObjectName("helperText")
        sc_text.addWidget(lbl_sc_desc)
        row_sc.addLayout(sc_text)
        row_sc.addStretch()

        sc_box = QFrame()
        sc_box.setObjectName("inputContainer")
        sc_box.setFixedSize(380, 46)
        sc_box_layout = QHBoxLayout(sc_box)
        sc_box_layout.setContentsMargins(14, 0, 14, 0)
        sc_box_layout.setSpacing(8)

        lbl_key_shift = QLabel("Shift")
        lbl_key_shift.setObjectName("keycapBadge")
        lbl_key_shift.setFixedHeight(28)
        sc_box_layout.addWidget(lbl_key_shift)

        lbl_plus = QLabel("+")
        lbl_plus.setStyleSheet("font-size: 12px; color: #9294A1; background: transparent;")
        sc_box_layout.addWidget(lbl_plus)

        lbl_key_enter = QLabel("Enter")
        lbl_key_enter.setObjectName("keycapBadge")
        lbl_key_enter.setFixedHeight(28)
        sc_box_layout.addWidget(lbl_key_enter)

        sc_box_layout.addStretch()
        row_sc.addWidget(sc_box)
        t_layout.addLayout(row_sc)

        layout.addWidget(card_typing)

        # 3. General Settings Card
        card_general = QFrame()
        card_general.setObjectName("cardFrame")
        apply_card_shadow(card_general, blur_radius=20, y_offset=8, alpha=12)
        g_layout = QVBoxLayout(card_general)
        g_layout.setContentsMargins(24, 22, 24, 22)
        g_layout.setSpacing(14)

        lbl_sec2 = QLabel("General settings")
        lbl_sec2.setObjectName("cardHeading")
        g_layout.addWidget(lbl_sec2)

        div2 = QFrame()
        div2.setObjectName("sectionDivider")
        g_layout.addWidget(div2)

        # Toggle 1: Show Notifications
        self.chk_notifications = ToggleSwitch(width=44, height=26)
        g_layout.addLayout(self._create_toggle_row("Show Notifications", self.chk_notifications))

        pdiv1 = QFrame()
        pdiv1.setObjectName("subtleDivider")
        g_layout.addWidget(pdiv1)

        # Toggle 2: Always on Top
        self.chk_always_on_top = ToggleSwitch(width=44, height=26)
        self.chk_always_on_top.toggled.connect(self.always_on_top_toggled.emit)
        g_layout.addLayout(self._create_toggle_row("Always on Top", self.chk_always_on_top))

        pdiv2 = QFrame()
        pdiv2.setObjectName("subtleDivider")
        g_layout.addWidget(pdiv2)

        # Toggle 3: Stop on Error
        self.chk_stop_on_error = ToggleSwitch(width=44, height=26)
        g_layout.addLayout(self._create_toggle_row("Stop on Error", self.chk_stop_on_error))

        layout.addWidget(card_general)

        # 4. Action Buttons (Bottom)
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)

        self.btn_reset = SecondaryButton("Reset Defaults")
        self.btn_reset.setFixedSize(176, 54)
        self.btn_reset.setStyleSheet(
            self.btn_reset.styleSheet() + "QPushButton#secondaryButton { border-radius: 12px; font-size: 14px; }"
        )
        self.btn_reset.clicked.connect(self._on_reset_defaults)
        btn_row.addWidget(self.btn_reset)

        btn_row.addStretch()

        self.btn_save = PrimaryButton("Save Settings")
        self.btn_save.setFixedSize(220, 54)
        self.btn_save.clicked.connect(self._on_save_settings)
        btn_row.addWidget(self.btn_save)

        layout.addLayout(btn_row)
        layout.addStretch()

        scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _create_toggle_row(self, title: str, switch: ToggleSwitch) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(0, 4, 0, 4)
        lbl = QLabel(title)
        lbl.setObjectName("settingTitle")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(switch)
        return row

    def _load_values(self):
        self.spin_interval.setValue(self.settings.interval_ms)
        self.chk_notifications.setChecked(self.settings.show_notifications)
        self.chk_always_on_top.setChecked(self.settings.always_on_top)
        self.chk_stop_on_error.setChecked(self.settings.stop_on_error)

    def _on_save_settings(self):
        updated = {
            "interval_ms": self.spin_interval.value(),
            "first_delay_ms": FIRST_MESSAGE_DELAY_MS,
            "approval_hotkey": "SHIFT+ENTER",
            "show_notifications": self.chk_notifications.isChecked(),
            "always_on_top": self.chk_always_on_top.isChecked(),
            "stop_on_error": self.chk_stop_on_error.isChecked(),
        }
        self.settings.update_all(updated)
        self.notifier.show_success("Settings Saved", "Your preferences have been saved successfully.")

    def _on_reset_defaults(self):
        modal = ConfirmationModal(
            "Reset Settings",
            "Are you sure you want to restore all settings to default values?",
            "Reset to Defaults",
            is_destructive=True,
            parent=self.window(),
        )
        if modal.exec() == ConfirmationModal.Accepted:
            self.settings.reset_to_defaults()
            self._load_values()
            self.notifier.show_info("Settings Reset", "Settings have been restored to defaults.")
