from moviepy import VideoFileClip, AudioFileClip
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import ffmpeg
import os
import srt
from datetime import timedelta

class VideoTranslator:
    def __init__(self, video_path, audio_language="ru-RU", translation_language="en", srt_path="subtitles.srt"):
        self.video_path = video_path
        self.audio_path = "example.wav"
        self.tts_path = "output.mp3"
        self.final_video_path = "final_clip.mp4"
        self.audio_language = audio_language
        self.translation_language = translation_language
        self.text = ""
        self.translated_text = ""
        self.srt_path = srt_path
    
    def video_to_audio(self):
        video = VideoFileClip(self.video_path)
        video.audio.write_audiofile(self.audio_path)
    
    def audio_to_text(self):
        recognizer = sr.Recognizer()
        with sr.AudioFile(self.audio_path) as source:
            audio_data = recognizer.record(source)
            self.text = recognizer.recognize_google(audio_data, language=self.audio_language)
    
    def translate_text(self):
        translator = Translator()
        self.translated_text = translator.translate(self.text, src="ru", dest=self.translation_language).text
    
    def text_to_speech(self):
        tts = gTTS(text=self.translated_text, lang=self.translation_language)
        tts.save(self.tts_path)
    
    def create_srt(self, subtitle_duration=5):
        sentences = self.translated_text.split(".")
        subtitles = []
        start_time = 0
        video_duration = VideoFileClip(self.video_path).duration

        words_per_second = len(self.translated_text.split()) / video_duration
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            word_count = len(sentence.split())
            end_time = start_time+max(subtitle_duration, word_count/words_per_second)

            if end_time>video_duration:
                end_time = video_duration

            subtitle = srt.Subtitle(
                index = i,
                start = timedelta(seconds=start_time),
                end = timedelta(seconds=end_time),
                content = sentence
            )
            subtitles.append(subtitle)
            start_time = end_time
        
        with open(self.srt_path, "w", encoding="utf-8") as f:
            f.write(srt.compose(subtitles))

    def add_subtitles(self):  
        (
            ffmpeg
            .input(self.video_path)
            .output(self.final_video_path, vf=f"subtitles={self.srt_path}")
            .run(overwrite_output=True)
        )
    
    def create_final_video(self):
        translated_audio = AudioFileClip(self.tts_path)
        video = VideoFileClip(self.video_path)
        video = video.with_audio(translated_audio) 
        video.write_videofile(self.final_video_path, codec="libx264", audio_codec="aac")
    
    def clear_files(self):
        os.remove(self.audio_path)
        os.remove(self.tts_path)
        # os.remove(self.srt_path)


video_translator = VideoTranslator("example.mp4")
video_translator.video_to_audio()
video_translator.audio_to_text()
video_translator.translate_text()
video_translator.text_to_speech()
video_translator.create_srt()
video_translator.create_final_video()
video_translator.add_subtitles()
video_translator.clear_files()
