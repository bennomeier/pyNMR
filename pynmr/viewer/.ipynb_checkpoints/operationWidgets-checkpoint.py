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


class Phase0D(qtw.QWidget):
    reprocess = qtc.pyqtSignal()

    def __init__(self, operation):
        super().__init__()
        self.operation = operation

        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        box = qtw.QGroupBox(self.operation.name)
        layout.addWidget(box)

        # the box is a VBoxLayout with a slider and an entry
        groupBoxLayout = qtw.QVBoxLayout()
        box.setLayout(groupBoxLayout)

        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-180)
        self.sl.setMaximum(180)
        self.sl.setValue(self.operation.phase)
        self.sl.valueChanged.connect(self.handleChange)

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
            self.reprocess.emit()
