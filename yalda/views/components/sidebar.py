from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
import config

class Sidebar(QFrame):
    page_changed = pyqtSignal(str) # Emits view name, e.g. "dashboard", "members"
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)
        self.setStyleSheet("""
            QFrame#sidebar {
                background-color: #161616;
                border-left: 1px solid #282828;
            }
            QPushButton {
                background-color: transparent;
                color: #B0B0B0;
                text-align: right;
                padding: 12px 16px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #222222;
                color: #FFFFFF;
            }
            QPushButton[active="true"] {
                background-color: #8B0000;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)

        self.buttons = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        # Brand Header
        header = QHBoxLayout()
        logo_lbl = QLabel("🔥")
        logo_lbl.setStyleSheet("font-size: 24px;")
        
        title_lbl = QLabel(config.APP_NAME)
        title_lbl.setStyleSheet("color: #8B0000; font-size: 20px; font-weight: bold;")

        header.addWidget(logo_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)

        sub_lbl = QLabel("نرم‌افزار مدیریت باشگاه بدنسازی")
        sub_lbl.setStyleSheet("color: #666666; font-size: 11px; margin-bottom: 15px;")
        layout.addWidget(sub_lbl)

        # Navigation Buttons
        menu_items = [
            ("dashboard", "📊  داشبورد"),
            ("members", "👥  اعضای باشگاه"),
            ("workouts", "🏋️  برنامه‌ریزی تمرینی"),
            ("nutrition", "🥗  برنامه‌ریزی تغذیه"),
            ("exercises", "🏃  بانک حرکات ورزشی"),
            ("foods", "🍎  بانک مواد غذایی"),
            ("backup", "💾  پشتیبان‌گیری و تنظیمات")
        ]

        for nav_id, title in menu_items:
            btn = QPushButton(title)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, nid=nav_id: self.navigate(nid))
            layout.addWidget(btn)
            self.buttons[nav_id] = btn

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Logout Button
        btn_logout = QPushButton("🚪  خروج از حساب")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                font-weight: bold;
                text-align: right;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #B91C1C;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        btn_logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(btn_logout)

        # Set default active page
        self.set_active("dashboard")

    def navigate(self, nav_id: str):
        self.set_active(nav_id)
        self.page_changed.emit(nav_id)

    def set_active(self, nav_id: str):
        for key, btn in self.buttons.items():
            is_active = (key == nav_id)
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
