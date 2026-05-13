import os
import subprocess

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QSystemTrayIcon, QMenu,
    QStatusBar, QLabel, QApplication,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction, QGuiApplication

from app.db.database import Database
from app.tabs.dictionary_tab import DictionaryTab
from app.tabs.translate_tab import TranslateTab
from app.tabs.words_tab import WordsTab
from app.overlay.selection_watcher import SelectionWatcher
from app.overlay.popup_button import PopupButton
from app.overlay.popup_panel import PopupPanel
from app.overlay import evdev_hooks
from app.config import CONFIG
from app import styles


def _read_clipboard_text() -> str:
    """
    Read CLIPBOARD (not PRIMARY) as plain text. Returns an empty string when
    the clipboard holds non-text content (e.g. an image), so callers can
    distinguish "no usable selection" from a real string.
    """
    if os.environ.get("WAYLAND_DISPLAY"):
        try:
            # First check what mime-types are offered. If text/* isn't on
            # offer, wl-paste --no-newline would dump binary bytes and
            # Python's text=True decoder would explode on UnicodeDecodeError.
            types = subprocess.run(
                ["wl-paste", "--list-types"],
                capture_output=True, text=True, timeout=0.4,
            )
            if types.returncode != 0 or "text/" not in types.stdout.lower():
                return ""
            r = subprocess.run(
                ["wl-paste", "--no-newline", "--type", "text/plain"],
                capture_output=True, text=True, timeout=0.4,
                errors="replace",
            )
            if r.returncode == 0 and r.stdout:
                return r.stdout
        except (FileNotFoundError, subprocess.TimeoutExpired,
                UnicodeDecodeError, OSError):
            pass

    try:
        return QApplication.clipboard().text()
    except Exception:
        return ""

try:
    from app.APIs.tureng import TurengAPI
    from app.APIs.deeplTranslate import DeeplAPI

    _tureng = TurengAPI()
    try:
        _deepl: DeeplAPI | None = DeeplAPI()
    except ValueError:
        _deepl = None
except Exception:
    _tureng = None  # type: ignore
    _deepl = None


def _make_tray_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(Qt.GlobalColor.transparent)
    painter = QPainter(px)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(styles.C["accent"]))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    painter.drawText(px.rect(), Qt.AlignmentFlag.AlignCenter, "T")
    painter.end()
    return QIcon(px)


class MainWindow(QMainWindow):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db = db
        self.setWindowTitle("TranslateApp")
        self.resize(1200, 720)
        self.setMinimumSize(900, 600)

        self._build_ui()
        self._build_tray()
        self._build_overlay()
        self._connect_signals()
        self._set_active_tab(0)

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralwidget")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navigation bar
        nav = QWidget()
        nav.setFixedHeight(56)
        nav.setStyleSheet(
            f"background-color: {styles.C['bg_panel']};"
            f"border-bottom: 1px solid {styles.C['border']};"
        )
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        self._btn_dict      = QPushButton("📖  Sözlük")
        self._btn_translate = QPushButton("🌐  Çeviri")
        self._btn_words     = QPushButton("📝  Kelimelerim")

        for btn in (self._btn_dict, self._btn_translate, self._btn_words):
            btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            btn.setMinimumWidth(180)
            btn.setFixedHeight(56)
            btn.setStyleSheet(styles.NAV_BUTTON)
            nav_layout.addWidget(btn)

        nav_layout.addStretch(1)
        root.addWidget(nav)

        # Stacked tabs
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background-color: {styles.C['bg_main']};")
        root.addWidget(self._stack, 1)

        self._dict_tab      = DictionaryTab()
        self._translate_tab = TranslateTab()
        self._words_tab     = WordsTab(self._db)

        self._stack.addWidget(self._dict_tab)
        self._stack.addWidget(self._translate_tab)
        self._stack.addWidget(self._words_tab)

        # Status bar
        sb = QStatusBar()
        sb.setSizeGripEnabled(False)
        self.setStatusBar(sb)
        self._status = QLabel("Hazır")
        sb.addWidget(self._status)

    def _build_tray(self):
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(_make_tray_icon())
        self._tray.setToolTip("TranslateApp")

        menu = QMenu()
        show_action = QAction("Göster / Gizle", self)
        quit_action = QAction("Çıkış", self)
        menu.addAction(show_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        show_action.triggered.connect(self._toggle_window)
        quit_action.triggered.connect(self._quit_app)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _build_overlay(self):
        self._watcher = SelectionWatcher(CONFIG["selection_poll_interval_ms"])
        # Running under XWayland (xcb): popup windows can float freely with
        # no transient-parent requirement. Using self as parent keeps them
        # associated with the app (no separate taskbar entry, correct WM hints).
        self._popup_btn   = PopupButton(self)
        self._popup_panel = PopupPanel(_tureng, _deepl, self) if _tureng else None
        # evdev: reads /dev/input/event* directly, bypassing Wayland's focus
        # restrictions. Provides global Ctrl+C+C detection and accurate cursor
        # tracking (XWayland's view stops updating when a Wayland app is focused).
        self._evdev = evdev_hooks.init(self)

    def _connect_signals(self):
        self._btn_dict.clicked.connect(lambda: self._set_active_tab(0))
        self._btn_translate.clicked.connect(lambda: self._set_active_tab(1))
        self._btn_words.clicked.connect(lambda: self._set_active_tab(2))

        self._translate_tab.save_requested.connect(self._save_word)
        self._dict_tab.save_requested.connect(self._save_word)

        self._watcher.text_selected.connect(self._on_text_selected)
        self._popup_btn.translate_requested.connect(self._on_translate_requested)

        if self._popup_panel:
            self._popup_panel.save_requested.connect(self._save_word)
            self._popup_panel.search_dict_requested.connect(self._on_search_dict_requested)
            self._popup_panel.edit_requested.connect(self._on_popup_edit_requested)

        self._evdev.double_ctrl_c.connect(self._on_ctrl_c_c)

    # ------------------------------------------------------------------
    def _set_active_tab(self, index: int):
        self._stack.setCurrentIndex(index)
        buttons = [self._btn_dict, self._btn_translate, self._btn_words]
        for i, btn in enumerate(buttons):
            btn.setStyleSheet(styles.NAV_BUTTON_ACTIVE if i == index else styles.NAV_BUTTON)

    def _save_word(self, original: str, translation: str, source_lang: str):
        self._words_tab.add_word(original, translation, source_lang)
        preview = original[:30] + "…" if len(original) > 30 else original
        self._status.setText(f"✓ '{preview}' kaydedildi.")

    @pyqtSlot(str, int, int)
    def _on_text_selected(self, text: str, x: int, y: int):
        self._popup_btn.show_near(text, x, y)

    @pyqtSlot(str, int, int)
    def _on_translate_requested(self, text: str, x: int, y: int):
        if self._popup_panel:
            self._popup_panel.show_for(text, x, y)

    @pyqtSlot(str)
    def _on_search_dict_requested(self, word: str):
        self._set_active_tab(0)
        self._dict_tab.set_search_word(word)
        self.show()
        self.raise_()
        self.activateWindow()

    @pyqtSlot(str, str, str)
    def _on_popup_edit_requested(self, text: str, src: str, tgt: str):
        """Popup 'Edit' button → bring up the Translate tab pre-filled."""
        self._set_active_tab(1)   # Translate tab
        self._translate_tab.set_input(text, src, tgt)
        self.show()
        self.raise_()
        self.activateWindow()

    @pyqtSlot()
    def _on_ctrl_c_c(self):
        """Ctrl+C+C detected via evdev → open popup at screen center with clipboard text."""
        if not self._popup_panel:
            return
        # The clipboard might not be updated yet (KWin syncs Wayland → X11 with
        # a tiny delay). Read after a short timeout so we see the new content.
        QTimer.singleShot(80, self._open_popup_from_clipboard)

    def _open_popup_from_clipboard(self):
        try:
            text = _read_clipboard_text().strip()
        except Exception:
            text = ""

        if not text or not self._popup_panel:
            # No usable text (empty clipboard, image, etc.) → show the main
            # app instead of crashing or popping an empty translation panel.
            self.show()
            self.raise_()
            self.activateWindow()
            return

        x, y = evdev_hooks.get_cursor_pos()
        self._popup_panel.show_for(text, x, y)

    # ------------------------------------------------------------------
    def _toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_window()

    def _quit_app(self):
        self._watcher.stop()
        evdev_hooks.shutdown()
        QApplication.quit()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self._tray.showMessage(
            "TranslateApp",
            "Uygulama arka planda çalışmaya devam ediyor.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def start_watcher(self):
        self._watcher.start()
