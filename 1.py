from moviepy import VideoFileClip, AudioFileClip
from gtts import gTTS
import os
import srt
import random
import speech_recognition as sr
from googletrans import Translator
import ffmpeg

def video_to_audio():
    video = VideoFileClip("example.mp4")
    video.audio.write_audiofile("example.wav")

def audio_to_text():
    r = sr.Recognizer()
    audio_file_path = "example.wav"
    with sr.AudioFile(audio_file_path) as source:
        audio_data = r.record(source)
        global text
        text = r.recognize_google(audio_data, language="ru-RU")
        print(text)

def translate():
    translator = Translator()
    global translated_text
    translated_text = translator.translate(text, src="ru", dest="en").text

def tts():
    tts = gTTS(text=translated_text, lang='en')
    tts.save("output.mp3")

def generate_timecode(start_seconds, duration):
    start_minutes = start_seconds // 60
    start_seconds = start_seconds % 60
    end_seconds = start_seconds + duration
    end_minutes = end_seconds // 60
    end_seconds = end_seconds % 60
    
    start_time = f"00:{start_minutes:02}:{start_seconds:02},000"
    end_time = f"00:{end_minutes:02}:{end_seconds:02},000"
    
    return start_time, end_time

def insert_periods(text):
    result = ""
    for i, char in enumerate(text):
        if char.isupper() and i != 0:
            result += "."
        result += char
    return result

def split_into_sentences(text):
    return text.split('.')

def create_srt(text, duration_per_line=4):
    srt_content = []
    sentences = split_into_sentences(text)
    start_seconds = 0
    sequence_number = 1
    for sentence in sentences:
        duration = duration_per_line
        if len(sentence) > 100:
            duration += random.randint(1, 3)
        start_time, end_time = generate_timecode(start_seconds, duration)
        srt_content.append(f"{sequence_number}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(sentence.strip())
        srt_content.append("")
        start_seconds += duration
        sequence_number += 1

    try:
        with open('subtitles.srt', 'w', encoding='utf-8') as file:
            file.write("\n".join(srt_content))
        print("SRT файл создан успешно!")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")

def create_final_video():
    translated_audio = AudioFileClip("output.mp3")
    video = VideoFileClip("example.mp4")
    final_clip = video.with_audio(translated_audio)
    final_clip.write_videofile("final_clip.mp4", codec="libx264", audio_codec="aac")

def add_subtitles():
    (
        ffmpeg
        .input('final_clip.mp4')
        .output('final_clip_with_subtitles.mp4', vf='subtitles=subtitles.srt')
        .run()
    )


def clean():
    os.remove("example.wav")
    os.remove("output.mp3")
    os.remove("final_clip.mp4")
    os.remove("subtitles.srt")

video_to_audio()
audio_to_text()
translate()
tts()
modiefied_text = insert_periods(text)   
create_srt(modiefied_text)
create_final_video()
add_subtitles()
clean()