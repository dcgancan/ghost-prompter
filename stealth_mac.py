"""
macOS stealth backend.

Uses NSWindow.sharingType to exclude the prompter window from screen capture -
the macOS counterpart of Windows' SetWindowDisplayAffinity - plus
ignoresMouseEvents for click-through and a collection behaviour that lets the
window float over full-screen apps.

Do not import this module directly - go through `stealth`, which picks the
backend for the current platform.

Verified on macOS 27.0 against four capture paths (CGWindowList, the
`screencapture` tool, SCScreenshotManager, and a live SCStream - the last being
what OBS / Zoom / Teams / Loom actually run). See spike/stealth_spike.py, which
doubles as a regression test when macOS updates.
"""

NAME = "macos"

# NSWindowSharingType
NS_WINDOW_SHARING_NONE = 0
NS_WINDOW_SHARING_READ_ONLY = 1

# NSWindowCollectionBehavior
NS_COLLECTION_CAN_JOIN_ALL_SPACES = 1 << 0
NS_COLLECTION_FULL_SCREEN_AUXILIARY = 1 << 8

objc = None
try:
    import objc  # noqa: F811  (pyobjc; only present on macOS installs)
except Exception as e:
    print(f"[Stealth/mac] pyobjc unavailable: {e}")


def _ns_window(handle: int):
    """Resolve Qt's winId() to the NSWindow behind it.

    On macOS winId() is an NSView*, not a window handle, so we have to hop from
    the view to its window. Returns None if the view is not on a window yet.
    """
    if objc is None or not handle:
        return None
    try:
        view = objc.objc_object(c_void_p=handle)
        return view.window()
    except Exception as e:
        print(f"[Stealth/mac] Could not resolve NSWindow: {e}")
        return None


def is_stealth_supported() -> bool:
    return objc is not None


def set_stealth_mode(handle: int, enable: bool = True) -> bool:
    """Hide the window from screen capture.

    Returns True only if the window reports the sharing type we asked for, so a
    silently-ignored call is reported as a failure rather than as success.
    """
    window = _ns_window(handle)
    if window is None:
        return False

    wanted = NS_WINDOW_SHARING_NONE if enable else NS_WINDOW_SHARING_READ_ONLY
    try:
        window.setSharingType_(wanted)
        return int(window.sharingType()) == wanted
    except Exception as e:
        print(f"[Stealth/mac] Error setting sharing type: {e}")
        return False


def set_click_through(handle: int, enable: bool = True) -> bool:
    """Let mouse clicks pass through to whatever is behind the window."""
    window = _ns_window(handle)
    if window is None:
        return False
    try:
        window.setIgnoresMouseEvents_(bool(enable))
        return True
    except Exception as e:
        print(f"[Stealth/mac] Error setting click-through: {e}")
        return False


def set_floating_above_fullscreen(handle: int, enable: bool = True) -> bool:
    """Keep the prompter visible over full-screen apps and across Spaces.

    Qt's WindowStaysOnTopHint only raises the window above ordinary windows on
    macOS; a full-screen app still covers it. Full-screen sharing is a normal
    way to present, so without this the prompter disappears exactly when it is
    needed.
    """
    window = _ns_window(handle)
    if window is None:
        return False
    try:
        if enable:
            behavior = (
                NS_COLLECTION_CAN_JOIN_ALL_SPACES | NS_COLLECTION_FULL_SCREEN_AUXILIARY
            )
        else:
            behavior = 0
        window.setCollectionBehavior_(behavior)
        return True
    except Exception as e:
        print(f"[Stealth/mac] Error setting collection behavior: {e}")
        return False
