"""
Unit tests for Rock-Solid WordMatcher and Anti-Jump mechanics
"""

import sys
import unittest
from word_matcher import WordMatcher, normalize_turkish, levenshtein_similarity
import stealth


class TestPrompterCore(unittest.TestCase):
    def test_turkish_normalization(self):
        self.assertEqual(normalize_turkish("Şemsiye"), "semsiye")
        self.assertEqual(normalize_turkish("Çiğdem"), "cigdem")
        self.assertEqual(normalize_turkish("Öğrenci"), "ogrenci")
        self.assertEqual(normalize_turkish("İstanbul!"), "istanbul")
        self.assertEqual(normalize_turkish("Isparta?"), "isparta")

    def test_anti_jump_protection(self):
        script = (
            "Bugün Ulusoy Digital stüdyolarında geliştirdiğimiz yeni nesil ses takipli teleprompter yazılımını inceliyoruz. "
            "Bu uygulamanın en büyük gücü ben konuştukça sesimi kelime kelime takip edip metni tam konuşma hızımda otomatik kaydırması. "
            "Üstelik şu anda ekran kaydı alırken bu prompter penceresi video kaydında kesinlikle görünmüyor. "
            "Otomatik olarak yeni içerikler için bizi takip edin."
        )
        matcher = WordMatcher(script)
        
        # Say first words
        idx = matcher.match_spoken_phrase("bugün ulusoy digital")
        self.assertEqual(idx, 2)  # Points to "digital"
        
        # Say next words
        idx = matcher.match_spoken_phrase("stüdyolarında geliştirdiğimiz")
        self.assertEqual(idx, 4)  # Points to "geliştirdiğimiz"
        
        # Saying "ses takipli teleprompter" matches index 9 ("teleprompter")
        idx = matcher.match_spoken_phrase("ses takipli teleprompter")
        self.assertEqual(idx, 9)
        
        # Saying "otomatik kaydırması" when reached near it (index 27) matches index 29 ("kaydırması")
        matcher.set_index(26)  # Near "konuşma"
        idx = matcher.match_spoken_phrase("otomatik kaydırması")
        self.assertEqual(idx, 29)  # Points cleanly to "kaydırması" at index 29, NOT index 43!

    def test_cursor_can_move_past_last_word(self):
        matcher = WordMatcher("bir iki")
        matcher.set_index(2)
        self.assertEqual(matcher.current_index, 2)

    def test_fast_growing_partial_phrase_uses_its_recent_words(self):
        matcher = WordMatcher("bir iki üç dört beş altı yedi sekiz")
        # First Vosk partial has advanced the cursor past "üç".
        self.assertEqual(matcher.match_spoken_phrase("bir iki üç"), 2)
        matcher.set_index(3)

        # A later partial includes old words and one imperfect recognition,
        # but its recent sequence must still advance to "altı".
        self.assertEqual(
            matcher.match_spoken_phrase("bir iki üç dört bes altı"), 5
        )

    def test_stealth_support(self):
        supported = stealth.is_stealth_supported()
        print(f"\n[Test] Stealth backend: {stealth.backend_name()} (supported: {supported})")
        if sys.platform in ("win32", "darwin"):
            self.assertTrue(supported)

    def test_stealth_backend_selection(self):
        expected = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "unsupported")
        self.assertEqual(stealth.backend_name(), expected)

    def test_stealth_rejects_null_handle(self):
        # A zero handle means the window is not realised yet. Every entry point
        # has to refuse it rather than hand it to a native API.
        self.assertFalse(stealth.set_stealth_mode(0, True))
        self.assertFalse(stealth.set_click_through(0, True))
        self.assertFalse(stealth.set_floating_above_fullscreen(0, True))


if __name__ == "__main__":
    unittest.main()
