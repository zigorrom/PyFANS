import os
import sys
import numpy as np

from PyQt4 import QtCore, QtGui, uic

import pyfans.plot as plt


main_view_base, main_view = uic.loadUiType("UI/UI_Analyzer.ui")

class MainView(main_view_base, main_view):
    def __init__(self):
        super().__init__()
        self.setupUi()
        

    def setupUi(self):
        super().setupUi(self)
        self._spectrumPlotWidget = plt.SpectrumPlotWidget(self.ui_plot, {})
        
    
    def setModel(self, model):
        pass

    def closeEvent(self, event):
        pass

def main():
    import ctypes
    myappid = "fzj.pyfans_analyzer.pyfans_analyzer.21" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS Analyzer")
    app.setStyle("cleanlooks")
    
    main_window = MainView()
    
    
    # main_window.setModel(settings_model)
    main_window.showMaximized()

    sys.exit(app.exec_())