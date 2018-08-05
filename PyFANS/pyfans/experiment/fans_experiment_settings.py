from enum import Enum
import pyfans.utils.ui_helper as uih
# import range_handlers as rh
import pyfans.ranges.modern_range_editor as mredit 


def assert_characteristic_type(function):
    return uih.__assert_isinstance_wrapper(function, CharacteristicType)

def assert_timetrace_mode_type(function):
    return uih.__assert_isinstance_wrapper(function, TimetraceMode)

class CharacteristicType(Enum):
    Output = 0
    Transfer = 1

class TimetraceMode(Enum):
    NONE = 0
    PARTIAL = 1
    FULL = 2

class ExperimentSettings(uih.NotifyPropertyChanged):
    def __init__(self):
        super().__init__()
        #this settings - separate class. shoy\uld be saved to file
        self.__simulate_experiment = False #None
        self.__working_directory = "F:\\" #None
        self.__experiment_name = "test_exp" #None
        self.__measurement_name = "test_meas"#None
        self.__measurement_count  = 123 #None
        
        self.__calibrate_before_measurement = None
        self.__overload_rejecion = None
        self.__display_refresh = None
        self.__averages = None
        self.__use_homemade_amplifier = None
        self.__homemade_amp_coeff = None
        self.__use_second_amplifier = None
        self.__second_amp_coeff = None
        self.__load_resistance = None
        #self.__use_dut_selector = None

        self.__current_temperature = None
        self.__need_measure_temperature = None
        self.__use_temperature_range = None
        self.__temp_range = None

        
        self.__meas_gated_structure = None
        self.__meas_characteristic_type = None
        self.__use_automated_voltage_control = None
        self.__use_transistor_selector = None
        self.__transistor_list = None
        self.__use_set_vds_range = None
        self.__vds_range = None
        self.__use_set_vfg_range = None
        self.__vfg_range = None
        self.__front_gate_voltage = None
        self.__drain_source_voltage = None
        self.__write_timetrace = None
        self.__set_zero_after_measurement = None
        self.__timetrace_mode = None
        self.__timetrace_length = None
    
    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state
        super().__init__()
   
    @property
    def vds_range(self):
        return self.__vds_range

    @vds_range.setter
    def vds_range(self,value):
        if self.__vds_range == value:
            return

        assert isinstance(value, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo))
        # assert isinstance(value, rh.RangeObject)
        #assert isinstance(value, rh.float_range)
        self.__vds_range = value
        self.onPropertyChanged("vds_range", self, value)

    @property
    def vfg_range(self):
        return self.__vfg_range

    @vfg_range.setter
    def vfg_range(self,value):
        if self.__vfg_range == value:
            return 

        assert isinstance(value, (mredit.RangeInfo, mredit.CenteredRangeInfo, mredit.CustomRangeInfo))
        # assert isinstance(value, rh.RangeObject)
        #assert isinstance(value, rh.float_range)
        self.__vfg_range = value
        self.onPropertyChanged("vfg_range", self, value)
    
    #@property
    #def use_dut_selector(self):
    #    return self.__use_dut_selector

    #@use_dut_selector.setter
    #@uih.assert_boolean_argument
    #def use_dut_selector(self,value):
    #    self.__use_dut_selector = value

    @property
    def current_temperature(self):
        return self.__current_temperature

    @current_temperature.setter
    @uih.assert_int_or_float_argument
    def current_temperature(self, value):
        if self.__current_temperature == value:
            return 

        self.__current_temperature = value
        self.onPropertyChanged("current_temperature", self, value)

    @property
    def simulate_experiment(self):
        return self.__simulate_experiment

    @simulate_experiment.setter
    @uih.assert_boolean_argument
    def simulate_experiment(self,value):
        if self.__simulate_experiment == value:
            return

        self.__simulate_experiment = value
        self.onPropertyChanged("simulate_experiment", self,value)

    @property 
    def use_automated_voltage_control(self):
        return self.__use_automated_voltage_control

    @use_automated_voltage_control.setter
    @uih.assert_boolean_argument
    def use_automated_voltage_control(self, value):
        if self.__use_automated_voltage_control == value:
            return 

        self.__use_automated_voltage_control = value
        self.onPropertyChanged("use_automated_voltage_control", self, value)

    @property
    def front_gate_voltage(self):
        return self.__front_gate_voltage

    @front_gate_voltage.setter
    @uih.assert_int_or_float_argument
    def front_gate_voltage(self,value):
        if self.__front_gate_voltage == value:
            return 

        self.__front_gate_voltage = value
        self.onPropertyChanged("front_gate_voltage", self, value)

    @property
    def drain_source_voltage(self):
        return self.__drain_source_voltage

    @drain_source_voltage.setter
    @uih.assert_int_or_float_argument
    def drain_source_voltage(self,value):
        if self.__drain_source_voltage == value:
            return 

        self.__drain_source_voltage = value
        self.onPropertyChanged("drain_source_voltage", self, value)

    @property
    def working_directory(self):
        return self.__working_directory

    @working_directory.setter
    @uih.assert_string_argument
    def working_directory(self,value):
        if self.__working_directory == value:
            return 

        self.__working_directory = value
        self.onPropertyChanged("working_directory", self, value)

    #self.__expeiment_name = None
    @property
    def experiment_name(self):
        return self.__experiment_name

    @experiment_name.setter
    @uih.assert_string_argument
    def experiment_name(self,value):
        if self.__experiment_name == value:
            return

        self.__experiment_name = value
        self.onPropertyChanged("experiment_name", self, value)

    #self.__measurement_name = None
    @property
    def measurement_name(self):
        return self.__measurement_name

    @measurement_name.setter
    @uih.assert_string_argument
    def measurement_name(self,value):
        if self.__measurement_name == value:
            return

        self.__measurement_name = value
        self.onPropertyChanged("measurement_name", self, value)

    #self.__measurement_count  = 0
    @property
    def measurement_count(self):
        return self.__measurement_count

    @measurement_count.setter
    @uih.assert_integer_argument
    def measurement_count(self,value):
        if self.__measurement_count == value:
            return

        self.__measurement_count = value    
        self.onPropertyChanged("measurement_count", self, value)

        

    @property
    def calibrate_before_measurement(self):
        return self.__calibrate_before_measurement

    @calibrate_before_measurement.setter
    @uih.assert_boolean_argument
    def calibrate_before_measurement(self,value):
        if self.__calibrate_before_measurement == value:
            return

        self.__calibrate_before_measurement= value    
        self.onPropertyChanged("calibrate_before_measurement", self, value)

    @property
    def overload_rejecion(self):
        return self.__overload_rejecion

    @overload_rejecion.setter
    @uih.assert_boolean_argument
    def overload_rejecion(self,value):
        if self.__overload_rejecion == value:
            return

        self.__overload_rejecion= value    
        self.onPropertyChanged("overload_rejection", self, value)

    @property
    def display_refresh(self):
        return self.__display_refresh

    @display_refresh.setter
    @uih.assert_integer_argument
    def display_refresh(self,value):
        if self.__display_refresh == value:
            return

        self.__display_refresh= value    
        self.onPropertyChanged("display_refresh", self, value)

    @property
    def averages(self):
        return self.__averages

    @averages.setter
    @uih.assert_integer_argument
    def averages(self,value):
        if self.__averages == value:
            return

        self.__averages= value  
        self.onPropertyChanged("averages", self, value)

    @property
    def use_homemade_amplifier(self):
        return self.__use_homemade_amplifier

    @use_homemade_amplifier.setter
    @uih.assert_boolean_argument
    def use_homemade_amplifier(self,value):
        if self.__use_homemade_amplifier == value:
            return

        self.__use_homemade_amplifier= value  
        self.onPropertyChanged("use_homemade_amplifier", self, value)

    @property
    def homemade_amp_coeff(self):
        return self.__homemade_amp_coeff

    @homemade_amp_coeff.setter
    @uih.assert_int_or_float_argument
    def homemade_amp_coeff(self,value):
        if self.__homemade_amp_coeff == value:
            return

        self.__homemade_amp_coeff= value  
        self.onPropertyChanged("homemade_amp_coeff", self, value)

    @property
    def use_second_amplifier(self):
        return self.__use_second_amplifier

    @use_second_amplifier.setter
    @uih.assert_boolean_argument
    def use_second_amplifier(self,value):
        if self.__use_second_amplifier == value:
            return

        self.__use_second_amplifier= value 
        self.onPropertyChanged("use_second_amplifier", self, value)

    @property
    def second_amp_coeff(self):
        return self.__second_amp_coeff

    @second_amp_coeff.setter
    @uih.assert_int_or_float_argument
    def second_amp_coeff(self,value):
        if self.__second_amp_coeff == value:
            return

        self.__second_amp_coeff= value 
        self.onPropertyChanged("second_amp_coeff", self, value)

    @property
    def load_resistance(self):
        return self.__load_resistance

    @load_resistance.setter
    @uih.assert_int_or_float_argument
    def load_resistance(self,value):
        if self.__load_resistance == value:
            return

        self.__load_resistance= value 
        self.onPropertyChanged("load_resistance", self, value)

    @property
    def need_measure_temperature(self):
        return self.__need_measure_temperature

    @need_measure_temperature.setter
    @uih.assert_boolean_argument
    def need_measure_temperature(self,value):
        if self.__need_measure_temperature == value:
            return

        self.__need_measure_temperature= value 
        self.onPropertyChanged("need_measure_temperature", self, value)

    @property
    def meas_gated_structure(self):
        return self.__meas_gated_structure

    @meas_gated_structure.setter
    @uih.assert_boolean_argument
    def meas_gated_structure(self,value):
        if self.__meas_gated_structure == value:
            return

        self.__meas_gated_structure= value 
        self.onPropertyChanged("meas_gated_structure", self, value)

  
    @property
    def meas_characteristic_type(self):
        return self.__meas_characteristic_type

    @meas_characteristic_type.setter
    @assert_characteristic_type
    def meas_characteristic_type(self,value):
        if self.__meas_characteristic_type == value:
            return

        self.__meas_characteristic_type= value
        self.onPropertyChanged("meas_characteristic_type", self, value)

    @property
    def use_transistor_selector(self):
        return self.__use_transistor_selector

    @use_transistor_selector.setter
    @uih.assert_boolean_argument
    def use_transistor_selector(self,value):
        if self.__use_transistor_selector == value:
            return 

        self.__use_transistor_selector= value
        self.onPropertyChanged("use_transistor_selector", self, value)

    @property
    def transistor_list(self):
        return self.__transistor_list

    @transistor_list.setter
    @uih.assert_list_argument
    def transistor_list(self,value):
        if self.__transistor_list == value:
            return

        self.__transistor_list= value
        self.onPropertyChanged("transistor_list", self, value)

    @property
    def use_set_vds_range(self):
        return self.__use_set_vds_range

    @use_set_vds_range.setter
    @uih.assert_boolean_argument
    def use_set_vds_range(self,value):
        if self.__use_set_vds_range == value:
            return

        self.__use_set_vds_range= value
        self.onPropertyChanged("use_set_vds_range", self, value)
 
    @property
    def use_set_vfg_range(self):
        return self.__use_set_vfg_range

    @use_set_vfg_range.setter
    @uih.assert_boolean_argument
    def use_set_vfg_range(self,value):
        if self.__use_set_vfg_range == value:
            return

        self.__use_set_vfg_range= value
        self.onPropertyChanged("use_set_vfg_range", self, value)

    #self.__write_timetrace = None
    @property
    def write_timetrace(self):
        return self.__write_timetrace

    @write_timetrace.setter
    @uih.assert_integer_argument
    def write_timetrace(self, value):
        if self.__write_timetrace == value:
            return

        self.__write_timetrace = value
        self.onPropertyChanged("write_timetrace", self, value)

    @property
    def timetrace_mode(self):
        return self.__timetrace_mode

    @timetrace_mode.setter
    @assert_timetrace_mode_type
    def timetrace_mode(self, value):
        if self.__timetrace_mode == value:
            return

        self.__timetrace_mode = value
        self.onPropertyChanged("timetrace_mode", self, value)

    @property
    def timetrace_length(self):
        return self.__timetrace_length

    @timetrace_length.setter
    @uih.assert_integer_argument
    def timetrace_length(self, value):
        if self.__timetrace_length == value:
            return

        self.__timetrace_length = value
        self.onPropertyChanged("timetrace_length", self, value)


    #self.__set_zero_after_measurement = None
    @property
    def set_zero_after_measurement(self):
        return self.__set_zero_after_measurement

    @set_zero_after_measurement.setter
    @uih.assert_boolean_argument
    def set_zero_after_measurement(self, value):
        if self.__set_zero_after_measurement == value:
            return
            
        self.__set_zero_after_measurement = value
        self.onPropertyChanged("set_zero_after_measurement", self, value)

if __name__ == "__main__":
    pass