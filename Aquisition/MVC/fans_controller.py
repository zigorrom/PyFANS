##from n_enum import enum
import time
from fans_constants import *
from agilent_u2542a import *
from agilent_u2542a_constants import *
from node_configuration import Configuration
from multiprocessing import Process, Event, JoinableQueue
from acquisition_process import Acquisition,AcquisitionProcess


class FANS_controller:
    def __init__(self, visa_resource="ADC", data_storage=None, configuration = None):
        self.visa_resource = visa_resource
        self.device = AgilentU2542A(visa_resource)

        self.data_queue = None
        self.config = configuration

##        subscribe to all events in configuration changes


        ## INITIALIZE VALUES FOR OUTPUT CHANNELS
        self.ao_channel_params = dict((ch,get_fans_ao_channel_default_params()) for ch in AO_CHANNELS.indexes)
        self.ai_channel_params = dict((ch,get_fans_ai_channel_default_params()) for ch in AI_CHANNELS.indexes)
        
        
        
##        print(self.config.get_root_node())
##        self.config = Configuration()
##        print(self.config.get_root_node())
        self.initialize_hardware()

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
            cs_hold = CS_HOLD.OFF
            filter_cutoff = FILTER_CUTOFF_FREQUENCIES.f100
            filter_gain = FILTER_GAINS.x1
            pga_gain = PGA_GAINS.x1
##            time.sleep(1)
            self._set_fans_ai_channel_params(mode,cs_hold,filter_cutoff, filter_gain,pga_gain,channel)
        ## END INITIALIZE FANS INPUT CHANNELS
        ## need to check which channels are for acquisition, for vds, for vlg, etc.
        
    
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
        self.device.daq_set_enable_ai_channels(STATES.ON,channels)
##        self.device.daq_init_channels()

    def start_acquisition(self):
        self.data_queue = JoinableQueue()
        fs = self.sample_rate
        t = 600 #16*60*60

##        data_storage = DataHandler(sample_rate=fs,points_per_shot = self.points_per_shot)
        self.dac_proc = Acquisition(self.visa_resource,self.data_queue, fs, self.points_per_shot, t*fs)
        self.data_thread = AcquisitionProcess(None,self.data_queue)#self.data_storage,self.data_queue)
        
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

    def acquisition_alive(self):
        return self.dac_proc.is_alive()

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
        
       
    def _set_output_channels(self,ao1_channel,ao1_enabled,ao2_channel,ao2_enabled):
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
        
        
    def _init_fans_ao_channels(self):
        ## set fans output for hardware channel
        self._set_output_channels(0,True,0,True)
        
        
    

    def _set_fans_ao_channel_params(self, enable, polarity, channel ):
        pass

    def fans_output_channel_voltage(self,voltage,channel):
        self.device.dac_source_channel_voltage(voltage,channel)

    def fans_output_voltage(self, ao1_voltage, ao2_voltage ):#, box_ao_channels):
        ## ON

        
        self.device.dac_source_channel_voltage(ao1_voltage,AO_CHANNELS.AO_201)
        self.device.dac_source_channel_voltage(ao2_voltage,AO_CHANNELS.AO_202)
##        time.sleep(20)
##        ## OFF
##        self.device.dac_source_voltage(0,ao_all_channels)
    
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
##    cfg = Configuration()
    f = FANS_controller("ADC")#,configuration = cfg)
    f.init_acquisition(500000,50000,[AI_CHANNELS.AI_101,AI_CHANNELS.AI_102,AI_CHANNELS.AI_103,AI_CHANNELS.AI_104])
    f.fans_output_voltage(0,0)
    time.sleep(2)
    f.fans_output_voltage(6,-6)
    time.sleep(2)
    f.fans_output_voltage(0,4)
    time.sleep(2)
    f.fans_output_voltage(-6,6)
    time.sleep(2)
    f.fans_output_voltage(4,0)
    time.sleep(2)
    f.fans_output_voltage(0,0)
##    f.start_acquisition()
####    sleep(1)
##    try:
##        c = 0
##        while True:
####            print(c)
##            c+=1
####            sleep(1)
##            if not f.acquisition_alive():
##                break
##    except Exception as e:
##        print(str(e))
##    finally:       
##        print("stopping acquisition")
##        f.stop_acquisition()

if __name__ == "__main__":
    main()
