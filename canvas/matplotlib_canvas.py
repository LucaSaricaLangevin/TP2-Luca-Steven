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

        self.fig, self.ax = plt.subplots()

        super().__init__(self.fig)
        self.model = model
        self.model.modelChanged.connect(self.dessiner)

        # Couleurs par défaut (dark mode)
        self.bg_color = '#2b2b2b'
        self.text_color = '#e0e0e0'

    def set_theme_colors(self, bg_color, text_color):
        """Change les couleurs du thème en mettant à jour les rcParams"""
        self.bg_color = bg_color
        self.text_color = text_color

        # Mettre à jour les paramètres globaux de matplotlib
        matplotlib.rcParams['figure.facecolor'] = bg_color
        matplotlib.rcParams['axes.facecolor'] = bg_color
        matplotlib.rcParams['axes.edgecolor'] = text_color
        matplotlib.rcParams['axes.labelcolor'] = text_color
        matplotlib.rcParams['text.color'] = text_color
        matplotlib.rcParams['xtick.color'] = text_color
        matplotlib.rcParams['ytick.color'] = text_color
        matplotlib.rcParams['legend.facecolor'] = bg_color
        matplotlib.rcParams['legend.edgecolor'] = text_color

        # Appliquer directement sur la figure et les axes
        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(bg_color)
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['top'].set_color(text_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.spines['right'].set_color(text_color)
        self.ax.tick_params(colors=text_color, which='both')
        self.ax.xaxis.label.set_color(text_color)
        self.ax.yaxis.label.set_color(text_color)
        self.ax.title.set_color(text_color)

        # Redessiner
        if self.model.function:
            self.dessiner()
        else:
            self.draw()

    def dessiner(self):
        try:
            self.ax.clear()
            f = self.model.function
            if f:
                a, b = self.model.borne_inf, self.model.borne_sup
                x = np.linspace(a, b, 1000)
                y = f(x)
                self.ax.plot(x, y, label="f(x)")

                # rectangles (seulement si actifs ET nb_rectangles > 0)
                if self.model.rectangles_active and self.model.nb_rectangles > 0:
                    n = self.model.nb_rectangles
                    dx = (b - a) / n
                    if self.model.orientation == "Droite":
                        x_rect = np.linspace(a + dx, b, n)
                    else:  # Gauche
                        x_rect = np.linspace(a, b - dx, n)

                    y_rect = f(x_rect)

                    # Pour "Gauche", on doit dessiner le rectangle en partant de x_rect - dx
                    if self.model.orientation == "Gauche":
                        self.ax.bar(
                            x_rect - dx, y_rect, width=dx,
                            alpha=0.3, align='edge',
                            edgecolor='black', color='orange',
                            label=f"Somme de Riemann ({self.model.orientation})"
                        )
                    else:
                        self.ax.bar(
                            x_rect, y_rect, width=dx,
                            alpha=0.3, align='edge',
                            edgecolor='black', color='orange',
                            label=f"Somme de Riemann ({self.model.orientation})"
                        )

            self.ax.legend()
            self.draw()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur dans le dessin : {e}")