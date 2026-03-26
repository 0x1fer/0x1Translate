import requests
from bs4 import BeautifulSoup

class TurengAPI:

    def __init__(self):     
        self.base_url = f"https://tureng.com/tr/turkce-ingilizce/"


        self.headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def getWord(self, word):
        url = f"{self.base_url}{word}"
        try:

                response = self.session.get(url,  timeout=5)

                response.raise_for_status()

        except requests.exceptions.RequestException as e:
                # İnternet yoksa, site çökmüşse veya timeout olursa burası çalışır.
                return [f"Hata: Tureng'e bağlanılamadı. Detay: {e}"]



        soup = BeautifulSoup(response.content, "html.parser")

        results = []
        all_rows = soup.find_all("tr")

        for rows in all_rows[:20]:

                english_cell = rows.find("td", class_="en")
                turkish_cell = rows.find("td", class_="tr")

                if english_cell and turkish_cell:
                        tr_text = turkish_cell.text.strip()
                        en_text = english_cell.text.strip()
                        

                        if tr_text.lower()==word.lower():                              
                                
                            results.append(f"{word} -> {en_text}")
 
                        elif en_text[:len(word)].lower()==word.lower():
    
                            results.append(f"{word} -> {tr_text}")
    
                        
                              
        
        return results
