from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from yalda.services.backup_service import BackupService
from yalda.auth.authentication import CurrentUser, update_user_credentials

class BackupView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title
        title = QLabel("💾 پشتیبان‌گیری، بازگردانی و تنظیمات سیستم")
        title.setObjectName("h1")
        layout.addWidget(title)

        # User Credentials Box (Account Settings)
        creds_box = QGroupBox("🔑 تنظیمات نام کاربری و کلمه عبور اختصاصی مربی")
        layout_creds = QVBoxLayout(creds_box)
        layout_creds.setSpacing(12)

        lbl_creds_note = QLabel("مربی محترم، می‌توانید نام کاربری و کلمه عبور دلخواه خود را جهت ورود به برنامه تنظیم کنید.")
        lbl_creds_note.setStyleSheet("color: #888888; font-size: 12px;")
        layout_creds.addWidget(lbl_creds_note)

        grid_creds = QGridLayout()
        grid_creds.setHorizontalSpacing(15)
        grid_creds.setVerticalSpacing(10)

        # Row 0: Username
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(38)
        self.txt_username.setPlaceholderText("نام کاربری جدید مربی")
        grid_creds.addWidget(QLabel("نام کاربری جدید:"), 0, 0)
        grid_creds.addWidget(self.txt_username, 0, 1, 1, 3)

        # Row 1: New Password & Confirm Password
        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(38)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("کلمه عبور جدید (در صورت عدم تغییر خالی بگذارید)")

        btn_eye1 = QPushButton("👁️")
        btn_eye1.setObjectName("eye_button")
        btn_eye1.setFixedSize(42, 38)
        btn_eye1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye1.setToolTip("نمایش / پنهان‌سازی کلمه عبور")
        btn_eye1.setStyleSheet("""
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
        btn_eye1.clicked.connect(lambda: self.toggle_password(self.txt_password, btn_eye1))

        pass1_box = QHBoxLayout()
        pass1_box.setSpacing(6)
        pass1_box.addWidget(self.txt_password)
        pass1_box.addWidget(btn_eye1)

        self.txt_password_confirm = QLineEdit()
        self.txt_password_confirm.setFixedHeight(38)
        self.txt_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password_confirm.setPlaceholderText("تکرار کلمه عبور جدید")

        btn_eye2 = QPushButton("👁️")
        btn_eye2.setObjectName("eye_button")
        btn_eye2.setFixedSize(42, 38)
        btn_eye2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye2.setToolTip("نمایش / پنهان‌سازی کلمه عبور")
        btn_eye2.setStyleSheet("""
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
        btn_eye2.clicked.connect(lambda: self.toggle_password(self.txt_password_confirm, btn_eye2))

        pass2_box = QHBoxLayout()
        pass2_box.setSpacing(6)
        pass2_box.addWidget(self.txt_password_confirm)
        pass2_box.addWidget(btn_eye2)

        grid_creds.addWidget(QLabel("کلمه عبور جدید:"), 1, 0)
        grid_creds.addLayout(pass1_box, 1, 1)
        grid_creds.addWidget(QLabel("تکرار کلمه عبور:"), 1, 2)
        grid_creds.addLayout(pass2_box, 1, 3)

        layout_creds.addLayout(grid_creds)

        btn_save_creds = QPushButton("💾 ذخیره مشخصات ورود")
        btn_save_creds.setFixedHeight(40)
        btn_save_creds.setFixedWidth(200)
        btn_save_creds.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_creds.clicked.connect(self.save_user_credentials)
        layout_creds.addWidget(btn_save_creds, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(creds_box)

        # Backup Action Box
        action_box = QGroupBox("پشتیبان‌گیری محلی یک کلیکی")
        layout_act = QHBoxLayout(action_box)

        lbl_desc = QLabel("با کلیک روی کلید زیر، از پایگاه‌داده و تمامی تصاویر ورزشکاران فایل فشرده ZIP ایجاد می‌شود.")
        lbl_desc.setStyleSheet("color: #AAAAAA;")

        btn_create = QPushButton("⚡ ایجاد فایل پشتیبان جدید")
        btn_create.setFixedSize(220, 42)
        btn_create.clicked.connect(self.create_backup)

        layout_act.addWidget(lbl_desc)
        layout_act.addStretch()
        layout_act.addWidget(btn_create)
        layout.addWidget(action_box)

        # Backups List Table
        row_table_header = QHBoxLayout()
        lbl_table = QLabel("📋 لیست آرشیوهای پشتیبان موجود")
        lbl_table.setObjectName("h2")

        btn_restore_file = QPushButton("📁 بازگردانی از فایل خارجی...")
        btn_restore_file.setObjectName("secondary_button")
        btn_restore_file.clicked.connect(self.restore_from_file)

        row_table_header.addWidget(lbl_table)
        row_table_header.addStretch()
        row_table_header.addWidget(btn_restore_file)
        layout.addLayout(row_table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["نام فایل پشتیبان", "تاریخ ثبت (شمسی)", "حجم (MB)", "عملیات بازگردانی"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        self.load_backups()

    def load_backups(self):
        self.load_user_credentials()
        backups = BackupService.get_all_backups()
        self.table.setRowCount(len(backups))

        for row, b in enumerate(backups):
            self.table.setItem(row, 0, QTableWidgetItem(b.file_name))
            self.table.setItem(row, 1, QTableWidgetItem(b.backup_date_shamsi))
            self.table.setItem(row, 2, QTableWidgetItem(f"{b.backup_size_mb} MB"))

            btn_restore = QPushButton("🔄 بازگردانی")
            btn_restore.setObjectName("danger_button")
            btn_restore.clicked.connect(lambda _, fp=b.file_path: self.restore_backup(fp))
            self.table.setCellWidget(row, 3, btn_restore)

    def toggle_password(self, field: QLineEdit, button: QPushButton):
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁️")

    def load_user_credentials(self):
        user = CurrentUser.get()
        if user and user.username:
            self.txt_username.setText(user.username)
        self.txt_password.clear()
        self.txt_password_confirm.clear()

    def save_user_credentials(self):
        new_username = self.txt_username.text().strip()
        new_password = self.txt_password.text().strip()
        confirm_password = self.txt_password_confirm.text().strip()

        if not new_username:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری را وارد کنید.")
            return

        if new_password:
            if new_password != confirm_password:
                QMessageBox.warning(self, "خطا", "کلمه عبور جدید و تکرار آن یکسان نیستند.")
                return

        try:
            update_user_credentials(new_username=new_username, new_password=new_password if new_password else None)
            QMessageBox.information(self, "موفقیت", "مشخصات ورود با موفقیت ذخیره شد.\nاز این پس می‌توانید با نام کاربری و کلمه عبور جدید وارد شوید.")
            self.load_user_credentials()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره مشخصات: {str(e)}")

    def create_backup(self):
        try:
            filepath = BackupService.create_backup()
            self.load_backups()
            QMessageBox.information(self, "موفقیت", f"فایل پشتیبان با موفقیت ایجاد شد:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد پشتیبان: {str(e)}")

    def restore_from_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل پشتیبان ZIP", "", "Backup Files (*.zip *.yalda_bak)")
        if filepath:
            self.restore_backup(filepath)

    def restore_backup(self, filepath: str):
        reply = QMessageBox.warning(
            self,
            "تایید بازگردانی اطلاعات",
            "⚠️ آیا مطمئن هستید؟ با بازگردانی اطلاعات، تمام داده‌های فعلی جایگزین خواهند شد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                BackupService.restore_backup(filepath)
                QMessageBox.information(self, "موفقیت", "اطلاعات دیتابیس و تصاویر با موفقیت بازگردانی شد. لطفا برنامه را یکبار باز و بست کنید.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در بازگردانی: {str(e)}")
