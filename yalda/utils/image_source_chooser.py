from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt


class ImageSourceChoiceDialog(QDialog):
    """
    A small dialog prompting the user to choose between selecting a file from system
    or capturing a new photo with the camera.
    """
    def __init__(self, parent=None, title="انتخاب روش افزودن تصویر"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(360, 180)
        self.selected_choice = None  # 'file' or 'camera'

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("لطفاً نحوه افزودن تصویر را انتخاب کنید:")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_file = QPushButton("📁 انتخاب از سیستم")
        btn_file.setStyleSheet(
            "font-size: 13px; padding: 10px; background-color: #0088cc; color: white; border-radius: 6px; font-weight: bold;"
        )
        btn_file.clicked.connect(self.on_choose_file)

        btn_cam = QPushButton("📷 عکس با دوربین")
        btn_cam.setStyleSheet(
            "font-size: 13px; padding: 10px; background-color: #2e7d32; color: white; border-radius: 6px; font-weight: bold;"
        )
        btn_cam.clicked.connect(self.on_choose_camera)

        btn_layout.addWidget(btn_file)
        btn_layout.addWidget(btn_cam)
        layout.addLayout(btn_layout)

        btn_cancel = QPushButton("انصراف")
        btn_cancel.setObjectName("secondary_button")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def on_choose_file(self):
        self.selected_choice = 'file'
        self.accept()

    def on_choose_camera(self):
        self.selected_choice = 'camera'
        self.accept()


def get_image_file_path(parent, dialog_title="افزودن تصویر", file_filter="تصاویر (*.png *.jpg *.jpeg *.bmp)"):
    """
    Prompt user for source choice ('file' or 'camera').
    If 'file', opens QFileDialog.
    If 'camera', opens CameraCaptureDialog.
    Returns selected/captured filepath or None.
    """
    from PyQt6.QtWidgets import QFileDialog
    from yalda.views.camera_dialog import CameraCaptureDialog

    choice_dlg = ImageSourceChoiceDialog(parent, title=dialog_title)
    if choice_dlg.exec() == QDialog.DialogCode.Accepted:
        choice = choice_dlg.selected_choice
        if choice == 'file':
            file_path, _ = QFileDialog.getOpenFileName(parent, dialog_title, "", file_filter)
            return file_path if file_path else None
        elif choice == 'camera':
            cam_dlg = CameraCaptureDialog(parent, title=dialog_title)
            if cam_dlg.exec() == QDialog.DialogCode.Accepted:
                return cam_dlg.captured_file_path
    return None
