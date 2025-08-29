from googletrans import Translator
from langdetect import detect
from gtts import gTTS
import os
import pygame
import time

def detect_language(text):
    return detect(text)

def translate_text(text):
    translator = Translator()
    lang = detect_language(text)
    # Chinese -> English, anything else -> Traditional Chinese
    dest_lang = 'en' if lang in ['zh-cn', 'zh-tw', 'zh'] else 'zh-tw'
    if dest_lang != "en": lang = "en"
    result = translator.translate(text, dest=dest_lang, src=lang)
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