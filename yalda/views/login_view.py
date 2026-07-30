from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
import config
from yalda.auth.authentication import authenticate_user

class LoginView(QWidget):
    login_success = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config.APP_NAME} - ورود به سیستم")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #121212;")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card Container (Pure Black Background on Matte Dark Window)
        card = QFrame()
        card.setFixedSize(440, 450)
        card.setObjectName("login_card")
        card.setStyleSheet("""
            QFrame#login_card {
                background-color: #000000;
                border: 1px solid #222222;
                border-radius: 12px;
                padding: 25px;
            }
            QLabel {
                background-color: transparent;
                background: transparent;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)

        # Header Title
        title_lbl = QLabel(config.APP_NAME)
        title_lbl.setStyleSheet("color: #8B0000; font-size: 32px; font-weight: bold; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("ورود به نرم‌افزار مدیریت باشگاه بدنسازی")
        sub_lbl.setStyleSheet("color: #CCCCCC; font-size: 13px; background: transparent;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title_lbl)
        card_layout.addWidget(sub_lbl)
        card_layout.addSpacing(10)

        # Username Input
        lbl_user = QLabel("نام کاربری:")
        lbl_user.setStyleSheet("color: #DDDDDD; font-weight: bold; background: transparent;")
        
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(42)
        self.txt_username.setPlaceholderText("نام کاربری را وارد کنید")
        self.txt_username.setText("")
        self.txt_username.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #8B0000;
            }
        """)
        
        card_layout.addWidget(lbl_user)
        card_layout.addWidget(self.txt_username)

        # Password Input Layout with Large Red Square Eye Button
        lbl_pass = QLabel("کلمه عبور:")
        lbl_pass.setStyleSheet("color: #DDDDDD; font-weight: bold; background: transparent;")
        
        pass_box = QHBoxLayout()
        pass_box.setSpacing(6)

        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(42)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("کلمه عبور را وارد کنید")
        self.txt_password.setText("")
        self.txt_password.returnPressed.connect(self.do_login)
        self.txt_password.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #8B0000;
            }
        """)

        btn_eye = QPushButton("👁️")
        btn_eye.setObjectName("eye_button")
        btn_eye.setFixedSize(44, 42)
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setToolTip("نمایش / پنهان‌سازی کلمه عبور")
        btn_eye.setStyleSheet("""
            QPushButton#eye_button {
                background-color: #8B0000;
                color: #FFFFFF;
                border: 1px solid #A00000;
                border-radius: 6px;
                font-size: 16px;
                padding: 0px;
                margin: 0px;
            }
            QPushButton#eye_button:hover {
                background-color: #A00000;
            }
        """)
        btn_eye.clicked.connect(lambda: self.toggle_password(self.txt_password, btn_eye))

        pass_box.addWidget(self.txt_password)
        pass_box.addWidget(btn_eye)

        card_layout.addWidget(lbl_pass)
        card_layout.addLayout(pass_box)
        card_layout.addSpacing(10)

        # Submit Button (Red Background)
        btn_login = QPushButton("ورود به سیستم")
        btn_login.setFixedHeight(44)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: #FFFFFF;
                font-size: 15px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #A00000;
            }
        """)
        btn_login.clicked.connect(self.do_login)
        card_layout.addWidget(btn_login)

        main_layout.addWidget(card)

    def toggle_password(self, field: QLineEdit, button: QPushButton):
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁️")

    def do_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری و کلمه عبور را وارد کنید.")
            return

        user = authenticate_user(username, password)
        if user:
            self.login_success.emit()
        else:
            QMessageBox.critical(self, "ورود ناموفق", "نام کاربری یا کلمه عبور اشتباه است.")
