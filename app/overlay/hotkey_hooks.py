"""
Platform-dispatching facade for global hotkey + cursor position.

Linux  → evdev (/dev/input/event*); requires 'input' group membership.
Windows → pynput (Win32 keyboard hook); no special permissions.

Public API (identical across platforms):
  init(parent) -> object with .double_ctrl_c pyqtSignal
  instance()   -> the singleton, or None
  shutdown()   -> stop + clear singleton
  get_cursor_pos() -> (x, y) absolute screen coordinates
"""
import sys

if sys.platform == "win32":
    from app.overlay._win_hooks import (   # noqa: F401
        init, instance, shutdown, get_cursor_pos, reload_shortcut,
    )
else:
    from app.overlay.evdev_hooks import (   # noqa: F401
        init, instance, shutdown, get_cursor_pos, reload_shortcut,
    )
