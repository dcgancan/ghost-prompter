"""
Windows Screen Capture Invisibility (Stealth Mode) & Click-Through Module
Uses Windows Win32 API SetWindowDisplayAffinity to exclude the prompter window
from screen recordings, and SetWindowLongPtr for Click-Through mouse transparency.
"""

import sys
import ctypes
from ctypes import wintypes

# Win32 Constants
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Windows 10 Version 2004+ / Windows 11

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

user32 = None
if sys.platform == "win32":
    try:
        user32 = ctypes.windll.user32
        
        user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
        user32.SetWindowDisplayAffinity.restype = wintypes.BOOL
        
        user32.GetWindowDisplayAffinity.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user32.GetWindowDisplayAffinity.restype = wintypes.BOOL

        # 64-bit and 32-bit window long pointer functions
        if hasattr(user32, "GetWindowLongPtrW"):
            user32.GetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int]
            user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
            user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]
            user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
            _get_long = user32.GetWindowLongPtrW
            _set_long = user32.SetWindowLongPtrW
        else:
            user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
            user32.GetWindowLongW.restype = wintypes.LONG
            user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
            user32.SetWindowLongW.restype = wintypes.LONG
            _get_long = user32.GetWindowLongW
            _set_long = user32.SetWindowLongW

    except Exception as e:
        print(f"[Stealth] Win32 init warning: {e}")


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
            res = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
            if not res:
                res = user32.SetWindowDisplayAffinity(hwnd, WDA_MONITOR)
            return bool(res)
        else:
            res = user32.SetWindowDisplayAffinity(hwnd, WDA_NONE)
            return bool(res)
    except Exception as e:
        print(f"[Stealth] Error setting display affinity: {e}")
        return False


def set_click_through(hwnd: int, enable: bool = True) -> bool:
    """
    Toggles mouse click-through for the given window handle.
    When enable is True, mouse clicks pass directly to the application behind it.
    """
    if user32 is None or not hwnd:
        return False
    try:
        style = _get_long(hwnd, GWL_EXSTYLE)
        if enable:
            new_style = style | WS_EX_TRANSPARENT | WS_EX_LAYERED
        else:
            new_style = style & ~WS_EX_TRANSPARENT
        _set_long(hwnd, GWL_EXSTYLE, new_style)
        return True
    except Exception as e:
        print(f"[Stealth] Error setting click-through: {e}")
        return False
