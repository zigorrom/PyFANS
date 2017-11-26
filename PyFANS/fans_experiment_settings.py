import ui_helper as uih
import range_handlers as rh

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
        #self.__use_dut_selector = None
        self.__need_measure_temperature = None
        self.__current_temperature = None
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

    @property
    def vds_range(self):
        return self.__vds_range

    @vds_range.setter
    def vds_range(self,value):
        assert isinstance(value, rh.float_range)
        self.__vds_range = value

    @property
    def vfg_range(self):
        return self.__vfg_range

    @vfg_range.setter
    def vfg_range(self,value):
        assert isinstance(value, rh.float_range)
        self.__vfg_range = value
    
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
        self.__current_temperature = value

    @property
    def simulate_experiment(self):
        return self.__simulate_experiment

    @simulate_experiment.setter
    @uih.assert_boolean_argument
    def simulate_experiment(self,value):
        self.__simulate_experiment = value

    @property 
    def use_automated_voltage_control(self):
        return self.__use_automated_voltage_control

    @use_automated_voltage_control.setter
    @uih.assert_boolean_argument
    def use_automated_voltage_control(self, value):
        self.__use_automated_voltage_control = value

    @property
    def front_gate_voltage(self):
        return self.__front_gate_voltage

    @front_gate_voltage.setter
    @uih.assert_float_argument
    def front_gate_voltage(self,value):
        self.__front_gate_voltage = value

    @property
    def drain_source_voltage(self):
        return self.__drain_source_voltage

    @drain_source_voltage.setter
    @uih.assert_float_argument
    def drain_source_voltage(self,value):
        self.__drain_source_voltage = value

    @property
    def working_directory(self):
        return self.__working_directory

    @working_directory.setter
    @uih.assert_string_argument
    def working_directory(self,value):
        self.__working_directory = value

    #self.__expeiment_name = None
    @property
    def experiment_name(self):
        return self.__experiment_name

    @experiment_name.setter
    @uih.assert_string_argument
    def experiment_name(self,value):
        self.__experiment_name = value

    #self.__measurement_name = None
    @property
    def measurement_name(self):
        return self.__measurement_name

    @measurement_name.setter
    @uih.assert_string_argument
    def measurement_name(self,value):
        self.__measurement_name = value

    #self.__measurement_count  = 0
    @property
    def measurement_count(self):
        return self.__measurement_count

    @measurement_count.setter
    @uih.assert_integer_argument
    def measurement_count(self,value):
        self.__measurement_count = value    

    @property
    def calibrate_before_measurement(self):
        return self.__calibrate_before_measurement

    @calibrate_before_measurement.setter
    @uih.assert_boolean_argument
    def calibrate_before_measurement(self,value):
        self.__calibrate_before_measurement= value    

    @property
    def overload_rejecion(self):
        return self.__overload_rejecion

    @overload_rejecion.setter
    @uih.assert_boolean_argument
    def overload_rejecion(self,value):
        self.__overload_rejecion= value    

    @property
    def display_refresh(self):
        return self.__display_refresh

    @display_refresh.setter
    @uih.assert_integer_argument
    def display_refresh(self,value):
        self.__display_refresh= value    

    @property
    def averages(self):
        return self.__averages

    @averages.setter
    @uih.assert_integer_argument
    def averages(self,value):
        self.__averages= value  

    @property
    def use_homemade_amplifier(self):
        return self.__use_homemade_amplifier

    @use_homemade_amplifier.setter
    @uih.assert_boolean_argument
    def use_homemade_amplifier(self,value):
        self.__use_homemade_amplifier= value  

    @property
    def homemade_amp_coeff(self):
        return self.__homemade_amp_coeff

    @homemade_amp_coeff.setter
    @uih.assert_int_or_float_argument
    def homemade_amp_coeff(self,value):
        self.__homemade_amp_coeff= value  

    @property
    def use_second_amplifier(self):
        return self.__use_second_amplifier

    @use_second_amplifier.setter
    @uih.assert_boolean_argument
    def use_second_amplifier(self,value):
        self.__use_second_amplifier= value 

    @property
    def second_amp_coeff(self):
        return self.__second_amp_coeff

    @second_amp_coeff.setter
    @uih.assert_int_or_float_argument
    def second_amp_coeff(self,value):
        self.__second_amp_coeff= value 

    @property
    def load_resistance(self):
        return self.__load_resistance

    @load_resistance.setter
    @uih.assert_int_or_float_argument
    def load_resistance(self,value):
        self.__load_resistance= value 

    @property
    def need_measure_temperature(self):
        return self.__need_measure_temperature

    @need_measure_temperature.setter
    @uih.assert_boolean_argument
    def need_measure_temperature(self,value):
        self.__need_measure_temperature= value 

    @property
    def meas_gated_structure(self):
        return self.__meas_gated_structure

    @meas_gated_structure.setter
    @uih.assert_boolean_argument
    def meas_gated_structure(self,value):
        self.__meas_gated_structure= value 
  
    @property
    def meas_characteristic_type(self):
        return self.__meas_characteristic_type

    @meas_characteristic_type.setter
    @uih.assert_integer_argument
    def meas_characteristic_type(self,value):
        self.__meas_characteristic_type= value

    @property
    def use_transistor_selector(self):
        return self.__use_transistor_selector

    @use_transistor_selector.setter
    @uih.assert_boolean_argument
    def use_transistor_selector(self,value):
        self.__use_transistor_selector= value

    @property
    def transistor_list(self):
        return self.__transistor_list

    @transistor_list.setter
    @uih.assert_list_argument
    def transistor_list(self,value):
        self.__transistor_list= value

    @property
    def use_set_vds_range(self):
        return self.__use_set_vds_range

    @use_set_vds_range.setter
    @uih.assert_boolean_argument
    def use_set_vds_range(self,value):
        self.__use_set_vds_range= value
 
    @property
    def use_set_vfg_range(self):
        return self.__use_set_vfg_range

    @use_set_vfg_range.setter
    @uih.assert_boolean_argument
    def use_set_vfg_range(self,value):
        self.__use_set_vfg_range= value