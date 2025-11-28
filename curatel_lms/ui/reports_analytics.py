# ui/reports_analytics.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class ReportsAnalytics(QMainWindow):
    """Reports and Analytics screen"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.setWindowTitle("Reports and Analytics - Curatel LMS")
        try:
            self.setup_ui()
            self.show_fullscreen()
            print("[INFO] Reports and Analytics opened successfully")
        except Exception as e:
            print(f"[ERROR] Failed to setup Reports and Analytics: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #C9B8A8;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        header_text = QVBoxLayout()
        title = QLabel("Reports and Analytics")
        title.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; border: none;")
        header_text.addWidget(title)
        
        subtitle = QLabel("View library statistics, analyze trends, and track overall activity")
        subtitle.setFont(QFont("Montserrat", 10))
        subtitle.setStyleSheet("color: #333333; border: none;")
        header_text.addWidget(subtitle)
        
        header_text.setSpacing(0)
        header_text.setContentsMargins(0, 0, 0, 0)
        
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFont(QFont("Montserrat", 10))
        back_btn.setFixedSize(150, 35)
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
        main_layout.addSpacing(20)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        stats_layout.addWidget(self.create_stat_card("Total Members", "28 active | 4 inactive"))
        stats_layout.addWidget(self.create_stat_card("Currently Borrowed", "0 book"))
        stats_layout.addWidget(self.create_stat_card("Overdue Books", "0 book"))
        stats_layout.addWidget(self.create_stat_card("Total Fines", "₽0.00"))
        
        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(30)
        
        # Tables section
        tables_layout = QHBoxLayout()
        
        # Top Borrowers
        borrowers_container = self.create_table_section("Top Borrowers", "Members with the most borrowed books")
        self.top_borrowers_table = borrowers_container[0]
        tables_layout.addWidget(borrowers_container[1])
        
        # Most Popular Books
        popular_container = self.create_table_section("Most Popular Books", "Books borrowed most of the time")
        self.popular_books_table = popular_container[0]
        tables_layout.addWidget(popular_container[1])
        
        main_layout.addLayout(tables_layout)
        main_layout.addStretch()
    
    def create_stat_card(self, title, value):
        """Create a statistics card"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #D4C4B4;
                border: 2px solid #8B7E66;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Montserrat", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #000000; background-color: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Montserrat", 11))
        value_label.setStyleSheet("color: #333333; background-color: transparent;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        return card
    
    def create_table_section(self, title, subtitle):
        """Create a table section"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #D4C4B4;
                border: 2px solid #8B7E66;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Montserrat", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("Montserrat", 9))
        subtitle_label.setStyleSheet("color: #555555; background-color: transparent;")
        layout.addWidget(subtitle_label)
        
        layout.addSpacing(10)
        
        table = QTableWidget()
        
        if "Borrowers" in title:
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Rank", "Full Name", "Books", "Fines"])
            self.populate_borrowers_table(table)
        else:
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Rank", "Book", "Times Borrowed"])
            self.populate_popular_books_table(table)
        
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #8B7E66;
                border-radius: 10px;
                background-color: white;
                gridline-color: #EEEEEE;
            }
            QHeaderView::section {
                background-color: #A89B8E;
                padding: 6px;
                border: 1px solid #8B7E66;
                font-weight: bold;
                color: white;
                font-family: Montserrat;
            }
            QTableWidget::item {
                padding: 5px;
                color: #000000;
                background-color: white;
            }
            QTableWidget::item:alternate {
                background-color: #FAFAFA;
            }
        """)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.setFixedHeight(260)
        
        layout.addWidget(table)
        
        return (table, container)
    
    def populate_borrowers_table(self, table):
        """Populate borrowers table"""
        data = [
            ("1", "John Doe", "12", "₽0.00"),
            ("2", "Jane Smith", "10", "₽0.00"),
            ("3", "Robert Johnson", "8", "₽150.00"),
            ("4", "Maria Garcia", "7", "₽0.00"),
            ("5", "David Lee", "6", "₽0.00"),
        ]
        
        table.setRowCount(len(data))
        
        for row, (rank, name, books, fines) in enumerate(data):
            items = [
                QTableWidgetItem(rank),
                QTableWidgetItem(name),
                QTableWidgetItem(books),
                QTableWidgetItem(fines)
            ]
            for col, item in enumerate(items):
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)
    
    def populate_popular_books_table(self, table):
        """Populate popular books table"""
        data = [
            ("1", "To Kill a Mockingbird", "28"),
            ("2", "1984", "25"),
            ("3", "Pride and Prejudice", "22"),
            ("4", "The Great Gatsby", "20"),
            ("5", "The Hobbit", "18"),
        ]
        
        table.setRowCount(len(data))
        
        for row, (rank, book, times) in enumerate(data):
            items = [
                QTableWidgetItem(rank),
                QTableWidgetItem(book),
                QTableWidgetItem(times)
            ]
            for col, item in enumerate(items):
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col, item)
    
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