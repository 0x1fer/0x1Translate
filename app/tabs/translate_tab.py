import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QTextBrowser, QLabel, QPushButton, QComboBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from app.APIs.deeplTranslate import DeeplAPI
from app import styles
from app.i18n import tr, lang_key
from app.widgets import BoundedComboBox, style_combo_view

# DeepL language codes — display names resolved at populate time via tr().
SOURCE_CODES: list[str | None] = [
    None, "AR", "BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI", "FR",
    "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT", "RO",
    "RU", "SK", "SL", "SV", "TR", "UK", "ZH",
]

TARGET_CODES: list[str] = [
    "AR", "BG", "CS", "DA", "DE", "EL", "EN-GB", "EN-US", "ES", "ET", "FI",
    "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL",
    "PT-BR", "PT-PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH-HANS",
    "ZH-HANT",
]

MAX_CHARS = 5000


class _DeepLWorker(QThread):
    finished = pyqtSignal(str, int)
    error    = pyqtSignal(str, int)

    def __init__(self, api: DeeplAPI, text: str, target: str, source: str | None, req_id: int):
        super().__init__()
        self._api    = api
        self._text   = text
        self._target = target
        self._source = source
        self._id     = req_id

    def run(self):
        try:
            result = self._api.translate(self._text, self._target, self._source)
            self.finished.emit(result, self._id)
        except Exception as exc:
            self.error.emit(str(exc), self._id)


class TranslateTab(QWidget):
    save_requested = pyqtSignal(str, str, str)  # original, translation, source_lang

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api: DeeplAPI | None = None
        self._api_error: str | None = None
        try:
            self._api = DeeplAPI()
        except ValueError as e:
            self._api_error = str(e)

        self._worker: _DeepLWorker | None = None
        self._req_id = 0

        self._build_ui()
        self._connect_signals()
        self._populate_lang_boxes()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Top bar: header (left) — language controls (centred)
        top = QHBoxLayout()
        top.setSpacing(10)

        hdr = QLabel(tr("tr_header"))
        hdr.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color: {styles.C['accent']}; background: transparent;")
        top.addWidget(hdr)
        top.addStretch(1)

        self._src_combo = BoundedComboBox()
        self._src_combo.setMinimumWidth(180)
        top.addWidget(self._src_combo)

        self._swap_btn = QPushButton("⇆")
        self._swap_btn.setFixedSize(36, 36)
        self._swap_btn.setFont(QFont("Segoe UI", 14))
        self._swap_btn.setStyleSheet(styles.BTN_GHOST)
        self._swap_btn.setToolTip(tr("swap_tooltip"))
        top.addWidget(self._swap_btn)

        self._tgt_combo = BoundedComboBox()
        self._tgt_combo.setMinimumWidth(200)
        top.addWidget(self._tgt_combo)

        top.addStretch(1)        # symmetrical right stretch → language group is centred

        root.addLayout(top)

        # Main translation area
        panels = QHBoxLayout()
        panels.setSpacing(14)

        # --- Input panel ---
        in_wrap = QVBoxLayout()
        in_wrap.setSpacing(6)

        self._input = QTextEdit()
        self._input.setPlaceholderText(tr("tr_placeholder"))
        self._input.setAcceptRichText(False)
        in_wrap.addWidget(self._input, 1)

        in_bottom = QHBoxLayout()
        self._char_counter = QLabel(f"0 / {MAX_CHARS}")
        self._char_counter.setStyleSheet(f"color: {styles.C['text_dim']}; font-size: 12px; background: transparent;")
        in_bottom.addStretch(1)
        in_bottom.addWidget(self._char_counter)
        in_wrap.addLayout(in_bottom)
        panels.addLayout(in_wrap, 1)

        # --- Output panel ---
        out_wrap = QVBoxLayout()
        out_wrap.setSpacing(6)

        self._output = QTextBrowser()
        out_wrap.addWidget(self._output, 1)

        out_bottom = QHBoxLayout()
        self._save_btn = QPushButton(tr("tr_save_btn"))
        self._save_btn.setStyleSheet(styles.BTN_SUCCESS)
        self._save_btn.setEnabled(False)
        out_bottom.addStretch(1)
        out_bottom.addWidget(self._save_btn)
        out_wrap.addLayout(out_bottom)
        panels.addLayout(out_wrap, 1)

        root.addLayout(panels, 1)

        # Status
        self._status = QLabel(tr("tr_status_start"))
        self._status.setStyleSheet(f"color: {styles.C['text_dim']}; font-size: 12px; background: transparent;")
        root.addWidget(self._status)

        if self._api_error:
            self._status.setText(tr("tr_deepl_error", err=self._api_error))
            self._status.setStyleSheet(f"color: {styles.C['danger']}; font-size: 12px; background: transparent;")

        # Debounce timer
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(500)

    def _populate_lang_boxes(self):
        for code in SOURCE_CODES:
            self._src_combo.addItem(tr(lang_key(code)), code)

        for code in TARGET_CODES:
            self._tgt_combo.addItem(tr(lang_key(code)), code)

        # Default: auto-detect → TR
        default_tgt = next((i for i, c in enumerate(TARGET_CODES) if c == "TR"), 0)
        self._tgt_combo.setCurrentIndex(default_tgt)

        # The global QSS rules for "QComboBox QAbstractItemView" don't always
        # reach the popup window on XWayland; paint the view explicitly.
        C = styles.C
        for cb in (self._src_combo, self._tgt_combo):
            style_combo_view(cb,
                surface=C["surface"], bg=C["bg_main"], text=C["text"],
                border=C["border"], accent=C["accent"], muted=C["text_dim"])

    def _connect_signals(self):
        self._input.textChanged.connect(self._on_input_changed)
        self._swap_btn.clicked.connect(self._swap_languages)
        self._timer.timeout.connect(self._translate)
        self._save_btn.clicked.connect(self._on_save)
        # Re-translate when either language changes (cheap; debounced via timer)
        self._src_combo.currentIndexChanged.connect(self._on_lang_changed)
        self._tgt_combo.currentIndexChanged.connect(self._on_lang_changed)

    def _on_lang_changed(self):
        if self._input.toPlainText().strip():
            self._timer.start()

    # ------------------------------------------------------------------
    def _on_input_changed(self):
        text = self._input.toPlainText()
        # Enforce character limit
        if len(text) > MAX_CHARS:
            cursor = self._input.textCursor()
            pos = cursor.position()
            self._input.blockSignals(True)
            self._input.setPlainText(text[:MAX_CHARS])
            cursor.setPosition(min(pos, MAX_CHARS))
            self._input.setTextCursor(cursor)
            self._input.blockSignals(False)
            text = self._input.toPlainText()

        self._char_counter.setText(f"{len(text)} / {MAX_CHARS}")

        if text.strip():
            self._timer.start()
        else:
            self._timer.stop()
            self._output.clear()
            self._save_btn.setEnabled(False)
            self._status.setText(tr("tr_status_start"))

    def _swap_languages(self):
        src_code = self._src_combo.currentData()
        tgt_code = self._tgt_combo.currentData()

        # Swap the comboboxes (currentIndexChanged → _on_lang_changed → retranslate)
        if tgt_code:
            base = tgt_code.split("-")[0]
            for i, code in enumerate(SOURCE_CODES):
                if code == base:
                    self._src_combo.setCurrentIndex(i)
                    break
        if src_code:
            for i, code in enumerate(TARGET_CODES):
                if code == src_code or code.startswith(src_code):
                    self._tgt_combo.setCurrentIndex(i)
                    break

        # Also swap the text content. Block signals on input so we don't fire
        # two retranslate cycles; the language change above already scheduled one.
        in_text  = self._input.toPlainText()
        out_text = self._output.toPlainText()
        if out_text:
            self._input.blockSignals(True)
            self._input.setPlainText(out_text)
            self._input.blockSignals(False)
            self._char_counter.setText(f"{len(out_text)} / {MAX_CHARS}")
        self._output.setPlainText(in_text)
        # Trigger a fresh translation of the (now) new input
        if self._input.toPlainText().strip():
            self._timer.start()

    def _translate(self):
        if not self._api:
            return
        text = self._input.toPlainText().strip()
        if not text:
            return

        self._req_id += 1
        req_id = self._req_id
        source = self._src_combo.currentData()
        target = self._tgt_combo.currentData()

        self._status.setText(tr("tr_status_translating"))
        self._save_btn.setEnabled(False)

        worker = _DeepLWorker(self._api, text, target, source, req_id)
        worker.finished.connect(self._on_translated)
        worker.error.connect(self._on_error)
        self._worker = worker
        worker.start()

    def _on_translated(self, result: str, req_id: int):
        if req_id != self._req_id:
            return  # stale response
        self._output.setPlainText(result)
        self._save_btn.setEnabled(True)
        self._status.setText(tr("tr_status_done"))

    def _on_error(self, msg: str, req_id: int):
        if req_id != self._req_id:
            return
        self._output.setPlainText(tr("tr_error_prefix", msg=msg))
        self._status.setText(tr("tr_status_error"))

    def _on_save(self):
        original = self._input.toPlainText().strip()
        translation = self._output.toPlainText().strip()
        if not original or not translation:
            return
        src_code = self._src_combo.currentData() or "AUTO"
        self.save_requested.emit(original, translation, src_code)
        self._status.setText(tr("tr_status_saved"))

    def reload_api(self):
        """Re-instantiate DeeplAPI (e.g. after the user updated the key in Settings)."""
        self._api_error = None
        try:
            self._api = DeeplAPI()
            self._status.setText(tr("tr_status_start"))
            self._status.setStyleSheet(
                f"color: {styles.C['text_dim']}; font-size: 12px; background: transparent;"
            )
        except ValueError as e:
            self._api = None
            self._api_error = str(e)
            self._status.setText(tr("tr_deepl_error", err=self._api_error))
            self._status.setStyleSheet(
                f"color: {styles.C['danger']}; font-size: 12px; background: transparent;"
            )

    def set_text(self, text: str):
        """Set source text from external caller (e.g. popup)."""
        self._input.setPlainText(text)

    def set_input(self, text: str, src_code: str = "", tgt_code: str = ""):
        """Populate the input + language combos, focus and auto-translate."""
        if src_code:
            for i in range(self._src_combo.count()):
                if self._src_combo.itemData(i) == src_code:
                    self._src_combo.setCurrentIndex(i)
                    break
        if tgt_code:
            for i in range(self._tgt_combo.count()):
                if self._tgt_combo.itemData(i) == tgt_code:
                    self._tgt_combo.setCurrentIndex(i)
                    break
        self._input.setPlainText(text)
        self._input.setFocus()
        # textChanged fires automatically and starts the debounce timer.
