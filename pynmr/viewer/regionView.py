import sys
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import pynmr.viewer.operationWidgets as ow
#from pynmr.model import region
from functools import partial

#operationWidgets = {"Left Shift": ow.LeftShiftWidget,
#                    "Exponential Linebroadening": ow.ExponentialLineBroadening,
#                    "Fourier Transform": ow.FourierTransform,
#                    "Phase Zero Order": ow.Phase0D,
#                    "Phase First Order": ow.Phase1D}


class RegionViewWidget(qtw.QFrame):
    """A wdiget to display NMR data"""
    reprocessed = qtc.pyqtSignal()

    # this signal is emitted after Fourier Transform, and should
    # cause the axis to change to the ppm scale
    changeAxis = qtc.pyqtSignal(str)
    pivotPositionSignal = qtc.pyqtSignal(str)
    showPivotSignal = qtc.pyqtSignal(int)

    def __init__(self, model=None, dataSetIndex = 0, parent = None):

        super().__init__()
        
        self.model = model
        self.parent = parent
        self.dataSetIndex = dataSetIndex
        
        
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        groupBox = qtw.QGroupBox("Regions")
        layout.addWidget(groupBox, 1)

        self.rStack = self.model.dataSets[dataSetIndex].regionStack
        
        groupBoxLayout = qtw.QVBoxLayout()
        groupBox.setLayout(groupBoxLayout)

        self.regionSelBox = qtw.QComboBox(self, currentIndexChanged=self.changeActiveRegion)

        self.scaleSelBox = qtw.QComboBox(self)

        groupBoxLayout.addWidget(self.regionSelBox)
        
        for scale in ["Hz", "ppm"]:
            self.scaleSelBox.addItem(scale)

        groupBoxLayout.addWidget(self.scaleSelBox)
        self.scaleSelBox.setDisabled(True)
        # now comes a table widget

        self.tableWidget = qtw.QTableWidget(itemChanged=self.updateRegionSet)
        self.tableWidget.setRowCount(30)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)

        self.tableWidget.setDisabled(True)
        
        groupBoxLayout.addWidget(self.tableWidget)

        self.showRegionCheckBox = qtw.QCheckBox("Show RegionSet", self,
                                                stateChanged=self.updateRegionSet)
        
        self.showRegionCheckBox.setDisabled(True)
        
        groupBoxLayout.addWidget(self.showRegionCheckBox)
        
        buttonLayout = qtw.QHBoxLayout()
        buttonNew = qtw.QPushButton("New", self, clicked=self.newRegionSet)
        buttonDelete = qtw.QPushButton("Delete", self, clicked=self.deleteRegionSet)
        buttonRename = qtw.QPushButton("Rename", self, clicked=self.renameRegionSet)


        for b in [buttonNew, buttonDelete, buttonRename]:
            buttonLayout.addWidget(b)

        groupBoxLayout.addLayout(buttonLayout)

        saveStackButton = qtw.QPushButton("Save Stack", self, clicked=self.saveStack)
        groupBoxLayout.addWidget(saveStackButton)

        self.activeRegion = None

        if len(self.rStack.regionSets.keys()) > 0:
            self.activeRegion = list(self.rStack.regionSets.keys())[0]
        
        self.redraw()
            
        
    def newRegionSet(self):
        name, done1 = qtw.QInputDialog.getText(
             self, 'Region Name', 'Enter Region Name:')

        self.rStack.add(name, scale="ppm", regions=[])

        self.activeRegion = name
        self.scaleSelBox.setCurrentText(self.rStack[name].scale)
        
        self.redraw()

    def changeActiveRegion(self):
        
        self.activeRegion = str(self.regionSelBox.currentText())
        print(self.activeRegion)
        #self.redraw()

    def redraw(self):
        self.regionSelBox.clear()
        
        for rSetKey in sorted(self.rStack.regionSets.keys()):
            self.regionSelBox.addItem(rSetKey)

        # if self.activeRegion is not None and self.activeRegion != self.regionSelBox.currentText():
            #self.regionSelBox.setCurrentText(self.activeRegion)

        self.scaleSelBox.setDisabled(False)
        self.tableWidget.setDisabled(False)
        self.showRegionCheckBox.setDisabled(False)

        # clear tableWidget
        self.tableWidget.clear()

        if self.activeRegion is not None:
            rSet = self.rStack[self.activeRegion].regions
            for row, interval in enumerate(rSet):
                i1 = qtw.QTableWidgetItem()
                i2 = qtw.QTableWidgetItem()
                i1.setText(str(interval[0]))
                i2.setText(str(interval[1]))
                self.tableWidget.setItem(row, 0, i1)
                self.tableWidget.setItem(row, 1, i2)
            

    def updateRegionSet(self):
        # now we need to parse the tableWidget information
        self.rStack[self.activeRegion].regions = []
        for line in range(self.tableWidget.rowCount()):
            try:
                self.rStack[self.activeRegion].regions.append(
                    [float(self.tableWidget.item(line,0).text()),
                     float(self.tableWidget.item(line,1).text())])
            except:
                break

        print(self.rStack[self.activeRegion].regions)

        if self.showRegionCheckBox.isChecked():
            self.parent.dataWidget.updateRegions(self)
                     
    def saveStack(self):
        fileName = self.model.dataSets[self.dataSetIndex].data.path + "pynmrRegionStack1.dill"

        self.rStack.save(fileName)
    

        
    def deleteRegionSet(self):
        pass

    def renameRegionSet(self):
        pass
