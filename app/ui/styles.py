"""Global design system, color palette, SVG icons, and Polished White Glass QSS styles."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from app.utils.constants import (
    COLOR_BG,
    COLOR_BG_END,
    COLOR_SURFACE,
    COLOR_SURFACE_SECONDARY,
    COLOR_SURFACE_HOVER,
    COLOR_BORDER,
    COLOR_BORDER_LIGHT,
    COLOR_BORDER_FOCUS,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_LIGHT,
    COLOR_ACCENT_BG,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_ERROR,
    COLOR_ERROR_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
)


def apply_card_shadow(
    widget: QWidget,
    blur_radius: int = 24,
    y_offset: int = 8,
    alpha: int = 13,
) -> None:
    """Applies a soft, subtle drop shadow matching the white-glass Figma elevation."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur_radius)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(56, 64, 82, alpha))
    widget.setGraphicsEffect(shadow)


# Fallback inline SVGs (primary icons load from assets/icons/*.svg)
ICONS_SVG = {
    "bolt": """<svg viewBox="0 0 24 24" fill="none" stroke="#7654DB" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "check": """<svg viewBox="0 0 24 24" fill="none" stroke="#268266" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>""",
    "info": """<svg viewBox="0 0 24 24" fill="none" stroke="#7654DB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>""",
    "warning": """<svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "error": """<svg viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>""",
}


GLOBAL_STYLESHEET = f"""
/* Global Typography & Base */
QWidget {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background: transparent;
}}

QFrame#rootWindowFrame {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {COLOR_BG}, stop:1 {COLOR_BG_END});
    border: 1px solid #FFFFFF;
    border-radius: 18px;
}}

QFrame#rootWindowFrame[maximized="true"] {{
    border: none;
    border-radius: 0px;
}}

/* Custom Title Bar */
QFrame#titleBar {{
    background-color: rgba(255, 255, 255, 0.78);
    border-bottom: 1px solid #FFFFFF;
    border-top-left-radius: 18px;
    border-top-right-radius: 18px;
}}

QFrame#titleBar[maximized="true"] {{
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}}

QPushButton#titleBarBtn {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px;
}}

QPushButton#titleBarBtn:hover {{
    background-color: rgba(56, 64, 82, 0.08);
}}

QPushButton#titleBarCloseBtn {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px;
}}

QPushButton#titleBarCloseBtn:hover {{
    background-color: rgba(220, 38, 38, 0.12);
}}

/* Scroll Areas & Thin Scrollbars */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 4px 0px;
}}

QScrollBar::handle:vertical {{
    background: #D6D9E4;
    min-height: 28px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background: #A18AE8;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

/* Cards */
QFrame#cardFrame {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.45 #FDFDFF, stop:1 #F6F7FB);
    border: 1px solid #E1E4EC;
    border-top: 1px solid #FFFFFF;
    border-radius: 22px;
}}

QFrame#overviewMetricsCard {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.45 #FCFCFE, stop:1 #F5F6FA);
    border: 1px solid #DFE1E8;
    border-top: 1px solid #FFFFFF;
    border-radius: 20px;
}}

QFrame#innerCardFrame {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.5 #FDFDFF, stop:1 #F7F8FC);
    border: 1px solid {COLOR_BORDER};
    border-top: 1px solid #FFFFFF;
    border-radius: 16px;
}}

/* Approval Banner */
QFrame#approvalBanner {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F4F0FD, stop:1 #FAF8FF);
    border: 1px solid #A18AE8;
    border-radius: 16px;
}}

/* Typography */
QLabel#pageTitle {{
    font-size: 32px;
    font-weight: 600;
    color: {COLOR_TEXT_PRIMARY};
    letter-spacing: -0.8px;
    background: transparent;
}}

QLabel#pageSubtitle {{
    font-size: 13px;
    font-weight: 400;
    color: {COLOR_TEXT_MUTED};
    background: transparent;
}}

QLabel#cardHeading {{
    font-size: 16px;
    font-weight: 600;
    color: {COLOR_TEXT_PRIMARY};
    background: transparent;
}}

QLabel#fieldLabel {{
    font-size: 12px;
    font-weight: 500;
    color: {COLOR_TEXT_SECONDARY};
    background: transparent;
}}

QLabel#settingTitle {{
    font-size: 14px;
    font-weight: 500;
    color: #343945;
    background: transparent;
}}

QLabel#helperText {{
    font-size: 12px;
    font-weight: 400;
    color: {COLOR_TEXT_MUTED};
    background: transparent;
}}

QFrame#sectionDivider {{
    background-color: #EBECF1;
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

QFrame#subtleDivider {{
    background-color: #EDF0F5;
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

/* Editor & Inputs */
QFrame#messageEditorBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F5F5F9, stop:1 #FCFCFE);
    border: 1px solid #DFE1EA;
    border-radius: 12px;
}}

QFrame#messageEditorBox:focus-within {{
    border: 1px solid {COLOR_BORDER_FOCUS};
}}

QPlainTextEdit#messagePlainEdit {{
    background: transparent;
    border: none;
    color: #384152;
    font-size: 15px;
    font-weight: 500;
    selection-background-color: rgba(118, 84, 219, 0.22);
}}

QFrame#inputContainer {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F5F5F9, stop:1 #FCFCFE);
    border: 1px solid #DFE1EA;
    border-radius: 10px;
}}

QFrame#inputContainer:focus-within {{
    border: 1px solid {COLOR_BORDER_FOCUS};
}}

QFrame#readOnlyContainer {{
    background-color: #F1F2F6;
    border: 1px solid #DFE1EA;
    border-radius: 10px;
}}

QSpinBox#cleanSpinBox {{
    background: transparent;
    border: none;
    color: {COLOR_TEXT_PRIMARY};
    font-size: 14px;
    font-weight: 500;
    padding: 0px;
}}

QSpinBox#cleanSpinBox:disabled {{
    color: #8B8E9C;
}}

QSpinBox#cleanSpinBox::up-button, QSpinBox#cleanSpinBox::down-button {{
    width: 0px;
    height: 0px;
    border: none;
}}

QLineEdit#readOnlyBox {{
    background-color: #F1F2F6;
    border: 1px solid #DFE1EA;
    border-radius: 10px;
    padding: 8px 14px;
    color: #8B8E9C;
    font-size: 14px;
    font-weight: 500;
}}

/* Keycap Badges */
QLabel#keycapBadge {{
    background-color: #FFFFFF;
    border: 1px solid #DFE1EA;
    border-radius: 6px;
    color: #59606F;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 14px;
}}

/* Progress Bar */
QProgressBar {{
    background-color: #ECEFF7;
    border: none;
    border-radius: 3px;
    text-align: center;
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #A18AE8, stop:1 #7654DB);
    border-radius: 3px;
}}

/* Buttons */
QPushButton#primaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #C5B4FC, stop:0.08 #A589EC, stop:0.52 #835FD8, stop:1 #673FBC);
    border: 1px solid #7553BC;
    border-top: 1px solid #D3C5FD;
    border-radius: 12px;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 600;
    padding: 0px 20px;
}}

QPushButton#primaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #CEBFFB, stop:0.08 #AE94F0, stop:0.52 #8B68DF, stop:1 #7047C6);
}}

QPushButton#primaryButton:pressed {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6E46C2, stop:1 #5A35A8);
}}

QPushButton#primaryButton:disabled {{
    background: #C9BFE8;
    border: 1px solid #BEB3DF;
    color: rgba(255, 255, 255, 0.85);
}}

QPushButton#stopButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.45 #FAFBFD, stop:1 #ECEEF4);
    border: 1px solid #DFE1E8;
    border-top: 1px solid #FFFFFF;
    border-radius: 12px;
    color: {COLOR_TEXT_MUTED};
    font-size: 14px;
    font-weight: 500;
    padding: 0px 16px;
}}

QPushButton#stopButton[activeState="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFF8F8, stop:0.45 #FEEAEA, stop:1 #FDD8D8);
    border: 1px solid #FCA5A5;
    border-top: 1px solid #FFFFFF;
    color: {COLOR_ERROR};
    font-weight: 600;
}}

QPushButton#stopButton[activeState="true"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FEE2E2, stop:1 #FECACA);
    border: 1px solid #F87171;
}}

QPushButton#secondaryButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.45 #FAFBFD, stop:1 #ECEEF4);
    border: 1px solid #DFE1E8;
    border-top: 1px solid #FFFFFF;
    border-radius: 10px;
    color: #59606F;
    font-size: 12px;
    font-weight: 500;
    padding: 0px 16px;
}}

QPushButton#secondaryButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F3F5F9);
    border: 1px solid #CFD3DF;
    color: {COLOR_TEXT_PRIMARY};
}}

/* Sidebar Nav Buttons */
QPushButton#navButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    color: #616B7D;
    font-size: 13px;
    font-weight: 500;
    text-align: left;
    padding: 0px 14px;
    height: 44px;
}}

QPushButton#navButton:hover {{
    background-color: rgba(255, 255, 255, 0.72);
    color: {COLOR_TEXT_PRIMARY};
}}

QPushButton#navButton[active="true"] {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:0.5 #FCFBFE, stop:1 #F4F1FA);
    border: 1px solid #DDD9E8;
    border-top: 1px solid #FFFFFF;
    color: {COLOR_ACCENT};
    font-weight: 600;
}}

/* Segmented Tabs (Logs) */
QFrame#segmentedTabs {{
    background-color: #EAEAF1;
    border-radius: 12px;
}}

QPushButton#segmentTabBtn {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    color: {COLOR_TEXT_MUTED};
    font-size: 13px;
    font-weight: 500;
}}

QPushButton#segmentTabBtn:hover {{
    color: {COLOR_TEXT_PRIMARY};
}}

QPushButton#segmentTabBtn[active="true"] {{
    background-color: #FFFFFF;
    border: 1px solid #E1DEEA;
    color: {COLOR_ACCENT};
    font-weight: 600;
}}

/* ComboBox */
QComboBox#filterCombo {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F1F2F6);
    border: 1px solid #DFE1E8;
    border-radius: 10px;
    padding: 0px 14px;
    color: #343945;
    font-size: 12px;
    font-weight: 500;
}}

QComboBox#filterCombo:hover {{
    border: 1px solid #CFD3DF;
}}

QComboBox#filterCombo::drop-down {{
    border: none;
    width: 28px;
}}

QComboBox#filterCombo QAbstractItemView {{
    background-color: #FFFFFF;
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    color: {COLOR_TEXT_PRIMARY};
    selection-background-color: {COLOR_ACCENT_BG};
    selection-color: {COLOR_ACCENT};
    padding: 4px;
}}

/* Table Widget (Logs) */
QTableWidget#logsTable {{
    background-color: transparent;
    border: none;
    outline: none;
    gridline-color: transparent;
    alternate-background-color: #FAFAFD;
}}

QTableWidget#logsTable::item {{
    padding: 4px 12px;
    border-bottom: 1px solid #EEEFF4;
    color: #343945;
    font-size: 13px;
}}

QTableWidget#logsTable::item:selected {{
    background-color: #F4F2FA;
    color: {COLOR_TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: #F5F5F9;
    color: {COLOR_TEXT_MUTED};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 9px 14px;
    border: none;
}}

QHeaderView::section:first {{
    border-top-left-radius: 8px;
    border-bottom-left-radius: 8px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}}
"""
