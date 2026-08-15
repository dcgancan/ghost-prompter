"""
GUI Integration Verification Script
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from word_matcher import WordMatcher
from voice_engine import VoiceEngine
from prompter_window import PrompterWindow
from editor_window import EditorWindow


def test_gui_lifecycle():
    app = QApplication.instance() or QApplication(sys.argv)
    
    script = "Bu bir test konuşma metnidir. Teleprompter harika çalışıyor."
    matcher = WordMatcher(script)
    voice_engine = VoiceEngine(language="tr-TR")
    
    prompter = PrompterWindow(matcher, voice_engine)
    editor = EditorWindow(voice_engine)
    
    prompter.show()
    editor.show()
    
    # Test layout and active word update
    prompter.canvas.update_active_word(2)
    assert prompter.matcher.current_index == 2
    
    # Test font resize
    prompter.adjust_font_size(4)
    
    # Test theme change
    prompter.canvas.set_theme("Gold")
    
    # Test mirror toggle
    prompter.canvas.toggle_mirror_h()
    
    # Test stealth toggle
    prompter.toggle_stealth_mode()
    
    print("[GUI Test] All GUI widgets, canvas layout, and event handlers initialized successfully!")
    
    # Close after 500ms
    QTimer.singleShot(500, app.quit)
    app.exec()


if __name__ == "__main__":
    test_gui_lifecycle()
