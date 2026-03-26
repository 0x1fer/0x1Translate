import os
import deepl
from dotenv import load_dotenv

class DeeplAPI:
    def __init__(self):
        load_dotenv()
        self.api_key=os.getenv("DEEPL_API_KEY")
        if not self.api_key:
            raise ValueError("Kritik Hata: DEEPL_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")
        self.translator = deepl.Translator(self.api_key)

    def translate(self, text, target_lang, source_lang=None):
        try:
            sonuc = self.translator.translate_text(
                text,
                target_lang=target_lang,
                source_lang=source_lang
            )
            return sonuc.text
        except deepl.DeepLException as e:
            return f"Çeviri işleminde bir hata oluştu: {e}"
            