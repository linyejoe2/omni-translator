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
        
        # Set application icon
        try:
            self.root.iconphoto(True, tk.PhotoImage(file='icon.png'))
        except:
            pass  # Fallback if icon file is not found
        
        # Translation history
        self.history = []
        self.filtered_history = []  # For search filtering
        self.last_result = None
        self.storage = HistoryStorage("translation_history.json")
        
        self.setup_ui()
        self.setup_hotkeys()
        self.load_history()
        self.show_window()
        
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
        
        # History search input
        history_search_frame = ttk.Frame(history_frame)
        history_search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(history_search_frame, text="搜尋:").pack(side=tk.LEFT)
        self.history_search = ttk.Entry(history_search_frame)
        self.history_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.history_search.bind('<KeyRelease>', self.on_history_search)
        
        # History listbox with scrollbar and delete button
        history_scroll_frame = ttk.Frame(history_frame)
        history_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_listbox = tk.Listbox(history_scroll_frame, font=("Arial", 10))
        history_scrollbar = ttk.Scrollbar(history_scroll_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox.bind('<Double-Button-1>', self.on_history_click)
        
        # Delete button frame
        delete_frame = ttk.Frame(history_frame)
        delete_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.delete_button = ttk.Button(delete_frame, text="刪除選取項目", command=self.delete_selected_history)
        self.delete_button.pack(side=tk.LEFT)
        
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
        
        # Pre-lowercase input if it contains uppercase letters (A-Z)
        if any(c.isupper() for c in input_text):
            input_text = input_text.lower()
            # Update the input field to show the lowercased text
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, input_text)
            
        # Check if same as last result
        if self.last_result and input_text == self.last_result['input']:
            self.play_sound_async(self.last_result['english_text'])
            return
        
        # Check if input exists in history
        history_index, existing_result = self.find_in_history(input_text)
        if existing_result:
            # Found in history - display existing result and highlight
            self.display_result(existing_result)
            self.last_result = existing_result
            self.play_sound_async(existing_result['english_text'])
            # Highlight the item in history list
            self.history_listbox.selection_clear(0, tk.END)
            self.history_listbox.selection_set(history_index)
            self.history_listbox.see(history_index)
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
        
        # Update filtered history if no search is active
        if not self.history_search.get():
            self.filtered_history.append(result)
            display_text = f"{result['input']}"
            self.history_listbox.insert(tk.END, display_text)
            self.history_listbox.see(tk.END)
        else:
            # Refresh the filtered view
            self.filter_history(self.history_search.get().lower())
        
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
            if index < len(self.filtered_history):
                result = self.filtered_history[index]
                self.display_result(result)
                self.last_result = result
                # Update search input to match
                self.history_search.delete(0, tk.END)
                self.history_search.insert(0, result['input'])
                
    def on_history_search(self, event):
        search_text = self.history_search.get().lower()
        self.filter_history(search_text)
        
    def delete_selected_history(self):
        """Delete the selected history item"""
        selection = self.history_listbox.curselection()
        if not selection:
            return
            
        # Get the selected index in the filtered list
        filtered_index = selection[0]
        if filtered_index >= len(self.filtered_history):
            return
            
        # Get the selected item from filtered history
        selected_item = self.filtered_history[filtered_index]
        
        # Find and remove from main history
        for i, item in enumerate(self.history):
            if item == selected_item:
                del self.history[i]
                break
        
        # Remove from filtered history and listbox
        del self.filtered_history[filtered_index]
        self.history_listbox.delete(filtered_index)
        
        # Save updated history
        self.save_history()
        
        # Clear description if the deleted item was being displayed
        if self.last_result == selected_item:
            self.description_text.delete(1.0, tk.END)
            self.last_result = None
                
    def play_sound_async(self, text):
        # Play sound in separate thread to avoid blocking UI
        threading.Thread(target=lambda: speak_english(text), daemon=True).start()
        
    def find_in_history(self, input_text):
        """Find existing translation in history by input text"""
        for i, result in enumerate(self.history):
            if result['input'].lower() == input_text.lower():
                return i, result
        return None, None
        
    def filter_history(self, search_text):
        """Filter history based on search text and update the listbox"""
        self.history_listbox.delete(0, tk.END)
        
        if not search_text:
            # Show all history
            self.filtered_history = self.history.copy()
        else:
            # Filter history based on search text
            self.filtered_history = [
                result for result in self.history
                if search_text in result['input'].lower() or 
                   (result.get('translation') and search_text in result['translation'].lower())
            ]
        
        # Populate listbox with filtered results
        for result in self.filtered_history:
            display_text = f"{result['input']}"
            self.history_listbox.insert(tk.END, display_text)
        
    def save_history(self):
        self.storage.save_history(self.history)
            
    def load_history(self):
        self.history = self.storage.load_history()
        self.filtered_history = self.history.copy()  # Initially show all history
                    
        # Populate history listbox
        for result in self.history:
            display_text = f"{result['input']}"
            # display_text = f"[{result['timestamp']}] {result['input'][:30]}{'...' if len(result['input']) > 30 else ''}"
            self.history_listbox.insert(tk.END, display_text)
            
        # Set last result to most recent
        if self.history:
            self.last_result = self.history[-1]
        
    def run(self):
        self.root.mainloop()