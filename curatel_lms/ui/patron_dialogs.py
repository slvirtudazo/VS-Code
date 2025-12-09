# curatel_lms/ui/patron_dialogs.py

"""
Patron management dialog windows.
Provides Add, View, Update, Delete dialogs for members.
"""

import re
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
DIALOG_HEIGHT_COMPACT = 680
FORM_WIDTH = 600
FORM_HEIGHT = 450
FORM_HEIGHT_COMPACT = 390
FIELD_WIDTH = 540
FIELD_HEIGHT = 50

# Color Constants
HEADER_BG = "#3C2A21"
DIALOG_BG = "#8B7E66"
BUTTON_GREEN = "#8BAE66"
BUTTON_GREEN_HOVER = "#A3B087"
BUTTON_RED = "#AF3E3E"
BUTTON_RED_HOVER = "#CD5656"

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

# Member status options
MEMBER_STATUSES = ["Active", "Inactive"]


class BaseMemberDialog(QDialog):
    """Base dialog class for member operations."""
    
    def __init__(self, parent=None, db=None, member_data=None, callback=None):
        """
        Initialize base dialog.
        Args:
            parent: Parent widget
            db: Database connection object
            member_data: Dictionary containing member data
            callback: Function to call after operation
        """
        super().__init__(parent)
        self.db = db
        self.member_data = member_data or {}
        self.callback = callback
        
        self._configure_window()
    
    def _configure_window(self):
        """Configure window properties."""
        self.setWindowTitle("Curatel - Patron Management")
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
    
    def _create_form_container(self, height=FORM_HEIGHT):
        """
        Create form container widget.
        Args:
            height: Container height
        Returns: QWidget configured as form container
        """
        container = QWidget()
        container.setFixedSize(FORM_WIDTH, height)
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
        layout.addSpacing(-20)
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
        primary_btn.setFixedSize(180, 60)
        primary_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_GREEN};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-weight: bold;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_GREEN_HOVER};
            }}
        """)
        primary_btn.clicked.connect(primary_callback)
        layout.addWidget(primary_btn)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(180, 60)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RED};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-weight: bold;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_RED_HOVER};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        layout.addStretch()
        return layout
    
    def _validate_inputs(self, full_name, email, mobile):
        """
        Validate member input fields.
        Args:
            full_name: Member full name
            email: Member email
            mobile: Member mobile number
        Returns: True if valid, False otherwise
        """
        if not all([full_name, email, mobile]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return False
        
        if not self._validate_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return False
        
        return True
    
    def _validate_email(self, email):
        """
        Validate email format using regex.
        Args:
            email: Email address to validate
        Returns: True if valid, False otherwise
        """
        if "@" not in email or "." not in email:
            return False
        return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None
    
    def _generate_member_id(self):
        """
        Generate next member ID.
        Returns: New member ID string
        """
        last_member = self.db.fetch_one(
            "SELECT member_id FROM members ORDER BY member_id DESC LIMIT 1"
        )
        
        if last_member:
            last_num = int(last_member['member_id'].split('-')[1])
            return f"MEM-{last_num + 1:03d}"
        
        return "MEM-001"


class AddMemberDialog(BaseMemberDialog):
    """Dialog for adding new members."""
    
    def __init__(self, parent=None, db=None, callback=None):
        """
        Initialize add member dialog.
        Args:
            parent: Parent widget
            db: Database connection object
            callback: Function to call after adding member
        """
        super().__init__(parent, db, None, callback)
        self.setFixedSize(DIALOG_WIDTH, DIALOG_HEIGHT_COMPACT)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        layout.addSpacing(-20)
        header = self._create_header("ADD MEMBER")
        layout.addWidget(header)
        layout.addSpacing(30)
        
        # Form container
        form_container = self._create_form_container(FORM_HEIGHT_COMPACT)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 50)
        form_layout.setSpacing(0)
        
        # Input fields
        self.fullname_input = QLineEdit()
        self.fullname_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.fullname_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Full Name", self.fullname_input)
        
        self.email_input = QLineEdit()
        self.email_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.email_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Email", self.email_input)
        
        self.mobile_input = QLineEdit()
        self.mobile_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.mobile_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Mobile Number (+63)", self.mobile_input)
        
        # Center form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(30)
        
        # Action buttons
        buttons = self._create_buttons("Save", self._save_member)
        layout.addLayout(buttons)
    
    def _save_member(self):
        """Save new member to database."""
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        
        # Validate inputs
        if not self._validate_inputs(full_name, email, mobile):
            return
        
        # Check for duplicate email
        check_query = "SELECT member_id FROM members WHERE email = %s"
        existing = self.db.fetch_one(check_query, (email,))
        if existing:
            QMessageBox.warning(self, "Error", "Email already exists in the system")
            return
        
        # Generate member ID
        member_id = self._generate_member_id()
        
        # Insert into database
        now = datetime.now()
        query = """
            INSERT INTO members 
            (member_id, full_name, email, mobile_number, status, borrowed_books, added_at, updated_at)
            VALUES (%s, %s, %s, %s, 'Active', 0, %s, %s)
        """
        
        try:
            if self.db.execute_query(query, (member_id, full_name, email, mobile, now, now)):
                QMessageBox.information(
                    self, "Success",
                    f"Member added successfully!\n\nMember ID: {member_id}"
                )
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add member to database")
        except Exception as e:
            print(f"[ERROR] Add member failed: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")


class ViewMemberDialog(BaseMemberDialog):
    """Dialog for viewing member details."""
    
    def __init__(self, parent=None, member_data=None):
        """
        Initialize view member dialog.
        Args:
            parent: Parent widget
            member_data: Dictionary containing member data
        """
        super().__init__(parent, None, member_data, None)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header("MEMBER INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        # Info container
        info_container = self._create_form_container()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)
        
        # Display fields
        self._add_info_field(info_layout, "Member ID:", self.member_data.get('member_id', ''))
        self._add_info_field(info_layout, "Full Name:", self.member_data.get('full_name', ''))
        self._add_info_field(info_layout, "Email:", self.member_data.get('email', ''))
        self._add_info_field(info_layout, "Mobile Number:", self.member_data.get('mobile_number', ''))
        self._add_info_field(info_layout, "Status:", self.member_data.get('status', ''))
        self._add_info_field(info_layout, "Borrowed Books:", self.member_data.get('borrowed_books', '0'))
        
        # Format and display dates
        added_at = self._format_date(self.member_data.get('added_at'))
        updated_at = self._format_date(self.member_data.get('updated_at'))
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
        close_btn.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RED};
                color: white;
                border: none;
                border-radius: 10px;
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


class UpdateMemberDialog(BaseMemberDialog):
    """Dialog for updating member information."""
    
    def __init__(self, parent=None, db=None, member_data=None, callback=None):
        """
        Initialize update member dialog.
        Args:
            parent: Parent widget
            db: Database connection object
            member_data: Dictionary containing member data
            callback: Function to call after updating member
        """
        super().__init__(parent, db, member_data, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header("UPDATE MEMBER")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        # Form container
        form_container = self._create_form_container()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        
        # Input fields with existing data
        self.fullname_input = QLineEdit()
        self.fullname_input.setText(self.member_data.get('full_name', ''))
        self.fullname_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.fullname_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Full Name", self.fullname_input)
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.member_data.get('email', ''))
        self.email_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.email_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Email", self.email_input)
        
        self.mobile_input = QLineEdit()
        self.mobile_input.setText(self.member_data.get('mobile_number', ''))
        self.mobile_input.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.mobile_input.setStyleSheet(INPUT_STYLE)
        self._add_field(form_layout, "Mobile Number (+63)", self.mobile_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(MEMBER_STATUSES)
        self.status_combo.setCurrentText(self.member_data.get('status', 'Active'))
        self.status_combo.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        self.status_combo.setStyleSheet(COMBO_STYLE)
        self._add_field(form_layout, "Status", self.status_combo)
        
        # Center form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(50)
        
        # Action buttons
        buttons = self._create_buttons("Update", self._update_member)
        layout.addLayout(buttons)
    
    def _update_member(self):
        """Update member in database."""
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        status = self.status_combo.currentText()
        
        # Validate inputs
        if not self._validate_inputs(full_name, email, mobile):
            return
        
        # Check for duplicate email
        check_query = "SELECT member_id FROM members WHERE email = %s AND member_id != %s"
        existing = self.db.fetch_one(check_query, (email, self.member_data['member_id']))
        if existing:
            QMessageBox.warning(self, "Error", "Email already exists for another member")
            return
        
        # Update in database
        now = datetime.now()
        query = """
            UPDATE members 
            SET full_name = %s, email = %s, mobile_number = %s, status = %s, updated_at = %s
            WHERE member_id = %s
        """
        
        try:
            if self.db.execute_query(
                query,
                (full_name, email, mobile, status, now, self.member_data['member_id'])
            ):
                QMessageBox.information(self, "Success", "Member updated successfully!")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update member")
        except Exception as e:
            print(f"[ERROR] Update member failed: {e}")
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")


class ConfirmDeleteMemberDialog(QDialog):
    """Confirmation dialog for deleting a member."""
    
    def __init__(self, parent=None, member_name=""):
        """
        Initialize delete confirmation dialog.
        Args:
            parent: Parent widget
            member_name: Name of member to delete
        """
        super().__init__(parent)
        self.member_name = member_name
        
        self._configure_window()
        self._setup_ui()
    
    def _configure_window(self):
        """Configure window properties."""
        self.setWindowTitle("Curatel - Patron Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(DIALOG_WIDTH, 500)
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
        
        header_label = QLabel("CONFIRM DELETE MEMBER")
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
            f"Are you sure you want to permanently delete\n'{self.member_name}'?"
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