# ui/login_screen.py

import os
import re
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QRect # QRect for manual geometry/positioning
from PyQt6.QtGui import QFont, QColor, QIcon, QCursor # QCursor for hand cursor

class ResetPasswordDialog(QDialog):
    # Reset Password Dialog (unchanged setup)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Curatel - Password Reset")
        self.setFixedSize(500, 350)
        self.setStyleSheet("background-color: #3C2A21;")
        self.setup_ui()
        self.center_window()

    def setup_ui(self):
        # Configures the dialog layout and widgets
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 40)
    
        subtitle = QLabel(
            "Enter your registered email address to\n"
            "receive password reset instructions"
        )
        subtitle.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        subtitle.setStyleSheet("color: #FFFFFF;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(50)

        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Montserrat", 12, QFont.Weight.Normal))
        email_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(email_label)
        layout.addSpacing(5)

        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(50)
        self.email_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #FFFFFF;
                border: none;
                border-radius: 20px;
                padding: 12px 20px;
                font-family: Montserrat;
                font-size: 12px;
                color: #000000;
            }
            QLineEdit:focus { background-color: #FFFFFF; }
            QLineEdit::placeholder { color: gray; }
            """
        )
        layout.addWidget(self.email_input)
        layout.addSpacing(50)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        send_btn = QPushButton("Send")
        send_btn.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        send_btn.setFixedSize(135, 45)
        send_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #8BAE66;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #A3B087; }
            """
        )
        send_btn.clicked.connect(self.send_reset)
        btn_layout.addWidget(send_btn)

        btn_layout.addSpacing(20)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        cancel_btn.setFixedSize(135, 45)
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #CD5656; }
            """
        )
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch() 

    def send_reset(self):
        # Validates email and simulates sending reset instructions.
        email = self.email_input.text().strip()
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email address.")
            return

        if not re.match(email_pattern, email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address.")
            return

        QMessageBox.information(self, "Success", "Password reset instructions sent to your email.")
        print(f"[INFO] Password reset sent to: {email}")
        self.close()

    def center_window(self):
        # Centers the dialog on the screen.
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

class LoginScreen(QMainWindow):
    """Main login window with background image"""

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.closing_without_prompt = False
        self.password_visible = False
        
        # Load icon assets from the base directory.
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_open = QIcon(os.path.join(self.base_dir, "assets", "eye_open.png"))
        self.icon_closed = QIcon(os.path.join(self.base_dir, "assets", "eye_closed.png"))

        try:
            self.setup_ui()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] LoginScreen setup failed: {e}")
            raise

    def setup_ui(self):
        # Sets up the main window structure and background.
        self.setWindowTitle("Curatel - Library Management System")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Background Setup
        bg_path = os.path.join(self.base_dir, "assets", "curatel_bg.png")

        if os.path.exists(bg_path):
            bg_path = bg_path.replace("\\", "/")
            central_widget.setStyleSheet(
                f"""
                QWidget {{
                    background-image: url('{bg_path}');
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
                """
            )
        else:
            central_widget.setStyleSheet("background-color: #8B7E66;")

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 80, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.create_login_form(main_layout)

    def create_login_form(self, parent_layout):
        # Creates the fixed-size central login form container.
        form_container = QWidget()
        form_container.setFixedSize(500, 550)
        form_container.setStyleSheet(
            """
            background-color: transparent;
            border: 1px solid #FFFFFF;
            border-radius: 50px;
            """
        )

        # Applies drop shadow effect to the form container.
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(100)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(30, 30)
        form_container.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(50, 30, 50, 50)
        form_layout.addSpacing(20)

        # Welcome message label setup.
        welcome_msg = QLabel("Welcome, Sam!\nSign in to manage book collections")
        welcome_msg.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        welcome_msg.setStyleSheet("color: white; background: transparent; border : none;")
        welcome_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_msg.setWordWrap(True)
        form_layout.addWidget(welcome_msg)
        form_layout.addSpacing(30)

        # Username label setup.
        username_label = QLabel("Username")
        username_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        username_label.setStyleSheet("color: white; background: transparent; border: none;")
        form_layout.addWidget(username_label)

        # Username input field setup.
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid white;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 12px;
                color: black;
                background-color: black;
                background: white;
            }
            QLineEdit:focus { background-color: white; color: black;}
            QLineEdit::placeholder { color: gray; }
            """
        )

        form_layout.addWidget(username_label)
        form_layout.addSpacing(-20)
        form_layout.addWidget(self.username_input)

        # Password label setup.
        password_label = QLabel("Password")
        password_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        password_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        form_layout.addWidget(password_label)
        form_layout.addSpacing(-10)

        # Container for password input to manage overlay.
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent; border: none;")

        # Layout to ensure QLineEdit fills the container.
        container_layout = QVBoxLayout(password_container) 
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Password input setup (child of password_container).
        self.password_input = QLineEdit(password_container)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid white;
                border-radius: 20px;
                padding: 12px 20px;
                /* Extra padding for the overlay icon */
                padding-right: 50px; 
                font-size: 12px;
                color: black;
                background-color: white;
                background: white;
            }
            QLineEdit:focus { background-color: white; color: black; }
            QLineEdit::placeholder { color: gray; }
            """
        )
        self.password_input.returnPressed.connect(self.handle_login)

        # Add the QLineEdit to the container's layout.
        container_layout.addWidget(self.password_input)

        # Eye icon button setup (OVERLAY - child of QLineEdit).
        self.toggle_password_btn = QPushButton(self.password_input)
        self.toggle_password_btn.setFixedSize(20, 25)
        self.toggle_password_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Set the initial 'closed eye' icon.
        self.toggle_password_btn.setIcon(self.icon_closed)
        self.toggle_password_btn.setIconSize(self.toggle_password_btn.size())

        self.toggle_password_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
            """
        )
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

        # Place the password container into the main form layout.
        form_layout.addSpacing(-10)
        form_layout.addWidget(password_container)

        # Set the initial manual position of the eye icon.
        self.position_eye_icon() 
        
        form_layout.addSpacing(50)

        # Sign Up button setup.
        self.signin_btn = QPushButton("Sign Up")
        self.signin_btn.setFont(QFont("Montserrat", 13, QFont.Weight.Bold))
        self.signin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.signin_btn.setFixedHeight(50)
        self.signin_btn.setStyleSheet(
            """
            QPushButton {
                color: white;
                border: none;
                border-radius: 20px;
                background: #8B7E66;
            }
            QPushButton:hover { background-color: #7A6D55; }
            """
        )
        self.signin_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.signin_btn)

        form_layout.addSpacing(-15)

        # Forgot Password button setup
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        forgot_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        forgot_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #FFFFFF;
                text-decoration: underline;
            }
            QPushButton:hover { color: black; }
            """
        )
        forgot_btn.clicked.connect(self.show_reset_password)
        form_layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(form_container, alignment=Qt.AlignmentFlag.AlignCenter)

    def position_eye_icon(self):
        """Manually sets the X/Y position of the eye icon button inside the QLineEdit."""
        
        # Exit if widgets aren't initialized yet.
        if not hasattr(self, 'password_input') or not hasattr(self, 'toggle_password_btn'):
            return

        input_height = self.password_input.height()
        button_size = 25  
        right_margin = 15

        # Calculate X position (distance from left edge of QLineEdit).
        x = self.password_input.width() - button_size - right_margin

        # Calculate Y position (vertically centered, ensuring integer type).
        y = int((input_height - button_size) / 2) 

        # Apply manual geometry using QRect.
        self.toggle_password_btn.setGeometry(QRect(x, y, button_size, button_size))
        
        # Bring the button to the front (on top of text).
        self.toggle_password_btn.raise_()
        
    def resizeEvent(self, event):
        """Reposition the icon whenever the parent window is resized."""
        super().resizeEvent(event)
        self.position_eye_icon()

    def toggle_password_visibility(self):
        """Toggles the password echo mode and updates the eye icon."""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setIcon(self.icon_closed)
            self.password_visible = False
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setIcon(self.icon_open)
            self.password_visible = True

    def handle_login(self):
        """Handles the login process: validates input and checks credentials."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        if username == "slav" and password == "554893":
            QMessageBox.information(self, "Success", f"Welcome, {username}!")
            self.show_dashboard()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password.")

    def show_reset_password(self):
        """Opens the password reset dialog."""
        ResetPasswordDialog(self).exec()

    def show_dashboard(self):
        """Loads and displays the dashboard, then closes the login screen."""
        try:
            from curatel_lms.ui.dashboard import Dashboard 
            self.dashboard = Dashboard(self.db)
            self.dashboard.show()
            self.closing_without_prompt = True
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to open dashboard")
            print(f"[ERROR] Failed to open dashboard: {e}")

    def show_fullscreen(self):
        """Sets the main window to maximized state."""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()

    def closeEvent(self, event):
        """Handles the window close event, asking for confirmation if not opening dashboard."""
        if self.closing_without_prompt:
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()