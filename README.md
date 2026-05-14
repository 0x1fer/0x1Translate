# TranslateApp

PyQt6 tabanlı masaüstü çeviri uygulaması (Linux + Windows). Sözlük (Tureng) ve çeviri (DeepL) servislerini tek bir arayüzde toplar, sistem genelinde metin yakalama overlay'i ile seçilen metni anında çevirir.

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

- **Python:** 3.11+
- **OS:** Linux (Arch / KDE Plasma 6 üzerinde test edildi) veya Windows 10/11
- **Görüntü sunucu (Linux):** X11 veya Wayland (Wayland'de uygulama otomatik XWayland'e geçer)

### Platform farkları

| | Linux | Windows |
|---|---|---|
| Ctrl+C+C global kısayolu | ✅ (evdev) | ✅ (pynput Win32 hook) |
| Tepsi simgesi & arka plan | ✅ | ✅ |
| **Metin seçince otomatik 🌐 buton** | ✅ | ❌ — Windows'ta PRIMARY selection yok, popup yalnızca Ctrl+C+C ile açılır |
| Özel sistem paketi | wl-clipboard / xclip / xdotool | yok |
| Özel yetki | `input` grubu üyeliği | yok |

### Linux: sistem paketleri (pacman / apt / dnf)

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

### Linux: yetki gereksinimi

evdev `/dev/input/event*` cihazlarını doğrudan okur. Kullanıcının `input` grubunda olması gerekir:

```bash
sudo usermod -aG input $USER
# Sonra çıkış yapıp tekrar giriş yapın (veya `newgrp input`)
```

### Windows: özel gereksinim yok

- Sistem paketi gerekmez (`wl-clipboard`, `xclip`, vs. Linux'a özeldir).
- Yönetici (admin) yetkisi gerekmez — `pynput` kullanıcı modu Win32 keyboard hook'u kullanır.
- Antivirüs / Defender bazen klavye hook'lu uygulamaları uyarı olarak işaretleyebilir.

---

## Kurulum

### Linux

```bash
git clone <repo-url> translateV2
cd translateV2

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
git clone <repo-url> translateV2
cd translateV2

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` platform-koşullu marker'lar kullanır: Linux'ta yalnızca `evdev`, Windows'ta yalnızca `pynput` kurulur.

### DeepL API anahtarı

Proje kökünde `.env` dosyası oluşturun:

```env
DEEPL_API_KEY=your_api_key_here
```

> Free hesap [deepl.com/pro-api](https://www.deepl.com/pro-api) üzerinden alınabilir (aylık 500 000 karakter ücretsiz).

---

## Çalıştırma

```bash
python main.py        # Linux
py main.py            # Windows (veya `python main.py`)
```

Uygulama açılırken terminale platforma göre şu satırlardan biri yazılır:

```
[evdev] watching N keyboard(s) and M mouse device(s)   # Linux
[hotkey] Win32 global hotkey listener active           # Windows
```

Linux'ta evdev satırı görünmüyorsa `input` grup üyeliği aktif değildir (yukarıdaki yetki bölümüne bakın). Windows'ta `pynput not installed` mesajı görünüyorsa `pip install pynput` çalıştırın.

---

## Kullanım

### Ana pencere

Üç sekmeden oluşur:

- **📖 Sözlük** — kelime yazın, Tureng'den TR↔EN sonuçlar gelir, her satırdaki `💾 Kaydet` ile veritabanına eklenir.
- **🌐 Çeviri** — sol panele metin yazın; dil seçicilerinin ortasındaki `⇄` swap butonu metni de değiştirir. Save ile çeviri kaydedilir.
- **📝 Kelimelerim** — kayıtlı tüm çeviriler. `➕ Ekle` ile manuel kelime ekleyin, `📥 Dışa Aktar` ile JSON/CSV/Excel'e aktarın.
- **⚙️ Ayarlar** — klavye kısayolu (modifier + tetik harfi), DeepL API anahtarı ve uygulama dili (TR/EN). Ayarlar `settings.json` dosyasına kaydedilir; kısayol ve API anahtarı anında, dil değişikliği yeniden başlatma sonrası devreye girer.

### Overlay (en kritik bileşen)

**Linux:**
1. Herhangi bir uygulamada metin seçin
2. Birkaç ms sonra cursor yakınında küçük `🌐` butonu çıkar
3. Butona tıklayın → ortada büyük çeviri paneli açılır
4. Ya da metni kopyaladıktan sonra Ctrl+C'ye bir kez daha bas (Ctrl+C+C) → clipboard'taki metin popup'ta açılır

**Windows:**
1. Herhangi bir uygulamada metin seçin ve **Ctrl+C** ile kopyalayın
2. Hemen ardından **bir kez daha Ctrl+C** (toplam Ctrl+C+C) → popup açılır
3. Clipboard boşsa veya metin değilse Ctrl+C+C ana uygulamayı öne getirir

> Not: Windows'ta PRIMARY selection olmadığı için "metni seçince otomatik buton" davranışı yoktur — sadece Ctrl+C+C kısayolu vardır.

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
├── settings.json                 # Kullanıcı ayarları (kısayol, dil, API key)
├── .env                          # DEEPL_API_KEY (Ayarlar > API key boş bırakılırsa fallback)
└── app/
    ├── config.py                 # Path/timing sabitleri
    ├── settings.py               # settings.json yükle/kaydet
    ├── i18n.py                   # TR / EN sözlüğü, tr() fonksiyonu
    ├── styles.py                 # Merkezi QSS dark tema
    ├── widgets.py                # Paylaşılan widget'lar (BoundedComboBox)
    ├── main_window.py            # 4 sekme + tray + overlay orkestratörü
    ├── APIs/
    │   ├── tureng.py             # Tureng HTML scraper
    │   └── deeplTranslate.py     # DeepL wrapper
    ├── db/
    │   ├── models.py             # SavedWord dataclass
    │   └── database.py           # SQLite CRUD
    ├── tabs/
    │   ├── dictionary_tab.py
    │   ├── translate_tab.py
    │   ├── words_tab.py
    │   └── settings_tab.py       # Klavye kısayolu, API key, dil
    └── overlay/
        ├── hotkey_hooks.py       # Platform dispatcher (Linux/Windows)
        ├── evdev_hooks.py        # Linux: /dev/input/event* — Ctrl+C+C + cursor pos
        ├── _win_hooks.py         # Windows: pynput Win32 keyboard hook
        ├── selection_watcher.py  # Linux only: PRIMARY selection polling
        ├── popup_button.py       # Linux only: selection sonrası küçük buton
        └── popup_panel.py        # Frameless çeviri paneli (her iki OS'ta)
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

| Hata | Platform | Çözüm |
|------|----------|-------|
| `ModuleNotFoundError: No module named 'deepl'` | Hepsi | Venv aktif değil. Linux: `source .venv/bin/activate` · Windows: `.\.venv\Scripts\Activate.ps1` |
| `[evdev] N device(s) refused (PermissionError)` | Linux | `input` grubunda değilsiniz. `sudo usermod -aG input $USER` + relogin |
| `[hotkey] pynput not installed` | Windows | `pip install pynput` |
| `Kritik Hata: DEEPL_API_KEY bulunamadı` | Hepsi | `.env` dosyası eksik veya yanlış konumda |
| Popup buton seçim sonrası rastgele konumda | Linux | `xdotool` kurulmamış olabilir; Ctrl+C+C kısayolu daima merkezde çalışır |
| Ctrl+C+C tepki vermiyor | Windows | Antivirüs klavye hook'unu engellemiş olabilir; bir kez yönetici olarak çalıştırıp izin verin |
| Excel dışa aktarma "openpyxl gereklidir" diyor | Hepsi | `pip install openpyxl` |

---

## Lisans

Şahsi proje. Bağımlılıklar kendi lisansları altındadır:
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — GPLv3 / Commercial
- [deepl-python](https://github.com/DeepLcom/deepl-python) — MIT
- [openpyxl](https://openpyxl.readthedocs.io/) — MIT
- [python-evdev](https://github.com/gvalkov/python-evdev) — BSD-3
