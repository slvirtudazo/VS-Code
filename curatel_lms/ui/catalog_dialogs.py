# curatel_lms/ui/catalog_dialogs.py

# Handles book add, view, update, and delete dialogs using structured OOP patterns

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime
from curatel_lms.config import AppConfig

class BaseBookDialog(QDialog):
    # Base dialog for book operations: config, header, form, validation
    
    def __init__(self, parent=None, db=None, book_data=None, callback=None):
        # Init with db, book data, and callback
        super().__init__(parent)
        self.db = db
        self.book_data = book_data if book_data else {}
        self.callback = callback
        self._configure_window()
    
    def _configure_window(self):
        # Set title, size, style, and center dialog
        self.setWindowTitle("Curatel - Catalog Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, AppConfig.DIALOG_HEIGHT)
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_dialog']};")
        self._center_on_screen()
    
    def _center_on_screen(self):
        # Center dialog on screen
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
    
    def _create_header(self, text):
        # Make styled header widget
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(AppConfig.STYLES['dialog_header'])
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(AppConfig.STYLES['dialog_header_text'])
        layout.addWidget(label)
        return header
    
    def _create_form_container(self, height=None):
        # Make styled form container
        container_height = height if height else AppConfig.FORM_HEIGHT
        container = QWidget()
        container.setFixedSize(AppConfig.FORM_WIDTH, container_height)
        container.setStyleSheet(AppConfig.STYLES['form_container'])
        return container
    
    def _add_field(self, layout, label_text, widget):
        # Add labeled input field
        label = QLabel(label_text)
        label.setStyleSheet(AppConfig.STYLES['dialog_label'])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(widget)
    
    def _create_buttons(self, primary_text, primary_callback):
        # Make primary and cancel buttons
        layout = QHBoxLayout()
        layout.setSpacing(30)
        layout.addStretch()
        primary_btn = QPushButton(primary_text)
        primary_btn.setFixedSize(150, AppConfig.BUTTON_HEIGHT_LARGE)
        primary_btn.setStyleSheet(AppConfig.get_green_button_style())
        primary_btn.clicked.connect(primary_callback)
        layout.addWidget(primary_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(150, AppConfig.BUTTON_HEIGHT_LARGE)
        cancel_btn.setStyleSheet(AppConfig.get_red_button_style())
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        layout.addStretch()
        return layout
    
    def _validate_inputs(self, title, author, isbn):
        # Check required fields
        if not all([title, author, isbn]):
            QMessageBox.warning(self, "Validation Error", "All fields are required. Please fill in title, author, and ISBN.")
            return False
        return True
    
    def _generate_book_id(self):
        # Generate next book ID like BK-001
        last_book = self.db.fetch_one("SELECT book_id FROM books ORDER BY book_id DESC LIMIT 1")
        if last_book:
            last_num = int(last_book['book_id'].split('-')[1])
            return f"BK-{last_num + 1:03d}"
        return "BK-001"

class AddBookDialog(BaseBookDialog):
    # Dialog to add new books with auto ID and validation
    
    def __init__(self, parent=None, db=None, callback=None):
        # Init without existing data
        super().__init__(parent, db, None, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build add book form
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("ADD BOOK")
        layout.addWidget(header)
        layout.addSpacing(40)

        form_container = self._create_form_container()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        form_layout.setSpacing(10)

        self.title_input = QLineEdit()
        self.title_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.title_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Title", self.title_input)

        self.author_input = QLineEdit()
        self.author_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.author_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Author", self.author_input)

        self.isbn_input = QLineEdit()
        self.isbn_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.isbn_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "ISBN", self.isbn_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(AppConfig.BOOK_CATEGORIES)
        self.category_combo.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.category_combo.setStyleSheet(AppConfig.STYLES['combo_with_dropdown'])
        self._add_field(form_layout, "Category", self.category_combo)

        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()

        layout.addLayout(container_layout)
        layout.addSpacing(50)

        buttons = self._create_buttons("Save", self._save_book)
        layout.addLayout(buttons)
    
    def _save_book(self):
        # Save validated book to DB
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        if not self._validate_inputs(title, author, isbn):
            return
        book_id = self._generate_book_id()
        now = datetime.now()
        query = """
            INSERT INTO books 
            (book_id, title, author, isbn, category, status, added_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, 'Available', %s, %s)
        """
        try:
            if self.db.execute_query(query, (book_id, title, author, isbn, category, now, now)):
                QMessageBox.information(self, "Success", f"Book added successfully!\n\nBook ID: {book_id}")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to add book to database")
        except Exception as e:
            print(f"[ERROR] Add book failed: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while adding book:\n{str(e)}")

class ViewBookDialog(BaseBookDialog):
    # Read-only dialog showing book details
    
    def __init__(self, parent=None, book_data=None):
        # Init without db or callback
        super().__init__(parent, None, book_data, None)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build read-only book info view
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("BOOK INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)

        info_container = self._create_form_container()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)

        self._add_info_field(info_layout, "Book ID:", self.book_data.get('book_id', ''))
        self._add_info_field(info_layout, "Title:", self.book_data.get('title', ''))
        self._add_info_field(info_layout, "Author:", self.book_data.get('author', ''))
        self._add_info_field(info_layout, "ISBN:", self.book_data.get('isbn', ''))
        self._add_info_field(info_layout, "Category:", self.book_data.get('category', ''))
        self._add_info_field(info_layout, "Status:", self.book_data.get('status', ''))

        added_at = self._format_date(self.book_data.get('added_at'))
        updated_at = self._format_date(self.book_data.get('updated_at'))
        self._add_info_field(info_layout, "Added At:", added_at)
        self._add_info_field(info_layout, "Updated At:", updated_at)

        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(info_container)
        container_layout.addStretch()

        layout.addLayout(container_layout)
        layout.addSpacing(40)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(150, AppConfig.BUTTON_HEIGHT_LARGE)
        close_btn.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(AppConfig.get_red_button_style())
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _add_info_field(self, layout, label_text, value_text):
        # Add read-only label-value row
        row = QWidget()
        row.setStyleSheet("border: none; background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(100)

        label = QLabel(label_text)
        label.setStyleSheet(AppConfig.STYLES['dialog_label'])
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        value = QLabel(str(value_text))
        value.setStyleSheet(AppConfig.STYLES['info_value'])
        value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value.setWordWrap(True)

        row_layout.addWidget(label, 1)
        row_layout.addWidget(value, 2)
        layout.addWidget(row)
    
    def _format_date(self, date_value):
        # Format date as YYYY-MM-DD
        if date_value:
            return str(date_value).split()[0]
        return ''

class UpdateBookDialog(BaseBookDialog):
    # Dialog to edit existing book info (ID unchanged)
    
    def __init__(self, parent=None, db=None, book_data=None, callback=None):
        # Init with current book data
        super().__init__(parent, db, book_data, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build update form with current values
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("UPDATE BOOK")
        layout.addWidget(header)
        layout.addSpacing(40)

        form_container = self._create_form_container()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)

        self.title_input = QLineEdit()
        self.title_input.setText(self.book_data.get('title', ''))
        self.title_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.title_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Title", self.title_input)

        self.author_input = QLineEdit()
        self.author_input.setText(self.book_data.get('author', ''))
        self.author_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.author_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Author", self.author_input)

        self.isbn_input = QLineEdit()
        self.isbn_input.setText(self.book_data.get('isbn', ''))
        self.isbn_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.isbn_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "ISBN", self.isbn_input)

        self.category_combo = QComboBox()
        self.category_combo.addItems(AppConfig.BOOK_CATEGORIES)
        self.category_combo.setCurrentText(self.book_data.get('category', 'Fiction'))
        self.category_combo.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.category_combo.setStyleSheet(AppConfig.STYLES['combo_with_dropdown'])
        self._add_field(form_layout, "Category", self.category_combo)

        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()

        layout.addLayout(container_layout)
        layout.addSpacing(50)

        buttons = self._create_buttons("Update", self._update_book)
        layout.addLayout(buttons)
    
    def _update_book(self):
        # Update validated book in DB
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        if not self._validate_inputs(title, author, isbn):
            return
        now = datetime.now()
        query = """
            UPDATE books 
            SET title = %s, author = %s, isbn = %s, 
                category = %s, updated_at = %s
            WHERE book_id = %s
        """
        try:
            if self.db.execute_query(query, (title, author, isbn, category, now, self.book_data['book_id'])):
                QMessageBox.information(self, "Success", "Book information updated successfully!")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to update book in database")
        except Exception as e:
            print(f"[ERROR] Update book failed: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while updating book:\n{str(e)}")

class ConfirmDeleteDialog(QDialog):
    # Simple yes/no dialog to confirm book deletion
    
    def __init__(self, parent=None, book_title=""):
        # Init with book title
        super().__init__(parent)
        self.book_title = book_title
        self._configure_window()
        self._setup_ui()
    
    def _configure_window(self):
        # Set smaller fixed size and center
        self.setWindowTitle("Curatel - Catalog Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, 500)
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_dialog']};")
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
    
    def _setup_ui(self):
        # Build confirmation layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(AppConfig.STYLES['dialog_header'])

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header_label = QLabel("CONFIRM DELETE BOOK")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(AppConfig.STYLES['dialog_header_text'])
        header_layout.addWidget(header_label)

        layout.addWidget(header)
        layout.addSpacing(40)
        
        frame = QWidget()
        frame.setFixedSize(600, 250)
        frame.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_dialog']}; border: none;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(30, 20, 30, 20)

        message = QLabel(f"Are you sure you want to permanently delete\n'{self.book_title}'?")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("""
            font-family: Montserrat;
            font-size: 20px;
            border: none;
            color: white;
        """)
        frame_layout.addStretch()
        frame_layout.addWidget(message)
        frame_layout.addStretch()

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(frame)
        center_layout.addStretch()

        layout.addLayout(center_layout)
        layout.addSpacing(40)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.setSpacing(30)

        yes_btn = QPushButton("Yes")
        yes_btn.setFixedSize(150, AppConfig.BUTTON_HEIGHT_LARGE)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.setStyleSheet(AppConfig.get_red_button_style())
        yes_btn.clicked.connect(self.accept)

        no_btn = QPushButton("No")
        no_btn.setFixedSize(150, AppConfig.BUTTON_HEIGHT_LARGE)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setStyleSheet(AppConfig.get_green_button_style())
        no_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(yes_btn)
        buttons_layout.addWidget(no_btn)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)