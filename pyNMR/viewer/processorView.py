import sys
import numpy as np
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

import pynmr.viewer.operationWidgets as ow
from functools import partial

operationWidgets = {"Left Shift": ow.LeftShiftWidget,
                    "Exponential Linebroadening": ow.ExponentialLineBroadening,
                    "Fourier Transform": ow.FourierTransform,
                    "Phase Zero Order": ow.Phase0D}


class ProcessorViewWidget(qtw.QFrame):
    """A wdiget to display NMR data"""
    reprocessed = qtc.pyqtSignal()

    def __init__(self, model=None, dataSetIndex=0):

        super().__init__()
        self.model = model

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        self.dataSetIndex = dataSetIndex
        pStack = self.model.dataSets[dataSetIndex].processorStack

        # for every processor add a little frame
        for number, p in enumerate(pStack):
            pBox = qtw.QGroupBox("Processor {}".format(number + 1))
            layout.addWidget(pBox, 1)

            thisProcessorLayout = qtw.QVBoxLayout()
            pBox.setLayout(thisProcessorLayout)

            for op in p[:3]:
                opWidget = operationWidgets[op.name]
                print(type(opWidget))
                thisProcessorLayout.addWidget(opWidget(op))

                if hasattr(opWidget, "reprocess"):
                    print(dir(opWidget.reprocess))
                    opWidget.reprocess.connect(partial(self.runProcessor, p))

            runButton = qtw.QPushButton("Process (P)", self,
                                        shortcut=qtg.QKeySequence("P"),
                                        clicked=partial(self.runProcessor, p))

            thisProcessorLayout.addWidget(runButton)

    def runProcessor(self, processor):
        processor.runStack(self.model.dataSets[self.dataSetIndex].data)
        self.reprocessed.emit()

    def keyPressEvent(self, event):
        if event.key() == qtc.Qt.Key_P:
            print("F5 pressed. Run processor.")
            self.model.dataSets[0].processorStack[0].runStack(
                self.model.dataSets[self.dataSetIndex])
