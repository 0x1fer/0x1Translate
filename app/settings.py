"""
Persistent app settings stored as JSON.

settings.json lives next to words.db (project root by default; overridable
via the TRANSLATE_DB_PATH environment variable).

Keys:
  language        — "tr" | "en"
  deepl_api_key   — string; empty falls back to .env DEEPL_API_KEY
  shortcut        — {"modifier": "ctrl"|"alt"|"shift", "trigger_key": "C"}
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from app import config


DEFAULTS: dict[str, Any] = {
    "language": "tr",
    "deepl_api_key": "",
    "shortcut": {
        "modifier": "ctrl",
        "trigger_key": "C",
    },
}


def path() -> Path:
    return config.data_root() / "settings.json"


def load() -> dict:
    data = copy.deepcopy(DEFAULTS)
    p = path()
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                stored = json.load(f)
            for k, v in stored.items():
                if k == "shortcut" and isinstance(v, dict):
                    data["shortcut"].update(v)
                else:
                    data[k] = v
        except (OSError, json.JSONDecodeError):
            pass
    return data


def save(data: dict) -> None:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update(**fields) -> dict:
    """Merge `fields` into the stored settings; return the resulting dict."""
    data = load()
    for k, v in fields.items():
        if k == "shortcut" and isinstance(v, dict):
            data["shortcut"].update(v)
        else:
            data[k] = v
    save(data)
    return data
