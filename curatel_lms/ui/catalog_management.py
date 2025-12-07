# curatel_lms/ui/catalog_management.py

"""
Catalog management module.
Main window for managing library book inventory.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtGui import QFont, QColor

from curatel_lms.ui.catalog_dialogs import (
    AddBookDialog, ViewBookDialog, UpdateBookDialog, ConfirmDeleteDialog
)

# UI Constants
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
SEARCH_HEIGHT = 40

# Color Constants
STATUS_AVAILABLE = "#228C3A"
STATUS_BORROWED = "#DC3545"
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

# Table column configuration
TABLE_COLUMNS = ["Book ID", "Title", "Author", "ISBN", "Category", "Status", "Added At", "Updated At"]
COLUMN_WIDTHS = [80, 300, 180, 150, 140, 160, 200, 220]
COLUMN_NAMES = ['book_id', 'title', 'author', 'isbn', 'category', 'status', 'added_at', 'updated_at']


class CatalogManagement(QMainWindow):
    """Main window for catalog management operations."""
    
    def __init__(self, db=None):
        """
        Initialize catalog management window.
        Args:
            db: Database connection object
        """
        super().__init__()
        self.db = db
        self.all_books = []
        self.selected_book_id = None
        self.sort_column = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        
        self.setWindowTitle("Curatel - Catalog Management")
        
        try:
            self._setup_ui()
            self._load_books_from_database()
            self._show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Catalog Management: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Error",
                f"Failed to initialize Catalog Management:\n{str(e)}"
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
        main_layout.addWidget(self._create_books_table())
        main_layout.addSpacing(5)
        main_layout.addLayout(self._create_action_buttons())
    
    def _create_header(self):
        """
        Create header section with title and subtitle.
        Returns: QHBoxLayout containing header
        """
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
        self.search_input.setPlaceholderText("Search by id, title, author, or isbn")
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.setFixedHeight(SEARCH_HEIGHT)
        self.search_input.textChanged.connect(self._filter_books)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        # Category filter
        search_layout.addWidget(self._create_label("Category"))
        self.category_combo = self._create_combo(
            ["All", "Adventure", "Art", "Biography", "Business", "Cooking",
             "Fantasy", "Fiction", "History", "Horror", "Mystery", "Non-Fiction",
             "Poetry", "Romance", "Science", "Technology"]
        )
        search_layout.addWidget(self.category_combo)
        search_layout.addSpacing(30)
        
        # Status filter
        search_layout.addWidget(self._create_label("Status"))
        self.status_combo = self._create_combo(["All", "Available", "Borrowed"])
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
        combo.currentTextChanged.connect(self._filter_books)
        return combo
    
    def _create_books_table(self):
        """
        Create books table widget.
        Returns: QTableWidget configured for books
        """
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(len(TABLE_COLUMNS))
        self.books_table.setSortingEnabled(False)
        self.books_table.setHorizontalHeaderLabels(TABLE_COLUMNS)
        
        # Configure table behavior
        self.books_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.books_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setStyleSheet(TABLE_STYLE)
        
        # Configure header
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self._handle_header_click)
        
        # Set column widths
        for col, width in enumerate(COLUMN_WIDTHS):
            self.books_table.setColumnWidth(col, width)
        
        # Configure scrolling
        self.books_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.books_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.books_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Connect selection signal
        self.books_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        return self.books_table
    
    def _create_action_buttons(self):
        """
        Create action button layout.
        Returns: QHBoxLayout containing action buttons
        """
        action_layout = QHBoxLayout()
        
        # CRUD buttons
        buttons = [
            ("Add Book", self._add_book),
            ("View Book", self._view_book),
            ("Update Book", self._update_book),
            ("Delete Book", self._delete_book)
        ]
        
        for text, callback in buttons:
            btn = self._create_button(text, callback)
            action_layout.addWidget(btn)
        
        action_layout.addStretch()
        
        # Back button
        back_btn = self._create_button("Back to Dashboard", self._go_back_to_dashboard)
        back_btn.setFixedSize(150, BUTTON_HEIGHT)
        action_layout.addWidget(back_btn)
        
        return action_layout
    
    def _create_button(self, text, callback):
        """
        Create styled button.
        Args:
            text: Button text
            callback: Click callback function
        Returns: QPushButton
        """
        btn = QPushButton(text)
        btn.setFont(QFont("Montserrat", 10))
        btn.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        btn.setStyleSheet(BUTTON_STYLE)
        btn.clicked.connect(callback)
        return btn
    
    def _on_selection_changed(self):
        """Track selected book when selection changes."""
        try:
            selected_row = self.books_table.currentRow()
            if selected_row >= 0:
                self.selected_book_id = self.books_table.item(selected_row, 0).text()
            else:
                self.selected_book_id = None
        except Exception as e:
            print(f"[ERROR] Selection change: {e}")
            self.selected_book_id = None
    
    def _clear_selection(self, event):
        """Clear table selection when clicking empty space."""
        try:
            if self.books_table:
                self.books_table.clearSelection()
                self.selected_book_id = None
            
            # Clear focus from input widgets
            for widget in [self.search_input, self.category_combo, self.status_combo]:
                if hasattr(self, widget.__class__.__name__.lower().replace('q', '')):
                    widget.clearFocus()
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
            
            self._filter_books()
        except Exception as e:
            print(f"[ERROR] Header click: {e}")
            QMessageBox.warning(self, "Error", "Failed to sort table")
    
    def _load_books_from_database(self):
        """Load all books from database."""
        if not self._validate_database_connection():
            return
        
        try:
            query = "SELECT * FROM books ORDER BY book_id"
            self.all_books = self.db.fetch_all(query)
            
            if self.all_books:
                print(f"[OK] Loaded {len(self.all_books)} books")
                self._filter_books()
            else:
                print("[WARNING] No books found")
                self.books_table.setRowCount(0)
                
        except Exception as e:
            print(f"[ERROR] Failed to load books: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load books:\n{str(e)}")
    
    def _display_books(self, books):
        """
        Display books in table.
        Args:
            books: List of book dictionaries
        """
        try:
            self.books_table.setRowCount(len(books))
            
            for row, book in enumerate(books):
                for col, key in enumerate(COLUMN_NAMES):
                    value = str(book.get(key, ''))
                    item = self._create_table_item(value)
                    
                    # Apply status color
                    if col == 5:  # Status column
                        color = STATUS_AVAILABLE if book['status'] == 'Available' else STATUS_BORROWED
                        item.setForeground(QColor(color))
                    
                    self.books_table.setItem(row, col, item)
                    
        except Exception as e:
            print(f"[ERROR] Display books: {e}")
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
    
    def _filter_books(self):
        """Filter books based on search criteria."""
        try:
            if not self.all_books:
                return
            
            search_text = self.search_input.text().lower().strip()
            category = self.category_combo.currentText()
            status = self.status_combo.currentText()
            
            # Apply filters
            filtered_books = [
                book for book in self.all_books
                if self._matches_filters(book, search_text, category, status)
            ]
            
            # Apply sorting
            if self.sort_column is not None and filtered_books:
                filtered_books = self._sort_books(filtered_books)
            
            self._display_books(filtered_books)
            print(f"[INFO] Filtered to {len(filtered_books)} books")
            
        except Exception as e:
            print(f"[ERROR] Filter books: {e}")
            import traceback
            traceback.print_exc()
    
    def _matches_filters(self, book, search_text, category, status):
        """
        Check if book matches filter criteria.
        Args:
            book: Book dictionary
            search_text: Search string
            category: Category filter
            status: Status filter
        Returns: True if matches, False otherwise
        """
        if category != "All" and book['category'] != category:
            return False
        
        if status != "All" and book['status'] != status:
            return False
        
        if search_text:
            searchable = [
                str(book.get('book_id', '')),
                str(book.get('title', '')),
                str(book.get('author', '')),
                str(book.get('isbn', ''))
            ]
            if not any(search_text in field.lower() for field in searchable):
                return False
        
        return True
    
    def _sort_books(self, books):
        """
        Sort books by selected column.
        Args:
            books: List of book dictionaries
        Returns: Sorted list
        """
        if self.sort_column < len(COLUMN_NAMES):
            sort_key = COLUMN_NAMES[self.sort_column]
            return sorted(
                books,
                key=lambda x: str(x.get(sort_key, '')).lower(),
                reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
            )
        return books
    
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
        Validate book selection.
        Returns: True if book selected, False otherwise
        """
        if not self.selected_book_id:
            QMessageBox.warning(self, "No Selection", "Please select a book first.")
            return False
        return True
    
    def _add_book(self):
        """Open add book dialog."""
        try:
            dialog = AddBookDialog(self, self.db, self._load_books_from_database)
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add book: {e}")
            QMessageBox.critical(self, "Error", "Failed to open add book dialog")
    
    def _view_book(self):
        """View selected book."""
        if not self._validate_selection():
            return
        
        try:
            query = "SELECT * FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (self.selected_book_id,))
            
            if book_data:
                dialog = ViewBookDialog(self, book_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Book not found in database")
                self._load_books_from_database()
                
        except Exception as e:
            print(f"[ERROR] View book: {e}")
            QMessageBox.critical(self, "Error", f"Failed to view book:\n{str(e)}")
    
    def _update_book(self):
        """Update selected book."""
        if not self._validate_selection():
            return
        
        try:
            query = "SELECT * FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (self.selected_book_id,))
            
            if book_data:
                dialog = UpdateBookDialog(self, self.db, book_data, self._load_books_from_database)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Book not found in database")
                self._load_books_from_database()
                
        except Exception as e:
            print(f"[ERROR] Update book: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update book:\n{str(e)}")
    
    def _delete_book(self):
        """Delete selected book."""
        if not self._validate_selection():
            return
        
        try:
            query = "SELECT title FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (self.selected_book_id,))
            
            if not book_data:
                QMessageBox.warning(self, "Error", "Book not found in database")
                self._load_books_from_database()
                return
            
            dialog = ConfirmDeleteDialog(self, book_data['title'])
            if dialog.exec() == QDialog.DialogCode.Accepted:
                delete_query = "DELETE FROM books WHERE book_id = %s"
                if self.db.execute_query(delete_query, (self.selected_book_id,)):
                    QMessageBox.information(
                        self, "Success",
                        f"Book '{book_data['title']}' deleted successfully!"
                    )
                    self.selected_book_id = None
                    self._load_books_from_database()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete book")
                    
        except Exception as e:
            print(f"[ERROR] Delete book: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete book:\n{str(e)}")
    
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