import time
import math

import modern_fans_controller as mfc
import modern_agilent_u2542a as mdaq
import numpy as np

DRAIN_SOURCE_SWITCH_VOLTAGE = 8.4


MIN_MOVING_VOLTAGE = 0.3
MAX_MOVING_VOLTAGE = 6
VALUE_DIFFERENCE = MAX_MOVING_VOLTAGE-MIN_MOVING_VOLTAGE
FD_CONST = -0.1

FANS_VOLTAGE_SET_ERROR  = 0.002  #mV
FANS_VOLTAGE_FINE_TUNING_INTERVAL = 5*FANS_VOLTAGE_SET_ERROR  #### set here function for interval selection

A1 = 0.01
A2 = 0.002
X0 = 0.007
p = 3

FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION = lambda error: A2 + (A1 - A2)/(1+math.pow(error/X0,p))

FANS_ZERO_VOLTAGE_INTERVAL = 0.01#0.005

FANS_VOLTAGE_SET_MAXITER = 10000

FANS_POLARITY_CHANGE_VOLTAGE = (-5,5)
FANS_NEGATIVE_POLARITY,FANS_POSITIVE_POLARITY = FANS_POLARITY_CHANGE_VOLTAGE
 
X0_VOLTAGE_SET = 0.1
POWER_VOLTAGE_SET = 5#3


def voltage_setting_function(current_value, set_value, fine_tuning = False):
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
    
    if fine_tuning:
        #return MIN_MOVING_VOLTAGE
        return sign*MIN_MOVING_VOLTAGE
    else:
        diff = math.fabs(current_value-set_value)
        return sign*(MAX_MOVING_VOLTAGE + (MIN_MOVING_VOLTAGE-MAX_MOVING_VOLTAGE)/(1+math.pow(diff/X0_VOLTAGE_SET,POWER_VOLTAGE_SET)))
        

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
        self.set_smu_parameters(self.smu_averaging_number, self.smu_load_resistance)


    def set_smu_parameters(self, averaging, load_resistance):
        self.smu_load_resistance = load_resistance
        self.smu_averaging_number = averaging
        
    

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
        output_channel = self._fans_controller.get_fans_output_channel(voltage_set_channel)
        output_channel.ao_voltage = direction*speed
        time.sleep(timeout)
        output_channel.ao_voltage = 0

    def move_ds_motor_left(self):
        self.move_motor(self._drain_source_motor, -1, LOW_SPEED, SHORT_TIME)

    def move_ds_motor_left_fast(self):
        self.move_motor(self._drain_source_motor, -1, FAST_SPEED, LONG_TIME)

    def move_ds_motor_right(self):
        self.move_motor(self._drain_source_motor, 1, LOW_SPEED, SHORT_TIME)

    def move_ds_motor_right_fast(self):
        self.move_motor(self._drain_source_motor, 1, FAST_SPEED, LONG_TIME)

    def move_gate_motor_left(self):
        self.move_motor(self._gate_motor, -1, LOW_SPEED,SHORT_TIME)

    def move_gate_motor_left_fast(self):
        self.move_motor(self._gate_motor, -1, FAST_SPEED, LONG_TIME)

    def move_gate_motor_right(self):
        self.move_motor(self._gate_motor, 1, LOW_SPEED, SHORT_TIME)

    def move_gate_motor_right_fast(self):
        self.move_motor(self._gate_motor, 1, FAST_SPEED, LONG_TIME)

   
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

        fans_channels = [self._fans_controller.get_fans_channel_by_name(ch) for ch in channels]
        fans_multichannel = mfc.FANS_AI_MULTICHANNEL(*fans_channels)
        result = fans_multichannel.analog_read()
        converted_dict = {ch: result[fans_ch.ai_daq_input] for ch, fans_ch in zip(channels,fans_channels) }
        return converted_dict

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
        
        return {"Vds":ds_voltage,"Vgs":gate_voltage,"Vmain":main_voltage, "Ids":current,"Rs":resistance}




class FANS_SMU_Specialized(FANS_SMU):
    def __init__(self, fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback, drain_source_switch_channel, drain_source_switch_voltage = DRAIN_SOURCE_SWITCH_VOLTAGE):
        super().__init__(fans_controller, drain_source_motor, drain_source_relay, drain_source_feedback,  gate_motor, gate_relay, gate_feedback, main_feedback)
        assert isinstance(drain_source_switch_channel, mfc.FANS_AO_CHANNELS)
        assert isinstance(drain_source_switch_voltage, float)

        self._drain_source_switch_channel = drain_source_switch_channel
        self._drain_source_switch_voltage = drain_source_switch_voltage


    def __set_voltage_polarity(self, polarity, voltage_set_channel, relay_channel, additional_channel = None, additional_control_voltage = 0.0):
        assert isinstance(relay_channel, mfc.FANS_AO_CHANNELS), "Wrong channel!"
        assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS), "Wrong channel!"
        assert isinstance(additional_control_voltage, float)
        rel_ch = self._fans_controller.get_fans_output_channel(relay_channel) #.fans_ao_switch.select_channel(relay_channel)
        #assert isinstance(rel_ch, mfc.FANS_AO_CHANNEL)
        rel_ch.analog_write(polarity)
        time.sleep(0.5)
        rel_ch.analog_write(0)

        if isinstance(additional_channel, mfc.FANS_AO_CHANNELS):
            output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(voltage_set_channel, additional_channel)
            assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
            assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
            additional_output_channel.analog_write(additional_control_voltage)
        else:
            self._fans_controller.get_fans_output_channel(voltage_set_channel)


    def __set_voltage_for_function(self,voltage, voltage_set_channel, relay_channel, feedback_channel, additional_channel = None, additional_control_voltage = 0.0):
        assert isinstance(voltage, float) or isinstance(voltage, int)
        assert isinstance(voltage_set_channel, mfc.FANS_AO_CHANNELS)
        assert isinstance(relay_channel, mfc.FANS_AO_CHANNELS)
        assert isinstance(feedback_channel, mfc.FANS_AI_CHANNELS)
        assert isinstance(additional_control_voltage, float)

        output_channel = None
        additional_output_channel = None

        if isinstance(additional_channel, mfc.FANS_AO_CHANNELS):
            output_channel, additional_output_channel = self._fans_controller.get_fans_output_channels(voltage_set_channel, additional_channel)
            assert output_channel != additional_output_channel, "Cannot use same channel for different functions"
            assert isinstance(additional_output_channel, mfc.FANS_AO_CHANNEL)
            additional_output_channel.analog_write(additional_control_voltage)
        else:
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
                set_result = self.__set_voltage_for_function(0, voltage_set_channel, relay_channel, feedback_channel,additional_channel, additional_control_voltage )
        
                if set_result:
                    polarity = FANS_NEGATIVE_POLARITY if voltage<0 else FANS_POSITIVE_POLARITY
                    self.__set_voltage_polarity(polarity, voltage_set_channel, relay_channel, additional_channel, additional_control_voltage)
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
                #self.set_analog_read_averaging(fine_averaging)
                #current_value = self.analog_read(feedback_channel)
                #abs_distance = math.fabs(current_value - voltage)
                #if abs_distance < VoltageSetError:
                #    return True
                ##for i in range(stabilization_counter):
                ##    current_value = self.analog_read(feedback_channel)
                #self.set_analog_read_averaging(coarse_averaging)


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

    def smu_set_drain_source_voltage(self, voltage):
        self.__set_voltage_for_function(voltage, self.smu_ds_motor, self.smu_ds_relay, self.smu_drain_source_feedback, self._drain_source_switch_channel, self._drain_source_switch_voltage)

    

    def read_all_test(self):
        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        result = super().read_all_test() 
        drain_source_switch_channel.analog_write(0)
        return result

    def read_feedback_voltages(self):
        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        result = super().read_feedback_voltages()
        drain_source_switch_channel.analog_write(0)
        return result

    def read_all_parameters(self):
        drain_source_switch_channel = self._fans_controller.get_fans_output_channel(self._drain_source_switch_channel)
        drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        result = super().read_all_parameters()
        drain_source_switch_channel.analog_write(0)
        return result


if __name__ == "__main__":

   
    f = mfc.FANS_CONTROLLER("ADC");   #USB0::0x0957::0x1718::TW52524501::INSTR")
    
    smu = FANS_SMU(f, mfc.FANS_AO_CHANNELS.AO_CH_1,
                   mfc.FANS_AO_CHANNELS.AO_CH_4, 
                   mfc.FANS_AI_CHANNELS.AI_CH_2, #ds
                   mfc.FANS_AO_CHANNELS.AO_CH_9,
                   mfc.FANS_AO_CHANNELS.AO_CH_12, 
                   mfc.FANS_AI_CHANNELS.AI_CH_4, #gate
                   mfc.FANS_AI_CHANNELS.AI_CH_3) #main

    smu.set_smu_parameters(100, 5000)
    smu.init_smu_mode()

    try:

        #while True:
        #    smu.read_all_test()
        #    time.sleep(0.5)

        smu.smu_set_drain_source_voltage(0.1)
        for vg in np.arange(-2,2,0.5):
          print("setting gate")
          smu.smu_set_gate_voltage(vg)
          print(smu.read_all_parameters())
          
          time.sleep(2)

        smu.smu_set_drain_source_voltage(1)
        smu.smu_set_gate_voltage(1) 
        smu.smu_set_drain_source_voltage(-1)
        smu.smu_set_gate_voltage(-1)

        smu.smu_set_drain_source_voltage(0)
        smu.smu_set_gate_voltage(0)


        print("finish")
        smu.smu_set_drain_source_voltage(-1)
        print(smu.read_all_parameters())
    except Exception as e:
        raise
        print(str(e))
    finally:
        f.switch_all_fans_output_state(mfc.SWITCH_STATES.OFF)
  