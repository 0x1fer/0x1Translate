"""
Minimal i18n layer — `tr(key, **fmt)` returns the active-language string.

Two locales:
  tr — Türkçe (default)
  en — English

UI files import `tr` and call it with stable string keys. The active language
is read once at startup from settings.json; changing it requires an app
restart (the UI text is bound at construction time, so a live swap would
require every widget to expose a retranslateUi() method).
"""
from __future__ import annotations

from app import settings


SUPPORTED = ("tr", "en")
DEFAULT = "tr"

# ---------------------------------------------------------------------------
# Strings
# ---------------------------------------------------------------------------
STRINGS: dict[str, dict[str, str]] = {
    # --- App / window / tray ------------------------------------------
    "app_title":             {"tr": "TranslateApp",            "en": "TranslateApp"},
    "status_ready":          {"tr": "Hazır",                   "en": "Ready"},
    "status_saved_preview":  {"tr": "✓ '{preview}' kaydedildi.", "en": "✓ '{preview}' saved."},
    "tray_show_hide":        {"tr": "Göster / Gizle",          "en": "Show / Hide"},
    "tray_quit":             {"tr": "Çıkış",                   "en": "Quit"},
    "tray_running_msg":      {"tr": "Uygulama arka planda çalışmaya devam ediyor.",
                              "en": "App keeps running in the background."},

    # --- Nav buttons --------------------------------------------------
    "nav_dictionary":        {"tr": "📖  Sözlük",              "en": "📖  Dictionary"},
    "nav_translate":         {"tr": "🌐  Çeviri",              "en": "🌐  Translate"},
    "nav_words":             {"tr": "📝  Kelimelerim",         "en": "📝  My Words"},
    "nav_settings":          {"tr": "⚙️  Ayarlar",             "en": "⚙️  Settings"},

    # --- Shared buttons / actions -------------------------------------
    "btn_save":              {"tr": "Kaydet",                  "en": "Save"},
    "btn_cancel":            {"tr": "İptal",                   "en": "Cancel"},
    "btn_delete":            {"tr": "Sil",                     "en": "Delete"},
    "btn_close":             {"tr": "Kapat",                   "en": "Close"},
    "swap_tooltip":          {"tr": "Dilleri değiştir",        "en": "Swap languages"},
    "copy_tooltip":          {"tr": "Kopyala",                 "en": "Copy"},

    # --- Dictionary tab ----------------------------------------------
    "dict_header":           {"tr": "📖  Sözlük",              "en": "📖  Dictionary"},
    "dict_placeholder":      {"tr": "Türkçe veya İngilizce kelime arayın…",
                              "en": "Search a Turkish or English word…"},
    "dict_status_start":     {"tr": "Aramak için kelime yazın.",
                              "en": "Type a word to search."},
    "dict_status_searching": {"tr": "Aranıyor…",               "en": "Searching…"},
    "dict_status_no_result": {"tr": "Sonuç yok.",              "en": "No results."},
    "dict_no_result_for":    {"tr": "'{word}' için sonuç bulunamadı.",
                              "en": "No results for '{word}'."},
    "dict_status_conn_err":  {"tr": "Bağlantı hatası.",        "en": "Connection error."},
    "dict_status_results":   {"tr": "{n} sonuç bulundu.",      "en": "{n} results found."},
    "dict_status_error":     {"tr": "Hata oluştu.",            "en": "An error occurred."},
    "dict_col_source":       {"tr": "Kaynak",                  "en": "Source"},
    "dict_col_translation":  {"tr": "Çeviri",                  "en": "Translation"},
    "dict_save_link":        {"tr": "💾 Kaydet",               "en": "💾 Save"},
    "dict_status_saved_row": {"tr": "✓ '{word}' kaydedildi.",  "en": "✓ '{word}' saved."},

    # --- Translate tab -----------------------------------------------
    "tr_header":             {"tr": "🌐  Çeviri",              "en": "🌐  Translate"},
    "tr_placeholder":        {"tr": "Çevirmek için metin girin veya yapıştırın…",
                              "en": "Type or paste text to translate…"},
    "tr_save_btn":           {"tr": "💾  Kaydet",              "en": "💾  Save"},
    "tr_status_start":       {"tr": "Yazmaya başlayın, otomatik çevirilecek.",
                              "en": "Start typing — auto-translates."},
    "tr_status_translating": {"tr": "Çevriliyor…",             "en": "Translating…"},
    "tr_status_done":        {"tr": "Çeviri tamamlandı.",      "en": "Translation complete."},
    "tr_status_error":       {"tr": "Çeviri hatası.",          "en": "Translation error."},
    "tr_status_saved":       {"tr": "✓ Kelimelerime kaydedildi.",
                              "en": "✓ Saved to My Words."},
    "tr_deepl_error":        {"tr": "⚠ DeepL hatası: {err}",   "en": "⚠ DeepL error: {err}"},
    "tr_error_prefix":       {"tr": "Hata: {msg}",             "en": "Error: {msg}"},

    # --- Words tab ----------------------------------------------------
    "words_header":          {"tr": "📝  Kelimelerim",         "en": "📝  My Words"},
    "words_count":           {"tr": "{n} kayıt",               "en": "{n} records"},
    "words_btn_add":         {"tr": "➕  Ekle",                "en": "➕  Add"},
    "words_btn_export":      {"tr": "📥  Dışa Aktar",          "en": "📥  Export"},
    "words_btn_export_sel":  {"tr": "📤  Seçilenleri Dışa Aktar ({n})",
                              "en": "📤  Export selected ({n})"},
    "words_search_ph":       {"tr": "Kayıtlarda ara…",         "en": "Search records…"},
    "words_select_all":      {"tr": "Tümünü seç",              "en": "Select all"},
    "words_bulk_del":        {"tr": "🗑️  Seçilenleri sil",     "en": "🗑️  Delete selected"},
    "words_bulk_del_n":      {"tr": "🗑️  Seçilenleri sil ({n})",
                              "en": "🗑️  Delete selected ({n})"},
    "words_n_selected":      {"tr": "{n} seçili",              "en": "{n} selected"},
    "words_col_original":    {"tr": "Orijinal",                "en": "Original"},
    "words_col_translation": {"tr": "Çeviri",                  "en": "Translation"},
    "words_col_language":    {"tr": "Dil",                     "en": "Language"},
    "words_col_date":        {"tr": "Tarih",                   "en": "Date"},
    "words_empty_state":     {"tr": "📚  Henüz kayıtlı kelime yok.\nÇeviri / sözlük sekmesinden kelime kaydedin veya yukarıdaki “Ekle” butonunu kullanın.",
                              "en": "📚  No saved words yet.\nSave from the Translate / Dictionary tab or use the “Add” button above."},
    "words_confirm_del_t":   {"tr": "Sil",                     "en": "Delete"},
    "words_confirm_del_m":   {"tr": "Bu kaydı silmek istediğinizden emin misiniz?",
                              "en": "Are you sure you want to delete this record?"},
    "words_confirm_bulk_t":  {"tr": "Toplu sil",               "en": "Bulk delete"},
    "words_confirm_bulk_m":  {"tr": "Seçili {n} kaydı silmek istediğinizden emin misiniz?",
                              "en": "Delete {n} selected records?"},
    "words_export_empty_t":  {"tr": "Boş",                     "en": "Empty"},
    "words_export_empty_m":  {"tr": "Dışa aktarılacak kayıt yok.",
                              "en": "No records to export."},
    "words_export_done_t":   {"tr": "Tamamlandı",              "en": "Done"},
    "words_export_done_m":   {"tr": "{n} {scope} kayıt başarıyla aktarıldı:\n{path}",
                              "en": "{n} {scope} records exported successfully:\n{path}"},
    "words_export_scope_sel": {"tr": "seçili",                 "en": "selected"},
    "words_export_scope_all": {"tr": "tüm",                    "en": "total"},
    "words_export_dlg_title": {"tr": "Dışa Aktar",             "en": "Export"},
    "words_export_filter_json": {"tr": "JSON dosyası (*.json)", "en": "JSON file (*.json)"},
    "words_export_filter_csv":  {"tr": "CSV dosyası (*.csv)",   "en": "CSV file (*.csv)"},
    "words_export_filter_xlsx": {"tr": "Excel dosyası (*.xlsx)", "en": "Excel file (*.xlsx)"},
    "words_export_missing_t": {"tr": "Eksik bağımlılık",       "en": "Missing dependency"},
    "words_export_missing_m": {"tr": "Excel dışa aktarımı için 'openpyxl' paketi gereklidir.\n\nKurulum:  pip install openpyxl\n\nDetay: {err}",
                               "en": "Exporting to Excel requires the 'openpyxl' package.\n\nInstall:  pip install openpyxl\n\nDetail: {err}"},
    "words_export_file_err_t": {"tr": "Hata",                  "en": "Error"},
    "words_export_file_err_m": {"tr": "Dosya yazılamadı:\n{err}",
                                "en": "Could not write file:\n{err}"},
    "words_add_dlg_title":   {"tr": "Yeni kelime ekle",        "en": "Add new word"},
    "words_add_label_orig":  {"tr": "Orijinal:",               "en": "Original:"},
    "words_add_label_trans": {"tr": "Çeviri:",                 "en": "Translation:"},
    "words_add_label_lang":  {"tr": "Dil:",                    "en": "Language:"},
    "words_add_ph_orig":     {"tr": "Orijinal metin",          "en": "Original text"},
    "words_add_ph_trans":    {"tr": "Çeviri",                  "en": "Translation"},
    "words_add_missing_t":   {"tr": "Eksik bilgi",             "en": "Missing info"},
    "words_add_missing_m":   {"tr": "Orijinal metin ve çeviri boş bırakılamaz.",
                              "en": "Original text and translation can't be empty."},

    # --- Popup --------------------------------------------------------
    "popup_translator":      {"tr": "Translator",              "en": "Translator"},
    "popup_dictionary":      {"tr": "Dictionary",              "en": "Dictionary"},
    "popup_translating":     {"tr": "Çevriliyor…",             "en": "Translating…"},
    "popup_searching_for":   {"tr": "'{text}' aranıyor…",      "en": "Searching '{text}'…"},
    "popup_no_result":       {"tr": "Sonuç bulunamadı.",       "en": "No results."},
    "popup_tr_placeholder":  {"tr": "Çeviri burada görünecek…",
                              "en": "Translation will appear here…"},
    "popup_dc_placeholder":  {"tr": "Sözlük sonucu burada görünecek…",
                              "en": "Dictionary result will appear here…"},
    "popup_edit":            {"tr": "Edit",                    "en": "Edit"},
    "popup_save":            {"tr": "Save",                    "en": "Save"},
    "popup_saved":           {"tr": "✓ Kaydedildi",            "en": "✓ Saved"},
    "popup_error":           {"tr": "Hata: {msg}",             "en": "Error: {msg}"},
    "popup_btn_tooltip":     {"tr": "Çevir",                   "en": "Translate"},

    # --- Settings tab -------------------------------------------------
    "settings_header":            {"tr": "⚙️  Ayarlar",        "en": "⚙️  Settings"},
    "settings_section_shortcut":  {"tr": "Klavye Kısayolu",    "en": "Keyboard Shortcut"},
    "settings_shortcut_help":     {"tr": "Çift basma şeklinde çalışır (örnek: Ctrl+C+C). 500 ms içinde tetik tuşuna iki kez basılırsa popup açılır.",
                                   "en": "Activated by double-press (e.g. Ctrl+C+C). Press the trigger key twice within 500 ms to open the popup."},
    "settings_label_modifier":    {"tr": "Modifier:",          "en": "Modifier:"},
    "settings_label_trigger":     {"tr": "Tetik tuşu:",        "en": "Trigger key:"},
    "settings_preview":           {"tr": "Önizleme: {combo}",  "en": "Preview: {combo}"},

    "settings_section_apikey":    {"tr": "DeepL API Anahtarı", "en": "DeepL API Key"},
    "settings_apikey_help":       {"tr": "Boş bırakılırsa .env dosyasındaki DEEPL_API_KEY kullanılır.",
                                   "en": "Leave empty to fall back to DEEPL_API_KEY in .env."},
    "settings_apikey_placeholder": {"tr": "DeepL API anahtarınız",
                                    "en": "Your DeepL API key"},
    "settings_apikey_show":       {"tr": "Göster",             "en": "Show"},
    "settings_apikey_hide":       {"tr": "Gizle",              "en": "Hide"},

    "settings_section_lang":      {"tr": "Uygulama Dili",      "en": "App Language"},
    "settings_lang_help":         {"tr": "Değişiklik için uygulamayı yeniden başlatın.",
                                   "en": "Restart the app to apply the change."},
    "settings_lang_tr":           {"tr": "Türkçe",             "en": "Turkish"},
    "settings_lang_en":           {"tr": "İngilizce",          "en": "English"},

    "settings_btn_save":          {"tr": "💾  Ayarları kaydet", "en": "💾  Save settings"},
    "settings_saved_status":      {"tr": "✓ Ayarlar kaydedildi.",
                                   "en": "✓ Settings saved."},
    "settings_restart_t":         {"tr": "Yeniden başlatma gerekli",
                                   "en": "Restart required"},
    "settings_restart_m":         {"tr": "Dil değişikliğinin etkin olması için uygulamayı yeniden başlatın.",
                                   "en": "Restart the app for the language change to take effect."},

    # --- DeepL API ----------------------------------------------------
    "deepl_no_key":          {"tr": "Kritik Hata: DEEPL_API_KEY bulunamadı! Lütfen .env dosyasını veya Ayarlar sekmesini kontrol edin.",
                              "en": "Critical: DEEPL_API_KEY not found! Check the .env file or the Settings tab."},
    "deepl_translate_err":   {"tr": "Çeviri işleminde bir hata oluştu: {err}",
                              "en": "A translation error occurred: {err}"},

    # --- Languages ----------------------------------------------------
    "lang_auto_detect":      {"tr": "Otomatik Algıla",         "en": "Auto Detect"},
    "lang_auto":             {"tr": "Otomatik",                "en": "Automatic"},
    "lang_auto_unknown":     {"tr": "Otomatik / Bilinmiyor",   "en": "Automatic / Unknown"},
    "lang_AR":      {"tr": "Arapça",     "en": "Arabic"},
    "lang_BG":      {"tr": "Bulgarca",   "en": "Bulgarian"},
    "lang_CS":      {"tr": "Çekçe",      "en": "Czech"},
    "lang_DA":      {"tr": "Danca",      "en": "Danish"},
    "lang_DE":      {"tr": "Almanca",    "en": "German"},
    "lang_EL":      {"tr": "Yunanca",    "en": "Greek"},
    "lang_EN":      {"tr": "İngilizce",  "en": "English"},
    "lang_EN_GB":   {"tr": "İngilizce (İngiltere)", "en": "English (UK)"},
    "lang_EN_US":   {"tr": "İngilizce (Amerika)",   "en": "English (US)"},
    "lang_ES":      {"tr": "İspanyolca", "en": "Spanish"},
    "lang_ET":      {"tr": "Estonca",    "en": "Estonian"},
    "lang_FI":      {"tr": "Fince",      "en": "Finnish"},
    "lang_FR":      {"tr": "Fransızca",  "en": "French"},
    "lang_HU":      {"tr": "Macarca",    "en": "Hungarian"},
    "lang_ID":      {"tr": "Endonezce",  "en": "Indonesian"},
    "lang_IT":      {"tr": "İtalyanca",  "en": "Italian"},
    "lang_JA":      {"tr": "Japonca",    "en": "Japanese"},
    "lang_KO":      {"tr": "Korece",     "en": "Korean"},
    "lang_LT":      {"tr": "Litvanca",   "en": "Lithuanian"},
    "lang_LV":      {"tr": "Letonca",    "en": "Latvian"},
    "lang_NB":      {"tr": "Norveççe (Bokmål)", "en": "Norwegian (Bokmål)"},
    "lang_NL":      {"tr": "Felemenkçe", "en": "Dutch"},
    "lang_PL":      {"tr": "Lehçe",      "en": "Polish"},
    "lang_PT":      {"tr": "Portekizce", "en": "Portuguese"},
    "lang_PT_BR":   {"tr": "Portekizce (Brezilya)", "en": "Portuguese (Brazil)"},
    "lang_PT_PT":   {"tr": "Portekizce (Portekiz)", "en": "Portuguese (Portugal)"},
    "lang_RO":      {"tr": "Romence",    "en": "Romanian"},
    "lang_RU":      {"tr": "Rusça",      "en": "Russian"},
    "lang_SK":      {"tr": "Slovakça",   "en": "Slovak"},
    "lang_SL":      {"tr": "Slovence",   "en": "Slovenian"},
    "lang_SV":      {"tr": "İsveççe",    "en": "Swedish"},
    "lang_TR":      {"tr": "Türkçe",     "en": "Turkish"},
    "lang_UK":      {"tr": "Ukraynaca",  "en": "Ukrainian"},
    "lang_ZH":      {"tr": "Çince",      "en": "Chinese"},
    "lang_ZH_HANS": {"tr": "Çince (Basitleştirilmiş)", "en": "Chinese (Simplified)"},
    "lang_ZH_HANT": {"tr": "Çince (Geleneksel)",       "en": "Chinese (Traditional)"},
    "lang_TR_EN":   {"tr": "TR ↔ EN (sözlük)",         "en": "TR ↔ EN (dictionary)"},
}


# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
_current_lang = DEFAULT


def _normalize(code: str) -> str:
    code = (code or "").lower()
    return code if code in SUPPORTED else DEFAULT


def init() -> str:
    """Load language from settings.json. Call once at startup."""
    global _current_lang
    _current_lang = _normalize(settings.load().get("language", DEFAULT))
    return _current_lang


def get_language() -> str:
    return _current_lang


def set_language(code: str) -> None:
    global _current_lang
    _current_lang = _normalize(code)


def tr(key: str, **fmt) -> str:
    """Look up `key` in the current language. Falls back to TR, then to key."""
    bundle = STRINGS.get(key)
    if bundle is None:
        return key.format(**fmt) if fmt else key
    s = bundle.get(_current_lang) or bundle.get(DEFAULT) or key
    return s.format(**fmt) if fmt else s


def lang_key(code: str | None) -> str:
    """
    Map a DeepL language code (e.g. "EN-GB") to its translation key
    (e.g. "lang_EN_GB").
    """
    if code is None:
        return "lang_auto_detect"
    return "lang_" + code.replace("-", "_").upper()


# Auto-init on import so any module can call tr() right away.
init()
