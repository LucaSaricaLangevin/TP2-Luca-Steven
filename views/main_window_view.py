import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QValidator

from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QMainWindow, QSlider, QComboBox, QMessageBox
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from canvas.matplotlib_canvas import PlotCanvas
from models.main_window_model import MainWindowModel


class MainWindowView(QMainWindow):
    functionLayout: QVBoxLayout
    functionLineEdit: QLineEdit
    infLineEdit: QLineEdit
    supLineEdit: QLineEdit
    nombreSlider: QSlider
    orientationComboBox: QComboBox
    calculerButton: QPushButton
    exportButton: QPushButton
    sommeLineEdit: QLineEdit
    integraleLineEdit: QLineEdit

    __model: MainWindowModel

    def __init__(self):
        super().__init__()
        loadUi("ui/mainWindow.ui", self)

        self.model = MainWindowModel()
        canvas = PlotCanvas(self.model)
        toolbar = NavigationToolbar(canvas, self)

        self.functionLayout.insertWidget(0, toolbar)
        self.functionLayout.insertWidget(1, canvas)

        self.functionLineEdit.editingFinished.connect(self.on_function_edited)

    def on_function_edited(self):
        function_str = self.functionLineEdit.text()
        if self.model.validate_fonction(function_str):
            self.model.function = function_str
        else:
            QMessageBox.critical(self, "Erreur", "La fonction est invalide")
            self.functionLineEdit.clear()
            self.functionLineEdit.setStyleSheet("background-color: white;")
