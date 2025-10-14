import sympy as sp
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtDesigner import QDesignerCustomWidgetCollectionInterface
from PyQt6.QtGui import QColor



class MainWindowModel(QObject):
    __x = sp.symbols("x")
    __fonction: None = None

    modelChanged = pyqtSignal()

    def __init__(self):
        super().__init__()

    @property
    def fonction(self):
        try:
            f = sp.lambdify(self.__x, self.__fonction, 'numpy')
        except   Exception as e:
            print(e)
            f = None
        return f

    @fonction.setter
    def fonction(self, value):

        self.__fonction = sp.sympify(value)
        self.modelChanged.emit()

    @property
    def variable(self):
        return self.__x


