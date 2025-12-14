# curatel_lms/ui/patron_dialogs.py
# Patron dialogs: add, view, update, delete library members

import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

from curatel_lms.config import AppConfig


class BaseMemberDialog(QDialog):
    # Base class for member dialogs: shared layout, validation, DB ops
    
    def __init__(self, parent=None, db=None, member_data=None, callback=None):
        # Init with DB, data, and optional callback
        super().__init__(parent)
        self.db = db
        self.member_data = member_data if member_data else {}
        self.callback = callback
        self._configure_window()
    
    def _configure_window(self):
        # Set title, size, style, and center on screen
        self.setWindowTitle("Curatel - Patron Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, AppConfig.DIALOG_HEIGHT)
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_dialog']};")
        self._center_on_screen()
    
    def _center_on_screen(self):
        # Center dialog on primary screen
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
    
    def _create_header(self, text):
        # Make styled centered header widget
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
        # Create styled form container
        container_height = height if height else AppConfig.FORM_HEIGHT
        container = QWidget()
        container.setFixedSize(AppConfig.FORM_WIDTH, container_height)
        container.setStyleSheet(AppConfig.STYLES['form_container'])
        return container
    
    def _add_field(self, layout, label_text, widget):
        # Add labeled input field with tight spacing
        label = QLabel(label_text)
        label.setStyleSheet(AppConfig.STYLES['dialog_label'])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addSpacing(-20)
        layout.addWidget(widget)
    
    def _create_buttons(self, primary_text, primary_callback):
        # Create primary + cancel button row
        layout = QHBoxLayout()
        layout.setSpacing(30)
        layout.addStretch()
        primary_btn = QPushButton(primary_text)
        primary_btn.setFixedSize(AppConfig.BUTTON_WIDTH_EXTRA_WIDE, AppConfig.BUTTON_HEIGHT_LARGE)
        primary_btn.setStyleSheet(AppConfig.get_green_button_style())
        primary_btn.clicked.connect(primary_callback)
        layout.addWidget(primary_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(AppConfig.BUTTON_WIDTH_EXTRA_WIDE, AppConfig.BUTTON_HEIGHT_LARGE)
        cancel_btn.setStyleSheet(AppConfig.get_red_button_style())
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        layout.addStretch()
        return layout
    
    def _validate_inputs(self, full_name, email, mobile):
        # Check all fields filled and email valid
        if not all([full_name, email, mobile]):
            QMessageBox.warning(self, "Validation Error", "All fields are required. Please fill in name, email, and mobile number.")
            return False
        if not self._validate_email(email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address (e.g., name@example.com)")
            return False
        return True
    
    def _validate_email(self, email):
        # Basic email format check
        if "@" not in email or "." not in email:
            return False
        return re.match(r"^[^@]+@[^@]+\.[^@]+$", email) is not None
    
    def _generate_member_id(self):
        # Generate next sequential ID: MEM-001, MEM-002, etc.
        last_member = self.db.fetch_one("SELECT member_id FROM members ORDER BY member_id DESC LIMIT 1")
        if last_member:
            last_num = int(last_member['member_id'].split('-')[1])
            return f"MEM-{last_num + 1:03d}"
        return "MEM-001"


class AddMemberDialog(BaseMemberDialog):
    # Dialog to register new library members
    
    def __init__(self, parent=None, db=None, callback=None):
        # Init without existing data; compact size
        super().__init__(parent, db, None, callback)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, AppConfig.DIALOG_HEIGHT_COMPACT)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build add-member form with name, email, mobile
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        layout.addSpacing(-20)
        header = self._create_header("ADD MEMBER")
        layout.addWidget(header)
        layout.addSpacing(30)
        form_container = self._create_form_container(AppConfig.FORM_HEIGHT_COMPACT)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 50)
        form_layout.setSpacing(0)
        self.fullname_input = QLineEdit()
        self.fullname_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.fullname_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Full Name", self.fullname_input)
        self.email_input = QLineEdit()
        self.email_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.email_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Email", self.email_input)
        self.mobile_input = QLineEdit()
        self.mobile_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.mobile_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Mobile Number (+63)", self.mobile_input)
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        layout.addSpacing(30)
        buttons = self._create_buttons("Save", self._save_member)
        layout.addLayout(buttons)
    
    def _save_member(self):
        # Validate, check duplicate email, save to DB
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        if not self._validate_inputs(full_name, email, mobile):
            return
        check_query = "SELECT member_id FROM members WHERE email = %s"
        existing = self.db.fetch_one(check_query, (email,))
        if existing:
            QMessageBox.warning(self, "Duplicate Email", "This email address is already registered in the system.")
            return
        member_id = self._generate_member_id()
        now = datetime.now()
        query = """
            INSERT INTO members 
            (member_id, full_name, email, mobile_number, status, 
             borrowed_books, added_at, updated_at)
            VALUES (%s, %s, %s, %s, 'Active', 0, %s, %s)
        """
        try:
            if self.db.execute_query(query, (member_id, full_name, email, mobile, now, now)):
                QMessageBox.information(self, "Success", f"Member added successfully!\n\nMember ID: {member_id}")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to add member to database")
        except Exception as e:
            print(f"[ERROR] Add member failed: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while adding member:\n{str(e)}")


class ViewMemberDialog(BaseMemberDialog):
    # Read-only display of member details
    
    def __init__(self, parent=None, member_data=None):
        # Init without DB or callback
        super().__init__(parent, None, member_data, None)
        self._setup_ui()
    
    def _setup_ui(self):
        # Show all member fields as labels
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        header = self._create_header("MEMBER INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)
        info_container = self._create_form_container()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)
        self._add_info_field(info_layout, "Member ID:", self.member_data.get('member_id', ''))
        self._add_info_field(info_layout, "Full Name:", self.member_data.get('full_name', ''))
        self._add_info_field(info_layout, "Email:", self.member_data.get('email', ''))
        self._add_info_field(info_layout, "Mobile Number:", self.member_data.get('mobile_number', ''))
        self._add_info_field(info_layout, "Status:", self.member_data.get('status', ''))
        self._add_info_field(info_layout, "Borrowed Books:", self.member_data.get('borrowed_books', '0'))
        added_at = self._format_date(self.member_data.get('added_at'))
        updated_at = self._format_date(self.member_data.get('updated_at'))
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
        close_btn.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(AppConfig.get_red_button_style())
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _add_info_field(self, layout, label_text, value_text):
        # Add label-value row for read-only display
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
        # Convert datetime to YYYY-MM-DD string
        if date_value:
            return str(date_value).split()[0]
        return ''


class UpdateMemberDialog(BaseMemberDialog):
    # Edit existing member info (except ID)
    
    def __init__(self, parent=None, db=None, member_data=None, callback=None):
        # Init with existing data
        super().__init__(parent, db, member_data, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build update form pre-filled with current data
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        header = self._create_header("UPDATE MEMBER")
        layout.addWidget(header)
        layout.addSpacing(40)
        form_container = self._create_form_container()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        self.fullname_input = QLineEdit()
        self.fullname_input.setText(self.member_data.get('full_name', ''))
        self.fullname_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.fullname_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Full Name", self.fullname_input)
        self.email_input = QLineEdit()
        self.email_input.setText(self.member_data.get('email', ''))
        self.email_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.email_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Email", self.email_input)
        self.mobile_input = QLineEdit()
        self.mobile_input.setText(self.member_data.get('mobile_number', ''))
        self.mobile_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.mobile_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Mobile Number (+63)", self.mobile_input)
        self.status_combo = QComboBox()
        self.status_combo.addItems(AppConfig.MEMBER_STATUSES)
        self.status_combo.setCurrentText(self.member_data.get('status', 'Active'))
        self.status_combo.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.status_combo.setStyleSheet(AppConfig.STYLES['combo_with_dropdown'])
        self._add_field(form_layout, "Status", self.status_combo)
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        layout.addSpacing(50)
        buttons = self._create_buttons("Update", self._update_member)
        layout.addLayout(buttons)
    
    def _update_member(self):
        # Validate, check email conflict, update DB
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        status = self.status_combo.currentText()
        if not self._validate_inputs(full_name, email, mobile):
            return
        check_query = "SELECT member_id FROM members WHERE email = %s AND member_id != %s"
        existing = self.db.fetch_one(check_query, (email, self.member_data['member_id']))
        if existing:
            QMessageBox.warning(self, "Duplicate Email", "This email address is already used by another member.")
            return
        now = datetime.now()
        query = """
            UPDATE members 
            SET full_name = %s, email = %s, mobile_number = %s,
                status = %s, updated_at = %s
            WHERE member_id = %s
        """
        try:
            if self.db.execute_query(query, (full_name, email, mobile, status, now, self.member_data['member_id'])):
                QMessageBox.information(self, "Success", "Member information updated successfully!")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to update member in database")
        except Exception as e:
            print(f"[ERROR] Update member failed: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while updating member:\n{str(e)}")


class ConfirmDeleteMemberDialog(QDialog):
    # Confirm irreversible member deletion
    
    def __init__(self, parent=None, member_name=""):
        # Init with member name to display
        super().__init__(parent)
        self.member_name = member_name
        self._configure_window()
        self._setup_ui()
    
    def _configure_window(self):
        # Set compact size, title, style, center
        self.setWindowTitle("Curatel - Patron Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, 500)
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_dialog']};")
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
    
    def _setup_ui(self):
        # Show warning message and Yes/No buttons
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(AppConfig.STYLES['dialog_header'])
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_label = QLabel("CONFIRM DELETE MEMBER")
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
        message = QLabel(f"Are you sure you want to permanently delete\n'{self.member_name}'?")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("font-family: Montserrat; font-size: 20px; border: none; color: white;")
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