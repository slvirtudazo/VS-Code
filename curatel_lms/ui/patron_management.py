# ui/patron_management.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
                              QComboBox, QMessageBox, QHeaderView, QAbstractItemView, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from curatel_lms.ui.patron_dialogs import (AddMemberDialog, ViewMemberDialog, 
                                            UpdateMemberDialog, ConfirmDeleteMemberDialog)

class PatronManagement(QMainWindow):
    """Patron Management screen"""
    
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.all_members = []
        self.selected_member_id = None
        self.sort_column = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.setWindowTitle("Curatel - Patron Management")
        try:
            self.setup_ui()
            self.load_members_from_database()
            self.show_fullscreen()
        except Exception as e:
            print(f"[ERROR] Failed to setup Patron Management: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to initialize Patron Management:\n{str(e)}")
    
    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.mousePressEvent = self.clear_selection
        central_widget.setStyleSheet("background-color: white;")
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 30)
        main_layout.setSpacing(-5)
        
        # Header section
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()

        title = QLabel("Patron Management")
        title.setFont(QFont("Montserrat", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_text.addWidget(title)

        subtitle = QLabel("Manage member records, status, and registration details")
        subtitle.setFont(QFont("Montserrat", 11))
        subtitle.setStyleSheet("color: #333333;")
        header_text.addWidget(subtitle)
        header_text.addSpacing(15)

        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by id, name, email, or mobile number")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #8B7E66;
                border-radius: 10px;
                padding: 8px 10px;
                font-family: Montserrat;
                font-size: 11px;
                color: black;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #6B5E46;
            }
            QLineEdit::placeholder {
                color: gray;
            }
        """)
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self.filter_members)
        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(50)
        
        status_label = QLabel("Status")
        status_label.setFont(QFont("Montserrat", 10))
        status_label.setStyleSheet("color: #000000;")
        search_layout.addWidget(status_label)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Active", "Inactive"])
        self.status_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #8B7E66;
                border-radius: 10px;
                padding: 5px 10px;
                font-family: Montserrat;
                font-size: 12px;
                color: #000000;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #6B5E46;
            }
            QComboBox QAbstractItemView {
                color: #000000;
                background-color: white;
                selection-background-color: #D9CFC2;
                selection-color: black;
            }
        """)
        self.status_combo.setFixedSize(120, 40)
        self.status_combo.currentTextChanged.connect(self.filter_members)
        search_layout.addWidget(self.status_combo)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)
        main_layout.addSpacing(5)
        
        # Members table
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(8)
        self.members_table.setSortingEnabled(False)
        self.members_table.setHorizontalHeaderLabels(["Member ID", "Full Name", "Email", 
                                                      "Mobile Number", "Status", "Borrowed Books", 
                                                      "Added At", "Updated At"])
        
        self.members_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.members_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.members_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.members_table.setAlternatingRowColors(True)
        self.members_table.setStyleSheet("""
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
        """)
        
        header = self.members_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.members_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setSectionsClickable(True)
        header.setStretchLastSection(True)
        header.setSectionsMovable(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.sectionClicked.connect(self.handle_header_click)
        
        self.members_table.setColumnWidth(0, 100)
        self.members_table.setColumnWidth(1, 200)
        self.members_table.setColumnWidth(2, 250)
        self.members_table.setColumnWidth(3, 180)
        self.members_table.setColumnWidth(4, 100)
        self.members_table.setColumnWidth(5, 140)
        self.members_table.setColumnWidth(6, 200)
        self.members_table.setColumnWidth(7, 200)
        
        self.members_table.verticalHeader().setVisible(False)
        self.members_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.members_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.members_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.members_table.itemSelectionChanged.connect(self.on_selection_changed)

        main_layout.addWidget(self.members_table)
        main_layout.addSpacing(5)

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
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """)
        add_btn.clicked.connect(self.add_member)
        action_layout.addWidget(add_btn)

        view_btn = QPushButton("View Member")
        view_btn.setFont(QFont("Montserrat", 10))
        view_btn.setFixedSize(120, 40)
        view_btn.setStyleSheet("""
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
        view_btn.clicked.connect(self.view_member)
        action_layout.addWidget(view_btn)
        
        update_btn = QPushButton("Update Member")
        update_btn.setFont(QFont("Montserrat", 10))
        update_btn.setFixedSize(130, 40)
        update_btn.setStyleSheet("""
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
        update_btn.clicked.connect(self.update_member)
        action_layout.addWidget(update_btn)
        
        delete_btn = QPushButton("Delete Member")
        delete_btn.setFont(QFont("Montserrat", 10))
        delete_btn.setFixedSize(130, 40)
        delete_btn.setStyleSheet("""
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
        delete_btn.clicked.connect(self.delete_member)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        
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
        action_layout.addWidget(back_btn)
        
        main_layout.addLayout(action_layout)
    
    def on_selection_changed(self):
        """Track selected member when selection changes"""
        try:
            selected_row = self.members_table.currentRow()
            if selected_row >= 0:
                self.selected_member_id = self.members_table.item(selected_row, 0).text()
            else:
                self.selected_member_id = None
        except Exception as e:
            print(f"[ERROR] Selection change error: {e}")
            self.selected_member_id = None
    
    def clear_selection(self, event):
        """Clear table selection when clicking empty space"""
        try:
            if self.members_table:
                self.members_table.clearSelection()
                self.selected_member_id = None
            if hasattr(self, "search_input"):
                self.search_input.clearFocus()
            if hasattr(self, "status_combo"):
                self.status_combo.clearFocus()
        except Exception as e:
            print(f"[WARN] clear_selection error: {e}")
        QWidget.mousePressEvent(self.centralWidget(), event)
    
    def handle_header_click(self, logical_index):
        """Handle column header click for sorting"""
        try:
            if self.sort_column == logical_index:
                self.sort_order = Qt.SortOrder.DescendingOrder if self.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            else:
                self.sort_column = logical_index
                self.sort_order = Qt.SortOrder.AscendingOrder
            
            self.filter_members()
        except Exception as e:
            print(f"[ERROR] Header click error: {e}")
            QMessageBox.warning(self, "Error", "Failed to sort table")

    def load_members_from_database(self):
        """Load all members from database"""
        if not self.db or not self.db.connection:
            print("[WARNING] No database connection")
            QMessageBox.warning(self, "Database Error", "Not connected to database.")
            return
        
        try:
            query = "SELECT * FROM members ORDER BY member_id"
            self.all_members = self.db.fetch_all(query)
            
            if self.all_members:
                print(f"[OK] Loaded {len(self.all_members)} members")
                self.filter_members()
            else:
                print("[WARNING] No members found")
                self.members_table.setRowCount(0)
                
        except Exception as e:
            print(f"[ERROR] Failed to load members: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to load members:\n{str(e)}")
    
    def display_members(self, members):
        """Display members in the table"""
        try:
            self.members_table.setRowCount(len(members))
            
            for row, member in enumerate(members):
                # Member ID
                item = QTableWidgetItem(str(member['member_id']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 0, item)
                
                # Full Name
                item = QTableWidgetItem(str(member['full_name']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 1, item)
                
                # Email
                item = QTableWidgetItem(str(member['email']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 2, item)
                
                # Mobile Number
                item = QTableWidgetItem(str(member['mobile_number']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 3, item)
                
                # Status with color
                item = QTableWidgetItem(str(member['status']))
                item.setFont(QFont("Montserrat", 10))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                if member['status'] == 'Active':
                    item.setForeground(QColor("#228C3A"))
                else:
                    item.setForeground(QColor("#DC3545"))
                self.members_table.setItem(row, 4, item)
                
                # Borrowed Books
                item = QTableWidgetItem(str(member['borrowed_books']))
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 5, item)
                
                # Added At
                added_at = str(member['added_at']) if member['added_at'] else ""
                item = QTableWidgetItem(added_at)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 6, item)
                
                # Updated At
                updated_at = str(member['updated_at']) if member['updated_at'] else ""
                item = QTableWidgetItem(updated_at)
                item.setFont(QFont("Montserrat", 10))
                item.setForeground(QColor("#000000"))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(row, 7, item)
        except Exception as e:
            print(f"[ERROR] Display members error: {e}")
            import traceback
            traceback.print_exc()
    
    def filter_members(self):
        """Filter members based on search and status selection"""
        try:
            if not self.all_members:
                return
            
            search_text = self.search_input.text().lower().strip()
            status = self.status_combo.currentText()
            
            filtered_members = []
            
            for member in self.all_members:
                if status != "All" and member['status'] != status:
                    continue
                
                if search_text:
                    if not (search_text in str(member['member_id']).lower() or
                            search_text in str(member['full_name']).lower() or
                            search_text in str(member['email']).lower() or
                            search_text in str(member['mobile_number']).lower()):
                        continue
                
                filtered_members.append(member)
            
            # Apply sorting
            if self.sort_column is not None and filtered_members:
                column_names = ['member_id', 'full_name', 'email', 'mobile_number', 'status', 'borrowed_books', 'added_at', 'updated_at']
                if self.sort_column < len(column_names):
                    sort_key = column_names[self.sort_column]
                    filtered_members.sort(
                        key=lambda x: str(x.get(sort_key, '')).lower(),
                        reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
                    )
            
            self.display_members(filtered_members)
            print(f"[INFO] Filtered to {len(filtered_members)} members")
        except Exception as e:
            print(f"[ERROR] Filter members error: {e}")
            import traceback
            traceback.print_exc()
    
    def add_member(self):
        """Open add member dialog"""
        try:
            dialog = AddMemberDialog(self, self.db, self.load_members_from_database)
            dialog.exec()
        except Exception as e:
            print(f"[ERROR] Add member error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", "Failed to open add member dialog")
    
    def view_member(self):
        """View selected member"""
        try:
            if not self.selected_member_id:
                QMessageBox.warning(self, "No Selection", "Please select a member to view")
                return
            
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            
            if member_data:
                dialog = ViewMemberDialog(self, member_data)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Member not found in database")
                self.load_members_from_database()
        except Exception as e:
            print(f"[ERROR] View member error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to view member:\n{str(e)}")

    def update_member(self):
        """Update selected member"""
        try:
            if not self.selected_member_id:
                QMessageBox.warning(self, "No Selection", "Please select a member to update")
                return
            
            query = "SELECT * FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            
            if member_data:
                dialog = UpdateMemberDialog(self, self.db, member_data, self.load_members_from_database)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Member not found in database")
                self.load_members_from_database()
        except Exception as e:
            print(f"[ERROR] Update member error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to update member:\n{str(e)}")
    
    def delete_member(self):
        """Delete selected member"""
        try:
            if not self.selected_member_id:
                QMessageBox.warning(self, "No Selection", "Please select a member to delete")
                return
            
            query = "SELECT full_name FROM members WHERE member_id = %s"
            member_data = self.db.fetch_one(query, (self.selected_member_id,))
            
            if not member_data:
                QMessageBox.warning(self, "Error", "Member not found in database")
                self.load_members_from_database()
                return
            
            member_name = member_data['full_name']
            
            dialog = ConfirmDeleteMemberDialog(self, member_name)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                query = "DELETE FROM members WHERE member_id = %s"
                if self.db.execute_query(query, (self.selected_member_id,)):
                    QMessageBox.information(self, "Success", f"Member '{member_name}' deleted successfully!")
                    self.selected_member_id = None
                    self.load_members_from_database()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete member from database")
        except Exception as e:
            print(f"[ERROR] Delete member error: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to delete member:\n{str(e)}")
    
    def go_back_to_dashboard(self):
        """Go back to dashboard"""
        try:
            self.close()
        except Exception as e:
            print(f"[ERROR] Go back error: {e}")
    
    def show_fullscreen(self):
        """Show window maximized"""
        try:
            self.setWindowState(Qt.WindowState.WindowMaximized)
            self.showMaximized()
        except Exception as e:
            print(f"[ERROR] Show fullscreen error: {e}")
    
    def closeEvent(self, event):
        """Handle window close"""
        try:
            event.accept()
        except Exception as e:
            print(f"[ERROR] Close event error: {e}")
            event.accept()