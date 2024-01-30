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

from pynmr.viewer.nmrView import NmrViewWidget
from pynmr.viewer.processorView import ProcessorViewWidget

from pynmr.model.parser import topSpin
from pynmr.model.model import pyNmrDataSet, pyNmrDataModel

# the modules below are used only for processing of examples.
# Make sure not to violate the Model View pattern.

import pynmr.model.processor as PROC
import pynmr.model.operations as OPS

class MainWindow(qtw.QMainWindow):

    def __init__(self, model=None):
        super().__init__()

        self.model = model

        self.width=400
        self.height = 400
        self.setWindowTitle("pyNMR")
        
        self.statusBar().showMessage("Welcome to pyNMR")

        menubar = self.menuBar()        

        # break macOS menubar handling
        # self.menuBar().setNativeMenuBar(False)

        file_menu = menubar.addMenu("File")
        op_menu = menubar.addMenu("Operations")
        region_menu = menubar.addMenu("Regions")
        analysis_menu = menubar.addMenu("Analysis")

        open_action = file_menu.addAction("Open", self.open)
        save_action = file_menu.addAction("Save")
        openSSH_action = file_menu.addAction("Open via SSH")
        quit_action = file_menu.addAction("Quit", self.destroy)

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
        TBviewerNavigation.setAllowedAreas(
            qtc.Qt.TopToolBarArea |
            qtc.Qt.BottomToolBarArea
        )

        mainLayout = qtw.QHBoxLayout()
        # self.setLayout(mainLayout)

        if model is not None:
            self.updateView()

        self.show()

    def updateView(self):
        widgetAll = qtw.QWidget()
        widgetAllLayout = qtw.QHBoxLayout()
        widgetAll.setLayout(widgetAllLayout)

        self.dataWidget = NmrViewWidget(model=self.model)

        self.processorWidget = ProcessorViewWidget(model=self.model)

        self.processorWidget.reprocessed.connect(self.dataWidget.update)

        widgetAllLayout.addWidget(self.dataWidget)
        widgetAllLayout.addWidget(self.processorWidget)

        self.setCentralWidget(widgetAll)

        self.show()

    def open(self, exampleData=False):
        if exampleData:
            path = "/Users/benno/Dropbox/Software/pyNMR/examples/data/bruker/INADEQUATE/2/"

        else:
            path = qtw.QFileDialog.getExistingDirectory(self, "Open Experiment", os.path.expanduser('~')) + "/"

            print(path)
            
        data = topSpin.TopSpin(path)

        Processor = PROC.Processor([OPS.LeftShift(data.shiftPoints),
                                        OPS.LineBroadening(0.0),
                                        OPS.FourierTransform(),
                                        OPS.Phase0D(-90),
                                        OPS.Phase1D(data.timeShift,
                                                    unit="time")])
            

        self.model = pyNmrDataModel(dataSet=pyNmrDataSet(data=data,
                                                         processor=Processor))

        self.updateView()  
        
        


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
