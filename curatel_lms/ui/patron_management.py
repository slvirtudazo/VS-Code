# curatel_lms/ui/patron_management.py
# Patron Management Module - Main Window: manages library member records with search, filtering, CRUD, sortable table, modal dialogs, and status indicators.
# OOP: QMainWindow subclass with db composition, encapsulated logic, private methods, and single-responsibility design.

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from curatel_lms.config import AppConfig
from curatel_lms.ui.patron_dialogs import (
    AddMemberDialog, ViewMemberDialog, UpdateMemberDialog, 
    ConfirmDeleteMemberDialog
)


class PatronManagement(QMainWindow):
    # Main window for managing library members: displays sortable/filterable table, supports CRUD via modal dialogs, tracks selection, and uses db for data.
    
    def __init__(self, db=None):
        # Initialize UI, load members, maximize window; handles errors with alerts and logs.
        super().__init__()
        
        self.db = db
        self.all_members = []
        self.selected_member_id = None
        self.sort_column = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.setWindowTitle("Curatel - Patron Management")
        
        try:
            self._setup_ui()
            self._load_members_from_database()
            self._show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Patron Management: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Initialization Error",
                f"Failed to initialize Patron Management:\n{str(e)}"
            )
    
    def _setup_ui(self):
        # Build full UI: header, search, table, buttons; enables click-to-clear selection and applies consistent styling.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.mousePressEvent = self._clear_selection
        central_widget.setStyleSheet(
            f"background-color: {AppConfig.COLORS['bg_white']};"
        )
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        main_layout.addLayout(self._create_header())
        main_layout.addLayout(self._create_search_section())
        main_layout.addSpacing(5)
        main_layout.addWidget(self._create_members_table())
        main_layout.addSpacing(5)
        main_layout.addLayout(self._create_action_buttons())
    
    def _create_header(self):
        # Return header layout with title and subtitle, left-aligned.
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
        # Return layout with search input and status filter, connected to real-time filtering.
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by id, name, email, or mobile number"
        )
        self.search_input.setStyleSheet(AppConfig.STYLES['search_input'])
        self.search_input.setFixedHeight(AppConfig.SEARCH_HEIGHT)
        self.search_input.textChanged.connect(self._filter_members)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        search_layout.addWidget(self._create_filter_label("Status"))
        self.status_combo = self._create_filter_combo(
            ["All", "Active", "Inactive"]
        )
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()
        return search_layout
    
    def _create_filter_label(self, text):
        # Return styled label for filter controls.
        label = QLabel(text)
        label.setFont(QFont("Montserrat", 10))
        label.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
        return label
    
    def _create_filter_combo(self, items):
        # Return styled, connected combo box for filtering.
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(AppConfig.STYLES['combo'])
        combo.setFixedSize(120, AppConfig.SEARCH_HEIGHT)
        combo.currentTextChanged.connect(self._filter_members)
        return combo
    
    def _create_members_table(self):
        # Return fully configured, non-editable, sortable, scrollable table with row selection and status coloring.
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
        # Return layout with CRUD and navigation buttons.
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
        
        back_btn = self._create_action_button(
            "Back to Dashboard",
            self._go_back_to_dashboard,
            AppConfig.BUTTON_WIDTH_WIDE
        )
        action_layout.addWidget(back_btn)
        return action_layout
    
    def _create_action_button(self, text, callback, width=None):
        # Return styled, sized, connected action button.
        btn = QPushButton(text)
        btn.setFont(QFont("Montserrat", 10))
        button_width = width if width else AppConfig.BUTTON_WIDTH_STANDARD
        btn.setFixedSize(button_width, AppConfig.BUTTON_HEIGHT)
        btn.setStyleSheet(AppConfig.STYLES['button'])
        btn.clicked.connect(callback)
        return btn
    
    def _on_selection_changed(self):
        # Track selected member ID from table row; handle errors.
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
        # Deselect table and clear input focus on empty-space click.
        try:
            if self.members_table:
                self.members_table.clearSelection()
                self.selected_member_id = None
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] Clear selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)
    
    def _handle_header_click(self, logical_index):
        # Toggle sort order on header click and refresh display.
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
            QMessageBox.warning(self, "Sort Error", "Failed to sort table")
    
    def _load_members_from_database(self):
        # Fetch all members from db, store locally, and display; handle errors and empty cases.
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
            QMessageBox.critical(
                self, "Database Error",
                f"Failed to load members from database:\n{str(e)}"
            )
    
    def _display_members(self, members):
        # Populate table with member data; color status column.
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
        # Return centered, styled table cell item.
        item = QTableWidgetItem(text)
        item.setFont(QFont("Montserrat", 10))
        item.setForeground(QColor(AppConfig.COLORS['text_dark']))
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        return item
    
    def _filter_members(self):
        # Apply search and status filters, sort if active, then display results.
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
        # Return True if member matches status and text filters.
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
        # Return members sorted by current column and order.
        if self.sort_column < len(AppConfig.PATRON_TABLE['keys']):
            sort_key = AppConfig.PATRON_TABLE['keys'][self.sort_column]
            return sorted(
                members,
                key=lambda x: str(x.get(sort_key, '')).lower(),
                reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
            )
        return members
    
    def _validate_database_connection(self):
        # Return False if db missing; show warning.
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection available")
            QMessageBox.warning(
                self, "Database Error",
                "Not connected to database. Some features may be unavailable."
            )
            return False
        return True
    
    def _validate_selection(self):
        # Return False if no member selected; show warning.
        if not self.selected_member_id:
            QMessageBox.warning(
                self, "No Selection",
                "Please select a member from the table first."
            )
            return False
        return True
    
    def _add_member(self):
        # Open add-member dialog; refresh on success.
        try:
            dialog = AddMemberDialog(
                parent=self,
                db=self.db,
                callback=self._load_members_from_database
            )
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add member dialog failed: {e}")
            QMessageBox.critical(
                self, "Dialog Error",
                "Failed to open add member dialog"
            )
    
    def _view_member(self):
        # Open read-only view dialog for selected member; validate selection and existence.
        if not self._validate_selection():
            return
        try:
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            if member_data:
                dialog = ViewMemberDialog(parent=self, member_data=member_data)
                dialog.exec()
            else:
                QMessageBox.warning(
                    self, "Member Not Found",
                    "Selected member not found in database"
                )
                self._load_members_from_database()
        except Exception as e:
            print(f"[ERROR] View member failed: {e}")
            QMessageBox.critical(
                self, "View Error",
                f"Failed to view member:\n{str(e)}"
            )
    
    def _update_member(self):
        # Open editable update dialog; refresh on success.
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
                QMessageBox.warning(
                    self, "Member Not Found",
                    "Selected member not found in database"
                )
                self._load_members_from_database()
        except Exception as e:
            print(f"[ERROR] Update member failed: {e}")
            QMessageBox.critical(
                self, "Update Error",
                f"Failed to update member:\n{str(e)}"
            )
    
    def _delete_member(self):
        # Confirm and delete selected member; refresh on success.
        if not self._validate_selection():
            return
        try:
            query = "SELECT full_name FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            if not member_data:
                QMessageBox.warning(
                    self, "Member Not Found",
                    "Selected member not found in database"
                )
                self._load_members_from_database()
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
                    QMessageBox.information(
                        self, "Delete Successful",
                        f"Member '{member_data['full_name']}' has been deleted."
                    )
                    self.selected_member_id = None
                    self._load_members_from_database()
                else:
                    QMessageBox.critical(
                        self, "Delete Failed",
                        "Failed to delete member from database"
                    )
        except Exception as e:
            print(f"[ERROR] Delete member failed: {e}")
            QMessageBox.critical(
                self, "Delete Error",
                f"Failed to delete member:\n{str(e)}"
            )
    
    def _go_back_to_dashboard(self):
        # Close window to return to dashboard.
        self.close()
    
    def _show_fullscreen(self):
        # Maximize window on launch.
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        # Allow window to close normally.
        event.accept()