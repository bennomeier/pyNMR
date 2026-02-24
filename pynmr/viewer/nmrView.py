# import sys
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import QAction, QApplication, QLabel, QMainWindow, QMenu
# import os
# import dill
#from pynmr.viewer import regionView
# from pynmr.model.region import RegionStack
import pynmr.model.operations as O
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
    """A widget to display NMR data"""
    # Outgoing signals - data changes
    pivotPositionChanged = qtc.pyqtSignal(float)  # New pivot position
    regionsChanged = qtc.pyqtSignal(list)  # New region list
    regionAddRequested = qtc.pyqtSignal(list)  # Request to add a new region
    
    # Incoming signals - display updates needed
    reprocessingRequested = qtc.pyqtSignal()  # Request spectrum reprocessing
    
    # Legacy signals (to be removed gradually)
    pivotChanged = qtc.pyqtSignal()
    regionChanged = qtc.pyqtSignal()
    
    def __init__(self, parent, model=None, dataSetIndex=0):

        super().__init__()
        self.pw = pg.PlotWidget(name="plot1")

        self.dataSetIndex = dataSetIndex
        self.procIndex = -1
        self.representation = "Time.Points"
        self.parent = parent

        self.parent.viewParametersChanged.connect(self.update)

        self.baseline = False
        self.Bslgraph = None
        self.Graphdata = None
        self.applybaleline = False
        self.polynomialdegree = 0
        self.baselineRegions = []

        self.domain = None
        self.pivotPosition = 0
        self.showPivot = False

        self.showRegions = False

        # this is a plot data item
        self.p1 = self.pw.plot()
        self.p1.setPen((20, 20, 200))

        self.p2 = self.pw.plot()
        self.p2.setPen((200, 20, 200))

        self.p3 = self.pw.plot()
        self.p3.setPen((20, 200, 20))


        self.xLabel = "Time"
        self.xUnit = "s"
        self.pw.setXRange(0, 2)
        
        self.pPivot = pg.InfiniteLine(angle=90, movable=True)
        self.pPivot.setPen((200, 20, 20))

        self.pPivot.sigPositionChangeFinished.connect(self.onPivotMoved)
        
        self.pw.addItem(self.pPivot)
        
        self.y, self.x = rand(10000)
        self.data = []
        self.updatePW()

        layout = qtw.QVBoxLayout()

        self.setLayout(layout)

        layout.addWidget(self.pw)
   
        self.model = model

        self.regionPlotItems = []

        
        if model is not None and len(model.dataSets) > 0:
            self.update()
            self.pw.autoRange()
        

    
    
    def onPivotMoved(self):
        """Called when pivot is moved graphically - emit signal with new position"""
        new_position = self.pPivot.value()
        self.pivotPositionChanged.emit(new_position)
        self.pivotChanged.emit()  # Legacy signal
    
    def showPivotSignal(self, show):
        print("Setting Pivot to " + str(show))
        self.showPivot = show
        self.updatePW()
        
    def toggleRegionDisplay(self, show):
        """Legacy method - use updateRegionDisplay instead"""
        if show:
            self.showRegions = True
        if not show:
            self.showRegions = False
            self.clearRegions()
    
    def toggleBaselineDisplay(self, show):
        """Show or hide baseline display"""
        self.baseline = show
        if show:
            self.updateBaseline()
            pass
        else:
            self.removeBaseline()
            
    def toggleBaselineApplication(self, apply):
        """Apply or remove baseline correction to spectrum"""
        self.applybaleline = apply
        self.update()  # Redraw spectrum
    
    def plotBaseline(self, datax, datay):
        if self.Bslgraph is not None:
            self.pw.removeItem(self.Bslgraph)
        self.Bslgraph = pg.PlotDataItem(datax,datay, pen=(100, 100, 100))
        self.pw.addItem(self.Bslgraph)

    def removeBaseline(self):
        if self.Bslgraph is not None:
            self.pw.removeItem(self.Bslgraph)       

    def updateBaselinePlot(self, xdata, ydata, baseline_func):
        """Update the baseline plot with new data"""
        if self.baseline:
            self.plotBaseline(xdata, ydata)
            self.Graphdata = baseline_func
        else:
            self.removeBaseline()

    # def updateBaseline(self):
    #     """Update the baseline plot if baseline fitting is enabled."""
    #     if self.polynomialdegree is not None:
    #         return
    #         # Bsln = O.BaselineFitFunction(self.polynomialdegree)

    #         # if self.domain == "Frequency.Hz":
    #         #     xdata = self.model.dataSets[self.dataSetIndex].data.frequency
    #         # elif self.domain == "Frequency.ppm":
    #         #     xdata = self.model.dataSets[self.dataSetIndex].data.ppmScale
    #         # else:
    #         #     xdata = np.arange(len(self.data))

    #         # xdata = xdata[:len(self.data)]
    #         # min_x = np.min(xdata)
    #         # max_x = np.max(xdata)
    #         # regions = self.baselineRegions
    #         # print("Regions: "+str(regions))
    #         # mask = np.zeros_like(xdata, dtype=bool)
    #         # for region in regions:
    #         #     start, end = sorted(region)
    #         #     mask |= (xdata >= max(start, min_x)) & (xdata <= min(end, max_x))
    #         # xdata_masked = xdata[mask]
    #         # y_masked = self.data[mask]
    #         # self.Graphdata = Bsln.run(xdata_masked, y_masked)
    #         # ydata = self.Graphdata(xdata)
    #         # ydata = np.real(ydata)
    #     #if self.baseline:
    #         #self.plotBaseline(xdata, ydata)
    #     else:
    #         self.removeBaseline()

    def updateBaseline(self):
        if self.polynomialdegree is not None:
            if hasattr(self.parent, 'processorWidget') and hasattr(self.parent.processorWidget, 'baselineWidget'):
                self.parent.processorWidget.baselineWidget.calculateAndEmitBaseline()
                return
            return
        self.removeBaseline()

    def pivotPositionSignal(self, val):
        print("Updating pivot position to {}".format(val))
        
        self.pivotPosition = float(val)
        self.updatePW()

    def regionPositionrewriteobject(self,RegionSet,Region,newval):
        r = []
        r.append(newval[0])
        r.append(newval[1])
        RegionSet.regions[Region] = r
        print (str(RegionSet.regions))

        # regionWindow = regionView.RegionViewWidget()
        # regionWindow.redraw()
            
    def updateRegionDisplay(self, regions):
        """Update the visual display of regions from region widget"""
        print("Updating Regions to " + str(regions))
        if self.showRegions:
            self.clearRegions()
            for index, region in enumerate(regions):
                if isinstance(region, (list, tuple)) and len(region) == 2:
                    item = pg.LinearRegionItem(values=(region[0], region[1]))
                    item.sigRegionChangeFinished.connect(
                        lambda _, idx=index, itm=item: self.onRegionMoved(idx, itm.getRegion())
                    )
                    self.regionPlotItems.append(item)
                    self.pw.addItem(item)
                
    def onRegionMoved(self, index, new_region):
        """Called when a region is moved graphically - emit signal with new regions"""
        # Get all current regions and update the changed one
        all_regions = []
        for i, item in enumerate(self.regionPlotItems):
            if i == index:
                all_regions.append(list(new_region))
            else:
                all_regions.append(list(item.getRegion()))
        self.regionsChanged.emit(all_regions)
        self.regionChanged.emit()  # Legacy signal


    def clearRegions(self):
        for item in self.regionPlotItems:
            self.pw.removeItem(item)
        
        self.regionPlotItems = []
        
    def changeDomain(self, domain):
        print("Change Axis called in nmrView.")
        self.parent.domainBox.setCurrentText(domain)

    def update(self):
        print("NMRView Updating")
        autoScale = False
        self.dataSetIndex = 0
        TD1_index = self.parent.TD1_index

        if  self.parent.domain != self.domain:
            self.domain = self.parent.domain
            autoScale = True


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
        print("TD1_index: ", TD1_index)

        if self.domain is None:
            if hasattr(self.model.dataSets[self.dataSetIndex].data, "ppmScale"):
                domain = "PPM"
                self.domain = "PPM"
                replot  = True
            if len(self.model.dataSets[self.dataSetIndex].data.allSpectra) > 0:
                domain = "FREQUENCY"
            else:
                domain = "TIME"

        if self.baseline:
            self.updateBaseline()

           
        print("Domain: ", self.domain)
        if self.domain == "Time.Points":
            self.y = self.model.dataSets[self.dataSetIndex].data.allFid[self.procIndex][TD1_index]
            self.x = np.arange(len(self.y))
            self.xLabel = "Points"
            self.xUnit = ""
        elif self.domain == "Time.Time":
            self.y = self.model.dataSets[self.dataSetIndex].data.allFid[self.procIndex][TD1_index]
            self.x = self.model.dataSets[self.dataSetIndex].data.fidTime[:len(self.y)]
            self.xLabel = "Time"
            self.xUnit = "s"
        elif self.domain == "Frequency.Hz":
            self.data = self.model.dataSets[self.dataSetIndex].data.allSpectra[self.procIndex][TD1_index]
            self.x = self.model.dataSets[self.dataSetIndex].data.frequency
            if self.applybaleline:
                self.data = self.data - self.Graphdata(self.x)
            self.y = self.data
            self.xLabel = "Frequency"
            self.xUnit = "Hz"
        elif self.domain == "Frequency.ppm":
            self.data = self.model.dataSets[self.dataSetIndex].data.allSpectra[self.procIndex][TD1_index]
            self.x = self.model.dataSets[self.dataSetIndex].data.ppmScale
            if self.applybaleline:
                self.data = self.data - self.Graphdata(self.x)
            self.y = self.data
            self.xLabel = "Chemical Shift"
            self.xUnit = "PPM"


        self.updatePW(replot = autoScale)

        self.pw.setMouseEnabled(x=True, y=True)

        if autoScale:
            print("Rescaling")
            self.pw.autoRange()   

    # when Shift key is pressed, zoom y range as well.
    # for now you have to press shift as well.
    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_X:
            self.pw.setMouseEnabled(y=False)
        if event.key() == qtc.Qt.Key_Y or event.key() == qtc.Qt.Key_Z:
            self.pw.setMouseEnabled(x=False)
        if event.key() == qtc.Qt.Key_A:
            self.pw.autoRange()
        if event.key() == qtc.Qt.Key_R:
            span = 0.1
            mousePos = self.pw.plotItem.vb.mapSceneToView(self.mapFromGlobal(qtg.QCursor.pos()))
            x_pos = mousePos.x()
            region = [x_pos - span, x_pos + span]
            self.regionAddRequested.emit(region)
           
             # Define a small span around the x position
            
        # super(qtw.QDialog, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == qtc.Qt.Key_X:
            self.pw.setMouseEnabled(y=True)
        if event.key() == qtc.Qt.Key_Y or event.key() == qtc.Qt.Key_Z:
            self.pw.setMouseEnabled(x=True)
        # super(qtw.QDialog, self).keyReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == qtc.Qt.LeftButton: 
            print("Double clicked")
            self.pw.autoRange()
        super().mouseDoubleClickEvent(event) 
        
    def updatePW(self, replot = False):
        self.pw.setLabel('bottom', self.xLabel, units=self.xUnit)

        if self.parent.settings.value("showReal", True, type=bool):
            self.p1.setData(y=np.real(self.y), x=self.x)
        else:
            self.p1.setData(y=[], x=[])

        if self.parent.settings.value("showImag", False, type=bool):
            self.p2.setData(y=np.imag(self.y), x=self.x)
        else:
            self.p2.setData(y=[], x=[])

        if self.parent.settings.value("showMagn", False, type=bool):
            self.p3.setData(y=np.abs(self.y), x=self.x)
        else:
            self.p3.setData(y=[], x=[])

        # Show or hide the pivot line based on self.showPivot
        if not self.showPivot:
            self.pw.removeItem(self.pPivot)
        else:
            if self.pPivot not in self.pw.items():
                self.pw.addItem(self.pPivot)
            self.pPivot.setValue(self.pivotPosition)

        if self.domain == "PPM":
            self.p1.getViewBox().invertX(True)

        if replot:
            print("Replotting in PW")
            self.pw.autoRange()


    
    




    
