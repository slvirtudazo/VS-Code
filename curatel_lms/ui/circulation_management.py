# curatel_lms/ui/circulation_management.py

# Handles borrowing transactions with search, filtering, sorting, CRUD operations, and status updates

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from curatel_lms.config import AppConfig
from curatel_lms.ui.circulation_dialogs import (
    AddBorrowDialog, ViewBorrowDialog, UpdateBorrowDialog, ConfirmDeleteBorrowDialog
)

class CirculationManagement(QMainWindow):
    # Main window for managing library borrowing transactions with a sortable, filterable table and CRUD operations.

    def __init__(self, db=None):
        # Initialize window with database connection, UI, data load, and fullscreen display.
        super().__init__()
        
        self.db = db
        self.all_borrows = []
        self.filtered_borrows = []
        self.selected_borrow_id = None
        self.sort_column = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.setWindowTitle("Curatel - Circulation Management")
        
        try:
            self._setup_ui()
            self._load_borrows_from_database()
            self._show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Circulation Management: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Initialization Error",
                f"Failed to initialize Circulation Management:\n{str(e)}"
            )
    
    def _setup_ui(self):
        # Build full UI layout with header, search, table, and action buttons.
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.mousePressEvent = self._clear_selection
        central_widget.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        
        main_layout.addLayout(self._create_header())
        main_layout.addLayout(self._create_search_section())
        main_layout.addSpacing(5)
        main_layout.addWidget(self._create_borrows_table())
        main_layout.addSpacing(5)
        main_layout.addLayout(self._create_action_buttons())
    
    def _create_header(self):
        # Create title and subtitle layout.
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Circulation Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
        header_text.addWidget(title)

        subtitle = QLabel("Monitor issued books, returns, and charges")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet(f"color: {AppConfig.COLORS['text_gray']};")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)

        header_layout.addLayout(header_text)
        header_layout.addStretch()

        return header_layout
    
    def _create_search_section(self):
        # Create search input and status filter.
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by book id, member id, or book title")
        self.search_input.setStyleSheet(AppConfig.STYLES['search_input'])
        self.search_input.setFixedHeight(AppConfig.SEARCH_HEIGHT)
        self.search_input.textChanged.connect(self._filter_borrows)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        search_layout.addWidget(self._create_filter_label("Status"))
        self.status_combo = self._create_filter_combo(["All"] + AppConfig.TRANSACTION_STATUSES)
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()

        return search_layout
    
    def _create_filter_label(self, text):
        # Create styled filter label.
        label = QLabel(text)
        label.setFont(QFont("Montserrat", 10))
        label.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")

        return label
    
    def _create_filter_combo(self, items):
        # Create styled filter combo box.
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(AppConfig.STYLES['combo'])
        combo.setFixedSize(120, AppConfig.SEARCH_HEIGHT)
        combo.currentTextChanged.connect(self._filter_borrows)

        return combo
    
    def _create_borrows_table(self):
        # Create and configure main transactions table.
        self.borrows_table = QTableWidget()
        self.borrows_table.setColumnCount(len(AppConfig.CIRCULATION_TABLE['columns']))
        self.borrows_table.setSortingEnabled(False)
        self.borrows_table.setHorizontalHeaderLabels(AppConfig.CIRCULATION_TABLE['columns'])
        self.borrows_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.borrows_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.borrows_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.borrows_table.setAlternatingRowColors(True)
        self.borrows_table.setStyleSheet(AppConfig.STYLES['table_with_corner'])
        
        header = self.borrows_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self._handle_header_click)
        
        for col, width in enumerate(AppConfig.CIRCULATION_TABLE['widths']):
            self.borrows_table.setColumnWidth(col, width)
        
        self.borrows_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.borrows_table.verticalHeader().setVisible(False)
        self.borrows_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.borrows_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.borrows_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.borrows_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return self.borrows_table
    
    def _create_action_buttons(self):
        # Create CRUD and navigation buttons.
        action_layout = QHBoxLayout()
        
        button_configs = [
            ("Add Transaction", self._add_borrow, AppConfig.BUTTON_WIDTH_MEDIUM),
            ("View Transaction", self._view_borrow, AppConfig.BUTTON_WIDTH_MEDIUM),
            ("Update Transaction", self._update_borrow, AppConfig.BUTTON_WIDTH_WIDE),
            ("Delete Transaction", self._delete_borrow, AppConfig.BUTTON_WIDTH_WIDE)
        ]
        
        for text, callback, width in button_configs:
            btn = self._create_action_button(text, callback, width)
            action_layout.addWidget(btn)
        
        action_layout.addStretch()
        
        back_btn = self._create_action_button("Back to Dashboard", self._go_back_to_dashboard, AppConfig.BUTTON_WIDTH_WIDE)
        action_layout.addWidget(back_btn)
        
        return action_layout
    
    def _create_action_button(self, text, callback, width=None):
        # Create styled action button.
        btn = QPushButton(text)
        btn.setFont(QFont("Montserrat", 10))
        button_width = width if width else AppConfig.BUTTON_WIDTH_STANDARD
        btn.setFixedSize(button_width, AppConfig.BUTTON_HEIGHT)
        btn.setStyleSheet(AppConfig.STYLES['button'])
        btn.clicked.connect(callback)
        return btn
    
    def _on_selection_changed(self):
        # Track selected transaction ID from table row.
        try:
            selected_row = self.borrows_table.currentRow()
            if selected_row >= 0 and selected_row < len(self.filtered_borrows):
                self.selected_borrow_id = self.filtered_borrows[selected_row]['borrow_id']
                print(f"[INFO] Selected borrow_id: {self.selected_borrow_id}")
            else:
                self.selected_borrow_id = None
        except Exception as e:
            print(f"[ERROR] Selection change failed: {e}")
            self.selected_borrow_id = None
    
    def _clear_selection(self, event):
        # Clear table selection and widget focus on empty click.
        try:
            if self.borrows_table:
                self.borrows_table.clearSelection()
                self.selected_borrow_id = None
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] Clear selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)
    
    def _handle_header_click(self, logical_index):
        # Toggle sort order on column header click.
        try:
            if self.sort_column == logical_index:
                self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                self.sort_column = logical_index
                self.sort_order = Qt.SortOrder.AscendingOrder
            self._filter_borrows()
        except Exception as e:
            print(f"[ERROR] Header click failed: {e}")
            QMessageBox.warning(self, "Sort Error", "Failed to sort table")
    
    def _load_borrows_from_database(self):
        # Load all transactions from DB with book titles.
        if not self._validate_database_connection():
            return
        
        try:
            query = """
                SELECT bb.*, b.title as book_title 
                FROM borrowed_books bb
                LEFT JOIN books b ON bb.book_id = b.book_id
                ORDER BY bb.borrow_id DESC
            """
            self.all_borrows = self.db.fetch_all(query)
            
            if self.all_borrows:
                print(f"[OK] Loaded {len(self.all_borrows)} transactions")
                self._filter_borrows()
            else:
                print("[WARNING] No transactions found in database")
                self.borrows_table.setRowCount(0)
                self.filtered_borrows = []
        except Exception as e:
            print(f"[ERROR] Failed to load transactions: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Database Error", f"Failed to load transactions from database:\n{str(e)}")
    
    def _display_borrows(self, borrows):
        # Populate table with transaction data and status colors.
        try:
            self.borrows_table.setRowCount(len(borrows))
            for row, borrow in enumerate(borrows):
                for col, key in enumerate(AppConfig.CIRCULATION_TABLE['keys']):
                    value = borrow.get(key, '')
                    if key == 'return_date':
                        if value is None or str(value).strip().lower() in ('none', 'null', ''):
                            value = ''
                        else:
                            value = str(value)
                    elif key == 'fine_amount':
                        value = f"₱{float(value):.2f}"
                    else:
                        value = str(value)
                    item = self._create_table_item(value)
                    if col == 6:
                        status = borrow['status']
                        if status == 'Borrowed':
                            item.setForeground(QColor(AppConfig.COLORS['status_borrowed']))
                        elif status == 'Returned':
                            item.setForeground(QColor(AppConfig.COLORS['status_returned']))
                        elif status == 'Overdue':
                            item.setForeground(QColor(AppConfig.COLORS['status_overdue']))
                    self.borrows_table.setItem(row, col, item)
        except Exception as e:
            print(f"[ERROR] Display borrows failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_table_item(self, text):
        # Create styled table cell item.
        item = QTableWidgetItem(text)
        item.setFont(QFont("Montserrat", 10))
        item.setForeground(QColor(AppConfig.COLORS['text_dark']))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        return item
    
    def _filter_borrows(self):
        # Apply search and status filters, then sort and display.
        try:
            if not self.all_borrows:
                self.filtered_borrows = []
                return
            
            search_text = self.search_input.text().lower().strip()
            status = self.status_combo.currentText()
            
            filtered_borrows = [
                borrow for borrow in self.all_borrows
                if self._borrow_matches_filters(borrow, search_text, status)
            ]
            
            if self.sort_column is not None and filtered_borrows:
                filtered_borrows = self._sort_borrows(filtered_borrows)
            
            self.filtered_borrows = filtered_borrows
            self._display_borrows(filtered_borrows)
            print(f"[INFO] Filtered to {len(filtered_borrows)} transactions")
        except Exception as e:
            print(f"[ERROR] Filter borrows failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _borrow_matches_filters(self, borrow, search_text, status):
        # Check if transaction matches status and search filters.
        if status != "All" and borrow['status'] != status:
            return False
        if search_text:
            searchable_fields = [
                str(borrow.get('book_id', '')),
                str(borrow.get('member_id', '')),
                str(borrow.get('book_title', ''))
            ]
            if not any(search_text in field.lower() for field in searchable_fields):
                return False
        return True
    
    def _sort_borrows(self, borrows):
        # Sort transactions by selected column.
        if self.sort_column < len(AppConfig.CIRCULATION_TABLE['keys']):
            sort_key = AppConfig.CIRCULATION_TABLE['keys'][self.sort_column]
            def sort_value(item):
                value = item.get(sort_key)
                if value is None:
                    return ''
                if sort_key == 'fine_amount':
                    return float(value) if value else 0.0
                return str(value).lower()
            return sorted(borrows, key=sort_value, reverse=(self.sort_order == Qt.SortOrder.DescendingOrder))
        return borrows
    
    def _validate_database_connection(self):
        # Check if DB connection exists.
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection available")
            QMessageBox.warning(self, "Database Error", "Not connected to database. Some features may be unavailable.")
            return False
        return True
    
    def _validate_selection(self):
        # Check if a transaction is selected.
        if not self.selected_borrow_id:
            QMessageBox.warning(self, "No Selection", "Please select a transaction from the table first.")
            return False
        return True
    
    def _add_borrow(self):
        # Open dialog to add new transaction.
        try:
            dialog = AddBorrowDialog(parent=self, db=self.db, callback=self._load_borrows_from_database)
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add transaction dialog failed: {e}")
            QMessageBox.critical(self, "Dialog Error", "Failed to open add transaction dialog")
    
    def _view_borrow(self):
        # Open read-only dialog for selected transaction.
        if not self._validate_selection():
            return
        try:
            query = """
                SELECT bb.*, b.title as book_title, m.full_name as member_name
                FROM borrowed_books bb
                LEFT JOIN books b ON bb.book_id = b.book_id
                LEFT JOIN members m ON bb.member_id = m.member_id
                WHERE bb.borrow_id = %s
            """
            borrow_data = self.db.fetch_one(query, (self.selected_borrow_id,))
            if borrow_data:
                dialog = ViewBorrowDialog(parent=self, borrow_data=borrow_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Transaction Not Found", "Selected transaction not found in database")
                self._load_borrows_from_database()
        except Exception as e:
            print(f"[ERROR] View transaction failed: {e}")
            QMessageBox.critical(self, "View Error", f"Failed to view transaction:\n{str(e)}")
    
    def _update_borrow(self):
        # Open editable dialog for selected transaction.
        if not self._validate_selection():
            return
        try:
            query = """
                SELECT bb.*, b.title as book_title, m.full_name as member_name
                FROM borrowed_books bb
                LEFT JOIN books b ON bb.book_id = b.book_id
                LEFT JOIN members m ON bb.member_id = m.member_id
                WHERE bb.borrow_id = %s
            """
            borrow_data = self.db.fetch_one(query, (self.selected_borrow_id,))
            if borrow_data:
                dialog = UpdateBorrowDialog(parent=self, db=self.db, borrow_data=borrow_data, callback=self._load_borrows_from_database)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Transaction Not Found", "Selected transaction not found in database")
                self._load_borrows_from_database()
        except Exception as e:
            print(f"[ERROR] Update transaction failed: {e}")
            QMessageBox.critical(self, "Update Error", f"Failed to update transaction:\n{str(e)}")
    
    def _delete_borrow(self):
        # Delete selected transaction after confirmation.
        if not self._validate_selection():
            return
        try:
            borrow_data = None
            for borrow in self.filtered_borrows:
                if borrow['borrow_id'] == self.selected_borrow_id:
                    borrow_data = borrow
                    break
            if not borrow_data:
                QMessageBox.warning(self, "Transaction Not Found", "Selected transaction not found")
                self._load_borrows_from_database()
                return
            book_id = borrow_data['book_id']
            member_id = borrow_data['member_id']
            dialog = ConfirmDeleteBorrowDialog(parent=self, book_id=book_id, member_id=member_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                delete_query = "DELETE FROM borrowed_books WHERE borrow_id = %s"
                if self.db.execute_query(delete_query, (self.selected_borrow_id,)):
                    QMessageBox.information(self, "Delete Successful", f"Transaction for Book {book_id} and Member {member_id} has been deleted.")
                    self.selected_borrow_id = None
                    self._load_borrows_from_database()
                else:
                    QMessageBox.critical(self, "Delete Failed", "Failed to delete transaction from database")
        except Exception as e:
            print(f"[ERROR] Delete transaction failed: {e}")
            QMessageBox.critical(self, "Delete Error", f"Failed to delete transaction:\n{str(e)}")
    
    def _go_back_to_dashboard(self):
        # Close window and return to dashboard.
        self.close()
    
    def _show_fullscreen(self):
        # Maximize window on launch.
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        # Handle window close.
        event.accept()