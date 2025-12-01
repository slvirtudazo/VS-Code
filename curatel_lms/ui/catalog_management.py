# ui/catalog_management.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                              QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Import the dialogs
from curatel_lms.ui.dialogs import (AddBookDialog, ViewBookDialog, 
                                     UpdateBookDialog, ConfirmDeleteDialog)

class CatalogManagement(QMainWindow):
    """Catalog Management screen"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.all_books = []  # Store all books for filtering
        self.setWindowTitle("Curatel - Catalog Management")
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
        self.search_input.textChanged.connect(self.filter_books)
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
            QComboBox:focus {
                border: 2px solid #6B5E46;
            }
            QComboBox QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: black;
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
        self.status_combo.setFixedSize(120, 35)
        self.status_combo.currentTextChanged.connect(self.filter_books)
        search_layout.addWidget(self.status_combo)
        
        main_layout.addLayout(search_layout)
        
        # Books table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(8)
        self.books_table.setSortingEnabled(False)
        self.books_table.setHorizontalHeaderLabels(["Book ID", "Title", "Author", "ISBN", "Category", "Status", "Added At", "Updated At"])
        
        self.books_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.books_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setStyleSheet("""
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
        
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  
        self.books_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionsClickable(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        header.setSectionsMovable(False)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)
        
        self.books_table.setColumnWidth(0, 100)
        self.books_table.setColumnWidth(2, 180)
        self.books_table.setColumnWidth(3, 150)
        self.books_table.setColumnWidth(4, 120)
        self.books_table.setColumnWidth(5, 110)
        self.books_table.setColumnWidth(6, 120)
        self.books_table.setColumnWidth(7, 120)
        
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.books_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.books_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout.addWidget(self.books_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Book")
        add_btn.setFont(QFont("Montserrat", 10))
        add_btn.setFixedSize(120, 40)
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
            if self.books_table:
                self.books_table.clearSelection()
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "category_combo"):
                self.category_combo.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] clear_selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)

    def load_books_from_database(self):
        """Load all books from database"""
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection")
            QMessageBox.warning(self, "Database Error", "Not connected to database.")
            return
        
        try:
            query = "SELECT * FROM books ORDER BY book_id"
            self.all_books = self.db.fetch_all(query)
            
            if self.all_books:
                print(f"[OK] Loaded {len(self.all_books)} books")
                self.display_books(self.all_books)
            else:
                print("[WARNING] No books found")
                
        except Exception as e:
            print(f"[ERROR] Failed to load books: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")
    
    def display_books(self, books):
        """Display books in the table"""
        self.books_table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            # Book ID
            item = QTableWidgetItem(str(book['book_id']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 0, item)
            
            # Title
            item = QTableWidgetItem(str(book['title']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 1, item)
            
            # Author
            item = QTableWidgetItem(str(book['author']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 2, item)
            
            # ISBN
            item = QTableWidgetItem(str(book['isbn']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 3, item)
            
            # Category
            item = QTableWidgetItem(str(book['category']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 4, item)
            
            # Status with color
            item = QTableWidgetItem(str(book['status']))
            item.setFont(QFont("Montserrat", 10))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            if book['status'] == 'Available':
                item.setForeground(QColor("#228C3A"))
            else:
                item.setForeground(QColor("#DC3545"))
            self.books_table.setItem(row, 5, item)
            
            # Added At
            added_at = str(book['added_at']).split()[0] if book['added_at'] else ""
            item = QTableWidgetItem(added_at)
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 6, item)
            
            # Updated At
            updated_at = str(book['updated_at']).split()[0] if book['updated_at'] else ""
            item = QTableWidgetItem(updated_at)
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.books_table.setItem(row, 7, item)
    
    def filter_books(self):
        """Filter books based on search and combo selections"""
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
            
            # Search filter
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
        """Open add book dialog"""
        dialog = AddBookDialog(self, self.db, self.load_books_from_database)
        dialog.exec()
    
    def view_book(self):
        """View selected book"""
        selected_row = self.books_table.currentRow()
        if selected_row >= 0:
            book_id = self.books_table.item(selected_row, 0).text()
            
            # Get full book data from database
            query = "SELECT * FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (book_id,))
            
            if book_data:
                dialog = ViewBookDialog(self, book_data)
                dialog.exec()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to view")

    def update_book(self):
        """Update selected book"""
        selected_row = self.books_table.currentRow()
        if selected_row >= 0:
            book_id = self.books_table.item(selected_row, 0).text()
            
            # Get full book data from database
            query = "SELECT * FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (book_id,))
            
            if book_data:
                dialog = UpdateBookDialog(self, self.db, book_data, self.load_books_from_database)
                dialog.exec()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to update")
    
    def delete_book(self):
        """Delete selected book"""
        selected_row = self.books_table.currentRow()
        if selected_row >= 0:
            book_id = self.books_table.item(selected_row, 0).text()
            book_title = self.books_table.item(selected_row, 1).text()
            
            # Show confirmation dialog
            dialog = ConfirmDeleteDialog(self, book_title)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Delete from database
                query = "DELETE FROM books WHERE book_id = %s"
                if self.db.execute_query(query, (book_id,)):
                    QMessageBox.information(self, "Success", f"Book '{book_title}' deleted successfully!")
                    self.load_books_from_database()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete book from database")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a book to delete")
    
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