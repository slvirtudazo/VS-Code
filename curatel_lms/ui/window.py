# curatel_lms/ui/window.py

# Central window with sidebar navigation for all management sections

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QStackedWidget, QMessageBox, QFrame, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from curatel_lms.config import AppConfig

class MainWindow(QMainWindow):
    # Single-window application with sidebar navigation between all sections
    
    def __init__(self, db=None):
        # Initialize with database connection and setup UI
        super().__init__()
        self.db = db
        self.closing_without_prompt = False
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        
        try:
            self._setup_ui()
            self._show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup main window: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to initialize application:\n{str(e)}")
    
    def _setup_ui(self):
        # Build main layout with sidebar and content area
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            central_widget.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
            
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create sidebar navigation
            sidebar = self._create_sidebar()
            main_layout.addWidget(sidebar)
            
            # Create content area with stacked screens
            self.content_stack = QStackedWidget()
            self.content_stack.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
            main_layout.addWidget(self.content_stack)
            
            # Load all management screens as widgets
            self._load_management_screens()
        except Exception as e:
            print(f"[ERROR] Setup UI failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_sidebar(self):
        # Build left sidebar with navigation buttons and logout
        try:
            sidebar = QWidget()
            sidebar.setFixedWidth(280)
            sidebar.setStyleSheet(f"""
                QWidget {{
                    background-color: {AppConfig.COLORS['primary_light']};
                }}
            """)
            
            layout = QVBoxLayout(sidebar)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Header with logo - moved up with less spacing
            header = self._create_sidebar_header()
            layout.addWidget(header)
            
            # Divider line
            layout.addWidget(self._create_divider())
            layout.addSpacing(20)  # Reduced from 30
            
            # Navigation buttons
            nav_configs = [
                ("Catalog Management", "catalog_logo.png", 0),
                ("Patron Management", "patron_logo.png", 1),
                ("Circulation Management", "circulation_logo.png", 2),
                ("Library Reports", "reports_logo.png", 3)
            ]
            
            self.nav_buttons = []
            for title, icon_file, index in nav_configs:
                icon_path = os.path.join(self.base_dir, "assets", icon_file)
                btn = self._create_nav_button(title, icon_path, index)
                layout.addWidget(btn)
                layout.addSpacing(5)  # Reduced spacing between nav buttons
                self.nav_buttons.append(btn)
            
            # Push logout to bottom to align with dialog buttons
            layout.addStretch()
            
            # Logout button at bottom with proper margin
            logout_btn = self._create_logout_button()
            layout.addWidget(logout_btn)
            layout.addSpacing(20)  # Bottom margin to align with dialog buttons
            
            # Highlight first button (Catalog Management)
            self._highlight_button(0)
            
            return sidebar
        except Exception as e:
            print(f"[ERROR] Create sidebar failed: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _create_sidebar_header(self):
        # Create header with Curatel text instead of logo image
        try:
            header = QWidget()
            header.setFixedHeight(100)
            header.setStyleSheet("background-color: transparent;")
            
            layout = QVBoxLayout(header)
            layout.setContentsMargins(20, 10, 20, 10)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setSpacing(0)  # Remove spacing between labels
            
            # Main title "Curatel" with Montserrat Bold
            title = QLabel("Curatel")
            title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
            title.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']};")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Subtitle "Library Management" with Montserrat Normal
            subtitle = QLabel("Library Management")
            subtitle.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))
            subtitle.setStyleSheet(f"color: {AppConfig.COLORS['text_gray']};")
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)
            
            return header
        except Exception as e:
            print(f"[ERROR] Create sidebar header failed: {e}")
            # Return simple fallback header
            header = QWidget()
            header.setFixedHeight(100)
            return header
    
    def _create_divider(self):
        # Create horizontal separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet(
            f"color: {AppConfig.COLORS['border_dark']}; "
            f"background-color: {AppConfig.COLORS['border_color']};"
        )
        line.setFixedHeight(2)
        return line
    
    def _create_nav_button(self, title, icon_path, index):
        # Create styled navigation button with icon and text using Montserrat Normal
        try:
            btn = QPushButton()
            btn.setFixedHeight(70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-left: 4px solid transparent;
                    text-align: left;
                    padding-left: 20px;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                    border-left: 4px solid {AppConfig.COLORS['button_primary']};
                }}
            """)
            
            # Button layout with icon and text
            layout = QHBoxLayout(btn)
            layout.setContentsMargins(15, 0, 15, 0)
            layout.setSpacing(15)
            
            # Icon
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(
                    35, 35,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                icon_label.setPixmap(pixmap)
                icon_label.setStyleSheet("background: transparent;")
                layout.addWidget(icon_label)
            
            # Text with Montserrat Normal font
            text_label = QLabel(title)
            text_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))  # Changed to Normal weight
            text_label.setStyleSheet("color: black; background: transparent;")
            layout.addWidget(text_label)
            layout.addStretch()
            
            # Connect to navigation handler
            btn.clicked.connect(lambda: self._switch_screen(index))
            
            return btn
        except Exception as e:
            print(f"[ERROR] Create nav button failed for {title}: {e}")
            # Return simple fallback button
            btn = QPushButton(title)
            btn.setFixedHeight(70)
            btn.clicked.connect(lambda: self._switch_screen(index))
            return btn
    
    def _create_logout_button(self):
        # Create logout button with Montserrat Normal font
        try:
            btn = QPushButton()
            btn.setFixedHeight(70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    border-left: 4px solid transparent;
                    text-align: left;
                    padding-left: 20px;
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: rgba(0, 0, 0, 0.1);
                    border-left: 4px solid {AppConfig.COLORS['button_red']};
                }}
            """)
            
            # Button layout with icon and text
            layout = QHBoxLayout(btn)
            layout.setContentsMargins(15, 0, 15, 0)
            layout.setSpacing(15)
            layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            
            # Icon
            icon_path = os.path.join(self.base_dir, "assets", "logout_logo.png")
            if os.path.exists(icon_path):
                icon_label = QLabel()
                pixmap = QPixmap(icon_path).scaled(
                    35, 35,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                icon_label.setPixmap(pixmap)
                icon_label.setStyleSheet("background: transparent;")
                layout.addWidget(icon_label)
            
            # Text with Montserrat Normal font
            text_label = QLabel("Logout")
            text_label.setFont(QFont("Montserrat", 11, QFont.Weight.Normal))  # Changed to Normal weight
            text_label.setStyleSheet("color: black; background: transparent;")
            layout.addWidget(text_label)
            layout.addStretch()
            
            btn.clicked.connect(self._logout)
            return btn
        except Exception as e:
            print(f"[ERROR] Create logout button failed: {e}")
            # Return simple fallback button
            btn = QPushButton("Logout")
            btn.setFixedHeight(70)
            btn.clicked.connect(self._logout)
            return btn
    
    def _load_management_screens(self):
        # Import and add all management screens to stack as regular widgets (not windows)
        try:
            from curatel_lms.ui.catalog_management import CatalogManagement
            from curatel_lms.ui.patron_management import PatronManagement
            from curatel_lms.ui.circulation_management import CirculationManagement
            from curatel_lms.ui.library_reports import ReportsAnalytics

            # Create screen instances — now all are QWidgets
            self.catalog_screen = CatalogManagement(self.db)
            self.patron_screen = PatronManagement(self.db)
            self.circulation_screen = CirculationManagement(self.db)
            self.reports_screen = ReportsAnalytics(self.db)

            # Add directly to stack — no centralWidget() needed
            self.content_stack.addWidget(self.catalog_screen)
            self.content_stack.addWidget(self.patron_screen)
            self.content_stack.addWidget(self.circulation_screen)
            self.content_stack.addWidget(self.reports_screen)

            # Show catalog management first
            self.content_stack.setCurrentIndex(0)
            print("[INFO] All management screens loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load management screens: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Initialization Error",
                f"Failed to load application screens:\n{str(e)}"
            )
    
    def _switch_screen(self, index):
        # Switch to selected screen and update button highlights
        try:
            self.content_stack.setCurrentIndex(index)
            self._highlight_button(index)
            
            # Force update to ensure screen renders properly
            self.content_stack.currentWidget().update()
            
            print(f"[INFO] Switched to screen {index}")
        except Exception as e:
            print(f"[ERROR] Failed to switch screen: {e}")
            QMessageBox.warning(self, "Error", "Failed to switch to selected screen")
    
    def _highlight_button(self, index):
        # Highlight active navigation button
        try:
            for i, btn in enumerate(self.nav_buttons):
                if i == index:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: rgba(0, 0, 0, 0.2);
                            border: none;
                            border-left: 4px solid {AppConfig.COLORS['bg_white']};
                            text-align: left;
                            padding-left: 20px;
                            color: white;
                        }}
                        QPushButton:hover {{
                            background-color: rgba(0, 0, 0, 0.2);
                            border-left: 4px solid {AppConfig.COLORS['bg_white']};
                        }}
                    """)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-left: 4px solid transparent;
                            text-align: left;
                            padding-left: 20px;
                            color: white;
                        }}
                        QPushButton:hover {{
                            background-color: rgba(0, 0, 0, 0.1);
                            border-left: 4px solid {AppConfig.COLORS['button_primary']};
                        }}
                    """)
        except Exception as e:
            print(f"[ERROR] Failed to highlight button: {e}")
    
    def _logout(self):
        # Confirm and return to login screen
        try:
            reply = QMessageBox.question(
                self, "Logout", "Are you sure you want to logout?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                from curatel_lms.ui.login_screen import LoginScreen
                self.closing_without_prompt = True
                self.login_window = LoginScreen(self.db)
                self.login_window.show()
                self.close()
        except Exception as e:
            print(f"[ERROR] Logout failed: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", "Logout failed")
    
    def _show_fullscreen(self):
        # Maximize window on launch
        try:
            self.setWindowState(Qt.WindowState.WindowMaximized)
            self.showMaximized()
        except Exception as e:
            print(f"[ERROR] Failed to show fullscreen: {e}")
    
    def closeEvent(self, event):
        # Confirm exit unless skipping prompt
        try:
            if self.closing_without_prompt:
                event.accept()
                return
            
            reply = QMessageBox.question(
                self, "Exit", "Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        except Exception as e:
            print(f"[ERROR] Close event handling failed: {e}")
            event.accept()  # Allow closing even if error occurs