from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QSlider, QHBoxLayout, QStackedWidget, QFileDialog, QMessageBox
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, QTime, Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon, QFont, QPixmap
import sys
import subprocess
import os
from moviepy import VideoFileClip, AudioFileClip
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import ffmpeg
import srt
from datetime import timedelta
import random


from register_window import RegistrationWindow


class VideoPlayer(QMainWindow):
    def __init__(self, username="Guest"):
        super().__init__()
        self.setWindowTitle("Voxideo")
        self.setGeometry(100, 100, 1300, 750)
        self.setMinimumSize(800, 600)
        
        self.username = username
        self.registration_window = None
        self.video_path = None
        self.translated_text = ""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        
        top_layout = QHBoxLayout()

        self.menu_button = QPushButton()
        self.menu_button.setIcon(QIcon('images/menu.png'))
        self.menu_button.setFixedSize(50, 50)
        self.menu_button.setStyleSheet("border: none;")
        self.menu_button.clicked.connect(self.toggle_menu)

        top_layout.addStretch()
        top_layout.addWidget(self.menu_button)

        self.main_layout.addLayout(top_layout)

       
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(800, 450)

        self.main_layout.addWidget(self.video_widget, alignment=Qt.AlignmentFlag.AlignCenter)
     
        


        

        
        self.progress_layout = QHBoxLayout()
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
            background: #333;
            height: 5px;
            border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #007BFF;
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #007BFF;
                border-radius: 2px;
                }
                                        
        """)


        self.timecode_label = QLabel("00:00:00")
        self.timecode_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.timecode_label.setStyleSheet("color: black;")

        self.progress_layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignBottom)
        self.progress_layout.addWidget(self.timecode_label)
        self.main_layout.addLayout(self.progress_layout)

        controls_layout = QHBoxLayout()
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon('images/play-button.png'))
        self.play_button.setFixedSize(30, 30)
        self.play_button.setStyleSheet("border: none;")

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon('images/stop.png'))
        self.stop_button.setFixedSize(30, 30)
        self.stop_button.setStyleSheet("border: none;")

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.main_layout.addLayout(controls_layout)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        self.play_button.clicked.connect(self.play_video_file)
        self.stop_button.clicked.connect(self.stop_video)
        self.media_player.positionChanged.connect(self.update_timecode_and_progress)
        self.media_player.durationChanged.connect(self.update_duration)
        self.progress_bar.sliderMoved.connect(self.set_position)

        self.buttons_layout = QHBoxLayout()



        self.translate_button = QPushButton("Translate")
        self.translate_button.setFixedSize(200, 50)
        self.translate_button.setStyleSheet("""
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
        self.buttons_layout.addWidget(self.translate_button)
        self.translate_button.clicked.connect(self.translating_video)


        self.add_subtitle_button = QPushButton("Add Subtitles")
        self.add_subtitle_button.setFixedSize(200, 50)
        self.add_subtitle_button.setStyleSheet("""
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
        self.buttons_layout.addWidget(self.add_subtitle_button)
        self.add_subtitle_button.clicked.connect(self.subtitles_adding)

      
        self.download_video_button = QPushButton("Download Video")
        self.download_video_button.setFixedSize(200, 50)
        self.download_video_button.setStyleSheet("""
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
        self.download_video_button.clicked.connect(self.download_video)

        self.buttons_layout.addWidget(self.download_video_button)



        self.main_layout.addLayout(self.buttons_layout)


        self.side_menu = QWidget(self)
        self.side_menu.setGeometry(QRect(1300, 0, 250, 750))  
        self.side_menu.setStyleSheet("background-color: #2E3A46;")

        menu_layout = QVBoxLayout(self.side_menu)

        self.user_label = QLabel()

        name_photo_layout = QHBoxLayout()

        self.user_name_label = QLabel(self.username)
        self.user_name_label.setStyleSheet("color: white; font-size: 16px;")
        self.user_name_label.setFixedSize(200, 30)

        

       

        self.get_premium_button = QPushButton("Get Premium")
        self.get_premium_button.setFixedSize(200, 50)
        self.get_premium_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(233, 235, 35, 1), 
                    stop:1 rgba(233, 220, 35, 1)
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
                    stop:0 rgba(252, 255, 0, 1),
                    stop:1 rgba(252, 255, 0, 1)
                );
            }
            QPushButton:pressed {
                background-color: rgba(194, 195, 48, 1);
            }
        """)

        self.logout_button = QPushButton("Log Out")
        self.logout_button.setFixedSize(200, 50)
        self.logout_button.setStyleSheet("""
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
        self.logout_button.clicked.connect(self.logout)

        self.close_menu_button = QPushButton("Close")
        self.close_menu_button.setFixedSize(200, 40)
        self.close_menu_button.setStyleSheet("""
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
        self.close_menu_button.clicked.connect(self.toggle_menu)

        

        avatar_path = f"images/profile_pictures/{self.username[0].upper()}.png"
        pixmap = QPixmap(avatar_path)
        pixmap = pixmap.scaled(50,50)
        self.user_label.setPixmap(pixmap)
        self.user_label.setFixedSize(50, 50)
        
        
        
        

        # menu_layout.addWidget(self.user_label)
        # menu_layout.addWidget(self.user_name_label)
   

        name_photo_layout.addWidget(self.user_label)
        name_photo_layout.addWidget(self.user_name_label)
        menu_layout.addLayout(name_photo_layout)
        menu_layout.addWidget(self.get_premium_button)
        menu_layout.addWidget(self.logout_button)
        menu_layout.addWidget(self.close_menu_button)
        menu_layout.addStretch()

        self.menu_animation = QPropertyAnimation(self.side_menu, b"geometry")

        self.file_picker_button = QPushButton("Open Video")
        self.file_picker_button.setFixedSize(200, 50)
        self.file_picker_button.setStyleSheet("""
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
        self.file_picker_button.clicked.connect(self.open_file_dialog)
        self.main_layout.addWidget(self.file_picker_button, alignment=Qt.AlignmentFlag.AlignCenter)


    # def set_avatar(self):
    #     avatar_path = f"profile_pictures/{self.username[0].upper()}.png"
    #     if not os.path.exists(avatar_path):
    #         avatar_path = "profile_pictures/default.png"
    #     self.user_label.setPixmap(QPixmap(avatar_path).scaled(50, 50))

    def translating_video(self):
        self.transale_video()
        self.clear_files()

    def subtitles_adding(self):
        self.create_srt()
        self.add_subtitles()
#         # self.clear_files()

    def transale_video(self):
        video = VideoFileClip(self.video_path)
        video.audio.write_audiofile("audio.wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile("audio.wav") as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language="ru")
            except sr.UnknownValueError:
                QMessageBox.warning(self, "Error", "Google Speech Recognition could not understand the audio.")
                return
            except sr.RequestError as e:
                QMessageBox.warning(self, "Error", f"Could not request results from Google Speech Recognition service; {e}")
                return

        translator = Translator()
        self.translated_text = translator.translate(text, src="ru", dest="en").text
        print(f"Translated text: {self.translated_text}")  # Debugging statement

        tts = gTTS(text=self.translated_text, lang="en")
        tts.save("translated.mp3")

        audio = AudioFileClip("translated.mp3")
        video = video.with_audio(audio)
        video.write_videofile("translated_video.mp4")

        QMessageBox.information(self, "Success", "Video has been translated!")
        video_url = QUrl.fromLocalFile("translated_video.mp4")
        self.media_player.setSource(video_url)
        self.media_player.play()



    def generate_timecode(self, start_seconds, duration):
        start_minutes = start_seconds // 60
        start_seconds = start_seconds % 60
        end_seconds = start_seconds + duration
        end_minutes = end_seconds // 60
        end_seconds = end_seconds % 60

        start_time = f"00:{start_minutes:02}:{start_seconds:02},000"
        end_time = f"00:{end_minutes:02}:{end_seconds:02},000"

        return start_time, end_time
    
    def insert_periods(self, text):
        result = ""
        for i, char in enumerate(text):
            if char.isupper() and i != 0:
                result += "."
            result += char
        return result
       
    def split_into_sentences(self, text):
        return text.split('.')
    
    def create_srt(self, duration_per_line=4):
        srt_content = []
        sentences = self.split_into_sentences(self.insert_periods(self.translated_text))
        start_seconds = 0
        sequence = 1

        for sentence in sentences:
            duration = 4
            if len(sentence.split()) > 100:
                duration += random.randint(1, 3)
            start_time, end_time = self.generate_timecode(start_seconds, duration)
            srt_content.append(f"{sequence}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(sentence.strip())
            srt_content.append("")
            start_seconds += duration
            sequence += 1

        try:
            with open("subtitles.srt", "w", encoding="utf-8") as file:
                file.write("\n".join(srt_content))
            print("srt создан")
            print(self.translated_text)  # Debugging statement
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")

    def add_subtitles(self):
        (
            ffmpeg
            .input("translated_video.mp4")
            .output("final_video.mp4", vf="subtitles=subtitles.srt")
            .run(overwrite_output=True)
        )
        QMessageBox.information(self, "Success", "Subtitles have been added!")
        video_url = QUrl.fromLocalFile("final_video.mp4")
        self.media_player.setSource(video_url)
        self.media_player.play()

    def clear_files(self):
        os.remove("audio.wav")
        os.remove("translated.mp3")
        try:
            os.remove("subtitles.srt")
        except FileNotFoundError:
            pass

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Videos (*.mp4 *.avi)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            self.video_path = file_dialog.selectedFiles()[0]
            self.play_video_file(self.video_path)

    def play_video_file(self, video_path):
        video_url = QUrl.fromLocalFile(video_path)
        print(video_url)
        self.media_player.setSource(video_url)
        self.media_player.play()

    def stop_video(self):
        self.media_player.stop()
        self.progress_bar.setValue(0)
        self.timecode_label.setText("00:00:00")

    def update_timecode_and_progress(self, position):
        time = QTime(0, 0, 0).addMSecs(position)
        self.timecode_label.setText(time.toString("hh:mm:ss"))
        if self.media_player.duration() > 0:
            self.progress_bar.setValue((position * 100) // self.media_player.duration())

    def update_duration(self, duration):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

    def set_position(self, position):
        if self.media_player.duration() > 0:
            self.media_player.setPosition((position * self.media_player.duration()) // 100)

    
    def toggle_menu(self):
        if self.side_menu.geometry().x() == 1300:
            self.menu_animation.setStartValue(QRect(1300, 0, 250, 750))
            self.menu_animation.setEndValue(QRect(1050, 0, 250, 750))
        else:
            self.menu_animation.setStartValue(QRect(1050, 0, 250, 750))
            self.menu_animation.setEndValue(QRect(1300, 0, 250, 750))

        self.menu_animation.setDuration(300)
        self.menu_animation.start()

    def logout(self):
        self.close()
        subprocess.Popen(["python", "register_window.py"])

    def download_video(self):
         subprocess.Popen(["python", "download_from_socialmedia.py"])


app = QApplication(sys.argv)
username = sys.argv[1] if len(sys.argv) > 1 else "Guest"
window = VideoPlayer(username)
window.show()
sys.exit(app.exec())
