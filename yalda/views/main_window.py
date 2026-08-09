from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import config
from yalda.views.components.sidebar import Sidebar
from yalda.views.dashboard_view import DashboardView
from yalda.views.member_list_view import MemberListView
from yalda.views.member_detail_view import MemberDetailView
from yalda.views.workout_editor_view import WorkoutEditorView
from yalda.views.nutrition_editor_view import NutritionEditorView
from yalda.views.workout_library_view import WorkoutLibraryView
from yalda.views.food_library_view import FoodLibraryView
from yalda.views.backup_view import BackupView
from yalda.auth.authentication import CurrentUser

class MainWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{config.APP_NAME} - نرم‌افزار مدیریت باشگاه بدنسازی (نسخه ۱.۱.۱)")

        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.resize(1280, 800)
        self.setMinimumSize(1024, 700)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.switch_page)
        self.sidebar.logout_requested.connect(self.logout)
        self.sidebar.member_birthday_clicked.connect(self.open_member_detail)
        main_layout.addWidget(self.sidebar)


        # Stacked Container for Views
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Instantiate Views
        self.view_dashboard = DashboardView()
        self.view_dashboard.navigate_to.connect(self.handle_dashboard_navigation)

        self.view_members = MemberListView()
        self.view_members.open_member_detail.connect(self.open_member_detail)

        self.view_workouts = WorkoutEditorView()
        self.view_nutrition = NutritionEditorView()
        self.view_exercises = WorkoutLibraryView()
        self.view_foods = FoodLibraryView()
        self.view_backup = BackupView()

        self.stack.addWidget(self.view_dashboard) # Index 0
        self.stack.addWidget(self.view_members)   # Index 1
        self.stack.addWidget(self.view_workouts)  # Index 2
        self.stack.addWidget(self.view_nutrition) # Index 3
        self.stack.addWidget(self.view_exercises) # Index 4
        self.stack.addWidget(self.view_foods)     # Index 5
        self.stack.addWidget(self.view_backup)    # Index 6

    def switch_page(self, page_id: str):
        self.sidebar.refresh_notifications()
        page_map = {

            "dashboard": 0,
            "members": 1,
            "workouts": 2,
            "nutrition": 3,
            "exercises": 4,
            "foods": 5,
            "backup": 6
        }
        if page_id in page_map:
            if page_id == "dashboard":
                self.view_dashboard.refresh_dashboard()
            elif page_id == "members":
                self.view_members.load_members()
            elif page_id == "workouts":
                self.view_workouts.refresh_editor()
            elif page_id == "nutrition":
                self.view_nutrition.refresh_editor()
            elif page_id == "exercises":
                self.view_exercises.load_exercises()
            elif page_id == "foods":
                self.view_foods.load_foods()
            elif page_id == "backup":
                self.view_backup.load_backups()
            self.stack.setCurrentIndex(page_map[page_id])

    def handle_dashboard_navigation(self, target: str):
        if target == "add_member":
            self.sidebar.navigate("members")
            self.view_members.open_add_dialog()
        elif target == "new_workout":
            self.sidebar.navigate("workouts")
        elif target == "new_nutrition":
            self.sidebar.navigate("nutrition")

    def open_member_detail(self, member_id: int):
        detail_view = MemberDetailView(member_id)
        detail_view.back_requested.connect(lambda: self.sidebar.navigate("members"))
        idx = self.stack.addWidget(detail_view)
        self.stack.setCurrentIndex(idx)

    def logout(self):
        reply = QMessageBox.question(
            self, "خروج از حساب", "آیا مایل به خروج از حساب کاربری هستید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            CurrentUser.logout()
            self.logout_signal.emit()
            self.hide()
