from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt, pyqtSignal

class FunctionViewModel(QMainWindow):

    def __init__(self):
        super().__init__()

        loadUi("ui/function.ui", self)

        modelChanged = pyqtSignal()

        def __init__(self):
            super().__init__()

        self.addButton.clicked.connect(self.on_add_function())
        self.cancelButton.clicked.connect(self.on_remove_function)
        self.saveButton.clicked.connect(self.on_save_function)

        self.update_list_widget()

    def on_add_function(self):
        function_text = self.functionLineEdit.text()
        if function_text:
            self.model.add_function(function_text)
            self.functionLineEdit.clear()

    def on_remove_function(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            row = self.listWidget.row(selected_item)
            self.model.remove_function(row)

#    def on_save_function(self):

#    def update_list_widget(self):
#        self.listWidget.clear()
#        for function in self.model.functions:
#            self.listWidget.addItem(function)