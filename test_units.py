"""
Unit tests for WordMatcher and Stealth modules
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

    def test_levenshtein_similarity(self):
        self.assertEqual(levenshtein_similarity("merhaba", "merhaba"), 1.0)
        self.assertGreater(levenshtein_similarity("arkadaslar", "arkadas"), 0.6)
        self.assertLess(levenshtein_similarity("araba", "bilgisayar"), 0.3)

    def test_word_matcher_tracking(self):
        script = "Herkese merhaba arkadaşlar. Bugün sizlerle beraber yeni bir proje inceliyoruz."
        matcher = WordMatcher(script)
        
        self.assertEqual(matcher.total_words, 10)
        self.assertEqual(matcher.current_index, 0)
        
        # Match first phrase
        idx = matcher.match_spoken_phrase("herkese merhaba")
        self.assertIsNotNone(idx)
        self.assertEqual(idx, 1)  # Points to "merhaba"
        
        # Match next phrase
        idx = matcher.match_spoken_phrase("arkadaşlar bugün sizlerle")
        self.assertIsNotNone(idx)
        self.assertEqual(idx, 4)  # Points to "sizlerle"
        
        # Match with a skipped word or slight speech typo
        idx = matcher.match_spoken_phrase("yeni proje inceliyoruz")
        self.assertIsNotNone(idx)
        self.assertEqual(idx, 9)  # Points to "inceliyoruz"

    def test_stealth_support(self):
        supported = stealth.is_stealth_supported()
        print(f"\n[Test] Windows Stealth Display Affinity Supported: {supported}")
        if sys.platform == "win32":
            self.assertTrue(supported)


if __name__ == "__main__":
    unittest.main()
