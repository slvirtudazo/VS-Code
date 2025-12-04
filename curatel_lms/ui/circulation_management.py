# ui/circulation_management.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                              QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Import the dialogs
from curatel_lms.ui.circulation_dialogs import (AddBorrowDialog, ViewBorrowDialog, 
                                                 UpdateBorrowDialog, ConfirmDeleteBorrowDialog)

class CirculationManagement(QMainWindow):
    """Circulation Management screen - manages book borrowing transactions"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.all_borrows = []  # Store all borrowing records for filtering
        self.setWindowTitle("Curatel - Circulation Management")
        try:
            self.setup_ui()
            self.load_borrows_from_database()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Circulation Management: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup UI matching patron management design"""
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
                background-color: #D9CFC2;
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
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.borrows_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionsClickable(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Column width resize
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)

        # Set column widths
        self.borrows_table.setColumnWidth(0, 80)    # Book ID
        self.borrows_table.setColumnWidth(1, 90)    # Member ID
        self.borrows_table.setColumnWidth(2, 300)   # Book Title
        self.borrows_table.setColumnWidth(3, 180)   # Borrow Date
        self.borrows_table.setColumnWidth(4, 180)   # Due Date
        self.borrows_table.setColumnWidth(5, 180)   # Return Date
        self.borrows_table.setColumnWidth(6, 100)   # Status
        self.borrows_table.setColumnWidth(7, 120)   # Fine Amount
        self.borrows_table.setColumnWidth(8, 180)   # Updated At

        
        self.borrows_table.verticalHeader().setVisible(False)
        self.borrows_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.borrows_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.borrows_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout.addWidget(self.borrows_table)
        main_layout.addSpacing(5)

        # Action buttons matching patron management
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
    
    def clear_selection(self, event):
        """Clear table selection when clicking empty space"""
        try:
            if self.borrows_table:
                self.borrows_table.clearSelection()
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] clear_selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)

    def load_borrows_from_database(self):
        """Load all borrowing records from database with book titles"""
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection")
            QMessageBox.warning(self, "Database Error", "Not connected to database.")
            return
        
        try:
            # Join borrowed_books with books table to get book titles
            query = """
            SELECT bb.*, b.title as book_title 
            FROM borrowed_books bb
            LEFT JOIN books b ON bb.book_id = b.book_id
            ORDER BY bb.borrow_id DESC
            """
            self.all_borrows = self.db.fetch_all(query)
            
            if self.all_borrows:
                print(f"[OK] Loaded {len(self.all_borrows)} borrowing records")
                self.display_borrows(self.all_borrows)
            else:
                print("[WARNING] No borrowing records found")
                
        except Exception as e:
            print(f"[ERROR] Failed to load borrowing records: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load borrowing records: {str(e)}")
    
    def display_borrows(self, borrows):
        """Display borrowing records in the table"""
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
            
            # Return Date
            return_date = str(borrow['return_date']) if borrow['return_date'] else "Not Returned"
            item = QTableWidgetItem(return_date)
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.borrows_table.setItem(row, 5, item)
            
            # Status with color coding
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
            
            # Updated At - Display full datetime matching patron management format
            updated_at = str(borrow['updated_at']) if borrow['updated_at'] else ""
            item = QTableWidgetItem(updated_at)
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.borrows_table.setItem(row, 8, item)
    
    def filter_borrows(self):
        """Filter borrowing records based on search and status"""
        if not self.all_borrows:
            return
        
        search_text = self.search_input.text().lower().strip()
        status = self.status_combo.currentText()
        
        filtered_borrows = []
        
        for borrow in self.all_borrows:
            # Status filter
            if status != "All" and borrow['status'] != status:
                continue
            
            # Search filter
            if search_text:
                book_title = str(borrow.get('book_title', '')).lower()
                if not (search_text in str(borrow['book_id']).lower() or
                        search_text in str(borrow['member_id']).lower() or
                        search_text in book_title):
                    continue
            
            filtered_borrows.append(borrow)
        
        self.display_borrows(filtered_borrows)
        print(f"[INFO] Filtered to {len(filtered_borrows)} borrowing records")
    
    def add_borrow(self):
        """Open add borrowing transaction dialog"""
        dialog = AddBorrowDialog(self, self.db, self.load_borrows_from_database)
        dialog.exec()
    
    def view_borrow(self):
        """View selected borrowing transaction"""
        selected_row = self.borrows_table.currentRow()
        if selected_row >= 0:
            borrow_id = self.all_borrows[selected_row]['borrow_id']
            
            # Get full borrow data from database
            query = """
            SELECT bb.*, b.title as book_title, m.full_name as member_name
            FROM borrowed_books bb
            LEFT JOIN books b ON bb.book_id = b.book_id
            LEFT JOIN members m ON bb.member_id = m.member_id
            WHERE bb.borrow_id = %s
            """
            borrow_data = self.db.fetch_one(query, (borrow_id,))
            
            if borrow_data:
                dialog = ViewBorrowDialog(self, borrow_data)
                dialog.exec()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to view")

    def update_borrow(self):
        """Update selected borrowing transaction"""
        selected_row = self.borrows_table.currentRow()
        if selected_row >= 0:
            borrow_id = self.all_borrows[selected_row]['borrow_id']
            
            # Get full borrow data from database
            query = """
            SELECT bb.*, b.title as book_title, m.full_name as member_name
            FROM borrowed_books bb
            LEFT JOIN books b ON bb.book_id = b.book_id
            LEFT JOIN members m ON bb.member_id = m.member_id
            WHERE bb.borrow_id = %s
            """
            borrow_data = self.db.fetch_one(query, (borrow_id,))
            
            if borrow_data:
                dialog = UpdateBorrowDialog(self, self.db, borrow_data, self.load_borrows_from_database)
                dialog.exec()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to update")
    
    def delete_borrow(self):
        """Delete selected borrowing transaction"""
        selected_row = self.borrows_table.currentRow()
        if selected_row >= 0:
            borrow_id = self.all_borrows[selected_row]['borrow_id']
            book_id = self.borrows_table.item(selected_row, 1).text()
            member_id = self.borrows_table.item(selected_row, 2).text()
            
            # Show confirmation dialog
            dialog = ConfirmDeleteBorrowDialog(self, book_id, member_id)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Delete from database
                query = "DELETE FROM borrowed_books WHERE borrow_id = %s"
                if self.db.execute_query(query, (borrow_id,)):
                    QMessageBox.information(self, "Success", 
                                          f"Transaction deleted successfully!")
                    self.load_borrows_from_database()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete transaction from database")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to delete")
    
    def go_back_to_dashboard(self):
        """Go back to dashboard"""
        self.close()
    
    def show_fullscreen(self):
        """Show window maximized"""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        """Handle window close"""
        event.accept()