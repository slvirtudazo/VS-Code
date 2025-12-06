# ui/library_reports.py - Updated to show real-time Overdue Books and Total Fines WITH SORTING

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime

class ReportsAnalytics(QMainWindow):
    """Library Reports screen - displays dynamic data from database with real-time overdue and fines"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.setWindowTitle("Curatel - Library Reports")
        
        # Initialize statistics storage
        self.stats = {
            'total_members': 0,
            'active_members': 0,
            'inactive_members': 0,
            'currently_borrowed': 0,
            'overdue_books': 0,
            'total_fines': 0.0
        }
        
        # Initialize table data storage for sorting
        self.top_borrowers_data = []
        self.popular_books_data = []
        
        # Initialize sort states
        self.top_borrowers_sort_column = None
        self.top_borrowers_sort_order = Qt.SortOrder.AscendingOrder
        self.popular_books_sort_column = None
        self.popular_books_sort_order = Qt.SortOrder.AscendingOrder
        
        try:
            self.setup_ui()
            self.load_statistics()  # Load data after UI is ready
            self.show_fullscreen()
            print("[INFO] Library Reports opened successfully with live data")
        except Exception as e:
            print(f"[ERROR] Failed to setup Library Reports: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup UI matching circulation management design"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)

        # Header section
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Library Reports")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_text.addWidget(title)

        subtitle = QLabel("View library statistics, analyze trends, and track overall activity")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333;")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)

        header_layout.addLayout(header_text)
        header_layout.addStretch()

        back_btn = QPushButton("Back to Dashboard")
        back_btn.setFont(QFont("Montserrat", 10))
        back_btn.setFixedSize(150, 40)
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
        self.total_members_card = self.create_stat_card("Total Members", "Loading...")
        self.currently_borrowed_card = self.create_stat_card("Currently Borrowed", "Loading...")
        self.overdue_books_card = self.create_stat_card("Overdue Books", "Loading...")
        self.total_fines_card = self.create_stat_card("Total Fines", "Loading...")
        stats_layout.addWidget(self.total_members_card)
        stats_layout.addWidget(self.currently_borrowed_card)
        stats_layout.addWidget(self.overdue_books_card)
        stats_layout.addWidget(self.total_fines_card)
        main_layout.addLayout(stats_layout)
        main_layout.addSpacing(30)

        # Create two frames side by side for tables
        tables_layout = QHBoxLayout()

        # Left frame: Top Borrowers
        self.top_borrowers_table, top_borrowers_widget = self.create_table_section(
            "Top Borrowers",
            "Members with the most borrowed books",
            ["Rank", "Full Name", "Books", "Fine"]
        )
        # Connect header click for sorting
        self.top_borrowers_table.horizontalHeader().sectionClicked.connect(self.handle_top_borrowers_header_click)
        tables_layout.addWidget(top_borrowers_widget)

        # Right frame: Most Popular Books
        self.popular_books_table, popular_books_widget = self.create_table_section(
            "Most Popular Books",
            "Books borrowed most of the time",
            ["Rank", "Book Title", "Times Borrowed"]
        )
        # Connect header click for sorting
        self.popular_books_table.horizontalHeader().sectionClicked.connect(self.handle_popular_books_header_click)
        tables_layout.addWidget(popular_books_widget)

        main_layout.addLayout(tables_layout)
        main_layout.addStretch()

    
    def create_stat_card(self, title, value):
        """Create a statistics card that can be updated later"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1.5px solid #8B7E66;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        title_label.setStyleSheet("color: black; background-color: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        title_label.setStyleSheet("""
            color: black; 
            background-color: transparent;
            border: none;
        """)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Montserrat", 11))
        value_label.setStyleSheet("color: #333333; background-color: transparent;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value_label")  # Set object name so we can find and update it later
        layout.addWidget(value_label)
        value_label.setStyleSheet("""
            color: black; 
            background-color: transparent;
            border: none;
        """)
        
        return card
    
    def update_stat_card(self, card, value):
        """Update the value displayed in a stat card"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
    
    def load_statistics(self):
        """Load all statistics from the database"""
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection for reports")
            return
        
        try:
            # Load member statistics
            self.load_member_stats()
            
            # Load borrowing statistics
            self.load_borrowing_stats()
            
            # Update the stat cards with live data
            self.update_stat_cards()
            
            # Populate the tables with live data (store raw data for sorting)
            self.load_borrowers_data()
            self.load_popular_books_data()
            self.display_sorted_borrowers()
            self.display_sorted_popular_books()
            
            print("[INFO] Successfully loaded all report statistics")
            
        except Exception as e:
            print(f"[ERROR] Failed to load statistics: {e}")
            import traceback
            traceback.print_exc()
    
    def load_member_stats(self):
        """Load member-related statistics from database"""
        try:
            # Get total members count
            query = "SELECT COUNT(*) as total FROM members"
            result = self.db.fetch_one(query)
            self.stats['total_members'] = result['total'] if result else 0
            
            # Get active members count
            query = "SELECT COUNT(*) as active FROM members WHERE status = 'Active'"
            result = self.db.fetch_one(query)
            self.stats['active_members'] = result['active'] if result else 0
            
            # Get inactive members count
            query = "SELECT COUNT(*) as inactive FROM members WHERE status = 'Inactive'"
            result = self.db.fetch_one(query)
            self.stats['inactive_members'] = result['inactive'] if result else 0
            
            print(f"[INFO] Loaded member stats: {self.stats['total_members']} total, "
                  f"{self.stats['active_members']} active, {self.stats['inactive_members']} inactive")
            
        except Exception as e:
            print(f"[ERROR] Failed to load member stats: {e}")
    
    def load_borrowing_stats(self):
        """Load borrowing-related statistics from database - REAL-TIME overdue and fines"""
        try:
            # Get currently borrowed books count (status = 'Borrowed')
            query = "SELECT COUNT(*) as borrowed FROM borrowed_books WHERE status = 'Borrowed'"
            result = self.db.fetch_one(query)
            self.stats['currently_borrowed'] = result['borrowed'] if result else 0
            
            # Get OVERDUE books count - includes both status='Overdue' AND borrowed past due date
            query = """
                SELECT COUNT(*) as overdue 
                FROM borrowed_books 
                WHERE status = 'Overdue'
            """
            result = self.db.fetch_one(query)
            self.stats['overdue_books'] = result['overdue'] if result else 0
            
            # Get TOTAL FINES from ALL transactions (not just overdue)
            query = "SELECT SUM(fine_amount) as total_fines FROM borrowed_books WHERE fine_amount > 0"
            result = self.db.fetch_one(query)
            self.stats['total_fines'] = float(result['total_fines']) if result and result['total_fines'] else 0.0
            
            print(f"[INFO] Loaded borrowing stats: {self.stats['currently_borrowed']} borrowed, "
                  f"{self.stats['overdue_books']} overdue, ₱{self.stats['total_fines']:.2f} in fines")
            
        except Exception as e:
            print(f"[ERROR] Failed to load borrowing stats: {e}")
            import traceback
            traceback.print_exc()
    
    def update_stat_cards(self):
        """Update all stat cards with loaded data"""
        # Update Total Members card
        members_text = f"{self.stats['active_members']} active | {self.stats['inactive_members']} inactive"
        self.update_stat_card(self.total_members_card, members_text)
        
        # Update Currently Borrowed card
        borrowed_text = f"{self.stats['currently_borrowed']} {'book' if self.stats['currently_borrowed'] == 1 else 'books'}"
        self.update_stat_card(self.currently_borrowed_card, borrowed_text)
        
        # Update Overdue Books card
        overdue_text = f"{self.stats['overdue_books']} {'book' if self.stats['overdue_books'] == 1 else 'books'}"
        self.update_stat_card(self.overdue_books_card, overdue_text)
        
        # Update Total Fines card
        fines_text = f"₱{self.stats['total_fines']:.2f}"
        self.update_stat_card(self.total_fines_card, fines_text)
    
    def create_table_section(self, title_text, subtitle_text, headers):
        """Creates a frame with a title, subtitle, spacing, and a QTableWidget"""
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1.5px solid #8B7E66;
                border-radius: 15px;
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel(title_text)
        title.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        title.setStyleSheet("""
            QWidget {
                color: black;
                background-color: white;
                border: none
            }
        """)
        layout.addWidget(title)
        layout.addSpacing(-10)

        # Subtitle
        subtitle = QLabel(subtitle_text)
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("""
            QWidget {
                color: black;           
                background-color: white;
                border: none
            }
        """)
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        # Table
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setFixedSize(685, 400) 
        
        # Hide the default row number column (vertical header)
        table.verticalHeader().setVisible(False)
        
        # Configure horizontal header to stretch columns
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)  # Enable header clicking

        if title_text == "Top Borrowers":
            table.setColumnWidth(0, 50)             # Rank
            table.setColumnWidth(1, 400)            # Full Name
            table.setColumnWidth(2, 60)             # Books
            table.setColumnWidth(3, 50)             # Fine
        
        elif title_text == "Most Popular Books":
            table.setColumnWidth(0, 50)             # Rank
            table.setColumnWidth(1, 400)            # Book Title
            table.setColumnWidth(2, 50)             # Times Borrowed

        # Table settings
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setShowGrid(True)
        
        # Enable vertical scrollbar when needed
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        # Table-specific stylesheet with black borders and gridlines
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: black;
                background-color: white;
                selection-background-color: #D9CFC2;
                selection-color: black;
            }
            QHeaderView::section {
                background-color: #9B8B7E;
                padding: 8px;
                font-weight: bold;
                color: white;
                font-family: Montserrat;
                font-size: 12px;
                border: 1px solid transparent;
            }
            QHeaderView::section:hover {
                background-color: #7A6D55;
            }
            QTableWidget::item:selected {
                background-color: #C9B8A8;
            }
            QScrollBar:vertical {
                border: none;
                background: #D4C4B4;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #8B7E66;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6B5E46;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        layout.addWidget(table)

        return table, container

    def load_borrowers_data(self):
        """Load raw borrowers data from database for sorting"""
        try:
            query = """
                SELECT 
                    m.member_id,
                    m.full_name,
                    COUNT(bb.borrow_id) as books_borrowed,
                    SUM(bb.fine_amount) as total_fines
                FROM members m
                LEFT JOIN borrowed_books bb ON m.member_id = bb.member_id
                GROUP BY m.member_id, m.full_name
                HAVING books_borrowed > 0
                ORDER BY books_borrowed DESC, total_fines DESC
            """
            
            self.top_borrowers_data = self.db.fetch_all(query) or []
            print(f"[INFO] Loaded {len(self.top_borrowers_data)} borrowers for sorting")
            
        except Exception as e:
            print(f"[ERROR] Failed to load borrowers data: {e}")
            self.top_borrowers_data = []
    
    def load_popular_books_data(self):
        """Load raw popular books data from database for sorting"""
        try:
            query = """
                SELECT 
                    b.book_id,
                    b.title,
                    COUNT(bb.borrow_id) as times_borrowed
                FROM books b
                LEFT JOIN borrowed_books bb ON b.book_id = bb.book_id
                GROUP BY b.book_id, b.title
                HAVING times_borrowed > 0
                ORDER BY times_borrowed DESC
            """
            
            self.popular_books_data = self.db.fetch_all(query) or []
            print(f"[INFO] Loaded {len(self.popular_books_data)} popular books for sorting")
            
        except Exception as e:
            print(f"[ERROR] Failed to load popular books data: {e}")
            self.popular_books_data = []

    def handle_top_borrowers_header_click(self, logical_index):
        """Handle header click for Top Borrowers table sorting"""
        try:
            # Skip sorting for Rank column (index 0) since it's derived
            if logical_index == 0:
                return
                
            if self.top_borrowers_sort_column == logical_index:
                # Toggle sort order
                self.top_borrowers_sort_order = Qt.SortOrder.DescendingOrder if self.top_borrowers_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                # New column, start with ascending
                self.top_borrowers_sort_column = logical_index
                self.top_borrowers_sort_order = Qt.SortOrder.AscendingOrder
            
            self.display_sorted_borrowers()
            
        except Exception as e:
            print(f"[ERROR] Top borrowers header click error: {e}")

    def handle_popular_books_header_click(self, logical_index):
        """Handle header click for Popular Books table sorting"""
        try:
            # Skip sorting for Rank column (index 0) since it's derived
            if logical_index == 0:
                return
                
            if self.popular_books_sort_column == logical_index:
                # Toggle sort order
                self.popular_books_sort_order = Qt.SortOrder.DescendingOrder if self.popular_books_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                # New column, start with ascending
                self.popular_books_sort_column = logical_index
                self.popular_books_sort_order = Qt.SortOrder.AscendingOrder
            
            self.display_sorted_popular_books()
            
        except Exception as e:
            print(f"[ERROR] Popular books header click error: {e}")

    def display_sorted_borrowers(self):
        """Display sorted borrowers data in table"""
        try:
            if not self.top_borrowers_data:
                self.top_borrowers_table.setRowCount(0)
                return
            
            # Create a copy to sort
            sorted_data = self.top_borrowers_data.copy()
            
            # Map column indices to data keys
            column_keys = {
                1: 'full_name',      # Full Name
                2: 'books_borrowed', # Books
                3: 'total_fines'     # Fine
            }
            
            if self.top_borrowers_sort_column in column_keys:
                sort_key = column_keys[self.top_borrowers_sort_column]
                
                def sort_value(item):
                    value = item.get(sort_key)
                    if sort_key == 'full_name':
                        return str(value).lower() if value else ''
                    elif sort_key == 'books_borrowed':
                        return int(value) if value else 0
                    elif sort_key == 'total_fines':
                        return float(value) if value else 0.0
                    return value
                
                sorted_data.sort(
                    key=sort_value,
                    reverse=(self.top_borrowers_sort_order == Qt.SortOrder.DescendingOrder)
                )
            
            # Limit to top 5 after sorting
            display_data = sorted_data[:5]
            self.top_borrowers_table.setRowCount(len(display_data))
            
            for row, borrower in enumerate(display_data):
                rank = row + 1
                
                # Rank column
                item = QTableWidgetItem(str(rank))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.top_borrowers_table.setItem(row, 0, item)
                
                # Full Name column
                item = QTableWidgetItem(str(borrower['full_name']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.top_borrowers_table.setItem(row, 1, item)
                
                # Books borrowed column
                item = QTableWidgetItem(str(borrower['books_borrowed']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.top_borrowers_table.setItem(row, 2, item)
                
                # Total fines column
                fines = float(borrower['total_fines']) if borrower['total_fines'] else 0.0
                item = QTableWidgetItem(f"₱{fines:.2f}")
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.top_borrowers_table.setItem(row, 3, item)
            
            print(f"[INFO] Displayed {len(display_data)} sorted borrowers")
            
        except Exception as e:
            print(f"[ERROR] Display sorted borrowers error: {e}")
            self.top_borrowers_table.setRowCount(0)
    
    def display_sorted_popular_books(self):
        """Display sorted popular books data in table"""
        try:
            if not self.popular_books_data:
                self.popular_books_table.setRowCount(0)
                return
            
            # Create a copy to sort
            sorted_data = self.popular_books_data.copy()
            
            # Map column indices to data keys
            column_keys = {
                1: 'title',             # Book Title
                2: 'times_borrowed'     # Times Borrowed
            }
            
            if self.popular_books_sort_column in column_keys:
                sort_key = column_keys[self.popular_books_sort_column]
                
                def sort_value(item):
                    value = item.get(sort_key)
                    if sort_key == 'title':
                        return str(value).lower() if value else ''
                    elif sort_key == 'times_borrowed':
                        return int(value) if value else 0
                    return value
                
                sorted_data.sort(
                    key=sort_value,
                    reverse=(self.popular_books_sort_order == Qt.SortOrder.DescendingOrder)
                )
            
            # Limit to top 5 after sorting
            display_data = sorted_data[:5]
            self.popular_books_table.setRowCount(len(display_data))
            
            for row, book in enumerate(display_data):
                rank = row + 1
                
                # Rank column
                item = QTableWidgetItem(str(rank))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.popular_books_table.setItem(row, 0, item)
                
                # Book title column
                item = QTableWidgetItem(str(book['title']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.popular_books_table.setItem(row, 1, item)
                
                # Times borrowed column
                item = QTableWidgetItem(str(book['times_borrowed']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.popular_books_table.setItem(row, 2, item)
            
            print(f"[INFO] Displayed {len(display_data)} sorted popular books")
            
        except Exception as e:
            print(f"[ERROR] Display sorted popular books error: {e}")
            self.popular_books_table.setRowCount(0)
    
    def go_back_to_dashboard(self):
        """Go back to dashboard"""
        self.close()
    
    def show_fullscreen(self):
        """Show window maximized"""
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()