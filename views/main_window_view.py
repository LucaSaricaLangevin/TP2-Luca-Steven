import os
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QLineEdit, QSlider,QComboBox, QPushButton, QMessageBox, QGroupBox, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from canvas.matplotlib_canvas import PlotCanvas
from models.main_window_model import MainWindowModel
from models.function_list_model import FunctionListModel
from views.function_list_view import FunctionListView


class MainWindowView(QMainWindow):
    functionComboBox: QComboBox  # Changé de LineEdit à ComboBox
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

        # Remplir le ComboBox avec les fonctions du modèle
        self.update_function_combobox()

        # Connexions des signaux
        self.functionComboBox.currentTextChanged.connect(self.on_function_changed)
        self.infLineEdit.textChanged.connect(self.on_borne_inf_edited)
        self.supLineEdit.textChanged.connect(self.on_borne_sup_edited)
        self.nombreSlider.sliderMoved.connect(lambda: setattr(self.model, "rectangles_active", True))
        self.nombreSlider.sliderMoved.connect(self.on_nb_rectangles_changed)
        self.orientationComboBox.currentIndexChanged.connect(self.on_orientation_changed)
        self.calculerButton.clicked.connect(self.on_calculer_clicked)
        self.exportButton.clicked.connect(self.on_export_clicked)

        # Connecter le signal personnalisé de la liste de fonctions
        self.function_list_model.functionsChanged.connect(self.update_function_combobox)

        # Connecter modelChanged pour valider les boutons
        self.model.modelChanged.connect(self.validate_buttons)

        # Validation initiale des boutons
        self.validate_buttons()

    def setup_menu(self):
        """Configure le menu pour afficher/masquer le dock"""
        toggle_action = self.function_list_view.toggleViewAction()
        toggle_action.setText("Afficher/Masquer liste des fonctions")
        self.menufonction.addAction(toggle_action)

    @pyqtSlot()
    def update_function_combobox(self):
        """Met à jour le ComboBox avec les fonctions du modèle"""
        current_text = self.functionComboBox.currentText()

        self.functionComboBox.clear()
        self.functionComboBox.addItem("")  # Option vide

        for function in self.function_list_model.functions:
            self.functionComboBox.addItem(function)

        # Restaurer la sélection si elle existe toujours
        index = self.functionComboBox.findText(current_text)
        if index >= 0:
            self.functionComboBox.setCurrentIndex(index)

    def on_function_changed(self, text):
        """Appelé quand la fonction sélectionnée change"""
        if text and text.strip():
            if self.model.validate_function(text):
                self.functionComboBox.setStyleSheet("")
            else:
                self.functionComboBox.setStyleSheet("border: 2px solid red;")
        else:
            self.model.function = None
            self.model.function_str = ""
            self.functionComboBox.setStyleSheet("")

    def on_borne_inf_edited(self):
        try:
            val = float(self.infLineEdit.text())
            self.model.borne_inf = val
            self.infLineEdit.setStyleSheet("")
        except ValueError:
            self.infLineEdit.setStyleSheet("border: 1px solid red;")

    def on_borne_sup_edited(self):
        try:
            val = float(self.supLineEdit.text())
            self.model.borne_sup = val
            self.supLineEdit.setStyleSheet("")
        except ValueError:
            self.supLineEdit.setStyleSheet("border: 1px solid red;")

    def on_nb_rectangles_changed(self):
        self.model.nb_rectangles = int((self.nombreSlider.value() + 1) * 2)

    def on_orientation_changed(self):
        self.model.orientation = self.orientationComboBox.currentText()

    @pyqtSlot()
    def validate_buttons(self):
        """Active/désactive les boutons selon la validité des données"""
        is_valid = self.model.is_valid_for_calculation()
        self.calculerButton.setEnabled(is_valid)
        self.exportButton.setEnabled(is_valid and self.model.function is not None)

    def on_calculer_clicked(self):
        if not self.model.function:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une fonction valide")
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

    def on_export_clicked(self):
        """Exporte le graphique en image"""
        if not self.model.function:
            QMessageBox.warning(self, "Attention", "Aucun graphique à exporter")
            return

        # Ouvrir dialogue de sauvegarde
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le graphique",
            "",
            "Images PNG (*.png);;Images JPEG (*.jpg);;Images SVG (*.svg);;Tous les fichiers (*.*)"
        )

        if file_path:
            try:
                # Sauvegarder la figure
                self.canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Succès", f"Graphique exporté avec succès :\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'exporter le graphique :\n{str(e)}")
