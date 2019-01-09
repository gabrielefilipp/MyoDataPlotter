from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import *
from MultiGraphWidget import MultiGraphWidget
from DataManager import *
from LogWindow import LogWindow

HEIGHT = 450
WIDTH = 450

class InfoWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.data_manager = DataManager()
        self.data_manager.myo.interval.connect(self.interval)

        self.data_manager.add_event_handler(EventType.connected, self.connectionChanged)
        self.data_manager.add_event_handler(EventType.disconnected, self.connectionChanged)
        self.data_manager.add_event_handler(EventType.rssi, self.newRssiData)
        self.data_manager.add_event_handler(EventType.battery_level, self.newBatteryData)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateBattery)
        self.last_battery = -1

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Device Info")
        self.setGeometry(240, 120, WIDTH, HEIGHT)
        self.setFixedSize(QSize(WIDTH, HEIGHT))

        self.rssiGraph = MultiGraphWidget(self, max_data=60, y_range=100, y_neg=False, background="w", channels=1, colors=["r"], title="<b>Bluetooth Level</b>")
        self.rssiGraph.setGeometry(10, 10, WIDTH - 20, 150)

        self.battGraph = MultiGraphWidget(self, max_data=60, y_range=100, y_neg=False, background="w", channels=1, colors=["b"], title="<b>Battery Level</b>")
        self.battGraph.setGeometry(10, 170, WIDTH - 20, 150)

        self.mac_lbl = QLabel(self)
        self.mac_lbl.setText("MAC ADDRESS: ")
        self.mac_lbl.setGeometry(10, 330, WIDTH - 20, 20)

        self.name_lbl = QLabel(self)
        self.name_lbl.setText("NAME: ")
        self.name_lbl.setGeometry(10, 360, WIDTH - 20, 20)

        self.refresh_lbl = QLabel(self)
        self.refresh_lbl.setText("REFRESH: ")
        self.refresh_lbl.setGeometry(170, 360, WIDTH - 20, 20)

        self.lock_btn = QPushButton(self)
        self.lock_btn.setText("LOCK")
        self.lock_btn.setGeometry(10, 390, 100, 60)
        self.lock_btn.clicked.connect(self.data_manager.request_lock)

        self.unlock_btn = QPushButton(self)
        self.unlock_btn.setText("UNLOCK")
        self.unlock_btn.setGeometry(120, 390, 100, 60)
        self.unlock_btn.clicked.connect(self.data_manager.request_unlock)

        self.request_rssi_btn = QPushButton(self)
        self.request_rssi_btn.setText("RSSI")
        self.request_rssi_btn.setGeometry(230, 390, 100, 60)
        self.request_rssi_btn.clicked.connect(self.data_manager.request_rssi)

        self.request_battery_btn = QPushButton(self)
        self.request_battery_btn.setText("BATTERY")
        self.request_battery_btn.setGeometry(340, 390, 100, 60)
        self.request_battery_btn.clicked.connect(self.data_manager.request_battery)

    def show(self):
        super().show()
        #TODO: Update infos

    def interval(self, value):
        self.refresh_lbl.setText("REFRESH: " + repr(value) + "ms")

    def updateBattery(self):
        if self.last_battery != -1:
            self.battGraph.add_data_to_channel(0, self.last_battery)
            self.data_manager.request_rssi()

    def connectionChanged(self, event):
        connected = event["type"] == EventType.connected
        if connected:
            data = event["data"]
            self.timer.start(5000)
            self.name_lbl.setText("NAME: " + repr(data["name"]))
            self.mac_lbl.setText("MAC ADDRESS: " + repr(data["mac_address"]))
        else:
            self.last_battery = -1
            self.timer.stop()
        pass

    def getStrengthFromRssi(self, rssi):
        t = -95
        s = -40
        if t > rssi:
            rssi = t
        if rssi > s:
            rssi = s
        return round(100 * (rssi - t) / (s - t) * 100) / 100

    def newRssiData(self, event):
        if self.isVisible() or 1:
            data = event["data"]
            rssi = data["rssi"]

            self.rssiGraph.add_data_to_channel(0, self.getStrengthFromRssi(rssi))

    def newBatteryData(self, event):
        if self.isVisible() or 1:
            data = event["data"]
            self.last_battery = data["battery"]
            self.battGraph.add_data_to_channel(0, self.last_battery)