import sys
from PyQt6.QtWidgets import QApplication
from views.main_window_view import MainWindowView

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Charger le fichier QSS
    with open("../styles/dark_theme.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    mainWindow = MainWindowView()
    mainWindow.show()
    sys.exit(app.exec())

