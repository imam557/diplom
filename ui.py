from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QSlider, QHBoxLayout, QFrame, QStackedWidget, QFileDialog
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, QTime, Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon
import sys

from register_window import RegistrationWindow

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voxideo")
        self.setGeometry(100, 100, 1300, 750)
        self.setMinimumSize(800, 600)

        self.registration_window = None

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # ========== Верхняя панель ==========
        top_layout = QHBoxLayout()

        self.menu_button = QPushButton()
        self.menu_button.setIcon(QIcon('images/menu.png'))
        self.menu_button.setFixedSize(50, 50)
        self.menu_button.setStyleSheet("border: none;")
        self.menu_button.clicked.connect(self.toggle_menu)

        top_layout.addStretch()
        top_layout.addWidget(self.menu_button)

        self.main_layout.addLayout(top_layout)

        # ========== Видеоплеер ==========
        self.video_frame = QFrame()
        self.video_frame.setFrameShape(QFrame.Shape.Box)
        self.video_frame.setLineWidth(2)

        self.video_widget = QVideoWidget(self.video_frame)
        self.video_widget.setFixedSize(800, 450)

        frame_layout = QVBoxLayout(self.video_frame)
        frame_layout.addWidget(self.video_widget)
        self.main_layout.addWidget(self.video_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        # ========== Кнопки управления ==========
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

        # ========== Прогресс-бар ==========
        self.progress_layout = QHBoxLayout()
        self.progress_bar = QSlider(Qt.Orientation.Horizontal)
        self.progress_bar.setRange(0, 100)
        self.timecode_label = QLabel("00:00:00")

        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.timecode_label)
        self.main_layout.addLayout(self.progress_layout)

        # Apply stylesheet to progress bar
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #ddd;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3a7bd5;
                border: 1px solid #5c5c5c;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #3a7bd5;
                border: 1px solid #777;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #fff;
                border: 1px solid #777;
                height: 8px;
                border-radius: 4px;
            }
        """)

        # ========== Настройка медиаплеера ==========
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        self.play_button.clicked.connect(self.play_video)
        self.stop_button.clicked.connect(self.stop_video)
        self.media_player.positionChanged.connect(self.update_timecode_and_progress)
        self.media_player.durationChanged.connect(self.update_duration)
        self.progress_bar.sliderMoved.connect(self.set_position)

        # ========== Боковое меню ==========
        self.side_menu = QWidget(self)
        self.side_menu.setGeometry(QRect(1300, 0, 250, 750))  # За пределами экрана
        self.side_menu.setStyleSheet("background-color: #2E3A46;")

        menu_layout = QVBoxLayout(self.side_menu)

        self.create_account_button = QPushButton("Create Account")
        self.create_account_button.setFixedSize(200, 50)
        self.create_account_button.setStyleSheet("""
            background-color: #4CAF50; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)
        self.create_account_button.clicked.connect(self.open_registration)

        self.login_button = QPushButton("Login")
        self.login_button.setFixedSize(200, 50)
        self.login_button.setStyleSheet("""
            background-color: #4CAF50; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)
        self.login_button.clicked.connect(self.open_registration)

        self.get_premium_button = QPushButton("Get Premium")
        self.get_premium_button.setFixedSize(200, 50)
        self.get_premium_button.setStyleSheet("""
            background-color: #dde00b; color: white; font-size: 16px;
            border: none; border-radius: 5px; padding: 10px 24px;
            cursor: pointer;
        """)

        self.close_menu_button = QPushButton("Close")
        self.close_menu_button.setFixedSize(200, 40)
        self.close_menu_button.setStyleSheet("""
            background-color: #FF3B30; color: white; font-size: 14px;
            border: none; border-radius: 5px;
        """)
        self.close_menu_button.clicked.connect(self.toggle_menu)

        menu_layout.addWidget(self.create_account_button)
        menu_layout.addWidget(self.login_button)
        menu_layout.addWidget(self.get_premium_button)
        menu_layout.addWidget(self.close_menu_button)
        menu_layout.addStretch()

        # Анимация меню
        self.menu_animation = QPropertyAnimation(self.side_menu, b"geometry")

    # ========== Функции управления видео ==========
    def play_video(self):
        video_url = QUrl.fromLocalFile('final_clip_with_subtitles.mp4')
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

    # ========== Функция анимации меню ==========
    def toggle_menu(self):
        if self.side_menu.geometry().x() == 1300:  # Скрыто
            self.menu_animation.setStartValue(QRect(1300, 0, 250, 750))
            self.menu_animation.setEndValue(QRect(1050, 0, 250, 750))  # Показываем
        else:
            self.menu_animation.setStartValue(QRect(1050, 0, 250, 750))
            self.menu_animation.setEndValue(QRect(1300, 0, 250, 750))  # Прячем

        self.menu_animation.setDuration(300)
        self.menu_animation.start()


    def open_registration(self):
        if not self.registration_window or not self.registration_window.isVisible():
            self.registration_window = RegistrationWindow()
            self.registration_window.show()

app = QApplication(sys.argv)
window = VideoPlayer()
window.show()
sys.exit(app.exec())
