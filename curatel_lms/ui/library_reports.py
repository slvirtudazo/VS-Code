# curatel_lms/ui/library_reports.py

# Displays system statistics, usage trends, and real-time database insights

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import csv
from PyQt6.QtWidgets import QFileDialog

# UI layout constants
BUTTON_HEIGHT = 40
CARD_PADDING = 15
TABLE_HEIGHT = 400
TABLE_WIDTH = 685

# Table appearance style
TABLE_STYLE = """
    QTableWidget {
        border: 1px solid #8B7E66;
        gridline-color: #8B7E66;
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
        border: none;
    }
    QHeaderView::section:hover {
        background-color: #7A6D55;
    }
    QTableWidget::item:hover {
        background-color: #D9CFC2;
    }
    QTableWidget::item:selected {
        background-color: #C9B8A8;
    }
    QTableCornerButton::section {
        background-color: #9B8B7E;
        border: 1px solid #8B7E66;
    }
"""

# Button appearance style
BUTTON_STYLE = """
    QPushButton {
        background-color: #8B7E66;
        color: white;
        border: none;
        border-radius: 10px;
    }
    QPushButton:hover {
        background-color: #6B5E46;
    }
"""

# Database queries for stats
QUERY_TOTAL_MEMBERS = "SELECT COUNT(*) as total FROM members"
QUERY_ACTIVE_MEMBERS = "SELECT COUNT(*) as active FROM members WHERE status = 'Active'"
QUERY_INACTIVE_MEMBERS = "SELECT COUNT(*) as inactive FROM members WHERE status = 'Inactive'"
QUERY_BORROWED_BOOKS = "SELECT COUNT(*) as borrowed FROM borrowed_books WHERE status = 'Borrowed'"
QUERY_OVERDUE_BOOKS = "SELECT COUNT(*) as overdue FROM borrowed_books WHERE status = 'Overdue'"
QUERY_TOTAL_FINES = "SELECT SUM(fine_amount) as total_fines FROM borrowed_books WHERE fine_amount > 0"

QUERY_TOP_BORROWERS = """
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

QUERY_POPULAR_BOOKS = """
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

class ReportsAnalytics(QMainWindow):
    # Main reports window: shows real-time library stats and sortable tables
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.setWindowTitle("Curatel - Library Reports")
        
        # Store key metrics
        self.stats = {
            'total_members': 0,
            'active_members': 0,
            'inactive_members': 0,
            'currently_borrowed': 0,
            'overdue_books': 0,
            'total_fines': 0.0
        }
        
        # Store raw table data for sorting
        self.top_borrowers_data = []
        self.popular_books_data = []
        
        # Track sort state per table
        self.top_borrowers_sort_column = None
        self.top_borrowers_sort_order = Qt.SortOrder.AscendingOrder
        self.popular_books_sort_column = None
        self.popular_books_sort_order = Qt.SortOrder.AscendingOrder
        
        try:
            self.setup_ui()
            self.load_statistics()
            self.show_fullscreen()
            print("[INFO] Library Reports opened successfully with live data")
        except Exception as e:
            print(f"[ERROR] Failed to setup Library Reports: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        # Build UI matching circulation screen style
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)

        # Header with title, subtitle, and back button
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

        # In setup_ui method, modify the header section:
        export_btn = QPushButton("Export to CSV")
        export_btn.setFont(QFont("Montserrat", 10))
        export_btn.setFixedSize(150, 40)
        export_btn.setStyleSheet("""
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
        export_btn.clicked.connect(self.export_to_csv)
        header_layout.addWidget(export_btn)
        header_layout.addSpacing(10)

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

        # Stats cards row
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

        # Side-by-side tables
        tables_layout = QHBoxLayout()

        # Top Borrowers table
        self.top_borrowers_table, top_borrowers_widget = self.create_table_section(
            "Top Borrowers",
            "Members with the most borrowed books",
            ["Rank", "Full Name", "Books", "Fine"]
        )
        self.top_borrowers_table.horizontalHeader().sectionClicked.connect(self.handle_top_borrowers_header_click)
        tables_layout.addWidget(top_borrowers_widget)

        # Popular Books table
        self.popular_books_table, popular_books_widget = self.create_table_section(
            "Most Popular Books",
            "Books borrowed most of the time",
            ["Rank", "Book Title", "Times Borrowed"]
        )
        self.popular_books_table.horizontalHeader().sectionClicked.connect(self.handle_popular_books_header_click)
        tables_layout.addWidget(popular_books_widget)

        main_layout.addLayout(tables_layout)
        main_layout.addStretch()

    def _fetch_count(self, query):
        # Get single count value from query
        result = self.db.fetch_one(query)
        if result:
            key = list(result.keys())[0]
            return result.get(key, 0)
        return 0

    def _calculate_statistics(self):
        # Compute all report metrics
        self.stats = {
            'total_members': self._fetch_count(QUERY_TOTAL_MEMBERS),
            'active_members': self._fetch_count(QUERY_ACTIVE_MEMBERS),
            'inactive_members': self._fetch_count(QUERY_INACTIVE_MEMBERS),
            'currently_borrowed': self._fetch_count(QUERY_BORROWED_BOOKS),
            'overdue_books': self._fetch_count(QUERY_OVERDUE_BOOKS),
            'total_fines': self._fetch_total_fines()
        }

    def _fetch_total_fines(self):
        # Get sum of all fines
        result = self.db.fetch_one(QUERY_TOTAL_FINES)
        if result and result['total_fines']:
            return float(result['total_fines'])
        return 0.0
    
    def create_stat_card(self, title, value):
        # Build reusable stat card widget
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
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        value_label.setStyleSheet("""
            color: black; 
            background-color: transparent;
            border: none;
        """)
        return card
    
    def update_stat_card(self, card, value):
        # Update stat card value by name
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)
    
    def load_statistics(self):
        # Load all stats and tables from DB
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection for reports")
            return
        
        try:
            self.load_member_stats()
            self.load_borrowing_stats()
            self.update_stat_cards()
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
        # Load member counts from DB
        try:
            query = "SELECT COUNT(*) as total FROM members"
            result = self.db.fetch_one(query)
            self.stats['total_members'] = result['total'] if result else 0
            
            query = "SELECT COUNT(*) as active FROM members WHERE status = 'Active'"
            result = self.db.fetch_one(query)
            self.stats['active_members'] = result['active'] if result else 0
            
            query = "SELECT COUNT(*) as inactive FROM members WHERE status = 'Inactive'"
            result = self.db.fetch_one(query)
            self.stats['inactive_members'] = result['inactive'] if result else 0
            
            print(f"[INFO] Loaded member stats: {self.stats['total_members']} total, "
                  f"{self.stats['active_members']} active, {self.stats['inactive_members']} inactive")
        except Exception as e:
            print(f"[ERROR] Failed to load member stats: {e}")
    
    def load_borrowing_stats(self):
        # Load real-time borrowing data
        try:
            query = "SELECT COUNT(*) as borrowed FROM borrowed_books WHERE status = 'Borrowed'"
            result = self.db.fetch_one(query)
            self.stats['currently_borrowed'] = result['borrowed'] if result else 0
            
            query = "SELECT COUNT(*) as overdue FROM borrowed_books WHERE status = 'Overdue'"
            result = self.db.fetch_one(query)
            self.stats['overdue_books'] = result['overdue'] if result else 0
            
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
        # Refresh all stat card displays
        members_text = f"{self.stats['active_members']} active | {self.stats['inactive_members']} inactive"
        self.update_stat_card(self.total_members_card, members_text)
        
        borrowed_text = f"{self.stats['currently_borrowed']} {'book' if self.stats['currently_borrowed'] == 1 else 'books'}"
        self.update_stat_card(self.currently_borrowed_card, borrowed_text)
        
        overdue_text = f"{self.stats['overdue_books']} {'book' if self.stats['overdue_books'] == 1 else 'books'}"
        self.update_stat_card(self.overdue_books_card, overdue_text)
        
        fines_text = f"₱{self.stats['total_fines']:.2f}"
        self.update_stat_card(self.total_fines_card, fines_text)
    
    def create_table_section(self, title_text, subtitle_text, headers):
        # Build styled table container
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

        title = QLabel(title_text)
        title.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background-color: white; border: none")
        layout.addWidget(title)
        layout.addSpacing(-10)

        subtitle = QLabel(subtitle_text)
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: black; background-color: white; border: none")
        layout.addWidget(subtitle)
        layout.addSpacing(10)

        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setFixedSize(685, 400) 
        
        table.verticalHeader().setVisible(False)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setSectionsClickable(True)

        if title_text == "Top Borrowers":
            table.setColumnWidth(0, 50)
            table.setColumnWidth(1, 400)
            table.setColumnWidth(2, 60)
            table.setColumnWidth(3, 50)
        elif title_text == "Most Popular Books":
            table.setColumnWidth(0, 50)
            table.setColumnWidth(1, 400)
            table.setColumnWidth(2, 50)

        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setShowGrid(True)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
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
        # Fetch top borrowers raw data
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
        # Fetch popular books raw data
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
        # Sort borrowers table by clicked column
        if logical_index == 0: return
        if self.top_borrowers_sort_column == logical_index:
            self.top_borrowers_sort_order = Qt.SortOrder.DescendingOrder if self.top_borrowers_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.top_borrowers_sort_column = logical_index
            self.top_borrowers_sort_order = Qt.SortOrder.AscendingOrder
        self.display_sorted_borrowers()

    def handle_popular_books_header_click(self, logical_index):
        # Sort books table by clicked column
        if logical_index == 0: return
        if self.popular_books_sort_column == logical_index:
            self.popular_books_sort_order = Qt.SortOrder.DescendingOrder if self.popular_books_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.popular_books_sort_column = logical_index
            self.popular_books_sort_order = Qt.SortOrder.AscendingOrder
        self.display_sorted_popular_books()

    def display_sorted_borrowers(self):
        # Render sorted top borrowers (top 5)
        if not self.top_borrowers_data:
            self.top_borrowers_table.setRowCount(0)
            return
        
        sorted_data = self.top_borrowers_data.copy()
        column_keys = {1: 'full_name', 2: 'books_borrowed', 3: 'total_fines'}
        
        if self.top_borrowers_sort_column in column_keys:
            sort_key = column_keys[self.top_borrowers_sort_column]
            def sort_value(item):
                value = item.get(sort_key)
                if sort_key == 'full_name': return str(value).lower() if value else ''
                elif sort_key == 'books_borrowed': return int(value) if value else 0
                elif sort_key == 'total_fines': return float(value) if value else 0.0
                return value
            sorted_data.sort(key=sort_value, reverse=(self.top_borrowers_sort_order == Qt.SortOrder.DescendingOrder))
        
        display_data = sorted_data[:5]
        self.top_borrowers_table.setRowCount(len(display_data))
        
        for row, borrower in enumerate(display_data):
            rank = row + 1
            item = QTableWidgetItem(str(rank))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_borrowers_table.setItem(row, 0, item)
            
            item = QTableWidgetItem(str(borrower['full_name']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_borrowers_table.setItem(row, 1, item)
            
            item = QTableWidgetItem(str(borrower['books_borrowed']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_borrowers_table.setItem(row, 2, item)
            
            fines = float(borrower['total_fines']) if borrower['total_fines'] else 0.0
            item = QTableWidgetItem(f"₱{fines:.2f}")
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_borrowers_table.setItem(row, 3, item)
        
        print(f"[INFO] Displayed {len(display_data)} sorted borrowers")
    
    def display_sorted_popular_books(self):
        # Render sorted popular books (top 5)
        if not self.popular_books_data:
            self.popular_books_table.setRowCount(0)
            return
        
        sorted_data = self.popular_books_data.copy()
        column_keys = {1: 'title', 2: 'times_borrowed'}
        
        if self.popular_books_sort_column in column_keys:
            sort_key = column_keys[self.popular_books_sort_column]
            def sort_value(item):
                value = item.get(sort_key)
                if sort_key == 'title': return str(value).lower() if value else ''
                elif sort_key == 'times_borrowed': return int(value) if value else 0
                return value
            sorted_data.sort(key=sort_value, reverse=(self.popular_books_sort_order == Qt.SortOrder.DescendingOrder))
        
        display_data = sorted_data[:5]
        self.popular_books_table.setRowCount(len(display_data))
        
        for row, book in enumerate(display_data):
            rank = row + 1
            item = QTableWidgetItem(str(rank))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.popular_books_table.setItem(row, 0, item)
            
            item = QTableWidgetItem(str(book['title']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.popular_books_table.setItem(row, 1, item)
            
            item = QTableWidgetItem(str(book['times_borrowed']))
            item.setFont(QFont("Montserrat", 10))
            item.setForeground(QColor("#000000"))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.popular_books_table.setItem(row, 2, item)
        
        print(f"[INFO] Displayed {len(display_data)} sorted popular books")
    
    def export_to_csv(self):
        # Export all report data to CSV file
        try:
            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Library Report to CSV",
                "library_report.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write statistics section
                writer.writerow(['LIBRARY STATISTICS'])
                writer.writerow([''])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Members', f"{self.stats['active_members']} active | {self.stats['inactive_members']} inactive"])
                writer.writerow(['Currently Borrowed', f"{self.stats['currently_borrowed']} books"])
                writer.writerow(['Overdue Books', f"{self.stats['overdue_books']} books"])
                writer.writerow(['Total Fines', f"₱{self.stats['total_fines']:.2f}"])
                writer.writerow([''])
                writer.writerow([''])
                
                # Write Top Borrowers section
                writer.writerow(['TOP BORROWERS'])
                writer.writerow([''])
                writer.writerow(['Rank', 'Full Name', 'Books Borrowed', 'Total Fines'])
                
                for idx, borrower in enumerate(self.top_borrowers_data[:5], 1):
                    fines = float(borrower['total_fines']) if borrower['total_fines'] else 0.0
                    writer.writerow([
                        idx,
                        borrower['full_name'],
                        borrower['books_borrowed'],
                        f"₱{fines:.2f}"
                    ])
                
                writer.writerow([''])
                writer.writerow([''])
                
                # Write Popular Books section
                writer.writerow(['MOST POPULAR BOOKS'])
                writer.writerow([''])
                writer.writerow(['Rank', 'Book Title', 'Times Borrowed'])
                
                for idx, book in enumerate(self.popular_books_data[:5], 1):
                    writer.writerow([
                        idx,
                        book['title'],
                        book['times_borrowed']
                    ])
            
            QMessageBox.information(
                self, "Export Successful",
                f"Library report has been exported to:\n{file_path}"
            )
            print(f"[INFO] Report exported to: {file_path}")
            
        except Exception as e:
            print(f"[ERROR] Export to CSV failed: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Export Failed",
                f"Failed to export report:\n{str(e)}"
            )
    
    def go_back_to_dashboard(self):
        # Close and return to main screen
        self.close()
    
    def show_fullscreen(self):
        # Maximize window on open
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.showMaximized()
    
    def closeEvent(self, event):
        # Confirm window close
        event.accept()