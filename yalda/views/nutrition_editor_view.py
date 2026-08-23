from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from yalda.services.nutrition_service import NutritionService
from yalda.services.member_service import MemberService
from yalda.views.components.searchable_combo_box import SearchableComboBox

class NutritionEditorView(QWidget):
    manage_templates_requested = pyqtSignal()
    open_food_bank_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.meal_tables = []
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

        # Header Title & Action Buttons
        header = QHBoxLayout()
        self.lbl_header_title = QLabel("🥗 برنامه‌ریزی تغذیه")
        self.lbl_header_title.setObjectName("h1")

        btn_new_plan = QPushButton("➕ رژیم جدید")
        btn_new_plan.setObjectName("secondary_button")
        btn_new_plan.clicked.connect(self.reset_form)

        btn_manage_tpl = QPushButton("📋 مدیریت و مشاهده الگوها")
        btn_manage_tpl.setObjectName("secondary_button")
        btn_manage_tpl.clicked.connect(self.manage_templates_requested.emit)

        btn_food_bank = QPushButton("🥗 بانک مواد غذایی")
        btn_food_bank.setObjectName("secondary_button")
        btn_food_bank.clicked.connect(self.open_food_bank_requested.emit)

        header.addWidget(self.lbl_header_title)
        header.addStretch()
        header.addWidget(btn_new_plan)
        header.addWidget(btn_manage_tpl)
        header.addWidget(btn_food_bank)
        layout.addLayout(header)

        # Macros Goal Box
        goal_box = QGroupBox("اهداف فیزیکی و درشت‌مغذی‌های رژیم (Macronutrients)")
        layout_goal = QVBoxLayout(goal_box)
        layout_goal.setSpacing(12)
        layout_goal.setContentsMargins(12, 12, 12, 12)

        # Row 1: Title -> Goal -> Days Pattern -> Template Picker
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        lbl_title = QLabel("عنوان رژیم:")
        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("مثلاً: رژیم افزایش حجم عضلانی...")

        lbl_goal = QLabel("هدف رژیم:")
        self.combo_goal = QComboBox()
        self.combo_goal.addItem("عضله‌سازی (Muscle Gain)", "muscle_gain")
        self.combo_goal.addItem("کاهش وزن و چربی‌سوزی (Weight Loss)", "weight_loss")
        self.combo_goal.addItem("افزایش وزن (Weight Gain)", "weight_gain")
        self.combo_goal.addItem("تثبیت وزن (Maintenance)", "maintenance")

        lbl_days = QLabel("روزهای هفته:")
        self.combo_days = QComboBox()
        self.combo_days.addItem("الگوی ثابت (کلیه روزهای هفته)", "all_days")
        self.combo_days.addItem("شنبه تا جمعه (۷ روز هفته)", "7_days")
        self.combo_days.addItem("روزهای تمرین و استراحت (۲ روزه)", "2_days")
        self.combo_days.addItem("۳ روز در هفته", "3_days")
        self.combo_days.addItem("۴ روز در هفته", "4_days")
        self.combo_days.addItem("۵ روز در هفته", "5_days")
        self.combo_days.addItem("۶ روز در هفته", "6_days")
        self.combo_days.currentIndexChanged.connect(self.setup_meal_tabs)

        lbl_template = QLabel("الگوی آماده:")
        self.combo_templates = QComboBox()
        self.load_template_dropdown()
        self.combo_templates.currentIndexChanged.connect(self.on_template_selected)

        row1.addWidget(lbl_title)
        row1.addWidget(self.txt_title, 2)
        row1.addWidget(lbl_goal)
        row1.addWidget(self.combo_goal, 1)
        row1.addWidget(lbl_days)
        row1.addWidget(self.combo_days, 1)
        row1.addWidget(lbl_template)
        row1.addWidget(self.combo_templates, 2)
        layout_goal.addLayout(row1)

        # Row 2: Target Calories & Macros
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.spin_cal = QDoubleSpinBox()
        self.spin_cal.setRange(500, 10000)
        self.spin_cal.setValue(2000.0)
        self.spin_cal.setDecimals(0)
        self.spin_cal.setFixedWidth(100)

        self.spin_protein = QDoubleSpinBox()
        self.spin_protein.setRange(0, 1000)
        self.spin_protein.setValue(150.0)
        self.spin_protein.setDecimals(0)
        self.spin_protein.setFixedWidth(90)

        self.spin_carbs = QDoubleSpinBox()
        self.spin_carbs.setRange(0, 1000)
        self.spin_carbs.setValue(200.0)
        self.spin_carbs.setDecimals(0)
        self.spin_carbs.setFixedWidth(90)

        self.spin_fat = QDoubleSpinBox()
        self.spin_fat.setRange(0, 1000)
        self.spin_fat.setValue(60.0)
        self.spin_fat.setDecimals(0)
        self.spin_fat.setFixedWidth(90)

        self.spin_total_grams = QDoubleSpinBox()
        self.spin_total_grams.setRange(0, 5000)
        self.spin_total_grams.setReadOnly(True)
        self.spin_total_grams.setDecimals(0)
        self.spin_total_grams.setFixedWidth(90)
        self.spin_total_grams.setStyleSheet("font-weight: bold; color: #4ADE80; background-color: #1A1A1A;")

        self.txt_calorie_percent = QLineEdit()
        self.txt_calorie_percent.setReadOnly(True)
        self.txt_calorie_percent.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_calorie_percent.setFixedWidth(210)

        h_cal = QHBoxLayout()
        h_cal.setSpacing(4)
        h_cal.addWidget(QLabel("کالری (kcal):"))
        h_cal.addWidget(self.spin_cal)

        h_pro = QHBoxLayout()
        h_pro.setSpacing(4)
        h_pro.addWidget(QLabel("پروتئین (g):"))
        h_pro.addWidget(self.spin_protein)

        h_carbs = QHBoxLayout()
        h_carbs.setSpacing(4)
        h_carbs.addWidget(QLabel("کربوهیدرات (g):"))
        h_carbs.addWidget(self.spin_carbs)

        h_fat = QHBoxLayout()
        h_fat.setSpacing(4)
        h_fat.addWidget(QLabel("چربی (g):"))
        h_fat.addWidget(self.spin_fat)

        h_total_g = QHBoxLayout()
        h_total_g.setSpacing(4)
        h_total_g.addWidget(QLabel("گرم مواد غذایی (g):"))
        h_total_g.addWidget(self.spin_total_grams)

        h_pct = QHBoxLayout()
        h_pct.setSpacing(4)
        h_pct.addWidget(QLabel("درصد کالری (٪):"))
        h_pct.addWidget(self.txt_calorie_percent)

        row2.addLayout(h_cal)
        row2.addLayout(h_pro)
        row2.addLayout(h_carbs)
        row2.addLayout(h_fat)
        row2.addLayout(h_total_g)
        row2.addLayout(h_pct)
        row2.addStretch()
        layout_goal.addLayout(row2)

        self.spin_cal.valueChanged.connect(self.update_macro_calculations)
        self.spin_protein.valueChanged.connect(self.update_macro_calculations)
        self.spin_carbs.valueChanged.connect(self.update_macro_calculations)
        self.spin_fat.valueChanged.connect(self.update_macro_calculations)
        self.update_macro_calculations()

        layout.addWidget(goal_box)

        # Tabs for Meals
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.setup_meal_tabs()

        # Assignment Box & Actions
        assign_box = QGroupBox("تخصیص برنامه تغذیه به ورزشکار")
        layout_assign = QHBoxLayout(assign_box)

        self.combo_member = SearchableComboBox(placeholder="جستجو یا تایپ نام ورزشکار...")
        self.load_members_dropdown()

        btn_save = QPushButton("💾 ذخیره الگوی رژیم در بانک")
        btn_save.setObjectName("secondary_button")
        btn_save.clicked.connect(self.save_plan)

        btn_assign = QPushButton("✅ تخصیص به ورزشکار")
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
        self.combo_member.addItem("--- انتخاب ورزشکار ---", None)
        members = MemberService.get_all_members(status_filter="active")
        for m in members:
            self.combo_member.addItem(f"{m.full_name} ({m.phone})", m.id)
        if cur is not None:
            idx = self.combo_member.findData(cur)
            if idx >= 0:
                self.combo_member.setCurrentIndex(idx)
        self.combo_member.blockSignals(False)

    def set_selected_member(self, member_id: int):
        self.load_members_dropdown()
        idx = self.combo_member.findData(member_id)
        if idx >= 0:
            self.combo_member.setCurrentIndex(idx)

    def load_template_dropdown(self):
        cur = self.combo_templates.currentData()
        self.combo_templates.blockSignals(True)
        self.combo_templates.clear()
        self.combo_templates.addItem("--- انتخاب و بارگذاری الگوی آماده رژیم از بانک ---", None)
        plans = NutritionService.get_all_plans()
        for p in plans:
            goal_title = {
                "muscle_gain": "عضله‌سازی",
                "weight_loss": "کاهش وزن",
                "weight_gain": "افزایش وزن",
                "maintenance": "تثبیت وزن"
            }.get(p.goal, p.goal)
            self.combo_templates.addItem(f"🥗 {p.title} ({int(p.target_calories)} kcal - {goal_title})", p.id)
        if cur is not None:
            idx = self.combo_templates.findData(cur)
            if idx >= 0:
                self.combo_templates.setCurrentIndex(idx)
        else:
            self.combo_templates.setCurrentIndex(0)
        self.combo_templates.blockSignals(False)

    def on_template_selected(self, index: int):
        try:
            plan_id = self.combo_templates.currentData()
            if not plan_id:
                return

            plan = NutritionService.get_plan_by_id(plan_id)
            if not plan:
                return

            self.txt_title.setText(plan.title or "")

            idx_g = self.combo_goal.findData(plan.goal)
            if idx_g >= 0:
                self.combo_goal.setCurrentIndex(idx_g)

            self.spin_cal.setValue(plan.target_calories or 2000.0)
            self.spin_protein.setValue(plan.target_protein or 150.0)
            self.spin_carbs.setValue(plan.target_carbs or 200.0)
            self.spin_fat.setValue(plan.target_fat or 60.0)

            # Rebuild meal tabs
            self.setup_meal_tabs()

            foods_list = NutritionService.get_all_foods()

            # Map meals from loaded plan into meal tables
            meal_dict = {m.meal_name: m for m in plan.meals}

            for meal_key, table in self.meal_tables:
                table.setRowCount(0)
                matched_m = meal_dict.get(meal_key)
                if not matched_m:
                    for k, v in meal_dict.items():
                        if k in meal_key or meal_key in k:
                            matched_m = v
                            break

                if matched_m:
                    for item in matched_m.items:
                        row = table.rowCount()
                        table.insertRow(row)

                        combo_food = SearchableComboBox(placeholder="جستجو یا تایپ نام ماده غذایی...")
                        for f in foods_list:
                            combo_food.addItem(f"{f.name_fa} ({f.unit} - {int(f.calories)}kcal)", f.id)

                        if item.food_id:
                            idx_f = combo_food.findData(item.food_id)
                            if idx_f >= 0:
                                combo_food.setCurrentIndex(idx_f)

                        txt_amount = QLineEdit(str(item.amount or 1.0))
                        txt_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        txt_notes = QLineEdit(item.notes or "")
                        txt_notes.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        txt_notes.setPlaceholderText("توضیحات اختصاصی...")

                        btn_del = QPushButton("🗑️")
                        btn_del.setObjectName("danger_button")
                        btn_del.setToolTip("حذف ماده غذایی")
                        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
                        btn_del.clicked.connect(lambda _, t=table, r=row: t.removeRow(r))

                        table.setCellWidget(row, 0, combo_food)
                        table.setCellWidget(row, 1, txt_amount)
                        table.setCellWidget(row, 2, txt_notes)
                        table.setCellWidget(row, 3, btn_del)

            QMessageBox.information(self, "موفقیت", f"الگوی رژیم '{plan.title}' با موفقیت در فرم بارگذاری شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری الگوی رژیم: {str(e)}")

    def setup_meal_tabs(self):
        self.tabs.clear()
        self.meal_tables.clear()
        foods_list = NutritionService.get_all_foods()

        days_mode = self.combo_days.currentData() or "all_days"
        
        if days_mode == "7_days":
            days = [
                ("sat", "شنبه"),
                ("sun", "یکشنبه"),
                ("mon", "دوشنبه"),
                ("tue", "سه‌شنبه"),
                ("wed", "چهارشنبه"),
                ("thu", "پنج‌شنبه"),
                ("fri", "جمعه")
            ]
        elif days_mode == "2_days":
            days = [
                ("training", "روزهای تمرینی"),
                ("rest", "روزهای استراحت")
            ]
        elif days_mode == "3_days":
            days = [("day1", "روز اول"), ("day2", "روز دوم"), ("day3", "روز سوم")]
        elif days_mode == "4_days":
            days = [("day1", "روز اول"), ("day2", "روز دوم"), ("day3", "روز سوم"), ("day4", "روز چهارم")]
        elif days_mode == "5_days":
            days = [("day1", "روز اول"), ("day2", "روز دوم"), ("day3", "روز سوم"), ("day4", "روز چهارم"), ("day5", "روز پنجم")]
        elif days_mode == "6_days":
            days = [("day1", "روز اول"), ("day2", "روز دوم"), ("day3", "روز سوم"), ("day4", "روز چهارم"), ("day5", "روز پنجم"), ("day6", "روز ششم")]
        else:
            days = [("daily", "برنامه کلیه روزهای هفته")]

        meals = [
            ("breakfast", "🌅 صبحانه"),
            ("morning_snack", "🍎 میان‌وعده صبح"),
            ("lunch", "🍗 ناهار"),
            ("afternoon_snack", "🍌 عصرانه"),
            ("dinner", "🍲 شام"),
            ("evening_snack", "🥛 قبل از خواب")
        ]

        if len(days) == 1:
            for meal_key, meal_title in meals:
                widget = self._create_meal_widget(meal_key, meal_title, foods_list)
                self.tabs.addTab(widget, meal_title)
        else:
            for day_key, day_title in days:
                day_tab_widget = QTabWidget()
                for meal_key, meal_title in meals:
                    full_key = f"{day_title}: {meal_title}"
                    widget = self._create_meal_widget(full_key, meal_title, foods_list)
                    day_tab_widget.addTab(widget, meal_title)
                self.tabs.addTab(day_tab_widget, f"📅 {day_title}")

    def _create_meal_widget(self, meal_key: str, meal_title: str, foods_list: list) -> QWidget:
        widget = QWidget()
        layout_meal = QVBoxLayout(widget)
        layout_meal.setContentsMargins(8, 8, 8, 8)
        layout_meal.setSpacing(10)

        row_top = QHBoxLayout()
        btn_add_item = QPushButton("➕ افزودن ماده غذایی")
        btn_add_item.setObjectName("secondary_button")
        row_top.addStretch()
        row_top.addWidget(btn_add_item)
        layout_meal.addLayout(row_top)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["نام ماده غذایی", "مقدار (ضریب واحد)", "توضیحات مربی", "حذف"])
        table.verticalHeader().setDefaultSectionSize(48)
        table.verticalHeader().setMinimumSectionSize(40)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        table.setColumnWidth(1, 140)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(3, 60)

        btn_add_item.clicked.connect(lambda _, t=table: self.add_food_row(t, foods_list))

        layout_meal.addWidget(table)
        self.meal_tables.append((meal_key, table))
        return widget

    def update_macro_calculations(self):
        cal = self.spin_cal.value()
        p = self.spin_protein.value()
        c = self.spin_carbs.value()
        f = self.spin_fat.value()

        total_g = p + c + f
        self.spin_total_grams.setValue(total_g if total_g > 0 else 0.0)

        if cal > 0 and total_g > 0:
            p_pct = (p * 4 / cal) * 100
            c_pct = (c * 4 / cal) * 100
            f_pct = (f * 9 / cal) * 100
            self.txt_calorie_percent.setText(f"{p_pct:.0f}% پروتئین | {c_pct:.0f}% کربوهیدرات | {f_pct:.0f}% چربی")
        else:
            self.txt_calorie_percent.setText("")

    def refresh_editor(self):
        self.load_members_dropdown()
        cur_tpl = self.combo_templates.currentData()
        self.combo_templates.blockSignals(True)
        self.load_template_dropdown()
        if cur_tpl is not None:
            idx = self.combo_templates.findData(cur_tpl)
            if idx >= 0:
                self.combo_templates.setCurrentIndex(idx)
        self.combo_templates.blockSignals(False)

    def add_food_row(self, table: QTableWidget, foods_list: list = None):
        row = table.rowCount()
        table.insertRow(row)

        if not foods_list:
            foods_list = NutritionService.get_all_foods()

        combo_food = SearchableComboBox(placeholder="جستجو یا تایپ نام ماده غذایی...")
        for f in foods_list:
            combo_food.addItem(f"{f.name_fa} ({f.unit} - {int(f.calories)}kcal)", f.id)
        combo_food.set_empty()

        txt_amount = QLineEdit("1.0")
        txt_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_notes = QLineEdit("")
        txt_notes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt_notes.setPlaceholderText("توضیحات اختصاصی...")

        btn_del = QPushButton("🗑️")
        btn_del.setObjectName("danger_button")
        btn_del.setToolTip("حذف ماده غذایی")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda _, t=table, r=row: t.removeRow(r))

        table.setCellWidget(row, 0, combo_food)
        table.setCellWidget(row, 1, txt_amount)
        table.setCellWidget(row, 2, txt_notes)
        table.setCellWidget(row, 3, btn_del)

    def get_plan_data(self):
        title = self.txt_title.text().strip() or "برنامه غذایی ایرانی"
        meals_data = []

        for idx, (meal_key, table) in enumerate(self.meal_tables, start=1):
            items = []
            for row in range(table.rowCount()):
                combo_food = table.cellWidget(row, 0)
                if not combo_food:
                    continue
                food_id = combo_food.currentData()
                amount_str = table.cellWidget(row, 1).text().strip()
                notes = table.cellWidget(row, 2).text().strip()

                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 1.0

                items.append({
                    "food_id": food_id,
                    "amount": amount,
                    "notes": notes
                })

            meals_data.append({
                "meal_name": meal_key,
                "order_index": idx,
                "items": items
            })

        plan_info = {
            "title": title,
            "goal": self.combo_goal.currentData(),
            "target_calories": self.spin_cal.value(),
            "target_protein": self.spin_protein.value(),
            "target_carbs": self.spin_carbs.value(),
            "target_fat": self.spin_fat.value()
        }
        return plan_info, meals_data

    def save_plan(self, auto_reset: bool = True):
        plan_info, meals_data = self.get_plan_data()
        if self.editing_plan_id:
            plan = NutritionService.update_nutrition_plan(self.editing_plan_id, plan_info, meals_data)
            if auto_reset:
                self.reset_form()
            else:
                self.combo_templates.blockSignals(True)
                self.load_template_dropdown()
                self.combo_templates.blockSignals(False)
            QMessageBox.information(self, "موفقیت", f"الگوی برنامه غذایی «{plan.title}» با موفقیت به‌روزرسانی شد.")
        else:
            plan = NutritionService.create_nutrition_plan(plan_info, meals_data)
            if auto_reset:
                self._do_reset_fields()
            self.combo_templates.blockSignals(True)
            self.load_template_dropdown()
            self.combo_templates.blockSignals(False)
            if auto_reset:
                self.setup_meal_tabs()
            QMessageBox.information(self, "موفقیت", "الگوی برنامه غذایی با موفقیت در بانک ذخیره شد.")
        return plan

    def _do_reset_fields(self):
        """فقط پاکسازی فیلدهای کادر اهداف فیزیکی، بدون لمس جدول وعده‌ها"""
        for w in [self.txt_title, self.combo_goal, self.combo_days, self.spin_cal, self.spin_protein,
                  self.spin_carbs, self.spin_fat, self.spin_total_grams, self.combo_templates]:
            w.blockSignals(True)

        self.txt_title.setText("")
        self.combo_goal.setCurrentIndex(0)
        self.combo_days.setCurrentIndex(0)
        self.spin_cal.setValue(0.0)
        self.spin_protein.setValue(0.0)
        self.spin_carbs.setValue(0.0)
        self.spin_fat.setValue(0.0)
        self.spin_total_grams.setValue(0.0)
        self.txt_calorie_percent.setText("")

        for w in [self.txt_title, self.combo_goal, self.combo_days, self.spin_cal, self.spin_protein,
                  self.spin_carbs, self.spin_fat, self.spin_total_grams, self.combo_templates]:
            w.blockSignals(False)

    def reset_form(self):
        self.editing_plan_id = None
        self.lbl_header_title.setText("🥗 برنامه‌ریزی تغذیه")
        self._do_reset_fields()
        self.combo_templates.blockSignals(True)
        if self.combo_templates.count() > 0:
            self.combo_templates.setCurrentIndex(0)
        self.combo_templates.blockSignals(False)
        self.setup_meal_tabs()

    def load_plan_for_edit(self, plan_id: int):
        self.editing_plan_id = plan_id
        idx_tpl = self.combo_templates.findData(plan_id)
        if idx_tpl >= 0:
            self.combo_templates.setCurrentIndex(idx_tpl)
        else:
            plan = NutritionService.get_plan_by_id(plan_id)
            if plan:
                self.txt_title.setText(plan.title or "")
                idx_g = self.combo_goal.findData(plan.goal)
                if idx_g >= 0: self.combo_goal.setCurrentIndex(idx_g)
                self.spin_cal.setValue(plan.target_calories or 0.0)
                self.spin_protein.setValue(plan.target_protein or 0.0)
                self.spin_carbs.setValue(plan.target_carbs or 0.0)
                self.spin_fat.setValue(plan.target_fat or 0.0)

        plan = NutritionService.get_plan_by_id(plan_id)
        if plan:
            self.lbl_header_title.setText(f"✏️ ویرایش الگوی غذایی: {plan.title}")

    def assign_plan(self):
        member_id = self.combo_member.currentData()
        if not member_id:
            QMessageBox.warning(self, "خطا", "لطفاً یک ورزشکار را جهت تخصیص انتخاب کنید.")
            return

        plan = self.save_plan(auto_reset=False)
        NutritionService.assign_nutrition_plan(member_id, plan.id)
        QMessageBox.information(self, "موفقیت", "برنامه غذایی با موفقیت به ورزشکار تخصیص یافت.")
        self.reset_form()

    def open_food_bank(self):
        from yalda.views.food_library_dialog import FoodLibraryDialog
        dlg = FoodLibraryDialog(self)
        dlg.exec()
        self.setup_meal_tabs()
