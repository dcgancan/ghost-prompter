# GhostPrompter — macOS Port

A macOS port of [**muqo16/ghost-prompter**](https://github.com/muqo16/ghost-prompter) by [Muzaffer Ulusoy](https://github.com/muqo16) ([ulusoydigital.com](https://ulusoydigital.com)).

All features, design and original implementation are his. This fork only adds macOS support; the app still runs on Windows exactly as before.

For what GhostPrompter is and how to use it, see the [original repository](https://github.com/muqo16/ghost-prompter).

---

## What this fork changes

- **Stealth mode on macOS** — `NSWindow.sharingType = .none`, the counterpart of the original's `SetWindowDisplayAffinity`. Window stays invisible to screen recorders.
- **Click-through on macOS** — `NSWindow.ignoresMouseEvents`.
- **Floats over full-screen apps** — Qt's always-on-top flag alone does not do this on macOS.
- **`stealth.py` split into per-platform backends** (`stealth_win.py` / `stealth_mac.py`) behind an unchanged API.
- **`requirements.txt` fixed** — `vosk` was missing entirely, and is now pinned to `0.3.44` because `0.3.45` has no macOS wheel. Unused `pyaudio` / `SpeechRecognition` removed.
- **`run.command` launcher**, platform-aware shortcut labels, macOS UI font.

## Run

**macOS**
```bash
./run.command
```
Creates a virtual environment, installs dependencies and downloads the offline speech model on first launch. Allow microphone access when asked.

**Windows** — unchanged, use `run.bat`.

> macOS reserves `F8`, so use **`fn+F8`** or **`⌘⇧C`** for click-through.

## Verification

macOS stealth was tested on macOS 27.0 against four capture paths — `CGWindowList`, `screencapture`, `SCScreenshotManager`, and a live `SCStream` (what OBS, Zoom, Teams and Loom use). The window was excluded from all four.

```bash
.venv/bin/python spike/stealth_spike.py   # re-run the stealth test
.venv/bin/python spike/verify_port.py     # check the port wiring
.venv/bin/python spike/verify_voice.py    # check the microphone path
```

⚠️ Apple has changed capture behaviour before. **Do a real test recording before relying on stealth.**

## License

MIT, © Muzaffer Ulusoy — see [LICENSE](LICENSE). Unchanged from the original.
