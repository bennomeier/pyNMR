# import sys
import numpy as np
from PyQt5 import QtWidgets as qtw
# from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from pynmr.model.operations import SetPPMScale as sppm, FourierTransform as FT
# from pynmr.model.region import RegionStack, RegionSet
# from functools import partial
#from pynmr.viewer.nmrView import NmrViewWidget

class RegionViewWidget(qtw.QFrame):
    """A widget to display and manage NMR regions."""
    # Signals for region management
    regionsUpdated = qtc.pyqtSignal(list)  # New region list for display
    activeRegionSetChanged = qtc.pyqtSignal(str)  # Active region set name changed
    regionDisplayToggled = qtc.pyqtSignal(bool)  # Show/hide regions
    
    # Legacy signal (to be removed)
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
        self.RegionDomain = None
        if hasattr(self.parent, 'domainBox'):
            self.DomainNMRView = (self.parent.domainBox.currentText())
        self.rStack = self.model.dataSets[dataSetIndex].regionStack 

        self.initUI()

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
        self.scaleSelBox.currentTextChanged.connect(self.DomainRegionViewChangeUpdate)
        groupBoxLayout.addWidget(self.scaleSelBox)

        self.tableWidget = qtw.QTableWidget(itemChanged=self.updateRegionSet)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 100)
        self.tableWidget.setDisabled(True)
        self.tableWidget.setSizePolicy(qtw.QSizePolicy.MinimumExpanding, qtw.QSizePolicy.MinimumExpanding)
        groupBoxLayout.addWidget(self.tableWidget)

        self.showRegionCheckBox = qtw.QCheckBox("Show RegionSet", self, stateChanged=self.ChangeShowRegion)
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
                self.rStack.add(name, scale=self.scaleSelBox.currentText(), regions=[])  
                self.activeRegion = name
                self.tableWidget.clearContents()
                self.updateRegionSet()
                self.scaleSelBox.setCurrentText(self.rStack[name].scale)
                self.redraw()
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
                    i1 = qtw.QTableWidgetItem(str(np.round(r[0], 1)))
                    i2 = qtw.QTableWidgetItem(str(np.round(r[1], 1)))
                    self.tableWidget.setItem(index, 0, i1)
                    self.tableWidget.setItem(index, 1, i2)
                self.activeRegion = aktiveregion
            self.reload = False

    def updateRegionSet(self):

        """Aktualisiere die Regionen in der aktiven Region."""
        print("Update")
        if not self.activeRegion and self.reload != True:
            
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
        
        if self.DomainNMRView == "Time.Points" or self.DomainNMRView == "Time.Time":
            try:
                self.showRegionCheckBox.setDisabled(True)
                self.showRegionCheckBox.setChecked(False)
            except:
                return
            
            regions = []
        # Emit signal with new regions
        if self.showRegionCheckBox.isChecked():
            self.regionsUpdated.emit(regions)

    def ChangeShowRegion(self):
        """Toggle the display of regions."""
        if self.DomainNMRView == "Time.Points" or self.DomainNMRView == "Time.Time":
            try: 
                self.showRegionCheckBox.setDisabled(True)
                self.showRegionCheckBox.setChecked(False)
                self.regionDisplayToggled.emit(False)
            except:
                return
            return
        if self.showRegionCheckBox.isChecked():
            self.regionDisplayToggled.emit(True)
            self.updateRegionSet()
        else:
            self.regionDisplayToggled.emit(False)

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
                    self.regionDisplayToggled.emit(False)
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
            self.activeRegionSetChanged.emit(name)
            if self.activeRegion:
                regions = self.rStack[self.activeRegion].regions
                self.regionsUpdated.emit(regions)

    def redraw(self):
        """Redraw the UI to reflect the current state of the RegionStack."""
        self.regionSelBox.clear()
        self.regionSelBox.addItems(sorted(self.rStack.regionSets.keys()))
        if self.activeRegion:
            self.showRegionCheckBox.setDisabled(False)
        self.scaleSelBox.setDisabled(False)
        self.tableWidget.setDisabled(False)
        
    def updateFromDataWidget(self, regions):
        """Update regions from data widget changes"""
        if self.activeRegion and not self.reload:
            self.reload = True
            self.rStack[self.activeRegion].regions = regions
            self.reloadRegions()
            self.reload = False
    
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
        regions = self.rStack[RSname].regions
        self.regionsUpdated.emit(regions)

        self.redraw()

    def DomainNMRViewChangeUpdate(self):
        """Update regions based on domain change."""
        self.DomainNMRView = (self.parent.domainBox.currentText())
        #self.updateRegionSet()
        

    def DomainRegionViewChangeUpdate(self):
        """Update the scale of the active region set."""
        new_scale = self.scaleSelBox.currentText()
        
        if self.activeRegion and not self.reload:
            old_scale = self.rStack[self.activeRegion].scale
            regions = self.rStack[self.activeRegion].regions.copy()
            
            print(f"DomainRegionViewChangeUpdate: old_scale={old_scale}, new_scale={new_scale}")
            print(f"Original regions: {regions}")
            
            #Convert regions based on new scale:
            if old_scale == new_scale:
                print("No conversion needed")
                return
                
            self.reload = True
            print(f"Converting from {old_scale} to {new_scale}")
            regions_converted = []
            
            try:
                xp = self.model.dataSets[self.dataSetIndex].data.ppmScale
                xf = self.model.dataSets[self.dataSetIndex].data.frequency
                print(f"ppmScale range: {xp.min():.2f} to {xp.max():.2f}")
                print(f"frequency range: {xf.min():.2f} to {xf.max():.2f}")
            except:
                data = self.model.dataSets[self.dataSetIndex].data
                FoTr = FT()
                FoTr.run(data)
                setPPM = sppm()
                setPPM.run(data)
                xp = data.ppmScale
                xf = data.frequency
            
            if old_scale == "Hz" and new_scale == "ppm":
                # Convert Hz to ppm
                for r in regions:
                    idx_start = np.argmin(np.abs(xf - r[0]))
                    idx_end = np.argmin(np.abs(xf - r[1]))
                    r_converted = [xp[idx_start], xp[idx_end]]
                    print(f"  Hz {r} -> ppm {r_converted} (indices: {idx_start}, {idx_end})")
                    regions_converted.append(r_converted)
                    
            elif old_scale == "ppm" and new_scale == "Hz":
                # Convert ppm to Hz
                for r in regions:
                    idx_start = np.argmin(np.abs(xp - r[0]))
                    idx_end = np.argmin(np.abs(xp - r[1]))
                    r_converted = [xf[idx_start], xf[idx_end]]
                    print(f"  ppm {r} -> Hz {r_converted} (indices: {idx_start}, {idx_end})")
                    regions_converted.append(r_converted)
            else:
                print("Region Scale Error - unknown conversion")
                self.reload = False
                return
                
            self.rStack[self.activeRegion].scale = new_scale
            self.rStack[self.activeRegion].regions = regions_converted
            self.reloadRegions()
            self.reload = False

            
