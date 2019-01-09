import myo
from myo import *
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import threading
import LogWindow as lw

class Listener(myo.DeviceListener):
    manager = None

    clock_emg = 0
    clock_orientation = 0

    def __init__(self, m):
        super().__init__();
        self.manager = m;

    def on_connected(self, event:Event):
        self.manager.connecting = False
        self.manager.connected = True
        event.device.stream_emg(True)
        event.device.request_battery_level()
        event.device.request_rssi()
        lw.LogWindow.addToLog("Connected to " + repr(event.device_name) + " with mac address: " + repr(event.mac_address))
        event.device.vibrate(myo.VibrationType.short)
        self.manager.signals.emit({"type": event.type, "data": {"name": event.device_name, "mac_address": event.mac_address, "firmware_version": event.firmware_version}, "timestamp" : time.clock()})

    def on_disconnected(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {"name": event.device_name, "mac_address": event.mac_address, "firmware_version": event.firmware_version}, "timestamp" : time.clock()})
        self.manager.connected = False

    def on_paired(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {"name": event.device_name, "mac_address": event.mac_address, "firmware_version": event.firmware_version}, "timestamp" : time.clock()})

    def on_unpaired(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {"name": event.device_name, "mac_address": event.mac_address, "firmware_version": event.firmware_version}, "timestamp" : time.clock()})
        return False

    def on_orientation(self, event:Event):
        if not self.manager.refresh_rate:
            self.manager.signals.emit({"type": event.type, "data": {"gyroscope": event.gyroscope, "acceleration": event.acceleration, "orientation": event.orientation}, "timestamp" : time.clock()})
        else:
            t = time.clock()
            if (not self.clock_orientation) or (t - self.clock_orientation) >= (self.manager.refresh_rate / 10000):
                self.clock_orientation = t
                self.manager.signals.emit({"type" : event.type, "data" : {"gyroscope" : event.gyroscope, "acceleration" : event.acceleration, "orientation" : event.orientation}, "timestamp" : time.clock()})

    def on_emg(self, event:Event):
        if not self.manager.refresh_rate:
            self.manager.signals.emit({"type": event.type, "data": {"emg": event.emg}, "timestamp" : time.clock()})
        else:
            t = time.clock()
            if (not self.clock_emg) or (t - self.clock_emg) >= (self.manager.refresh_rate / 10000):
                self.clock_emg = t
                self.manager.signals.emit({"type": event.type, "data": {"emg": event.emg}, "timestamp" : time.clock()})

    def on_event(self, event):
        super().on_event(event)
        if self.manager.battery:
            self.manager.battery = False
            event.device.request_battery_level()
        if self.manager.rssi:
            self.manager.rssi = False
            event.device.request_rssi()
        if self.manager.lock:
            self.manager.lock = False
            event.device.lock()
        if self.manager.unlock:
            self.manager.unlock = False
            event.device.unlock()

    def on_battery_level(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {"battery" : event.battery_level}, "timestamp" : time.clock()})

    def on_pose(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {"pose": event.pose}, "timestamp" : time.clock()})

    def on_rssi(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {"rssi": event.rssi}, "timestamp" : time.clock()})

    def on_locked(self, event:Event):
        self.manager.signals.emit({"type": event.type, "data": {}, "timestamp" : time.clock()})

    def on_unlocked(self, event):
        self.manager.signals.emit({"type": event.type, "data": {}, "timestamp" : time.clock()})


class MyoManager(QThread):

    signals = pyqtSignal(dict)
    interval = pyqtSignal(int)
    connecting = False
    connected = False
    timer = None
    stop = False
    rssi = False
    battery = False
    lock = False
    unlock = False

    @property
    def refresh_rate(self):
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        self.interval.emit(value)
        self._refresh_rate = value

    def __init__(self, callback):
        super().__init__()
        self.refresh_rate = 300
        self.signals.connect(callback)
        myo.init() #sdk_path="/Developer/sdk"

    def timed_out(self):
        if (not self.connected) and self.connecting:
            lw.LogWindow.addToLog("Connection timed out!")
            self.disconnect()

    def connect(self):
        if not self.connected and not self.connecting:
            self.connecting = True
            self.stop = False
            QTimer.singleShot(5000, self.timed_out)  # Let's wait for 5 seconds
            lw.LogWindow.addToLog("Trying to connect to Myo (connection will timeout in 5 seconds)")
            self.start()

    def run(self):
        try:
            listener = Listener(self)
            hub = myo.Hub("com.twins.emg")

            while hub.run(listener.on_event, self.refresh_rate):
                if self.stop:
                    self.stop = False
                    break
        except:
            self.connecting = False
            lw.LogWindow.addToLog("An error has occured!")
            lw.LogWindow.addToLog("********END********")

    def disconnect(self):
        if self.connected:
            #hub.shutdown()
            lw.LogWindow.addToLog("Disconnected!")
            self.signals.emit({"type": EventType.disconnected, "data": {}, "timestamp" : time.clock()})
        self.connecting = False
        self.connected = False
        self.stop = True
