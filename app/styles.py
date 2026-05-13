C = {
    "bg_main":       "#0D0D0F",
    "bg_panel":      "#141416",
    "surface":       "#1C1C1F",
    "border":        "#2A2A2E",
    "accent":        "#5B6AF0",
    "accent_hover":  "#6E7CF5",
    "text":          "#E8E8EC",
    "text_dim":      "#888892",
    "danger":        "#E05555",
    "success":       "#3DB87A",
}

MAIN = f"""
QMainWindow, QWidget {{
    background-color: {C['bg_main']};
    color: {C['text']};
    font-family: 'Segoe UI', 'Liberation Sans', sans-serif;
}}
QWidget#centralwidget {{
    background-color: {C['bg_main']};
}}
QLineEdit {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    font-size: 14px;
    padding: 8px 12px;
    selection-background-color: {C['accent']};
}}
QLineEdit:focus {{
    border: 1.5px solid {C['accent']};
}}
QTextEdit {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    font-size: 15px;
    padding: 10px 12px;
    selection-background-color: {C['accent']};
}}
QTextEdit:focus {{
    border: 1.5px solid {C['accent']};
}}
QTextBrowser {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    font-size: 15px;
    padding: 10px 12px;
}}
QComboBox {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    font-size: 13px;
    padding: 6px 10px;
    min-height: 30px;
}}
QComboBox:hover {{
    border: 1px solid {C['accent']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    selection-background-color: {C['accent']};
    selection-color: white;
    padding: 4px;
    outline: none;
}}
QScrollBar:vertical {{
    background-color: {C['bg_panel']};
    width: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background-color: {C['border']};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {C['accent']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0; border: none; background: none;
}}
QScrollBar:horizontal {{
    background-color: {C['bg_panel']};
    height: 8px;
    border-radius: 4px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background-color: {C['border']};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {C['accent']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0; border: none; background: none;
}}
QStatusBar {{
    background-color: {C['bg_panel']};
    color: {C['text_dim']};
    font-size: 12px;
    border-top: 1px solid {C['border']};
}}
QLabel {{
    color: {C['text']};
    background: transparent;
}}
QTableWidget {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    gridline-color: {C['border']};
    font-size: 13px;
    outline: none;
}}
QTableWidget::item {{
    padding: 8px 10px;
    border: none;
}}
QTableWidget::item:selected {{
    background-color: {C['accent']};
    color: white;
}}
QHeaderView::section {{
    background-color: {C['bg_panel']};
    color: {C['text_dim']};
    border: none;
    border-bottom: 1px solid {C['border']};
    border-right: 1px solid {C['border']};
    padding: 8px 10px;
    font-weight: bold;
    font-size: 12px;
}}
QTableWidget QTableCornerButton::section {{
    background-color: {C['bg_panel']};
    border: none;
    border-bottom: 1px solid {C['border']};
    border-right: 1px solid {C['border']};
}}
"""

NAV_BUTTON = f"""
QPushButton {{
    background-color: {C['bg_panel']};
    color: {C['text_dim']};
    border: none;
    border-bottom: 3px solid transparent;
    font-size: 14px;
    font-weight: bold;
    padding: 14px 20px;
    border-radius: 0px;
}}
QPushButton:hover {{
    background-color: {C['surface']};
    color: {C['accent']};
    border-bottom: 3px solid {C['accent']};
}}
"""

NAV_BUTTON_ACTIVE = f"""
QPushButton {{
    background-color: {C['surface']};
    color: {C['accent']};
    border: none;
    border-bottom: 3px solid {C['accent']};
    font-size: 14px;
    font-weight: bold;
    padding: 14px 20px;
    border-radius: 0px;
}}
"""

BTN_PRIMARY = f"""
QPushButton {{
    background-color: {C['accent']};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 22px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {C['accent_hover']};
}}
QPushButton:pressed {{
    background-color: {C['accent']};
}}
"""

BTN_DANGER = f"""
QPushButton {{
    background-color: transparent;
    color: {C['danger']};
    border: 1px solid {C['danger']};
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {C['danger']};
    color: white;
}}
"""

BTN_SUCCESS = f"""
QPushButton {{
    background-color: {C['success']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: #50c987;
}}
"""

BTN_GHOST = f"""
QPushButton {{
    background-color: transparent;
    color: {C['text_dim']};
    border: 1px solid {C['border']};
    border-radius: 6px;
    padding: 7px 16px;
    font-size: 12px;
}}
QPushButton:hover {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['accent']};
}}
"""

POPUP_WIDGET = f"""
QWidget {{
    background-color: {C['surface']};
    color: {C['text']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    font-family: 'Segoe UI', sans-serif;
}}
QLabel {{
    color: {C['text']};
    background: transparent;
    border: none;
}}
QTextBrowser {{
    background-color: transparent;
    color: {C['text']};
    border: none;
    font-size: 13px;
}}
"""

POPUP_BUTTON_WIDGET = f"""
QWidget {{
    background: transparent;
    border: none;
}}
QPushButton {{
    background-color: {C['accent']};
    color: white;
    border: none;
    border-radius: 20px;
    font-size: 16px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {C['accent_hover']};
}}
"""
