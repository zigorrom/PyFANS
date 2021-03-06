﻿import time
import math
import numpy as np

import pyfans.hardware.modern_fans_controller as mfc
import pyfans.hardware.modern_agilent_u2542a as mdaq
import pyfans.hardware.modern_fans_pid_controller as mfpid
from pyfans.utils.binding import Observable
from multiprocessing import Event

DRAIN_SOURCE_SWITCH_VOLTAGE = 8.4

##### TODO:
#Create a moving average array of length(trusted length) and fill with 0 
#Create index to calculate how many values is already in the list and use it for averaging 
#if value does not change the average of moving average list would be in some error range
#if value is not changing raise error

MIN_MOVING_VOLTAGE = 0.6
MAX_MOVING_VOLTAGE = 6
VALUE_DIFFERENCE = MAX_MOVING_VOLTAGE-MIN_MOVING_VOLTAGE
FD_CONST = -0.1

FANS_VOLTAGE_SET_ERROR  = 0.002  #mV
FANS_VOLTAGE_FINE_TUNING_INTERVAL = 5*FANS_VOLTAGE_SET_ERROR  #### set here function for interval selection

A1 = 0.02
A2 = 0.002
X0 = 0.007
p = 3

FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION = lambda error: A2 + (A1 - A2)/(1+math.pow(error/X0,p))

FANS_ZERO_VOLTAGE_INTERVAL = 0.01#0.005

FANS_VOLTAGE_SET_MAXITER = 10000

FANS_POLARITY_SWITCH_VOLTAGE = 5
FANS_POLARITY_CHANGE_VOLTAGE = (-FANS_POLARITY_SWITCH_VOLTAGE ,FANS_POLARITY_SWITCH_VOLTAGE)
FANS_NEGATIVE_POLARITY,FANS_POSITIVE_POLARITY = FANS_POLARITY_CHANGE_VOLTAGE
 
X0_VOLTAGE_SET = 0.1
POWER_VOLTAGE_SET = 5#3


def voltage_setting_function(current_value, set_value, fine_tuning = False, correction_coefficient = 1):
    # fermi-dirac-distribution
    sign = -1
    if current_value <0:
        if current_value > set_value:
            sign = -1   
        else:
            sign = +1
    else:
        if current_value > set_value:
            sign = +1
        else:
            sign = -1
    
    result = 0
    #correction_coefficient = 1
    if correction_coefficient <= 1:
        correction_coefficient = 1

    if fine_tuning:
        #return MIN_MOVING_VOLTAGE
        #return sign*MIN_MOVING_VOLTAGE
        result = sign* correction_coefficient *MIN_MOVING_VOLTAGE
    else:
        diff = math.fabs(current_value-set_value)
        result = (MAX_MOVING_VOLTAGE + (MIN_MOVING_VOLTAGE-MAX_MOVING_VOLTAGE)/(1+math.pow(diff/X0_VOLTAGE_SET,POWER_VOLTAGE_SET)))
        if result < MIN_MOVING_VOLTAGE:
            result = MIN_MOVING_VOLTAGE
        elif result> MAX_MOVING_VOLTAGE:
            result = MAX_MOVING_VOLTAGE
        result = correction_coefficient * sign*result
    return result
        #try:
        #    exponent = math.exp(diff/FD_CONST)
        #except OverflowError:
        #    exponent = float("inf")
        
        #return (MIN_MOVING_VOLTAGE + VALUE_DIFFERENCE/(exponent+1))
        #return sign*(MIN_MOVING_VOLTAGE + VALUE_DIFFERENCE/(exponent+1))
        #return 


OUT_ENABLED_CH, OUT_CH, FEEDBACK_CH, POLARITY_RELAY_CH , CH_POLARITY = [0,1,2,3,4]

LOW_SPEED, FAST_SPEED = (1,5)
SHORT_TIME,LONG_TIME = (0.3,2)



class FANS_SMU:
    #{"Vds":ds_voltage,"Vgs":gate_voltage,"Vmain":main_voltage, "Ids":current,"Rs":resistance}
    DRAIN_SOURCE_VOLTAGE_VAR = "Vds"
    GATE_SOURVCE_VOLTAGE_VAR = "Vgs"
    MAIN_VOLTAGE_VAR = "Vmain"
    DRAIN_CURRENT_VAR = "Ids"
    SAMPLE_RESISTANCE_VAR = "Rs"

    def __init__(self,fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback):
        assert isinstance(fans_controller, mfc.FANS_CONTROLLER), "Wrong controller type"
        assert isinstance(drain_source_motor, mfc.FANS_AO_CHANNELS)
        assert isinstance(drain_source_relay, mfc.FANS_AO_CHANNELS)
        assert isinstance(gate_motor, mfc.FANS_AO_CHANNELS)
        assert isinstance(gate_relay, mfc.FANS_AO_CHANNELS)
        assert isinstance(drain_source_feedback, mfc.FANS_AI_CHANNELS)
        assert isinstance(gate_feedback, mfc.FANS_AI_CHANNELS)
        assert isinstance(main_feedback, mfc.FANS_AI_CHANNELS)

    
        self._fans_controller = fans_controller #FANS_CONTROLLER("") #
        self._drain_source_motor = drain_source_motor
        self._gate_motor = gate_motor
        
        self._drain_source_relay = drain_source_relay
        self._gate_relay = gate_relay
        
        self._drain_source_feedback = drain_source_feedback
        self._gate_feedback = gate_feedback
        self._main_feedback = main_feedback
        
        ###
        ### TO DO
        ### get references to the channels in init_smu method in order to use them in read methods and set_voltage
        ###


        self._load_resistance = 5000
        self._averageing_number = 100
        self._smu_sample_rate = 1000

        self.set_smu_parameters(self.smu_averaging_number, self.smu_load_resistance)


    def set_smu_parameters(self, averaging, load_resistance):
        self.smu_load_resistance = load_resistance
        self.smu_averaging_number = averaging
        self._fans_controller.set_sampling_rate(self._smu_sample_rate)
        
    @property
    def fans_controller(self):
        return self._fans_controller

    @property
    def smu_averaging_number(self):
        return self._averageing_number

    @smu_averaging_number.setter
    def smu_averaging_number(self,value):
        self._averageing_number = value
        self._fans_controller.set_analog_read_averaging(self.smu_averaging_number)

    @property
    def smu_load_resistance(self):
        return self._load_resistance

    @smu_load_resistance.setter
    def smu_load_resistance(self,value):
        self._load_resistance = value

    @property
    def smu_ds_motor(self):
        return self._drain_source_motor

    @smu_ds_motor.setter
    def smu_ds_motor(self,value):
        self._drain_source_motor = value

    @property
    def smu_gate_motor(self):
        return self._gate_motor

    @smu_gate_motor.setter
    def smu_gate_motor(self,value):
        self._gate_motor = value

    @property
    def smu_ds_relay(self):
        return self._drain_source_relay

    @smu_ds_relay.setter
    def smu_ds_relay(self,value):
        self._drain_source_relay = value

    @property
    def smu_gate_relay(self):
        return self._gate_relay

    @smu_gate_relay.setter
    def smu_gate_relay(self,value):
        self._gate_relay = value

    @property
    def smu_drain_source_feedback(self):
        return self._drain_source_feedback

    @smu_drain_source_feedback.setter
    def smu_drain_source_feedback(self,value):
        self._drain_source_feedback = value

    @property
    def smu_gate_feedback(self):
        return self._gate_feedback

    @smu_gate_feedback.setter
    def smu_gate_feedback(self,value):
        self._gate_feedback = value

    @property
    def smu_main_feedback(self):
        return self._main_feedback

    @smu_main_feedback.setter
    def smu_main_feedback(self,value):
        self._main_feedback = value

    def init_smu_mode(self):
        # here use multichannel !!!
        for ch in [self.smu_drain_source_feedback, self.smu_gate_feedback, self.smu_main_feedback]:
            #TODO insert here check of selected feedback channel - it should correspond to DC mode!!!
            ai_mode = mfc.get_ai_mode_for_fans_ai_channel(ch)
            assert ai_mode == mfc.AI_MODES.DC, "Selected channel has no DC configuration"
            ai_feedback = self._fans_controller.get_fans_channel_by_name(ch)
            assert isinstance(ai_feedback, mfc.FANS_AI_CHANNEL)

            ai_feedback.ai_mode = ai_mode #mfc.AI_MODES.DC
            ai_feedback.ai_polling_polarity = mdaq.BIPOLAR
            ai_feedback.ai_polling_range = mdaq.AUTO_RANGE
            ai_feedback.apply_fans_ai_channel_params()

        #set averaging and load resistance
        self.set_smu_parameters(self.smu_averaging_number, self.smu_load_resistance)
       ## TODO: set also parameters for output channels



    def __set_voltage_polarity(self, polarity, voltage_set_channel, relay_channel):
        assert isinstance(relay_channel, mfc.FANS_AO_CHANNELS), "Wrong channel!"
        assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS), "Wrong channel!"
        rel_ch = self._fans_controller.get_fans_output_channel(relay_channel) #.fans_ao_switch.select_channel(relay_channel)
        #assert isinstance(rel_ch, mfc.FANS_AO_CHANNEL)
        rel_ch.analog_write(polarity)
        time.sleep(0.5)
        rel_ch.analog_write(0)
        self._fans_controller.get_fans_output_channel(voltage_set_channel)
        

    def set_drain_source_polarity_positiv(self):
        self.__set_voltage_polarity(FANS_POSITIVE_POLARITY, self._drain_source_motor, self._drain_source_relay)

    def set_drain_source_polarity_negativ(self):
        self.__set_voltage_polarity(FANS_NEGATIVE_POLARITY, self._drain_source_motor, self._drain_source_relay)

    def set_gate_polarity_positiv(self):
        self.__set_voltage_polarity(FANS_POSITIVE_POLARITY, self._gate_motor, self._gate_relay)

    def set_gate_polarity_negativ(self):
        self.__set_voltage_polarity(FANS_NEGATIVE_POLARITY, self._gate_motor, self._gate_relay)

    def move_motor(self, voltage_set_channel, direction, speed, timeout = 0.1):
        assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS),"Incorrect channel"
        output_channel = self._fans_controller.get_fans_output_channel(voltage_set_channel)
        output_channel.analog_write(direction*speed)
        time.sleep(timeout)
        output_channel.analog_write(0)

    LEFT_DIRECTION = 1
    RIGHT_DIRECTION = -1

    def move_ds_motor_left(self):
        self.move_motor(self._drain_source_motor, self.LEFT_DIRECTION, LOW_SPEED, SHORT_TIME)

    def move_ds_motor_left_fast(self):
        self.move_motor(self._drain_source_motor, self.LEFT_DIRECTION, FAST_SPEED, LONG_TIME)

    def move_ds_motor_right(self):
        self.move_motor(self._drain_source_motor, self.RIGHT_DIRECTION, LOW_SPEED, SHORT_TIME)

    def move_ds_motor_right_fast(self):
        self.move_motor(self._drain_source_motor, self.RIGHT_DIRECTION, FAST_SPEED, LONG_TIME)

    def move_gate_motor_left(self):
        self.move_motor(self._gate_motor, self.LEFT_DIRECTION, LOW_SPEED,SHORT_TIME)

    def move_gate_motor_left_fast(self):
        self.move_motor(self._gate_motor, self.LEFT_DIRECTION, FAST_SPEED, LONG_TIME)

    def move_gate_motor_right(self):
        self.move_motor(self._gate_motor, self.RIGHT_DIRECTION, LOW_SPEED, SHORT_TIME)

    def move_gate_motor_right_fast(self):
        self.move_motor(self._gate_motor, self.RIGHT_DIRECTION, FAST_SPEED, LONG_TIME)

   
    def __set_voltage_for_function(self,voltage, voltage_set_channel, relay_channel, feedback_channel):
        assert isinstance(voltage, float) or isinstance(voltage, int)
        assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS)
        assert isinstance(relay_channel, mfc.FANS_AO_CHANNELS)
        assert isinstance(feedback_channel, mfc.FANS_AI_CHANNELS)
        
        #
        #  TO IMPLEMENT: use here UNIPOLAR voltage read and select appropriate range
        #

        output_channel = self._fans_controller.get_fans_output_channel(voltage_set_channel)
        
        #self._fans_controller.fans_ao_switch.select_channel(voltage_set_channel)
        assert isinstance(output_channel, mfc.FANS_AO_CHANNEL)

        #set read averaging to small value for fast acquisition
        coarse_averaging = 20
        fine_averaging = 50
        stabilization_counter = 200

        self.smu_averaging_number = coarse_averaging

        prev_value = self.analog_read(feedback_channel)
        fine_tuning = False
        polarity_switched = False
        
        VoltageSetError = FANS_VOLTAGE_SET_ERROR
        VoltageTuningInterval = FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION(VoltageSetError)

        if math.fabs(voltage) < FANS_ZERO_VOLTAGE_INTERVAL :
            VoltageSetError = FANS_ZERO_VOLTAGE_INTERVAL
            VoltageTuningInterval =  VoltageTuningInterval+VoltageSetError     #5*VoltageSetError   

        while True: #continue_setting:    
            current_value = self.analog_read(feedback_channel)
            if current_value*voltage<0 and not polarity_switched:
                set_result = self.__set_voltage_for_function(0, voltage_set_channel, relay_channel, feedback_channel)
        
                if set_result:
                    polarity = FANS_NEGATIVE_POLARITY if voltage<0 else FANS_POSITIVE_POLARITY
                    self.__set_voltage_polarity(polarity, voltage_set_channel, relay_channel)
                    polarity_switched = True
                else:
                    return set_result

            value_to_set = voltage_setting_function(current_value,voltage)
            abs_distance = math.fabs(current_value - voltage)

            if abs_distance < VoltageSetError and fine_tuning: #FANS_VOLTAGE_SET_ERROR and fine_tuning:
                # set high averaging, moving voltage to 0 and check condition again count times if is of return true if not repeat adjustment
                output_channel.analog_write(0)
                condition_sattisfied = True
                for i in range(fine_averaging):
                    current_value = self.analog_read(feedback_channel)
                    abs_distance = math.fabs(current_value - voltage)

                    print("current distanse: {0}, trust_error: {1}, count: {2}, value: {3}".format(abs_distance, VoltageSetError, i, current_value))
                    if abs_distance > VoltageSetError:
                        condition_sattisfied = False
                        break

                if condition_sattisfied:
                    return True
                

            elif abs_distance < VoltageTuningInterval or fine_tuning: #FANS_VOLTAGE_FINE_TUNING_INTERVAL:
                fine_tuning = True
                value_to_set = voltage_setting_function(current_value,voltage,True)
            
            
            
            if polarity_switched:
                abs_value = math.fabs(value_to_set)
                if voltage * current_value < 0:
                    if voltage > 0:
                        value_to_set = abs_value
                    else:
                        value_to_set = -abs_value
            print("current: {0}; goal: {1};to set: {2};".format(current_value,voltage, value_to_set))    
            output_channel.analog_write(value_to_set)
            #output_channel.ao_voltage = value_to_set 
        output_channel.analog_write(0)

   


    def smu_set_drain_source_voltage(self,voltage):
        self.__set_voltage_for_function(voltage, self.smu_ds_motor, self.smu_ds_relay, self.smu_drain_source_feedback)

    def smu_set_gate_voltage(self,voltage):
        self.__set_voltage_for_function(voltage, self.smu_gate_motor, self.smu_gate_relay, self.smu_gate_feedback)

    def analog_read(self, channel):
        fans_channel = self._fans_controller.get_fans_channel_by_name(channel)
        assert isinstance(fans_channel, mfc.FANS_AI_CHANNEL)
        return fans_channel.analog_read()

    def analog_read_channels(self, channels):
        ## to do 
        ## improve speed here 

        #fans_channels = [self._fans_controller.get_fans_channel_by_name(ch) for ch in channels]
        #fans_multichannel = mfc.FANS_AI_MULTICHANNEL(*fans_channels)
        fans_multichannel = mfc.FANS_AI_MULTICHANNEL(self._fans_controller, *channels)
        result = fans_multichannel.analog_read()
        #converted_dict = {ch: result[fans_ch.ai_daq_input] for ch, fans_ch in zip(channels,fans_channels) }
        return result ##converted_dict

    def read_all_test(self):
        result = self.analog_read_channels([self.smu_drain_source_feedback,self.smu_gate_feedback,self.smu_main_feedback])
        ds_voltage = result[self.smu_drain_source_feedback]
        main_voltage = result[self.smu_main_feedback]
        gate_voltage = result[self.smu_gate_feedback]

        print("ds: {0}; gs: {1}; m: {2}".format(ds_voltage, gate_voltage, main_voltage))

    def read_feedback_voltages(self):
        result = self.analog_read_channels([self.smu_drain_source_feedback,self.smu_gate_feedback,self.smu_main_feedback])
        ds_voltage = result[self.smu_drain_source_feedback]
        main_voltage = result[self.smu_main_feedback]
        gate_voltage = result[self.smu_gate_feedback]
        return (ds_voltage, main_voltage, gate_voltage)


    def read_all_parameters(self):
        # can be a problem with an order of arguments
        result = self.analog_read_channels([self.smu_drain_source_feedback,self.smu_gate_feedback,self.smu_main_feedback])
        ds_voltage = result[self.smu_drain_source_feedback]
        main_voltage = result[self.smu_main_feedback]
        gate_voltage = result[self.smu_gate_feedback]


        ### fix divide by zero exception
        try:
            current = (main_voltage-ds_voltage)/self.smu_load_resistance
            resistance = ds_voltage/current
        except ZeroDivisionError:
            current = 0
            resistance = 0

        return {self.DRAIN_SOURCE_VOLTAGE_VAR:ds_voltage,
                self.GATE_SOURVCE_VOLTAGE_VAR:gate_voltage,
                self.MAIN_VOLTAGE_VAR:main_voltage, 
                self.DRAIN_CURRENT_VAR:current,
                self.SAMPLE_RESISTANCE_VAR:resistance}
        #return {"Vds":ds_voltage,"Vgs":gate_voltage,"Vmain":main_voltage, "Ids":current,"Rs":resistance}

class MaxIterationReachedError(Exception):
    pass

class DesiredErrorReachedError(Exception):
    pass

class PolaritySwitchError(Exception):
    pass

class InstabilityError(Exception):
    pass

class VoltageSetInterruptError(Exception):
    pass

class IterationCounter(object):
    def __init__(self, max_iteration, exception_to_call = None):
        self._max_iteration = max_iteration
        self._current_index = 0
        self._exception_to_call = exception_to_call

    @property
    def max_iteration(self):
        return self._max_iteration

    @max_iteration.setter
    def max_iteration(self,value):
        assert isinstance(value, int), "max iteration can only be integer"
        self._max_iteration = value

    @property
    def current_index(self):
        return self._current_index

    def increment(self):
        self._current_index += 1
        if self._current_index > self._max_iteration:
            self.__call_exception()
            #raise MaxIterationReachedError()

    def __call_exception(self):
        if self._exception_to_call:
            if issubclass(self._exception_to_call, Exception):
                raise self._exception_to_call()

    def reset(self):
        self._current_index = 0





class FANS_VoltageSetter(Observable):
    COARSE_MODE, FINE_MODE, STABILIZATION_MODE = range(3)
    ABS_VOLTAGE_INCREASE_DIRECTION = -1
    ABS_VOLTAGE_DECREASE_DIRECTION = -ABS_VOLTAGE_INCREASE_DIRECTION 
    ZERO_VOLTAGE_INTERVAL = 0.01
    NEGATIVE_POLARITY, POSITIVE_POLARITY = (-1,1)
    STABILIZATION_COUNTER = 50
    INSTABILITY_COUNTER = 7
    MAX_ITERATIONS = 100*STABILIZATION_COUNTER

    def __init__(self):#,voltage):
        super().__init__()
        #self.voltage_to_set = voltage
        self.reset()
        #self.current_voltage = 0
        #self.correction_coefficient = 1
        #self.mode = COARSE_MODE
        #self.current_polarity = self.POSITIVE_POLARITY
        #self.iteration_counter = IterationCounter(self.MAX_ITERATIONS, MaxIterationReachedError)
        #self.stabilization_counter = IterationCounter(self.STABILIZATION_COUNTER, DesiredErrorReachedError)

    def reset(self):
        self.current_voltage = 0
        self.correction_coefficient = 1
        self.mode = self.COARSE_MODE
        self.current_polarity = self.POSITIVE_POLARITY
        self.iteration_counter = IterationCounter(self.MAX_ITERATIONS, MaxIterationReachedError)
        self.stabilization_counter = IterationCounter(self.STABILIZATION_COUNTER, DesiredErrorReachedError)
        self.instability_counter = IterationCounter(self.INSTABILITY_COUNTER, InstabilityError)

    def subscribe_to_voltage_change(self, callback):
        self.addObserver("set_voltage", callback)

    def on_voltage_changed(self, voltage):
        self._Observable__fireCallbacks("set_voltage",voltage = voltage)

    def move_to_zero(self):
        try:
            print("Moving to zero voltage")
            self.zero_reached_counter = IterationCounter(10, DesiredErrorReachedError)
            self.set_moving_voltage(ABS_VOLTAGE_DECREASE_DIRECTION *  MAX_MOVING_VOLTAGE)
            while True:
                value = math.fabs(self.read_feedback_voltage())
                self.on_voltage_changed(value)
                if value < self.ZERO_VOLTAGE_INTERVAL:
                    self.zero_reached_counter.increment()

        except DesiredErrorReachedError as err:
            print("Zero volts reached")
        finally:
            self.set_moving_voltage(0)

    def move_from_zero_trust_interval(self):
        try:
            print("Moving out of zero interval voltage")
            self.out_of_zero_interval_countert = IterationCounter(2, DesiredErrorReachedError)
            self.set_moving_voltage(ABS_VOLTAGE_INCREASE_DIRECTION * MIN_MOVING_VOLTAGE)
            while True:
                value = math.fabs(self.read_feedback_voltage())
                self.on_voltage_changed(value)
                if value > self.ZERO_VOLTAGE_INTERVAL:
                    self.out_of_zero_interval_countert.increment()

        except DesiredErrorReachedError as err:
            print("Out of zero interval")
        finally:
            self.set_moving_voltage(0)

    def move_step_abs_voltage_increase(self, timeout=0.5):
        try:
            self.set_moving_voltage(ABS_VOLTAGE_INCREASE_DIRECTION * MAX_MOVING_VOLTAGE)#MIN_MOVING_VOLTAGE)
            time.sleep(timeout)
            self.set_moving_voltage(0)

            value = math.fabs(self.read_feedback_voltage())
            self.on_voltage_changed(value)

        except:
            print("Error when step increasing abs voltage")
        finally:
            self.set_moving_voltage(0)

    def voltage_under_zero_trust_interval(self, current_voltage):
        if math.fabs(current_voltage) < self.ZERO_VOLTAGE_INTERVAL:
            return True
        else:
            return False

    def check_polarity(self, voltage_to_set,current_voltage):
        """Returns tuple with fields: need_to_switch_polarity - bool; polarity_to_switch - FANS_POSITIVE_POLARITY or FANS_NEGATIVE_POLARITY.
        When need_to_switch_polarity==True - returns polarity to which it shoud be switched.
        When need_to_switch_polarity==True - returns current polarity
        """
        need_to_switch_polarity = False
        polarity_to_switch = None
        if voltage_to_set * current_voltage < 0:
            need_to_switch_polarity = True
            if voltage_to_set >= 0:
                polarity_to_switch = self.POSITIVE_POLARITY
            else:
                polarity_to_switch = self.NEGATIVE_POLARITY
        else:
            if current_voltage < 0:
                polarity_to_switch = self.NEGATIVE_POLARITY
            else:
                polarity_to_switch = self.POSITIVE_POLARITY

        return (need_to_switch_polarity, polarity_to_switch)

    def switch_to_polarity(self,polarity):
        raise NotImplementedError()
        #self.move_to_zero()

    def set_correction_coefficient(self, coefficient):
        if coefficient >= 1:
            self.correction_coefficient = coefficient

    def read_feedback_voltage(self):
        raise NotImplementedError()
        #value = 0
        #self.recalculate_correction_coefficient()
        #self.current_voltage = value
        #return value

    def set_moving_voltage(self, voltage):
        raise NotImplementedError()

    def voltage_setting_function(self,current_value, set_value, correction_coefficient = 1):
    # fermi-dirac-distribution
        result = 0
        try:
            diff = math.fabs(current_value - set_value)
            result = (MAX_MOVING_VOLTAGE + (MIN_MOVING_VOLTAGE-MAX_MOVING_VOLTAGE)/(1+math.pow(diff/X0_VOLTAGE_SET,POWER_VOLTAGE_SET)))
            if result < MIN_MOVING_VOLTAGE:
                result = MIN_MOVING_VOLTAGE
            elif result> MAX_MOVING_VOLTAGE:
                result = MAX_MOVING_VOLTAGE
            result = correction_coefficient * result

        except ZeroDivisionError as err:
            result = 0

        return result

    def voltage_set_sign_calculation(self, voltage_to_set, current_voltage, current_polarity):
        assert isinstance(voltage_to_set, (int,float)) and isinstance(current_voltage, (int,float)) and isinstance(current_polarity, (int,float)), "Value error"
        #assert voltage_to_set*current_voltage >= 0, "Switch polarity first"

        sign = math.copysign(1,(current_voltage - voltage_to_set) * current_polarity) #self.ABS_VOLTAGE_INCREASE_DIRECTION * (current_voltage - voltage_to_set) * current_polarity)
        return sign
        #sign = 
        #if voltage_to_set * current_voltage >= 0:
        #    voltage_to_set = math.fabs(voltage_to_set)
        #    current_voltage = math.fabs(current_voltage)
        #    if current_polarity is self.POSITIVE_POLARITY:

        #if voltage_to_set*current_voltage < 0:
        #    raise ValueError("Voltage to set and current voltage must be same sign")

    def normalize_motor_value(self,motor_value):
        abs_motor_value = math.fabs(motor_value)
        if abs_motor_value > MAX_MOVING_VOLTAGE:
            abs_motor_value = MAX_MOVING_VOLTAGE
        elif abs_motor_value < MIN_MOVING_VOLTAGE:
            abs_motor_value = MIN_MOVING_VOLTAGE

        motor_value = math.copysign(abs_motor_value, motor_value)
        return motor_value


    def set_voltage(self, voltage_to_set, error = None, stopEvent = None):

        def assert_stop_voltage_set():
            if stopEvent.is_set():
                raise VoltageSetInterruptError()
            
        assert_stop_func = assert_stop_voltage_set if stopEvent is not None else lambda *args: None

        assert_stop_func()
        self.voltage_to_set = voltage_to_set
        abs_voltage_to_set = math.fabs(voltage_to_set)
        value = self.read_feedback_voltage()
        if self.voltage_under_zero_trust_interval(value):
            self.move_from_zero_trust_interval()

        value = self.read_feedback_voltage()
        (need_to_switch_polarity, polarity_to_switch) = self.check_polarity(voltage_to_set,value)
        if need_to_switch_polarity:
            self.move_to_zero()
            self.switch_to_polarity(polarity_to_switch)
            #move a bit towards increasing abs voltage
            self.move_step_abs_voltage_increase()
        
        value = self.read_feedback_voltage()
        (need_to_switch_polarity, polarity_to_switch) = self.check_polarity(voltage_to_set,value)
        if need_to_switch_polarity:
            raise PolaritySwitchError()
            #raise Exception("Cannot switch polarity")

        self.current_polarity = polarity_to_switch
        
        VoltageSetError = FANS_VOLTAGE_SET_ERROR
        if isinstance(error, (int,float)):
            VoltageSetError = math.fabs(error)

        if self.voltage_under_zero_trust_interval(abs_voltage_to_set):
            VoltageSetError = self.ZERO_VOLTAGE_INTERVAL + VoltageSetError

        VoltageTuningInterval = FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION(VoltageSetError)
        if VoltageTuningInterval<VoltageSetError:
            VoltageTuningInterval += VoltageSetError

        try:
            while True:
                try:
                    assert_stop_func()
                    value = self.read_feedback_voltage()
                    abs_value = math.fabs(value)
                    difference = math.fabs(value - self.voltage_to_set)
                    motor_value_to_set = 0
                    self.on_voltage_changed(value)
                

                    if self.mode == self.COARSE_MODE:
                        if difference < VoltageTuningInterval:
                            self.mode = self.FINE_MODE
                            continue

                        motor_value_to_set = self.voltage_setting_function(value,voltage_to_set, correction_coefficient = self.correction_coefficient) # main_voltage/sample_voltage)
                        motor_value_to_set = math.copysign(motor_value_to_set, self.voltage_set_sign_calculation(abs_voltage_to_set, abs_value, self.POSITIVE_POLARITY))  #self.voltage_set_sign_calculation(voltage_to_set, value, self.current_polarity)) 
                        motor_value_to_set = self.normalize_motor_value(motor_value_to_set)
                        self.set_moving_voltage(motor_value_to_set)

                    elif self.mode == self.FINE_MODE:
                        if difference < VoltageSetError:
                            self.mode = self.STABILIZATION_MODE
                            self.set_moving_voltage(0)
                            continue

                        motor_value_to_set = math.copysign(MIN_MOVING_VOLTAGE, self.voltage_set_sign_calculation(abs_voltage_to_set, abs_value, self.POSITIVE_POLARITY)) 
                        motor_value_to_set = self.normalize_motor_value(motor_value_to_set)
                        self.set_moving_voltage(motor_value_to_set)
                        self.iteration_counter.increment()

                    elif self.mode == self.STABILIZATION_MODE:
                        if difference < VoltageSetError:
                            self.stabilization_counter.increment()
                        else:
                            self.mode = self.FINE_MODE
                            self.stabilization_counter.reset()
                            self.instability_counter.increment()

                    else:
                        raise ValueError("mode valiable has wrong value")

                    print("CURRENT VALUE:{0}; GOAL:{1}; MOTOR:{2}; MODE:{3}; ERR:{4}".format(value, voltage_to_set, motor_value_to_set,self.mode, VoltageSetError))

                except InstabilityError as err:
                    self.instability_counter.reset()
                    error_to_add = math.fabs(VoltageSetError)
                    if voltage_to_set != 0.0:
                        error_to_add = 0.01* math.fabs(voltage_to_set)
                        
                    VoltageSetError += error_to_add
                    VoltageTuningInterval += error_to_add
            
            return 0

        except VoltageSetInterruptError as err:
            print("Voltage setting interrupted")
            raise err

        except DesiredErrorReachedError as err:
            print("Desired error is reached")
            return 0
        except ValueError as err:
            print(str(err))
            return 1
        except MaxIterationReachedError as err:
            print("Max iteratuions achieved")
            return 2
        finally:
            self.set_moving_voltage(0)


class FANS_DrainSourceVoltageSetter(FANS_VoltageSetter):
    ZERO_VOLTAGE_INTERVAL = 0.005
    def __init__(self, fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback, drain_source_switch_channel, main_feedback, drain_source_switch_voltage = DRAIN_SOURCE_SWITCH_VOLTAGE):
        super().__init__()
        self.fans_controller = fans_controller
        self.drain_source_motor = drain_source_motor
        self.drain_source_relay = drain_source_relay
        self.drain_source_feedback = drain_source_feedback
        self.drain_source_switch_channel = drain_source_switch_channel
        self.drain_source_switch_voltage = drain_source_switch_voltage
        self.main_feedback = main_feedback

        self.output_channel = None
        self.switch_drain_feedback_output = None

        self.feedback_multichannel = mfc.FANS_AI_MULTICHANNEL(self.fans_controller, self.drain_source_feedback, self.main_feedback)


    def __prepare_feedback_voltage_measurement(self):
        self.output_channel, self.switch_drain_feedback_output = self.fans_controller.get_fans_output_channels(self.drain_source_motor, self.drain_source_switch_channel)
        assert self.output_channel != self.switch_drain_feedback_output, "Cannot use same channel for different functions"
        assert isinstance(self.switch_drain_feedback_output, mfc.FANS_AO_CHANNEL)
        self.switch_drain_feedback_output.analog_write(self.drain_source_switch_voltage)
        assert isinstance(self.output_channel, mfc.FANS_AO_CHANNEL)

    #def __prepare_polarity_switch(self):
    #    pass

    def read_feedback_voltage(self):
        res = self.feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
        sample_voltage = res[self.drain_source_feedback]
        main_voltage = res[self.main_feedback]
        correction_coefficient = 1
        try:
            correction_coefficient = main_voltage/sample_voltage
            if correction_coefficient < 1:
                correction_coefficient = 1
        except ZeroDivisionError:
            correction_coefficient = 1

        self.set_correction_coefficient(correction_coefficient)

        return sample_voltage
        
        #return super().read_feedback_voltage()

    def set_moving_voltage(self, voltage):
        self.output_channel.analog_write(voltage)


    def switch_to_polarity(self, polarity):
        #self.__prepare_polarity_switch()
        #switch polarities
        polarity = math.copysign(FANS_POLARITY_SWITCH_VOLTAGE, polarity)
        assert isinstance(self.drain_source_relay, mfc.FANS_AO_CHANNELS), "Wrong channel!"
        rel_ch = self.fans_controller.get_fans_output_channel(self.drain_source_relay) #.fans_ao_switch.select_channel(relay_channel)
        rel_ch.analog_write(polarity)
        time.sleep(0.5)
        rel_ch.analog_write(0)
        #return back to main channel
        self.__prepare_feedback_voltage_measurement()

    def set_voltage(self, voltage_to_set, stopEvent=None):
        self.__prepare_feedback_voltage_measurement()
        return super().set_voltage(voltage_to_set, stopEvent=stopEvent)

    
class FANS_GateSourceVoltageSetter(FANS_VoltageSetter):
    ZERO_VOLTAGE_INTERVAL = 0.01
    def __init__(self, fans_controller, gate_motor, gate_relay, gate_feedback):
        super().__init__()
        self.fans_controller = fans_controller
        self.gate_motor = gate_motor
        self.gate_relay = gate_relay
        self.gate_feedback = gate_feedback

        self.output_channel = None

        self.feedback_channel = self.fans_controller.get_fans_channel_by_name(self.gate_feedback)#mfc.FANS_AI_MULTICHANNEL(self.fans_controller, self.drain_source_feedback, self.main_feedback)


    def __prepare_feedback_voltage_measurement(self):
        self.output_channel = self.fans_controller.get_fans_output_channel(self.gate_motor)
        assert isinstance(self.output_channel, mfc.FANS_AO_CHANNEL)

    #def __prepare_polarity_switch(self):
    #    pass

    def read_feedback_voltage(self):
        gate_voltage = self.feedback_channel.analog_read() #self.analog_read(feedback_channel)
        return gate_voltage
        
        #return super().read_feedback_voltage()

    def set_moving_voltage(self, voltage):
        self.output_channel.analog_write(voltage)


    def switch_to_polarity(self, polarity):
        #self.__prepare_polarity_switch()
        #switch polarities
        polarity = math.copysign(FANS_POLARITY_SWITCH_VOLTAGE, polarity)
        assert isinstance(self.gate_relay, mfc.FANS_AO_CHANNELS), "Wrong channel!"
        rel_ch = self.fans_controller.get_fans_output_channel(self.gate_relay) #.fans_ao_switch.select_channel(relay_channel)
        rel_ch.analog_write(polarity)
        time.sleep(0.5)
        rel_ch.analog_write(0)
        #return back to main channel
        self.__prepare_feedback_voltage_measurement()

    def set_voltage(self, voltage_to_set, error=None, stopEvent=None):
        self.__prepare_feedback_voltage_measurement()
        return super().set_voltage(voltage_to_set, error, stopEvent=stopEvent)


class FANS_SMU_Specialized(FANS_SMU):
    def __init__(self, fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback, drain_source_switch_channel, drain_source_switch_voltage = DRAIN_SOURCE_SWITCH_VOLTAGE):
        super().__init__(fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback)
        assert isinstance(drain_source_switch_channel, mfc.FANS_AO_CHANNELS)
        assert isinstance(drain_source_switch_voltage, float)

        self._drain_source_switch_channel = drain_source_switch_channel
        self._drain_source_switch_voltage = drain_source_switch_voltage

        self.drain_source_voltage_setter = FANS_DrainSourceVoltageSetter(fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback, drain_source_switch_channel, main_feedback, drain_source_switch_voltage)
        self.gate_source_voltage_setter = FANS_GateSourceVoltageSetter(fans_controller, gate_motor, gate_relay, gate_feedback)

    def subscribe_to_drain_source_voltage_change(self, callback):
        self.drain_source_voltage_setter.subscribe_to_voltage_change(callback)

    def subscribe_to_gate_source_voltage_change(self, callback):
        self.gate_source_voltage_setter.subscribe_to_voltage_change(callback)

    def smu_set_drain_source_voltage(self, voltage, error = None, stopEvent=None):
        self.drain_source_voltage_setter.reset()
        self.drain_source_voltage_setter.set_voltage(voltage, stopEvent=stopEvent)

    def smu_set_gate_voltage(self, voltage, error = None, stopEvent=None):
        self.gate_source_voltage_setter.reset()
        self.gate_source_voltage_setter.set_voltage(voltage, stopEvent=stopEvent)

    def read_all_test(self):
        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        print ("stabilizing voltages after drain switch on. waiting...")
        time.sleep(5)
        result = super().read_all_test() 
        drain_source_switch_channel.analog_write(0)
        return result

    def read_feedback_voltages(self):
        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        print ("stabilizing voltages after drain switch on. waiting...")
        time.sleep(5)
        result = super().read_feedback_voltages()
        drain_source_switch_channel.analog_write(0)
        return result

    def read_all_parameters(self):
        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        print ("stabilizing voltages after drain switch on. waiting...")
        time.sleep(5)
        result = super().read_all_parameters()
        drain_source_switch_channel.analog_write(0)
        return result


#class FANS_SMU_Specialized(FANS_SMU):
#    def __init__(self, fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback, drain_source_switch_channel, drain_source_switch_voltage = DRAIN_SOURCE_SWITCH_VOLTAGE):
#        super().__init__(fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback)
#        assert isinstance(drain_source_switch_channel, mfc.FANS_AO_CHANNELS)
#        assert isinstance(drain_source_switch_voltage, float)

#        self._drain_source_switch_channel = drain_source_switch_channel
#        self._drain_source_switch_voltage = drain_source_switch_voltage


#    def __set_voltage_polarity(self, polarity, voltage_set_channel, relay_channel, additional_channel = None, additional_control_voltage = 0.0):
#        assert isinstance(relay_channel, mfc.FANS_AO_CHANNELS), "Wrong channel!"
#        assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS), "Wrong channel!"
#        assert isinstance(additional_control_voltage, float)
#        rel_ch = self._fans_controller.get_fans_output_channel(relay_channel) #.fans_ao_switch.select_channel(relay_channel)
#        #assert isinstance(rel_ch, mfc.FANS_AO_CHANNEL)
#        rel_ch.analog_write(polarity)
#        time.sleep(0.5)
#        rel_ch.analog_write(0)

#        if isinstance(additional_channel, mfc.FANS_AO_CHANNELS):
#            output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(voltage_set_channel, additional_channel)
#            assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
#            assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
#            additional_output_channel.analog_write(additional_control_voltage)
#        else:
#            self._fans_controller.get_fans_output_channel(voltage_set_channel)

#    def smu_set_drain_source_voltage(self, voltage):
#        drain_motor = self.smu_ds_motor
#        drain_relay = self.smu_ds_relay
#        drain_feedback = self.smu_drain_source_feedback
#        drain_switch_channel = self._drain_source_switch_channel
#        drain_switch_voltage = self._drain_source_switch_voltage

#        main_feedback = self.smu_main_feedback
#        feedback_multichannel = mfc.FANS_AI_MULTICHANNEL(self._fans_controller, drain_feedback, main_feedback)
#        fine_tuning = False
#        current_polarity = None
        
        
#        stabilization_counter = 50

#        #str_name = ".".join(["pid_test_Kp{0}Ki{1}Kd{2}V{3}".format(self.Kp, self.Ki, self.Kd,voltage).replace(".","_").replace(",","_"),"dat"])

#        #with open(str_name,"w") as test_file:
#        # check if value is in the range of ZERO_TRUST_ERROR
#        # if it is there -> move to the direction of value increasing.
#        # check polarity
#        # check if desired value is the same polarity as current value
#        # if so = move to value
#        # else 
#        # move to zero 
#        # then switch polarity 
#        # set desired voltage

#        output_channel = None
#        additional_output_channel = None
            
#        output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(drain_motor, drain_switch_channel)
#        assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
#        assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
#        additional_output_channel.analog_write(drain_switch_voltage)
#        assert isinstance(output_channel, mfc.FANS_AO_CHANNEL)

#        res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
#        sample_voltage = res[drain_feedback]
#        abs_sample_voltage = math.fabs(sample_voltage)
#        main_voltage = res[main_feedback]
            
#        if abs_sample_voltage < FANS_ZERO_VOLTAGE_INTERVAL:
#            # make small move to direction of increasing value to guess where we are in polarity terms
#            # important to do so before next block of code since it switches output channel off
#            #move to direction of increased value
#            increase_abs_voltage_control_value = ABS_VOLTAGE_INCREASE_DIRECTION * MIN_MOVING_VOLTAGE
#            output_channel.analog_write(increase_abs_voltage_control_value)
#            while abs_sample_voltage < FANS_ZERO_VOLTAGE_INTERVAL:
#                res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
#                sample_voltage = res[drain_feedback]
#                abs_sample_voltage = math.fabs(sample_voltage)
#            output_channel.analog_write(0)
              
#        current_polarity = FANS_NEGATIVE_POLARITY if sample_voltage < 0 else FANS_POSITIVE_POLARITY
                      
#        #def set_zero_voltage_for_channel(output_channel, 
                      
#        if sample_voltage * voltage < 0:
#            #desired value and current values are of different polarities
#            #set zero voltage
#            decrease_abs_voltage_control_value = ABS_VOLTAGE_DECREASE_DIRECTION * MAX_MOVING_VOLTAGE
#            error_check_length = 10
#            error_check_array = np.zeros(error_check_length)
#            error_check_counter = 0
#            output_channel.analog_write(decrease_abs_voltage_control_value)
#            while not ((np.std(error_check_array) < FANS_VOLTAGE_SET_ERROR) and (error_check_counter > error_check_length)):    #np.std(error_check_array) > self.DESIRED_ERROR or error_check_counter > error_check_length:
#                res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
#                sample_voltage = res[drain_feedback]
#                abs_sample_voltage = math.fabs(sample_voltage)
#                error_check_array  = np.roll(error_check_array,1)
#                error_check_array[0] = abs_sample_voltage
#                error_check_counter += 1 
#            output_channel.analog_write(0)
                
#            #switch polarity
#            current_polarity = -current_polarity
        
#            rel_ch = self._fans_controller.get_fans_output_channel(drain_relay)
#            rel_ch.analog_write(current_polarity)
#            time.sleep(0.5)
#            rel_ch.analog_write(0)

#            output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(drain_motor, drain_switch_channel)
#            assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
#            assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
#            additional_output_channel.analog_write(drain_switch_voltage)
                
#        VOLTAGE_SET_DIRECTION = ABS_VOLTAGE_INCREASE_DIRECTION if math.fabs(sample_voltage) < math.fabs(voltage) else -ABS_VOLTAGE_INCREASE_DIRECTION

#        #voltage  = math.fabs(voltage)
            
#        ref_time = time.time()
#        VoltageSetError = FANS_VOLTAGE_SET_ERROR
#        VoltageTuningInterval = FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION(VoltageSetError)

#        MAX_ALLOWED_ITERATIONS = 1000
#        iteration_counter = 0

#        while True:
#            res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
#            sample_voltage = res[drain_feedback]
#            abs_sample_voltage = math.fabs(sample_voltage)
#            main_voltage = res[main_feedback]
#            value_to_set = voltage_setting_function(sample_voltage,voltage, correction_coefficient = main_voltage/sample_voltage)
#            abs_distance = math.fabs(sample_voltage - voltage)

#            if abs_distance < VoltageSetError and fine_tuning: #FANS_VOLTAGE_SET_ERROR and fine_tuning:
#                # set high averaging, moving voltage to 0 and check condition again count times if is of return true if not repeat adjustment
#                output_channel.analog_write(0)
#                condition_sattisfied = True
#                for i in range(stabilization_counter):
#                    res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
#                    sample_voltage = res[drain_feedback]
#                    abs_sample_voltage = math.fabs(sample_voltage)
#                    main_voltage = res[main_feedback]

#                    #current_value = self.analog_read(feedback_channel)
#                    abs_distance = math.fabs(sample_voltage - voltage)

#                    print("current distanse: {0}, trust_error: {1}, count: {2}, value: {3}".format(abs_distance, VoltageSetError, i, sample_voltage))
#                    iteration_counter += 1
#                    if iteration_counter > MAX_ALLOWED_ITERATIONS:
#                        break

#                    if abs_distance > VoltageSetError:
#                        condition_sattisfied = False
#                        iteration_counter = 0
#                        break

#                if condition_sattisfied:
#                    return True
#            #self.set_analog_read_averaging(fine_averaging)
#            #current_value = self.analog_read(feedback_channel)
#            #abs_distance = math.fabs(current_value - voltage)
#            #if abs_distance < VoltageSetError:
#            #    return True
#            ##for i in range(stabilization_counter):
#            ##    current_value = self.analog_read(feedback_channel)
#            #self.set_analog_read_averaging(coarse_averaging)


#            elif abs_distance < VoltageTuningInterval or fine_tuning: #FANS_VOLTAGE_FINE_TUNING_INTERVAL:
#                fine_tuning = True
#                value_to_set = voltage_setting_function(sample_voltage,voltage,True)
#                iteration_counter += 1
#                if iteration_counter > MAX_ALLOWED_ITERATIONS:
#                        break

                
#            value_to_set = VOLTAGE_SET_DIRECTION * value_to_set
#            abs_value_to_set = math.fabs(value_to_set)
#            if abs_value_to_set > MAX_MOVING_VOLTAGE:
#                abs_value_to_set = MAX_MOVING_VOLTAGE

#            value_to_set = math.copysign(abs_value_to_set, value_to_set)
#            output_channel.analog_write(value_to_set)
#        output_channel.analog_write(0)
#    #def __set_drain_source_voltage(self,voltage, voltage_set_channel, relay_channel, feedback_channel, additional_channel = None, additional_control_voltage = 0.0):
#    #    assert isinstance(voltage, float) or isinstance(voltage, int)
#    #    assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS)
#    #    assert isinstance(relay_channel, mfc.FANS_AO_CHANNELS)
#    #    assert isinstance(feedback_channel, mfc.FANS_AI_CHANNELS)
#    #    assert isinstance(additional_control_voltage, float)

#    #    output_channel = None
#    #    additional_output_channel = None

#    #    if isinstance(additional_channel, mfc.FANS_AO_CHANNELS):
#    #        output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(voltage_set_channel, additional_channel)
#    #        assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
#    #        assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
#    #        additional_output_channel.analog_write(additional_control_voltage)
#    #    else:
#    #        output_channel = self._fans_controller.get_fans_output_channel(voltage_set_channel)

#    #    #self._fans_controller.fans_ao_switch.select_channel(voltage_set_channel)
#    #    assert isinstance(output_channel, mfc.FANS_AO_CHANNEL)

#    #    #set read averaging to small value for fast acquisition
#    #    coarse_averaging = 20
#    #    fine_averaging = 50
#    #    stabilization_counter = 200

#    #    self.smu_averaging_number = coarse_averaging

#    #    prev_value = self.analog_read(feedback_channel)
#    #    fine_tuning = False
#    #    polarity_switched = False
        
#    #    VoltageSetError = FANS_VOLTAGE_SET_ERROR
#    #    VoltageTuningInterval = FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION(VoltageSetError)

#    #    # Adding here correction for ressitance relation
#    #    feedback_multichannel = mfc.FANS_AI_MULTICHANNEL(self._fans_controller, self.smu_drain_source_feedback, self.smu_main_feedback)


#    #    if math.fabs(voltage) < FANS_ZERO_VOLTAGE_INTERVAL :
#    #        VoltageSetError = FANS_ZERO_VOLTAGE_INTERVAL
#    #        VoltageTuningInterval =  VoltageTuningInterval+VoltageSetError     #5*VoltageSetError   

#    #    while True: #continue_setting:    
#    #        res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
#    #        current_value  = res[self.smu_drain_source_feedback]
#    #        main_voltage = res[self.smu_main_feedback]

#    #        #current_value = self.analog_read(feedback_channel)

#    #        if current_value*voltage<0 and not polarity_switched:
#    #            set_result = self.__set_drain_source_voltage(0, voltage_set_channel, relay_channel, feedback_channel,additional_channel, additional_control_voltage )
        
#    #            if set_result:
#    #                polarity = FANS_NEGATIVE_POLARITY if voltage<0 else FANS_POSITIVE_POLARITY
#    #                self.__set_voltage_polarity(polarity, voltage_set_channel, relay_channel, additional_channel, additional_control_voltage)
#    #                polarity_switched = True
#    #            else:
#    #                return set_result

#    #        value_to_set = voltage_setting_function(current_value,voltage, correction_coefficient = main_voltage/current_value)
#    #        abs_distance = math.fabs(current_value - voltage)

#    #        if abs_distance < VoltageSetError and fine_tuning: #FANS_VOLTAGE_SET_ERROR and fine_tuning:
#    #            # set high averaging, moving voltage to 0 and check condition again count times if is of return true if not repeat adjustment
#    #            output_channel.analog_write(0)
#    #            condition_sattisfied = True
#    #            for i in range(fine_averaging):
#    #                current_value = self.analog_read(feedback_channel)
#    #                abs_distance = math.fabs(current_value - voltage)

#    #                print("current distanse: {0}, trust_error: {1}, count: {2}, value: {3}".format(abs_distance, VoltageSetError, i, current_value))
#    #                if abs_distance > VoltageSetError:
#    #                    condition_sattisfied = False
#    #                    break

#    #            if condition_sattisfied:
#    #                return True
#    #            #self.set_analog_read_averaging(fine_averaging)
#    #            #current_value = self.analog_read(feedback_channel)
#    #            #abs_distance = math.fabs(current_value - voltage)
#    #            #if abs_distance < VoltageSetError:
#    #            #    return True
#    #            ##for i in range(stabilization_counter):
#    #            ##    current_value = self.analog_read(feedback_channel)
#    #            #self.set_analog_read_averaging(coarse_averaging)


#    #        elif abs_distance < VoltageTuningInterval or fine_tuning: #FANS_VOLTAGE_FINE_TUNING_INTERVAL:
#    #            fine_tuning = True
#    #            value_to_set = voltage_setting_function(current_value,voltage,True)
            
            
            
#    #        if polarity_switched:
#    #            abs_value = math.fabs(value_to_set)
#    #            if voltage * current_value < 0:
#    #                if voltage > 0:
#    #                    value_to_set = abs_value
#    #                else:
#    #                    value_to_set = -abs_value
#    #        print("current: {0}; goal: {1};to set: {2};".format(current_value,voltage, value_to_set))    
#    #        output_channel.analog_write(value_to_set)
#    #        #output_channel.ao_voltage = value_to_set 

#    #def smu_set_drain_source_voltage(self, voltage):
#    #    self.__set_drain_source_voltage(voltage, self.smu_ds_motor, self.smu_ds_relay, self.smu_drain_source_feedback, self._drain_source_switch_channel, self._drain_source_switch_voltage)

#    #def smu_set_gate_voltage(self, voltage):
#    #    return super().__set
    

#    def read_all_test(self):
#        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
#        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
#        print ("stabilizing voltages after drain switch on. waiting...")
#        time.sleep(5)
#        result = super().read_all_test() 
#        drain_source_switch_channel.analog_write(0)
#        return result

#    def read_feedback_voltages(self):
#        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
#        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
#        print ("stabilizing voltages after drain switch on. waiting...")
#        time.sleep(5)
#        result = super().read_feedback_voltages()
#        drain_source_switch_channel.analog_write(0)
#        return result

#    def read_all_parameters(self):
#        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
#        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
#        print ("stabilizing voltages after drain switch on. waiting...")
#        time.sleep(5)
#        result = super().read_all_parameters()
#        drain_source_switch_channel.analog_write(0)
#        return result

ZERO_TRUST_INTERVAL = 0.02
ABS_VOLTAGE_INCREASE_DIRECTION = -1
ABS_VOLTAGE_DECREASE_DIRECTION = 1

def pid_voltage_settings_function(current_value, set_value, fine_tuning = False, correction_coefficient = 1):
    # fermi-dirac-distribution
    result = 0

    #sign = 1 if current_value > set_value else -1

    #correction_coefficient = 1
    if correction_coefficient <= 1:
        correction_coefficient = 1

    if fine_tuning:
        #return MIN_MOVING_VOLTAGE
        #return sign*MIN_MOVING_VOLTAGE
        result = correction_coefficient *MIN_MOVING_VOLTAGE
    else:
        diff = math.fabs(current_value-set_value)
        result = (MAX_MOVING_VOLTAGE + (MIN_MOVING_VOLTAGE-MAX_MOVING_VOLTAGE)/(1+math.pow(diff/X0_VOLTAGE_SET,POWER_VOLTAGE_SET)))
        if result < MIN_MOVING_VOLTAGE:
            result = MIN_MOVING_VOLTAGE
        elif result> MAX_MOVING_VOLTAGE:
            result = MAX_MOVING_VOLTAGE
        result = correction_coefficient * result

    #result = sign * result
    return result
        #try:

class FANS_SMU_PID(FANS_SMU_Specialized):
    #Kp = 1
    #Ki = 0
    #Kd = 0
    DESIRED_ERROR = 0.002

    def __init__(self, fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback, gate_motor, gate_relay, gate_feedback, main_feedback, drain_source_switch_channel, drain_source_switch_voltage = DRAIN_SOURCE_SWITCH_VOLTAGE, Kp = 1, Ki = 0, Kd = 0):
        super().__init__(fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback, gate_motor, gate_relay, gate_feedback, main_feedback, drain_source_switch_channel, drain_source_switch_voltage)
        #FANS_SMU_Specialized.__init__(fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback, gate_motor, gate_relay, gate_feedback, main_feedback, drain_source_switch_channel, drain_source_switch_voltage)
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd

    @property
    def Kp(self):
        return self._Kp
    
    @Kp.setter
    def Kp(self, value):
        self._Kp = value

    @property
    def Ki(self):
        return self._Ki
    
    @Ki.setter
    def Ki(self, value):
        self._Ki = value

    @property
    def Kd(self):
        return self._Kd
    
    @Kd.setter
    def Kd(self, value):
        self._Kd = value

    
            
            #output_channel.analog_write(0)
    def smu_set_drain_source_voltage(self, voltage):
        drain_motor = self.smu_ds_motor
        drain_relay = self.smu_ds_relay
        drain_feedback = self.smu_drain_source_feedback
        drain_switch_channel = self._drain_source_switch_channel
        drain_switch_voltage = self._drain_source_switch_voltage

        main_feedback = self.smu_main_feedback
        feedback_multichannel = mfc.FANS_AI_MULTICHANNEL(self._fans_controller, drain_feedback, main_feedback)

        pid = mfpid.FANS_PID(self._Kp, self._Ki, self._Kd,self.DESIRED_ERROR, points_to_check_error = 100) #self.pid_controller
        pid.sampling_time = 0.001
        #pid.clear()
        pid.guard_value = MAX_MOVING_VOLTAGE
        pid.desired_error = self.DESIRED_ERROR
        current_polarity = None
        
        str_name = ".".join(["pid_test_Kp{0}Ki{1}Kd{2}V{3}".format(self.Kp, self.Ki, self.Kd,voltage).replace(".","_").replace(",","_"),"dat"])

        with open(str_name,"w") as test_file:
        # check if value is in the range of ZERO_TRUST_ERROR
        # if it is there -> move to the direction of value increasing.
        # check polarity
        # check if desired value is the same polarity as current value
        # if so = move to value
        # else 
        # move to zero 
        # then switch polarity 
        # set desired voltage

            output_channel = None
            additional_output_channel = None
            
            output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(drain_motor, drain_switch_channel)
            assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
            assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
            additional_output_channel.analog_write(drain_switch_voltage)
            assert isinstance(output_channel, mfc.FANS_AO_CHANNEL)

            res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
            sample_voltage = res[drain_feedback]
            abs_sample_voltage = math.fabs(sample_voltage)
            main_voltage = res[main_feedback]
            
            if abs_sample_voltage < FANS_ZERO_VOLTAGE_INTERVAL:
                # make small move to direction of increasing value to guess where we are in polarity terms
                # important to do so before next block of code since it switches output channel off
                #move to direction of increased value
                increase_abs_voltage_control_value = ABS_VOLTAGE_INCREASE_DIRECTION * MIN_MOVING_VOLTAGE
                output_channel.analog_write(increase_abs_voltage_control_value)
                while abs_sample_voltage < FANS_ZERO_VOLTAGE_INTERVAL:
                    res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
                    sample_voltage = res[drain_feedback]
                    abs_sample_voltage = math.fabs(sample_voltage)
                output_channel.analog_write(0)
              
            current_polarity = FANS_NEGATIVE_POLARITY if sample_voltage < 0 else FANS_POSITIVE_POLARITY
                      
            #def set_zero_voltage_for_channel(output_channel, 
                      
            if sample_voltage * voltage < 0:
                #desired value and current values are of different polarities
                #set zero voltage
                decrease_abs_voltage_control_value = ABS_VOLTAGE_DECREASE_DIRECTION * MAX_MOVING_VOLTAGE
                error_check_length = 10
                error_check_array = np.zeros(error_check_length)
                error_check_counter = 0
                output_channel.analog_write(decrease_abs_voltage_control_value)
                while not ((np.std(error_check_array) < self.DESIRED_ERROR) and (error_check_counter > error_check_length)):    #np.std(error_check_array) > self.DESIRED_ERROR or error_check_counter > error_check_length:
                    res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
                    sample_voltage = res[drain_feedback]
                    abs_sample_voltage = math.fabs(sample_voltage)
                    error_check_array  = np.roll(error_check_array,1)
                    error_check_array[0] = abs_sample_voltage
                    error_check_counter += 1 
                output_channel.analog_write(0)
                
                #switch polarity
                current_polarity = -current_polarity
        
                rel_ch = self._fans_controller.get_fans_output_channel(drain_relay)
                rel_ch.analog_write(current_polarity)
                time.sleep(0.5)
                rel_ch.analog_write(0)

                output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(drain_motor, drain_switch_channel)
                assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
                assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
                additional_output_channel.analog_write(drain_switch_voltage)
                
            VOLTAGE_SET_DIRECTION = ABS_VOLTAGE_INCREASE_DIRECTION if math.fabs(sample_voltage) < math.fabs(voltage) else -ABS_VOLTAGE_INCREASE_DIRECTION

            #voltage  = math.fabs(voltage)
            pid.SetPoint = voltage
            ref_time = time.time()
            try:
                while(True):
                    res = feedback_multichannel.analog_read()
                    sample_voltage = res[drain_feedback]
                    main_voltage = res[main_feedback]

                    correction = math.fabs(main_voltage/sample_voltage)
                    if correction <= 1:
                        correction = 1

                    #sample_voltage = math.fabs(sample_voltage)

                    current_time = time.time() - ref_time
                    test_file.write("{0}\t{1}\n".format(current_time,sample_voltage))

                    print("{0}\t{1}\t{2}\t{3}".format(current_time, voltage, sample_voltage, main_voltage))
                    
                    value_to_set = VOLTAGE_SET_DIRECTION * pid.update(sample_voltage)
                    # correction for resistances
                    value_to_set = correction * value_to_set
                    abs_value_to_set = math.fabs(value_to_set)
                    abs_value_to_set += MIN_MOVING_VOLTAGE
                    if abs_value_to_set > MAX_MOVING_VOLTAGE:
                        abs_value_to_set = MAX_MOVING_VOLTAGE

                    value_to_set = math.copysign(abs_value_to_set, value_to_set)
                    print("value to set {0}".format(value_to_set))
                    output_channel.analog_write(value_to_set)

            except mfpid.PID_ReachedDesiredErrorException:
                print("reached desired error")
                return True
            except mfpid.PID_ErrorNotChangingException:
                print("error is not changing")
                return False
            except mfpid.PID_ReachedMaximumAllowedUpdatesException:
                print("max updates reached")
                return False
            else:
                return True
            finally:
                output_channel.analog_write(0)

#def set_voltage_using_pid_controller(pid_controller, voltage_set_channel, 


def test_pid_smu():
    f = mfc.FANS_CONTROLLER("ADC");   #USB0::0x0957::0x1718::TW52524501::INSTR")
    
    smu = FANS_SMU_PID(f, mfc.FANS_AO_CHANNELS.AO_CH_1,
                   mfc.FANS_AO_CHANNELS.AO_CH_4, 
                   mfc.FANS_AI_CHANNELS.AI_CH_6, 
                   mfc.FANS_AO_CHANNELS.AO_CH_9,
                   mfc.FANS_AO_CHANNELS.AO_CH_12, 
                   mfc.FANS_AI_CHANNELS.AI_CH_8,
                   mfc.FANS_AI_CHANNELS.AI_CH_7,
                   mfc.FANS_AO_CHANNELS.AO_CH_10
                   

                   ) #main
    smu.Kp = 4
    smu.Ki = 0.025 # 0.01 #0.01 #0.5#10000
    smu.Kd = 100 #10 #0.5 #  0.05
    
    smu.set_smu_parameters(100, 100000)
    smu.init_smu_mode()

    try:
        smu.smu_set_drain_source_voltage(-0.5)
        #smu.smu_set_drain_source_voltage(0)

    except Exception as e:
        #raise
        print(str(e))
    finally:
        f.switch_all_fans_output_state(mfc.SWITCH_STATES.OFF)

   

def fans_test_2():
    
    f = mfc.FANS_CONTROLLER("ADC");   #USB0::0x0957::0x1718::TW52524501::INSTR")
    f.daq_parent_device.debug_mode = False
    smu = FANS_SMU_Specialized(f, mfc.FANS_AO_CHANNELS.AO_CH_1,
                   mfc.FANS_AO_CHANNELS.AO_CH_4, 
                   mfc.FANS_AI_CHANNELS.AI_CH_6,
                   mfc.FANS_AO_CHANNELS.AO_CH_9,
                   mfc.FANS_AO_CHANNELS.AO_CH_12, 
                   mfc.FANS_AI_CHANNELS.AI_CH_7,
                   mfc.FANS_AI_CHANNELS.AI_CH_8,
                   mfc.FANS_AO_CHANNELS.AO_CH_10
                   ) 

    smu.set_smu_parameters(100, 100000)
    smu.init_smu_mode()

    try:

        #while True:
        #    smu.read_all_test()
        #    time.sleep(0.5)

        smu.smu_set_drain_source_voltage(-0.1)
        #for vg in np.arange(-2,2,0.5):
        #  print("setting gate")
        #  smu.smu_set_gate_voltage(vg)
        #  print(smu.read_all_parameters())
          
        #  time.sleep(2)

        #smu.smu_set_drain_source_voltage(1)
        #smu.smu_set_gate_voltage(1) 
        #smu.smu_set_drain_source_voltage(-1)
        #smu.smu_set_gate_voltage(-1)

        #smu.smu_set_drain_source_voltage(0)
        #smu.smu_set_gate_voltage(0)


        #print("finish")
        #smu.smu_set_drain_source_voltage(-1)
        #print(smu.read_all_parameters())
    except Exception as e:
        raise
        print(str(e))
    finally:
        f.switch_all_fans_output_state(mfc.SWITCH_STATES.OFF)
  

if __name__ == "__main__":
    #test_pid_smu()
    fans_test_2()









     #if voltage * sample_voltage < 0:
            #    #set 0 volts
            #    pid.SetPoint = 0
            #    try:
            #        while(True):
            #            res = feedback_multichannel.analog_read() #self.analog_read(feedback_channel)
            #            sample_voltage = res[drain_feedback]
            #            main_voltage = res[main_feedback]
            #            print("{0}\t{1}\t{2}\t{3}".format(time.time(), voltage, sample_voltage, main_voltage))
                    
            #            value_to_set = VOLTAGE_SET_DIRECTION * pid.update(sample_voltage)
            #            #value_to_set = pid.update(math.fabs(sample_voltage))
            #            # correction for resistances
            #            correction = math.fabs(main_voltage/sample_voltage)
            #            if correction <= 1:
            #                correction = 1
    
            #            value_to_set = correction * value_to_set
            #            abs_value_to_set = math.fabs(value_to_set)
            #            abs_value_to_set += MIN_MOVING_VOLTAGE
            #            if abs_value_to_set > MAX_MOVING_VOLTAGE:
            #                abs_value_to_set = MAX_MOVING_VOLTAGE

            #            value_to_set = math.copysign(abs_value_to_set, value_to_set)
            #            #value_to_set = math.copysign(abs_value_to_set, VOLTAGE_SET_DIRECTION)
            #            output_channel.analog_write(value_to_set)

            #    except mfpid.PID_ReachedDesiredErrorException:
            #        print("reached desired error")#return True
            #    except mfpid.PID_ErrorNotChangingException:
            #        print("error is not changing")
            #        if math.fabs(sample_voltage) > ZERO_TRUST_INTERVAL:
            #            return False
            #    except mfpid.PID_ReachedMaximumAllowedUpdatesException:
            #        print("max updates reached")
            #        return False
            #    else:
            #        pass#return True

            #    #switch polarity here 
            #    if voltage >= 0:
            #        current_polarity = FANS_POSITIVE_POLARITY
            #    else :
            #        current_polarity = FANS_NEGATIVE_POLARITY

            #    self.__set_voltage_polarity(polarity, drain_motor,drain_relay, drain_switch_channel, drain_switch_voltage)

                #set desired voltage