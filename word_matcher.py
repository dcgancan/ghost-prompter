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
        # current_index is a cursor: it points at the word to be read next.
        # Keeping ``len(tokens)`` as a valid value lets the UI represent a
        # completed script (all words are marked read) without re-highlighting
        # the final word.
        self.current_index = max(0, min(index, len(self.tokens))) if self.tokens else 0

    def advance_by(self, delta: int = 1):
        self.set_index(self.current_index + delta)

    def match_spoken_phrase(self, recognized_phrase: str) -> Optional[int]:
        """
        Match Vosk's growing partial phrase against the upcoming script.

        A fast speaker commonly produces partials such as ``"bir iki üç dört"``
        after the cursor has already passed ``"bir iki"``.  Matching that full
        phrase only from the cursor loses the sequence.  We therefore align its
        trailing 2–6 words around the cursor and use the end of the best match.
        Single words remain deliberately conservative to avoid false jumps.
        """
        if not self.tokens or not recognized_phrase.strip():
            return None

        clean_phrase = normalize_turkish(recognized_phrase)
        spoken_words = clean_phrase.split()
        if not spoken_words:
            return None

        cur = self.current_index
        total = len(self.tokens)
        if cur >= total:
            return None

        def score_words(spoken: str, script: str) -> float:
            if spoken == script:
                return 1.0
            if min(len(spoken), len(script)) >= 3 and (
                spoken.startswith(script) or script.startswith(spoken)
            ):
                return 0.88
            if min(len(spoken), len(script)) >= 4:
                return levenshtein_similarity(spoken, script)
            return 0.0

        # Sequence alignment is the primary path.  A sequence can safely move
        # farther than a single word, which is essential when the recognizer
        # emits several fast-spoken words in one update.
        max_phrase_words = min(6, len(spoken_words))
        best_match: Optional[Tuple[float, int]] = None
        for count in range(max_phrase_words, 1, -1):
            suffix = spoken_words[-count:]
            first_start = max(0, cur - 3)
            last_start = min(total - count, cur + self.lookahead_window - count + 1)
            for start in range(first_start, last_start + 1):
                end = start + count - 1
                if end < cur:
                    continue

                scores = [
                    score_words(spoken, self.tokens[start + offset].clean_text)
                    for offset, spoken in enumerate(suffix)
                ]
                strong_words = sum(score >= 0.82 for score in scores)
                average = sum(scores) / count

                # Two exact/strong words tolerate one Vosk misrecognition in a
                # fast phrase; a two-word phrase still needs both words solid.
                required_strong = 2
                threshold = 0.64 if count >= 3 else 0.78
                if strong_words < required_strong or average < threshold:
                    continue

                # Favor the closest sequential occurrence when the script has
                # repeated wording, without blocking a confirmed fast jump.
                adjusted = average - max(0, start - cur) * 0.012
                if best_match is None or adjusted > best_match[0]:
                    best_match = (adjusted, end)

        if best_match is not None:
            self.set_index(best_match[1])
            return self.current_index

        # One-word fallback: only inspect the immediately upcoming words.
        # This keeps short/common words from jumping to another paragraph.
        latest_spoken = spoken_words[-1]
        immediate_end = min(total, cur + self.max_single_jump + 1)
        for i in range(cur, immediate_end):
            script_clean = self.tokens[i].clean_text
            if not script_clean:
                continue
            score = score_words(latest_spoken, script_clean)
            if score >= 1.0 or (
                latest_spoken not in COMMON_STOP_WORDS and score >= 0.76
            ):
                self.set_index(i)
                return self.current_index

        return None
