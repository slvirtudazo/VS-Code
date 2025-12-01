# ui/dialogs.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, 
                              QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

class BaseDialog(QDialog):
    """Base dialog class with common styling and centering"""
    
    def __init__(self, parent=None, width=1000, height=600):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setModal(True)
        self.setup_style()
        self.center_dialog()
    
    def setup_style(self):
        """Apply dialog styling with transparency"""
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(139, 126, 102, 0.95);
            }
            QLabel {
                color: white;
                font-family: 'Montserrat';
                background: transparent;
            }
            QLineEdit, QComboBox {
                background-color: white;
                border: none;
                border-radius: 15px;
                padding: 15px 20px;
                font-size: 14px;
                font-family: 'Montserrat';
                color: #000000;
            }
            QLineEdit:focus, QComboBox:focus {
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #000000;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #D9CFC2;
                selection-color: black;
                border: 1px solid #8B7E66;
            }
        """)
    
    def center_dialog(self):
        """Center dialog on screen or parent"""
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)
        else:
            screen_geo = self.screen().geometry()
            x = (screen_geo.width() - self.width()) // 2
            y = (screen_geo.height() - self.height()) // 2
            self.move(x, y)
    
    def create_header(self, title):
        """Create dialog header with dark background"""
        header = QLabel(title)
        header.setFont(QFont("Playfair Display", 28, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: #3C2A21;
                padding: 40px;
                color: white;
                letter-spacing: 8px;
            }
        """)
        return header
    
    def create_buttons(self, btn1_text="Save", btn2_text="Cancel", btn1_callback=None, btn2_callback=None):
        """Create action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.addStretch()
        
        # Save button
        btn1 = QPushButton(btn1_text)
        btn1.setFixedSize(200, 60)
        btn1.setFont(QFont("Montserrat", 14, QFont.Weight.Bold))
        btn1.setCursor(Qt.CursorShape.PointingHandCursor)
        btn1.setStyleSheet("""
            QPushButton {
                background-color: #8BAE66;
                color: white;
                border: none;
                border-radius: 15px;            
            }
            QPushButton:hover {
                background-color: #A3B087;
            }
        """)
        if btn1_callback:
            btn1.clicked.connect(btn1_callback)
        button_layout.addWidget(btn1)
        
        # Cancel button
        btn2 = QPushButton(btn2_text)
        btn2.setFixedSize(200, 60)
        btn2.setFont(QFont("Montserrat", 14, QFont.Weight.Bold))
        btn2.setCursor(Qt.CursorShape.PointingHandCursor)
        btn2.setStyleSheet("""
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #CD5656;
            }
        """)
        if btn2_callback:
            btn2.clicked.connect(btn2_callback)
        else:
            btn2.clicked.connect(self.reject)
        button_layout.addWidget(btn2)
        
        button_layout.addStretch()
        return button_layout

class AddBookDialog(BaseDialog):
    """Dialog for adding new books"""
    
    def __init__(self, parent=None, db=None, callback=None):
        self.db = db
        self.callback = callback
        super().__init__(parent)

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)

        self.setFixedSize(800, 700)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())

        self.setWindowTitle("Add Book")
        self.setup_ui()
    
    def create_header(self, text):
        header = QWidget()
        header.setFixedHeight(80)  # decreased by 20
        header.setStyleSheet("""
            background-color: #3C2A21;
            border: none;
        """)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-family: Montserrat;
            font-size: 30px;
            font-weight: bold;
            letter-spacing: 5px;
            color: white;
        """)

        header_layout.addWidget(label)
        return header

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self.create_header("ADD BOOK")
        layout.addWidget(header)

        layout.addSpacing(40)

        # --- Main Frame Container ---
        form_container = QWidget()
        form_container.setFixedSize(600, 450)
        form_container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)

        # --- Styles ---
        label_style = """
            font-family: Montserrat;
            font-size: 15px;
            color: white;
            border: none;
            background: transparent;
        """

        input_style = """
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

        combo_style = """
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

        FIELD_W = 540
        FIELD_H = 50

        # Helpers
        def add_field(label_text, widget):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            form_layout.addWidget(label)
            # form_layout.setSpacing(-5)
            form_layout.addWidget(widget)

        # TITLE
        self.title_input = QLineEdit()
        self.title_input.setFixedSize(FIELD_W, FIELD_H)
        self.title_input.setStyleSheet(input_style)
        add_field("Title", self.title_input)

        # AUTHOR
        self.author_input = QLineEdit()
        self.author_input.setFixedSize(FIELD_W, FIELD_H)
        self.author_input.setStyleSheet(input_style)
        add_field("Author", self.author_input)

        # ISBN
        self.isbn_input = QLineEdit()
        self.isbn_input.setFixedSize(FIELD_W, FIELD_H)
        self.isbn_input.setStyleSheet(input_style)
        add_field("ISBN", self.isbn_input)

        # CATEGORY
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All", "Adventure", "Art", "Biography", "Business", "Cooking",
            "Fantasy", "Fiction", "History", "Horror", "Mystery",
            "Non-Fiction", "Poetry", "Romance", "Science", "Technology"
        ])
        self.category_combo.setFixedSize(FIELD_W, FIELD_H)
        self.category_combo.setStyleSheet(combo_style)
        add_field("Category", self.category_combo)

        # Center form
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)

        layout.addSpacing(50)

        # BUTTONS
        buttons = self.create_buttons("Save", "Cancel", self.save_book)

        for btn in buttons.findChildren(QPushButton):
            btn.setFixedSize(100, 50)
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #8B7E66;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-family: Montserrat;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #6B5E46;
                }
            """)

        layout.addLayout(buttons)

    def save_book(self):
        """Save new book to database"""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        
        # Validation
        if not all([title, author, isbn]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Generate book ID
        last_book = self.db.fetch_one("SELECT book_id FROM books ORDER BY book_id DESC LIMIT 1")
        if last_book:
            last_num = int(last_book['book_id'].split('-')[1])
            book_id = f"BK-{last_num + 1:03d}"
        else:
            book_id = "BK-001"
        
        # Insert into database
        now = datetime.now()
        query = """
        INSERT INTO books (book_id, title, author, isbn, category, status, added_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, 'Available', %s, %s)
        """
        
        if self.db.execute_query(query, (book_id, title, author, isbn, category, now, now)):
            QMessageBox.information(self, "Success", f"Book added successfully!\n\nBook ID: {book_id}")
            if self.callback:
                self.callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add book to database")


class ViewBookDialog(BaseDialog):
    """Dialog for viewing book details"""
    
    def __init__(self, parent=None, book_data=None):
        self.book_data = book_data
        super().__init__(parent)
        self.setWindowTitle("View Book")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup view book UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 50)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header("VIEW BOOK")
        layout.addWidget(header)
        
        layout.addSpacing(60)
        
        # Info container
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: 3px solid white;
                border-radius: 30px;
            }
        """)
        info_container.setFixedSize(800, 560)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(80, 50, 80, 50)
        info_layout.setSpacing(25)
        
        # Display fields
        fields = [
            ("Book ID:", self.book_data.get('book_id', '')),
            ("Title:", self.book_data.get('title', '')),
            ("Author:", self.book_data.get('author', '')),
            ("ISBN:", self.book_data.get('isbn', '')),
            ("Category:", self.book_data.get('category', '')),
            ("Status:", self.book_data.get('status', '')),
            ("Added At:", str(self.book_data.get('added_at', ''))),
            ("Updated At:", str(self.book_data.get('updated_at', '')))
        ]
        
        for label_text, value_text in fields:
            field_layout = QHBoxLayout()
            
            label = QLabel(label_text)
            label.setFont(QFont("Montserrat", 14))
            label.setFixedWidth(200)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            field_layout.addWidget(label)
            
            value = QLabel(str(value_text))
            value.setFont(QFont("Montserrat", 14))
            value.setStyleSheet("text-decoration: underline;")
            value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            field_layout.addWidget(value)
            
            field_layout.addStretch()
            info_layout.addLayout(field_layout)
        
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(info_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addStretch()
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(200, 60)
        close_btn.setFont(QFont("Montserrat", 14, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(74, 74, 50, 0.9);
                color: white;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(74, 74, 50, 1.0);
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)


class UpdateBookDialog(BaseDialog):
    """Dialog for updating book information"""
    
    def __init__(self, parent=None, db=None, book_data=None, callback=None):
        self.db = db
        self.book_data = book_data
        self.callback = callback
        super().__init__(parent)
        self.setWindowTitle("Update Book")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup update book UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 50)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header("UPDATE BOOK INFORMATION")
        layout.addWidget(header)
        
        layout.addSpacing(60)
        
        # Form container
        form_container = QWidget()
        form_container.setStyleSheet("""
            QWidget {
                background: transparent;
                border: 3px solid white;
                border-radius: 30px;
            }
        """)
        form_container.setFixedSize(800, 450)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(100, 40, 100, 40)
        form_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Title")
        title_label.setFont(QFont("Montserrat", 14))
        form_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.title_input = QLineEdit()
        self.title_input.setText(self.book_data.get('title', ''))
        self.title_input.setFixedHeight(50)
        form_layout.addWidget(self.title_input)
        
        # Author
        author_label = QLabel("Author")
        author_label.setFont(QFont("Montserrat", 14))
        form_layout.addWidget(author_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.author_input = QLineEdit()
        self.author_input.setText(self.book_data.get('author', ''))
        self.author_input.setFixedHeight(50)
        form_layout.addWidget(self.author_input)
        
        # ISBN
        isbn_label = QLabel("ISBN")
        isbn_label.setFont(QFont("Montserrat", 14))
        form_layout.addWidget(isbn_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.isbn_input = QLineEdit()
        self.isbn_input.setText(self.book_data.get('isbn', ''))
        self.isbn_input.setFixedHeight(50)
        form_layout.addWidget(self.isbn_input)
        
        # Category
        category_label = QLabel("Category")
        category_label.setFont(QFont("Montserrat", 14))
        form_layout.addWidget(category_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.category_combo = QComboBox()
        categories = [
            "Adventure", "Art", "Biography", "Business", "Cooking",
            "Fantasy", "Fiction", "History", "Horror", "Mystery",
            "Non-Fiction", "Poetry", "Romance", "Science", "Technology"
        ]
        self.category_combo.addItems(categories)
        current_category = self.book_data.get('category', '')
        if current_category in categories:
            self.category_combo.setCurrentText(current_category)
        self.category_combo.setFixedHeight(50)
        form_layout.addWidget(self.category_combo)
        
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addStretch()
        
        # Buttons
        buttons = self.create_buttons("Update", "Cancel", self.update_book)
        layout.addLayout(buttons)
    
    def update_book(self):
        """Update book in database"""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        
        # Validation
        if not all([title, author, isbn]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Update database
        now = datetime.now()
        query = """
        UPDATE books 
        SET title = %s, author = %s, isbn = %s, category = %s, updated_at = %s
        WHERE book_id = %s
        """
        
        if self.db.execute_query(query, (title, author, isbn, category, now, self.book_data['book_id'])):
            QMessageBox.information(self, "Success", "Book updated successfully!")
            if self.callback:
                self.callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update book")


class ConfirmDeleteDialog(BaseDialog):
    """Confirmation dialog for delete operations"""
    
    def __init__(self, parent=None, book_title=""):
        self.book_title = book_title
        super().__init__(parent, 1000, 500)
        self.setWindowTitle("Confirm Delete")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup confirmation UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 60)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header("CONFIRM DELETE BOOK")
        layout.addWidget(header)
        
        layout.addSpacing(100)
        
        # Message
        message = QLabel(f"Are you sure you want to delete '{self.book_title}'?")
        message.setFont(QFont("Montserrat", 18))
        message.setStyleSheet("color: white; background: transparent;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        layout.addStretch()
        
        # Buttons
        buttons = self.create_buttons("Yes", "No", self.accept, self.reject)
        layout.addLayout(buttons)