import json
import os
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal


class FunctionListModel(QObject):
    # signal si fonction change
    functionsChanged = pyqtSignal()

    def __init__(self, json_file="functions.json"):
        super().__init__()
        self.__functions = []
        self.__json_file = json_file
        self.load_from_json()

    @property
    def functions(self):
        return self.__functions.copy()

    def add_function(self, function_str: str) -> bool:
        # ajoute fonction après validation, retourne true si ca a marché, sinon false.
        if not function_str or function_str.strip() == "":
            return False

        function_str = function_str.strip()

        # check si elle existe déjà
        if function_str in self.__functions:
            return False

        # valide la fonction
        if not self.__validate_function(function_str):
            return False

        self.__functions.append(function_str)
        self.functionsChanged.emit()
        return True

    def remove_function(self, index: int) -> bool:
        # retire la fonction à l'index donné, true si réussi sinon false
        if 0 <= index < len(self.__functions):
            self.__functions.pop(index)
            self.functionsChanged.emit()
            return True
        return False

    def __validate_function(self, f_str: str) -> bool:
        # true si réussi sinon false
        try:
            code = compile(f_str, "<string>", "eval")

            def f(x):
                return eval(code, {"x": x, "np": np, "__builtins__": {}})

            # test avec plusieurs valeurs pour détecter les erreurs
            f(1.0)
            f(np.array([1.0, 2.0, 3.0]))
            return True
        except Exception:
            return False

    def save_to_json(self) -> bool:
        # Sauvegarde la liste des fonctions dans un fichier JSON en format simple: {"functions": ["x**2", "np.sin(x)", ...]}
        # retourne true si sauvegarde réussi sinon false

        try:
            data = {"functions": self.__functions}
            with open(self.__json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False

    def load_from_json(self) -> bool:
        # Charge la liste des fonctions depuis un fichier JSON, retourne true si chargement réussi, false sinon

        if not os.path.exists(self.__json_file):
            # fichier par défault vide
            self.__functions = []
            self.save_to_json()
            return True

        try:
            with open(self.__json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.__functions = data.get("functions", [])
            self.functionsChanged.emit()
            return True
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            self.__functions = []
            return False

    def get_function(self, index: int) -> str:
        # retourne la fonction à la position demandée
        if 0 <= index < len(self.__functions):
            return self.__functions[index]
        return ""

    def count(self) -> int:
        # nb de fonctions
        return len(self.__functions)
