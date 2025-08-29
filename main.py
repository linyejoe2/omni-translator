from googletrans import Translator
from langdetect import detect
from gtts import gTTS
import os
import pygame
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
import keyboard
import threading
from datetime import datetime

def detect_language(text):
    return detect(text)

def translate_text(text):
    translator = Translator()
    result = translator.translate(text, dest='zh-tw' if detect_language(text) == 'en' else 'en')
    return result.text

def speak_english(text):
    tts = gTTS(text=text, lang='en')
    filename = "temp_audio.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    time.sleep(0.2)
    pygame.mixer.music.play()

    # 等待播放完成
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.music.unload()
    pygame.mixer.quit()
    os.remove(filename)

def main():
    while True:
        user_input = input("\n請輸入中英文（輸入 'q' 離開）：").strip()
        if user_input.lower() == 'q':
            print("再見！")
            break

        lang = detect_language(user_input)
        print("detect:", lang)
        
        if lang == 'en':
            translation = translate_text(user_input)
            print(f"👉 中文翻譯：{translation}")
            print(f"🔊 正在播放 '{user_input}' 的發音...")
            speak_english(user_input)

        elif lang == 'zh-cn' or lang == 'zh-tw':
            translation = translate_text(user_input)
            print(f"👉 英文翻譯：{translation}")
            print(f"🔊 正在播放 '{translation}' 的發音...")
            speak_english(translation)
        else:
            translation = translate_text(user_input)
            print(f"👉 中文翻譯：{translation}")
            print(f"🔊 正在播放 '{user_input}' 的發音...")
            speak_english(user_input)
            # print("⚠️ 目前僅支援中文與英文。")

if __name__ == "__main__":
    main()
