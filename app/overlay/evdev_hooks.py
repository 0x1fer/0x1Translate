"""
Bypass Wayland's focus restrictions by reading /dev/input/event* directly.

Wayland (and therefore XWayland) deliberately hides cursor position and global
keystrokes from background apps. Reading the evdev devices skips this layer:
the kernel reports raw mouse motion and key presses to every reader that has
permission. This module uses that capability for two things:

  1. Cursor tracking — accumulate relative mouse motion to maintain an
     absolute cursor position that stays fresh even when a native Wayland
     app has pointer focus. The starting point comes from xdotool, after
     which evdev keeps it in sync.

  2. Global Ctrl+C+C detection — fire the `double_ctrl_c` signal when
     Ctrl+C is pressed twice within 500 ms in *any* application.

Requires the running user to be in the `input` group (default on most
distros). If devices can't be opened the thread exits silently and the
get_cursor_pos fallback transparently switches to xdotool.
"""
from __future__ import annotations

import select
import subprocess
import time
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QGuiApplication

from app import settings as _settings


# ---------------------------------------------------------------------------
# Module-level singleton (created by init(), accessed via instance())
# ---------------------------------------------------------------------------
_instance: Optional["EvdevHooks"] = None


def init(parent=None) -> "EvdevHooks":
    global _instance
    if _instance is None:
        _instance = EvdevHooks(parent)
        _instance.start()
    return _instance


def instance() -> Optional["EvdevHooks"]:
    return _instance


def shutdown():
    global _instance
    if _instance is not None:
        _instance.stop()
        _instance.wait(1000)
        _instance = None


def reload_shortcut(parent=None):
    """Restart the listener so it picks up the new shortcut from settings.json."""
    shutdown()
    return init(parent)


def get_cursor_pos() -> tuple[int, int]:
    """Current cursor position. Prefers our evdev tracker; falls back to xdotool."""
    if _instance is not None and _instance.is_tracking():
        return _instance.current_pos()
    return _xdotool_pos()


# ---------------------------------------------------------------------------
# Worker thread
# ---------------------------------------------------------------------------
class EvdevHooks(QThread):
    double_ctrl_c = pyqtSignal()

    DOUBLE_PRESS_MS = 500

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._tracking = False        # True once at least one device is open
        x, y = _xdotool_pos()
        self._x, self._y = x, y
        screen = QGuiApplication.primaryScreen().geometry()
        self._sx_min, self._sy_min = screen.left(),  screen.top()
        self._sx_max, self._sy_max = screen.right(), screen.bottom()

        sc = _settings.load().get("shortcut", {})
        self._modifier_name = sc.get("modifier", "ctrl")
        self._trigger_letter = (sc.get("trigger_key") or "C").upper()[:1] or "C"

    # ------------------------------------------------------------------
    def stop(self):
        self._running = False

    def is_tracking(self) -> bool:
        return self._tracking

    def current_pos(self) -> tuple[int, int]:
        return self._x, self._y

    # ------------------------------------------------------------------
    def run(self):
        import sys
        try:
            import evdev
            from evdev import ecodes
        except ImportError:
            print("[evdev] python-evdev not installed in this Python environment.",
                  "Install via 'pip install evdev' or pacman.", file=sys.stderr)
            return

        modifier_codes = _modifier_keycodes(self._modifier_name, ecodes)
        trigger_code = _trigger_keycode(self._trigger_letter, ecodes)
        modifier_probe = next(iter(modifier_codes))   # any one is enough to identify keyboards

        keyboards: list = []
        mice:      list = []
        perm_err = 0
        for path in evdev.list_devices():
            try:
                dev = evdev.InputDevice(path)
                caps = dev.capabilities()

                keys = caps.get(ecodes.EV_KEY, [])
                if trigger_code in keys and modifier_probe in keys:
                    keyboards.append(dev)

                rels = caps.get(ecodes.EV_REL, [])
                if ecodes.REL_X in rels and ecodes.REL_Y in rels:
                    mice.append(dev)
            except PermissionError:
                perm_err += 1
                continue
            except OSError:
                continue
            except Exception:
                continue

        devices = list({d.path: d for d in keyboards + mice}.values())
        if not devices:
            if perm_err:
                print(f"[evdev] {perm_err} device(s) refused (PermissionError). "
                      f"Add yourself to the 'input' group and re-login: "
                      f"'sudo usermod -aG input $USER'", file=sys.stderr)
            else:
                print("[evdev] no usable input devices found.", file=sys.stderr)
            return

        shortcut_label = f"{self._modifier_name.capitalize()}+{self._trigger_letter}+{self._trigger_letter}"
        print(f"[evdev] watching {len(keyboards)} keyboard(s) "
              f"and {len(mice)} mouse device(s); hotkey {shortcut_label}",
              file=sys.stderr)
        self._tracking = True
        modifier_held = False
        last_trigger_ms = 0.0

        while self._running:
            try:
                r, _, _ = select.select(devices, [], [], 0.3)
                for dev in r:
                    try:
                        for event in dev.read():
                            t, code, val = event.type, event.code, event.value

                            if t == ecodes.EV_REL:
                                if code == ecodes.REL_X:
                                    self._x = _clamp(self._x + val, self._sx_min, self._sx_max)
                                elif code == ecodes.REL_Y:
                                    self._y = _clamp(self._y + val, self._sy_min, self._sy_max)

                            elif t == ecodes.EV_KEY:
                                if code in modifier_codes:
                                    modifier_held = (val != 0)
                                elif code == trigger_code and val == 1 and modifier_held:
                                    now_ms = time.monotonic() * 1000.0
                                    if last_trigger_ms and (now_ms - last_trigger_ms) < self.DOUBLE_PRESS_MS:
                                        import sys
                                        print(f"[evdev] {shortcut_label} detected", file=sys.stderr)
                                        self.double_ctrl_c.emit()
                                        last_trigger_ms = 0.0
                                    else:
                                        last_trigger_ms = now_ms
                    except BlockingIOError:
                        pass
                    except OSError:
                        # device disappeared (unplugged, etc.)
                        if dev in devices:
                            devices.remove(dev)
                        continue
            except Exception:
                time.sleep(0.3)

        self._tracking = False


# ---------------------------------------------------------------------------
def _modifier_keycodes(name: str, ecodes) -> set[int]:
    name = (name or "ctrl").lower()
    if name == "alt":
        return {ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT}
    if name == "shift":
        return {ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT}
    return {ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL}


def _trigger_keycode(letter: str, ecodes) -> int:
    return getattr(ecodes, f"KEY_{(letter or 'C').upper()}", ecodes.KEY_C)


def _clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else (hi if v > hi else v)


def _xdotool_pos() -> tuple[int, int]:
    try:
        r = subprocess.run(
            ["xdotool", "getmouselocation", "--shell"],
            capture_output=True, text=True, timeout=0.3,
        )
        if r.returncode == 0:
            pos: dict[str, int] = {}
            for line in r.stdout.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    try:
                        pos[k.strip()] = int(v.strip())
                    except ValueError:
                        pass
            x, y = pos.get("X"), pos.get("Y")
            if x is not None and y is not None:
                return x, y
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    geo = QGuiApplication.primaryScreen().geometry()
    return geo.center().x(), geo.center().y()
