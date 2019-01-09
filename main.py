import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import *
from LogWindow import LogWindow

import PyInstaller as pi

import cProfile

debug = False

def main():
    app = QApplication(sys.argv)
    w = MainWindow(app)
    # w.setStyleSheet('QMainWindow{background-color: white}')
    LogWindow.addToLog("Application Started!")
    sys.exit(app.exec_())


if __name__ == '__main__':
    if debug:
        cProfile.run("main()", sort="time")
    else:
        main()
