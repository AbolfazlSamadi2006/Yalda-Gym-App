from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PyQt6.QtCore import pyqtSignal, Qt
from yalda.services.member_service import MemberService
from yalda.views.member_form_dialog import MemberFormDialog

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
        self.combo_status.addItem("اعضای فعال", "active")
        self.combo_status.addItem("اعضای انقضا یافته", "expired")
        self.combo_status.addItem("اعضای آرشیو شده", "archived")
        self.combo_status.addItem("همه اعضا", "all")
        self.combo_status.currentIndexChanged.connect(self.load_members)

        controls.addWidget(QLabel("جستجو:"))
        controls.addWidget(self.txt_search)
        controls.addWidget(QLabel("وضعیت:"))
        controls.addWidget(self.combo_status)
        layout.addLayout(controls)

        # Members Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "کد", "نام و نام خانوادگی", "شماره تماس", "قد / وزن", "نوع عضویت", "تاریخ انقضا (شمسی)", "وضعیت", "عملیات"
        ])
        self.table.verticalHeader().setDefaultSectionSize(54)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 235)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        self.load_members()

    def load_members(self):
        search_query = self.txt_search.text().strip()
        status_filter = self.combo_status.currentData()
        members = MemberService.get_all_members(search_query=search_query, status_filter=status_filter)

        MEMBERSHIP_TYPE_MAP = {
            "12_sessions": "۱۲ جلسه در ماه",
            "8_sessions": "۸ جلسه در ماه",
            "16_sessions": "۱۶ جلسه در ماه",
            "20_sessions": "۲۰ جلسه در ماه",
            "daily_access": "دسترسی روزانه"
        }

        self.table.setRowCount(len(members))
        for row, m in enumerate(members):
            self.table.setItem(row, 0, QTableWidgetItem(str(m.id)))
            self.table.setItem(row, 1, QTableWidgetItem(m.full_name))
            self.table.setItem(row, 2, QTableWidgetItem(m.phone))
            self.table.setItem(row, 3, QTableWidgetItem(f"{int(m.height_cm or 0)}cm / {int(m.initial_weight_kg or 0)}kg"))
            m_type_fa = MEMBERSHIP_TYPE_MAP.get(m.membership_type, m.membership_type or "")
            self.table.setItem(row, 4, QTableWidgetItem(m_type_fa))
            self.table.setItem(row, 5, QTableWidgetItem(m.membership_expire_shamsi or ""))

            # Status Column
            status_map = {"active": "فعال", "expired": "انقضا یافته", "archived": "آرشیو شده"}
            status_item = QTableWidgetItem(status_map.get(m.status, m.status))
            if m.status == "active":
                status_item.setForeground(Qt.GlobalColor.green)
            elif m.status == "expired":
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 6, status_item)

            # Actions Button Widget (View File, Edit, Delete)
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(2, 4, 2, 4)
            btn_layout.setSpacing(4)

            btn_view = QPushButton("📋 پرونده")
            btn_view.setObjectName("secondary_button")
            btn_view.setStyleSheet("padding: 4px 6px; font-size: 11px; height: 32px;")
            btn_view.clicked.connect(lambda _, mid=m.id: self.open_member_detail.emit(mid))

            btn_edit = QPushButton("✏️ ویرایش")
            btn_edit.setStyleSheet("padding: 4px 6px; font-size: 11px; height: 32px;")
            btn_edit.clicked.connect(lambda _, member=m: self.open_edit_dialog(member))

            btn_delete = QPushButton("🗑️")
            btn_delete.setObjectName("danger_button")
            btn_delete.setToolTip("حذف پرونده ورزشکار")
            btn_delete.setStyleSheet("padding: 4px 6px; font-size: 12px; height: 32px; min-width: 32px;")
            btn_delete.clicked.connect(lambda _, member=m: self.delete_member(member))

            btn_layout.addWidget(btn_view)
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_delete)

            self.table.setCellWidget(row, 7, btn_container)

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
