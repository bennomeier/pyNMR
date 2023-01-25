import sys
import numpy as np
import dill
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import pynmr.viewer.operationWidgets as ow
from functools import partial

#operationWidgets = {"Left Shift": ow.LeftShiftWidget,
#                    "Exponential Linebroadening": ow.ExponentialLineBroadening,
#                    "Fourier Transform": ow.FourierTransform,
#                    "Phase Zero Order": ow.Phase0D,
#                    "Phase First Order": ow.Phase1D}


class ProcessorViewWidget(qtw.QFrame):
    """A wdiget to display NMR data"""
    reprocessed = qtc.pyqtSignal()

    # this signal is emitted after Fourier Transform, and should
    # cause the axis to change to the ppm scale
    changeAxis = qtc.pyqtSignal(str)

    # this will set the pivot
    pivotPositionSignal = qtc.pyqtSignal(str)

    pivotPositionChange = qtc.pyqtSignal()
    showPivotSignal = qtc.pyqtSignal(int)

    def __init__(self, model=None, dataSetIndex=0, parent=None):

        super().__init__()
        self.model = model
        self.parent = parent

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.dataSetIndex = dataSetIndex
        pStack = self.model.dataSets[dataSetIndex].processorStack

        self.pWidgets = []
        
        # for every processor add a little frame
        for number, p in enumerate(pStack):
            runFunc = partial(self.runProcessor, p)
            
            pBox = qtw.QGroupBox("Processor {}".format(number + 1))
            layout.addWidget(pBox, 1)

            thisProcessorLayout = qtw.QVBoxLayout()
            pBox.setLayout(thisProcessorLayout)

            # add widgets for operatin
            # widgets that can initate a run of the processor get the run function as
            # an optional keyword argument. If they have it, they will run it,
            # and this function will run the processor within this object.
            for op in p:
                print("name: ", op.name)

                if op.name == "Left Shift":
                    self.pWidgets.append(ow.LeftShiftWidget(op))
                elif op.name == "Exponential Linebroadening":
                    self.pWidgets.append(ow.ExponentialLineBroadening(op))
                elif op.name == "Fourier Transform":
                    self.pWidgets.append(ow.FourierTransform(op))
                elif op.name == "Set PPM Scale":
                    self.pWidgets.append(ow.SetPPMScale(op, parent=self, runFunc = runFunc))
                    print("Emitting change Axis signal.")
                    self.changeAxis.emit("PPM")
                elif op.name == "Phase Zero Order":
                    self.pWidgets.append(ow.PhaseZeroOrder(op, runFunc = runFunc))
                elif op.name == "Phase First Order":
                    self.pWidgets.append(ow.PhaseFirstOrder(op, parent=self, runFunc = runFunc))
                    self.pWidgets[-1].showPivotSignal.connect(self.showPivotSignal)
                    self.pWidgets[-1].pivotPositionSignal.connect(self.pivotPositionSignal)
                    self.parent.dataWidget.pivotChanged.connect(self.pWidgets[-1].updatePivotPosition)
                
                
                thisProcessorLayout.addWidget(self.pWidgets[-1])
                    
            runButton = qtw.QPushButton("Process (P)", self,
                                        shortcut=qtg.QKeySequence("P"),
                                        clicked=partial(self.runProcessor, p))

            saveParametersButton = qtw.QPushButton("Save Processor", self,
                                             clicked=self.saveProcessor)

            saveSpectrumButton = qtw.QPushButton("Save Data", self, clicked=self.saveData)

            thisProcessorLayout.addWidget(runButton)
            thisProcessorLayout.addWidget(saveParametersButton)
            thisProcessorLayout.addWidget(saveSpectrumButton)
            
    def saveProcessor(self):
        # for now we save processor 1 of this widgets dataset.
        pathToProcessorFile = self.model.dataSets[self.dataSetIndex].data.path + "pynmrProcessor1.pickle"
        dill.dump(self.model.dataSets[self.dataSetIndex].processorStack[0],
                  file = open(pathToProcessorFile, "wb"))
        

    def saveData(self):
        self.model.dataSets[self.dataSetIndex].data.saveAscii()
            
    def test(self):
        print("HI")

    def runProcessor(self, processor):
        processor.runStack(self.model.dataSets[self.dataSetIndex].data)
        self.reprocessed.emit()
        self.changeAxis.emit("PPM")

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_P:
            print("F5 pressed. Run processor.")
            self.model.dataSets[0].processorStack[0].runStack(
                self.model.dataSets[self.dataSetIndex])

    #def pivotPositionChange(self):
    #    p = self.parent.dataWidget.pPivot.value()
    #    print("Hello", p)
