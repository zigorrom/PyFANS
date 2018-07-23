import sys

import numpy as np
import pandas as pd
from PyQt4 import QtCore, QtGui, uic

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from measurement_data_structures import MeasurementInfo



class ExperimentData(object):
    def __init__(self):
        cols = MeasurementInfo.header_options()
        self._data = pd.DataFrame(columns = cols)
        # c = list(self._data)
        # print(c)

    @property
    def variables(self):
        var_list = ["index"]
        var_list.extend(list(self._data))
        return var_list

    def getDataFrame(self):
        return self._data

    def append(self, measurement_data):
        pass
    
class PlotDock(Dock):
    def __init__(self, name, closable=True, **kwargs):
        super().__init__(name, closable=closable, **kwargs)
        self._plot = pg.PlotWidget(title=name)
        self.addWidget(self._plot)

    def plot(self, *args, **kwargs):
        self._plot.plot(*args, **kwargs)

    @property
    def plotter(self):
        return self._plot

    def setXLink(self, *args, **kwargs):
        self._plot.setXLink(*args, **kwargs)

    def setYLink(self, *args, **kwargs):
        self._plot.setYLink(*args, **kwargs)


mainViewBase, mainViewForm = uic.loadUiType("UI/UI_ExperimentDataAnalysis.ui")
class ExperimentDataAnalysis(mainViewBase,mainViewForm):
    def __init__(self, parent = None ):
        super().__init__(parent)
        self.setupUi()
        self.data = ExperimentData()
        print(self.data.variables)
    
    def setupUi(self):
        super().setupUi(self)
        self._dockArea = DockArea()
        self.setCentralWidget(self._dockArea)

        

    @QtCore.pyqtSlot()
    def on_actionAddPlot_triggered(self):
        print("adding plot")
        # self._dockArea.setVisible(True)
        plot1 = PlotDock("new")
        plot1.plot(np.random.normal(size=100))
        plot2 = PlotDock("new2")
        plot2.plot(np.random.normal(size=100))
        
        plot1.setYLink(plot2.plotter)
        self._dockArea.addDock(plot1, "right")
        self._dockArea.addDock(plot2, "right")

    @QtCore.pyqtSlot()
    def on_actionAddCurve_triggered(self):
        print("adding curve")
        
    

    

if __name__== "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ExperimentDataAnalysis")
    app.setStyle("cleanlooks")
    wnd = ExperimentDataAnalysis()
    wnd.show()

    sys.exit(app.exec_())