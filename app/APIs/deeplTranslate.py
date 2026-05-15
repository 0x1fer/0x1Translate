import os

import deepl
from dotenv import load_dotenv

from app import config as _config, settings as _settings
from app.i18n import tr


class DeeplAPI:
    def __init__(self, api_key: str | None = None):
        # Priority: explicit api_key arg > settings.json > .env
        if api_key is None:
            stored = _settings.load().get("deepl_api_key", "").strip()
            if stored:
                api_key = stored
            else:
                # Look for .env next to user data (frozen apps don't share
                # cwd with the project) AND fall back to default search.
                load_dotenv(dotenv_path=_config.data_root() / ".env")
                load_dotenv()
                api_key = os.getenv("DEEPL_API_KEY")
        self.api_key = api_key
        if not self.api_key:
            raise ValueError(tr("deepl_no_key"))
        self.translator = deepl.Translator(self.api_key)

    def translate(self, text, target_lang, source_lang=None):
        try:
            sonuc = self.translator.translate_text(
                text,
                target_lang=target_lang,
                source_lang=source_lang,
            )
            return sonuc.text
        except deepl.DeepLException as e:
            return tr("deepl_translate_err", err=str(e))
