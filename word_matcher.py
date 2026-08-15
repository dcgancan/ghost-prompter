"""
Smart Word Matcher and Alignment Engine
Tokenizes prompter text and synchronizes spoken speech with the script in real-time.
Handles Turkish characters, punctuation, pauses, stuttering, and word skips.
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple


def normalize_turkish(text: str) -> str:
    """
    Normalizes Turkish string for fuzzy phonetic matching:
    - Lowercase with Turkish casing (I -> ı, İ -> i)
    - Replaces Turkish diacritics with ASCII equivalents (ç->c, ğ->g, ı->i, ö->o, ş->s, ü->u)
    - Strips punctuation and extra whitespace
    """
    if not text:
        return ""
    
    # Custom Turkish lowercase mapping
    text = text.replace("İ", "i").replace("I", "ı")
    text = text.lower()
    
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
        
    # Remove non-alphanumeric characters (keep basic latin and digits)
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
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost # substitution
            )
            
    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return 1.0 - (distance / max_len)


class ScriptToken:
    def __init__(self, index: int, original_text: str, line_number: int, is_newline: bool = False):
        self.index = index
        self.original_text = original_text
        self.clean_text = normalize_turkish(original_text)
        self.line_number = line_number
        self.is_newline = is_newline
        self.is_read = False
        self.is_active = False

    def __repr__(self):
        return f"Token({self.index}: '{self.original_text}')"


class WordMatcher:
    def __init__(self, script_text: str = "", lookahead_window: int = 15, lookbehind_window: int = 4):
        self.script_text = script_text
        self.lookahead_window = lookahead_window
        self.lookbehind_window = lookbehind_window
        self.tokens: List[ScriptToken] = []
        self.current_index: int = 0
        self.min_similarity_threshold: float = 0.65
        self.load_script(script_text)

    def load_script(self, script_text: str):
        """Tokenizes the raw text into words while keeping track of formatting."""
        self.script_text = script_text
        self.tokens = []
        self.current_index = 0
        
        if not script_text.strip():
            return

        lines = script_text.splitlines()
        token_counter = 0
        
        for line_num, line in enumerate(lines):
            # Split line into words
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
        """Resets pointer back to beginning."""
        self.current_index = 0
        for token in self.tokens:
            token.is_read = False
            token.is_active = False

    def set_index(self, index: int):
        """Manually jumps to a specific word index."""
        self.current_index = max(0, min(index, len(self.tokens) - 1)) if self.tokens else 0
        for i, token in enumerate(self.tokens):
            token.is_read = (i < self.current_index)
            token.is_active = (i == self.current_index)

    def match_spoken_phrase(self, recognized_phrase: str) -> Optional[int]:
        """
        Takes newly recognized speech string (one or several words) and
        finds the best matching position in the script within the search window.
        Returns the new active token index if matched, or None if no confident match.
        """
        if not self.tokens or not recognized_phrase.strip():
            return None

        # Clean and split spoken words
        clean_phrase = normalize_turkish(recognized_phrase)
        spoken_words = clean_phrase.split()
        if not spoken_words:
            return None

        # Define search window around current_index
        start_idx = max(0, self.current_index - self.lookbehind_window)
        end_idx = min(len(self.tokens), self.current_index + self.lookahead_window)

        best_match_idx = None
        best_score = 0.0

        # 1. Try multi-word sequence match first (most accurate)
        if len(spoken_words) > 1:
            for i in range(start_idx, end_idx - len(spoken_words) + 1):
                script_slice = [self.tokens[i + k].clean_text for k in range(len(spoken_words))]
                # Compare concatenated or average word similarity
                score_sum = 0.0
                for s_word, sc_word in zip(spoken_words, script_slice):
                    if s_word == sc_word:
                        score_sum += 1.0
                    elif s_word.startswith(sc_word) or sc_word.startswith(s_word):
                        score_sum += 0.85
                    else:
                        score_sum += levenshtein_similarity(s_word, sc_word)
                avg_score = score_sum / len(spoken_words)
                
                if avg_score > best_score and avg_score >= self.min_similarity_threshold:
                    best_score = avg_score
                    # Point to the last matched word in the sequence
                    best_match_idx = i + len(spoken_words) - 1

        # 2. If no multi-word sequence match found, try matching individual spoken words
        if best_match_idx is None:
            # We check the spoken words from right to left (latest spoken word)
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

        # Update index if a confident match is found
        if best_match_idx is not None and best_score >= self.min_similarity_threshold:
            # Prevent jumping too far backward unless high confidence
            self.set_index(best_match_idx)
            return self.current_index

        return None
