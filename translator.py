from googletrans import Translator
from langdetect import detect
from gtts import gTTS
import os
import pygame
import time
from dictionary import get_dictionary_info

def detect_language(text):
    lang =  detect(text)
    if lang in ['zh-cn', 'zh-tw', 'zh']:
        return 'zh-tw'
    else:
        return "en"

def translate_text(text):
    translator = Translator()
    lang = detect_language(text)
    # Chinese -> English, anything else -> Traditional Chinese
    dest_lang = 'en' if lang in ['zh-cn', 'zh-tw', 'zh'] else 'zh-tw'
    if dest_lang != "en": lang = "en"
    result = translator.translate(text, dest=dest_lang, src=lang)
    return result.text

def get_word_info(text, detected_lang):
    """
    Get comprehensive word information including translation and dictionary data
    """
    result = {
        'input': text,
        'detected_lang': detected_lang,
        'translation': translate_text(text),
        'dictionary': None
    }
    
    # Get dictionary info for English words only
    if detected_lang == 'en':  # Single word or two words max
        dictionary_info = get_dictionary_info(text)
        if dictionary_info:
            result['dictionary'] = dictionary_info
    
    return result

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