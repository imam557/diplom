from moviepy import *
import speech_recognition as sr
from googletrans import Translator 
from gtts import gTTS
import os


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

def final_video():
    translated_audio = AudioFileClip("output.mp3")
    video = VideoFileClip("example.mp4")
    final_clip = video.with_audio(translated_audio)
    final_clip.write_videofile('1final_clip.mp4')

# video_to_audio()
# audio_to_text()
# translate()
# print(translated_text)
# tts()
# final_video()
os.remove("output.mp3")
os.remove("example.wav")