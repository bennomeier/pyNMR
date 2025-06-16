
import sys
from pynmr.viewer import gui as mygui
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
m = mygui.MainWindow(arg = [])
m.show()
sys.exit(app.exec_())
