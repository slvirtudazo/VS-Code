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

from curatel_lms.config import AppConfig


class Dashboard(QMainWindow):
    """Main dashboard with navigation to all management modules."""
    
    # Navigation card configuration
    CARDS = [
        {
            'title': 'Catalog Management',
            'subtitle': 'Inventory & Maintenance',
            'image': 'catalog_logo.png',
            'handler': '_open_catalog_management'
        },
        {
            'title': 'Circulation Management',
            'subtitle': 'Transactions & Tracking',
            'image': 'circulation_logo.png',
            'handler': '_open_circulation_management'
        },
        {
            'title': 'Patron Management',
            'subtitle': 'Profiles & Status',
            'image': 'patron_logo.png',
            'handler': '_open_patron_management'
        },
        {
            'title': 'Library Reports',
            'subtitle': 'Activity Overview & Patterns',
            'image': 'reports_logo.png',
            'handler': '_open_reports_analytics'
        }
    ]
    
    def __init__(self, db=None):
        """
        Initialize dashboard.
        Args:
            db: Database connection object
        """
        super().__init__()
        self.db = db
        self.closing_without_prompt = False
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.setWindowTitle(AppConfig.WINDOW_TITLE)
        self._setup_ui()
        self._show_fullscreen()
    
    def _setup_ui(self):
        """Configure dashboard layout with header and navigation cards."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        main_layout.addWidget(self._create_header())
        
        # Divider line
        main_layout.addSpacing(5)
        main_layout.addWidget(self._create_divider())
        
        # Content area with navigation cards
        main_layout.addWidget(self._create_content())
    
    def _create_header(self):
        """
        Create header with title and logout button.
        Returns: QWidget containing header
        """
        header_widget = QWidget()
        header_widget.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
        header_widget.setFixedHeight(100)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(50, 20, 50, 20)
        
        # Title section
        title_layout = QVBoxLayout()
        title_layout.setSpacing(10)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Curatel")
        title.setFont(QFont("Montserrat", 25, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {AppConfig.COLORS['text_dark']}; border: none;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Dashboard Panel")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet(f"color: {AppConfig.COLORS['text_gray']}; border: none;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
        logout_btn.setFixedSize(140, 50)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppConfig.COLORS['primary_light']};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{ background-color: {AppConfig.COLORS['button_gray_hover']}; }}
        """)
        logout_btn.clicked.connect(self._logout)
        header_layout.addWidget(logout_btn)
        
        return header_widget

    def _create_divider(self):
        """
        Create horizontal divider line.
        Returns: QFrame configured as divider
        """
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet(
            f"color: {AppConfig.COLORS['border_dark']}; "
            f"background-color: {AppConfig.COLORS['border_color']};"
        )
        line.setFixedHeight(2)
        return line

    def _create_content(self):
        """
        Create content area with navigation cards.
        Returns: QWidget containing navigation cards
        """
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {AppConfig.COLORS['bg_white']};")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(60, 90, 60, 90)
        
        # Create two rows of navigation cards
        content_layout.addLayout(self._create_card_row(0, 2))
        content_layout.addSpacing(70)
        content_layout.addLayout(self._create_card_row(2, 4))
        content_layout.addStretch()
        
        return content_widget
    
    def _create_card_row(self, start_idx, end_idx):
        """
        Create row of navigation cards.
        Args:
            start_idx: Starting index in CARDS list
            end_idx: Ending index in CARDS list
        Returns: QHBoxLayout containing card buttons
        """
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 30, 0, 0)
        row_layout.addStretch()
        
        for i in range(start_idx, end_idx):
            if i > start_idx:
                row_layout.addSpacing(70)
            
            card_config = self.CARDS[i]
            image_path = os.path.join(self.base_dir, "assets", card_config['image'])
            card_btn = self._create_menu_card(
                card_config['title'],
                card_config['subtitle'],
                image_path
            )
            # Connect to handler method
            card_btn.clicked.connect(getattr(self, card_config['handler']))
            row_layout.addWidget(card_btn)
        
        row_layout.addStretch()
        return row_layout
    
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
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1.5px solid {AppConfig.COLORS['border_color']};
                border-radius: 20px;
                text-align: left;
                padding: 0px;
                color: {AppConfig.COLORS['text_dark']};
            }}
            QPushButton:hover {{
                background-color: rgba(201, 184, 168, 0.3);
                border: 1.5px solid {AppConfig.COLORS['border_dark']};
            }}
        """)

        layout = QHBoxLayout(btn)
        layout.setContentsMargins(50, 0, 50, 0)
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel()
        icon_label.setStyleSheet("background-color: transparent;")
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                80, 80, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Text section
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(15, 70, 15, 0)
        text_layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(
            f"color: {AppConfig.COLORS['text_dark']}; background-color: transparent;"
        )
        text_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Montserrat", 13))
        subtitle_label.setStyleSheet(
            f"color: {AppConfig.COLORS['text_gray']}; background-color: transparent;"
        )
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
    
    def _show_fullscreen(self):
        """Set window to maximized state."""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        """
        Handle window close with confirmation.
        Args:
            event: Close event
        """
        if self.closing_without_prompt:
            event.accept()
            return
        
        reply = QMessageBox.question(
            self, "Exit", "Are you sure you want to quit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        event.accept() if reply == QMessageBox.StandardButton.Yes else event.ignore()