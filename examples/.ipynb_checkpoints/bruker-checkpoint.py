# check this for reloading: https://stackoverflow.com/questions/5364050/reloading-submodules-in-ipython
# %load_ext autoreload
# %autoreload 2

import pyNMR.model.parser.topSpin as T
import pyNMR.model.processor as P
import pyNMR.model.model as M

import pyNMR.model.operations as O

import pyNMR.viewer.gui as G

from PyQt5 import QtWidgets as qtw
import sys

data = T.TopSpin("./data/bruker/STD/1/")
Processor = P.Processor(["LS 10", "LB 0.2", "FT"])
Processor = P.Processor([O.LeftShift(10),
                         O.LineBroadening(0.2),
                         O.FourierTransform()])

Processor.runStack(data)

print("Hello")

print(len(data.allFid))

dataSet = M.pyNmrDataSet(data = data, processor = Processor)
model = M.pyNmrDataModel(dataSet)


app = qtw.QApplication(sys.argv)
mw = G.MainWindow(model)
sys.exit(app.exec())
