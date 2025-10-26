import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QSlider, QComboBox, QPushButton, QMessageBox
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from canvas.matplotlib_canvas import PlotCanvas
from models.main_window_model import MainWindowModel
from models import main_window_model



class MainWindowView(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(r"C:\Users\lucas\PycharmProjects\TP2-Luca-Steven\ui\mainWindow.ui", self)

        self.model = MainWindowModel()
        self.canvas = PlotCanvas(self.model)
        toolbar = NavigationToolbar(self.canvas, self)
        self.functionLayout.insertWidget(0, toolbar)
        self.functionLayout.insertWidget(1, self.canvas)

        # connexions
        self.functionLineEdit.editingFinished.connect(self.on_function_edited)
        self.infLineEdit.editingFinished.connect(self.on_borne_inf_edited)
        self.supLineEdit.editingFinished.connect(self.on_borne_sup_edited)
        self.nombreSlider.sliderMoved.connect(lambda: setattr(self.model, "rectangles_active", True))
        self.nombreSlider.sliderMoved.connect(self.on_nb_rectangles_changed)
        self.orientationComboBox.currentIndexChanged.connect(self.on_orientation_changed)
        self.calculerButton.clicked.connect(self.on_calculer_clicked)

    def on_function_edited(self):
        f_str = self.functionLineEdit.text()
        if self.model.validate_function(f_str):
            self.model.function_str = f_str
        else:
            QMessageBox.critical(self, "Erreur", "Fonction invalide")
            self.functionLineEdit.clear()

    def on_borne_inf_edited(self):
        try:
            self.model.borne_inf = float(self.infLineEdit.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Borne inférieure invalide")

    def on_borne_sup_edited(self):
        try:
            self.model.borne_sup = float(self.supLineEdit.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Borne supérieure invalide")

    def on_nb_rectangles_changed(self):
        self.model.nb_rectangles = int((self.nombreSlider.value() + 1) * 2)

    def on_orientation_changed(self):
        self.model.orientation = self.orientationComboBox.currentText()

    def on_calculer_clicked(self):
        if not self.model.function:
            QMessageBox.warning(self, "Attention", "Veuillez entrer une fonction valide")
            return

        a, b = self.model.borne_inf, self.model.borne_sup
        if a >= b:
            QMessageBox.warning(self, "Attention", "Borne inférieure >= borne supérieure")
            return

        # calculer
        riemann, integrale = self.model.calculer()

        if riemann is None or integrale is None:
            QMessageBox.critical(self, "Erreur", "Impossible de calculer la somme ou l'intégrale")
            self.sommeLineEdit.clear()
            self.integraleLineEdit.clear()
            return

        # mise à jour UI
        self.sommeLineEdit.setText(f"{riemann:.6f}")
        self.integraleLineEdit.setText(f"{integrale:.6f}")

        # redessiner le graphique
        self.model.modelChanged.emit()
