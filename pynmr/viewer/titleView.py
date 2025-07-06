import sys
import numpy as np
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


class TitleViewWidget(qtw.QFrame):
    """A wdiget to display NMR data"""
    reprocessed = qtc.pyqtSignal()

    # this signal is emitted after Fourier Transform, and should
    # cause the axis to change to the ppm scale
    changeAxis = qtc.pyqtSignal(str)
    pivotPositionSignal = qtc.pyqtSignal(str)
    showPivotSignal = qtc.pyqtSignal(int)

    def __init__(self, model=None, dataSetIndex=0):

        super().__init__()
        self.model = model

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        pBox = qtw.QGroupBox("Title")
        pBox.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        layout.addWidget(pBox, 1)

        thisProcessorLayout = qtw.QVBoxLayout()
        pBox.setLayout(thisProcessorLayout)

        textField = qtw.QTextEdit()
        textField.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
        textField.setMinimumHeight(100)
        
        thisProcessorLayout.addWidget(textField)

        textField.setText("\n".join(self.model.dataSets[dataSetIndex].data.title))
        
