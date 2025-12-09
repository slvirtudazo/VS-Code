# curatel_lms/ui/patron_management.py

"""
Patron management module.
Main window for managing library member records.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from curatel_lms.ui.patron_dialogs import (
    AddMemberDialog, ViewMemberDialog, UpdateMemberDialog, ConfirmDeleteMemberDialog
)

# UI Constants
BUTTON_WIDTH_STANDARD = 120
BUTTON_WIDTH_WIDE = 130
BUTTON_HEIGHT = 40
SEARCH_HEIGHT = 40

# Color Constants
STATUS_ACTIVE = "#228C3A"
STATUS_INACTIVE = "#DC3545"
TEXT_BLACK = "#000000"

# Style Constants
SEARCH_INPUT_STYLE = """
    QLineEdit {
        border: 2px solid #8B7E66;
        border-radius: 10px;
        padding: 8px 10px;
        font-family: Montserrat;
        font-size: 11px;
        color: black;
        background-color: white;
    }
    QLineEdit:focus {
        border: 2px solid #6B5E46;
    }
    QLineEdit::placeholder {
        color: gray;
    }
"""

COMBO_STYLE = """
    QComboBox {
        border: 2px solid #8B7E66;
        border-radius: 10px;
        padding: 5px 10px;
        font-family: Montserrat;
        font-size: 12px;
        color: #000000;
        background-color: white;
    }
    QComboBox:focus {
        border: 2px solid #6B5E46;
    }
    QComboBox QAbstractItemView {
        color: #000000;
        background-color: white;
        selection-background-color: #D9CFC2;
        selection-color: black;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        border: 1px solid #8B7E66;
        gridline-color: #8B7E66;
        background-color: white;
        selection-background-color: #D9CFC2;
        selection-color: black;
    }
    QHeaderView::section {
        background-color: #9B8B7E;
        padding: 8px;
        font-weight: bold;
        color: white;
        font-family: Montserrat;
        font-size: 12px;
        border: none;
    }
    QHeaderView::section:hover {
        background-color: #7A6D55;
    }
    QTableWidget::item:hover {
        background-color: #D9CFC2;
    }
    QTableWidget::item:selected {
        background-color: #C9B8A8;
    }
    QTableCornerButton::section {
        background-color: #9B8B7E;
        border: 1px solid #8B7E66;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #8B7E66;
        color: white;
        border: none;
        border-radius: 10px;
    }
    QPushButton:hover {
        background-color: #6B5E46;
    }
"""

# Table Configuration
TABLE_COLUMNS = [
    "Member ID", "Full Name", "Email", "Mobile Number",
    "Status", "Borrowed Books", "Added At", "Updated At"
]
COLUMN_WIDTHS = [100, 200, 250, 180, 100, 140, 200, 200]
COLUMN_NAMES = [
    'member_id', 'full_name', 'email', 'mobile_number',
    'status', 'borrowed_books', 'added_at', 'updated_at'
]


class PatronManagement(QMainWindow):
    """Main window for patron management operations."""
    
    def __init__(self, db=None):
        """
        Initialize patron management window.
        Args:
            db: Database connection object
        """
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
                self, "Error",
                f"Failed to initialize Patron Management:\n{str(e)}"
            )
    
    def _setup_ui(self):
        """Configure main window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.mousePressEvent = self._clear_selection
        central_widget.setStyleSheet("background-color: white;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        
        # Add UI sections
        main_layout.addLayout(self._create_header())
        main_layout.addLayout(self._create_search_section())
        main_layout.addSpacing(5)
        main_layout.addWidget(self._create_members_table())
        main_layout.addSpacing(5)
        main_layout.addLayout(self._create_action_buttons())
    
    def _create_header(self):
        """
        Create header section with title and subtitle.
        Returns: QHBoxLayout containing header
        """
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Patron Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_text.addWidget(title)

        subtitle = QLabel("Manage member records, status, and registration details")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333;")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        return header_layout
    
    def _create_search_section(self):
        """
        Create search and filter section.
        Returns: QHBoxLayout containing search controls
        """
        search_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by id, name, email, or mobile number")
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.setFixedHeight(SEARCH_HEIGHT)
        self.search_input.textChanged.connect(self._filter_members)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        # Status filter
        search_layout.addWidget(self._create_label("Status"))
        self.status_combo = self._create_combo(["All", "Active", "Inactive"])
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()
        
        return search_layout
    
    def _create_label(self, text):
        """
        Create filter label.
        Args:
            text: Label text
        Returns: QLabel
        """
        label = QLabel(text)
        label.setFont(QFont("Montserrat", 10))
        label.setStyleSheet("color: #000000;")
        return label
    
    def _create_combo(self, items):
        """
        Create combo box with items.
        Args:
            items: List of items for combo box
        Returns: QComboBox
        """
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(COMBO_STYLE)
        combo.setFixedSize(120, SEARCH_HEIGHT)
        combo.currentTextChanged.connect(self._filter_members)
        return combo
    
    def _create_members_table(self):
        """
        Create members table widget.
        Returns: QTableWidget configured for members
        """
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(len(TABLE_COLUMNS))
        self.members_table.setSortingEnabled(False)
        self.members_table.setHorizontalHeaderLabels(TABLE_COLUMNS)
        
        # Configure table behavior
        self.members_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.members_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.members_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.members_table.setAlternatingRowColors(True)
        self.members_table.setStyleSheet(TABLE_STYLE)
        
        # Configure header
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self._handle_header_click)
        
        # Set column widths
        for col, width in enumerate(COLUMN_WIDTHS):
            self.members_table.setColumnWidth(col, width)
        
        # Configure scrolling
        self.members_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.members_table.verticalHeader().setVisible(False)
        self.members_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.members_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.members_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Connect selection signal
        self.members_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return self.members_table
    
    def _create_action_buttons(self):
        """
        Create action button layout.
        Returns: QHBoxLayout containing action buttons
        """
        action_layout = QHBoxLayout()
        
        # CRUD buttons
        buttons = [
            ("Add Member", self._add_member, BUTTON_WIDTH_STANDARD),
            ("View Member", self._view_member, BUTTON_WIDTH_STANDARD),
            ("Update Member", self._update_member, BUTTON_WIDTH_WIDE),
            ("Delete Member", self._delete_member, BUTTON_WIDTH_WIDE)
        ]
        
        for text, callback, width in buttons:
            btn = self._create_button(text, callback, width)
            action_layout.addWidget(btn)
        
        action_layout.addStretch()
        
        # Back button
        back_btn = self._create_button("Back to Dashboard", self._go_back_to_dashboard, 150)
        action_layout.addWidget(back_btn)
        
        return action_layout
    
    def _create_button(self, text, callback, width=BUTTON_WIDTH_STANDARD):
        """
        Create styled button.
        Args:
            text: Button text
            callback: Click callback function
            width: Button width
        Returns: QPushButton
        """
        btn = QPushButton(text)
        btn.setFont(QFont("Montserrat", 10))
        btn.setFixedSize(width, BUTTON_HEIGHT)
        btn.setStyleSheet(BUTTON_STYLE)
        btn.clicked.connect(callback)
        return btn
    
    def _on_selection_changed(self):
        """Track selected member when selection changes."""
        try:
            selected_row = self.members_table.currentRow()
            if selected_row >= 0:
                self.selected_member_id = self.members_table.item(selected_row, 0).text()
            else:
                self.selected_member_id = None
        except Exception as e:
            print(f"[ERROR] Selection change: {e}")
            self.selected_member_id = None
    
    def _clear_selection(self, event):
        """Clear table selection when clicking empty space."""
        try:
            if self.members_table:
                self.members_table.clearSelection()
                self.selected_member_id = None
            
            # Clear focus from input widgets
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] Clear selection: {e}")
        
        QWidget.mousePressEvent(self.centralWidget(), event)
    
    def _handle_header_click(self, logical_index):
        """
        Handle column header click for sorting.
        Args:
            logical_index: Column index clicked
        """
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
            print(f"[ERROR] Header click: {e}")
            QMessageBox.warning(self, "Error", "Failed to sort table")
    
    def _load_members_from_database(self):
        """Load all members from database."""
        if not self._validate_database_connection():
            return
        
        try:
            query = "SELECT * FROM members ORDER BY member_id"
            self.all_members = self.db.fetch_all(query)
            
            if self.all_members:
                print(f"[OK] Loaded {len(self.all_members)} members")
                self._filter_members()
            else:
                print("[WARNING] No members found")
                self.members_table.setRowCount(0)
                
        except Exception as e:
            print(f"[ERROR] Failed to load members: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load members:\n{str(e)}")
    
    def _display_members(self, members):
        """
        Display members in table.
        Args:
            members: List of member dictionaries
        """
        try:
            self.members_table.setRowCount(len(members))
            
            for row, member in enumerate(members):
                for col, key in enumerate(COLUMN_NAMES):
                    value = str(member.get(key, ''))
                    item = self._create_table_item(value)
                    
                    # Apply status color
                    if col == 4:  # Status column
                        color = self._get_status_color(member['status'])
                        item.setForeground(QColor(color))
                    
                    self.members_table.setItem(row, col, item)
                    
        except Exception as e:
            print(f"[ERROR] Display members: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_table_item(self, text):
        """
        Create formatted table item.
        Args:
            text: Item text
        Returns: QTableWidgetItem
        """
        item = QTableWidgetItem(text)
        item.setFont(QFont("Montserrat", 10))
        item.setForeground(QColor(TEXT_BLACK))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        return item
    
    def _filter_members(self):
        """Filter members based on search criteria."""
        try:
            if not self.all_members:
                return
            
            search_text = self.search_input.text().lower().strip()
            status = self.status_combo.currentText()
            
            # Apply filters
            filtered_members = [
                member for member in self.all_members
                if self._matches_filters(member, search_text, status)
            ]
            
            # Apply sorting
            if self.sort_column is not None and filtered_members:
                filtered_members = self._sort_members(filtered_members)
            
            self._display_members(filtered_members)
            print(f"[INFO] Filtered to {len(filtered_members)} members")
            
        except Exception as e:
            print(f"[ERROR] Filter members: {e}")
            import traceback
            traceback.print_exc()
    
    def _matches_filters(self, member, search_text, status):
        """
        Check if member matches filter criteria.
        Args:
            member: Member dictionary
            search_text: Search string
            status: Status filter
        Returns: True if matches, False otherwise
        """
        if status != "All" and member['status'] != status:
            return False
        
        if search_text:
            searchable = [
                str(member.get('member_id', '')),
                str(member.get('full_name', '')),
                str(member.get('email', '')),
                str(member.get('mobile_number', ''))
            ]
            if not any(search_text in field.lower() for field in searchable):
                return False
        
        return True
    
    def _sort_members(self, members):
        """
        Sort members by selected column.
        Args:
            members: List of member dictionaries
        Returns: Sorted list
        """
        if self.sort_column < len(COLUMN_NAMES):
            sort_key = COLUMN_NAMES[self.sort_column]
            return sorted(
                members,
                key=lambda x: str(x.get(sort_key, '')).lower(),
                reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
            )
        return members
    
    def _get_status_color(self, status):
        """
        Get color for member status.
        Args:
            status: Member status
        Returns: Color code string
        """
        return STATUS_ACTIVE if status == 'Active' else STATUS_INACTIVE
    
    def _validate_database_connection(self):
        """
        Validate database connection.
        Returns: True if connected, False otherwise
        """
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection")
            QMessageBox.warning(self, "Database Error", "Not connected to database.")
            return False
        return True
    
    def _validate_selection(self):
        """
        Validate member selection.
        Returns: True if member selected, False otherwise
        """
        if not self.selected_member_id:
            QMessageBox.warning(self, "No Selection", "Please select a member first.")
            return False
        return True
    
    def _add_member(self):
        """Open add member dialog."""
        try:
            dialog = AddMemberDialog(self, self.db, self._load_members_from_database)
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add member: {e}")
            QMessageBox.critical(self, "Error", "Failed to open add member dialog")
    
    def _view_member(self):
        """View selected member."""
        if not self._validate_selection():
            return
        
        try:
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            
            if member_data:
                dialog = ViewMemberDialog(self, member_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Member not found in database")
                self._load_members_from_database()
                
        except Exception as e:
            print(f"[ERROR] View member: {e}")
            QMessageBox.critical(self, "Error", f"Failed to view member:\n{str(e)}")
    
    def _update_member(self):
        """Update selected member."""
        if not self._validate_selection():
            return
        
        try:
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            
            if member_data:
                dialog = UpdateMemberDialog(self, self.db, member_data, self._load_members_from_database)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Member not found in database")
                self._load_members_from_database()
                
        except Exception as e:
            print(f"[ERROR] Update member: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update member:\n{str(e)}")
    
    def _delete_member(self):
        """Delete selected member."""
        if not self._validate_selection():
            return
        
        try:
            query = "SELECT full_name FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            
            if not member_data:
                QMessageBox.warning(self, "Error", "Member not found in database")
                self._load_members_from_database()
                return
            
            dialog = ConfirmDeleteMemberDialog(self, member_data['full_name'])
            if dialog.exec() == QDialog.DialogCode.Accepted:
                delete_query = "DELETE FROM members WHERE member_id = %s"
                if self.db.execute_query(delete_query, (self.selected_member_id,)):
                    QMessageBox.information(
                        self, "Success",
                        f"Member '{member_data['full_name']}' deleted successfully!"
                    )
                    self.selected_member_id = None
                    self._load_members_from_database()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete member")
                    
        except Exception as e:
            print(f"[ERROR] Delete member: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete member:\n{str(e)}")
    
    def _go_back_to_dashboard(self):
        """Close window and return to dashboard."""
        self.close()
    
    def _show_fullscreen(self):
        """Display window in maximized state."""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        """Handle window close event."""
        event.accept()