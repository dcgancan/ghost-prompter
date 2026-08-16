"""
Visual smoke check: render the real prompter window with stealth OFF and
screenshot it.

Stealth is on by default, which means the app is invisible to every screenshot
tool - useful in production, unhelpful when you want to look at the UI. This
shows the same window with sharing enabled so layout and fonts can be reviewed.

Run:  .venv/bin/python spike/screenshot_ui.py [out.png]
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from prompter_window import PrompterWindow
from voice_engine import VoiceEngine
from word_matcher import WordMatcher

SCRIPT = (
    "Herkese merhaba arkadaşlar. Bugün ses takipli teleprompter yazılımını "
    "inceliyoruz. Bu uygulama ben konuştukça metni kelime kelime takip ediyor "
    "ve tam konuşma hızımda otomatik kaydırıyor."
)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ui_preview.png"
    )

    app = QApplication(sys.argv)
    matcher = WordMatcher(SCRIPT)
    voice = VoiceEngine(language="tr-TR")  # constructed, never started
    window = PrompterWindow(matcher, voice)
    window.show()
    window.raise_()

    def shoot():
        try:
            # showEvent turns stealth on; turn it back off so the window can be
            # photographed at all.
            window.apply_stealth_mode(False)
            for _ in range(20):
                app.processEvents()

            import objc

            ns = objc.objc_object(c_void_p=int(window.winId())).window()
            print(f"visible={window.isVisible()} geometry={window.geometry()}")
            print(f"sharingType={int(ns.sharingType())} (1 = shareable)")
            print(f"nsVisible={bool(ns.isVisible())} alpha={float(ns.alphaValue())}")
            print(f"nsFrame={ns.frame()} level={int(ns.level())}")

            # Capture the display the window actually landed on. With more than
            # one monitor Qt may open it on the secondary screen, and
            # `screencapture` grabs only the main display unless told otherwise.
            screen = window.screen() or app.primaryScreen()
            display_index = app.screens().index(screen) + 1
            print(f"capturing display {display_index} ({screen.name()})")

            subprocess.run(
                ["screencapture", "-x", "-D", str(display_index), "-t", "png", out],
                check=True,
            )
            print(f"Wrote {out}")
        finally:
            app.quit()

    QTimer.singleShot(1500, shoot)
    app.exec()


if __name__ == "__main__":
    main()
