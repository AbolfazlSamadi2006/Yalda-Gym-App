import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from yalda.services.member_service import MemberService
from yalda.views.member_form_dialog import MemberFormDialog
from yalda.utils.image_utils import get_circular_pixmap
from yalda.views.components.circular_image_preview_dialog import CircularImagePreviewDialog

class MemberListView(QWidget):
    open_member_detail = pyqtSignal(int) # Member ID

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title & Add Button
        header = QHBoxLayout()
        title = QLabel("👥 مدیریت اعضای باشگاه")
        title.setObjectName("h1")

        btn_add = QPushButton("➕ ثبت ورزشکار جدید")
        btn_add.clicked.connect(self.open_add_dialog)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(btn_add)
        layout.addLayout(header)

        # Search & Filter Controls Bar
        controls = QHBoxLayout()
        
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("جستجو بر اساس نام یا شماره تلفن...")
        self.txt_search.textChanged.connect(self.load_members)

        self.combo_status = QComboBox()
        self.combo_status.addItem("همه اعضا", "all")
        self.combo_status.addItem("اعضای فعال", "active")
        self.combo_status.addItem("اعضای انقضا یافته", "expired")
        self.combo_status.addItem("اعضای آرشیو شده", "archived")
        self.combo_status.currentIndexChanged.connect(self.load_members)

        controls.addWidget(QLabel("جستجو:"))
        controls.addWidget(self.txt_search)
        controls.addWidget(QLabel("وضعیت:"))
        controls.addWidget(self.combo_status)
        layout.addLayout(controls)

        # Members Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ورزشکار", "مربی مربوطه", "شماره تماس", "نوع عضویت", "تاریخ انقضا (شمسی)", "وضعیت", "عملیات"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(52)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 230)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        self.load_members()

    def open_avatar_preview(self, photo_path: str, member_name: str):
        """Opens a circular animated popup zoom of athlete's photo."""
        if photo_path and os.path.exists(photo_path):
            dlg = CircularImagePreviewDialog(photo_path, title=member_name, parent=self)
            dlg.exec()

    def load_members(self):
        search_query = self.txt_search.text().strip()
        status_filter = self.combo_status.currentData()
        members = MemberService.get_all_members(search_query=search_query, status_filter=status_filter)

        MEMBERSHIP_TYPE_MAP = {
            "12_sessions": "۱۲ جلسه در ماه",
            "8_sessions": "۸ جلسه در ماه",
            "16_sessions": "۱۶ جلسه در ماه",
            "20_sessions": "۲۰ جلسه در ماه",
            "daily_access": "همه روزه"
        }

        self.table.setRowCount(len(members))
        for row, m in enumerate(members):
            # Column 0: Circular Avatar + Name
            cell_w = QWidget()
            cell_w.setStyleSheet("background: transparent;")
            cell_l = QHBoxLayout(cell_w)
            cell_l.setContentsMargins(8, 3, 8, 3)
            cell_l.setSpacing(10)
            cell_l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            lbl_avatar = QLabel()
            lbl_avatar.setFixedSize(36, 36)
            lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

            has_valid_photo = False
            if m.photo_path and os.path.exists(m.photo_path):
                pix = QPixmap(m.photo_path)
                if not pix.isNull():
                    circ_pix = get_circular_pixmap(pix, 36, border_color="#8B0000", border_width=2)
                    lbl_avatar.setPixmap(circ_pix)
                    lbl_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
                    lbl_avatar.setToolTip(f"برای مشاهده تصویر بزرگ‌تر «{m.full_name}» کلیک کنید")
                    lbl_avatar.mousePressEvent = lambda e, p=m.photo_path, n=m.full_name: self.open_avatar_preview(p, n)
                    has_valid_photo = True

            if not has_valid_photo:
                lbl_avatar.setText("👤")
                lbl_avatar.setStyleSheet("""
                    QLabel {
                        background-color: #242424;
                        border: 1px solid #444444;
                        border-radius: 18px;
                        color: #777777;
                        font-size: 16px;
                    }
                """)

            lbl_name = QLabel(m.full_name)
            lbl_name.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: bold; background: transparent;")

            cell_l.addWidget(lbl_avatar)
            cell_l.addWidget(lbl_name)
            cell_l.addStretch()

            self.table.setCellWidget(row, 0, cell_w)

            # Column 1: Trainer
            item_trainer = QTableWidgetItem(m.trainer_name or "-")
            item_trainer.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item_trainer)

            # Column 2: Phone
            item_phone = QTableWidgetItem(m.phone or "-")
            item_phone.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_phone)

            # Column 3: Membership Type
            m_type_fa = MEMBERSHIP_TYPE_MAP.get(m.membership_type, m.membership_type or "-")
            item_type = QTableWidgetItem(m_type_fa)
            item_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_type)

            # Column 4: Expiration Date
            item_exp = QTableWidgetItem(m.membership_expire_shamsi or "-")
            item_exp.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 4, item_exp)

            # Column 5: Status
            status_map = {"active": "فعال 🟢", "expired": "انقضا یافته 🔴", "archived": "آرشیو شده ⚪"}
            status_text = status_map.get(m.status, m.status)
            status_item = QTableWidgetItem(status_text)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if m.status == "active":
                status_item.setForeground(Qt.GlobalColor.green)
            elif m.status == "expired":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, status_item)

            # Column 6: Actions Button Widget (Index 6: View File, Edit, Delete)
            btn_container = QWidget()
            btn_container.setStyleSheet("background: transparent;")
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn_layout.setSpacing(6)

            btn_view = QPushButton("📋 پرونده")
            btn_view.setFixedHeight(30)
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 4px 10px; font-size: 12px;
                }
                QPushButton:hover { background-color: #1D4ED8; }
            """)
            btn_view.clicked.connect(lambda _, mid=m.id: self.open_member_detail.emit(mid))

            btn_edit = QPushButton("✏️ ویرایش")
            btn_edit.setFixedHeight(30)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #D97706; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 4px 10px; font-size: 12px;
                }
                QPushButton:hover { background-color: #B45309; }
            """)
            btn_edit.clicked.connect(lambda _, member=m: self.open_edit_dialog(member))

            btn_delete = QPushButton("🗑️ حذف")
            btn_delete.setFixedHeight(30)
            btn_delete.setToolTip("حذف پرونده ورزشکار")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #DC2626; color: #FFFFFF; font-weight: bold; border-radius: 6px; padding: 4px 10px; font-size: 12px;
                }
                QPushButton:hover { background-color: #B91C1C; }
            """)
            btn_delete.clicked.connect(lambda _, member=m: self.delete_member(member))

            btn_layout.addWidget(btn_view)
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)

            self.table.setCellWidget(row, 6, btn_container)

    def delete_member(self, member):
        reply = QMessageBox.question(
            self, "تایید حذف ورزشکار",
            f"آیا از حذف کامل پرونده ورزشکار '{member.full_name}' اطمینان دارید؟ تمام سوابق پزشکی و برنامه‌های وی نیز پاک خواهد شد.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            MemberService.delete_member(member.id)
            self.load_members()
            QMessageBox.information(self, "موفقیت", "پرونده ورزشکار با موفقیت حذف گردید.")

    def open_add_dialog(self):
        try:
            dialog = MemberFormDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_members()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطایی رخ داد: {str(e)}")

    def open_edit_dialog(self, member):
        try:
            dialog = MemberFormDialog(self, member_data=member)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_members()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطایی رخ داد: {str(e)}")

