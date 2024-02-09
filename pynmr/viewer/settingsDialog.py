from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class SettingsDialog(qtw.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")

        self.myLayout = qtw.QVBoxLayout()

        self.cbReal = qtw.QCheckBox("Show Real Part")
        self.cbImag = qtw.QCheckBox("Show Imaginary Part")
        self.cbMagn = qtw.QCheckBox("Show Magnitude")

        self.myLayout.addWidget(self.cbReal)
        self.myLayout.addWidget(self.cbImag)
        self.myLayout.addWidget(self.cbMagn)

        print("showImag Settings VAlue: ")
        print(parent.settings.value("showImag", False, type=bool))

        if parent.settings.value("showReal", True, type = bool):
            self.cbReal.setChecked(True)

        if parent.settings.value("showImag", False, type = bool):
            self.cbImag.setChecked(True)
        if parent.settings.value("showMagn", False, type = bool):
            self.cbMagn.setChecked(True)

                               
        self.qbtnOk = qtw.QDialogButtonBox.Ok   
        buttons = self.qbtnOk | qtw.QDialogButtonBox.Cancel

        self.buttonBox = qtw.QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.myLayout.addWidget(self.buttonBox)
        
        self.setLayout(self.myLayout)
        

    def accept(self):
        # update settings.
        self.parent.settings.setValue("showReal", bool(self.cbReal.isChecked()))
        self.parent.settings.setValue("showImag", bool(self.cbImag.isChecked()))
        self.parent.settings.setValue("showMagn", bool(self.cbMagn.isChecked()))

        self.parent.dataWidget.updatePW()
        
        super().accept()


        
