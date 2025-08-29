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

These need to be installed before running the application:
```bash
pip install googletrans==4.0.0rc1 langdetect gtts pygame
```

## Running the Application

```bash
python main.py
```

The application runs as an interactive console program where users input text and receive:
1. Language detection results
2. Translation to the target language (English ↔ Chinese)
3. Audio pronunciation for English text

## Architecture

The application follows a simple modular structure:

- `detect_language(text)`: Uses langdetect to identify input language
- `translate_text(text)`: Handles bidirectional translation using Google Translate
- `speak_english(text)`: Generates and plays English audio using gTTS and pygame
- `main()`: Interactive loop managing user input and coordinating all functions

## Audio Handling

The TTS functionality creates temporary MP3 files (`temp_audio.mp3`) that are automatically cleaned up after playback. The pygame mixer is properly initialized and cleaned up for each audio session.

## Language Support

Currently supports:
- English (`en`) → Traditional Chinese (`zh-tw`)
- Chinese Simplified (`zh-cn`) and Traditional (`zh-tw`) → English  
- Other detected languages default to Chinese translation with English pronunciation