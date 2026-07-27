import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import config
from yalda.database.connection import init_db
from yalda.views.login_view import LoginView
from yalda.views.main_window import MainWindow

class YaldaApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(config.APP_NAME)
        self.app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        # Initialize Database
        init_db()

        # Load Dark Red & Black QSS Theme
        self.load_stylesheet()

        # Windows setup
        self.login_view = LoginView()
        self.main_window = None

        self.login_view.login_success.connect(self.on_login_success)

    def load_stylesheet(self):
        qss_path = config.BASE_DIR / "resources" / "qss" / "dark_theme.qss"
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                content = f.read()
                arrow_down_path = (config.BASE_DIR / "resources" / "images" / "arrow_down.svg").as_posix()
                arrow_up_path = (config.BASE_DIR / "resources" / "images" / "arrow_up.svg").as_posix()
                content = content.replace("resources/images/arrow_down.svg", arrow_down_path)
                content = content.replace("resources/images/arrow_up.svg", arrow_up_path)
                self.app.setStyleSheet(content)

    def run(self):
        self.login_view.showMaximized()
        return self.app.exec()

    def on_login_success(self):
        self.login_view.hide()
        if not self.main_window:
            self.main_window = MainWindow()
            self.main_window.logout_signal.connect(self.on_logout)
        self.main_window.showMaximized()

    def on_logout(self):
        from yalda.auth.authentication import CurrentUser
        CurrentUser.logout()
        if self.main_window:
            self.main_window.hide()
        self.login_view.txt_username.clear()
        self.login_view.txt_password.clear()
        self.login_view.showMaximized()
