import csv
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QHeaderView, QAbstractItemView, QMessageBox, QDialog,
    QDialogButtonBox, QMenu, QFileDialog, QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction

from app.db.database import Database
from app.db.models import SavedWord
from app import styles


# ---------------------------------------------------------------------------
class _AddWordDialog(QDialog):
    """Modal form to add a word/phrase manually."""

    LANG_CHOICES = [
        ("AUTO", "Otomatik / Bilinmiyor"),
        ("EN",   "İngilizce"),
        ("TR",   "Türkçe"),
        ("DE",   "Almanca"),
        ("FR",   "Fransızca"),
        ("ES",   "İspanyolca"),
        ("IT",   "İtalyanca"),
        ("RU",   "Rusça"),
        ("JA",   "Japonca"),
        ("AR",   "Arapça"),
        ("ZH",   "Çince"),
        ("TR-EN","TR ↔ EN (sözlük)"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeni kelime ekle")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setStyleSheet(f"background-color: {styles.C['bg_main']}; color: {styles.C['text']};")

        form = QFormLayout(self)
        form.setContentsMargins(20, 20, 20, 20)
        form.setSpacing(12)

        self._original    = QLineEdit()
        self._original.setPlaceholderText("Orijinal metin")
        self._translation = QLineEdit()
        self._translation.setPlaceholderText("Çeviri")

        self._lang = QComboBox()
        for code, label in self.LANG_CHOICES:
            self._lang.addItem(label, code)

        form.addRow(self._label("Orijinal:"),  self._original)
        form.addRow(self._label("Çeviri:"),    self._translation)
        form.addRow(self._label("Dil:"),       self._lang)

        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        save_btn   = bb.button(QDialogButtonBox.StandardButton.Save)
        cancel_btn = bb.button(QDialogButtonBox.StandardButton.Cancel)
        if save_btn:
            save_btn.setText("Kaydet")
            save_btn.setStyleSheet(styles.BTN_SUCCESS)
        if cancel_btn:
            cancel_btn.setText("İptal")
            cancel_btn.setStyleSheet(styles.BTN_GHOST)
        bb.accepted.connect(self._on_accept)
        bb.rejected.connect(self.reject)
        form.addRow(bb)

        self._original.setFocus()

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {styles.C['text_dim']}; background: transparent;")
        return lbl

    def _on_accept(self):
        if not self._original.text().strip() or not self._translation.text().strip():
            QMessageBox.warning(self, "Eksik bilgi",
                                "Orijinal metin ve çeviri boş bırakılamaz.")
            return
        self.accept()

    def data(self) -> tuple[str, str, str]:
        return (
            self._original.text().strip(),
            self._translation.text().strip(),
            self._lang.currentData() or "AUTO",
        )


# ---------------------------------------------------------------------------
class WordsTab(QWidget):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db = db
        self._build_ui()
        self._connect_signals()
        self.refresh()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        # Header row
        hdr_row = QHBoxLayout()
        hdr = QLabel("📝  Kelimelerim")
        hdr.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color: {styles.C['accent']}; background: transparent;")
        hdr_row.addWidget(hdr)
        hdr_row.addStretch(1)

        self._count_label = QLabel("0 kayıt")
        self._count_label.setStyleSheet(
            f"color: {styles.C['text_dim']}; font-size: 12px; background: transparent;"
        )
        hdr_row.addWidget(self._count_label)
        hdr_row.addSpacing(12)

        self._add_btn = QPushButton("➕  Ekle")
        self._add_btn.setStyleSheet(styles.BTN_GHOST)
        self._add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hdr_row.addWidget(self._add_btn)

        self._export_btn = QPushButton("📥  Dışa Aktar")
        self._export_btn.setStyleSheet(styles.BTN_GHOST)
        self._export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        hdr_row.addWidget(self._export_btn)
        # Build export menu
        export_menu = QMenu(self._export_btn)
        export_menu.addAction("JSON (.json)").triggered.connect(lambda: self._export("json"))
        export_menu.addAction("CSV (.csv)").triggered.connect(lambda: self._export("csv"))
        export_menu.addAction("Excel (.xlsx)").triggered.connect(lambda: self._export("xlsx"))
        self._export_btn.setMenu(export_menu)

        root.addLayout(hdr_row)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Kayıtlarda ara…")
        self._search.setMaximumHeight(40)
        root.addWidget(self._search)

        # Table
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["Orijinal", "Çeviri", "Dil", "Tarih", ""])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(4, 90)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.setShowGrid(False)
        self._table.setStyleSheet(
            f"QTableWidget::item:alternate {{ background-color: {styles.C['bg_panel']}; }}"
        )
        root.addWidget(self._table, 1)

        # Empty state label (shown when no rows)
        self._empty_label = QLabel(
            "📚  Henüz kayıtlı kelime yok.\n"
            "Çeviri / sözlük sekmesinden kelime kaydedin veya yukarıdaki “Ekle” butonunu kullanın."
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            f"color: {styles.C['text_dim']}; font-size: 15px; background: transparent;"
        )
        self._empty_label.hide()
        root.addWidget(self._empty_label)

    def _connect_signals(self):
        self._search.textChanged.connect(self._on_search)
        self._add_btn.clicked.connect(self._on_add_clicked)

    # ------------------------------------------------------------------
    def refresh(self):
        words = self._db.get_all()
        self._populate(words)

    def _on_search(self, query: str):
        if query.strip():
            words = self._db.search(query.strip())
        else:
            words = self._db.get_all()
        self._populate(words)

    def _populate(self, words: list[SavedWord]):
        self._table.setRowCount(0)
        if not words:
            self._table.hide()
            self._empty_label.show()
            self._count_label.setText("0 kayıt")
            return

        self._empty_label.hide()
        self._table.show()
        self._count_label.setText(f"{len(words)} kayıt")

        for word in words:
            row = self._table.rowCount()
            self._table.insertRow(row)

            self._table.setItem(row, 0, self._cell(word.original_text))
            self._table.setItem(row, 1, self._cell(word.translation))
            self._table.setItem(row, 2, self._cell(word.source_lang))
            self._table.setItem(row, 3, self._cell(word.created_at.strftime("%d.%m.%Y %H:%M")))

            del_btn = QPushButton("Sil")
            del_btn.setStyleSheet(styles.BTN_DANGER)
            del_btn.setFixedHeight(30)
            del_btn.clicked.connect(lambda checked, wid=word.id: self._delete(wid))
            self._table.setCellWidget(row, 4, del_btn)
            self._table.setRowHeight(row, 46)

    def _cell(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        return item

    def _delete(self, word_id: int | None):
        if word_id is None:
            return
        reply = QMessageBox.question(
            self, "Sil",
            "Bu kaydı silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._db.delete(word_id)
            self._on_search(self._search.text())

    # ------------------------------------------------------------------
    def add_word(self, original: str, translation: str, source_lang: str):
        word = SavedWord(original_text=original, translation=translation, source_lang=source_lang)
        self._db.save_word(word)
        self._on_search(self._search.text())

    # ------------------------------------------------------------------
    def _on_add_clicked(self):
        dlg = _AddWordDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        original, translation, lang = dlg.data()
        self.add_word(original, translation, lang)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def _export(self, fmt: str):
        words = self._db.get_all()
        if not words:
            QMessageBox.information(self, "Boş", "Dışa aktarılacak kayıt yok.")
            return

        ext_filter = {
            "json": ("kelimelerim.json", "JSON dosyası (*.json)"),
            "csv":  ("kelimelerim.csv",  "CSV dosyası (*.csv)"),
            "xlsx": ("kelimelerim.xlsx", "Excel dosyası (*.xlsx)"),
        }[fmt]
        default_name, file_filter = ext_filter

        path, _ = QFileDialog.getSaveFileName(
            self, "Dışa Aktar", default_name, file_filter,
        )
        if not path:
            return

        try:
            if fmt == "json":
                self._write_json(path, words)
            elif fmt == "csv":
                self._write_csv(path, words)
            elif fmt == "xlsx":
                self._write_xlsx(path, words)
        except ImportError as e:
            QMessageBox.warning(
                self, "Eksik bağımlılık",
                f"Excel dışa aktarımı için 'openpyxl' paketi gereklidir.\n\n"
                f"Kurulum:  pip install openpyxl\n\n"
                f"Detay: {e}",
            )
            return
        except OSError as e:
            QMessageBox.critical(self, "Hata", f"Dosya yazılamadı:\n{e}")
            return

        QMessageBox.information(
            self, "Tamamlandı",
            f"{len(words)} kayıt başarıyla aktarıldı:\n{path}",
        )

    @staticmethod
    def _rows(words: list[SavedWord]) -> list[dict]:
        return [
            {
                "original":    w.original_text,
                "translation": w.translation,
                "language":    w.source_lang,
                "created_at":  w.created_at.isoformat(),
            }
            for w in words
        ]

    def _write_json(self, path: str, words: list[SavedWord]):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._rows(words), f, ensure_ascii=False, indent=2)

    def _write_csv(self, path: str, words: list[SavedWord]):
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Original", "Translation", "Language", "Created At"])
            for w in words:
                writer.writerow([
                    w.original_text, w.translation, w.source_lang,
                    w.created_at.isoformat(),
                ])

    def _write_xlsx(self, path: str, words: list[SavedWord]):
        from openpyxl import Workbook          # raises ImportError if missing
        from openpyxl.styles import Font, PatternFill

        wb = Workbook()
        ws = wb.active
        ws.title = "Kelimeler"
        ws.append(["Original", "Translation", "Language", "Created At"])

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="5B6AF0")
        for col in ws[1]:
            col.font = header_font
            col.fill = header_fill

        for w in words:
            ws.append([
                w.original_text, w.translation, w.source_lang,
                w.created_at.isoformat(),
            ])

        for column_cells in ws.columns:
            length = max(len(str(c.value or "")) for c in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = min(60, length + 2)

        wb.save(path)
