# ui/dialogs.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QComboBox, QSpinBox,
                              QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import AppConfig
from datetime import datetime, timedelta
import re

class BaseDialog(QDialog):
    """Base dialog class with common styling and centering"""
    
    def __init__(self, parent=None, width=500, height=450):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setModal(True)
        self.setup_style()
        self.center_dialog()
    
    def setup_style(self):
        """Apply dialog styling with transparency"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(139, 126, 102, 0.8);
            }}
            QLabel {{
                color: white;
                font-family: 'Montserrat';
                background: transparent;
            }}
            QLineEdit, QComboBox, QSpinBox, QTextEdit {{
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Montserrat';
                color: #000000;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 2px solid {AppConfig.COLORS['button_primary']};
            }}
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
        header.setFont(QFont("Playfair Display", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: rgba(60, 42, 33, 1.0);
                padding: 20px;
                color: white;
            }
        """)
        return header
    
    def create_buttons(self, save_text="Save", save_callback=None):
        """Create action buttons (Save/Cancel)"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()
        
        # Save button
        save_btn = QPushButton(save_text)
        save_btn.setFixedSize(140, 45)
        save_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(AppConfig.get_button_style('primary'))
        if save_callback:
            save_btn.clicked.connect(save_callback)
        button_layout.addWidget(save_btn)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(140, 45)
        cancel_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(AppConfig.get_button_style('primary'))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        return button_layout


class ResetPasswordDialog(BaseDialog):
    """Password reset dialog for forgotten passwords"""
    
    def __init__(self, parent=None):
        super().__init__(parent, 400, 300)
        self.setWindowTitle("Reset Password")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup reset password UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header("RESET PASSWORD")
        layout.addWidget(header)
        
        layout.addSpacing(30)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(40, 0, 40, 0)
        content_layout.setSpacing(15)
        
        # Instructions
        instruction = QLabel("Enter your registered email address to\nreceive password reset instructions")
        instruction.setFont(QFont("Montserrat", 11))
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setWordWrap(True)
        content_layout.addWidget(instruction)
        
        content_layout.addSpacing(10)
        
        # Email field
        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Montserrat", 11))
        content_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFixedHeight(40)
        content_layout.addWidget(self.email_input)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        # Buttons
        buttons = self.create_buttons("Send", self.send_reset)
        layout.addLayout(buttons)
    
    def send_reset(self):
        """Send password reset email"""
        email = self.email_input.text().strip()
        
        # Validation
        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email address")
            return
        
        # Validate email format
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        QMessageBox.information(
            self,
            "Request Sent",
            f"Password reset instructions have been sent to:\n{email}\n\nPlease check your inbox."
        )
        self.accept()


class AddBookDialog(BaseDialog):
    """Dialog for adding new books to the catalog"""
    
    def __init__(self, parent=None, db=None, callback=None):
        self.db = db
        self.callback = callback
        super().__init__(parent)
        self.setWindowTitle("Add Book")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup add book UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self.create_header("ADD BOOK")
        layout.addWidget(header)
        
        layout.addSpacing(30)
        
        # Form fields
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(40, 0, 40, 0)
        form_layout.setSpacing(12)
        
        # Title field
        title_label = QLabel("Title")
        form_layout.addWidget(title_label)
        self.title_input = QLineEdit()
        self.title_input.setFixedHeight(40)
        form_layout.addWidget(self.title_input)
        
        # Author field
        author_label = QLabel("Author")
        form_layout.addWidget(author_label)
        self.author_input = QLineEdit()
        self.author_input.setFixedHeight(40)
        form_layout.addWidget(self.author_input)
        
        # ISBN field
        isbn_label = QLabel("ISBN")
        form_layout.addWidget(isbn_label)
        self.isbn_input = QLineEdit()
        self.isbn_input.setFixedHeight(40)
        form_layout.addWidget(self.isbn_input)
        
        # Category dropdown
        category_label = QLabel("Category")
        form_layout.addWidget(category_label)
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Adventure", "Art", "Biography", "Business", "Cooking",
            "Fantasy", "Fiction", "History", "Horror", "Mystery",
            "Non-Fiction", "Poetry", "Romance", "Science", "Technology"
        ])
        self.category_combo.setFixedHeight(40)
        form_layout.addWidget(self.category_combo)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        buttons = self.create_buttons("Save Book", self.save_book)
        layout.addLayout(buttons)
    
    def save_book(self):
        """Save new book to database"""
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = self.isbn_input.text().strip()
        category = self.category_combo.currentText()
        
        # Validation
        if not all([title, author, isbn, category]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Validate ISBN
        isbn_clean = isbn.replace('-', '').replace(' ', '')
        if not (len(isbn_clean) in [10, 13] and isbn_clean.isdigit()):
            QMessageBox.warning(self, "Error", "Invalid ISBN format")
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
            QMessageBox.information(self, "Success", f"Book added successfully! (ID: {book_id})")
            if self.callback:
                self.callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add book")


class ConfirmDeleteDialog(QDialog):
    """Confirmation dialog for delete operations"""
    
    def __init__(self, parent=None, title="Confirm Delete", message="Are you sure?"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(700, 300)
        self.setModal(True)
        self.setup_ui(title, message)
        self.center_dialog()
    
    def setup_ui(self, title, message):
        """Setup confirmation UI"""
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['body']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(30)
        
        # Title
        title_label = QLabel(title.upper())
        title_label.setFont(QFont("Playfair Display", 22, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont("Montserrat", 13))
        message_label.setStyleSheet("color: white; background: transparent;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addStretch()
        
        # Yes button
        yes_btn = QPushButton("Yes")
        yes_btn.setFixedSize(140, 50)
        yes_btn.setFont(QFont("Montserrat", 12, QFont.Weight.Bold))
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.setStyleSheet(AppConfig.get_button_style('primary'))
        yes_btn.clicked.connect(self.accept)
        button_layout.addWidget(yes_btn)
        
        # No button
        no_btn = QPushButton("No")
        no_btn.setFixedSize(140, 50)
        no_btn.setFont(QFont("Montserrat", 12, QFont.Weight.Bold))
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setStyleSheet(AppConfig.get_button_style('primary'))
        no_btn.clicked.connect(self.reject)
        button_layout.addWidget(no_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def center_dialog(self):
        """Center dialog on screen"""
        if self.parent():
            parent_geo = self.parent().geometry()
            x = parent_geo.x() + (parent_geo.width() - self.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - self.height()) // 2
            self.move(x, y)