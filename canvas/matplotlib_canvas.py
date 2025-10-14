import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from models.main_window_model import MainWindowModel


class PlotCanvas(FigureCanvas):
    __model: MainWindowModel

    def __init__(self, model: MainWindowModel):
        self.__fig, self.__ax = plt.subplots()
        super().__init__(self.__fig)
        self.__model = model
        self.__model.modelChanged.connect(self.dessiner)

    def dessiner(self):
        self.__ax.clear()
        f = self.__model.fonction
        if f:
            x = np.linspace(0, 10, 1000)
            y = f(x)

            self.__ax.plot(x, y)
        self.draw()
