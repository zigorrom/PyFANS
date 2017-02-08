import time
import math
from fans_controller import FANS_controller
from fans_constants import *
from agilent_u2542a_constants import *
from node_configuration import Configuration
import numpy as np

MIN_MOVING_VOLTAGE = 3
MAX_MOVING_VOLTAGE = 6
VALUE_DIFFERENCE = MAX_MOVING_VOLTAGE-MIN_MOVING_VOLTAGE
FD_CONST = 0.001

FANS_VOLTAGE_SET_ERROR  = 0.001 #mV
FANS_VOLTAGE_SET_MAXITER = 1000

FANS_POLARITY_CHANGE_VOLTAGE = (-3,3)
FANS_NEGATIVE_POLARITY,FANS_POSITIVE_POLARITY = FANS_POLARITY_CHANGE_VOLTAGE
 


def voltage_setting_function(current_value, set_value):
    # fermi-dirac-distribution
    return MIN_MOVING_VOLTAGE + VALUE_DIFFERENCE/(math.exp((current_value-set_value)/FD_CONST)+1)


# output channel - A0_BOX_CHANNELS
# feedback_channel - AI_BOX_CHANNELS
def generate_state_dictionary(enabled, output_channel, feedback_channel, polarity_relay_channel):
    return {OUT_ENABLED_CH:enabled, OUT_CH:output_channel, FEEDBACK_CH:feedback_channel, POLARITY_RELAY_CH: polarity_relay_channel}

OUT_ENABLED_CH, OUT_CH, FEEDBACK_CH, POLARITY_RELAY_CH = [0,1,2,3]

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
        self._init_fans_ao_channels()
        


    def _init_fans_ao_channels(self):
        #self.fans_controller._set_output_channels(self.fans_drain_source_set_channel,self.ao_ch1_enabled,self.fans_drain_source_set_channel,self.ao_ch2_enabled)
        ao1_channel = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][OUT_CH]
        ao1_enabled = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][OUT_ENABLED_CH]
        ao2_channel = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][OUT_CH]
        ao2_enabled = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][OUT_ENABLED_CH]
        self.fans_controller._set_output_channels(ao1_channel,ao1_enabled,ao2_channel,ao2_enabled)

    def init_smu_mode(self):
        for ch in [FANS_AI_FUNCTIONS.DrainSourceVoltage, FANS_AI_FUNCTIONS.GateVoltage]:
            self.fans_controller.set_fans_ai_channel_mode(AI_MODES.DC,self.state_dictionary[ch][FEEDBACK_CH])
        #self.fans_controller.set_fans_ai_channel_mode(AI_MODES.DC,channel)
        #self.fans_controller.analog_read_averaging(1000)

   
    def set_fans_ao_channel_for_function(self,function, ao_channel,enabled):
        self.state_dictionary[funciton][OUT_CH] = ao_channel
        self.state_dictionary[funciton][OUT_ENABLED_CH] = enabled
      
    def set_fans_ao_polarity_for_function(self,function, polarity):
        self.state_dictionary[funciton][POLARITY_RELAY_CH] = polarity

    def set_fans_ao_feedback_for_function(self,function,feedback):
        self.state_dictionary[funciton][FEEDBACK_CH] = feedback

    #def set_fans_ao_channels(self,ao1,ao1_en,ao2,ao2_en):
    #    self.ao_ch1_enabled = ao1_en
    #    self.ao_ch2_enabled = ao2_en
    #    self.fans_drain_source_set_channel = ao1
    #    self.fans_drain_source_set_channel = ao2
    #    self._init_fans_ao_channels()

    #def set_feedback_ai_channels(self,drain_source_feedback,gate_feedback,main_feedback):
    #    self.fans_drain_source_feedback = drain_source_feedback
    #    self.fans_gate_feedback = gate_feedback
    #    self.fans_main_feedback = main_feedback

    #def set_fans_polarity_relay_outputs(self, drain_source_polarity_relay, gate_polarity_relay):
    #    self.drain_source_polarity_relay = drain_source_polarity_relay
    #    self.gate_polarity_relay = gate_polarity_relay

    def set_hardware_voltage(self,voltage, channel):
        self.fans_controller.fans_output_channel_voltage(voltage, channel)

    def set_hardware_voltage_channels(self, voltage, channels):
        self.fans_controller.fans_output_voltage_to_channels(voltage,channels)

    def set_hardware_voltages(self,channel_voltage_pairs):
        for channel,voltage in channel_voltage_pairs:
            self.fans_controller.fans_output_channel_voltage(voltage, channel)

    def analog_read(self,channels):
        return self.fans_controller.analog_read(channels)

    def set_fans_output_polarity(self,polarity,function):
        pass


    def set_fans_voltage_for_channel(self,voltage,function):

        ai_feedback = self.state_dictionary[function][FEEDBACK_CH]
        output_ch = self.state_dictionary[function][OUT_CH]

        current_value = self.analog_read(ai_feedback)
        if current_value*voltage<0:
            set_result = self.set_fans_voltage_for_channel(0,ai_feedback,ao_channel)
            if set_result:
                polarity = FANS_NEGATIVE_POLARITY if voltage<0 else FANS_POSITIVE_POLARITY
                
                self.set_fans_output_polarity(polarity)
            else:
                return set_result

        #continue_setting = True
        counter = 0
        while True: #continue_setting:    
            curren_value = self.analog_read(ai_feedback)
            value_to_set = voltage_setting_function(current_value,voltage)
            if abs(current_value-voltage)<FANS_VOLTAGE_SET_ERROR:
                return True
            elif counter > FANS_VOLTAGE_SET_MAXITER:
                return False

            self.set_hardware_voltage(value_to_set,ao_channel)



            #self.set_hardware_voltage(value_to_set,ao_channel)
            

    

    def set_drain_voltage(self,voltage):
        #feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][FEEDBACK_CH]
        #output_ch = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][OUT_CH]
        self.set_fans_voltage_for_channel(voltage,FANS_AI_FUNCTIONS.DrainSourceVoltage) #feedback_ch,output_ch)
        #self.set_fans_voltage_for_channel(voltage,self.fans_drain_source_feedback)



    def set_gate_voltage(self, voltage):
        #feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][FEEDBACK_CH]
        #output_ch = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][OUT_CH]
        self.set_fans_voltage_for_channel(voltage,FANS_AI_FUNCTIONS.GateVoltage) #feedback_ch,output_ch)
        #self.set_fans_voltage_for_channel(voltage, self.fans_gate_feedback)
    
    
    
    #def read_drain_source_current(self):
    #    pass    

    def read_all_parameters(self):
        drain_feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.DrainSourceVoltage][FEEDBACK_CH]
        gate_feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.GateVoltage][FEEDBACK_CH]
        main_feedback_ch = self.state_dictionary[FANS_AI_FUNCTIONS.MainVoltage][FEEDBACK_CH]

        # can be a problem with an order of arguments
        ds_voltage, main_voltage, gate_voltage = self.analog_read([drain_feedback_ch,main_feedback_ch,gate_feedback_ch])
        current = (main_voltage-ds_voltage)/self.load_resistance
        resistance = ds_voltage/current
        return {"Vds":ds_voltage,"Vgs":gate_voltage,"Vmain":main_voltage, "Ids":current,"Rs":resistance}
        


##    def set_fans_voltage(self, voltage,channel):
##        pass
##    


if __name__ == "__main__":
    cfg = Configuration()
    f = FANS_controller("ADC",configuration=cfg)
    smu = fans_smu(f)
    
    smu.set_fans_ao_channels(1,True,0,True)
    smu.set_hardware_voltage_channels(1.5, AO_CHANNELS.indexes)

    #mode = AI_MODES.AC
    #for i in range(10):
    #    print("mode={0}, i={1}".format(AI_MODES[mode],i))
    #    f.set_fans_ai_channel_mode(mode,AI_CHANNELS.AI_101)
    #    mode = AI_MODES.DC if mode==AI_MODES.AC else AI_MODES.AC
    #    print(smu.analog_read(AI_CHANNELS.indexes))
    #    time.sleep(1)
        


    #smu.init_smu_mode(AI_CHANNELS.AI_101)
    #sign = 1
    #for i in range(10):
    #    smu.set_hardware_voltage_channels(sign*6, AO_CHANNELS.indexes)
    #    print(smu.analog_read(AI_CHANNELS.AI_101))
    #    time.sleep(4)

    #    smu.set_hardware_voltage_channels(0, AO_CHANNELS.indexes)
    #    print(smu.analog_read(AI_CHANNELS.AI_101))
    #    time.sleep(0.5)
    #    sign = -sign
    
    #smu.init_smu_mode(AI_CHANNELS.AI_101)
    f.set_fans_ai_channel_mode(AI_MODES.DC,AI_CHANNELS.AI_101)
    sign = 1
    for i in np.arange(0,6,0.2):
        smu.set_hardware_voltage_channels(i, AO_CHANNELS.indexes)
        time.sleep(1)
        print(smu.analog_read(AI_CHANNELS.AI_101))
    smu.set_hardware_voltage_channels(0, AO_CHANNELS.indexes)
        
