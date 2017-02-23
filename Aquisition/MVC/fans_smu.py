import time
import math
from fans_controller import FANS_controller
from fans_constants import *
from agilent_u2542a_constants import *
from node_configuration import Configuration
import numpy as np

MIN_MOVING_VOLTAGE = 0.5
MAX_MOVING_VOLTAGE = 6
VALUE_DIFFERENCE = MAX_MOVING_VOLTAGE-MIN_MOVING_VOLTAGE
FD_CONST = -0.1

FANS_VOLTAGE_SET_ERROR  = 0.001  #mV
FANS_VOLTAGE_FINE_TUNING_INTERVAL = 5*FANS_VOLTAGE_SET_ERROR  #### set here function for interval selection

A1 = 0.006
A2 = 0.002
X0 = 0.01
p = 3

FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION = lambda error: A2 + (A1 - A2)/(1+math.pow(error/X0,p))


FANS_ZERO_VOLTAGE_INTERVAL = 0.02#0.005

FANS_VOLTAGE_SET_MAXITER = 10000

FANS_POLARITY_CHANGE_VOLTAGE = (-5,5)
FANS_NEGATIVE_POLARITY,FANS_POSITIVE_POLARITY = FANS_POLARITY_CHANGE_VOLTAGE
 


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
        try:
            exponent = math.exp(diff/FD_CONST)
        except OverflowError:
            exponent = float("inf")
        
        #return (MIN_MOVING_VOLTAGE + VALUE_DIFFERENCE/(exponent+1))
        return sign*(MIN_MOVING_VOLTAGE + VALUE_DIFFERENCE/(exponent+1))

OUT_ENABLED_CH, OUT_CH, FEEDBACK_CH, POLARITY_RELAY_CH , CH_POLARITY = [0,1,2,3,4]
# output channel - A0_BOX_CHANNELS
# feedback_channel - AI_BOX_CHANNELS
def generate_state_dictionary(enabled, output_channel, feedback_channel, polarity_relay_channel):
    return {OUT_ENABLED_CH:enabled, OUT_CH:output_channel, FEEDBACK_CH:feedback_channel, POLARITY_RELAY_CH: polarity_relay_channel, CH_POLARITY:FANS_POSITIVE_POLARITY}



class fans_smu:
    def __init__(self, fans_controller):
        self.fans_controller = fans_controller
        self.load_resistance = fans_controller.load_resistance

        self.state_dictionary = dict()
        self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage] = generate_state_dictionary(True,0,0,0) # {OUT_CH:0, FEEDBACK_CH:1}
        self.state_dictionary[FANS_AI_FUNCTIONS.MainVoltage]= generate_state_dictionary(True,None,0,0)
        self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage]=generate_state_dictionary(True, 0,0,0) #{OUT_CH:0, FEEDBACK_CH:1}

        #self.ao_ch1_hardware_voltage = 0
        #self.ao_ch2_hardware_voltage = 0
        #self.ao_ch1_enabled = True
        #self.ao_ch2_enabled = True
        #self.fans_drain_source_set_channel = 0
        #self.fans_drain_source_set_channel = 0


        #self._init_fans_ao_channels()
        #self.init_smu_mode()
        


    def _init_fans_ao_channels(self):
        #self.fans_controller._set_output_channels(self.fans_drain_source_set_channel,self.ao_ch1_enabled,self.fans_drain_source_set_channel,self.ao_ch2_enabled)
        ao1_channel = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][OUT_CH]
        ao1_enabled = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][OUT_ENABLED_CH]
        ao2_channel = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][OUT_CH]
        ao2_enabled = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][OUT_ENABLED_CH]
        self.fans_controller._set_output_channels(ao1_channel,ao1_enabled,ao2_channel,ao2_enabled)

    def init_smu_mode(self):
        for ch in [FANS_AI_FUNCTIONS.DrainSourceVoltage, FANS_AI_FUNCTIONS.GateVoltage, FANS_AI_FUNCTIONS.MainVoltage]:
            self.fans_controller.set_fans_ai_channel_mode(AI_MODES.AC,self.state_dictionary[ch][FEEDBACK_CH])
        #self.fans_controller.set_fans_ai_channel_mode(AI_MODES.DC,channel)
        #self.fans_controller.analog_read_averaging(1000)

   
    def set_fans_ao_relay_channel_for_function(self,function, ao_channel):
        self.state_dictionary[function][POLARITY_RELAY_CH] = ao_channel
   
    def set_fans_ao_channel_for_function(self,function, ao_channel,enabled):
        self.state_dictionary[function][OUT_CH] = ao_channel
        self.state_dictionary[function][OUT_ENABLED_CH] = enabled
        self.fans_controller.set_selected_output(ao_channel,enabled)
      
    def set_fans_ao_polarity_for_function(self,function, polarity):
        self.state_dictionary[function][CH_POLARITY] = polarity

    def set_fans_ao_feedback_for_function(self,function,feedback):
        self.state_dictionary[function][FEEDBACK_CH] = feedback

    def set_hardware_voltage(self,voltage, channel):
        self.fans_controller.fans_output_channel_voltage(voltage, channel)

    def set_hardware_voltage_channels(self, voltage, channels):
        self.fans_controller.fans_output_voltage_to_channels(voltage,channels)

    def set_hardware_voltages(self,channel_voltage_pairs):
        for channel,voltage in channel_voltage_pairs:
            self.fans_controller.fans_output_channel_voltage(voltage, channel)

    def analog_read(self,channels):
        return self.fans_controller.analog_read(channels)


    def __start_polarity_change(self,function):
        box_ao_ch = self.state_dictionary[function][OUT_CH]
        ao_ch = BOX_AO_CHANNEL_MAP[box_ao_ch]
        switch_ch = self.state_dictionary[function][POLARITY_RELAY_CH]
        
        self.set_hardware_voltage(0,ao_ch)
        self.fans_controller._set_output_channel(switch_ch,STATES.ON)
        
        #self.fans_controller._set_output_channels(
    def __stop_polarity_change(self,function):
        box_ao_ch = self.state_dictionary[function][OUT_CH]
        ao_ch = BOX_AO_CHANNEL_MAP[box_ao_ch]
        #out_ch = self.state_dictionary[function][POLARITY_RELAY_CH]
        self.set_hardware_voltage(0,ao_ch)
        self.fans_controller._set_output_channel(box_ao_ch,STATES.ON)


    def set_fans_output_polarity(self,polarity,function):
        self.__start_polarity_change(function)
        box_ao_ch = self.state_dictionary[function][POLARITY_RELAY_CH]
        ao_ch = BOX_AO_CHANNEL_MAP[box_ao_ch]
        self.set_hardware_voltage(polarity,ao_ch)
        time.sleep(0.5)
        self.set_hardware_voltage(0,ao_ch)
        self.state_dictionary[function][CH_POLARITY] = polarity
        #self.set_hardware_voltage(0,hardware_relay_ch)

        self.__stop_polarity_change(function)



    def set_fans_voltage_for_channel(self,voltage,function):

        ai_feedback = self.state_dictionary[function][FEEDBACK_CH]
        output_ch = self.state_dictionary[function][OUT_CH]

        hardware_feedback_ch = BOX_AI_CHANNELS_MAP[ai_feedback]["channel"]
        hardware_output_ch = BOX_AO_CHANNEL_MAP[output_ch]
       
        prev_value = self.analog_read(hardware_feedback_ch)[hardware_feedback_ch]
        fine_tuning = False
        polarity_switched = False
        
        VoltageSetError = FANS_VOLTAGE_SET_ERROR
        VoltageTuningInterval = FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION(VoltageSetError)

        if math.fabs(voltage) < FANS_ZERO_VOLTAGE_INTERVAL :
            VoltageSetError = FANS_ZERO_VOLTAGE_INTERVAL
            VoltageTuningInterval =  VoltageTuningInterval+VoltageSetError     #5*VoltageSetError   

        #VoltageSetError = FANS_ZERO_VOLTAGE_INTERVAL if math.fabs(voltage) < FANS_ZERO_VOLTAGE_INTERVAL else FANS_VOLTAGE_SET_ERROR
        #VoltageTuningInterval =  FANS_VOLTAGE_FINE_TUNING_INTERVAL_FUNCTION(VoltageSetError)   #5*VoltageSetError
        print("Voltage set error = {0}, Voltage Tuning Interval = {1}".format(VoltageSetError,VoltageTuningInterval))
        
        time.sleep(1)


        while True: #continue_setting:    
            values = self.analog_read(AI_CHANNELS.indexes)
            current_value = self.analog_read(hardware_feedback_ch)[hardware_feedback_ch]

            if current_value*voltage<0 and not polarity_switched:
                set_result = self.set_fans_voltage_for_channel(0,function)
                if set_result:
                    polarity = FANS_NEGATIVE_POLARITY if voltage<0 else FANS_POSITIVE_POLARITY
                    self.set_fans_output_polarity(polarity,function)
                    polarity_switched = True
                else:
                    return set_result

            print((FANS_AI_FUNCTIONS[function], current_value,voltage))
            value_to_set = voltage_setting_function(current_value,voltage)
            values["value_to_set"] = value_to_set

            abs_distance = math.fabs(current_value - voltage)
            if abs_distance < VoltageTuningInterval: #FANS_VOLTAGE_FINE_TUNING_INTERVAL:
                fine_tuning = True
                value_to_set = voltage_setting_function(current_value,voltage,True)
            
            if abs_distance < VoltageSetError and fine_tuning: #FANS_VOLTAGE_SET_ERROR and fine_tuning:
                self.set_hardware_voltage(0,hardware_output_ch)
                return True
            
            if polarity_switched:
                abs_value = math.fabs(value_to_set)
                if voltage * current_value < 0:
                    if voltage > 0:
                        value_to_set = -abs_value
                    else:
                        value_to_set = abs_value
                

            self.set_hardware_voltage(value_to_set,hardware_output_ch)



            

    def _start_setting_voltage(self,function):
        box_ao_ch = self.state_dictionary[function][OUT_CH]
        ao_ch = BOX_AO_CHANNEL_MAP[box_ao_ch]
        #out_ch = self.state_dictionary[function][POLARITY_RELAY_CH]
        self.set_hardware_voltage(0,ao_ch)
        self.fans_controller._set_output_channel(box_ao_ch,STATES.ON)

    def set_drain_voltage(self,voltage):
        #feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][FEEDBACK_CH]
        #output_ch = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][OUT_CH]
        self._start_setting_voltage(FANS_AI_FUNCTIONS.DrainSourceVoltage)
        self.set_fans_voltage_for_channel(voltage,FANS_AI_FUNCTIONS.DrainSourceVoltage) #feedback_ch,output_ch)
        #self.set_fans_voltage_for_channel(voltage,self.fans_drain_source_feedback)



    def set_gate_voltage(self, voltage):
        #feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][FEEDBACK_CH]
        #output_ch = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][OUT_CH]
        self._start_setting_voltage(FANS_AI_FUNCTIONS.GateVoltage)
        self.set_fans_voltage_for_channel(voltage,FANS_AI_FUNCTIONS.GateVoltage) #feedback_ch,output_ch)
        #self.set_fans_voltage_for_channel(voltage, self.fans_gate_feedback)
    
    
    
    #def read_drain_source_current(self):
    #    pass    

    def read_all_parameters(self):
        drain_feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][FEEDBACK_CH]
        gate_feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][FEEDBACK_CH]
        main_feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.MainVoltage][FEEDBACK_CH]

        drain_hardware_ch = BOX_AI_CHANNELS_MAP[drain_feedback_ch]["channel"]
        gate_hardware_ch = BOX_AI_CHANNELS_MAP[gate_feedback_ch]["channel"]
        main_hardware_ch = BOX_AI_CHANNELS_MAP[main_feedback_ch]["channel"]
        
        # can be a problem with an order of arguments
        result = self.analog_read([drain_hardware_ch,main_hardware_ch,gate_hardware_ch])
        ds_voltage = result[drain_hardware_ch]
        main_voltage = result[main_hardware_ch]
        gate_voltage = result[gate_hardware_ch]


        ### fix divide by zero exception
        try:
            current = (main_voltage-ds_voltage)/self.load_resistance
            resistance = ds_voltage/current
        except ZeroDivisionError:
            current = 0
            resistance = 0
        
        return {"Vds":ds_voltage,"Vgs":gate_voltage,"Vmain":main_voltage, "Ids":current,"Rs":resistance}
        


##    def set_fans_voltage(self, voltage,channel):
##        pass
##    


if __name__ == "__main__":
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

    smu.set_fans_ao_feedback_for_function(FANS_AI_FUNCTIONS.DrainSourceVoltage, AI_BOX_CHANNELS.ai_ch_1)    #ai_ch5
    smu.set_fans_ao_feedback_for_function(FANS_AI_FUNCTIONS.GateVoltage, AI_BOX_CHANNELS.ai_ch_2)   #ai_ch6
    smu.set_fans_ao_feedback_for_function(FANS_AI_FUNCTIONS.MainVoltage,AI_BOX_CHANNELS.ai_ch_3 )   #ai_ch7

    smu.init_smu_mode()
    smu._init_fans_ao_channels()
    
    try:
      #smu.set_drain_voltage(0)
      #smu.set_gate_voltage(0)
      #smu.set_drain_voltage(0.3)
      smu.set_drain_voltage(-0.1)
      
      for vds in np.arange(5,-5,-0.2):
          #print("setting drain-source")
          smu.set_drain_voltage(vds)
          print("setting gate")
          smu.set_gate_voltage(vds)
          res = smu.read_all_parameters()
          #print(smu.read_all_parameters())
          print("Vgs = {0}; Id = {1}".format(res["Vgs"],res["Ids"]))
          time.sleep(2)

      #smu.set_drain_voltage(-0.5)
      #smu.set_gate_voltage(-0.5)
       

    except Exception as e:
        raise
        print(str(e))
    finally:
        smu.set_hardware_voltage_channels(0, AO_CHANNELS.indexes)








