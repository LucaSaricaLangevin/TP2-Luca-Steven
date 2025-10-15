import sympy as sp
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtDesigner import QDesignerCustomWidgetCollectionInterface
from PyQt6.QtGui import QColor
import numpy as np


class MainWindowModel(QObject):
    __x = sp.symbols("x")
    __function: None = None
    __borne_inf: float = 0
    __borne_sup: float = 10
    __nb_rectangles: int = 20
    __orientation: str = "Gauche"

    modelChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

    @property
    def function(self):
        try:
            f = sp.lambdify(self.__x, self.__function, 'numpy')
        except   Exception as e:
            print(e)
            f = None
        return f

    @function.setter
    def function(self, value):
        self.__function = sp.sympify(value)
        self.modelChanged.emit()

    @property
    def variable(self):
        return self.__x

    @variable.setter
    def variable(self, value):
        self.__x = value

    @property
    def borne_inf(self):
        return self.__borne_inf

    @borne_inf.setter
    def borne_inf(self, value):
        self.__borne_inf = value

    @property
    def borne_sup(self):
        return self.__borne_sup

    @borne_sup.setter
    def borne_sup(self, value):
        self.__borne_sup = value

    @property
    def nb_rectangles(self):
        return self.__nb_rectangles

    @nb_rectangles.setter
    def nb_rectangles(self, value):
        self.__nb_rectangles = value

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = value

    #Méthode de validation de la fonction
    @staticmethod
    def validate_function(f_str):
        x = sp.Symbol('x')
        try:
            f_sympy = sp.sympify(f_str)
            f_numpy = sp.lambdify(x, f_sympy, 'numpy')
            x_test = np.linspace(-10, 10, 100)
            y_test = f_numpy(x_test)
            # .isfinite : avec l'aide de chatGPT
            return np.all(np.isfinite(y_test))
        except Exception:
            return False
