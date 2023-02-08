"""Custom frameless title bar matching the Polished White Glass Figma design."""

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from app.ui.widgets.buttons import load_svg_icon
from app.utils.constants import APP_DISPLAY_NAME


class TitleBar(QFrame):
    """60px frameless window title bar with drag, centered page name, and window controls."""

    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(60)
        self._drag_pos: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 20, 0)
        layout.setSpacing(0)

        # Left: App Display Name
        self.lbl_brand = QLabel(APP_DISPLAY_NAME)
        self.lbl_brand.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #202633; background: transparent;"
        )
        self.lbl_brand.setFixedWidth(180)
        layout.addWidget(self.lbl_brand)

        layout.addStretch()

        # Center: Current Page Name
        self.lbl_page = QLabel("Dashboard")
        self.lbl_page.setAlignment(Qt.AlignCenter)
        self.lbl_page.setStyleSheet(
            "font-size: 12px; font-weight: 500; color: #747783; background: transparent;"
        )
        layout.addWidget(self.lbl_page)

        layout.addStretch()

        # Right: Window Controls (Minimize, Maximize, Close)
        controls_wrap = QWidget()
        controls_wrap.setFixedWidth(180)
        controls_wrap.setStyleSheet("background: transparent;")
        controls_layout = QHBoxLayout(controls_wrap)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        controls_layout.addStretch()

        self.btn_min = QPushButton()
        self.btn_min.setObjectName("titleBarBtn")
        self.btn_min.setFixedSize(32, 32)
        self.btn_min.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_min.setIcon(load_svg_icon("win_minimize.svg", QSize(16, 16)))
        self.btn_min.setIconSize(QSize(16, 16))
        self.btn_min.clicked.connect(self.minimize_clicked.emit)
        controls_layout.addWidget(self.btn_min)

        self.btn_max = QPushButton()
        self.btn_max.setObjectName("titleBarBtn")
        self.btn_max.setFixedSize(32, 32)
        self.btn_max.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_max.setIcon(load_svg_icon("win_maximize.svg", QSize(16, 16)))
        self.btn_max.setIconSize(QSize(16, 16))
        self.btn_max.clicked.connect(self.maximize_clicked.emit)
        controls_layout.addWidget(self.btn_max)

        self.btn_close = QPushButton()
        self.btn_close.setObjectName("titleBarCloseBtn")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setCursor(QCursor(Qt.PointingHandCursor))
        self.btn_close.setIcon(load_svg_icon("win_close.svg", QSize(16, 16)))
        self.btn_close.setIconSize(QSize(16, 16))
        self.btn_close.clicked.connect(self.close_clicked.emit)
        controls_layout.addWidget(self.btn_close)

        layout.addWidget(controls_wrap)

    def set_page_title(self, title: str):
        self.lbl_page.setText(title)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            win = self.window()
            if win and not win.isMaximized():
                self._drag_pos = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            win = self.window()
            if win and not win.isMaximized():
                win.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
