from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QTextEdit, QPushButton, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from yalda.services.member_service import MemberService

class HealthRecordView(QWidget):
    def __init__(self, member_id: int, parent=None):
        super().__init__(parent)
        self.member_id = member_id
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Medical History Group
        group_med = QGroupBox("📋 سابقه پزشکی و بیماری‌های خاص")
        layout_med = QVBoxLayout(group_med)
        
        row_cb = QHBoxLayout()
        self.cb_hypertension = QCheckBox("فشار خون بالا")
        self.cb_diabetes = QCheckBox("دیابت")
        self.cb_heart = QCheckBox("مشکلات قلبی-عروقی")
        row_cb.addWidget(self.cb_hypertension)
        row_cb.addWidget(self.cb_diabetes)
        row_cb.addWidget(self.cb_heart)
        layout_med.addLayout(row_cb)

        layout_med.addWidget(QLabel("توضیحات سایر بیماری‌ها:"))
        self.txt_other_med = QTextEdit()
        self.txt_other_med.setMaximumHeight(60)
        layout_med.addWidget(self.txt_other_med)
        layout.addWidget(group_med)

        # Injury History Group
        group_inj = QGroupBox("⚠️ سابقه آسیب‌دیدگی مفاصل و عضلات")
        layout_inj = QVBoxLayout(group_inj)

        row_inj1 = QHBoxLayout()
        self.txt_knee = QTextEdit()
        self.txt_knee.setPlaceholderText("مثلاً: آسیب رباط صلیبی زانوی راست...")
        self.txt_knee.setMaximumHeight(50)
        
        self.txt_back = QTextEdit()
        self.txt_back.setPlaceholderText("مثلاً: فتق دیسک مهره L4-L5...")
        self.txt_back.setMaximumHeight(50)

        row_inj1.addWidget(QLabel("آسیب زانو:"))
        row_inj1.addWidget(self.txt_knee)
        row_inj1.addWidget(QLabel("دیسک و کمر:"))
        row_inj1.addWidget(self.txt_back)
        layout_inj.addLayout(row_inj1)

        row_inj2 = QHBoxLayout()
        self.txt_shoulder = QTextEdit()
        self.txt_shoulder.setPlaceholderText("مثلاً: التهاب تاندون شانه چپ...")
        self.txt_shoulder.setMaximumHeight(50)

        self.txt_wrist = QTextEdit()
        self.txt_wrist.setPlaceholderText("مثلاً: سندروم تونل کارپال مچ...")
        self.txt_wrist.setMaximumHeight(50)

        row_inj2.addWidget(QLabel("آسیب شانه:"))
        row_inj2.addWidget(self.txt_shoulder)
        row_inj2.addWidget(QLabel("آسیب مچ:"))
        row_inj2.addWidget(self.txt_wrist)
        layout_inj.addLayout(row_inj2)

        layout.addWidget(group_inj)

        # Limitations & Warnings
        group_lim = QGroupBox("🛑 محدودیت‌های ورزشی و هشدارهای مربی")
        layout_lim = QVBoxLayout(group_lim)
        
        self.txt_limitations = QTextEdit()
        self.txt_limitations.setPlaceholderText("حرکاتی که به هیچ عنوان نباید تجویز شوند...")
        self.txt_limitations.setMaximumHeight(60)
        
        layout_lim.addWidget(QLabel("محدودیت‌های صریح حرکتی:"))
        layout_lim.addWidget(self.txt_limitations)
        layout.addWidget(group_lim)

        # Save Button
        btn_save = QPushButton("💾 ثبت و بروزرسانی پرونده سلامت")
        btn_save.setFixedHeight(40)
        btn_save.clicked.connect(self.save_data)
        layout.addWidget(btn_save)

    def load_data(self):
        rec = MemberService.get_health_record(self.member_id)
        if rec:
            self.cb_hypertension.setChecked(rec.has_hypertension or False)
            self.cb_diabetes.setChecked(rec.has_diabetes or False)
            self.cb_heart.setChecked(rec.has_heart_issue or False)
            self.txt_other_med.setText(rec.other_medical or "")
            self.txt_knee.setText(rec.knee_injury or "")
            self.txt_back.setText(rec.back_injury or "")
            self.txt_shoulder.setText(rec.shoulder_injury or "")
            self.txt_wrist.setText(rec.wrist_injury or "")
            self.txt_limitations.setText(rec.exercise_limitations or "")

    def save_data(self):
        data = {
            "has_hypertension": self.cb_hypertension.isChecked(),
            "has_diabetes": self.cb_diabetes.isChecked(),
            "has_heart_issue": self.cb_heart.isChecked(),
            "other_medical": self.txt_other_med.toPlainText().strip(),
            "knee_injury": self.txt_knee.toPlainText().strip(),
            "back_injury": self.txt_back.toPlainText().strip(),
            "shoulder_injury": self.txt_shoulder.toPlainText().strip(),
            "wrist_injury": self.txt_wrist.toPlainText().strip(),
            "exercise_limitations": self.txt_limitations.toPlainText().strip()
        }
        MemberService.update_health_record(self.member_id, data)
        QMessageBox.information(self, "موفقیت", "پرونده سلامت با موفقیت ذخیره شد.")
