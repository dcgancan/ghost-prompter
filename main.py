"""
Main Application Entrypoint
Ulusoy Digital - Muzaffer Ulusoy Teleprompter
Windows Stealth & Voice-Follow Teleprompter
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from word_matcher import WordMatcher
from voice_engine import VoiceEngine
from prompter_window import PrompterWindow
from editor_window import EditorWindow, SAMPLE_SCRIPTS


def main():
    # High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Ulusoy Digital Prompter - Muzaffer Ulusoy")

    # Initial default script
    initial_text = SAMPLE_SCRIPTS["🎬 Ulusoy Digital - YouTube & Video Açılışı"]
    matcher = WordMatcher(initial_text)
    
    # Voice recognition engine (defaults to Turkish tr-TR)
    voice_engine = VoiceEngine(language="tr-TR")

    # Create windows
    prompter_win = PrompterWindow(matcher, voice_engine)
    editor_win = EditorWindow(voice_engine)

    # Signal connections between Editor and Prompter
    prompter_win.open_editor_requested.connect(lambda: (editor_win.show(), editor_win.raise_(), editor_win.activateWindow()))
    
    def on_script_applied(text: str):
        prompter_win.load_new_script(text)
        prompter_win.show()
        prompter_win.raise_()
        prompter_win.activateWindow()

    def on_settings_changed(settings: dict):
        if "theme" in settings:
            prompter_win.canvas.set_theme(settings["theme"])

    editor_win.script_applied.connect(on_script_applied)
    editor_win.settings_changed.connect(on_settings_changed)

    # Show windows
    prompter_win.show()
    
    # Start microphone background listening
    voice_engine.start()

    # Clean shutdown
    def on_app_exit():
        voice_engine.stop()

    app.aboutToQuit.connect(on_app_exit)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
