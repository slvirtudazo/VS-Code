# curatel_lms/ui/login_screen.py

"""
Login screen module.
Provides authentication interface with password reset functionality.
"""

import os
import re
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon, QCursor

class ResetPasswordDialog(QDialog):
    """Dialog for password reset functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Curatel - Password Reset")
        self.setFixedSize(500, 350)
        self.setStyleSheet("background-color: #3C2A21;")
        self.setup_ui()
        self._center_window()

    def setup_ui(self):
        """Configure dialog layout and widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 40)
    
        # Instructions label
        subtitle = QLabel(
            "Enter your registered email address to\n"
            "receive password reset instructions"
        )
        subtitle.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        subtitle.setStyleSheet("color: #FFFFFF;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        layout.addSpacing(50)

        # Email input section
        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Montserrat", 12, QFont.Weight.Normal))
        email_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(email_label)
        layout.addSpacing(5)

        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(50)
        self.email_input.setStyleSheet("""
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
        """)
        layout.addWidget(self.email_input)
        layout.addSpacing(50)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        send_btn = QPushButton("Send")
        send_btn.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        send_btn.setFixedSize(135, 45)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #8BAE66;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #A3B087; }
        """)
        send_btn.clicked.connect(self._send_reset)
        btn_layout.addWidget(send_btn)

        btn_layout.addSpacing(20)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        cancel_btn.setFixedSize(135, 45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #AF3E3E;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #CD5656; }
        """)
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        layout.addStretch()

    def _send_reset(self):
        """Validate email and simulate sending reset instructions."""
        email = self.email_input.text().strip()

        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email address.")
            return

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            QMessageBox.warning(self, "Error", "Please enter a valid email address.")
            return

        QMessageBox.information(self, "Success", "Password reset instructions sent to your email.")
        print(f"[INFO] Password reset sent to: {email}")
        self.close()

    def _center_window(self):
        """Center dialog on screen."""
        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

class LoginScreen(QMainWindow):
    """Main login window with authentication."""

    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.closing_without_prompt = False
        self.password_visible = False
        
        # Load icon assets
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_open = QIcon(os.path.join(self.base_dir, "assets", "eye_open.png"))
        self.icon_closed = QIcon(os.path.join(self.base_dir, "assets", "eye_closed.png"))

        self.setup_ui()
        self.show_fullscreen()

    def setup_ui(self):
        """Configure main window structure."""
        self.setWindowTitle("Curatel - Library Management System")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Set background image
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

        self._create_login_form(main_layout)

    def _create_login_form(self, parent_layout):
        """Create login form container with inputs and buttons."""
        form_container = QWidget()
        form_container.setFixedSize(500, 550)
        form_container.setStyleSheet("""
            background-color: transparent;
            border: 1px solid #FFFFFF;
            border-radius: 50px;
        """)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(100)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(30, 30)
        form_container.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(50, 30, 50, 50)
        form_layout.addSpacing(20)

        # Welcome message
        welcome_msg = QLabel("Welcome, Sam!\nSign in to manage book collections")
        welcome_msg.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        welcome_msg.setStyleSheet("color: white; background: transparent; border: none;")
        welcome_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_msg.setWordWrap(True)
        form_layout.addWidget(welcome_msg)
        form_layout.addSpacing(30)

        # Username input
        username_label = QLabel("Username")
        username_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        username_label.setStyleSheet("color: white; background: transparent; border: none;")
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid white;
                border-radius: 20px;
                padding: 12px 20px;
                font-size: 12px;
                color: black;
                background: white;
            }
            QLineEdit:focus { background-color: white; color: black; }
            QLineEdit::placeholder { color: gray; }
        """)
        form_layout.addSpacing(-20)
        form_layout.addWidget(self.username_input)

        # Password input
        password_label = QLabel("Password")
        password_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        password_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        form_layout.addWidget(password_label)
        form_layout.addSpacing(-10)

        # Password container for eye icon overlay
        password_container = QWidget()
        password_container.setStyleSheet("background: transparent; border: none;")
        container_layout = QVBoxLayout(password_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.password_input = QLineEdit(password_container)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid white;
                border-radius: 20px;
                padding: 12px 20px;
                padding-right: 50px;
                font-size: 12px;
                color: black;
                background: white;
            }
            QLineEdit:focus { background-color: white; color: black; }
            QLineEdit::placeholder { color: gray; }
        """)
        self.password_input.returnPressed.connect(self._handle_login)
        container_layout.addWidget(self.password_input)

        # Eye icon toggle button
        self.toggle_password_btn = QPushButton(self.password_input)
        self.toggle_password_btn.setFixedSize(20, 25)
        self.toggle_password_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_password_btn.setIcon(self.icon_closed)
        self.toggle_password_btn.setIconSize(self.toggle_password_btn.size())
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
        """)
        self.toggle_password_btn.clicked.connect(self._toggle_password_visibility)

        form_layout.addSpacing(-10)
        form_layout.addWidget(password_container)
        self._position_eye_icon()
        
        form_layout.addSpacing(50)

        # Sign In button
        self.signin_btn = QPushButton("Sign In")
        self.signin_btn.setFont(QFont("Montserrat", 13, QFont.Weight.Bold))
        self.signin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.signin_btn.setFixedHeight(50)
        self.signin_btn.setStyleSheet("""
            QPushButton {
                color: white;
                border: none;
                border-radius: 20px;
                background: #8B7E66;
            }
            QPushButton:hover { background-color: #7A6D55; }
        """)
        self.signin_btn.clicked.connect(self._handle_login)
        form_layout.addWidget(self.signin_btn)

        form_layout.addSpacing(-15)

        # Forgot Password button
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        forgot_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        forgot_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #FFFFFF;
                text-decoration: underline;
            }
            QPushButton:hover { color: black; }
        """)
        forgot_btn.clicked.connect(self._show_reset_password)
        form_layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        parent_layout.addWidget(form_container, alignment=Qt.AlignmentFlag.AlignCenter)

    def _position_eye_icon(self):
        """Position eye icon button inside password input field."""
        if not hasattr(self, 'password_input') or not hasattr(self, 'toggle_password_btn'):
            return

        input_height = self.password_input.height()
        button_size = 25
        right_margin = 15

        x = self.password_input.width() - button_size - right_margin
        y = int((input_height - button_size) / 2)

        self.toggle_password_btn.setGeometry(x, y, button_size, button_size)
        self.toggle_password_btn.raise_()
        
    def resizeEvent(self, event):
        """Reposition icon on window resize."""
        super().resizeEvent(event)
        self._position_eye_icon()

    def _toggle_password_visibility(self):
        """Toggle password visibility and update icon."""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setIcon(self.icon_closed)
            self.password_visible = False
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setIcon(self.icon_open)
            self.password_visible = True

    def _handle_login(self):
        """Validate credentials and authenticate user."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        # Authenticate (hardcoded for demo)
        if username == "slav" and password == "554893":
            QMessageBox.information(self, "Success", f"Welcome, {username}!")
            self._show_dashboard()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password.")

    def _show_reset_password(self):
        """Open password reset dialog."""
        ResetPasswordDialog(self).exec()

    def _show_dashboard(self):
        """Load and display dashboard."""
        try:
            from curatel_lms.ui.dashboard import Dashboard
            self.dashboard = Dashboard(self.db)
            self.dashboard.show()
            self.closing_without_prompt = True
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to open dashboard")
            print(f"[ERROR] Dashboard error: {e}")

    def show_fullscreen(self):
        """Set window to maximized state."""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()

    def closeEvent(self, event):
        """Handle window close with confirmation."""
        if self.closing_without_prompt:
            event.accept()
            return

        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        event.accept() if reply == QMessageBox.StandardButton.Yes else event.ignore()