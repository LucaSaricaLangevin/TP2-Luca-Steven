import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QSlider, QComboBox, QPushButton, QMessageBox
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from canvas.matplotlib_canvas import PlotCanvas
from models.main_window_model import MainWindowModel
from models import main_window_model


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
        self.calculerButton.clicked.connect(self.on_calculer_clicked)
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

    def on_calculer_clicked(self):
        """
        Méthode appelée lors du clic sur le bouton Calculer
        """
        # Valider que la fonction existe
        if self.model.function is None:
            QMessageBox.warning(self, "Attention", "Veuillez entrer une fonction valide")
            return

        # Valider les bornes
        try:
            borne_inf = self.model.borne_inf
            borne_sup = self.model.borne_sup

            if borne_inf >= borne_sup:
                QMessageBox.warning(self, "Attention",
                                    "La borne inférieure doit être plus petite que la borne supérieure")
                return
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur avec les bornes : {e}")
            return

        # Calculer l'intégrale
        resultat = self.model.calculer()

        if resultat is None:
            QMessageBox.critical(self, "Erreur",
                                 "Impossible de calculer l'intégrale. Vérifiez votre fonction et vos paramètres.")
            self.integraleLineEdit.clear()
        else:
            # Afficher le résultat dans le champ integraleLineEdit
            self.integraleLineEdit.setText(f"{resultat:.6f}")

            # Optionnel : calculer aussi la somme de Riemann (avant multiplication par dx)
            dx = (self.model.borne_sup - self.model.borne_inf) / self.model.nb_rectangles
            somme = resultat / dx
            self.sommeLineEdit.setText(f"{somme:.6f}")

        # Le canvas se mettra à jour automatiquement grâce au signal modelChanged
