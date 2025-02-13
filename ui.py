from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QSlider, QHBoxLayout, QFrame, QStackedWidget, QFileDialog, QMessageBox
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, QTime, Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon, QFont
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

       
        self.video_frame = QFrame()
        self.video_frame.setFrameShape(QFrame.Shape.Box)
        self.video_frame.setLineWidth(2)

        self.video_widget = QVideoWidget(self.video_frame)
        self.video_widget.setFixedSize(800, 450)

        frame_layout = QVBoxLayout(self.video_frame)
        frame_layout.addWidget(self.video_widget)
        self.main_layout.addWidget(self.video_frame, alignment=Qt.AlignmentFlag.AlignCenter)

     
        self.translate_button = QPushButton("Translate")
        self.translate_button.setFixedSize(200, 50)
        self.translate_button.setStyleSheet("""
            background-color: #007BFF; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)
        self.main_layout.addWidget(self.translate_button, alignment=Qt.AlignmentFlag.AlignBottom)
        self.translate_button.clicked.connect(self.transale_video)


        self.add_subtitle_button = QPushButton("Add Subtitles")
        self.add_subtitle_button.setFixedSize(200, 50)
        self.add_subtitle_button.setStyleSheet("""
            background-color: #007BFF; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)
        self.main_layout.addWidget(self.add_subtitle_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.add_subtitle_button.clicked.connect(self.add_subtitles)


        controls_layout = QHBoxLayout()
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon('images/play-button.png'))
        self.play_button.setFixedSize(50, 50)
        self.play_button.setStyleSheet("border: none;")

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon('images/stop.png'))
        self.stop_button.setFixedSize(50, 50)
        self.stop_button.setStyleSheet("border: none;")

        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addLayout(controls_layout)

        
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

        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.timecode_label)
        self.main_layout.addLayout(self.progress_layout)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        self.play_button.clicked.connect(self.play_video_file)
        self.stop_button.clicked.connect(self.stop_video)
        self.media_player.positionChanged.connect(self.update_timecode_and_progress)
        self.media_player.durationChanged.connect(self.update_duration)
        self.progress_bar.sliderMoved.connect(self.set_position)

      
        self.side_menu = QWidget(self)
        self.side_menu.setGeometry(QRect(1300, 0, 250, 750))  
        self.side_menu.setStyleSheet("background-color: #2E3A46;")

        menu_layout = QVBoxLayout(self.side_menu)

  
        self.user_label = QLabel(f"Logged in as: {self.username}")
        self.user_label.setStyleSheet("color: white; font-size: 16px;")
        self.user_label.setFixedSize(200, 30)

        

       

        self.get_premium_button = QPushButton("Get Premium")
        self.get_premium_button.setFixedSize(200, 50)
        self.get_premium_button.setStyleSheet("""
            background-color: #dde00b; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)

        self.logout_button = QPushButton("Log Out")
        self.logout_button.setFixedSize(200, 50)
        self.logout_button.setStyleSheet("""
            background-color: #FF3B30; color: white; font-size: 16px;
            border: none; border-radius: 5px;
        """)
        self.logout_button.clicked.connect(self.logout)

        self.close_menu_button = QPushButton("Close")
        self.close_menu_button.setFixedSize(200, 40)
        self.close_menu_button.setStyleSheet("""
            background-color: #FF3B30; color: white; font-size: 14px;
            border: none; border-radius: 5px;
        """)
        self.close_menu_button.clicked.connect(self.toggle_menu)

        menu_layout.addWidget(self.user_label)
   
        menu_layout.addWidget(self.get_premium_button)
        menu_layout.addWidget(self.logout_button)
        menu_layout.addWidget(self.close_menu_button)
        menu_layout.addStretch()

        self.menu_animation = QPropertyAnimation(self.side_menu, b"geometry")

        self.file_picker_button = QPushButton("Open Video")
        self.file_picker_button.setFixedSize(200, 50)
        self.file_picker_button.setStyleSheet("""
            background-color: #007BFF; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)
        self.file_picker_button.clicked.connect(self.open_file_dialog)
        self.main_layout.addWidget(self.file_picker_button, alignment=Qt.AlignmentFlag.AlignCenter)

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
        translated_text = translator.translate(text, src="ru", dest="en").text

        tts = gTTS(text=translated_text, lang="ru")
        tts.save("translated.mp3")

        audio = AudioFileClip("translated.mp3")
        video = video.with_audio(audio)
        video.write_videofile("translated_video.mp4")

        QMessageBox.information(self, "Success", "Video has been translated!")


    def add_subtitles(self):
        sentences = self.translated_text.split(".")
        subtitles = []
        start_time = 0
        video_duration = VideoFileClip(self.video_path).duration

        words_per_second = len(self.translated_text.split()) / video_duration
        for i, sentences in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            word_count = len(sentence.split())
            end_time = start_time + max(5, word_count / words_per_second)

            if end_time > video_duration:
                end_time = video_duration

            subtitle = srt.Subtitle(
                index=i,
                start=timedelta(seconds=start_time),
                end=timedelta(seconds=end_time),
                content=sentence
            )
            subtitles.append(subtitle)
            start_time = end_time

        with open("subtitles.srt", "w", encoding="utf-8") as f:
            f.write(srt.compose(subtitles))

        (
            ffmpeg
            .input("translated_video.mp4")
            .ouput("final_clip.mp4", vf=f"subtitles=subtitles.srt")
            .run(overwrite_output=True)
        )
        audio = AudioFileClip("translated.mp3")
        video = VideoFileClip("final_clip.mp4")
        video = video.with_audio(audio)
        video.write_videofile("final_clip.mp4", codec="libx264", audio_codec="aac")

        QMessageBox.information(self, "Success", "Subtitles have been added!")

        os.remove("audio.wav")
        os.remove("translated.mp3")
        os.remove("translated_video.mp4")
        os.remove("subtitles.srt")



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


app = QApplication(sys.argv)
username = sys.argv[1] if len(sys.argv) > 1 else "Guest"
window = VideoPlayer(username)
window.show()
sys.exit(app.exec())
