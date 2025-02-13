import sys
import sqlite3
import bcrypt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, 
    QVBoxLayout, QWidget, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import subprocess


conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
conn.commit()

class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Authorization App")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("""

            color: black;
            font-size: 14px;
        """)

        self.label_register = QLabel("Registration")
        self.label_register.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_register.setFont(QFont("Arial", 40, QFont.Weight.Bold))

        self.inputlogin = QLineEdit(self)
        self.inputlogin.setPlaceholderText("Input login")
        self.inputlogin.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 2px solid #dcdcdc;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #4ca1af;
                background-color: #ffffff;
                outline: none;
            }
        """)
        self.inputPassword = QLineEdit(self)
        self.inputPassword.setPlaceholderText("Input password")
        self.inputPassword.setEchoMode(QLineEdit.EchoMode.Password)
        self.inputPassword.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 2px solid #dcdcdc;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #4ca1af;
                background-color: #ffffff;
                outline: none;
            }
        """)
        self.button = QPushButton("Register", self)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(72, 149, 239, 255), 
                    stop:1 rgba(86, 204, 242, 255)
                );
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 123, 255, 255),
                    stop:1 rgba(50, 150, 250, 255)
                );
            }
            QPushButton:pressed {
                background-color: rgba(0, 123, 255, 200);
            }
        """)        
        self.button.clicked.connect(self.register)
        
        self.label_login = QLabel("Log In")
        self.label_login.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_login.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        self.inputloginForLogin = QLineEdit(self)
        self.inputloginForLogin.setPlaceholderText("Enter login")
        self.inputloginForLogin.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 2px solid #dcdcdc;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #4ca1af;
                background-color: #ffffff;
                outline: none;
            }
        """)
        self.inputPasswordForLogin = QLineEdit(self)
        self.inputPasswordForLogin.setPlaceholderText("Enter password")
        self.inputPasswordForLogin.setEchoMode(QLineEdit.EchoMode.Password)
        self.inputPasswordForLogin.setStyleSheet("""
            QLineEdit {
                background-color: #f9f9f9;
                border: 2px solid #dcdcdc;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #4ca1af;
                background-color: #ffffff;
                outline: none;
            }
        """)
        self.buttonLogin = QPushButton("Log In", self)
        self.buttonLogin.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 99, 71, 1), 
                    stop:1 rgba(255, 71, 71, 1)
                );
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 31, 26, 1),
                    stop:1 rgba(255, 31, 26, 0.7)
                );
            }
            QPushButton:pressed {
                background-color: rgba(255, 0, 0, 1);
            }
        """)        
        self.buttonLogin.clicked.connect(self.logIn)

        layout = QVBoxLayout()
        layout.addWidget(self.label_register)
        layout.addWidget(self.inputlogin)
        layout.addWidget(self.inputPassword)
        layout.addWidget(self.button)
        layout.addWidget(self.label_login)
        layout.addWidget(self.inputloginForLogin)
        layout.addWidget(self.inputPasswordForLogin)
        layout.addWidget(self.buttonLogin)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def register(self):
        login = self.inputlogin.text().strip()
        password = self.inputPassword.text().strip()

        if not login or not password:
            QMessageBox.warning(self, "Error", "Login and password cannot be empty!")
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            cursor.execute("INSERT INTO users (login, password) VALUES (?, ?)", (login, hashed_password))
            conn.commit()
            QMessageBox.information(self, "Success", "You registered!")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "User already exists!")

    def logIn(self):
        login = self.inputloginForLogin.text().strip()
        password = self.inputPasswordForLogin.text().strip()

        cursor.execute("SELECT password FROM users WHERE login = ?", (login,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode(), user[0]):
            QMessageBox.information(self, "Success", f"You are logged in as {login}!")
            self.open_video_player(login) 
        else:
            QMessageBox.warning(self, "Error", "Invalid login or password")

    def open_video_player(self, username):
        self.close()
        subprocess.Popen(["python", "ui.py", username])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec())
