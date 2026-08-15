"""
Main Application Entrypoint
Ulusoy Digital - GhostPrompter
Full Bilingual Support (Turkish 🇹🇷 & English 🇺🇸)
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from word_matcher import WordMatcher
from voice_engine import VoiceEngine
from prompter_window import PrompterWindow
from editor_window import EditorWindow
from i18n import I18nManager


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("GhostPrompter - Muzaffer Ulusoy")

    # Initial default script
    initial_samples = I18nManager.get_samples()
    first_key = list(initial_samples.keys())[0]
    initial_text = initial_samples[first_key]
    
    matcher = WordMatcher(initial_text)
    voice_engine = VoiceEngine(language="tr-TR")

    # Create windows
    prompter_win = PrompterWindow(matcher, voice_engine)
    editor_win = EditorWindow(voice_engine)

    # Signal connections
    prompter_win.open_editor_requested.connect(lambda: (editor_win.show(), editor_win.raise_(), editor_win.activateWindow()))
    
    def on_script_applied(text: str):
        prompter_win.load_new_script(text)
        prompter_win.show()
        prompter_win.raise_()
        prompter_win.activateWindow()

    def on_settings_changed(settings: dict):
        if "theme" in settings:
            prompter_win.canvas.set_theme(settings["theme"])

    def on_prompter_lang_switched(lang_code: str):
        editor_win.set_active_language(lang_code)

    def on_editor_lang_switched(lang_code: str):
        prompter_win.set_language(lang_code)

    editor_win.script_applied.connect(on_script_applied)
    editor_win.settings_changed.connect(on_settings_changed)
    editor_win.ui_language_changed.connect(on_editor_lang_switched)
    prompter_win.language_switched.connect(on_prompter_lang_switched)

    # Show windows
    prompter_win.show()
    voice_engine.start()

    def on_app_exit():
        voice_engine.stop()

    app.aboutToQuit.connect(on_app_exit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
