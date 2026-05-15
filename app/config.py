import os
import shutil
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Static timing / poll-interval constants. Always loaded at import time.
# ---------------------------------------------------------------------------
CONFIG: dict = {
    "debounce_dictionary_ms": 300,
    "debounce_translate_ms":  500,
    "popup_auto_hide_ms":     2000,
    "selection_poll_interval_ms": 300,
}


# ---------------------------------------------------------------------------
# Data dir resolution.
#
# Three modes:
#   1. TRANSLATE_DB_PATH env var → absolute path to words.db (highest priority,
#      used by tests / power users; data_root = its parent dir).
#   2. PyInstaller-frozen (`sys.frozen` True) → Qt's per-platform AppData dir:
#        Linux:   ~/.local/share/TranslateApp/
#        Windows: %APPDATA%/TranslateApp/TranslateApp/
#      Requires QApplication's applicationName/organizationName to be set
#      first (done in main.py before any data path is touched).
#   3. Dev mode (running from source) → project root, preserving the existing
#      `python main.py` workflow.
#
# These are FUNCTIONS, not module-level values, because QStandardPaths reads
# from the live QApplication, which doesn't exist yet at module-import time.
# ---------------------------------------------------------------------------
def data_root() -> Path:
    env = os.environ.get("TRANSLATE_DB_PATH")
    if env:
        return Path(env).parent

    if getattr(sys, "frozen", False):
        from PyQt6.QtCore import QStandardPaths
        return Path(QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        ))

    return _project_root


def db_path() -> Path:
    """Return the SQLite DB path, creating parent dirs and migrating once."""
    env = os.environ.get("TRANSLATE_DB_PATH")
    if env:
        return Path(env)

    root = data_root()
    root.mkdir(parents=True, exist_ok=True)
    new_path = root / "words.db"

    # One-shot migration: bring forward an existing dev-mode DB the first
    # time the frozen app runs, so users don't lose their saved words.
    legacy = _project_root / "words.db"
    if (
        getattr(sys, "frozen", False)
        and not new_path.exists()
        and legacy.exists()
        and legacy != new_path
    ):
        try:
            shutil.copy2(legacy, new_path)
        except OSError:
            pass

    return new_path
