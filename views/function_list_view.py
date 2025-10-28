from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDockWidget, QMessageBox, QListWidget, QLineEdit, QPushButton, QListWidgetItem
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.uic import loadUi
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO

from models.function_list_model import FunctionListModel


class FunctionListView(QDockWidget):

    def __init__(self, model: FunctionListModel = None, main_window=None):
        super().__init__()
        loadUi("../ui/function_list.ui", self)

        self.__model = model if model else FunctionListModel()
        self.__main_window = main_window

        self.listWidget: QListWidget
        self.functionLineEdit: QLineEdit
        self.addButton: QPushButton
        self.cancelButton: QPushButton
        self.saveButton: QPushButton

        self.addButton.clicked.connect(self.__on_add_function)
        self.cancelButton.clicked.connect(self.__on_remove_function)
        self.saveButton.clicked.connect(self.__on_save_functions)

        self.__model.functionsChanged.connect(self.update_list_widget)
        self.listWidget.itemClicked.connect(self.__on_item_selected)
        self.listWidget.itemDoubleClicked.connect(self.__on_item_double_clicked)

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
        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )

    def __get_latex_color(self):
        if self.__main_window and hasattr(self.__main_window, '_MainWindowView__is_dark_mode'):
            return 'white' if self.__main_window._MainWindowView__is_dark_mode else 'black'
        return 'white'

    def __function_to_latex(self, function_str: str) -> str:
        try:
            import sympy as sp
            sympy_str = function_str.replace('np.', '')
            expr = sp.sympify(sympy_str)
            latex = sp.latex(expr)
            return f'${latex}$'
        except:
            latex = function_str
            latex = latex.replace('**', '^')
            latex = latex.replace('*', r'\cdot ')
            latex = latex.replace('np.sin', r'\sin')
            latex = latex.replace('np.cos', r'\cos')
            latex = latex.replace('np.exp', r'e^')
            return f'${latex}$'

    def __render_latex_to_pixmap(self, latex_str: str) -> QPixmap:
        try:
            fig = plt.figure(figsize=(4, 0.5))
            fig.patch.set_visible(False)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')

            text_color = self.__get_latex_color()

            ax.text(0.5, 0.5, latex_str,
                    fontsize=32,
                    color=text_color,
                    ha='center',
                    va='center',
                    transform=ax.transAxes)

            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                        transparent=True, pad_inches=0.1)
            buf.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buf.read())

            plt.close(fig)
            return pixmap

        except Exception as e:
            print(f"Erreur de rendu LaTeX: {e}")
            return QPixmap()

    def update_list_widget(self):
        self.listWidget.clear()
        for function in self.__model.functions:
            item = QListWidgetItem()

            latex_str = self.__function_to_latex(function)
            pixmap = self.__render_latex_to_pixmap(latex_str)

            if not pixmap.isNull():
                item.setIcon(QIcon(pixmap))
                item.setText("")
            else:
                item.setText(function)

            item.setData(Qt.ItemDataRole.UserRole, function)

            self.listWidget.addItem(item)

    def update_latex_color(self):
        self.update_list_widget()

    def __on_add_function(self):
        function_text = self.functionLineEdit.text().strip()

        if not function_text:
            QMessageBox.warning(self, "Attention",
                                "Veuillez entrer une fonction")
            return

        if function_text in self.__model.functions:
            QMessageBox.warning(self, "Attention",
                                "Cette fonction existe déjà dans la liste, espèce de clown !!")
            return

        if self.__model.add_function(function_text):
            self.functionLineEdit.clear()
        else:
            QMessageBox.critical(self, "Erreur",
                                 "Fonction invalide. Vérifiez la syntaxe.\n\n"
                                 "Exemples valides:\n"
                                 "- x**2\n"
                                 "- np.sin(x)\n"
                                 "- x**3 - 2*x + 1\n"
                                 "- np.exp(-x**2/4)")

    def __on_remove_function(self):
        selected_item = self.listWidget.currentItem()

        if not selected_item:
            QMessageBox.warning(self, "Attention",
                                "Veuillez sélectionner une fonction à supprimer")
            return

        row = self.listWidget.row(selected_item)
        function_text = selected_item.data(Qt.ItemDataRole.UserRole)
        if not function_text:
            function_text = selected_item.text()

        reply = QMessageBox.question(self, "Confirmation",
                                     f"Voulez-vous vraiment supprimer '{function_text}' ?",
                                     QMessageBox.StandardButton.Yes |
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.__model.remove_function(row):
                pass

    def __on_save_functions(self):
        # sauvegarde en JSON
        if self.__model.save_to_json():
            QMessageBox.information(self, "Sauvegarde effectuée",
                                    "La liste des fonctions a été sauvegardée dans functions.json")
        else:
            QMessageBox.critical(self, "Erreur",
                                 "Impossible de sauvegarder la liste des fonctions")

    def __on_item_selected(self, item):
        pass

    def __on_item_double_clicked(self, item):
        # il faut double-click pour edit la fonction
        # Récupérer la fonction originale (pas le rendu LaTeX)
        function_text = item.data(Qt.ItemDataRole.UserRole)
        if not function_text:
            function_text = item.text()
        self.functionLineEdit.setText(function_text)
