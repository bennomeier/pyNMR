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
import datetime
import dill
import time

from functools import partial

from pynmr.viewer.nmrView import NmrViewWidget
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

    def __init__(self, model=None, arg = None):
        super().__init__()

        self.model = model

        self.width=400
        self.height = 400
        self.setWindowTitle("pynmr")

        self.settings = qtc.QSettings('Karlsruhe Institute of Technology', 'pyNMR') # name of company and name of app 

        

        
        menubar = self.menuBar()        

        # break macOS menubar handling
        # self.menuBar().setNativeMenuBar(False)

        file_menu = menubar.addMenu("File")

        op_menu = menubar.addMenu("Operations")
        region_menu = menubar.addMenu("Regions")
        analysis_menu = menubar.addMenu("Analysis")

        

        open_action = file_menu.addAction("Open", self.openAskPath)
        open_action_example = file_menu.addAction("Open Example", self.openExample)

        self.openRecentMenu = file_menu.addMenu("Open Recent")
        
        save_action = file_menu.addAction("Save")
        openSSH_action = file_menu.addAction("Open via SSH")
        quit_action = file_menu.addAction("Quit", self.endProgram)
        quit_action.setShortcut('CTRL+Q')

        self.settings = qtc.QSettings('apps', 'settings')

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
        TBviewerNavigation.addAction("<")
        TBviewerNavigation.addAction(">")

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

        
        self.statusBar().showMessage("Welcome to pynmr")

        
        self.show()

    def endProgram(self):
        sys.exit()

    def updateView(self):
        widgetAll = qtw.QWidget()
        widgetAllLayout = qtw.QHBoxLayout()
        widgetAll.setLayout(widgetAllLayout)

        titleAndProcessorLayout = qtw.QVBoxLayout()

        regionAndAnalysisLayout = qtw.QVBoxLayout()
        
        self.dataWidget = NmrViewWidget(model=self.model)
        
        self.processorWidget = ProcessorViewWidget(model=self.model, parent=self)

        self.regionWidget = RegionViewWidget(model = self.model, parent = self)
        regionAndAnalysisLayout.addWidget(self.regionWidget)

        self.titleWidget = TitleViewWidget(model=self.model)

        titleAndProcessorLayout.addWidget(self.titleWidget)
        titleAndProcessorLayout.addWidget(self.processorWidget)
        
        widgetAllLayout.addWidget(self.dataWidget)
        widgetAllLayout.addLayout(titleAndProcessorLayout)
        widgetAllLayout.addLayout(regionAndAnalysisLayout)

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
        self.processorWidget.changeAxis.connect(self.dataWidget.changeAxis)
        self.processorWidget.reprocessed.connect(self.dataWidget.reprocessed)
        self.processorWidget.pivotPositionSignal.connect(self.dataWidget.pivotPositionSignal)
        self.processorWidget.showPivotSignal.connect(self.dataWidget.showPivotSignal)

        self.dataWidget.pivotChanged.connect(self.processorWidget.pivotPositionChange)
        
        self.show()

    def report(self, arg):
        print("Report in :", arg)

    def openExample(self):
        path = "/Users/benno/Dropbox/Software/pyNMR/examples/data/bruker/INADEQUATE/2/"
        self.openByPath(path)

    def openAskPath(self):
        path = qtw.QFileDialog.getExistingDirectory(self, "Open Experiment", os.path.expanduser('~')) + "/"

        print(path)
        self.openByPath(path)
        
    def openByPath(self, path):
        data = topSpin.TopSpin(path)

        pathToProcessor = path + "pynmrProcessor1.pickle"

        if os.path.isfile(pathToProcessor):
            print("Parsing Processor from " + pathToProcessor)
            Processor = dill.load(open(pathToProcessor, "rb")) 
        else:
            Processor = PROC.Processor([OPS.LeftShift(data.shiftPoints),
                                        OPS.LineBroadening(0.0),
                                        OPS.FourierTransform(),
                                        OPS.SetPPMScale(),
                                        OPS.Phase0D(0),
                                        OPS.Phase1D(data.timeShift,
                                                    unit="time")])

        pathToRegionStack = path + "pynmrRegionStack1.dill"

        if os.path.isfile(pathToRegionStack):
            print("Parsing RegionStack from " + pathToRegionStack)
            regionStack = dill.load(open(pathToRegionStack, "rb")) 
        else:
            regionStack = REGION.RegionStack()
        
            

        self.model = pyNmrDataModel(dataSet=pyNmrDataSet(data=data,
                                                         processor=Processor,
                                                         regionStack=regionStack))

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

    def populateOpenRecent(self, openString = ""):
        # Step 1. Remove the old options from the menu
        self.openRecentMenu.clear()
        # Step 2. Dynamically create the actions
        actions = []
        if self.settings.contains("recentFilesList"):
            filenames = self.settings.value("recentFilesList")
        else:
            filenames = []

        for filename in filenames[::-1]:
            action = qtg.QAction(filename, self)
            action.triggered.connect(partial(self.openByPath, filename))
            actions.append(action)
        # Step 3. Add the actions to the menu
        self.openRecentMenu.addActions(actions)

        if len(openString) > 0:
            try:
                self.openByPath(filenames[int(openString)])
            except:
                print("Could not open file specified by ", openString)

    def closeEvent(self, e):
        # Write window size and position to config file
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    mw = MainWindow(arg = sys.argv)
    sys.exit(app.exec())
