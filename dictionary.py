import requests
import re
from typing import Dict, List, Optional

class CambridgeDictionary:
    """Cambridge Dictionary API integration for word definitions and examples"""
    
    def __init__(self):
        # https://dictionary.cambridge.org/zht/%E8%A9%9E%E5%85%B8/%E8%8B%B1%E8%AA%9E-%E6%BC%A2%E8%AA%9E-%E7%B9%81%E9%AB%94/exception?q=exceptions
        self.base_url = "https://dictionary.cambridge.org/dictionary/english/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def lookup_word(self, word: str) -> Optional[Dict]:
        """
        Look up a word in Cambridge Dictionary
        Returns dictionary data with definitions, examples, and pronunciation
        """
        try:
            clean_word = word
            # Clean the word for URL
            # clean_word = re.sub(r'[^\w\s-]', '', word.lower().strip())
            # if not clean_word or len(clean_word.split()) > 2:
            #     return None
                
            url = f"{self.base_url}{clean_word}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
                
            return self._parse_dictionary_page(response.text, word)
            
        except Exception as e:
            print(f"Dictionary lookup error: {e}")
            return None
    
    def _parse_dictionary_page(self, html: str, word: str) -> Optional[Dict]:
        """Parse Cambridge Dictionary HTML page to extract definitions and examples"""
        try:
            result = {
                'word': word,
                'definitions': [],
                'examples': [],
                'pronunciation': '',
                'part_of_speech': ''
            }
            
            # Extract pronunciation (phonetic) - multiple patterns
            pronunciation_patterns = [
                r'<span class="ipa dipa lpr-2 lpl-1">([^<]+)</span>',
                r'<span class="ipa dipa[^>]*">([^<]+)</span>',
                r'<span class="pron dpron[^>]*">.*?<span class="ipa[^>]*">([^<]+)</span>'
            ]
            
            for pattern in pronunciation_patterns:
                pronunciation_match = re.search(pattern, html)
                if pronunciation_match:
                    result['pronunciation'] = pronunciation_match.group(1).strip()
                    break
            
            # Extract part of speech - multiple patterns
            pos_patterns = [
                r'<span class="pos dpos">([^<]+)</span>',
                r'<span class="pos[^>]*">([^<]+)</span>'
            ]
            
            for pattern in pos_patterns:
                pos_match = re.search(pattern, html)
                if pos_match:
                    result['part_of_speech'] = pos_match.group(1).strip()
                    break
            
            # Find pos-body sections which contain the main content
            pos_body_pattern = r'<div class="pos-body">(.*?)</div>\s*</div>\s*</div>'
            pos_body_matches = re.findall(pos_body_pattern, html, re.DOTALL)
            
            definitions = []
            examples = []
            
            for pos_body in pos_body_matches:
                # Extract definitions from def ddef_d db divs
                def_patterns = [
                    r'<div class="def ddef_d db">([^<]*(?:<[^/>]+>[^<]*</[^>]+>[^<]*)*)</div>',
                    r'<div class="def ddef_d db">(.*?)</div>'
                ]
                
                for def_pattern in def_patterns:
                    def_matches = re.findall(def_pattern, pos_body, re.DOTALL)
                    for def_match in def_matches:
                        # Clean up HTML tags and get text content
                        clean_def = re.sub(r'<[^>]+>', '', def_match).strip()
                        if clean_def and len(clean_def) > 3:  # Avoid empty or very short definitions
                            definitions.append(clean_def)
                
                # Extract examples from eg deg spans
                example_patterns = [
                    r'<span class="eg deg">([^<]*(?:<[^/>]+>[^<]*</[^>]+>[^<]*)*)</span>',
                    r'<span class="eg deg">(.*?)</span>'
                ]
                
                for ex_pattern in example_patterns:
                    ex_matches = re.findall(ex_pattern, pos_body, re.DOTALL)
                    for ex_match in ex_matches:
                        # Clean up HTML tags and get text content
                        clean_ex = re.sub(r'<[^>]+>', '', ex_match).strip()
                        if clean_ex and len(clean_ex) > 3:  # Avoid empty or very short examples
                            examples.append(clean_ex)
            
            # Fallback: try broader patterns if pos-body didn't work
            if not definitions:
                def_pattern = r'<div class="def ddef_d db">(.*?)</div>'
                definitions = re.findall(def_pattern, html, re.DOTALL)
                definitions = [re.sub(r'<[^>]+>', '', def_text).strip() for def_text in definitions]
                definitions = [d for d in definitions if d and len(d) > 3]
            
            if not examples:
                example_pattern = r'<span class="eg deg">(.*?)</span>'
                examples = re.findall(example_pattern, html, re.DOTALL)
                examples = [re.sub(r'<[^>]+>', '', ex).strip() for ex in examples]
                examples = [e for e in examples if e and len(e) > 3]
            
            # Limit results and remove duplicates
            result['definitions'] = list(dict.fromkeys(definitions))[:3]
            result['examples'] = list(dict.fromkeys(examples))[:3]
            
            print(f"Dictionary result for '{word}':")
            print(f"  Definitions: {result['definitions']}")
            print(f"  Examples: {result['examples']}")
            print(f"  Pronunciation: {result['pronunciation']}")
            print(f"  Part of speech: {result['part_of_speech']}")
            
            # Only return result if we found at least one definition
            if result['definitions']:
                return result
            return None
            
        except Exception as e:
            print(f"Dictionary parsing error: {e}")
            return None

def get_dictionary_info(word: str) -> Optional[Dict]:
    """
    Convenience function to get dictionary information for a word
    """
    dictionary = CambridgeDictionary()
    return dictionary.lookup_word(word)