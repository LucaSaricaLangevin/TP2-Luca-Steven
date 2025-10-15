import numpy as np
from PyQt6.QtWidgets import QMessageBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from models.main_window_model import MainWindowModel


# Aide de ChatGPT pour les mathématiques de la somme de Riemann, oui je suis pas bon en math -Steven
class PlotCanvas(FigureCanvas):
    __model: MainWindowModel

    def __init__(self, model: MainWindowModel):
        self.__fig, self.__ax = plt.subplots()
        super().__init__(self.__fig)
        self.__model = model
        self.__model.modelChanged.connect(self.dessiner)

    def dessiner(self):
        try:
            self.__ax.clear()
            f = self.__model.function
            if f:
                borne_inf = float(self.__model.variable.infLineEdit.text())
                borne_sup = float(self.__model.variable.supLineEdit.text())
                nb_rectangles = int(self.__model.variable.nbRectSpinBox.value())
                orientation = self.__model.variable.orientationComboBox.currentText()

                x = np.linspace(borne_inf, borne_sup, 1000) # le 1000 à adapter selon la fluidité ?
                y = f(x)
                self.__ax.plot(x, y, label="f(x)")

                # Calcul des bornes et de la largeur des rectangles
                x_rect = np.linspace(borne_inf, borne_sup, nb_rectangles + 1)
                dx = (borne_sup - borne_inf) / nb_rectangles

                # Oriente la somme de Riemann
                if orientation == "Gauche":
                    x_points = x_rect[:-1]
                elif orientation == "Droite":
                    x_points = x_rect[1:]

                # Hauteur des rectangles
                y_points = f(x_points)

                # Dessine les rectangles
                self.__ax.bar(
                    x_points, y_points, width=dx,
                    alpha=0.3, align='edge' if orientation == "Gauche" else 'center',
                    edgecolor='black', color='orange',
                    label=f"Somme de Riemann ({orientation})"
                )

            self.draw()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"La fonction est invalide : {e}")
