"""About Page: Polished white-glass application identity, credits, and branding."""

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QCursor, QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.styles import apply_card_shadow
from app.ui.widgets.buttons import AppEmblem
from app.utils.constants import (
    APP_AUTHOR,
    APP_COPYRIGHT,
    APP_DISPLAY_NAME,
    APP_EDITION,
    APP_GITHUB_DISPLAY,
    APP_GITHUB_URL,
    APP_SUBTITLE,
    APP_VERSION,
)


class ClickableLabel(QLabel):
    """Clickable label that opens a URL in the system browser."""

    def __init__(self, text: str, url: str = "", color: str = "#343945", parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                font-weight: 600;
                color: {color};
                background: transparent;
                text-decoration: none;
            }}
            QLabel:hover {{
                color: #7654DB;
                text-decoration: underline;
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.url:
            QDesktopServices.openUrl(QUrl(self.url))
        super().mousePressEvent(event)


class AboutPage(QWidget):
    """Polished white-glass About view with unified branding."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 28, 40, 28)
        layout.setSpacing(24)

        # 1. Page Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        lbl_title = QLabel("About")
        lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("Application information, creator credits, and contact information.")
        lbl_subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(lbl_subtitle)

        layout.addLayout(header_layout)

        # 2. Application Identity Card
        hero_card = QFrame()
        hero_card.setObjectName("cardFrame")
        apply_card_shadow(hero_card, blur_radius=20, y_offset=8, alpha=12)
        h_layout = QHBoxLayout(hero_card)
        h_layout.setContentsMargins(28, 32, 28, 32)
        h_layout.setSpacing(24)

        emblem = AppEmblem(size=72, radius=22, icon_size=40)
        h_layout.addWidget(emblem)

        hero_titles = QVBoxLayout()
        hero_titles.setSpacing(4)
        hero_titles.setAlignment(Qt.AlignVCenter)

        lbl_app_name = QLabel(APP_DISPLAY_NAME)
        lbl_app_name.setStyleSheet(
            "font-size: 26px; font-weight: 600; color: #202633; letter-spacing: -0.65px; background: transparent;"
        )
        hero_titles.addWidget(lbl_app_name)

        lbl_tagline = QLabel(APP_SUBTITLE)
        lbl_tagline.setStyleSheet(
            "font-size: 14px; font-weight: 500; color: #8061C9; background: transparent;"
        )
        hero_titles.addWidget(lbl_tagline)

        h_layout.addLayout(hero_titles)
        h_layout.addStretch()

        lbl_version_pill = QLabel(f"Version {APP_VERSION} • {APP_EDITION}")
        lbl_version_pill.setAlignment(Qt.AlignCenter)
        lbl_version_pill.setFixedHeight(36)
        lbl_version_pill.setStyleSheet("""
            QLabel {
                background-color: #F4F2FA;
                border: none;
                border-radius: 10px;
                color: #747783;
                font-size: 12px;
                font-weight: 500;
                padding: 0px 24px;
            }
        """)
        h_layout.addWidget(lbl_version_pill, alignment=Qt.AlignVCenter)

        layout.addWidget(hero_card)

        # 3. About This Application Card
        about_card = QFrame()
        about_card.setObjectName("cardFrame")
        apply_card_shadow(about_card, blur_radius=20, y_offset=8, alpha=12)
        a_layout = QVBoxLayout(about_card)
        a_layout.setContentsMargins(24, 22, 24, 22)
        a_layout.setSpacing(14)

        lbl_a_title = QLabel("About this application")
        lbl_a_title.setObjectName("cardHeading")
        a_layout.addWidget(lbl_a_title)

        div1 = QFrame()
        div1.setObjectName("sectionDivider")
        a_layout.addWidget(div1)

        lbl_a_intro = QLabel(
            "Auto Typo is a high-precision, portable desktop utility engineered for seamless "
            "keyboard simulation. It is designed specifically for:"
        )
        lbl_a_intro.setStyleSheet(
            "font-size: 14px; color: #646B7A; line-height: 1.5; background: transparent;"
        )
        lbl_a_intro.setWordWrap(True)
        a_layout.addWidget(lbl_a_intro)

        bullets_layout = QVBoxLayout()
        bullets_layout.setSpacing(8)
        bullets = [
            "Entertainment and fast typing automation",
            "Software testing and form filling simulations",
            "Repetitive keyboard workflows and productivity macros",
            "Benchmark tests and chat interaction demonstrations",
        ]
        for b_text in bullets:
            b_row = QHBoxLayout()
            b_row.setContentsMargins(2, 0, 0, 0)
            b_row.setSpacing(12)

            dot = QFrame()
            dot.setFixedSize(5, 5)
            dot.setStyleSheet("background-color: #9C87CC; border-radius: 2px; border: none;")
            b_row.addWidget(dot, alignment=Qt.AlignVCenter)

            lbl_b = QLabel(b_text)
            lbl_b.setStyleSheet("font-size: 14px; color: #4E5666; background: transparent;")
            b_row.addWidget(lbl_b)
            b_row.addStretch()
            bullets_layout.addLayout(b_row)

        a_layout.addLayout(bullets_layout)

        div2 = QFrame()
        div2.setObjectName("sectionDivider")
        a_layout.addWidget(div2)

        lbl_a_footer = QLabel(
            "Built with Python and PySide6 with zero cloud dependencies, complete offline persistence, "
            "and global approval safety."
        )
        lbl_a_footer.setStyleSheet(
            "font-size: 13px; color: #747783; background: transparent;"
        )
        lbl_a_footer.setWordWrap(True)
        a_layout.addWidget(lbl_a_footer)

        layout.addWidget(about_card)

        # 4. Author Card
        dev_card = QFrame()
        dev_card.setObjectName("cardFrame")
        apply_card_shadow(dev_card, blur_radius=20, y_offset=8, alpha=12)
        dev_layout = QVBoxLayout(dev_card)
        dev_layout.setContentsMargins(24, 22, 24, 24)
        dev_layout.setSpacing(16)

        lbl_dev_heading = QLabel("Author")
        lbl_dev_heading.setObjectName("cardHeading")
        dev_layout.addWidget(lbl_dev_heading)

        div3 = QFrame()
        div3.setObjectName("sectionDivider")
        dev_layout.addWidget(div3)

        cols_row = QHBoxLayout()
        cols_row.setSpacing(0)

        # Col 1: Name
        col1 = QVBoxLayout()
        col1.setSpacing(6)
        lbl_auth_cap = QLabel("Name")
        lbl_auth_cap.setStyleSheet("font-size: 11px; font-weight: 500; color: #747783; background: transparent;")
        col1.addWidget(lbl_auth_cap)
        lbl_author_name = QLabel(APP_AUTHOR)
        lbl_author_name.setStyleSheet("font-size: 15px; font-weight: 600; color: #343945; background: transparent;")
        col1.addWidget(lbl_author_name)
        cols_row.addLayout(col1, 1)

        cols_row.addWidget(self._create_vertical_divider())
        cols_row.addSpacing(28)

        # Col 2: GitHub Repo
        col2 = QVBoxLayout()
        col2.setSpacing(6)
        lbl_gh_cap = QLabel("GitHub")
        lbl_gh_cap.setStyleSheet("font-size: 11px; font-weight: 500; color: #747783; background: transparent;")
        col2.addWidget(lbl_gh_cap)
        col2.addWidget(ClickableLabel(APP_GITHUB_DISPLAY, APP_GITHUB_URL, color="#7654DB"))
        cols_row.addLayout(col2, 2)

        dev_layout.addLayout(cols_row)
        layout.addWidget(dev_card)

        # 5. Copyright Footer
        lbl_copy = QLabel(APP_COPYRIGHT)
        lbl_copy.setStyleSheet("font-size: 11px; color: #747783; padding-top: 6px; background: transparent;")
        lbl_copy.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_copy)

        layout.addStretch()

        scroll.setWidget(container)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    def _create_vertical_divider(self) -> QFrame:
        sep = QFrame()
        sep.setFixedSize(1, 48)
        sep.setStyleSheet("background-color: #EBECF1; border: none;")
        return sep
