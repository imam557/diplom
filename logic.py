from moviepy import *
import speech_recognition as sr
from googletrans import Translator 
from gtts import gTTS
import os
import srt

class VideoTranslator:
    def __init__(self, video_path, audio_language = "ru-RU", translation_language = "en"):
        self.video_path = video_path
        self.audio_path = "example.wav"
        self.tts_path = "output.mp3"
        self.final_video_path = "final_clip.mp4"
        self.audio_language = audio_language
        self.translation_language = translation_language
        self.text = ""
        self.translated_text = ""

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

    def create_srt(translated_text, video_duration, subttitle_duration = 5):
        sentences = translated_text.split(".")
        subtitles = []

        start_time = 0
        for i, sentences in enumerate(sentences):
            end_time = start_time + subttitle_duration
            
            if end_time > video_duration:
                end_time = video_duration

            subtitles = srt.Subtitle(index = i,
                                    start = srt.timedelta(seconds = start_time),
                                    end = srt.timedelta(seconds = end_time),
                                    content = sentences.strip())
            subtitles.append(subtitles)
            start_time = end_time
        
        return srt.compose(subtitles)
        
    def create_final_video(self):
        translated_audio = AudioFileClip(self.tts_path)
        video = VideoFileClip(self.video_path)
        final_clip = video.with_audio(translated_audio)
        final_clip.write_videofile(self.final_video_path)

    def cleanup(self):
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)
        if os.path.exists(self.tts_path):
            os.remove(self.tts_path)

video_translator = VideoTranslator("example.mp4")
video_translator.video_to_audio()
video_translator.audio_to_text()
video_translator.translate_text()
# video_translator.text_to_speech()
# video_translator.create_final_video()
# video_translator.cleanup()
video_duration = video_translator.get_video_duration()
srt_content = video_translator.create_srt(video_translator.translated_text, video_duration)
print(srt_content)