# curatel_lms/ui/patron_dialogs.py

"""
Patron management dialog windows.
Provides Add, View, Update, Delete dialogs for members.
"""

import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QWidget, QSizePolicy, QLineEdit, QPushButton,
    QComboBox, QMessageBox, QApplication
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

    def _validate_inputs(self, full_name, email, mobile):
        """Validate member input fields."""
        if not all([full_name, email, mobile]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return False

        if not self._validate_email(email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return False

        return True

    def _validate_email(self, email):
        """Validate email format using regex."""
        return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None

    def _generate_member_id(self):
        """Generate next member ID."""
        last_member = self.db.fetch_one(
            "SELECT member_id FROM members ORDER BY member_id DESC LIMIT 1"
        )
        if last_member:
            last_num = int(last_member['member_id'].split('-')[1])
            return f"MEM-{last_num + 1:03d}"
        return "MEM-001"

    def _create_header(self, text):
        """Reusable header widget."""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background-color: {HEADER_BG}; border: none;")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            font-family: Montserrat;
            font-size: 30px;
            font-weight: bold;
            letter-spacing: 3px;
            color: white;
        """)
        header_layout.addWidget(label)
        return header

    def _add_info_field(self, parent_layout, label_text, value_text):
        """Helper to add a label-value field pair in View dialog."""
        row = QWidget()
        row.setStyleSheet("border: none; background: transparent;")

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(100)

        label = QLabel(label_text)
        label.setStyleSheet(LABEL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

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
        parent_layout.addWidget(row)

class AddMemberDialog(BaseMemberDialog):
    """Dialog for adding new members."""

    def __init__(self, parent=None, db=None, callback=None):
        super().__init__(parent, db=db, callback=callback)
        self.setFixedSize(DIALOG_WIDTH, 640)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("ADD MEMBER")
        layout.addWidget(header)
        layout.addSpacing(40)

        form_container = self._create_form_container()
        layout.addLayout(self._center_widget(form_container))
        layout.addSpacing(40)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(30)

        save_btn = QPushButton("Save")
        save_btn.setFixedSize(150, 60)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
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
        save_btn.clicked.connect(self._save_member)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(150, 60)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_form_container(self):
        container = QWidget()
        container.setFixedSize(FORM_WIDTH, 390)
        container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        form_layout = QVBoxLayout(container)
        form_layout.setContentsMargins(30, 10, 30, 50)
        form_layout.setSpacing(0)

        self.fullname_input = self._create_input_field(form_layout, "Full Name")
        self.email_input = self._create_input_field(form_layout, "Email")
        self.mobile_input = self._create_input_field(form_layout, "Mobile Number (+63)")

        return container

    def _create_input_field(self, parent_layout, label_text):
        label = QLabel(label_text)
        label.setStyleSheet(LABEL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(label)
        parent_layout.addSpacing(-20)

        line_edit = QLineEdit()
        line_edit.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        line_edit.setStyleSheet(INPUT_STYLE)
        parent_layout.addWidget(line_edit)
        return line_edit

    def _save_member(self):
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()

        if not self._validate_inputs(full_name, email, mobile):
            return

        # Check email uniqueness
        existing = self.db.fetch_one("SELECT member_id FROM members WHERE email = %s", (email,))
        if existing:
            QMessageBox.warning(self, "Error", "Email already exists in the system")
            return

        member_id = self._generate_member_id()
        now = datetime.now()
        query = """
        INSERT INTO members (member_id, full_name, email, mobile_number, status, borrowed_books, added_at, updated_at)
        VALUES (%s, %s, %s, %s, 'Active', 0, %s, %s)
        """

        if self.db.execute_query(query, (member_id, full_name, email, mobile, now, now)):
            QMessageBox.information(self, "Success", f"Member added successfully!\n\nMember ID: {member_id}")
            if self.callback:
                self.callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add member to database")

    def _center_widget(self, widget):
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        return layout

class ViewMemberDialog(BaseMemberDialog):
    """Dialog for viewing member details."""

    def __init__(self, parent=None, member_data=None):
        super().__init__(parent, member_data=member_data)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("MEMBER INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)

        info_container = self._create_info_container()
        layout.addLayout(self._center_widget(info_container))
        layout.addSpacing(40)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(150, 60)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor) 
        close_btn.setStyleSheet(f"""
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
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _create_info_container(self):
        container = QWidget()
        container.setFixedSize(FORM_WIDTH, FORM_HEIGHT)
        container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        info_layout = QVBoxLayout(container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)

        self._add_info_field(info_layout, "Member ID:", self.member_data.get('member_id', ''))
        self._add_info_field(info_layout, "Full Name:", self.member_data.get('full_name', ''))
        self._add_info_field(info_layout, "Email:", self.member_data.get('email', ''))
        self._add_info_field(info_layout, "Mobile Number:", self.member_data.get('mobile_number', ''))
        self._add_info_field(info_layout, "Status:", self.member_data.get('status', ''))
        self._add_info_field(info_layout, "Borrowed Books:", self.member_data.get('borrowed_books', '0'))

        added_at = str(self.member_data.get('added_at', '')).split()[0] if self.member_data.get('added_at') else ''
        updated_at = str(self.member_data.get('updated_at', '')).split()[0] if self.member_data.get('updated_at') else ''
        self._add_info_field(info_layout, "Added At:", added_at)
        self._add_info_field(info_layout, "Updated At:", updated_at)

        return container

    def _center_widget(self, widget):
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        return layout

class UpdateMemberDialog(BaseMemberDialog):
    """Dialog for updating member information."""

    def __init__(self, parent=None, db=None, member_data=None, callback=None):
        super().__init__(parent, db=db, member_data=member_data, callback=callback)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("UPDATE MEMBER")
        layout.addWidget(header)
        layout.addSpacing(40)

        form_container = self._create_form_container()
        layout.addLayout(self._center_widget(form_container))
        layout.addSpacing(40)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(30)

        update_btn = QPushButton("Update")
        update_btn.setFixedSize(150, 60)
        update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        update_btn.setStyleSheet(f"""
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
        update_btn.clicked.connect(self._update_member)
        button_layout.addWidget(update_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(150, 60)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
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
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_form_container(self):
        container = QWidget()
        container.setFixedSize(FORM_WIDTH, FORM_HEIGHT)
        container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        form_layout = QVBoxLayout(container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        form_layout.setSpacing(10)

        self.fullname_input = self._create_input_field(form_layout, "Full Name", self.member_data.get('full_name', ''))
        self.email_input = self._create_input_field(form_layout, "Email", self.member_data.get('email', ''))
        self.mobile_input = self._create_input_field(form_layout, "Mobile Number (+63)", self.member_data.get('mobile_number', ''))
        self.status_combo = self._create_status_combo(form_layout, self.member_data.get('status', 'Active'))

        return container

    def _create_input_field(self, parent_layout, label_text, default=""):
        label = QLabel(label_text)
        label.setStyleSheet(LABEL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(label)

        line_edit = QLineEdit()
        line_edit.setText(default)
        line_edit.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        line_edit.setStyleSheet(INPUT_STYLE)
        parent_layout.addWidget(line_edit)
        return line_edit

    def _create_status_combo(self, parent_layout, current_status):
        label = QLabel("Status")
        label.setStyleSheet(LABEL_STYLE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(label)

        combo = QComboBox()
        combo.addItems(MEMBER_STATUSES)
        combo.setCurrentText(current_status)
        combo.setFixedSize(FIELD_WIDTH, FIELD_HEIGHT)
        combo.setStyleSheet(COMBO_STYLE)
        parent_layout.addWidget(combo)
        return combo

    def _update_member(self):
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        status = self.status_combo.currentText()

        if not self._validate_inputs(full_name, email, mobile):
            return

        # Check for duplicate email (excluding current member)
        existing = self.db.fetch_one(
            "SELECT member_id FROM members WHERE email = %s AND member_id != %s",
            (email, self.member_data['member_id'])
        )
        if existing:
            QMessageBox.warning(self, "Error", "Email already exists for another member")
            return

        now = datetime.now()
        query = """
        UPDATE members 
        SET full_name = %s, email = %s, mobile_number = %s, status = %s, updated_at = %s
        WHERE member_id = %s
        """

        if self.db.execute_query(query, (full_name, email, mobile, status, now, self.member_data['member_id'])):
            QMessageBox.information(self, "Success", "Member updated successfully!")
            if self.callback:
                self.callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update member")

    def _center_widget(self, widget):
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        return layout

class ConfirmDeleteMemberDialog(BaseMemberDialog):
    """Confirmation dialog for deleting a member."""

    def __init__(self, parent=None, member_name=""):
        super().__init__(parent)
        self.member_name = member_name
        self.setFixedSize(DIALOG_WIDTH, 500)
        self._center_on_screen()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        header = self._create_header("CONFIRM DELETE MEMBER")
        layout.addWidget(header)
        layout.addSpacing(40)

        frame = self._create_message_frame()
        layout.addLayout(self._center_widget(frame))
        layout.addSpacing(40)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.setSpacing(30)

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

        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_message_frame(self):
        frame = QWidget()
        frame.setFixedSize(600, 250)
        frame.setStyleSheet(f"background-color: {DIALOG_BG}; border: none;")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(30, 20, 30, 20)
        frame_layout.setSpacing(20)

        message = QLabel(f"Are you sure you want to permanently delete\n'{self.member_name}'?")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("""
            font-family: Montserrat;
            font-size: 20px;
            color: white;
            background-color: transparent;
            border: none;
        """)
        frame_layout.addStretch()
        frame_layout.addWidget(message)
        frame_layout.addStretch()

        return frame

    def _center_widget(self, widget):
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        return layout