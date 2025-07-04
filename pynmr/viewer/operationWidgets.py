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

class BaselineCorrectionWidget(qtw.QWidget):
    def __init__(self, operation,model,dataSetIndex,parent=None):
        super().__init__()
        self.operation = operation
        self.model = model
        self.parent = parent
        self.dataSetIndex = dataSetIndex
        self.activeBaselineRegion = None

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        box = qtw.QGroupBox("Baseline Correction")
        layout.addWidget(box)

        mainLayout = qtw.QVBoxLayout()
        box.setLayout(mainLayout)

        self.typeCombo = qtw.QComboBox()
        self.typeCombo.addItems(["Polynomial", "Spline", "Median", "Other"])
        self.typeCombo.currentTextChanged.connect(self.updateType)
        mainLayout.addWidget(qtw.QLabel("Correction Type"))
        mainLayout.addWidget(self.typeCombo)

        # Stacked widget for different correction types
        self.stacked = qtw.QStackedWidget()
        mainLayout.addWidget(self.stacked)

        # Polynomial correction page
        polyWidget = qtw.QWidget()
        polyLayout = qtw.QVBoxLayout()
        polyWidget.setLayout(polyLayout)

        # Polynomial Degree
        degreeLayout = qtw.QHBoxLayout()
        degreeLabel = qtw.QLabel("Polynomial Degree")
        self.polyDegreeEntry = qtw.QLineEdit(str(getattr(self.operation, "polyDegree", 1)))
        self.polyDegreeEntry.setValidator(qtg.QIntValidator(1, 20))
        self.polyDegreeEntry.textChanged.connect(self.handlePolyDegreeChange)
        degreeLayout.addWidget(degreeLabel)
        degreeLayout.addWidget(self.polyDegreeEntry)
        polyLayout.addLayout(degreeLayout)

        # RegioSet selection
        regioLayout = qtw.QHBoxLayout()
        regioLabel = qtw.QLabel("RegioSet")
        self.regioCombo = qtw.QComboBox()
        regiostack = self.model.dataSets[self.dataSetIndex].regionStack
        regioset_names = list(regiostack.regionSets.keys()) if hasattr(regiostack, "regionSets") else []
        self.regioCombo.addItems(regioset_names)
        print("regioset_names:", regioset_names)
        self.regioCombo.currentIndexChanged.connect(self.handleRegioSetChange)
        regioLayout.addWidget(regioLabel)
        regioLayout.addWidget(self.regioCombo)
        polyLayout.addLayout(regioLayout)

        # Show Baseline checkbox
        self.showBaselineCheck = qtw.QCheckBox("Show Baseline")
        self.showBaselineCheck.setChecked(getattr(self.operation, "showBaseline", False))
        self.showBaselineCheck.stateChanged.connect(self.handleShowBaselineChange)
        polyLayout.addWidget(self.showBaselineCheck)

        self.stacked.addWidget(polyWidget)

        # Placeholder for Spline
        splineWidget = qtw.QWidget()
        splineLayout = qtw.QHBoxLayout()
        splineWidget.setLayout(splineLayout)
        splineLayout.addWidget(qtw.QLabel("Spline options coming soon"))
        self.stacked.addWidget(splineWidget)

        # Placeholder for Rolling Ball / Rubberband
        rollingBallWidget = qtw.QWidget()
        rollingBallLayout = qtw.QHBoxLayout()
        rollingBallWidget.setLayout(rollingBallLayout)
        rollingBallLayout.addWidget(qtw.QLabel("Rolling Ball / Rubberband options coming soon"))
        self.stacked.addWidget(rollingBallWidget)

        # Placeholder for Wavelet-basiert
        waveletWidget = qtw.QWidget()
        waveletLayout = qtw.QHBoxLayout()
        waveletWidget.setLayout(waveletLayout)
        waveletLayout.addWidget(qtw.QLabel("Wavelet-based options coming soon"))
        self.stacked.addWidget(waveletWidget)

        # Placeholder for Median-/Quantil-basiert
        medianQuantilWidget = qtw.QWidget()
        medianQuantilLayout = qtw.QHBoxLayout()
        medianQuantilWidget.setLayout(medianQuantilLayout)
        medianQuantilLayout.addWidget(qtw.QLabel("Median-/Quantil-based options coming soon"))
        self.stacked.addWidget(medianQuantilWidget)

        # Placeholder for Asymmetrische Least Squares (ALS)
        alsWidget = qtw.QWidget()
        alsLayout = qtw.QHBoxLayout()
        alsWidget.setLayout(alsLayout)
        alsLayout.addWidget(qtw.QLabel("Asymmetric Least Squares (ALS) options coming soon"))
        self.stacked.addWidget(alsWidget)

        # Placeholder for Whittaker 
        whittakerWidget = qtw.QWidget()
        whittakerLayout = qtw.QHBoxLayout()
        whittakerWidget.setLayout(whittakerLayout)
        whittakerLayout.addWidget(qtw.QLabel("Whittaker options coming soon"))
        self.stacked.addWidget(whittakerWidget)

        self.applyButton = qtw.QPushButton("Apply Baseline")
        self.applyButton.setCheckable(True)
        self.applyButton.toggled.connect(self.toggleApply)
        mainLayout.addWidget(self.applyButton)

        self.updateType(self.typeCombo.currentText())

    def updateType(self, text):
        idx = self.typeCombo.currentIndex()
        self.stacked.setCurrentIndex(idx)
        self.operation.correctionType = text

    ##Polynominal Baselinecorrection
    def handleRegioSetChange(self, regioset):
        if len(regioset) >= 2:
            self.parent.dataWidget.baselineRegions = regioset
        else:
            Warning("Ausgewähltes Regioset besitzt zu wenige Regionen")
        

    def handlePolyDegreeChange(self, value):
        if value:
            print("New PolyDegree " +str(value))
            self.parent.dataWidget.polynomialdegree = int(value)
            self.parent.dataWidget.update

    def handleShowBaselineChange(self, state):
        if self.parent.dataWidget.baselineRegions is not None:
            if state:
                print("show Baseline")
                self.parent.dataWidget.baseline = True
                self.parent.dataWidget.updateBaseline()
                self.parent.dataWidget.update()
            else:
                print("dont show Baseline")
                self.parent.dataWidget.baseline = False
                self.parent.dataWidget.update()
    
    def updateRegioStack(self):
        """Update the regioCombo with the latest regionSets from the model."""
        regiostack = self.model.dataSets[self.dataSetIndex].regionStack
        regioset_names = list(regiostack.regionSets.keys()) if hasattr(regiostack, "regionSets") else []
        self.regioCombo.clear()
        self.regioCombo.addItems(regioset_names)
    

    def toggleApply(self, checked):
        print("apply")
