import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont
from PyQt6 import uic
from tureng import TurengAPI
from deeplTranslate import DeeplAPI

class CeviriUygulamasi(QMainWindow):

    # DeepL supported source languages (code, display name)
    SOURCE_LANGUAGES = [
        (None,  "Otomatik Algıla"),
        ("AR",  "Arapça"),
        ("BG",  "Bulgarca"),
        ("CS",  "Çekçe"),
        ("DA",  "Danca"),
        ("DE",  "Almanca"),
        ("EL",  "Yunanca"),
        ("EN",  "İngilizce"),
        ("ES",  "İspanyolca"),
        ("ET",  "Estonca"),
        ("FI",  "Fince"),
        ("FR",  "Fransızca"),
        ("HU",  "Macarca"),
        ("ID",  "Endonezce"),
        ("IT",  "İtalyanca"),
        ("JA",  "Japonca"),
        ("KO",  "Korece"),
        ("LT",  "Litvanca"),
        ("LV",  "Letonca"),
        ("NB",  "Norveççe (Bokmål)"),
        ("NL",  "Felemenkçe"),
        ("PL",  "Lehçe"),
        ("PT",  "Portekizce"),
        ("RO",  "Romence"),
        ("RU",  "Rusça"),
        ("SK",  "Slovakça"),
        ("SL",  "Slovence"),
        ("SV",  "İsveççe"),
        ("TR",  "Türkçe"),
        ("UK",  "Ukraynaca"),
        ("ZH",  "Çince"),
    ]

    # DeepL supported target languages (code, display name)
    TARGET_LANGUAGES = [
        ("AR",    "Arapça"),
        ("BG",    "Bulgarca"),
        ("CS",    "Çekçe"),
        ("DA",    "Danca"),
        ("DE",    "Almanca"),
        ("EL",    "Yunanca"),
        ("EN-GB", "İngilizce (İngiltere)"),
        ("EN-US", "İngilizce (Amerika)"),
        ("ES",    "İspanyolca"),
        ("ET",    "Estonca"),
        ("FI",    "Fince"),
        ("FR",    "Fransızca"),
        ("HU",    "Macarca"),
        ("ID",    "Endonezce"),
        ("IT",    "İtalyanca"),
        ("JA",    "Japonca"),
        ("KO",    "Korece"),
        ("LT",    "Litvanca"),
        ("LV",    "Letonca"),
        ("NB",    "Norveççe (Bokmål)"),
        ("NL",    "Felemenkçe"),
        ("PL",    "Lehçe"),
        ("PT-BR", "Portekizce (Brezilya)"),
        ("PT-PT", "Portekizce (Portekiz)"),
        ("RO",    "Romence"),
        ("RU",    "Rusça"),
        ("SK",    "Slovakça"),
        ("SL",    "Slovence"),
        ("SV",    "İsveççe"),
        ("TR",    "Türkçe"),
        ("UK",    "Ukraynaca"),
        ("ZH-HANS", "Çince (Basitleştirilmiş)"),
        ("ZH-HANT", "Çince (Geleneksel)"),
    ]

    def __init__(self):
        super().__init__()

        uic.loadUi("form.ui", self)

        # --- Populate language comboboxes ---
        self.inputBox.clear()
        for code, name in self.SOURCE_LANGUAGES:
            self.inputBox.addItem(name, code)
        # Default source: Otomatik Algıla (index 0)

        self.outputBox.clear()
        for code, name in self.TARGET_LANGUAGES:
            self.outputBox.addItem(name, code)
        # Default target: İngilizce (Amerika)
        default_target_idx = next(
            (i for i, (c, _) in enumerate(self.TARGET_LANGUAGES) if c == "EN-US"), 0
        )
        self.outputBox.setCurrentIndex(default_target_idx)

        # --- Navigation ---
        self.btnTureng.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btnTranslate.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btnMyWords.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        # --- Tureng ---
        self.tureng_api = TurengAPI()
        self.turengTranslateBtn.clicked.connect(self.startTureng)

        # --- DeepL ---
        self.deepl_api = DeeplAPI()
        self.deeplTranslateBtn.clicked.connect(self.startDeepl)

        # --- Swap languages button ---
        self.reverseButton.clicked.connect(self.swapLanguages)

    def swapLanguages(self):
        """Swap the selected source and target languages."""
        src_code = self.inputBox.currentData()
        tgt_code = self.outputBox.currentData()

        # Find matching target in source list (skip auto-detect)
        if tgt_code:
            # Target codes like EN-GB/EN-US → source uses EN
            src_search = tgt_code.split("-")[0]
            for i, (code, _) in enumerate(self.SOURCE_LANGUAGES):
                if code == src_search:
                    self.inputBox.setCurrentIndex(i)
                    break

        # Find matching source in target list
        if src_code:
            for i, (code, _) in enumerate(self.TARGET_LANGUAGES):
                if code == src_code or code.startswith(src_code):
                    self.outputBox.setCurrentIndex(i)
                    break

    def startTureng(self):
        word = self.turengInput.text()
        results = self.tureng_api.getWord(word)
        self.turengResults.clear()

        html_metin = f"<h3>'{word}' için sonuçlar:</h3><ul>"

        for result in results:
            parcalar = result.split(" -> ")
            if len(parcalar) == 2:
                ingilizce = parcalar[0]
                turkce = parcalar[1]
                html_metin += f"<li><b>{ingilizce}</b> : {turkce}</li>"
            else:
                html_metin += f"<li>{result}</li>"

        html_metin += "</ul>"
        self.turengResults.setHtml(html_metin)

    def startDeepl(self):
        text = self.translateInput.toPlainText()
        source_lang = self.inputBox.currentData()   # None = auto-detect
        target_lang = self.outputBox.currentData()   # e.g. "EN-US", "TR"
        results = self.deepl_api.translate(text, target_lang, source_lang)
        self.translateOutput.setText(results)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = CeviriUygulamasi()
    pencere.show()
    sys.exit(app.exec())
