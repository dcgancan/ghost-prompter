"""
Windows stealth backend.

Uses SetWindowDisplayAffinity to exclude the prompter window from screen
recordings, and SetWindowLongPtr to toggle mouse click-through.

Do not import this module directly - go through `stealth`, which picks the
backend for the current platform.
"""

import ctypes
from ctypes import wintypes

# Win32 constants
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Windows 10 version 2004+ / Windows 11

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT = 0x00000020
WS_EX_LAYERED = 0x00080000

NAME = "windows"

user32 = None
_get_long = None
_set_long = None

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
    print(f"[Stealth/win] Win32 init warning: {e}")


def is_stealth_supported() -> bool:
    return user32 is not None and hasattr(user32, "SetWindowDisplayAffinity")


def set_stealth_mode(handle: int, enable: bool = True) -> bool:
    """`handle` is an HWND. Sets WDA_EXCLUDEFROMCAPTURE so recorders skip us."""
    if not is_stealth_supported() or not handle:
        return False

    try:
        if enable:
            res = user32.SetWindowDisplayAffinity(handle, WDA_EXCLUDEFROMCAPTURE)
            if not res:
                res = user32.SetWindowDisplayAffinity(handle, WDA_MONITOR)
            return bool(res)
        res = user32.SetWindowDisplayAffinity(handle, WDA_NONE)
        return bool(res)
    except Exception as e:
        print(f"[Stealth/win] Error setting display affinity: {e}")
        return False


def set_click_through(handle: int, enable: bool = True) -> bool:
    """Lets mouse clicks pass through to whatever is behind the window."""
    if user32 is None or _get_long is None or not handle:
        return False
    try:
        style = _get_long(handle, GWL_EXSTYLE)
        if enable:
            new_style = style | WS_EX_TRANSPARENT | WS_EX_LAYERED
        else:
            new_style = style & ~WS_EX_TRANSPARENT
        _set_long(handle, GWL_EXSTYLE, new_style)
        return True
    except Exception as e:
        print(f"[Stealth/win] Error setting click-through: {e}")
        return False


def set_floating_above_fullscreen(handle: int, enable: bool = True) -> bool:
    """No-op on Windows.

    WS_EX_TOPMOST (which Qt already applies for WindowStaysOnTopHint) is enough
    here; the macOS backend needs an extra call to reach the same result.
    """
    return True
