from fans_controller import FANS_controller
from node_configuration import Configuration

class fans_smu:
    def __init__(self, fans_controller):
        self.fans_controller = fans_controller
        self.ao_ch1_hardware_voltage = 0
        self.ao_ch2_hardware_voltage = 0
        self.ao_ch1_enabled = True
        self.ao_ch2_enabled = True
        self.fans_ao1_channel = 0
        self.fans_ao2_channel = 0

    def _init_fans_ao_channels(self):
        self.fans_controller._set_output_channels(self.fans_ao1_channel,self.ao_ch1_enabled,self.fans_ao2_channel,ao_ch2_enabled)

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
        self.fans_controller.fans_output_voltage_channel

    def set_hardware_voltages(self,channel_voltage_pairs):
        pass


if __name__ == "__main__":
    cfg = Configuration()
    f = FANS_controller("ADC",configuration=cfg)
    
        
