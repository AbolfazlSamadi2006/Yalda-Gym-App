from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import shutil
import config
from yalda.views.components.jalali_calendar_widget import JalaliDatePicker
from yalda.services.assessment_service import AssessmentService

class CompareDialog(QDialog):
    """Side-by-Side Comparison Dialog for 2 Assessment Dates"""
    def __init__(self, comparison_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("مقایسه پیشرفت بدنی ورزشکار")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(650, 500)

        layout = QVBoxLayout(self)
        a1 = comparison_data["first"]
        a2 = comparison_data["second"]
        diff = comparison_data["diff"]

        title = QLabel(f"مقایسه ارزیابی {a1.assessment_date_shamsi} با {a2.assessment_date_shamsi}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #8B0000;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Stats Diff Table
        table = QTableWidget(7, 4)
        table.setHorizontalHeaderLabels(["شاخص", f"تاریخ {a1.assessment_date_shamsi}", f"تاریخ {a2.assessment_date_shamsi}", "تغییرات"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        metrics = [
            ("وزن (kg)", a1.weight_kg, a2.weight_kg, diff['weight_diff']),
            ("درصد چربی (%)", a1.body_fat_percentage, a2.body_fat_percentage, diff['fat_diff']),
            ("شاخص BMI", a1.bmi, a2.bmi, diff['bmi_diff']),
            ("دور بازو (cm)", a1.arm_circ, a2.arm_circ, diff['arm_diff']),
            ("دور سینه (cm)", a1.chest_circ, a2.chest_circ, diff['chest_diff']),
            ("دور کمر (cm)", a1.waist_circ, a2.waist_circ, diff['waist_diff']),
            ("دور ران (cm)", a1.thigh_circ, a2.thigh_circ, diff['thigh_diff'])
        ]

        for row, (name, v1, v2, d) in enumerate(metrics):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(str(v1 or "-")))
            table.setItem(row, 2, QTableWidgetItem(str(v2 or "-")))
            
            diff_item = QTableWidgetItem(f"{d:+}" if d else "0")
            if d < 0:
                diff_item.setForeground(Qt.GlobalColor.green if "کمر" in name or "چربی" in name or "وزن" in name else Qt.GlobalColor.red)
            elif d > 0:
                diff_item.setForeground(Qt.GlobalColor.green if "بازو" in name or "سینه" in name or "ران" in name else Qt.GlobalColor.yellow)
            table.setItem(row, 3, diff_item)

        layout.addWidget(table)

        btn_close = QPushButton("بستن")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

class AssessmentView(QWidget):
    def __init__(self, member_id: int, parent=None):
        super().__init__(parent)
        self.member_id = member_id
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.before_photo_path = None
        self.after_photo_path = None

        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # New Assessment Group Box
        group_new = QGroupBox("➕ ثبت ارزیابی فیزیکی و سایز جدید")
        layout_form = QVBoxLayout(group_new)

        row1 = QHBoxLayout()
        self.picker_date = JalaliDatePicker(default_today=True)
        self.spin_weight = QDoubleSpinBox()
        self.spin_weight.setRange(30.0, 200.0)
        self.spin_weight.setValue(75.0)

        self.spin_fat = QDoubleSpinBox()
        self.spin_fat.setRange(0.0, 60.0)
        self.spin_fat.setValue(15.0)

        row1.addWidget(QLabel("تاریخ ارزیابی:"))
        row1.addWidget(self.picker_date)
        row1.addWidget(QLabel("وزن (kg):"))
        row1.addWidget(self.spin_weight)
        row1.addWidget(QLabel("درصد چربی (%):"))
        row1.addWidget(self.spin_fat)
        layout_form.addLayout(row1)

        row2 = QHBoxLayout()
        self.spin_arm = QDoubleSpinBox()
        self.spin_arm.setRange(15.0, 70.0)
        self.spin_chest = QDoubleSpinBox()
        self.spin_chest.setRange(50.0, 180.0)
        self.spin_waist = QDoubleSpinBox()
        self.spin_waist.setRange(40.0, 160.0)
        self.spin_thigh = QDoubleSpinBox()
        self.spin_thigh.setRange(30.0, 100.0)

        row2.addWidget(QLabel("دور بازو:"))
        row2.addWidget(self.spin_arm)
        row2.addWidget(QLabel("دور سینه:"))
        row2.addWidget(self.spin_chest)
        row2.addWidget(QLabel("دور کمر:"))
        row2.addWidget(self.spin_waist)
        row2.addWidget(QLabel("دور ران:"))
        row2.addWidget(self.spin_thigh)
        layout_form.addLayout(row2)

        # Photos Upload
        row_photos = QHBoxLayout()
        btn_before = QPushButton("📷 عکس قبل (Before)")
        btn_before.setObjectName("secondary_button")
        btn_before.clicked.connect(self.select_before_photo)

        btn_after = QPushButton("📷 عکس بعد (After)")
        btn_after.setObjectName("secondary_button")
        btn_after.clicked.connect(self.select_after_photo)

        btn_save = QPushButton("ذخیره ارزیابی")
        btn_save.clicked.connect(self.save_assessment)

        row_photos.addWidget(btn_before)
        row_photos.addWidget(btn_after)
        row_photos.addStretch()
        row_photos.addWidget(btn_save)
        layout_form.addLayout(row_photos)

        layout.addWidget(group_new)

        # History Table & Compare Button
        row_hist = QHBoxLayout()
        lbl_hist = QLabel("📊 تاریخچه ارزیابی‌های آنتروپومتریک")
        lbl_hist.setObjectName("h2")
        
        btn_compare = QPushButton("🔍 مقایسه دو تاریخ")
        btn_compare.setObjectName("secondary_button")
        btn_compare.clicked.connect(self.compare_selected)

        row_hist.addWidget(lbl_hist)
        row_hist.addStretch()
        row_hist.addWidget(btn_compare)
        layout.addLayout(row_hist)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "تاریخ (شمسی)", "وزن (kg)", "درصد چربی", "BMI", "دور بازو", "دور سینه", "دور کمر", "دور ران"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

    def select_before_photo(self):
        fp, _ = QFileDialog.getOpenFileName(self, "عکس قبل", "", "Images (*.png *.jpg *.jpeg)")
        if fp:
            dest = config.PROGRESS_PHOTOS_DIR / f"before_{os.path.basename(fp)}"
            shutil.copy2(fp, dest)
            self.before_photo_path = str(dest)

    def select_after_photo(self):
        fp, _ = QFileDialog.getOpenFileName(self, "عکس بعد", "", "Images (*.png *.jpg *.jpeg)")
        if fp:
            dest = config.PROGRESS_PHOTOS_DIR / f"after_{os.path.basename(fp)}"
            shutil.copy2(fp, dest)
            self.after_photo_path = str(dest)

    def save_assessment(self):
        data = {
            "assessment_date_shamsi": self.picker_date.text(),
            "weight_kg": self.spin_weight.value(),
            "body_fat_percentage": self.spin_fat.value(),
            "arm_circ": self.spin_arm.value(),
            "chest_circ": self.spin_chest.value(),
            "waist_circ": self.spin_waist.value(),
            "thigh_circ": self.spin_thigh.value(),
            "before_photo_path": self.before_photo_path,
            "after_photo_path": self.after_photo_path
        }
        AssessmentService.add_assessment(self.member_id, data)
        self.load_history()
        QMessageBox.information(self, "موفقیت", "ارزیابی فیزیکی جدید ذخیره شد.")

    def load_history(self):
        records = AssessmentService.get_member_assessments(self.member_id)
        self.table.setRowCount(len(records))
        self.records_list = records

        for row, rec in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(rec.assessment_date_shamsi))
            self.table.setItem(row, 1, QTableWidgetItem(str(rec.weight_kg)))
            self.table.setItem(row, 2, QTableWidgetItem(str(rec.body_fat_percentage or "-")))
            self.table.setItem(row, 3, QTableWidgetItem(str(rec.bmi or "-")))
            self.table.setItem(row, 4, QTableWidgetItem(str(rec.arm_circ or "-")))
            self.table.setItem(row, 5, QTableWidgetItem(str(rec.chest_circ or "-")))
            self.table.setItem(row, 6, QTableWidgetItem(str(rec.waist_circ or "-")))
            self.table.setItem(row, 7, QTableWidgetItem(str(rec.thigh_circ or "-")))

    def compare_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) != 2:
            QMessageBox.warning(self, "راهنما", "لطفاً دقیقاً دو سطر از جدول تاریخچه را جهت مقایسه انتخاب کنید (با کلید Ctrl).")
            return

        idx1 = selected_rows[0].row()
        idx2 = selected_rows[1].row()
        rec1 = self.records_list[idx1]
        rec2 = self.records_list[idx2]

        comp_data = AssessmentService.compare_assessments(rec1.id, rec2.id)
        if comp_data:
            dlg = CompareDialog(comp_data, self)
            dlg.exec()
