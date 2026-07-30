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

        # Phone, Job & Gender Row
        row2 = QHBoxLayout()
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("09123456789")
        self.txt_phone.setMaxLength(11)
        self.txt_phone.setFixedWidth(115)

        self.txt_job = QLineEdit()
        self.txt_job.setPlaceholderText("شغل / حرفه")

        self.combo_gender = QComboBox()
        self.combo_gender.addItem("آقا", "male")
        self.combo_gender.addItem("خانم", "female")
        self.combo_gender.setMinimumWidth(90)

        row2.addWidget(QLabel("تلفن همراه:"))
        row2.addWidget(self.txt_phone)
        row2.addWidget(QLabel("شغل:"))
        row2.addWidget(self.txt_job)
        row2.addWidget(QLabel("جنسیت:"))
        row2.addWidget(self.combo_gender)
        layout.addLayout(row2)

        # Birthdate & Profile Photo Selection Row
        row_birth_photo = QHBoxLayout()
        self.picker_birth = JalaliDatePicker(default_today=False)
        self.picker_birth.setFixedWidth(155)

        self.btn_photo = QPushButton("📷 تصویر پروفایل")
        self.btn_photo.setObjectName("secondary_button")
        self.btn_photo.clicked.connect(self.choose_photo)

        row_birth_photo.addWidget(QLabel("تاریخ تولد:"))
        row_birth_photo.addWidget(self.picker_birth)
        row_birth_photo.addSpacing(15)
        row_birth_photo.addWidget(self.btn_photo)
        row_birth_photo.addStretch()
        layout.addLayout(row_birth_photo)

        # Physical Stats Box (Height & Weight stacked vertically, BMI opposite)
        row_stats_container = QHBoxLayout()
        
        vbox_hw = QVBoxLayout()
        vbox_hw.setSpacing(8)

        row_h = QHBoxLayout()
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(100.0, 230.0)
        self.spin_height.setValue(175.0)
        self.spin_height.setDecimals(0)
        self.spin_height.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_height.setFixedWidth(90)
        self.spin_height.setStyleSheet("padding: 2px 4px;")

        lbl_h = QLabel("قد (cm):")
        lbl_h.setFixedWidth(65)

        row_h.addWidget(lbl_h)
        row_h.addWidget(self.spin_height)
        row_h.addStretch()
        vbox_hw.addLayout(row_h)

        row_w = QHBoxLayout()
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(30.0, 200.0)
        self.spin_weight.setValue(75.0)
        self.spin_weight.setDecimals(1)
        self.spin_weight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_weight.setFixedWidth(90)
        self.spin_weight.setStyleSheet("padding: 2px 4px;")

        lbl_w = QLabel("وزن (kg):")
        lbl_w.setFixedWidth(65)

        row_w.addWidget(lbl_w)
        row_w.addWidget(self.spin_weight)
        row_w.addStretch()
        vbox_hw.addLayout(row_w)

        self.lbl_bmi_badge = QLabel("BMI: 24.5 (طبیعی)")
        self.lbl_bmi_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_bmi_badge.setFixedHeight(65)
        self.lbl_bmi_badge.setMinimumWidth(180)
        self.lbl_bmi_badge.setStyleSheet("font-size: 13px; font-weight: bold; padding: 10px; border-radius: 8px; background-color: #10B981; color: white;")

        self.spin_height.valueChanged.connect(self.update_bmi_display)
        self.spin_weight.valueChanged.connect(self.update_bmi_display)

        row_stats_container.addLayout(vbox_hw)
        row_stats_container.addSpacing(20)
        row_stats_container.addWidget(self.lbl_bmi_badge)
        row_stats_container.addStretch()

        layout.addLayout(row_stats_container)
        self.update_bmi_display()

        # Membership Dates & Type Layout
        grid_mem = QHBoxLayout()

        # Dates column (Start Date on top, Expiry Date on bottom)
        vbox_dates = QVBoxLayout()
        vbox_dates.setSpacing(10)

        row_s = QHBoxLayout()
        lbl_start = QLabel("تاریخ شروع:")
        lbl_start.setFixedWidth(65)
        self.picker_start = JalaliDatePicker(default_today=True)
        self.picker_start.setFixedWidth(155)
        self.picker_start.date_changed.connect(self.recalculate_expiry)
        row_s.addWidget(lbl_start)
        row_s.addWidget(self.picker_start)
        vbox_dates.addLayout(row_s)

        row_e = QHBoxLayout()
        lbl_expire = QLabel("تاریخ انقضا:")
        lbl_expire.setFixedWidth(65)
        self.picker_expire = JalaliDatePicker(default_today=False)
        self.picker_expire.setFixedWidth(155)
        row_e.addWidget(lbl_expire)
        row_e.addWidget(self.picker_expire)
        vbox_dates.addLayout(row_e)

        # Membership Type side-by-side (Label + Dropdown), vertically centered in the middle
        hbox_type = QHBoxLayout()
        hbox_type.setSpacing(10)
        lbl_membership_type = QLabel("نوع عضویت:")
        lbl_membership_type.setFixedWidth(80)

        self.combo_membership = QComboBox()
        self.combo_membership.addItem("۱۲ جلسه در ماه", "12_sessions")
        self.combo_membership.addItem("۸ جلسه در ماه", "8_sessions")
        self.combo_membership.addItem("۱۶ جلسه در ماه", "16_sessions")
        self.combo_membership.addItem("۲۰ جلسه در ماه", "20_sessions")
        self.combo_membership.addItem("دسترسی روزانه", "daily_access")
        self.combo_membership.setFixedWidth(160)
        self.combo_membership.currentIndexChanged.connect(self.on_membership_type_changed)

        hbox_type.addWidget(lbl_membership_type)
        hbox_type.addWidget(self.combo_membership)

        self.recalculate_expiry()

        grid_mem.addLayout(vbox_dates)
        grid_mem.addSpacing(15)
        grid_mem.addLayout(hbox_type)
        grid_mem.addStretch()

        layout.addLayout(grid_mem)

        # Notes Section (Higher label & expanded text edit)
        layout.addSpacing(4)
        lbl_notes = QLabel("یادداشت‌های مربی:")
        layout.addWidget(lbl_notes)

        self.txt_notes = QTextEdit()
        self.txt_notes.setAcceptRichText(False)
        self.txt_notes.setMinimumHeight(95)
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
            self.btn_photo.setText(f"📷 عکس: {os.path.basename(filepath)[:15]}")

    def update_bmi_display(self):
        from yalda.utils.bmi_calculator import calculate_bmi_info
        h = self.spin_height.value()
        w = self.spin_weight.value()
        bmi, cat, color = calculate_bmi_info(h, w)
        if bmi > 0:
            self.lbl_bmi_badge.setText(f"BMI: {bmi}\n({cat})")
            self.lbl_bmi_badge.setStyleSheet(f"font-size: 13px; font-weight: bold; padding: 10px; border-radius: 8px; background-color: {color}; color: white;")
        else:
            self.lbl_bmi_badge.setText("BMI: -")
            self.lbl_bmi_badge.setStyleSheet("font-size: 13px; font-weight: bold; padding: 10px; border-radius: 8px; background-color: #555555; color: white;")

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
            "job": self.txt_job.text().strip(),
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
        if hasattr(m, 'job') and m.job:
            self.txt_job.setText(m.job)
        self.spin_height.setValue(m.height_cm or 175.0)
        self.spin_weight.setValue(m.initial_weight_kg or 75.0)
        self.photo_path = m.photo_path
        if self.photo_path and os.path.exists(self.photo_path):
            self.btn_photo.setText(f"📷 عکس: {os.path.basename(self.photo_path)[:15]}")
        
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
