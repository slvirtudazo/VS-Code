# curatel_lms/ui/circulation_management.py - COMPLETE FIXED VERSION

"""
Circulation management module.
Main window for managing library transactions.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                              QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from curatel_lms.ui.circulation_dialogs import (AddBorrowDialog, ViewBorrowDialog, 
                                                 UpdateBorrowDialog, ConfirmDeleteBorrowDialog)

# UI Constants
BUTTON_WIDTH_STANDARD = 140
BUTTON_WIDTH_WIDE = 150
BUTTON_HEIGHT = 40
SEARCH_HEIGHT = 40

# Color Constants
STATUS_BORROWED = "#FFA500"
STATUS_RETURNED = "#228C3A"
STATUS_OVERDUE = "#DC3545"
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
    "Book ID", "Member ID", "Book Title", "Borrow Date",
    "Due Date", "Return Date", "Status", "Fine Amount", "Updated At"
]
COLUMN_WIDTHS = [80, 90, 300, 180, 180, 180, 100, 120, 180]
COLUMN_NAMES = [
    'book_id', 'member_id', 'book_title', 'borrow_date',
    'due_date', 'return_date', 'status', 'fine_amount', 'updated_at'
]

class CirculationManagement(QMainWindow):
    """Circulation Management screen"""

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.all_borrows = []
        self.filtered_borrows = []
        self.selected_borrow_id = None
        self.sort_column = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.setWindowTitle("Curatel - Circulation Management")
        try:
            self.setup_ui()
            self.load_borrows_from_database()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Circulation Management: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to initialize Circulation Management:\n{str(e)}")
    
    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.mousePressEvent = self.clear_selection
        central_widget.setStyleSheet("background-color: white;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        
        # Header section
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Circulation Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_text.addWidget(title)

        subtitle = QLabel("Monitor issued books, returns, and charges")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333;")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by book id, member id, or book title")
        self.search_input.setStyleSheet("""
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
        """)
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.filter_borrows)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        status_label = QLabel("Status")
        status_label.setFont(QFont("Montserrat", 10))
        status_label.setStyleSheet("color: #000000;")
        search_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Borrowed", "Returned", "Overdue"])
        self.status_combo.setStyleSheet("""
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
        """)
        self.status_combo.setFixedSize(120, 40)
        self.status_combo.currentTextChanged.connect(self.filter_borrows)
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)
        main_layout.addSpacing(5)
        
        # Borrowing records table
        self.borrows_table = QTableWidget()
        self.borrows_table.setColumnCount(9)
        self.borrows_table.setSortingEnabled(False)
        self.borrows_table.setHorizontalHeaderLabels(["Book ID", "Member ID", "Book Title", 
                                                    "Borrow Date", "Due Date", "Return Date", 
                                                        "Status", "Fine Amount", "Updated At"])
        
        self.borrows_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.borrows_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.borrows_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.borrows_table.setAlternatingRowColors(True)
        self.borrows_table.setStyleSheet("""
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
        """)
        
        header = self.borrows_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.borrows_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self.handle_header_click)
        
        self.borrows_table.setColumnWidth(0, 80)
        self.borrows_table.setColumnWidth(1, 90)
        self.borrows_table.setColumnWidth(2, 300)
        self.borrows_table.setColumnWidth(3, 180)
        self.borrows_table.setColumnWidth(4, 180)
        self.borrows_table.setColumnWidth(5, 180)
        self.borrows_table.setColumnWidth(6, 100)
        self.borrows_table.setColumnWidth(7, 120)
        self.borrows_table.setColumnWidth(8, 180)
        
        self.borrows_table.verticalHeader().setVisible(False)
        self.borrows_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.borrows_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.borrows_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.borrows_table.itemSelectionChanged.connect(self.on_selection_changed)

        main_layout.addWidget(self.borrows_table)
        main_layout.addSpacing(5)

        # Action buttons
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Transaction")
        add_btn.setFont(QFont("Montserrat", 10))
        add_btn.setFixedSize(140, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        add_btn.clicked.connect(self.add_borrow)
        action_layout.addWidget(add_btn)

        view_btn = QPushButton("View Transaction")
        view_btn.setFont(QFont("Montserrat", 10))
        view_btn.setFixedSize(140, 40)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        view_btn.clicked.connect(self.view_borrow)
        action_layout.addWidget(view_btn)
        
        update_btn = QPushButton("Update Transaction")
        update_btn.setFont(QFont("Montserrat", 10))
        update_btn.setFixedSize(150, 40)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        update_btn.clicked.connect(self.update_borrow)
        action_layout.addWidget(update_btn)
        
        delete_btn = QPushButton("Delete Transaction")
        delete_btn.setFont(QFont("Montserrat", 10))
        delete_btn.setFixedSize(150, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        delete_btn.clicked.connect(self.delete_borrow)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFont(QFont("Montserrat", 10))
        back_btn.setFixedSize(150, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_dashboard)
        action_layout.addWidget(back_btn)
        
        main_layout.addLayout(action_layout)

    def _get_status_color(self, status):
        """Get color for transaction status."""
        color_map = {
            'Borrowed': STATUS_BORROWED,
            'Returned': STATUS_RETURNED,
            'Overdue': STATUS_OVERDUE
        }
        return color_map.get(status, TEXT_BLACK)

    def _format_return_date(self, return_date):
        """Format return date, show blank if NULL."""
        if return_date is None or str(return_date).strip().lower() in ('none', 'null', ''):
            return ""
        return str(return_date)
    
    def on_selection_changed(self):
        """Track selected borrow when selection changes"""
        try:
            selected_row = self.borrows_table.currentRow()
            if selected_row >= 0 and selected_row < len(self.filtered_borrows):
                self.selected_borrow_id = self.filtered_borrows[selected_row]['borrow_id']
                print(f"[INFO] Selected borrow_id: {self.selected_borrow_id}")
            else:
                self.selected_borrow_id = None
        except Exception as e:
            print(f"[ERROR] Selection change error: {e}")
            import traceback
            traceback.print_exc()
            self.selected_borrow_id = None
    
    def clear_selection(self, event):
        """Clear table selection when clicking empty space"""
        try:
            if self.borrows_table:
                self.borrows_table.clearSelection()
                self.selected_borrow_id = None
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] clear_selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)
    
    def handle_header_click(self, logical_index):
        """Handle column header click for sorting"""
        try:
            if self.sort_column == logical_index:
                self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                self.sort_column = logical_index
                self.sort_order = Qt.SortOrder.AscendingOrder
            
            self.filter_borrows()
        except Exception as e:
            print(f"[ERROR] Header click error: {e}")
            QMessageBox.warning(self, "Error", "Failed to sort table")

    def load_borrows_from_database(self):
        """Load all borrowing records from database"""
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection")
            QMessageBox.warning(self, "Database Error", "Not connected to database.")
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
                print(f"[OK] Loaded {len(self.all_borrows)} borrowing records")
                self.filter_borrows()
            else:
                print("[WARNING] No borrowing records found")
                self.borrows_table.setRowCount(0)
                self.filtered_borrows = []
                
        except Exception as e:
            print(f"[ERROR] Failed to load borrowing records: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load borrowing records:\n{str(e)}")
    
    def display_borrows(self, borrows):
        """FIXED: Display borrowing records - show BLANK for NULL return_date"""
        try:
            self.borrows_table.setRowCount(len(borrows))
            
            for row, borrow in enumerate(borrows):    
                # Book ID
                item = QTableWidgetItem(str(borrow['book_id']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 0, item)
                
                # Member ID
                item = QTableWidgetItem(str(borrow['member_id']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 1, item)
                
                # Book Title
                book_title = str(borrow.get('book_title', 'Unknown'))
                item = QTableWidgetItem(book_title)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 2, item)
                
                # Borrow Date
                borrow_date = str(borrow['borrow_date']) if borrow['borrow_date'] else ""
                item = QTableWidgetItem(borrow_date)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 3, item)
                
                # Due Date
                due_date = str(borrow['due_date']) if borrow['due_date'] else ""
                item = QTableWidgetItem(due_date)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 4, item)
                
                # FIXED: Return Date - SHOW BLANK IF NULL/NONE
                return_date_raw = borrow.get('return_date')
                if return_date_raw is None or str(return_date_raw).strip().lower() in ('none', 'null', ''):
                    return_date = ""  # Show as blank/empty
                else:
                    return_date = str(return_date_raw)
                
                item = QTableWidgetItem(return_date)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 5, item)
                
                # Status with color
                item = QTableWidgetItem(str(borrow['status']))
                item.setFont(QFont("Montserrat", 10))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                if borrow['status'] == 'Borrowed':
                    item.setForeground(QColor("#FFA500"))
                elif borrow['status'] == 'Returned':
                    item.setForeground(QColor("#228C3A"))
                elif borrow['status'] == 'Overdue':
                    item.setForeground(QColor("#DC3545"))
                self.borrows_table.setItem(row, 6, item)
                
                # Fine Amount
                fine = f"₱{float(borrow['fine_amount']):.2f}"
                item = QTableWidgetItem(fine)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 7, item)
                
                # Updated At
                updated_at = str(borrow['updated_at']) if borrow['updated_at'] else ""
                item = QTableWidgetItem(updated_at)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.borrows_table.setItem(row, 8, item)
        except Exception as e:
            print(f"[ERROR] Display borrows error: {e}")
            import traceback
            traceback.print_exc()
    
    def filter_borrows(self):
        """Filter borrowing records based on search and status"""
        try:
            if not self.all_borrows:
                self.filtered_borrows = []
                return
            
            search_text = self.search_input.text().lower().strip()
            status = self.status_combo.currentText()
            
            filtered_borrows = []
            
            for borrow in self.all_borrows:
                if status != "All" and borrow['status'] != status:
                    continue
                
                if search_text:
                    book_title = str(borrow.get('book_title', '')).lower()
                    if not (search_text in str(borrow['book_id']).lower() or
                            search_text in str(borrow['member_id']).lower() or
                            search_text in book_title):
                        continue
                
                filtered_borrows.append(borrow)
            
            # Apply sorting
            if self.sort_column is not None and filtered_borrows:
                column_names = ['book_id', 'member_id', 'book_title', 'borrow_date', 'due_date', 'return_date', 'status', 'fine_amount', 'updated_at']
                if self.sort_column < len(column_names):
                    sort_key = column_names[self.sort_column]
                    filtered_borrows.sort(
                        key=lambda x: str(x.get(sort_key, '')).lower(),
                        reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
                    )
            
            self.filtered_borrows = filtered_borrows
            
            self.display_borrows(filtered_borrows)
            print(f"[INFO] Filtered to {len(filtered_borrows)} borrowing records")
        except Exception as e:
            print(f"[ERROR] Filter borrows error: {e}")
            import traceback
            traceback.print_exc()
    
    def add_borrow(self):
        """Open add borrowing transaction dialog"""
        try:
            dialog = AddBorrowDialog(self, self.db, self.load_borrows_from_database)
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add borrow error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", "Failed to open add transaction dialog")
    
    def view_borrow(self):
        """View selected borrowing transaction"""
        try:
            if not self.selected_borrow_id:
                QMessageBox.warning(self, "No Selection", "Please select a transaction to view")
                return
            
            query = """
            SELECT bb.*, b.title as book_title, m.full_name as member_name
            FROM borrowed_books bb
            LEFT JOIN books b ON bb.book_id = b.book_id
            LEFT JOIN members m ON bb.member_id = m.member_id
            WHERE bb.borrow_id = %s
            """
            borrow_data = self.db.fetch_one(query, (self.selected_borrow_id,))
            
            if borrow_data:
                dialog = ViewBorrowDialog(self, borrow_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Transaction not found in database")
                self.load_borrows_from_database()
        except Exception as e:
            print(f"[ERROR] View borrow error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to view transaction:\n{str(e)}")

    def update_borrow(self):
        """Open update borrowing transaction dialog - FIXED: Fetch fresh data from DB"""
        try:
            if not self.selected_borrow_id:
                QMessageBox.warning(self, "No Selection", "Please select a transaction to update")
                return
            
            # ✅ CRITICAL FIX: Fetch the FULL row directly from database to preserve original dates
            query = """
            SELECT bb.*, b.title as book_title, m.full_name as member_name
            FROM borrowed_books bb
            LEFT JOIN books b ON bb.book_id = b.book_id
            LEFT JOIN members m ON bb.member_id = m.member_id
            WHERE bb.borrow_id = %s
            """
            borrow_data = self.db.fetch_one(query, (self.selected_borrow_id,))
            
            if not borrow_data:
                QMessageBox.warning(self, "Error", "Transaction not found in database")
                self.load_borrows_from_database()
                return
            
            # Build complete data with original dates preserved
            complete_borrow_data = {
                "borrow_id": borrow_data.get('borrow_id'),
                "book_id": borrow_data.get('book_id', ''),
                "member_id": borrow_data.get('member_id', ''),
                "book_title": borrow_data.get('book_title', 'Unknown'),
                "member_name": borrow_data.get('member_name', ''),
                "borrow_date": borrow_data.get('borrow_date', ''),      # ← Original from DB
                "due_date": borrow_data.get('due_date', ''),            # ← Original from DB
                "return_date": borrow_data.get('return_date', None),
                "status": borrow_data.get('status', 'Borrowed'),
                "fine_amount": float(borrow_data.get('fine_amount', 0.0))
            }
            
            dialog = UpdateBorrowDialog(
                parent=self,
                db=self.db,
                borrow_data=complete_borrow_data,
                callback=self.load_borrows_from_database
            )
            
            dialog.exec()
                
        except Exception as e:
            print(f"[ERROR] Update borrow error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to open update transaction dialog:\n{str(e)}")


    def delete_borrow(self):
        """Delete selected borrowing transaction"""
        try:
            if not self.selected_borrow_id:
                QMessageBox.warning(self, "No Selection", "Please select a transaction to delete")
                return
            
            borrow_data = None
            for borrow in self.filtered_borrows:
                if borrow['borrow_id'] == self.selected_borrow_id:
                    borrow_data = borrow
                    break
            
            if not borrow_data:
                QMessageBox.warning(self, "Error", "Transaction not found")
                self.load_borrows_from_database()
                return
            
            book_id = borrow_data['book_id']
            member_id = borrow_data['member_id']
            
            dialog = ConfirmDeleteBorrowDialog(self, book_id, member_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                query = "DELETE FROM borrowed_books WHERE borrow_id = %s"
                if self.db.execute_query(query, (self.selected_borrow_id,)):
                    QMessageBox.information(self, "Success", "Transaction deleted successfully!")
                    self.selected_borrow_id = None
                    self.load_borrows_from_database()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete transaction from database")
        except Exception as e:
            print(f"[ERROR] Delete borrow error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to delete transaction:\n{str(e)}")
    
    def go_back_to_dashboard(self):
        """Go back to dashboard"""
        try:
            self.close()
        except Exception as e:
            print(f"[ERROR] Go back error: {e}")
    
    def show_fullscreen(self):
        """Show window maximized"""
        try:
            self.setWindowState(Qt.WindowState.WindowMaximized)
            self.showMaximized()
        except Exception as e:
            print(f"[ERROR] Show fullscreen error: {e}")
    
    def closeEvent(self, event):
        """Handle window close"""
        try:
            event.accept()
        except Exception as e:
            print(f"[ERROR] Close event error: {e}")
            event.accept()