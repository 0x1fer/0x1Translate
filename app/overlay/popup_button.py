from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QFont

from app import styles


class PopupButton(QWidget):
    """Small floating button that appears near a text selection."""

    translate_requested = pyqtSignal(str, int, int)  # text, x, y

    AUTO_HIDE_MS = 2500

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.ToolTip
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._selected_text = ""
        self._cx = 0
        self._cy = 0

        self._build_ui()

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(self.AUTO_HIDE_MS)
        self._hide_timer.timeout.connect(self.hide)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._btn = QPushButton("🌐")
        self._btn.setFixedSize(40, 40)
        self._btn.setFont(QFont("Segoe UI", 16))
        self._btn.setToolTip("Çevir")
        self._btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.C['accent']};
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: {styles.C['accent_hover']};
            }}
        """)
        self._btn.clicked.connect(self._on_clicked)
        layout.addWidget(self._btn)

        self.setFixedSize(48, 48)

    # ------------------------------------------------------------------
    def show_near(self, text: str, x: int, y: int):
        """Show the button near the cursor (x, y) — accurate via evdev now."""
        self._selected_text = text
        self._cx = x
        self._cy = y

        bw, bh = self.width(), self.height()
        target = _safe_global_pos(x + 12, y - bh - 6, bw, bh)
        self.move(target)
        self.show()
        self.raise_()
        # Compositor maps windows asynchronously — re-raise to ensure top.
        QTimer.singleShot(60,  self.raise_)
        QTimer.singleShot(150, self.raise_)
        # Always auto-hide after AUTO_HIDE_MS — no hover-keep-alive, otherwise
        # spurious EnterNotify events on Wayland would freeze the button on
        # screen forever.
        self._hide_timer.start()

    def _on_clicked(self):
        self._hide_timer.stop()
        self.hide()
        self.translate_requested.emit(self._selected_text, self._cx, self._cy)


# ---------------------------------------------------------------------------
def _safe_global_pos(x: int, y: int, w: int, h: int) -> QPoint:
    """Clamp (x, y) so the popup stays within the screen bounds."""
    screen = QApplication.primaryScreen().geometry()
    x = max(screen.left(), min(x, screen.right()  - w))
    y = max(screen.top(),  min(y, screen.bottom() - h))
    return QPoint(x, y)
