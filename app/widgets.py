"""Shared custom widgets used by multiple tabs and the popup."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QComboBox


def style_combo_view(cb: QComboBox, surface: str, bg: str, text: str,
                     border: str, accent: str, muted: str) -> None:
    """
    Apply the dark theme to a QComboBox's *popup view*. Qt's parent-cascade
    stylesheet selectors don't always reach the popup (it's a separate
    top-level window owned by the platform plugin), so we set the view's
    stylesheet directly.  Without this, the popup may render with the
    platform's default light background.
    """
    view = cb.view()
    view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    view.setStyleSheet(f"""
        QAbstractItemView {{
            background-color: {surface};
            color: {text};
            border: 1px solid {border};
            border-radius: 6px;
            selection-background-color: {accent};
            selection-color: {bg};
            outline: none;
            padding: 4px;
            font-size: 14px;
        }}
        QAbstractItemView::item {{
            min-height: 28px;
            padding: 4px 10px;
            color: {text};
            background-color: transparent;
        }}
        QAbstractItemView::item:hover {{
            background-color: {border};
        }}
        QAbstractItemView::item:selected {{
            background-color: {accent};
            color: {bg};
        }}
        QScrollBar:vertical {{
            background: {surface};
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {border};
            border-radius: 5px;
            min-height: 24px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {accent};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0; border: none; background: none;
        }}
    """)
    # The popup-container (the view's top-level window) has its own default
    # background that bleeds through anywhere the view's stylesheet doesn't
    # paint. Force it opaque too.
    win = view.window()
    if win is not None and win is not view:
        win.setStyleSheet(f"background-color: {surface}; border-radius: 6px;")


class BoundedComboBox(QComboBox):
    """
    QComboBox that always caps its popup at MAX_VISIBLE rows.

    Several Qt styles ignore setMaxVisibleItems(); we override showPopup so
    Qt first sizes the popup for all items and we then shrink it. We also
    re-anchor the popup relative to the combo's screen position, otherwise
    when Qt opens the popup *above* the combo (because the original tall
    popup didn't fit below) the shrunk popup ends up floating off-screen.
    """

    MAX_VISIBLE = 8
    ROW_PX      = 30          # matches our item padding + font

    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        if popup is None:
            return

        max_h = self.ROW_PX * self.MAX_VISIBLE + 14   # rows + small chrome
        if popup.height() <= max_h:
            return

        popup.setMaximumHeight(max_h)
        popup.resize(popup.width(), max_h)

        # Re-anchor the popup to the combo. Qt's initial Y may have been
        # computed for the un-capped (much taller) popup, so we recompute.
        screen      = QGuiApplication.primaryScreen().geometry()
        combo_top   = self.mapToGlobal(QPoint(0, 0)).y()
        combo_bot   = combo_top + self.height()
        space_below = screen.bottom() - combo_bot
        space_above = combo_top - screen.top()

        if space_below >= max_h or space_below >= space_above:
            new_y = combo_bot                       # plenty of room below
        else:
            new_y = combo_top - max_h               # use the space above

        new_y = max(screen.top(), min(new_y, screen.bottom() - max_h))
        popup.move(popup.geometry().x(), new_y)
