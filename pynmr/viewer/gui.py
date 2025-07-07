#!/usr/bin/python
# GUI
# Several usage scenarios
# 1. Standalone - Inspect and Phase Nmr data, define Regions, analyse.
# NMR data, Operation Stacks, Region Stacks, Analysis Steps are carried
# out in the app.

# 2. Interactive - Call from Jupyter Notebook...
# NMR data, Operation Stacks, Region Stacks, Analysis Steps
# are passed to the app, modified, and returned.
#
# To launch from a notebook you have to enable gui event loop
# integration via %gui ,  i.e.
# from pyNMR.viewer import gui as mygui
# %gui qt5
# m = mygui.MainWindow()
# m.show()

import sys
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
# import datetime
import dill
# import time

from functools import partial

from pynmr.viewer.nmrView import NmrViewWidget
from pynmr.viewer.settingsDialog import SettingsDialog
from pynmr.viewer.processorView import ProcessorViewWidget
from pynmr.viewer.titleView import TitleViewWidget
from pynmr.viewer.regionView import RegionViewWidget

from pynmr.model.parser import topSpin
from pynmr.model.model import pyNmrDataSet, pyNmrDataModel

# the modules below are used only for processing of examples.
# Make sure not to violate the Model View pattern.

import pynmr.model.processor as PROC
import pynmr.model.region as REGION
import pynmr.model.operations as OPS

class MainWindow(qtw.QMainWindow):
    viewParametersChanged = qtc.pyqtSignal(int)

    def __init__(self, model=None, arg = None):
        super().__init__()

        self.model = model
        self.TD1Change = False

        self.width=400
        self.height = 400
        self.setWindowTitle("pyNMR")

        self.settings = qtc.QSettings('Karlsruhe Institute of Technology', 'pyNMR') # name of company and name of app 
        #self.settings.clear()
        self.path = None
        self.TD1_index = 0
        self.processorIndex = 0 # which processor is in use
        self.procIndex = -1 # how far to we progress in applying the processor (-1 equals to all the way to the last operation).
        self.domain = "Time.Points"

        #self.settings = qtc.QSettings('apps', 'settings')

        
        menubar = self.menuBar()        

        # break macOS menubar handling
        # self.menuBar().setNativeMenuBar(False)

        file_menu = menubar.addMenu("File")

        op_menu = menubar.addMenu("Operations")
        region_menu = menubar.addMenu("Regions")
        analysis_menu = menubar.addMenu("Analysis")

        

        open_action = file_menu.addAction("Open", self.openAskPath)
        open_action.setShortcut('CTRL+O')


        open_action_example = file_menu.addAction("Open Example", self.openExample)

        self.openRecentMenu = file_menu.addMenu("Open Recent")
        
        save_action = file_menu.addAction("Save")
        openSSH_action = file_menu.addAction("Open via SSH")

        settings_action = file_menu.addAction("Settings", self.settingsDialog)

        quit_action = file_menu.addAction("Quit", self.endProgram)
        quit_action.setShortcut('CTRL+Q')


        server = {"cohn" : "ibg-4-cohn.ibg.kit.edu"}
        self.settings.setValue("server", server)
        # Toolbars
        TBfile = self.addToolBar("File")
        TBfile.addAction(open_action)
        TBfile.addAction(save_action)

        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
        save_icon = self.style().standardIcon(qtw.QStyle.SP_DriveHDIcon)

        open_action.setIcon(open_icon)
        save_action.setIcon(save_icon)
        
        TBfile.setAllowedAreas(
            qtc.Qt.TopToolBarArea
        )

        TBviewerNavigation = self.addToolBar("Viewer Navigation")

        # first have a combo box to set Time Domain, Frequency Domain or Chemical Shift Domain
        self.domainBox = qtw.QComboBox()
        self.domainBox.addItems(["Time.Points", "Time.Time", "Frequency.Hz", "Frequency.ppm"])
        self.domainBox.currentTextChanged.connect(self.setDomain)
        TBviewerNavigation.addWidget(self.domainBox)
        
        # then have a box to set the processing index
        self.procEntry = qtw.QLineEdit(str(self.procIndex), textChanged = self.setProcIndex)
        self.procEntry.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)

        TBviewerNavigation.addWidget(qtw.QLabel("Proc Index: "))
        TBviewerNavigation.addWidget(self.procEntry)

        self.procIndexValidator = qtg.QIntValidator(-1, 10)
        self.procEntry.setValidator(self.procIndexValidator)

        
        # this is for flipping through the fids or spectra
        decrAction = TBviewerNavigation.addAction("<", self.decrTD1_index)
        decrAction.setShortcut('p')

        # now add one that shows the current FID
        self.td1Entry = qtw.QLineEdit("0", textChanged = self.setTD1_index)
        self.td1Entry.setSizePolicy(qtw.QSizePolicy.Maximum, qtw.QSizePolicy.Maximum)
    
        TBviewerNavigation.addWidget(self.td1Entry)

        self.td1Validator = qtg.QIntValidator(0, 1000)
        self.td1Entry.setValidator(self.td1Validator)
        
        incrAction = TBviewerNavigation.addAction(">", self.incrTD1_index)
        incrAction.setShortcut('n')
        
        # find out some toolbar actions here. A switch would be nice.

        TBviewerNavigation.setAllowedAreas(
            qtc.Qt.TopToolBarArea |
            qtc.Qt.BottomToolBarArea
        )

        mainLayout = qtw.QHBoxLayout()
        # self.setLayout(mainLayout)

        if model is not None:
            self.updateView()

        self.resize(self.settings.value("size", qtc.QSize(270, 225)))
        self.move(self.settings.value("pos", qtc.QPoint(50, 50)))


        if len(arg) > 1:
            print(arg)

            if (arg[1][0] == "-" and arg[1][1:].isnumeric) or arg[1].isnumeric():
                self.populateOpenRecent(openString = sys.argv[1])
            else:
                self.populateOpenRecent()
                self.openByPath(arg[1])
        else:
            self.populateOpenRecent()

        # self.statusBar().showMessage("Welcome to pynmr")
        
        self.show()

    def endProgram(self):
        sys.exit()

    def settingsDialog(self):
        dlg = SettingsDialog(self)
        dlg.exec()
        

    def updateView(self):
        oldWidget = self.centralWidget()
        if oldWidget is not None:
            oldWidget.deleteLater()

        widgetAll = qtw.QWidget()
        widgetAllLayout = qtw.QHBoxLayout()
        widgetAll.setLayout(widgetAllLayout)

        titleAndProcessorLayout = qtw.QSplitter(qtc.Qt.Vertical)

        regionAndAnalysisLayout = qtw.QVBoxLayout()
        
        self.dataWidget = NmrViewWidget(self, model=self.model)
        
        self.processorWidget = ProcessorViewWidget(model=self.model, parent=self)

        self.regionWidget = RegionViewWidget(model = self.model, parent = self)
        regionAndAnalysisLayout.addWidget(self.regionWidget)

        self.titleWidget = TitleViewWidget(model=self.model)
    
        titleAndProcessorLayout.addWidget(self.titleWidget)
        titleAndProcessorLayout.addWidget(self.processorWidget)
        
        widgetAllLayout.addWidget(self.dataWidget)
        widgetAllLayout.addWidget(titleAndProcessorLayout)
        widgetAllLayout.addLayout(regionAndAnalysisLayout)

        self.setCentralWidget(widgetAll)


        self.regionWidget.setMinimumSize(150,300)
        self.regionWidget.setMaximumSize(410,2600)

        self.titleWidget.setMinimumSize(300,300)
        self.titleWidget.setMaximumSize(800,2600)

        self.processorWidget.setMinimumSize(300,800)
        self.processorWidget.setMaximumSize(800,2600)

        
        self.regionWidget.setSizePolicy(
            qtw.QSizePolicy.Minimum,
            qtw.QSizePolicy.Minimum
            )

        
        #(self.processorWidget)

        self.setCentralWidget(widgetAll)

        # signals
        self.processorWidget.changeAxis.connect(self.dataWidget.changeDomain)
        self.processorWidget.reprocessed.connect(self.dataWidget.update)
        self.processorWidget.pivotPositionSignal.connect(self.dataWidget.pivotPositionSignal)
        self.processorWidget.showPivotSignal.connect(self.dataWidget.showPivotSignal)

        

        self.dataWidget.regionChanged.connect(self.regionWidget.reprocessed)
        self.dataWidget.regionChanged.connect(self.regionWidget.reloadRegions)
        self.dataWidget.regionChanged.connect(self.processorWidget.BaselineWidget.RegiochangeBaseline)
        
        self.show()


    def report(self, arg):
        print("Report in :", arg)


    def openExample(self):
        path = "/Users/benno/Dropbox/Software/pyNMR/examples/data/bruker/INADEQUATE/2/"
        self.openByPath(path)

    def openAskPath(self):
        path = qtw.QFileDialog.getExistingDirectory(self, "Open Experiment", self.settings.value("openPath", os.path.expanduser('~'))) + "/"

        if path:

            if "/" in path:
                self.settings.setValue("openPath", "/".join(path.split("/")[:-1]))
            elif "\\" in path:
                self.settings.setValue("openPath", "\\".join(path.split("\\")[:-1]))
                                                
        print(path)
        self.path = path
        self.openByPath(path)

    def openinDoc(self, docdata, Processorpath, TD1_index=0):
        data = docdata
        matches = [f for f in os.listdir(Processorpath) if f.startswith("pynmrProcessor")]
        if len(matches) > 0:
            pathToProcessor = os.path.join(Processorpath, "pynmrProcessor.pickle")
            if os.path.isfile(pathToProcessor):
                print("Parsing Processor from " + pathToProcessor)
                Processor = [dill.load(open(pathToProcessor, "rb"))]
            else:
                pathToProcessor = os.path.join(Processorpath, matches[0])
                print("Parsing Processor from " + pathToProcessor)
                Processor = [dill.load(open(pathToProcessor, "rb"))]
        else:
            print("No Processor found. Using default.")
            Processor = [PROC.Processor([
                OPS.LeftShift(data.shiftPoints),
                OPS.LineBroadening(0.0),
                OPS.ZeroFilling(0),
                OPS.LeftShift(0),
                OPS.FourierTransform(),
                OPS.SetPPMScale(),
                OPS.Phase0D(0),
                OPS.Phase1D(data.timeShift, unit="time")
            ])]

        pathToRegionStack = os.path.join(Processorpath, "pynmrRegionStack.dill")

        if os.path.isfile(pathToRegionStack):
            print("Parsing RegionStack from " + pathToRegionStack)
            regionStack = dill.load(open(pathToRegionStack, "rb"))
            print("RegionStack loaded with ", len(regionStack), " regions.")
        else:
            print("No RegionStack found. Using default.")
            regionStack = REGION.RegionStack()

        self.model = pyNmrDataModel(dataSet=pyNmrDataSet(
            data=data,
            processor=None,
            regionStack=regionStack
        ))

        for i in range(len(Processor)):
            self.model.dataSets[0].processorStack.append(Processor[i])
        
        self.model.dataSets[0].processorStack[0].runStack(data)


        self.setWindowTitle("pyNMR - " + Processorpath)
        self.updateView()

        
    def openByPath(self, path,TD1_index = 0):
        self.td1_Index = 0
        self.procIndex = -1
        self.domainBox.setCurrentText("Time.Points")
        self.td1Entry.setText("0")
        data = topSpin.TopSpin(path)
        print("Opening file: ", path)
        matches = [f for f in os.listdir(path) if f.startswith("pynmrProcessor")]
        if len(matches) > 0:
            pathToProcessor = os.path.join(path, f"pynmrProcessor.pickle")
            if os.path.isfile(pathToProcessor):
                print("Parsing Processor from " + pathToProcessor)
                Processor = dill.load(open(pathToProcessor, "rb"))
            else:
                pathToProcessor = matches[0]
                print("Parsing Processor from "+ path + pathToProcessor)
                Processor = dill.load(open(path + pathToProcessor, "rb"))
        else:
            print("No Processor found. Using default.")
            Processor = [PROC.Processor([OPS.LeftShift(data.shiftPoints),
                                        OPS.LineBroadening(0.0),
                                         OPS.ZeroFilling(0),
                                        OPS.FourierTransform(),
                                        OPS.SetPPMScale(),
                                        OPS.Phase0D(0),
                                        OPS.Phase1D(data.timeShift,
                                                    unit="time")])]

        pathToRegionStack = path + "pynmrRegionStack.dill"

        if os.path.isfile(pathToRegionStack):
            print("Parsing RegionStack from " + pathToRegionStack)
            regionStack = dill.load(open(pathToRegionStack, "rb")) 
        else:
            print("No RegionStack found. Using default.")
            regionStack = REGION.RegionStack()

       
        print("Processor loaded with ", str(Processor))


        self.model = pyNmrDataModel(dataSet=pyNmrDataSet(data=data,
                                                             processor=None,
                                                             regionStack=regionStack))

        for i in range(0,len(Processor)):  
            self.model.dataSets[0].processorStack.append(Processor[i])
        

        if self.settings.contains("recentFilesList"):
            files = self.settings.value("recentFilesList")

            files = [f for f in files if f != path]            
            files.append(path)

            if (len(files) > 30):
                files = files[-30:]
            self.settings.setValue("recentFilesList", files)
        else:
            self.settings.setValue("recentFilesList", [path])


        #print(self.settings.value("recentFilesList"))
            
        self.setWindowTitle("pyNMR - " + path)
        self.populateOpenRecent()

        self.updateView()
        self.ProcessortoTD1()

    def populateOpenRecent(self, openString = ""):
        self.openRecentMenu.clear()

        actions = []
        if self.settings.contains("recentFilesList"):
            filenames = self.settings.value("recentFilesList")
        else:
            filenames = []

        for filename in filenames[::-1]:
            action = qtw.QAction(filename, self)
            action.triggered.connect(partial(self.openByPath, filename))
            actions.append(action)

        self.openRecentMenu.addActions(actions)

        if len(openString) > 0:
            try:
                print("Opening by Path")
                self.openByPath(filenames[int(openString)])
            except:
                print("Could not open file specified by ", openString)

    def closeEvent(self, e):
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())


    def incrTD1_index(self):
        if self.TD1_index <  self.model.dataSets[0].data.sizeTD1:
            self.TD1_index += 1
            self.td1Entry.setText(str(self.TD1_index))
            self.viewParametersChanged.emit(1)

    def decrTD1_index(self):
        if self.TD1_index > 0:
            self.TD1_index -= 1
            self.td1Entry.setText(str(self.TD1_index))
            self.viewParametersChanged.emit(1)


    def setTD1_index(self, value):
        v = int(value)
        assert 0 <= v <= self.model.dataSets[0].data.sizeTD1
        self.td1Entry.setText(str(self.TD1_index))
        self.viewParametersChanged.emit(1)

    def setProcIndex(self, value):
        self.procIndex = int(value)
        self.viewParametersChanged.emit(1)


    def setDomain(self):
        self.domain = self.domainBox.currentText()

        if len(self.model.dataSets[0].data.allSpectra) == 0:
            P = self.model.dataSets[0].processorStack[0]
            print(P)
            self.processorWidget.runProcessor(self.model.dataSets[self.processorWidget.dataSetIndex].processorStack[0])
            
        self.viewParametersChanged.emit(1)
    
 #   def ProcessortoTD1(self):
 #       """Update the Processor to the current TD1 index."""
 #       if len(self.model.dataSets[0].processorStack) < self.TD1_index + 1:
 #           print("No Processor defined for TD1 index ", self.TD1_index)
 #           for i in range(self.TD1_index + 1 - len(self.model.dataSets[0].processorStack)):
 #               data = self.model.dataSets[0].data
 #               self.model.dataSets[0].processorStack.append(
 #                   PROC.Processor([
 #                       OPS.LeftShift(data.shiftPoints),
 #                       OPS.LineBroadening(0.0),
 #                       OPS.FourierTransform(),
 #                       OPS.SetPPMScale(),
 #                       OPS.Phase0D(0),
 #                       OPS.Phase1D(data.timeShift, unit="time")
 #                   ])
 #               
 #               )
#
 #       print("Running Processor for TD1 index ", self.TD1_index)
 #       Region = self.regionWidget.GetactiveRegion()
  ##      self.processorWidget = ProcessorViewWidget(model=self.model, parent=self,TD1_index=self.TD1_index)
  #      self.dataWidget = NmrViewWidget(self, model=self.model)
  #      self.updateView()
  #      self.processorWidget.runProcessor(self.model.dataSets[self.processorWidget.dataSetIndex].processorStack[self.TD1_index])
  #      self.processorWidget.reprocessed.emit()
  #      self.processorWidget.changeAxis.emit("PPM")
  #      if Region is not None:
  #         self.regionWidget.setActiveRegion(Region)


        
        
if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    mw = MainWindow(arg = sys.argv)
    sys.exit(app.exec())
