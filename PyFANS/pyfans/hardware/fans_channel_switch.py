import pyfans.hardware.modern_agilent_u2542a as daq
import pyfans.hardware.modern_fans_controller as mfc


class FANS_DUT_Switch:
    MAX_CHANNELS = 32
    def __init__(self, fans_controller):
        assert isinstance(fans_controller, mfc.FANS_CONTROLLER), "Wrong fans controller type"
        self._fans_controller = fans_controller
        self.control_channel = daq.DIG_CHANNEL_501
        self.pulse_bit = daq.DIG_CH503_BIT3
        self.set_reset_bit = daq.DIG_CH504_BIT1
    
    @property
    def fans_controller(self):
        return self._fans_controller

    @property
    def daq_device(self):
        return self.fans_controller.daq_parent_device


    def switch_to_dut(self, dut):
        if not isinstance(dut, int):
            raise TypeError("Channel should be an integer from 0 to 31 inclusively")

        if not (0 <= dut < self.MAX_CHANNELS):
            raise ValueError("channel should be in the range from 0 to 31 inclusively")

        self.daq_device.digital_write_bit(self.set_reset_bit, 1)
        self.daq_device.digital_write(self.control_channel, dut)
        self.daq_device.digital_pulse_bit(self.pulse_bit, pulse_width=0.005)

        