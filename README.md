# TranslateApp

Linux için PyQt6 tabanlı masaüstü çeviri uygulaması. Sözlük (Tureng) ve çeviri (DeepL) servislerini tek bir arayüzde toplar, sistem genelinde metin yakalama overlay'i ile herhangi bir uygulamadan seçilen metni anında çevirir.

---

## Özellikler

| | |
|--|--|
| 🌐 **Çeviri** | DeepL üzerinden 30+ dil çiftinde anlık çeviri (debounce'lu, dil değişimine otomatik tepki) |
| 📖 **Sözlük** | Tureng üzerinden TR ↔ EN sözlük araması (debounce'lu) |
| 📝 **Kelimelerim** | SQLite tabanlı kişisel kelime arşivi — manuel ekleme, arama, silme |
| 📥 **Dışa aktarma** | JSON / CSV / Excel (`.xlsx`) formatlarında kayıt dışa aktarma |
| 🔍 **Overlay** | Herhangi bir uygulamada metin seçince çıkan "Çevir" butonu + popup paneli |
| ⌨️ **Global kısayol** | `Ctrl+C+C` çift basışında popup'ı doğrudan açar (Wayland-uyumlu) |
| 🎨 **Karanlık tema** | Catppuccin Mocha esinli, frameless ve resize edilebilir popup |
| 🖥️ **Tepsi** | Sistem tepsisine küçültme, arka planda overlay aktif kalır |

---

## Sistem gereksinimleri

- **OS:** Linux (Arch / KDE Plasma 6 üzerinde test edildi)
- **Python:** 3.11+
- **Görüntü sunucu:** X11 veya Wayland (Wayland'de uygulama otomatik XWayland'e geçer)

### Sistem paketleri (pacman / apt / dnf üzerinden)

```bash
# Arch
sudo pacman -S wl-clipboard xclip xdotool python-evdev
```

| Paket | Niçin |
|-------|-------|
| `wl-clipboard` | `wl-paste` → Wayland clipboard / PRIMARY selection erişimi |
| `xclip` | X11 fallback |
| `xdotool` | İlk açılışta cursor pozisyonunu öğrenmek için |
| `python-evdev` | Global Ctrl+C+C ve Wayland-bağımsız cursor takibi |

### Yetki gereksinimi

evdev `/dev/input/event*` cihazlarını doğrudan okur. Kullanıcının `input` grubunda olması gerekir:

```bash
sudo usermod -aG input $USER
# Sonra çıkış yapıp tekrar giriş yapın (veya `newgrp input`)
```

---

## Kurulum

```bash
git clone <repo-url> translateV2
cd translateV2

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### DeepL API anahtarı

Proje kökünde `.env` dosyası oluşturun:

```env
DEEPL_API_KEY=your_api_key_here
```

> Free hesap [deepl.com/pro-api](https://www.deepl.com/pro-api) üzerinden alınabilir (aylık 500 000 karakter ücretsiz).

---

## Çalıştırma

```bash
python main.py
```

Uygulama açılırken terminale şunu yazmalı:

```
[evdev] watching N keyboard(s) and M mouse device(s)
```

Bu satır görünmüyorsa `input` grup üyeliği aktif değildir (yukarıdaki yetki bölümüne bakın).

---

## Kullanım

### Ana pencere

Üç sekmeden oluşur:

- **📖 Sözlük** — kelime yazın, Tureng'den TR↔EN sonuçlar gelir, her satırdaki `💾 Kaydet` ile veritabanına eklenir.
- **🌐 Çeviri** — sol panele metin yazın; dil seçicilerinin ortasındaki `⇄` swap butonu metni de değiştirir. Save ile çeviri kaydedilir.
- **📝 Kelimelerim** — kayıtlı tüm çeviriler. `➕ Ekle` ile manuel kelime ekleyin, `📥 Dışa Aktar` ile JSON/CSV/Excel'e aktarın.

### Overlay (en kritik bileşen)

1. Herhangi bir uygulamada metin seçin
2. Birkaç ms sonra cursor yakınında küçük `🌐` butonu çıkar
3. Butona tıklayın → ortada büyük çeviri paneli açılır
4. Pano genelinde Ctrl+C'ye iki kez bas → seçim yoksa ana pencere açılır, varsa popup çıkar

Popup paneli:
- Tek kelime seçilmişse otomatik **Dictionary** sekmesi
- Birden fazla kelime/cümle ise otomatik **Translator** sekmesi
- Boş bir yere tıklayınca otomatik kapanır
- Kenarlardan resize, başlık çubuğundan sürükle
- `Edit` → ana uygulamanın Çeviri sekmesinde düzenlemeye geçer

---

## Mimari

```
translateV2/
├── main.py                       # Giriş noktası — QT_QPA_PLATFORM=xcb forced
├── words.db                      # SQLite, runtime'da oluşturulur
├── .env                          # DEEPL_API_KEY
└── app/
    ├── config.py                 # Path/timing sabitleri
    ├── styles.py                 # Merkezi QSS dark tema
    ├── widgets.py                # Paylaşılan widget'lar (BoundedComboBox)
    ├── main_window.py            # 3 sekme + tray + overlay orkestratörü
    ├── APIs/
    │   ├── tureng.py             # Tureng HTML scraper
    │   └── deeplTranslate.py     # DeepL wrapper
    ├── db/
    │   ├── models.py             # SavedWord dataclass
    │   └── database.py           # SQLite CRUD
    ├── tabs/
    │   ├── dictionary_tab.py
    │   ├── translate_tab.py
    │   └── words_tab.py
    └── overlay/
        ├── selection_watcher.py  # PRIMARY selection polling
        ├── evdev_hooks.py        # /dev/input/event* — Ctrl+C+C + cursor pos
        ├── popup_button.py       # Selection sonrası küçük buton
        └── popup_panel.py        # Frameless çeviri paneli
```

---

## Wayland notları

Wayland, güvenlik gerekçesiyle global pencere overlay'lerini, klavye hook'larını ve cursor pozisyonu paylaşımını kısıtlar. Uygulama bu kısıtları aşmak için aşağıdaki katmanları kullanır:

| Sorun | Çözüm |
|-------|-------|
| Native Wayland uygulamasından gelen PRIMARY selection X11'e senkronize edilmiyor | `wl-paste --primary --type text/plain` ile compositor'a doğrudan sorgu |
| Global Ctrl+C+C duyulmuyor | `evdev` ile `/dev/input/event*` doğrudan okuma |
| Cursor pozisyonu XWayland penceresi focuslu olmadığında bayatlıyor | evdev `REL_X`/`REL_Y` event'leri biriktirilerek absolute pozisyon tutuluyor |
| Frameless overlay penceresi Wayland'de reddediliyor | Uygulama `QT_QPA_PLATFORM=xcb` ile XWayland'de çalışıyor |

Kullanıcı `QT_QPA_PLATFORM=wayland python main.py` ile native Wayland'e zorlayabilir, ama overlay özellikleri kısıtlanır.

---

## Sorun giderme

| Hata | Çözüm |
|------|-------|
| `ModuleNotFoundError: No module named 'deepl'` | Venv aktif değil. `source .venv/bin/activate` |
| `[evdev] N device(s) refused (PermissionError)` | `input` grubunda değilsiniz. `sudo usermod -aG input $USER` + relogin |
| `Kritik Hata: DEEPL_API_KEY bulunamadı` | `.env` dosyası eksik veya yanlış konumda |
| Popup buton seçim sonrası rastgele konumda | `xdotool` kurulmamış olabilir, veya evdev fokus dışı çalışıyor — boşver, Ctrl+C+C kısayolu daima merkezde çalışır |
| Excel dışa aktarma "openpyxl gereklidir" diyor | `pip install openpyxl` |

---

## Lisans

Şahsi proje. Bağımlılıklar kendi lisansları altındadır:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — GPLv3 / Commercial
- [deepl-python](https://github.com/DeepLcom/deepl-python) — MIT
- [openpyxl](https://openpyxl.readthedocs.io/) — MIT
- [python-evdev](https://github.com/gvalkov/python-evdev) — BSD-3
