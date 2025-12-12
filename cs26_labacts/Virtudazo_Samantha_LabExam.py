# Name: Virtudazo, Samantha Lewis A.
# Date: 12/11/2025

# Description:
# Class List Manager using Object-Oriented Programming (OOP),
# File Handling, and a basic PyQt6 GUI.

# NOTE: The interface is intentionally LEFT-ALIGNED.
# Students must redesign and CENTER the GUI layout.

# Imports needed for system access, Qt functions, fonts, and GUI widgets
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QTextEdit, QVBoxLayout,
)

# Defines a Student object that stores basic student details
class Student:
    def __init__(self, student_id, name, course):
        self.student_id = student_id
        self.name = name
        self.course = course
    
    # Converts student data into a single text line
    def to_string(self):
        return f"{self.student_id}, {self.name}, {self.course}"

# Handles saving and loading student records to a text file
class StudentManager:
    def __init__(self, filename="students.txt"):
        self.filename = filename

    # Saves one student entry to the file
    def save_student(self, student):
        with open(self.filename, "a") as file:
            print(student.to_string(), file=file)

    # Reads all saved students from the file
    def load_students(self):
        try:
            with open(self.filename, "r") as file:
                return file.read().splitlines()
        except FileNotFoundError:
            return []

# Creates the main GUI window and controls for the app
class StudentApp(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = StudentManager()
        self.setWindowTitle("Class List Manager")
        self.setStyleSheet("background-color: white;")

        # Defines default style for input fields
        self.common_style = """
            color: black;
            border: 1px solid black;
            border-radius: 15px;
            padding: 5px;
            background-color: white;
        """

        # Creates input label and box for Student ID
        self.lbl_id = QLabel("Student ID:")
        self.lbl_id.setFont(QFont("Poppins", 13))
        self.lbl_id.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_id.setStyleSheet("color: black;")
        self.txt_id = QLineEdit()
        self.txt_id.setStyleSheet(self.common_style)

        # Creates input label and box for student name
        self.lbl_name = QLabel("Name:")
        self.lbl_name.setFont(QFont("Poppins", 13))
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_name.setStyleSheet("color: black;")
        self.txt_name = QLineEdit()
        self.txt_name.setStyleSheet(self.common_style)

        # Creates input label and box for course and section
        self.lbl_course = QLabel("Course / Section:")
        self.lbl_course.setFont(QFont("Poppins", 13))
        self.lbl_course.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_course.setStyleSheet("color: black;")
        self.txt_course = QLineEdit()
        self.txt_course.setStyleSheet(self.common_style)

        # Button for saving a new student record
        self.btn_add = QPushButton("Add Student")
        self.btn_add.setFont(QFont("Poppins", 13))
        self.btn_add.setStyleSheet(
            "background-color: #96A78D;"
            "color: black;"
            "border: 1px solid black;"
            "border-radius: 15px;"
            "padding: 5px;"
        )

        # Button for loading and showing saved students
        self.btn_load = QPushButton("Load Students")
        self.btn_load.setFont(QFont("Poppins", 13))
        self.btn_load.setStyleSheet(
            "background-color: #6D94C5;"
            "color: black;"
            "border: 1px solid black;"
            "border-radius: 15px;"
            "padding: 5px;"
        )

        # Text area to display all loaded student entries
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet(
            "font-family: Poppins;"   
            "font-size: 10pt;"
            "color: black;"
            "background-color: #B6AE9F;")

        # Lays out all widgets vertically and centers them
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        
        layout.addStretch()

        layout.addWidget(self.lbl_id, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.txt_id, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_name, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.txt_name, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_course, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.txt_course, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_add, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.btn_load, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.display, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        self.setLayout(layout)

        # Fixes the size of all input fields, buttons, and display
        self.txt_id.setFixedWidth(250)
        self.txt_id.setFixedHeight(35)
        self.txt_name.setFixedWidth(250)
        self.txt_name.setFixedHeight(35)
        self.txt_course.setFixedWidth(250)
        self.txt_course.setFixedHeight(35)
        self.btn_add.setFixedWidth(250)
        self.btn_add.setFixedHeight(35)
        self.btn_load.setFixedWidth(250)
        self.btn_load.setFixedHeight(35)
        self.display.setFixedWidth(250)
        self.display.setFixedHeight(200)

        # Connects button clicks to their functions
        self.btn_add.clicked.connect(self.add_student)
        self.btn_load.clicked.connect(self.load_students)

    # Saves a student's input data to the file
    def add_student(self):
        student = Student(
            self.txt_id.text(),
            self.txt_name.text(),
            self.txt_course.text()
        )
        print(f"\nStudent information saved successfully to 'students.txt'")
        self.manager.save_student(student)
        self.txt_id.clear()
        self.txt_name.clear()
        self.txt_course.clear()

    # Loads and displays all student records
    def load_students(self):
        self.display.clear()
        students = self.manager.load_students()
        for student in students:
            self.display.append(student)

    # Allows ESC key to reset window state
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()

# Main entry point - runs the application and opens the GUI window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentApp()
    window.showMaximized()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec())