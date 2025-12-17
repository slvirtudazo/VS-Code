# curatel_lms/ui/patron_management.py

# Manages library member records with search, filtering, sorting, status indicators, and CRUD actions

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from curatel_lms.config import AppConfig
from curatel_lms.ui.patron_dialogs import (
    AddMemberDialog, ViewMemberDialog, UpdateMemberDialog, 
    ConfirmDeleteMemberDialog
)

class PatronManagement(QWidget):
    # Main widget for managing library members: displays sortable/filterable table,
    # supports CRUD via modal dialogs, tracks selection, and uses db for data.
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.all_members = []
        self.selected_member_id = None
        self.sort_column = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        try:
            self._setup_ui()
            self._load_members_from_database()
        except Exception as e:
            print(f"[ERROR] Failed to setup Patron Management: {e}")
            import traceback
            traceback.print_exc()
            self._show_critical("Initialization Error", f"Failed to initialize Patron Management:\n{str(e)}")

    def _setup_ui(self):
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        main_layout.addLayout(self._create_header())
        main_layout.addLayout(self._create_search_section())
        main_layout.addSpacing(5)
        main_layout.addWidget(self._create_members_table())
        main_layout.addSpacing(5)
        main_layout.addLayout(self._create_action_buttons())

    def mousePressEvent(self, event):
        self._clear_selection(event)
        super().mousePressEvent(event)

    def _create_header(self):
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        title = QLabel("Patron Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
        header_text.addWidget(title)
        subtitle = QLabel("Manage member records, status, and registration details")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet(f"color: {AppConfig.COLORS['text_gray']};")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        return header_layout

    def _create_search_section(self):
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by id, name, email, or mobile number"
        )
        self.search_input.setStyleSheet(AppConfig.STYLES['search_input'])
        self.search_input.setFixedHeight(AppConfig.SEARCH_HEIGHT)
        self.search_input.textChanged.connect(self._filter_members)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        search_layout.addWidget(self._create_filter_label("Status"))
        self.status_combo = self._create_filter_combo(
            ["All", "Active", "Inactive"]
        )
        search_layout.addWidget(self.status_combo)
        return search_layout

    def _create_filter_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Montserrat", 10))
        label.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
        return label

    def _create_filter_combo(self, items):
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(AppConfig.STYLES['combo'])
        combo.setFixedSize(120, AppConfig.SEARCH_HEIGHT)
        combo.currentTextChanged.connect(self._filter_members)
        return combo

    def _create_members_table(self):
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(
            len(AppConfig.PATRON_TABLE['columns'])
        )
        self.members_table.setSortingEnabled(False)
        self.members_table.setHorizontalHeaderLabels(
            AppConfig.PATRON_TABLE['columns']
        )
        self.members_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.members_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.members_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.members_table.setAlternatingRowColors(True)
        self.members_table.setStyleSheet(AppConfig.STYLES['table_with_corner'])
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self._handle_header_click)
        for col, width in enumerate(AppConfig.PATRON_TABLE['widths']):
            self.members_table.setColumnWidth(col, width)
        self.members_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed
        )
        self.members_table.verticalHeader().setVisible(False)
        self.members_table.setHorizontalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )
        self.members_table.setVerticalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )
        self.members_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.members_table.itemSelectionChanged.connect(
            self._on_selection_changed
        )
        return self.members_table

    def _create_action_buttons(self):
        action_layout = QHBoxLayout()
        button_configs = [
            ("Add Member", self._add_member, AppConfig.BUTTON_WIDTH_STANDARD),
            ("View Member", self._view_member, AppConfig.BUTTON_WIDTH_STANDARD),
            ("Update Member", self._update_member, AppConfig.BUTTON_WIDTH_MEDIUM),
            ("Delete Member", self._delete_member, AppConfig.BUTTON_WIDTH_MEDIUM)
        ]
        for text, callback, width in button_configs:
            btn = self._create_action_button(text, callback, width)
            action_layout.addWidget(btn)
        action_layout.addStretch()
        return action_layout

    def _create_action_button(self, text, callback, width=None):
        btn = QPushButton(text)
        btn.setFont(QFont("Montserrat", 10))
        button_width = width if width else AppConfig.BUTTON_WIDTH_STANDARD
        btn.setFixedSize(button_width, AppConfig.BUTTON_HEIGHT)
        btn.setStyleSheet(AppConfig.STYLES['button'])
        btn.clicked.connect(callback)
        return btn

    def _on_selection_changed(self):
        try:
            selected_row = self.members_table.currentRow()
            if selected_row >= 0:
                self.selected_member_id = self.members_table.item(
                    selected_row, 0
                ).text()
            else:
                self.selected_member_id = None
        except Exception as e:
            print(f"[ERROR] Selection change failed: {e}")
            self.selected_member_id = None

    def _clear_selection(self, event):
        try:
            if hasattr(self, 'members_table') and self.members_table:
                self.members_table.clearSelection()
                self.selected_member_id = None
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] Clear selection error: {e}")

    def _handle_header_click(self, logical_index):
        try:
            if self.sort_column == logical_index:
                self.sort_order = (
                    Qt.SortOrder.DescendingOrder
                    if self.sort_order == Qt.SortOrder.AscendingOrder
                    else Qt.SortOrder.AscendingOrder
                )
            else:
                self.sort_column = logical_index
                self.sort_order = Qt.SortOrder.AscendingOrder
            self._filter_members()
        except Exception as e:
            print(f"[ERROR] Header click failed: {e}")
            self._show_warning("Sort Error", "Failed to sort table")

    def _load_members_from_database(self):
        if not self._validate_database_connection():
            return
        try:
            query = "SELECT * FROM members ORDER BY member_id"
            self.all_members = self.db.fetch_all(query)
            if self.all_members:
                print(f"[OK] Loaded {len(self.all_members)} members")
                self._filter_members()
            else:
                print("[WARNING] No members found in database")
                self.members_table.setRowCount(0)
        except Exception as e:
            print(f"[ERROR] Failed to load members: {e}")
            import traceback
            traceback.print_exc()
            self._show_critical("Database Error", f"Failed to load members from database:\n{str(e)}")

    def _display_members(self, members):
        try:
            self.members_table.setRowCount(len(members))
            for row, member in enumerate(members):
                for col, key in enumerate(AppConfig.PATRON_TABLE['keys']):
                    value = str(member.get(key, ''))
                    item = self._create_table_item(value)
                    if col == 4:
                        color = (
                            AppConfig.COLORS['status_active']
                            if member['status'] == 'Active'
                            else AppConfig.COLORS['status_inactive']
                        )
                        item.setForeground(QColor(color))
                    self.members_table.setItem(row, col, item)
        except Exception as e:
            print(f"[ERROR] Display members failed: {e}")
            import traceback
            traceback.print_exc()

    def _create_table_item(self, text):
        item = QTableWidgetItem(text)
        item.setFont(QFont("Montserrat", 10))
        item.setForeground(QColor(AppConfig.COLORS['text_dark']))
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        return item

    def _filter_members(self):
        try:
            if not self.all_members:
                return
            search_text = self.search_input.text().lower().strip()
            status = self.status_combo.currentText()
            filtered_members = [
                member for member in self.all_members
                if self._member_matches_filters(member, search_text, status)
            ]
            if self.sort_column is not None and filtered_members:
                filtered_members = self._sort_members(filtered_members)
            self._display_members(filtered_members)
            print(f"[INFO] Filtered to {len(filtered_members)} members")
        except Exception as e:
            print(f"[ERROR] Filter members failed: {e}")
            import traceback
            traceback.print_exc()

    def _member_matches_filters(self, member, search_text, status):
        if status != "All" and member['status'] != status:
            return False
        if search_text:
            searchable_fields = [
                str(member.get('member_id', '')),
                str(member.get('full_name', '')),
                str(member.get('email', '')),
                str(member.get('mobile_number', ''))
            ]
            if not any(search_text in field.lower() for field in searchable_fields):
                return False
        return True

    def _sort_members(self, members):
        if self.sort_column < len(AppConfig.PATRON_TABLE['keys']):
            sort_key = AppConfig.PATRON_TABLE['keys'][self.sort_column]
            return sorted(
                members,
                key=lambda x: str(x.get(sort_key, '')).lower(),
                reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
            )
        return members

    def _validate_database_connection(self):
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection available")
            self._show_warning(
                "Database Error",
                "Not connected to database. Some features may be unavailable."
            )
            return False
        return True

    def _validate_selection(self):
        if not self.selected_member_id:
            self._show_warning(
                "No Selection",
                "Please select a member from the table first."
            )
            return False
        return True

    def _add_member(self):
        try:
            dialog = AddMemberDialog(
                parent=self,
                db=self.db,
                callback=self._load_members_from_database
            )
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add member dialog failed: {e}")
            self._show_critical("Dialog Error", "Failed to open add member dialog")

    def _view_member(self):
        if not self._validate_selection():
            return
        try:
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            if member_data:
                dialog = ViewMemberDialog(parent=self, member_data=member_data)
                dialog.exec()
            else:
                self._show_warning("Member Not Found", "Selected member not found in database")
                self._load_members_from_database()
        except Exception as e:
            print(f"[ERROR] View member failed: {e}")
            self._show_critical("View Error", f"Failed to view member:\n{str(e)}")

    def _update_member(self):
        if not self._validate_selection():
            return
        try:
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            if member_data:
                dialog = UpdateMemberDialog(
                    parent=self,
                    db=self.db,
                    member_data=member_data,
                    callback=self._load_members_from_database
                )
                dialog.exec()
            else:
                self._show_warning("Member Not Found", "Selected member not found in database")
                self._load_members_from_database()
        except Exception as e:
            print(f"[ERROR] Update member failed: {e}")
            self._show_critical("Update Error", f"Failed to update member:\n{str(e)}")

    def _delete_member(self):
        if not self._validate_selection():
            return
        try:
            query = "SELECT full_name FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            if not member_data:
                self._show_warning("Member Not Found", "Selected member not found in database")
                self._load_members_from_database()
                return
            fine_query = """
                SELECT SUM(fine_amount) as total_fines 
                FROM borrowed_books 
                WHERE member_id = %s AND fine_amount > 0
            """
            fine_result = self.db.fetch_one(fine_query, (self.selected_member_id,))
            if fine_result and fine_result['total_fines'] and float(fine_result['total_fines']) > 0:
                total_fines = float(fine_result['total_fines'])
                self._show_warning(
                    "Cannot Deactivate Member",
                    f"Member '{member_data['full_name']}' has outstanding fines of ₱{total_fines:.2f}.\n"
                    f"Please clear all fines before deleting this member."
                )
                return
            dialog = ConfirmDeleteMemberDialog(
                parent=self,
                member_name=member_data['full_name']
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                delete_query = "DELETE FROM members WHERE member_id = %s"
                if self.db.execute_query(
                    delete_query,
                    (self.selected_member_id,)
                ):
                    self._show_info(
                        "Delete Successful",
                        f"Member '{member_data['full_name']}' has been deleted."
                    )
                    self.selected_member_id = None
                    self._load_members_from_database()
                else:
                    self._show_critical("Delete Failed", "Failed to delete member from database")
        except Exception as e:
            print(f"[ERROR] Delete member failed: {e}")
            self._show_critical("Delete Error", f"Failed to delete member:\n{str(e)}")
    
    def _show_fullscreen(self):
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        event.accept()

    # Message Box Helpers
    def _show_warning(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #3C2A21;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)
        msg.exec()

    def _show_critical(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #3C2A21;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)
        msg.exec()

    def _show_info(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #3C2A21;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)
        msg.exec()