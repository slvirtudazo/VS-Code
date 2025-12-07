# curatel_lms/ui/catalog_dialogs.py

"""
Catalog management dialog windows.
Provides Add, View, Update, Delete dialogs for books.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

# UI Constants
DIALOG_WIDTH = 800
DIALOG_HEIGHT = 700
FORM_WIDTH = 600
FORM_HEIGHT = 450
FIELD_WIDTH = 540
FIELD_HEIGHT = 50

# Color Constants
HEADER_BG = "#3C2A21"
DIALOG_BG = "#8B7E66"
BUTTON_GREEN = "#8BAE66"
BUTTON_GREEN_HOVER = "#A3B087"
BUTTON_RED = "#AF3E3E"
BUTTON_RED_HOVER = "#CD5656"
BUTTON_GRAY = "#8B7E66"
BUTTON_GRAY_HOVER = "#6B5E46"

# Style Constants
LABEL_STYLE = """
    font-family: Montserrat;
    font-size: 15px;
    color: white;
    border: none;
    background: transparent;
"""

INPUT_STYLE = """
    QLineEdit {
        font-family: Montserrat;
        font-size: 13px;
        border: 1px solid #8B7E66;
        border-radius: 10px;
        padding: 8px;
        background-color: white;
        color: black;
    }
    QLineEdit:focus {
        border: 2px solid #6B5E46;
    }
"""

COMBO_STYLE = """
    QComboBox {
        font-family: Montserrat;
        font-size: 13px;
        border: 1px solid #8B7E66;
        border-radius: 10px;
        padding: 5px 10px;
        background-color: white;
        color: black;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: none;
    }
    QComboBox:focus {
        border: 2px solid #6B5E46;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        color: black;
        selection-background-color: #E0D6C8;
        border: 1px solid #8B7E66;
        outline: 0;
    }
"""

# Book categories
BOOK_CATEGORIES = [
    "All", "Adventure", "Art", "Biography", "Business",
    "Cooking", "Fantasy", "Fiction", "History", "Horror",
    "Mystery", "Non-Fiction", "Poetry", "Romance", "Science", "Technology"
]

class BaseBookDialog(QDialog):
    """Base dialog class for book operations."""
    
    def __init__(self, parent=None, db=None, book_data=None, callback=None):
        """
        Initialize base dialog.
        Args:
            parent: Parent widget
            db: Database connection object
            book_data: Dictionary containing book data
            callback: Function to call after operation
        """
        super().__init__(parent)
        self.db = db
        self.book_data = book_data or {}
        self.callback = callback
        
        self._configure_window()
    
    def _configure_window(self):
        """Configure window properties."""
        self.setWindowTitle("Curatel - Catalog Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(DIALOG_WIDTH, DIALOG_HEIGHT)
        self.setStyleSheet(f"background-color: {DIALOG_BG};")
        self._center_on_screen()
    
    def _center_on_screen(self):
        """Center dialog on screen."""
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
    
    def _create_header(self, text):
        """
        Create dialog header.
        Args:
            text: Header text
        Returns: QWidget containing header
        """
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background-color: {HEADER_BG}; border: none;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-family: Montserrat;
            font-size: 30px;
            font-weight: bold;
            letter-spacing: 3px;
            color: white;
        """)
        layout.addWidget(label)
        
        return header
    
    def _create_form_container(self):
        """
        Create form container widget.
        Returns: QWidget configured as form container
        """
        container = QWidget()
        container.setFixedSize(FORM_WIDTH, FORM_HEIGHT)
        container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)
        return container
    
    def _add_field(self, layout, label_text, widget):
        """
        Add labeled field to layout.
        Args:
            layout: Target QVBoxLayout
            label_text: Label text
            widget: Input widget
        """
        label = QLabel(label_text)
        label.setStyleSheet(LABEL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(widget)
    
    def _create_buttons(self, primary_text, primary_callback):
        """
        Create action buttons.
        Args:
            primary_text: Text for primary action button
            primary_callback: Callback for primary button
        Returns: QHBoxLayout containing buttons
        """
        layout = QHBoxLayout()
        layout.setSpacing(30)
        layout.addStretch()
        
        # Primary button
        primary_btn = QPushButton(primary_text)
        primary_btn.setFixedSize(150, 60)
        primary_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_GREEN};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_GREEN_HOVER};
            }}
        """)
        primary_btn.clicked.connect(primary_callback)
        layout.addWidget(primary_btn)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(150, 60)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RED};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_RED_HOVER};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        layout.addStretch()
        return layout
    
    def _validate_inputs(self, title, author, isbn):
        """
        Validate book input fields.
        Args:
            title: Book title
            author: Book author
            isbn: Book ISBN
        Returns: True if valid, False otherwise
        """
        if not all([title, author, isbn]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return False
        return True
    
    def _generate_book_id(self):
        """
        Generate next book ID.
        Returns: New book ID string
        """
        last_book = self.db.fetch_one(
            "SELECT book_id FROM books ORDER BY book_id DESC LIMIT 1"
        )
        
        if last_book:
            last_num = int(last_book['book_id'].split('-')[1])
            return f"BK-{last_num + 1:03d}"
        
        return "BK-001"

class AddBookDialog(BaseBookDialog):
    """Dialog for adding new books."""
    
    def __init__(self, parent=None, db=None, callback=None):
        """
        Initialize add book dialog.
        Args:
            parent: Parent widget
            db: Database connection object
            callback: Function to call after adding book
        """
        super().__init__(parent, db, None, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header("ADD BOOK")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        # Form container
        form_container = self._create_form_container()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        
        # Input fields
        self.title_input = QLineEdit()
        self.title_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.title_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Title", self.title_input)
        
        self.author_input = QLineEdit()
        self.author_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.author_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Author", self.author_input)
        
        self.isbn_input = QLineEdit()
        self.isbn_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.isbn_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "ISBN", self.isbn_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(BOOK_CATEGORIES)
        self.category_combo.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.category_combo.setStyleSheet(COMBO_STYLE)
        self._add_field(form_layout, "Category", self.category_combo)
        
        # Center form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(50)
        
        # Action buttons
        buttons = self._create_buttons("Save", self._save_book)
        layout.addLayout(buttons)
    
    def _save_book(self):
        """Save new book to database."""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        
        # Validate inputs
        if not self._validate_inputs(title, author, isbn):
            return
        
        # Generate book ID
        book_id = self._generate_book_id()
        
        # Insert into database
        now = datetime.now()
        query = """
            INSERT INTO books 
            (book_id, title, author, isbn, category, status, added_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, 'Available', %s, %s)
        """
        
        try:
            if self.db.execute_query(query, (book_id, title, author, isbn, category, now, now)):
                QMessageBox.information(
                    self, "Success",
                    f"Book added successfully!\n\nBook ID: {book_id}"
                )
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add book to database")
        except Exception as e:
            print(f"[ERROR] Add book failed: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")

class ViewBookDialog(BaseBookDialog):
    """Dialog for viewing book details."""
    
    def __init__(self, parent=None, book_data=None):
        """
        Initialize view book dialog.
        Args:
            parent: Parent widget
            book_data: Dictionary containing book data
        """
        super().__init__(parent, None, book_data, None)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header("BOOK INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        # Info container
        info_container = self._create_form_container()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)
        
        # Display fields
        self._add_info_field(info_layout, "Book ID:", self.book_data.get('book_id', ''))
        self._add_info_field(info_layout, "Title:", self.book_data.get('title', ''))
        self._add_info_field(info_layout, "Author:", self.book_data.get('author', ''))
        self._add_info_field(info_layout, "ISBN:", self.book_data.get('isbn', ''))
        self._add_info_field(info_layout, "Category:", self.book_data.get('category', ''))
        self._add_info_field(info_layout, "Status:", self.book_data.get('status', ''))
        
        # Format and display dates
        added_at = self._format_date(self.book_data.get('added_at'))
        updated_at = self._format_date(self.book_data.get('updated_at'))
        self._add_info_field(info_layout, "Added At:", added_at)
        self._add_info_field(info_layout, "Updated At:", updated_at)
        
        # Center container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(info_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(40)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(150, 60)
        close_btn.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RED};
                color: white;
                border: none;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_RED_HOVER};
            }}
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _add_info_field(self, layout, label_text, value_text):
        """
        Add information field row.
        Args:
            layout: Target layout
            label_text: Label text
            value_text: Value text
        """
        row = QWidget()
        row.setStyleSheet("border: none; background: transparent;")
        
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(100)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet(LABEL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Value
        value = QLabel(str(value_text))
        value.setStyleSheet("""
            font-family: Montserrat;
            font-size: 15px;
            color: white;
            border: none;
            background: transparent;
            text-decoration: underline;
        """)
        value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value.setWordWrap(True)
        
        row_layout.addWidget(label, 1)
        row_layout.addWidget(value, 2)
        
        layout.addWidget(row)
    
    def _format_date(self, date_value):
        """
        Format date for display.
        Args:
            date_value: Date value to format
        Returns: Formatted date string
        """
        if date_value:
            return str(date_value).split()[0]
        return ''

class UpdateBookDialog(BaseBookDialog):
    """Dialog for updating book information."""
    
    def __init__(self, parent=None, db=None, book_data=None, callback=None):
        """
        Initialize update book dialog.
        Args:
            parent: Parent widget
            db: Database connection object
            book_data: Dictionary containing book data
            callback: Function to call after updating book
        """
        super().__init__(parent, db, book_data, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header("UPDATE BOOK")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        # Form container
        form_container = self._create_form_container()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        
        # Input fields with existing data
        self.title_input = QLineEdit()
        self.title_input.setText(self.book_data.get('title', ''))
        self.title_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.title_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Title", self.title_input)
        
        self.author_input = QLineEdit()
        self.author_input.setText(self.book_data.get('author', ''))
        self.author_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.author_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Author", self.author_input)
        
        self.isbn_input = QLineEdit()
        self.isbn_input.setText(self.book_data.get('isbn', ''))
        self.isbn_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.isbn_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "ISBN", self.isbn_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(BOOK_CATEGORIES)
        self.category_combo.setCurrentText(self.book_data.get('category', 'Fiction'))
        self.category_combo.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.category_combo.setStyleSheet(COMBO_STYLE)
        self._add_field(form_layout, "Category", self.category_combo)
        
        # Center form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(50)
        
        # Action buttons
        buttons = self._create_buttons("Update", self._update_book)
        layout.addLayout(buttons)
    
    def _update_book(self):
        """Update book in database."""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        
        # Validate inputs
        if not self._validate_inputs(title, author, isbn):
            return
        
        # Update in database
        now = datetime.now()
        query = """
            UPDATE books 
            SET title = %s, author = %s, isbn = %s, category = %s, updated_at = %s
            WHERE book_id = %s
        """
        
        try:
            if self.db.execute_query(
                query,
                (title, author, isbn, category, now, self.book_data['book_id'])
            ):
                QMessageBox.information(self, "Success", "Book updated successfully!")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update book")
        except Exception as e:
            print(f"[ERROR] Update book failed: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")

class ConfirmDeleteDialog(QDialog):
    """Confirmation dialog for deleting a book."""
    
    def __init__(self, parent=None, book_title=""):
        """
        Initialize delete confirmation dialog.
        Args:
            parent: Parent widget
            book_title: Title of book to delete
        """
        super().__init__(parent)
        self.book_title = book_title
        
        self._configure_window()
        self._setup_ui()
    
    def _configure_window(self):
        """Configure window properties."""
        self.setWindowTitle("Curatel - Catalog Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 500)
        self.setStyleSheet(f"background-color: {DIALOG_BG};")
        
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background-color: {HEADER_BG}; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header_label = QLabel("CONFIRM DELETE BOOK")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("""
            font-family: Montserrat;
            font-size: 30px;
            font-weight: bold;
            letter-spacing: 3px;
            color: white;
        """)
        header_layout.addWidget(header_label)
        layout.addWidget(header)
        
        layout.addSpacing(40)
        
        # Message frame
        frame = QWidget()
        frame.setFixedSize(600, 250)
        frame.setStyleSheet(f"background-color: {DIALOG_BG}; border: none;")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(30, 20, 30, 20)
        
        message = QLabel(
            f"Are you sure you want to permanently delete\n'{self.book_title}'?"
        )
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
        
        # Center frame
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(frame)
        center_layout.addStretch()
        layout.addLayout(center_layout)
        
        layout.addSpacing(40)
        
        # Confirmation buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.setSpacing(30)
        
        yes_btn = QPushButton("Yes")
        yes_btn.setFixedSize(150, 60)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RED};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_RED_HOVER};
            }}
        """)
        yes_btn.clicked.connect(self.accept)
        
        no_btn = QPushButton("No")
        no_btn.setFixedSize(150, 60)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_GREEN};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_GREEN_HOVER};
            }}
        """)
        no_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(yes_btn)
        buttons_layout.addWidget(no_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)