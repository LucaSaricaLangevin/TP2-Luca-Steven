#Classe cree avec Claude pour integrer le LaTeX au combo box des fonctions
from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO


class LatexDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.__main_window = main_window

    def __get_latex_color(self):
        if self.__main_window and hasattr(self.__main_window, '_MainWindowView__is_dark_mode'):
            return 'white' if self.__main_window._MainWindowView__is_dark_mode else 'black'
        return 'white'

    def __function_to_latex(self, function_str: str) -> str:
        try:
            import sympy as sp
            sympy_str = function_str.replace('np.', '')
            expr = sp.sympify(sympy_str)
            latex = sp.latex(expr)
            return f'${latex}$'
        except:
            latex = function_str
            latex = latex.replace('**', '^')
            latex = latex.replace('*', r'\cdot ')
            latex = latex.replace('np.sin', r'\sin')
            latex = latex.replace('np.cos', r'\cos')
            latex = latex.replace('np.exp', r'e^')
            return f'${latex}$'

    def __render_latex_to_pixmap(self, latex_str: str) -> QPixmap:
        try:
            fig = plt.figure(figsize=(4, 0.5))
            fig.patch.set_visible(False)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.axis('off')

            text_color = self.__get_latex_color()

            ax.text(0.5, 0.5, latex_str,
                    fontsize=18,
                    color=text_color,
                    ha='center',
                    va='center',
                    transform=ax.transAxes)

            buf = BytesIO()
            fig.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                        transparent=True, pad_inches=0.1)
            buf.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buf.read())

            plt.close(fig)
            return pixmap

        except Exception as e:
            print(f"Erreur de rendu LaTeX: {e}")
            return QPixmap()

    def paint(self, painter, option, index):
        function_str = index.data(Qt.ItemDataRole.DisplayRole)

        if not function_str or function_str.strip() == "":
            super().paint(painter, option, index)
            return

        latex_str = self.__function_to_latex(function_str)
        pixmap = self.__render_latex_to_pixmap(latex_str)

        if not pixmap.isNull():
            painter.save()

            x = option.rect.x() + (option.rect.width() - pixmap.width()) // 2
            y = option.rect.y() + (option.rect.height() - pixmap.height()) // 2

            painter.drawPixmap(x, y, pixmap)
            painter.restore()
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        function_str = index.data(Qt.ItemDataRole.DisplayRole)

        if not function_str or function_str.strip() == "":
            return QSize(200, 25)

        return QSize(200, 40)