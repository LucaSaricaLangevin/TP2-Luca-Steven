import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QSlider, QComboBox, QPushButton, QMessageBox
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

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

    def __init__(self):
        super().__init__()
        loadUi("ui/mainWindow.ui", self)

        self.model = MainWindowModel()
        self.canvas = PlotCanvas(self.model)
        toolbar = NavigationToolbar(self.canvas, self)

        self.functionLayout.insertWidget(0, toolbar)
        self.functionLayout.insertWidget(1, self.canvas)

        self.functionLineEdit.editingFinished.connect(self.on_function_edited)
        self.infLineEdit.editingFinished.connect(self.on_borne_inf_edited)
        self.supLineEdit.editingFinished.connect(self.on_borne_sup_edited)
        self.nombreSlider.sliderMoved.connect(lambda: setattr(self.model, "rectangles_active", True))
        self.nombreSlider.sliderMoved.connect(self.on_nb_rectangles_changed)
        self.orientationComboBox.currentIndexChanged.connect(self.on_orientation_changed)
        # self.calculerButton.clicked.connect(...)
        # self.exportButton.clicked.connect(...)

    def on_function_edited(self):
        function_str = self.functionLineEdit.text()
        if self.model.validate_function(function_str):
            self.model.function = function_str
        else:
            QMessageBox.critical(self, "Erreur", "La fonction est invalide")
            self.functionLineEdit.clear()
            self.functionLineEdit.setStyleSheet("background-color: white;")

    def on_borne_inf_edited(self):
        self.model.borne_inf = float(self.infLineEdit.text())

    def on_borne_sup_edited(self):
        self.model.borne_sup = float(self.supLineEdit.text())

    def on_nb_rectangles_changed(self):
        self.model.nb_rectangles = int(self.nombreSlider.value())

    def on_orientation_changed(self):
        self.model.orientation = self.orientationComboBox.currentText()
