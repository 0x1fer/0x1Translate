import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QComboBox, QStackedWidget, QApplication, QSizePolicy,
)
from PyQt6.QtCore import Qt, QEvent, QThread, QTimer, QPoint, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QGuiApplication

from app.APIs.tureng import TurengAPI
from app.APIs.deeplTranslate import DeeplAPI
from app.widgets import BoundedComboBox


# ---------------------------------------------------------------------------
# Theme (Catppuccin-mocha-inspired, per spec)
# ---------------------------------------------------------------------------
BG       = "#1e1e2e"
SURFACE  = "#2a2a3d"
SURFACE2 = "#363651"
BORDER   = "#3a3a5c"
TEXT     = "#cdd6f4"
MUTED    = "#6c7086"
ACCENT   = "#cba6f7"

# ---------------------------------------------------------------------------
# Languages (compact subset; full list lives in translate_tab.py)
# ---------------------------------------------------------------------------
DEEPL_SOURCES: list[tuple[str | None, str]] = [
    (None,   "Otomatik Algıla"),
    ("AR",   "Arapça"),
    ("BG",   "Bulgarca"),
    ("CS",   "Çekçe"),
    ("DA",   "Danca"),
    ("DE",   "Almanca"),
    ("EL",   "Yunanca"),
    ("EN",   "İngilizce"),
    ("ES",   "İspanyolca"),
    ("ET",   "Estonca"),
    ("FI",   "Fince"),
    ("FR",   "Fransızca"),
    ("HU",   "Macarca"),
    ("ID",   "Endonezce"),
    ("IT",   "İtalyanca"),
    ("JA",   "Japonca"),
    ("KO",   "Korece"),
    ("LT",   "Litvanca"),
    ("LV",   "Letonca"),
    ("NB",   "Norveççe (Bokmål)"),
    ("NL",   "Felemenkçe"),
    ("PL",   "Lehçe"),
    ("PT",   "Portekizce"),
    ("RO",   "Romence"),
    ("RU",   "Rusça"),
    ("SK",   "Slovakça"),
    ("SL",   "Slovence"),
    ("SV",   "İsveççe"),
    ("TR",   "Türkçe"),
    ("UK",   "Ukraynaca"),
    ("ZH",   "Çince"),
]

DEEPL_TARGETS: list[tuple[str, str]] = [
    ("AR",      "Arapça"),
    ("BG",      "Bulgarca"),
    ("CS",      "Çekçe"),
    ("DA",      "Danca"),
    ("DE",      "Almanca"),
    ("EL",      "Yunanca"),
    ("EN-GB",   "İngilizce (İngiltere)"),
    ("EN-US",   "İngilizce (Amerika)"),
    ("ES",      "İspanyolca"),
    ("ET",      "Estonca"),
    ("FI",      "Fince"),
    ("FR",      "Fransızca"),
    ("HU",      "Macarca"),
    ("ID",      "Endonezce"),
    ("IT",      "İtalyanca"),
    ("JA",      "Japonca"),
    ("KO",      "Korece"),
    ("LT",      "Litvanca"),
    ("LV",      "Letonca"),
    ("NB",      "Norveççe (Bokmål)"),
    ("NL",      "Felemenkçe"),
    ("PL",      "Lehçe"),
    ("PT-BR",   "Portekizce (Brezilya)"),
    ("PT-PT",   "Portekizce (Portekiz)"),
    ("RO",      "Romence"),
    ("RU",      "Rusça"),
    ("SK",      "Slovakça"),
    ("SL",      "Slovence"),
    ("SV",      "İsveççe"),
    ("TR",      "Türkçe"),
    ("UK",      "Ukraynaca"),
    ("ZH-HANS", "Çince (Basitleştirilmiş)"),
    ("ZH-HANT", "Çince (Geleneksel)"),
]


# ---------------------------------------------------------------------------
# Background workers
# ---------------------------------------------------------------------------
class _TurengWorker(QThread):
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, api: TurengAPI, word: str):
        super().__init__()
        self._api  = api
        self._word = word

    def run(self):
        try:
            self.finished.emit(self._api.getWord(self._word))
        except Exception as e:
            self.error.emit(str(e))


class _DeepLWorker(QThread):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)

    def __init__(self, api: DeeplAPI, text: str, target: str, source: str | None):
        super().__init__()
        self._api    = api
        self._text   = text
        self._target = target
        self._source = source

    def run(self):
        try:
            self.finished.emit(self._api.translate(self._text, self._target, self._source))
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------------------------------------------------------
# Title bar — handles drag-to-move
# ---------------------------------------------------------------------------
class _TitleBar(QWidget):
    """Custom title bar; whole bar is a drag handle for the parent window."""

    close_requested = pyqtSignal()
    tab_changed     = pyqtSignal(int)  # 0 = Translator, 1 = Dictionary

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(42)
        self.setStyleSheet(f"background-color: {BG}; border-bottom: 1px solid {BORDER};")
        self._drag_offset: QPoint | None = None
        self._build()

    def _build(self):
        h = QHBoxLayout(self)
        h.setContentsMargins(12, 0, 6, 0)
        h.setSpacing(6)

        icon = QLabel("◆")
        icon.setStyleSheet(f"color: {ACCENT}; font-size: 13px; background: transparent;")
        h.addWidget(icon)
        h.addSpacing(4)

        self._tab_translator = self._make_tab("⇄", "Translator")
        self._tab_dictionary = self._make_tab("📖", "Dictionary")
        h.addWidget(self._tab_translator)
        h.addWidget(self._tab_dictionary)
        h.addStretch(1)

        close = QPushButton("✕")
        close.setFixedSize(26, 26)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {MUTED};
                border: none;
                border-radius: 6px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {TEXT};
                background-color: {SURFACE2};
            }}
        """)
        close.clicked.connect(self.close_requested.emit)
        h.addWidget(close)

        self._tab_translator.clicked.connect(lambda: self.tab_changed.emit(0))
        self._tab_dictionary.clicked.connect(lambda: self.tab_changed.emit(1))

        self.set_active_tab(0)

    def _make_tab(self, icon: str, text: str) -> QPushButton:
        b = QPushButton(f"{icon}  {text}")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setFixedHeight(36)
        b.setFlat(True)
        return b

    def set_active_tab(self, idx: int):
        for i, btn in enumerate((self._tab_translator, self._tab_dictionary)):
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {TEXT};
                        background: transparent;
                        border: none;
                        border-bottom: 2px solid {ACCENT};
                        padding: 0 12px;
                        font-size: 14px;
                        font-weight: 600;
                        text-align: center;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        color: {MUTED};
                        background: transparent;
                        border: none;
                        border-bottom: 2px solid transparent;
                        padding: 0 12px;
                        font-size: 14px;
                        text-align: center;
                    }}
                    QPushButton:hover {{
                        color: {TEXT};
                    }}
                """)

    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            self._drag_offset = event.globalPosition().toPoint() - win.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and (event.buttons() & Qt.MouseButton.LeftButton):
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)


# ---------------------------------------------------------------------------
# Text area: dark surface, drag handle on left, copy button bottom-right
# ---------------------------------------------------------------------------
class _TextArea(QWidget):
    copy_requested = pyqtSignal()

    def __init__(self, read_only: bool = False, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {SURFACE};
                border-radius: 8px;
            }}
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # Drag handle (visual only)
        handle = QLabel("⠿")
        handle.setStyleSheet(f"color: {MUTED}; font-size: 16px; background: transparent;")
        handle.setFixedWidth(20)
        handle.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        handle.setContentsMargins(0, 10, 0, 0)
        h.addWidget(handle)

        self.text = QTextEdit()
        self.text.setReadOnly(read_only)
        self.text.setPlaceholderText(placeholder)
        self.text.setAcceptRichText(False)
        if read_only:
            # No keyboard input — popup is for display only. Mouse selection
            # for copy still works via ClickFocus when the user clicks the text.
            self.text.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
            self.text.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
                | Qt.TextInteractionFlag.TextSelectableByKeyboard
            )
        self.text.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                color: {TEXT};
                border: none;
                font-size: 15px;
                padding: 10px 12px 30px 4px;
                selection-background-color: {ACCENT};
            }}
        """)
        h.addWidget(self.text, 1)

        # Copy button overlay (bottom-right)
        self._copy = QPushButton("📋", self)
        self._copy.setFixedSize(26, 26)
        self._copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self._copy.setToolTip("Kopyala")
        self._copy.setStyleSheet(f"""
            QPushButton {{
                background-color: {SURFACE2};
                color: {TEXT};
                border: none;
                border-radius: 6px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT};
                color: {BG};
            }}
        """)
        self._copy.clicked.connect(self._on_copy)

    def _on_copy(self):
        QApplication.clipboard().setText(self.text.toPlainText())
        self.copy_requested.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._copy.move(self.width() - self._copy.width() - 8,
                        self.height() - self._copy.height() - 8)


# ---------------------------------------------------------------------------
# Helper: styled language combobox with chevron arrow
# ---------------------------------------------------------------------------
def _make_combo(items: list[tuple], default_data=None) -> QComboBox:
    cb = BoundedComboBox()
    cb.setCursor(Qt.CursorShape.PointingHandCursor)
    cb.setMaxVisibleItems(8)
    cb.setStyleSheet(f"""
        QComboBox {{
            background-color: {SURFACE};
            color: {TEXT};
            border: none;
            border-radius: 6px;
            padding: 6px 24px 6px 10px;
            font-size: 14px;
            min-height: 24px;
        }}
        QComboBox:hover {{
            background-color: {SURFACE2};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {MUTED};
            margin-right: 6px;
        }}
        /* Cascade into the popup container/view so the popup also has the
           dark theme AND a hard height cap (some styles ignore
           setMaxVisibleItems but always honour max-height in CSS). */
        QComboBox QAbstractItemView {{
            background-color: {SURFACE};
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 6px;
            selection-background-color: {ACCENT};
            selection-color: {BG};
            outline: none;
            padding: 4px;
            font-size: 14px;
            max-height: 250px;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 28px;
            padding: 4px 10px;
        }}
    """)
    for code, name in items:
        cb.addItem(name, code)

    # The popup view is a separate top-level window and Qt's parent-cascade
    # stylesheet selectors don't always reach it — particularly when the
    # parent is Qt.WindowType.Popup. Style the view directly so it always
    # renders in the dark theme.
    view = cb.view()
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    # setMaxVisibleItems() is ignored by several Qt styles. Force the popup
    # height directly so that only ~8 rows are visible and the rest scroll.
    ROW_PX = 30                                  # matches item padding+font
    view.setMaximumHeight(ROW_PX * 8 + 12)       # 8 rows + small padding
    view.setMinimumWidth(160)
    view.setStyleSheet(f"""
        QAbstractItemView {{
            background-color: {SURFACE};
            color: {TEXT};
            border: 1px solid {BORDER};
            border-radius: 6px;
            selection-background-color: {ACCENT};
            selection-color: {BG};
            outline: none;
            padding: 4px;
            font-size: 14px;
        }}
        QAbstractItemView::item {{
            min-height: 26px;
            padding: 4px 10px;
            color: {TEXT};
            background-color: transparent;
        }}
        QAbstractItemView::item:hover {{
            background-color: {SURFACE2};
        }}
        QAbstractItemView::item:selected {{
            background-color: {ACCENT};
            color: {BG};
        }}
        QScrollBar:vertical {{
            background: {SURFACE};
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {SURFACE2};
            border-radius: 5px;
            min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {ACCENT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0; border: none; background: none;
        }}
    """)
    # The popup container has its own frame/background — force opaque.
    if view.window() is not None:
        view.window().setStyleSheet(f"background-color: {SURFACE}; border-radius: 6px;")

    if default_data is not None:
        for i in range(cb.count()):
            if cb.itemData(i) == default_data:
                cb.setCurrentIndex(i)
                break
    return cb


# ---------------------------------------------------------------------------
# Main popup widget
# ---------------------------------------------------------------------------
class PopupPanel(QWidget):
    """Frameless, draggable, resizable translator/dictionary popup."""

    save_requested        = pyqtSignal(str, str, str)   # original, translation, source_lang
    search_dict_requested = pyqtSignal(str)
    edit_requested        = pyqtSignal(str, str, str)   # text, src_code, tgt_code

    INITIAL_W, INITIAL_H = 460, 340
    MIN_W,     MIN_H     = 360, 240
    RESIZE_MARGIN        = 6

    def __init__(self, tureng_api: TurengAPI, deepl_api: DeeplAPI | None, parent=None):
        # Tool, not Popup: Qt.WindowType.Popup grabs all input which breaks
        # combo-box dropdowns on XWayland (the dropdown is itself a popup and
        # the chain doesn't always render correctly). We implement the
        # outside-click-closes behaviour manually via WindowDeactivate.
        super().__init__(
            parent,
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.resize(self.INITIAL_W, self.INITIAL_H)
        self.setMinimumSize(self.MIN_W, self.MIN_H)

        self._tureng_api = tureng_api
        self._deepl_api  = deepl_api

        self._original_text   = ""
        self._translated_text = ""
        self._dict_results: list[str] = []
        self._is_phrase       = False

        # Resize state
        self._resize_edge: str | None = None
        self._resize_start_geo: QRect | None = None
        self._resize_start_pos: QPoint | None = None

        self._worker: QThread | None = None

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # Outer 6 px transparent margin = resize zone
        outer = QVBoxLayout(self)
        outer.setContentsMargins(self.RESIZE_MARGIN, self.RESIZE_MARGIN,
                                 self.RESIZE_MARGIN, self.RESIZE_MARGIN)
        outer.setSpacing(0)

        self._root = QWidget()
        self._root.setObjectName("popup_root")
        self._root.setStyleSheet(f"""
            #popup_root {{
                background-color: {BG};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        outer.addWidget(self._root)

        v = QVBoxLayout(self._root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        # Title bar
        self._title_bar = _TitleBar(self._root)
        self._title_bar.tab_changed.connect(self._set_tab)
        self._title_bar.close_requested.connect(self.hide)
        v.addWidget(self._title_bar)

        # Stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        v.addWidget(self._stack, 1)

        self._stack.addWidget(self._build_translator_page())
        self._stack.addWidget(self._build_dictionary_page())

    # ---- Translator page ---------------------------------------------
    def _build_translator_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(10)

        # Language row
        lang_row = QHBoxLayout()
        lang_row.setSpacing(6)

        self._tr_src = _make_combo(DEEPL_SOURCES, default_data=None)
        self._tr_tgt = _make_combo(DEEPL_TARGETS, default_data="TR")

        swap = QPushButton("⇄")
        swap.setFixedSize(30, 30)
        swap.setCursor(Qt.CursorShape.PointingHandCursor)
        swap.setToolTip("Dilleri değiştir")
        swap.setStyleSheet(f"""
            QPushButton {{
                background-color: {SURFACE};
                color: {TEXT};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT};
                color: {BG};
            }}
        """)
        swap.clicked.connect(self._swap_langs)

        # Swap sits between the two language pickers.
        lang_row.addWidget(self._tr_src, 1)
        lang_row.addSpacing(2)
        lang_row.addWidget(swap)
        lang_row.addSpacing(2)
        lang_row.addWidget(self._tr_tgt, 1)
        v.addLayout(lang_row)

        # Text area
        self._tr_area = _TextArea(read_only=True, placeholder="Çeviri burada görünecek…")
        v.addWidget(self._tr_area, 1)

        # Bottom bar
        bottom = self._make_bottom_bar()
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(self._ghost_btn_style())
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.clicked.connect(self._on_edit_clicked)
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(self._primary_btn_style())
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_from_translator)
        bottom.layout().addWidget(edit_btn)
        bottom.layout().addWidget(save_btn)
        self._tr_save = save_btn
        self._tr_edit = edit_btn
        v.addWidget(bottom)

        # Language changes → re-translate (text itself is read-only)
        self._tr_src.currentIndexChanged.connect(self._maybe_retranslate)
        self._tr_tgt.currentIndexChanged.connect(self._maybe_retranslate)

        self._retranslate_timer = QTimer(self)
        self._retranslate_timer.setSingleShot(True)
        self._retranslate_timer.setInterval(500)
        self._retranslate_timer.timeout.connect(self._run_translate)

        return page

    # ---- Dictionary page ---------------------------------------------
    def _build_dictionary_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        v = QVBoxLayout(page)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(10)

        # Language row (TR ↔ EN — Tureng is bilingual)
        lang_row = QHBoxLayout()
        lang_row.setSpacing(6)

        self._dc_src = _make_combo([("auto", "Otomatik"), ("en", "İngilizce"), ("tr", "Türkçe")],
                                   default_data="auto")
        self._dc_tgt = _make_combo([("auto", "Otomatik"), ("tr", "Türkçe"), ("en", "İngilizce")],
                                   default_data="auto")

        swap = QPushButton("⇄")
        swap.setFixedSize(30, 30)
        swap.setCursor(Qt.CursorShape.PointingHandCursor)
        swap.setToolTip("Dilleri değiştir")
        swap.setStyleSheet(f"""
            QPushButton {{
                background-color: {SURFACE};
                color: {TEXT};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT};
                color: {BG};
            }}
        """)
        swap.clicked.connect(self._swap_dict_langs)

        lang_row.addWidget(self._dc_src, 1)
        lang_row.addSpacing(2)
        lang_row.addWidget(swap)
        lang_row.addSpacing(2)
        lang_row.addWidget(self._dc_tgt, 1)
        v.addLayout(lang_row)

        # Text area (read-only, results)
        self._dc_area = _TextArea(read_only=True, placeholder="Sözlük sonucu burada görünecek…")
        v.addWidget(self._dc_area, 1)

        # Bottom bar — only Save
        bottom = self._make_bottom_bar()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(self._primary_btn_style())
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_from_dictionary)
        bottom.layout().addWidget(save_btn)
        self._dc_save = save_btn
        v.addWidget(bottom)

        return page

    # ---- Bottom bar helper -------------------------------------------
    def _make_bottom_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"background: transparent; border-top: 1px solid {BORDER};")
        h = QHBoxLayout(bar)
        h.setContentsMargins(8, 8, 8, 8)
        h.setSpacing(6)
        h.addStretch(1)
        return bar

    # ---- Button styles -----------------------------------------------
    @staticmethod
    def _primary_btn_style() -> str:
        return f"""
            QPushButton {{
                background-color: {ACCENT};
                color: {BG};
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: #b794f4;
            }}
            QPushButton:disabled {{
                background-color: {SURFACE2};
                color: {MUTED};
            }}
        """

    @staticmethod
    def _ghost_btn_style() -> str:
        return f"""
            QPushButton {{
                background: transparent;
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 14px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: {SURFACE2};
                border-color: {ACCENT};
            }}
        """

    # ==================================================================
    # PUBLIC API
    # ==================================================================
    def show_for(self, text: str, x: int, y: int):
        """Show popup near (x, y) with the given selected text."""
        self._original_text   = text
        self._translated_text = ""
        self._dict_results    = []
        self._is_phrase       = len(text.split()) > 1

        # Auto-pick tab and run lookup
        if self._is_phrase:
            self._set_tab(0)
            self._tr_area.text.setPlainText("Çevriliyor…")
            self._tr_save.setEnabled(False)
            self._run_translate()
        else:
            self._set_tab(1)
            self._dc_area.text.setPlainText(f"'{text}' aranıyor…")
            self._dc_save.setEnabled(False)
            self._run_dictionary(text)

        self._position_near(x, y)
        self.show()
        self.raise_()
        QTimer.singleShot(80, self.raise_)

    # ==================================================================
    # Tab management
    # ==================================================================
    def _set_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)
        self._title_bar.set_active_tab(idx)

    # ==================================================================
    # Translator behaviour
    # ==================================================================
    def _on_edit_clicked(self):
        """Hand the text off to the main app's Translate tab for editing."""
        src = self._tr_src.currentData() or ""
        tgt = self._tr_tgt.currentData() or "TR"
        self.edit_requested.emit(self._original_text, src or "", tgt)
        self.hide()

    def _maybe_retranslate(self):
        if self._original_text:
            self._retranslate_timer.start()

    def _swap_langs(self):
        s = self._tr_src.currentData()
        t = self._tr_tgt.currentData()
        if t:
            base = t.split("-")[0]
            for i in range(self._tr_src.count()):
                if self._tr_src.itemData(i) == base:
                    self._tr_src.setCurrentIndex(i)
                    break
        if s:
            for i in range(self._tr_tgt.count()):
                td = self._tr_tgt.itemData(i)
                if td == s or td.startswith(s):
                    self._tr_tgt.setCurrentIndex(i)
                    break

    def _run_translate(self):
        if not self._deepl_api or not self._original_text:
            return
        target = self._tr_tgt.currentData() or "TR"
        source = self._tr_src.currentData()

        self._tr_area.text.setPlainText("Çevriliyor…")
        self._tr_save.setEnabled(False)

        worker = _DeepLWorker(self._deepl_api, self._original_text, target, source)
        worker.finished.connect(self._on_translate_done)
        worker.error.connect(self._on_worker_error)
        self._worker = worker
        worker.start()

    def _on_translate_done(self, result: str):
        self._translated_text = result
        self._tr_area.text.setPlainText(result)
        self._tr_save.setEnabled(bool(result))

    # ==================================================================
    # Dictionary behaviour
    # ==================================================================
    def _swap_dict_langs(self):
        s = self._dc_src.currentIndex()
        t = self._dc_tgt.currentIndex()
        # rotate via swap
        s_data = self._dc_src.currentData()
        t_data = self._dc_tgt.currentData()
        for i in range(self._dc_src.count()):
            if self._dc_src.itemData(i) == t_data:
                self._dc_src.setCurrentIndex(i)
                break
        for i in range(self._dc_tgt.count()):
            if self._dc_tgt.itemData(i) == s_data:
                self._dc_tgt.setCurrentIndex(i)
                break

    def _run_dictionary(self, word: str):
        worker = _TurengWorker(self._tureng_api, word)
        worker.finished.connect(self._on_dict_done)
        worker.error.connect(self._on_worker_error)
        self._worker = worker
        worker.start()

    def _on_dict_done(self, results: list):
        self._dict_results = results
        if not results or (len(results) == 1 and results[0].startswith("Hata:")):
            msg = results[0] if results else "Sonuç bulunamadı."
            self._dc_area.text.setPlainText(msg)
            self._dc_save.setEnabled(False)
            return

        lines = []
        for item in results[:12]:
            parts = item.split(" -> ", 1)
            if len(parts) == 2:
                lines.append(f"• {parts[1]}")
            else:
                lines.append(f"• {item}")
        self._translated_text = "\n".join(lines)
        self._dc_area.text.setPlainText(self._translated_text)
        self._dc_save.setEnabled(True)

    # ==================================================================
    # Save handlers
    # ==================================================================
    def _save_from_translator(self):
        if not self._translated_text or not self._original_text:
            return
        src = self._tr_src.currentData() or "AUTO"
        self.save_requested.emit(self._original_text, self._translated_text, src)
        self._flash_button(self._tr_save, "✓ Kaydedildi")

    def _save_from_dictionary(self):
        if not self._translated_text or not self._original_text:
            return
        self.save_requested.emit(self._original_text, self._translated_text, "TR-EN")
        self._flash_button(self._dc_save, "✓ Kaydedildi")

    def _flash_button(self, btn: QPushButton, label: str):
        original = btn.text()
        btn.setText(label)
        btn.setEnabled(False)
        QTimer.singleShot(1500, lambda: (btn.setText(original), btn.setEnabled(True)))

    def _on_worker_error(self, msg: str):
        for area in (self._tr_area, self._dc_area):
            if area.text.toPlainText().endswith("aranıyor…") or area.text.toPlainText() == "Çevriliyor…":
                area.text.setPlainText(f"Hata: {msg}")

    # ==================================================================
    # Positioning
    # ==================================================================
    def _position_near(self, x: int, y: int):
        screen = QGuiApplication.primaryScreen().geometry()
        w = self.width() or self.INITIAL_W
        h = self.height() or self.INITIAL_H
        px = x - w // 2
        py = y + 24
        if px + w > screen.right() - 8:
            px = screen.right() - w - 8
        if px < screen.left() + 8:
            px = screen.left() + 8
        if py + h > screen.bottom() - 8:
            py = y - h - 24
        if py < screen.top() + 8:
            py = screen.top() + 8
        self.move(px, py)

    # ==================================================================
    # Resize from edges (the 6 px transparent margin)
    # ==================================================================
    def _edge_at(self, pos: QPoint) -> str | None:
        m = self.RESIZE_MARGIN + 2  # slightly larger hit area for usability
        w, h = self.width(), self.height()
        on_l = pos.x() <= m
        on_r = pos.x() >= w - m
        on_t = pos.y() <= m
        on_b = pos.y() >= h - m
        if on_t and on_l: return "topleft"
        if on_t and on_r: return "topright"
        if on_b and on_l: return "bottomleft"
        if on_b and on_r: return "bottomright"
        if on_l: return "left"
        if on_r: return "right"
        if on_t: return "top"
        if on_b: return "bottom"
        return None

    def _cursor_for(self, edge: str | None) -> Qt.CursorShape:
        return {
            "left":        Qt.CursorShape.SizeHorCursor,
            "right":       Qt.CursorShape.SizeHorCursor,
            "top":         Qt.CursorShape.SizeVerCursor,
            "bottom":      Qt.CursorShape.SizeVerCursor,
            "topleft":     Qt.CursorShape.SizeFDiagCursor,
            "bottomright": Qt.CursorShape.SizeFDiagCursor,
            "topright":    Qt.CursorShape.SizeBDiagCursor,
            "bottomleft":  Qt.CursorShape.SizeBDiagCursor,
        }.get(edge or "", Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._edge_at(event.position().toPoint())
            if edge:
                self._resize_edge      = edge
                self._resize_start_geo = self.geometry()
                self._resize_start_pos = event.globalPosition().toPoint()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_edge and (event.buttons() & Qt.MouseButton.LeftButton):
            self._do_resize(event.globalPosition().toPoint())
            event.accept()
            return
        edge = self._edge_at(event.position().toPoint())
        self.setCursor(self._cursor_for(edge))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_edge      = None
        self._resize_start_geo = None
        self._resize_start_pos = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    # ------------------------------------------------------------------
    # Click outside → close.
    #
    # On XWayland Qt.WindowType.Popup's auto-close doesn't reliably fire for
    # clicks in other apps. We watch WindowDeactivate instead — fires whenever
    # another window takes focus. We schedule the hide so combo dropdowns
    # (which briefly grab focus) don't cause a false close.
    # ------------------------------------------------------------------
    def event(self, e):
        if e.type() == QEvent.Type.WindowDeactivate:
            QTimer.singleShot(180, self._maybe_close_on_deactivate)
        return super().event(e)

    def _maybe_close_on_deactivate(self):
        if not self.isVisible():
            return
        if self.isActiveWindow():
            return                                    # we re-gained focus
        # If a popup descendant (e.g. a combo dropdown) is open, keep us alive.
        from PyQt6.QtWidgets import QApplication
        popup = QApplication.activePopupWidget()
        if popup is not None and self.isAncestorOf(popup):
            return
        self.hide()

    def _do_resize(self, gpos: QPoint):
        delta = gpos - self._resize_start_pos
        geo   = QRect(self._resize_start_geo)
        edge  = self._resize_edge
        min_w, min_h = self.minimumWidth(), self.minimumHeight()

        if "left" in edge:
            new_w = geo.width() - delta.x()
            if new_w >= min_w:
                geo.setX(geo.x() + delta.x())
                geo.setWidth(new_w)
        if "right" in edge:
            new_w = geo.width() + delta.x()
            if new_w >= min_w:
                geo.setWidth(new_w)
        if "top" in edge:
            new_h = geo.height() - delta.y()
            if new_h >= min_h:
                geo.setY(geo.y() + delta.y())
                geo.setHeight(new_h)
        if "bottom" in edge:
            new_h = geo.height() + delta.y()
            if new_h >= min_h:
                geo.setHeight(new_h)

        self.setGeometry(geo)
