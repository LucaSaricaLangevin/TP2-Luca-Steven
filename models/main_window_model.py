import sympy as sp
from PyQt6.QtCore import pyqtSignal, QObject
import numpy as np


class MainWindowModel(QObject):
    modelChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__function_str = ""
        self.__function = None
        self.__x = sp.Symbol("x")
        self.__borne_inf = 0.0
        self.__borne_sup = 1.0
        self.__nb_rectangles = 0
        self.__orientation = "Gauche"
        self.__rectangles_active = False
        self.__valeur_riemann = None
        self.__valeur_integrale = None

    @property
    def function_str(self):
        return self.__function_str

    @function_str.setter
    def function_str(self, s):
        self.__function_str = s

    @property
    def function(self):
        return self.__function

    @function.setter
    def function(self, f):
        self.__function = f
        self.modelChanged.emit()

    @property
    def borne_inf(self):
        return self.__borne_inf

    @borne_inf.setter
    def borne_inf(self, val):
        self.__borne_inf = float(val)
        self.modelChanged.emit()

    @property
    def borne_sup(self):
        return self.__borne_sup

    @borne_sup.setter
    def borne_sup(self, val):
        self.__borne_sup = float(val)
        self.modelChanged.emit()

    @property
    def nb_rectangles(self):
        return self.__nb_rectangles

    @nb_rectangles.setter
    def nb_rectangles(self, val):
        self.__nb_rectangles = max(1, int(val))
        self.modelChanged.emit()

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, val):
        self.__orientation = val
        self.modelChanged.emit()

    @property
    def rectangles_active(self):
        return self.__rectangles_active

    @rectangles_active.setter
    def rectangles_active(self, val):
        self.__rectangles_active = val
        self.modelChanged.emit()

    @property
    def valeur_riemann(self):
        return self.__valeur_riemann

    @property
    def valeur_integrale(self):
        return self.__valeur_integrale

    # Methode de validation de la fonction, avec l'aide de chatGPT pour certains elements
    def validate_function(self, f_str: str):
        try:
            code = compile(f_str, "<string>", "eval")

            def f(x):
                safe_dict = {
                    "x": x,
                    "np": np,
                    "sin": np.sin,
                    "cos": np.cos,
                    "tan": np.tan,
                    "exp": np.exp,
                    "log": np.log,
                    "sqrt": np.sqrt,
                    "abs": np.abs,
                    "pi": np.pi,
                    "e": np.e,
                    "__builtins__": {}
                }
                return eval(code, safe_dict)

            f(1)
            self.function_str = f_str
            self.function = f
            return True
        except Exception:
            return False

    def is_valid_for_calculation(self) -> bool:
        if not self.function:
            return False

        try:
            if self.borne_inf >= self.borne_sup:
                return False
        except:
            return False

        return True

    # Calculs des integrales
    def calculer_somme_riemann(self):
        if not self.function:
            return None

        a, b = self.borne_inf, self.borne_sup
        n = self.nb_rectangles
        dx = (b - a) / n

        if self.orientation == "Droite":
            x_points = np.linspace(a + dx, b, n)
        else:
            x_points = np.linspace(a, b - dx, n)

        y_points = self.function(x_points)
        self.__valeur_riemann = np.sum(y_points) * dx
        return self.__valeur_riemann

    def calculer_integrale(self):
        if not self.function_str:
            return None
        try:
            f_sympy = sp.sympify(self.function_str)
            integrale_definie = sp.integrate(f_sympy, (self.__x, self.borne_inf, self.borne_sup))
            self.__valeur_integrale = float(integrale_definie.evalf())
            return self.__valeur_integrale
        except Exception:
            self.__valeur_integrale = None
            return None

    def calculer(self):
        self.calculer_somme_riemann()
        self.calculer_integrale()
        self.modelChanged.emit()
        return self.__valeur_riemann, self.__valeur_integrale
