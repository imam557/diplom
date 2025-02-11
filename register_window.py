from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import sys


class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Authorization App")
        self.setGeometry(100, 100, 400, 300)

        self.label_register = QLabel("Registration")
        self.label_register.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_register.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        # self.label_register.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")




        self.inputlogin = QLineEdit(self)
        self.inputlogin.setPlaceholderText("input login")
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
        self.inputPassword.setPlaceholderText("input password")
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

        self.inputloginAndPassword = QLineEdit(self)
        self.inputloginAndPassword.setPlaceholderText("Write your login and password in one line and separate it with a space")
        self.inputloginAndPassword.setStyleSheet("""
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
        self.buttonLogin.clicked.connect(self.logIn)
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

        layout = QVBoxLayout()
        layout.addWidget(self.label_register)
        layout.addWidget(self.inputlogin)
        layout.addWidget(self.inputPassword)
        layout.addWidget(self.button)
        layout.addWidget(self.label_login)
        layout.addWidget(self.inputloginAndPassword)
        layout.addWidget(self.buttonLogin)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)


        container = QWidget()
        container.setLayout(layout)
        
        self.setCentralWidget(container)


    
    def register(self):
        login = self.inputlogin.text()
        password = self.inputPassword.text()

        with open("data.txt", "a") as file:
            file.write(f"{login} {password}\n")
        print(f"You registered with login: {login} and password: {password}")

        msg = QMessageBox(self)
        msg.setWindowTitle("Succesful")
        msg.setText("You registred!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    
    
    def logIn(self):
        with open("data.txt", "r") as file:
            for line in file:
                if line == self.inputloginAndPassword.text() + "\n":
                    print("Access granted", QMessageBox.Icon.Information)
                    self.show_message()
                    return
            
        print("Access denied")
        msg = QMessageBox(self)
        msg.setWindowTitle("Succesful")
        msg.setText("invalid login or password")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    
        
        
    def show_message(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Succesful")
        msg.setText("you in yor account")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()
        

