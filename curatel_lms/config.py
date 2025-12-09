# curatel_lms/config.py

"""
Centralized application configuration.
Contains all system constants, UI dimensions, colors, and database settings.
"""

class AppConfig:
    """Application-wide configuration constants."""
    
    # Window Configuration
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    WINDOW_TITLE = "Curatel - Library Management System"
    
    # UI Dimensions
    DIALOG_WIDTH = 800
    DIALOG_HEIGHT = 700
    FORM_WIDTH = 600
    FORM_HEIGHT = 450
    FIELD_WIDTH = 540
    FIELD_HEIGHT = 50
    BUTTON_WIDTH = 120
    BUTTON_HEIGHT = 40
    SEARCH_HEIGHT = 40
    
    # Color Palette
    COLORS = {
        # Primary Colors
        'primary_dark': '#3C2A21',
        'primary_light': '#8B7E66',
        'secondary': '#C4A680',
        
        # Button Colors
        'button_primary': '#B8956A',
        'button_hover': '#A8855A',
        'button_green': '#8BAE66',
        'button_green_hover': '#A3B087',
        'button_red': '#AF3E3E',
        'button_red_hover': '#CD5656',
        'button_gray': '#8B7E66',
        'button_gray_hover': '#6B5E46',
        
        # Status Colors
        'status_available': '#228C3A',
        'status_borrowed': '#FFA500',
        'status_returned': '#228C3A',
        'status_overdue': '#DC3545',
        'status_active': '#228C3A',
        'status_inactive': '#DC3545',
        
        # Text Colors
        'text_dark': '#000000',
        'text_white': '#FFFFFF',
        'text_gray': '#333333',
        
        # Background Colors
        'bg_light': '#C9B8A8',
        'bg_table': '#E8DCC8',
        'bg_dialog': '#8B7E66',
        'bg_white': '#FFFFFF',
        
        # Border Colors
        'border_color': '#8B7E66',
        'border_dark': '#6B5E46',
    }
    
    # Database Configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'db_library'
    }
    
    # UI Style Templates
    STYLES = {
        'input': """
            QLineEdit {
                font-family: Montserrat;
                font-size: 13px;
                border: 1px solid #8B7E66;
                border-radius: 10px;
                padding: 8px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #6B5E46;
            }
        """,
        
        'combo': """
            QComboBox {
                font-family: Montserrat;
                font-size: 13px;
                border: 1px solid #8B7E66;
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
    }
    
    # Book Categories
    BOOK_CATEGORIES = [
        "All", "Adventure", "Art", "Biography", "Business",
        "Cooking", "Fantasy", "Fiction", "History", "Horror",
        "Mystery", "Non-Fiction", "Poetry", "Romance", "Science", "Technology"
    ]
    
    # Member Status Options
    MEMBER_STATUSES = ["Active", "Inactive"]
    
    # Transaction Status Options
    TRANSACTION_STATUSES = ["Borrowed", "Returned", "Overdue"]