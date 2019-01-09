from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtWidgets import *
from CubeWidget import *
from AllInOneWidget import AllInOneWidget
from MultiGraphWidget import *
from DataManager import *
from InfoWindow import InfoWindow
from LogWindow import LogWindow
import math
import inspect
from myo._ffi import Quaternion

HEIGHT = 600
WIDTH = 1080

class MainWindow(QMainWindow):

    all_one :AllInOneWidget = None
    gyroGraph :MultiGraphWidget = None
    accGraph :MultiGraphWidget = None
    orienGraph: MultiGraphWidget = None
    emgGrapgs = []
    data_manager :DataManager = None
    disc:QAction = None
    info:QAction = None
    infoWindow:InfoWindow = None
    logWindow: LogWindow = None
    center_vect:Quaternion = Quaternion(0, 0, 0, 0)
    need_center = False
    requested_center = False

    def __init__(self, app):
        super(MainWindow, self).__init__()
        self.title = 'EMG Myo'

        self.width = WIDTH#app.desktop().width()
        self.height = HEIGHT#app.desktop().height()

        self.left = (app.desktop().width() - self.width) / 2
        self.top = (app.desktop().height() - self.height) / 2
        self.setMinimumSize(QSize(WIDTH * 3 / 4, HEIGHT * 3 / 4))

        self.data_manager = DataManager()
        self.data_manager.add_event_handler(EventType.orientation, self.newOrientationData)
        self.data_manager.add_event_handler(EventType.emg, self.newEmgData)
        self.data_manager.add_event_handler(EventType.connected, self.connectionChanged)
        self.data_manager.add_event_handler(EventType.disconnected, self.connectionChanged)

        self.initUI()
        self.createMenus()
        self.show()

    def initUI(self):
        dim = self.get_max_data_points()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.gyroGraph = MultiGraphWidget(self, max_data=dim, y_range=1000, background="w", channels=3, title="<b>Gyroscope</b>")

        self.accGraph = MultiGraphWidget(self, max_data=dim, y_range=3, background="w", channels=3, title="<b>Acceleration</b>")

        self.orienGraph = MultiGraphWidget(self, max_data=dim, y_range=1, background="w", channels=4, title="<b>Orientation</b>")

        for i in range(8):
            if i==0:
                color=(255, 0, 0)
            elif i==1:
                color=(255, 165, 0)
            elif i==2:
                color=(255, 210, 0)
            elif i==3:
                color=(0, 128, 0)
            elif i==4:
                color=(0, 255, 255)
            elif i==5:
                color=(0, 0, 255)
            elif i==6:
                color=(255, 0, 255)
            elif i==7:
                color=(205, 133, 63)
            g = MultiGraphWidget(self, max_data=dim, y_range=100, channels=1, colors=[color], background="w", title="<b>Pod " + repr(i + 1) + "</b>")
            self.emgGrapgs.append(g)

        self.all_one = AllInOneWidget(self)
        self.infoWindow = InfoWindow(self)
        self.logWindow = LogWindow(self)

        self.resizeStuff()

    def createMenus(self):
        bar:QMenuBar = self.menuBar()

        device = bar.addMenu("Device")
        connect = QAction("Connect", self)
        connect.setShortcut("Ctrl+C")
        connect.triggered.connect(self.connect)
        device.addAction(connect)

        self.disc = QAction("Disconnect", self)
        self.disc.setShortcut("Ctrl+D")
        self.disc.setEnabled(False)
        self.disc.triggered.connect(self.disconnect)
        device.addAction(self.disc)

        device.addSeparator()

        self.info = QAction("Info", self)
        self.info.setShortcut("Ctrl+I")
        self.info.setEnabled(False)
        self.info.triggered.connect(self.infoWindow.show)
        device.addAction(self.info)

        log = QAction("Log Console", self)
        log.setShortcut("Ctrl+L")
        log.triggered.connect(self.logWindow.show)
        device.addAction(log)

        view = bar.addMenu("View")

        reset = QAction("Default", self)
        reset.setCheckable(False)
        reset.setShortcut("Ctrl+R")
        view.addAction(reset)

        once = view.addMenu("Show");
        only = view.addMenu("Show only");

        for i in range(8):
            pod = QAction("Show Pod " + repr(i + 1), self)
            pod.setData(self.emgGrapgs[i])
            pod.setCheckable(True)
            pod.setChecked(True)
            pod.setShortcut("Ctrl+" + repr(i + 1))
            once.addAction(pod)

            s = i + 1
            e = 7 + i
            if e > 7:
                e = i

            pod1 = QAction("Show only Pod " + repr(i + 1), self)
            pod1.setData([self.emgGrapgs[i]])
            pod1.setShortcut("Ctrl+Alt+" + repr(i + 1))
            only.addAction(pod1)

        once.addSeparator()
        only.addSeparator()
        c = QAction("Show Cube", self)
        c.setData(self.all_one)
        c.setCheckable(True)
        c.setChecked(True)
        c.setShortcut("Ctrl+Shift+C")
        once.addAction(c)

        c1 = QAction("Show only Cube", self)
        c1.setData([self.all_one])
        c1.setShortcut("Ctrl+Alt+C")
        only.addAction(c1)

        g = QAction("Show Gyroscope", self)
        g.setData(self.gyroGraph)
        g.setCheckable(True)
        g.setChecked(True)
        g.setShortcut("Ctrl+G")
        once.addAction(g)

        g1 = QAction("Show only Gyroscope", self)
        g1.setData([self.gyroGraph])
        g1.setShortcut("Ctrl+Alt+G")
        only.addAction(g1)

        o = QAction("Show Orientation", self)
        o.setData(self.orienGraph)
        o.setCheckable(True)
        o.setChecked(True)
        o.setShortcut("Ctrl+O")
        once.addAction(o)

        o1 = QAction("Show only Orientation", self)
        o1.setData([self.orienGraph])
        o1.setShortcut("Ctrl+Alt+O")
        only.addAction(o1)

        a = QAction("Show Acceleration", self)
        a.setData(self.accGraph)
        a.setCheckable(True)
        a.setChecked(True)
        a.setShortcut("Ctrl+A")
        once.addAction(a)

        a1 = QAction("Show Acceleration", self)
        a1.setData([self.accGraph])
        a1.setShortcut("Ctrl+Alt+A")
        only.addAction(a1)

        only.addSeparator()
        pods = QAction("Show only pods", self)
        pods.setData(self.emgGrapgs)
        pods.setShortcut("Ctrl+Alt+P")
        only.addAction(pods)

        oriens = QAction("Show only orientation graphs", self)
        oriens.setData([self.all_one, self.orienGraph, self.accGraph, self.gyroGraph])
        oriens.setShortcut("Ctrl+Alt+K")
        only.addAction(oriens)

        view.triggered[QAction].connect(self.viewTrigger)

        time = bar.addMenu("Interval")
        lag = QAction("Refresh as soon as new data is available", self)
        lag.setCheckable(True)
        lag.setChecked(self.data_manager.myo.refresh_rate == 0 and (not self.data_manager.auto))
        lag.setData(0)
        time.addAction(lag)
        for i in range(5):
            interval = QAction("Refresh every " + repr((i + 1) * 100) + "ms", self)
            interval.setCheckable(True)
            interval.setChecked(self.data_manager.myo.refresh_rate == (i + 1) * 100 and (not self.data_manager.auto))
            interval.setData((i + 1) * 100)
            time.addAction(interval)
        interval = QAction("Refresh every 1s", self)
        interval.setCheckable(True)
        interval.setChecked(self.data_manager.myo.refresh_rate == 1000 and (not self.data_manager.auto))
        interval.setData(1000)
        time.addAction(interval)
        time.addSeparator()
        auto = QAction("Auto refresh rate", self)
        auto.setCheckable(True)
        auto.setChecked(self.data_manager.auto)
        auto.setData(-1)
        #auto.setChecked(self.data_manager.setAuto())
        time.addAction(auto)

        time.triggered[QAction].connect(self.refreshTrigger)

        orien = bar.addMenu("Orientation")
        center = QAction("Set origin", self)
        center.triggered.connect(self.center)
        orien.addAction(center)
        decenter = QAction("Set default origin", self)
        decenter.triggered.connect(self.decenter)
        orien.addAction(decenter)


        self.setWindowTitle("EMG")

    def closeEvent(self, event):
        result = QMessageBox.question(
            self, 'Conferma', 'Sei sicuro di volere uscire?',
            QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, QKeyEvent):
        super().keyPressEvent(QKeyEvent)
        if self.isFullScreen():
            if QKeyEvent.key() == QtCore.Qt.Key_Escape:
                self.showNormal()

    def center(self):
        self.requested_center = True
        self.need_center = True

    def decenter(self):
        self.requested_center = False
        self.need_center = False
        self.center_vect.x = 0
        self.center_vect.y = 0
        self.center_vect.z = 0
        self.center_vect.w = 0

    def get_max_data_points(self):
        data = self.data_manager.myo.refresh_rate
        if data == 0:
            return 200
        else:
            return math.floor(1000 / math.sqrt(data))

    def refreshTrigger(self, act:QAction):
        #if self.data_manager.myo.refresh_rate == act.data():
        #    act.setChecked(True)
        #    return
        for a in self.menuBar().children()[3].actions():
            if a.isCheckable() and a != act:
                a.setChecked(False)
        if act.data() == -1:
            self.data_manager.auto = True
            max_p = 100
        else:
            self.data_manager.auto = False
            self.data_manager.setRefreshRate(act.data())
            max_p = self.get_max_data_points()

        for emg in self.emgGrapgs:
            emg.max_data_points = max_p
        self.orienGraph.max_data_points = max_p
        self.accGraph.max_data_points = max_p
        self.gyroGraph.max_data_points = max_p

    def viewTrigger(self, act:QAction):
        if act.text() == "Default":
            for a in self.menuBar().children()[2].children()[1].actions():
                if a.isCheckable():
                    a.setChecked(True)
                    self.show_hide_widget_to_action(a)
        else:
            data = act.data()
            if isinstance(data, list):
                for a in self.menuBar().children()[2].children()[1].actions():
                    if a.isCheckable():
                        a.setChecked(data.__contains__(a.data()))
            self.show_hide_widget_to_action(act)

    def show_hide_widget_to_action(self, act:QAction):
        data = act.data()
        if isinstance(data, list):
            tmp = self.emgGrapgs + [self.all_one, self.gyroGraph, self.orienGraph, self.accGraph]
            for view in tmp:
                view.setHidden(True)
            for view in data:
                view.setHidden(False)
        else:
            act.data().setHidden(not act.isChecked())
        self.resizeStuff()

    def connect(self):
        self.data_manager.startCollectingData()

    def disconnect(self):
        self.data_manager.stopCollectingData()

    def connectionChanged(self, event):
        connected = event["type"] == EventType.connected
        self.disc.setEnabled(connected)
        self.info.setEnabled(connected)
        if connected:
            self.gyroGraph.center()
            self.accGraph.center()
            self.orienGraph.center()
            for i in range(len(self.emgGrapgs)):
                self.emgGrapgs[i].center()
        else:
            if self.infoWindow.isVisible():
                self.infoWindow.close()
            self.gyroGraph.plot_all_data()
            self.accGraph.plot_all_data()
            self.orienGraph.plot_all_data()
            for i in range(len(self.emgGrapgs)):
                self.emgGrapgs[i].plot_all_data()

    def quatRotate(self, e, t):
        rotate:Quaternion  = Quaternion(0, 0, 0, 0)
        rotate.w = e.w * t.w - e.x * t.x - e.y * t.y - e.z * t.z
        rotate.x = e.w * t.x + e.x * t.w + e.y * t.z - e.z * t.y
        rotate.y = e.w * t.y - e.x * t.z + e.y * t.w + e.z * t.x
        rotate.z = e.w * t.z + e.x * t.y - e.y * t.x + e.z * t.w
        return rotate

    def newOrientationData(self, event):
        data = event["data"]
        gyroscope = data["gyroscope"]
        acceleration = data["acceleration"]
        orientation:Quaternion = data["orientation"]

        #orientation = orientation.normalized()

        if self.need_center:
            self.need_center = False
            self.center_vect = orientation.normalized().__invert__()

        if self.requested_center: #TODO: Rotate quatern to new orientation
             orientation = self.quatRotate(self.center_vect, orientation)

        pitch = orientation.pitch * 180 / math.pi
        yam = orientation.yaw * 180 / math.pi
        roll = orientation.roll * 180 / math.pi

        self.all_one.cube.vector_rotate = [roll, pitch, yam]

        self.gyroGraph.add_data_to_channel(0, gyroscope[0])
        self.gyroGraph.add_data_to_channel(1, gyroscope[1])
        self.gyroGraph.add_data_to_channel(2, gyroscope[2])

        self.accGraph.add_data_to_channel(0, acceleration[0])
        self.accGraph.add_data_to_channel(1, acceleration[1])
        self.accGraph.add_data_to_channel(2, acceleration[2])

        self.orienGraph.add_data_to_channel(0, orientation.x)
        self.orienGraph.add_data_to_channel(1, orientation.y)
        self.orienGraph.add_data_to_channel(2, orientation.z)
        self.orienGraph.add_data_to_channel(3, orientation.w)

    def newEmgData(self, event):
        data = event["data"]
        emg = data["emg"]
        for i in range(8):
            self.emgGrapgs[i].add_data_to_channel(0, emg[i])

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.resizeStuff()

    def resizeStuff(self):
        size :QSize = self.size()

        tmp = self.emgGrapgs + [self.gyroGraph, self.orienGraph, self.accGraph]
        tmp.insert(7, self.all_one)

        removed = 0
        for i in range(len(tmp)):
            if tmp[i - removed].isHidden():
                tmp.remove(tmp[i - removed])
                removed = removed + 1

        le = len(tmp)
        if le == 0:
            return
        if le <= 4:
            in_w = max(math.floor(le / 2), 1)
        else:
            in_w = min(le, 3)

        in_h = math.ceil(le / in_w)

        space = 10

        x = space
        y = space
        h = (size.height() - ((in_h + 1) * space)) / in_h
        w = (size.width() - ((in_w + 1) * space)) / in_w

        for i in range(len(tmp)):
            g:QWidget = tmp[i]
            g.setGeometry(x, y, w, h)
            if (i + 1) % in_w == 0:
                x = space
                y = y + h + space
            else:
                x = x + space + w