from PyQt5.QtCore import QObject, QThread, QTimer
from MyoManager import MyoManager
from myo._ffi import EventType, Pose, VibrationType
import math

import time

class EventTypeThread(QThread):
    def __init__(self):
        super().__init__()

class DataManager(QObject):
    
    # **DataManager class** to handle the device. I wanted a single ton class so i'm defining a class __SingleTon to do that. Also this variable is going to store the instance of the that class.
    instance = None

    class __SingleTon(QObject):
        
        dim = 100   # Dimension of the n° latest data to store in a vector.
        myo = None  # Variable to store the myo data type.
        handlers :dict = {} # Here i wanted to use this class for everything so i created a dictionary to keep track of all the handlers that were registered.
        collecting = False # Did we started yet?

        @property
        def auto(self):     # The purpose of the 'auto' property is to have a way of limiting the refresh rate in order to mantain the application responding to user events
            return self._auto

        @auto.setter    # setter; here i initialize a few variables
        def auto(self, value):
            self.c = 0  # variable counter
            self.average = []   # array to store timestamps
            self._auto = value

        def __init__(self): # class init method; here i initialize a few variables
            super().__init__()
            self.myo = MyoManager(self.callback)    # instanciate the class MyoManager and register this class as the callback
            self._auto = True   # start with auto mode ON
            self.average = []
            self.c = 0
            for type in EventType:  # loop every possible EventType and initiliaze the dictionary handlers. In this dictionary every EventType is a key
                self.handlers[type] = []

        def startCollectingData(self):  # Start collecting data
            self.collecting = True
            self.myo.connect()  # connect to myo is stopped or not already started
            #self.fps = PyQt5.QtCore.QTimer()


        def stopCollectingData(self):   # Stop collecting data
            if self.collecting:
                self.collecting = False
                self.myo.disconnect()   # disconnect the armband

        def callback(self, dict):  # TODO: probably a bottle neck since we are passing to this every event of myo (montgomery burns's illness >:D)
            if self._auto:  # if auto then try to limit refresh rate
                diff = (time.clock() - dict["timestamp"]) * 100 # calculate the difference between the current timestamp and the last one that we stored in last callback
                if diff < 4.5:  # 4.5 is an hard-coded value to avoid collecting 'spikes'
                    if len(self.average) <= self.dim:   # NOTE: the vector 'average' here is used a circular vector
                        self.average.append(diff)
                    else:
                        self.average[self.c] = diff
                        self.c = self.c + 1
                        if self.c == self.dim:
                            self.c = 0
                    ave = sum(self.average) / len(self.average) # calculate the average response time
                    self.myo.refresh_rate = max(int(300 * ave), 0)  # set the appropriate refresh rate
            if self.collecting:
                for handler in self.handlers[dict["type"]]:
                    handler(dict)   # if started inform every handlers that we have new data available
            else:
                if dict["type"] != EventType.orientation and dict["type"] != EventType.emg:
                    for handler in self.handlers[dict["type"]]:
                        handler(dict)   # send to handlers new data when we are not listening yet (like a disconnection)

        def add_event_handler(self, type, handler): # method to add an handler
            if not handler in self.handlers[type]:
                self.handlers[type].append(handler)

        def remove_event_handler(self, type, handler): # method to remove an handler
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
            DataManager.instance = DataManager.__SingleTon()    #instanciate our Single Ton class

    def __getattr__(self, item):
        return getattr(self.instance, item)  # redirect everything to the single ton instance

    def __setattr__(self, key, value):
        setattr(self.instance, key, value)  # redirect everything to the single ton instance

    def __str__(self):
        return self.instance.__str__()  # redirect everything to the single ton instance
