##from n_enum import enum
from fans_constants import *
from agilent_u2542a import *
from node_configuration import Configuration


class FANS_controller:
    def __init__(self, visa_resource="ADC", data_storage=None, configuration = None):
        self.visa_resource = visa_resource
        self.device = AgilentU2542A(visa_resource)

        self.data_queue = None
        self.config = Configuration()
##        print(self.config.get_root_node())
        self._init_daq_dig_channels()
        


    def fans_reset(self):
        self.device.daq_reset()
        
        
##
##    ANALOG INPUT SECTION
##
    def _init_daq_ai_channels(self):
        pass

    def _set_daq_ai_channel_params(self, ai_enabled, ai_range, ai_polarity, ai_channel):
        self.device.daq_set_channel_enable(ai_enabled,ai_channel)
        self.device.daq_set_range(ai_range, [ai_channel])
        self.device.daq_setpolarity(ai_polarity,[ai_channel])

    def _init_fans_ai_channels(self):
        ## CALL DAQ HARDWARE INITIALIZATION
        self._init_daq_ai_channels()
        ## INITIALIZE FANS INPUT CHANNELS
        for channel in AI_CHANNELS.names:
            ## create dummy variables
            ## need to replace by real values
            mode = AI_MODES.DC
            cs_hold = CS_HOLD.OFF
            filter_cutoff = FILTER_CUTOFF_FREQUENCIES.f100k
            filter_gain = FILTER_GAINS.x1
            self._set_fans_ai_channel_params(mode,cs_hold,filter_cutoff, filter_gain)
        ## END INITIALIZE FANS INPUT CHANNELS
        ## need to check which channels are for acquisition, for vds, for vlg, etc.
        
    
    def _set_fans_ai_channel_params(self, ai_mode, ai_cs_hold, ai_filter_cutoff,ai_filter_gain ):
        pass

    def _init_acquisiion(self):
        pass

    def _start_acquisition(self):
        pass

    def _stop_acquisition(self):
        pass

    def _acquisition_alive(self):
        pass

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
            pass
    
    

def main():
    f = FANS_controller("ADC")

if __name__ == "__main__":
    main()
