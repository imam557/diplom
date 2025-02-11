from moviepy import VideoFileClip, AudioFileClip
from gtts import gTTS
import os
import srt
import random
import speech_recognition as sr
from googletrans import Translator
import ffmpeg

class VideoTransaltor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.audio_path = "example.wav"
        self.translated_audio_path = "output.mp3"
        self.final_video_path = "final_video.mp4"
        self.final_video_with_subtitles_path = "final_video_with_subtitles.mp4"
        self.srt_path = "subtitles.srt"
        self.text = ""
        self.translated_text = ""

    def video_to_audio(self):
        video = VideoFileClip(self.video_path)
        video.audio.write_audiofile(self.audio_path)
        
    def audio_to_text(self):
        r = sr.Recognizer()
        with sr.AudioFile(self.audio_path) as source:
            audio_data = r.record(source)
            self.text = r.recognize_google(audio_data, language="ru-RU")
            print(self.text)
    
    def translate(self):
        translator = Translator
        self.translated_text = translator.translate(self.text, src="ru", dest="en").text

    def tts(self):
        tts = gTTS(text=self.translated_text, lang='en')
        tts.save(self.translated_audio_path)

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
    

    def create_srt(self, text, duration_per_line=4):
        srt_content = []
        modifed_text = self.insert_periods(self.text)
        sentences = self
        start_seconds = 0
        sequence_number = 1
        
        for sentence in sentences:
            duration = 4
            if len(sentence) > 100:
                duration += random.randint(1, 3)
            start_time, end_time = self.generate_timecode(start_seconds, duration)
            srt_content.append(f"{sequence_number}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(sentence.strip())
            srt_content.append("")
            start_seconds += duration
            sequence_number += 1

        try:
            with open(self.srt_path, 'w', encoding='utf-8') as file:
                file.write("\n".join(srt_content))
            print("SRT файл создан успешно!")
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")

    
    def create_final_video(self):
        translated_audio = AudioFileClip(self.translated_audio_path)
        video = VideoFileClip(self.video_path)
        final_clip = video.with_audio(translated_audio)
        final_clip.write_videofile(self.final_video_path, codec="libx264", audio_codec="aac")

    def add_subtitles(self):
        (
            ffmpeg
            .input(self.final_video_path)
            .output(self.final_video_with_subtitles_path, vf=f'subtitles={self.srt_path}')
            .run()
        )

    def clean_up(self):
        os.remove(self.audio_path)
        os.remove(self.translated_audio_path)
        os.remove(self.srt_path)
        os.remove(self.final_video_path)
    
    def run(self):
        self.video_to_audio()
        self.audio_to_text()
        self.translate()
        self.tts()
        self.create_srt()
        self.create_final_video()
        self.add_subtitles()
        self.clean_up()


if __name__ == "__main__":
    translator = VideoTransaltor("example.mp4")
    translator.run()



   
    