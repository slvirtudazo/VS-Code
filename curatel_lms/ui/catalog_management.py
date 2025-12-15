# curatel_lms/ui/catalog_management.py

# Manages library books through search, filter, sort, and full CRUD operations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtGui import QFont, QColor
from curatel_lms.config import AppConfig
from curatel_lms.ui.catalog_dialogs import (
    AddBookDialog, ViewBookDialog, UpdateBookDialog, ConfirmDeleteDialog
)

class CatalogManagement(QMainWindow):
    # Main window for book catalog management with table, filters, and actions

    def __init__(self, db=None):
        # Initialize UI, load books, show maximized; handle errors
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
                self, "Initialization Error",
                f"Failed to initialize Catalog Management:\n{str(e)}"
            )
    
    def _setup_ui(self):
        # Build main layout: header, search, table, action buttons
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
        main_layout.addWidget(self._create_books_table())
        main_layout.addSpacing(5)
        main_layout.addLayout(self._create_action_buttons())
    
    def _create_header(self):
        # Create title and subtitle labels
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Catalog Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
        header_text.addWidget(title)

        subtitle = QLabel("Organize, update, and track books in the library")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet(f"color: {AppConfig.COLORS['text_gray']};")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        return header_layout
    
    def _create_search_section(self):
        # Create search bar and category/status filters
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by id, title, author, or isbn"
        )
        self.search_input.setStyleSheet(AppConfig.STYLES['search_input'])
        self.search_input.setFixedHeight(AppConfig.SEARCH_HEIGHT)
        self.search_input.textChanged.connect(self._filter_books)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        search_layout.addWidget(self._create_filter_label("Category"))
        self.category_combo = self._create_filter_combo(
            AppConfig.BOOK_CATEGORIES
        )
        search_layout.addWidget(self.category_combo)
        search_layout.addSpacing(30)
        
        search_layout.addWidget(self._create_filter_label("Status"))
        self.status_combo = self._create_filter_combo(
            ["All", "Available", "Borrowed"]
        )
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()
        
        return search_layout
    
    def _create_filter_label(self, text):
        # Create styled filter label
        label = QLabel(text)
        label.setFont(QFont("Montserrat", 10))
        label.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
        return label
    
    def _create_filter_combo(self, items):
        # Create styled dropdown filter
        combo = QComboBox()
        combo.addItems(items)
        combo.setStyleSheet(AppConfig.STYLES['combo'])
        combo.setFixedSize(120, AppConfig.SEARCH_HEIGHT)
        combo.currentTextChanged.connect(self._filter_books)
        return combo
    
    def _create_books_table(self):
        # Create sortable, styled book table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(
            len(AppConfig.CATALOG_TABLE['columns'])
        )
        self.books_table.setSortingEnabled(False)
        self.books_table.setHorizontalHeaderLabels(
            AppConfig.CATALOG_TABLE['columns']
        )
        self.books_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.books_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.books_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setStyleSheet(AppConfig.STYLES['table_with_corner'])
        
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self._handle_header_click)
        
        for col, width in enumerate(AppConfig.CATALOG_TABLE['widths']):
            self.books_table.setColumnWidth(col, width)
        
        self.books_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed
        )
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setHorizontalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )
        self.books_table.setVerticalScrollMode(
            QTableWidget.ScrollMode.ScrollPerPixel
        )
        self.books_table.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.books_table.itemSelectionChanged.connect(
            self._on_selection_changed
        )
        
        return self.books_table
    
    def _create_action_buttons(self):
        # Create CRUD and back buttons
        action_layout = QHBoxLayout()
        
        button_configs = [
            ("Add Book", self._add_book, AppConfig.BUTTON_WIDTH_STANDARD),
            ("View Book", self._view_book, AppConfig.BUTTON_WIDTH_STANDARD),
            ("Update Book", self._update_book, AppConfig.BUTTON_WIDTH_STANDARD),
            ("Delete Book", self._delete_book, AppConfig.BUTTON_WIDTH_STANDARD)
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
        # Create styled action button
        btn = QPushButton(text)
        btn.setFont(QFont("Montserrat", 10))
        button_width = width if width else AppConfig.BUTTON_WIDTH_STANDARD
        btn.setFixedSize(button_width, AppConfig.BUTTON_HEIGHT)
        btn.setStyleSheet(AppConfig.STYLES['button'])
        btn.clicked.connect(callback)
        return btn
    
    def _on_selection_changed(self):
        # Track selected book ID
        try:
            selected_row = self.books_table.currentRow()
            if selected_row >= 0:
                self.selected_book_id = self.books_table.item(
                    selected_row, 0
                ).text()
            else:
                self.selected_book_id = None
        except Exception as e:
            print(f"[ERROR] Selection change failed: {e}")
            self.selected_book_id = None
    
    def _clear_selection(self, event):
        # Deselect rows and clear input focus on empty click
        try:
            if self.books_table:
                self.books_table.clearSelection()
                self.selected_book_id = None
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "category_combo"):
                self.category_combo.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] Clear selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)
    
    def _handle_header_click(self, logical_index):
        # Handle column sort on header click
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
            print(f"[ERROR] Header click failed: {e}")
            QMessageBox.warning(self, "Sort Error", "Failed to sort table")
    
    def _load_books_from_database(self):
        # Load all books from DB; refresh display
        if not self._validate_database_connection():
            return
        
        try:
            query = "SELECT * FROM books ORDER BY book_id"
            self.all_books = self.db.fetch_all(query)
            if self.all_books:
                print(f"[OK] Loaded {len(self.all_books)} books")
                self._filter_books()
            else:
                print("[WARNING] No books found in database")
                self.books_table.setRowCount(0)
        except Exception as e:
            print(f"[ERROR] Failed to load books: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Database Error",
                f"Failed to load books from database:\n{str(e)}"
            )
    
    def _display_books(self, books):
        # Populate table with book data and status colors
        try:
            self.books_table.setRowCount(len(books))
            for row, book in enumerate(books):
                for col, key in enumerate(AppConfig.CATALOG_TABLE['keys']):
                    value = str(book.get(key, ''))
                    item = self._create_table_item(value)
                    if col == 5:
                        color = (
                            AppConfig.COLORS['status_available']
                            if book['status'] == 'Available'
                            else AppConfig.COLORS['status_borrowed']
                        )
                        item.setForeground(QColor(color))
                    self.books_table.setItem(row, col, item)
        except Exception as e:
            print(f"[ERROR] Display books failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_table_item(self, text):
        # Create centered, styled table cell
        item = QTableWidgetItem(text)
        item.setFont(QFont("Montserrat", 10))
        item.setForeground(QColor(AppConfig.COLORS['text_dark']))
        item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        return item
    
    def _filter_books(self):
        # Apply search, category, and status filters; then sort and display
        try:
            if not self.all_books:
                return
            search_text = self.search_input.text().lower().strip()
            category = self.category_combo.currentText()
            status = self.status_combo.currentText()
            filtered_books = [
                book for book in self.all_books
                if self._book_matches_filters(book, search_text, category, status)
            ]
            if self.sort_column is not None and filtered_books:
                filtered_books = self._sort_books(filtered_books)
            self._display_books(filtered_books)
            print(f"[INFO] Filtered to {len(filtered_books)} books")
        except Exception as e:
            print(f"[ERROR] Filter books failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _book_matches_filters(self, book, search_text, category, status):
        # Check if book matches all active filters
        if category != "All" and book['category'] != category:
            return False
        if status != "All" and book['status'] != status:
            return False
        if search_text:
            searchable_fields = [
                str(book.get('book_id', '')),
                str(book.get('title', '')),
                str(book.get('author', '')),
                str(book.get('isbn', ''))
            ]
            if not any(search_text in field.lower() for field in searchable_fields):
                return False
        return True
    
    def _sort_books(self, books):
        # Sort books by selected column
        if self.sort_column < len(AppConfig.CATALOG_TABLE['keys']):
            sort_key = AppConfig.CATALOG_TABLE['keys'][self.sort_column]
            return sorted(
                books,
                key=lambda x: str(x.get(sort_key, '')).lower(),
                reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
            )
        return books
    
    def _validate_database_connection(self):
        # Check if DB is connected
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection available")
            QMessageBox.warning(
                self, "Database Error",
                "Not connected to database. Some features may be unavailable."
            )
            return False
        return True
    
    def _validate_selection(self):
        # Check if a book is selected
        if not self.selected_book_id:
            QMessageBox.warning(
                self, "No Selection",
                "Please select a book from the table first."
            )
            return False
        return True
    
    def _add_book(self):
        # Open add book dialog
        try:
            dialog = AddBookDialog(
                parent=self,
                db=self.db,
                callback=self._load_books_from_database
            )
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add book dialog failed: {e}")
            QMessageBox.critical(
                self, "Dialog Error",
                "Failed to open add book dialog"
            )
    
    def _view_book(self):
        # Open view book dialog
        if not self._validate_selection():
            return
        try:
            query = "SELECT * FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (self.selected_book_id,))
            if book_data:
                dialog = ViewBookDialog(parent=self, book_data=book_data)
                dialog.exec()
            else:
                QMessageBox.warning(
                    self, "Book Not Found",
                    "Selected book not found in database"
                )
                self._load_books_from_database()
        except Exception as e:
            print(f"[ERROR] View book failed: {e}")
            QMessageBox.critical(
                self, "View Error",
                f"Failed to view book:\n{str(e)}"
            )
    
    def _update_book(self):
        # Open update book dialog
        if not self._validate_selection():
            return
        try:
            query = "SELECT * FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (self.selected_book_id,))
            if book_data:
                dialog = UpdateBookDialog(
                    parent=self,
                    db=self.db,
                    book_data=book_data,
                    callback=self._load_books_from_database
                )
                dialog.exec()
            else:
                QMessageBox.warning(
                    self, "Book Not Found",
                    "Selected book not found in database"
                )
                self._load_books_from_database()
        except Exception as e:
            print(f"[ERROR] Update book failed: {e}")
            QMessageBox.critical(
                self, "Update Error",
                f"Failed to update book:\n{str(e)}"
            )
    
    def _delete_book(self):
        # Delete selected book after confirmation
        if not self._validate_selection():
            return
        try:
            query = "SELECT title FROM books WHERE book_id = %s"
            book_data = self.db.fetch_one(query, (self.selected_book_id,))
            if not book_data:
                QMessageBox.warning(
                    self, "Book Not Found",
                    "Selected book not found in database"
                )
                self._load_books_from_database()
                return
            dialog = ConfirmDeleteDialog(
                parent=self,
                book_title=book_data['title']
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                delete_query = "DELETE FROM books WHERE book_id = %s"
                if self.db.execute_query(
                    delete_query, 
                    (self.selected_book_id,)
                ):
                    QMessageBox.information(
                        self, "Delete Successful",
                        f"Book '{book_data['title']}' has been deleted."
                    )
                    self.selected_book_id = None
                    self._load_books_from_database()
                else:
                    QMessageBox.critical(
                        self, "Delete Failed",
                        "Failed to delete book from database"
                    )
        except Exception as e:
            print(f"[ERROR] Delete book failed: {e}")
            QMessageBox.critical(
                self, "Delete Error",
                f"Failed to delete book:\n{str(e)}"
            )
    
    def _go_back_to_dashboard(self):
        # Close window to return to dashboard
        self.close()
    
    def _show_fullscreen(self):
        # Maximize window on launch
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        # Allow window to close
        event.accept()