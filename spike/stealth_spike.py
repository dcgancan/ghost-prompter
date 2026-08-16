"""
macOS stealth spike for GhostPrompter.

Question this answers: does `NSWindow.sharingType = .none` (the macOS analogue of
Windows' SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)) still hide a window
from screen capture on this machine?

Method: show a PyQt6 window painted a marker colour, then capture the screen
through three different macOS capture paths, twice:

    control : sharingType = .readOnly  -> the window MUST appear (validates the
                                          detector; if it doesn't, the test
                                          itself is broken)
    test    : sharingType = .none      -> does the window still appear?

Run:  .venv/bin/python spike/stealth_spike.py
"""

import json
import os
import subprocess
import sys

import objc
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter
from PyQt6.QtWidgets import QApplication, QWidget

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE = os.path.join(HERE, "capture_probe.py")

# AppKit NSWindowSharingType
NS_WINDOW_SHARING_NONE = 0
NS_WINDOW_SHARING_READ_ONLY = 1

MARKER_COLOR = QColor(255, 0, 255)
METHODS = ["cgwindow", "screencapture", "sck", "sckstream"]


class MarkerWindow(QWidget):
    """A big, unmistakable block of colour that stands in for the prompter."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setGeometry(200, 200, 900, 500)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), MARKER_COLOR)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont("Helvetica", 40, QFont.Weight.Bold))
        painter.drawText(
            self.rect(), Qt.AlignmentFlag.AlignCenter, "GHOST SPIKE\nmarker window"
        )

    def ns_window(self):
        """The NSWindow backing this Qt widget (winId() is an NSView* on macOS)."""
        view = objc.objc_object(c_void_p=int(self.winId()))
        return view.window()

    def set_sharing_type(self, value: int) -> int:
        win = self.ns_window()
        win.setSharingType_(value)
        return int(win.sharingType())


def run_probe(method: str, save_path: str | None = None) -> dict:
    cmd = [sys.executable, PROBE, method]
    if save_path:
        cmd += ["--save", save_path]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    line = proc.stdout.strip().splitlines()
    if not line:
        return {"method": method, "ok": False, "error": f"no output (stderr: {proc.stderr.strip()[:300]})"}
    try:
        return json.loads(line[-1])
    except json.JSONDecodeError:
        return {"method": method, "ok": False, "error": f"bad output: {line[-1][:300]}"}


def run_phase(window: MarkerWindow, app: QApplication, label: str, sharing: int) -> dict:
    applied = window.set_sharing_type(sharing)
    # Give the compositor a moment to pick up the new sharing type, and let Qt
    # finish painting before anything grabs the screen.
    for _ in range(20):
        app.processEvents()

    print(f"\n=== {label}: sharingType requested={sharing} applied={applied} ===")
    if applied != sharing:
        print(f"  !! sharingType did not stick (wanted {sharing}, got {applied})")

    results = {}
    for method in METHODS:
        out = os.path.join(HERE, f"capture_{label}_{method}.png")
        res = run_probe(method, out)
        results[method] = res
        if res.get("ok"):
            px = res["marker_pixels"]
            total = res["total_pixels"]
            verdict = "VISIBLE" if px > 1000 else "hidden"
            print(f"  {method:<14} {verdict:<8} marker_pixels={px:,} / {total:,}")
        else:
            print(f"  {method:<14} ERROR    {res.get('error')}")
    return results


def report(control: dict, test: dict, restore: dict):
    print("\n" + "=" * 68)
    print("RESULT")
    print("=" * 68)
    print()

    for method in METHODS:
        c = control.get(method, {})
        t = test.get(method, {})
        r = restore.get(method, {})

        if not (c.get("ok") and t.get("ok") and r.get("ok")):
            print(f"  {method:<14} INCONCLUSIVE - a capture errored")
            continue

        c_px, t_px, r_px = c["marker_pixels"], t["marker_pixels"], r["marker_pixels"]

        if c_px <= 1000:
            # The detector never saw the window even with sharing enabled, so
            # nothing below it can be trusted for this backend.
            print(f"  {method:<14} INVALID - control never saw the window ({c_px} px)")
        elif r_px <= 1000:
            # Sharing was turned back on but the window did not come back, which
            # means it stopped being visible for some unrelated reason.
            print(f"  {method:<14} INVALID - window did not reappear after restore")
        elif t_px > 1000:
            print(f"  {method:<14} STEALTH FAILS - captured with sharingType=none ({t_px:,} px)")
        else:
            print(
                f"  {method:<14} STEALTH WORKS - "
                f"control {c_px:,} -> none {t_px:,} -> restored {r_px:,}"
            )

    print("\n  sckstream = a live SCStream, which is what OBS / Zoom / Teams / Loom")
    print("  and the macOS screen recorder actually run. That row is the verdict.")
    print("  sck is the one-shot screenshot API; useful, but not what recorders use.")
    print("  The restore column rules out occlusion: the window has to come back.")
    print("  PNGs of every capture were written next to this script.\n")


def main():
    app = QApplication(sys.argv)
    window = MarkerWindow()
    window.show()
    window.raise_()

    result = {}

    def go():
        try:
            control = run_phase(window, app, "control", NS_WINDOW_SHARING_READ_ONLY)
            test = run_phase(window, app, "test", NS_WINDOW_SHARING_NONE)
            # Flip sharing back on without touching anything else.  If the marker
            # reappears, the window was on screen and on top the whole time, so
            # the "hidden" result above was sharingType and not occlusion.
            restore = run_phase(window, app, "restore", NS_WINDOW_SHARING_READ_ONLY)
            report(control, test, restore)
        finally:
            result["done"] = True
            app.quit()

    # Let the window actually appear before the first capture.
    QTimer.singleShot(1200, go)
    app.exec()


if __name__ == "__main__":
    main()
