# curatel_lms/main.py

"""
Application entry point.
Initializes the library management system with GUI, database, and custom fonts.
"""

import sys
import os
from typing import List

# Configure import paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Verify required dependencies
try:
    import mysql.connector
    print("[OK] MySQL connector available")
except ImportError:
    print("[ERROR] mysql-connector-python not installed")
    print("Install: pip install mysql-connector-python")
    sys.exit(1)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from curatel_lms.ui.login_screen import LoginScreen
from curatel_lms.database import Database

# Application base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Font configuration
REQUIRED_FONTS = [
    "Montserrat-Regular.ttf",
    "Montserrat-Bold.ttf",
    "PlayfairDisplay-Regular.ttf",
    "PlayfairDisplay-Bold.ttf"
]

def load_fonts() -> bool:
    """
    Load custom fonts from fonts directory.
    
    Returns:
        bool: True if all fonts loaded successfully, False otherwise
    """
    fonts_dir = os.path.join(BASE_DIR, "fonts")
    all_loaded = True
    
    for font_file in REQUIRED_FONTS:
        font_path = os.path.join(fonts_dir, font_file)
        
        # Check if font file exists
        if not os.path.exists(font_path):
            print(f"[WARNING] Font missing: {font_file}")
            all_loaded = False
            continue
        
        # Load font into application
        if QFontDatabase.addApplicationFont(font_path) == -1:
            print(f"[ERROR] Failed to load font: {font_file}")
            all_loaded = False
        else:
            print(f"[OK] Font loaded: {font_file}")
    
    # Print summary
    if all_loaded:
        print("✓ All fonts loaded successfully")
    else:
        print("⚠ Some fonts missing, using system defaults")
    
    return all_loaded

def connect_database() -> Database:
    """
    Initialize and connect to MySQL database.
    
    Returns:
        Database: Database instance (connected or not)
    """
    db = Database()
    
    if db.connect():
        print(f"[OK] Database ready: {db.database}")
    else:
        print("[WARNING] Database connection failed")
        print("Check: MySQL server running, database exists, credentials correct")
    
    return db

def main() -> None:
    """
    Main application entry point.
    Initializes Qt application, loads resources, and displays login screen.
    """
    try:
        # Initialize Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Curatel Library Management System")
        app.setOrganizationName("Curatel")
        
        print("[INFO] Application initialized")
        
        # Load custom fonts
        load_fonts()
        
        # Connect to database
        db = connect_database()
        
        if not db.connection:
            print("[WARNING] Starting without database connection")
        
        # Create and show login window
        print("[INFO] Launching login screen")
        login_window = LoginScreen(db)
        login_window.show()
        print("[OK] Application started successfully")
        
        # Start Qt event loop
        sys.exit(app.exec())
    
    except Exception as e:
        # Handle critical errors
        print(f"[CRITICAL] Application error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()