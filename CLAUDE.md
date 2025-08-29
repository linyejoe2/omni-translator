# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Omni-translator is a Python-based translation tool that provides bidirectional translation between Chinese (Traditional/Simplified) and English, with text-to-speech functionality for English pronunciation.

## Key Dependencies

The project relies on several external libraries:
- `googletrans`: For translation services
- `langdetect`: For automatic language detection  
- `gtts`: For Google Text-to-Speech functionality
- `pygame`: For audio playback
- `keyboard`: For global hotkey support (Ctrl+Alt+T)
- `requests`: For Cambridge Dictionary web scraping
- `tkinter`: For GUI interface (usually included with Python)

These need to be installed before running the application:
```bash
pip install googletrans==4.0.0rc1 langdetect gtts pygame keyboard requests
```

## Running the Application

```bash
python main.py
```

The application starts with a hidden GUI window. Use **Ctrl+Alt+T** to toggle the window visibility. The GUI provides:
1. Input field for text entry
2. Description area showing translation results
3. History list on the left side for previous translations
4. Auto-focus on input when window appears
5. Input clearing when window is hidden

## UI Usage

- **Ctrl+Alt+T**: Toggle window visibility
- **Enter with text**: Translate input and play pronunciation
- **Enter with empty input**: Replay last translation's pronunciation
- **Double-click history**: View previous translation result
- **History search**: Search through translation history using the search field
- **Click on history item**: Populate search field with selected translation
- Window automatically focuses on input field when shown

## Architecture

The application follows a modular structure with separate concerns:

**translator.py:**
- `detect_language(text)`: Uses langdetect to identify input language
- `translate_text(text)`: Handles bidirectional translation using Google Translate
- `get_word_info(text, lang)`: Comprehensive word analysis with dictionary lookup
- `speak_english(text)`: Generates and plays English audio using gTTS and pygame

**dictionary.py:**
- `CambridgeDictionary`: Web scraper for Cambridge Dictionary
- `lookup_word()`: Extracts definitions, examples, pronunciation, and part of speech
- Supports English words only, with fallback for unavailable entries

**ui.py (TranslatorUI):**
- `setup_ui()`: Creates Tkinter interface with input, description area, and history
- `setup_hotkeys()`: Configures global Ctrl+Alt+T hotkey using keyboard library
- `toggle_window()`: Shows/hides window with proper focus management
- `process_translation()`: Coordinates translation, dictionary lookup, and UI updates
- `display_result()`: Shows translation and dictionary data (definitions, examples)
- `filter_history()`: Filters translation history based on search text
- `on_history_search()`: Handles real-time history search functionality

**storage.py (HistoryStorage):**
- `save_history()` / `load_history()`: JSON-based persistence with UTF-8 support
- Handles dictionary data in translation history

## Audio Handling

The TTS functionality creates temporary MP3 files (`temp_audio.mp3`) that are automatically cleaned up after playback. The pygame mixer is properly initialized and cleaned up for each audio session.

## Language Support

Currently supports:
- English (`en`) → Traditional Chinese (`zh-tw`)
- Chinese Simplified (`zh-cn`) and Traditional (`zh-tw`) → English  
- Korean (`ko`) and Japanese (`ja`) → Traditional Chinese (`zh-tw`)
- Other detected languages default to English translation with English pronunciation
- Enhanced language detection provides dictionary lookup for both input and translated text