"""
Rock-Solid Sequential Word Matcher
Strict sequential progression with proximity weighting and jump dampening.
Prevents skipping ahead, wild jumps, and short-word false triggers.
"""

import re
from typing import List, Optional, Tuple


def normalize_turkish(text: str) -> str:
    """Normalizes Turkish string for instant phonetic matching."""
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


# Common Turkish stop words that should not trigger distant jumps
COMMON_STOP_WORDS = {
    "ve", "veya", "ile", "bir", "bu", "şu", "o", "de", "da", "ki",
    "mi", "mu", "mü", "mı", "en", "çok", "daha", "için", "gibi", "kadar"
}


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
    def __init__(self, script_text: str = "", max_single_jump: int = 4, lookahead_window: int = 15):
        self.script_text = script_text
        self.max_single_jump = max_single_jump
        self.lookahead_window = lookahead_window
        self.tokens: List[ScriptToken] = []
        self.current_index: int = 0
        self.load_script(script_text)

    def load_script(self, script_text: str):
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
        self.set_index(self.current_index + delta)

    def match_spoken_phrase(self, recognized_phrase: str) -> Optional[int]:
        """
        Ultra-stable sequential matching:
        - Strongly favors the immediate next words (index + 1, index + 2).
        - Penalizes distant candidates so it NEVER jumps far ahead.
        - Multi-word confirmation required for larger leaps.
        """
        if not self.tokens or not recognized_phrase.strip():
            return None

        clean_phrase = normalize_turkish(recognized_phrase)
        spoken_words = clean_phrase.split()
        if not spoken_words:
            return None

        cur = self.current_index
        total = len(self.tokens)

        # 1. First priority: Check immediate next words [cur, cur + 1, cur + 2, cur + 3]
        # Compare with the latest spoken word
        latest_spoken = spoken_words[-1]
        
        # Check immediate next 4 words with priority
        immediate_end = min(total, cur + self.max_single_jump + 1)
        for i in range(cur, immediate_end):
            script_clean = self.tokens[i].clean_text
            if not script_clean:
                continue
                
            # Exact or strong prefix match on immediate next words
            if latest_spoken == script_clean or (len(latest_spoken) >= 3 and (latest_spoken.startswith(script_clean) or script_clean.startswith(latest_spoken))):
                self.set_index(i)
                return self.current_index
            
            # High Levenshtein on immediate word
            if len(latest_spoken) >= 4 and len(script_clean) >= 4:
                sim = levenshtein_similarity(latest_spoken, script_clean)
                if sim >= 0.75:
                    self.set_index(i)
                    return self.current_index

        # 2. Multi-word exact sequence check (if spoken_words > 1)
        if len(spoken_words) >= 2:
            search_end = min(total - len(spoken_words) + 1, cur + self.lookahead_window)
            best_multi_idx = None
            best_multi_score = 0.0

            for i in range(cur, search_end):
                score_sum = 0.0
                for k, s_word in enumerate(spoken_words):
                    sc_word = self.tokens[i + k].clean_text
                    if s_word == sc_word:
                        score_sum += 1.0
                    elif len(s_word) >= 3 and (s_word.startswith(sc_word) or sc_word.startswith(s_word)):
                        score_sum += 0.85
                    else:
                        score_sum += levenshtein_similarity(s_word, sc_word)

                avg_score = score_sum / len(spoken_words)
                
                # Distance penalty to prevent jumping across paragraphs
                distance = i - cur
                distance_penalty = distance * 0.02
                adjusted_score = avg_score - distance_penalty

                if adjusted_score > best_multi_score and adjusted_score >= 0.70:
                    best_multi_score = adjusted_score
                    best_multi_idx = i + len(spoken_words) - 1

            if best_multi_idx is not None:
                # Ensure jump is within safe distance
                if best_multi_idx - cur <= self.lookahead_window:
                    self.set_index(best_multi_idx)
                    return self.current_index

        # 3. Fuzzy check on the immediate next 2 words only
        if len(latest_spoken) >= 4 and latest_spoken not in COMMON_STOP_WORDS:
            for i in range(cur, min(total, cur + 3)):
                script_clean = self.tokens[i].clean_text
                if len(script_clean) >= 4:
                    sim = levenshtein_similarity(latest_spoken, script_clean)
                    if sim >= 0.70:
                        self.set_index(i)
                        return self.current_index

        return None
