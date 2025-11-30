# ui/catalog_management.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                              QComboBox, QMessageBox, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

class CatalogManagement(QMainWindow):
    """Catalog Management screen"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.all_books = []  # Store all books for filtering
        self.setWindowTitle("Catalog Management - Curatel LMS")
        try:
            self.setup_ui()
            self.load_books_from_database()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Catalog Management: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.mousePressEvent = self.clear_selection
        central_widget.setStyleSheet("background-color: #C9B8A8;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-10)
        
        # Header
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Catalog Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_text.addWidget(title)

        subtitle = QLabel("Organize, update, and track books in the library")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333;")
        header_text.addWidget(subtitle)
        header_text.addSpacing(20)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by id, title, author, or isbn")
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
        self.search_input.setFixedHeight(38)
        self.search_input.textChanged.connect(self.filter_books)  # Real-time search
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(20)
        
        category_label = QLabel("Category")
        category_label.setFont(QFont("Montserrat", 10))
        category_label.setStyleSheet("color: #000000;")
        search_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Adventure", "Art", "Biography", "Business", 
                                       "Cooking", "Fantasy", "Fiction", "History", "Horror", 
                                       "Mystery", "Non-Fiction", "Poetry", "Romance", "Science", "Technology"])
        # --- EDITED: Dropdown text color black ---
        self.category_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #8B7E66;
                border-radius: 10px;
                padding: 5px 10px;
                font-family: Montserrat;
                font-size: 12px;
                color: #000000;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6B5E46;
            }
            QComboBox QAbstractItemView {
                color: #000000;
                background-color: white;
                selection-background-color: #D9CFC2;
                selection-color: black;
            }
        """)
        self.category_combo.setFixedSize(120, 35)
        self.category_combo.currentTextChanged.connect(self.filter_books)
        search_layout.addWidget(self.category_combo)
        
        search_layout.addSpacing(20)
        
        status_label = QLabel("Status")
        status_label.setFont(QFont("Montserrat", 10))
        status_label.setStyleSheet("color: #000000;")
        search_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Available", "Borrowed"])
        # --- EDITED: Dropdown text color black ---
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
            QLineEdit:focus {
                border: 2px solid #6B5E46;
            }
            QComboBox QAbstractItemView {
                color: #000000;
                background-color: white;
                selection-background-color: #D9CFC2;  /* Full highlight on hover/click */
                selection-color: black;
            }
        """)
        self.status_combo.setFixedSize(120, 35)
        self.status_combo.currentTextChanged.connect(self.filter_books)
        search_layout.addWidget(self.status_combo)
        
        main_layout.addLayout(search_layout)
        
        # Books table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(8)
        self.books_table.setSortingEnabled(False)
        self.books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Author", "ISBN", "Category", "Status", "Added At", "Updated At"])
        
        # Make table cells uneditable but allow row selection
        self.books_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.books_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #8B7E66;
                gridline-color: #8B7E66;
                gridline-width: 1px;  /* Ensure all lines are 1px */
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
                border: none;  /* Remove double-thickness effect */
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
        
        # Configure header and column sizing
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  
        self.books_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionsClickable(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        header.setSectionsMovable(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header.setSectionsClickable(True)
        header.setHighlightSections(False)

        self.books_table.setShowGrid(True)
        self.books_table.setGridStyle(Qt.PenStyle.SolidLine)

        # set individual columns to ResizeToContents too (keeps consistent behavior)
        for i in range(self.books_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

        # Set specific columns to resize based on content for better visibility
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # Book ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)      # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Author
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # ISBN
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Category
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)  # Added At
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)  # Updated At
        
        self.books_table.setColumnWidth(0, 100)
        self.books_table.setColumnWidth(2, 180)
        self.books_table.setColumnWidth(3, 150)
        self.books_table.setColumnWidth(4, 120)
        self.books_table.setColumnWidth(5, 110)
        self.books_table.setColumnWidth(6, 120)
        self.books_table.setColumnWidth(7, 120)
        
        # Make vertical header (row numbers) bold and black with hover/click highlight
        self.books_table.verticalHeader().setVisible(False)

        self.books_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.books_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.books_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout.addWidget(self.books_table)
        
        # Action buttons - moved "Back to Dashboard" to far right
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Book")
        add_btn.setFont(QFont("Montserrat", 10))
        add_btn.setFixedSize(120, 40)
        # --- EDITED: Foreground text black ---
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
        add_btn.clicked.connect(self.add_book)
        action_layout.addWidget(add_btn)

        view_btn = QPushButton("View Book")
        view_btn.setFont(QFont("Montserrat", 10))
        view_btn.setFixedSize(120, 40)
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
        view_btn.clicked.connect(self.view_book)
        action_layout.addWidget(view_btn)
        
        update_btn = QPushButton("Update Book")
        update_btn.setFont(QFont("Montserrat", 10))
        update_btn.setFixedSize(120, 40)
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
        update_btn.clicked.connect(self.update_book)
        action_layout.addWidget(update_btn)
        
        delete_btn = QPushButton("Delete Book")
        delete_btn.setFont(QFont("Montserrat", 10))
        delete_btn.setFixedSize(120, 40)
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
        delete_btn.clicked.connect(self.delete_book)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFont(QFont("Montserrat", 10))  # --- EDITED: Match other buttons ---
        back_btn.setFixedSize(150, 40)  # --- EDITED: Match other buttons ---
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
        action_layout.addWidget(back_btn)  # --- EDITED: Positioned to far right ---
        
        main_layout.addLayout(action_layout)
    
    def clear_selection(self, event):
        """Clear any table selection and remove focus from inputs when clicking empty space.
           NOTE: this does NOT clear search text (per user's choice). """
        try:
            if self.books_table:
                self.books_table.clearSelection()
            # Remove focus from input widgets (keeps their text intact)
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "category_combo"):
                self.category_combo.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] clear_selection encountered error: {e}")
        # call original QWidget mousePressEvent so other behavior isn't blocked
        QWidget.mousePressEvent(self.centralWidget(), event)

    def load_books_from_database(self):
        """Load all books from database"""
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection, showing empty table")
            QMessageBox.warning(self, "Database Error", "Not connected to database. Please check your connection.")
            return
        
        try:
            query = "SELECT * FROM books ORDER BY book_id"
            self.all_books = self.db.fetch_all(query)
            
            if self.all_books:
                print(f"[OK] Loaded {len(self.all_books)} books from database")
                self.display_books(self.all_books)
            else:
                print("[WARNING] No books found in database")
                QMessageBox.information(self, "No Data", "No books found in the database.")
                
        except Exception as e:
            print(f"[ERROR] Failed to load books: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load books from database: {str(e)}")
    
    def display_books(self, books):
        """Display books in the table"""
        self.books_table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            # Book ID - Center aligned, normal weight
            item = QTableWidgetItem(str(book['book_id']))
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 0, item)
            
            # Title - Center aligned, normal weight
            item = QTableWidgetItem(str(book['title']))
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 1, item)
            
            # Author - Center aligned, normal weight
            item = QTableWidgetItem(str(book['author']))
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 2, item)
            
            # ISBN - Center aligned, normal weight
            item = QTableWidgetItem(str(book['isbn']))
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 3, item)
            
            # Category - Center aligned, normal weight
            item = QTableWidgetItem(str(book['category']))
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 4, item)
            
            # Status - Center aligned with color (regular weight now)
            item = QTableWidgetItem(str(book['status']))
            item.setFont(QFont("Montserrat", 10))  # Changed to regular weight
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            # Color code status
            if book['status'] == 'Available':
                item.setForeground(QColor("#228C3A"))  # Green
            else:
                item.setForeground(QColor("#DC3545"))  # Red
            self.books_table.setItem(row, 5, item)
            
            # Added At - Center aligned, normal weight
            added_at = str(book['added_at']).split()[0] if book['added_at'] else ""
            item = QTableWidgetItem(added_at)
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 6, item)
            
            # Updated At - Center aligned, normal weight
            updated_at = str(book['updated_at']).split()[0] if book['updated_at'] else ""
            item = QTableWidgetItem(updated_at)
            item.setFont(QFont("Montserrat", 10))  # Normal weight
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 7, item)
    
    def filter_books(self):
        """Filter books based on search and combo box selections"""
        if not self.all_books:
            return
        
        search_text = self.search_input.text().lower().strip()
        category = self.category_combo.currentText()
        status = self.status_combo.currentText()
        
        filtered_books = []
        
        for book in self.all_books:
            # Category filter
            if category != "All" and book['category'] != category:
                continue
            
            # Status filter
            if status != "All" and book['status'] != status:
                continue
            
            # Search filter (searches in ID, title, author, ISBN)
            if search_text:
                if not (search_text in str(book['book_id']).lower() or
                        search_text in str(book['title']).lower() or
                        search_text in str(book['author']).lower() or
                        search_text in str(book['isbn']).lower()):
                    continue
            
            filtered_books.append(book)
        
        self.display_books(filtered_books)
        print(f"[INFO] Filtered to {len(filtered_books)} books")
    
    def add_book(self):
        """Add new book - placeholder"""
        QMessageBox.information(self, "Add Book", "Add Book functionality will be implemented here")
    
    def view_book(self):
        """View selected book - placeholder"""
        selected_row = self.books_table.currentRow()
        if selected_row >= 0:
            book_id = self.books_table.item(selected_row, 0).text()
            QMessageBox.information(self, "View Book", f"View details for Book ID {book_id}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to view")

    def update_book(self):
        """Update selected book - placeholder"""
        selected_row = self.books_table.currentRow()
        if selected_row >= 0:
            book_id = self.books_table.item(selected_row, 0).text()
            QMessageBox.information(self, "Update Book", f"Update functionality for {book_id} will be implemented here")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to update")
    
    def delete_book(self):
        """Delete selected book - placeholder"""
        selected_row = self.books_table.currentRow()
        if selected_row >= 0:
            book_id = self.books_table.item(selected_row, 0).text()
            reply = QMessageBox.question(self, "Confirm Delete", 
                                        f"Are you sure you want to delete book {book_id}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                QMessageBox.information(self, "Delete", "Delete functionality will be implemented here")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to delete")
    
    def go_back_to_dashboard(self):
        """Go back to dashboard without terminating"""
        self.close()
    
    def show_fullscreen(self):
        """Show window in fixed fullscreen 1920x1080"""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()