import numpy as np
from PyQt6.QtWidgets import QMessageBox
from matplotlib import pyplot as plt
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from models.main_window_model import MainWindowModel


class PlotCanvas(FigureCanvas):
    def __init__(self, model: MainWindowModel):
        # Configurer les paramètres de matplotlib pour dark mode par défaut
        matplotlib.rcParams['figure.facecolor'] = '#2b2b2b'
        matplotlib.rcParams['axes.facecolor'] = '#2b2b2b'
        matplotlib.rcParams['axes.edgecolor'] = '#e0e0e0'
        matplotlib.rcParams['axes.labelcolor'] = '#e0e0e0'
        matplotlib.rcParams['text.color'] = '#e0e0e0'
        matplotlib.rcParams['xtick.color'] = '#e0e0e0'
        matplotlib.rcParams['ytick.color'] = '#e0e0e0'
        matplotlib.rcParams['grid.color'] = '#555555'
        matplotlib.rcParams['legend.facecolor'] = '#2b2b2b'
        matplotlib.rcParams['legend.edgecolor'] = '#e0e0e0'

        self.__fig, self.__ax = plt.subplots()

        super().__init__(self.__fig)
        self.__model = model
        self.__model.modelChanged.connect(self.dessiner)

        self.__bg_color = '#2b2b2b'
        self.__text_color = '#e0e0e0'

    @property
    def fig(self):
        return self.__fig

    @property
    def ax(self):
        return self.__ax

    def set_theme_colors(self, bg_color, text_color):
        self.__bg_color = bg_color
        self.__text_color = text_color

        matplotlib.rcParams['figure.facecolor'] = bg_color
        matplotlib.rcParams['axes.facecolor'] = bg_color
        matplotlib.rcParams['axes.edgecolor'] = text_color
        matplotlib.rcParams['axes.labelcolor'] = text_color
        matplotlib.rcParams['text.color'] = text_color
        matplotlib.rcParams['xtick.color'] = text_color
        matplotlib.rcParams['ytick.color'] = text_color
        matplotlib.rcParams['legend.facecolor'] = bg_color
        matplotlib.rcParams['legend.edgecolor'] = text_color

        self.__fig.patch.set_facecolor(bg_color)
        self.__ax.set_facecolor(bg_color)
        self.__ax.spines['bottom'].set_color(text_color)
        self.__ax.spines['top'].set_color(text_color)
        self.__ax.spines['left'].set_color(text_color)
        self.__ax.spines['right'].set_color(text_color)
        self.__ax.tick_params(colors=text_color, which='both')
        self.__ax.xaxis.label.set_color(text_color)
        self.__ax.yaxis.label.set_color(text_color)
        self.__ax.title.set_color(text_color)

        if self.__model.function:
            self.dessiner()
        else:
            self.draw()

    def dessiner(self):
        try:
            self.__ax.clear()
            f = self.__model.function
            if f:
                a, b = self.__model.borne_inf, self.__model.borne_sup
                x = np.linspace(a, b, 1000)
                y = f(x)
                self.__ax.plot(x, y, label="f(x)")

                # rectangles (seulement si actifs ET nb_rectangles > 0)
                if self.__model.rectangles_active and self.__model.nb_rectangles > 0:
                    n = self.__model.nb_rectangles
                    dx = (b - a) / n
                    if self.__model.orientation == "Droite":
                        x_rect = np.linspace(a + dx, b, n)
                    else:
                        x_rect = np.linspace(a, b - dx, n)

                    y_rect = f(x_rect)

                    # Pour "Gauche", on doit dessiner le rectangle en partant de x_rect - dx
                    if self.__model.orientation == "Gauche":
                        self.__ax.bar(
                            x_rect - dx, y_rect, width=dx,
                            alpha=0.3, align='edge',
                            edgecolor='black', color='orange',
                            label=f"Somme de Riemann ({self.__model.orientation})"
                        )
                    else:
                        self.__ax.bar(
                            x_rect, y_rect, width=dx,
                            alpha=0.3, align='edge',
                            edgecolor='black', color='orange',
                            label=f"Somme de Riemann ({self.__model.orientation})"
                        )

            self.__ax.legend()
            self.draw()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur dans le dessin : {e}")
