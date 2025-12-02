# ui/patron_dialogs.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, 
                              QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime

class AddMemberDialog(QDialog):
    """Dialog for adding new members - matches AddBookDialog design"""
    
    def __init__(self, parent=None, db=None, callback=None):
        super().__init__(parent)
        self.db = db
        self.callback = callback

        # Same window setup as AddBookDialog
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 680)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())

        self.setWindowTitle("Curatel - Patron Management")
        self.setup_ui()
    
    def create_header(self, text):
        """Create header matching book dialog style"""
        header = QWidget()
        header.setFixedHeight(80)
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
            letter-spacing: 3px;
            color: white;
        """)

        header_layout.addWidget(label)
        return header

    def setup_ui(self):
        """Setup UI matching AddBookDialog"""
        # Set dialog background to match book dialog
        self.setStyleSheet("background-color: #8B7E66;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        layout.addSpacing(-20)
        header = self.create_header("ADD MEMBER")
        layout.addWidget(header)
        layout.addSpacing(30)

        # Main frame container - same size and style as book dialog
        form_container = QWidget()
        form_container.setFixedSize(600, 390)
        form_container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 50)
        form_layout.setSpacing(0)

        # Styles matching book dialog
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

        FIELD_W = 540
        FIELD_H = 50

        # Helper function to add fields
        def add_field(label_text, widget):  
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            form_layout.addWidget(label)
            form_layout.addSpacing(-20)           # label to field spacing
            form_layout.addWidget(widget)

        # FULL NAME
        self.fullname_input = QLineEdit()
        self.fullname_input.setFixedSize(FIELD_W, FIELD_H)
        self.fullname_input.setStyleSheet(input_style)
        add_field("Full Name", self.fullname_input)

        # EMAIL
        self.email_input = QLineEdit()
        self.email_input.setFixedSize(FIELD_W, FIELD_H)
        self.email_input.setStyleSheet(input_style)
        add_field("Email", self.email_input)

        # MOBILE NUMBER
        self.mobile_input = QLineEdit()
        self.mobile_input.setFixedSize(FIELD_W, FIELD_H)
        self.mobile_input.setStyleSheet(input_style)
        add_field("Mobile Number (+63)", self.mobile_input)

        # Center the form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)

        layout.addSpacing(30)

        # Buttons - matching book dialog button style
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setFixedSize(180, 60)
        save_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #8BAE66;
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #A3B087;
            }
        """)
        save_btn.clicked.connect(self.save_member)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(180, 60)
        cancel_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #CD5656;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def save_member(self):
        """Save new member to database"""
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        
        # Validation
        if not all([full_name, email, mobile]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        # Check if email already exists
        check_query = "SELECT member_id FROM members WHERE email = %s"
        existing = self.db.fetch_one(check_query, (email,))
        if existing:
            QMessageBox.warning(self, "Error", "Email already exists in the system")
            return
        
        # Generate member ID
        last_member = self.db.fetch_one("SELECT member_id FROM members ORDER BY member_id DESC LIMIT 1")
        if last_member:
            last_num = int(last_member['member_id'].split('-')[1])
            member_id = f"MEM-{last_num + 1:03d}"
        else:
            member_id = "MEM-001"
        
        # Insert into database
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

class ViewMemberDialog(QDialog):
    """Dialog for viewing member details - matches ViewBookDialog design"""
    
    def __init__(self, parent=None, member_data=None):
        super().__init__(parent)
        self.member_data = member_data
        
        # Same window setup as ViewBookDialog
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 700)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())
        
        self.setWindowTitle("Curatel - Patron Management")
        self.setup_ui()
    
    def create_header(self, text):
        """Create header matching ViewBookDialog style"""
        header = QWidget()
        header.setFixedHeight(80)
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
            letter-spacing: 3px;
            color: white;
        """)

        header_layout.addWidget(label)
        return header

    def setup_ui(self):
        """Setup view member UI matching ViewBookDialog"""
        # Set dialog background
        self.setStyleSheet("background-color: #8B7E66;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        header = self.create_header("MEMBER INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)

        # Main frame container
        info_container = QWidget()
        info_container.setFixedSize(600, 450)
        info_container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)

        # Label and value styles
        label_style = """
            font-family: Montserrat;
            font-size: 15px;
            color: white;
            border: none;
            background: transparent;
        """

        value_style = """
            font-family: Montserrat;
            font-size: 15px;
            color: white;
            border: none;
            background: transparent;
            text-decoration: underline;
        """

        def add_field(label_text, value_text):
            """Add a field row with label and value"""
            row = QWidget()
            row.setStyleSheet("border: none; background: transparent;")

            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(100)

            # Left label
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Right value
            value = QLabel(str(value_text))
            value.setStyleSheet(value_style)
            value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            value.setWordWrap(True)

            row_layout.addWidget(label, 1)
            row_layout.addWidget(value, 2)

            info_layout.addWidget(row)

        # Display member fields
        add_field("Member ID:", self.member_data.get('member_id', ''))
        add_field("Full Name:", self.member_data.get('full_name', ''))
        add_field("Email:", self.member_data.get('email', ''))
        add_field("Mobile Number:", self.member_data.get('mobile_number', ''))
        add_field("Status:", self.member_data.get('status', ''))
        add_field("Borrowed Books:", self.member_data.get('borrowed_books', '0'))

        # Format dates
        added_at = str(self.member_data.get('added_at', '')).split()[0] if self.member_data.get('added_at') else ''
        updated_at = str(self.member_data.get('updated_at', '')).split()[0] if self.member_data.get('updated_at') else ''

        add_field("Added At:", added_at)
        add_field("Updated At:", updated_at)

        # Center the container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(info_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)

        layout.addSpacing(40)

        # Close button matching ViewBookDialog
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedSize(150, 60)
        close_btn.setFont(QFont("Montserrat", 15))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 10px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CD5656;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

class UpdateMemberDialog(QDialog):
    """Dialog for updating member information - matches UpdateBookDialog design"""

    def __init__(self, parent=None, db=None, member_data=None, callback=None):
        super().__init__(parent)
        self.db = db
        self.member_data = member_data
        self.callback = callback

        # Same window setup as UpdateBookDialog
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 700)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())
        self.setWindowTitle("Curatel - Patron Management")

        self.setup_ui()

    def create_header(self, text):
        """Create header matching UpdateBookDialog style"""
        header = QWidget()
        header.setFixedHeight(80)
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
            letter-spacing: 3px;
            color: white;
        """)

        header_layout.addWidget(label)
        return header

    def setup_ui(self):
        """Setup update member UI matching UpdateBookDialog"""
        # Set dialog background
        self.setStyleSheet("background-color: #8B7E66;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        header = self.create_header("UPDATE MEMBER")
        layout.addWidget(header)
        layout.addSpacing(40)

        # Frame container
        form_container = QWidget()
        form_container.setFixedSize(600, 450)
        form_container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)

        # Styles
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

        # Helper function
        def add_field(label_text, widget):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            form_layout.addWidget(label)
            form_layout.addWidget(widget)

        # FULL NAME
        self.fullname_input = QLineEdit()
        self.fullname_input.setText(self.member_data.get('full_name', ''))
        self.fullname_input.setFixedSize(FIELD_W, FIELD_H)
        self.fullname_input.setStyleSheet(input_style)
        add_field("Full Name", self.fullname_input)

        # EMAIL
        self.email_input = QLineEdit()
        self.email_input.setText(self.member_data.get('email', ''))
        self.email_input.setFixedSize(FIELD_W, FIELD_H)
        self.email_input.setStyleSheet(input_style)
        add_field("Email", self.email_input)

        # MOBILE NUMBER
        self.mobile_input = QLineEdit()
        self.mobile_input.setText(self.member_data.get('mobile_number', ''))
        self.mobile_input.setFixedSize(FIELD_W, FIELD_H)
        self.mobile_input.setStyleSheet(input_style)
        add_field("Mobile Number (+63)", self.mobile_input)

        # STATUS
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Inactive"])
        current_status = self.member_data.get('status', 'Active')
        self.status_combo.setCurrentText(current_status)
        self.status_combo.setFixedSize(FIELD_W, FIELD_H)
        self.status_combo.setStyleSheet(combo_style)
        add_field("Status", self.status_combo)

        # Center frame
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)

        layout.addSpacing(50)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.addStretch()

        update_btn = QPushButton("Update")
        update_btn.setFixedSize(150, 60)
        update_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #8BAE66;
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;                 
            }
            QPushButton:hover {
                background-color: #A3B087;
            }
        """)
        update_btn.clicked.connect(self.update_member)
        button_layout.addWidget(update_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(150, 60)
        cancel_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;                 
            }
            QPushButton:hover {
                background-color: #CD5656;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def update_member(self):
        """Update member in database"""
        full_name = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        mobile = self.mobile_input.text().strip()
        status = self.status_combo.currentText()

        # Validation
        if not all([full_name, email, mobile]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        # Email validation
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Error", "Please enter a valid email address")
            return
        
        # Check if email exists for another member
        check_query = "SELECT member_id FROM members WHERE email = %s AND member_id != %s"
        existing = self.db.fetch_one(check_query, (email, self.member_data['member_id']))
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

class ConfirmDeleteMemberDialog(QDialog):
    """Confirmation dialog for deleting a member - matches ConfirmDeleteDialog design"""

    def __init__(self, parent=None, member_name=""):
        super().__init__(parent)
        self.member_name = member_name

        # Same window setup as ConfirmDeleteDialog
        self.setWindowTitle("Curatel - Patron Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 500)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())

        # Set main background color
        self.setStyleSheet("background-color: #8B7E66;")

        self.setup_ui()

    def setup_ui(self):
        """Setup UI matching ConfirmDeleteDialog"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #3C2A21; border: none;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

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

        # Frame Container
        frame = QWidget()
        frame.setFixedSize(600, 250)
        frame.setStyleSheet("""
            background-color: #8B7E66;
            border: none
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(30, 20, 30, 20)
        frame_layout.setSpacing(20)

        message = QLabel(f"Are you sure you want to permanently delete:\n'{self.member_name}'?")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setWordWrap(True)
        message.setStyleSheet("""
            font-family: Montserrat;
            font-size: 20px;
            border: none;
            color: white;
            background-color: #8B7E66;
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

        # Buttons matching ConfirmDeleteDialog
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        buttons_layout.setSpacing(30)

        yes_btn = QPushButton("Yes")
        yes_btn.setFixedSize(150, 60)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #CD5656;
            }
        """)
        yes_btn.clicked.connect(self.accept)

        no_btn = QPushButton("No")
        no_btn.setFixedSize(150, 60)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setStyleSheet("""
            QPushButton {
                background-color: #8BAE66;
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #A3B087;
            }
        """)
        no_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(yes_btn)
        buttons_layout.addWidget(no_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)