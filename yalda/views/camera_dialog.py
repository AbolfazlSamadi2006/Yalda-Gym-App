import os
import tempfile
import time
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap



class CameraCaptureDialog(QDialog):
    """
    Dialog for live laptop/webcam camera stream (up to 60 FPS) and snapshot capture.
    """
    def __init__(self, parent=None, title="ثبت تصویر با دوربین"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedSize(700, 580)

        self.cap = None
        self.timer = QTimer(self)
        self.timer.setInterval(16)  # ~60 FPS update rate
        self.timer.timeout.connect(self.update_frame)

        self.current_frame_rgb = None
        self.captured_bgr_frame = None
        self.captured_file_path = None
        self.active_cam_index = 0

        self.init_ui()
        self.detect_and_start_camera()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header bar (Camera selector)
        header_layout = QHBoxLayout()
        lbl_cam = QLabel("انتخاب دوربین:")
        lbl_cam.setStyleSheet("font-weight: bold;")
        
        self.combo_cam = QComboBox()
        self.combo_cam.setMinimumWidth(160)
        self.combo_cam.currentIndexChanged.connect(self.on_camera_selected)

        self.chk_flip = QCheckBox("تصویر واقعی (غیرآینه‌ای)")
        self.chk_flip.setChecked(True)
        self.chk_flip.setStyleSheet("font-size: 13px;")

        header_layout.addWidget(lbl_cam)
        header_layout.addWidget(self.combo_cam)
        header_layout.addSpacing(20)
        header_layout.addWidget(self.chk_flip)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Live Video Preview Display Area
        self.lbl_video = QLabel("در حال اتصال به دوربین...")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_video.setFixedSize(670, 440)
        self.lbl_video.setStyleSheet(
            "background-color: #1a1a1a; color: #aaaaaa; border: 2px solid #333333; border-radius: 10px; font-size: 14px;"
        )
        layout.addWidget(self.lbl_video)

        # Control Buttons Row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_capture = QPushButton("📸 ثبت عکس")
        self.btn_capture.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 18px; background-color: #0088cc; color: white; border-radius: 6px;"
        )
        self.btn_capture.clicked.connect(self.take_snapshot)

        self.btn_retake = QPushButton("🔄 عکس مجدد")
        self.btn_retake.setObjectName("secondary_button")
        self.btn_retake.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 18px; background-color: #555555; color: white; border-radius: 6px;"
        )
        self.btn_retake.clicked.connect(self.resume_camera_stream)
        self.btn_retake.hide()

        self.btn_confirm = QPushButton("✅ تایید و استفاده")
        self.btn_confirm.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 8px 18px; background-color: #2e7d32; color: white; border-radius: 6px;"
        )
        self.btn_confirm.clicked.connect(self.confirm_snapshot)
        self.btn_confirm.hide()

        self.btn_cancel = QPushButton("انصراف")
        self.btn_cancel.setObjectName("secondary_button")
        self.btn_cancel.setStyleSheet(
            "font-size: 14px; padding: 8px 16px; border-radius: 6px;"
        )
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_capture)
        btn_layout.addWidget(self.btn_retake)
        btn_layout.addWidget(self.btn_confirm)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def populate_cameras(self):
        """Scan available video devices and open index 0."""
        import cv2
        self.combo_cam.blockSignals(True)
        self.combo_cam.clear()
        
        # Quick check for index 0 and 1
        available = []
        for i in range(3):
            temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
            if temp_cap.isOpened():
                available.append(i)
                temp_cap.release()

        if not available:
            # Fallback to index 0 anyway
            available = [0]

        for cam_id in available:
            self.combo_cam.addItem(f"دوربین {cam_id + 1}", cam_id)

        self.combo_cam.blockSignals(False)
        self.open_camera(available[0])

    def open_camera(self, cam_index: int):
        import cv2
        self.stop_camera()
        self.active_cam_index = cam_index

        # Open video capture with DirectShow backend for fast initialization on Windows
        if os.name == 'nt':
            self.cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(cam_index)

        if self.cap and self.cap.isOpened():
            # Attempt to request 60 FPS and 720p HD stream
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 60)
            self.timer.start()
        else:
            self.lbl_video.setText("❌ هیچ دوربینی یافت نشد یا دوربین توسط برنامه دیگری در حال استفاده است.")

    def on_camera_selected(self, index: int):
        cam_id = self.combo_cam.currentData()
        if cam_id is not None:
            self.open_camera(cam_id)

    def update_frame(self):
        import cv2
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()

            if ret and frame is not None:
                if self.chk_flip.isChecked():
                    frame = cv2.flip(frame, 1)

                self.captured_bgr_frame = frame.copy()
                
                # BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame_rgb = rgb_frame

                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                pixmap = QPixmap.fromImage(qimg)
                scaled_pixmap = pixmap.scaled(
                    self.lbl_video.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_video.setPixmap(scaled_pixmap)

    def take_snapshot(self):
        if self.captured_bgr_frame is not None:
            self.timer.stop()
            self.btn_capture.hide()
            self.btn_retake.show()
            self.btn_confirm.show()

    def resume_camera_stream(self):
        self.btn_retake.hide()
        self.btn_confirm.hide()
        self.btn_capture.show()
        if self.cap and self.cap.isOpened():
            self.timer.start()

    def confirm_snapshot(self):
        if self.captured_bgr_frame is not None:
            # Save frame to a temporary file
            temp_dir = tempfile.gettempdir()
            filename = f"cam_snapshot_{int(time.time())}.jpg"
            save_path = os.path.join(temp_dir, filename)
            
            # Save image using OpenCV
            cv2.imwrite(save_path, self.captured_bgr_frame)
            
            self.captured_file_path = save_path
            self.stop_camera()
            self.accept()

    def stop_camera(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)

    def reject(self):
        self.stop_camera()
        super().reject()
