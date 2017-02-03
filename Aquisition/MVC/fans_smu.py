import time
from fans_controller import FANS_controller
from fans_constants import *
from agilent_u2542a_constants import *
from node_configuration import Configuration
import numpy as np

class fans_smu:
    def __init__(self, fans_controller):
        self.fans_controller = fans_controller
        self.ao_ch1_hardware_voltage = 0
        self.ao_ch2_hardware_voltage = 0
        self.ao_ch1_enabled = True
        self.ao_ch2_enabled = True
        self.fans_ao1_channel = 0
        self.fans_ao2_channel = 0
        self._init_fans_ao_channels()

    def _init_fans_ao_channels(self):
        self.fans_controller._set_output_channels(self.fans_ao1_channel,self.ao_ch1_enabled,self.fans_ao2_channel,self.ao_ch2_enabled)

    def init_smu_mode(self,channel):
        self.fans_controller.set_fans_ai_channel_mode(AI_MODES.DC,channel)
        self.fans_controller.analog_read_averaging(1000);

    def set_fans_ao_channels(self,ao1,ao1_en,ao2,ao2_en):
        self.ao_ch1_enabled = ao1_en
        self.ao_ch2_enabled = ao2_en
        self.fans_ao1_channel = ao1
        self.fans_ao2_channel = ao2
        self._init_fans_ao_channels()

    def set_feedback_ai_channels(self,feedback_ch1,feedback_ch2):
        self.feedback_ch1 = feedback_ch1
        self.feedback_ch2 = feedback_ch2

    def set_hardware_voltage(self,voltage, channel):
        self.fans_controller.fans_output_channel_voltage(voltage, channel)

    def set_hardware_voltage_channels(self, voltage, channels):
        self.fans_controller.fans_output_voltage_to_channels(voltage,channels)

    def set_hardware_voltages(self,channel_voltage_pairs):
        for channel,voltage in channel_voltage_pairs:
            self.fans_controller.fans_output_channel_voltage(voltage, channel)

    def analog_read(self,channels):
        return self.fans_controller.analog_read(channels)
    



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
        