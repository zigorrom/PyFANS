##from n_enum import enum
import time
from fans_constants import *
from agilent_u2542a import *
from agilent_u2542a_constants import *
from node_configuration import Configuration
from multiprocessing import Process, Event, JoinableQueue
from acquisition_process import Acquisition,AcquisitionProcess
from PyQt4 import QtCore, QtGui
from settings import WndTutorial



#enabled
#range
#polarity
#function
#mode: ac/dc
#cs_hold
#filter_cutoff
#filter_gain
#pga_gain

##
##  NEW VERSION
##
class FANS_AO_channel:
    def __init__(self,name,parent_device):
        self._parent_device = parent_device
        self._name = name
        self._range = DAQ_RANGES.RANGE_10
        self._polarity = POLARITIES.BIP
        self._function = None
        self._enabled = STATES.ON
        if self.ao_name == AO_CHANNELS.AO_201:
            self._output_pin = AO_BOX_CHANNELS.ao_ch_9
        else:
            self._output_pin = AO_BOX_CHANNELS.ao_ch_1
        self._voltage = 0


    def set_hardware_params(self):
        self.ao_enabled = self.ao_enabled
        self.ao_range = self.ao_range
        self.ao_polarity = self.ao_polarity

    @property
    def ao_name(self):
        return self._name

    #@name.setter
    #def name(self,value):
    #    self.name = value

    @property
    def ao_enabled(self):
        return self._enabled

    @ao_enabled.setter
    def ao_enabled(self,value):
        self._enabled = value
        self._parent_device.daq_set_enable_ao_channel(self.ao_enabled, self.ao_name)

    @property
    def ao_range(self):
        return self._range

    @ao_range.setter
    def ao_range(self,value):
        self._range = value
        self._parent_device.daq_set_channel_range(self.ao_range,self.ao_name)

    @property
    def ao_polarity(self):
        return self._polarity

    @ao_polarity.setter
    def ao_polarity(self,value):
        self._polarity = value
        self._parent_device.daq_set_ao_channel_polarity(self.ao_polarity,self.ao_name)

    @property
    def ao_voltage(self):
        return self._voltage 

    @ao_voltage.setter
    def ao_voltage(self,value):
        self._voltage = value
        self._parent_device.dac_source_channel_voltage(value,self.ao_name)

    @property
    def ao_function(self):
        return self._function

    @ao_function.setter
    def ao_function(self, value):
        self._function = value

    @property
    def ao_output_pin(self):
        return self._output_pin

    @ao_output_pin.setter
    def ao_output_pin(self,value):
        self._output_pin = value

class FANS_AO_Channel_Switch:
    def __init__(self, parent_device, *channels):
        self._parent_device = parent_device
        self._ao_channels = {channel.ao_name: channel for channel in channels}
        #self._ao_channels = {AO_CHANNELS.AO_201: ao1_channel, AO_CHANNELS.AO_202: ao2_channel}
        

    def select_channel(self, fans_ao_channel):
        dev_channel = BOX_AO_CHANNEL_MAP[fans_ao_channel]
        ao_channel = self._ao_channels[dev_channel]
        ao_channel.ao_output_pin = fans_ao_channel
        
        ao1_channel = self._ao_channels[AO_CHANNELS.AO_201]
        ao2_channel = self._ao_channels[AO_CHANNELS.AO_202]

        if ao1_channel.ao_output_pin is None:
            ao1_channel.ao_output_pin = AO_BOX_CHANNELS.ao_ch_9

        if ao2_channel.ao_output_pin is None:
            ao2_channel.ao_output_pin = AO_BOX_CHANNELS.ao_ch_1

        self._set_output_channels(ao1_channel.ao_output_pin, True, ao2_channel.ao_output_pin,True)

        return ao_channel



    def _set_output_channels(self,ao1_channel,ao1_enabled,ao2_channel,ao2_enabled):
        if ao1_channel<AO_BOX_CHANNELS.ao_ch_9 or ao1_channel > AO_BOX_CHANNELS.ao_ch_16:
            raise ValueError("Output channel for AO_201 is wrong")
        if ao2_channel<AO_BOX_CHANNELS.ao_ch_1 or ao2_channel > AO_BOX_CHANNELS.ao_ch_8:
            raise ValueError("Output channel for AO_202 is wrong")

        ###
        ###     bag with setting the enable bits
        ###
        ao1_channel = ao1_channel-AO_BOX_CHANNELS.ao_ch_9
        ao1_enable_bit_mask = 1<<7
        ao1_disable_bit_mask = ~ao1_enable_bit_mask
        ao2_enable_bit_mask = 1<<3
        ao2_disable_bit_mask = ~ao2_enable_bit_mask
        channels_enab = ao1_enable_bit_mask | ao2_enable_bit_mask
        if not ao1_enabled:
            channels_enab = channels_enab&ao1_disable_bit_mask
        if not ao2_enabled:
            channels_enab = channels_enab&ao2_disable_bit_mask

        channels = (ao1_channel<<4)|ao2_channel
##        print("channels {0:08b}".format(channels))
        val_to_write = channels_enab|channels
        print("value to write {0:08b}".format(val_to_write))
        self._parent_device.dig_write_channel(val_to_write,DIGITAL_CHANNELS.DIG_501)
        self._parent_device.pulse_digital_bit(AO_DAC_LETCH_PULS_BIT,DIGITAL_CHANNELS.DIG_504)

class FANS_AI_channel:
    def __init__(self, name, parent_device, range = DAQ_RANGES.RANGE_10, polarity = POLARITIES.BIP, mode = AI_MODES.DC, cs_hold = CS_HOLD.OFF, filter_cutoff = FILTER_CUTOFF_FREQUENCIES.f150, filter_gain = FILTER_GAINS.x1, pga_gain = PGA_GAINS.x1):
        self._parent_device = parent_device
        self.ai_name = name
        self.ai_enabled = STATES.ON
        self.ai_range = range
        self.ai_polarity = polarity
        self.ai_function = None
        self.ai_mode = mode
        self.ai_cs_hold = cs_hold
        self.ai_filter_cutoff = filter_cutoff
        self.ai_filter_gain = filter_gain
        self.ai_pga_gain = pga_gain
        self.set_fans_ai_channel_params()

    def __add__(self,other):
        new_name = None # sum of all names
        return FANS_AI_multichannel(new_name, self._parent_device) 

    #def start_editing_parameters():
    #    pass

    #def stop_editing_parameter():
    #    pass 

    def set_fans_ai_channel_params(self):
##        print(ai_channel)
        ## set channel selected
        ##print("seelct channel {0:08b}".format(AI_ChannelSelector[ch]))
        self._parent_device.dig_write_channel(self.ai_name, DIGITAL_CHANNELS.DIG_502)
        ## set DC or AC position of relays
        ##print("mode value {0:08b}".format(AI_MODE_VAL[mode]))
        self._parent_device.dig_write_bit_channel(self.ai_mode,AI_SET_MODE_BIT,DIGITAL_CHANNELS.DIG_504)#AI_MODE_VAL[mode]
        self._parent_device.pulse_digital_bit(AI_SET_MODE_PULS_BIT,DIGITAL_CHANNELS.DIG_504)
        
            
        ## set filter frequency and gain parameters
        filter_val = get_filter_value(self.ai_filter_gain,self.ai_filter_cutoff)
        self._parent_device.dig_write_channel(filter_val,DIGITAL_CHANNELS.DIG_501)

        ## set pga params
        pga_val = get_pga_value(self.ai_pga_gain,self.ai_cs_hold)
        self._parent_device.dig_write_channel(pga_val, DIGITAL_CHANNELS.DIG_503)
        self._parent_device.pulse_digital_bit(AI_ADC_LETCH_PULS_BIT,DIGITAL_CHANNELS.DIG_504)
    

    def set_hardware_params(self):
        self.ai_enabled = self.ai_enabled
        self.ai_range = self.ai_range
        self.ai_polarity = self.ai_polarity

    @property        
    def ai_amplification(self):
        if self.ai_mode == AI_MODES.AC:
            return self.ai_filter_gain*self.ai_pga_gain
        return 1

    @property
    def ai_name(self):
        return self._name
    
    @ai_name.setter
    def ai_name(self,value):
        self._name = value

    @property
    def ai_enabled(self):
        return self._enabled
    
    @ai_enabled.setter
    def ai_enabled(self,value):
        self._enabled = value
        self._parent_device.daq_set_enable_ai_channel(self.ai_enabled,self.ai_name)

    
    @property
    def ai_range(self):
        return self._range
    
    @ai_range.setter
    def ai_range(self,value):
        self._range = value
        self._parent_device.daq_set_channel_range(self.ai_range,self.ai_name)

    @property
    def ai_polarity(self):
        return self._polarity
    
    @ai_polarity.setter
    def ai_polarity(self,value):
        self._polarity = value
        self._parent_device.daq_set_ai_channel_polarity(self.ai_polarity,self.ai_name)
    
    @property
    def ai_function(self):
        return self._function
    
    @ai_function.setter
    def ai_function(self,value):
        self._function = value
    
    @property
    def ai_mode(self):
        return self._mode
    
    @ai_mode.setter
    def ai_mode(self,value):
        self._mode = value
        #self._set_fans_ai_channel_params()
    
    @property
    def ai_cs_hold(self):
        return self._cs_hold
    
    @ai_cs_hold.setter
    def ai_cs_hold(self,value):
        self._cs_hold = value
        #self._set_fans_ai_channel_params()

    @property
    def ai_filter_cutoff(self):
        return self._filter_cutoff

    @ai_filter_cutoff.setter
    def ai_filter_cutoff(self,value):
        self._filter_cutoff = value
        #self._set_fans_ai_channel_params()

    @property
    def ai_filter_gain(self):
        return self._filter_gain

    @ai_filter_gain.setter
    def ai_filter_gain(self,value):
        self._filter_gain = value
        #self._set_fans_ai_channel_params()
    
    @property
    def ai_pga_gain(self):
        return self._pga_gain

    @ai_pga_gain.setter
    def ai_pga_gain(self,value):
        self._pga_gain = value

class FANS_AI_multichannel(FANS_AI_channel):
    def __init__(self, names, parent_device):
        super(FANS_AI_channel,self).__init__(names, parent_device)

class FANS_AQUISITION_CONTROLLER:
    def __init__(self, fans_controller):
        self._fans_controller = fans_controller
        self._sample_rate = None
        self._recording_time = None
        self._noise_averaging = None
        self._use_homemade_amplifier = False
        self._homemade_amplifier_amplification = 178

        self._use_additional_amplifier = False
        self._additional_amplifier_amplification = 1


    @property
    def daq_sample_rate(self):
        return self._sample_rate

    @daq_sample_rate.setter
    def daq_sample_rate(self,value):
        self._sample_rate = value

    @property
    def daq_recording_time(self):
        return self._recording_time

    @daq_recording_time.setter
    def daq_recording_time(self,value):
        self._recording_time = value
        
    @property
    def daq_noise_averaging(self):
        return self._noise_averaging

    @daq_noise_averaging.setter
    def daq_noise_averaging(self,value):
        self._noise_averaging = value

    @property
    def daq_use_homemade_amplifier(self):
        self._use_homemade_amplifier
    
    @daq_use_homemade_amplifier.setter
    def daq_use_homemade_amplifier(self,value):
        self._use_homemade_amplifier = value

    @property
    def daq_homemade_amplifier_amplification(self):
        return self._homemade_amplifier_amplification


    @property
    def daq_use_additional_amplifier(self):
        return self._use_additional_amplifier 
    
    @daq_use_additional_amplifier.setter
    def daq_use_additional_amplifier(self,value):
        self._use_additional_amplifier = value
        
    @property
    def daq_additional_amplifier_amplification(self):
        return self._additional_amplifier_amplification

    @daq_additional_amplifier_amplification.setter
    def daq_additional_amplifier_amplification(self,value):
        self._additional_amplifier_amplification = value

    
    def daq_init_acquisition(self):
        pass

    def daq_start_acquisition(self):
        pass

    def daq_stop_acquisition(self):
        pass

    def daq_acquisition_is_alive(self):
        pass


class FANS_CONTROLLER:
    def __init__(self,visa_resource):
        self._device = AgilentU2542A(visa_resource)
        self.fans_reset()
        self._ai_channels = {ch: FANS_AI_channel(ch, self.fans_device) for ch in AI_CHANNELS.indexes}
        self._ao_channels = {ch: FANS_AO_channel(ch, self.fans_device) for ch in AO_CHANNELS.indexes}
        self._ao_switch = FANS_AO_Channel_Switch(self.fans_device, *self._ao_channels.values())
        self.initialize_hardware()

    def initialize_hardware(self):
        ## CALL DIG DAQ HARDWARE INITIALIZATION
        self.__init_daq_dig_channels()

        ## CALL DAQ HARDWARE INITIALIZATION
        self.__init_ai_channels()
        self.__init_ao_channels()
        

    def __init_daq_dig_channels(self):
        self.fans_device.dig_set_direction(DIGITAL_DIRECTIONS.OUTP,DIGITAL_CHANNELS.indexes)

    def __init_ai_channels(self):
        for name, channel in self._ai_channels.items():
            channel.set_hardware_params()
            channel.set_fans_ai_channel_params()
            

    def __init_ao_channels(self):
        for name, channel in self._ao_channels.items():
            channel.set_hardware_params()



    def set_configuration(self,configuration):
        self._config = configuration
        self.__apply_configuration()

    def __apply_cofiguration(self):
        pass

    def set_data_storage(self,data_storage):
        self._data_storage = data_storage
    
    def fans_reset(self):
        self.fans_device.daq_reset()

    @property
    def fans_device(self):
        return self._device

    @property
    def fans_ao_switch(self):
        return self._ao_switch

    def get_ai_channel(self, channel):
        return self._ai_channels[channel]

    def get_ao_channel(self,channel):
        return self._ao_channels[channel]

    def analog_read(self,channels):
        arg_type = type(channels)
        if arg_type is tuple: channels = list(channels)
        elif arg_type is not list: channels = [channels]
        channels.sort()
        channel_value_pairs = self.fans_device.adc_measure(channels)
        if len(channel_value_pairs) == 1:
            return list(channel_value_pairs.values())[0]
        return channel_value_pairs

    def analog_read_averaging(self,averaging):
        return self.fans_device.adc_set_voltage_average(averaging)


##
##  OLD VERSION
##

class FANS_controller:
    def __init__(self, visa_resource="ADC", data_storage=None, configuration = None):
        self.visa_resource = visa_resource
        self.device = AgilentU2542A(visa_resource)

        self.data_storage = data_storage
        self.data_queue = None
        self.config = configuration

##        subscribe to all events in configuration changes
        self.initialize_configuration()


        ## INITIALIZE VALUES FOR OUTPUT CHANNELS
        self.ao_channel_params = dict((ch,get_fans_ao_channel_default_params(ch)) for ch in AO_CHANNELS.indexes)
        self.ai_channel_params = dict((ch,get_fans_ai_channel_default_params()) for ch in AI_CHANNELS.indexes)
        
        
        
##        print(self.config.get_root_node())
##        self.config = Configuration()
##        print(self.config.get_root_node())
        self.initialize_hardware()

        self.load_resistance = 100000


    def ch_ch(self,value,sender):
        print("value changed")
        print(sender)
        print(value)
            

    def initialize_configuration(self):
        self.config.set_binding("input_settings.ch1.enabled","checked",self.ch_ch)

    def initialize_hardware(self):
        ## CALL DIG DAQ HARDWARE INITIALIZATION
        self._init_daq_dig_channels()

        ## CALL DAQ HARDWARE INITIALIZATION
        self._init_daq_ai_channels()
        self._init_daq_ao_channels()
        
        ## CALL FANS HARDWARE INITIALIZATION
        self._init_fans_ai_channels()
        self._init_fans_ao_channels()

        


    def fans_reset(self):
        self.device.daq_reset()
        
        
##
##    ANALOG INPUT SECTION
##
    def _init_daq_ai_channels(self):
        for channel in AI_CHANNELS.indexes:
            en = STATES.ON
            rng = DAQ_RANGES.RANGE_10
            pol = POLARITIES.BIP
            ch = channel
            self._set_daq_ai_channel_params(en,rng,pol,ch)
        ## 
        print("read back hardware params")
        self.device.daq_init_channels()
        
    ## set parameters for daq hardware
    ## ai_enabled: type STATES
    ## ai_range: type DAQ_RANGES
    ## ai_polarity: type POLARITIES
    ## ai_channel: type AI_CHANNELS
    def _set_daq_ai_channel_params(self, ai_enabled, ai_range, ai_polarity, ai_channel):
        self.device.daq_set_enable_ai_channel(ai_enabled,ai_channel)
        self.device.daq_set_channel_range(ai_range, ai_channel)
        self.device.daq_set_channel_polarity(ai_polarity,ai_channel)


    def _init_fans_ai_channels(self):
        
        ## INITIALIZE FANS INPUT CHANNELS
        for channel in AI_CHANNELS.indexes:
            ## create dummy variables
            ## need to replace by real values
            
            mode = AI_MODES.DC
            cs_hold = CS_HOLD.ON
            filter_cutoff = FILTER_CUTOFF_FREQUENCIES.f50
            filter_gain = FILTER_GAINS.x1
            pga_gain = PGA_GAINS.x1
##            time.sleep(1)
            self._set_fans_ai_channel_params(mode,cs_hold,filter_cutoff, filter_gain,pga_gain,channel)
        ## END INITIALIZE FANS INPUT CHANNELS
        ## need to check which channels are for acquisition, for vds, for vlg, etc.
        
    def set_fans_ai_channel_mode(self,ai_mode,ai_channel):
        self.device.dig_write_channel(ai_channel, DIGITAL_CHANNELS.DIG_502)
        self.device.dig_write_bit_channel(ai_mode,AI_SET_MODE_BIT,DIGITAL_CHANNELS.DIG_504)#AI_MODE_VAL[mode]
        self._pulse_digital_bit(AI_SET_MODE_PULS_BIT,DIGITAL_CHANNELS.DIG_504)

    def _set_fans_ai_channel_params(self, ai_mode, ai_cs_hold, ai_filter_cutoff,ai_filter_gain, ai_pga_gain, ai_channel):
##        print(ai_channel)
        ## set channel selected
        ##print("seelct channel {0:08b}".format(AI_ChannelSelector[ch]))
        self.device.dig_write_channel(ai_channel, DIGITAL_CHANNELS.DIG_502)
        ## set DC or AC position of relays
        ##print("mode value {0:08b}".format(AI_MODE_VAL[mode]))
        self.device.dig_write_bit_channel(ai_mode,AI_SET_MODE_BIT,DIGITAL_CHANNELS.DIG_504)#AI_MODE_VAL[mode]
        self._pulse_digital_bit(AI_SET_MODE_PULS_BIT,DIGITAL_CHANNELS.DIG_504)
        
            
        ## set filter frequency and gain parameters
        filter_val = get_filter_value(ai_filter_gain,ai_filter_cutoff)
        self.device.dig_write_channel(filter_val,DIGITAL_CHANNELS.DIG_501)

        ## set pga params
        pga_val = get_pga_value(ai_pga_gain,ai_cs_hold)
        self.device.dig_write_channel(pga_val, DIGITAL_CHANNELS.DIG_503)
        self._pulse_digital_bit(AI_ADC_LETCH_PULS_BIT,DIGITAL_CHANNELS.DIG_504)
            
##        print("ch: {0} - set".format(ai_channel))
        

    def init_acquisition(self, sample_rate,points_per_shot,channels):
        self.sample_rate = sample_rate
        self.points_per_shot = points_per_shot
        self.device.daq_setup(sample_rate,points_per_shot)
        self.device.daq_set_enable_ai_channels(STATES.OFF, AI_CHANNELS.indexes)
        self.device.daq_set_enable_ai_channels(STATES.ON,channels)
##        self.device.daq_init_channels()

    def start_acquisition(self):
        self.data_queue = JoinableQueue()
        fs = self.sample_rate
        t = 2400 #600 #16*60*60

##        data_storage = DataHandler(sample_rate=fs,points_per_shot = self.points_per_shot)
        self.dac_proc = Acquisition(self.visa_resource,self.data_queue, fs, self.points_per_shot, t*fs)
        #self.data_thread = AcquisitionProcess(None,self.data_queue)#self.data_storage,self.data_queue)
        self.data_thread = AcquisitionProcess(self.data_storage,self.data_queue)

        self.dac_proc.start()
        self.data_thread.start()
        print("started")

    def stop_acquisition(self):
        self.dac_proc.stop()
        print("stopped process")
        self.dac_proc.join()
        print("joined process")
        
        self.data_queue.join()
        self.data_thread.stop()
        print("joined thread")
        self.data_storage.stop_acuqisition()

    def acquisition_alive(self):
        return self.dac_proc.is_alive()

    def analog_read(self,channels):
        arg_type = type(channels)
        if arg_type is tuple: channels = list(channels)
        elif arg_type is not list: channels = [channels]
        channels.sort()
        channel_value_pairs = self.device.adc_measure(channels)
        return channel_value_pairs

    def analog_read_averaging(self,averaging):
        return self.device.adc_set_voltage_average(averaging);

##
##    ANALOG OUTPUT SECTION
##    
    def _init_daq_ao_channels(self):
        for ch in AO_CHANNELS.indexes:
            polarity = POLARITIES.BIP
            enable = STATES.ON
            self._set_daq_ao_channel_params(enable,polarity,ch)
        ## set polarity
        ## set enable
       
        
    def _set_daq_ao_channel_params(self, ao_enable, ao_polarity, ao_channel):
##        channel = ao_all_channels[ao_channel]
        self.device.daq_set_enable_ao_channel(ao_enable,ao_channel)
        self.device.daq_set_ao_channel_polarity(ao_polarity, ao_channel)
        
    def set_selected_output(self,ao_channel,ao_enabled):
        hardware_ao_ch = BOX_AO_CHANNEL_MAP[ao_channel]
        self.ao_channel_params[hardware_ao_ch]["selected_output"] = ao_channel
        self.ao_channel_params[hardware_ao_ch]["enabled"] = ao_enabled

    def _set_output_channel(self,ao_channel,ao_enabled):
        
        self.set_selected_output(ao_channel,ao_enabled)
        #hardware_ao_ch = BOX_AO_CHANNEL_MAP[ao_channel]
        #self.ao_channel_params[hardware_ao_ch]["selected_output"] = ao_channel
        #self.ao_channel_params[hardware_ao_ch]["enabled"] = ao_enabled

        ao1_channel = self.ao_channel_params[AO_CHANNELS.AO_202]["selected_output"]
        ao1_enabled = self.ao_channel_params[AO_CHANNELS.AO_202]["enabled"]
        ao2_channel = self.ao_channel_params[AO_CHANNELS.AO_201]["selected_output"]
        ao2_enabled = self.ao_channel_params[AO_CHANNELS.AO_201]["enabled"]

        self._set_output_channels(ao1_channel,ao1_enabled,ao2_channel,ao2_enabled)     

        ### ao1 - correcponds to AO_202, ao2 - corresponds to ao_201
    def _set_output_channels(self,ao1_channel,ao1_enabled,ao2_channel,ao2_enabled):
        if ao1_channel<NUMBER_OF_SWITCH_CHANNELS and ao2_channel>= NUMBER_OF_SWITCH_CHANNELS and (ao2_channel % NUMBER_OF_SWITCH_CHANNELS) < NUMBER_OF_SWITCH_CHANNELS:

            ###
            ###     bag with setting the enable bits
            ###

            ao1_enable_bit_mask = 1<<3
            ao1_disable_bit_mask = ~ao1_enable_bit_mask
            ao2_enable_bit_mask = 1<<7
            ao2_disable_bit_mask = ~ao2_enable_bit_mask
        
    ##        print("ao1_enable {0:08b}".format(ao1_enable))
    ##        print("ao2_enable {0:08b}".format(ao2_enable))
            channels_enab = ao1_enable_bit_mask | ao2_enable_bit_mask
            if not ao1_enabled:
                channels_enab = channels_enab&ao1_disable_bit_mask
            if not ao2_enabled:
                channels_enab = channels_enab&ao2_disable_bit_mask

    ##        print("enable {0:08b}".format(channels_enab))
            channels = (ao2_channel<<4)|ao1_channel
    ##        print("channels {0:08b}".format(channels))
            val_to_write = channels_enab|channels
            print("value to write {0:08b}".format(val_to_write))
            self.device.dig_write_channel(val_to_write,DIGITAL_CHANNELS.DIG_501)
            self._pulse_digital_bit(AO_DAC_LETCH_PULS_BIT,DIGITAL_CHANNELS.DIG_504)
        else:
            raise Exception("Incorrect channel values")

        
    def _init_fans_ao_channels(self):
        ## set fans output for hardware channel
        ao1_channel = self.ao_channel_params[AO_CHANNELS.AO_201]["selected_output"]
        ao1_enabled = self.ao_channel_params[AO_CHANNELS.AO_201]["enabled"]
        ao2_channel = self.ao_channel_params[AO_CHANNELS.AO_202]["selected_output"]
        ao2_enabled = self.ao_channel_params[AO_CHANNELS.AO_202]["enabled"]
        self._set_output_channels(ao1_channel,ao1_enabled,ao2_channel,ao2_enabled)
        

    def _set_fans_ao_channel_params(self, enable, polarity, channel ):
        self._set_daq_ao_channel_params(enable,polarity,channel)

    def fans_output_channel_voltage(self,voltage,channel):
        self.device.dac_source_channel_voltage(voltage,channel)

    def fans_output_voltage_to_channels(self,voltage,channels):
        self.device.dac_source_voltage(voltage,channels)
    
    def fans_output_voltage(self, ao1_voltage, ao2_voltage ):#, box_ao_channels):
        self.device.dac_source_channel_voltage(ao1_voltage,AO_CHANNELS.AO_201)
        self.device.dac_source_channel_voltage(ao2_voltage,AO_CHANNELS.AO_202)
    
##
##    DIGITAL OUTPUT SECTION
##
    
    def _init_daq_dig_channels(self):
##        configure digital pins for output
##        since we need them only to control the FANS box
        self.device.dig_set_direction(DIGITAL_DIRECTIONS.OUTP,DIGITAL_CHANNELS.indexes)


    def _pulse_digital_bit(self,bit,channel,pulse_width=0.005):
        self.device.dig_write_bit_channel(1,bit,channel)
        time.sleep(pulse_width)
        self.device.dig_write_bit_channel(0,bit,channel)
    
    

def main():
    device = AgilentU2542A("USB0::0x0957::0x1718::TW52524501::INSTR")#"ADC")
    channel = FANS_AI_channel(AI_CHANNELS.AI_101, device, mode = AI_MODES.DC)
    channel = FANS_AI_channel(AI_CHANNELS.AI_102, device, mode = AI_MODES.DC)
    channel = FANS_AI_channel(AI_CHANNELS.AI_103, device, mode = AI_MODES.DC)
    channel = FANS_AI_channel(AI_CHANNELS.AI_104, device, mode = AI_MODES.DC)

    ao_chan1 = FANS_AO_channel(AO_CHANNELS.AO_201, device)
    ao_chan2 = FANS_AO_channel(AO_CHANNELS.AO_202, device)
    
    switch = FANS_AO_Channel_Switch(device, ao_chan1,ao_chan2)
    out = switch.select_channel(AO_BOX_CHANNELS.ao_ch_1)

    #for i in np.arange(-10,10,0.5):
    #    out.ao_voltage = i
    #    time.sleep(1)

    for channel in AO_BOX_CHANNELS.indexes:
        output = switch.select_channel(channel)
        print(AO_CHANNELS[output.ao_name])
        print(AO_BOX_CHANNELS[channel])
        output.ao_voltage = 1
        time.sleep(5)
        output.ao_voltage = 0
    #val_to_write = 0xCC
    #device.dig_write_channel(val_to_write,DIGITAL_CHANNELS.DIG_501)
    #device.pulse_digital_bit(AO_DAC_LETCH_PULS_BIT,DIGITAL_CHANNELS.DIG_504)
    #ao_chan1.ao_voltage = 1
    #ao_chan2.ao_voltage = 2

    #switch.select_channel(AO_BOX_CHANNELS.ao_ch_1)
    #switch.select_channel(AO_BOX_CHANNELS.ao_ch_9)

    #ao_chan1.ao_voltage = 1
    #ao_chan2.ao_voltage = 2

    
    #ao_chan1.ao_voltage = 0
    #ao_chan2.ao_voltage = 0
    
    #cfg = Configuration()
    #f = FANS_controller("ADC",configuration=cfg)
    #f._set_output_channels(AO_BOX_CHANNELS.ao_ch_1,True,AO_BOX_CHANNELS.ao_ch_9,False)
    #f.fans_output_voltage(1,1)

    #channel.ai_filter_cutoff = 
    #switch = FANS_AO_Channel_Switch(device,


# UNCOMMENT THIS TO TEST FUNCTIONONALITY
#    cfg = Configuration()
#    f = FANS_controller("ADC",configuration = cfg)
#    f.init_acquisition(500000,50000,[AI_CHANNELS.AI_101,AI_CHANNELS.AI_102,AI_CHANNELS.AI_103,AI_CHANNELS.AI_104])
    
#    app = QtGui.QApplication(sys.argv)
#    app.setStyle("cleanlooks")
    
#    wnd = WndTutorial(configuration = cfg)
###    wnd.show()
###    sys.exit(app.exec_())
#    #f.fans_output_voltage(0,0)
#    #time.sleep(2)
#    #f.fans_output_voltage(6,-6)
#    #time.sleep(2)
#    #f.fans_output_voltage(0,4)
#    #time.sleep(2)
#    #f.fans_output_voltage(-6,6)
#    #time.sleep(2)
#    #f.fans_output_voltage(4,0)
#    #time.sleep(2)
#    #f.fans_output_voltage(0,0)
#    f.start_acquisition()
###    sleep(1)
#    try:
#        c = 0
#        while True:
###            print(c)
#            c+=1
###            sleep(1)
#            if not f.acquisition_alive():
#                break
#    except Exception as e:
#        print(str(e))
#    finally:       
#        print("stopping acquisition")
#        f.stop_acquisition()

if __name__ == "__main__":
    main()
