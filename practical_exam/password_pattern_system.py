import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import csv
import sys

class PasswordPatternSystem:
    """System for password generation and binary pattern analysis using discrete structures"""
    
    def __init__(self):
        self.uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.lowercase = 'abcdefghijklmnopqrstuvwxyz'
        self.digits = '0123456789'
    
    # PASSWORD GENERATOR MODULE
    
    def calculate_total_passwords(self):
        """
        Calculate total passwords using Fundamental Counting Principle
        Format: 1 uppercase + 3 unique digits + 1 lowercase
        Total = 26 × P(10,3) × 26 = 26 × 720 × 26 = 486,720
        """
        return 26 * 10 * 9 * 8 * 26  # 486,720
    
    def generate_password(self):
        """Generate single password: Uppercase + 3 unique digits + Lowercase"""
        upper = random.choice(self.uppercase)
        three_digits = ''.join(random.sample(self.digits, 3))
        lower = random.choice(self.lowercase)
        return upper + three_digits + lower
    
    def generate_multiple_passwords(self, count):
        """Generate 'count' unique passwords (1-20)"""
        if not 1 <= count <= 20:
            raise ValueError("Password count must be between 1 and 20")
        
        passwords = set()
        attempts = 0
        max_attempts = count * 100
        
        while len(passwords) < count and attempts < max_attempts:
            passwords.add(self.generate_password())
            attempts += 1
        
        return list(passwords)
    
    # BINARY PATTERN ANALYZER MODULE
    
    def count_valid_binary_strings(self, n):
        """
        Count binary strings of length n without consecutive 1s
        Recurrence: S(n) = S(n-1) + S(n-2), Base: S(0)=1, S(1)=2
        Uses dynamic programming for O(n) complexity
        """
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return 1
        if n == 1:
            return 2
        
        # DP array stores computed values
        dp = [0] * (n + 1)
        dp[0], dp[1] = 1, 2
        
        for i in range(2, n + 1):
            dp[i] = dp[i-1] + dp[i-2]
        
        return dp[n]
    
    def generate_valid_binary_strings(self, n):
        """Generate all valid binary strings using recursive backtracking"""
        if n < 0:
            raise ValueError("n must be non-negative")
        if n == 0:
            return ['']
        
        valid = []
        
        def backtrack(s):
            """Build valid strings recursively"""
            if len(s) == n:
                valid.append(s)
                return
            
            # Always append 0
            backtrack(s + '0')
            
            # Append 1 only if previous char is not 1
            if not s or s[-1] == '0':
                backtrack(s + '1')
        
        backtrack('')
        return valid
    
    # FILE EXPORT FUNCTIONS
    
    def export_passwords_to_txt(self, passwords, filename='passwords.txt'):
        """Export passwords to text file"""
        try:
            with open(filename, 'w') as f:
                f.write("Generated Passwords\n\n")
                for i, pwd in enumerate(passwords, 1):
                    f.write(f"{i}. {pwd}\n")
                f.write(f"\nTotal Generated: {len(passwords)}\n")
                f.write(f"Total Possible: {self.calculate_total_passwords():,}\n")
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def export_binary_strings_to_csv(self, n, strings, count, filename='binary_strings.csv'):
        """Export binary analysis to CSV file"""
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Binary String Analysis Results'])
                writer.writerow([])
                writer.writerow(['Length (n)', n])
                writer.writerow(['Total Valid Strings', count])
                writer.writerow([])
                
                if strings:
                    writer.writerow(['Valid Binary Strings'])
                    for s in strings:
                        writer.writerow([s])
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False


# CONSOLE INTERFACE

def console_app():
    """Console-based user interface"""
    system = PasswordPatternSystem()
    
    print("\n--- PASSWORD GENERATOR AND PATTERN ANALYZER ---")
    
    while True:
        print("\nMain Menu:")
        print("1. Password Generator")
        print("2. Pattern Analyzer")
        print("3. Exit")
        
        try:
            choice = input("\nChoice (1-3): ").strip()
            
            if choice == '1':
                # Password Generator
                print("\n--- PASSWORD GENERATOR ---")
                print(f"\nTotal possible combinations: {system.calculate_total_passwords():,}")
                
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
                
                # Export option
                if input("\nExport to file? (y/n): ").lower() == 'y':
                    fname = input("Filename (default: passwords.txt): ").strip()
                    fname = fname if fname else 'passwords.txt'
                    if system.export_passwords_to_txt(passwords, fname):
                        print(f"Exported to {fname}")
                
            elif choice == '2':
                # Pattern Analyzer
                print("\n--- PATTERN ANALYZER ---")
                print("\nCount binary strings without consecutive 1s")
                
                while True:
                    try:
                        n = int(input("\nEnter length n (>= 0): "))
                        if n >= 0:
                            break
                        print("Enter a non-negative integer.")
                    except ValueError:
                        print("Invalid input. Enter an integer.")
                
                count = system.count_valid_binary_strings(n)
                print(f"\nResults for n = {n}:")
                print(f"Valid strings: {count}")
                
                # Show strings if n <= 5
                if n <= 5:
                    strings = system.generate_valid_binary_strings(n)
                    print("\nAll valid strings:")
                    for i, s in enumerate(strings, 1):
                        print(f"{i:2}. {s if s else '(empty)'}")
                    
                    # Export option
                    if input("\nExport to CSV? (y/n): ").lower() == 'y':
                        fname = input("Filename (default: binary_strings.csv): ").strip()
                        fname = fname if fname else 'binary_strings.csv'
                        if system.export_binary_strings_to_csv(n, strings, count, fname):
                            print(f"Exported to {fname}")
                else:
                    print("(List not shown for n > 5)")
            
            elif choice == '3':
                print("\nThank you! Exiting the program...\n")
                sys.exit(0)
            else:
                print("Invalid choice. Enter 1-3.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...\n")
            break
        except Exception as e:
            print(f"\nError: {e}")


# GRAPHICAL USER INTERFACE

class PasswordPatternGUI:
    """GUI for password generation and pattern analysis"""
    
    def __init__(self, root):
        self.root = root
        self.system = PasswordPatternSystem()
        
        self.root.title("Password Generator & Pattern Analyzer")
        self.root.geometry("800x600")
        
        # Create tabbed interface
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_password_tab()
        self.create_pattern_tab()
    
    def create_password_tab(self):
        """Create password generator tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Password Generator')
        
        # Title
        tk.Label(tab, text="Password Generator", 
                font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Info display
        total = self.system.calculate_total_passwords()
        tk.Label(tab, text=f"Total possible combinations: {total:,}", 
                font=('Arial', 11)).pack(pady=5)
        
        # Input controls
        input_frame = tk.Frame(tab)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Count (1-20):").pack(side='left', padx=5)
        self.pwd_count = tk.StringVar(value="10")
        tk.Entry(input_frame, textvariable=self.pwd_count, width=10).pack(side='left', padx=5)
        
        tk.Button(input_frame, text="Generate", command=self.generate_passwords,
                 bg='#4CAF50', fg='white', padx=20).pack(side='left', padx=5)
        tk.Button(input_frame, text="Export", command=self.export_passwords,
                 bg='#2196F3', fg='white', padx=20).pack(side='left', padx=5)
        
        # Output area
        self.pwd_output = scrolledtext.ScrolledText(tab, width=70, height=20)
        self.pwd_output.pack(pady=10, padx=20)
    
    def create_pattern_tab(self):
        """Create pattern analyzer tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Pattern Analyzer')
        
        # Title
        tk.Label(tab, text="Binary Pattern Analyzer", 
                font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Label(tab, text="Count strings without consecutive 1s", 
                font=('Arial', 10, 'italic')).pack()
        
        # Input controls
        input_frame = tk.Frame(tab)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Length n:").pack(side='left', padx=5)
        self.n_var = tk.StringVar(value="4")
        tk.Entry(input_frame, textvariable=self.n_var, width=10).pack(side='left', padx=5)
        
        tk.Button(input_frame, text="Analyze", command=self.analyze_pattern,
                 bg='#4CAF50', fg='white', padx=20).pack(side='left', padx=5)
        tk.Button(input_frame, text="Export", command=self.export_binary,
                 bg='#2196F3', fg='white', padx=20).pack(side='left', padx=5)
        
        # Output area
        self.pattern_output = scrolledtext.ScrolledText(tab, width=70, height=20)
        self.pattern_output.pack(pady=10, padx=20)
    
    def generate_passwords(self):
        """Handle password generation button"""
        try:
            count = int(self.pwd_count.get())
            if not 1 <= count <= 20:
                messagebox.showerror("Error", "Enter a number between 1 and 20")
                return
            
            passwords = self.system.generate_multiple_passwords(count)
            
            self.pwd_output.delete(1.0, tk.END)
            self.pwd_output.insert(tk.END, "Generated Passwords:\n\n")
            
            for i, pwd in enumerate(passwords, 1):
                self.pwd_output.insert(tk.END, f"{i:2}. {pwd}\n")
            
            self.pwd_output.insert(tk.END, f"\nTotal: {len(passwords)}\n")
            self.current_passwords = passwords
            
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")
    
    def export_passwords(self):
        """Export passwords to file"""
        if not hasattr(self, 'current_passwords'):
            messagebox.showwarning("Warning", "Generate passwords first")
            return
        
        fname = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if fname and self.system.export_passwords_to_txt(self.current_passwords, fname):
            messagebox.showinfo("Success", f"Exported to {fname}")
    
    def analyze_pattern(self):
        """Handle pattern analysis button"""
        try:
            n = int(self.n_var.get())
            if n < 0:
                messagebox.showerror("Error", "Enter a non-negative integer")
                return
            
            count = self.system.count_valid_binary_strings(n)
            
            self.pattern_output.delete(1.0, tk.END)
            self.pattern_output.insert(tk.END, f"Results for n = {n}:\n\n")
            self.pattern_output.insert(tk.END, f"Valid strings: {count}\n\n")
            
            if n <= 5:
                strings = self.system.generate_valid_binary_strings(n)
                self.pattern_output.insert(tk.END, "All valid strings:\n")
                for i, s in enumerate(strings, 1):
                    self.pattern_output.insert(tk.END, f"{i:2}. {s if s else '(empty)'}\n")
                self.current_binary_data = (n, strings, count)
            else:
                self.pattern_output.insert(tk.END, "(List not shown for n > 5)")
                self.current_binary_data = (n, None, count)
            
        except ValueError:
            messagebox.showerror("Error", "Enter a valid integer")
    
    def export_binary(self):
        """Export binary analysis to CSV"""
        if not hasattr(self, 'current_binary_data'):
            messagebox.showwarning("Warning", "Analyze a pattern first")
            return
        
        fname = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if fname:
            n, strings, count = self.current_binary_data
            if self.system.export_binary_strings_to_csv(n, strings, count, fname):
                messagebox.showinfo("Success", f"Exported to {fname}")

def run_gui():
    """Launch GUI application"""
    root = tk.Tk()
    PasswordPatternGUI(root)

    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.focus_force()
    
    root.mainloop()

# MAIN ENTRY POINT

if __name__ == "__main__":
    print("\nSelect Interface:")
    print("1. Console Mode")
    print("2. GUI Mode")
    print("3. Exit")
    
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