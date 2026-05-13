import os

# Run as an X11 app (via XWayland on Wayland desktops).
# Wayland's xdg_popup protocol requires a visible mapped parent surface for
# every overlay window, making global floating overlays impossible without
# layer-shell. XWayland removes all these restrictions:
#   - popup windows can float freely with no transient parent
#   - move() with screen coordinates works as expected
#   - PRIMARY selection is available via Qt's X11 clipboard
# KDE Plasma 6 starts XWayland on demand; no manual setup is required.
# Override by setting QT_QPA_PLATFORM=wayland in the environment.
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from app.config import CONFIG
from app.db.database import Database
from app.main_window import MainWindow
from app import styles


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TranslateApp")
    app.setOrganizationName("TranslateApp")
    app.setQuitOnLastWindowClosed(False)

    app.setFont(QFont("Segoe UI", 11))
    app.setStyleSheet(styles.MAIN)

    db = Database(CONFIG["db_path"])

    window = MainWindow(db)
    window.show()
    window.start_watcher()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
