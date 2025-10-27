from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDockWidget, QMessageBox, QListWidget, QLineEdit, QPushButton
from PyQt6.uic import loadUi

from models.function_list_model import FunctionListModel


class FunctionListView(QDockWidget):

    def __init__(self, model: FunctionListModel = None):
        super().__init__()
        loadUi("../ui/function_list.ui", self)

        self.model = model if model else FunctionListModel()

        self.listWidget: QListWidget
        self.functionLineEdit: QLineEdit
        self.addButton: QPushButton
        self.cancelButton: QPushButton
        self.saveButton: QPushButton

        self.addButton.clicked.connect(self.on_add_function)
        self.cancelButton.clicked.connect(self.on_remove_function)
        self.saveButton.clicked.connect(self.on_save_functions)

        self.model.functionsChanged.connect(self.update_list_widget)
        self.listWidget.itemClicked.connect(self.on_item_selected)
        self.listWidget.itemDoubleClicked.connect(self.on_item_double_clicked)  # pour éditer la liste

        self.update_list_widget()
        self.setWindowTitle("Liste des fonctions")

        # taille minimal et pref du widget
        self.setMinimumWidth(250)
        self.resize(300, 600)

        # les fonctionnalités du dock (aide Claude pour l'intégration du DockWidget au projet)
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        # Zones d'ancrage autorisées
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )

    def update_list_widget(self):
        # met à jour le widget selon les fonctions du modèle
        self.listWidget.clear()
        for function in self.model.functions:
            self.listWidget.addItem(function)

    def on_add_function(self):
        function_text = self.functionLineEdit.text().strip()

        if not function_text:
            QMessageBox.warning(self, "Attention",
                                "Veuillez entrer une fonction")
            return

        if function_text in self.model.functions:
            QMessageBox.warning(self, "Attention",
                                "Cette fonction existe déjà dans la liste")
            return

        if self.model.add_function(function_text):
            self.functionLineEdit.clear()
            QMessageBox.information(self, "Succès",
                                    f"Fonction '{function_text}' ajoutée avec succès")
        else:
            QMessageBox.critical(self, "Erreur",
                                 "Fonction invalide. Vérifiez la syntaxe.\n\n"
                                 "Exemples valides:\n"
                                 "- x**2\n"
                                 "- np.sin(x)\n"
                                 "- x**3 - 2*x + 1\n"
                                 "- np.exp(-x**2/4)")

    def on_remove_function(self):
        selected_item = self.listWidget.currentItem()

        if not selected_item:
            QMessageBox.warning(self, "Attention",
                                "Veuillez sélectionner une fonction à supprimer")
            return

        row = self.listWidget.row(selected_item)
        function_text = selected_item.text()

        reply = QMessageBox.question(self, "Confirmation",
                                     f"Voulez-vous vraiment supprimer '{function_text}' ?",
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.model.remove_function(row):
                QMessageBox.information(self, "Succès",
                                        "Fonction supprimée avec succès")


    def on_save_functions(self):
        #sauvegarde en JSON
        if self.model.save_to_json():
            QMessageBox.information(self, "Succès",
                                    "Liste des fonctions sauvegardée dans functions.json")
        else:
            QMessageBox.critical(self, "Erreur",
                                 "Impossible de sauvegarder la liste des fonctions")

    def on_item_selected(self, item):
        pass

    def on_item_double_clicked(self, item):
        # il faut double-click pour edit la fonction
        self.functionLineEdit.setText(item.text())
