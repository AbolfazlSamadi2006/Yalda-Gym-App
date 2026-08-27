import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QGroupBox, QGridLayout, QComboBox, QFrame, QDialog, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import config
from yalda.services.backup_service import BackupService
from yalda.auth.authentication import (
    CurrentUser, update_trainer_profile, is_app_license_active, set_app_license_active, register_trainer, delete_trainer_account, get_all_trainers
)
from yalda.views.components.jalali_calendar_widget import JalaliDatePicker
from yalda.utils.image_utils import get_circular_pixmap



class BackupView(QWidget):
    account_deleted_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.selected_photo_path = None
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_all_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
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
        self.txt_phone.setMaxLength(11)

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

        # Action Buttons for Profile
        row_prof_actions = QHBoxLayout()
        row_prof_actions.setSpacing(12)

        self.btn_save_prof = QPushButton("💾 ذخیره مشخصات مربی")
        self.btn_save_prof.setFixedHeight(40)
        self.btn_save_prof.setFixedWidth(200)
        self.btn_save_prof.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_prof.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: #FFFFFF;
                border: 1px solid #A91D22;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #A00000;
            }
            QPushButton:disabled {
                background-color: #2D2D2D;
                color: #777777;
                border: 1px solid #444444;
            }
        """)
        self.btn_save_prof.setEnabled(False)
        self.btn_save_prof.clicked.connect(self.save_trainer_profile)
        row_prof_actions.addWidget(self.btn_save_prof)

        # Connect listeners to detect profile changes
        self.txt_first_name.textChanged.connect(self.check_profile_dirty)
        self.txt_last_name.textChanged.connect(self.check_profile_dirty)
        self.txt_phone.textChanged.connect(self.check_profile_dirty)
        self.picker_birth_date.line_edit.textChanged.connect(self.check_profile_dirty)
        self.txt_username.textChanged.connect(self.check_profile_dirty)
        self.txt_password.textChanged.connect(self.check_profile_dirty)
        self.txt_recovery_code.textChanged.connect(self.check_profile_dirty)

        btn_del_account = QPushButton("🗑️ حذف حساب مربی و کلیه شاگردان")
        btn_del_account.setFixedHeight(40)
        btn_del_account.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del_account.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #EF4444;
                border: 1px solid #DC2626;
                border-radius: 6px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover {
                background-color: #DC2626;
                color: #FFFFFF;
            }
        """)
        btn_del_account.clicked.connect(self.delete_current_trainer_account)
        row_prof_actions.addWidget(btn_del_account)
        row_prof_actions.addStretch()

        layout_prof.addLayout(row_prof_actions)

        layout.addWidget(profile_box)

        # ----------------------------------------------------
        # BOX 2: Admin Trainers Management & Account Deletion (Admin Only)
        # ----------------------------------------------------
        self.box_admin_trainers = QGroupBox("👥 مدیریت مربیان و حذف حساب‌ها (مخصوص مدیر ارشد سیستم)")
        layout_adm = QVBoxLayout(self.box_admin_trainers)
        layout_adm.setSpacing(10)

        lbl_adm_desc = QLabel("به عنوان مدیر ارشد سیستم، می‌توانید حساب هر مربی را به همراه کلیه شاگردان، سوابق و برنامه‌هایش به صورت یکجا حذف کنید.")
        lbl_adm_desc.setStyleSheet("color: #AAAAAA; font-size: 13px;")
        layout_adm.addWidget(lbl_adm_desc)

        self.table_trainers = QTableWidget()
        self.table_trainers.setColumnCount(6)
        self.table_trainers.setHorizontalHeaderLabels(["ردیف", "نام و نام خانوادگی مربی", "نام کاربری", "شماره تماس", "تعداد شاگردان", "عملیات"])
        header_tr = self.table_trainers.horizontalHeader()
        header_tr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table_trainers.setColumnWidth(0, 55)
        header_tr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_trainers.setColumnWidth(2, 160)
        self.table_trainers.setColumnWidth(3, 160)
        self.table_trainers.setColumnWidth(4, 140)
        self.table_trainers.setColumnWidth(5, 200)
        self.table_trainers.verticalHeader().setVisible(False)
        self.table_trainers.verticalHeader().setDefaultSectionSize(54)
        self.table_trainers.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_trainers.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_trainers.setMinimumHeight(200)
        layout_adm.addWidget(self.table_trainers)

        layout.addWidget(self.box_admin_trainers)

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
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #8B0000;
                color: #FFFFFF;
                border: 1px solid #A91D22;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #A00000;
                border: 1px solid #DC2626;
            }
            QPushButton:pressed {
                background-color: #700000;
            }
        """)
        btn_create.clicked.connect(self.create_backup)

        layout_act.addWidget(lbl_desc)
        layout_act.addStretch()
        layout_act.addWidget(btn_create)
        layout.addWidget(action_box)

        # Backups List Table
        row_table_header = QHBoxLayout()
        lbl_table = QLabel("📋 لیست آرشیوهای پشتیبان موجود")
        lbl_table.setObjectName("h2")

        btn_restore_cloud = QPushButton("☁️ بازگردانی از سرور ابری...")
        btn_restore_cloud.setStyleSheet("""
            QPushButton {
                background-color: #1E3A8A;
                color: #93C5FD;
                border: 1px solid #2563EB;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563EB;
                color: #FFFFFF;
            }
        """)
        btn_restore_cloud.clicked.connect(self.open_cloud_restore_dialog)

        btn_restore_file = QPushButton("📁 بازگردانی از فایل خارجی...")
        btn_restore_file.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restore_file.setStyleSheet("""
            QPushButton {
                background-color: #262626;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #333333;
                border: 1px solid #71717A;
            }
        """)
        btn_restore_file.clicked.connect(self.restore_from_file)

        row_table_header.addWidget(lbl_table)
        row_table_header.addStretch()
        row_table_header.addWidget(btn_restore_cloud)
        row_table_header.addWidget(btn_restore_file)
        layout.addLayout(row_table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ردیف", "نام فایل پشتیبان", "تاریخ و زمان ثبت (شمسی)", "حجم فایل", "عملیات"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setColumnWidth(0, 50)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(2, 175)
        self.table.setColumnWidth(3, 90)
        self.table.setColumnWidth(4, 190)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setMinimumHeight(270)

        layout.addWidget(self.table)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

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
            self.check_profile_dirty()


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

    def check_profile_dirty(self):
        if getattr(self, "_loading_profile", False):
            return

        current = {
            "first_name": self.txt_first_name.text().strip(),
            "last_name": self.txt_last_name.text().strip(),
            "phone": self.txt_phone.text().strip(),
            "birth_date": self.picker_birth_date.get_date().strip(),
            "username": self.txt_username.text().strip(),
            "recovery_code": self.txt_recovery_code.text().strip(),
            "photo_path": self.selected_photo_path or ""
        }
        new_pass = self.txt_password.text().strip()
        is_dirty = bool(new_pass) or (current != getattr(self, "_baseline_profile", {}))
        self.btn_save_prof.setEnabled(is_dirty)

    def load_all_data(self):
        # 1. Current trainer profile
        u = CurrentUser.get()
        if u:
            self._loading_profile = True
            self.txt_first_name.setText(u.first_name or "")
            self.txt_last_name.setText(u.last_name or "")
            self.txt_phone.setText(u.phone or "")
            self.picker_birth_date.set_date(u.birth_date_shamsi or "")
            self.txt_username.setText(u.username or "")
            self.txt_password.clear()
            self.txt_recovery_code.setText(u.recovery_code or "")
            self.selected_photo_path = u.photo_path
            self.display_photo(u.photo_path)

            self._baseline_profile = {
                "first_name": (u.first_name or "").strip(),
                "last_name": (u.last_name or "").strip(),
                "phone": (u.phone or "").strip(),
                "birth_date": (u.birth_date_shamsi or "").strip(),
                "username": (u.username or "").strip(),
                "recovery_code": (u.recovery_code or "").strip(),
                "photo_path": u.photo_path or ""
            }
            self._loading_profile = False
            self.btn_save_prof.setEnabled(False)

        # 2. Admin Trainers Box visibility
        if CurrentUser.is_admin():
            self.box_admin_trainers.setVisible(True)
            self.load_trainers_for_admin()
        else:
            self.box_admin_trainers.setVisible(False)

        # 3. Backups
        self.load_backups()

    def load_trainers_for_admin(self):
        trainers = get_all_trainers()
        self.table_trainers.setRowCount(len(trainers))

        for row, t in enumerate(trainers):
            self.table_trainers.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_trainers.setItem(row, 1, QTableWidgetItem(t["full_name"]))
            self.table_trainers.setItem(row, 2, QTableWidgetItem(t["username"]))
            self.table_trainers.setItem(row, 3, QTableWidgetItem(t["phone"]))
            self.table_trainers.setItem(row, 4, QTableWidgetItem(f"{t['member_count']} نفر"))

            for c in (0, 2, 3, 4):
                item = self.table_trainers.item(row, c)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            action_w = QWidget()
            action_w.setStyleSheet("background: transparent;")
            action_l = QHBoxLayout(action_w)
            action_l.setContentsMargins(8, 6, 8, 6)
            action_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_del = QPushButton("🗑️ حذف مربی و شاگردان")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setFixedHeight(34)
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #EF4444;
                    border: 1px solid #DC2626;
                    border-radius: 6px;
                    font-weight: bold;
                    padding: 4px 14px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                    color: #FFFFFF;
                }
            """)
            btn_del.clicked.connect(lambda _, t_id=t["id"], t_name=t["full_name"], m_cnt=t["member_count"]: self.admin_delete_trainer(t_id, t_name, m_cnt))
            action_l.addWidget(btn_del)
            self.table_trainers.setCellWidget(row, 5, action_w)

    def admin_delete_trainer(self, trainer_id: int, trainer_name: str, member_count: int):
        reply1 = QMessageBox.warning(
            self,
            "⚠️ تایید حذف مربی توسط مدیر ارشد",
            f"آیا مطمئن هستید که می‌خواهید مربی «{trainer_name}» را به همراه کلیه {member_count} شاگرد، سوابق و برنامه‌های ایشان حذف کنید؟\n\nاین عملیات غیرقابل بازگشت است!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply1 != QMessageBox.StandardButton.Yes:
            return

        reply2 = QMessageBox.critical(
            self,
            "🔴 تایید نهایی حذف",
            f"تمامی اطلاعات مربی «{trainer_name}» از دیتابیس و فضای ابری پاک خواهد شد. آیا تایید می‌کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply2 == QMessageBox.StandardButton.Yes:
            try:
                delete_trainer_account(trainer_id)
                QMessageBox.information(self, "موفقیت", f"حساب مربی «{trainer_name}» و کلیه شاگردان ایشان با موفقیت حذف شدند.")
                self.load_all_data()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف مربی: {str(e)}")

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

        if phone:
            phone_digits = "".join(filter(str.isdigit, phone.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789'))))
            if len(phone_digits) > 11:
                QMessageBox.warning(
                    self,
                    "خطا در شماره تلفن",
                    "شماره تماس نمی‌تواند بیشتر از ۱۱ رقم باشد."
                )
                self.txt_phone.setFocus()
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
                password=password if password else None,
                recovery_code=recovery_code if recovery_code else None
            )
            QMessageBox.information(self, "موفقیت", "اطلاعات مربی با موفقیت به‌روزرسانی شد.")
            self.load_all_data()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش اطلاعات مربی: {str(e)}")


    def load_backups(self):
        backups = BackupService.get_all_backups()
        self.table.setRowCount(len(backups))

        for row, b in enumerate(backups):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(b.file_name))
            self.table.setItem(row, 2, QTableWidgetItem(b.backup_date_shamsi))
            self.table.setItem(row, 3, QTableWidgetItem(f"{b.backup_size_mb} MB"))

            for c in (0, 2, 3):
                item = self.table.item(row, c)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            action_w = QWidget()
            action_w.setStyleSheet("background: transparent;")
            action_l = QHBoxLayout(action_w)
            action_l.setContentsMargins(4, 4, 4, 4)
            action_l.setSpacing(6)
            action_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_restore = QPushButton("🔄 بازگردانی")
            btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_restore.setFixedHeight(30)
            btn_restore.setStyleSheet("background-color: #D97706; color: #FFFFFF; font-weight: bold; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
            btn_restore.clicked.connect(lambda _, fp=b.file_path: self.restore_backup(fp))

            btn_delete = QPushButton("🗑️ حذف")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.setFixedHeight(30)
            btn_delete.setStyleSheet("background-color: #DC2626; color: #FFFFFF; font-weight: bold; border-radius: 4px; padding: 2px 8px; font-size: 11px;")
            btn_delete.clicked.connect(lambda _, b_id=b.id, fn=b.file_name: self.delete_backup_item(b_id, fn))

            action_l.addWidget(btn_restore)
            action_l.addWidget(btn_delete)
            self.table.setCellWidget(row, 4, action_w)

    def delete_backup_item(self, backup_id: int, file_name: str):
        reply = QMessageBox.warning(
            self,
            "⚠️ تایید حذف نسخه پشتیبان",
            f"آیا مطمئن هستید که می‌خواهید فایل پشتیبان «{file_name}» را حذف کنید؟\nاین فایل به طور کامل از روی حافظه سیستم پاک خواهد شد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if BackupService.delete_backup(backup_id):
                    QMessageBox.information(self, "موفقیت", f"نسخه پشتیبان «{file_name}» با موفقیت حذف گردید.")
                    self.load_backups()
                else:
                    QMessageBox.warning(self, "خطا", "یافتن یا حذف فایل پشتیبان با خطا مواجه شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف فایل پشتیبان: {str(e)}")

    def create_backup(self):
        try:
            filepath = BackupService.create_backup()
            self.load_backups()
            QMessageBox.information(self, "موفقیت", f"فایل پشتیبان با موفقیت ایجاد شد:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد پشتیبان: {str(e)}")

    def open_cloud_restore_dialog(self):
        from yalda.views.cloud_restore_dialog import CloudRestoreDialog
        u = CurrentUser.get()
        init_phone = u.phone if u else ""
        dlg = CloudRestoreDialog(self, initial_phone=init_phone)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.load_all_data()

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

    def delete_current_trainer_account(self):
        u = CurrentUser.get()
        if not u:
            return

        if u.username == "admin" or u.role == "admin":
            QMessageBox.warning(self, "خطا", "حساب کاربری مدیر ارشد سیستم قابل حذف نمی‌باشد.")
            return

        reply1 = QMessageBox.warning(
            self,
            "⚠️ هشدار حذف کامل حساب کاربری مربی",
            f"آیا مطمئن هستید که می‌خواهید حساب کاربری «{u.display_name}» را به همراه کلیه شاگردان، سوابق و برنامه‌ها حذف کنید؟\n\nاین عملیات غیرقابل بازگشت است!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply1 != QMessageBox.StandardButton.Yes:
            return

        reply2 = QMessageBox.critical(
            self,
            "🔴 تایید نهایی حذف",
            "کلیه اطلاعات این مربی از حافظه سیستم و سرور ابری پاک خواهد شد. آیا تایید نهایی را صادر می‌کنید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply2 == QMessageBox.StandardButton.Yes:
            try:
                delete_trainer_account(u.id)
                QMessageBox.information(self, "موفقیت", "حساب کاربری مربی و تمامی اطلاعات شاگردان با موفقیت حذف گردید.")
                CurrentUser.logout()
                self.account_deleted_signal.emit()
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در حذف حساب کاربری: {str(e)}")

