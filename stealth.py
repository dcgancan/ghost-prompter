"""
Windows Screen Capture Invisibility (Stealth Mode) Module
Uses Windows Win32 API SetWindowDisplayAffinity to exclude the prompter window
from screen recordings (OBS, Loom, Zoom, Windows Screen Recorder, etc.).
"""

import sys
import ctypes
from ctypes import wintypes

# Win32 Constants for SetWindowDisplayAffinity
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Windows 10 Version 2004 (20H1) / Windows 11 and later

user32 = None
if sys.platform == "win32":
    try:
        user32 = ctypes.windll.user32
        user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
        user32.SetWindowDisplayAffinity.restype = wintypes.BOOL
        
        user32.GetWindowDisplayAffinity.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowDisplayAffinity.restype = wintypes.BOOL
    except Exception as e:
        print(f"[Stealth] user32 init warning: {e}")


def is_stealth_supported() -> bool:
    """Returns True if running on Windows with SetWindowDisplayAffinity support."""
    return user32 is not None and hasattr(user32, "SetWindowDisplayAffinity")


def set_stealth_mode(hwnd: int, enable: bool = True) -> bool:
    """
    Toggles stealth mode for the given window handle.
    When enable is True, sets WDA_EXCLUDEFROMCAPTURE (0x11) so screen recorders
    will not capture this window at all.
    """
    if not is_stealth_supported() or not hwnd:
        return False

    try:
        if enable:
            # Try WDA_EXCLUDEFROMCAPTURE first (Windows 10 2004+)
            res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            if not res:
                # Fallback to WDA_MONITOR if 0x11 fails on older Windows 10
                res = user32.SetWindowDisplayAffinity(hwnd, WDA_MONITOR)
            return bool(res)
        else:
            res = user32.SetWindowDisplayAffinity(hwnd, WDA_NONE)
            return bool(res)
    except Exception as e:
        print(f"[Stealth] Error setting display affinity: {e}")
        return False


def get_stealth_mode(hwnd: int) -> int:
    """Gets current affinity status of the window."""
    if not is_stealth_supported() or not hwnd:
        return WDA_NONE
    try:
        affinity = wintypes.DWORD()
        res = user32.GetWindowDisplayAffinity(hwnd, ctypes.byref(affinity))
        if res:
            return affinity.value
    except Exception as e:
        print(f"[Stealth] Error getting display affinity: {e}")
    return WDA_NONE
