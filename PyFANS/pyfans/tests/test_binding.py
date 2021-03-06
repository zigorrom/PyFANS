import sys
import pint
from pint import UnitRegistry

from PyQt4 import uic, QtCore, QtGui

import pyfans.utils.ui_helper as uih
from pyfans.experiment.fans_experiment_settings import CharacteristicType
from pyfans.main_window import CharacteristicTypeToStrConverter
from pyfans.main_window import FANS_UI_MainView as MainWindow
from pyfans.experiment.fans_experiment_settings import ExperimentSettings

class Settings(uih.NotifyPropertyChanged):
    def __init__(self):
        super().__init__()
        self._automated = True
        self._averages = 15   
        self._dsv = "0.0001 as"
        self._characType = CharacteristicType.Output

    @property
    def automated(self):
        return self._automated

    @automated.setter
    def automated(self, value):
        if self._automated != value:
            self._automated = value
            self.onPropertyChanged("automated", self, value)
            print("automated value changed to {0}!".format(value))
        
    @property
    def averages(self):
        return self._averages

    @averages.setter
    def averages(self, value):
        if self._averages != value:
            self._averages = value
            self.onPropertyChanged("averages", self, value)
            print("averages value changed to {0}!".format(value))

    @property
    def dsv(self):
        return self._dsv

    @dsv.setter
    def dsv(self, value):
        if self._dsv != value:
            self._dsv = value
            self.onPropertyChanged("dsv", self, value)
            print("dsv value changed to {0}!".format(value))

    @property
    def characType(self):
        return self._characType

    @characType.setter
    def characType(self, value):
        if self._characType != value:
            self._characType = value
            self.onPropertyChanged("characType", self, value)
            print("characType value changed to {0}!".format(value))




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
        self.averages = uih.Binding(self.ui_averages,"value", self.settings, "averages", converter=uih.AssureIntConverter())
        self.dsv = uih.Binding(self.ui_drain_source_voltage,"text", self.settings, "dsv", converter=uih.StringToVoltageConverter())
        
        # self.dsv.targetData = 123.456
#drain_source_voltage = uih.bind("ui_drain_source_voltage", "text", uih.string_to_volt_converter(ureg))#, voltage_format) # ureg) #
    
        
        
    


def main():
    print("testing binding")

    app = QtGui.QApplication(sys.argv)
    # wnd = FANS_UI_MainView()
    combobox = QtGui.QComboBox()
    combobox.addItem(CharacteristicType.Transfer.name)
    combobox.addItem(CharacteristicType.Output.name)
    s = Settings()
    comboboxProp = uih.Binding(combobox, "currentText", s,  "characType", converter=CharacteristicTypeToStrConverter())
   
    combobox.show()
    
    lineedit = QtGui.QLineEdit()
    lineeditProp = uih.Binding(lineedit, "text", s,  "dsv", converter=uih.StringToVoltageConverter(), validator=uih.VoltageValidator())
    lineedit.show()
    # wnd.show()
    return app.exec_()


def test_main_window():
    import pickle
    app = QtGui.QApplication(sys.argv)
    wnd = MainWindow()
    exp_setting = ExperimentSettings()
    
    str_pickle = pickle.dumps(exp_setting)
    exp_setting = pickle.loads(str_pickle)
    
    wnd.dataContext = exp_setting
    wnd.experiment_settings = exp_setting
    wnd.showMaximized()
    return app.exec_()
