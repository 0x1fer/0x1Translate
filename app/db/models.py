from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SavedWord:
    original_text: str
    translation: str
    source_lang: str
    id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
