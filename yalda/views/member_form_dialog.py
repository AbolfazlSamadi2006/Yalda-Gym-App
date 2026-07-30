from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QMessageBox, QDoubleSpinBox, QFileDialog
)
from PyQt6.QtCore import Qt
from yalda.views.components.jalali_calendar_widget import JalaliDatePicker
from yalda.utils.jalali_date import get_today_shamsi, add_months_shamsi
import os

class MemberFormDialog(QDialog):
    def __init__(self, parent=None, member_data=None):
        super().__init__(parent)
        self.member_data = member_data
        self.photo_path = None
        self.setWindowTitle("ثبت / ویرایش ورزشکار جدید")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(540, 630)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Name Row
        row1 = QHBoxLayout()
        self.txt_first_name = QLineEdit()
        self.txt_first_name.setPlaceholderText("نام")
        self.txt_last_name = QLineEdit()
        self.txt_last_name.setPlaceholderText("نام خانوادگی")
        row1.addWidget(QLabel("نام:"))
        row1.addWidget(self.txt_first_name)
        row1.addWidget(QLabel("نام خانوادگی:"))
        row1.addWidget(self.txt_last_name)
        layout.addLayout(row1)

        # Phone & Gender Row
        row2 = QHBoxLayout()
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("09123456789")
        self.combo_gender = QComboBox()
        self.combo_gender.addItem("آقا", "male")
        self.combo_gender.addItem("خانم", "female")
        row2.addWidget(QLabel("تلفن همراه:"))
        row2.addWidget(self.txt_phone)
        row2.addWidget(QLabel("جنسیت:"))
        row2.addWidget(self.combo_gender)
        layout.addLayout(row2)

        # Birthdate Row
        row_birth = QHBoxLayout()
        self.picker_birth = JalaliDatePicker(default_today=False)
        row_birth.addWidget(QLabel("تاریخ تولد:"))
        row_birth.addWidget(self.picker_birth)
        layout.addLayout(row_birth)

        # Photo Selection Row (Optional)
        row_photo = QHBoxLayout()
        btn_photo = QPushButton("📷 انتخاب عکس پروفایل (اختیاری)")
        btn_photo.setObjectName("secondary_button")
        btn_photo.clicked.connect(self.choose_photo)
        self.lbl_photo_status = QLabel("عکس انتخاب نشده است")
        self.lbl_photo_status.setStyleSheet("color: #888888; font-size: 11px;")
        row_photo.addWidget(btn_photo)
        row_photo.addWidget(self.lbl_photo_status)
        row_photo.addStretch()
        layout.addLayout(row_photo)

        # Physical Stats Row (Height & Weight)
        row_stats = QHBoxLayout()
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(100.0, 230.0)
        self.spin_height.setValue(175.0)
        self.spin_height.setDecimals(0)
        self.spin_height.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_height.setMinimumWidth(90)

        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(30.0, 200.0)
        self.spin_weight.setValue(75.0)
        self.spin_weight.setDecimals(1)
        self.spin_weight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_weight.setMinimumWidth(90)

        self.lbl_bmi_badge = QLabel("BMI: 24.5 (طبیعی)")
        self.lbl_bmi_badge.setStyleSheet("font-weight: bold; padding: 4px 10px; border-radius: 6px; background-color: #10B981; color: white;")

        self.spin_height.valueChanged.connect(self.update_bmi_display)
        self.spin_weight.valueChanged.connect(self.update_bmi_display)

        row_stats.addWidget(QLabel("قد (cm):"))
        row_stats.addWidget(self.spin_height)
        row_stats.addSpacing(10)
        row_stats.addWidget(QLabel("وزن (kg):"))
        row_stats.addWidget(self.spin_weight)
        row_stats.addSpacing(10)
        row_stats.addWidget(self.lbl_bmi_badge)
        layout.addLayout(row_stats)

        self.update_bmi_display()

        # Membership Type Row
        row4 = QHBoxLayout()
        self.combo_membership = QComboBox()
        self.combo_membership.addItem("۱۲ جلسه در ماه", "12_sessions")
        self.combo_membership.addItem("۸ جلسه در ماه", "8_sessions")
        self.combo_membership.addItem("۱۶ جلسه در ماه", "16_sessions")
        self.combo_membership.addItem("۲۰ جلسه در ماه", "20_sessions")
        self.combo_membership.addItem("دسترسی روزانه", "daily_access")
        self.combo_membership.currentIndexChanged.connect(self.on_membership_type_changed)

        row4.addWidget(QLabel("نوع عضویت:"))
        row4.addWidget(self.combo_membership)
        layout.addLayout(row4)

        # Membership Dates Row
        row5 = QHBoxLayout()
        self.picker_start = JalaliDatePicker(default_today=True)
        self.picker_start.date_changed.connect(self.recalculate_expiry)
        
        self.picker_expire = JalaliDatePicker(default_today=False)
        self.recalculate_expiry()

        row5.addWidget(QLabel("تاریخ شروع:"))
        row5.addWidget(self.picker_start)
        row5.addWidget(QLabel("تاریخ انقضا:"))
        row5.addWidget(self.picker_expire)
        layout.addLayout(row5)

        # Notes
        layout.addWidget(QLabel("یادداشت‌های مربی:"))
        self.txt_notes = QTextEdit()
        self.txt_notes.setAcceptRichText(False)
        self.txt_notes.setMaximumHeight(70)
        layout.addWidget(self.txt_notes)

        # Submit Buttons
        btn_box = QHBoxLayout()
        btn_save = QPushButton("ذخیره اطلاعات")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("انصراف")
        btn_cancel.setObjectName("secondary_button")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addWidget(btn_save)
        btn_box.addWidget(btn_cancel)
        layout.addLayout(btn_box)

        # Load existing data if editing
        if self.member_data:
            self.load_member_data()

    def choose_photo(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "انتخاب تصویر پروفایل ورزشکار", "", "فایل‌های تصویری (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if filepath:
            self.photo_path = filepath
            self.lbl_photo_status.setText(f"عکس: {os.path.basename(filepath)}")
            self.lbl_photo_status.setStyleSheet("color: #4CAF50; font-size: 11px;")

    def update_bmi_display(self):
        from yalda.utils.bmi_calculator import calculate_bmi_info
        h = self.spin_height.value()
        w = self.spin_weight.value()
        bmi, cat, color = calculate_bmi_info(h, w)
        if bmi > 0:
            self.lbl_bmi_badge.setText(f"BMI: {bmi} ({cat})")
            self.lbl_bmi_badge.setStyleSheet(f"font-weight: bold; padding: 4px 10px; border-radius: 6px; background-color: {color}; color: white;")
        else:
            self.lbl_bmi_badge.setText("BMI: -")
            self.lbl_bmi_badge.setStyleSheet("font-weight: bold; padding: 4px 10px; border-radius: 6px; background-color: #555555; color: white;")

    def recalculate_expiry(self):
        start_date = self.picker_start.text()
        if start_date:
            expire_date = add_months_shamsi(start_date, 1)
            self.picker_expire.setText(expire_date)

    def on_membership_type_changed(self):
        self.recalculate_expiry()

    def save(self):
        if not self.txt_first_name.text().strip() or not self.txt_last_name.text().strip() or not self.txt_phone.text().strip():
            QMessageBox.warning(self, "خطا", "لطفاً نام، نام خانوادگی و شماره تلفن را وارد کنید.")
            return

        try:
            from yalda.services.member_service import MemberService
            data = self.get_data()
            if self.member_data:
                MemberService.update_member(self.member_data.id, data)
                QMessageBox.information(self, "موفقیت", "اطلاعات ورزشکار با موفقیت ویرایش شد.")
            else:
                MemberService.create_member(data)
                QMessageBox.information(self, "موفقیت", "ورزشکار جدید با موفقیت ثبت شد.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت اطلاعات: {str(e)}")

    def get_data(self) -> dict:
        return {
            "first_name": self.txt_first_name.text().strip(),
            "last_name": self.txt_last_name.text().strip(),
            "phone": self.txt_phone.text().strip(),
            "gender": self.combo_gender.currentData(),
            "birth_date_shamsi": self.picker_birth.text(),
            "height_cm": self.spin_height.value(),
            "initial_weight_kg": self.spin_weight.value(),
            "membership_type": self.combo_membership.currentData(),
            "membership_start_shamsi": self.picker_start.text(),
            "membership_expire_shamsi": self.picker_expire.text(),
            "photo_path": self.photo_path,
            "notes": self.txt_notes.toPlainText().strip()
        }

    def load_member_data(self):
        m = self.member_data
        self.txt_first_name.setText(m.first_name)
        self.txt_last_name.setText(m.last_name)
        self.txt_phone.setText(m.phone)
        self.spin_height.setValue(m.height_cm or 175.0)
        self.spin_weight.setValue(m.initial_weight_kg or 75.0)
        self.photo_path = m.photo_path
        if self.photo_path and os.path.exists(self.photo_path):
            self.lbl_photo_status.setText(f"عکس: {os.path.basename(self.photo_path)}")
            self.lbl_photo_status.setStyleSheet("color: #4CAF50; font-size: 11px;")
        
        idx_g = self.combo_gender.findData(m.gender)
        if idx_g >= 0:
            self.combo_gender.setCurrentIndex(idx_g)

        idx_m = self.combo_membership.findData(m.membership_type)
        if idx_m >= 0:
            self.combo_membership.setCurrentIndex(idx_m)

        if m.birth_date_shamsi:
            self.picker_birth.setText(m.birth_date_shamsi)
        if m.membership_start_shamsi:
            self.picker_start.setText(m.membership_start_shamsi)
        if m.membership_expire_shamsi:
            self.picker_expire.setText(m.membership_expire_shamsi)
        if m.notes:
            self.txt_notes.setText(m.notes)
        self.update_bmi_display()
