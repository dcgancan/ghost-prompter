"""
Smart Word Matcher and Alignment Engine
Tokenizes prompter text of ANY length without character limits.
Synchronizes spoken speech with script in real-time with zero latency.
"""

import re
from typing import List, Optional, Tuple


def normalize_turkish(text: str) -> str:
    """Normalizes Turkish string for fuzzy phonetic matching."""
    if not text:
        return ""
    
    text = text.replace("İ", "i").replace("I", "ı").lower()
    
    mapping = {
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "i": "i",
        "ö": "o",
        "ş": "s",
        "ü": "u",
        "â": "a",
        "î": "i",
        "û": "u"
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
        
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text.strip()


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Calculates Levenshtein similarity ratio between 0.0 and 1.0."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    if s1 == s2:
        return 1.0
        
    len1, len2 = len(s1), len(s2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
        
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            )
            
    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)


class ScriptToken:
    __slots__ = ('index', 'original_text', 'clean_text', 'line_number', 'is_newline')
    
    def __init__(self, index: int, original_text: str, line_number: int, is_newline: bool = False):
        self.index = index
        self.original_text = original_text
        self.clean_text = normalize_turkish(original_text)
        self.line_number = line_number
        self.is_newline = is_newline

    def __repr__(self):
        return f"Token({self.index}: '{self.original_text}')"


class WordMatcher:
    def __init__(self, script_text: str = "", lookahead_window: int = 25, lookbehind_window: int = 4):
        self.script_text = script_text
        self.lookahead_window = lookahead_window
        self.lookbehind_window = lookbehind_window
        self.tokens: List[ScriptToken] = []
        self.current_index: int = 0
        self.min_similarity_threshold: float = 0.62
        self.load_script(script_text)

    def load_script(self, script_text: str):
        """Tokenizes arbitrary length text with zero limits."""
        self.script_text = script_text
        self.tokens = []
        self.current_index = 0
        
        if not script_text.strip():
            return

        lines = script_text.splitlines()
        token_counter = 0
        
        for line_num, line in enumerate(lines):
            words = line.split()
            for w_idx, word in enumerate(words):
                is_last_in_line = (w_idx == len(words) - 1)
                token = ScriptToken(
                    index=token_counter,
                    original_text=word,
                    line_number=line_num,
                    is_newline=is_last_in_line
                )
                self.tokens.append(token)
                token_counter += 1

    @property
    def total_words(self) -> int:
        return len(self.tokens)

    def reset_progress(self):
        self.current_index = 0

    def set_index(self, index: int):
        self.current_index = max(0, min(index, len(self.tokens) - 1)) if self.tokens else 0

    def advance_by(self, delta: int = 1):
        """Steps forward by delta words."""
        self.set_index(self.current_index + delta)

    def match_spoken_phrase(self, recognized_phrase: str) -> Optional[int]:
        """
        Matches incoming spoken speech with forward lookahead window.
        Returns matched token index or None.
        """
        if not self.tokens or not recognized_phrase.strip():
            return None

        clean_phrase = normalize_turkish(recognized_phrase)
        spoken_words = clean_phrase.split()
        if not spoken_words:
            return None

        start_idx = max(0, self.current_index - self.lookbehind_window)
        end_idx = min(len(self.tokens), self.current_index + self.lookahead_window)

        best_match_idx = None
        best_score = 0.0

        # 1. Multi-word sequence match
        if len(spoken_words) > 1:
            for i in range(start_idx, end_idx - len(spoken_words) + 1):
                score_sum = 0.0
                for k, s_word in enumerate(spoken_words):
                    sc_word = self.tokens[i + k].clean_text
                    if s_word == sc_word:
                        score_sum += 1.0
                    elif s_word.startswith(sc_word) or sc_word.startswith(s_word):
                        score_sum += 0.85
                    else:
                        score_sum += levenshtein_similarity(s_word, sc_word)
                        
                avg_score = score_sum / len(spoken_words)
                if avg_score > best_score and avg_score >= self.min_similarity_threshold:
                    best_score = avg_score
                    best_match_idx = i + len(spoken_words) - 1

        # 2. Single-word lookahead match
        if best_match_idx is None:
            for spoken_word in reversed(spoken_words):
                if len(spoken_word) <= 1:
                    continue
                for i in range(start_idx, end_idx):
                    script_word = self.tokens[i].clean_text
                    if not script_word:
                        continue
                        
                    sim = 0.0
                    if spoken_word == script_word:
                        sim = 1.0
                    elif spoken_word.startswith(script_word) or script_word.startswith(spoken_word):
                        sim = 0.9
                    else:
                        sim = levenshtein_similarity(spoken_word, script_word)
                        
                    if sim > best_score and sim >= self.min_similarity_threshold:
                        best_score = sim
                        best_match_idx = i

        if best_match_idx is not None and best_score >= self.min_similarity_threshold:
            self.set_index(best_match_idx)
            return self.current_index

        return None
