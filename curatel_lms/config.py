# curatel_lms/config.py

# Central app config: UI dims, colors, styles, DB settings

class AppConfig:
    # App-wide constants for UI, colors, styles, and settings

    # WINDOW CONFIGURATION
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    WINDOW_TITLE = "Curatel - Library Management System"
    
    # DIALOG DIMENSIONS
    DIALOG_WIDTH = 800
    DIALOG_HEIGHT = 700
    DIALOG_HEIGHT_COMPACT = 680     # Shorter dialogs
    DIALOG_HEIGHT_EXTENDED = 750    # View dialogs with more info
    
    # Form container dimensions
    FORM_WIDTH = 600
    FORM_HEIGHT = 450
    FORM_HEIGHT_COMPACT = 390       # Fewer fields
    FORM_HEIGHT_MEDIUM = 440        # Medium forms
    FORM_HEIGHT_LARGE = 500         # Larger forms
    
    # Input field dimensions
    FIELD_WIDTH = 540
    FIELD_HEIGHT = 50
    
    # BUTTON DIMENSIONS
    BUTTON_WIDTH_STANDARD = 120
    BUTTON_WIDTH_MEDIUM = 140
    BUTTON_WIDTH_WIDE = 150
    BUTTON_WIDTH_EXTRA_WIDE = 180
    BUTTON_HEIGHT = 40
    BUTTON_HEIGHT_LARGE = 60  # Dialog action buttons
    
    # Search bar dimensions
    SEARCH_HEIGHT = 40

    # TABLE DIMENSIONS
    TABLE_HEIGHT = 400
    TABLE_WIDTH = 685
    
    # COLOR PALETTE
    COLORS = {
        # Primary brand colors
        'primary_dark': '#3C2A21',          # Headers
        'primary_light': '#8B7E66',         # Main UI
        'secondary': '#C4A680',             # Accent
        
        # Button colors
        'button_primary': '#B8956A',
        'button_hover': '#A8855A',
        'button_green': '#8BAE66',          # Success
        'button_green_hover': '#A3B087',
        'button_red': '#AF3E3E',            # Delete/cancel
        'button_red_hover': '#CD5656',
        'button_gray': '#8B7E66',           # Standard
        'button_gray_hover': '#6B5E46',
        
        # Status colors
        'status_available': '#228C3A',      # Available/active
        'status_borrowed': '#FFA500',       # Borrowed/ongoing
        'status_returned': '#228C3A',       # Completed
        'status_overdue': '#DC3545',        # Overdue/inactive
        'status_active': '#228C3A',
        'status_inactive': '#DC3545',
        
        # Text colors
        'text_dark': '#000000',
        'text_white': '#FFFFFF',
        'text_gray': '#333333',
        
        # Backgrounds
        'bg_light': '#C9B8A8',
        'bg_table': '#E8DCC8',
        'bg_dialog': '#8B7E66',
        'bg_white': '#FFFFFF',
        
        # Borders
        'border_color': '#8B7E66',
        'border_dark': '#6B5E46',
    }
    
    # STYLE TEMPLATES
    STYLES = {
        # Input field
        'input': """
            QLineEdit {
                font-family: Montserrat;
                font-size: 13px;
                border: 2px solid #6B5E46;
                border-radius: 10px;
                padding: 8px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #6B5E46;
            }
        """,
        
        # Search input
        'search_input': """
            QLineEdit {
                border: 2px solid #6B5E46;
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
        """,
        
        # Combo box
        'combo': """
            QComboBox {
                font-family: Montserrat;
                font-size: 13px;
                border: 2px solid #6B5E46;
                border-radius: 10px;
                padding: 5px 10px;
                background-color: white;
                color: black;
            }
            QComboBox:focus {
                border: 2px solid #6B5E46;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #E0D6C8;
                border: 1px solid #8B7E66;
            }
        """,
        
        # Combo with dropdown arrow
        'combo_with_dropdown': """
            QComboBox {
                font-family: Montserrat;
                font-size: 13px;
                border: 1px solid #8B7E66;
                border-radius: 10px;
                padding: 5px 10px;
                background-color: white;
                color: black;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            QComboBox:focus {
                border: 2px solid #6B5E46;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #E0D6C8;
                border: 1px solid #8B7E66;
                outline: 0;
            }
        """,
        
        # Standard button
        'button': """
            QPushButton {
                background-color: #8B7E66;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #6B5E46;
            }
        """,
        
        # Table widget
        'table': """
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
        """,
        
        # Table with corner button
        'table_with_corner': """
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
        """,
        
        # Dialog form label
        'dialog_label': """
            font-family: Montserrat;
            font-size: 15px;
            color: white;
            border: none;
            background: transparent;
        """,
        
        # Dialog header
        'dialog_header': """
            background-color: #3C2A21;
            border: none;
        """,
        
        # Form container
        'form_container': """
            background: transparent;
            border: 3px solid white;
            border-radius: 30px;
        """,
        
        # Dialog header text
        'dialog_header_text': """
            font-family: Montserrat;
            font-size: 30px;
            font-weight: bold;
            letter-spacing: 3px;
            color: white;
        """,
        
        # Info field value
        'info_value': """
            font-family: Montserrat;
            font-size: 15px;
            color: white;
            border: none;
            background: transparent;
            text-decoration: underline;
        """,
    }
    
    # BUTTON STYLE BUILDERS
    @staticmethod
    def get_action_button_style(bg_color, hover_color):
        # Generate action button style (Save, Update, etc.)
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 15px;
                font-family: Montserrat;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """
    
    @staticmethod
    def get_green_button_style():
        # Green button for success actions
        return AppConfig.get_action_button_style(
            AppConfig.COLORS['button_green'],
            AppConfig.COLORS['button_green_hover']
        )
    
    @staticmethod
    def get_red_button_style():
        # Red button for delete/cancel
        return AppConfig.get_action_button_style(
            AppConfig.COLORS['button_red'],
            AppConfig.COLORS['button_red_hover']
        )
    
    # DATA CATEGORIES AND OPTIONS
    BOOK_CATEGORIES = [
        "All", "Adventure", "Art", "Biography", "Business",
        "Cooking", "Fantasy", "Fiction", "History", "Horror",
        "Mystery", "Non-Fiction", "Poetry", "Romance", "Science", "Technology"
    ]
    
    MEMBER_STATUSES = ["Active", "Inactive"]
    TRANSACTION_STATUSES = ["Borrowed", "Returned", "Overdue"]

    # TABLE COLUMN CONFIGURATION

    # Catalog Management
    CATALOG_TABLE = {
        'columns': ["Book ID", "Title", "Author", "ISBN", "Category", "Status", "Added At", "Updated At"],
        'widths': [80, 300, 180, 150, 140, 160, 200, 220],
        'keys': ['book_id', 'title', 'author', 'isbn', 'category', 'status', 'added_at', 'updated_at']
    }
    
    # Patron Management
    PATRON_TABLE = {
        'columns': ["Member ID", "Full Name", "Email", "Mobile Number", "Status", "Borrowed Books", "Added At", "Updated At"],
        'widths': [100, 200, 250, 180, 100, 140, 200, 200],
        'keys': ['member_id', 'full_name', 'email', 'mobile_number', 'status', 'borrowed_books', 'added_at', 'updated_at']
    }
    
    # Circulation Management
    CIRCULATION_TABLE = {
        'columns': ["Book ID", "Member ID", "Book Title", "Borrow Date", "Due Date", "Return Date", "Status", "Fine Amount", "Updated At"],
        'widths': [80, 90, 300, 180, 180, 180, 100, 120, 180],
        'keys': ['book_id', 'member_id', 'book_title', 'borrow_date', 'due_date', 'return_date', 'status', 'fine_amount', 'updated_at']
    }
    
    # DATABASE CONFIGURATION
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'db_library'
    }
    
    # QUERY CONSTANTS
    QUERIES = {
        # Member stats
        'total_members': "SELECT COUNT(*) as total FROM members",
        'active_members': "SELECT COUNT(*) as active FROM members WHERE status = 'Active'",
        'inactive_members': "SELECT COUNT(*) as inactive FROM members WHERE status = 'Inactive'",
        
        # Borrowing stats
        'borrowed_books': "SELECT COUNT(*) as borrowed FROM borrowed_books WHERE status = 'Borrowed'",
        'overdue_books': "SELECT COUNT(*) as overdue FROM borrowed_books WHERE status = 'Overdue'",
        'total_fines': "SELECT SUM(fine_amount) as total_fines FROM borrowed_books WHERE fine_amount > 0",
        
        # Top borrowers
        'top_borrowers': """
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
        """,
        
        # Popular books
        'popular_books': """
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
    }