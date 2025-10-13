from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QMainWindow, QSlider, QComboBox


class MainWindowView(QMainWindow):
    functionLayout: QVBoxLayout
    functionLineEdit: QLineEdit
    infLineEdit: QLineEdit
    supLineEdit: QLineEdit
    nombreSlider: QSlider
    orientationComboBox: QComboBox
    calculerButton: QPushButton
    exportButton: QPushButton
    sommeLineEdit: QLineEdit
    integraleLineEdit: QLineEdit
