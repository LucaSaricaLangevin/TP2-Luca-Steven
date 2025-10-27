import os
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLineEdit, QSlider, QComboBox, QPushButton, QMessageBox, \
    QGroupBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from canvas.matplotlib_canvas import PlotCanvas
from models.main_window_model import MainWindowModel
from models.function_list_model import FunctionListModel
from views.function_list_view import FunctionListView


class MainWindowView(QMainWindow):
    functionLineEdit: QLineEdit
    infLineEdit: QLineEdit
    supLineEdit: QLineEdit
    nombreSlider: QSlider
    orientationComboBox: QComboBox
    calculerButton: QPushButton
    exportButton: QPushButton
    sommeLineEdit: QLineEdit
    integraleLineEdit: QLineEdit
    functionLayout: QVBoxLayout

    def __init__(self):
        super().__init__()
        loadUi("../ui/mainWindow.ui", self)
        
        # Définir la taille de la fenêtre par défaut
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

        # Modèle principal
        self.model = MainWindowModel()
        
        # Canvas matplotlib
        self.canvas = PlotCanvas(self.model)
        toolbar = NavigationToolbar(self.canvas, self)
        self.functionLayout.insertWidget(0, toolbar)
        self.functionLayout.insertWidget(1, self.canvas)

        # Créer le modèle et la vue de la liste de fonctions
        self.function_list_model = FunctionListModel()
        self.function_list_view = FunctionListView(self.function_list_model)
        
        # Ajouter la vue comme DockWidget à droite
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.function_list_view)
        
        # Configurer le menu pour afficher/masquer le dock
        self.setup_menu()

        # Connexions des signaux
        self.functionLineEdit.editingFinished.connect(self.on_function_edited)
        self.infLineEdit.textChanged.connect(self.on_borne_inf_edited)
        self.supLineEdit.textChanged.connect(self.on_borne_sup_edited)
        self.nombreSlider.sliderMoved.connect(lambda: setattr(self.model, "rectangles_active", True))
        self.nombreSlider.sliderMoved.connect(self.on_nb_rectangles_changed)
        self.orientationComboBox.currentIndexChanged.connect(self.on_orientation_changed)
        self.calculerButton.clicked.connect(self.on_calculer_clicked)

    def setup_menu(self):
        """Configure le menu pour afficher/masquer le dock"""
        toggle_action = self.function_list_view.toggleViewAction()
        toggle_action.setText("Afficher/Masquer liste des fonctions")
        self.menufonction.addAction(toggle_action)

    def on_function_edited(self):
        f_str = self.functionLineEdit.text()
        if self.model.validate_function(f_str):
            self.model.function_str = f_str
        else:
            QMessageBox.critical(self, "Erreur", "Fonction invalide")
            self.functionLineEdit.clear()

    def on_borne_inf_edited(self):
        try:
            val = float(self.infLineEdit.text())
            self.model.borne_inf = val
            self.infLineEdit.setStyleSheet("")  # Réinitialiser le style si valide
        except ValueError:
            # Style visuel pour indiquer une erreur
            self.infLineEdit.setStyleSheet("border: 1px solid red;")

    def on_borne_sup_edited(self):
        try:
            val = float(self.supLineEdit.text())
            self.model.borne_sup = val
            self.supLineEdit.setStyleSheet("")  # Réinitialiser le style si valide
        except ValueError:
            # Style visuel pour indiquer une erreur
            self.supLineEdit.setStyleSheet("border: 1px solid red;")

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
