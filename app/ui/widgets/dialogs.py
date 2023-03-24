"""Polished white-glass modal dialogs."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from app.ui.styles import apply_card_shadow
from app.ui.widgets.buttons import DestructiveButton, PrimaryButton, SecondaryButton


class ConfirmationModal(QDialog):
    """White-glass modal for confirming actions like clearing logs or reset."""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        is_destructive: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(420, 196)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        container = QFrame(self)
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #FCFCFE);
                border: 1px solid #DEE1E9;
                border-radius: 18px;
            }
        """)
        apply_card_shadow(container, blur_radius=24, y_offset=8, alpha=35)

        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(24, 22, 24, 20)
        c_layout.setSpacing(10)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #202633; border: none; background: transparent;"
        )
        c_layout.addWidget(lbl_title)

        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet(
            "font-size: 13px; color: #747783; border: none; background: transparent;"
        )
        lbl_msg.setWordWrap(True)
        c_layout.addWidget(lbl_msg)

        c_layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        btn_cancel = SecondaryButton("Cancel")
        btn_cancel.setFixedHeight(38)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        if is_destructive:
            btn_confirm = DestructiveButton(confirm_text, "")
            btn_confirm.setEnabled(True)
            btn_confirm.setFixedHeight(38)
        else:
            btn_confirm = PrimaryButton(confirm_text, "")
            btn_confirm.setFixedHeight(38)

        btn_confirm.clicked.connect(self.accept)
        btn_row.addWidget(btn_confirm)

        c_layout.addLayout(btn_row)
        main_layout.addWidget(container)
