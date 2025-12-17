# curatel_lms/ui/library_reports.py

# Displays system statistics, usage trends, and real-time database insights

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QFileDialog, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import csv

from curatel_lms.config import AppConfig

class ReportsAnalytics(QWidget):
    # Main reports widget: shows real-time library stats and sortable tables
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.stats = {
            'total_members': 0,
            'active_members': 0,
            'inactive_members': 0,
            'currently_borrowed': 0,
            'overdue_books': 0,
            'total_fines': 0.0
        }
        self.top_borrowers_data = []
        self.popular_books_data = []
        self.top_borrowers_sort_column = None
        self.top_borrowers_sort_order = Qt.SortOrder.AscendingOrder
        self.popular_books_sort_column = None
        self.popular_books_sort_order = Qt.SortOrder.AscendingOrder
        try:
            self.setup_ui()
            self.load_statistics()
            print("[INFO] Library Reports opened successfully with live data")
        except Exception as e:
            print(f"[ERROR] Failed to setup Library Reports: {e}")
            import traceback
            traceback.print_exc()
            self._show_critical("Initialization Error", f"Failed to initialize Library Reports:\n{str(e)}")

    def setup_ui(self):
        self.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        # Header
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
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)
        # Stats cards
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
        # Tables
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(20)
        self.top_borrowers_table, top_borrowers_widget = self.create_table_section(
            "Top Borrowers",
            "Members with the most borrowed books",
            ["Rank", "Full Name", "Books", "Fine"]
        )
        self.top_borrowers_table.horizontalHeader().sectionClicked.connect(self.handle_top_borrowers_header_click)
        tables_layout.addWidget(top_borrowers_widget)
        self.popular_books_table, popular_books_widget = self.create_table_section(
            "Most Popular Books",
            "Books borrowed most of the time",
            ["Rank", "Book Title", "Times Borrowed"]
        )
        self.popular_books_table.horizontalHeader().sectionClicked.connect(self.handle_popular_books_header_click)
        tables_layout.addWidget(popular_books_widget)
        main_layout.addLayout(tables_layout)
        main_layout.addStretch()

    def mousePressEvent(self, event):
        self._clear_selection(event)
        super().mousePressEvent(event)

    def _clear_selection(self, event):
        try:
            if hasattr(self, 'top_borrowers_table') and self.top_borrowers_table:
                self.top_borrowers_table.clearSelection()
            if hasattr(self, 'popular_books_table') and self.popular_books_table:
                self.popular_books_table.clearSelection()
        except Exception as e:
            print(f"[WARN] Clear selection error: {e}")

    def _fetch_count(self, query):
        try:
            result = self.db.fetch_one(query)
            if result:
                key = list(result.keys())[0]
                return result.get(key, 0)
            return 0
        except Exception as e:
            print(f"[ERROR] Fetch count failed: {e}")
            return 0

    def _fetch_total_fines(self):
        try:
            query = "SELECT SUM(fine_amount) as total_fines FROM borrowed_books WHERE fine_amount > 0"
            result = self.db.fetch_one(query)
            if result and result['total_fines']:
                return float(result['total_fines'])
            return 0.0
        except Exception as e:
            print(f"[ERROR] Fetch total fines failed: {e}")
            return 0.0

    def create_stat_card(self, title, value):
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
        title_label.setStyleSheet("color: black; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        value_label = QLabel(value)
        value_label.setFont(QFont("Montserrat", 11))
        value_label.setStyleSheet("color: black; background-color: transparent; border: none;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        return card

    def update_stat_card(self, card, value):
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(value)

    def load_statistics(self):
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
            import traceback
            traceback.print_exc()

    def load_borrowing_stats(self):
        try:
            query = "SELECT COUNT(*) as borrowed FROM borrowed_books WHERE status = 'Borrowed'"
            result = self.db.fetch_one(query)
            self.stats['currently_borrowed'] = result['borrowed'] if result else 0
            query = "SELECT COUNT(*) as overdue FROM borrowed_books WHERE status = 'Overdue'"
            result = self.db.fetch_one(query)
            self.stats['overdue_books'] = result['overdue'] if result else 0
            self.stats['total_fines'] = self._fetch_total_fines()
            print(f"[INFO] Loaded borrowing stats: {self.stats['currently_borrowed']} borrowed, "
                  f"{self.stats['overdue_books']} overdue, ₱{self.stats['total_fines']:.2f} in fines")
        except Exception as e:
            print(f"[ERROR] Failed to load borrowing stats: {e}")
            import traceback
            traceback.print_exc()

    def update_stat_cards(self):
        members_text = f"{self.stats['active_members']} active | {self.stats['inactive_members']} inactive"
        self.update_stat_card(self.total_members_card, members_text)
        borrowed_text = f"{self.stats['currently_borrowed']} {'book' if self.stats['currently_borrowed'] == 1 else 'books'}"
        self.update_stat_card(self.currently_borrowed_card, borrowed_text)
        overdue_text = f"{self.stats['overdue_books']} {'book' if self.stats['overdue_books'] == 1 else 'books'}"
        self.update_stat_card(self.overdue_books_card, overdue_text)
        fines_text = f"₱{self.stats['total_fines']:.2f}"
        self.update_stat_card(self.total_fines_card, fines_text)

    def create_table_section(self, title_text, subtitle_text, headers):
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
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title = QLabel(title_text)
        title.setFont(QFont("Montserrat", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: black; background-color: white; border: none")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(-10)
        subtitle = QLabel(subtitle_text)
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: black; background-color: white; border: none")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(10)
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setMinimumSize(540, 400)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionsClickable(True)
        if title_text == "Top Borrowers":
            table.setColumnWidth(0, 60)
            table.setColumnWidth(1, 250)
            table.setColumnWidth(2, 110)
            table.setColumnWidth(3, 110)
        elif title_text == "Most Popular Books":
            table.setColumnWidth(0, 60)
            table.setColumnWidth(1, 340)
            table.setColumnWidth(2, 130)
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
        layout.addWidget(table, alignment=Qt.AlignmentFlag.AlignCenter)
        return table, container

    def load_borrowers_data(self):
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
            import traceback
            traceback.print_exc()
            self.top_borrowers_data = []

    def load_popular_books_data(self):
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
            import traceback
            traceback.print_exc()
            self.popular_books_data = []

    def handle_top_borrowers_header_click(self, logical_index):
        try:
            if logical_index == 0: return
            if self.top_borrowers_sort_column == logical_index:
                self.top_borrowers_sort_order = Qt.SortOrder.DescendingOrder if self.top_borrowers_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                self.top_borrowers_sort_column = logical_index
                self.top_borrowers_sort_order = Qt.SortOrder.AscendingOrder
            self.display_sorted_borrowers()
        except Exception as e:
            print(f"[ERROR] Handle top borrowers header click failed: {e}")

    def handle_popular_books_header_click(self, logical_index):
        try:
            if logical_index == 0: return
            if self.popular_books_sort_column == logical_index:
                self.popular_books_sort_order = Qt.SortOrder.DescendingOrder if self.popular_books_sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                self.popular_books_sort_column = logical_index
                self.popular_books_sort_order = Qt.SortOrder.AscendingOrder
            self.display_sorted_popular_books()
        except Exception as e:
            print(f"[ERROR] Handle popular books header click failed: {e}")

    def display_sorted_borrowers(self):
        try:
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
        except Exception as e:
            print(f"[ERROR] Display sorted borrowers failed: {e}")
            import traceback
            traceback.print_exc()

    def display_sorted_popular_books(self):
        try:
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
        except Exception as e:
            print(f"[ERROR] Display sorted popular books failed: {e}")
            import traceback
            traceback.print_exc()

    def export_to_csv(self):
        try:
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
                writer.writerow(['LIBRARY STATISTICS'])
                writer.writerow([''])
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Members', f"{self.stats['active_members']} active | {self.stats['inactive_members']} inactive"])
                writer.writerow(['Currently Borrowed', f"{self.stats['currently_borrowed']} books"])
                writer.writerow(['Overdue Books', f"{self.stats['overdue_books']} books"])
                writer.writerow(['Total Fines', f"₱{self.stats['total_fines']:.2f}"])
                writer.writerow([''])
                writer.writerow([''])
                writer.writerow(['TOP BORROWERS'])
                writer.writerow([''])
                writer.writerow(['Rank', 'Full Name', 'Books Borrowed', 'Total Fines'])
                for idx, borrower in enumerate(self.top_borrowers_data[:5], 1):
                    fines = float(borrower['total_fines']) if borrower['total_fines'] else 0.0
                    writer.writerow([idx, borrower['full_name'], borrower['books_borrowed'], f"₱{fines:.2f}"])
                writer.writerow([''])
                writer.writerow([''])
                writer.writerow(['MOST POPULAR BOOKS'])
                writer.writerow([''])
                writer.writerow(['Rank', 'Book Title', 'Times Borrowed'])
                for idx, book in enumerate(self.popular_books_data[:5], 1):
                    writer.writerow([idx, book['title'], book['times_borrowed']])
            self._show_info(
                "Export Successful",
                f"Library report has been exported to:\n{file_path}"
            )
            print(f"[INFO] Report exported to: {file_path}")
        except Exception as e:
            print(f"[ERROR] Export to CSV failed: {e}")
            import traceback
            traceback.print_exc()
            self._show_critical("Export Failed", f"Failed to export report:\n{str(e)}")
    
    # Message Box Helpers
    def _show_warning(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #3C2A21;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)
        msg.exec()

    def _show_critical(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #3C2A21;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)
        msg.exec()

    def _show_info(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #3C2A21;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
            QMessageBox QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)
        msg.exec()