import pint 
from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore
import ui_helper as uih
import range_handlers as rh

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



if __name__ == "__main__":
    app = QtGui.QApplication([])
    
    vr = rh.float_range(0,10,0.1)
    ro = rh.RangeObject(vr)
    

    wnd = RangeSelectorView()
    wnd.set_range(ro)
    wnd.exec_()
    #return app.exec_()