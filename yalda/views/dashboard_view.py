from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from yalda.views.components.stat_card import StatCard
from yalda.services.member_service import MemberService
from yalda.services.workout_service import WorkoutService
from yalda.services.nutrition_service import NutritionService
from yalda.utils.jalali_date import days_until_expire, get_today_shamsi

class DashboardView(QWidget):
    navigate_to = pyqtSignal(str) # Emits target page name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title & Date
        header_layout = QHBoxLayout()
        title = QLabel("داشبورد مدیریتی باشگاه یلدا")
        title.setObjectName("h1")
        
        date_lbl = QLabel(f"تاریخ امروز: {get_today_shamsi()}")
        date_lbl.setStyleSheet("color: #8B0000; font-weight: bold; font-size: 14px;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(date_lbl)
        layout.addLayout(header_layout)

        # Stat Cards Grid Layout
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.card_members = StatCard("اعضای فعال", "0", "ورزشکار ثبت شده", "👥")
        self.card_expired = StatCard("عضویت‌های انقضا یافته", "0", "نیازمند تمدید", "⚠️")
        self.card_workouts = StatCard("برنامه‌های تمرینی", "0", "الگوی آماده", "🏋️")
        self.card_nutrition = StatCard("برنامه‌های غذایی", "0", "رژیم غذایی", "🥗")

        stats_layout.addWidget(self.card_members)
        stats_layout.addWidget(self.card_expired)
        stats_layout.addWidget(self.card_workouts)
        stats_layout.addWidget(self.card_nutrition)
        layout.addLayout(stats_layout)

        # Quick Actions Bar
        actions_frame = QFrame()
        actions_frame.setObjectName("card")
        actions_layout = QHBoxLayout(actions_frame)
        actions_layout.setContentsMargins(12, 12, 12, 12)

        lbl_quick = QLabel("دسترسی سریع:")
        lbl_quick.setStyleSheet("font-weight: bold; color: #FFFFFF; background: transparent;")

        btn_add_member = QPushButton("➕ ثبت عضو جدید")
        btn_add_member.clicked.connect(lambda: self.navigate_to.emit("add_member"))

        btn_new_workout = QPushButton("🏋️ ساخت برنامه تمرینی")
        btn_new_workout.setObjectName("secondary_button")
        btn_new_workout.clicked.connect(lambda: self.navigate_to.emit("new_workout"))

        btn_new_nutrition = QPushButton("🥗 ساخت برنامه غذایی")
        btn_new_nutrition.setObjectName("secondary_button")
        btn_new_nutrition.clicked.connect(lambda: self.navigate_to.emit("new_nutrition"))

        actions_layout.addWidget(lbl_quick)
        actions_layout.addWidget(btn_add_member)
        actions_layout.addWidget(btn_new_workout)
        actions_layout.addWidget(btn_new_nutrition)
        actions_layout.addStretch()

        layout.addWidget(actions_frame)

        # All Members Table
        table_title = QLabel("📋 لیست کلیه ورزشکاران و وضعیت انقضای عضویت")
        table_title.setObjectName("h2")
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["نام و نام خانوادگی", "مربی مربوطه", "شماره تماس", "نوع عضویت", "تاریخ انقضا (شمسی)", "وضعیت"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        
        # Initial Data Refresh
        self.refresh_dashboard()

    def refresh_dashboard(self):
        members = MemberService.get_all_members(status_filter="all")
        active_count = sum(1 for m in members if m.status == "active" and (not m.membership_expire_shamsi or days_until_expire(m.membership_expire_shamsi) >= 0))
        expired_count = sum(1 for m in members if m.status == "expired" or (m.membership_expire_shamsi and days_until_expire(m.membership_expire_shamsi) < 0))

        workouts_count = len(WorkoutService.get_all_plans())
        nutrition_count = len(NutritionService.get_all_plans())

        self.card_members.set_value(str(active_count))
        self.card_expired.set_value(str(expired_count))
        self.card_workouts.set_value(str(workouts_count))
        self.card_nutrition.set_value(str(nutrition_count))
        
        # Populate All Members Table
        self.table.setRowCount(len(members))

        MEMBERSHIP_TYPE_MAP = {
            "12_sessions": "۱۲ جلسه در ماه",
            "8_sessions": "۸ جلسه در ماه",
            "16_sessions": "۱۶ جلسه در ماه",
            "20_sessions": "۲۰ جلسه در ماه",
            "daily_access": "دسترسی روزانه"
        }

        for row, m in enumerate(members):
            self.table.setItem(row, 0, QTableWidgetItem(m.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(m.trainer_name))
            self.table.setItem(row, 2, QTableWidgetItem(m.phone))
            m_type_fa = MEMBERSHIP_TYPE_MAP.get(m.membership_type, m.membership_type or "")
            self.table.setItem(row, 3, QTableWidgetItem(m_type_fa))
            self.table.setItem(row, 4, QTableWidgetItem(m.membership_expire_shamsi or ""))
            
            days_left = days_until_expire(m.membership_expire_shamsi)
            if m.status == "archived":
                status_text = "آرشیو شده"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(Qt.GlobalColor.gray)
            elif days_left < 0 or m.status == "expired":
                status_text = "انقضا یافته"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(Qt.GlobalColor.red)
            elif 0 <= days_left <= 5:
                status_text = f"در آستانه انقضا ({days_left} روز)"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(Qt.GlobalColor.yellow)
            else:
                status_text = f"فعال ({days_left} روز باقی‌مانده)"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(Qt.GlobalColor.green)

            self.table.setItem(row, 5, status_item)

