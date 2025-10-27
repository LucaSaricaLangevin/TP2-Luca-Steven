from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDockWidget, QMessageBox, QListWidget, QLineEdit, QPushButton, QListWidgetItem
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.uic import loadUi
import matplotlib
matplotlib.use('Agg')  # Backend sans interface graphique
import matplotlib.pyplot as plt
from io import BytesIO

from models.function_list_model import FunctionListModel


class FunctionListView(QDockWidget):

    def __init__(self, model: FunctionListModel = None, main_window=None):
        super().__init__()
        loadUi("../ui/function_list.ui", self)

        self.model = model if model else FunctionListModel()
        self.main_window = main_window

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
        self.listWidget.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Configurer le QListWidget pour afficher des icônes LaTeX
        self.listWidget.setIconSize(QSize(200, 40))

        self.update_list_widget()
        self.setWindowTitle("Liste des fonctions")

        # taille minimal et pref du widget
        self.setMinimumWidth(250)
        self.resize(300, 600)

        # les fonctionnalités du dock
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

    def get_latex_color(self):
        if self.main_window and hasattr(self.main_window, 'is_dark_mode'):
            return 'white' if self.main_window.is_dark_mode else 'black'
        return 'white'  # Par défaut dark mode

    def function_to_latex(self, function_str: str) -> str:
        try:
            import sympy as sp
            # Remplacer np.fonction par fonction pour sympy
            sympy_str = function_str.replace('np.', '')
            # Parser avec sympy
            expr = sp.sympify(sympy_str)
            # Convertir en LaTeX
            latex = sp.latex(expr)
            return f'${latex}$'
        except:
            # Fallback : conversion manuelle
            latex = function_str
            latex = latex.replace('**', '^')
            latex = latex.replace('*', r'\cdot ')
            latex = latex.replace('np.sin', r'\sin')
            latex = latex.replace('np.cos', r'\cos')
            latex = latex.replace('np.exp', r'e^')
            return f'${latex}$'

    def render_latex_to_pixmap(self, latex_str: str) -> QPixmap:
        try:
            # Créer une figure matplotlib
            fig = plt.figure(figsize=(4, 0.5))
            fig.patch.set_visible(False)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')

            # Obtenir la couleur appropriée
            text_color = self.get_latex_color()

            # Rendre le texte LaTeX
            ax.text(0.5, 0.5, latex_str,
                   fontsize=18,
                   color=text_color,
                   ha='center',
                   va='center',
                   transform=ax.transAxes)

            # Sauvegarder dans un buffer
            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                       transparent=True, pad_inches=0.1)
            buf.seek(0)

            # Convertir en QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buf.read())

            plt.close(fig)
            return pixmap

        except Exception as e:
            print(f"Erreur de rendu LaTeX: {e}")
            return QPixmap()

    def update_list_widget(self):
        self.listWidget.clear()
        for function in self.model.functions:
            # Créer un item
            item = QListWidgetItem()

            # Convertir en LaTeX et créer l'icône
            latex_str = self.function_to_latex(function)
            pixmap = self.render_latex_to_pixmap(latex_str)

            if not pixmap.isNull():
                item.setIcon(QIcon(pixmap))
                item.setText("")  # Pas de texte, juste l'icône LaTeX
            else:
                # Fallback : afficher le texte normal si le rendu échoue
                item.setText(function)

            # Stocker la fonction originale dans les données de l'item
            item.setData(Qt.ItemDataRole.UserRole, function)

            self.listWidget.addItem(item)

    def update_latex_color(self):
        self.update_list_widget()

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
        # Récupérer la fonction originale depuis les données
        function_text = selected_item.data(Qt.ItemDataRole.UserRole)
        if not function_text:
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
        # sauvegarde en JSON
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
        # Récupérer la fonction originale (pas le rendu LaTeX)
        function_text = item.data(Qt.ItemDataRole.UserRole)
        if not function_text:
            function_text = item.text()
        self.functionLineEdit.setText(function_text)
