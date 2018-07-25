import sys
import re
import traceback
import functools
import numpy as np
import pandas as pd
from PyQt4 import QtCore, QtGui, uic

import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqtgraph import PlotDataItem
from py_expression_eval import Parser

from measurement_data_structures import MeasurementInfo

# def getValueAndName(func, var):


class VariableMapper:
    def __init__(self, variable_list=None,prefix="var_"):
        self._prefix = prefix
        self._baseVarNames = variable_list
        
    @property
    def baseVarNames(self):
        return self._baseVarNames

    @baseVarNames.setter
    def baseVarNames(self, value):
        self._baseVarNames = value
    
    @property
    def encodedVarNames(self):
        return map(self.encode, self._baseVarNames)

    def encode(self, var_name):
        idx = self.baseVarNames.index(var_name)
        return "{0}{1}".format(self._prefix, idx)

    def decode(self, encoded_name):
        if encoded_name.startswith(self._prefix):
            index = int(encoded_name[len(self._prefix):])
            return self.baseVarNames[index]

        return None


class ExperimentData(QtCore.QObject):
    newDataArrived = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        cols = MeasurementInfo.header_options()
        self._data = pd.DataFrame(columns = cols)
        

    @property
    def variables(self):
        var_list = []#  ["index"]
        var_list.extend(list(self._data))
        return var_list

    @property
    def variableMapper(self):
        return VariableMapper(self.variables)

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

    def __getitem__(self, *args):
        print("getting index {0}".format(args))
        return self._data.__getitem__(*args)

    def __str__(self, *args, **kwargs):
        return "ExpeimentData\n"+str(self._data)

    def __repr__(self):
        return self.__str__()


class UpdatablePlotDataItem(PlotDataItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = kwargs.get("curveName","curve")

    @property
    def curveName(self):
        return self._name

    def getBareData(self):
        return self.xData, self.yData

class PlotDock(Dock):
    def __init__(self, name, label, closable=True, **kwargs):
        super().__init__(name, closable=closable, **kwargs)
        self._plot = pg.PlotWidget(title=label)
        self.addWidget(self._plot)
        self.curves = {}

    # def plot(self, curveName, *args, **kwargs):
    def plot(self, *args, **kwargs):
        curve = self.addCurve(*args,**kwargs)
        return curve

    # def addCurve(self, curveName, *args, **kwargs):
    def addCurve(self, *args, **kwargs):
        """Arguments are same as for PlotWidget.plot()"""
        curve = UpdatablePlotDataItem(*args, **kwargs)
        self._plot.addItem(curve)
        # curve = self._plot.plot(*args, **kwargs)
        self.curves[curve.curveName] = curve
        return curve

    def updateCurve(self, xData, yData):
        pass

    @property
    def plotter(self):
        return self._plot

    def setXLink(self, otherPlot):
        if isinstance(otherPlot, PlotDock):
            self._plot.setXLink(otherPlot.plotter)
        
        else: # otherPlot is None:
            self._plot.setXLink(None)
        
            
        # pass
        # self._plot.setXLink(*args, **kwargs)

    def setYLink(self, otherPlot):
        if isinstance(otherPlot, PlotDock):
            self._plot.setYLink(otherPlot.plotter)
        
        else:# otherPlot is None:
            self._plot.setYLink(None)
            
        # self._plot.setYLink(otherPlot.plotter)
        # pass
        # self._plot.setYLink(*args, **kwargs)

    def setAxesLink(self, otherPlot):
        self.setXLink(otherPlot)
        self.setYLink(otherPlot)
        
editExpressionViewBase, editExpressionViewForm = uic.loadUiType("UI/UI_EditExpression.ui")
class EditExpressionDialog(editExpressionViewBase, editExpressionViewForm):
    def __init__(self, variableMapper, stringExpression = "",  parent = None):
        super().__init__(parent)
        self.setupUi(stringExpression)
        self._variableMapper = variableMapper
        self._parsedExpression = None
        self._availableFunctions = ['+','-','*','/','PI','E','abs()','sin()','cos()','tan()','log()']

    @property
    def stringExpression(self):
        return self._stringExpression

    @property
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

        functionMenu = self.menuBar.addMenu("Functions")
        addFunctionAction = QtGui.QAction('Add', self)
        addFunctionAction.triggered.connect(self.on_add_function_to_expression)
        functionMenu.addAction(addFunctionAction)

        self.ui_main_layout.insertWidget(0,self.menuBar)
        self.ui_expression.setText(expression)
    
    @QtCore.pyqtSlot()
    def on_add_function_to_expression(self):
        items = self._availableFunctions
        item, ok = QtGui.QInputDialog.getItem(self, "Select function", "list of functions", items, 0, False)
        if ok:
            # idx = 
            self.ui_expression.insert(item)

    @QtCore.pyqtSlot()
    def on_add_variable_to_expression(self):
        items = self._variableMapper.baseVarNames
        item, ok = QtGui.QInputDialog.getItem(self, "Select variable", "list of variables", items, 0, False)
        if ok:
            item = self._variableMapper.encode(item)
            self.ui_expression.insert(item)

    def accept(self):
        try:
            self._parsedExpression = self.parseExpression()
            variables = self.parsedExpression.variables()
            print(variables)
            if not all(variable in self._variableMapper.encodedVarNames for variable in variables):
                raise ValueError("variables are not in variable list")
            print(self.parsedExpression.toString())
            super().accept()

        except Exception as e:
            print("cannot accept")
            print("Exception")
            traceback.print_exc(file=sys.stdout)
            print(e)


addCurveViewBase, addCurveViewForm = uic.loadUiType("UI/UI_AddCurveDialog.ui")
class AddCurveDialog(addCurveViewBase, addCurveViewForm):
    def __init__(self, variableMapper,  parent = None ):
        super(addCurveViewBase,self).__init__(parent)
        self.setupUi()
        self.variableMapper = variableMapper
        self.x_axis_function = None
        self.y_axis_function = None

        self.ui_x_axis_value.clear()
        self.ui_x_axis_value.addItems(self.variableMapper.baseVarNames)
        self.ui_y_axis_value.clear()
        self.ui_y_axis_value.addItems(self.variableMapper.baseVarNames)
        
    
    def setupUi(self):
        super().setupUi(self)

    @property
    def xAxisFunction(self):
        return self.x_axis_function

    @property
    def yAxisFunction(self):
        return self.y_axis_function

    @property
    def selectedXVariable(self):
        return self.ui_x_axis_value.currentText()

    @property
    def selectedYVariable(self):
        return self.ui_y_axis_value.currentText()

    @property
    def autoUpdate(self):
        return self.ui_auto_update.isChecked()

    @QtCore.pyqtSlot()
    def on_ui_x_axis_function_clicked(self):
        print("add x function")
        dialog = EditExpressionDialog(self.variableMapper)
        res = dialog.exec_()
        if res:
            self.x_axis_function = dialog.parsedExpression

    @QtCore.pyqtSlot()
    def on_ui_y_axis_function_clicked(self):
        print("add y function")
        dialog = EditExpressionDialog(self.variableMapper)
        res = dialog.exec_()
        if res:
            self.y_axis_function = dialog.parsedExpression

selectPlotViewBase, selectPlotViewForm = uic.loadUiType("UI/UI_SelectPlots.ui")
class SelectPlotsDialog(selectPlotViewBase, selectPlotViewForm):
    def __init__(self, parent = None):
        super(selectPlotViewBase,self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        super().setupUi(self)

    def setList(self, plotNames):
        self.ui_plot_list.clear()
        for n in plotNames:
            item = QtGui.QListWidgetItem(n)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.ui_plot_list.addItem(item)

    def getSelectedList(self):
        res = []
        for index in range(self.ui_plot_list.count()):
            item = self.ui_plot_list.item(index)
            state = item.checkState()
            if state == QtCore.Qt.Checked:
                res.append(item.text())
        return res

    @QtCore.pyqtSlot()
    def on_ui_select_all_clicked(self):
        for index in range(self.ui_plot_list.count()):
            item = self.ui_plot_list.item(index)
            item.setCheckState(QtCore.Qt.Checked)

    @QtCore.pyqtSlot()
    def on_ui_clear_all_clicked(self):
        for index in range(self.ui_plot_list.count()):
            item = self.ui_plot_list.item(index)
            item.setCheckState(QtCore.Qt.Unchecked)
    
mainViewBase, mainViewForm = uic.loadUiType("UI/UI_ExperimentDataAnalysis.ui")
class ExperimentDataAnalysis(mainViewBase,mainViewForm):
    def __init__(self, layout="horizontal", parent = None ):
        super(mainViewBase,self).__init__(parent)
        self.setupUi()
        self._layout = layout
        self._data = ExperimentData()
        for i in range(10):
            self._data.append(generate_meas_data(i))

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
        mapper = self.data.variableMapper
        dialog = AddCurveDialog(variableMapper=mapper,parent=self)
        res = dialog.exec_()
        if res:
            print("adding plot")
            xVal = None
            yVal = None
            
            xName = ""
            yName = ""
            # plot1.plot(x,y, pen=(0,0,200))#, symbolBrush=(0,0,200), symbolPen='w', symbol='o', symbolSize=14, name="symbol='o'")
            
            x_var = dialog.selectedXVariable
            funcx = dialog.xAxisFunction

            if funcx is not None:
                v = funcx.variables()
                vdecod = [mapper.decode(i) for i in v]
                data = self.data[vdecod].values.T
                params = {key: value for key,value in zip(v,data)}
                xVal = funcy.evaluate(params)
                xName = funcx.simplify({}).toString()
                for ve, vd in zip(v,vdecod):
                    xName = xName.replace(ve,vd)

            else:
                xVal = self.data[[x_var]].values.T[0]
                xName = x_var

            y_var = dialog.selectedYVariable
            funcy = dialog.yAxisFunction

            if funcy is not None:
                v = funcy.variables()
                vdecod = [mapper.decode(i) for i in v]
                data = self.data[vdecod].values.T
                params = {key: value for key,value in zip(v,data)}
                yVal = funcy.evaluate(params)
                yName = funcy.simplify({}).toString()
                for ve, vd in zip(v,vdecod):
                    yName = yName.replace(ve,vd)
            else:
                yVal = self.data[[y_var]].values.T[0]
                yName = y_var
            
            print(xVal)
            print(yVal)
            plotName = "plot_{0}".format(len(self._plot_dict))
            label = "{y} =f( {x} )".format(y=yName, x=xName)
            plot = PlotDock(plotName, label)
            # curve = plot.plot("curve", xVal, yVal)
            curve = plot.plot(xVal, yVal, curveName="curve1")
            print("reading back x and y values")
            xv,yv = curve.getBareData()
            print(xv)
            print(yv)

            whereToAppend = "right" 
            if self._layout == "horizontal":
                whereToAppend = "right"
            elif self._layout == "vertical":
                whereToAppend = "bottom"
            else:
                whereToAppend = "right"

            self._dockArea.addDock(plot, whereToAppend)
            self._plot_dict[plotName] = plot
            
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
        
    @QtCore.pyqtSlot()
    def on_actionLinkXAxis_triggered(self):
        # plots = self._plot_dict.keys()
        plotNamesToLink = self.getPlotsToLink()
        # print(plotNamesToLink)
        if not plotNamesToLink:
            return 
        functools.reduce(lambda p1, p2: self.linkViews(p1,p2,True, False), plotNamesToLink)


    @QtCore.pyqtSlot()
    def on_actionLinkYAxis_triggered(self):
        plotNamesToLink = self.getPlotsToLink()
        # print(plotNamesToLink)
        if not plotNamesToLink:
            return 
        functools.reduce(lambda p1, p2: self.linkViews(p1,p2,False, True), plotNamesToLink)

    @QtCore.pyqtSlot()
    def on_actionLinkAxes_triggered(self):
        plotNamesToLink = self.getPlotsToLink()
        # print(plotNamesToLink)
        if not plotNamesToLink:
            return 
        functools.reduce(lambda p1, p2: self.linkViews(p1,p2,True, True), plotNamesToLink)
        
    @QtCore.pyqtSlot()
    def on_actionUnlink_triggered(self):
        plotNamesToLink = self.getPlotsToLink()
        # print(plotNamesToLink)
        if not plotNamesToLink:
            return 
        print("Unlinking...")
        print(plotNamesToLink)
        for name in plotNamesToLink:
            p = self._plot_dict[name]  
            p.setAxesLink(None)
        # p1 = self._plot_dict["plot_0"]
        # p1.set

        print("Unlinking successful")

   

    def linkViews(self, plotName1, plotName2, linkX=False, linkY=False):
        plot1 = self._plot_dict.get(plotName1)
        plot2 = self._plot_dict.get(plotName2)
        if linkX and linkY:
            plot1.setAxesLink(plot2)
        elif linkX:
            plot1.setXLink(plot2)
        elif linkY:
            plot1.setYLink(plot2)
        else:
            plot1.setAxesLink(None)
            plot2.setAxesLink(None)

        return plotName2

    def getPlotsToLink(self):
        plotNames = list(self._plot_dict.keys())
        print("Plot Names")
        print(plotNames)
        dialog = SelectPlotsDialog()
        dialog.setList(plotNames)
        res = dialog.exec_()
        plotList = dialog.getSelectedList()
        if len(plotList)>1:
            return plotList
        return None
        # print("Plots to link")
        # print(plotList)
        
        

        

        

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
    add_val = np.random.random_sample()
    main_volt = add_val+val
    sample_volt = val
    gate_volt = np.random.random_sample()
    md.update_start_values(main_volt, sample_volt, gate_volt, 279)
    md.update_end_values(main_volt, sample_volt, gate_volt, 279)
    return md

def test_exp_data():
    exp_data = ExperimentData()
    for i in range(10):
        exp_data.append(generate_meas_data(i))
    
    m = exp_data.variables
    var1 = m[2]
    var2 = m[15]


    data = exp_data[[var1,var2]]
    print(data)


    
    # print(exp_data)


if __name__== "__main__":
    
    sys.exit(test_ui())
    # sys.exit(test_exp_data())