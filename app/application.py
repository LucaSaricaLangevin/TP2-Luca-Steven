import sys

from PyQt6.QtWidgets import QApplication

from views.function_list_view import FunctionView
from views.main_window_view import MainWindowView

if __name__ == "__main__":
    app = QApplication(sys.argv)
    #functionList = FunctionView()
    mainWindow = MainWindowView()
    #functionList.show()
    mainWindow.show()
    sys.exit(app.exec())