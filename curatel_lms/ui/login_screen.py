# ui/login_screen.py

import os
import re
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
    QGraphicsBlurEffect, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class ResetPasswordDialog(QDialog):
    """Reset Password Dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reset Password")
        self.setFixedSize(500, 350)
        self.setStyleSheet("background-color: #3C2A21;")
        self.setup_ui()
        self.center_window()

    def setup_ui(self):
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
                border-radius: 25px;
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
                background-color: #6B7366;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #5A6255; }
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
                background-color: #6E6060;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #664F4F; }
            """
        )
        cancel_btn.clicked.connect(self.close)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch() 

    def send_reset(self):
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

        try:
            self.setup_ui()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] LoginScreen setup failed: {e}")
            raise

    def setup_ui(self):
        self.setWindowTitle("Curatel - Library Management System")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(base_dir, "assets", "library_image.png")

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
        # Only main login frame remains
        form_container = QWidget()
        form_container.setFixedSize(500, 520)
        form_container.setStyleSheet(
            """
            background-color: transparent;
            border: 1px solid #FFFFFF;
            border-radius: 50px;
            """
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))  # soft black shadow
        shadow.setOffset(0, 5)
        form_container.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(50, 30, 50, 60)
        form_layout.addSpacing(20)

        # Welcome message
        welcome_msg = QLabel("Welcome, Sam!\nSign in to manage book collections")
        welcome_msg.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        welcome_msg.setStyleSheet("color: #FFFFFF; background: transparent; border : none;")
        welcome_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_msg.setWordWrap(True)
        form_layout.addWidget(welcome_msg)
        form_layout.addSpacing(30)

        # Username label
        username_label = QLabel("Username")
        username_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        username_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        form_layout.addWidget(username_label)

        # Username input - solid white rounded rectangle
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFixedHeight(50)
        self.username_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid white;
                border-radius: 25px;
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
        form_layout.addSpacing(-10)  # smaller space between label and input
        form_layout.addWidget(self.username_input)

        # Password label
        password_label = QLabel("Password")
        password_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        password_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        form_layout.addWidget(password_label)

        # Password input - solid white rounded rectangle
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(50)
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid white;
                border-radius: 25px;
                padding: 12px 20px;
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

        form_layout.addWidget(password_label)
        form_layout.addSpacing(-10)  # smaller space between label and input
        form_layout.addWidget(self.password_input)

        # Forgot Password button
        forgot_btn = QPushButton("Forgot Password?")
        forgot_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.setStyleSheet(
            """
            QPushButton {
                background: transparent;
                border: none;
                color: #FFFFFF;
                text-decoration: underline;
            }
            QPushButton:hover { color: #E0E0E0; }
            """
        )
        forgot_btn.clicked.connect(self.show_reset_password)
        form_layout.addWidget(forgot_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        form_layout.addSpacing(35)

        # Sign Up button - solid #BDA984
        self.signin_btn = QPushButton("Sign Up")
        self.signin_btn.setFont(QFont("Montserrat", 13, QFont.Weight.Bold))
        self.signin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.signin_btn.setFixedHeight(50)
        self.signin_btn.setStyleSheet(
            """
            QPushButton {
                color: white;
                border: none;
                border-radius: 25px;
                background: #8B7E66;
            }
            QPushButton:hover { background-color: #7A6D55; }
            """
        )
        self.signin_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.signin_btn)

        parent_layout.addWidget(form_container, alignment=Qt.AlignmentFlag.AlignCenter)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password.")
            return

        if username == "slvirtudazo" and password == "554893":
            QMessageBox.information(self, "Success", f"Welcome, {username}!")
            self.show_dashboard()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password.")

    def show_reset_password(self):
        ResetPasswordDialog(self).exec()

    def show_dashboard(self):
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
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()

    def closeEvent(self, event):
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