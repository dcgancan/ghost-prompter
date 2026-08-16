"""
End-to-end check that the real PrompterWindow actually gets macOS stealth.

The unit tests only cover the dispatcher in isolation. This drives the actual
window and reads the state back off the live NSWindow, which is the only way to
know the wiring in prompter_window.py works.

The voice engine is never started, so this does not download a speech model or
touch the microphone.

Run:  .venv/bin/python spike/verify_port.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import objc
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

import stealth
from prompter_window import PrompterWindow
from voice_engine import VoiceEngine
from word_matcher import WordMatcher

NS_WINDOW_SHARING_NONE = 0
NS_WINDOW_SHARING_READ_ONLY = 1
NS_COLLECTION_CAN_JOIN_ALL_SPACES = 1 << 0
NS_COLLECTION_FULL_SCREEN_AUXILIARY = 1 << 8

failures = []


def check(label, actual, expected):
    ok = actual == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: got {actual!r}, expected {expected!r}")
    if not ok:
        failures.append(label)


def ns_window(widget):
    return objc.objc_object(c_void_p=int(widget.winId())).window()


def main():
    if sys.platform != "darwin":
        print("This check is macOS-only.")
        return 0

    app = QApplication(sys.argv)

    matcher = WordMatcher("bir iki üç dört beş")
    # Constructed but never started: the window needs one to connect signals to.
    voice = VoiceEngine(language="tr-TR")
    window = PrompterWindow(matcher, voice)
    window.show()

    def run_checks():
        try:
            win = ns_window(window)

            print("\nBackend")
            check("stealth.backend_name()", stealth.backend_name(), "macos")
            check("stealth.is_stealth_supported()", stealth.is_stealth_supported(), True)

            print("\nStealth on show (showEvent should have applied it)")
            check("NSWindow.sharingType", int(win.sharingType()), NS_WINDOW_SHARING_NONE)
            check("window.is_stealth_active", window.is_stealth_active, True)

            print("\nFloat above full-screen apps")
            behavior = int(win.collectionBehavior())
            check(
                "collectionBehavior has canJoinAllSpaces",
                bool(behavior & NS_COLLECTION_CAN_JOIN_ALL_SPACES),
                True,
            )
            check(
                "collectionBehavior has fullScreenAuxiliary",
                bool(behavior & NS_COLLECTION_FULL_SCREEN_AUXILIARY),
                True,
            )

            print("\nStealth toggle off/on")
            window.toggle_stealth_mode()
            check("sharingType after toggle off", int(win.sharingType()), NS_WINDOW_SHARING_READ_ONLY)
            check("is_stealth_active after toggle off", window.is_stealth_active, False)
            window.toggle_stealth_mode()
            check("sharingType after toggle on", int(win.sharingType()), NS_WINDOW_SHARING_NONE)
            check("is_stealth_active after toggle on", window.is_stealth_active, True)

            print("\nClick-through toggle")
            window.toggle_click_through()
            check("ignoresMouseEvents ON", bool(win.ignoresMouseEvents()), True)
            window.toggle_click_through()
            check("ignoresMouseEvents OFF", bool(win.ignoresMouseEvents()), False)

            print("\nShortcut labels")
            from i18n import I18nManager

            tip = I18nManager.t("btn_restore_size_tip")
            check("restore tip mentions Cmd+0", "Cmd+0" in tip, True)
            check("no leftover placeholder", "%" in tip, False)

            print("\nSpeech advances the prompter (real signal wiring)")
            # The recogniser is known to work on its own; what this checks is
            # that a recognised phrase actually travels engine -> window ->
            # matcher -> canvas and moves the highlight.
            start_index = matcher.current_index
            progress_before = window.progress_lbl.text()
            voice.signals.speech_detected.emit("bir iki üç")
            for _ in range(10):
                app.processEvents()
            check("matcher advanced past 'üç'", matcher.current_index > start_index, True)
            # The canvas keeps no index of its own; it republishes the matcher's
            # position through progress_changed, so a changed label proves the
            # signal reached the UI rather than stopping at the matcher.
            check(
                "progress label updated",
                window.progress_lbl.text() != progress_before,
                True,
            )
        finally:
            app.quit()

    QTimer.singleShot(600, run_checks)
    app.exec()

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s): {', '.join(failures)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
