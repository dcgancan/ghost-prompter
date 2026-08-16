"""
Screen Capture Invisibility (Stealth Mode) & Click-Through

Platform-neutral front door. The real work lives in a per-platform backend:

    Windows -> stealth_win.py   SetWindowDisplayAffinity / SetWindowLongPtr
    macOS   -> stealth_mac.py   NSWindow.sharingType / ignoresMouseEvents

Every function takes the value of Qt's `winId()`. That is an HWND on Windows
and an NSView* on macOS; each backend knows what to do with its own. On any
other platform the calls become no-ops that report failure, so the UI can show
the prompter as visible rather than silently pretending it is hidden.
"""

import sys

BACKEND = None

if sys.platform == "win32":
    import stealth_win as BACKEND
elif sys.platform == "darwin":
    import stealth_mac as BACKEND


def backend_name() -> str:
    """Human-readable backend name, e.g. for status text and tests."""
    return getattr(BACKEND, "NAME", "unsupported")


def is_stealth_supported() -> bool:
    """True if this platform can hide the window from screen recorders."""
    if BACKEND is None:
        return False
    return BACKEND.is_stealth_supported()


def set_stealth_mode(handle: int, enable: bool = True) -> bool:
    """Hide (or unhide) the window from screen recorders.

    Returns True only when the platform confirms it took effect.
    """
    if BACKEND is None or not handle:
        return False
    return BACKEND.set_stealth_mode(handle, enable)


def set_click_through(handle: int, enable: bool = True) -> bool:
    """Toggle mouse click-through, so clicks reach the app behind the window."""
    if BACKEND is None or not handle:
        return False
    return BACKEND.set_click_through(handle, enable)


def set_floating_above_fullscreen(handle: int, enable: bool = True) -> bool:
    """Keep the window above full-screen apps.

    Windows gets this from the topmost flag Qt already sets; macOS needs an
    explicit call, which is why this is part of the backend interface.
    """
    if BACKEND is None or not handle:
        return False
    return BACKEND.set_floating_above_fullscreen(handle, enable)
