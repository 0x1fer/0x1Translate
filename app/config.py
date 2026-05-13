import os
from pathlib import Path

_project_root = Path(__file__).parent.parent

CONFIG: dict = {
    "db_path": Path(os.environ.get("TRANSLATE_DB_PATH", str(_project_root / "words.db"))),
    "debounce_dictionary_ms": 300,
    "debounce_translate_ms": 500,
    "popup_auto_hide_ms": 2000,
    "selection_poll_interval_ms": 300,
}
