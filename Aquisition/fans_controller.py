from agilent_u2542a import *

PGA_GAINS = {1:     0,
             10:    1,
             100:   2}

FINTER_CUTOFF_FREQUENCIES ={
        '0':0,
        '10k': 1,
        '20k':2,
        '30k':3,
        '40k':4,
        '50k':5,
        '60k':6,
        '70k':7,
        '80k':8,
        '90k':9,
        '100k':10,
        '110k':11,
        '120k':12,
        '130k':13,
        '140k':14,
        '150k':15
    }

FILTER_GAINS = {
        1:0,
        2:1,
        3:2,
        4:3,
        5:4,
        6:5,
        7:6,
        8:7,
        9:8,
        10:9,
        11:10,
        12:11,
        13:12,
        14:13,
        15:14,
        16:15
    }
CS_HOLD = {'ON':4,'OFF':0}

AI_MODEs = ["DC","AC"]
AI_DC_mode, AI_AC_mode = AI_MODEs

AI_ChannelSelector = {
                AI_1: 0,
                AI_2: 1,
                AI_3: 2,
                AI_4: 3
                      }

AI_MODE_SET_PULS_MASK = 1
AI_MODE_SET_MASK = 2
AI_ADC_LETCH_MASK = 4
AO_CHANNEL_LETCH_MASK = 8



def get_ai_channel_default_params():
    return {
        'mode': AI_AC_mode,
        'filter_cutoff': '0',
        'filter_gain': 1,
        'pga_gain':1,
        'cs_hold':'OFF'
        }

def get_ao_channel_default_params():
    return {'selected_output':0}

def get_channel_selector_params():
    return {'selected_meas_ch':0}

def get_filter_value(pga,filter_cutoff):
    if (pga in PGA_GAINS) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES):
        fs = FINTER_CUTOFF_FREQUENCIES[filter_cutoff]
        fg = FILTER_GAINS[pga]
        val = (fg<<4)|fs
        return val


class FANScontroller:
    def __init__(self, visa_resource):
        print("initialization")
        self.dev = AgilentU2542A(visa_resource)

        self.ai_channel_params = {
            AI_1:get_ai_channel_default_params(),
            AI_2:get_ai_channel_default_params(),
            AI_3:get_ai_channel_default_params(),
            AI_4:get_ai_channel_default_params()
            }
        
        self.ao_channel_params = {
            AO_1: get_ao_channel_default_params(),
            AO_2: get_ao_channel_default_params()
            }

        self.ch_selector_params = get_channel_selector_params()
        
##        print(self.ai_channel_params)
##        print(self.ao_channel_params)
        self.init_channels()
        

    def pulse_bit(self,bit,channel, pulse_width = 0.001):
        self.dev.dig_write_bit_channel(1,bit,(channel,))
        time.sleep(pulse_width)
        self.dev.dig_write_bit_channel(0,bit,(channel,))

    def init_channels(self):
        defaults = get_ai_channel_default_params()
        self.set_ai_params(defaults['mode'],defaults['cs_hold'],defaults['filter_cutoff'],defaults['filter_gain'],defaults['pga_gain'],ai_all_channels)
        
    def set_ai_params(self, mode, cs_hold, filter_cutoff, filter_gain, pga_gain, channels):
        if (mode in AI_MODEs) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES) and (filter_gain in FILTER_GAINS) and (pga_gain in PGA_GAINS) and all(ch in ai_all_channels for ch in channels):
            for ch in channels:
                self.ai_channel_params[ch]['mode'] = mode
                self.ai_channel_params[ch]['filter_cutoff'] = filter_cutoff
                self.ai_channel_params[ch]['filter_gain'] = filter_gain
                self.ai_channel_params[ch]['pga_gain'] = pga_gain
                self.ai_channel_params[ch]['cs_hold'] = cs_hold

                self.dev.dig_write_channel(AI_ChannelSelector[ch],(ch,))
                val = 0
                if mode == AI_DC_mode:
                    val = AI_MODE_SET_MASK
                self.dev.dig_write_channel(val,(DIG_4,))
                self.pulse_bit(AI_MODE_SET_PULS_MASK,DIG_4)
                print("ch: {0} - set".format(ch))
                
            

            

    
    
    

def main():
    d = FANScontroller('ADC')
    fs = FINTER_CUTOFF_FREQUENCIES['60k']
    fg = FILTER_GAINS[3]
##    print("{0:08b}".format(AI_MODE_SET_PULS_MASK|AI_ADC_LETCH_MASK |AO_CHANNEL_LETCH_MASK))

##    a  = {'a':123,'b':321}
##    a['a'] = 222
##    if 'a' in a:
##        print("yes")
##    print(a)
##    print(DIG_1)
##    print("{0:08b}".format(fs))
##    print("{0:08b}".format(fg))
##    print("{0:08b}".format((fg<<4)|(fs)))

##    print(",".join(("101","102")))

if __name__ == "__main__":
    main()
