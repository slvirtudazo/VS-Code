# config.py

class AppConfig:
    """Application configuration constants"""
    
    # Window dimensions based on 1920x1080 display
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    WINDOW_TITLE = "Curatel - Library Management System"
    
    # Color scheme with exact specifications from design
    COLORS = {
        # Dialog colors
        'primary_dark': '#3C2A21',          # Dialog header (100% opacity)
        'primary_light': '#8B7E66',         # Dialog body (80% opacity applied in stylesheets)
        'secondary': '#C4A680',             # Sign Up button (100% opacity)
        
        # Button colors
        'button_primary': '#B8956A',   # Add/Search buttons (50% opacity)
        'button_hover': '#A8855A',    # Hover state for primary buttons
        
        # Text colors
        'text_dark': '#000000',        # Input text color (pure black)
        'text_white': '#FFFFFF',       # Light text for dark backgrounds
        
        # Background colors
        'background_light': '#C9B8A8',       # Main background
        'background_table': '#E8DCC8',
        
        # Border color
        'border_color': '#8B7E66',
    }
    
    # database
    # Database connection settings
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'db_library'
    }
    
    @staticmethod
    def get_input_style():
        """Returns stylesheet for input fields with pure black text"""
        return """
            QLineEdit {
                border: none;
                border-radius: 20px;
                padding: 15px 20px;
                font-family: Montserrat;
                font-size: 13px;
                color: #000000;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                background-color: #FFFFFF;
                color: #000000;
            }
            QLineEdit::placeholder {
                color: #D0D0D0;
            }
        """
    
    @staticmethod
    def get_button_style(button_type='primary'):
        """Returns stylesheet for buttons based on type"""
        if button_type == 'signup':
            return """
                QPushButton {
                    background-color: #BDA984;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-family: 'Montserrat';
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #A89570;
                }
                QPushButton:pressed {
                    background-color: #8B7E66;
                }
            """
        else:  # primary
            return """
                QPushButton {
                    background-color: rgba(74, 74, 50, 0.5);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-family: 'Montserrat';
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(107, 107, 74, 0.6);
                }
                QPushButton:pressed {
                    background-color: rgba(107, 107, 74, 0.8);
                }
            """