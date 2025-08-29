import json
import os

class HistoryStorage:
    def __init__(self, filename="translation_history.json"):
        self.filename = filename
    
    def save_history(self, history):
        """Save translation history to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load translation history from JSON file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading history: {e}")
            return []