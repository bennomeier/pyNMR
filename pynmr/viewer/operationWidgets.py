from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import numpy as np



class CollapsibleWidget(qtw.QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.toggle_button = qtw.QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("""
        QToolButton {
        border: none;
        font-size: 14pt;
        padding: 2px 6px;
        }
        """)
        self.toggle_button.setToolButtonStyle(qtc.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(qtc.Qt.RightArrow)
        self.toggle_button.setIconSize(qtc.QSize(12, 12))
        self.toggle_button.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum)
        self.toggle_button.setMinimumHeight(20)
        self.toggle_button.setMaximumHeight(26)
        self.toggle_button.clicked.connect(self.toggle)

        
        #self.toggle_button = qtw.QToolButton(text=title, checkable=True, checked=False)
        #self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        #self.toggle_button.setToolButtonStyle(qtc.Qt.ToolButtonTextBesideIcon)
        #self.toggle_button.setArrowType(qtc.Qt.RightArrow)
        #self.toggle_button.setIconSize(qtc.Qt.QSize(12, 12))  # Smaller arrow icon
        #self.toggle_button.clicked.connect(self.toggle)

        self.content_area = qtw.QScrollArea()
        self.content_area.setStyleSheet("QScrollArea { background-color: white; }")
        self.content_area.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)
        self.content_area.setFrameShape(qtw.QFrame.NoFrame)

        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)

        # Layout setup
        main_layout = qtw.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)

        self.toggle_animation_duration = 150  # Optional: you can add animation later

        # Widget inside the scroll area
        self.content_widget = qtw.QWidget()
        self.content_layout = qtw.QVBoxLayout(self.content_widget)
        self.content_area.setWidget(self.content_widget)
        self.content_area.setWidgetResizable(True)

    def toggle(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(qtc.Qt.DownArrow if checked else qtc.Qt.RightArrow)

        if checked:
            self.content_area.setMaximumHeight(self.content_widget.sizeHint().height())
        else:
            self.content_area.setMaximumHeight(0)

    def add_layout(self, layout):
        self.content_layout.addLayout(layout)


class LeftShiftWidget(CollapsibleWidget):
    def __init__(self, operation):
        super().__init__(title="Left Shift")
        self.operation = operation
        
        self.shiftEntry = qtw.QLineEdit(str(self.operation.shiftPoints))
        self.shiftEntry.setValidator(qtg.QIntValidator())
        self.shiftEntry.textChanged.connect(self.handleChange)

        groupBoxLayout = qtw.QHBoxLayout()
        groupBoxLayout.addWidget(qtw.QLabel("Left Shift"))
        groupBoxLayout.addWidget(self.shiftEntry)
        groupBoxLayout.addWidget(qtw.QLabel("Points"))
        self.add_layout(groupBoxLayout)

    def handleChange(self, value):
        self.operation.shiftPoints = int(value)

    def updateValues(self, operation):
        """Update the widget's text field with the new operation values."""
        self.operation = operation
        self.shiftEntry.setText(str(self.operation.shiftPoints))



class ExponentialLineBroadening(CollapsibleWidget):
    def __init__(self, operation):
        super().__init__(title="Line Broadening")
        self.operation = operation

        self.entry = qtw.QLineEdit(str(self.operation.lineBroadening))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        groupBoxLayout = qtw.QHBoxLayout()
        groupBoxLayout.addWidget(qtw.QLabel("Exponential Broadening "))
        groupBoxLayout.addWidget(self.entry)
        groupBoxLayout.addWidget(qtw.QLabel("(Hz)"))
        self.add_layout(groupBoxLayout)

    def handleChange(self, value):
        self.operation.lineBroadening = float(value)

    def updateValues(self, operation):
        """Update the widget's text field with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.lineBroadening))


class ZeroFilling(CollapsibleWidget):
    def __init__(self, operation):
        super().__init__(title="Zero Fill")
        self.operation = operation

        self.entry = qtw.QLineEdit(str(self.operation.totalPoints))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        groupBoxLayout = qtw.QHBoxLayout()
        groupBoxLayout.addWidget(qtw.QLabel("Zero Fill "))
        groupBoxLayout.addWidget(self.entry)
        groupBoxLayout.addWidget(qtw.QLabel("(Points)"))
        self.add_layout(groupBoxLayout)

    def handleChange(self, value):
        self.operation.totalPoints = int(value)

    def updateValues(self, operation):
        """Update the widget's text field with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.totalPoints))
        

class FourierTransform(CollapsibleWidget):
    def __init__(self, operation):
        super().__init__(title = "Fourier Transform")
        self.operation = operation

    def updateValues(self, operation):
        """No values to update for Fourier Transform."""
        self.operation = operation

class SetPPMScale(CollapsibleWidget):
    def __init__(self, operation, parent=None, runFunc=None):
        super().__init__(title="Set PPM Scale")
        self.operation = operation
        self.parent = parent
        self.refVal = 0


        self.entry = qtw.QLineEdit(str(self.operation.shift))
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.textChanged.connect(self.handleChange)

        self.button = qtw.QPushButton("Calib Axis (C)", self,
                                      shortcut=qtg.QKeySequence("C"),
                                      clicked=self.calibAxis)

        groupBoxLayout = qtw.QHBoxLayout()        
        groupBoxLayout.addWidget(self.entry)
        groupBoxLayout.addWidget(qtw.QLabel("Set PPM Scale"))
        groupBoxLayout.addWidget(self.button)
        self.add_layout(groupBoxLayout)
        
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

class PhaseZeroOrder(CollapsibleWidget):
    reprocessWidget = qtc.pyqtSignal()

    def __init__(self, operation, runFunc=None):
        super().__init__(title="Phase 0D")
        self.operation = operation
        self.runFunc = runFunc


        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-360)
        self.sl.setMaximum(360)
        self.sl.setValue(int(self.operation.phase*2))
        self.sl.valueChanged.connect(self.handleSliderChange)

        self.sl.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)


        self.entry = qtw.QLineEdit(str(self.operation.phase)) 
        self.entry.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Fixed)

        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.editingFinished.connect(self.handleEntryChange)

        
        groupBoxLayout = qtw.QHBoxLayout()
        #groupBoxLayout.addWidget(qtw.QLabel("Phase 0D"))
        groupBoxLayout.addWidget(self.sl)
        groupBoxLayout.addWidget(self.entry)

        self.add_layout(groupBoxLayout)

    def handleSliderChange(self, value):
        phase = value / 2.0
        while phase < -180 or phase > 180:
            if phase < 0:
                phase = phase + 360
            else:
                phase = phase - 360
        self.operation.phase = float(phase)
        self.entry.blockSignals(True)
        self.entry.setText(str(phase))
        self.entry.blockSignals(False)
        if self.runFunc:
            self.runFunc()
        self.reprocessWidget.emit()

    def handleEntryChange(self):
        try:
            phase = float(self.entry.text())
            while phase < -180 or phase > 180:
                if phase < 0:
                    phase = phase + 360
                else:
                    phase = phase - 360
            self.operation.phase = float(phase)
            self.sl.blockSignals(True)
            self.sl.setValue(int(phase * 2))
            self.sl.blockSignals(False)
            if self.runFunc:  
                self.runFunc()
            self.reprocessWidget.emit()
        except ValueError:
            pass


    def updateValues(self, operation):
        """Update the widget's text field and slider with the new operation values."""
        self.operation = operation
        self.entry.setText(str(self.operation.phase))


class PhaseFirstOrder(CollapsibleWidget):
    reprocessWidget = qtc.pyqtSignal()
    pivotPositionSignal = qtc.pyqtSignal(str)
    showPivotSignal = qtc.pyqtSignal(int)
    

    def __init__(self, operation, parent=None, runFunc = None):
        super().__init__(title = "Phase 1D")
        self.operation = operation
        if not hasattr(self.operation, "phase"):
            self.operation.phase = 0
        self.runFunc = runFunc
        self.Reproces = False

        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        #self.setLayout(layout)
        
        self.parent = parent
        
        phaseLayout = qtw.QHBoxLayout()

        self.sl = qtw.QSlider(qtc.Qt.Horizontal)
        self.sl.setMinimum(-1080)
        self.sl.setMaximum(1080)
        self.sl.setValue(int(self.operation.phase*2))
        self.sl.valueChanged.connect(self.handleSliderChange)

        self.sl.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Fixed)
        self.entry = qtw.QLineEdit(str(self.operation.phase)) 
        self.entry.setSizePolicy(qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Fixed)
        self.entry.setValidator(qtg.QDoubleValidator())
        self.entry.editingFinished.connect(self.handleEntryChange)

        phaseLayout.addWidget(self.sl)
        phaseLayout.addWidget(self.entry)
        
        pivotLayout = qtw.QHBoxLayout()
        self.pivotLabel = qtw.QLabel("Pivot Position")
        self.pivot = qtw.QLineEdit(str(self.operation.pivot))
        self.pivot.setValidator(qtg.QDoubleValidator())
        self.pivot.textChanged.connect(self.pivotPositionSignal)
        self.showPivot = qtw.QCheckBox("Show Pivot")
        self.showPivot.stateChanged.connect(self.showPivotSignal)

        pivotLayout.addWidget(self.pivotLabel)
        pivotLayout.addWidget(self.pivot)
        pivotLayout.addWidget(self.showPivot)

        self.reproBox = qtw.QCheckBox("Reprocess")
        self.reproBox.setChecked(False)
        self.reproBox.stateChanged.connect(self.toggleReprocess)

        mylayout = qtw.QVBoxLayout()
        mylayout.addLayout(phaseLayout)
        mylayout.addLayout(pivotLayout)
        mylayout.addWidget(self.reproBox)
        self.add_layout(mylayout)


        
    def handleSliderChange(self, value):
        phase = value / 2.0
        while phase < -540 or phase > 540:
            if phase < 0:
                phase = phase + 1080
            else:
                phase = phase - 1080
        self.operation.value = float(phase)
        self.operation.pivot = float(self.pivot.text())
        self.operation.unit = "degree"
        self.operation.scale = "ppm"
        self.entry.blockSignals(True)
        self.entry.setText(str(phase))
        self.entry.blockSignals(False)
        if self.Reproces:
            if self.runFunc:
                self.runFunc()  
            self.reprocessWidget.emit()

    def handleEntryChange(self):
        try:
            phase = float(self.entry.text())
            while phase < -540 or phase > 540:
                if phase < 0:
                    phase = phase + 1080
                else:
                    phase = phase - 1080
            self.operation.phase = float(phase)
            self.operation.pivot = float(self.pivot.text())
            self.operation.unit = "degree"
            self.operation.scale = "ppm"
            self.sl.blockSignals(True)
            self.sl.setValue(int(phase * 2))
            self.sl.blockSignals(False)
            if self.Reproces:
                self.runFunc()
            self.reprocessWidget.emit()
        except ValueError:
            pass

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

    def toggleReprocess(self):
        if self.reproBox.isChecked():
            self.Reproces = True
            if self.runFunc:
                self.runFunc()
            self.reprocessWidget.emit()
        else:
            self.Reproces = False

class BaselineCorrectionWidget(CollapsibleWidget):
    # Signals for baseline correction
    baselineParametersChanged = qtc.pyqtSignal()  # Parameters changed, need recalculation
    baselineDisplayToggled = qtc.pyqtSignal(bool)  # Show/hide baseline
    baselineApplyToggled = qtc.pyqtSignal(bool)  # Apply/unapply baseline
    regionsRequested = qtc.pyqtSignal()  # Request current regions from region widget
    baselineCalculated = qtc.pyqtSignal(object, object, object)
    
    def __init__(self, operation, parent=None , runFunc = None):
        super().__init__(title = "Baseline Correction")
        self.operation = operation
        self.runFunc = runFunc
        self.parent = parent
        self.model = self.parent.model
        self.dataSetIndex = self.parent.dataSetIndex
        self.dataWidget = self.parent.parent.dataWidget

        self.activeBaselineRegion = None

        mainLayout = qtw.QVBoxLayout()

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
        self.polyDegreeEntry.textChanged.connect(lambda: self.baselineParametersChanged.emit())
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
        if self.dataWidget.baselineRegions == [] and len(regioset_names) > 0:
            self.activeBaselineRegion = regioset_names[0]
            self.dataWidget.baselineRegions = regiostack.regionSets[regioset_names[0]].regions
            self.regioCombo.setCurrentText(self.activeBaselineRegion)
        self.regioCombo.currentIndexChanged.connect(
            lambda idx: self.handleRegioSetChange(self.regioCombo.itemText(idx))
        )
        self.regioCombo.currentTextChanged.connect(lambda: self.baselineParametersChanged.emit())
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
        self.add_layout(mainLayout)
        

    def updateType(self, text):
        idx = self.typeCombo.currentIndex()
        self.stacked.setCurrentIndex(idx)
        self.operation.correctionType = text

    ##Polynominal Baselinecorrection
    def handleRegioSetChange(self, regioset):
        print("regioset wurde zu"+str(regioset)+" geaendert")
        if len(self.model.dataSets[self.dataSetIndex].regionStack[regioset].regions ) >= 2:
            self.dataWidget.baselineRegions =  self.model.dataSets[self.dataSetIndex].regionStack[regioset].regions
            self.activeBaselineRegion = regioset
            self.dataWidget.update()
        else:
            Warning("Ausgewähltes Regioset besitzt zu wenige Regionen")
        

    def handlePolyDegreeChange(self, value):
        if value and value.isdigit():
            self.dataWidget.polynomialdegree = int(value)
            # Only recalculate if baseline is currently shown
            if hasattr(self, 'showBaselineCheck') and self.showBaselineCheck.isChecked():
                self.calculateAndEmitBaseline()

    def handleShowBaselineChange(self, state):
        """Handle baseline display toggle"""
        show_baseline = bool(state)
        self.baselineDisplayToggled.emit(show_baseline)
        if show_baseline:
            self.calculateAndEmitBaseline()
    
    def updateRegioStack(self):
        """Update the regioCombo with the latest regionSets from the model."""
        regiostack = self.model.dataSets[self.dataSetIndex].regionStack
        regioset_names = list(regiostack.regionSets.keys()) if hasattr(regiostack, "regionSets") else []
        current_text = self.regioCombo.currentText()
        self.regioCombo.clear()
        self.regioCombo.addItems(regioset_names)
        # Restore previous selection if still available
        if current_text in regioset_names:
            self.regioCombo.setCurrentText(current_text)
    
    def handleRegioSetChange(self, regioset_name):
        """Handle RegioSet selection change"""
        if regioset_name and regioset_name in self.model.dataSets[self.dataSetIndex].regionStack.regionSets:
            self.activeBaselineRegion = regioset_name
            regions = self.model.dataSets[self.dataSetIndex].regionStack.regionSets[regioset_name].regions
            self.dataWidget.baselineRegions = regions
            # Only recalculate baseline if it's currently being shown
            if hasattr(self, 'showBaselineCheck') and self.showBaselineCheck.isChecked():
                self.calculateAndEmitBaseline()
                
    def RegiochangeBaseline(self):
        if self.activeBaselineRegion is not None:
            self.dataWidget.baselineRegions = self.model.dataSets[self.dataSetIndex].regionStack[self.activeBaselineRegion].regions
            self.dataWidget.update()

    def toggleApply(self, checked):
        """Handle baseline application toggle"""
        self.baselineApplyToggled.emit(bool(checked))
        
    def updateRegions(self, regions):
        """Update regions from region widget - does not auto-calculate baseline"""
        self.current_regions = regions
        # Update RegioCombo with latest region sets
        self.updateRegioStack()
        # Baseline is only calculated when explicitly requested via Show Baseline checkbox
            
    def calculateAndEmitBaseline(self):
        """Calculate baseline and emit the result using selected RegioSet"""
        if not hasattr(self, 'activeBaselineRegion') or not self.activeBaselineRegion:
            return
            
        try:
            import pynmr.model.operations as O
            regiostack = self.model.dataSets[self.dataSetIndex].regionStack
            if self.activeBaselineRegion not in regiostack.regionSets:
                return
            baseline_regions = regiostack.regionSets[self.activeBaselineRegion].regions
            
            if not baseline_regions:
                return
            
            # Get current spectrum data from parent
            data = self.parent.parent.dataWidget.data
            domain = self.parent.parent.dataWidget.domain
            
            if data is None or domain is None:
                return
            
            if domain == "Frequency.Hz":
                x_data = self.model.dataSets[self.dataSetIndex].data.frequency
            elif domain == "Frequency.ppm":
                x_data = self.model.dataSets[self.dataSetIndex].data.ppmScale
            else:
                x_data = np.arange(len(data))
            
            degree = int(self.polyDegreeEntry.text()) if hasattr(self, 'polyDegreeEntry') else 1

            min_x = np.min(x_data)
            max_x = np.max(x_data)
            mask = np.zeros_like(x_data, dtype=bool)
            for region in baseline_regions:
                start, end = sorted(region)
                mask |= (x_data >= max(start, min_x)) & (x_data <= min(end, max_x))

            if np.any(mask):
                x_masked = x_data[mask]
                y_masked = np.real(data)[mask]
                Bsln = O.BaselineFitFunction(degree)
                baseline_func = Bsln.run(x_masked, y_masked)
                y_data = baseline_func(x_data)
                y_data = np.real(y_data)
                self.baselineCalculated.emit(x_data, y_data, baseline_func)
        except Exception as e:
            print(f"Error calculating baseline: {e}")