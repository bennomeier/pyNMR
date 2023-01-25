from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class LeftShiftWidget(qtw.QWidget):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        shiftEntry = qtw.QLineEdit(str(self.operation.shiftPoints))
        shiftEntry.setValidator(qtg.QIntValidator())
        
        groupBoxLayout.addWidget(shiftEntry)
        groupBoxLayout.addWidget(qtw.QLabel("Shift Points"))


class ExponentialLineBroadening(qtw.QWidget):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        entry = qtw.QLineEdit(str(self.operation.lineBroadening))
        entry.setValidator(qtg.QIntValidator())
        entry.textChanged.connect(self.handleChange)

        groupBoxLayout.addWidget(entry)
        groupBoxLayout.addWidget(qtw.QLabel("Broadening (Hz)"))

    def handleChange(self, value):
        self.operation.lineBroadening = float(value)


class FourierTransform(qtw.QWidget):
    def __init__(self, operation):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        groupBoxLayout.addWidget(qtw.QLabel("Fourier Transform"))


class SetPPMScale(qtw.QWidget):
    def __init__(self, operation, parent=None, runFunc=None):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        self.parent = parent
        self.refVal = 0
        
        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        groupBoxLayout = qtw.QHBoxLayout()
        box.setLayout(groupBoxLayout)

        self.entry = qtw.QLineEdit(str(self.operation.shift))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        self.button = qtw.QPushButton("Calib Axis (C)", self,
                                      shortcut = qtg.QKeySequence("C"),
                                      clicked=self.calibAxis)
        
        groupBoxLayout.addWidget(self.entry)
        groupBoxLayout.addWidget(qtw.QLabel("Set PPM Scale"))
        groupBoxLayout.addWidget(self.button)

    def calibAxis(self):
        # this should open a popup where you enter the ppm value of the reference
        # then the position of the pivot is set to this reference value.

        #  https://stackoverflow.com/questions/42534378/c-qt-creator-how-to-have-dot-and-comma-as-decimal-separator-on-a-qdoubles

        shiftValue, ok = qtg.QInputDialog.getDouble(self, "Chemical Shift", "Enter Chemical Shift", decimals=3)

        if ok:
            pivotPosition = self.parent.parent.dataWidget.pPivot.value()
            print("pivotPosition: ", pivotPosition)
            print("shiftValue: ", shiftValue)
            delta = shiftValue - pivotPosition
            self.operation.shift += delta
            self.entry.setText(str(delta))  
            print(position)
        
    def handleChange(self):
        self.operation.shift = float(self.entry.text())
        
class PhaseZeroOrder(qtw.QWidget):
    reprocessWidget = qtc.pyqtSignal()
    reprocessSignal = 1

    def __init__(self, operation, runFunc = None):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        self.runFunc = runFunc

        # the box is a VBoxLayout with a slider and an entry
        groupBoxLayout = qtw.QVBoxLayout()
        box.setLayout(groupBoxLayout)

        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-180)
        self.sl.setMaximum(180)
        self.sl.setValue(self.operation.phase)
        self.sl.valueChanged.connect(self.handleChange)

        self.reprocessSignal = 1

        groupBoxLayout.addWidget(self.sl)
       
        phaseEntryLayout = qtw.QHBoxLayout()

        self.entry = qtw.QLineEdit(str(self.operation.phase))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        phaseEntryLayout.addWidget(self.entry)
        phaseEntryLayout.addWidget(qtw.QLabel("Phase Zero Order"))

        reprocessLayout = qtw.QHBoxLayout()

        self.reproBox = qtw.QCheckBox("Reprocess")

        reprocessLayout.addWidget(self.reproBox)
        
        groupBoxLayout.addLayout(phaseEntryLayout)
        groupBoxLayout.addLayout(reprocessLayout)

    def handleChange(self, value):
        self.operation.phase = float(value)
        self.entry.setText(str(value))
        self.sl.setValue(float(value))

        if self.reproBox.isChecked:
            print("Emitting Reprocessed Signal.")

            if self.runFunc:
                self.runFunc()
            
            self.reprocessWidget.emit()


class PhaseFirstOrder(qtw.QWidget):
    reprocessWidget = qtc.pyqtSignal()
    pivotPositionSignal = qtc.pyqtSignal(str)
    showPivotSignal = qtc.pyqtSignal(int)
    

    def __init__(self, operation, parent=None, runFunc = None):
        super().__init__()
        self.operation = operation
        self.runFunc = runFunc

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        self.parent = parent
        
        groupBoxLayout = qtw.QVBoxLayout()
        box.setLayout(groupBoxLayout)

        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-540)
        self.sl.setMaximum(540)
        self.sl.setValue(self.operation.phase)
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
        self.sl.setValue(float(value))

        if self.reproBox.isChecked:
            print("Emitting Reprocessed Signal.")
            self.reprocessWidget.emit()

            if self.runFunc:
                self.runFunc()
            #self.parent().parent().reprocessed.emit()

    def updatePivotPosition(self):
        # update pivot position text after pivot has been changed.
        self.operation.pivot = self.parent.parent.dataWidget.pPivot.value()
        self.pivot.setText(str(self.operation.pivot))
