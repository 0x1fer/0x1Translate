import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QFont
from PyQt6 import uic
from tureng import TurengAPI

class CeviriUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()

    
        uic.loadUi("form.ui", self)
    
        # Tureng butonuna basılınca 0. indeksteki (ilk) sayfayı aç
        self.btnTureng.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        # DeepL butonuna basılınca 1. indeksteki (ikinci) sayfayı aç
        self.btnTranslate.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # Kelimelerim butonuna basılınca 2. indeksteki (üçüncü) sayfayı aç
        self.btnMyWords.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        self.api = TurengAPI()
        
        self.turengTranslateBtn.clicked.connect(self.startTureng)

        

    def startTureng(self):
        # Metin kutusuna girilen kelimeyi alıyoruz
        word = self.turengInput.text()
        results = self.api.getWord(word)
        # Yeni bir arama yapmadan önce eski sonuçları temizliyoruz
        # Yeni bir arama yapmadan önce eski sonuçları temizliyoruz
        self.turengResults.clear()

        # Ekrana basılacak HTML yapısını başlatıyoruz
        html_metin = f"<h3>'{word}' için sonuçlar:</h3><ul>"

        for result in results:
            # Tureng'den gelen "apple -> elma" formatındaki veriyi oktan (->) bölüyoruz
            parcalar = result.split(" -> ")
            
            if len(parcalar) == 2:
                ingilizce = parcalar[0]
                turkce = parcalar[1]
                # İngilizce kısmı kalın (bold) yapıp HTML madde işaretli listesine ekliyoruz
                html_metin += f"<li><b>{ingilizce}</b> : {turkce}</li>"
            else:
                # Eğer hata mesajı ('Tam eşleşen bulunamadı' vb.) ise direkt ekle
                html_metin += f"<li>{result}</li>"

        html_metin += "</ul>" # HTML listesini kapatıyoruz

        # Hazırladığımız bu şık yapıyı tek seferde ekrana basıyoruz
        self.turengResults.setHtml(html_metin)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = CeviriUygulamasi()
    pencere.show()
    sys.exit(app.exec())
