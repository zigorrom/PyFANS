import pint 
from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore
import ui_helper as uih
import range_handlers as rh


class RangeItem(QtGui.QStandardItem):
    TYPE_NAME = "RANGE ITEM"
    NAME_OPTION = 0
    TYPE_OPTION = 1
    RANGE_START_OPTION = 2
    RANGE_END_OPTION = 3
    RANGE_COUNT_OPTION = 4
    RANGE_STEP_OPTION = 5
    COLUMN_COUNT = 6

    def __init__(self, range_name, rng, **kwargs):
        super().__init__(**kwargs)
        self._range_name = range_name
        if not rng :
            rng = rh.float_range(0,0)
        self._rng = rng

    def columnCount(self):
        return RangeItem.COLUMN_COUNT #(NUMBER OF OPTIONS)

    @property
    def range_item(self):
        return self._rng

    def typeInfo(self):
        return RangeItem.TYPE_NAME

    @classmethod
    def typeInfo(cls):
        return RangeItem.TYPE_NAME

    @property
    def range_name(self):
        return self._range_name

    @property
    def range_start(self):
        return self._rng.start

    @range_start.setter
    def range_start(self, value):
        self._rng.start = value 

    @property
    def range_stop(self):
        return self._rng.stop

    @range_stop.setter
    def range_stop(self, value):
        self._rng.stop = value

    @property
    def count(self):
        return self._rng.length

    @count.setter
    def count(self, value):
        self._rng.length = value

    @property
    def step(self):
        return self._rng.step

    @step.setter
    def step(self, value):
        self._rng.step = value

    def data(self,column):
        #print("getting data col:{0}".format(column))
        if column is RangeItem.NAME_OPTION: return self.range_name
        elif column is RangeItem.TYPE_OPTION: return self.typeInfo()
        elif column is RangeItem.RANGE_START_OPTION: return self.range_start
        elif column is RangeItem.RANGE_END_OPTION: return self.range_stop
        elif column is RangeItem.RANGE_COUNT_OPTION: return self.count
        elif column is RangeItem.RANGE_STEP_OPTION: return self.step
        else: return None
        
    def setData(self,column,value):
        #print("setting data")
        if column is Node.NAME_OPTION: 
            self.range_name=value
            return True
        elif column is Node.TYPE_OPTION: 
            return True
        elif column is RangeItem.RANGE_START_OPTION: 
            self.range_start = value
            return True
        elif column is RangeItem.RANGE_END_OPTION: 
            self.range_stop = value
            return True
        elif column is RangeItem.RANGE_COUNT_OPTION: 
            self.count = value
            return True
        elif column is RangeItem.RANGE_STEP_OPTION: 
            self.step = value
            return True
        else:
            return False




compositeRangeSelectorBase, compositeRangeSelectorForm = uic.loadUiType("UI/UI_RangeSelector_v4.ui")
class CompositeRangeSelectorView(compositeRangeSelectorBase, compositeRangeSelectorForm ):
    def __init__(self, parent = None):
        super(compositeRangeSelectorBase, self).__init__(parent)
        self.setupUi()
        self.model = QtGui.QStandardItemModel(self) #RangeItem.COLUMN_COUNT, self)
        self.model.setItem(0, RangeItem("rng_0", None))
        self.model.setItem(1, RangeItem("rng_1", None))
        self.data_mapper = QtGui.QDataWidgetMapper(self)
        self.setModel(self.model)
        

    def setModel(self, model):
        self.ui_range_list.setModel(model)
        self.data_mapper.setModel(model)
        self.data_mapper.addMapping(self.ui_start_val, RangeItem.RANGE_START_OPTION)
        self.data_mapper.addMapping(self.ui_stop_val, RangeItem.RANGE_END_OPTION)
        self.data_mapper.addMapping(self.ui_count, RangeItem.RANGE_COUNT_OPTION)
        self.data_mapper.addMapping(self.ui_step, RangeItem.RANGE_STEP_OPTION)

        self.ui_range_list.clicked.connect(self.setSelection)

        self.data_mapper.toFirst()

    def setSelection(self, current):
        #parent = current.parent()
        self.data_mapper.setCurrentModelIndex(current)

    def setupUi(self):
        super().setupUi(self)




rangeSelectorBase, rangeSelectorForm = uic.loadUiType("UI/UI_RangeSelector_v3.ui")
class RangeSelectorView(rangeSelectorBase,rangeSelectorForm):
    ureg = UnitRegistry()
    voltage_start = uih.bind("ui_start_val", "text", uih.string_to_volt_converter(ureg))
    voltage_stop = uih.bind("ui_stop_val", "text", uih.string_to_volt_converter(ureg))
    voltage_step = uih.bind("ui_step", "text", uih.string_to_volt_converter(ureg))
    counts = uih.bind("ui_count", "value", int)
    range_handler = uih.bind("ui_range_mode", "currentIndex", int)
    repeats = uih.bind("ui_repeats", "value", int)

    def __init__(self, parent = None):
        super(rangeSelectorBase,self).__init__(parent)
        self.setupUi()
        self._value_range = None
        #self._range_handler = None
        

    def setupUi(self):
        super().setupUi(self)
        self.ui_start_val.setValidator(uih.QVoltageValidator())
        self.ui_stop_val.setValidator(uih.QVoltageValidator())

    def set_range(self, value_range):
        assert isinstance(value_range, rh.RangeObject)
        self._value_range = value_range
        self.refresh_view()

    def get_range(self):
        return self._value_range

    def refresh_view(self):
        if isinstance(self._value_range, rh.RangeObject) and isinstance(self._value_range.floatRange, rh.float_range):
            uih.setAllChildObjectSignaling(self, True)
            self.voltage_start = self._value_range.floatRange.start
            self.voltage_stop = self._value_range.floatRange.stop
            self.voltage_step = self._value_range.floatRange.step
            self.counts = self._value_range.floatRange.length
            self.range_handler = self._value_range.rangeHandler.value
            self.repeats = self._value_range._repeats
            uih.setAllChildObjectSignaling(self, False)

    def refresh_step_count(self):
        if isinstance(self._value_range, rh.RangeObject) and isinstance(self._value_range.floatRange, rh.float_range):
            uih.setAllChildObjectSignaling(self, True)
            self.voltage_step = self._value_range.floatRange.step
            self.counts = self._value_range.floatRange.length
            uih.setAllChildObjectSignaling(self, False)

    @QtCore.pyqtSlot(str)
    def on_ui_start_val_textChanged(self, value):
        if self._value_range:
            val = self.voltage_start
            self._value_range.floatRange.start = val 
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(str)
    def on_ui_stop_val_textChanged(self, value):
        if self._value_range:
            self._value_range.floatRange.stop = self.voltage_stop
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(str)
    def on_ui_count_valueChanged(self, value):
        if self._value_range:
            self._value_range.floatRange.length = self.counts
            self.voltage_step = self._value_range.floatRange.step
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(int)
    def on_ui_range_mode_currentIndexChanged(self, value):
        if self._value_range:
            self._value_range.rangeHandler = rh.RANGE_HANDLERS(value)

    @QtCore.pyqtSlot(int)
    def on_ui_repeats_valueChanged(self, value):
        if self._value_range:
            self._value_range.rangeRepeats = value



def test_RangeSelectorView():
    app = QtGui.QApplication([])
    
    vr = rh.float_range(0,10,0.1)
    ro = rh.RangeObject(vr)
    

    wnd = RangeSelectorView()
    wnd.set_range(ro)
    wnd.exec_()
    return app.exec_()

def test_CompositeRangeSelectorView():
    app = QtGui.QApplication([])
    
    wnd = CompositeRangeSelectorView()
    
    wnd.exec_()
    return app.exec_()


if __name__ == "__main__":
    import sys
    #sys.exit(test_RangeSelectorView())
    sys.exit(test_CompositeRangeSelectorView())