import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QGroupBox, QGridLayout, QComboBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import config
from yalda.services.backup_service import BackupService
from yalda.auth.authentication import (
    CurrentUser, update_trainer_profile, is_app_license_active, set_app_license_active, register_trainer
)
from yalda.views.components.jalali_calendar_widget import JalaliDatePicker
from yalda.utils.image_utils import get_circular_pixmap



class BackupView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.selected_photo_path = None
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_all_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title
        title = QLabel("⚙️ اطلاعات شخص مربی و پشتیبان‌گیری دیتابیس")
        title.setObjectName("h1")
        layout.addWidget(title)

        # ----------------------------------------------------
        # BOX 1: Trainer Profile & Credentials Settings
        # ----------------------------------------------------
        profile_box = QGroupBox("👤 اطلاعات شخص مربی و تنظیمات ورود")

        layout_prof = QVBoxLayout(profile_box)
        layout_prof.setSpacing(12)

        grid_prof = QGridLayout()
        grid_prof.setHorizontalSpacing(15)
        grid_prof.setVerticalSpacing(10)

        # Row 0: Photo & Names
        self.lbl_trainer_photo = QLabel("📷 بدون عکس")
        self.lbl_trainer_photo.setFixedSize(65, 65)
        self.lbl_trainer_photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_trainer_photo.setStyleSheet("border: 1px dashed #666; border-radius: 32px; color: #888;")

        btn_change_photo = QPushButton("📷 تغییر عکس مربی")
        btn_change_photo.setFixedHeight(36)
        btn_change_photo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change_photo.clicked.connect(self.choose_trainer_photo)

        photo_layout = QVBoxLayout()
        photo_layout.addWidget(self.lbl_trainer_photo, alignment=Qt.AlignmentFlag.AlignCenter)
        photo_layout.addWidget(btn_change_photo)

        grid_prof.addLayout(photo_layout, 0, 0, 2, 1)

        # Name fields
        self.txt_first_name = QLineEdit()
        self.txt_first_name.setFixedHeight(36)
        self.txt_first_name.setPlaceholderText("نام")

        self.txt_last_name = QLineEdit()
        self.txt_last_name.setFixedHeight(36)
        self.txt_last_name.setPlaceholderText("نام خانوادگی")

        grid_prof.addWidget(QLabel("نام مربی:"), 0, 1)
        grid_prof.addWidget(self.txt_first_name, 0, 2)
        grid_prof.addWidget(QLabel("نام خانوادگی:"), 0, 3)
        grid_prof.addWidget(self.txt_last_name, 0, 4)

        # Phone & Birthdate

        self.txt_phone = QLineEdit()
        self.txt_phone.setFixedHeight(36)
        self.txt_phone.setPlaceholderText("شماره همراه مربی")

        self.picker_birth_date = JalaliDatePicker(default_today=False)
        self.picker_birth_date.setFixedHeight(36)

        grid_prof.addWidget(QLabel("شماره همراه:"), 1, 1)
        grid_prof.addWidget(self.txt_phone, 1, 2)
        grid_prof.addWidget(QLabel("تاریخ تولد:"), 1, 3)
        grid_prof.addWidget(self.picker_birth_date, 1, 4)


        # Username, Passwords & Secret Recovery Code
        self.txt_username = QLineEdit()
        self.txt_username.setFixedHeight(36)
        self.txt_username.setPlaceholderText("نام کاربری مربی")

        self.txt_password = QLineEdit()
        self.txt_password.setFixedHeight(36)
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("کلمه عبور جدید (اختیاری)")

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

        btn_eye_pass = QPushButton("👁️")
        btn_eye_pass.setFixedSize(42, 36)
        btn_eye_pass.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_pass.setStyleSheet(EYE_STYLE)
        btn_eye_pass.clicked.connect(lambda: self.toggle_eye(self.txt_password, btn_eye_pass))
        pass_box = QHBoxLayout()
        pass_box.setSpacing(4)
        pass_box.addWidget(self.txt_password)
        pass_box.addWidget(btn_eye_pass)

        self.txt_recovery_code = QLineEdit()
        self.txt_recovery_code.setFixedHeight(36)
        self.txt_recovery_code.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_recovery_code.setPlaceholderText("رمز ریکاوری مخفی مربی")

        btn_eye_rec = QPushButton("👁️")
        btn_eye_rec.setFixedSize(42, 36)
        btn_eye_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye_rec.setStyleSheet(EYE_STYLE)
        btn_eye_rec.clicked.connect(lambda: self.toggle_eye(self.txt_recovery_code, btn_eye_rec))

        rec_box = QHBoxLayout()
        rec_box.setSpacing(4)
        rec_box.addWidget(self.txt_recovery_code)
        rec_box.addWidget(btn_eye_rec)

        grid_prof.addWidget(QLabel("نام کاربری:"), 2, 1)
        grid_prof.addWidget(self.txt_username, 2, 2)
        grid_prof.addWidget(QLabel("کلمه عبور جدید:"), 2, 3)
        grid_prof.addLayout(pass_box, 2, 4)

        grid_prof.addWidget(QLabel("رمز ریکاوری مخفی:"), 3, 1)
        grid_prof.addLayout(rec_box, 3, 2, 1, 3)

        layout_prof.addLayout(grid_prof)

        btn_save_prof = QPushButton("💾 ذخیره مشخصات مربی")
        btn_save_prof.setFixedHeight(40)
        btn_save_prof.setFixedWidth(200)
        btn_save_prof.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_prof.setStyleSheet("""
            QPushButton { background-color: #8B0000; color: white; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #A00000; }
        """)
        btn_save_prof.clicked.connect(self.save_trainer_profile)
        layout_prof.addWidget(btn_save_prof, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(profile_box)

        # ----------------------------------------------------
        # BOX 3: Backup & Restore Table
        # ----------------------------------------------------
        action_box = QGroupBox("💾 پشتیبان‌گیری محلی دیتابیس و عکس‌ها")
        layout_act = QHBoxLayout(action_box)

        lbl_desc = QLabel("با کلیک روی کلید زیر، از فایل دیتابیس و تمامی تصاویر فشرده‌سازی ZIP ایجاد می‌شود.")
        lbl_desc.setStyleSheet("color: #AAAAAA;")

        btn_create = QPushButton("⚡ ایجاد فایل پشتیبان جدید")
        btn_create.setFixedSize(220, 42)
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
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
        btn_restore_file.setCursor(Qt.CursorShape.PointingHandCursor)
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
        self.load_all_data()

    def toggle_eye(self, field: QLineEdit, button: QPushButton):
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            button.setText("🙈")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setText("👁️")

    def choose_trainer_photo(self):
        from yalda.utils.image_source_chooser import get_image_file_path
        temp_path = get_image_file_path(
            self,
            dialog_title="انتخاب یا ثبت تصویر مربی",
            file_filter="فایل‌های تصویری (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if temp_path and os.path.exists(temp_path):
            dest_dir = config.PROFILE_PHOTOS_DIR
            dest_dir.mkdir(parents=True, exist_ok=True)
            ext = Path(temp_path).suffix or ".jpg"
            import uuid
            filename = f"trainer_{uuid.uuid4().hex[:8]}{ext}"
            dest_path = dest_dir / filename
            import shutil
            shutil.copy2(temp_path, dest_path)
            self.selected_photo_path = str(dest_path)
            self.display_photo(str(dest_path))


    def display_photo(self, photo_path: str):
        if photo_path and os.path.exists(photo_path):
            pixmap = QPixmap(photo_path)
            circ = get_circular_pixmap(pixmap, 65)
            self.lbl_trainer_photo.setPixmap(circ)
            self.lbl_trainer_photo.setText("")
            self.lbl_trainer_photo.setStyleSheet("border: none; background: transparent;")
        else:
            self.lbl_trainer_photo.setText("📷 بدون عکس")
            self.lbl_trainer_photo.setStyleSheet("border: 1px dashed #666; border-radius: 32px; color: #888;")

    def load_all_data(self):
        # 1. Current trainer profile
        u = CurrentUser.get()
        if u:
            self.txt_first_name.setText(u.first_name or "")
            self.txt_last_name.setText(u.last_name or "")
            self.txt_phone.setText(u.phone or "")
            self.picker_birth_date.set_date(u.birth_date_shamsi or "")
            self.txt_username.setText(u.username or "")
            self.txt_password.clear()
            self.txt_recovery_code.setText(u.recovery_code or "")
            self.selected_photo_path = u.photo_path
            self.display_photo(u.photo_path)

        # 2. Backups
        self.load_backups()

    def save_trainer_profile(self):
        u = CurrentUser.get()
        if not u:
            return

        username = self.txt_username.text().strip()
        first_name = self.txt_first_name.text().strip()
        last_name = self.txt_last_name.text().strip()
        phone = self.txt_phone.text().strip()
        birth_date = self.picker_birth_date.get_date()
        password = self.txt_password.text().strip()
        recovery_code = self.txt_recovery_code.text().strip()

        if not username:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری را وارد کنید.")
            return

        try:
            update_trainer_profile(
                user_id=u.id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                birth_date_shamsi=birth_date,
                photo_path=self.selected_photo_path,
                username=username,
                new_password=password if password else None,
                recovery_code=recovery_code if recovery_code else None
            )
            QMessageBox.information(self, "موفقیت", "اطلاعات مربی با موفقیت به‌روزرسانی شد.")
            QMessageBox.information(self, "موفقیت", "اطلاعات مربی با موفقیت به‌روزرسانی شد.")
            self.load_all_data()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش اطلاعات مربی: {str(e)}")


    def load_backups(self):
        backups = BackupService.get_all_backups()
        self.table.setRowCount(len(backups))

        for row, b in enumerate(backups):
            self.table.setItem(row, 0, QTableWidgetItem(b.file_name))
            self.table.setItem(row, 1, QTableWidgetItem(b.backup_date_shamsi))
            self.table.setItem(row, 2, QTableWidgetItem(f"{b.backup_size_mb} MB"))

            btn_restore = QPushButton("🔄 بازگردانی")
            btn_restore.setObjectName("danger_button")
            btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_restore.clicked.connect(lambda _, fp=b.file_path: self.restore_backup(fp))
            self.table.setCellWidget(row, 3, btn_restore)

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
