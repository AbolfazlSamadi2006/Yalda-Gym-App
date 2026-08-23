from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from yalda.services.workout_service import WorkoutService
from yalda.services.member_service import MemberService
from yalda.views.components.searchable_combo_box import SearchableComboBox

class WorkoutEditorView(QWidget):
    manage_templates_requested = pyqtSignal()
    open_exercise_bank_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.day_tables = []
        self.editing_plan_id = None
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_members_dropdown()
        self.load_template_dropdown()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title and Action Bar
        header = QHBoxLayout()
        self.lbl_header_title = QLabel("🏋️ برنامه‌ریزی تمرینی")
        self.lbl_header_title.setObjectName("h1")

        btn_new_plan = QPushButton("➕ برنامه جدید")
        btn_new_plan.setObjectName("secondary_button")
        btn_new_plan.clicked.connect(self.reset_to_new_plan)

        btn_manage_tpl = QPushButton("📋 مدیریت و مشاهده الگوها")
        btn_manage_tpl.setObjectName("secondary_button")
        btn_manage_tpl.clicked.connect(self.manage_templates_requested.emit)

        btn_exercise_bank = QPushButton("🏃 بانک حرکات ورزشی")
        btn_exercise_bank.setObjectName("secondary_button")
        btn_exercise_bank.clicked.connect(self.open_exercise_bank_requested.emit)

        header.addWidget(self.lbl_header_title)
        header.addStretch()
        header.addWidget(btn_new_plan)
        header.addWidget(btn_manage_tpl)
        header.addWidget(btn_exercise_bank)
        layout.addLayout(header)

        # Program Details Form Box
        form_box = QGroupBox("مشخصات کلی برنامه تمرینی")
        layout_form = QVBoxLayout(form_box)

        # Template Picker Row
        row_tpl = QHBoxLayout()
        self.combo_templates = QComboBox()
        self.combo_templates.addItem("--- انتخاب و بارگذاری الگوی آماده از بانک ---", None)
        self.load_template_dropdown()
        self.combo_templates.currentIndexChanged.connect(self.on_template_selected)

        row_tpl.addWidget(QLabel("📂 الگوهای آماده بانک:"))
        row_tpl.addWidget(self.combo_templates)
        layout_form.addLayout(row_tpl)

        row1 = QHBoxLayout()
        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("عنوان برنامه (مثلاً: برنامه حجمی ۴ روزه)...")

        self.combo_goal = QComboBox()
        self.combo_goal.addItem("هایپرتروفی (عضله‌سازی)", "hypertrophy")
        self.combo_goal.addItem("چربی‌سوزی و کاهش وزن", "fat_loss")
        self.combo_goal.addItem("افزایش قدرت بی‌هوازی", "strength")
        self.combo_goal.addItem("حرکات اصلاحی و بهبود قامت", "corrective")
        self.combo_goal.addItem("آمادگی جسمانی عمومی", "general_fitness")
        self.combo_goal.addItem("استقامت عضلانی", "endurance")

        self.combo_days = QComboBox()
        for d in range(2, 7):
            self.combo_days.addItem(f"{d} روز در هفته", d)
        self.combo_days.setCurrentIndex(1) # Default 3 days
        self.combo_days.currentIndexChanged.connect(self.setup_day_tabs)

        self.combo_level = QComboBox()
        self.combo_level.addItem("مبتدی", "beginner")
        self.combo_level.addItem("متوسط", "intermediate")
        self.combo_level.addItem("پیشرفته", "advanced")

        row1.addWidget(QLabel("عنوان:"))
        row1.addWidget(self.txt_title)
        row1.addWidget(QLabel("هدف:"))
        row1.addWidget(self.combo_goal)
        row1.addWidget(QLabel("روزهای هفته:"))
        row1.addWidget(self.combo_days)
        row1.addWidget(QLabel("سطح تمرین:"))
        row1.addWidget(self.combo_level)
        layout_form.addLayout(row1)

        layout.addWidget(form_box)

        # Tabs for Training Days
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.setup_day_tabs()

        # Assignment Box & Actions
        assign_box = QGroupBox("تخصیص برنامه به ورزشکار")
        layout_assign = QHBoxLayout(assign_box)

        self.combo_member = SearchableComboBox(placeholder="جستجو یا تایپ نام ورزشکار...")
        self.load_members_dropdown()

        btn_save = QPushButton("💾 ذخیره الگو در بانک")
        btn_save.setObjectName("secondary_button")
        btn_save.clicked.connect(self.save_plan)

        btn_assign = QPushButton("✅ تخصیص و صدور برنامه")
        btn_assign.clicked.connect(self.assign_plan)

        layout_assign.addWidget(QLabel("انتخاب ورزشکار:"))
        layout_assign.addWidget(self.combo_member)
        layout_assign.addStretch()
        layout_assign.addWidget(btn_save)
        layout_assign.addWidget(btn_assign)

        layout.addWidget(assign_box)

    def load_members_dropdown(self):
        cur = self.combo_member.currentData()
        self.combo_member.blockSignals(True)
        self.combo_member.clear()
        members = MemberService.get_all_members(status_filter="active")
        for m in members:
            self.combo_member.addItem(f"{m.full_name} ({m.phone})", m.id)
        if cur is not None:
            idx = self.combo_member.findData(cur)
            if idx >= 0:
                self.combo_member.setCurrentIndex(idx)
            else:
                self.combo_member.set_empty()
        else:
            self.combo_member.set_empty()
        self.combo_member.blockSignals(False)

    def set_selected_member(self, member_id: int):
        self.load_members_dropdown()
        idx = self.combo_member.findData(member_id)
        if idx >= 0:
            self.combo_member.setCurrentIndex(idx)

    def setup_day_tabs(self):
        self.tabs.clear()
        self.day_tables.clear()
        num_days = self.combo_days.currentData() or 3
        exercises_list = WorkoutService.get_all_exercises()

        for d in range(1, num_days + 1):
            day_widget = QWidget()
            layout_day = QVBoxLayout(day_widget)

            # Header row for day
            row_top = QHBoxLayout()
            lbl_title = QLabel(f"عنوان روز {d}:")
            txt_day_title = QLineEdit(f"روز {d}: تمرین عضلات")
            
            btn_add_row = QPushButton("➕ افزودن حرکت")
            btn_add_row.setObjectName("secondary_button")

            row_top.addWidget(lbl_title)
            row_top.addWidget(txt_day_title)
            row_top.addStretch()
            row_top.addWidget(btn_add_row)
            layout_day.addLayout(row_top)

            # Table for exercises in this day
            table = QTableWidget(0, 7)
            table.setHorizontalHeaderLabels(["نام حرکت ورزشی", "ست", "تکرار", "وزنه (kg)", "استراحت (ثانیه)", "ریتم (Tempo)", "حذف"])
            
            # Row height & Column width setup
            table.verticalHeader().setDefaultSectionSize(50)
            table.verticalHeader().setMinimumSectionSize(45)
            
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)     # Exercise name
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Sets
            table.setColumnWidth(1, 70)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # Reps
            table.setColumnWidth(2, 95)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # Weight
            table.setColumnWidth(3, 95)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive) # Rest
            table.setColumnWidth(4, 115)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive) # Tempo
            table.setColumnWidth(5, 115)
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)       # Delete
            table.setColumnWidth(6, 60)

            btn_add_row.clicked.connect(lambda _, t=table: self.add_exercise_row(t, exercises_list))

            layout_day.addWidget(table)
            self.tabs.addTab(day_widget, f"روز {d}")
            self.day_tables.append((txt_day_title, table))
            # بدون حرکت پیش‌فرض اولیه - مربی خودش حرکات را اضافه می‌کند

    def refresh_editor(self):
        self.load_members_dropdown()
        cur_tpl = self.combo_templates.currentData()
        self.load_template_dropdown()
        if cur_tpl is not None:
            idx = self.combo_templates.findData(cur_tpl)
            if idx >= 0:
                self.combo_templates.blockSignals(True)
                self.combo_templates.setCurrentIndex(idx)
                self.combo_templates.blockSignals(False)

    def add_exercise_row(self, table: QTableWidget, exercises_list: list = None):
        row = table.rowCount()
        table.insertRow(row)

        if not exercises_list:
            exercises_list = WorkoutService.get_all_exercises()

        combo_ex = SearchableComboBox(placeholder="جستجو یا تایپ نام حرکت...")
        for ex in exercises_list:
            combo_ex.addItem(f"{ex.name_fa} ({ex.primary_muscle})", ex.id)
        combo_ex.set_empty()

        txt_sets = QLineEdit("3")
        txt_sets.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_reps = QLineEdit("10-12")
        txt_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_weight = QLineEdit("-")
        txt_weight.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_rest = QLineEdit("60")
        txt_rest.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_tempo = QLineEdit("2-0-2-0")
        txt_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_del = QPushButton("🗑️")
        btn_del.setObjectName("danger_button")
        btn_del.setToolTip("حذف حرکت ورزشی")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda _, t=table, r=row: t.removeRow(r))

        table.setCellWidget(row, 0, combo_ex)
        table.setCellWidget(row, 1, txt_sets)
        table.setCellWidget(row, 2, txt_reps)
        table.setCellWidget(row, 3, txt_weight)
        table.setCellWidget(row, 4, txt_rest)
        table.setCellWidget(row, 5, txt_tempo)
        table.setCellWidget(row, 6, btn_del)

    def get_plan_data(self):
        title = self.txt_title.text().strip() or "برنامه تمرینی سفارشی"
        days_data = []

        for idx, (txt_day_title, table) in enumerate(self.day_tables, start=1):
            ex_list = []
            for row in range(table.rowCount()):
                combo_ex = table.cellWidget(row, 0)
                if not combo_ex:
                    continue
                ex_id = combo_ex.currentData()
                sets = table.cellWidget(row, 1).text().strip()
                reps = table.cellWidget(row, 2).text().strip()
                weight = table.cellWidget(row, 3).text().strip()
                rest = table.cellWidget(row, 4).text().strip()
                tempo = table.cellWidget(row, 5).text().strip()

                ex_list.append({
                    "exercise_id": ex_id,
                    "sets": int(sets) if sets.isdigit() else 3,
                    "reps": reps,
                    "weight_suggestion": weight,
                    "rest_seconds": int(rest) if rest.isdigit() else 60,
                    "tempo": tempo
                })

            days_data.append({
                "day_number": idx,
                "day_title": txt_day_title.text().strip(),
                "exercises": ex_list
            })

        plan_info = {
            "title": title,
            "goal": self.combo_goal.currentData(),
            "days_per_week": self.combo_days.currentData(),
            "training_level": self.combo_level.currentData()
        }
        return plan_info, days_data

    def load_template_dropdown(self):
        cur = self.combo_templates.currentData()
        self.combo_templates.blockSignals(True)
        self.combo_templates.clear()
        self.combo_templates.addItem("--- انتخاب و بارگذاری الگوی آماده از بانک ---", None)
        goal_names = {
            "hypertrophy": "عضله‌سازی",
            "fat_loss": "چربی‌سوزی",
            "strength": "قدرت",
            "corrective": "حرکات اصلاحی",
            "general_fitness": "آمادگی جسمانی",
            "endurance": "استقامت"
        }
        plans = WorkoutService.get_all_plans()
        for p in plans:
            g_fa = goal_names.get(p.goal, p.goal)
            self.combo_templates.addItem(f"📋 {p.title} ({p.days_per_week} روزه - {g_fa})", p.id)
        if cur is not None:
            idx = self.combo_templates.findData(cur)
            if idx >= 0:
                self.combo_templates.setCurrentIndex(idx)
        self.combo_templates.blockSignals(False)

    def on_template_selected(self, index: int):
        try:
            plan_id = self.combo_templates.currentData()
            if not plan_id:
                return

            plan = WorkoutService.get_plan_by_id(plan_id)
            if not plan:
                return

            self.txt_title.setText(plan.title or "")
            
            idx_g = self.combo_goal.findData(plan.goal)
            if idx_g >= 0: self.combo_goal.setCurrentIndex(idx_g)

            # Update days per week without triggering signals recursively
            self.combo_days.blockSignals(True)
            idx_d = self.combo_days.findData(plan.days_per_week)
            if idx_d >= 0:
                self.combo_days.setCurrentIndex(idx_d)
            self.combo_days.blockSignals(False)

            idx_l = self.combo_level.findData(plan.training_level)
            if idx_l >= 0: self.combo_level.setCurrentIndex(idx_l)

            # Rebuild day tabs for loaded template's days_per_week
            self.setup_day_tabs()

            # Ensure all_exercises is populated
            if not hasattr(self, 'all_exercises') or not self.all_exercises:
                self.all_exercises = WorkoutService.get_all_exercises()

            # Populate day tables with exercises from loaded template
            for day_idx, w_day in enumerate(plan.days):
                if day_idx < len(self.day_tables):
                    txt_day_title, table = self.day_tables[day_idx]
                    txt_day_title.setText(w_day.day_title or f"روز {day_idx + 1}")
                    table.setRowCount(0)
                    
                    for we in w_day.workout_exercises:
                        row = table.rowCount()
                        table.insertRow(row)

                        combo_ex = SearchableComboBox(placeholder="جستجو یا تایپ نام حرکت...")
                        for ex in self.all_exercises:
                            combo_ex.addItem(f"{ex.name_fa} ({ex.primary_muscle})", ex.id)
                        
                        if we.exercise_id:
                            idx_ex = combo_ex.findData(we.exercise_id)
                            if idx_ex >= 0: combo_ex.setCurrentIndex(idx_ex)

                        txt_sets = QLineEdit(str(we.sets or 3))
                        txt_sets.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        txt_reps = QLineEdit(str(we.reps or "10-12"))
                        txt_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        txt_weight = QLineEdit(str(we.weight_suggestion or "-"))
                        txt_weight.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        txt_rest = QLineEdit(str(we.rest_seconds or 60))
                        txt_rest.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        txt_tempo = QLineEdit(str(we.tempo or "2-0-2-0"))
                        txt_tempo.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        btn_del = QPushButton("🗑️")
                        btn_del.setObjectName("danger_button")
                        btn_del.setFixedWidth(35)
                        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
                        btn_del.clicked.connect(lambda _, t=table, r=row: t.removeRow(r))

                        table.setCellWidget(row, 0, combo_ex)
                        table.setCellWidget(row, 1, txt_sets)
                        table.setCellWidget(row, 2, txt_reps)
                        table.setCellWidget(row, 3, txt_weight)
                        table.setCellWidget(row, 4, txt_rest)
                        table.setCellWidget(row, 5, txt_tempo)
                        table.setCellWidget(row, 6, btn_del)

            if not hasattr(self, '_suppress_loaded_alert') or not self._suppress_loaded_alert:
                QMessageBox.information(self, "موفقیت", f"الگوی '{plan.title}' با موفقیت در فرم بارگذاری شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در لود الگوی تمرینی: {str(e)}")

    def reset_to_new_plan(self):
        self.editing_plan_id = None
        self.lbl_header_title.setText("🏋️ برنامه‌ریزی تمرینی")
        self.txt_title.clear()
        self.combo_goal.setCurrentIndex(0)
        self.combo_days.setCurrentIndex(1)
        self.combo_level.setCurrentIndex(0)
        self.setup_day_tabs()
        self.combo_templates.blockSignals(True)
        self.combo_templates.setCurrentIndex(0)
        self.combo_templates.blockSignals(False)

    def load_plan_for_edit(self, plan_id: int):
        self._suppress_loaded_alert = True
        try:
            self.editing_plan_id = plan_id
            idx_tpl = self.combo_templates.findData(plan_id)
            if idx_tpl >= 0:
                self.combo_templates.setCurrentIndex(idx_tpl)
            else:
                # Direct load
                plan = WorkoutService.get_plan_by_id(plan_id)
                if plan:
                    self.txt_title.setText(plan.title or "")
                    idx_g = self.combo_goal.findData(plan.goal)
                    if idx_g >= 0: self.combo_goal.setCurrentIndex(idx_g)
                    idx_d = self.combo_days.findData(plan.days_per_week)
                    if idx_d >= 0: self.combo_days.setCurrentIndex(idx_d)
                    idx_l = self.combo_level.findData(plan.training_level)
                    if idx_l >= 0: self.combo_level.setCurrentIndex(idx_l)
                    self.setup_day_tabs()
            
            plan = WorkoutService.get_plan_by_id(plan_id)
            if plan:
                self.lbl_header_title.setText(f"✏️ ویرایش الگوی تمرینی: {plan.title}")
        finally:
            self._suppress_loaded_alert = False

    def save_plan(self):
        plan_info, days_data = self.get_plan_data()
        if self.editing_plan_id:
            plan = WorkoutService.update_workout_plan(self.editing_plan_id, plan_info, days_data)
            self.load_template_dropdown()
            QMessageBox.information(self, "موفقیت", f"الگوی تمرینی «{plan.title}» با موفقیت به‌روزرسانی شد.")
        else:
            plan = WorkoutService.create_workout_plan(plan_info, days_data)
            self.load_template_dropdown()
            QMessageBox.information(self, "موفقیت", "الگوی برنامه تمرینی در بانک ذخیره گردید.")
        return plan

    def assign_plan(self):
        member_id = self.combo_member.currentData()
        if not member_id:
            QMessageBox.warning(self, "خطا", "لطفاً یک ورزشکار را جهت تخصیص انتخاب کنید.")
            return

        # Check Smart Limitations
        health_rec = MemberService.get_health_record(member_id)
        plan_info, days_data = self.get_plan_data()
        
        warnings = []
        if health_rec:
            if health_rec.knee_injury:
                warnings.append("ورزشکار سابقه آسیب زانو دارد.")
            if health_rec.back_injury:
                warnings.append("ورزشکار سابقه فتق دیسک کمر دارد.")
            if health_rec.shoulder_injury:
                warnings.append("ورزشکار سابقه آسیب شانه دارد.")

        if warnings:
            msg = "⚠️ هشدارهای پزشکی ورزشکار:\n" + "\n".join(warnings) + "\n\nآیا مایل به تخصیص برنامه هستید؟"
            reply = QMessageBox.question(self, "هشدار پزشکی", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        plan = WorkoutService.create_workout_plan(plan_info, days_data)
        WorkoutService.assign_plan_to_member(member_id, plan.id)
        QMessageBox.information(self, "موفقیت", "برنامه تمرینی با موفقیت به ورزشکار تخصیص یافت.")
        self.reset_to_new_plan()
