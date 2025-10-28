from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QLineEdit, QSlider, QComboBox,
                             QPushButton, QMessageBox, QLabel, QFileDialog, QHBoxLayout, QWidget)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.uic import loadUi
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

from canvas.matplotlib_canvas import PlotCanvas
from models.main_window_model import MainWindowModel
from models.function_list_model import FunctionListModel
from views.function_list_view import FunctionListView
from styles.latex_delegate import LatexDelegate


class MainWindowView(QMainWindow):
    functionComboBox: QComboBox
    infLineEdit: QLineEdit
    supLineEdit: QLineEdit
    nombreSlider: QSlider
    orientationComboBox: QComboBox
    calculerButton: QPushButton
    exportButton: QPushButton
    sommeLineEdit: QLineEdit
    integraleLineEdit: QLineEdit
    functionLayout: QVBoxLayout

    def __init__(self, app):
        super().__init__()
        loadUi("../ui/mainWindow.ui", self)

        self.__app = app
        self.__is_dark_mode = True

        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

        self.__model = MainWindowModel()

        self.__canvas = PlotCanvas(self.__model)
        self.__toolbar = NavigationToolbar(self.__canvas, self)

        self.__original_toolbar_icons = {}
        self.__save_original_toolbar_icons()

        self.functionLayout.insertWidget(0, self.__toolbar)
        self.functionLayout.insertWidget(1, self.__canvas)

        self.__function_list_model = FunctionListModel()
        self.__function_list_view = FunctionListView(self.__function_list_model, self)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.__function_list_view)

        self.__setup_menu()
        self.__setup_theme_toggle()
        self.__create_rectangle_count_label()

        # Configuration du délégué LaTeX pour le ComboBox
        self.__latex_delegate = LatexDelegate(self.functionComboBox, self)
        self.functionComboBox.setItemDelegate(self.__latex_delegate)

        self.update_function_combobox()

        self.functionComboBox.currentTextChanged.connect(self.on_function_changed)
        self.infLineEdit.textChanged.connect(self.on_borne_inf_edited)
        self.supLineEdit.textChanged.connect(self.on_borne_sup_edited)
        self.nombreSlider.valueChanged.connect(self.on_nb_rectangles_changed)
        self.orientationComboBox.currentIndexChanged.connect(self.on_orientation_changed)
        self.calculerButton.clicked.connect(self.on_calculer_clicked)
        self.exportButton.clicked.connect(self.on_export_clicked)

        self.__function_list_model.functionsChanged.connect(self.update_function_combobox)
        self.__model.modelChanged.connect(self.__validate_buttons)

        self.__validate_buttons()

    def __save_original_toolbar_icons(self):
        for action in self.__toolbar.actions():
            if not action.isSeparator():
                icon = action.icon()
                if not icon.isNull():
                    self.__original_toolbar_icons[action] = icon.pixmap(24, 24).copy()

    def __update_toolbar_icons(self, invert=False):
        for action, original_pixmap in self.__original_toolbar_icons.items():
            if invert:
                image = original_pixmap.toImage()
                image.invertPixels()
                action.setIcon(QIcon(QPixmap.fromImage(image)))
            else:
                action.setIcon(QIcon(original_pixmap))

    def __setup_theme_toggle(self):
        self.__theme_toggle_button = QPushButton("🌙")
        self.__theme_toggle_button.setObjectName("themeToggleButton")
        self.__theme_toggle_button.setToolTip("Basculer entre mode clair et sombre")
        self.__theme_toggle_button.clicked.connect(self.__toggle_theme)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(self.__theme_toggle_button)
        layout.setContentsMargins(0, 0, 10, 0)

        self.menubar.setCornerWidget(container, Qt.Corner.TopRightCorner)

    def __create_rectangle_count_label(self):
        slider_layout = self.findChild(QVBoxLayout, "verticalLayout_5")

        if slider_layout:
            self.__rectangle_count_label = QLabel(f"{self.__model.nb_rectangles}")
            self.__rectangle_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.__rectangle_count_label.setStyleSheet("font-weight: bold; font-size: 11pt;")

            slider_layout.addWidget(self.__rectangle_count_label)

    def __toggle_theme(self):
        self.__is_dark_mode = not self.__is_dark_mode

        if self.__is_dark_mode:
            theme_file = "../styles/dark_theme.qss"
            self.__theme_toggle_button.setText("🌙")
            bg_color = '#2b2b2b'
            text_color = '#e0e0e0'
            self.__update_toolbar_icons(invert=False)
        else:
            theme_file = "../styles/light_theme.qss"
            self.__theme_toggle_button.setText("☀️")
            bg_color = '#ffffff'
            text_color = '#333333'
            self.__update_toolbar_icons(invert=True)

        self.__canvas.set_theme_colors(bg_color, text_color)

        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                self.__app.setStyleSheet(f.read())

            # Notifier la liste de fonctions pour mettre à jour la couleur LaTeX
            self.__function_list_view.update_latex_color()

            # Rafraîchir le ComboBox pour le nouveau thème
            self.update_function_combobox()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger le thème: {e}")

    def __setup_menu(self):
        toggle_action = self.__function_list_view.toggleViewAction()
        toggle_action.setText("Afficher/Masquer liste des fonctions")
        self.menufonction.addAction(toggle_action)

    @pyqtSlot()
    def update_function_combobox(self):
        current_text = self.functionComboBox.currentText()

        self.functionComboBox.clear()
        self.functionComboBox.addItem("")

        for function in self.__function_list_model.functions:
            self.functionComboBox.addItem(function)

        index = self.functionComboBox.findText(current_text)
        if index >= 0:
            self.functionComboBox.setCurrentIndex(index)

    def on_function_changed(self, text):
        if text and text.strip():
            if self.__model.validate_function(text):
                self.functionComboBox.setStyleSheet("")
            else:
                self.functionComboBox.setStyleSheet("border: 2px solid red;")
        else:
            self.__model.function = None
            self.__model.function_str = ""
            self.functionComboBox.setStyleSheet("")

    def on_borne_inf_edited(self):
        try:
            val = float(self.infLineEdit.text())
            self.__model.borne_inf = val
            self.infLineEdit.setStyleSheet("")
        except ValueError:
            self.infLineEdit.setStyleSheet("border: 1px solid red;")

    def on_borne_sup_edited(self):
        try:
            val = float(self.supLineEdit.text())
            self.__model.borne_sup = val
            self.supLineEdit.setStyleSheet("")
        except ValueError:
            self.supLineEdit.setStyleSheet("border: 1px solid red;")

    # Petite utilisation de Claude pour permettre aux rectangles de changer en temps reel
    def on_nb_rectangles_changed(self):
        slider_value = self.nombreSlider.value()

        if slider_value == 0:
            self.__model.rectangles_active = False
            self.__model.nb_rectangles = 0
            if hasattr(self, '_MainWindowView__rectangle_count_label'):
                self.__rectangle_count_label.setText("0")
        else:
            self.__model.rectangles_active = True
            self.__model.nb_rectangles = slider_value * 5
            if hasattr(self, '_MainWindowView__rectangle_count_label'):
                self.__rectangle_count_label.setText(f"{self.__model.nb_rectangles}")

    def on_orientation_changed(self):
        self.__model.orientation = self.orientationComboBox.currentText()

    @pyqtSlot()
    def __validate_buttons(self):
        is_valid = self.__model.is_valid_for_calculation()
        self.calculerButton.setEnabled(is_valid)
        self.exportButton.setEnabled(is_valid and self.__model.function is not None)

    def on_calculer_clicked(self):
        if not self.__model.function:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une fonction valide")
            return

        a, b = self.__model.borne_inf, self.__model.borne_sup
        if a >= b:
            QMessageBox.warning(self, "Attention", "Borne inférieure >= borne supérieure")
            return

        riemann, integrale = self.__model.calculer()

        if riemann is None or integrale is None:
            QMessageBox.critical(self, "Erreur", "Impossible de calculer la somme ou l'intégrale")
            self.sommeLineEdit.clear()
            self.integraleLineEdit.clear()
            return

        self.sommeLineEdit.setText(f"{riemann:.6f}")
        self.integraleLineEdit.setText(f"{integrale:.6f}")

        self.__model.modelChanged.emit()

    def on_export_clicked(self):
        if not self.__model.function:
            QMessageBox.warning(self, "Attention", "Aucun graphique à exporter")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le graphique",
            "",
            "Images PNG (*.png);;Images JPEG (*.jpg);;Images SVG (*.svg);;Tous les fichiers (*.*)"
        )

        if file_path:
            try:
                self.__canvas.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Succès", f"Graphique exporté avec succès :\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible d'exporter le graphique :\n{str(e)}")