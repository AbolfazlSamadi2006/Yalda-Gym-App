from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QScrollArea
)

from PyQt6.QtCore import Qt, pyqtSignal
import config
from yalda.auth.authentication import verify_recovery_credentials, update_trainer_profile, CurrentUser

class PasswordRecoveryDialog(QDialog):
    recovery_success = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("بازیابی نام کاربری و کلمه عبور مربی")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(500, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.matched_user = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #121212;
                color: #FFFFFF;
                font-family: 'Vazirmatn', 'Segoe UI', sans-serif;
            }}
            QFrame#cardFrame {{
                background-color: #000000;
                border: 1px solid #333333;
                border-radius: 12px;
                padding: 15px;
            }}
            QLabel {{
                color: #E5E7EB;
                background: transparent;
            }}
            QLineEdit {{
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid #8B0000;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        # Header Title
        title_lbl = QLabel("🔑 بازیابی حساب کاربری مربی")
        title_lbl.setStyleSheet("color: #8B0000; font-size: 20px; font-weight: bold;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_lbl)

        desc_lbl = QLabel("لطفاً شماره تلفن همراه و رمز ریکاوری مخفی ثبت‌شده خود را وارد کنید:")
        desc_lbl.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        card_layout.addWidget(desc_lbl)

        # Inputs Step 1: Phone & Recovery Code
        card_layout.addWidget(QLabel("شماره همراه مربی:"))
        self.txt_phone = QLineEdit()
        self.txt_phone.setFixedHeight(38)
        self.txt_phone.setPlaceholderText("مثال: 09123456789")
        card_layout.addWidget(self.txt_phone)

        card_layout.addWidget(QLabel("رمز ریکاوری مخفی:"))
        pass_rec_box = QHBoxLayout()
        pass_rec_box.setSpacing(6)

        self.txt_recovery_code = QLineEdit()
        self.txt_recovery_code.setFixedHeight(38)
        self.txt_recovery_code.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_recovery_code.setPlaceholderText("رمز ریکاوری مخفی خود را وارد کنید")

        EYE_STYLE = """
            QPushButton {
                background-color: #8B0000;
                color: #FFFFFF;
                border: 1px solid #A91D22;
                border-radius: 6px;
                font-size: 16px;
                font-family: "Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji", sans-serif;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #A91D22;
            }
        """

        btn_eye_rec = QPushButton("👁️")
        btn_eye_rec.setFixedSize(42, 38)
        btn_eye_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_rec.setStyleSheet(EYE_STYLE)
        btn_eye_rec.clicked.connect(lambda: self.toggle_eye(self.txt_recovery_code, btn_eye_rec))

        pass_rec_box.addWidget(self.txt_recovery_code)
        pass_rec_box.addWidget(btn_eye_rec)
        card_layout.addLayout(pass_rec_box)

        # Verify Button
        self.btn_verify = QPushButton("🔍 بررسی و تایید اطلاعات")
        self.btn_verify.setFixedHeight(40)
        self.btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verify.setStyleSheet("""
            QPushButton {
                background-color: #2563EB; color: white; font-size: 14px; font-weight: bold; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #1D4ED8; }
        """)
        self.btn_verify.clicked.connect(self.do_verify)
        card_layout.addWidget(self.btn_verify)

        # Step 2 Container (Hidden initially)
        self.step2_frame = QFrame()
        self.step2_frame.setStyleSheet("background: transparent; border: none;")
        step2_layout = QVBoxLayout(self.step2_frame)
        step2_layout.setContentsMargins(0, 8, 0, 0)
        step2_layout.setSpacing(8)

        self.lbl_matched_username = QLabel("نام کاربری شما:")
        self.lbl_matched_username.setStyleSheet("color: #10B981; font-size: 14px; font-weight: bold;")
        step2_layout.addWidget(self.lbl_matched_username)

        step2_layout.addWidget(QLabel("کلمه عبور جدید:"))
        pass_new_box = QHBoxLayout()
        pass_new_box.setSpacing(6)

        self.txt_new_password = QLineEdit()
        self.txt_new_password.setFixedHeight(38)
        self.txt_new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_password.setPlaceholderText("کلمه عبور جدید را وارد کنید")

        btn_eye_new = QPushButton("👁️")
        btn_eye_new.setFixedSize(42, 38)
        btn_eye_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_new.setStyleSheet(EYE_STYLE)
        btn_eye_new.clicked.connect(lambda: self.toggle_eye(self.txt_new_password, btn_eye_new))

        pass_new_box.addWidget(self.txt_new_password)
        pass_new_box.addWidget(btn_eye_new)
        step2_layout.addLayout(pass_new_box)

        self.btn_reset_and_login = QPushButton("🔐 ذخیره کلمه عبور جدید و ورود")
        self.btn_reset_and_login.setFixedHeight(40)
        self.btn_reset_and_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset_and_login.setStyleSheet("""
            QPushButton {
                background-color: #8B0000; color: white; font-size: 14px; font-weight: bold; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #A00000; }
        """)
        self.btn_reset_and_login.clicked.connect(self.do_reset_and_login)
        step2_layout.addWidget(self.btn_reset_and_login)

        card_layout.addWidget(self.step2_frame)
        self.step2_frame.setVisible(False)

        scroll.setWidget(card)
        layout.addWidget(scroll)

    def toggle_eye(self, field: QLineEdit, btn: QPushButton):
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setText("👁️")

    def do_verify(self):
        phone = self.txt_phone.text().strip()
        code = self.txt_recovery_code.text().strip()

        if not phone or not code:
            QMessageBox.warning(self, "خطا", "لطفاً هم شماره همراه و هم رمز ریکاوری مخفی را وارد کنید.")
            return

        user = verify_recovery_credentials(phone, code)
        if user:
            self.matched_user = user
            self.lbl_matched_username.setText(f"✅ نام کاربری شما: {user.username}")
            self.txt_phone.setEnabled(False)
            self.txt_recovery_code.setEnabled(False)
            self.btn_verify.setEnabled(False)
            self.step2_frame.setVisible(True)
            self.setFixedSize(500, 680)
        else:
            QMessageBox.critical(self, "اطلاعات نادرست", "هیچ حسابی با این شماره همراه و رمز ریکاوری یافت نشد.")


    def do_reset_and_login(self):
        if not self.matched_user:
            return

        new_pass = self.txt_new_password.text().strip()
        if not new_pass:
            QMessageBox.warning(self, "خطا", "لطفاً کلمه عبور جدید را وارد کنید.")
            return

        try:
            update_trainer_profile(
                user_id=self.matched_user.id,
                first_name=self.matched_user.first_name,
                last_name=self.matched_user.last_name,
                phone=self.matched_user.phone,
                birth_date_shamsi=self.matched_user.birth_date_shamsi,
                photo_path=self.matched_user.photo_path,
                username=self.matched_user.username,
                password=new_pass,
                recovery_code=self.matched_user.recovery_code
            )
            CurrentUser.set(self.matched_user)
            QMessageBox.information(self, "موفقیت", f"کلمه عبور جدید با موفقیت ذخیره شد. خوش آمدید {self.matched_user.display_name}!")
            self.recovery_success.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در تغییر کلمه عبور: {str(e)}")
