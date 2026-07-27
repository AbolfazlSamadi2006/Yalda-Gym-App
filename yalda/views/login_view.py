from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QAction
import config
from yalda.auth.authentication import authenticate_user

class LoginView(QWidget):
    login_success = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config.APP_NAME} - ورود به سیستم")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card Container
        card = QFrame()
        card.setFixedSize(420, 440)
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #1E1E1E;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 30px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Header Title
        title_lbl = QLabel(config.APP_NAME)
        title_lbl.setStyleSheet("color: #8B0000; font-size: 28px; font-weight: bold; text-align: center;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("ورود به نرم‌افزار مدیریت باشگاه بدنسازی")
        sub_lbl.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title_lbl)
        card_layout.addWidget(sub_lbl)
        card_layout.addSpacing(10)

        # Username Input
        lbl_user = QLabel("نام کاربری:")
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(40)
        self.txt_username.setPlaceholderText("نام کاربری را وارد کنید")
        self.txt_username.setText("")
        
        card_layout.addWidget(lbl_user)
        card_layout.addWidget(self.txt_username)

        # Password Input Layout with Large Red Square Eye Button
        lbl_pass = QLabel("کلمه عبور:")
        pass_box = QHBoxLayout()
        pass_box.setSpacing(6)

        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(40)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("کلمه عبور را وارد کنید")
        self.txt_password.setText("")
        self.txt_password.returnPressed.connect(self.do_login)

        btn_eye = QPushButton("👁️")
        btn_eye.setObjectName("eye_button")
        btn_eye.setFixedSize(42, 40)
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
        card_layout.addSpacing(15)

        # Submit Button
        btn_login = QPushButton("ورود به سیستم")
        btn_login.setFixedHeight(44)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
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
