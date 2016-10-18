from agilent_u2542a import *
from multiprocessing import Process
from time import sleep

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
AI_MODE_VAL = {"DC":1,"AC":0}
AI_DC_mode, AI_AC_mode = AI_MODEs

AI_ChannelSelector = {
                AI_1: 0,
                AI_2: 1,
                AI_3: 2,
                AI_4: 3
                      }

AI_SET_MODE_PULS_BIT = 0
AI_SET_MODE_BIT = 1
AI_ADC_LETCH_PULS_BIT = 2
AO_DAC_LETCH_PULS_BIT = 3


BOX_AI_CHANNELS_MAP = {1: {"channel": AI_1,"mode": AI_AC_mode},
                       2: {"channel": AI_2,"mode": AI_AC_mode},
                       3: {"channel": AI_3,"mode": AI_AC_mode},
                       4: {"channel": AI_4,"mode": AI_AC_mode},
                       5: {"channel": AI_1,"mode": AI_DC_mode},
                       6: {"channel": AI_2,"mode": AI_DC_mode},
                       7: {"channel": AI_3,"mode": AI_DC_mode},
                       8: {"channel": AI_4,"mode": AI_DC_mode}
                       }

def get_ai_channel_default_params():
    return {
        'mode': AI_AC_mode,
        'filter_cutoff': '0',
        'filter_gain': 1,
        'pga_gain':1,
        'cs_hold':'OFF'
        }

def get_ao_channel_default_params():
    return {
        'selected_output':0,
        'voltage':0
            }

MAX_MEAS_CHANNELS = 32
##def get_channel_selector_params():
##    return {'selected_meas_ch':0}

def get_filter_value(filter_gain,filter_cutoff):
    if (filter_gain in FILTER_GAINS) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES):
        fs = FINTER_CUTOFF_FREQUENCIES[filter_cutoff]
        fg = FILTER_GAINS[filter_gain]
        val = (fg<<4)|fs
        return val

def get_pga_value(pga_gain, cs_hold):
    if(pga_gain in PGA_GAINS) and (cs_hold in CS_HOLD):
        pg = PGA_GAINS[pga_gain]
        cs = CS_HOLD[cs_hold]
        val = cs & pg
        return val

class FANScontroller:
    def __init__(self, visa_resource):
        print("initialization")
        self.dev = AgilentU2542A(visa_resource)
        self.dev.dig_set_direction(DIG_OUTP,dig_all_channels)
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

        self.measurement_channel = 0

        self.init_channels()
        self.daq_proc = None
        

    def pulse_bit(self,bit,channel, pulse_width = 0.005):
        self.dev.dig_write_bit_channel(1,bit,channel)
        time.sleep(pulse_width)
        self.dev.dig_write_bit_channel(0,bit,channel)

    def init_channels(self):
        defaults = get_ai_channel_default_params()
        self.set_ai_params(defaults['mode'],defaults['cs_hold'],defaults['filter_cutoff'],defaults['filter_gain'],defaults['pga_gain'],ai_all_channels)
        
    def set_ai_channel_params(self, mode, cs_hold, filter_cutoff, filter_gain, pga_gain, channel):
        if (mode in AI_MODEs) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES) and (filter_gain in FILTER_GAINS) and (pga_gain in PGA_GAINS) and (channel in ai_all_channels):
            ch = self.ai_channel_params[channel]
            ch['mode'] = mode
            ch['filter_cutoff'] = filter_cutoff
            ch['filter_gain'] = filter_gain
            ch['pga_gain'] = pga_gain
            ch['cs_hold'] = cs_hold
            ## set channel selected
##                print("seelct channel {0:08b}".format(AI_ChannelSelector[ch]))
            self.dev.dig_write_channel(AI_ChannelSelector[channel],DIG_2)
                
            ## set DC or AC position of relays
##                print("mode value {0:08b}".format(AI_MODE_VAL[mode]))
            self.dev.dig_write_bit_channel(AI_MODE_VAL[mode],AI_SET_MODE_BIT,DIG_4)#AI_MODE_VAL[mode]
            self.pulse_bit(AI_SET_MODE_PULS_BIT,DIG_4)

                
            ## set filter frequency and gain parameters
            filter_val = get_filter_value(filter_gain,filter_cutoff)
            self.dev.dig_write_channel(filter_val,DIG_1)

            ## set pga params
            pga_val = get_pga_value(pga_gain,cs_hold)
            self.dev.dig_write_channel(pga_val, DIG_3)
            self.pulse_bit(AI_ADC_LETCH_PULS_BIT,DIG_4)
                
            print("ch: {0} - set".format(ch))


    def set_ai_params(self, mode, cs_hold, filter_cutoff, filter_gain, pga_gain, channels):
        if (mode in AI_MODEs) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES) and (filter_gain in FILTER_GAINS) and (pga_gain in PGA_GAINS) and all(ch in ai_all_channels for ch in channels):
            for ch in channels:
                self.set_ai_channel_params(mode,cs_hold,filter_cutoff,filter_gain,pga_gain,ch)

        
    def set_measurement_channel(self, meas_channel):
        if (meas_channel<=MAX_MEAS_CHANNELS) and (meas_channel>=0):
            self.measurement_channel = meas_channel
            self.dev.dig_write_channel(meas_channel,DIG_1)
            self.pulse_bit(3,DIG_3)
            
    def start_acquisition(self):
        self.dac_proc = Process(target = acquisition)
        self.dac_proc.start()
        print("started")
        

    def stop_acquisition(self):
        self.dac_proc.terminate()
        self.dac_proc.join()
        print("joined")
        
    
def acquisition(res = 'ADC'):
##    sys.stdout = open(str(os.getpid()) + ".txt", "w")
    sys.stdout = open("log.txt", "w")
    try:
        d = AgilentU2542A('ADC')
        counter = 0
##        d.daq_reset()
##        d.daq_setup(500000,50000)
##        d.daq_enable_channels([AI_1,AI_2,AI_3,AI_4])
        d.daq_run()
        print("started")
        init_time = time.time()
        max_count = 10000
        while counter < max_count:
            try:
                if d.daq_is_data_ready():

                    counter += 1
                    t = time.time()-init_time

                    data = d.daq_read_data()
    ##                        q.put(t)
    ##                        q.put(data)
    ##                        if counter % 10 == 0:
    ##                            plt.plot(data[0])
    ##                            plt.pause(0.05)
    ##                        print()
                    print(t)
                    print(data)
                    

            except Exception as e:
                err = str(e)
                print(err)
                if err== 'overload':
                    counter = max_count
            
                
    except Exception as e:
    ##            pass
        print ("exception"+str(e))
    finally:
        d.daq_stop()
##        d.daq_reset()
        print("finished") 


def main():
##    d = AgilentU2542A('ADC')
##    d.dig_set_direction(DIG_OUTP,dig_all_channels)
##    set_reset = True
##    for i in range(3):
##        print("**********************************************")
##        print(i)
##        print("**********************************************")
##        for a in AI_ChannelSelector:
##            val = AI_ChannelSelector[a]
##            d.dig_write_channel(val, DIG_2)
##            if set_reset:
##                d.dig_write_bit_channel(1,1,DIG_4)
##            else:
##                d.dig_write_bit_channel(0,1,DIG_4)
##            d.dig_write_bit_channel(1,0,DIG_4)
##            time.sleep(0.005)
##            d.dig_write_bit_channel(0,0,DIG_4)
##        time.sleep(1)
##        set_reset= not set_reset
        
        
    d = FANScontroller('ADC')
    d.start_acquisition()
    c = 0
    while c<10:
        print(c)
        c+=1
        sleep(0.5)
    
    d.stop_acquisition()
##    fs = FINTER_CUTOFF_FREQUENCIES['60k']
##    fg = FILTER_GAINS[3]
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
