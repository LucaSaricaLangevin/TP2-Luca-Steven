import sympy as sp
from PyQt6.QtCore import pyqtSignal, QObject
import numpy as np


class MainWindowModel(QObject):
    modelChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__x = sp.Symbol("x")
        self.__function = None
        self.__borne_inf = 0.0
        self.__borne_sup = 10.0
        self.__nb_rectangles = 20
        self.__orientation = "Gauche"
        self.__rectangles_active = False

    @property
    def function(self):
        if self.__function is None:
            return None
        try:
            return sp.lambdify(self.__x, self.__function, "numpy")
        except Exception as e:
            print(f"Erreur dans lambdify : {e}")
            return None

    @function.setter
    def function(self, value):
        try:
            self.__function = sp.sympify(value)
            self.modelChanged.emit()
        except Exception as e:
            print(f"Erreur lors de la conversion de la fonction : {e}")
            self.__function = None

    @property
    def variable(self):
        return self.__x

    @variable.setter
    def variable(self, value):
        self.__x = sp.Symbol(value)
        self.modelChanged.emit()

    @property
    def borne_inf(self):
        return self.__borne_inf

    @borne_inf.setter
    def borne_inf(self, value):
        self.__borne_inf = float(value)
        self.modelChanged.emit()

    @property
    def borne_sup(self):
        return self.__borne_sup

    @borne_sup.setter
    def borne_sup(self, value):
        self.__borne_sup = float(value)
        self.modelChanged.emit()

    @property
    def nb_rectangles(self):
        return self.__nb_rectangles

    @nb_rectangles.setter
    def nb_rectangles(self, value):
        self.__nb_rectangles = int(value)
        self.__rectangles_active = True
        self.modelChanged.emit()

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = value
        self.modelChanged.emit()

    @property
    def rectangles_active(self):
        return self.__rectangles_active

    @rectangles_active.setter
    def rectangles_active(self, value: bool):
        self.__rectangles_active = value
        self.modelChanged.emit()

    @staticmethod
    def validate_function(f_str: str) -> bool:
        x = sp.Symbol("x")
        try:
            f_sympy = sp.sympify(f_str)
            f_numpy = sp.lambdify(x, f_sympy, "numpy")
            x_test = np.linspace(-10, 10, 100)
            y_test = f_numpy(x_test)
            return np.all(np.isfinite(y_test))
        except Exception:
            return False
