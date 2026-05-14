import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTextBrowser, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from app.APIs.tureng import TurengAPI
from app import styles
from app.i18n import tr


class _TurengWorker(QThread):
    finished = pyqtSignal(list, str)
    error    = pyqtSignal(str)

    def __init__(self, api: TurengAPI, word: str, request_id: int):
        super().__init__()
        self._api = api
        self._word = word
        self._id = request_id

    def run(self):
        try:
            results = self._api.getWord(self._word)
            self.finished.emit(results, self._word)
        except Exception as exc:
            self.error.emit(str(exc))


class DictionaryTab(QWidget):
    save_requested = pyqtSignal(str, str, str)  # original, translation, source_lang

    def __init__(self, parent=None):
        super().__init__(parent)
        self._api = TurengAPI()
        self._worker: _TurengWorker | None = None
        self._request_id = 0
        self._last_results: list[str] = []        # cached for per-row save

        self._build_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Header
        hdr = QLabel(tr("dict_header"))
        hdr.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color: {styles.C['accent']}; background: transparent;")
        root.addWidget(hdr)

        # Search row
        search_row = QHBoxLayout()
        search_row.setSpacing(10)

        self._input = QLineEdit()
        self._input.setPlaceholderText(tr("dict_placeholder"))
        self._input.setMinimumHeight(42)
        search_row.addWidget(self._input, 1)

        self._clear_btn = QPushButton("✕")
        self._clear_btn.setFixedSize(42, 42)
        self._clear_btn.setStyleSheet(styles.BTN_GHOST)
        self._clear_btn.hide()
        search_row.addWidget(self._clear_btn)

        root.addLayout(search_row)

        # Status label
        self._status = QLabel(tr("dict_status_start"))
        self._status.setStyleSheet(f"color: {styles.C['text_dim']}; font-size: 12px; background: transparent;")
        root.addWidget(self._status)

        # Results
        self._results = QTextBrowser()
        self._results.setOpenExternalLinks(False)
        self._results.setOpenLinks(False)
        root.addWidget(self._results, 1)

        # Debounce timer
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(300)

    def _connect_signals(self):
        self._input.textChanged.connect(self._on_text_changed)
        self._clear_btn.clicked.connect(self._clear)
        self._timer.timeout.connect(self._search)
        self._results.anchorClicked.connect(self._on_anchor_clicked)

    # ------------------------------------------------------------------
    def _on_text_changed(self, text: str):
        self._clear_btn.setVisible(bool(text))
        if text.strip():
            self._timer.start()
        else:
            self._timer.stop()
            self._results.clear()
            self._status.setText(tr("dict_status_start"))

    def _clear(self):
        self._input.clear()
        self._results.clear()

    def _search(self):
        word = self._input.text().strip()
        if not word:
            return
        self._request_id += 1
        self._status.setText(tr("dict_status_searching"))
        worker = _TurengWorker(self._api, word, self._request_id)
        worker.finished.connect(self._on_results)
        worker.error.connect(self._on_error)
        self._worker = worker
        worker.start()

    def _on_results(self, results: list, word: str):
        col_dim     = styles.C["text_dim"]
        col_danger  = styles.C["danger"]
        col_text    = styles.C["text"]
        col_accent  = styles.C["accent"]
        col_panel   = styles.C["bg_panel"]
        col_surf    = styles.C["surface"]
        col_success = styles.C["success"]

        if not results:
            self._last_results = []
            self._results.setHtml(
                f"<p style='color:{col_dim};'><i>{tr('dict_no_result_for', word=word)}</i></p>"
            )
            self._status.setText(tr("dict_status_no_result"))
            return

        # Error strings from tureng.py start with "Hata:"
        if len(results) == 1 and results[0].startswith("Hata:"):
            self._last_results = []
            self._results.setHtml(f"<p style='color:{col_danger};'>{results[0]}</p>")
            self._status.setText(tr("dict_status_conn_err"))
            return

        # Cache for the anchor handler below.
        self._last_results = list(results)

        rows_html = ""
        for i, item in enumerate(results):
            parts = item.split(" -> ", 1)
            bg = col_surf if i % 2 == 0 else col_panel
            if len(parts) == 2:
                src, tgt = parts
                # Use 'save:N' (no //) so QUrl reliably puts N in .path()
                save_cell = (
                    f"<td style='padding:6px 12px; text-align:right;'>"
                    f"<a href='save:{i}' style='color:{col_success}; text-decoration:none; "
                    f"font-weight:600;'>{tr('dict_save_link')}</a>"
                    f"</td>"
                )
                rows_html += (
                    f"<tr style='background:{bg};'>"
                    f"<td style='padding:8px 12px; color:{col_text};'><b>{src}</b></td>"
                    f"<td style='padding:8px 12px; color:{col_dim};'>→</td>"
                    f"<td style='padding:8px 12px; color:{col_accent};'>{tgt}</td>"
                    f"{save_cell}"
                    f"</tr>"
                )
            else:
                rows_html += (
                    f"<tr style='background:{bg};'>"
                    f"<td colspan='4' style='padding:8px 12px; color:{col_dim};'>{item}</td>"
                    f"</tr>"
                )

        html = (
            f"<table width='100%' cellspacing='0' style='font-size:14px; border-collapse:collapse;'>"
            f"<tr style='background:{col_panel};'>"
            f"<th style='padding:8px 12px; text-align:left; color:{col_dim};'>{tr('dict_col_source')}</th>"
            f"<th></th>"
            f"<th style='padding:8px 12px; text-align:left; color:{col_dim};'>{tr('dict_col_translation')}</th>"
            f"<th></th>"
            f"</tr>"
            f"{rows_html}"
            f"</table>"
        )
        self._results.setHtml(html)
        self._status.setText(tr("dict_status_results", n=len(results)))

    def _on_anchor_clicked(self, url):
        """Handle the per-row Save links (save:<index>)."""
        if url.scheme() != "save":
            return
        # QUrl("save:N") → scheme="save", path="N"; toString fallback for safety.
        raw = url.path() or url.host() or url.toString().split(":", 1)[-1]
        try:
            idx = int(raw.lstrip("/").strip())
        except ValueError:
            return
        if not (0 <= idx < len(self._last_results)):
            return
        item = self._last_results[idx]
        parts = item.split(" -> ", 1)
        if len(parts) != 2:
            return
        src, tgt = parts
        self.save_requested.emit(src.strip(), tgt.strip(), "TR-EN")
        self._status.setText(tr("dict_status_saved_row", word=src.strip()))

    def _on_error(self, msg: str):
        self._status.setText(tr("dict_status_error"))
        col = styles.C["danger"]
        self._results.setHtml(f"<p style='color:{col};'>{msg}</p>")

    def set_search_word(self, word: str):
        """Called externally (e.g. from popup 'Search in dict' button)."""
        self._input.setText(word)
