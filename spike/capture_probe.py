"""
Screen capture probe for the macOS stealth spike.

Captures the screen through three different macOS capture paths and reports how
many "marker colored" pixels are visible.  Run as a subprocess so each capture
backend gets a clean process and its own run loop.

Usage:
    python capture_probe.py <cgwindow|screencapture|sck> [--save out.png]

Prints a single JSON line to stdout:
    {"method": "...", "ok": true, "marker_pixels": 12345, "total_pixels": 8294400}
"""

import json
import subprocess
import sys
import tempfile

import numpy as np
import Quartz
from Foundation import NSURL

# The spike window paints itself pure magenta.  No normal desktop content is
# this saturated, so counting these pixels tells us whether the window survived
# the capture.
MARKER_RGB = (255, 0, 255)


def cgimage_to_rgba(cgimg):
    """Render a CGImage into a known RGBA8 buffer (avoids guessing its format)."""
    if cgimg is None:
        return None

    width = Quartz.CGImageGetWidth(cgimg)
    height = Quartz.CGImageGetHeight(cgimg)
    if width == 0 or height == 0:
        return None

    colorspace = Quartz.CGColorSpaceCreateDeviceRGB()
    buf = bytearray(width * height * 4)
    ctx = Quartz.CGBitmapContextCreate(
        buf,
        width,
        height,
        8,
        width * 4,
        colorspace,
        Quartz.kCGImageAlphaPremultipliedLast | Quartz.kCGBitmapByteOrder32Big,
    )
    if ctx is None:
        return None

    Quartz.CGContextDrawImage(ctx, Quartz.CGRectMake(0, 0, width, height), cgimg)
    arr = np.frombuffer(bytes(buf), dtype=np.uint8).reshape(height, width, 4)
    return arr[:, :, :3]


def count_marker(rgb):
    """Count marker-colored pixels.

    The capture pipeline colour-manages the frame, so an exact match is too
    strict.  A loose predicate on the channel relationship is what actually
    survives the round trip.
    """
    if rgb is None:
        return None
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    mask = (r > 180) & (b > 180) & (g < 90)
    return int(mask.sum())


def save_png(rgb, path):
    if rgb is None:
        return
    from PIL import Image  # optional; only used with --save

    Image.fromarray(rgb).save(path)


# --------------------------------------------------------------------------
# Backend A: legacy CoreGraphics window list capture
# --------------------------------------------------------------------------
def capture_cgwindow():
    cgimg = Quartz.CGWindowListCreateImage(
        Quartz.CGRectInfinite,
        Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID,
        Quartz.kCGWindowImageDefault,
    )
    return cgimage_to_rgba(cgimg)


# --------------------------------------------------------------------------
# Backend B: the `screencapture` CLI (the system screenshot path)
# --------------------------------------------------------------------------
def capture_screencapture():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        path = tmp.name
    # -x silences the shutter sound, -o omits window shadows.
    subprocess.run(["screencapture", "-x", "-t", "png", path], check=True)

    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        return None
    cgimg = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    return cgimage_to_rgba(cgimg)


def _get_shareable_content(sck):
    """Fetch SCShareableContent, pumping the run loop until the callback fires."""
    from Foundation import NSRunLoop, NSDate

    state = {"content": None, "error": None, "done": False}

    def on_content(content, error):
        state["content"] = content
        state["error"] = error
        state["done"] = True

    sck.SCShareableContent.getShareableContentWithCompletionHandler_(on_content)

    deadline = NSDate.dateWithTimeIntervalSinceNow_(10.0)
    while not state["done"] and NSDate.date().compare_(deadline) < 0:
        NSRunLoop.currentRunLoop().runMode_beforeDate_(
            "kCFRunLoopDefaultMode", NSDate.dateWithTimeIntervalSinceNow_(0.05)
        )

    if state["error"] is not None:
        raise RuntimeError(f"SCShareableContent error: {state['error']}")
    if state["content"] is None:
        raise RuntimeError("SCShareableContent timed out (Screen Recording permission?)")
    return state["content"]


# --------------------------------------------------------------------------
# Backend C: ScreenCaptureKit one-shot screenshot
# --------------------------------------------------------------------------
def capture_sck():
    import ScreenCaptureKit as sck
    from Foundation import NSRunLoop, NSDate

    content = _get_shareable_content(sck)
    displays = content.displays()
    if not displays or len(displays) == 0:
        raise RuntimeError("no SCDisplay available")
    display = displays[0]

    # An empty exclusion list is the point: we exclude nothing ourselves, so if
    # the window is missing it is the OS honouring sharingType, not our filter.
    content_filter = sck.SCContentFilter.alloc().initWithDisplay_excludingWindows_(
        display, []
    )

    config = sck.SCStreamConfiguration.alloc().init()
    config.setWidth_(display.width())
    config.setHeight_(display.height())
    config.setCapturesAudio_(False)

    shot = {"image": None, "error": None, "done": False}

    def on_image(image, error):
        shot["image"] = image
        shot["error"] = error
        shot["done"] = True

    sck.SCScreenshotManager.captureImageWithFilter_configuration_completionHandler_(
        content_filter, config, on_image
    )

    deadline = NSDate.dateWithTimeIntervalSinceNow_(10.0)
    while not shot["done"] and NSDate.date().compare_(deadline) < 0:
        NSRunLoop.currentRunLoop().runMode_beforeDate_(
            "kCFRunLoopDefaultMode", NSDate.dateWithTimeIntervalSinceNow_(0.05)
        )

    if shot["error"] is not None:
        raise RuntimeError(f"SCScreenshotManager error: {shot['error']}")
    if shot["image"] is None:
        raise RuntimeError("SCScreenshotManager timed out")

    return cgimage_to_rgba(shot["image"])


# --------------------------------------------------------------------------
# Backend D: live SCStream — the continuous-capture path.
#
# This is the one that matters most.  `SCScreenshotManager` (backend C) is a
# one-shot API; OBS, Zoom, Teams and Loom run a live SCStream instead, and the
# reported macOS 15+ regression is specifically about streaming.  Testing only
# the one-shot API would leave the real question unanswered.
# --------------------------------------------------------------------------
def capture_sckstream():
    import ScreenCaptureKit as sck
    import CoreMedia
    import objc
    from Foundation import NSObject, NSRunLoop, NSDate
    from libdispatch import dispatch_queue_create

    content = _get_shareable_content(sck)
    displays = content.displays()
    if not displays or len(displays) == 0:
        raise RuntimeError("no SCDisplay available")
    display = displays[0]

    content_filter = sck.SCContentFilter.alloc().initWithDisplay_excludingWindows_(
        display, []
    )
    config = sck.SCStreamConfiguration.alloc().init()
    config.setWidth_(display.width())
    config.setHeight_(display.height())
    config.setCapturesAudio_(False)
    # Ask for a steady frame rate so we reliably get buffers within the timeout.
    config.setMinimumFrameInterval_(CoreMedia.CMTimeMake(1, 30))

    frames = {"rgb": None, "count": 0}

    class StreamOutput(
        NSObject, protocols=[objc.protocolNamed("SCStreamOutput"), objc.protocolNamed("SCStreamDelegate")]
    ):
        def stream_didOutputSampleBuffer_ofType_(self, stream, sbuf, stype):
            if frames["rgb"] is not None:
                return  # already captured a good frame
            try:
                pixel_buffer = CoreMedia.CMSampleBufferGetImageBuffer(sbuf)
                if pixel_buffer is None:
                    return
                ci = Quartz.CIImage.imageWithCVPixelBuffer_(pixel_buffer)
                if ci is None:
                    return
                ctx = Quartz.CIContext.context()
                cgimg = ctx.createCGImage_fromRect_(ci, ci.extent())
                rgb = cgimage_to_rgba(cgimg)
                if rgb is not None:
                    frames["count"] += 1
                    # Skip the very first frame: the compositor sometimes emits a
                    # stale/blank buffer before the stream settles.
                    if frames["count"] >= 3:
                        frames["rgb"] = rgb
            except Exception:
                pass

        def stream_didStopWithError_(self, stream, error):
            pass

    output = StreamOutput.alloc().init()
    stream = sck.SCStream.alloc().initWithFilter_configuration_delegate_(
        content_filter, config, output
    )

    queue = dispatch_queue_create(b"ghost.spike.sck", None)
    ok, err = stream.addStreamOutput_type_sampleHandlerQueue_error_(
        output, sck.SCStreamOutputTypeScreen, queue, None
    )
    if not ok:
        raise RuntimeError(f"addStreamOutput failed: {err}")

    started = {"done": False, "error": None}

    def on_start(error):
        started["error"] = error
        started["done"] = True

    stream.startCaptureWithCompletionHandler_(on_start)

    deadline = NSDate.dateWithTimeIntervalSinceNow_(15.0)
    while frames["rgb"] is None and NSDate.date().compare_(deadline) < 0:
        NSRunLoop.currentRunLoop().runMode_beforeDate_(
            "kCFRunLoopDefaultMode", NSDate.dateWithTimeIntervalSinceNow_(0.05)
        )

    stopped = {"done": False}

    def on_stop(error):
        stopped["done"] = True

    stream.stopCaptureWithCompletionHandler_(on_stop)
    deadline = NSDate.dateWithTimeIntervalSinceNow_(5.0)
    while not stopped["done"] and NSDate.date().compare_(deadline) < 0:
        NSRunLoop.currentRunLoop().runMode_beforeDate_(
            "kCFRunLoopDefaultMode", NSDate.dateWithTimeIntervalSinceNow_(0.05)
        )

    if started["error"] is not None:
        raise RuntimeError(f"startCapture error: {started['error']}")
    if frames["rgb"] is None:
        raise RuntimeError(f"no frame received (got {frames['count']} raw buffers)")

    return frames["rgb"]


BACKENDS = {
    "cgwindow": capture_cgwindow,
    "screencapture": capture_screencapture,
    "sck": capture_sck,
    "sckstream": capture_sckstream,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in BACKENDS:
        print(json.dumps({"ok": False, "error": f"usage: {sys.argv[0]} {'|'.join(BACKENDS)}"}))
        return 2

    method = sys.argv[1]
    save_path = None
    if "--save" in sys.argv:
        save_path = sys.argv[sys.argv.index("--save") + 1]

    result = {"method": method, "ok": False}
    try:
        if not Quartz.CGPreflightScreenCaptureAccess():
            Quartz.CGRequestScreenCaptureAccess()
            result["error"] = (
                "Screen Recording permission not granted. Grant it in "
                "System Settings > Privacy & Security > Screen & System Audio Recording, "
                "then re-run."
            )
            print(json.dumps(result))
            return 1

        rgb = BACKENDS[method]()
        if rgb is None:
            result["error"] = "capture returned no image"
            print(json.dumps(result))
            return 1

        if save_path:
            save_png(rgb, save_path)

        result["ok"] = True
        result["marker_pixels"] = count_marker(rgb)
        result["total_pixels"] = int(rgb.shape[0] * rgb.shape[1])
        result["size"] = [int(rgb.shape[1]), int(rgb.shape[0])]
    except Exception as exc:  # noqa: BLE001 - spike: report anything that goes wrong
        result["error"] = f"{type(exc).__name__}: {exc}"

    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
