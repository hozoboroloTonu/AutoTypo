"""Non-blocking white-glass toast notification overlay."""

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.styles import ICONS_SVG, apply_card_shadow
from app.ui.widgets.buttons import create_svg_icon
from app.utils.constants import (
    COLOR_ACCENT,
    COLOR_ERROR,
    COLOR_SUCCESS,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_WARNING,
    LOG_ERROR,
    LOG_INFO,
    LOG_SUCCESS,
    LOG_WARNING,
)


class ToastItem(QFrame):
    """Single floating white-glass toast notification card."""

    def __init__(self, title: str, message: str, level: str, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        border_color = "#DEE1E9"
        icon_key = "info"
        if level == LOG_SUCCESS:
            border_color = COLOR_SUCCESS
            icon_key = "check"
        elif level == LOG_WARNING:
            border_color = COLOR_WARNING
            icon_key = "warning"
        elif level == LOG_ERROR:
            border_color = COLOR_ERROR
            icon_key = "error"
        else:
            border_color = "#C8BBE8"

        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #FCFCFE);
                border: 1px solid {border_color};
                border-radius: 14px;
            }}
        """)
        apply_card_shadow(self, blur_radius=20, y_offset=6, alpha=22)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        lbl_icon = QLabel()
        lbl_icon.setFixedSize(22, 22)
        lbl_icon.setStyleSheet("border: none; background: transparent;")
        lbl_icon.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        pix = create_svg_icon(ICONS_SVG.get(icon_key, ICONS_SVG["info"]), QSize(20, 20)).pixmap(20, 20)
        lbl_icon.setPixmap(pix)
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon, alignment=Qt.AlignTop)

        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel(title)
        lbl_title.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        lbl_title.setStyleSheet(
            f"font-size: 13px; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; border: none; background: transparent;"
        )
        content_layout.addWidget(lbl_title)

        lbl_msg = QLabel(message)
        lbl_msg.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        lbl_msg.setStyleSheet(
            f"font-size: 11px; color: {COLOR_TEXT_MUTED}; border: none; background: transparent;"
        )
        lbl_msg.setWordWrap(True)
        content_layout.addWidget(lbl_msg)

        layout.addLayout(content_layout)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close)
        self.timer.start(4000)


class ToastOverlay(QWidget):
    """Container overlay positioned at bottom-right, transparent to mouse events."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 24, 24)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)

    def show_toast(self, title: str, message: str, level: str = LOG_INFO):
        toast = ToastItem(title, message, level, self)
        self.layout.addWidget(toast)
        toast.show()
        self.raise_()

    def update_position(self):
        if self.parent():
            pw = self.parent().width()
            ph = self.parent().height()
            w = min(360, pw)
            h = min(400, ph)
            self.setGeometry(pw - w, ph - h, w, h)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_position()
