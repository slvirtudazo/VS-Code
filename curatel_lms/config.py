# curatel_lms/config.py

"""
Application configuration module.
Centralizes all system constants, colors, and database settings.
"""

class AppConfig:
    """Application-wide configuration constants."""
    
    # Window settings
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    WINDOW_TITLE = "Curatel - Library Management System"
    
    # Color palette
    COLORS = {
        'primary_dark': '#3C2A21',
        'primary_light': '#8B7E66',
        'secondary': '#C4A680',
        'button_primary': '#B8956A',
        'button_hover': '#A8855A',
        'text_dark': '#000000',
        'text_white': '#FFFFFF',
        'background_light': '#C9B8A8',
        'background_table': '#E8DCC8',
        'border_color': '#8B7E66',
    }
    
    # Database credentials
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'db_library'
    }