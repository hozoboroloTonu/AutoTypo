"""Overview metrics bar and live character counter components."""

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.styles import apply_card_shadow
from app.ui.widgets.buttons import load_svg_pixmap
from app.utils.constants import (
    COLOR_ACCENT,
    COLOR_ERROR,
    COLOR_ERROR_BG,
    COLOR_SUCCESS,
    COLOR_SUCCESS_BG,
    COLOR_TEXT_PRIMARY,
    COLOR_WARNING,
    COLOR_WARNING_BG,
    DEFAULT_TARGET_COUNT,
    STATUS_COMPLETED,
    STATUS_ERROR,
    STATUS_READY,
    STATUS_RUNNING,
    STATUS_STOPPED,
    STATUS_WAITING,
)


class _MetricSlot(QWidget):
    """Single metric column inside the unified OverviewMetricsBar."""

    def __init__(
        self,
        title: str,
        initial_value: str,
        icon_file: str,
        icon_bg: str = "#F1EFF7",
        is_status: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.is_status = is_status
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        text_col.setAlignment(Qt.AlignVCenter)

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(
            "font-size: 12px; font-weight: 500; color: #747783; background: transparent;"
        )
        text_col.addWidget(self.lbl_title)

        self.lbl_value = QLabel(initial_value)
        if is_status:
            self.lbl_value.setStyleSheet(
                f"font-size: 26px; font-weight: 600; color: {COLOR_SUCCESS}; letter-spacing: -0.8px; background: transparent;"
            )
        else:
            self.lbl_value.setStyleSheet(
                "font-size: 30px; font-weight: 600; color: #24252E; letter-spacing: -0.8px; background: transparent;"
            )
        text_col.addWidget(self.lbl_value)

        layout.addLayout(text_col)
        layout.addStretch()

        self.icon_surface = QFrame()
        self.icon_surface.setFixedSize(34, 34)
        self.icon_surface.setStyleSheet(
            f"background-color: {icon_bg}; border: none; border-radius: 12px;"
        )
        icon_layout = QVBoxLayout(self.icon_surface)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        lbl_icon = QLabel()
        lbl_icon.setStyleSheet("background: transparent; border: none;")
        lbl_icon.setPixmap(load_svg_pixmap(icon_file, QSize(18, 18)))
        lbl_icon.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(lbl_icon)

        layout.addWidget(self.icon_surface, alignment=Qt.AlignVCenter)

    def set_value(self, value: str):
        self.lbl_value.setText(value)
        if self.is_status:
            self._update_status_style(value)

    def _update_status_style(self, status: str):
        color = COLOR_TEXT_PRIMARY
        bg = "#F1EFF7"

        if status == STATUS_READY:
            color = COLOR_SUCCESS
            bg = COLOR_SUCCESS_BG
        elif status == STATUS_WAITING:
            color = COLOR_ACCENT
            bg = "#F1EFF7"
        elif status in (STATUS_RUNNING, STATUS_COMPLETED):
            color = COLOR_SUCCESS
            bg = COLOR_SUCCESS_BG
        elif status == STATUS_STOPPED:
            color = COLOR_WARNING
            bg = COLOR_WARNING_BG
        elif status == STATUS_ERROR:
            color = COLOR_ERROR
            bg = COLOR_ERROR_BG

        self.lbl_value.setStyleSheet(
            f"font-size: 26px; font-weight: 600; color: {color}; letter-spacing: -0.8px; background: transparent;"
        )
        self.icon_surface.setStyleSheet(
            f"background-color: {bg}; border: none; border-radius: 12px;"
        )


class OverviewMetricsBar(QFrame):
    """Unified 4-column overview metrics card matching the Figma design."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overviewMetricsCard")
        self.setFixedHeight(104)
        apply_card_shadow(self, blur_radius=16, y_offset=5, alpha=8)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.slot_sent = _MetricSlot("Messages sent", "0", "metric_sent.svg", "#F1EFF7")
        self.slot_target = _MetricSlot(
            "Target messages", str(DEFAULT_TARGET_COUNT), "metric_target.svg", "#F1EFF7"
        )
        self.slot_progress = _MetricSlot("Progress", "0%", "metric_progress.svg", "#F1EFF7")
        self.slot_status = _MetricSlot(
            "Status", STATUS_READY, "metric_status.svg", COLOR_SUCCESS_BG, is_status=True
        )

        slots = [self.slot_sent, self.slot_target, self.slot_progress, self.slot_status]
        for idx, slot in enumerate(slots):
            layout.addWidget(slot, 1)
            if idx < len(slots) - 1:
                sep = QFrame()
                sep.setFixedSize(1, 56)
                sep.setStyleSheet("background-color: #E7E7EF; border: none;")
                layout.addWidget(sep, alignment=Qt.AlignVCenter)


class LiveCharacterCounter(QLabel):
    """Pill-styled dynamic character counter badge."""

    def __init__(self, parent=None):
        super().__init__("0 characters", parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(26)
        self.setStyleSheet("""
            QLabel {
                background-color: #F4F5FA;
                border: none;
                border-radius: 8px;
                color: #747783;
                font-size: 10px;
                font-weight: 500;
                padding: 0px 12px;
            }
        """)

    def update_count(self, count: int):
        self.setText(f"{count:,} {'character' if count == 1 else 'characters'}")
