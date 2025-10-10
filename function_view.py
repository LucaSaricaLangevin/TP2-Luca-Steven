from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QCheckBox, QPushButton


class FunctionView(QMainWindow):
    matplotlibVLayout: QVBoxLayout
    fonctionLineEdit: QLineEdit
    titreLineEdit: QLineEdit
    afficherGrilleCheckBox: QCheckBox
    dessinerPushButton: QPushButton
    actionCouleur: QAction

    __model: FunctionModel

    def __init__(self):
        super().__init__()
        #loadUi("ui/#mettre nom du UI ici.ui", self)

        self.model = FunctionModel()
        canvas = MPLCanvas(self.model)
        # Canvas Qt pour matplotlib
        toolbar = NavigationToolbar(canvas, self)
        #
        self.matplotlibVLayout.insertWidget(0,toolbar)
        self.matplotlibVLayout.insertWidget(1, canvas)

        self.fonctionLineEdit.editingFinished.connect(self.on_fonction_edited)

        self.titreLineEdit.editingFinished.connect(self.on_title_edited)
        self.afficherGrilleCheckBox.checkStateChanged.connect(self.on_grille_check_state_changed)
        self.dessinerPushButton.clicked.connect(canvas.dessiner)
        self.actionCouleur.triggered.connect(self.on_action_couleur)