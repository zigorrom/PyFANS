import os
import sys
import re
import math
import traceback
import functools
import numpy as np
import pandas as pd

from PyQt4 import QtCore, QtGui, uic

import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqtgraph.dockarea.Dock import DockLabel
from pyqtgraph import PlotDataItem
from pyqtgraph.graphicsItems.LegendItem import LegendItem
from pyqtgraph import exporters as pg_exp
# from py_expression_eval import Parser

from pyfans_analyzer.expression_parser_patch import PatchedParser
from pyfans.experiment.measurement_data_structures import MeasurementInfo

# def getValueAndName(func, var):
# def get_function_variables(function):
def updateDockLabelStylePatched(self):
    pass
    # r = '3px'
    # if self.dim:
    #     fg = '#b0b0b0'
    #     bg = '#94f5bb'
    #     border = '#94f5bb'
    #     # border = '#7cf3ac'
    # else:
    #     fg = '#fff'
    #     bg = '#10b151'
    #     border = '#10b151'

    # if self.orientation == 'vertical':
    #     self.vStyle = """DockLabel {
    #         background-color : %s;
    #         color : %s;
    #         border-top-right-radius: 0px;
    #         border-top-left-radius: %s;
    #         border-bottom-right-radius: 0px;
    #         border-bottom-left-radius: %s;
    #         border-width: 0px;
    #         border-right: 2px solid %s;
    #         padding-top: 3px;
    #         padding-bottom: 3px;
    #         font-size: 18px;
    #     }""" % (bg, fg, r, r, border)
    #     self.setStyleSheet(self.vStyle)
    # else:
    #     self.hStyle = """DockLabel {
    #         background-color : %s;
    #         color : %s;
    #         border-top-right-radius: %s;
    #         border-top-left-radius: %s;
    #         border-bottom-right-radius: 0px;
    #         border-bottom-left-radius: 0px;
    #         border-width: 0px;
    #         border-bottom: 2px solid %s;
    #         padding-left: 13px;
    #         padding-right: 13px;
    #         font-size: 18px
    #     }""" % (bg, fg, r, r, border)
    #     self.setStyleSheet(self.hStyle)
DockLabel.updateStyle = updateDockLabelStylePatched

def open_folder_in_explorer(folder):
    print("opening folder")
    folder = os.path.abspath(folder)
    request = 'explorer "{0}"'.format(folder)#self._settings.working_directory)
    print(request)
    os.system(request)


class CustomLegendItem(LegendItem):
    def __init__(self, size = None, offset = None):
        super().__init__(size, offset)

    

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
        if not var_name:
            return None

        idx = self.baseVarNames.index(var_name)
        return "{0}{1}".format(self._prefix, idx)

    def decode(self, encoded_name):
        if not encoded_name:
            return None

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
        
    
    def importFromFile(self, filename):
        self._data = pd.read_csv(filename, delimiter="\t")
        keys = list(self._data)
        self.newDataArrived.emit(keys)


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
        c = 0 if math.isnan(self._data.index.max()) else self._data.index.max() + 1
        return c
        # return len(self._data.index)

    def clear(self):
        self._data = self._data.iloc[0:0]

    def append(self, measurement_data):
        new_data = measurement_data.to_dict()
        # newdf = pd.DataFrame.from_dict(new_data)
        # self._data.append(newdf)
        self._data.loc[self.count] = new_data
        keys = new_data.keys()
        # new_data = measurement_data.to_DataFrame()
        # self._data = self._data.append(new_data)
        # keys = list(new_data)
        self.newDataArrived.emit(keys)
        # print("appending data")
        # print(new_data)
        # print(self._data)

    def __getitem__(self, *args):
        # print("getting index {0}".format(args))
        return self._data.__getitem__(*args)

    def __str__(self, *args, **kwargs):
        return "ExpeimentData\n"+str(self._data)

    def __repr__(self):
        return self.__str__()

class CurveDataProvider(QtCore.QObject):
    dataUpdated = QtCore.pyqtSignal()
    def __init__(self, dataSource, xVariable=None, yVariable=None, xFunction=None, yFunction=None, autoUpdate=False):
        super().__init__()
        self._dataSource = dataSource
        self._autoUpdate = None
        self.AutoUpdated = autoUpdate
        # if autoUpdate:
        #     self._dataSource.newDataArrived.connect(self.on_data_source_updated)

        self._xVariable = xVariable
        self._yVariable = yVariable

        self._xFunction = xFunction
        self._yFunction = yFunction

        self._currentXdata = None
        self._currentYdata = None

        self._xDataProducer = None
        self._yDataProducer = None

        self._xCaption = ""
        self._yCaption = ""
        
        
       
        self.__initializeDataFunctions__()
        self.__refreshData__()
    
    def __initializeDataFunctions__(self):
        if self._xFunction:
            self._xDataProducer = functools.partial(self.__execute_function__, self._xFunction)
            self._xCaption = self.__get_caption_for_function__(self._xFunction)
        elif self._xVariable:
            self._xDataProducer = functools.partial(self.__get_data_for_variables__, self._xVariable)
            self._xCaption = self.__decode_variables__(self._xVariable)
        else:
            raise ValueError("Not enough data to intialize data provider")

        if self._yFunction:
            self._yDataProducer = functools.partial(self.__execute_function__, self._yFunction)
            self._yCaption = self.__get_caption_for_function__(self._yFunction)
        elif self._yVariable:
            self._yDataProducer = functools.partial(self.__get_data_for_variables__, self._yVariable)
            self._yCaption = self.__decode_variables__(self._yVariable)
        else:
            raise ValueError("Not enough data to intialize data provider")


    def __refreshData__(self):
        self._currentXdata = self._xDataProducer()
        self._currentYdata = self._yDataProducer()

    @property
    def AutoUpdated(self):
        return self._autoUpdate

    @AutoUpdated.setter
    def AutoUpdated(self, value):
        try:
            if value:
                self._dataSource.newDataArrived.connect(self.on_data_source_updated)
            else:
                self._dataSource.newDataArrived.disconnect(self.on_data_source_updated)
        except Exception:
            print("method is not connected")
        finally:
            self._autoUpdate = value
        

    @property
    def dataSource(self):
        return self._dataSource

    @property
    def xVariable(self):
        return self._dataSource.variableMapper.decode(self._xVariable)

    @property
    def yVariable(self):
        return self._dataSource.variableMapper.decode(self._yVariable)

    @property
    def xFunction(self):
        return self._xFunction
    
    @property
    def yFunction(self):
        return self._yFunction

    def __decode_variables__(self, variables):
        if isinstance(variables, str):
            return self._dataSource.variableMapper.decode(variables)
        elif isinstance(variables, (list,tuple)):
            return [self._dataSource.variableMapper.decode(v) for v in variables]
        else:
            return None

    def __get_function_variables__(self, function, decoded=False):
        if decoded:
            return self.__decode_variables__(function.variables())
        else:
            return function.variables()

    def __get_data_for_variables__(self, variables):
        columns = self.__decode_variables__(variables)
        return self.__get_data_for_columns__(columns)

    def __get_data_for_columns__(self, cols):
        if isinstance(cols,(list, tuple)):
            return self.dataSource[cols].values.T
        else:
            return self.dataSource[[cols]].values.T[0]

    def __execute_function__(self, function):
        funcVars = self.__get_function_variables__(function, decoded=False)
        data =  self.__get_data_for_variables__(funcVars)
        params = {key: value for key,value in zip(funcVars,data)}
        result = function.evaluate(params)
        return result 

    def __get_caption_for_function__(self, function):
        funcVars = self.__get_function_variables__(function, decoded=False)
        columns = self.__decode_variables__(funcVars)
        caption = function.simplify({}).toString()
        for ve, vd in zip(funcVars,columns):
            caption = caption.replace(ve,vd)

        return caption

    def on_data_source_updated(self, keys):
        # print(keys)
        self.__refreshData__()
        self.dataUpdated.emit()

    def getData(self):
        return self._currentXdata, self._currentYdata

    def getDependanceName(self):
        label = "{y} =f( {x} )".format(y=self._yCaption, x=self._xCaption)
        return label

class UpdatablePlotDataItem(PlotDataItem):
    def __init__(self, *args, **kwargs):
        # self._name = kwargs.get("curveName","curve")
        super().__init__(*args, **kwargs)
        
    def setData(self, *args, **kwargs):
        dataSource = kwargs.get("dataSource", None)
        if dataSource is None:
            super().setData(*args, **kwargs)
        else:
            x,y = dataSource.getData()
            super().setData(x,y, **kwargs)
            self._dataSource = dataSource
            self._dataSource.dataUpdated.connect(self.on_data_source_updated)

    def on_data_source_updated(self):
        x,y = self._dataSource.getData()
        super().setData(x,y)

    @property
    def curveName(self):
        return self.name()

    # def getBareData(self):
    #     return self.xData, self.yData


class PlotDock(Dock):
    def __init__(self, plotName, label, closable=True, logX=False, logY=False, **kwargs):
        super().__init__(plotName, closable=closable, **kwargs)        
        self._plot = pg.PlotWidget(title=label)
        self.addWidget(self._plot)
        self.setupPlot(logX=logX, logY=logY)

        self.curves = []

    def setupPlot(self, **kwargs):
        self._plot.showAxis("right", show=True)
        self._plot.showAxis("top", show=True)
        right_axis = self._plot.getAxis("right")
        right_axis.setStyle(showValues = False)
        right_axis.setWidth(20)
        top_axis = self._plot.getAxis("top")
        top_axis.setStyle(showValues = False)
        logX = kwargs.get("logX", False)
        logY = kwargs.get("logY", False)
        self._plot.setLogMode(x=logX, y=logY)
        self._plot.addLegend()

    def setLogScale(self, logX=False, logY=False):
        self._plot.setLogMode(x=logX, y=logY)

    # def plot(self, curveName, *args, **kwargs):
    def plot(self, *args, **kwargs):
        curve = self.addCurve(*args,**kwargs)
        return curve

    # def addCurve(self, curveName, *args, **kwargs):
    def addCurve(self, *args, **kwargs):
        """Arguments are same as for PlotWidget.plot()"""
        # if len(self.curves) > 0:
        #     self._plot.addLegend()

        curve = UpdatablePlotDataItem(*args, **kwargs)
        self._plot.addItem(curve)
        # curve = self._plot.plot(*args, **kwargs)
        self.curves.append(curve)
        
        return curve

    @property
    def plotter(self):
        return self._plot

    def setXLink(self, otherPlot):
        if isinstance(otherPlot, PlotDock):
            self._plot.setXLink(otherPlot.plotter)
        
        else: # otherPlot is None:
            self._plot.setXLink(None)
        

    def setYLink(self, otherPlot):
        if isinstance(otherPlot, PlotDock):
            self._plot.setYLink(otherPlot.plotter)
        
        else:# otherPlot is None:
            self._plot.setYLink(None)
        
    def setAxesLink(self, otherPlot):
        self.setXLink(otherPlot)
        self.setYLink(otherPlot)

    def addLegend(self, size=None, offset=(30, 30)):
        if self._plot.legend is None:
            self._plot.legend = CustomLegendItem(size, offset) #LegendItem(size, offset)
            self._plot.legend.setParentItem(self.vb)
        return self.legend 

    @property
    def items(self):
        return self._plot.getPlotItem().items

    def removeItem(self, item):
        self._plot.removeItem(item)

    def exportAsImage(self, filename, folder):
        vb = self._plot.plotItem#.getViewBox()
        exporter = pg_exp.ImageExporter(vb)
        exporter.export(os.path.join(folder,"{0}.png".format(filename)))
    
        
editExpressionViewBase, editExpressionViewForm = uic.loadUiType("UI/UI_EditExpression.ui")
class EditExpressionDialog(editExpressionViewBase, editExpressionViewForm):
    def __init__(self, variableMapper, stringExpression = "",  parent = None):
        super().__init__(parent)
        self.setupUi(stringExpression)
        self._variableMapper = variableMapper
        self._parsedExpression = None
        self._availableFunctions = ['+','-','*','/','PI','E','abs()','sin()','cos()','tan()','log()','Sv(filename,frequency)', "Si(filename,frequency,resistance)", "Sinorm(filename,frequency,resistance,current)"]

    @property
    def stringExpression(self):
        return self._stringExpression

    @property
    def parsedExpression(self):
        return self._parsedExpression

    def parseExpression(self):
        # parser = Parser()PatchedParser
        parser = PatchedParser()
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
    def __init__(self, variableMapper,  parent = None , **kwargs):
        super(addCurveViewBase,self).__init__(parent)
        self.setupUi()
        self.variableMapper = variableMapper
        self.x_axis_function = None
        self.y_axis_function = None

        self.ui_x_axis_value.clear()
        self.ui_x_axis_value.addItems(self.variableMapper.baseVarNames)
        self.ui_y_axis_value.clear()
        self.ui_y_axis_value.addItems(self.variableMapper.baseVarNames)
        self._curve_name = None
        self.curveName = kwargs.get("curveName", "")

        
    
    def setupUi(self):
        super().setupUi(self)
        self.ui_desired_position.setVisible(False)

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
    def useSelectedPosition(self):
        return self.ui_select_position.isChecked()

    @property
    def selectedPosition(self):
        return self.ui_desired_position.currentText()

    @property
    def autoUpdate(self):
        return self.ui_auto_update.isChecked()

    @property
    def logX(self):
        return self.ui_log_mode_x.isChecked()

    @property
    def logY(self):
        return self.ui_log_mode_y.isChecked()

    def getLogMode(self):
        return self.logX, self.logY

    @property
    def curveColor(self):
        return self.ui_curve_color.color()
        
    @property
    def lineWidth(self):
        return self.ui_line_width.value()

    @property
    def curveName(self):
        cn = self.ui_curve_name.text()
        if cn:
            return cn
        else:
            return self._curve_name

    @curveName.setter
    def curveName(self, value):
        self._curve_name = value
        self.ui_curve_name.setText(value)



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
    def __init__(self, experimentData = None, layout="horizontal", parent = None ):
        super(mainViewBase,self).__init__(parent)
        self.setupUi()
        self._layout = layout
        self._data = experimentData #ExperimentData()
        # for i in range(10):
        #     self._data.append(generate_meas_data(i))

        self._plot_dict = dict()
        self._curve_dict = dict()
        # print(self.data.variables)

        # self.counter = 0
        # self.max_count = 1000
        
        self.working_directory = None
        # self.timer = QtCore.QTimer(self)
        # self.timer.setInterval(500)
        # self.timer.timeout.connect(self.updatingPlot)
    
    # def setupConnectBackToParentMenu(self):
    #     pass
    
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
 
    def whereToAppendDockPlot(self):
        whereToAppend = "right" 
        if self._layout == "horizontal":
            whereToAppend = "right"
        elif self._layout == "vertical":
            whereToAppend = "bottom"
        else:
            whereToAppend = "right"
        return whereToAppend

    def addCurve(self, plot, curveName ):
        variables = self.data.variables
        mapper = self.data.variableMapper
        # plotName = "plot_{0}".format(len(self._plot_dict))
        #curveName = "curve {0}".format(len(self._curve_dict))
        dialog = AddCurveDialog(variableMapper=mapper,parent=self, curveName=curveName)
        res = dialog.exec_()
        if res:
            print("adding plot")
            
            x_var = dialog.selectedXVariable
            funcx = dialog.xAxisFunction

            y_var = dialog.selectedYVariable
            funcy = dialog.yAxisFunction

            autoUpdate = dialog.autoUpdate
            log_x,log_y = dialog.getLogMode()
            curveColor = dialog.curveColor
            lineWidth = dialog.lineWidth
            curveName = dialog.curveName
            p = pg.mkPen(color=curveColor, width=lineWidth)

            dataProvider = CurveDataProvider(self.data, mapper.encode(x_var), mapper.encode(y_var), funcx, funcy, autoUpdate)
            dependencyName = dataProvider.getDependanceName()
            plot.setLogScale(log_x,log_y)
            curve = plot.plot(dataSource=dataProvider, name=dependencyName, pen=p, symbol="o", symbolPen=p, symbolBrush=pg.mkBrush(color=curveColor), size=10, pxMode=True  )
            whereToAddPlot = dialog.selectedPosition if dialog.useSelectedPosition else None
            return curve, whereToAddPlot
            
        else:
            print("cancelled")
            return None

    @QtCore.pyqtSlot()
    def on_actionAddPlot_triggered(self):
        plotName = "plot_{0}".format(len(self._plot_dict))
        curveName = "curve {0}".format(len(self._curve_dict))
        plot = PlotDock(plotName,plotName)
        whereToAppend = self.whereToAppendDockPlot()
        curve, position = self.addCurve(plot, curveName)
        if not curve:
            print("cancelled")
            return

        self._plot_dict[plotName] = plot
        self._curve_dict[curve.curveName] = curve
       
        if position:
            whereToAppend = position
        self._dockArea.addDock(plot, whereToAppend)


#FIX in pyqtgraph line 765:
# fragments = [QtGui.QPainter.PixmapFragment.create(targetRect.center(), sourceRect, targetRect.width()/sourceRect.width(),targetRect.height()/sourceRect.height() ) for targetRect, sourceRect in zip(data['targetRect'].tolist(), data['sourceRect'].tolist()) ] 
# p.drawPixmapFragments(fragments, atlas) 
       

    @QtCore.pyqtSlot()
    def on_actionAddCurve_triggered(self):
        print("adding curve")
        items = list(self._plot_dict.keys())
        plotName, ok = QtGui.QInputDialog.getItem(self, "Select plot", "list of plots", items, 0, False)
        
        curveName = "curve {0}".format(len(self._curve_dict))
        
        plot = self._plot_dict[plotName]
        curve = self.addCurve(plot, curveName)
        if not curve:
            print("cancelled")
            return 
        
        self._curve_dict[curve.curveName] = curve

        
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

    @QtCore.pyqtSlot()
    def on_actionRemovePlot_triggered(self):
        print("removing plot")
        items = list(self._plot_dict.keys())
        plotName, ok = QtGui.QInputDialog.getItem(self, "Select plot", "list of plots", items, 0, False)
        if ok:
            plot = self._plot_dict[plotName]
            for curve in plot.curves:
                del self._curve_dict[curve.curveName]
            plot.close()



    @QtCore.pyqtSlot()
    def on_actionRemoveCurve_triggered(self):
        print("removing curve")
        items = list(self._curve_dict.keys())
        curveName, ok = QtGui.QInputDialog.getItem(self, "Select curve", "list of curves", items, 0, False)
        curve = self._curve_dict[curveName]
        for name,plot in self._plot_dict.items():
            if curve in plot.items:
                plot.removeItem(curve)

            del self._curve_dict[curveName]
                
        # parent = curve.parent()
        # parent.removeItem(curve)
        # del self._curve_dict[curveName]

    @QtCore.pyqtSlot()
    def on_actionCurveProperties_triggered(self):
        print("curve properties")

    def setWorkingDirectory(self, working_directory):
        if not os.path.isdir(working_directory):
            return

        self.working_directory = working_directory


    @QtCore.pyqtSlot()
    def on_actionImport_triggered(self):
        print("importing")
        fname = QtGui.QFileDialog.getOpenFileName()
        if os.path.isfile(fname):
            directory = os.path.dirname(fname)
            self.working_directory = directory
            os.chdir(directory)
            self.data.importFromFile(fname)

    @QtCore.pyqtSlot()
    def on_actionExport_triggered(self):
        print("exporting")
        saveFolder = QtGui.QFileDialog.getExistingDirectory(self, "Select Directory", directory=self.working_directory)
        plotNames = self.selectPlotsNames()
        print(plotNames)
        if not plotNames:
            print("no selected plots")
            return

        for pltName in plotNames:
            p = self._plot_dict[pltName]
            p.exportAsImage(pltName, saveFolder)
            # exporter = pg_exp.ImageExporter(p.view)
            # exporter.export(os.path.join(saveFolder,"{0}.png".format(pltName)))

        # items = list(self._plot_dict.keys())
        # plotName, ok = QtGui.QInputDialog.getItem(self, "Select plot", "list of plots", items, 0, False)


    @QtCore.pyqtSlot()
    def on_actionOpenWorkingFolder_triggered(self):
        if self.working_directory:
            open_folder_in_explorer(self.working_directory)
    

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
    
    def selectPlotsNames(self):
        plotNames = list(self._plot_dict.keys())
        dialog = SelectPlotsDialog()
        dialog.setList(plotNames)
        res = dialog.exec_()
        plotList = dialog.getSelectedList()
        return plotList

    def getPlotsToLink(self):
        plotList = self.selectPlotsNames()
        if len(plotList)>1:
            return plotList
        return None
        # print("Plots to link")
        # print(plotList)
        
        

        



def test_ui():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("ExperimentDataAnalysis")
    app.setStyle("cleanlooks")
    
    # plt = pg.PlotWidget()
    # c3 = plt.plot([4,3,2,1], pen=None, symbol='o', symbolPen='y', symbolBrush='r', name="point plot")
    # plt.show()
    # plt = pg.plot()
    # plt.setWindowTitle('pyqtgraph example: Legend')
    # plt.addLegend()

    # c1 = plt.plot([1,3,2,4], pen='r', name='red plot')
    # c2 = plt.plot([2,1,4,3], pen='g', fillLevel=0, fillBrush=(255,255,255,30), name='green plot')
    # c3 = plt.plot([4,3,2,1], pen=None, symbol='o', symbolPen='y', symbolBrush='r', name="point plot", pxMode=False)

    expData = ExperimentData()
    for i in range(10):
        expData.append(generate_meas_data(i))
    
    wnd = ExperimentDataAnalysis()
    wnd.setData(expData)
    # timer = QtCore.QTimer(wnd)
    # timer.setInterval(500)
    # timer.timeout.connect( lambda: expData.append(generate_meas_data(0)))
    # timer.start()

        
        

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
def test():
    from pyfans_analyzer import test_func
    test_func()
    return 0

if __name__== "__main__":
    sys.exit(test())
    # sys.exit(test_ui())
    # sys.exit(test_exp_data())