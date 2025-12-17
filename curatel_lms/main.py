# curatel_lms/main.py

# Starts the application and initializes the GUI, database connection, and fonts

import sys
import os
from typing import List

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check MySQL dependency
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

# Base project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# List of required font files
REQUIRED_FONTS = [
    "Montserrat-Regular.ttf",
    "Montserrat-Bold.ttf",
    "PlayfairDisplay-Regular.ttf",
    "PlayfairDisplay-Bold.ttf"
]

def load_fonts() -> bool:
    # Load custom fonts; return success status
    fonts_dir = os.path.join(BASE_DIR, "fonts")
    all_loaded = True
    
    for font_file in REQUIRED_FONTS:
        font_path = os.path.join(fonts_dir, font_file)
        
        # Skip if font file missing
        if not os.path.exists(font_path):
            print(f"[WARNING] Font missing: {font_file}")
            all_loaded = False
            continue
        
        # Add font to app
        if QFontDatabase.addApplicationFont(font_path) == -1:
            print(f"[ERROR] Failed to load font: {font_file}")
            all_loaded = False
        else:
            print(f"[OK] Font loaded: {font_file}")
    
    # Show font load summary
    if all_loaded:
        print("[OK] All fonts loaded successfully")
    else:
        print("[ERROR] Some fonts missing, using system defaults")
    
    return all_loaded

def connect_database() -> Database:
    # Connect to MySQL DB; return Database instance
    db = Database()
    
    if db.connect():
        print(f"[OK] Database ready: {db.database}")
    else:
        print("[WARNING] Database connection failed")
        print("Check: MySQL server running, database exists, credentials correct")
    
    return db

def main() -> None:
    # Start app: init Qt, load fonts, connect DB, show login
    try:
        # Create Qt app
        app = QApplication(sys.argv)
        app.setApplicationName("Curatel Library Management System")
        app.setOrganizationName("Curatel")
        
        print("[INFO] Application initialized")
        
        app.setStyleSheet("""
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
            }
            QMessageBox QPushButton:hover {
                background-color: #7A6D55;
            }
        """)

        # Load fonts
        load_fonts()
        
        # Connect DB
        db = connect_database()
        
        if not db.connection:
            print("[WARNING] Starting without database connection")
        
        # Show login screen
        print("[INFO] Launching login screen")
        login_window = LoginScreen(db)
        login_window.show()
        print("[OK] Application started successfully")
        
        # Run event loop
        sys.exit(app.exec())
    
    except Exception as e:
        # Log and exit on crash
        print(f"[CRITICAL] Application error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()