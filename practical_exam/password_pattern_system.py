import random
import csv
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QTextEdit, QTabWidget, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase

class PasswordPatternSystem:
    """Handles password generation and binary pattern analysis with discrete math"""
    
    def __init__(self):
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.digits = '0123456789'
    
    # Password Generator Module
    
    def calculate_total_passwords(self):
        """
        Calculates total possible passwords using counting principle
        Format: 1 uppercase + 3 unique digits + 1 lowercase
        Result: 26 × P(10,3) × 26 = 486,720
        """
        return 26 * 10 * 9 * 8 * 26  # 486,720
    
    def generate_password(self):
        """Creates one password: uppercase + 3 unique digits + lowercase"""
        upper = random.choice(self.uppercase)
        three_digits = ''.join(random.sample(self.digits, 3))
        lower = random.choice(self.lowercase)
        return upper + three_digits + lower
    
    def generate_multiple_passwords(self, count):
        """Creates multiple unique passwords (between 1-20)"""
        if not 1 <= count <= 20:
            raise ValueError("Password count must be between 1 and 20")
        
        passwords = set()
        attempts = 0
        max_attempts = count * 100
        
        while len(passwords) < count and attempts < max_attempts:
            passwords.add(self.generate_password())
            attempts += 1
        
        return list(passwords)
    
    # Binary Pattern Analyzer Module
    
    def count_valid_binary_strings(self, n):
        """
        Counts binary strings without consecutive 1s
        Uses recurrence: S(n) = S(n-1) + S(n-2) with S(0)=1, S(1)=2
        Runs in O(n) time via dynamic programming
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return 1
        if n == 1:
            return 2
        
        # Store computed values in array
        dp = [0] * (n + 1)
        dp[0], dp[1] = 1, 2
        
        for i in range(2, n + 1):
            dp[i] = dp[i-1] + dp[i-2]
        
        return dp[n]
    
    def generate_valid_binary_strings(self, n):
        """Builds all valid binary strings through recursive backtracking"""
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return ['']
        
        valid = []
        
        def backtrack(s):
            """Recursively constructs valid strings"""
            if len(s) == n:
                valid.append(s)
                return
            
            # Can always add 0
            backtrack(s + '0')
            
            # Add 1 only if last char isn't 1
            if not s or s[-1] == '0':
                backtrack(s + '1')
        
        backtrack('')
        return valid
    
    # File Export Functions
    
    def export_passwords_to_txt(self, passwords, filename='passwords.txt'):
        """Saves passwords to text file"""
        try:
            with open(filename, 'w') as f:
                f.write("Generated Passwords:\n\n")
                for i, pwd in enumerate(passwords, 1):
                    f.write(f"{i}. {pwd}\n")
                f.write(f"\nTotal: {len(passwords)}\n")
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def export_binary_strings_to_csv(self, n, strings, count, filename='binary_strings.csv'):
        """Saves binary analysis to CSV file"""
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Analyzed Binary Pattern:'])
                writer.writerow([])
                writer.writerow([f'Results for n = {n}:'])
                writer.writerow([])
                writer.writerow(['Valid strings:'])
                writer.writerow([])
                
                if strings:
                    for i, s in enumerate(strings, 1):
                        writer.writerow([f'{i}. {s if s else "(empty)"}'])
                
                writer.writerow([])
                writer.writerow([f'Total: {count}'])
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False

# Console Interface

def console_app():
    """Text-based user interface"""
    system = PasswordPatternSystem()
    
    print("\nPASSWORD GENERATOR AND PATTERN ANALYZER")
    
    while True:
        print("\nMain Menu:")
        print("1. Password Generator")
        print("2. Pattern Analyzer")
        print("3. Exit Program")
        
        try:
            choice = input("\nChoice (1-3): ").strip()
            
            if choice == '1':
                # Password Generator
                print("\nPASSWORD GENERATOR")
                print(f"Total possible combinations: {system.calculate_total_passwords():,}")
                
                while True:
                    try:
                        count = int(input("Generate how many passwords (1-20): "))
                        if 1 <= count <= 20:
                            break
                        print("Enter a number between 1 and 20.")
                    except ValueError:
                        print("Invalid input. Enter a number.")
                
                passwords = system.generate_multiple_passwords(count)
                
                print(f"\n{len(passwords)} passwords generated:")
                for i, pwd in enumerate(passwords, 1):
                    print(f"{i:2}. {pwd}")
                
                # Offer export option
                if input("\nExport to file? (Y/N): ").lower() == 'y':
                    fname = input("Enter filename (default: passwords.txt): ").strip()
                    fname = fname if fname else 'passwords.txt'
                    if system.export_passwords_to_txt(passwords, fname):
                        print(f"Exported to '{fname}'")
                
            elif choice == '2':
                # Pattern Analyzer
                print("\nPATTERN ANALYZER")
                print("Count binary strings without consecutive 1s")
                
                while True:
                    try:
                        n = int(input("Enter length n (≥ 0): "))
                        if n >= 0:
                            break
                        print("Enter a non-negative integer.")
                    except ValueError:
                        print("Invalid input. Enter an integer.")
                
                count = system.count_valid_binary_strings(n)
                print(f"\nResults for n = {n}:")
                
                # List strings if small enough
                if n <= 5:
                    strings = system.generate_valid_binary_strings(n)
                    print("\nValid strings:")
                    for i, s in enumerate(strings, 1):
                        print(f"{i:2}. {s if s else '(empty)'}")
                    print(f"\nValid strings: {count}")
                    
                    # Offer export option
                    if input("\nExport to CSV? (Y/N): ").lower() == 'y':
                        fname = input("Enter filename (default: binary_strings.csv): ").strip()
                        fname = fname if fname else 'binary_strings.csv'
                        if system.export_binary_strings_to_csv(n, strings, count, fname):
                            print(f"Exported to '{fname}'")
                else:
                    print("(List not shown for n > 5)")
            
            elif choice == '3':
                print("\nThank you! Exiting the program...\n")
                sys.exit(0)
            else:
                print("Invalid choice. Enter 1-3.")
        
        except KeyboardInterrupt:
            print("\n\nExiting the program...\n")
            break
        except Exception as e:
            print(f"\nError: {e}")

# Graphical User Interface

class PasswordPatternGUI(QMainWindow):
    """Visual interface for password and pattern operations"""
    
    def __init__(self):
        super().__init__()
        self.system = PasswordPatternSystem()
        self.current_passwords = None
        self.current_binary_data = None
        
        self.setWindowTitle("Password Generator & Pattern Analyzer")
        self.setGeometry(100, 100, 900, 700)
        
        # Set application stylesheet with pastel beige and deep maroon theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5E6D3;
            }
            QWidget {
                background-color: #F5E6D3;
                color: #4A0E0E;
            }
            QTabWidget::pane {
                border: 2px solid #8B4513;
                background-color: #F5E6D3;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #E8D4BC;
                color: #4A0E0E;
                padding: 12px 24px;
                margin: 2px;
                border: 2px solid #8B4513;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Montserrat';
                font-size: 11pt;
                font-weight: normal;
            }
            QTabBar::tab:selected {
                background-color: #F5E6D3;
                color: #4A0E0E;
                font-weight: bold;
            }
            QLabel {
                color: #4A0E0E;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #8B4513;
                border-radius: 6px;
                padding: 8px;
                color: #4A0E0E;
                font-family: 'Montserrat';
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #4A0E0E;
            }
            QTextEdit {
                background-color: #FFFFFF;
                border: 2px solid #8B4513;
                border-radius: 15px;
                padding: 15px;
                color: #4A0E0E;
                font-family: 'Tahoma';
                font-size: 10pt;
            }
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-family: 'Montserrat';
                font-size: 11pt;
                font-weight: bold;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton:pressed {
                padding: 11px 23px 9px 25px;
            }
        """)
        
        # Center window on screen
        self.center_on_screen()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_password_tab()
        self.create_pattern_tab()
    
    def center_on_screen(self):
        """Centers the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center = screen.center()
        window.moveCenter(center)
        self.move(window.topLeft())
    
    def create_password_tab(self):
        """Sets up password generator interface"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title section
        title = QLabel("Password Generator")
        title.setFont(QFont('Montserrat', 15, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4A0E0E; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Show total combinations
        total = self.system.calculate_total_passwords()
        info = QLabel(f"Total possible combinations: {total:,}")
        info.setFont(QFont('Montserrat', 11, QFont.Weight.Normal))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #4A0E0E; margin-bottom: 20px;")
        layout.addWidget(info)
        
        # Input controls
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        
        input_layout.addStretch()
        
        label = QLabel("Count (1-20):")
        label.setFont(QFont('Montserrat', 11, QFont.Weight.Normal))
        input_layout.addWidget(label)
        
        self.pwd_count_input = QLineEdit()
        self.pwd_count_input.setMaximumWidth(120)
        input_layout.addWidget(self.pwd_count_input)
        
        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8D4B8;
                color: #2D5016;
            }
            QPushButton:hover {
                background-color: #A8C4A8;
            }
        """)
        generate_btn.clicked.connect(self.generate_passwords)
        input_layout.addWidget(generate_btn)
        
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8D4E4;
                color: #1B4965;
            }
            QPushButton:hover {
                background-color: #A8C4D4;
            }
        """)
        export_btn.clicked.connect(self.export_passwords)
        input_layout.addWidget(export_btn)
        
        input_layout.addStretch()
        layout.addLayout(input_layout)
        
        # Results display
        self.pwd_output = QTextEdit()
        self.pwd_output.setReadOnly(True)
        layout.addWidget(self.pwd_output)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Password Generator")
    
    def create_pattern_tab(self):
        """Sets up pattern analyzer interface"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title section
        title = QLabel("Binary Pattern Analyzer")
        title.setFont(QFont('Montserrat', 15, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4A0E0E; margin-bottom: 10px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Count strings without consecutive 1s")
        subtitle.setFont(QFont('Montserrat', 11, QFont.Weight.Normal))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #4A0E0E; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Input controls
        input_layout = QHBoxLayout()
        input_layout.setSpacing(15)
        
        input_layout.addStretch()
        
        label = QLabel("Length n:")
        label.setFont(QFont('Montserrat', 11, QFont.Weight.Normal))
        input_layout.addWidget(label)
        
        self.n_input = QLineEdit()
        self.n_input.setMaximumWidth(120)
        input_layout.addWidget(self.n_input)
        
        analyze_btn = QPushButton("Analyze")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8D4B8;
                color: #2D5016;
            }
            QPushButton:hover {
                background-color: #A8C4A8;
            }
        """)
        analyze_btn.clicked.connect(self.analyze_pattern)
        input_layout.addWidget(analyze_btn)
        
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8D4E4;
                color: #1B4965;
            }
            QPushButton:hover {
                background-color: #A8C4D4;
            }
        """)
        export_btn.clicked.connect(self.export_binary)
        input_layout.addWidget(export_btn)
        
        input_layout.addStretch()
        layout.addLayout(input_layout)
        
        # Results display
        self.pattern_output = QTextEdit()
        self.pattern_output.setReadOnly(True)
        layout.addWidget(self.pattern_output)
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Pattern Analyzer")
    
    def generate_passwords(self):
        """Processes password generation request"""
        try:
            count = int(self.pwd_count_input.text())
            if not 1 <= count <= 20:
                QMessageBox.critical(self, "Error", "Enter a number between 1 and 20")
                return
            
            passwords = self.system.generate_multiple_passwords(count)
            
            output = "Generated Passwords:\n\n"
            for i, pwd in enumerate(passwords, 1):
                output += f"{i}. {pwd}\n"
            output += f"\nTotal: {len(passwords)}"
            
            self.pwd_output.setPlainText(output)
            self.current_passwords = passwords
            
        except ValueError:
            QMessageBox.critical(self, "Error", "Enter a valid number")
    
    def export_passwords(self):
        """Saves passwords to chosen file"""
        if not self.current_passwords:
            QMessageBox.warning(self, "Warning", "Generate passwords first")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save File", "passwords.txt", "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            if self.system.export_passwords_to_txt(self.current_passwords, filename):
                QMessageBox.information(self, "Success", f"Exported to '{filename}'")
    
    def analyze_pattern(self):
        """Processes pattern analysis request"""
        try:
            n = int(self.n_input.text())
            if n < 0:
                QMessageBox.critical(self, "Error", "Enter a non-negative integer")
                return
            
            count = self.system.count_valid_binary_strings(n)
            
            output = "Analyzed Binary Pattern:\n\n"
            output += f"Results for n = {n}:\n\n"
            output += "Valid strings:\n\n"
            
            if n <= 5:
                strings = self.system.generate_valid_binary_strings(n)
                for i, s in enumerate(strings, 1):
                    output += f"{i}. {s if s else '(empty)'}\n"
                self.current_binary_data = (n, strings, count)
            else:
                output += "(List not shown for n > 5)\n"
                self.current_binary_data = (n, None, count)
            
            output += f"\nTotal: {count}"
            
            self.pattern_output.setPlainText(output)
            
        except ValueError:
            QMessageBox.critical(self, "Error", "Enter a valid integer")
    
    def export_binary(self):
        """Saves binary analysis to chosen file"""
        if not self.current_binary_data:
            QMessageBox.warning(self, "Warning", "Analyze a pattern first")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save File", "binary_strings.csv", "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            n, strings, count = self.current_binary_data
            if self.system.export_binary_strings_to_csv(n, strings, count, filename):
                QMessageBox.information(self, "Success", f"Exported to '{filename}'")

def run_gui():
    """Opens the graphical interface"""
    app = QApplication(sys.argv)
    window = PasswordPatternGUI()
    window.show()
    
    # Bring window to front
    window.raise_()
    window.activateWindow()
    
    sys.exit(app.exec())

# Main Entry Point

if __name__ == "__main__":
    print("\nSelect Interface:")
    print("1. Console Mode")
    print("2. GUI Mode")
    print("3. Exit Program")
    
    while True:
        choice = input("\nChoice (1-3): ").strip()
        if choice == '1':
            console_app()
            break
        elif choice == '2':
            run_gui()
            break
        elif choice == '3':
            print("\nThank you! Exiting the program...\n")
            sys.exit(0)
        else:
            print("Invalid choice. Enter 1-3.")