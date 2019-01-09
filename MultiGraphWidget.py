from pyqtgraph import PlotWidget, mkPen, AxisItem, LabelItem, PlotDataItem
import numpy as np
import PyQt5.QtCore
from PyQt5.QtCore import *

class MultiGraphWidget(PlotWidget):

    @property
    def max_data_points(self):
        return self._max_data_points

    @max_data_points.setter
    def max_data_points(self, value):
        self._max_data_points = value
        self.setXRange(0, value)

    def __init__(self, parent=None, max_data=50, background="w", y_range=10, y_neg=True, channels=1, colors=["b", "g", "r", (0, 0, 0, 255)], **kargs):
        super().__init__(parent, background=background, **kargs)
        self._max_data_points = max_data
        self.setXRange(0, max_data)
        if y_neg:
            self.setYRange(-y_range, y_range)
        else:
            self.setYRange(0, y_range)

        self.counter = 0

        self.setAntialiasing(False)

        #lbl :LabelItem = self.getPlotItem().titleLabel
        #lbl.size = 30

        #axe:AxisItem = self.getPlotItem().getAxis("bottom")
        #axe.setStyle()
        #axe.showLabel(False)

        self.plots = []
        self.channels = []

        #self.getPlotItem().setLabel("bottom", "")

        self.getPlotItem().layout.setContentsMargins(0, 0, 0, 10)

        for i in range(channels):
            self.channels.append([])
            self.plots.append(self.getPlotItem().plot(pen=mkPen(width=2, color=colors[i])))

        self.getPlotItem().getAxis('bottom').setGrid(255)
        self.getPlotItem().getAxis('bottom').setStyle(showValues = False)
        self.getPlotItem().getAxis('left').setGrid(255)

    def add_data_to_channel_roll(self, channel, y):
        if len(self.channels[channel]) >= self.max_data_points:
            self.channels[channel] = np.roll(self.channels[channel], -1)
            self.channels[channel][-1] = y
        else:
            self.channels[channel].append(y)

        self.plots[channel].setData(self.channels[channel])

    def add_data_to_channel(self, channel, y):
        #if self.counter >= 3000: #TODO: Deleting some data to reduce performance
        #    self.counter = 50
        #    self.channels[channel] = self.channels[channel][-50:]

        #self.counter = self.counter + 1
        self.channels[channel].append(y) #Data is saved here

        if not self.isHidden():
            self.plots[channel].setData(self.channels[channel][-self.max_data_points:])
        #self.plots[channel].plot(y=self.channels[channel], clear=True)

        #self.plots[channel]

    def center(self):
        self.setXRange(0, self._max_data_points)

    def plot_all_data(self):
        channels = len(self.channels)
        for i in range(channels):
            self.plots[i].setData(self.channels[i])

        max = 0
        for i in range(channels):
            if max < len(self.channels[i]):
                max = len(self.channels[i])
        s = max - self._max_data_points
        e = max
        if s <= 0:
            s = 0
            e = self._max_data_points
        self.setXRange(s, e)