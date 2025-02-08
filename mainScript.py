from moviepy import *
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import ffmpeg
import os
import srt 

class VideoTranslator:
    def __init__(self, video_path, audio_language = "ru-RU", translation_language = "en", srt_path = "subtitles.srt", start_minutes, start_seconds = 0, end_minutes = 0, end_seconds = 0, duration = 0):
        self.video_path = video_path
        self.audio_path = 'example.wav'
        self.tts_path = 'output.mp3'
        self.final_video_path = 'final_clip.mp4'
        self.audio_language = audio_language
        self.translation_language = translation_language
        self.text = ""
        self.translated_text = ""
        self.srt_path = srt_path
        self.start_minutes = start_minutes
        self.start_seconds = start_seconds
        self.end_minutes = end_minutes
        self.end_seconds = end_seconds
        self.duration = duration

    def video_to_audio(self):
        video = VideoFileClip(self.video_path)
        video.audio.write_audiofile(self.audio_path)

    
    def audio_to_text(self):
        recognizer = sr.Recognizer()
        with sr.AudioFile(self.audio_path) as source:
            audio_data = recognizer.record(source)
            self.text = recognizer.recognize_google(audio_data, language = self.audio_language)

    def translate_text(self):
        translator = Translator()
        self.translated_text = translator.translate(self.text, src="ru", dest=self.translation_language).text

    def text_to_speech(self):
        tts = gTTS(text=self.translated_text, lang = self.translation_language)
        tts.save(self.tts_path)
    
    def generate_timecode(self,self.start_seconds, self.duration):
    self.start_minutes = self.start_seconds // 60
    start_seconds = start_seconds % 60
    end_seconds = start_seconds + duration
    end_minutes = end_seconds // 60
    end_seconds = end_seconds % 60
    
    start_time = f"{start_minutes:02}:{start_seconds:02},000"
    end_time = f"{end_minutes:02}:{end_seconds:02},000"
    
    return start_time, end_time