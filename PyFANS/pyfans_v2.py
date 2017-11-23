import sys
from PyQt4 import uic, QtGui, QtCore
import pint
from pint import UnitRegistry
import modern_fans_controller as mfc

def __assert_isinstance_wrapper(function, t):
    def wrapper(self,value):
        assert isinstance(value, t), "expected {0} - received {1}".format(t,type(value))
        return function(self, value)
    return wrapper

def assert_boolean_argument(function):
    return __assert_isinstance_wrapper(function, bool)

def assert_int_or_float_argument(function):
    return __assert_isinstance_wrapper(function,(int,float))

def assert_float_argument(function):
    return __assert_isinstance_wrapper(function, float)

def assert_string_argument(function):
    return __assert_isinstance_wrapper(function, str)

def assert_integer_argument(function):
    return __assert_isinstance_wrapper(function, int)

def assert_list_argument(function):
    return __assert_isinstance_wrapper(function, list)

def assert_tuple_argument(function):
    return __assert_isinstance_wrapper(function, tuple)

def assert_list_or_tuple_argument(function):
    return __assert_isinstance_wrapper(function, (list, tuple))

def has_same_value(a, b):
    return a == b

def get_module_name_and_type(t):
    module = t.__module__
    cls_name = type(t).__name__
    return "{0}.{1}".format(module,cls_name)

def get_value_of_module_type(value, module_type):
    module, t = module_type.split(".")
    mod = sys.modules[module]
    cls = getattr(mod, t)
    return cls(value)


def bind(objectName, propertyName, value_type):#, set_value_type):
    def getter(self):
        return value_type(self.findChild(QtCore.QObject, objectName).property(propertyName))

    def setter(self,value):
        #assert isinstance(value, set_value_type), "expected type {0}, reveiver {1}".format(set_value_type, type(value))
        self.findChild(QtCore.QObject, objectName).setProperty(propertyName, value)

    return property(getter, setter)


class QVoltageValidator(QtGui.QRegExpValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        regex = QtCore.QRegExp("^-?(?:0|[1-9]\d*).?(\d*)\s*(?:[yzafpnumcdhkMGTPEZY])?[V]")   #"(\d+).?(\d*)\s*(m|cm|km)")
        self.setRegExp(regex)



def convert_value_to_volts(ureg, value):
    assert isinstance(ureg, UnitRegistry)
    try:
          v = ureg(value)
          if not isinstance(v,pint.quantity._Quantity):
              v = v * ureg.volt
          print("{0} {1}".format(v.magnitude, v.units))
          v.ito(ureg.volt)
          return v.magnitude
    except:
          print("error while handling value")
          return None

def string_to_volt_converter(ureg):
    def wrapper(value):
       return convert_value_to_volts(ureg, value)
    return wrapper

mainViewBase, mainViewForm = uic.loadUiType("UI_NoiseMeasurement_v3.ui")
class FANS_UI_MainView(mainViewBase,mainViewForm):
    ureg = UnitRegistry()
    calibrate_before_measurement = bind("ui_calibrate", "checked", bool)
    overload_reject = bind("ui_overload_reject", "checked", bool)
    display_refresh = bind("ui_display_refresh", "value", int)
    simulate_measurement = bind("ui_simulate", "checked", bool)
    number_of_averages = bind("ui_averages", "value", int)
    use_homemade_amplifier = bind("ui_use_homemade_amplifier", "checked", bool)
    second_amplifier_gain = bind("ui_second_amp_coeff", "currentText", int)
    perform_temperature_measurement = bind("ui_need_meas_temp","checked", bool)
    current_temperature = bind("ui_current_temp", "text", float)
    load_resistance = bind("ui_load_resistance", "text", float)
    perform_measurement_of_gated_structure = bind("ui_meas_gated_structure", "checked", bool)
    use_dut_selector = bind("ui_use_dut_selector", "checked", bool)
    use_automated_voltage_control = bind("ui_use_automated_voltage_control", "checked", bool)
    measurement_characteristic_type = bind("ui_meas_characteristic_type", "currentIndex", int)
    drain_source_voltage = bind("ui_drain_source_voltage", "text",string_to_volt_converter(ureg))
    front_gate_voltage = bind("ui_front_gate_voltage", "text", string_to_volt_converter(ureg))
    sample_voltage_start = bind("ui_sample_voltage_start", "text", float)
    sample_voltage_end = bind("ui_sample_voltage_end", "text", float)
    front_gate_voltage_start = bind("ui_front_gate_voltage_start", "text", float)
    front_gate_voltage_end = bind("ui_front_gate_voltage_end", "text", float)
    sample_current_start = bind("ui_sample_current_start", "text", float)
    sample_current_end = bind("ui_sample_current_end", "text", float)
    sample_resistance_start = bind("ui_sample_resistance_start", "text", float)
    sample_resistance_end = bind("ui_sample_resistance_end", "text", float)
    experimentName = bind("ui_experimentName", "text", str)
    measurementName = bind("ui_measurementName", "text", str)
    measurementCount = bind("ui_measurementCount", "value", int)

    valueChanged = QtCore.pyqtSignal(str, object) #str - name of the object, object - new value

    def __init__(self, parent = None):
       super(mainViewBase,self).__init__(parent)
       self.setupUi()
       self.init_values()
       self._controller = None
       self.calibrate_before_measurement = True
    
    def setupUi(self):
        print("setting the ui up")
        super().setupUi(self)
        self.ui_current_temp.setValidator(QtGui.QDoubleValidator(notation = QtGui.QDoubleValidator.StandardNotation))
        self.ui_load_resistance.setValidator(QtGui.QIntValidator())
        self.ui_drain_source_voltage.setValidator(QVoltageValidator())
        self.ui_front_gate_voltage.setValidator(QVoltageValidator())

    @property
    def controller(self):
        return self._controller
    
    @controller.setter
    def controller(self,value):
        assert isinstance(value, FANS_UI_Controller)
        self._controller = value
          
    def set_controller(self, controller):
        self.controller = controller

    def init_values(self):
        pass#self._calibrate_before_measurement = False


    #**************
    #event handlers
    #**************
    @QtCore.pyqtSlot()
    def on_ui_open_hardware_settings_clicked(self):
        val = self.calibrate_before_measurement
        self.calibrate_before_measurement = not val
        if val is True:
            self.second_amplifier_gain = 20
        else:
            self.second_amplifier_gain = 100

        self.use_homemade_amplifier = not self.use_homemade_amplifier
        
        
    @QtCore.pyqtSlot(int)
    def on_ui_calibrate_stateChanged(self, value):
        print(self.calibrate_before_measurement)
        print(type(self.calibrate_before_measurement))        

    @QtCore.pyqtSlot(int)
    def on_ui_overload_reject_stateChanged(self, value):
        print("overload rejection")

    def _print_test(self):
        print("test")

    @QtCore.pyqtSlot(int)
    def on_ui_simulate_stateChanged(self,value):
        self._print_test()
       
    @QtCore.pyqtSlot(int)
    def on_ui_averages_valueChanged(self,value):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_use_homemade_amplifier_stateChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_second_amp_coeff_currentIndexChanged(self,value):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_need_meas_temp_stateChanged(self, value):
        self._print_test()
    
    @QtCore.pyqtSlot(str)
    def on_ui_current_temp_textChanged(self, value):
        self._print_test()
        print(self.current_temperature)

    @QtCore.pyqtSlot(str)
    def on_ui_load_resistance_textChanged(self, value):
        self._print_test()
    
    @QtCore.pyqtSlot(int)
    def on_ui_meas_gated_structure_stateChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_use_dut_selector_stateChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot()
    def on_ui_transistorSelector_clicked(self):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_use_automated_voltage_control_stateChanged(self, value):
        self._print_test()
    
    @QtCore.pyqtSlot()
    def on_ui_voltage_control_clicked(self):
        self._print_test()
    
    @QtCore.pyqtSlot(int)
    def on_ui_meas_characteristic_type_currentIndexChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot(str)
    def on_ui_drain_source_voltage_textChanged(self, value):
        self.ui_drain_source_voltage.setToolTip("Vds = {0} V".format(self.drain_source_voltage))
        print(self.drain_source_voltage)
        
    @QtCore.pyqtSlot(int)
    def on_ui_use_set_vds_range_stateChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot()
    def on_VdsRange_clicked(self):
        self._print_test()

    @QtCore.pyqtSlot(str)
    def on_ui_front_gate_voltage_textChanged(self, value):
        self.ui_front_gate_voltage.setToolTip("Vgs = {0} V".format(self.front_gate_voltage))
        print(self.front_gate_voltage)
    
    @QtCore.pyqtSlot(int)
    def on_ui_use_set_vfg_range_stateChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot()
    def on_VfgRange_clicked(self):
        self._print_test()
    
    @QtCore.pyqtSlot()
    def on_folderBrowseButton_clicked(self):
        self._print_test()

    @QtCore.pyqtSlot(str)
    def on_ui_experimentName_textChanged(self, value):
        self._print_test()

    @QtCore.pyqtSlot(str)
    def on_ui_measurementName_textChanged(self,value):
        self._print_test()

    @QtCore.pyqtSlot(int)
    def on_ui_measurementCount_valueChanged(self, value):
        self._print_test() 

    @QtCore.pyqtSlot()
    def on_ui_startButton_clicked(self):
        self.controller.start_experiment()

    @QtCore.pyqtSlot()
    def on_ui_stopButton_clicked(self):
        self.controller.stop_experiment()

    #**************
    #end event handlers
    #**************

    def ui_set_experiment_started(self):
        pass

    def ui_set_experiment_idle(self):
        pass

    def ui_set_experiment_stopped(self):
        pass

    def ui_show_message_in_status_bar(self, timeout):
        pass

    def ui_show_message_in_popup_window(self):
        pass




class FANS_UI_Controller():
    def __init__(self, view):
        assert isinstance(view, FANS_UI_MainView)
        self.main_view = view
        self.main_view.set_controller(self)
        self.settings = None

    def load_settings(self):
        self.settings = AppSettings()

    def start_experiment(self):
        print("start experiment")

    def stop_experiment(selt):
        print("stop experiment")

    def show_main_view(self):
        assert isinstance(self.main_view, FANS_UI_MainView)
        self.main_view.show()

    

class ExperimentSettings():
    def __init__(self):
        #this settings - separate class. shoy\uld be saved to file

        self.__simulate_experiment = None
        self.__working_directory = None
        self.__experiment_name = None
        self.__measurement_name = None
        self.__measurement_count  = None
        self.__calibrate_before_measurement = None
        self.__overload_rejecion = None
        self.__display_refresh = None
        self.__averages = None
        self.__use_homemade_amplifier = None
        self.__homemade_amp_coeff = None
        self.__use_second_amplifier = None
        self.__second_amp_coeff = None
        self.__load_resistance = None
        self.__need_measure_temperature = None
        self.__meas_gated_structure = None
        self.__meas_characteristic_type = None
        self.__use_automated_voltage_control = None
        self.__use_transistor_selector = None
        self.__transistor_list = None
        self.__use_set_vds_range = None
        #self.__vds_range = None
        self.__use_set_vfg_range = None
        #self.__vfg_range = None
        self.__front_gate_voltage = None
        self.__drain_source_voltage = None

   

    #@property
    #def vds_range(self):
    #    return self.__vds_range

    #@vds_range.setter
    #def vds_range(self,value):
    #    self.__vds_range = value

    #@property
    #def vfg_range(self):
    #    return self.__vfg_range

    #@vfg_range.setter
    #def vfg_range(self,value):
    #    self.__vfg_range = value

    @property
    def simulate_experiment(self):
        return self.__simulate_experiment

    @simulate_experiment.setter
    @assert_boolean_argument
    def simulate_experiment(self,value):
        self.__simulate_experiment = value

    @property 
    def use_automated_voltage_control(self):
        return self.__use_automated_voltage_control

    @use_automated_voltage_control.setter
    @assert_boolean_argument
    def use_automated_voltage_control(self, value):
        
        self.__use_automated_voltage_control = value


    @property
    def front_gate_voltage(self):
        return self.__front_gate_voltage

    @front_gate_voltage.setter
    @assert_float_argument
    def front_gate_voltage(self,value):
        self.__front_gate_voltage = value

    @property
    def drain_source_voltage(self):
        return self.__drain_source_voltage

    @drain_source_voltage.setter
    @assert_float_argument
    def drain_source_voltage(self,value):
        self.__drain_source_voltage = value

    @property
    def working_directory(self):
        return self.__working_directory

    @working_directory.setter
    @assert_string_argument
    def working_directory(self,value):
        self.__working_directory = value

    #self.__expeiment_name = None
    @property
    def experiment_name(self):
        return self.__experiment_name

    @experiment_name.setter
    @assert_string_argument
    def experiment_name(self,value):
        self.__experiment_name = value

    #self.__measurement_name = None
    @property
    def measurement_name(self):
        return self.__measurement_name

    @measurement_name.setter
    @assert_string_argument
    def measurement_name(self,value):
        self.__measurement_name = value

    #self.__measurement_count  = 0
    @property
    def measurement_count(self):
        return self.__measurement_count

    @measurement_count.setter
    @assert_integer_argument
    def measurement_count(self,value):
        self.__measurement_count = value    


    #self.__calibrate_before_measurement = False
    @property
    def calibrate_before_measurement(self):
        return self.__calibrate_before_measurement

    @calibrate_before_measurement.setter
    @assert_boolean_argument
    def calibrate_before_measurement(self,value):
        self.__calibrate_before_measurement= value    

    #self.__overload_rejecion = False
    @property
    def overload_rejecion(self):
        return self.__overload_rejecion

    @overload_rejecion.setter
    @assert_boolean_argument
    def overload_rejecion(self,value):
        self.__overload_rejecion= value    

    #self.__display_refresh = 10
    @property
    def display_refresh(self):
        return self.__display_refresh

    @display_refresh.setter
    @assert_integer_argument
    def display_refresh(self,value):
        self.__display_refresh= value    
    #self.__averages = 100
    @property
    def averages(self):
        return self.__averages

    @averages.setter
    @assert_integer_argument
    def averages(self,value):
        self.__averages= value  

    #self.__use_homemade_amplifier = True
    @property
    def use_homemade_amplifier(self):
        return self.__use_homemade_amplifier

    @use_homemade_amplifier.setter
    @assert_boolean_argument
    def use_homemade_amplifier(self,value):
        self.__use_homemade_amplifier= value  


    #self.__homemade_amp_coeff = 178
    @property
    def homemade_amp_coeff(self):
        return self.__homemade_amp_coeff

    @homemade_amp_coeff.setter
    @assert_int_or_float_argument
    def homemade_amp_coeff(self,value):
        self.__homemade_amp_coeff= value  

    #self.__use_second_amplifier = True
    @property
    def use_second_amplifier(self):
        return self.__use_second_amplifier

    @use_second_amplifier.setter
    @assert_boolean_argument
    def use_second_amplifier(self,value):
        self.__use_second_amplifier= value 


    #self.__second_amp_coeff = 100
    @property
    def second_amp_coeff(self):
        return self.__second_amp_coeff

    @second_amp_coeff.setter
    @assert_int_or_float_argument
    def second_amp_coeff(self,value):
        self.__second_amp_coeff= value 

    #self.__load_resistance = 5000
    @property
    def load_resistance(self):
        return self.__load_resistance

    @load_resistance.setter
    @assert_int_or_float_argument
    def load_resistance(self,value):
        self.__load_resistance= value 
        
    #self.__need_measure_temperature = False
    @property
    def need_measure_temperature(self):
        return self.__need_measure_temperature

    @need_measure_temperature.setter
    @assert_boolean_argument
    def need_measure_temperature(self,value):
        self.__need_measure_temperature= value 

    #self.__meas_gated_structure = True
    @property
    def meas_gated_structure(self):
        return self.__meas_gated_structure

    @meas_gated_structure.setter
    @assert_boolean_argument
    def meas_gated_structure(self,value):
        self.__meas_gated_structure= value 
   
    #self.__meas_characteristic_type = 0; # 0 is output 1 is transfer
    @property
    def meas_characteristic_type(self):
        return self.__meas_characteristic_type

    @meas_characteristic_type.setter
    @assert_integer_argument
    def meas_characteristic_type(self,value):
        self.__meas_characteristic_type= value

    #self.__use_transistor_selector = False
    @property
    def use_transistor_selector(self):
        return self.__use_transistor_selector

    @use_transistor_selector.setter
    @assert_boolean_argument
    def use_transistor_selector(self,value):
        self.__use_transistor_selector= value

    #self.__transistor_list = None
    @property
    def transistor_list(self):
        return self.__transistor_list

    @transistor_list.setter
    @assert_list_argument
    def transistor_list(self,value):
        self.__transistor_list= value

    #self.__use_set_vds_range = False
    @property
    def use_set_vds_range(self):
        return self.__use_set_vds_range

    @use_set_vds_range.setter
    @assert_boolean_argument
    def use_set_vds_range(self,value):
        self.__use_set_vds_range= value
    #self.__use_set_vfg_range = False
    @property
    def use_set_vfg_range(self):
        return self.__use_set_vfg_range

    @use_set_vfg_range.setter
    @assert_boolean_argument
    def use_set_vfg_range(self,value):
        self.__use_set_vfg_range= value

class HardwareSettings():
    def __init__(self):
        self._fans_controller_resource = None
        self._sample_motor_channel = None
        self._sample_relay_channel = None
        self._gate_motor_channel = None
        self._gate_relay_channel = None

    @property
    def fans_controller_resource(self):
        return self._fans_controller_resource

    @fans_controller_resource.setter
    def fans_controller_resource(self, value):
        assert isinstance(value, str), "unexpected data type"
        self._fans_controller_resource = value

    @property
    def sample_motor_channel(self):
        return self._sample_motor_channel
    
    @sample_motor_channel.setter
    def sample_motor_channel(self, value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._sample_motor_channel = value

    @property
    def sample_relay_channel(self):
        return self._sample_relay_channel

    @sample_relay_channel.setter
    def sample_relay_channel(self,value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._sample_relay_channel = value

    @property
    def gate_motor_channel(self):
        return self.gate_motor_channel
    
    @gate_motor_channel.setter
    def gate_motor_channel(self, value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._gate_motor_channel = value

    @property
    def gate_relay_channel(self):
        return self._gate_relay_channel

    @gate_relay_channel.setter
    def gate_relay_channel(self, value):
        assert isinstance(value, mfc.FANS_AO_CHANNELS), "unexpected data type"
        self._gate_relay_channel = value

class AppSettings():
    def __init__(self, **kwargs):
        return super().__init__(**kwargs)

def test_ui():
    
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS")
    app.setStyle("cleanlooks")
    app.setWindowIcon(QtGui.QIcon('pyfans.ico'))

    
    wnd = FANS_UI_MainView()
    controller = FANS_UI_Controller(wnd)
    controller.show_main_view()

    return app.exec_()
    
def test_cmd():
    s = ExperimentSettings()
    s.averages = 10
    t =get_module_name_and_type(1)
    print(t)
    v = get_value_of_module_type(6, t)
    print(v)
    return 0



if __name__== "__main__":
    sys.exit(test_ui())
    #sys.exit(test_cmd())


   

    #class QVoltageValidator(QtGui.QDoubleValidator):
#    def __init__(self, **kwargs):
#        super().__init__(**kwargs)
#        self.ureg = UnitRegistry()
#        #(\d+).?(\d*)\s*(m|cm|km)

#    def validate(self, string, position):
#        try:
#            value = self.ureg(string)#.ito(ureg.volt)
#            if isinstance(value, (int,float)):
#                print("{0} volt".format(value))
#            elif isinstance(value, pint.quantity._Quantity):
#                print("{0} {1}".format(value.magnitude, value.units))
                
#        except:
#            res = super().validate(string, position)
#            return res
#        else:
#            return (QtGui.QValidator.Acceptable, string, position)