import sys
from PyQt6.QtWidgets import QApplication
from views.main_window_view import MainWindowView

if __name__ == "__main__":
    app = QApplication(sys.argv)


    # Les thèmes ont en parti été fait par Claude, le changement de thème a été assisté par Claude.
    # Charger le thème par défaut (dark)
    # Le toggle sera géré par MainWindowView
    with open("../styles/dark_theme.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    mainWindow = MainWindowView(app)  # Passer l'app pour pouvoir changer le thème
    mainWindow.show()
    sys.exit(app.exec())
