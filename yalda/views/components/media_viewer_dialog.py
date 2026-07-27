import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import Qt, QUrl

class MediaViewerDialog(QDialog):
    """
    Dialog for displaying exercise media (images and videos).
    """
    def __init__(self, title: str, media_path: str, media_type: str = "image", parent=None):
        super().__init__(parent)
        self.title_str = title
        self.media_path = media_path
        self.media_type = media_type or "image"

        self.setWindowTitle(f"رسانه آموزشی: {title}")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setMinimumSize(550, 480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        lbl_header = QLabel(f"🎬 نمایش فایل آموزشی: {self.title_str}")
        lbl_header.setObjectName("h2")
        lbl_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_header)

        if not self.media_path or not os.path.exists(self.media_path):
            lbl_no_file = QLabel("❌ هیچ فایل رسانه‌ای (عکس یا ویدیو) برای این حرکت ثبت نشده است یا فایل در مسیر مربوطه یافت نشد.")
            lbl_no_file.setStyleSheet("color: #FF6B6B; font-size: 14px; padding: 20px;")
            lbl_no_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_no_file.setWordWrap(True)
            layout.addWidget(lbl_no_file)
        else:
            ext = os.path.splitext(self.media_path)[1].lower()
            is_video = ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm'] or self.media_type == 'video'

            if not is_video:
                # Image Display
                lbl_image = QLabel()
                lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pixmap = QPixmap(self.media_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(500, 360, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    lbl_image.setPixmap(scaled_pixmap)
                    layout.addWidget(lbl_image)
                else:
                    lbl_err = QLabel("❌ امکان لود تصویر وجود ندارد (فرمت نامعتبر یا فایل آسیب‌دیده).")
                    lbl_err.setStyleSheet("color: #FF6B6B; font-size: 14px;")
                    lbl_err.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    layout.addWidget(lbl_err)
            else:
                # Video Player Option
                lbl_video_info = QLabel("🎥 این حرکت دارای ویدیو آموزشی است.\nجهت پخش ویدیو با پخش‌کننده ویدیویی سیستم روی دکمه زیر کلیک کنید:")
                lbl_video_info.setStyleSheet("font-size: 14px; color: #FFFFFF; line-height: 1.6;")
                lbl_video_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(lbl_video_info)

                btn_play = QPushButton("▶️ پخش ویدیو آموزشی حرکت")
                btn_play.setFixedHeight(45)
                btn_play.setStyleSheet("""
                    QPushButton {
                        background-color: #8B0000;
                        color: #FFFFFF;
                        font-weight: bold;
                        font-size: 15px;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #A00000;
                    }
                """)
                btn_play.clicked.connect(self.play_video)
                layout.addWidget(btn_play)

        btn_close = QPushButton("بستن")
        btn_close.setObjectName("secondary_button")
        btn_close.setFixedHeight(38)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def play_video(self):
        if self.media_path and os.path.exists(self.media_path):
            url = QUrl.fromLocalFile(self.media_path)
            QDesktopServices.openUrl(url)
        else:
            QMessageBox.warning(self, "خطا", "فایل ویدیو یافت نشد.")
