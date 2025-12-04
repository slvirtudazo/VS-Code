# ui/circulation_dialogs.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy, 
                              QLineEdit, QPushButton, QComboBox, QMessageBox, QApplication, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta

class AddBorrowDialog(QDialog):
    """Dialog for adding new borrowing transactions - matches AddMemberDialog design"""
    
    def __init__(self, parent=None, db=None, callback=None):
        super().__init__(parent)
        self.db = db
        self.callback = callback

        # Same window setup as other add dialogs
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 720)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())

        self.setWindowTitle("Curatel - Circulation Management")
        self.setup_ui()
    
    def create_header(self, text):
        """Create header matching other dialog styles"""
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
        """Setup UI matching AddMemberDialog"""
        # Set dialog background to match other dialogs
        self.setStyleSheet("background-color: #8B7E66;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        layout.addSpacing(-30)
        header = self.create_header("ADD TRANSACTION")
        layout.addWidget(header)
        layout.addSpacing(30)

        # Main frame container - same size and style
        form_container = QWidget()
        form_container.setFixedSize(600, 420)
        form_container.setStyleSheet("""
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 20, 30, 50)
        form_layout.setSpacing(0)

        # Styles matching other dialogs
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

        date_style = """
            QDateEdit {
                font-family: Montserrat;
                font-size: 13px;
                border: 1px solid #8B7E66;
                border-radius: 10px;
                padding: 8px;
                background-color: white;
                color: black;
            }
            QDateEdit:focus {
                border: 2px solid #6B5E46;
            }
            QDateEdit::drop-down {
                border: none;
                padding-right: 10px;
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
            form_layout.addSpacing(-20)
            form_layout.addWidget(widget)

        # BOOK ID
        self.book_id_input = QLineEdit()
        self.book_id_input.setPlaceholderText("e.g., BK-001")
        self.book_id_input.setFixedSize(FIELD_W, FIELD_H)
        self.book_id_input.setStyleSheet(input_style)
        add_field("Book ID", self.book_id_input)

        # MEMBER ID
        self.member_id_input = QLineEdit()
        self.member_id_input.setPlaceholderText("e.g., MEM-001")
        self.member_id_input.setFixedSize(FIELD_W, FIELD_H)
        self.member_id_input.setStyleSheet(input_style)
        add_field("Member ID", self.member_id_input)

        # BORROW DATE
        self.borrow_date_input = QDateEdit()
        self.borrow_date_input.setCalendarPopup(True)

        self.borrow_date_input.setSpecialValueText(" ")          
        self.borrow_date_input.setDate(QDate())                  
        self.borrow_date_input.setMinimumDate(QDate(1752, 9, 14))  
        self.borrow_date_input.setMaximumDate(QDate(7999, 12, 31))

        self.borrow_date_input.setFixedSize(FIELD_W, FIELD_H)
        self.borrow_date_input.setStyleSheet(date_style)
        self.borrow_date_input.setDisplayFormat("yyyy-MM-dd")
        add_field("Borrow Date", self.borrow_date_input)

        # DUE DATE - Starts completely blank   🔹 CHANGED
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)

        self.due_date_input.setSpecialValueText(" ")      # stays
        self.due_date_input.setDate(QDate())              # 🔹 CHANGED (clear date)

        # REMOVE minimum/maximum limits completely  🔹 REMOVED
        # self.due_date_input.setMinimumDate(QDate(2000, 1, 1))

        self.due_date_input.setFixedSize(FIELD_W, FIELD_H)
        self.due_date_input.setStyleSheet(date_style)
        self.due_date_input.setDisplayFormat("yyyy-MM-dd")
        add_field("Due Date", self.due_date_input)


        # Center the form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)

        layout.addSpacing(30)

        # Buttons - matching other dialog button style
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
        save_btn.clicked.connect(self.save_borrow)
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

    def save_borrow(self):
        """Save new borrowing transaction to database (clean, DB-managed timestamps)."""
        book_id = self.book_id_input.text().strip()
        member_id = self.member_id_input.text().strip()

        # Get the borrow date
        borrow_date_qdate = self.borrow_date_input.date()
        
        # Get the due date - check if it's still at the special blank value
        due_date_qdate = self.due_date_input.date()
        
        # Check if due date is still blank (at minimum date)
        if due_date_qdate == QDate(2000, 1, 1):
            QMessageBox.warning(self, "Error", "Please set a due date")
            return

        # Create full datetime strings (YYYY-MM-DD HH:MM:SS)
        now = datetime.now()
        now_time_str = now.strftime("%H:%M:%S")
        
        borrow_date = f"{borrow_date_qdate.toString('yyyy-MM-dd')} {now_time_str}"
        due_date = f"{due_date_qdate.toString('yyyy-MM-dd')} {now_time_str}"

        # Validation
        if not all([book_id, member_id]):
            QMessageBox.warning(self, "Error", "Book ID and Member ID are required")
            return

        # Check if book exists and is available
        book_query = "SELECT book_id, status, title FROM books WHERE book_id = %s"
        book = self.db.fetch_one(book_query, (book_id,))
        if not book:
            QMessageBox.warning(self, "Error", f"Book ID '{book_id}' does not exist")
            return
        if book['status'] != 'Available':
            QMessageBox.warning(self, "Error", f"Book '{book['title']}' is not available for borrowing")
            return

        # Check if member exists and is active
        member_query = "SELECT member_id, status, full_name FROM members WHERE member_id = %s"
        member = self.db.fetch_one(member_query, (member_id,))
        if not member:
            QMessageBox.warning(self, "Error", f"Member ID '{member_id}' does not exist")
            return
        if member['status'] != 'Active':
            QMessageBox.warning(self, "Error", f"Member '{member['full_name']}' is not active")
            return

        # Insert into database — do NOT set updated_at manually; DB will handle it.
        query = """
        INSERT INTO borrowed_books (book_id, member_id, borrow_date, due_date, return_date, status, fine_amount)
        VALUES (%s, %s, %s, %s, NULL, 'Borrowed', 0.00)
        """

        if self.db.execute_query(query, (book_id, member_id, borrow_date, due_date)):
            # Update book status to Borrowed — let DB update timestamps automatically
            update_book_query = "UPDATE books SET status = 'Borrowed' WHERE book_id = %s"
            self.db.execute_query(update_book_query, (book_id,))

            QMessageBox.information(
                self,
                "Success",
                f"Transaction added successfully!\n\n"
                f"Book: {book['title']}\n"
                f"Member: {member['full_name']}\n"
                f"Due Date: {due_date_qdate.toString('yyyy-MM-dd')}"
            )
            if self.callback:
                self.callback()
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to add transaction to database")


class ViewBorrowDialog(QDialog):
    """Dialog for viewing borrowing transaction details - matches ViewMemberDialog design"""
    
    def __init__(self, parent=None, borrow_data=None):
        super().__init__(parent)
        self.borrow_data = borrow_data
        
        # Same window setup as ViewMemberDialog
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 750)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())
        
        self.setWindowTitle("Curatel - Circulation Management")
        self.setup_ui()
    
    def create_header(self, text):
        """Create header matching other view dialog styles"""
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
        """Setup view transaction UI matching ViewMemberDialog"""
        # Set dialog background
        self.setStyleSheet("background-color: #8B7E66;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        header = self.create_header("TRANSACTION INFORMATION")
        layout.addWidget(header)
        layout.addSpacing(40)

        # Main frame container
        info_container = QWidget()
        info_container.setFixedSize(600, 500)
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

        # Display transaction fields
        add_field("Book ID:", self.borrow_data.get('book_id', ''))
        add_field("Book Title:", self.borrow_data.get('book_title', 'Unknown'))
        add_field("Member ID:", self.borrow_data.get('member_id', ''))
        add_field("Member Name:", self.borrow_data.get('member_name', 'Unknown'))
        
        # Format dates
        borrow_date = str(self.borrow_data.get('borrow_date', ''))
        due_date = str(self.borrow_data.get('due_date', ''))
        return_date = str(self.borrow_data.get('return_date', '')) if self.borrow_data.get('return_date') else 'Not Returned'
        
        add_field("Borrow Date:", borrow_date)
        add_field("Due Date:", due_date)
        add_field("Return Date:", return_date)
        add_field("Status:", self.borrow_data.get('status', ''))
        
        # Format fine amount
        fine = f"₱{float(self.borrow_data.get('fine_amount', 0)):.2f}"
        add_field("Fine Amount:", fine)

        # Center the container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(info_container)
        container_layout.addStretch()
        layout.addLayout(container_layout)

        layout.addSpacing(40)

        # Close button matching other view dialogs
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


class UpdateBorrowDialog(QDialog):
    """Dialog for updating borrowing transaction - matches UpdateMemberDialog design"""

    def __init__(self, parent=None, db=None, borrow_data=None, callback=None):
        super().__init__(parent)
        self.db = db
        self.borrow_data = borrow_data
        self.callback = callback

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(750, 650)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())
        self.setWindowTitle("Curatel - Circulation Management")

        self.setup_ui()

    def create_header(self, text):
        """Create header matching other update dialog styles"""
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
        """Setup update transaction UI matching UpdateMemberDialog"""
        # Set dialog background
        self.setStyleSheet("background-color: #8B7E66;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 30)
        layout.setSpacing(0)

        # Header
        layout.addSpacing(-35)
        header = self.create_header("UPDATE TRANSACTION")
        layout.addWidget(header)
        layout.addSpacing(30)

        # Frame container
        form_container = QWidget()
        form_container.setFixedSize(600, 350)
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

        date_style = """
            QDateEdit {
                font-family: Montserrat;
                font-size: 13px;
                border: 1px solid #8B7E66;
                border-radius: 10px;
                padding: 8px;
                background-color: white;
                color: black;
            }
            QDateEdit:focus {
                border: 2px solid #6B5E46;
            }
            QDateEdit::drop-down {
                border: none;
                padding-right: 10px;
            }
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

        # RETURN DATE
        self.return_date_input = QLineEdit()
        self.return_date_input.setPlaceholderText("YY-MM-DD")
        if self.borrow_data.get('return_date'):
            return_date_str = str(self.borrow_data.get('return_date'))
            self.return_date_input.setText(return_date_str.split()[0])
        self.return_date_input.setFixedSize(FIELD_W, FIELD_H)
        self.return_date_input.setStyleSheet(input_style)
        add_field("Return Date", self.return_date_input)

        # STATUS
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Borrowed", "Returned", "Overdue"])
        current_status = self.borrow_data.get('status', 'Borrowed')
        self.status_combo.setCurrentText(current_status)
        self.status_combo.setFixedSize(FIELD_W, FIELD_H)
        self.status_combo.setStyleSheet(combo_style)
        add_field("Status", self.status_combo)

        # FINE AMOUNT - Starts blank with "0.00" placeholder
        self.fine_input = QLineEdit()
        # Only show existing fine if it's greater than 0
        current_fine = float(self.borrow_data.get('fine_amount', 0))
        if current_fine > 0:
            self.fine_input.setText(f"{current_fine:.2f}")
        else:
            # Leave blank with placeholder
            self.fine_input.setPlaceholderText("0.00")
        self.fine_input.setFixedSize(FIELD_W, FIELD_H)
        self.fine_input.setStyleSheet(input_style)
        add_field("Fine Amount (₱)", self.fine_input)

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
        update_btn.clicked.connect(self.update_borrow)
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

    def update_borrow(self):
        """Update borrowing transaction in database (sets return_date, status, fine; DB handles timestamps)."""
        
        # Get the return date from QLineEdit
        return_date_text = self.return_date_input.text().strip()
        
        if return_date_text:
            # Try to parse the date
            try:
                return_date_dt = datetime.strptime(return_date_text, "%Y-%m-%d")
                now = datetime.now()
                return_date = f"{return_date_dt.strftime('%Y-%m-%d')} {now.strftime('%H:%M:%S')}"
            except ValueError:
                QMessageBox.warning(self, "Error", "Return date must be in YYYY-MM-DD format")
                return
        else:
            return_date = None  # Keep NULL if blank

        status = self.status_combo.currentText()
        fine_text = self.fine_input.text().strip()

        # Validate fine amount
        if not fine_text:
            fine = 0.00
        else:
            try:
                fine = float(fine_text)
                if fine < 0:
                    QMessageBox.warning(self, "Error", "Fine amount cannot be negative")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Please enter a valid fine amount")
                return

        book_id = self.borrow_data.get('book_id')
        current_status = self.borrow_data.get('status')

        # Update book status if needed
        try:
            if status == 'Returned' and current_status != 'Returned':
                self.db.execute_query("UPDATE books SET status = 'Available' WHERE book_id = %s", (book_id,))
            elif status != 'Returned' and current_status == 'Returned':
                self.db.execute_query("UPDATE books SET status = 'Borrowed' WHERE book_id = %s", (book_id,))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update book status:\n{e}")
            return

        # Update borrowed_books
        try:
            query = """
                UPDATE borrowed_books
                SET return_date = %s, status = %s, fine_amount = %s
                WHERE borrow_id = %s
            """
            success = self.db.execute_query(query, (return_date, status, fine, self.borrow_data['borrow_id']))
            if success:
                QMessageBox.information(self, "Success", "Transaction updated successfully!")
                if self.callback:
                    self.callback()
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update transaction")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error:\n{e}")

class ConfirmDeleteBorrowDialog(QDialog):
    """Confirmation dialog for deleting a borrowing transaction - matches ConfirmDeleteMemberDialog design"""

    def __init__(self, parent=None, book_id="", member_id=""):
        super().__init__(parent)
        self.book_id = book_id
        self.member_id = member_id

        # Same window setup as other confirm delete dialogs
        self.setWindowTitle("Curatel - Circulation Management")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(800, 500)
        self.move(QApplication.primaryScreen().geometry().center() - self.rect().center())

        # Set main background color
        self.setStyleSheet("background-color: #8B7E66;")

        self.setup_ui()

    def setup_ui(self):
        """Setup UI matching other confirm delete dialogs"""
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

        header_label = QLabel("CONFIRM DELETE TRANSACTION")
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

        message = QLabel(f"Are you sure you want to permanently delete:\nBook: {self.book_id} | Member: {self.member_id}?")
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

        # Buttons matching other confirm delete dialogs
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