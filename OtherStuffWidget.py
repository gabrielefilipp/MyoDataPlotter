from PyQt5.QtWidgets import QWidget, QLabel, QFrame
from PyQt5.QtGui import QPixmap

from DataManager import *

class OtherStuffWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()

        self.d_m = DataManager()
        self.d_m.add_event_handler(EventType.pose, self.newPoseData)

    def initUI(self):
        self.frame = QFrame(self)
        self.frame.setStyleSheet('background-color: white;')

        self.gestures = []
        self.files = ["images/make_fist.png", "images/wave_right.png", "images/wave_left.png", "images/spread_fingers.png", "images/unlock_gesture.png"]
        for i in range(5):
            g = QLabel(self)
            g.setPixmap(QPixmap(self.files[i]))
            g.setScaledContents(True)
            self.gestures.append(g)

    def setGeometry(self, *__args):
        super().setGeometry(__args[0], __args[1], __args[2], __args[3])
        self.frame.resize(__args[2], __args[3])

        space = 10
        x = space
        y = space
        w = (__args[2] - space * 3) / 2
        if w * 2 + space * 3 > __args[2]:
            w = (__args[2] - space * 3) / 2
        h = w
        if h * 3 + space * 4 > __args[3]:
            h = (__args[3] - space * 4) / 3
        w = h

        for i in range(5):
            g = self.gestures[i]
            g.setGeometry(x, y, w, h)
            if (i + 1) % 2 == 0:
                x = space
                y = y + space + h
            else:
                x = x + space + w
            g.setStyleSheet("border-radius: " + repr(int(w / 2)) + "px; background-color: white;")

    def newPoseData(self, event):
        data = event["data"]
        pose = int(data["pose"])
        if pose == 0:
            for g in self.gestures:
                g.setStyleSheet(g.styleSheet().replace("yellow", "white"))
        else:
            g = self.gestures[pose - 1]
            g.setStyleSheet(g.styleSheet().replace("white", "yellow"))