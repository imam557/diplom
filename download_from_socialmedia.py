from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton, QCheckBox, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import os
from pytube import YouTube
import yt_dlp

class VideoDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Downloader")
        self.setGeometry(100, 100, 347, 230)
        self.setFixedSize( 347, 230)
        self.setStyleSheet("color: black; font-size: 14px;")

        self.label = QLabel("Download video from:")
        
        self.label.setFont(QFont("Arial", 20, QFont.Weight.Bold))

        self.checkbox1 = QCheckBox("YouTube")
        self.checkbox2 = QCheckBox("TikTok/Instagram")

        checkbox_style = """
            QCheckBox {
                spacing: 10px;
                font-size: 16px;
                color: #333;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid #dcdcdc;
                background-color: #f0f0f0;
            }
            QCheckBox::indicator:checked {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(72, 149, 239, 255), stop:1 rgba(86, 204, 242, 255));
                border: 2px solid #4ca1af;
            }
            QCheckBox::hover {
                color: #4ca1af;
            }
        """

        self.checkbox1.setStyleSheet(checkbox_style)
        self.checkbox2.setStyleSheet(checkbox_style)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Input URL")
        self.input.setStyleSheet("""
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
            }
        """)

        self.button = QPushButton("Download")
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

        self.button.clicked.connect(self.download_video)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.checkbox1)
        layout.addWidget(self.checkbox2)
        self.checkbox1.stateChanged.connect(self.checkbox_changed)
        self.checkbox2.stateChanged.connect(self.checkbox_changed)
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


    def download_video(self):
        url = self.input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "input video URL")
            return
        
        save_path = "downloads"
        os.makedirs(save_path, exist_ok=True)

        if self.checkbox1.isChecked():
            ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'noprogress': True,
            'quiet': False,
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    QMessageBox.information(self, "Успех", f"Видео скачано в папку '{save_path}'")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось скачать видео: {e}")
        
        
        elif self.checkbox2.isChecked():
            ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'quiet': False,
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
             ydl.download([url])
             QMessageBox.information(self, "Успех", f"Видео скачано в папку '{save_path}'")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось скачать видео: {e}")


    def checkbox_changed(self):
        sender = self.sender()
        if sender == self.checkbox1:
            self.checkbox2.setChecked(False)
        elif sender == self.checkbox2:
            self.checkbox1.setChecked(False)

app = QApplication([])
window = VideoDownloader()
window.show()
app.exec()
