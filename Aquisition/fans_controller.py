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
        1: 0,
        2: 1,
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

##FILTER_CHANNEL = RELAYS_CHANNEL = DAC_CHANNEL = DIG_1
##PGA_CHANNEL = FILTER_CS_CHANNEL = DIG_3
##

class FANScontroller:
    def __init__(self, visa_resource):
        print("initialization")
        self.dev = AgilentU2542A(visa_resource)
        self.f_cutoff = None
        self.f_gain = None
        self.cs_hold = None
        self.pga_gain = None
        self.ain_channel = None
        self.daq_channel = None

    def preset_filter_cutoff(self, cutoff):
        self.f_cutoff = cutoff

    def preset_filter_gain(self,gain):
        self.f_gain = gain

    def preset_pga(self, pga):
        self.pga_gain = pga

    def preset_cs_hold(self, cshold):
        self.cs_hold = cshold

    

    def get_filter_value(self,pga,filter_cutoff):
        if (pga in PGA_GAINS) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES):
            fs = FINTER_CUTOFF_FREQUENCIES[filter_cutoff]
            fg = FILTER_GAINS[pga]
            val = (fg<<4)|fs
            return val

    
    
    

def main():
    d = FANScontroller('ADC')
##    print(pga_gains)
##    print(filter_gains)
##    print(filter_cutoff_frequencies)
    fs = FINTER_CUTOFF_FREQUENCIES['60k']
    fg = FILTER_GAINS[3]
    print(FILTER_CHANNEL)
    print(DIG_1)
    print("{0:08b}".format(fs))
    print("{0:08b}".format(fg))
    print("{0:08b}".format((fg<<4)|(fs)))
    
##    print(",".join(("101","102")))

if __name__ == "__main__":
    main()
