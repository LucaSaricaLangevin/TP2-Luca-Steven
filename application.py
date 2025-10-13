import sys
from PyQt6.QtWidgets import QApplication
from function_view import FunctionView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FunctionView()
    fenetre.show()
    sys.exit(app.exec())