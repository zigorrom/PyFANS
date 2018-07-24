import sys
import re
import traceback
import numpy as np
import pandas as pd
from PyQt4 import QtCore, QtGui, uic

import pyqtgraph as pg
from pyqtgraph.dockarea import *
from py_expression_eval import Parser

from measurement_data_structures import MeasurementInfo

def escape_variable(string_var):
    # return re.escape(string)
    if isinstance(string_var, str):
        ret = string_var.replace("(","_<_")
        ret = ret.replace(")","_>_")
        ret = ret.replace(" ","_")
        return ret

    return string_var

def unescape_variable(string_var):
    if isinstance(string_var, str):
        ret = string_var.replace("_<_","(")
        ret = ret.replace("_>_", ")")
        ret = ret.replace("_", " ")
        return ret

    return string_var

class ExperimentData(QtCore.QObject):
    newDataArrived = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
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
    
    @property
    def count(self):
        return len(self._data.index)

    def append(self, measurement_data):
        new_data = measurement_data.to_dict()
        self._data.loc[self.count] = new_data
        keys = new_data.keys()
        self.newDataArrived.emit(keys)

    def __str__(self, *args, **kwargs):
        return "ExpeimentData\n"+str(self._data)

    def __repr__(self):
        return self.__str__()


    
class PlotDock(Dock):
    def __init__(self, name, closable=True, **kwargs):
        super().__init__(name, closable=closable, **kwargs)
        self._plot = pg.PlotWidget(title=name)
        self.addWidget(self._plot)

    def plot(self, *args, **kwargs):
        self._plot.plot(*args, **kwargs)

    def addCurve(self, *args, **kwargs):
        """Arguments are same as for PlotWidget.plot()"""
        self._plot.plot(*args, **kwargs)

    @property
    def plotter(self):
        return self._plot

    def setXLink(self, *args, **kwargs):
        self._plot.setXLink(*args, **kwargs)

    def setYLink(self, *args, **kwargs):
        self._plot.setYLink(*args, **kwargs)



editExpressionViewBase, editExpressionViewForm = uic.loadUiType("UI/UI_EditExpression.ui")
class EditExpressionDialog(editExpressionViewBase, editExpressionViewForm):
    def __init__(self, param_list, stringExpression = "",  parent = None):
        super().__init__(parent)
        self.setupUi(stringExpression)
        self._stringExpression = stringExpression
        self._parsedExpression = None
        self._param_list = param_list
        if self._param_list is None:
            self._param_list = "None"

    @property
    def stringExpression(self):
        return self._stringExpression

    def parsedExpression(self):
        return self._parsedExpression

    def parseExpression(self):
        parser = Parser()
        expr = parser.parse(self.ui_expression.text())
        return expr

    def setupUi(self, expression=""):
        super().setupUi(self)
        self.menuBar = QtGui.QMenuBar()
        variableMenu = self.menuBar.addMenu("Variables")
        addVariableAction = QtGui.QAction('Add', self)
        addVariableAction.triggered.connect(self.on_add_variable_to_expression)
        variableMenu.addAction(addVariableAction)
        self.ui_main_layout.insertWidget(0,self.menuBar)
        self.ui_expression.setText(expression)
    
    @QtCore.pyqtSlot()
    def on_add_variable_to_expression(self):
        items = self._param_list
        item, ok = QtGui.QInputDialog.getItem(self, "Select variable", "list of variables", items, 0, False)
        if ok:
            item = escape_variable(item)
            self.ui_expression.insert(item)

    def accept(self):
        try:
            self._parsedExpression = self.parseExpression()
            variables = self._parsedExpression.variables()
            print(variables)
            if not all(variable in self._param_list for variable in variables):
                raise ValueError("variables are not in variable list")
            print(self._parsedExpression.toString())
            super().accept()

        except Exception as e:
            # self.ui_expression.setStyleSheet("QLineEdit{border-color: red;}")
            print("cannot accept")
            print("Exception")
            traceback.print_exc(file=sys.stdout)
            print(e)


    

    

# class MeasurementCurve(QtCore.QObject):
#     def __init__(self, )
addCurveViewBase, addCurveViewForm = uic.loadUiType("UI/UI_AddCurveDialog.ui")
class AddCurveDialog(addCurveViewBase, addCurveViewForm):
    def __init__(self, param_list = None,  parent = None ):
        super(addCurveViewForm,self).__init__(parent)
        self.setupUi()
        self.param_list = ["None"] 
        if param_list:
            self.param_list.extend(param_list)
        # model = QtGui.QStringListModel(self.strLst)
        self.ui_x_axis_value.clear()
        self.ui_x_axis_value.addItems(self.param_list)
        self.ui_y_axis_value.clear()
        self.ui_y_axis_value.addItems(self.param_list)
        


    def setupUi(self):
        super().setupUi(self)

    @QtCore.pyqtSlot()
    def on_ui_x_axis_function_clicked(self):
        print("add x function")
        dialog = EditExpressionDialog(self.param_list)
        res = dialog.exec_()
        

    @QtCore.pyqtSlot()
    def on_ui_y_axis_function_clicked(self):
        print("add y function")
        dialog = EditExpressionDialog(self.param_list)
        res = dialog.exec_()


mainViewBase, mainViewForm = uic.loadUiType("UI/UI_ExperimentDataAnalysis.ui")
class ExperimentDataAnalysis(mainViewBase,mainViewForm):
    def __init__(self, parent = None ):
        super().__init__(parent)
        self.setupUi()
        self._data = ExperimentData()
        self._plot_dict = dict()
        self._curve_dict = dict()
        print(self.data.variables)
    
    def setupUi(self):
        super().setupUi(self)
        self._dockArea = DockArea()
        self.setCentralWidget(self._dockArea)

    @property
    def data(self):
        return self._data
    
    def setData(self, data):
        if not isinstance(data, ExperimentData):
            raise TypeError("data should of ExperimentData type ")
        
        self._data = data


    @QtCore.pyqtSlot()
    def on_actionAddPlot_triggered(self):
        variables = self.data.variables
        dialog = AddCurveDialog(param_list=variables,parent=self)
        res = dialog.exec_()
        if res:
            print("adding plot")
        else:
            print("cancelled")
        # self._dockArea.setVisible(True)
        # plot1 = PlotDock("new")
        # plot1.plot(np.random.normal(size=100))
        # plot2 = PlotDock("new2")
        # plot2.plot(np.random.normal(size=100))
        
        # plot1.setYLink(plot2.plotter)
        # self._dockArea.addDock(plot1, "right")
        # self._dockArea.addDock(plot2, "right")

    @QtCore.pyqtSlot()
    def on_actionAddCurve_triggered(self):
        print("adding curve")
        
    

def test_ui():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ExperimentDataAnalysis")
    app.setStyle("cleanlooks")
    wnd = ExperimentDataAnalysis()
    wnd.show()
    return app.exec_()
    
def generate_meas_data(count=0):
    md = MeasurementInfo("a", count)
    val = np.random.random_sample()
    main_volt = 1+val
    sample_volt = val
    gate_volt = np.random.random_sample()
    md.update_start_values(main_volt, sample_volt, gate_volt, 279)
    md.update_end_values(main_volt, sample_volt, gate_volt, 279)
    return md

def test_exp_data():
    exp_data = ExperimentData()
    for i in range(10):
        exp_data.append(generate_meas_data(i))


    print(exp_data)


if __name__== "__main__":
    
    sys.exit(test_ui())
    # sys.exit(test_exp_data())