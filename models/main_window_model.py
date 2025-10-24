import sympy as sp
from PyQt6.QtCore import pyqtSignal, QObject
import numpy as np
from PyQt6.QtWidgets import QMessageBox


class MainWindowModel(QObject):
    modelChanged = pyqtSignal()

    __x = sp.Symbol("x")
    __function = None
    __borne_inf = 0.0
    __borne_sup = 10.0
    __nb_rectangles = 20
    __orientation = "Gauche"
    __rectangles_active = False
    __valeur_integrale = None

    def __init__(self):
        super().__init__()

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

    @property
    def valeur_integrale(self):
        """Retourne la valeur calculée de l'intégrale"""
        return self.__valeur_integrale

    # Méthode de validation de la fonction, isfinite apprise à l'aide de chatGPT
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

    def calculer(self):
        """
        Méthode appelée lors du clic sur le bouton Calculer
        Calcule à la fois la somme de Riemann ET l'intégrale exacte
        """
        # Valider que la fonction existe
        if self.model.function is None:
            QMessageBox.warning(self, "Attention", "Veuillez entrer une fonction valide")
            return

        # Valider les bornes
        try:
            borne_inf = self.model.borne_inf
            borne_sup = self.model.borne_sup

            if borne_inf >= borne_sup:
                QMessageBox.warning(self, "Attention","La borne inférieure doit être plus petite que la borne supérieure")
                return
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur avec les bornes : {e}")
            return

        # === CALCUL 1 : SOMME DE RIEMANN (approximation numérique) ===
        try:
            f = self.model.function
            nb_rectangles = self.model.nb_rectangles
            orientation = self.model.orientation

            # Calcul de la largeur des rectangles
            dx = (borne_sup - borne_inf) / nb_rectangles

            # Calcul de la somme de Riemann
            somme = 0.0

            for i in range(nb_rectangles):
                if orientation == "Gauche":
                    x_i = borne_inf + i * dx
                elif orientation == "Droite":
                    x_i = borne_inf + (i + 1) * dx
                else:
                    x_i = borne_inf + i * dx

                y_i = f(x_i)

                if not np.isfinite(y_i):
                    raise ValueError("Valeur infinie ou NaN détectée")

                somme += y_i

            resultat_riemann = somme * dx
            self.sommeLineEdit.setText(f"{resultat_riemann:.6f}")

            # Activer les rectangles pour l'affichage
            self.model.rectangles_active = True

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul de Riemann : {e}")
            self.sommeLineEdit.clear()
            return

        # === CALCUL 2 : INTÉGRALE EXACTE (symbolique avec ∫) ===
        try:
            import sympy as sp

            # Récupérer la fonction symbolique
            fonction_str = self.functionLineEdit.text()
            x = sp.Symbol('x')
            fonction_sympy = sp.sympify(fonction_str)

            # Intégration symbolique
            integrale_indefinie = sp.integrate(fonction_sympy, x)

            # Calculer l'intégrale définie entre les bornes
            resultat_exact = integrale_indefinie.subs(x, borne_sup) - \
                             integrale_indefinie.subs(x, borne_inf)

            # Convertir en float
            resultat_exact_float = float(resultat_exact.evalf())
            self.integraleLineEdit.setText(f"{resultat_exact_float:.6f}")

        except Exception as e:
            print(f"Erreur lors du calcul de l'intégrale exacte : {e}")
            self.integraleLineEdit.setText("Non calculable")


