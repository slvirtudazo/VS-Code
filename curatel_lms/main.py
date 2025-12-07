# curatel_lms/main.py

"""
Main application entry point.
Initializes the library management system with GUI and database.
"""

import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_fonts():
    """
    Load custom fonts from fonts directory.
    Returns: True if all fonts loaded successfully.
    """
    fonts_dir = os.path.join(BASE_DIR, "fonts")
    font_files = [
        "Montserrat-Regular.ttf",
        "Montserrat-Bold.ttf",
        "PlayfairDisplay-Regular.ttf",
        "PlayfairDisplay-Bold.ttf"
    ]
    
    all_loaded = True
    for font_file in font_files:
        font_path = os.path.join(fonts_dir, font_file)
        
        if not os.path.exists(font_path):
            print(f"[WARNING] Missing: {font_file}")
            all_loaded = False
            continue
        
        if QFontDatabase.addApplicationFont(font_path) == -1:
            print(f"[ERROR] Failed to load: {font_file}")
            all_loaded = False
        else:
            print(f"[OK] Loaded: {font_file}")
    
    if all_loaded:
        print("✓ All fonts loaded")
    else:
        print("⚠ Some fonts missing, using system fonts")
    
    return all_loaded

def connect_database():
    """
    Connect to MySQL database.
    Returns: Database object (connected or not).
    """
    db = Database()
    
    if db.connect():
        print(f"[OK] Connected to: {db.database}")
    else:
        print("[WARNING] Database connection failed")
        print("Check: MySQL server running, database exists, credentials correct")
    
    return db

def main():
    """Main application entry point."""
    try:
        # Initialize Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Curatel Library Management System")
        app.setOrganizationName("Curatel")
        
        # Load fonts
        load_fonts()
        
        # Connect database
        db = connect_database()
        
        if not db.connection:
            print("[WARNING] Starting without database")
        
        # Show login window
        print("[INFO] Starting login screen")
        window = LoginScreen(db)
        window.show()
        print("[OK] Application started")
        
        # Start event loop
        sys.exit(app.exec())
    
    except Exception as e:
        print(f"[CRITICAL] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()