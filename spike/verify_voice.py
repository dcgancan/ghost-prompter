"""
Does audio actually reach the recogniser on this machine?

Everything else in the port was verified by reading state back off the window.
The voice path cannot be checked that way: macOS answers a denied microphone
with a stream of digital silence rather than an error, so "no exception" proves
nothing. This measures the signal itself.

Reports, in order:
  1. the input stream opened at all
  2. frames are arriving
  3. those frames are not pure silence  <- catches a denied mic permission
  4. Vosk decodes words from them       <- needs you to actually speak

Run:  .venv/bin/python spike/verify_voice.py [seconds]
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import sounddevice as sd
from PyQt6.QtCore import QCoreApplication

from voice_engine import VoiceEngine

DURATION = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0


def main():
    # VoiceEngine emits its results as Qt signals from a worker thread. Those
    # are queued and only delivered while an event loop is pumping, so without
    # a QCoreApplication here every recognised word would be silently dropped
    # and a working engine would look broken.
    app = QCoreApplication(sys.argv)
    print("Input devices:")
    for idx, name in VoiceEngine.get_microphone_list():
        print(f"  [{idx}] {name}")
    try:
        print(f"Default input: {sd.query_devices(kind='input')['name']}\n")
    except Exception as e:
        print(f"Default input: unavailable ({e})\n")

    stats = {"frames": 0, "peak": 0.0, "sum_sq": 0.0, "samples": 0, "recent_peak": 0.0}
    words = []
    errors = []

    engine = VoiceEngine(language="tr-TR")
    engine.signals.speech_detected.connect(lambda p: words.append(p))
    engine.signals.error_occurred.connect(lambda e: errors.append(e))
    engine.signals.status_changed.connect(lambda s: print(f"  status: {s}"))

    # Tap the audio callback to measure the raw signal before Vosk sees it.
    original_callback = engine._audio_callback

    def measuring_callback(indata, frames, time_info, status):
        pcm = np.frombuffer(bytes(indata), dtype=np.int16)
        if pcm.size:
            frame_peak = float(np.abs(pcm).max())
            stats["frames"] += 1
            stats["peak"] = max(stats["peak"], frame_peak)
            stats["recent_peak"] = max(stats["recent_peak"], frame_peak)
            stats["sum_sq"] += float(np.sum(pcm.astype(np.float64) ** 2))
            stats["samples"] += pcm.size
        original_callback(indata, frames, time_info, status)

    engine._audio_callback = measuring_callback

    print(f"\nGet ready -- you will have {DURATION:.0f}s to speak.")
    for n in (3, 2, 1):
        print(f"  {n}...", flush=True)
        time.sleep(1)
    print("  SPEAK NOW (Turkish)\n", flush=True)

    engine.start()

    # A live meter makes it obvious whether the voice is actually landing, which
    # a single number at the end cannot show.
    deadline = time.time() + DURATION
    last_word_count = 0
    while time.time() < deadline:
        # Pump the event loop so queued cross-thread signals actually arrive.
        end = time.time() + 0.5
        while time.time() < end:
            app.processEvents()
            time.sleep(0.01)
        peak_pct_now = stats["peak"] / 32768 * 100
        peak_pct_now = stats["recent_peak"] / 32768 * 100
        stats["recent_peak"] = 0.0  # instantaneous level, not a running maximum
        bar = "#" * min(40, int(peak_pct_now * 2))
        line = f"  level {peak_pct_now:5.1f}% |{bar:<40}|"
        if len(words) > last_word_count:
            last_word_count = len(words)
            line += f"  -> {words[-1][:40]}"
        print(line, flush=True)

    engine.stop()
    time.sleep(0.3)

    rms = (stats["sum_sq"] / stats["samples"]) ** 0.5 if stats["samples"] else 0.0
    peak_pct = stats["peak"] / 32768 * 100

    print("\n" + "=" * 60)
    print(f"  frames captured : {stats['frames']}")
    print(f"  peak amplitude  : {peak_pct:.2f}% of full scale")
    print(f"  RMS             : {rms:.1f}")
    print(f"  recognised      : {words[-1] if words else '(nothing)'}")
    if errors:
        print(f"  errors          : {errors}")
    print("=" * 60)

    if stats["frames"] == 0:
        print("\nFAIL: no audio frames. The input stream never delivered anything.")
        return 1
    if stats["peak"] == 0:
        print(
            "\nFAIL: frames arrived but every sample is zero -- digital silence.\n"
            "That is what a denied microphone permission looks like on macOS.\n"
            "Check System Settings > Privacy & Security > Microphone."
        )
        return 1
    if not words:
        print(
            "\nPARTIAL: real audio is reaching the recogniser, but no words were\n"
            "decoded. Fine if nobody spoke; a problem if someone did."
        )
        return 0

    print("\nPASS: audio is live and Vosk decoded speech from it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
