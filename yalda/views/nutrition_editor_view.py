from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from yalda.services.nutrition_service import NutritionService
from yalda.services.member_service import MemberService

class NutritionEditorView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.meal_tables = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title & Food Bank Button
        header = QHBoxLayout()
        title = QLabel("🥗 برنامه‌ریزی تغذیه و رژیم ایرانی")
        title.setObjectName("h1")

        btn_food_bank = QPushButton("🥗 بانک و ویرایش مواد غذایی")
        btn_food_bank.setObjectName("secondary_button")
        btn_food_bank.clicked.connect(self.open_food_bank)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_food_bank)
        layout.addLayout(header)

        # Macros Goal Box
        goal_box = QGroupBox("اهداف فیزیکی و درشت‌مغذی‌های رژیم (Macronutrients)")
        layout_goal = QVBoxLayout(goal_box)

        # Template Picker Row
        row_tpl = QHBoxLayout()
        self.combo_templates = QComboBox()
        self.combo_templates.addItem("--- انتخاب و بارگذاری الگوی آماده رژیم از بانک ---", None)
        self.load_template_dropdown()
        self.combo_templates.currentIndexChanged.connect(self.on_template_selected)

        row_tpl.addWidget(QLabel("📂 الگوهای آماده رژیم بانک:"))
        row_tpl.addWidget(self.combo_templates)
        layout_goal.addLayout(row_tpl)

        row1 = QHBoxLayout()
        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("عنوان رژیم (مثلاً: رژیم هایپرتروفی ۲۵۰۰ کالری)...")

        self.combo_goal = QComboBox()
        self.combo_goal.addItem("عضله‌سازی (Muscle Gain)", "muscle_gain")
        self.combo_goal.addItem("کاهش وزن و چربی‌سوزی (Weight Loss)", "weight_loss")
        self.combo_goal.addItem("افزایش وزن (Weight Gain)", "weight_gain")
        self.combo_goal.addItem("تثبیت وزن (Maintenance)", "maintenance")

        row1.addWidget(QLabel("عنوان رژیم:"))
        row1.addWidget(self.txt_title)
        row1.addWidget(QLabel("هدف رژیم:"))
        row1.addWidget(self.combo_goal)
        layout_goal.addLayout(row1)

        row2 = QHBoxLayout()
        self.spin_cal = QDoubleSpinBox()
        self.spin_cal.setRange(800, 5000)
        self.spin_cal.setValue(2200)

        self.spin_protein = QDoubleSpinBox()
        self.spin_protein.setRange(40, 350)
        self.spin_protein.setValue(160)

        self.spin_carbs = QDoubleSpinBox()
        self.spin_carbs.setRange(50, 600)
        self.spin_carbs.setValue(220)

        self.spin_fat = QDoubleSpinBox()
        self.spin_fat.setRange(20, 200)
        self.spin_fat.setValue(60)

        row2.addWidget(QLabel("کالری هدف (kcal):"))
        row2.addWidget(self.spin_cal)
        row2.addWidget(QLabel("پروتئین (g):"))
        row2.addWidget(self.spin_protein)
        row2.addWidget(QLabel("کربوهیدرات (g):"))
        row2.addWidget(self.spin_carbs)
        row2.addWidget(QLabel("چربی (g):"))
        row2.addWidget(self.spin_fat)
        layout_goal.addLayout(row2)

        layout.addWidget(goal_box)

        # Tabs for Meals
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.setup_meal_tabs()

        # Assignment Box & Actions
        assign_box = QGroupBox("تخصیص برنامه تغذیه به ورزشکار")
        layout_assign = QHBoxLayout(assign_box)

        self.combo_member = QComboBox()
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
        self.combo_member.clear()
        members = MemberService.get_all_members(status_filter="active")
        for m in members:
            self.combo_member.addItem(f"{m.full_name} ({m.phone})", m.id)

    def load_template_dropdown(self):
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
                if meal_key in meal_dict:
                    m_plan = meal_dict[meal_key]
                    for item in m_plan.items:
                        row = table.rowCount()
                        table.insertRow(row)

                        combo_food = QComboBox()
                        for f in foods_list:
                            combo_food.addItem(f"{f.name_fa} ({f.unit} - {int(f.calories)}kcal)", f.id)

                        if item.food_id:
                            idx_f = combo_food.findData(item.food_id)
                            if idx_f >= 0:
                                combo_food.setCurrentIndex(idx_f)

                        txt_amount = QLineEdit(str(item.amount or 1.0))
                        txt_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        txt_notes = QLineEdit(item.notes or "")
                        txt_notes.setPlaceholderText("توضیحات اختصاصی...")

                        btn_del = QPushButton("🗑️")
                        btn_del.setObjectName("danger_button")
                        btn_del.setToolTip("حذف ماده غذایی")
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

        meals = [
            ("breakfast", "🌅 صبحانه"),
            ("morning_snack", "🍎 میان‌وعده صبح"),
            ("lunch", "🍗 ناهار"),
            ("afternoon_snack", "🍌 عصرانه"),
            ("dinner", "🍲 شام"),
            ("evening_snack", "🥛 قبل از خواب")
        ]

        for meal_key, meal_title in meals:
            widget = QWidget()
            layout_meal = QVBoxLayout(widget)

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
            self.tabs.addTab(widget, meal_title)
            self.meal_tables.append((meal_key, table))

            # Add 1 initial row for primary meals
            if meal_key in ["breakfast", "lunch", "dinner"]:
                self.add_food_row(table, foods_list)

    def refresh_editor(self):
        self.load_members_dropdown()
        self.load_template_dropdown()
        self.setup_meal_tabs()

    def add_food_row(self, table: QTableWidget, foods_list: list = None):
        row = table.rowCount()
        table.insertRow(row)

        foods_list = NutritionService.get_all_foods()

        combo_food = QComboBox()
        for f in foods_list:
            combo_food.addItem(f"{f.name_fa} ({f.unit} - {int(f.calories)}kcal)", f.id)

        txt_amount = QLineEdit("1.0")
        txt_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_notes = QLineEdit("")
        txt_notes.setPlaceholderText("توضیحات اختصاصی...")

        btn_del = QPushButton("🗑️")
        btn_del.setObjectName("danger_button")
        btn_del.setToolTip("حذف ماده غذایی")
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

    def save_plan(self):
        plan_info, meals_data = self.get_plan_data()
        plan = NutritionService.create_nutrition_plan(plan_info, meals_data)
        self.load_template_dropdown()
        QMessageBox.information(self, "موفقیت", "الگوی برنامه غذایی با موفقیت در بانک ذخیره شد.")
        return plan

    def assign_plan(self):
        member_id = self.combo_member.currentData()
        if not member_id:
            QMessageBox.warning(self, "خطا", "لطفاً یک ورزشکار را جهت تخصیص انتخاب کنید.")
            return

        plan = self.save_plan()
        NutritionService.assign_nutrition_plan(member_id, plan.id)
        QMessageBox.information(self, "موفقیت", "برنامه غذایی با موفقیت به ورزشکار تخصیص یافت.")

    def open_food_bank(self):
        from yalda.views.food_library_dialog import FoodLibraryDialog
        dlg = FoodLibraryDialog(self)
        dlg.exec()
        self.setup_meal_tabs()
