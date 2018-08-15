import time
from enum import Enum, IntEnum, unique
import pyfans.hardware.modern_agilent_u2542a as daq
import pyfans.hardware.modern_fans_controller as mfc

@unique
class SET_RESET_STATES(IntEnum):
    ON = 0
    OFF = 1

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

    def switch_all_off(self):
        for dut in range(self.MAX_CHANNELS):
            self.switch_dut_state(dut, SET_RESET_STATES.OFF)

    # def switch_all_off(self):
    #     for dut in range(self.MAX_CHANNELS):
    #         self.switch_dut_state(dut, SET_RESET_STATES.OFF)

    def switch_dut_state(self, dut, state):
        if not isinstance(dut, int):
            raise TypeError("Channel should be an integer from 0 to 31 inclusively")

        if not (0 <= dut < self.MAX_CHANNELS):
            raise ValueError("channel should be in the range from 0 to 31 inclusively")

        if not isinstance(state, SET_RESET_STATES):
            raise TypeError("Wrong state type")

        self.daq_device.digital_write_bit(self.set_reset_bit, state)
        self.daq_device.digital_write(self.control_channel, dut)
        self.daq_device.digital_pulse_bit(self.pulse_bit, pulse_width=0.005)

    def switch_to_dut(self, dut):
        self.switch_all_off()
        time.sleep(0.005)
        self.switch_dut_state(dut, SET_RESET_STATES.ON)
