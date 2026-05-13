import os
import subprocess
import time

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QClipboard, QCursor
from PyQt6.QtWidgets import QApplication

from app.overlay.evdev_hooks import get_cursor_pos


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_session() -> str:
    """Return the actual *display server* (not the Qt platform plugin)."""
    if os.environ.get("WAYLAND_DISPLAY"):
        return "wayland"
    if os.environ.get("DISPLAY"):
        return "x11"
    return "wayland" if "wayland" in os.environ.get("XDG_SESSION_TYPE", "") else "x11"


# Backwards-compat alias
_detect_backend = _detect_session


def _get_primary_selection() -> str:
    """
    Read the PRIMARY selection as plain text.

    On Wayland sessions we ALWAYS prefer wl-paste, even when our app runs as
    XWayland: KWin's X11 clipboard bridge only syncs PRIMARY when an XWayland
    window has focus, so xclip would silently return empty for selections
    made in native Wayland apps.

    Returns an empty string when:
      • the selection holds non-text data (image, PDF, etc.)
      • all tools are missing or time out
      • the underlying bytes can't be decoded as UTF-8

    *Never raises*. This function runs inside a polling QThread; an unhandled
    exception (e.g. UnicodeDecodeError on binary clipboard data) would crash
    the whole app.
    """
    if _detect_session() == "wayland":
        # Probe mime-types first; bail out if there's no text on offer.
        try:
            t = subprocess.run(
                ["wl-paste", "--list-types", "--primary"],
                capture_output=True, text=True, timeout=0.4,
                errors="replace",
            )
            if t.returncode == 0 and "text/" not in t.stdout.lower():
                return ""
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        for cmd in (
            ["wl-paste", "--primary", "--no-newline", "--type", "text/plain"],
            ["wl-paste", "--primary", "--no-newline"],
        ):
            try:
                # capture as bytes so a binary payload never raises during
                # subprocess's automatic UTF-8 decoding; decode manually with
                # 'replace' so junk bytes don't kill the watcher.
                r = subprocess.run(cmd, capture_output=True, timeout=0.5)
                if r.returncode == 0:
                    return r.stdout.decode("utf-8", errors="replace")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
            except OSError:
                continue

    for cmd in (
        ["xclip", "-selection", "primary", "-o"],
        ["xsel", "--primary", "--output"],
    ):
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=0.5)
            if r.returncode == 0:
                return r.stdout.decode("utf-8", errors="replace")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        except OSError:
            continue

    return ""


# ---------------------------------------------------------------------------
# Background polling thread
# ---------------------------------------------------------------------------

class _SubprocessPoller(QThread):
    """Polls PRIMARY selection via subprocess every `interval_ms` ms."""

    got_text = pyqtSignal(str, int, int)   # text, cursor_x, cursor_y

    def __init__(self, interval_ms: int = 300):
        super().__init__()
        self._interval = interval_ms / 1000.0
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            try:
                text = _get_primary_selection().strip()
                if text:
                    x, y = get_cursor_pos()
                    self.got_text.emit(text, x, y)
                else:
                    self.got_text.emit("", 0, 0)
            except Exception as exc:
                # Last-resort safety net so an unexpected error (e.g. a
                # subprocess decoding edge case) can never kill the poller.
                import sys
                print(f"[selection_watcher] poll error: {exc}", file=sys.stderr)
            time.sleep(self._interval)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class SelectionWatcher(QObject):
    """
    Detects PRIMARY selection changes and emits text_selected(text, x, y).

    Strategy:
    • Qt-native (QClipboard.selectionChanged) fires quickly and is accurate.
      Cursor position is captured IMMEDIATELY at the selection-change event
      (before the user can move the mouse away), stored as the pending position,
      and emitted after the debounce fires.
    • Subprocess polling (_SubprocessPoller) runs in a background thread and
      serves as a reliable fallback — particularly important when the app has
      no visible windows (tray mode), where Qt's X11 event processing might
      stall on some systems.

    Both paths share the same debounce timer.  Because the pending position is
    set at first-detection time (not at debounce-fire time), the popup always
    appears near where the cursor was when the selection ended.
    """

    text_selected = pyqtSignal(str, int, int)

    DEBOUNCE_MS = 120   # short enough that the cursor hasn't moved far yet

    def __init__(self, poll_interval_ms: int = 300, parent=None):
        super().__init__(parent)
        self._last_emitted = ""
        self._pending_text = ""
        self._pending_x    = 0
        self._pending_y    = 0

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(self.DEBOUNCE_MS)
        self._debounce.timeout.connect(self._emit_stable)

        # Subprocess poller — always active, works even with no visible windows
        self._poller = _SubprocessPoller(poll_interval_ms)
        self._poller.got_text.connect(self._on_polled)

        # Qt-native as an additional fast path
        clipboard = QApplication.clipboard()
        if clipboard.supportsSelection():
            clipboard.selectionChanged.connect(self._on_qt_changed)

    # ------------------------------------------------------------------
    def start(self):
        self._poller.start()

    def stop(self):
        self._debounce.stop()
        self._poller.stop()
        self._poller.wait(1000)

    # ------------------------------------------------------------------
    def _schedule(self, text: str, x: int, y: int):
        """Queue a new candidate; restart the debounce countdown."""
        if text:
            # Always overwrite pending pos: last detection before debounce fires
            # is the most accurate (closest to when the user finished selecting).
            self._pending_text = text
            self._pending_x    = x
            self._pending_y    = y
            self._debounce.start()   # restart resets the 120 ms window
        else:
            self._debounce.stop()
            self._last_emitted = ""
            self._pending_text = ""

    def _emit_stable(self):
        text = self._pending_text
        if text and text != self._last_emitted:
            self._last_emitted = text
            self.text_selected.emit(text, self._pending_x, self._pending_y)

    # ------------------------------------------------------------------
    def _on_qt_changed(self):
        # Capture cursor position NOW — before the user has a chance to move it.
        text = QApplication.clipboard().text(QClipboard.Mode.Selection).strip()
        x, y = get_cursor_pos()
        self._schedule(text, x, y)

    def _on_polled(self, text: str, x: int, y: int):
        self._schedule(text, x, y)
