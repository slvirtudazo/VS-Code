# curatel_lms/ui/dashboard.py

"""
Dashboard module.
Main navigation hub for library management system.
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

class Dashboard(QMainWindow):
    """Main dashboard with navigation to all modules."""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.closing_without_prompt = False
        self.setWindowTitle("Curatel - Dashboard")
        self.setup_ui()
        self.show_fullscreen()
    
    def setup_ui(self):
        """Configure dashboard layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #FFFFFF;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet("color: #6B5E46; background-color: #8B7E66;")
        line.setFixedHeight(2)
        main_layout.addSpacing(5)
        main_layout.addWidget(line)

        # Content area with navigation cards
        content_widget = self._create_content()
        main_layout.addWidget(content_widget)
    
    def _create_header(self):
        """Create header with title and logout button."""
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #FFFFFF;")
        header_widget.setFixedHeight(100)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(50, 20, 50, 20)
        
        # Title section
        title_layout = QVBoxLayout()
        title = QLabel("Curatel")
        title.setFont(QFont("Montserrat", 25, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; border: none;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Dashboard Panel")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333; border: none;")
        title_layout.addWidget(subtitle)
        
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        logout_btn.setFixedSize(140, 50)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover { background-color: #6B5E46; }
        """)
        logout_btn.clicked.connect(self._logout)
        header_layout.addWidget(logout_btn)
        
        return header_widget

    def _create_content(self):
        """Create content area with navigation cards."""
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #FFFFFF;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(60, 90, 60, 90)
        
        # Get asset paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        img_catalog = os.path.join(base_dir, "assets", "catalog_logo.png")
        img_circulation = os.path.join(base_dir, "assets", "circulation_logo.png")
        img_patron = os.path.join(base_dir, "assets", "patron_logo.png")
        img_reports = os.path.join(base_dir, "assets", "reports_logo.png")
        
        # First row of cards
        row1_layout = QHBoxLayout()
        row1_layout.setContentsMargins(0, 30, 0, 0)
        
        catalog_btn = self._create_menu_card("Catalog Management", "Inventory & Maintenance", img_catalog)
        catalog_btn.clicked.connect(self._open_catalog_management)
        row1_layout.addStretch()
        row1_layout.addWidget(catalog_btn)
        row1_layout.addSpacing(70)
        
        circulation_btn = self._create_menu_card("Circulation Management", "Transactions & Tracking", img_circulation)
        circulation_btn.clicked.connect(self._open_circulation_management)
        row1_layout.addWidget(circulation_btn)
        row1_layout.addStretch()

        content_layout.addLayout(row1_layout)
        
        # Second row of cards
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 70, 0, 0)
        
        patron_btn = self._create_menu_card("Patron Management", "Profiles & Status", img_patron)
        patron_btn.clicked.connect(self._open_patron_management)
        row2_layout.addStretch()
        row2_layout.addWidget(patron_btn)
        row2_layout.addSpacing(70)
        
        reports_btn = self._create_menu_card("Library Reports", "Activity Overview & Patterns", img_reports)
        reports_btn.clicked.connect(self._open_reports_analytics)
        row2_layout.addWidget(reports_btn)
        row2_layout.addStretch()
        
        content_layout.addLayout(row2_layout)
        content_layout.addStretch()
        
        return content_widget
    
    def _create_menu_card(self, title, subtitle, image_path=None):
        """
        Create navigation card button.
        Args:
            title: Card title text
            subtitle: Card subtitle text
            image_path: Path to icon image
        Returns: QPushButton configured as navigation card
        """
        btn = QPushButton()
        btn.setFixedSize(540, 200)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1.5px solid #8B7E66;
                border-radius: 20px;
                text-align: left;
                padding: 0px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: rgba(201, 184, 168, 0.3);
                border: 1.5px solid #6B5E46;
            }
        """)

        layout = QHBoxLayout(btn)
        layout.setContentsMargins(50, 0, 50, 0)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setStyleSheet("background-color: transparent;")
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Text section
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(15, 70, 15, 0)
        text_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #000000; background-color: transparent;")
        text_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Montserrat", 13))
        subtitle_label.setStyleSheet("color: #333333; background-color: transparent;")
        text_layout.addWidget(subtitle_label)

        text_layout.addStretch()
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        return btn
    
    def _open_catalog_management(self):
        """Open catalog management window."""
        try:
            from curatel_lms.ui.catalog_management import CatalogManagement
            self.catalog_window = CatalogManagement(self.db)
            self.catalog_window.show()
        except Exception as e:
            print(f"[ERROR] Catalog Management: {e}")
            QMessageBox.critical(self, "Error", "Failed to open Catalog Management")
    
    def _open_circulation_management(self):
        """Open circulation management window."""
        try:
            from curatel_lms.ui.circulation_management import CirculationManagement
            self.circulation_window = CirculationManagement(self.db)
            self.circulation_window.show()
        except Exception as e:
            print(f"[ERROR] Circulation Management: {e}")
            QMessageBox.critical(self, "Error", "Failed to open Circulation Management")
    
    def _open_patron_management(self):
        """Open patron management window."""
        try:
            from curatel_lms.ui.patron_management import PatronManagement
            self.patron_window = PatronManagement(self.db)
            self.patron_window.show()
        except Exception as e:
            print(f"[ERROR] Patron Management: {e}")
            QMessageBox.critical(self, "Error", "Failed to open Patron Management")
    
    def _open_reports_analytics(self):
        """Open reports and analytics window."""
        try:
            from curatel_lms.ui.library_reports import ReportsAnalytics
            self.reports_window = ReportsAnalytics(self.db)
            self.reports_window.show()
        except Exception as e:
            print(f"[ERROR] Library Reports: {e}")
            QMessageBox.critical(self, "Error", "Failed to open Library Reports")
    
    def _logout(self):
        """Handle logout with confirmation."""
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from curatel_lms.ui.login_screen import LoginScreen
                self.closing_without_prompt = True
                self.login_window = LoginScreen(self.db)
                self.login_window.show()
                self.close()
            except Exception as e:
                print(f"[ERROR] Logout failed: {e}")
                QMessageBox.critical(self, "Error", "Logout failed")
    
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