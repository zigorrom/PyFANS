import pint 
from pint import UnitRegistry
from PyQt4 import uic, QtGui, QtCore
import ui_helper as uih
import range_handlers as rh

rangeSelectorBase, rangeSelectorForm = uic.loadUiType("UI_RangeSelector_v3.ui")
class RangeSelectorView(rangeSelectorBase,rangeSelectorForm):
    ureg = UnitRegistry()
    voltage_start = uih.bind("ui_start_val", "text", uih.string_to_volt_converter(ureg))
    voltage_stop = uih.bind("ui_stop_val", "text", uih.string_to_volt_converter(ureg))
    voltage_step = uih.bind("ui_step", "text", uih.string_to_volt_converter(ureg))
    counts = uih.bind("ui_count", "value", int)


    def __init__(self, parent = None):
        super(rangeSelectorBase,self).__init__(parent)
        self.setupUi()
        self._value_range = None

    def setupUi(self):
        super().setupUi(self)
        self.ui_start_val.setValidator(uih.QVoltageValidator())
        self.ui_stop_val.setValidator(uih.QVoltageValidator())

    def set_range(self, value_range):
        assert isinstance(value_range, rh.float_range)
        self._value_range = value_range
        self.refresh_view()

    def get_range(self):
        return self._value_range

    def refresh_view(self):
        if self._value_range:
            uih.setAllChildObjectSignaling(self, True)
            self.voltage_start = self._value_range.start
            self.voltage_stop = self._value_range.stop
            self.voltage_step = self._value_range.step
            self.counts = self._value_range.length
            uih.setAllChildObjectSignaling(self, False)

    def refresh_step_count(self):
        if self._value_range:
            uih.setAllChildObjectSignaling(self, True)
            self.voltage_step = self._value_range.step
            self.counts = self._value_range.length
            uih.setAllChildObjectSignaling(self, False)

    @QtCore.pyqtSlot(str)
    def on_ui_start_val_textChanged(self, value):
        if self._value_range:
            val = self.voltage_start
            self._value_range.start = val 
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(str)
    def on_ui_stop_val_textChanged(self, value):
        if self._value_range:
            self._value_range.stop = self.voltage_stop
            #self.refresh_view()
            self.refresh_step_count()

    @QtCore.pyqtSlot(str)
    def on_ui_count_valueChanged(self, value):
        if self._value_range:
            self._value_range.length = self.counts
            self.voltage_step = self._value_range.step
            #self.refresh_view()
            self.refresh_step_count()

if __name__ == "__main__":
    app = QtGui.QApplication([])
    vr = rh.float_range(0,10,0.1)
    wnd = RangeSelectorView()
    wnd.set_range(vr)
    wnd.exec_()
    #return app.exec_()