import sys
import pint
from pint import UnitRegistry

from PyQt4 import uic, QtCore, QtGui

import pyfans.utils.ui_helper as uih

class Settings(uih.NotifyPropertyChanged):
    def __init__(self):
        super().__init__()
        self._automated = False
 
    

    @property
    def automated(self):
        return self._automated

    @automated.setter
    def automated(self, value):
        if self._automated != value:
            self._automated = value
            self.propertyChanged.emit("automated", self, value)
            print("value changed!")
        

mainViewBase, mainViewForm = uic.loadUiType("UI/UI_NoiseMeasurement_v5.ui")
class FANS_UI_MainView(mainViewBase,mainViewForm):
    # ureg = UnitRegistry()
    # voltage_format = "{:8.6f}"
    # resistance_format = "{:.3f}"
    # current_format = "{:.5e}"
    # temperature_format = "{:.2f}"
    # calibrate_before_measurement = uih.bind("ui_calibrate", "checked", bool)
    # overload_reject = uih.bind("ui_overload_reject", "checked", bool)
    # display_refresh = uih.bind("ui_display_refresh", "value", int)
    # simulate_measurement = uih.bind("ui_simulate", "checked", bool)
    # number_of_averages = uih.bind("ui_averages", "value", int)
    # use_homemade_amplifier = uih.bind("ui_use_homemade_amplifier", "checked", bool)
    # second_amplifier_gain = uih.bind("ui_second_amp_coeff", "currentText", int)
    # perform_temperature_measurement = uih.bind("ui_need_meas_temp","checked", bool)
    # current_temperature = uih.bind("ui_current_temp", "text", float, temperature_format)
    # load_resistance = uih.bind("ui_load_resistance", "text", float)
    # perform_measurement_of_gated_structure = uih.bind("ui_meas_gated_structure", "checked", bool)
    # use_dut_selector = uih.bind("ui_use_dut_selector", "checked", bool)
    # use_automated_voltage_control = uih.bind("ui_use_automated_voltage_control", "checked", bool)
    # measurement_characteristic_type = uih.bind("ui_meas_characteristic_type", "currentIndex", int)
    # drain_source_voltage = uih.bind("ui_drain_source_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
    # front_gate_voltage = uih.bind("ui_front_gate_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
    # use_drain_source_range = uih.bind("ui_use_set_vds_range","checked", bool)
    # use_gate_source_range = uih.bind("ui_use_set_vfg_range","checked", bool)
    # sample_voltage_start = uih.bind("ui_sample_voltage_start", "text", float, voltage_format)
    # sample_voltage_end = uih.bind("ui_sample_voltage_end", "text", float, voltage_format)
    # front_gate_voltage_start = uih.bind("ui_front_gate_voltage_start", "text", float, voltage_format)
    # front_gate_voltage_end = uih.bind("ui_front_gate_voltage_end", "text", float, voltage_format)
    # sample_current_start = uih.bind("ui_sample_current_start", "text", float, current_format)
    # sample_current_end = uih.bind("ui_sample_current_end", "text", float, current_format)
    # sample_resistance_start = uih.bind("ui_sample_resistance_start", "text", float,resistance_format)
    # sample_resistance_end = uih.bind("ui_sample_resistance_end", "text", float, resistance_format)
    # experimentName = uih.bind("ui_experimentName", "text", str)
    # measurementName = uih.bind("ui_measurementName", "text", str)
    # measurementCount = uih.bind("ui_measurementCount", "value", int)
    # timetrace_mode = uih.bind("ui_timetrace_mode", "currentIndex", int)
    # timetrace_length = uih.bind("ui_timetrace_length", "value", int)
    # set_zero_after_measurement = uih.bind("ui_set_zero_after_measurement", "checked", bool)
    # valueChanged = QtCore.pyqtSignal(str, object) #str - name of the object, object - new value

    def __init__(self, parent = None):
       super(mainViewBase,self).__init__(parent)
       self.settings = Settings()
       self.setupUi()
       
       
       
    def setupUi(self):
        print("setting the ui up")
        super().setupUi(self)
        self.use_automated_voltage_control = uih.Binding(self.ui_use_automated_voltage_control, "checked", self.settings, "automated")
        

    
        
        
    

def main():
    print("testing binding")

    app = QtGui.QApplication(sys.argv)
    wnd = FANS_UI_MainView()
    wnd.show()
    return app.exec_()