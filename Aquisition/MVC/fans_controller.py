##from n_enum import enum
from fans_constants import *
from agilent_u2542a import *
from node_configuration import Configuration
from multiprocessing import Process, Event, JoinableQueue
from acquisition_process import Acquisition,AcquisitionProcess


class FANS_controller:
    def __init__(self, visa_resource="ADC", data_storage=None, configuration = None):
        self.visa_resource = visa_resource
        self.device = AgilentU2542A(visa_resource)

        self.data_queue = None
        self.config = configuration
##        print(self.config.get_root_node())
##        self.config = Configuration()
##        print(self.config.get_root_node())
        
        ## CALL DIG DAQ HARDWARE INITIALIZATION
        self._init_daq_dig_channels()

        ## CALL DAQ HARDWARE INITIALIZATION
        self._init_daq_ai_channels()

        ## CALL FANS HARDWARE INITIALIZATION
        self._init_fans_ai_channels()


    def fans_reset(self):
        self.device.daq_reset()
        
        
##
##    ANALOG INPUT SECTION
##
    def _init_daq_ai_channels(self):
        for channel in AI_CHANNELS.names:
            en = STATE_ON
            rng = Range_10
            pol = Bipolar
            ch = AI_CHANNELS.names.index(channel)
            self._set_daq_ai_channel_params(en,rng,pol,ch)
        ## 
        print("read back hardware params")
        self.device.daq_init_channels()
        

    def _set_daq_ai_channel_params(self, ai_enabled, ai_range, ai_polarity, ai_channel):

    ## issue with channel names
        channel = ai_all_channels[ai_channel]
        self.device.daq_set_channel_enable(ai_enabled,channel)
        self.device.daq_set_range(ai_range, [channel])
        self.device.daq_setpolarity(ai_polarity,[channel])

    def _init_fans_ai_channels(self):
        
        ## INITIALIZE FANS INPUT CHANNELS
        for channel in range(len(AI_CHANNELS.names)):
            ## create dummy variables
            ## need to replace by real values
            
            mode = AI_MODES.AC
            cs_hold = CS_HOLD.OFF
            filter_cutoff = FILTER_CUTOFF_FREQUENCIES.f100k
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
        self.device.dig_write_channel(ai_channel, DIG_2)
        ## set DC or AC position of relays
        ##print("mode value {0:08b}".format(AI_MODE_VAL[mode]))
        self.device.dig_write_bit_channel(ai_mode,AI_SET_MODE_BIT,DIG_4)#AI_MODE_VAL[mode]
        self._pulse_digital_bit(AI_SET_MODE_PULS_BIT,DIG_4)
        
            
        ## set filter frequency and gain parameters
        filter_val = get_filter_value(ai_filter_gain,ai_filter_cutoff)
        self.device.dig_write_channel(filter_val,DIG_1)

        ## set pga params
        pga_val = get_pga_value(ai_pga_gain,ai_cs_hold)
        self.device.dig_write_channel(pga_val, DIG_3)
        self._pulse_digital_bit(AI_ADC_LETCH_PULS_BIT,DIG_4)
            
        print("ch: {0} - set".format(ai_channel))
        

    def init_acquisition(self, sample_rate,points_per_shot,channels):
        self.sample_rate = sample_rate
        self.points_per_shot = points_per_shot
        self.device.daq_setup(sample_rate,points_per_shot)
        self.device.daq_enable_channels(channels)

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
        pass
    
    def _init_fans_ao_channels(self):
        pass

    def _set_fans_ao_channel_params(self):
        pass

    
##
##    DIGITAL OUTPUT SECTION
##
    
    def _init_daq_dig_channels(self):
##        configure digital pins for output
##        since we need them only to control the FANS box
        self.device.dig_set_direction(DIG_OUTP,dig_all_channels)

    def _pulse_digital_bit(self,bit,channel,pulse_width=0.005):
        self.device.dig_write_bit_channel(1,bit,channel)
        time.sleep(pulse_width)
        self.device.dig_write_bit_channel(0,bit,channel)
    
    

def main():
##    cfg = Configuration()
    f = FANS_controller("ADC")#,configuration = cfg)
    f.init_acquisition(500000,50000,[AI_1,AI_2,AI_3,AI_4])
    f.start_acquisition()
##    sleep(1)
    try:
        c = 0
        while True:
##            print(c)
            c+=1
##            sleep(1)
            if not f.acquisition_alive():
                break
    except Exception as e:
        print(str(e))
    finally:       
        print("stopping acquisition")
        f.stop_acquisition()

if __name__ == "__main__":
    main()
