from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import *
import DataManager as dm
import datetime

HEIGHT = 450
WIDTH = 450

class LogWindow(QMainWindow):

    instances = []

    @staticmethod
    def addToLog(str, ms_digits=3):
        for instance in LogWindow.instances:
            instance.addLog(str, ms_digits)


    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.instances.append(self)
        self.data_manager = dm.DataManager()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Log Console")
        self.setGeometry(120, 160, WIDTH, HEIGHT)

        self.setMinimumSize(WIDTH, HEIGHT / 2)

        self.log = QTextBrowser(self)
        self.log.setGeometry(10, 10, WIDTH - 20, HEIGHT - 20)

    def addLog(self, log, ms_digits=2):
        if ms_digits > 6:
            ms_digits = 6
        str_time = datetime.datetime.now().strftime("%H:%M:%S.%f")[:(ms_digits - 6)]
        self.log.append("[" + str_time + "]: " + log)

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        rect:QRect = self.rect()
        self.log.setGeometry(10, 10, rect.width() - 20, rect.height() - 20)