from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
import config
from yalda.auth.authentication import authenticate_user, is_app_license_active
from yalda.views.password_recovery_dialog import PasswordRecoveryDialog
from yalda.views.trainer_register_dialog import TrainerRegisterDialog
from yalda.views.cloud_restore_dialog import CloudRestoreDialog

class LoginView(QWidget):
    login_success = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config.APP_NAME} - ورود به سیستم")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: #121212;")
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_activation_state()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card Container
        card = QFrame()
        card.setFixedSize(480, 590)
        card.setObjectName("login_card")
        card.setStyleSheet("""
            QFrame#login_card {
                background-color: #000000;
                border: 1px solid #222222;
                border-radius: 12px;
                padding: 20px 25px;
            }
            QLabel {
                background-color: transparent;
                background: transparent;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        # Logo Image
        icon_path = config.BASE_DIR / "resources" / "images" / "app_icon.png"
        if icon_path.exists():
            lbl_logo = QLabel()
            pix = QPixmap(str(icon_path)).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(pix)
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(lbl_logo)

        # Header Title
        title_lbl = QLabel(config.APP_NAME)
        title_lbl.setStyleSheet("color: #8B0000; font-size: 30px; font-weight: bold; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_lbl = QLabel("ورود به نرم‌افزار مدیریت باشگاه بدنسازی")
        sub_lbl.setStyleSheet("color: #CCCCCC; font-size: 13px; background: transparent;")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title_lbl)
        card_layout.addWidget(sub_lbl)
        card_layout.addSpacing(2)

        # Username Input
        lbl_user = QLabel("نام کاربری:")
        lbl_user.setStyleSheet("color: #DDDDDD; font-weight: bold; background: transparent;")
        
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(40)
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

        # Password Input Layout with Eye Button
        lbl_pass = QLabel("کلمه عبور:")
        lbl_pass.setStyleSheet("color: #DDDDDD; font-weight: bold; background: transparent;")
        
        pass_box = QHBoxLayout()
        pass_box.setSpacing(6)

        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(40)
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
        btn_eye.setFixedSize(44, 40)
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setToolTip("نمایش / پنهان‌سازی کلمه عبور")
        btn_eye.setStyleSheet("""
            QPushButton#eye_button {
                background-color: #8B0000;
                color: #FFFFFF;
                border: 1px solid #A00000;
                border-radius: 6px;
                font-size: 16px;
                font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", sans-serif;
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
        card_layout.addSpacing(4)

        # Actions Row: Forgot Password & Register New Trainer
        row_actions = QHBoxLayout()
        row_actions.setSpacing(8)

        self.btn_forgot = QPushButton("🔑 فراموشی کلمه عبور")
        self.btn_forgot.setFixedHeight(36)
        self.btn_forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_forgot.setStyleSheet("""
            QPushButton {
                background-color: #1F2937;
                color: #9CA3AF;
                border: 1px solid #374151;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #374151;
                color: #FFFFFF;
            }
        """)
        self.btn_forgot.clicked.connect(self.open_forgot_dialog)

        self.btn_register = QPushButton("📝 ثبت‌نام مربی جدید")
        self.btn_register.setFixedHeight(36)
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.clicked.connect(self.open_register_dialog)

        row_actions.addWidget(self.btn_forgot)
        row_actions.addWidget(self.btn_register)
        card_layout.addLayout(row_actions)

        # Cloud Restore Button (for new computer or fresh install)
        self.btn_cloud = QPushButton("☁️ بازیابی اطلاعات از سرور ابری (سیستم جدید)")
        self.btn_cloud.setFixedHeight(36)
        self.btn_cloud.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cloud.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: #93C5FD;
                border: 1px solid #2563EB;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
                color: #FFFFFF;
            }
        """)
        self.btn_cloud.clicked.connect(self.open_cloud_restore_dialog)
        card_layout.addWidget(self.btn_cloud)
        card_layout.addSpacing(6)

        # Submit Login Button
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
        self.refresh_activation_state()

    def refresh_activation_state(self):
        active = is_app_license_active()
        if active:
            self.btn_register.setEnabled(True)
            self.btn_register.setToolTip("ثبت‌نام مربی جدید در سیستم")
            self.btn_register.setStyleSheet("""
                QPushButton {
                    background-color: #065F46;
                    color: #A7F3D0;
                    border: 1px solid #059669;
                    border-radius: 6px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #047857;
                    color: #FFFFFF;
                }
            """)
        else:
            self.btn_register.setEnabled(False)
            self.btn_register.setToolTip("⚠️ ثبت‌نام مربی جدید در حال حاضر غیرفعال است.\nجهت فعال‌سازی، ابتدا ادمین کل باید وضعیت برنامه را فعال کند.")
            self.btn_register.setStyleSheet("""
                QPushButton {
                    background-color: #262626;
                    color: #666666;
                    border: 1px solid #333333;
                    border-radius: 6px;
                    font-size: 12px;
                }
            """)

    def toggle_password(self, field: QLineEdit, button: QPushButton):
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁️")

    def open_forgot_dialog(self):
        dlg = PasswordRecoveryDialog(self)
        dlg.recovery_success.connect(self.login_success.emit)
        dlg.exec()

    def open_register_dialog(self):
        if not is_app_license_active():
            QMessageBox.warning(self, "برنامه غیرفعال است", "ثبت‌نام مربی جدید غیرفعال می‌باشد. ادمین باید وضعیت برنامه را به فعال تغییر دهد.")
            return
        dlg = TrainerRegisterDialog(self)
        dlg.registration_success.connect(self.login_success.emit)
        dlg.exec()

    def open_cloud_restore_dialog(self):
        dlg = CloudRestoreDialog(self)
        dlg.restore_success.connect(self.login_success.emit)
        dlg.exec()

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
            reply = QMessageBox.question(
                self,
                "ورود ناموفق",
                "نام کاربری یا کلمه عبور در پایگاه‌داده محلی یافت نشد.\n\nآیا در حال راه‌اندازی نرم‌افزار روی سیستم جدید هستید و مایلید اطلاعات خود را با شماره موبایل از سرور ابری بازیابی کنید؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.open_cloud_restore_dialog()
