from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class LeftShiftWidget(qtw.QWidget):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation
        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        box = qtw.QGroupBox()
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        self.shiftEntry = qtw.QLineEdit(str(self.operation.shiftPoints))
        self.shiftEntry.setValidator(qtg.QIntValidator())
        self.shiftEntry.textChanged.connect(self.handleChange)

        groupBoxLayout.addWidget(qtw.QLabel("Left Shift"))
        groupBoxLayout.addWidget(self.shiftEntry)
        groupBoxLayout.addWidget(qtw.QLabel("Points"))

    def handleChange(self, value):
        self.operation.shiftPoints = int(value)

    def updateValues(self, operation):
        """Update the widget's text field with the new operation values."""
        self.operation = operation
        self.shiftEntry.setText(str(self.operation.shiftPoints))



class ExponentialLineBroadening(qtw.QWidget):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        box = qtw.QGroupBox()
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        self.entry = qtw.QLineEdit(str(self.operation.lineBroadening))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        groupBoxLayout.addWidget(qtw.QLabel("Exponential Broadening "))
        groupBoxLayout.addWidget(self.entry)
        groupBoxLayout.addWidget(qtw.QLabel("(Hz)"))

    def handleChange(self, value):
        self.operation.lineBroadening = float(value)

    def updateValues(self, operation):
        """Update the widget's text field with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.lineBroadening))



class FourierTransform(qtw.QWidget):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        box = qtw.QGroupBox()
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        groupBoxLayout.addWidget(qtw.QLabel("Fourier Transform"))

    def updateValues(self, operation):
        """No values to update for Fourier Transform."""
        self.operation = operation

class SetPPMScale(qtw.QWidget):
    def __init__(self, operation, parent=None, runFunc=None):
        super().__init__()
        self.operation = operation
        self.parent = parent
        self.refVal = 0

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        box = qtw.QGroupBox()
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        self.entry = qtw.QLineEdit(str(self.operation.shift))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        self.button = qtw.QPushButton("Calib Axis (C)", self,
                                      shortcut=qtg.QKeySequence("C"),
                                      clicked=self.calibAxis)
        
        groupBoxLayout.addWidget(self.entry)
        groupBoxLayout.addWidget(qtw.QLabel("Set PPM Scale"))
        groupBoxLayout.addWidget(self.button)

    def calibAxis(self):
        shiftValue, ok = qtw.QInputDialog.getDouble(self, "Chemical Shift", "Enter Chemical Shift", decimals=3)
        if ok:
            pivotPosition = self.parent.parent.dataWidget.pPivot.value()
            delta = shiftValue - pivotPosition
            self.operation.shift += delta
            self.entry.setText(str(delta)) 
    
    def handleChange(self):
        self.operation.shift = float(self.entry.text())
        
    def updateValues(self, operation):
        """Update the widget's text field with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.shift))

class PhaseZeroOrder(qtw.QWidget):
    reprocessWidget = qtc.pyqtSignal()

    def __init__(self, operation, runFunc=None):
        super().__init__()
        self.operation = operation
        self.runFunc = runFunc

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        box = qtw.QGroupBox()
        layout.addWidget(box)

        groupBoxLayout = qtw.QVBoxLayout()
        box.setLayout(groupBoxLayout)

        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-180)
        self.sl.setMaximum(180)
        self.sl.setValue(int(self.operation.phase))
        self.sl.valueChanged.connect(self.handleChange)

        self.entry = qtw.QLineEdit(str(self.operation.phase)) 
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        groupBoxLayout.addWidget(qtw.QLabel("Phase 0D"))
        groupBoxLayout.addWidget(self.sl)
        groupBoxLayout.addWidget(self.entry)

    def handleChange(self, value):
        while float(value)<-180 or float(value)>180:
            if float(value)<0:
                value = int(value)+ 360
            else:
                value = int(value)- 360
        self.operation.phase = float(value)
        self.entry.setText(str(value))
        if float(value)<0:
            val = int(abs(float(value)))
            self.sl.setValue(-val)
        else:
            self.sl.setValue(int(float(value)))
        if self.runFunc:
            self.runFunc()
        self.reprocessWidget.emit()


    def updateValues(self, operation):
        """Update the widget's text field and slider with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.phase))


class PhaseFirstOrder(qtw.QWidget):
    reprocessWidget = qtc.pyqtSignal()
    pivotPositionSignal = qtc.pyqtSignal(str)
    showPivotSignal = qtc.pyqtSignal(int)
    

    def __init__(self, operation, parent=None, runFunc = None):
        super().__init__()
        self.operation = operation
        if not hasattr(self.operation, "phase"):
            self.operation.phase = 0
        self.runFunc = runFunc

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
        
        box = qtw.QGroupBox()
        layout.addWidget(box)

        self.parent = parent
        
        groupBoxLayout = qtw.QVBoxLayout()
        box.setLayout(groupBoxLayout)

        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-540)
        self.sl.setMaximum(540)
        self.sl.setValue(int(self.operation.phase))
        self.sl.valueChanged.connect(self.handleChange)


        groupBoxLayout.addWidget(self.sl)
       
        phaseEntryLayout = qtw.QHBoxLayout()
        self.entry = qtw.QLineEdit(str(self.operation.phase))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)
        entryLabel = qtw.QLabel("Phase 1D")

        phaseEntryLayout.addWidget(self.entry)
        phaseEntryLayout.addWidget(entryLabel)

        pivotLayout = qtw.QHBoxLayout()
        self.pivot = qtw.QLineEdit(str(self.operation.pivot))
        self.pivot.setValidator(qtg.QDoubleValidator())
        self.pivot.textChanged.connect(self.pivotPositionSignal)
        self.showPivot = qtw.QCheckBox("Show Pivot")

        pivotLayout.addWidget(self.pivot)
        pivotLayout.addWidget(self.showPivot)

        self.showPivot.stateChanged.connect(self.showPivotSignal)
        
        reprocessLayout = qtw.QHBoxLayout()

        self.reproBox = qtw.QCheckBox("Reprocess")

        reprocessLayout.addWidget(self.reproBox)

        groupBoxLayout.addWidget(qtw.QLabel("Phase 1D"))
        groupBoxLayout.addLayout(phaseEntryLayout)
        groupBoxLayout.addLayout(pivotLayout)
        groupBoxLayout.addLayout(reprocessLayout)

        
    def handleChange(self, value):
        self.operation.value = float(value)
        self.operation.pivot = float(self.pivot.text())
        self.operation.unit = "degree"
        self.operation.scale = "ppm"
        self.entry.setText(str(value))
        while float(value)<-540 or float(value)>540:
            if float(value)<0:
                value = int(value)+ 1080
            else:
                value = int(value)- 1080
        self.operation.phase = float(value)
        self.entry.setText(str(value))
        if float(value)<0:
            val = int(abs(float(value)))
            self.sl.setValue(-val)
        else:
            self.sl.setValue(int(float(value)))

        if self.runFunc:
            self.runFunc()
        self.reprocessWidget.emit()

    def updatePivotPosition(self):
        # update pivot position text after pivot has been changed.
        self.operation.pivot = self.parent.parent.dataWidget.pPivot.value()
        self.pivot.setText(str(self.operation.pivot))

    def updateValues(self, operation):
        """Update the widget's text field and slider with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.phase))
        self.sl.setValue(int(self.operation.phase))
        self.pivot.setText(str(self.operation.pivot))
