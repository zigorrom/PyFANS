from n_enum import enum
from agilent_u2542a import *
from agilent_u2542a_constants import *

PGA_GAINS = enum("1","10","100", name_prefix= "x")
FILTER_CUTOFF_FREQUENCIES = enum(*["{0}".format(i) for i in range(0,160,10)], name_prefix="f")
FILTER_GAINS = enum(*["{0}".format(i) for i in range(1,16)],name_prefix = "x")

CS_HOLD = enum("OFF", "ON")

AI_MODES = enum("DC","AC")
#AI_CHANNELS = enum("AI_1","AI_2","AI_3","AI_4")

AI_SET_MODE_PULS_BIT = 0
AI_SET_MODE_BIT = 1
AI_ADC_LETCH_PULS_BIT = 2
AO_DAC_LETCH_PULS_BIT = 3

AI_BOX_CHANNELS = enum(*["ai_ch_{0}".format(i) for i in range(1,9)])

##AO_CHANNELS = enum("AO_1","AO_2")

BOX_AI_CHANNELS_MAP = {0: {"channel": AI_CHANNELS.AI_101,"mode": AI_MODES.AC},
                       1: {"channel": AI_CHANNELS.AI_102,"mode": AI_MODES.AC},
                       2: {"channel": AI_CHANNELS.AI_103,"mode": AI_MODES.AC},
                       3: {"channel": AI_CHANNELS.AI_104,"mode": AI_MODES.AC},
                       4: {"channel": AI_CHANNELS.AI_101,"mode": AI_MODES.DC},
                       5: {"channel": AI_CHANNELS.AI_102,"mode": AI_MODES.DC},
                       6: {"channel": AI_CHANNELS.AI_103,"mode": AI_MODES.DC},
                       7: {"channel": AI_CHANNELS.AI_104,"mode": AI_MODES.DC}
                       }



NUMBER_OF_SWITCH_CHANNELS = 8

BOX_AO_CHANNEL_MAP = dict((i , AO_CHANNELS.AO_202 if i<NUMBER_OF_SWITCH_CHANNELS else AO_CHANNELS.AO_201)  for i in range(16))

AO_BOX_CHANNELS = enum(*["ao_ch_{0}".format(i) for i in range(1,17)])

FANS_AI_FUNCTIONS = enum("DrainSourceVoltage","MainVoltage","GateVoltage")


def get_fans_ai_channel_default_params():
    return {
        'mode': AI_MODES.DC,
        'filter_cutoff': FILTER_CUTOFF_FREQUENCIES.f100,
        'filter_gain': FILTER_GAINS.x1,
        'pga_gain':PGA_GAINS.x1,
        'cs_hold':CS_HOLD.ON,
        'enabled' : STATES.ON,
        'range': DAQ_RANGES.RANGE_10,
        'polarity': POLARITIES.BIP
        }

def get_fans_ao_channel_default_params(HARDWARE_AO_CH):
    return {
        'selected_output':HARDWARE_AO_CH*NUMBER_OF_SWITCH_CHANNELS,
        'voltage':0,
        'polarity': POLARITIES.BIP,
        'range': DAQ_RANGES.RANGE_10,
        'enabled': STATES.ON
            }


def get_filter_value(filter_gain,filter_cutoff):
##    if (filter_gain in FILTER_GAINS) and (filter_cutoff in FINTER_CUTOFF_FREQUENCIES):
##    fs = FINTER_CUTOFF_FREQUENCIES[filter_cutoff]
##    fg = FILTER_GAINS[filter_gain]
    val = (filter_gain<<4)|filter_cutoff
    return val

def get_pga_value(pga_gain, cs_hold):
##    if(pga_gain in PGA_GAINS) and (cs_hold in CS_HOLD):
##    pg = PGA_GAINS[pga_gain]
##    cs = CS_HOLD[cs_hold]
    val = (cs_hold<<2) | pga_gain
    return val


#print(BOX_AO_CHANNEL_MAP)
#print(BOX_AO_CHANNEL_MAP[13])
#print(BOX_AO_CHANNEL_MAP[4])

if __name__ == "__main__":
    pass