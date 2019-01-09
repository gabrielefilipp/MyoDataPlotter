from PyQt5.QtWidgets import QWidget
from LegendWidget import LegendWidget
from CubeWidget import CubeWidget
from OtherStuffWidget import OtherStuffWidget

class AllInOneWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.legend = LegendWidget(self)
        self.cube = CubeWidget(self)
        self.other = OtherStuffWidget(self)

    def setGeometry(self, *__args):
        x = __args[0]
        y = __args[1]
        w = __args[2]
        h = __args[3]
        m = min(w, h)
        super().setGeometry(x, y, w, h)
        self.legend.setGeometry(0, 0, (w - m) / 2 - 10, h)
        self.cube.setGeometry((w - m) / 2, (h - m) / 2, m, m)
        self.other.setGeometry((w - m) / 2 + m + 10, 0, (w - m) / 2 - 10, h)