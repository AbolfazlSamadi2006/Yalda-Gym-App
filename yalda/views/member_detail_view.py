from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QFrame, QMessageBox, QFileDialog, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, Qt
from yalda.services.member_service import MemberService
from yalda.services.workout_service import WorkoutService
from yalda.services.nutrition_service import NutritionService
from yalda.views.health_record_view import HealthRecordView
from yalda.views.assessment_view import AssessmentView
from yalda.views.components.media_viewer_dialog import MediaViewerDialog
from yalda.pdf.pdf_generator import PDFGenerator
import config
import os

class MemberDetailView(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, member_id: int, parent=None):
        super().__init__(parent)
        self.member_id = member_id
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Bar with Back & Edit Buttons
        header = QHBoxLayout()
        btn_back = QPushButton("⬅️ بازگشت به لیست اعضا")
        btn_back.setObjectName("secondary_button")
        btn_back.clicked.connect(self.back_requested.emit)

        btn_edit_profile = QPushButton("✏️ ویرایش مشخصات")
        btn_edit_profile.clicked.connect(self.open_edit_dialog)

        self.lbl_title = QLabel("پرونده جامع ورزشکار")
        self.lbl_title.setObjectName("h1")

        header.addWidget(self.lbl_title)
        header.addStretch()
        header.addWidget(btn_edit_profile)
        header.addWidget(btn_back)
        layout.addLayout(header)

        # Member Quick Info Header Card
        self.card_info = QFrame()
        self.card_info.setObjectName("card")
        layout_card = QHBoxLayout(self.card_info)
        layout_card.setContentsMargins(15, 12, 15, 12)
        layout_card.setSpacing(15)

        self.lbl_avatar = QLabel()
        self.lbl_avatar.setFixedSize(64, 64)
        self.lbl_avatar.setStyleSheet("border-radius: 32px; background-color: #2E2E2E;")
        self.lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_member_details = QLabel()
        self.lbl_member_details.setStyleSheet("font-size: 14px; line-height: 1.6;")
        
        layout_card.addWidget(self.lbl_avatar)
        layout_card.addWidget(self.lbl_member_details)
        layout_card.addStretch()

        layout.addWidget(self.card_info)

        # Main Tabs Widget
        self.tabs = QTabWidget()
        
        # Tab 1: Health Record
        self.tab_health = HealthRecordView(self.member_id, self)
        self.tabs.addTab(self.tab_health, "📋 سوابق پزشکی و آسیب‌دیدگی")

        # Tab 2: Assessments
        self.tab_assessment = AssessmentView(self.member_id, self)
        self.tabs.addTab(self.tab_assessment, "📊 ارزیابی فیزیکی و سایز")

        # Tab 3: Active Workout Plan
        self.tab_workout = QWidget()
        self.init_workout_tab()
        self.tabs.addTab(self.tab_workout, "🏋️ برنامه تمرینی فعال")

        # Tab 4: Active Nutrition Plan
        self.tab_nutrition = QWidget()
        self.init_nutrition_tab()
        self.tabs.addTab(self.tab_nutrition, "🥗 برنامه غذایی فعال")

        layout.addWidget(self.tabs)
        self.load_member_info()

    def open_edit_dialog(self):
        try:
            from yalda.views.member_form_dialog import MemberFormDialog
            member = MemberService.get_member_by_id(self.member_id)
            if member:
                dlg = MemberFormDialog(self, member_data=member)
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    self.load_member_info()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطایی رخ داد: {str(e)}")

    def load_member_info(self):
        member = MemberService.get_member_by_id(self.member_id)
        if member:
            self.lbl_title.setText(f"پرونده جامع: {member.full_name}")
            from yalda.utils.bmi_calculator import calculate_bmi_info
            bmi, cat, color = calculate_bmi_info(member.height_cm, member.initial_weight_kg)
            bmi_str = f"<font color='{color}'><b>{bmi}</b> ({cat})</font>" if bmi > 0 else "-"
            info_str = f"<b>کد عضویت:</b> {member.id}  |  <b>تلفن:</b> {member.phone}  |  <b>قد/وزن:</b> {int(member.height_cm or 0)}cm / {int(member.initial_weight_kg or 0)}kg  |  <b>شاخص BMI:</b> {bmi_str}  |  <b>تاریخ انقضا:</b> <font color='#8B0000'>{member.membership_expire_shamsi}</font>"
            self.lbl_member_details.setText(info_str)

            if member.photo_path and os.path.exists(member.photo_path):
                pixmap = QPixmap(member.photo_path)
                if not pixmap.isNull():
                    scaled_pix = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    self.lbl_avatar.setPixmap(scaled_pix)
                else:
                    self.lbl_avatar.setText("👤")
                    self.lbl_avatar.setStyleSheet("font-size: 32px; background-color: #2E2E2E; border-radius: 32px;")
            else:
                self.lbl_avatar.setText("👤")
                self.lbl_avatar.setStyleSheet("font-size: 32px; background-color: #2E2E2E; border-radius: 32px;")

    def init_workout_tab(self):
        # Clear previous layout
        for i in reversed(range(self.tab_workout.layout().count() if self.tab_workout.layout() else 0)):
            item = self.tab_workout.layout().takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        layout = self.tab_workout.layout() if self.tab_workout.layout() else QVBoxLayout(self.tab_workout)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        assignment = WorkoutService.get_active_assignment(self.member_id)
        if assignment and assignment.plan:
            plan = assignment.plan
            
            top_box = QHBoxLayout()
            lbl = QLabel(f"🏋️ برنامه تمرینی فعال: <b>{plan.title}</b> ({plan.goal})")
            lbl.setStyleSheet("font-size: 15px; color: #FFFFFF;")
            
            btn_pdf = QPushButton("📄 صدور PDF")
            btn_pdf.setFixedSize(130, 36)
            btn_pdf.clicked.connect(lambda: self.export_workout_pdf(plan))

            btn_delete = QPushButton("🗑️ حذف برنامه")
            btn_delete.setObjectName("danger_button")
            btn_delete.setFixedSize(130, 36)
            btn_delete.clicked.connect(lambda: self.delete_workout_plan(assignment.id))

            top_box.addWidget(lbl)
            top_box.addStretch()
            top_box.addWidget(btn_pdf)
            top_box.addWidget(btn_delete)
            layout.addLayout(top_box)

            # Exercises Table
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["عنوان روز", "نام حرکت ورزشی", "ست × تکرار", "زمان استراحت", "آموزش (عکس / فیلم)"])
            table.verticalHeader().setDefaultSectionSize(48)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(4, 150)

            # Gather all exercises in plan
            rows_data = []
            for day in plan.days:
                for we in day.workout_exercises:
                    rows_data.append((day.day_title, we))

            table.setRowCount(len(rows_data))
            for row, (day_title, we) in enumerate(rows_data):
                table.setItem(row, 0, QTableWidgetItem(day_title))
                table.setItem(row, 1, QTableWidgetItem(we.exercise.name_fa if we.exercise else "-"))
                table.setItem(row, 2, QTableWidgetItem(f"{we.sets} × {we.reps}"))
                table.setItem(row, 3, QTableWidgetItem(f"{we.rest_seconds} ثانیه"))

                btn_media = QPushButton("🎬 عکس/فیلم")
                btn_media.setObjectName("secondary_button")
                btn_media.setStyleSheet("padding: 4px 8px; font-size: 11px; height: 32px;")
                if we.exercise:
                    btn_media.clicked.connect(lambda _, ex=we.exercise: self.show_exercise_media(ex))
                else:
                    btn_media.setEnabled(False)

                table.setCellWidget(row, 4, btn_media)

            layout.addWidget(table)
        else:
            lbl = QLabel("هیچ برنامه تمرینی فعالی برای این ورزشکار ثبت نشده است.")
            lbl.setStyleSheet("color: #888888; font-size: 14px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)

    def init_nutrition_tab(self):
        # Clear previous layout
        for i in reversed(range(self.tab_nutrition.layout().count() if self.tab_nutrition.layout() else 0)):
            item = self.tab_nutrition.layout().takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        layout = self.tab_nutrition.layout() if self.tab_nutrition.layout() else QVBoxLayout(self.tab_nutrition)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        assignment = NutritionService.get_active_assignment(self.member_id)
        if assignment and assignment.plan:
            plan = assignment.plan

            top_box = QHBoxLayout()
            lbl = QLabel(f"🥗 برنامه غذایی فعال: <b>{plan.title}</b> ({plan.goal}) | کالری هدف: {int(plan.target_calories)} kcal")
            lbl.setStyleSheet("font-size: 15px; color: #FFFFFF;")

            btn_pdf = QPushButton("📄 صدور PDF")
            btn_pdf.setFixedSize(130, 36)
            btn_pdf.clicked.connect(lambda: self.export_nutrition_pdf(plan))

            btn_delete = QPushButton("🗑️ حذف برنامه")
            btn_delete.setObjectName("danger_button")
            btn_delete.setFixedSize(130, 36)
            btn_delete.clicked.connect(lambda: self.delete_nutrition_plan(assignment.id))

            top_box.addWidget(lbl)
            top_box.addStretch()
            top_box.addWidget(btn_pdf)
            top_box.addWidget(btn_delete)
            layout.addLayout(top_box)

            # Meals Table
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["نام وعده", "نام ماده غذایی", "مقدار / واحد", "توضیحات مربی"])
            table.verticalHeader().setDefaultSectionSize(44)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            meal_name_fa = {
                "breakfast": "صبحانه", "morning_snack": "میان‌وعده صبح", "lunch": "ناهار",
                "afternoon_snack": "عصرانه", "dinner": "شام", "evening_snack": "قبل از خواب"
            }

            rows_data = []
            for meal in plan.meals:
                for item in meal.items:
                    rows_data.append((meal.meal_name, item))

            table.setRowCount(len(rows_data))
            for row, (m_name, item) in enumerate(rows_data):
                table.setItem(row, 0, QTableWidgetItem(meal_name_fa.get(m_name, m_name)))
                table.setItem(row, 1, QTableWidgetItem(item.food.name_fa if item.food else "-"))
                table.setItem(row, 2, QTableWidgetItem(f"{item.amount} {item.unit or ''}"))
                table.setItem(row, 3, QTableWidgetItem(item.notes or "-"))

            layout.addWidget(table)
        else:
            lbl = QLabel("هیچ برنامه غذایی فعالی برای این ورزشکار ثبت نشده است.")
            lbl.setStyleSheet("color: #888888; font-size: 14px; padding: 20px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)

    def show_exercise_media(self, exercise):
        dlg = MediaViewerDialog(title=exercise.name_fa, media_path=exercise.media_path, media_type=exercise.media_type, parent=self)
        dlg.exec()

    def delete_workout_plan(self, assignment_id):
        reply = QMessageBox.question(
            self, "تایید حذف برنامه تمرینی",
            "آیا از حذف این برنامه تمرینی از پرونده ورزشکار اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            WorkoutService.delete_workout_assignment(assignment_id)
            self.init_workout_tab()
            QMessageBox.information(self, "موفقیت", "برنامه تمرینی با موفقیت حذف گردید.")

    def delete_nutrition_plan(self, assignment_id):
        reply = QMessageBox.question(
            self, "تایید حذف برنامه غذایی",
            "آیا از حذف این برنامه غذایی از پرونده ورزشکار اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            NutritionService.delete_nutrition_assignment(assignment_id)
            self.init_nutrition_tab()
            QMessageBox.information(self, "موفقیت", "برنامه غذایی با موفقیت حذف گردید.")

    def export_workout_pdf(self, plan):
        member = MemberService.get_member_by_id(self.member_id)
        default_name = f"workout_{member.last_name}_{plan.id}.pdf"
        filepath, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF برنامه تمرینی", default_name, "PDF Files (*.pdf)")
        if filepath:
            PDFGenerator.generate_workout_pdf(member, plan, filepath)
            QMessageBox.information(self, "موفقیت", "فایل PDF برنامه تمرینی با موفقیت ایجاد شد.")

    def export_nutrition_pdf(self, plan):
        member = MemberService.get_member_by_id(self.member_id)
        default_name = f"nutrition_{member.last_name}_{plan.id}.pdf"
        filepath, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF برنامه غذایی", default_name, "PDF Files (*.pdf)")
        if filepath:
            PDFGenerator.generate_nutrition_pdf(member, plan, filepath)
            QMessageBox.information(self, "موفقیت", "فایل PDF برنامه غذایی با موفقیت ایجاد شد.")
