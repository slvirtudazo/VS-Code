# ui/circulation_management.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class CirculationManagement(QMainWindow):
    """Circulation Management screen"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.setWindowTitle("Circulation Management - Curatel LMS")
        try:
            self.setup_ui()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Circulation Management: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #C9B8A8;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_text = QVBoxLayout()
        title = QLabel("Circulation Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_text.addWidget(title)
        
        subtitle = QLabel("Monitor issued books, returns, and charges")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333;")
        header_text.addWidget(subtitle)
        
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFont(QFont("Montserrat", 11))
        back_btn.setFixedSize(160, 40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_dashboard)
        header_layout.addWidget(back_btn)
        
        main_layout.addLayout(header_layout)
        
        # Search section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by id, name, email, or mobile number")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #8B7E66;
                border-radius: 12px;
                padding: 8px 15px;
                font-family: Montserrat;
                font-size: 11px;
                color: #000000;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6B5E46;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
        """)
        self.search_input.setFixedHeight(38)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.setFont(QFont("Montserrat", 10))
        search_btn.setFixedSize(95, 38)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B8B7E;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B7B6E;
            }
        """)
        search_layout.addWidget(search_btn)
        
        search_layout.addSpacing(20)
        
        status_label = QLabel("Status")
        status_label.setFont(QFont("Montserrat", 10))
        status_label.setStyleSheet("color: #000000;")
        search_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Issued", "Returned"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #8B7E66;
                border-radius: 8px;
                padding: 5px 10px;
                font-family: Montserrat;
                font-size: 10px;
                color: #000000;
                background-color: white;
            }
        """)
        self.status_combo.setFixedSize(120, 35)
        search_layout.addWidget(self.status_combo)
        
        search_layout.addStretch()
        main_layout.addLayout(search_layout)
        
        # Circulation table
        self.circulation_table = QTableWidget()
        self.circulation_table.setColumnCount(9)
        self.circulation_table.setHorizontalHeaderLabels(["Book ID", "Member ID", "Book Title", "Borrow Date", "Return Date", "Due Date", "Status", "Fine Amount", "Updated At"])
        self.circulation_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #8B7E66;
                border-radius: 10px;
                background-color: #E8DCC8;
                gridline-color: #8B7E66;
            }
            QHeaderView::section {
                background-color: #9B8B7E;
                padding: 8px;
                border: 1px solid #8B7E66;
                font-weight: bold;
                color: #FFFFFF;
                font-family: Montserrat;
            }
            QTableWidget::item {
                padding: 8px;
                color: #000000;
                background-color: white;
            }
        """)
        self.circulation_table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.circulation_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Member")
        add_btn.setFont(QFont("Montserrat", 10))
        add_btn.setFixedSize(120, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        action_layout.addWidget(add_btn)
        
        update_btn = QPushButton("Update Member")
        update_btn.setFont(QFont("Montserrat", 10))
        update_btn.setFixedSize(130, 40)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        action_layout.addWidget(update_btn)
        
        delete_btn = QPushButton("Delete Member")
        delete_btn.setFont(QFont("Montserrat", 10))
        delete_btn.setFixedSize(130, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        main_layout.addLayout(action_layout)
    
    def go_back_to_dashboard(self):
        """Go back to dashboard without terminating"""
        self.close()
    
    def show_fullscreen(self):
        """Show window in fixed fullscreen 1920x1080"""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()