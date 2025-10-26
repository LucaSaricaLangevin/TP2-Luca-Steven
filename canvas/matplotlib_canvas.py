import numpy as np
from PyQt6.QtWidgets import QMessageBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from models.main_window_model import MainWindowModel


class PlotCanvas(FigureCanvas):
    def __init__(self, model: MainWindowModel):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.model = model
        self.model.modelChanged.connect(self.dessiner)

    def dessiner(self):
        try:
            self.ax.clear()
            f = self.model.function
            if f:
                a, b = self.model.borne_inf, self.model.borne_sup
                x = np.linspace(a, b, 1000)
                y = f(x)
                self.ax.plot(x, y, label="f(x)")

                # rectangles
                if self.model.rectangles_active:
                    n = self.model.nb_rectangles
                    dx = (b - a) / n
                    if self.model.orientation == "Droite":
                        x_rect = np.linspace(a + dx, b, n)
                        align = 'edge'  # Rectangle part de x_rect vers la droite
                    else:  # Gauche
                        x_rect = np.linspace(a, b - dx, n)
                        align = 'edge'  # Mais on veut qu'il parte vers la gauche!

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
