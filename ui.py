import tkinter as tk
from tkinter import ttk, scrolledtext
import keyboard
import threading
from datetime import datetime

from translator import detect_language, translate_text, speak_english, get_word_info
from storage import HistoryStorage

class TranslatorUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Omni Translator")
        self.root.geometry("800x600")
        self.root.attributes('-topmost', True)  # Always on top
        # self.root.withdraw()  # Start hidden
        
        # Translation history
        self.history = []
        self.last_result = None
        self.storage = HistoryStorage("translation_history.json")
        
        self.setup_ui()
        self.setup_hotkeys()
        self.load_history()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="輸入文字:").pack(anchor=tk.W)
        self.input_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.input_entry.pack(fill=tk.X, pady=(5, 0))
        self.input_entry.bind('<Return>', self.on_enter)
        
        # Content frame with history and description
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # History frame (left side)
        history_frame = ttk.LabelFrame(content_frame, text="歷史記錄", padding=5)
        history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # History listbox with scrollbar
        history_scroll_frame = ttk.Frame(history_frame)
        history_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_listbox = tk.Listbox(history_scroll_frame, font=("Arial", 10))
        history_scrollbar = ttk.Scrollbar(history_scroll_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox.bind('<Double-Button-1>', self.on_history_click)
        
        # Description frame (right side)
        desc_frame = ttk.LabelFrame(content_frame, text="翻譯結果", padding=5)
        desc_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.description_text = scrolledtext.ScrolledText(desc_frame, font=("Arial", 11), height=15, wrap=tk.WORD)
        self.description_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_hotkeys(self):
        # Use keyboard library for global hotkey
        keyboard.add_hotkey('ctrl+alt+t', self.toggle_window)
        
    def toggle_window(self):
        if self.root.winfo_viewable():
            self.hide_window()
        else:
            self.show_window()
            
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.input_entry.focus_set()
        
    def hide_window(self):
        self.input_entry.delete(0, tk.END)
        self.root.withdraw()
        
    def on_enter(self, event):
        input_text = self.input_entry.get().strip()
        
        if not input_text:
            # Empty input - replay last sound
            if self.last_result and self.last_result.get('english_text'):
                self.play_sound_async(self.last_result['english_text'])
            return
            
        # Check if same as last result
        if self.last_result and input_text == self.last_result['input']:
            self.play_sound_async(self.last_result['english_text'])
            return
            
        # New translation
        self.process_translation(input_text)
        
    def process_translation(self, text):
        try:
            lang = detect_language(text)
            
            # Get comprehensive word information (translation + dictionary)
            word_info = get_word_info(text, lang)
            
            # Determine which text to speak (always the English text)
            english_text = word_info['translation'] if lang in ['zh-cn', 'zh-tw', 'zh'] else text
            
            # Create result object
            result = {
                'input': text,
                'detected_lang': lang,
                'translation': word_info['translation'],
                'english_text': english_text,
                'dictionary': word_info.get('dictionary'),
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            self.last_result = result
            self.add_to_history(result)
            self.display_result(result)
            self.play_sound_async(english_text)
            
        except Exception as e:
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(tk.END, f"翻譯錯誤: {str(e)}")
            
    def add_to_history(self, result):
        self.history.append(result)
        display_text = f"[{result['timestamp']}] {result['input'][:30]}{'...' if len(result['input']) > 30 else ''}"
        self.history_listbox.insert(tk.END, display_text)
        self.history_listbox.see(tk.END)
        self.save_history()
        
    def display_result(self, result):
        self.description_text.delete(1.0, tk.END)
        
        content = "=== Google 翻譯 ===\n"
        content += f"{result['translation']}\n"
        
        # Add dictionary information if available
        if result.get('dictionary'):
            dict_info = result['dictionary']
            content += "\n=== 劍橋辭典 ===\n"
            
            if dict_info.get('part_of_speech'):
                content += f"詞性: {dict_info['part_of_speech']}\n"
            
            if dict_info.get('pronunciation'):
                content += f"發音: /{dict_info['pronunciation']}/\n"
            
            if dict_info.get('definitions'):
                content += "\n定義:\n"
                for i, definition in enumerate(dict_info['definitions'], 1):
                    content += f"  {i}. {definition}\n"
            
            if dict_info.get('examples'):
                content += "\n例句:\n"
                for i, example in enumerate(dict_info['examples'], 1):
                    content += f"  {i}. {example}\n"
                    
        content += f"\n=== 系統資訊 ===\n"
        content += f"原文: {result['input']}\n"
        content += f"檢測語言: {result['detected_lang']}\n"
        content += f"發音文字: {result['english_text']}\n"
        content += f"時間: {result['timestamp']}\n"
        
        self.description_text.insert(tk.END, content)
        
    def on_history_click(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.history):
                result = self.history[index]
                self.display_result(result)
                self.last_result = result
                
    def play_sound_async(self, text):
        # Play sound in separate thread to avoid blocking UI
        threading.Thread(target=lambda: speak_english(text), daemon=True).start()
        
    def save_history(self):
        self.storage.save_history(self.history)
            
    def load_history(self):
        self.history = self.storage.load_history()
                    
        # Populate history listbox
        for result in self.history:
            display_text = f"[{result['timestamp']}] {result['input'][:30]}{'...' if len(result['input']) > 30 else ''}"
            self.history_listbox.insert(tk.END, display_text)
            
        # Set last result to most recent
        if self.history:
            self.last_result = self.history[-1]
        
    def run(self):
        self.root.mainloop()