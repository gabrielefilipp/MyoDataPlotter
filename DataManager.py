from PyQt5.QtCore import QObject, QThread, QTimer
from MyoManager import MyoManager
from myo._ffi import EventType, Pose, VibrationType
import math

import time

class EventTypeThread(QThread):
    def __init__(self):
        super().__init__()

class DataManager(QObject):

    instance = None

    class __SingleTon(QObject):

        dim = 100
        myo = None
        handlers :dict = {}
        collecting = False

        @property
        def auto(self):
            return self._auto

        @auto.setter
        def auto(self, value):
            self.c = 0
            self.average = []
            self._auto = value

        def __init__(self):
            super().__init__()
            self.myo = MyoManager(self.callback)
            self._auto = True
            self.average = []
            self.c = 0
            for type in EventType:
                self.handlers[type] = []

        def startCollectingData(self):
            self.collecting = True
            self.myo.connect()
            #self.fps = PyQt5.QtCore.QTimer()


        def stopCollectingData(self):
            if self.collecting:
                self.collecting = False
                self.myo.disconnect()

        def callback(self, dict):  # TODO: probably a bottle neck since we are passing to this every event of myo (montgomery burns's illness >:D)
            if self._auto:
                diff = (time.clock() - dict["timestamp"]) * 100
                if diff < 4.5:
                    if len(self.average) <= self.dim:
                        self.average.append(diff)
                    else:
                        self.average[self.c] = diff
                        self.c = self.c + 1
                        if self.c == self.dim:
                            self.c = 0
                    ave = sum(self.average) / len(self.average)
                    self.myo.refresh_rate = max(int(300 * ave), 0)
            if self.collecting:
                for handler in self.handlers[dict["type"]]:
                    handler(dict)
            else:
                if dict["type"] != EventType.orientation and dict["type"] != EventType.emg:
                    for handler in self.handlers[dict["type"]]:
                        handler(dict)

        def add_event_handler(self, type, handler):
            if not handler in self.handlers[type]:
                self.handlers[type].append(handler)

        def remove_event_handler(self, type, handler):
            if handler in self.handlers[type]:
                self.handlers[type].remove(handler)

        def request_rssi(self):
            self.myo.rssi = True

        def request_battery(self):
            self.myo.battery = True

        def request_lock(self):
            self.myo.lock = True

        def request_unlock(self):
            self.myo.unlock = True

        def setRefreshRate(self, value):
            self.myo.refresh_rate = value

        def __str__(self):
            return repr(self) + "\n" + repr(self.handlers)

    def __init__(self):
        if not DataManager.instance:
            DataManager.instance = DataManager.__SingleTon()

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        setattr(self.instance, key, value)

    def __str__(self):
        return self.instance.__str__()
