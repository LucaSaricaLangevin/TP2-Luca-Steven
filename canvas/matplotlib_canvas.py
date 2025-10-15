import numpy as np
from PyQt6.QtWidgets import QMessageBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from models.main_window_model import MainWindowModel


class PlotCanvas(FigureCanvas):
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
                borne_inf = self.__model.borne_inf
                borne_sup = self.__model.borne_sup
                x = np.linspace(borne_inf, borne_sup, 1000)
                y = f(x)
                self.__ax.plot(x, y, label="f(x)")

                if self.__model.rectangles_active:
                    nb_rectangles = self.__model.nb_rectangles
                    orientation = self.__model.orientation
                    x_rect = np.linspace(borne_inf, borne_sup, nb_rectangles + 1)
                    dx = (borne_sup - borne_inf) / nb_rectangles
                    x_points = x_rect[1:] if orientation == "Droite" else x_rect[:-1]
                    y_points = f(x_points)
                    self.__ax.bar(
                        x_points, y_points, width=dx,
                        alpha=0.3, align='edge',
                        edgecolor='black', color='orange',
                        label=f"Somme de Riemann ({orientation})"
                    )

            self.__ax.legend()
            self.draw()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"La fonction est invalide : {e}")
