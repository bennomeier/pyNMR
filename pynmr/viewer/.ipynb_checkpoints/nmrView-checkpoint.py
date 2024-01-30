import sys
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


def rand(n):
    data = np.random.random(n)
    data[int(n*0.1):int(n*0.13)] += .5
    data[int(n*0.18)] += 2
    data[int(n*0.1):int(n*0.13)] *= 5
    data[int(n*0.18)] *= 20
    data *= 1e-12
    return data, np.arange(n, n+len(data)) / float(n)


class NmrViewWidget(qtw.QFrame):
    """A wdiget to display NMR data"""

    def __init__(self, model=None, dataSetIndex=0):

        super().__init__()
        self.pw = pg.PlotWidget(name="plot1")

        self.pivotPosition = 0
        self.showPivot = False

        # this is a plot data item
        self.p1 = self.pw.plot()
        self.p1.setPen((20, 20, 200))

        self.xLabel = "Time"
        self.xUnit = "s"
        self.pw.setXRange(0, 2)
        # pw.setYRange(0, 1e-10)

        self.y, self.x = rand(10000)
        self.updatePW()

        layout = qtw.QVBoxLayout()

        self.setLayout(layout)

        layout.addWidget(self.pw)

        self.model = model

        if model is not None and len(model.dataSets) > 0:
            self.update()

    def update(self, domain=None, position=-1, index=0, dataSetIndex=0):
        """Update plot.
        Optional keyword arguments:
        domain=None | "TIME" | "FREQUENCY" | "CS"
        position=-1
        index=0
        dataSetIndex = 0

        If no domain is specified the plot will show
        FREQUENCY domain data at the last position and at index 0.
        """

        if domain is None:
            if len(self.model.dataSets[dataSetIndex].data.allSpectra) > 0:
                domain = "FREQUENCY"
            else:
                domain = "TIME"
        print("Domain: ", domain)

        if domain == "TIME":
            self.y = np.real(self.model.dataSets[dataSetIndex].data.allFid[position][index])
            self.x = self.model.dataSets[dataSetIndex].data.fidTime
            self.xLabel = "Time"
            self.xUnit = "s"
        elif domain == "FREQUENCY":
            self.y = np.real(self.model.dataSets[dataSetIndex].data.allSpectra[position][index])
            self.x = self.model.dataSets[dataSetIndex].data.frequency
            self.xLabel = "Frequency"
            self.xUnit = "Hz"

        self.updatePW()

        # update the plots viewbox to show all data.
        self.pw.setMouseEnabled(x=True, y=True)
        self.pw.autoRange()

    # when Shift key is pressed, zoom y range as well.
    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_X:
            self.pw.setMouseEnabled(y=False)
        if event.key() == qtc.Qt.Key_Y:
            self.pw.setMouseEnabled(x=False)
        if event.key() == qtc.Qt.Key_A:
            self.pw.autoRange()
        # super(qtw.QDialog, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == qtc.Qt.Key_X:
            self.pw.setMouseEnabled(y=True)
        if event.key() == qtc.Qt.Key_Y:
            self.pw.setMouseEnabled(x=True)
        # super(qtw.QDialog, self).keyReleaseEvent(event)

        
    def updatePW(self):
        self.pw.setLabel('bottom', self.xLabel, units=self.xUnit)

        # self.pw.setXRange(0, 2)
        # pw.setYRange(0, 1e-10)
        self.p1.setData(y=self.y, x=self.x)

        
        

