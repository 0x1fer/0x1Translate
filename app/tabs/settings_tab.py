"""
Settings tab — keyboard shortcut, DeepL API key, app language.

Emits `settings_changed` after a successful save so the host (MainWindow) can
hot-reload anything that needs it (DeepL client, hotkey listener). The
`language_changed` signal fires when the language code actually changed; the
host can then show a "restart required" dialog.
"""
from __future__ import annotations

import string

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from app import settings, styles
from app.i18n import tr


# ---------------------------------------------------------------------------
class SettingsTab(QWidget):
    settings_changed  = pyqtSignal(dict)   # full settings dict
    language_changed  = pyqtSignal(str)    # new language code

    MODIFIERS = ("ctrl", "alt", "shift")
    LANGUAGES = (("tr", "settings_lang_tr"), ("en", "settings_lang_en"))

    def __init__(self, parent=None):
        super().__init__(parent)
        self._initial = settings.load()
        self._build_ui()
        self._load_values()
        self._connect_signals()
        self._update_preview()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Header
        hdr = QLabel(tr("settings_header"))
        hdr.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color: {styles.C['accent']}; background: transparent;")
        root.addWidget(hdr)

        # --- Shortcut section ---------------------------------------
        root.addWidget(self._section_title(tr("settings_section_shortcut")))
        root.addWidget(self._help_label(tr("settings_shortcut_help")))

        sc_grid = QGridLayout()
        sc_grid.setColumnStretch(2, 1)
        sc_grid.setHorizontalSpacing(12)
        sc_grid.setVerticalSpacing(10)

        sc_grid.addWidget(self._row_label(tr("settings_label_modifier")), 0, 0)
        self._mod_combo = QComboBox()
        self._mod_combo.setMinimumWidth(120)
        for m in self.MODIFIERS:
            self._mod_combo.addItem(m.capitalize(), m)
        sc_grid.addWidget(self._mod_combo, 0, 1)

        sc_grid.addWidget(self._row_label(tr("settings_label_trigger")), 1, 0)
        self._trigger_combo = QComboBox()
        self._trigger_combo.setMinimumWidth(120)
        for letter in string.ascii_uppercase:
            self._trigger_combo.addItem(letter, letter)
        sc_grid.addWidget(self._trigger_combo, 1, 1)

        self._preview_label = QLabel()
        self._preview_label.setStyleSheet(
            f"color: {styles.C['accent']}; background: transparent; font-weight: 600;"
        )
        sc_grid.addWidget(self._preview_label, 0, 2, 2, 1, Qt.AlignmentFlag.AlignCenter)
        root.addLayout(sc_grid)

        root.addWidget(self._separator())

        # --- DeepL API key section ----------------------------------
        root.addWidget(self._section_title(tr("settings_section_apikey")))
        root.addWidget(self._help_label(tr("settings_apikey_help")))

        key_row = QHBoxLayout()
        key_row.setSpacing(8)
        self._key_edit = QLineEdit()
        self._key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_edit.setPlaceholderText(tr("settings_apikey_placeholder"))
        self._key_edit.setMinimumHeight(36)
        key_row.addWidget(self._key_edit, 1)

        self._toggle_key_btn = QPushButton(tr("settings_apikey_show"))
        self._toggle_key_btn.setCheckable(True)
        self._toggle_key_btn.setMinimumWidth(80)
        self._toggle_key_btn.setStyleSheet(styles.BTN_GHOST)
        self._toggle_key_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        key_row.addWidget(self._toggle_key_btn)
        root.addLayout(key_row)

        root.addWidget(self._separator())

        # --- Language section ---------------------------------------
        root.addWidget(self._section_title(tr("settings_section_lang")))
        root.addWidget(self._help_label(tr("settings_lang_help")))

        self._lang_combo = QComboBox()
        self._lang_combo.setMinimumWidth(180)
        for code, key in self.LANGUAGES:
            self._lang_combo.addItem(tr(key), code)
        root.addWidget(self._lang_combo, alignment=Qt.AlignmentFlag.AlignLeft)

        root.addStretch(1)

        # --- Save row -----------------------------------------------
        bottom = QHBoxLayout()
        self._status = QLabel("")
        self._status.setStyleSheet(
            f"color: {styles.C['success']}; background: transparent;"
        )
        bottom.addWidget(self._status, 1)

        self._save_btn = QPushButton(tr("settings_btn_save"))
        self._save_btn.setStyleSheet(styles.BTN_SUCCESS)
        self._save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_btn.setMinimumHeight(36)
        bottom.addWidget(self._save_btn)
        root.addLayout(bottom)

    # ------------------------------------------------------------------
    def _section_title(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {styles.C['text']}; background: transparent;")
        return lbl

    def _help_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"color: {styles.C['text_dim']}; font-size: 12px; background: transparent;"
        )
        return lbl

    def _row_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {styles.C['text']}; background: transparent;")
        return lbl

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {styles.C['border']}; background: {styles.C['border']};")
        sep.setFixedHeight(1)
        return sep

    # ------------------------------------------------------------------
    def _load_values(self):
        sc = self._initial.get("shortcut", {})
        mod = (sc.get("modifier") or "ctrl").lower()
        idx = next((i for i, m in enumerate(self.MODIFIERS) if m == mod), 0)
        self._mod_combo.setCurrentIndex(idx)

        trig = (sc.get("trigger_key") or "C").upper()[:1]
        idx = next(
            (i for i, l in enumerate(string.ascii_uppercase) if l == trig), 2
        )  # 'C' is at index 2
        self._trigger_combo.setCurrentIndex(idx)

        self._key_edit.setText(self._initial.get("deepl_api_key", "") or "")

        lang = (self._initial.get("language") or "tr").lower()
        idx = next((i for i, (c, _) in enumerate(self.LANGUAGES) if c == lang), 0)
        self._lang_combo.setCurrentIndex(idx)

    def _connect_signals(self):
        self._mod_combo.currentIndexChanged.connect(self._update_preview)
        self._trigger_combo.currentIndexChanged.connect(self._update_preview)
        self._toggle_key_btn.toggled.connect(self._on_toggle_visibility)
        self._save_btn.clicked.connect(self._on_save)

    def _on_toggle_visibility(self, visible: bool):
        if visible:
            self._key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle_key_btn.setText(tr("settings_apikey_hide"))
        else:
            self._key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle_key_btn.setText(tr("settings_apikey_show"))

    def _update_preview(self):
        mod = (self._mod_combo.currentData() or "ctrl").capitalize()
        key = self._trigger_combo.currentData() or "C"
        self._preview_label.setText(tr("settings_preview", combo=f"{mod}+{key}+{key}"))

    def _on_save(self):
        new = {
            "shortcut": {
                "modifier":   self._mod_combo.currentData(),
                "trigger_key": self._trigger_combo.currentData(),
            },
            "deepl_api_key": self._key_edit.text().strip(),
            "language":      self._lang_combo.currentData(),
        }
        old_lang = (self._initial.get("language") or "tr").lower()
        merged = settings.update(**new)
        self._initial = merged

        self._status.setText(tr("settings_saved_status"))
        self.settings_changed.emit(merged)

        new_lang = new["language"]
        if new_lang and new_lang != old_lang:
            self.language_changed.emit(new_lang)
            QMessageBox.information(
                self,
                tr("settings_restart_t"),
                tr("settings_restart_m"),
            )
