# curatel_lms/main.py

import sys
import os

# Add parent directory to path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import mysql.connector
    print("[OK] MySQL connector available")
except ImportError:
    print("[ERROR] mysql-connector-python not installed!")
    print("Please install it using: pip install mysql-connector-python")
    sys.exit(1)

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFontDatabase
from curatel_lms.ui.login_screen import LoginScreen
from curatel_lms.database import Database

# Get base directory for relative paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_fonts():
    """
    Load custom fonts from the fonts directory
    Returns: True if all fonts loaded successfully, False otherwise
    """
    fonts_dir = os.path.join(BASE_DIR, "fonts")
    
    # List of required font files
    font_files = [
        "Montserrat-Regular.ttf",
        "Montserrat-Bold.ttf",
        "PlayfairDisplay-Regular.ttf",
        "PlayfairDisplay-Bold.ttf"
    ]
    
    all_loaded = True
    
    for font_file in font_files:
        font_path = os.path.join(fonts_dir, font_file)
        
        # Check if font file exists
        if not os.path.exists(font_path):
            print(f"[WARNING] Missing font: {font_path}")
            all_loaded = False
            continue
        
        # Try to load the font
        result = QFontDatabase.addApplicationFont(font_path)
        if result == -1:
            print(f"[ERROR] Failed to load font: {font_path}")
            all_loaded = False
        else:
            print(f"[OK] Loaded font: {font_file}")
    
    if all_loaded:
        print("✓ All fonts loaded successfully")
    else:
        print("⚠ Some fonts failed to load, using system fonts as fallback")
    
    families = QFontDatabase.families()
    custom_fonts = [f for f in families if 'Montserrat' in f or 'Playfair' in f]
    if custom_fonts:
        print(f"[OK] Custom fonts registered: {custom_fonts}")
    else:
        print("[WARNING] Custom fonts not found in font database")
    
    return all_loaded

def connect_database():
    """
    Attempt to connect to the MySQL database
    Returns: Database object (connected or not)
    """
    db = Database()
    
    if db.connect():
        print("[OK] Database connected successfully")
        print(f"[INFO] Connected to database: {db.database}")
        return db
    else:
        print("[ERROR] Database connection failed")
        print("[INFO] Please check:")
        print("  - MySQL server is running")
        print("  - Database 'db_library' exists")
        print("  - Credentials are correct (user: root, password: empty)")
        return db

def main():
    """Main application entry point"""
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("Curatel Library Management System")
        app.setOrganizationName("Curatel")
        
        # Load custom fonts (continue even if some fail)
        load_fonts()
        
        # Connect to database
        db = connect_database()
        
        # Check if database connection was successful
        if not db.connection:
            # Show warning but continue
            print("[WARNING] Starting application without database connection")
        
        print("[INFO] Creating LoginScreen window...")
        # Create and show login window
        window = LoginScreen(db)
        print("[INFO] Showing LoginScreen...")
        window.show()
        print("[INFO] Application started successfully")
        
        # Start application event loop
        sys.exit(app.exec())
    
    except Exception as e:
        print(f"[CRITICAL ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()