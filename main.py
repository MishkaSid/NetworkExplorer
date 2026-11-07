
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.main_window import NetworkExplorer
from gui.styles import DARK_THEME
from data.database import initialize_database


def resource_path(relative_path):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / relative_path


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    app.setWindowIcon(
        QIcon(str(resource_path("assets/icon.ico")))
    )

    initialize_database()

    window = NetworkExplorer()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

