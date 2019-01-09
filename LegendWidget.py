from PyQt5.QtWidgets import QWidget, QLabel, QFrame

class LegendWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.frame = QFrame(self)
        self.frame.setStyleSheet('background-color: white;')

        self.frames = []
        self.defaults = ["background-color: blue;", "background-color: rgba(0, 255, 0, 255);", "background-color: red;", "background-color: rgba(0, 0, 0, 255);"]

        self.labels = []

        for i in range(4):
            f = QFrame(self)
            f.setStyleSheet(self.defaults[i])
            self.frames.append(f)

            l = QLabel(self)
            if i == 0:
                l.setText(": x")
            elif i == 1:
                l.setText(": y")
            elif i == 2:
                l.setText(": z")
            else:
                l.setText(": w")
            l.setStyleSheet("font-weight: bold; font-size: 12px; color: rgba(150, 150, 150, 255);")
            self.labels.append(l)

    def setGeometry(self, *__args):
        super().setGeometry(__args[0], __args[1], __args[2], __args[3])
        self.frame.resize(__args[2], __args[3])

        space = 10
        h = (__args[3] - space * 5) / 4
        if h * 2 + space * 2 > __args[2]:
            h = (__args[2] - space * 2) / 2
        w = h
        x = (__args[2] - w * 2 - 4) / 2
        y = space

        for i in range(4):
            frame = self.frames[i]
            frame.setGeometry(x, y, w, h)
            frame.setStyleSheet(self.defaults[i] + " border-radius: " + repr(int(w / 2)) +"px;")

            label = self.labels[i]
            label.setGeometry(x + w + space, y, __args[2] - (x + w + space + space), h)
            y = y + h + space