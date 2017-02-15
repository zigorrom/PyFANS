import os
import numpy as np
from node_configuration import Configuration
from fans_controller import FANS_controller
from fans_constants import *   # FANS_AI_FUNCTIONS,A0_BOX_CHANNELS
from fans_smu import fans_smu,FANS_POSITIVE_POLARITY
import math
from PyQt4 import QtCore

class fans_fet_noise_experiment:
    def __init__(self, fans_controller, fans_smu, configuration):
        self._fans_controller = fans_controller
        self._fans_smu = fans_smu
        self._configuration = configuration
        self._filename = "unnamed"
        self._experiment_data_filename = "MeasurData"
        self._file_extention = ".dat"
        self._working_directory = os.getcwd()
        self._simulate_experiment = False
        #self.initialize_experiment()

    @property
    def simulate_experiment(self):
        return self._simulate_experiment
    
    @simulate_experiment.setter
    def simulate_experiment(self,value):
        self._simulate_experiment = value

    
    def initialize_experiment(self, independent_function, gate_range, drain_source_range):
        if independent_function == FANS_AI_FUNCTIONS.DrainSourceVoltage:
            self._inner_range_generator = enumerate(drain_source_range)
            self._outer_range_generator = enumerate(gate_range)
            self._inner_value_setter = self._fans_smu.set_drain_voltage
            self._outer_value_setter = self._fans_smu.set_gate_voltage

        elif independent_function == FANS_AI_FUNCTIONS.GateVoltage:
            self._inner_range_generator = enumerate(gate_range)
            self._outer_range_generator = enumerate(drain_source_range)
            self._inner_value_setter = self._fans_smu.set_gate_voltage
            self._outer_value_setter = self._fans_smu.set_drain_voltage

        else:
            raise ValueError("wrong independent variable was set")


    def start_experiment(self):
        pass

    def stop_experiment(self):
        pass


    def set_drain_source_voltage_range(self):
        pass

    def set_gate_voltage_range(self):
        pass

    def set_filename(self, filename):
        self._filename = filename

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory

    def set_sample_rate(self,sample_rate):
        pass

    def set_points_per_shot(self, points_per_shot):
        pass

    def __report_progress(self, progress):
        pass

    def __perform_experiment(self):
        self._fans_smu.init_smu_mode()
        for i,outer_value in self._outer_range_generator:
            self._outer_value_setter(outer_value)
            for j,inner_value in self._inner_range_generator:
                self._inner_value_setter(inner_value)    
                print(self._fans_smu.read_all_parameters())

    def __simulate_experiment(self):
        pass




RANGE_HANDLERS = ["normal","back_forth","zero_start","zero_start_back_forth"]
NORMAL_RANGE_HANDLER, BACK_FORTH_RANGE_HANDLER, ZERO_START_RANGE_HANDLER, ZERO_START_BACK_FORTH = RANGE_HANDLERS

class float_range:
    def __init__(self, start, stop, step = 1, len = -1):
        self.__start = start
        self.__stop = stop
        value_difference = math.fabs(self.__stop - self.__start)

        if len > 0:
            self.__length = len
            self.__step = value_difference / (self.__length - 1)
        elif step > 0:
            self.__length = math.floor(value_difference / step)
            self.__step = value_difference / (self.__length - 1)
        else:
            raise AttributeError("length or step is not set correctly")
        
    @property
    def start(self):
        return self.__start

    @property       
    def stop(self):
        return self.__stop

    @property
    def step(self):
        return self.__step

    @property
    def length(self):
        return self.__length

POSITIVE_DIRECTION, NEGATIVE_DIRECTION = (1,-1)       
class range_handler():
    def __init__(self, value_range, n_repeats):
        if not isinstance(value_range, float_range):
            raise TypeError("range parameter is of wrong type!")
        if n_repeats < 1:
            raise ValueError("n_repeats should be greater than one")

        

        self.__range = value_range
        self.__repeats = n_repeats

        self.__direction = POSITIVE_DIRECTION
        self.__comparison_function = self.__positive_comparator

        self.define_direction(self.__range.start,self.__range.stop)
        
    
    @property
    def comparison_function(self):
        return self.__comparison_function
    
    @property
    def number_of_repeats(self):
        return self.__repeats

    @property
    def woking_range(self):
        return self.__range
    
    @property
    def direction(self):
        return self.__direction
    
    def reset(self):
        self.__current_value = self.woking_range.start

     

    def increment_value(self, value_to_increment):
        return value_to_increment + self.__direction * self.__range.step
        
    def define_direction(self, start_value, stop_value):
        if stop_value > start_value:
            self.__direction = POSITIVE_DIRECTION
            self.__comparison_function = self.__positive_comparator
        else:
            self.__direction = NEGATIVE_DIRECTION
            self.__comparison_function = self.__negative_comparator

    def __positive_comparator(self, val1,val2):
        if val2 >= val1:
            return True
        return False

    def __negative_comparator(self,val1,val2):
        if val2 <= val1:
            return True
        return False

    def __iter__(self):
        return self

class normal_range_handler(range_handler):
    def __init__(self,start,stop,step=1,len=-1,repeats = 1):
        super().__init__(float_range(start,stop,step,len),repeats)
        self.__current_value = start
        self.__current_round = 0

    def __next__(self):
        if not self.comparison_function(self.__current_value, self.woking_range.stop):
            self.__current_round += 1
            self.reset()
        
        if self.__current_round >= self.number_of_repeats:
            raise StopIteration        

        #print("current round: {0}".format(self.__current_round))
        value = self.__current_value
        self.__current_value = self.increment_value(value)
        return value

class back_forth_range_handler(range_handler):
    def __init__(self, start, stop, step= 1, len=-1, repeats = 1):
        super().__init__(float_range(start,stop,step,len), repeats) 
        self.__current_value = start
        self.__current_round = 0
        self.__left_value = self.woking_range.start
        self.__right_value = self.woking_range.stop
        self.__change_dir_point = 0

        
    def __next__(self):
        if not self.comparison_function(self.__current_value, self.__right_value):
            value = self.__left_value
            self.__left_value = self.__right_value
            self.__right_value = value
            self.define_direction(self.__left_value,self.__right_value)
            self.__change_dir_point += 1
            if self.__change_dir_point == 2:
                self.__change_dir_point = 0
                self.__current_round += 1
                self.reset()
                

        if self.__current_round >= self.number_of_repeats:
            raise StopIteration        

        value = self.__current_value
        if self.__change_dir_point == 1:
            value = self.increment_value(self.__current_value)
            self.__current_value = self.increment_value(value)
        else:
            self.__current_value = self.increment_value(value)
            
        
        return value


class zero_start_range_handler(range_handler):
    def __init__(self, start, stop, step= 1, len=-1, repeats = 1):
        if start * stop >= 0:
            raise ValueError("Zero start range handler interval should cross zero")
        super().__init__(float_range(start,stop,step,len), repeats)


    def __next__(self):
        pass

class zero_start_back_borth(range_handler):
    def __init__(self, value_range, n_repeats):
        if start * stop >= 0:
            raise ValueError("Zero start range handler interval should cross zero")
        return super().__init__(float_range(start,stop,step,len), n_repeats) 

def print_enum(enumeration):
    for i,item in enumerate(enumeration):
        print("i = {0}; item = {1}".format(i,item))



if __name__ == "__main__":
    #bfrng = back_forth_range_handler(-2,2,len=11)
    #print_enum(bfrng)
        
    #bfrng = zero_start_range_handler(-2,2,len=11)
    
    cfg = Configuration()
    f = FANS_controller("ADC",configuration=cfg)
    smu = fans_smu(f)
    
    smu.set_fans_ao_channel_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, A0_BOX_CHANNELS.ao_ch_1,STATES.ON)
    #smu.set_fans_ao_channel_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, A0_BOX_CHANNELS.ao_ch_10,STATES.ON)
    smu.set_fans_ao_channel_for_function(FANS_AI_FUNCTIONS.GateVoltage, A0_BOX_CHANNELS.ao_ch_9,STATES.ON)

    smu.set_fans_ao_relay_channel_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, A0_BOX_CHANNELS.ao_ch_4)
    #smu.set_fans_ao_relay_channel_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, A0_BOX_CHANNELS.ao_ch_11)
    smu.set_fans_ao_relay_channel_for_function(FANS_AI_FUNCTIONS.GateVoltage,A0_BOX_CHANNELS.ao_ch_12)
     
    smu.set_fans_ao_polarity_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, FANS_POSITIVE_POLARITY )
    smu.set_fans_ao_polarity_for_function(FANS_AI_FUNCTIONS.GateVoltage, FANS_POSITIVE_POLARITY)

    smu.set_fans_ao_feedback_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, AI_BOX_CHANNELS.ai_ch_5)
    smu.set_fans_ao_feedback_for_function(FANS_AI_FUNCTIONS.GateVoltage, AI_BOX_CHANNELS.ai_ch_6)
    smu.set_fans_ao_feedback_for_function(FANS_AI_FUNCTIONS.MainVoltage,AI_BOX_CHANNELS.ai_ch_7 )

    try:

        gate_range = normal_range_handler(-0.15,0.15,0.1)
        drain_range = normal_range_handler(-0.15,0.15,0.1)

        exp = fans_fet_noise_experiment(f,smu,cfg)
        exp.initialize_experiment(FANS_AI_FUNCTIONS.GateVoltage,gate_range,drain_range)
        #exp.perform_experiment()

    except Exception as e:
        raise
    finally:
        smu.set_hardware_voltage_channels(0, AO_CHANNELS.indexes)