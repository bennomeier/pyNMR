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
    pivotChanged = qtc.pyqtSignal()
    
    def __init__(self, parent, model=None, dataSetIndex=0):

        super().__init__()
        self.pw = pg.PlotWidget(name="plot1")

        self.dataSetIndex = dataSetIndex
        self.procIndex = -1
        self.representation = "Time.Points"

        self.parent = parent

        self.parent.viewParametersChanged.connect(self.update)
        
        self.domain = None
        self.pivotPosition = 0
        self.showPivot = False

        # this is a plot data item
        self.p1 = self.pw.plot()
        self.p1.setPen((20, 20, 200))


        self.xLabel = "Time"
        self.xUnit = "s"
        self.pw.setXRange(0, 2)
        # pw.setYRange(0, 1e-10)

        #self.pivotLine =
        
        self.pPivot = pg.InfiniteLine(angle=90, movable=True)
        self.pPivot.setPen((200, 20, 20))

        self.pPivot.sigPositionChangeFinished.connect(self.pivotChanged)
        
        self.pw.addItem(self.pPivot)
        
        self.y, self.x = rand(10000)
        self.updatePW()

        layout = qtw.QVBoxLayout()

        self.setLayout(layout)

        layout.addWidget(self.pw)
   
        self.model = model

        self.regionPlotItems = []
        
        if model is not None and len(model.dataSets) > 0:
            self.update()
            self.pw.autoRange()

    def showPivotSignal(self, show):
        print("Setting Pivot to " + str(show))
        self.showPivot = show
        self.updatePW()

    def pivotPositionSignal(self, val):
        print("Updating pivot position to {}".format(val))
        
        self.pivotPosition = float(val)
        self.updatePW()
            

    def changeDomain(self, domain):
        print("Change Axis called in nmrView.")
        self.parent.domainBox.setCurrentText(domain)

    def reprocessed(self):
        self.update()

    def update(self):
        self.dataSetIndex = 0
        self.TD1_index = self.parent.TD1_index
        self.procIndex = self.parent.procIndex
        self.domain = self.parent.domain
        """Update plot.
        Optional keyword arguments:
        domain=None | "TIME" | "FREQUENCY" | "PPM"
        position=-1
        index=0
        dataSetIndex = 0

        If no domain is specified the plot will show
        FREQUENCY domain data at the last position and at index 0.
        """
        print("Datsetindex: ", self.dataSetIndex)
        print("Position: ", self.procIndex)

        replot = False
        
        if self.domain is None:
            if hasattr(self.model.dataSets[self.dataSetIndex].data, "ppmScale"):
                domain = "PPM"
                self.domain = "PPM"
                replot  = True
            if len(self.model.dataSets[self.dataSetIndex].data.allSpectra) > 0:
                domain = "FREQUENCY"
            else:
                domain = "TIME"
            
        print("Domain: ", self.domain)

        if self.domain == "Time.Points":
            self.y = np.real(self.model.dataSets[self.dataSetIndex].data.allFid[self.procIndex][self.TD1_index])
            self.x = np.arange(len(self.y))
            self.xLabel = "Points"
            self.xUnit = ""
        elif self.domain == "Time.Time":
            self.y = np.real(self.model.dataSets[self.dataSetIndex].data.allFid[self.procIndex][self.TD1_index])
            self.x = self.model.dataSets[self.dataSetIndex].data.fidTime[:len(self.y)]
            self.xLabel = "Time"
            self.xUnit = "s"
        elif self.domain == "Frequency.Hz":
            self.y = np.real(self.model.dataSets[self.dataSetIndex].data.allSpectra[self.procIndex][self.TD1_index])
            self.x = self.model.dataSets[self.dataSetIndex].data.frequency
            self.xLabel = "Frequency"
            self.xUnit = "Hz"
        elif self.domain == "Frequency.ppm":
            self.y = np.real(self.model.dataSets[self.dataSetIndex].data.allSpectra[self.procIndex][self.TD1_index])
            self.x = self.model.dataSets[self.dataSetIndex].data.ppmScale
            self.xLabel = "Chemical Shift"
            self.xUnit = "PPM"

        self.updatePW(replot = replot)

        # update the plots viewbox to show all data.
        self.pw.setMouseEnabled(x=True, y=True)

        if replot:
            print("Replotting")
            self.pw.autoRange()

        #self.pw.manualRange()
        

    # when Shift key is pressed, zoom y range as well.
    # for now you have to press shift as well.
    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_X:
            self.pw.setMouseEnabled(y=False)
        if event.key() == qtc.Qt.Key_Y or event.key() == qtc.Qt.Key_Z:
            self.pw.setMouseEnabled(x=False)
        if event.key() == qtc.Qt.Key_A:
            self.pw.autoRange()
        # super(qtw.QDialog, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == qtc.Qt.Key_X:
            self.pw.setMouseEnabled(y=True)
        if event.key() == qtc.Qt.Key_Y or event.key() == qtc.Qt.Key_Z:
            self.pw.setMouseEnabled(x=True)
        # super(qtw.QDialog, self).keyReleaseEvent(event)

        
    def updatePW(self, replot = False):
        self.pw.setLabel('bottom', self.xLabel, units=self.xUnit)

        # self.pw.setXRange(0, 2)
        # pw.setYRange(0, 1e-10)
        self.p1.setData(y=self.y, x=self.x)


        # change this code to draw a proper line, and
        # change it to be shown or not.

        self.pPivot.setValue(self.pivotPosition)

        #if self.showPivot:
        #    self.pPivot.
        #self.pPivot.setData(y=[-1e9,1e10], x=[self.pivotPosition, self.pivotPosition])

        if self.domain == "PPM":
            self.p1.getViewBox().invertX(True)
            

        if replot:
            print("Replotting in PW")
            self.pw.autoRange()
        
    def updateRegions(self, regionView):
        regionSet = regionView.rStack[regionView.activeRegion]
        
        regions = regionSet.regions

        for item in self.regionPlotItems:
            self.pw.removeItem(item)
            
        
        for index, r in enumerate(regions):
            item = pg.LinearRegionItem(values=(r[0], r[1]))
            #item.sigRegionChangeFinished.connect
            self.regionPlotItems.append(item)
            self.pw.addItem(item)

    
