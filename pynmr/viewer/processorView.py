# import sys
# import numpy as np
import dill
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import pynmr.viewer.operationWidgets as ow
from functools import partial
# from pynmr.viewer.view_tools.LayoutCollapsibleWidget import FrameLayout as fl


class ProcessorViewWidget(qtw.QFrame):
    """A widget to display NMR data"""
    reprocessed = qtc.pyqtSignal()
    changeAxis = qtc.pyqtSignal(str)
    pivotPositionSignal = qtc.pyqtSignal(str)
    pivotPositionChange = qtc.pyqtSignal()
    showPivotSignal = qtc.pyqtSignal(int)

    def __init__(self, model=None, dataSetIndex=0, parent=None):
        '''
        Initialize the ProcessorViewWidget.
        '''
        
        super().__init__()
        self.model = model
        self.parent = parent
        print("TD1_index in Prozessor: ", self.parent.TD1_index)
        print("Processor Index: ", self.parent.processorIndex)
        
        mainLayout = qtw.QVBoxLayout()
        self.setLayout(mainLayout)


        scrollArea = qtw.QScrollArea()
        scrollArea.setWidgetResizable(True)
        mainLayout.addWidget(scrollArea)

        scrollWidget = qtw.QWidget()
        scrollArea.setWidget(scrollWidget)

        scrollLayout = qtw.QVBoxLayout()
        scrollWidget.setLayout(scrollLayout)

        self.dataSetIndex = dataSetIndex
        pStack = self.model.dataSets[dataSetIndex].processorStack

        self.pWidgets = []

        #for number, p in enumerate(pStack):
        #pnumber = TD1_index
        #print("PNUMBER: ", pnumber)
        
        p = pStack[self.parent.processorIndex]
        runFunc = partial(self.runProcessor, p)
        
        pBox = qtw.QGroupBox(f"Processor {self.parent.processorIndex}")
        scrollLayout.addWidget(pBox, 1)

        thisProcessorLayout = qtw.QVBoxLayout()
        pBox.setLayout(thisProcessorLayout)

        for op in p:
            print("name: ", op.name)

            if op.name == "Left Shift":
                self.pWidgets.append(ow.LeftShiftWidget(op))
            elif op.name == "Exponential Linebroadening":
                self.pWidgets.append(ow.ExponentialLineBroadening(op))
            elif op.name == "Zero Filling":
                self.pWidgets.append(ow.ZeroFilling(op))
            elif op.name == "Fourier Transform":
                self.pWidgets.append(ow.FourierTransform(op))
            elif op.name == "Set PPM Scale":
                self.pWidgets.append(ow.SetPPMScale(op, parent=self, runFunc=runFunc))
                print("Emitting change Axis signal.")
                self.changeAxis.emit("PPM")
            elif op.name == "Phase Zero Order":
                self.pWidgets.append(ow.PhaseZeroOrder(op, runFunc=runFunc))
            elif op.name == "Phase First Order":
                self.pWidgets.append(ow.PhaseFirstOrder(op, parent=self, runFunc=runFunc))
                self.pWidgets[-1].showPivotSignal.connect(self.showPivotSignal)
                self.pWidgets[-1].pivotPositionSignal.connect(self.pivotPositionSignal)
                self.parent.dataWidget.pivotChanged.connect(self.pWidgets[-1].updatePivotPosition)
            
            thisProcessorLayout.addWidget(self.pWidgets[-1])
        
        self.BaselineWidget = ow.BaselineCorrectionWidget(op,model,dataSetIndex,parent=self.parent)
        thisProcessorLayout.addWidget(self.BaselineWidget)

        runButton = qtw.QPushButton("Process (Enter)", self, clicked=partial(self.runProcessor, p))

        saveParametersButton = qtw.QPushButton("Save Processor", self,
                                                clicked=self.saveProcessor)

        saveSpectrumButton = qtw.QPushButton("Save Data", self, clicked=self.saveData)


        

        thisProcessorLayout.addWidget(runButton)
        thisProcessorLayout.addWidget(saveParametersButton)
        thisProcessorLayout.addWidget(saveSpectrumButton)

        thisProcessorLayout.addSpacerItem(qtw.QSpacerItem(0, 0, qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Expanding))

    
    
    
    
    
    def saveProcessor(self):
        self.runProcessor(self.model.dataSets[self.dataSetIndex].processorStack[self.parent.processorIndex])
        self.reprocessed.emit()
        self.changeAxis.emit("PPM")
        pathToProcessorFile = self.model.dataSets[self.dataSetIndex].data.path + "pynmrProcessor.pickle"
        with open(pathToProcessorFile, "wb") as file:
            dill.dump(self.model.dataSets[self.dataSetIndex].processorStack, file)
        print(pathToProcessorFile)
        

    def saveData(self):
        self.model.dataSets[self.dataSetIndex].data.saveAscii()
            


    def runProcessor(self, processor):
        processor.runStack(self.model.dataSets[self.dataSetIndex].data)
        self.reprocessed.emit()
        self.changeAxis.emit("PPM")

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_Enter:
            print("Enter pressed. Run processor.")
            self.model.dataSets[self.dataSetIndex].processorStack[self.parent.TD1_index].runStack(
                self.model.dataSets[self.dataSetIndex])

    #def pivotPositionChange(self):
    #    p = self.parent.dataWidget.pPivot.value()
    #    print("Hello", p)

    def updateProcessor(self, newProcessorStack):
        """Update the processor stack."""

     # Update the values in the widgets
        for widget, operation in zip(self.pWidgets, newProcessorStack):
            if hasattr(widget, 'updateValues'):
                widget.updateValues(operation)
                
            else:
                print(f"Warning: Widget {widget} does not have an updateValues method.")

     # Emit a signal to notify that the processor stack has been updated
        self.reprocessed.emit()
