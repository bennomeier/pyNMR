# import sys
# import numpy as np
from PyQt5 import QtWidgets as qtw
# from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
# from pynmr.model.region import RegionStack, RegionSet
# from functools import partial
#from pynmr.viewer.nmrView import NmrViewWidget

class RegionViewWidget(qtw.QFrame):
    """A widget to display and manage NMR regions."""
    reprocessed = qtc.pyqtSignal()
    deleteRegions = False 


    def __init__(self, model=None, dataSetIndex=0, parent=None):
        super().__init__()
        if model is None:
            raise ValueError("Model cannot be None")
        
        self.model = model
        self.parent = parent
        self.dataSetIndex = dataSetIndex
        self.reload = False

        self.rStack = self.model.dataSets[dataSetIndex].regionStack 

        self.initUI()

        self.parent.processorWidget.BaselineWidget.updateRegioStack()

        self.activeRegion = None
        if len(self.rStack.regionSets.keys()) > 0:
            self.activeRegion = list(self.rStack.regionSets.keys())[0]
        
        self.redraw()

    def initUI(self):
        """Initialize the user interface."""
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        groupBox = qtw.QGroupBox("Regions")
        layout.addWidget(groupBox, 1)

        groupBoxLayout = qtw.QVBoxLayout()
        groupBox.setLayout(groupBoxLayout)

        self.regionSelBox = qtw.QComboBox(self, currentIndexChanged=self.ChooseRegionSet)
        groupBoxLayout.addWidget(self.regionSelBox)

        self.scaleSelBox = qtw.QComboBox(self)
        for scale in ["Hz", "ppm"]:
            self.scaleSelBox.addItem(scale)
        self.scaleSelBox.setDisabled(True)
        groupBoxLayout.addWidget(self.scaleSelBox)

        self.tableWidget = qtw.QTableWidget(itemChanged=self.updateRegionSet)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setDisabled(True)
        self.tableWidget.setSizePolicy(qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding)
        groupBoxLayout.addWidget(self.tableWidget)

        self.showRegionCheckBox = qtw.QCheckBox("Show RegionSet", self, stateChanged=self.updateRegionSet)
        groupBoxLayout.addWidget(self.showRegionCheckBox)
        self.showRegionCheckBox.setDisabled(True)
        buttonLayout = qtw.QHBoxLayout()
        buttonNew = qtw.QPushButton("New", self, clicked=self.newRegionSet)
        buttonDelete = qtw.QPushButton("Delete", self, clicked=self.deleteRegionSet)
        buttonRename = qtw.QPushButton("Rename", self, clicked=self.renameRegionSet)
        for b in [buttonNew, buttonDelete, buttonRename]:
            buttonLayout.addWidget(b)
        groupBoxLayout.addLayout(buttonLayout)

        saveStackButton = qtw.QPushButton("Save Stack", self, clicked=self.saveStack)
        groupBoxLayout.addWidget(saveStackButton)

        groupBoxLayout.addSpacerItem(qtw.QSpacerItem(0, 0, qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Expanding))


    def newRegionSet(self):
        """Erstelle eine neue Region."""
        name, done1 = qtw.QInputDialog.getText(self, 'Region Name', 'Enter Region Name:')
        if done1 and name:
            try:
                self.reload =True
                self.rStack.add(name, scale="ppm", regions=[])  
                self.activeRegion = name
                self.tableWidget.clearContents()
                self.updateRegionSet()
                self.scaleSelBox.setCurrentText(self.rStack[name].scale)
                self.redraw()
                self.parent.processorWidget.BaselineWidget.updateRegioStack()
                self.reload = False
            except Exception as e:
                qtw.QMessageBox.warning(self, "Error", str(e))

    def reloadRegions(self):
        """Redraw the UI to reflect the current state of the RegionStack."""
        if self.activeRegion and self.activeRegion in self.rStack.regionSets:
            self.reload = True
            aktiveregion = self.activeRegion
            #self.tableWidget.clearContents()
            regions = self.rStack[self.activeRegion].regions
            for index, r in enumerate(regions):
                if isinstance(r, (list, tuple)) and len(r) == 2:
                    i1 = qtw.QTableWidgetItem(str(r[0]))
                    i2 = qtw.QTableWidgetItem(str(r[1]))
                    self.tableWidget.setItem(index, 0, i1)
                    self.tableWidget.setItem(index, 1, i2)
                self.activeRegion = aktiveregion
            self.reload = False

    def updateRegionSet(self):

        """Aktualisiere die Regionen in der aktiven Region."""
        print("Update")
        if not self.activeRegion and self.reload != True:
            qtw.QMessageBox.warning(self, "No Active RegionSet", "No active RegionSet to update.")
            return
        
        if self.reload == True:
            return

        regions = []
        for row in range(self.tableWidget.rowCount()):
            try:
                start = float(self.tableWidget.item(row, 0).text())
                end = float(self.tableWidget.item(row, 1).text())
                regions.append([start, end])
            except (ValueError, AttributeError):
                break

        self.rStack[self.activeRegion].regions = regions
        self.parent.processorWidget.BaselineWidget.update
        if self.showRegionCheckBox.isChecked():
            self.parent.dataWidget.updateRegions(self)
        else:
            self.parent.dataWidget.clearRegions()


    def saveStack(self):
        """Speichere die RegionStack in eine Datei."""
        fileName = self.model.dataSets[self.dataSetIndex].data.path + "pynmrRegionStack.dill"
        self.rStack.save(fileName)

    def deleteRegionSet(self):
        """Delete the currently active region set."""
        if self.activeRegion:
            def Box():
                dlg = qtw.QMessageBox()
                dlg.setWindowTitle("Delete")
                dlg.setText("should the File be deleted?")
                dlg.setStandardButtons(qtw.QMessageBox.Yes | qtw.QMessageBox.No)
                dlg.setIcon(qtw.QMessageBox.Question)
                button = dlg.exec()
                if button == qtw.QMessageBox.Yes:
                    self.parent.dataWidget.clearRegions()
                    self.reload =True
                    del self.rStack.regionSets[self.activeRegion]
                    self.activeRegion = None if not self.rStack.regionSets else list(self.rStack.regionSets.keys())[0]
                    self.redraw()
                    self.tableWidget.clearContents()
                    self.deleteRegions = True
                    self.showRegionCheckBox.setCheckState(False)
                    self.showRegionCheckBox.setDisabled(True)
                    self.reload = False
                else:
                    return
            Box()
            #self.saveStack()
        else:
            qtw.QMessageBox.warning(self, "No RegionSet", "No RegionSet selected to delete.")

    def renameRegionSet(self):
        """Rename the currently active region set."""
        if self.activeRegion:
            newName, done1 = qtw.QInputDialog.getText(self, 'Rename RegionSet', 'Enter new name:')
            if done1 and newName:
                if newName in self.rStack.regionSets:
                    qtw.QMessageBox.warning(self, "Error", "A RegionSet with this name already exists.")
                else:
                    self.rStack.regionSets[newName] = self.rStack.regionSets.pop(self.activeRegion)
                    self.activeRegion = newName
                    self.redraw()
        else:
            qtw.QMessageBox.warning(self, "No RegionSet", "No RegionSet selected to rename.")

    def changeActiveRegion(self):
        """Change the active region set."""
        self.activeRegion = str(self.regionSelBox.currentText())
        self.redraw()

    def ChooseRegionSet(self):
        """Choose a region set from the combo box."""
        if self.reload:
            return
        else:
            self.reload = True
            name = self.regionSelBox.currentText()
            self.activeRegion = name
            self.tableWidget.clearContents()
            self.reload = False
            self.reloadRegions()
            self.parent.dataWidget.updateRegions(self)

    def redraw(self):
        """Redraw the UI to reflect the current state of the RegionStack."""
        self.regionSelBox.clear()
        self.regionSelBox.addItems(sorted(self.rStack.regionSets.keys()))
        if self.activeRegion:
            self.showRegionCheckBox.setDisabled(False)
        self.scaleSelBox.setDisabled(False)
        self.tableWidget.setDisabled(False)
    
    def setActiveRegion(self, regionSet):
        """Set the active region set."""
        if regionSet in self.rStack.regionSets:
            self.activeRegion = regionSet
            self.reloadRegions()
            self.showRegionCheckBox.setDisabled(False)

    
    def GetactiveRegion(self):
        """Get the currently active region set."""
        print("Active Region: ", self.activeRegion)
        return self.activeRegion
    
    def addRegion(self,region,regionSet=None):
        """Add a region to the active region set."""
        
        if regionSet is not None:
            if self.activeRegion is None:
                AttributeError("No RegionSet selected to add region.")
                return
            else:
                regionSet = self.activeRegion
        
        RSname = self.activeRegion
        self.rStack[RSname].regions.append(region)
        self.showRegionCheckBox.setChecked(True)
        self.parent.dataWidget.updateRegions(self)

        self.redraw()
