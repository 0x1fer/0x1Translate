"""
Windows implementation of global hotkey + cursor tracking.

Mirrors the public API of evdev_hooks (init/instance/shutdown/get_cursor_pos +
a `double_ctrl_c` pyqtSignal on the instance) so main_window can stay
platform-agnostic via the hotkey_hooks dispatcher.

Implementation notes:
  • Cursor position uses QCursor.pos() directly. Windows has no equivalent
    of Wayland's "hide pointer from background apps" restriction, so no
    kernel-level tracking is needed.
  • Global Ctrl+C+C is detected via pynput's low-level Win32 keyboard hook
    (SetWindowsHookEx). No admin rights required.
  • pynput's listener runs its callbacks from a background thread; we emit
    `double_ctrl_c` as a pyqtSignal so Qt marshals the slot call back to
    the GUI thread.
"""
from __future__ import annotations

import sys
import time
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QCursor

from app import settings as _settings


_instance: Optional["WinHooks"] = None


def init(parent=None) -> "WinHooks":
    global _instance
    if _instance is None:
        _instance = WinHooks(parent)
        _instance.start()
    return _instance


def instance() -> Optional["WinHooks"]:
    return _instance


def shutdown():
    global _instance
    if _instance is not None:
        _instance.stop()
        _instance = None


def reload_shortcut(parent=None):
    shutdown()
    return init(parent)


def get_cursor_pos() -> tuple[int, int]:
    p = QCursor.pos()
    return p.x(), p.y()


class WinHooks(QObject):
    double_ctrl_c = pyqtSignal()

    DOUBLE_PRESS_MS = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener = None
        self._modifier_held = False
        self._last_trigger_ms = 0.0

        sc = _settings.load().get("shortcut", {})
        self._modifier_name = (sc.get("modifier") or "ctrl").lower()
        self._trigger_letter = ((sc.get("trigger_key") or "C").upper()[:1]) or "C"
        # ASCII letter → VK code (A=0x41..Z=0x5A)
        self._trigger_vk = 0x40 + (ord(self._trigger_letter) - ord("A") + 1) \
            if "A" <= self._trigger_letter <= "Z" else 0x43

    def start(self):
        try:
            from pynput import keyboard
        except ImportError:
            print("[hotkey] pynput not installed. Install via 'pip install pynput'.",
                  file=sys.stderr)
            return

        Key = keyboard.Key
        modifier_keys = _modifier_pynput_keys(self._modifier_name, Key)
        shortcut_label = (
            f"{self._modifier_name.capitalize()}+"
            f"{self._trigger_letter}+{self._trigger_letter}"
        )

        def on_press(key):
            try:
                if key in modifier_keys:
                    self._modifier_held = True
                    return
                vk = getattr(key, "vk", None)
                if self._modifier_held and vk == self._trigger_vk:
                    now_ms = time.monotonic() * 1000.0
                    if self._last_trigger_ms and (now_ms - self._last_trigger_ms) < self.DOUBLE_PRESS_MS:
                        print(f"[hotkey] {shortcut_label} detected", file=sys.stderr)
                        self.double_ctrl_c.emit()
                        self._last_trigger_ms = 0.0
                    else:
                        self._last_trigger_ms = now_ms
            except Exception:
                pass

        def on_release(key):
            try:
                if key in modifier_keys:
                    self._modifier_held = False
            except Exception:
                pass

        try:
            self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self._listener.daemon = True
            self._listener.start()
            print(f"[hotkey] Win32 global hotkey listener active; hotkey {shortcut_label}",
                  file=sys.stderr)
        except Exception as exc:
            print(f"[hotkey] failed to start listener: {exc}", file=sys.stderr)
            self._listener = None

    def stop(self):
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

    def wait(self, msec: int = 0):
        # API-compat with QThread.wait() used by the Linux evdev impl.
        return

    def is_tracking(self) -> bool:
        return self._listener is not None and self._listener.is_alive()

    def current_pos(self) -> tuple[int, int]:
        return get_cursor_pos()


def _modifier_pynput_keys(name: str, Key) -> set:
    name = (name or "ctrl").lower()
    if name == "alt":
        return {Key.alt_l, Key.alt_r, Key.alt}
    if name == "shift":
        return {Key.shift_l, Key.shift_r, Key.shift}
    return {Key.ctrl_l, Key.ctrl_r, Key.ctrl}
