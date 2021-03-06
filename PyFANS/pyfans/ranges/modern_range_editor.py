﻿import sys
import math
import numpy as np

from enum import Enum
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QDoubleValidator
import pyqtgraph as pg

import pyfans.utils.ui_helper as uih
from pyfans.ranges.forms.UI_RangeSelector_v6 import Ui_RangeSelector

def assert_range_info(obj):
    assert isinstance(obj, (RangeInfo, CenteredRangeInfo, CustomRangeInfo))

class HandlersEnum(Enum):
    normal = 0
    back_forth = 1
    center_start = 2
    center_start_back_forth = 3
    custom = 4

class RangeInfo: #(QtCore.QObject):
    def __init__(self, **kwargs):
        """
        Initializes range info:

        """
        #super().__init__()
        self._start = kwargs.get("start", 0)
        self._end = kwargs.get("end", 0)
        self._step = kwargs.get("step", 0)
        

        self._log_scale = kwargs.get("log_scale", False)
        #self._count = kwargs.get("count", 0)
        self._handler = kwargs.get("handler", HandlersEnum.normal)
        self._repeats = kwargs.get("repeats", 1)
        
    # when handler = zero start -> we start from zero -> move to start ->move to zero -> move to end
    # when handler zero start back and forth -> repeat previous statement in reverse direction

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        self._step = value

    @property
    def log_scale(self):
        return self._log_scale

    @log_scale.setter
    def log_scale(self,value):
        self._log_scale = value

    # @property
    # def count(self):
    #     return self._count

    # @count.setter
    # def count(self, value):
    #     self._count = value

    @property
    def handler(self):
        return self._handler

    @handler.setter
    def handler(self, value):
        self._handler = value

    @property
    def repeats(self):
        return self._repeats

    @repeats.setter
    def repeats(self, value):
        self._repeats = value

    def __str__(self):
        strRepresentation = """
        RangeInfo:
           start:\t{0}
           end:\t{1}
           step:\t{2}
        """.format(self.start, self.end, self.step)
        return strRepresentation
    
class CenteredRangeInfo(RangeInfo):
    def __init__(self,**kwargs):
        self._span = span = kwargs.get("span", None)
        self._center = center = kwargs.get("center", None)
        start = kwargs.setdefault("start",0)
        end = kwargs.setdefault("end", 0)

        if span is not None and center is not None:
            kwargs["start"] = center - span/2
            kwargs["end"] = center + span/2
         
        super().__init__(**kwargs)
    
    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        self._center = value

    @property
    def span(self):
        return self._span

    @span.setter
    def span(self, value):
        self._span = value

    def __str__(self):
        strRepresentation = """
        CenteredRangeInfo:
           start:\t{0}
           end:\t{1}
           step:\t{2}

        """.format(self.start, self.end, self.step)
        return strRepresentation

class CustomRangeInfo:#(QtCore.QObject):
    def __init__(self, *args, **kwargs):
        #super().__init__()
        if isinstance(args[0],(tuple, list)):
            self._list_of_values = args[0]
        elif isinstance(args,(tuple, list)):
            if all(isinstance(x, (int,float)) for x in args):
                self._list_of_values = args
            else:
                self._list_of_values = list()    
        else:
            self._list_of_values = list()

        self._repeats = kwargs.get("repeats", 1)

    @property
    def values(self):
        return self._list_of_values

    @property
    def repeats(self):
        return self._repeats

    @repeats.setter
    def repeats(self, value):
        self._repeats = value

    def __getitem__(self, idx):
        return self._list_of_values[idx]

    def __setitem__(self, idx, value):
        self._list_of_values[idx] = value

    def __len__(self):
        return len(self._list_of_values)

    def __str__(self):
        return self._list_of_values.__str__()

class RangeHandler(QtCore.QObject):
    def __init__(self, rangeInfo):
        super().__init__()
        self._rangeInfo = rangeInfo
        self._currentValue = None
        self._currentCount = 0
        self._currentDirection = 1
        self._currentRepeat = 0
        self._totalIterationsMade = 0

    @property
    def totalIterationsMade(self):
        return self._totalIterationsMade

    def incrementTotalIterations(self):
        self._totalIterationsMade+=1

    @property
    def currentDirection(self):
        return self._currentDirection

    @currentDirection.setter
    def currentDirection(self, value):
        self._currentDirection = value

    def toggleDirection(self):
        self.currentDirection = -self.currentDirection

    @property
    def currentRepeat(self):
        return self._currentRepeat

    @currentRepeat.setter
    def currentRepeat(self, value):
        self._currentRepeat = value

    def incrementRepeat(self):
        self._currentRepeat += 1 #math.copysign(1, self._currentDirection)

    def decrementRepeat(self):
        self._currentRepeat -= 1#math.copysign(1, self._currentDirection)


    @property
    def rangeInfo(self):
        return self._rangeInfo

    @property
    def currentValue(self):
        return self._currentValue

    @currentValue.setter
    def currentValue(self,value):
        self._currentValue = value

    @property
    def currentCount(self):
        return self._currentCount

    @currentCount.setter
    def currentCount(self, value):
        self._currentCount = value

    def incrementCount(self):
        self._currentCount += 1 #math.copysign(1, self._currentDirection)

    def decrementCount(self):
        self._currentCount -= 1#math.copysign(1, self._currentDirection)

    def nextValue(self):
        self._currentValue += math.copysign(self.rangeInfo.step, self._currentDirection)
        return self.currentValue

    def prevValue(self):
        self._currentValue -= math.copysign(self.rangeInfo.step, self._currentDirection)
        return self.currentValue

    def __iter__(self):
        self.reset()
        return self

    def __next__(self):
        return self.next()
        # try:
        #     return iter(self.iterator())
        # except TypeError as te:
        #     print ("some_object is not iterable")
        #     raise

    def checkHitRangeEdge(self, direction, range_edge, current_value):
        if direction >= 0:
            if current_value <= range_edge:
                return False
        else:
            if current_value >= range_edge:
                return False

        return True
        



        # if math.copysign(1,range_edge - current_value) == direction:
        #     return False
        # else:
        #     return True


    def checkCondition(self):   
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()

    def next(self):
        if self.checkCondition():
            current = self.currentValue
            self.nextValue()
            self.incrementCount()
            self.incrementTotalIterations()
            return current
        else:
            raise StopIteration()

class NormalRangeHandler(RangeHandler):
    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, RangeInfo):
            raise TypeError("This range handler supports only RangeInfo ranges")

        super().__init__(rangeInfo)

    def __len__(self):
        try:
            start = self.rangeInfo.start
            end  = self.rangeInfo.end
            step = self.rangeInfo.step
            repeats = self.rangeInfo.repeats
            length = repeats * math.floor(math.fabs(end-start)/step)
            return length

        except Exception:
            return 0

    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True
                    
            elif not self.checkHitRangeEdge(self.currentDirection, self.rangeInfo.end, self.currentValue):
                return True
            
            elif self.__next_repetition():
                return True
            else:
                return False

            # elif self.currentDirection >= 0:
            #     if self.currentValue <= self.rangeInfo.end:
            #         return True
            #     elif self.__next_repetition():
            #         return True
            #     else:
            #         return False

            # else:
            #     if self.currentValue >= self.rangeInfo.end:
            #         return True
            #     elif self.__next_repetition():
            #         return True
            #     else:
            #         return False
             
        return False

    def __initialize_repetition(self):
        self.currentCount = 0
        self.currentDirection = math.copysign(1, self.rangeInfo.end - self.rangeInfo.start)
        self.currentValue = self.rangeInfo.start

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()
        
        if self.currentRepeat < self.rangeInfo.repeats:
            return True
        
        return False

class BackAndForthHandler(RangeHandler):
    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, RangeInfo):
            raise TypeError("This range handler supports only RangeInfo ranges")

        super().__init__(rangeInfo)
        self._directionChanged = False
    
    def __len__(self):
        try:
            start = self.rangeInfo.start
            end  = self.rangeInfo.end
            step = self.rangeInfo.step
            repeats = self.rangeInfo.repeats
            length = repeats*(2*math.floor(math.fabs(end-start)/step)-1)
            return length
            
        except Exception:
            return 0

    @property
    def directionChanged(self):
        return self._directionChanged

    @directionChanged.setter
    def directionChanged(self, value):
        self._directionChanged = value

    def changeDirection(self):
        prev_value = self.directionChanged
        self.directionChanged = True
        self.toggleDirection()
        self.nextValue()
        self.nextValue()
        if not prev_value:
            return True
        
        return False

    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            start_value = self.rangeInfo.start
            end_value = self.rangeInfo.end
            
            

            if self.directionChanged:
                start_value, end_value = end_value, start_value
            
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True
            
            elif not self.checkHitRangeEdge(self.currentDirection, end_value, self.currentValue):
                return True

            elif self.changeDirection():
                return True

            elif self.__next_repetition():
                return True

            else:
                return False
 
        return False

    def __initialize_repetition(self):
        self.currentCount = 0
        self.directionChanged = False
        self.currentDirection = math.copysign(1, self.rangeInfo.end - self.rangeInfo.start)
        self.currentValue = self.rangeInfo.start

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()
        if self.currentRepeat>0:
            self.nextValue()

        if self.currentRepeat < self.rangeInfo.repeats:
            return True

        return False
  
class CenterStartEndRangeHandler(RangeHandler):
    LEFT_SECTION, RIGHT_SECTION = SECTIONS = ("left", "right")

    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, CenteredRangeInfo):
            raise TypeError("This range handler supports only CenteredRangeInfo ranges")

        super().__init__(rangeInfo)
        self._current_section = self.LEFT_SECTION
        
    
    def __len__(self):
        try:
            center = self.rangeInfo.center
            start = self.rangeInfo.start
            end  = self.rangeInfo.end
            step = self.rangeInfo.step
            repeats = self.rangeInfo.repeats
            length = repeats*(math.floor(math.fabs(end-center)/step) + math.floor(math.fabs(start-center)/step))
            return length
            
        except Exception:
            return 0


    @property
    def currentSection(self):
        return self._current_section

    @currentSection.setter
    def currentSection(self, value):
        self._current_section = value
    
    def __condition_function__(self, current_value, start, end, section, direction):
        if not self.checkHitRangeEdge(direction, end, current_value):
            return True

        elif self.__change_to_right_section():
            return True

        elif self.__next_repetition():
            return True
        
        return False

        
    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True

            elif self.currentSection == self.LEFT_SECTION:
                return self.__condition_function__(self.currentValue,self.rangeInfo.center, self.rangeInfo.start, self.currentSection, self.currentDirection)
            
            elif self.currentSection == self.RIGHT_SECTION:
                return self.__condition_function__(self.currentValue,self.rangeInfo.center, self.rangeInfo.end, self.currentSection, self.currentDirection)

            else:
                return False

        return False

    def __change_to_right_section(self):
        if self.currentSection == self.LEFT_SECTION:
            self.currentSection = self.RIGHT_SECTION
            self.currentValue = self.rangeInfo.center
            self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.end)
            # self.nextValue()
            return True

        return False

    def __estimate_direction(self, start, end):
        return math.copysign(1, end - start)

    def __initialize_repetition(self):
        self.currentCount = 0
        self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.start)
        self.currentValue = self.rangeInfo.center
        self.currentSection = self.LEFT_SECTION

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()
        
        if self.currentRepeat < self.rangeInfo.repeats:
            return True
        
        return False  

class CenterStartEndBackForthRangeHandler(RangeHandler):
    LEFT_SECTION, RIGHT_SECTION = SECTIONS = ("left", "right")

    def __init__(self, rangeInfo):
        if not isinstance(rangeInfo, CenteredRangeInfo):
            raise TypeError("This range handler supports only CenteredRangeInfo ranges")

        super().__init__(rangeInfo)
        self._current_section = self.LEFT_SECTION
        self._directionChanged = False


    def __len__(self):
        try:
            center = self.rangeInfo.center
            start = self.rangeInfo.start
            end  = self.rangeInfo.end
            step = self.rangeInfo.step
            repeats = self.rangeInfo.repeats
            length = repeats*(2*math.floor(math.fabs(end-center)/step) + 2*math.floor(math.fabs(start-center)/step)-3 )
            return length
            
        except Exception:
            return 0

    @property
    def directionChanged(self):
        return self._directionChanged

    @directionChanged.setter
    def directionChanged(self, value):
        self._directionChanged = value

    def changeDirection(self):
        prev_value = self.directionChanged
        self.directionChanged = True
        self.toggleDirection()
        self.nextValue()
        self.nextValue()
        if not prev_value:
            return True
        
        return False

    @property
    def currentSection(self):
        return self._current_section

    @currentSection.setter
    def currentSection(self, value):
        self._current_section = value
    
    def __condition_function__(self, current_value, start, end, section, direction):
        if not self.checkHitRangeEdge(direction, end, current_value):
            return True

        elif self.changeDirection():
            return True

        elif self.__change_to_right_section():
            
            return True

        elif self.__next_repetition():
            return True
        
        return False

        
    def checkCondition(self):       
        if self.currentRepeat < self.rangeInfo.repeats:
            
            if self.rangeInfo.step == 0:
                if self.currentCount > 0:
                    if self.__next_repetition():
                        return True
                    else:
                        return False
                else:
                    return True

            elif self.currentSection == self.LEFT_SECTION:
                start_value = self.rangeInfo.center
                end_value = self.rangeInfo.start
                if self.directionChanged:
                    start_value, end_value = end_value, start_value

                return self.__condition_function__(self.currentValue,start_value, end_value, self.currentSection, self.currentDirection)
            
            elif self.currentSection == self.RIGHT_SECTION:
                start_value = self.rangeInfo.center
                end_value = self.rangeInfo.end
                if self.directionChanged:
                    start_value, end_value = end_value, start_value

                return self.__condition_function__(self.currentValue,start_value, end_value, self.currentSection, self.currentDirection)

            else:
                return False

        return False

    def __change_to_right_section(self):
        if self.currentSection == self.LEFT_SECTION:
            self.currentSection = self.RIGHT_SECTION
            # self.currentValue = self.rangeInfo.center
            self.directionChanged = False
            self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.end)
            self.nextValue()
            self.nextValue()
            return True

        return False

    def __estimate_direction(self, start, end):
        return math.copysign(1, end - start)

    def __initialize_repetition(self):
        self.currentCount = 0
        self.currentDirection = self.__estimate_direction(self.rangeInfo.center, self.rangeInfo.start)
        self.currentValue = self.rangeInfo.center
        self.currentSection = self.LEFT_SECTION
        self.directionChanged = False

    def reset(self):
        self.__initialize_repetition()
        self.currentRepeat = 0
        self._totalIterationsMade = 0

    def __next_repetition(self):
        self.incrementRepeat()
        self.__initialize_repetition()

        if self.currentRepeat>0:
            self.nextValue()

        if self.currentRepeat < self.rangeInfo.repeats:
            return True
        
        return False

class CustomRangeHandler(QtCore.QObject):
    def __init__(self, rangeInfo):
        super().__init__()
        self._rangeInfo = rangeInfo
        self.reset()
        # self._totalIterationsMade = 0
        # self._currentRepeat = 0
        # self._currentIndex = 0
     
    @property
    def currentRepeat(self):
        return self._currentRepeat

    @currentRepeat.setter
    def currentRepeat(self, value):
        self._currentRepeat = value
 
    def incrementRepeat(self):
        self._currentRepeat += 1 #math.copysign(1, self._currentDirection)
        return self._currentRepeat

    def decrementRepeat(self):
        self._currentRepeat -= 1#math.copysign(1, self._currentDirection)
        return self._currentRepeat

    @property
    def currentIndex(self):
        return self._currentIndex

    @currentIndex.setter
    def currentIndex(self, value):
        self._currentIndex = value

    def incrementIndex(self):
        self._currentIndex += 1
        return self._currentIndex

    def decrementIndex(self):
        self._currentIndex -= 1
        return self._currentIndex

    @property
    def totalIterationsMade(self):
        return len(self._rangeInfo)

    def incrementTotalIterations(self):
        self._totalIterationsMade+=1

    @property
    def rangeInfo(self):
        return self._rangeInfo

    def __len__(self):
        return self.rangeInfo.repeats * len(self.rangeInfo.values)

    def reset(self):
        self._totalIterationsMade = 0
        self._currentRepeat = 0
        self._currentIndex = 0

    def __next__(self):
            if self.currentRepeat >= self.rangeInfo.repeats:
                raise StopIteration()
            
            length_of_list = len(self.rangeInfo.values)
            
            if self.currentIndex < length_of_list:
                value = self.rangeInfo.values[self.currentIndex]
                self.incrementIndex()
                self.incrementTotalIterations()
                return value

            elif self.incrementRepeat() < self.rangeInfo.repeats:
                self.currentIndex = 0
                value = self.rangeInfo.values[self.currentIndex]
                self.incrementIndex()
                self.incrementTotalIterations()
                return value

            else:
                raise StopIteration()



    def __iter__(self):
        self.reset()
        return self #iter(self.rangeInfo.values)



class RangeHandlerFactory(QtCore.QObject):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def createHandler(rangeInfo):
        if isinstance(rangeInfo, RangeInfo):
            if rangeInfo.handler is HandlersEnum.normal:
                return NormalRangeHandler(rangeInfo)

            elif rangeInfo.handler is HandlersEnum.back_forth:
                return BackAndForthHandler(rangeInfo)

            elif rangeInfo.handler is HandlersEnum.center_start:
                return CenterStartEndRangeHandler(rangeInfo)
                #return ZeroStartRangeHandler(rangeInfo)

            elif rangeInfo.handler is HandlersEnum.center_start_back_forth:
                return CenterStartEndBackForthRangeHandler(rangeInfo)
                #return ZeroStartBackAndForthRangeHandler(rangeInfo)

            else:
                raise ValueError("handler is not specified in range info")

        elif isinstance(rangeInfo, CustomRangeInfo):
            return CustomRangeHandler(rangeInfo)

        else:
            raise TypeError("rangeInfo has wrong data type")



# RangeEditorBase, RangeEditorForm = uic.loadUiType("UI/UI_RangeSelector_v6.ui")
# class RangeEditorView(RangeEditorBase, RangeEditorForm):
class RangeEditorView(QtGui.QDialog, Ui_RangeSelector):
    rangeStart = uih.bind("ui_start_val", "text", float)
    rangeEnd = uih.bind("ui_stop_val", "text", float)
    rangeStep = uih.bind("ui_step_val", "text", float)
    rangeCenter = uih.bind("ui_center_val", "text", float)
    rangeSpan = uih.bind("ui_span_val", "text", float)
    # rangeRepeats = uih.bind("ui_range_repeats", "value", int)

    def __init__(self, parent = None):
        # super(RangeEditorBase, self).__init__(parent)
        super().__init__(parent)
        self._composed_range_view = False
        

        self.setupUi()
        

    def setupUi(self):
        super().setupUi(self)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowContextHelpButtonHint)

        self.ui_normal_handler.setChecked(True)
        self.ui_composed_handler.setChecked(False)
        self.ui_normal_handler.toggled.connect(self.on_composite_view_changed)
        self.ui_composed_handler.toggled.connect(self.on_composite_view_changed)
        self.ui_composite_ranges.hide()
        
        self.ui_handler_selector.currentIndexChanged.connect(self.on_range_handler_changed)
        self.ui_span_mode.stateChanged.connect(self.on_span_mode_changed)
        
        self.ui_span_mode.setChecked(False)
        self.ui_span_mode.hide()
        self.on_span_mode_changed(0)
        
        self.ui_view_range_dock.hide()

        self.rangeMode = HandlersEnum.normal
        self.adjustSize()

        self.ui_start_val.setValidator(QDoubleValidator())
        self.ui_stop_val.setValidator(QDoubleValidator())
        self.ui_step_val.setValidator(QDoubleValidator())
        self.ui_center_val.setValidator(QDoubleValidator())
        self.ui_span_val.setValidator(QDoubleValidator())
        
        self.plot = self.ui_range_plot.addPlot()
        self.range_curve = self.plot.plot(pen=pg.mkPen(color="r",width=2),symbolPen = pg.mkPen(color="r",width=1), symbolBrush="r", symbol='o', size= 0, pxMode=True ) #pg.ScatterPlotItem()#size=10, pen=pg.mkPen('r'))
        # self.plot.setLabel("left", "<font size=\"5\">Value</font>")#, units="<font size=\"15\">V^2Hz-1</font>")
        # self.plot.setLabel("bottom", "<font size=\"5\">Index</font>")#, units="Hz")
        self.plot.getAxis("left").setWidth(20)
        self.plot.showAxis("right", show=True)
        self.plot.showAxis("top", show=True)
        self.plot.getAxis("right").setStyle(showValues = False)
        self.plot.getAxis("top").setStyle(showValues = False)
        # self.plot.addItem(self.scatterPlot)
        
        
        
        #ui_range_plot
    @QtCore.pyqtSlot(bool)
    def on_ui_view_range_dock_visibilityChanged(self, value):
        self.adjustSize()

        
    @QtCore.pyqtSlot()
    def on_ui_add_custom_value_clicked(self):
        print("adding value")
        try:
            value_str = self.ui_custom_value_to_add.text()
            value = float(value_str)
            self.ui_list_of_values.addItem(value_str)
            self.ui_custom_value_to_add.setFocus()
            self.ui_custom_value_to_add.clear()
        except:
            print("value is empty")
            self.ui_custom_value_to_add.setFocus()
        
    def add_values_to_custom_view(self, values):
        for value in values:
            if isinstance(value, (int, float)):
                self.ui_list_of_values.addItem(str(value))
        
        
    @QtCore.pyqtSlot()
    def on_ui_add_range_button_clicked(self):
        print("adding range")
        wnd = RangeEditorView()
        res = wnd.exec_()
        if res:
            ri = wnd.generateRangeInfo()
            rh = RangeHandlerFactory.createHandler(ri)
            lst = list(rh)
            self.add_values_to_custom_view(lst)
            print(lst)

    @QtCore.pyqtSlot()
    def on_ui_remove_custom_value_clicked(self):
        print("removing value")
        for item in self.ui_list_of_values.selectedItems():
            self.ui_list_of_values.takeItem(self.ui_list_of_values.row(item))
            
    @QtCore.pyqtSlot()
    def on_ui_clear_custom_value_clicked(self):
        self.ui_list_of_values.clear()
        self.ui_custom_value_to_add.setFocus()

    @QtCore.pyqtSlot()
    def on_ui_view_range_clicked(self):
        print("viewving range")
        self.ui_view_range_dock.show()

        ri = self.generateRangeInfo()
        rh = RangeHandlerFactory.createHandler(ri)
        
        dataList = list(rh)
        indexes = range(len(dataList))
        
        print(dataList)
        # self.scatterPlot.clear()
        self.range_curve.setData(indexes, dataList)
        

    @property
    def compositeRange(self):
        return self.ui_composed_handler.isChecked()

    @property
    def selectedHandlerIndex(self):
        return self.ui_handler_selector.currentIndex()
    
    @selectedHandlerIndex.setter
    def selectedHandlerIndex(self,value):
        self.ui_handler_selector.setCurrentIndex(value)

    @property
    def customListOfValues(self):
        values = [float(self.ui_list_of_values.item(i).text()) for i in range(self.ui_list_of_values.count()) ]

        return values

    @property
    def rangeMode(self):
        if  self.selectedHandlerIndex is 0:
            return HandlersEnum.normal
        
        elif self.selectedHandlerIndex is 1:
            return HandlersEnum.back_forth

        elif self.selectedHandlerIndex is 2:
            return HandlersEnum.center_start

        elif self.selectedHandlerIndex is 3:
            return HandlersEnum.center_start_back_forth

        elif self.selectedHandlerIndex is 4:
            return HandlersEnum.custom
        
        else:
            return None

    @rangeMode.setter
    def rangeMode(self, value):
        print("setting range mode to {0}".format(value))
        if value is HandlersEnum.back_forth:
            print("back forth")
            self.selectedHandlerIndex = 1

        elif value is HandlersEnum.center_start:
            print("center start")
            self.selectedHandlerIndex = 2

        elif value is HandlersEnum.center_start_back_forth:
            print("center start back forth")
            self.selectedHandlerIndex = 3

        elif value is HandlersEnum.custom:
            print("custom")
            self.selectedHandlerIndex = 4

        else:
            print("normal")
            self.selectedHandlerIndex = 0

    @property
    def spanMode(self):
        return self.ui_span_mode.isChecked()
            
    @property
    def rangeRepeats(self):
        return self.ui_range_repeats.value()

    @rangeRepeats.setter
    def rangeRepeats(self, value):
        self.ui_range_repeats.setValue(value)
    

    def accept(self):
        print("accepted")
        
        super().accept()

    def closeEvent(self, event):
        self.reject()

    @QtCore.pyqtSlot(bool)
    def on_composite_view_changed(self, bool):
        if self.ui_normal_handler.isChecked():
            self.ui_composite_ranges.hide()
        elif self.ui_composed_handler.isChecked():
            self.ui_composite_ranges.show()

    @QtCore.pyqtSlot(int)
    def on_span_mode_changed(self, state):
        self.on_range_handler_changed(self.selectedHandlerIndex)
       

    def setRangeViewVisible(self, centered=False, span=False):
        if not centered:
            span = False
        self.ui_start_label.setVisible(not span)
        self.ui_start_val.setVisible(not span)
        self.ui_stop_label.setVisible(not span)
        self.ui_stop_val.setVisible(not span)
        self.ui_span_label.setVisible(span)
        self.ui_span_val.setVisible(span)
        self.ui_center_label.setVisible(centered)
        self.ui_center_val.setVisible(centered)
        self.ui_step_label.setVisible(True)
        self.ui_step_val.setVisible(True)


    

    @QtCore.pyqtSlot(int)
    def on_range_handler_changed(self, idx):
        print("handler changed")
        if idx > 1 and idx <4:
            self.ui_span_mode.show()
        else:
            self.ui_span_mode.hide()
        
        if idx is 0 or idx is 1:
            self.ui_normal_range_info.show()
            self.setRangeViewVisible(False,False)
            self.ui_custom_list_view.hide()

        elif idx is 2 or idx is 3:
            self.ui_normal_range_info.show()
            self.setRangeViewVisible(True,self.spanMode)
            self.ui_custom_list_view.hide()

        elif idx is 4:
            self.ui_normal_range_info.hide()
            self.ui_custom_list_view.show()
        else:
            pass
        self.adjustSize()

    def setRange(self, rangeInfo):
        try:
            if isinstance(rangeInfo, CustomRangeInfo):
                # add_values_to_custom_view
                self.rangeMode = HandlersEnum.custom
                self.add_values_to_custom_view(rangeInfo.values)
                self.rangeRepeats = rangeInfo.repeats

            elif isinstance(rangeInfo, CenteredRangeInfo):
                if rangeInfo.span is None:
                    self.rangeStart = rangeInfo.start
                    self.rangeEnd  = rangeInfo.end
                    self.rangeStep = rangeInfo.step
                    self.rangeCenter = rangeInfo.center
                    self.rangeRepeats = rangeInfo.repeats

                else:
                    self.rangeSpan = rangeInfo.span
                    self.rangeStart = rangeInfo.start
                    self.rangeEnd  = rangeInfo.end
                    self.rangeStep = rangeInfo.step
                    self.rangeCenter = rangeInfo.center
                    self.rangeRepeats = rangeInfo.repeats
                
                self.rangeMode = rangeInfo.handler

            elif isinstance(rangeInfo, RangeInfo):
                self.rangeStart = rangeInfo.start
                self.rangeEnd  = rangeInfo.end
                self.rangeStep = rangeInfo.step
                self.rangeRepeats = rangeInfo.repeats
                self.rangeMode = rangeInfo.handler
                

        except Exception:
            self.rangeStart = rangeInfo.start
            self.rangeEnd  = rangeInfo.end
            self.rangeStep = rangeInfo.step
            self.rangeRepeats = rangeInfo.repeats
            self.rangeMode = HandlersEnum.normal
            

   
    def generateRangeInfo(self):
        try:
            mode = self.rangeMode
            if mode is HandlersEnum.normal or mode is HandlersEnum.back_forth:
                return RangeInfo(start=self.rangeStart, end=self.rangeEnd , step=self.rangeStep, handler=mode, repeats=self.rangeRepeats)
                # rngInfo = 

            elif mode is HandlersEnum.center_start or mode is HandlersEnum.center_start_back_forth:
                if self.spanMode:
                    return CenteredRangeInfo(span=self.rangeSpan, center=self.rangeCenter,step=self.rangeStep, handler=mode, repeats=self.rangeRepeats)

                else:
                    return CenteredRangeInfo(start=self.rangeStart, end=self.rangeEnd, center=self.rangeCenter,step=self.rangeStep, handler=mode, repeats=self.rangeRepeats)

            elif mode is HandlersEnum.custom:
                
                return CustomRangeInfo(self.customListOfValues, repeats=self.rangeRepeats)

            else:
                return None
        except Exception as e:
            print("exception occured while generating the range")
            return None



def test_smth():
    class firstn(object):
        def __init__(self, n):
            self.n = n
            self.num, self.nums = 0, []

        def __iter__(self):
            return self

        # Python 3 compatibility
        def __next__(self):
            return self.next()

        def next(self):
            if self.num < self.n:
                cur, self.num = self.num, self.num+1
                return cur
            else:
                raise StopIteration()

    sum_of_first_n = sum(firstn(1000000))
    print(sum_of_first_n)
    sum_of_first_n = sum(firstn(1000))
    print(sum_of_first_n)


def test_range():
    # ri = RangeInfo(start=-3, end=3, step=1, handler=HandlersEnum.normal, repeats=2)
    # print(ri)
    # print("NORMAL HANDLER")
    # rh = RangeHandlerFactory.createHandler(ri)
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)

    # print("Back Forth HANDLER")
    # ri.handler = HandlersEnum.back_forth
    # ri.repeats = 2
    # rh = RangeHandlerFactory.createHandler(ri)
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)
    
    # print("Center start Handler")
    # ri = CenteredRangeInfo(start=-3, end=3, center=1, step=1, handler=HandlersEnum.center_start, repeats=2)
    # rh = RangeHandlerFactory.createHandler(ri)
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)

    # print("Center start back forth Handler SPAN")
    # ri = CenteredRangeInfo(span = 6, center=1, step=1, handler=HandlersEnum.center_start_back_forth, repeats=2)#start=-2, end=2
    # rh = RangeHandlerFactory.createHandler(ri)
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)

    # print("Center start back forth Handler START-STOP")
    # ri = CenteredRangeInfo(start=-3, end=3, center=1, step=1, handler=HandlersEnum.center_start_back_forth, repeats=2)#start=-2, end=2
    # rh = RangeHandlerFactory.createHandler(ri)
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)


    # print("Custom range handler")
    # ri = CustomRangeInfo(1,2,3,4,5, repeats=4)
    # rh = RangeHandlerFactory.createHandler(ri)
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)

    print("Custom range handler")
    ri = CustomRangeInfo(1,2,3,4,5, repeats=4)
    rh = RangeHandlerFactory.createHandler(ri)
    for idx, i  in enumerate(rh):
        print("i={0}; val={1}".format(idx, i))
    # lst = list(rh)
    # print(lst)
    # print(rh.totalIterationsMade)


def test_ui():
    app = QtGui.QApplication([])
    wnd = RangeEditorView()
    ri = RangeInfo(start=-3, end=3, step=1, handler=HandlersEnum.normal, repeats=2)
    # ri = RangeInfo(start=-3, end=3, step=1, handler=HandlersEnum.back_forth, repeats=2)
    #ri = CenteredRangeInfo(start=-3, end=3, center=1, step=1, handler=HandlersEnum.center_start, repeats=2)
    # ri = CenteredRangeInfo(span = 6, center=1, step=1, handler=HandlersEnum.center_start_back_forth, repeats=2)
    # ri = CenteredRangeInfo(start=-3, end=3, center=1, step=1, handler=HandlersEnum.center_start_back_forth, repeats=2)

    wnd.setRange(ri)
    res = wnd.exec_()
    # wnd.close()
    if res:
        print("after closing")
        print(res)
        ri = wnd.generateRangeInfo()
        rh = RangeHandlerFactory.createHandler(ri)
        lst = list(rh)
        print(lst)
        print(rh.totalIterationsMade)
    else:
        print("cancelled")
    # return app.exec_()

if __name__ == "__main__":
    # sys.exit(test_range())
    sys.exit(test_ui())
    # test_smth()

    
