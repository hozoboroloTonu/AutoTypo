"""Custom styled buttons, toggle switch, app emblem, and SVG icon helpers."""

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QCursor, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QCheckBox, QFrame, QLabel, QPushButton, QVBoxLayout

from app.ui.styles import ICONS_SVG
from app.utils.resources import get_asset_path


def create_svg_icon(svg_str: str, size: QSize = QSize(18, 18)) -> QIcon:
    """Creates a crisp QIcon from an inline SVG string."""
    renderer = QSvgRenderer(svg_str.encode("utf-8"))
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def load_svg_pixmap(filename: str, size: QSize = QSize(18, 18)) -> QPixmap:
    """Loads a crisp QPixmap from an SVG file in assets/icons/, preserving aspect ratio."""
    path = get_asset_path(f"icons/{filename}")
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    if path.exists():
        renderer = QSvgRenderer(str(path))
        default_sz = renderer.defaultSize()
        if not default_sz.isEmpty():
            scaled = default_sz.scaled(size, Qt.KeepAspectRatio)
            x = (size.width() - scaled.width()) / 2.0
            y = (size.height() - scaled.height()) / 2.0
            target_rect = QRectF(x, y, scaled.width(), scaled.height())
        else:
            target_rect = QRectF(0, 0, size.width(), size.height())
        painter = QPainter(pixmap)
        renderer.render(painter, target_rect)
        painter.end()
    return pixmap


def load_svg_icon(filename: str, size: QSize = QSize(18, 18)) -> QIcon:
    """Loads a crisp QIcon from an SVG file in assets/icons/."""
    return QIcon(load_svg_pixmap(filename, size))


class AppEmblem(QFrame):
    """Glossy purple gradient rounded app emblem with white keyboard icon."""

    def __init__(self, size: int = 44, radius: int = 14, icon_size: int = 24, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B49FF5, stop:0.18 #9E85E6, stop:1 #6F4DC4);
                border: 1px solid rgba(255, 255, 255, 0.88);
                border-radius: {radius}px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        lbl = QLabel()
        lbl.setStyleSheet("background: transparent; border: none;")
        lbl.setPixmap(load_svg_pixmap("emblem_keyboard.svg", QSize(icon_size, icon_size)))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)


class ToggleSwitch(QCheckBox):
    """Smoothly animated pill-shaped toggle switch with glossy thumb."""

    def __init__(self, width: int = 38, height: int = 22, parent=None):
        super().__init__(parent)
        self._w = width
        self._h = height
        self._thumb_progress = 1.0 if self.isChecked() else 0.0
        self.setFixedSize(width, height)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        self._anim = QPropertyAnimation(self, b"thumbProgress", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self.toggled.connect(self._animate_toggle)

    def get_thumb_progress(self) -> float:
        return self._thumb_progress

    def set_thumb_progress(self, value: float):
        self._thumb_progress = value
        self.update()

    thumbProgress = Property(float, get_thumb_progress, set_thumb_progress)

    def _animate_toggle(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._thumb_progress)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self._anim.stop()
        self._thumb_progress = 1.0 if checked else 0.0
        self.update()

    def hitButton(self, pos):
        return self.rect().contains(pos)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        radius = rect.height() / 2.0
        p = self._thumb_progress

        # Interpolate track color smoothly between off (#DFE1E9) and on (#8763D8)
        if self.isEnabled():
            r = int(223 + (135 - 223) * p)
            g = int(225 + (99 - 225) * p)
            b = int(233 + (216 - 233) * p)
            track_color = QColor(r, g, b)
        else:
            track_color = QColor("#BEB0E6") if self.isChecked() else QColor("#ECEEF4")

        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(QRectF(rect), radius, radius)

        # Thumb
        margin = 3.0
        thumb_d = rect.height() - (margin * 2.0)
        min_x = margin
        max_x = rect.width() - thumb_d - margin
        thumb_x = min_x + (max_x - min_x) * p
        thumb_rect = QRectF(thumb_x, margin, thumb_d, thumb_d)

        # Subtle thumb shadow
        painter.setBrush(QColor(56, 71, 115, 26))
        painter.drawEllipse(thumb_rect.adjusted(0, 1.2, 0, 1.2))

        # Glossy white thumb
        grad = QLinearGradient(thumb_rect.topLeft(), thumb_rect.bottomLeft())
        grad.setColorAt(0.0, QColor("#FFFFFF"))
        grad.setColorAt(1.0, QColor("#F3F4F8"))
        painter.setBrush(grad)
        painter.drawEllipse(thumb_rect)
        painter.end()


class PrimaryButton(QPushButton):
    """Violet gradient primary action button (e.g., Start automation, Save Settings)."""

    def __init__(self, text: str, icon_name: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("primaryButton")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if icon_name:
            filename = icon_name if icon_name.endswith(".svg") else f"{icon_name}.svg"
            icon = load_svg_icon(filename, QSize(18, 18))
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(18, 18))
            elif icon_name in ICONS_SVG:
                self.setIcon(create_svg_icon(ICONS_SVG[icon_name], QSize(16, 16)))
                self.setIconSize(QSize(16, 16))


class DestructiveButton(QPushButton):
    """Stop action button matching Figma inactive/active states."""

    def __init__(self, text: str, icon_name: str = "stop.svg", parent=None):
        super().__init__(text, parent)
        self.setObjectName("stopButton")
        self.setProperty("activeState", "false")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if icon_name:
            filename = icon_name if icon_name.endswith(".svg") else f"{icon_name}.svg"
            self.setIcon(load_svg_icon(filename, QSize(16, 16)))
            self.setIconSize(QSize(16, 16))

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self.setProperty("activeState", "true" if enabled else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class SecondaryButton(QPushButton):
    """Polished white-glass secondary button (Reset Defaults, Refresh, Clear Logs)."""

    def __init__(self, text: str, icon_name: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("secondaryButton")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        if icon_name:
            filename = icon_name if icon_name.endswith(".svg") else f"{icon_name}.svg"
            icon = load_svg_icon(filename, QSize(15, 15))
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(15, 15))
            elif icon_name in ICONS_SVG:
                self.setIcon(create_svg_icon(ICONS_SVG[icon_name], QSize(14, 14)))
                self.setIconSize(QSize(14, 14))


class NavButton(QPushButton):
    """Sidebar navigation button with active state and Figma SVG icons."""

    def __init__(self, text: str, icon_file: str, active_icon_file: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("navButton")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.icon_file = icon_file
        self.active_icon_file = active_icon_file
        self._is_active = False
        self.update_icon()

    def set_active(self, active: bool):
        self._is_active = active
        self.setProperty("active", "true" if active else "false")
        self.update_icon()
        self.style().unpolish(self)
        self.style().polish(self)

    def update_icon(self):
        filename = self.active_icon_file if self._is_active else self.icon_file
        self.setIcon(load_svg_icon(filename, QSize(20, 20)))
        self.setIconSize(QSize(20, 20))
