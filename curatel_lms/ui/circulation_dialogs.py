# curatel_lms/ui/circulation_dialogs.py

# Provides dialog interfaces for adding, viewing, updating, and deleting transactions

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
from curatel_lms.config import AppConfig

class BaseTransactionDialog(QDialog):
    # Base dialog for transaction CRUD with shared UI/logic
    
    def __init__(self, parent=None, db=None, transaction_data=None, callback=None):
        # Init base dialog with db, data, and callback
        super().__init__(parent)
        
        self.db = db
        self.transaction_data = transaction_data if transaction_data else {}
        self.callback = callback
        
        self._configure_window()
    
    def _configure_window(self):
        # Set consistent dialog size, style, and centering
        self.setWindowTitle("Curatel - Circulation Management")
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
        # Create styled header widget
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
        container_height = height if height else AppConfig.FORM_HEIGHT_MEDIUM
        container = QWidget()
        container.setFixedSize(AppConfig.FORM_WIDTH, container_height)
        container.setStyleSheet(AppConfig.STYLES['form_container'])
        return container
    
    def _add_field(self, layout, label_text, widget):
        # Add labeled input field to layout
        label = QLabel(label_text)
        label.setStyleSheet(AppConfig.STYLES['dialog_label'])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
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
    
    @staticmethod
    def _validate_date_format(date_string):
        # Check if date string is YYYY-MM-DD
        qdate = QDate.fromString(date_string, "yyyy-MM-dd")
        return qdate.isValid()
    
    @staticmethod
    def _format_date_for_display(date_value):
        # Convert date to string; empty if None
        if date_value is None or str(date_value).strip().lower() in ('none', 'null', ''):
            return ""
        return str(date_value)

class AddBorrowDialog(BaseTransactionDialog):
    # Dialog to create new borrow transaction
    
    def __init__(self, parent=None, db=None, callback=None):
        # Init add dialog
        super().__init__(parent, db, None, callback)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build add transaction form
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        layout.addSpacing(-30)
        header = self._create_header("ADD TRANSACTION")
        layout.addWidget(header)
        layout.addSpacing(30)
        
        form_container = self._create_form_container(AppConfig.FORM_HEIGHT_MEDIUM)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 20, 30, 30)
        form_layout.setSpacing(10)
        
        # Book ID input
        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("e.g., BK-001")
        self.book_id_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.book_id_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Book ID", self.book_id_input)
        
        # Member ID input
        self.member_id_input = QLineEdit()
        self.member_id_input.setPlaceholderText("e.g., MEM-001")
        self.member_id_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.member_id_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Member ID", self.member_id_input)
        
        # Borrow date input
        self.borrow_date_input = QLineEdit()
        self.borrow_date_input.setPlaceholderText("YYYY-MM-DD")
        self.borrow_date_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.borrow_date_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Borrow Date", self.borrow_date_input)
        
        # Due date input
        self.due_date_input = QLineEdit()
        self.due_date_input.setPlaceholderText("YYYY-MM-DD")
        self.due_date_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.due_date_input.setStyleSheet(AppConfig.STYLES['input'])
        self._add_field(form_layout, "Due Date", self.due_date_input)
        
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(30)
        
        buttons = self._create_buttons("Save", self._save_transaction)
        layout.addLayout(buttons)
    
    def _save_transaction(self):
        # Validate and save new borrow record
        book_id = self.book_id_input.text().strip()
        member_id = self.member_id_input.text().strip()
        borrow_date_text = self.borrow_date_input.text().strip()
        due_date_text = self.due_date_input.text().strip()
        
        if not all([book_id, member_id, borrow_date_text, due_date_text]):
            QMessageBox.warning(self, "Validation Error", "All fields are required")
            return
        
        if not self._validate_date_format(borrow_date_text):
            QMessageBox.warning(self, "Invalid Date", "Invalid Borrow Date format. Use YYYY-MM-DD.")
            return
        
        if not self._validate_date_format(due_date_text):
            QMessageBox.warning(self, "Invalid Date", "Invalid Due Date format. Use YYYY-MM-DD.")
            return
        
        now_time_str = datetime.now().strftime("%H:%M:%S")
        borrow_date = f"{borrow_date_text} {now_time_str}"
        due_date = f"{due_date_text} {now_time_str}"
        
        book_query = "SELECT book_id, status, title FROM books WHERE book_id = %s"
        book = self.db.fetch_one(book_query, (book_id,))
        
        if not book:
            QMessageBox.warning(self, "Book Not Found", f"Book ID '{book_id}' does not exist.")
            return
        
        if book['status'] != 'Available':
            QMessageBox.warning(self, "Book Unavailable", 
                              f"Book '{book['title']}' is currently {book['status']}.")
            return
        
        member_query = "SELECT member_id, status, full_name FROM members WHERE member_id = %s"
        member = self.db.fetch_one(member_query, (member_id,))
        
        if not member:
            QMessageBox.warning(self, "Member Not Found", f"Member ID '{member_id}' does not exist.")
            return
        
        if member['status'] != 'Active':
            QMessageBox.warning(self, "Member Inactive", 
                              f"Member '{member['full_name']}' is currently {member['status']}.")
            return
        
        query = """
            INSERT INTO borrowed_books 
            (book_id, member_id, borrow_date, due_date, return_date, status, fine_amount)
            VALUES (%s, %s, %s, %s, NULL, 'Borrowed', 0.00)
        """
        
        try:
            if self.db.execute_query(query, (book_id, member_id, borrow_date, due_date)):
                self.db.execute_query("UPDATE books SET status='Borrowed' WHERE book_id=%s", (book_id,))
                
                QMessageBox.information(
                    self, "Success",
                    f"Transaction added successfully!\n\n"
                    f"Book: {book['title']}\n"
                    f"Member: {member['full_name']}\n"
                    f"Borrow Date: {borrow_date_text}\n"
                    f"Due Date: {due_date_text}"
                )
                
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to add transaction")
        except Exception as e:
            print(f"[ERROR] Add transaction failed: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")

class ViewBorrowDialog(BaseTransactionDialog):
    # Read-only dialog to show transaction details
    
    def __init__(self, parent=None, borrow_data=None):
        # Init view dialog
        super().__init__(parent, None, borrow_data, None)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, AppConfig.DIALOG_HEIGHT_EXTENDED)
        self._center_on_screen()
        self._setup_ui()
    
    def _setup_ui(self):
        # Build read-only transaction info layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        header = self._create_header("TRANSACTION INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        info_container = self._create_form_container(AppConfig.FORM_HEIGHT_LARGE)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(50, 20, 50, 20)
        info_layout.setSpacing(20)
        
        self._add_info_field(info_layout, "Book ID:", self.transaction_data.get('book_id', ''))
        self._add_info_field(info_layout, "Book Title:", self.transaction_data.get('book_title', 'Unknown'))
        self._add_info_field(info_layout, "Member ID:", self.transaction_data.get('member_id', ''))
        self._add_info_field(info_layout, "Member Name:", self.transaction_data.get('member_name', 'Unknown'))
        self._add_info_field(info_layout, "Borrow Date:", str(self.transaction_data.get('borrow_date', '')))
        self._add_info_field(info_layout, "Due Date:", str(self.transaction_data.get('due_date', '')))
        
        return_date = self.transaction_data.get('return_date')
        return_date_display = str(return_date) if return_date else 'Not Returned'
        self._add_info_field(info_layout, "Return Date:", return_date_display)
        
        self._add_info_field(info_layout, "Status:", self.transaction_data.get('status', ''))
        
        fine = f"₱{float(self.transaction_data.get('fine_amount', 0)):.2f}"
        self._add_info_field(info_layout, "Fine Amount:", fine)
        
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(info_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(AppConfig.BUTTON_WIDTH_EXTRA_WIDE, AppConfig.BUTTON_HEIGHT_LARGE)
        close_btn.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(AppConfig.get_red_button_style())
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _add_info_field(self, layout, label_text, value_text):
        # Add readonly label-value row
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

class UpdateBorrowDialog(BaseTransactionDialog):
    # Dialog to edit return date, status, and fine
    
    def __init__(self, parent=None, db=None, borrow_data=None, callback=None):
        # Init update dialog
        super().__init__(parent, db, borrow_data, callback)
        
        self._is_valid = bool(self.transaction_data and self.transaction_data.get("borrow_id"))
        
        self.setFixedSize(AppConfig.DIALOG_WIDTH, AppConfig.DIALOG_HEIGHT_COMPACT)
        self._setup_ui()
    
    def _setup_ui(self):
        # Build update form or error if invalid
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        if not self._is_valid:
            self._create_error_ui(layout)
            return
        
        layout.addSpacing(-35)
        header = self._create_header("UPDATE TRANSACTION")
        layout.addWidget(header)
        layout.addSpacing(30)
        
        form_container = self._create_form_container(AppConfig.FORM_HEIGHT_COMPACT)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 10, 30, 30)
        
        self.return_date_input = QLineEdit()
        self.return_date_input.setPlaceholderText("YYYY-MM-DD")
        self.return_date_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.return_date_input.setStyleSheet(AppConfig.STYLES['input'])
        
        existing_return = self.transaction_data.get('return_date')
        if existing_return and str(existing_return).strip().lower() not in ('none', 'null', ''):
            try:
                date_part = str(existing_return).split(' ')[0]
                self.return_date_input.setText(date_part)
            except Exception:
                pass
        
        self._add_field(form_layout, "Return Date", self.return_date_input)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(AppConfig.TRANSACTION_STATUSES)
        self.status_combo.setCurrentText(self.transaction_data.get('status', 'Borrowed'))
        self.status_combo.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.status_combo.setStyleSheet(AppConfig.STYLES['combo_with_dropdown'])
        self._add_field(form_layout, "Status", self.status_combo)
        
        self.fine_input = QLineEdit()
        self.fine_input.setPlaceholderText("0.00")
        self.fine_input.setFixedSize(AppConfig.FIELD_WIDTH, AppConfig.FIELD_HEIGHT)
        self.fine_input.setStyleSheet(AppConfig.STYLES['input'])
        
        existing_fine = self.transaction_data.get('fine_amount')
        if existing_fine is not None:
            try:
                self.fine_input.setText(f"{float(existing_fine):.2f}")
            except (ValueError, TypeError):
                pass
        
        self._add_field(form_layout, "Fine Amount (₱)", self.fine_input)
        
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)
        
        layout.addSpacing(30)
        
        buttons = self._create_buttons("Update", self._update_transaction)
        layout.addLayout(buttons)
    
    def _create_error_ui(self, layout):
        # Show error if no transaction selected
        header = self._create_header("UPDATE TRANSACTION")
        layout.addWidget(header)
        layout.addSpacing(40)
        
        error_label = QLabel("No valid transaction selected.\nPlease select a row from the table.")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet(AppConfig.STYLES['dialog_label'])
        layout.addWidget(error_label)
        layout.addSpacing(40)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(AppConfig.BUTTON_WIDTH_EXTRA_WIDE, AppConfig.BUTTON_HEIGHT_LARGE)
        close_btn.setStyleSheet(AppConfig.get_red_button_style())
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _update_transaction(self):
        # Validate and save updated fields
        return_date_text = self.return_date_input.text().strip()
        status = self.status_combo.currentText()
        fine_text = self.fine_input.text().strip()
        
        return_date = None
        if return_date_text:
            if not self._validate_date_format(return_date_text):
                QMessageBox.warning(self, "Invalid Date", 
                                  "Invalid Return Date format. Use YYYY-MM-DD.")
                return
            return_date = f"{return_date_text} {datetime.now().strftime('%H:%M:%S')}"
        
        if status == "Returned" and not return_date_text:
            reply = QMessageBox.question(
                self, 'Confirm Return Date',
                "Status is 'Returned' but no Return Date is entered. Use today's date?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                today = QDate.currentDate().toString("yyyy-MM-dd")
                return_date = f"{today} {datetime.now().strftime('%H:%M:%S')}"
            else:
                return
        
        try:
            fine = float(fine_text) if fine_text else 0.0
            if fine < 0:
                QMessageBox.warning(self, "Invalid Fine", "Fine cannot be negative")
                return
        except ValueError:
            QMessageBox.warning(self, "Invalid Fine", "Invalid fine amount")
            return
        
        borrow_id = self.transaction_data.get("borrow_id")
        book_id = self.transaction_data.get('book_id')
        current_status = self.transaction_data.get('status')
        
        if status == "Returned" and current_status != "Returned":
            self.db.execute_query("UPDATE books SET status='Available' WHERE book_id=%s", (book_id,))
        elif status != "Returned" and current_status == "Returned":
            self.db.execute_query("UPDATE books SET status='Borrowed' WHERE book_id=%s", (book_id,))
        
        query = """
            UPDATE borrowed_books
            SET return_date=%s, status=%s, fine_amount=%s
            WHERE borrow_id=%s
        """
        
        try:
            if self.db.execute_query(query, (return_date, status, fine, borrow_id)):
                QMessageBox.information(self, "Success", "Transaction updated successfully!")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Database Error", "Failed to update transaction")
        except Exception as e:
            print(f"[ERROR] Update transaction failed: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")

class ConfirmDeleteBorrowDialog(QDialog):
    # Confirm deletion of a transaction
    
    def __init__(self, parent=None, book_id="", member_id=""):
        # Init delete confirmation
        super().__init__(parent)
        self.book_id = book_id
        self.member_id = member_id
        
        self.setWindowTitle("Curatel - Circulation Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(AppConfig.DIALOG_WIDTH, 500)
        self.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_dialog']};")
        
        screen_center = QApplication.primaryScreen().geometry().center()
        self.move(screen_center - self.rect().center())
        
        self._setup_ui()
    
    def _setup_ui(self):
        # Build confirmation prompt with Yes/No
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)
        
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(AppConfig.STYLES['dialog_header'])
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        header_label = QLabel("CONFIRM DELETE TRANSACTION")
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
        
        message = QLabel(
            f"Are you sure you want to permanently delete:\n"
            f"Book: {self.book_id} | Member: {self.member_id}?"
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
        yes_btn.setFixedSize(AppConfig.BUTTON_WIDTH_EXTRA_WIDE, AppConfig.BUTTON_HEIGHT_LARGE)
        yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_btn.setStyleSheet(AppConfig.get_red_button_style())
        yes_btn.clicked.connect(self.accept)
        
        no_btn = QPushButton("No")
        no_btn.setFixedSize(AppConfig.BUTTON_WIDTH_EXTRA_WIDE, AppConfig.BUTTON_HEIGHT_LARGE)
        no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        no_btn.setStyleSheet(AppConfig.get_green_button_style())
        no_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(yes_btn)
        buttons_layout.addWidget(no_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)