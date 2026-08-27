from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QGroupBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from yalda.services.nutrition_service import NutritionService
from yalda.services.member_service import MemberService
from yalda.views.components.searchable_combo_box import SearchableComboBox

class NutritionEditorView(QWidget):
    manage_templates_requested = pyqtSignal()
    open_food_bank_requested = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.meal_tables = []
        self.editing_plan_id = None
        self._undo_stack = []
        self._redo_stack = []
        self._undo_buttons = []
        self._redo_buttons = []
        self._is_undoing_redoing = False
        self.init_ui()

        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.redo)

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

        btn_back = QPushButton("⬅️ بازگشت به صفحه قبل")
        btn_back.setObjectName("back_button")
        btn_back.clicked.connect(self.back_requested.emit)

        btn_reset = QPushButton("🔄 بازنشانی تغییرات")
        btn_reset.setObjectName("secondary_button")
        btn_reset.clicked.connect(self.revert_changes)

        btn_new_plan = QPushButton("➕ رژیم جدید")
        btn_new_plan.setObjectName("secondary_button")
        btn_new_plan.clicked.connect(self.reset_form)

        btn_manage_tpl = QPushButton("📋 مدیریت و مشاهده الگوها")
        btn_manage_tpl.setObjectName("secondary_button")
        btn_manage_tpl.clicked.connect(self.manage_templates_requested.emit)

        btn_food_bank = QPushButton("🥗 بانک مواد غذایی")
        btn_food_bank.setObjectName("secondary_button")
        btn_food_bank.clicked.connect(self.open_food_bank_requested.emit)

        header.addWidget(btn_back)
        header.addWidget(self.lbl_header_title)
        header.addStretch()
        header.addWidget(btn_reset)
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
        self.txt_title.textEdited.connect(lambda: self._snapshot_change())

        lbl_goal = QLabel("هدف رژیم:")
        self.combo_goal = QComboBox()
        self.combo_goal.addItem("عضله‌سازی (Muscle Gain)", "muscle_gain")
        self.combo_goal.addItem("کاهش وزن و چربی‌سوزی (Weight Loss)", "weight_loss")
        self.combo_goal.addItem("افزایش وزن (Weight Gain)", "weight_gain")
        self.combo_goal.addItem("تثبیت وزن (Maintenance)", "maintenance")
        self.combo_goal.currentIndexChanged.connect(lambda: self._snapshot_change())

        lbl_days = QLabel("روزهای هفته:")
        self.combo_days = QComboBox()
        self.combo_days.addItem("📅 شنبه تا جمعه (۷ روز هفته)", "7_days")
        self.combo_days.addItem("📅 روزهای تمرین و استراحت (۲ روزه)", "2_days")
        self.combo_days.addItem("📅 ۳ روز در هفته", "3_days")
        self.combo_days.addItem("📅 ۴ روز در هفته", "4_days")
        self.combo_days.addItem("📅 ۵ روز در هفته", "5_days")
        self.combo_days.addItem("📅 ۶ روز در هفته", "6_days")
        self.combo_days.addItem("📅 الگوی ثابت (کلیه روزهای هفته)", "all_days")
        self.combo_days.currentIndexChanged.connect(self.on_days_pattern_changed)

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
        self.spin_cal.valueChanged.connect(lambda: self._snapshot_change())

        self.spin_protein = QDoubleSpinBox()
        self.spin_protein.setRange(0, 1000)
        self.spin_protein.setValue(150.0)
        self.spin_protein.setDecimals(0)
        self.spin_protein.setFixedWidth(90)
        self.spin_protein.valueChanged.connect(lambda: self._snapshot_change())

        self.spin_carbs = QDoubleSpinBox()
        self.spin_carbs.setRange(0, 1000)
        self.spin_carbs.setValue(200.0)
        self.spin_carbs.setDecimals(0)
        self.spin_carbs.setFixedWidth(90)
        self.spin_carbs.valueChanged.connect(lambda: self._snapshot_change())

        self.spin_fat = QDoubleSpinBox()
        self.spin_fat.setRange(0, 1000)
        self.spin_fat.setValue(60.0)
        self.spin_fat.setDecimals(0)
        self.spin_fat.setFixedWidth(90)
        self.spin_fat.valueChanged.connect(lambda: self._snapshot_change())

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

    def _load_plan_data_to_form(self, plan):
        if not plan:
            return
        self._loading_plan = True
        try:
            self.txt_title.setText(plan.title or "")

            idx_g = self.combo_goal.findData(plan.goal)
            if idx_g >= 0:
                self.combo_goal.setCurrentIndex(idx_g)

            self.spin_cal.setValue(plan.target_calories or 2000.0)
            self.spin_protein.setValue(plan.target_protein or 150.0)
            self.spin_carbs.setValue(plan.target_carbs or 200.0)
            self.spin_fat.setValue(plan.target_fat or 60.0)

            # Detect days pattern from meal names in plan
            has_7_days = any(any(d in m.meal_name for d in ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"]) for m in plan.meals)
            has_2_days = any("تمرین" in m.meal_name or "استراحت" in m.meal_name for m in plan.meals)

            self.combo_days.blockSignals(True)
            if has_2_days:
                idx_d = self.combo_days.findData("2_days")
                if idx_d >= 0: self.combo_days.setCurrentIndex(idx_d)
            elif has_7_days:
                idx_d = self.combo_days.findData("7_days")
                if idx_d >= 0: self.combo_days.setCurrentIndex(idx_d)
            self.combo_days.blockSignals(False)

            # Rebuild meal tabs
            self.setup_meal_tabs()

            foods_list = NutritionService.get_all_foods()

            meal_alias_map = {
                "breakfast": ["breakfast", "صبحانه"],
                "morning_snack": ["morning_snack", "میان‌وعده صبح", "میان وعده صبح"],
                "lunch": ["lunch", "ناهار"],
                "afternoon_snack": ["afternoon_snack", "عصرانه"],
                "dinner": ["dinner", "شام"],
                "evening_snack": ["evening_snack", "قبل از خواب", "خواب"]
            }
            day_keys = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "تمرین", "استراحت", "روز اول", "روز دوم", "روز سوم", "روز چهارم", "روز پنجم", "روز ششم"]

            def match_meal(table_k, m_name):
                if table_k == m_name or m_name in table_k or table_k in m_name:
                    return True
                for meal_code, aliases in meal_alias_map.items():
                    if any(a in table_k for a in aliases):
                        if any(a in m_name for a in aliases):
                            t_day = next((d for d in day_keys if d in table_k), None)
                            m_day = next((d for d in day_keys if d in m_name), None)
                            if t_day and m_day:
                                return t_day == m_day
                            if t_day and not m_day:
                                return t_day == "شنبه" or len(plan.meals) <= 6
                            return True
                return False

            for meal_key, table in self.meal_tables:
                table.setRowCount(0)
                matched_m = None
                for m in plan.meals:
                    if match_meal(meal_key, m.meal_name):
                        matched_m = m
                        break

                if matched_m and matched_m.items:
                    for item in matched_m.items:
                        r = table.rowCount()
                        table.insertRow(r)
                        self._create_food_row_widgets(table, r, foods_list, {
                            "food_id": item.food_id,
                            "amount": item.amount or 1.0,
                            "notes": item.notes or ""
                        })
            self._undo_stack.clear()
            self._redo_stack.clear()
            self._last_state = self._capture_state()
            self._update_undo_redo_ui()
        finally:
            self._loading_plan = False

    def on_template_selected(self, index: int):
        try:
            plan_id = self.combo_templates.currentData()
            if not plan_id:
                return

            plan = NutritionService.get_plan_by_id(plan_id)
            if not plan:
                return

            self._load_plan_data_to_form(plan)
            QMessageBox.information(self, "موفقیت", f"الگوی رژیم '{plan.title}' با موفقیت در فرم بارگذاری شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری الگوی رژیم: {str(e)}")

    def on_days_pattern_changed(self):
        self.setup_meal_tabs()
        self._snapshot_change()

    def _capture_state(self):
        state = {
            "title": self.txt_title.text(),
            "goal": self.combo_goal.currentData(),
            "days_pattern": self.combo_days.currentData(),
            "cal": self.spin_cal.value(),
            "protein": self.spin_protein.value(),
            "carbs": self.spin_carbs.value(),
            "fat": self.spin_fat.value(),
            "tab_index": self.tabs.currentIndex(),
            "meals": []
        }
        for meal_key, table in self.meal_tables:
            meal_items = []
            for r in range(table.rowCount()):
                combo = table.cellWidget(r, 0)
                f_id = combo.currentData() if combo else None
                f_text = combo.currentText() if combo else ""
                txt_amount = table.cellWidget(r, 1)
                txt_notes = table.cellWidget(r, 2)
                meal_items.append({
                    "food_id": f_id,
                    "food_text": f_text,
                    "amount": txt_amount.text() if txt_amount else "1.0",
                    "notes": txt_notes.text() if txt_notes else ""
                })
            state["meals"].append({
                "meal_key": meal_key,
                "items": meal_items
            })
        return state

    def _snapshot_change(self):
        if self._is_undoing_redoing or getattr(self, '_loading_plan', False):
            return
        new_state = self._capture_state()
        if not hasattr(self, '_last_state') or self._last_state is None:
            self._last_state = new_state
            return
        if self._last_state == new_state:
            return
        self._undo_stack.append(self._last_state)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        self._last_state = new_state
        self._update_undo_redo_ui()

    def undo(self):
        if not self._undo_stack:
            return
        current = self._capture_state()
        self._redo_stack.append(current)
        prev = self._undo_stack.pop()
        self._restore_state(prev)
        self._last_state = prev
        self._update_undo_redo_ui()

    def redo(self):
        if not self._redo_stack:
            return
        current = self._capture_state()
        self._undo_stack.append(current)
        next_st = self._redo_stack.pop()
        self._restore_state(next_st)
        self._last_state = next_st
        self._update_undo_redo_ui()

    def _update_undo_redo_ui(self):
        can_undo = len(self._undo_stack) > 0
        can_redo = len(self._redo_stack) > 0
        for btn in getattr(self, '_undo_buttons', []):
            btn.setEnabled(can_undo)
        for btn in getattr(self, '_redo_buttons', []):
            btn.setEnabled(can_redo)

    def _restore_state(self, state: dict):
        self._is_undoing_redoing = True
        try:
            self.txt_title.setText(state.get("title", ""))

            idx_g = self.combo_goal.findData(state.get("goal"))
            if idx_g >= 0: self.combo_goal.setCurrentIndex(idx_g)

            pattern = state.get("days_pattern", "7_days")
            idx_d = self.combo_days.findData(pattern)
            if idx_d >= 0 and self.combo_days.currentIndex() != idx_d:
                self.combo_days.blockSignals(True)
                self.combo_days.setCurrentIndex(idx_d)
                self.combo_days.blockSignals(False)
                self.setup_meal_tabs()

            self.spin_cal.setValue(state.get("cal", 2000.0))
            self.spin_protein.setValue(state.get("protein", 150.0))
            self.spin_carbs.setValue(state.get("carbs", 200.0))
            self.spin_fat.setValue(state.get("fat", 60.0))
            self.update_macro_calculations()

            foods_list = NutritionService.get_all_foods()
            meal_state_map = {m["meal_key"]: m["items"] for m in state.get("meals", [])}

            for meal_key, table in self.meal_tables:
                if meal_key in meal_state_map:
                    table.setRowCount(0)
                    for itm in meal_state_map[meal_key]:
                        r = table.rowCount()
                        table.insertRow(r)
                        self._create_food_row_widgets(table, r, foods_list, itm)

            tab_idx = state.get("tab_index", 0)
            if 0 <= tab_idx < self.tabs.count():
                self.tabs.setCurrentIndex(tab_idx)
        finally:
            self._is_undoing_redoing = False

    def _create_food_row_widgets(self, table: QTableWidget, row: int, foods_list: list, data: dict = None):
        if not data:
            data = {}
        combo_food = SearchableComboBox(placeholder="جستجو یا تایپ نام ماده غذایی...")
        for f in foods_list:
            combo_food.addItem(f"{f.name_fa} ({f.unit} - {int(f.calories)}kcal)", f.id)

        f_id = data.get("food_id")
        if f_id:
            idx_f = combo_food.findData(f_id)
            if idx_f >= 0:
                combo_food.setCurrentIndex(idx_f)
            else:
                combo_food.set_empty()
        elif data.get("food_text"):
            combo_food.setCurrentText(data["food_text"])
        else:
            combo_food.set_empty()

        txt_amount = QLineEdit(str(data.get("amount", "1.0")))
        txt_amount.setAlignment(Qt.AlignmentFlag.AlignCenter)

        txt_notes = QLineEdit(str(data.get("notes", "")))
        txt_notes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt_notes.setPlaceholderText("توضیحات اختصاصی...")

        btn_del = QPushButton("🗑️")
        btn_del.setObjectName("danger_button")
        btn_del.setToolTip("حذف ماده غذایی")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda _, t=table, b=btn_del: self.remove_food_row(t, b))

        # Connect listeners to snapshot undo
        combo_food.currentIndexChanged.connect(lambda: self._snapshot_change())
        txt_amount.textEdited.connect(lambda: self._snapshot_change())
        txt_notes.textEdited.connect(lambda: self._snapshot_change())

        table.setCellWidget(row, 0, combo_food)
        table.setCellWidget(row, 1, txt_amount)
        table.setCellWidget(row, 2, txt_notes)
        table.setCellWidget(row, 3, btn_del)

    def add_food_row(self, table: QTableWidget, foods_list: list = None):
        row = table.rowCount()
        table.insertRow(row)
        if not foods_list:
            foods_list = NutritionService.get_all_foods()
        self._create_food_row_widgets(table, row, foods_list)
        self._snapshot_change()

    def remove_food_row(self, table: QTableWidget, btn: QPushButton):
        for r in range(table.rowCount()):
            if table.cellWidget(r, 3) == btn:
                table.removeRow(r)
                break
        self._snapshot_change()

    def _create_meal_widget(self, meal_key: str, meal_title: str, foods_list: list) -> QWidget:
        widget = QWidget()
        layout_meal = QVBoxLayout(widget)
        layout_meal.setContentsMargins(8, 8, 8, 8)
        layout_meal.setSpacing(10)

        row_top = QHBoxLayout()
        btn_undo = QPushButton("↩️ Undo")
        btn_undo.setObjectName("undo_button")
        btn_undo.setToolTip("بازگشت به مرحله قبل (Ctrl+Z)")
        btn_undo.clicked.connect(self.undo)

        btn_redo = QPushButton("↪️ Redo")
        btn_redo.setObjectName("redo_button")
        btn_redo.setToolTip("انجام مجدد مرحله بعد (Ctrl+Y)")
        btn_redo.clicked.connect(self.redo)

        self._undo_buttons.append(btn_undo)
        self._redo_buttons.append(btn_redo)

        btn_add_item = QPushButton("➕ افزودن ماده غذایی")
        btn_add_item.setObjectName("secondary_button")

        row_top.addStretch()
        row_top.addWidget(btn_undo)
        row_top.addWidget(btn_redo)
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

    def setup_meal_tabs(self):
        self.tabs.clear()
        self.meal_tables.clear()
        self._undo_buttons.clear()
        self._redo_buttons.clear()
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

        self._update_undo_redo_ui()

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

    def revert_changes(self):
        if self.editing_plan_id:
            self.load_plan_for_edit(self.editing_plan_id)
            QMessageBox.information(self, "بازنشانی", "تغییرات لغو شد و برنامه غذایی به حالت ذخیره‌شده اولیه بازگشت.")
        else:
            self.reset_form()
            QMessageBox.information(self, "بازنشانی", "فرم برنامه غذایی بازنشانی شد.")

    def reset_form(self):
        self.editing_plan_id = None
        self.lbl_header_title.setText("🥗 برنامه‌ریزی تغذیه")
        self._do_reset_fields()
        self.combo_templates.blockSignals(True)
        if self.combo_templates.count() > 0:
            self.combo_templates.setCurrentIndex(0)
        self.combo_templates.blockSignals(False)
        self.setup_meal_tabs()
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._last_state = self._capture_state()
        self._update_undo_redo_ui()

    def load_plan_for_edit(self, plan_id: int):
        self.editing_plan_id = plan_id
        plan = NutritionService.get_plan_by_id(plan_id)
        if plan:
            self.lbl_header_title.setText(f"✏️ ویرایش الگوی غذایی: {plan.title}")
            self._load_plan_data_to_form(plan)

    def assign_plan(self):
        member_id = self.combo_member.currentData()
        if not member_id:
            QMessageBox.warning(self, "خطا", "لطفاً یک ورزشکار را جهت تخصیص انتخاب کنید.")
            return

        plan_info, meals_data = self.get_plan_data()
        plan = NutritionService.create_nutrition_plan(plan_info, meals_data)
        NutritionService.assign_nutrition_plan(member_id, plan.id)
        QMessageBox.information(self, "موفقیت", "برنامه غذایی با موفقیت به ورزشکار تخصیص یافت.")
        self.reset_form()

    def open_food_bank(self):
        from yalda.views.food_library_dialog import FoodLibraryDialog
        dlg = FoodLibraryDialog(self)
        dlg.exec()
        self.setup_meal_tabs()
