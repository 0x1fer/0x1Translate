import sqlite3
from datetime import datetime
from pathlib import Path

from .models import SavedWord


class Database:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS saved_words (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_text TEXT NOT NULL,
                    translation   TEXT NOT NULL,
                    source_lang   TEXT NOT NULL,
                    created_at    TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_word(self, word: SavedWord) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO saved_words (original_text, translation, source_lang, created_at) VALUES (?, ?, ?, ?)",
                (word.original_text, word.translation, word.source_lang, word.created_at.isoformat()),
            )
            conn.commit()
            return cur.lastrowid  # type: ignore[return-value]

    def get_all(self) -> list[SavedWord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM saved_words ORDER BY created_at DESC"
            ).fetchall()
        return [self._to_model(r) for r in rows]

    def search(self, query: str) -> list[SavedWord]:
        pattern = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM saved_words WHERE original_text LIKE ? OR translation LIKE ? ORDER BY created_at DESC",
                (pattern, pattern),
            ).fetchall()
        return [self._to_model(r) for r in rows]

    def delete(self, word_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM saved_words WHERE id = ?", (word_id,))
            conn.commit()

    def update(self, word: SavedWord) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE saved_words SET original_text=?, translation=?, source_lang=? WHERE id=?",
                (word.original_text, word.translation, word.source_lang, word.id),
            )
            conn.commit()

    @staticmethod
    def _to_model(row: sqlite3.Row) -> SavedWord:
        return SavedWord(
            id=row["id"],
            original_text=row["original_text"],
            translation=row["translation"],
            source_lang=row["source_lang"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
