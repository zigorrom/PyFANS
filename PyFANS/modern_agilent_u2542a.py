import os
import sys
import time

import numpy as np
from scipy import signal
from enum import Enum, unique

from communication_layer import VisaInstrument, instrument_await_function


def Convertion(a):
    pol_idx = a[2]
    range_val = ai_all_fRanges[a[1]]
    f = ai_convertion_functions[pol_idx]
    # starting from 4 since the header has 4 items
    timetrace = f(range_val,a[4:])
##    fft = np.fft.fft(timetrace)
##    res = np.concatenate(timetrace,fft).reshape((timetrace.size,2))
    return timetrace



SWITCH_STATE_ON, SWITCH_STATE_OFF = SWITCH_STATES = ["ON","OFF"]
SWITCH_STATES_CONVERTER = {"0": False,
                           "1": True,
                           SWITCH_STATE_ON: True,
                           SWITCH_STATE_OFF: False}

AI_CHANNEL_101, AI_CHANNEL_102, AI_CHANNEL_103, AI_CHANNEL_104 = AI_CHANNELS = [101, 102, 103, 104]
AO_CHANNEL_201, AO_CHANNEL_202 = AO_CHANNELS = [201,202]


DIGITAL_MODE_INPUT, DIGITAL_MODE_OUTPUT = DIGITAL_MODES = ["INP", "OUTP"]
DIG_CHANNEL_501, DIG_CHANNEL_502, DIG_CHANNEL_503, DIG_CHANNEL_504 = DIG_CHANNELS = [501, 502, 503, 504]

DIG_CH501_BIT0 = (DIG_CHANNEL_501, 0)
DIG_CH501_BIT1 = (DIG_CHANNEL_501, 1)
DIG_CH501_BIT2 = (DIG_CHANNEL_501, 2)
DIG_CH501_BIT3 = (DIG_CHANNEL_501, 3)
DIG_CH501_BIT4 = (DIG_CHANNEL_501, 4)
DIG_CH501_BIT5 = (DIG_CHANNEL_501, 5)
DIG_CH501_BIT6 = (DIG_CHANNEL_501, 6)
DIG_CH501_BIT7 = (DIG_CHANNEL_501, 7)
DIG_CH502_BIT0 = (DIG_CHANNEL_502, 0)
DIG_CH502_BIT1 = (DIG_CHANNEL_502, 1)
DIG_CH502_BIT2 = (DIG_CHANNEL_502, 2)
DIG_CH502_BIT3 = (DIG_CHANNEL_502, 3)
DIG_CH502_BIT4 = (DIG_CHANNEL_502, 4)
DIG_CH502_BIT5 = (DIG_CHANNEL_502, 5)
DIG_CH502_BIT6 = (DIG_CHANNEL_502, 6)
DIG_CH502_BIT7 = (DIG_CHANNEL_502, 7)
DIG_CH503_BIT0 = (DIG_CHANNEL_503, 0)
DIG_CH503_BIT1 = (DIG_CHANNEL_503, 1)
DIG_CH503_BIT2 = (DIG_CHANNEL_503, 2)
DIG_CH503_BIT3 = (DIG_CHANNEL_503, 3)
DIG_CH504_BIT0 = (DIG_CHANNEL_504, 0)
DIG_CH504_BIT1 = (DIG_CHANNEL_504, 1)
DIG_CH504_BIT2 = (DIG_CHANNEL_504, 2)
DIG_CH504_BIT3 = (DIG_CHANNEL_504, 3)

DIGITAL_BIT_ON, DIGITAL_BIT_OFF = DIGITAL_BIT_STATES = ['1','0']

UNIPOLAR, BIPOLAR = POLARITIES = ["UNIP", "BIP"]

RANGE_125, RANGE_25, RANGE_5, RANGE_10 = DAQ_RANGES = [1.25, 2.5, 5, 10]
AUTO_RANGE = "AUTO"
AI_RANGES = [AUTO_RANGE, RANGE_125, RANGE_25, RANGE_5, RANGE_10]

MAX_INT16 = 65536
MAX_INT16_HALF = 32768

SINGLE_SHOT_READY, SINGLE_SHOT_IN_PROCESS = ["YES", "NO"]
ACQUISITION_EMPTY, ACQUISITION_FRAGMENT, ACQUSITION_DATA, ACQUISITION_OVERLOAD = ["EPTY","FRAG","DATA","OVER"]


def BipolarConversionFunction(range_value, data_code):
    return (data_code*range_value)/MAX_INT16_HALF

def UnipolarConversionFunction(range_value, data_code):
    return (data_code/MAX_INT16+0.5)*range_value

AI_CONVERSION_FUNCTION = {POLARITIES.index(BIPOLAR): BipolarConversionFunction,
                          POLARITIES.index(UNIPOLAR): UnipolarConversionFunction}

ERROR_SPECIFIED_CHANNEL_NOT_EXISTING = "Specified channel is not existing"

def join_channels(channels, char = ','):
    assert isinstance(char,str)
    return char.join((str(channel) for channel in channels))

def check_channel_exists(channel):
    if channel in AI_CHANNELS:
        return True
    elif channel in AO_CHANNELS:
        return True
    elif channel in DIG_CHANNELS:
        return False

def check_analog_in_channel_exists(channel):
    if channel in AI_CHANNELS:
        return True
    else:
        return False

def check_analog_out_channel_exists(channel):
    if channel in AO_CHANNELS:
        return True
    else:
        return False

def check_analog_channel_exists(channel):
    return check_analog_in_channel_exists(channel) or check_analog_out_channel_exists(channel)

def check_dig_channel_exists(channel):
    if channel in DIG_CHANNELS:
        return True
    else:
        return False

def check_dig_bit_exists(channel, bit):
    if check_dig_channel_exists(channel):
        if bit < 0:
            return False
        elif channel == DIG_CHANNEL_501 or channel == DIG_CHANNEL_502:
            if bit<8:
                return True
        elif channel == DIG_CHANNEL_503 or channel == DIG_CHANNEL_504:
            if bit<4:
                return True
    else:
        return False

def assert_state(state):
    assert state in SWITCH_STATES, "Wrong state!"
    return True

def assert_dig_mode(mode):
    assert mode in DIGITAL_MODES, "Wrong mode!"
    return True

def assert_polarity(polarity):
    assert polarity in POLARITIES, "Wrong polarity!"
    return True

def assert_range(range_value):
    assert range_value in DAQ_RANGES, "Wrong range!"
    return True

def assert_analog_range(range_value):
    assert range_value in AI_RANGES, "Wrong range!"
    return True

def check_single_shot_data_is_ready(state):
    if state == SINGLE_SHOT_READY:
        return True

def check_continuous_acquisition_data_is_ready(state):
    if state == ACQUISITION_OVERLOAD:
        raise OverflowError("Buffer is overloaded")
    elif state == ACQUSITION_DATA:
        return True
    else:
        return False

def check_continuous_acquisition_buffer_is_empty(state):
    if state == ACQUISITION_EMPTY:
        return True
    else:
        return False


def data_conversion_function(data):
    polarity = data[1]
    range_val = DAQ_RANGES[data[2]]
    conversion_function = AI_CONVERSION_FUNCTION[polarity]
    return conversion_function(range_val, data[3:])   #converted_data = 


ACQUIRED_DATA_HEADER_LENGTH = 10
ACQUIRED_DATA_HEADER_START = 2

def acqusition_convert_raw_data(raw_data, conversion_header):
    data_length_from_buffer_header = int(raw_data[ACQUIRED_DATA_HEADER_START:ACQUIRED_DATA_HEADER_LENGTH])
    raw_data = raw_data[ACQUIRED_DATA_HEADER_LENGTH:]
    int_converted_data = np.fromstring(raw_data, dtype = '<i2')
    number_of_channels = len(conversion_header)
    single_channel_data_length = int(int_converted_data.size / number_of_channels)
    array_for_final_convertion = np.hstack((conversion_header, int_converted_data.reshape((single_channel_data_length, number_of_channels)).transpose()))
    return np.apply_along_axis(data_conversion_function, 1, array_for_final_convertion)





class AgilentU2542A_DSP(VisaInstrument):
    def __init__(self, resource):
        super().__init__(resource)
        self.conversion_header = None
        

    def initialize_instrument(self, resource):
        pass

    def set_sample_rate(self,sample_rate):
        if sample_rate < 3 or sample_rate > 500000:
            raise Exception("Sample rate is out of allowed range")
        self.write("ACQ:SRAT {0}".format(sample_rate))


    def set_single_shot_acquisition_points(self, points):
        self.write("ACQ:POIN {0}".format(points))

    def set_continuous_acquisition_points(self,points):
        self.write("WAV:POIN {0}".format(points))


    def ask_idn(self):
        return self.query("*IDN?")
     
            
    def clear_status(self):
        self.write("*CLS")

    def reset_device(self):
        self.write("*RST")


    def switch_enabled(self, channel, state):
        assert check_analog_channel_exists(channel), "Channel is not existing in analog channels"
        assert_state(state)
        self.write("ROUT:ENAB {0},(@{1})".format(state,channel))
        

    def switch_enabled_for_channels(self, channels, state):
        assert all((check_analog_channel_exists(channel) for channel in channels)), "At least one of channels is not existing"
        assert_state(state)
        self.write("ROUT:ENAB {0},(@{1})".format(state, join_channels(channels)))

    def get_channel_enabled(self, channel):
        assert check_analog_channel_exists(channel), "Specified channel is not existing"
        result = self.query("ROUT:ENAB? (@{0})".format(channel))
        return SWITCH_STATES_CONVERTER[result]


    def check_channels_enabled(self, channels):
        if isinstance(channels, int):
            channels = [channels]

        assert all((check_analog_channel_exists(channel) for channel in channels)), "At least one of channels is not existing"
        result = self.query("ROUT:ENAB? (@{0})".format(join_channels(channels)))
        spl = result.split(',')
        assert len(spl) == len(channels), "Inconsistent result"
        return {channel: SWITCH_STATES_CONVERTER[state] for (channel, state) in zip(channels, spl) }

    def set_polarity(self, channel, polarity):
        assert check_analog_channel_exists(channel)
        assert_polarity(polarity)
        self.write("ROUT:CHAN:POL {0}, (@{1})".format(polarity, channel))

    def set_polarity_for_channels(self, channels, polarity):
        assert all((check_analog_channel_exists(channel) for channel in channels )), "At least one of channels is not existing"
        assert_polarity(polarity)
        self.write("ROUT:CHAN:POL {0}, (@{1})".format(polarity, join_channels(channels)))

    def get_polarity(self, channel):
        assert check_analog_in_channel_exists(channel), "Specified channel is not existing"
        result = self.query("ROUT:CHAN:POL? (@{0})".format(channel))
        assert result in POLARITIES, "unexpected response"
        return result

    def get_polarity_for_channels(self, channels):
        assert all((check_analog_channel_exists(channel) for channel in channels )), "At least one of channels is not existing"
        result = self.query("ROUT:CHAN:POL? (@{0})".format(join_channels(channels)))
        spl = result.split(',')
        assert len(spl) == len(channels), "Inconsistent result"
        return {channel: polarity for (channel, polarity) in zip(channels, spl) }

    def set_range(self, channel, range_value):
        assert check_analog_in_channel_exists(channel), "Specified analog in channel is not existing"
        assert_range(range_value)
        self.write("ROUT:CHAN:RANG {0}, (@{1})".format(range_value,channel))

    def set_range_for_channels(self, channels, range_value):
        assert all((check_analog_in_channel_exists(channel) for channel in channels)), "At least one of channels is not existing"
        assert_range(range_value)
        self.write("ROUT:CHAN:RANG {0}, (@{1})".format(range_value, join_channels(channels)))

    def get_range(self, channel):
        assert check_analog_in_channel_exists(channel), "Specified channel is not existing"
        result = self.query("ROUT:CHAN:RANG? (@{0})".format(channel))
        range_val = float(result)
        assert range_val in DAQ_RANGES, "unexpected responce"
        return range_val


    def get_range_for_channels(self, channels):
        assert all((check_analog_in_channel_exists(channel) for channel in channels)), "At least one of channels is not existing"
        result = self.query("ROUT:CHAN:RANG? (@{0})".format(join_channels(channels)))
        spl = result.split(',')
        assert len(spl) == len(channels), "Inconsistent result"
        return {channel: float(range_value) for (channel, range_value) in zip(channels, spl) }

    def set_digital_mode(self, channel, mode):
        assert check_dig_channel_exists(channel), "Digital channel is not existing"
        assert_dig_mode(mode)
        self.write("CONF:DIG:DIR {0},(@{1})".format(mode,channel))

    def set_digital_mode_for_channels(self, channels, mode):
        assert all((check_dig_channel_exists(channel) for channel in channels)),  "At least one of channels is not existing"
        assert_dig_mode(mode)
        self.write("CONF:DIG:DIR {0},(@{1})".format(mode,join_channels(channels)))

    def digital_write(self, channel, value):
        assert check_dig_channel_exists(channel), "Specified channel is not existing"
        self.write("SOUR:DIG:DATA {0},(@{1})".format(value,channel))

    def digital_write_channels(self, channels, value):
        assert all((check_dig_channel_exists(channel) for channel in channels)), "At least one of channels is not existing"
        self.write("SOUR:DIG:DATA {0},(@{1})".format(value,join_channels(channels)))

    def digital_write_bit(self,dig_bit, value):
        assert isinstance(dig_bit, tuple)
        channel, bit = dig_bit
        assert check_dig_bit_exists(channel, bit), "Specified digital bit is not exisiting"
        self.write("SOUR:DIG:DATA:BIT {0}, {1}, (@{2})".format(value,bit,channel))

    def digital_pulse_bit(self, dig_bit, pulse_width = 0.005):
        assert isinstance(dig_bit, tuple)
        channel, bit = dig_bit
        assert check_dig_bit_exists(channel, bit), "Specified digital bit is not exisiting"
        str_format = "SOUR:DIG:DATA:BIT {0}, {1}, (@{2})"
        #self.write(str_format.format(DIGITAL_BIT_OFF,bit,channel))
        #time.sleep(pulse_width)
        self.write(str_format.format(DIGITAL_BIT_ON,bit,channel))
        time.sleep(pulse_width)
        self.write(str_format.format(DIGITAL_BIT_OFF,bit,channel))

    def digital_read_bit(self, dig_bit):
        assert isinstance(dig_bit, tuple)
        channel, bit = dig_bit
        assert check_dig_bit_exists(channel, bit), "Specified digital bit is not exisiting"
        value = self.query("SOUR:DIG:DATA:BIT? {1}, (@{2})".format(value,bit,channel))
        return int(value)

    def digital_read(self,channel):
        assert check_dig_channel_exists(channel), "Specified channel is not existing"
        value = self.query("SOUR:DIG:DATA? (@{0})".format(channel))
        return int(value)

    def digital_measure(self, channel):
        raise NotImplementedError()


    def digital_measure_channels(self, channels):
        raise NotImplementedError()

    def analog_get_range(self, channel):
        assert check_analog_in_channel_exists(channel), "Specified channel is not existing"
        result = self.query("VOLT:RANG? (@{0})".format(channel))
        if result == AUTO_RANGE:
            return result
        
        range_val = float(result)
        assert range_val in AI_RANGES, "unexpected response"
        return range_val

    def analog_set_range(self, channel, range_value):
        assert check_analog_in_channel_exists(channel), "Specified channel is not existing"
        assert_analog_range(range_value)
        self.write("VOLT:RANG {0}, (@{1})".format(range_value, channel))

    def analog_set_range_for_channels(self, channels, range_value):
        assert all((check_analog_in_channel_exists(channel) for channel in channels )), "At least one of channels is not existing"
        assert_analog_range(range_value)
        self.write("VOLT:RANG {0}, (@{1})".format(range_value, join_channels(channels)))

    

    def analog_set_polarity(self, channel, polarity):
        assert check_analog_in_channel_exists(channel)
        assert_polarity(polarity)
        self.write("VOLT:POL {0}, (@{1})".format(polarity, channel))

    def analog_set_polarity_for_channels(self, channels, polarity):
        assert all((check_analog_in_channel_exists(channel) for channel in channels )), "At least one of channels is not existing"
        assert_polarity(polarity)
        self.write("VOLT:POL {0}, (@{1})".format(polarity, join_channels(channels)))

    def analog_set_averaging(self, averaging):
        assert isinstance(averaging, int), "averaging should be integer"
        assert averaging > 0 and averaging < 1001, "Averaging is out of range"
        self.write("VOLT:AVER {0}".format(averaging))

    def analog_averaging_query(self):
        value = self.query("VOLT:AVER?")
        return int(value)

    def analog_measure(self, channel):
        assert check_analog_in_channel_exists(channel)
        value = self.query("MEAS? (@{0})".format(channel))
        return float(value)

    def analog_measure_channels(self, channels):
        assert all((check_analog_in_channel_exists(channel) for channel in channels)), "At least one of channels is not existing"
        str_result = self.query("MEAS? (@{0})".format(join_channels(channels)))
        spl = str_result.split(',')
        assert len(spl) == len(channels), "Inconsistent result"
        return {channel: float(value) for (channel, value) in zip(channels, spl)}

    def analog_set_source_polarity(self, channel, polarity):
        assert check_analog_out_channel_exists(channel)
        assert_polarity(polarity)
        self.write("SOUR:VOLT:POL {0}, (@{1})".format(polarity, channel))

    def analog_set_source_polarity_for_channels(self,channels, polarity):
        assert(all(check_analog_out_channel_exists(channel) for channel in channels))
        assert_polarity(polarity)
        self.write("SOUR:VOLT:POL {0}, (@{1})".format(polarity, join_channels(channels)))

    def analog_source_voltage(self, channel, voltage):
        assert check_analog_out_channel_exists(channel)
        assert voltage >= -10 and voltage <= 10
        self.write("SOUR:VOLT {0}, (@{1})".format(voltage, channel))

    def analog_source_voltage_for_channels(self, channels, voltage):
        assert all((check_analog_out_channel_exists(channel) for channel in channels))
        assert voltage >= -10 and voltage <= 10
        self.write("SOUR:VOLT {0}, (@{1})".format(voltage, join_channels(channels)))

    def analog_set_output_state(self,state):
        assert state in SWITCH_STATES
        self.write("OUTP {0}".format(state))

   
    def create_conversion_header(self):
        #AI_CHANNELS 
        channels_enable_list = self.check_channels_enabled(AI_CHANNELS)
        enabled_channels = [channel for (channel, enabled) in channels_enable_list.items() if enabled]
        polarities_for_channels = self.get_polarity_for_channels(enabled_channels)
        ranges_for_channels = self.get_range_for_channels(enabled_channels)
        
        list_of_params = []

        for channel in enabled_channels:
            polarity = polarities_for_channels[channel]
            range_value = ranges_for_channels[channel]
            list_of_params.append([AI_CHANNELS.index(channel), POLARITIES.index(polarity), DAQ_RANGES.index(range_value)])

        return np.asarray(list_of_params)

    def initialize_conversion_header(self):
        self.conversion_header = self.create_conversion_header()

    def initialize_acqusition(self, sample_rate, points_per_shot, single_shot):
        self.set_sample_rate(sample_rate)
        if single_shot:
            self.set_single_shot_acquisition_points(points_per_shot)
        else: 
            self.set_continuous_acquisition_points(points_per_shot)

        self.initialize_conversion_header()
        #self.conversion_header = self.create_conversion_header()

    def start_acquisition(self):
        self.write("RUN")

    def start_single_shot_acquisition(self):
        self.write("DIG")

    def stop_acquisition(self):
        self.write("STOP")

    def single_shot_acquisition_completed(self):
        return self.query("WAV:COMP?")

    def continuous_acquisition_state(self):
        return self.query("WAV:STAT?")

    def acquisition_read_raw_data(self):
        self.write("WAV:DATA?")
        return self.read_raw()

    def acqusition_read_data(self):
        raw_data = self.acquisition_read_raw_data()
        return acqusition_convert_raw_data(raw_data, self.conversion_header)

    def read_acquisition_data_when_ready(self):
        while not check_continuous_acquisition_data_is_ready(self.continuous_acquisition_state()): pass
        return self.acqusition_read_data()

    def read_single_shot_data_when_ready(self):
        while not check_single_shot_data_is_ready(self.single_shot_acquisition_completed()): pass
        return self.acqusition_read_data()

    def empty_continuous_acquisition_buffer(self):
        # TODO send command to clear buffer
        while not check_continuous_acquisition_buffer_is_empty(self.continuous_acquisition_state()):
            rest_data = self.acquisition_read_raw_data()



def main():
        #d = AgilentU2542A('ADC')
    d = AgilentU2542A_DSP('ADC')
    print(d.ask_idn())
    
    d.switch_enabled_for_channels(AI_CHANNELS, SWITCH_STATE_OFF)
    d.switch_enabled_for_channels([AI_CHANNEL_101], SWITCH_STATE_ON)

    d.set_range(AI_CHANNEL_101, RANGE_125)
    d.set_polarity(AI_CHANNEL_101, BIPOLAR)

    try:
        ### single shot
    
        d.initialize_acqusition(5000, 50000,True)
        counter = 0
        print("start single shot")
        d.start_single_shot_acquisition()
        while not check_single_shot_data_is_ready(d.single_shot_acquisition_completed()):
            print(counter)
            counter += 1
            time.sleep(0.1)
        
        data =  d.acqusition_read_data()
        print(data)
        print("single shot finished")

        ### continuous 4 channels

        d.switch_enabled_for_channels(AI_CHANNELS, SWITCH_STATE_ON)
        #d.switch_enabled_for_channels([AI_CHANNEL_101], SWITCH_STATE_ON)
        d.set_range_for_channels(AI_CHANNELS, RANGE_125)
        d.set_polarity_for_channels(AI_CHANNELS, BIPOLAR)
        d.initialize_acqusition(500000, 50000,False)
        counter = 0
        max_count = 10 * 30
        d.start_acquisition()
        while counter < max_count:
            if check_continuous_acquisition_data_is_ready(d.continuous_acquisition_state()):
                start_time = time.time()
                data =  d.acqusition_read_data()
                print(counter)
                counter += 1
                print("converstion in", time.time() - start_time)
            time.sleep(0.02)
        d.stop_acquisition()
        d.clear_status()
    except Exception as e:
        print(e)
        d.stop_acquisition()
        d.clear_status()

    finally:
        print("finished")


if __name__ == "__main__":
    main()
    #os.system("pause")

   
