"""Polished white-glass sidebar navigation widget."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.ui.widgets.buttons import AppEmblem, NavButton
from app.utils.constants import APP_NAME, SIDEBAR_WIDTH


class SidebarWidget(QFrame):
    """Left 224px sidebar with brand emblem, workspace label, and navigation items."""

    page_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(SIDEBAR_WIDTH)
        self.setObjectName("sidebarFrame")
        self.setStyleSheet("""
            QFrame#sidebarFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FBFBFD, stop:1 #F2F2F7);
                border: none;
                border-bottom-left-radius: 18px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 30, 16, 24)
        layout.setSpacing(0)

        # 1. Brand Header (Emblem + Auto Typo)
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(8, 0, 0, 0)
        brand_layout.setSpacing(12)

        emblem = AppEmblem(size=44, radius=14, icon_size=24)
        brand_layout.addWidget(emblem)

        lbl_brand = QLabel(APP_NAME)
        lbl_brand.setStyleSheet(
            "font-size: 15px; font-weight: 600; color: #202633; letter-spacing: -0.35px; background: transparent;"
        )
        brand_layout.addWidget(lbl_brand)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)

        layout.addSpacing(42)

        # 2. Section Label
        lbl_section = QLabel("WORKSPACE")
        lbl_section.setStyleSheet(
            "font-size: 10px; font-weight: 600; color: #747783; letter-spacing: 1.6px; padding-left: 12px; background: transparent;"
        )
        layout.addWidget(lbl_section)

        layout.addSpacing(15)

        # 3. Nav Items
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard", "nav_dashboard.svg", "nav_dashboard_active.svg"),
            ("settings", "Settings", "nav_settings.svg", "nav_settings_active.svg"),
            ("logs", "Logs", "nav_logs.svg", "nav_logs_active.svg"),
            ("about", "About", "nav_about.svg", "nav_about_active.svg"),
        ]

        nav_container = QVBoxLayout()
        nav_container.setSpacing(8)
        for page_id, label, icon_file, active_icon_file in nav_items:
            btn = NavButton(label, icon_file, active_icon_file, self)
            btn.clicked.connect(lambda checked=False, pid=page_id: self._on_nav_clicked(pid))
            nav_container.addWidget(btn)
            self.nav_buttons[page_id] = btn

        layout.addLayout(nav_container)
        layout.addStretch()

        self.set_active_page("dashboard")

    def _on_nav_clicked(self, page_id: str):
        self.set_active_page(page_id)
        self.page_selected.emit(page_id)

    def set_active_page(self, active_id: str):
        for pid, btn in self.nav_buttons.items():
            btn.set_active(pid == active_id)

    def update_status(self, status: str):
        """Retained for controller signal compatibility."""
        pass
