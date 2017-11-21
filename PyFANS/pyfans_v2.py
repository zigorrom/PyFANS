import sys
from PyQt4 import uic, QtGui, QtCore

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



mainViewBase, mainViewForm = uic.loadUiType("UI_NoiseMeasurement_v2.ui")
class FANS_UI_MainView(mainViewBase,mainViewForm):
    def __init__(self, parent = None, controller = None):
       super(mainViewBase,self).__init__(parent)
       self.setupUi(self)
       self.init_values()
       self.connect_slots()
       assert isinstance(controller, FANS_UI_Controller), "unsuitable controller class"
       self._controller = controller
       self.calibrate_before_measurement = True
       
    def init_values(self):
        self._calibrate_before_measurement = False

    def connect_slots(self):
       self.ui_calibrate.stateChanged.connect(self._on_calibrate_before_measurement_value_changed)



    @property
    def controller(self):
        return self._controller

    def _on_calibrate_before_measurement_value_changed(self, value):
        if value == QtCore.Qt.Checked:
            self._calibrate_before_measurement = True
        else:
            self._calibrate_before_measurement = False

    @property
    def calibrate_before_measurement(self):
        return self._calibrate_before_measurement

    @calibrate_before_measurement.setter
    @assert_boolean_argument
    def calibrate_before_measurement(self, value):
        if self.calibrate_before_measurement != value:
            self._calibrate_before_measurement = value
            self.ui_calibrate.setChecked(value)



class FANS_UI_Controller():
    def __init__(self):
        pass


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



class HardwareSettingsModel():
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






def test_ui():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("PyFANS")
    app.setStyle("cleanlooks")
    app.setWindowIcon(QtGui.QIcon('pyfans.ico'))

    #css = "QLineEdit#sample_voltage_start {background-color: yellow}"
    #app.setStyleSheet(css)
    #sample_voltage_start
    controller = FANS_UI_Controller()
    wnd = FANS_UI_MainView(controller = controller)
    wnd.show()

    return app.exec_()
    
def test_cmd():
    s = ExperimentSettings()
    s.averages = 10
    t =get_module_name_and_type(mfc.FANS_AI_CHANNELS.AI_CH_1)
    print(t)
    v = get_value_of_module_type(8, t)
    print(v)
    return 0



if __name__== "__main__":
    #sys.exit(test_ui())
    sys.exit(test_cmd())


   

    