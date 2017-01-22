from n_enum import enum
from agilent_u2542a import *
from agilent_u2542a_constants import *

PGA_GAINS = enum("1","10","100", name_prifix= "x")
FILTER_CUTOFF_FREQUENCIES = enum(*["{0}".format(i) for i in range(0,160,10)], name_prefix="f")
FILTER_GAINS = enum(*["{0}".format(i) for i in range(1,16)],name_prefix = "x")

CS_HOLD = enum("ON", "OFF")

AI_MODES = enum("DC","AC")
#AI_CHANNELS = enum("AI_1","AI_2","AI_3","AI_4")

AI_SET_MODE_PULS_BIT = 0
AI_SET_MODE_BIT = 1
AI_ADC_LETCH_PULS_BIT = 2
AO_DAC_LETCH_PULS_BIT = 3

AI_BOX_CHANNELS = enum(*["ai_ch_{0}".format(i) for i in range(1,9)])

AO_CHANNELS = enum("AO_1","AO_2")

BOX_AI_CHANNELS_MAP = {1: {"channel": AI_CHANNELS.AI_1,"mode": AI_MODES.AC},
                       2: {"channel": AI_CHANNELS.AI_2,"mode": AI_MODES.AC},
                       3: {"channel": AI_CHANNELS.AI_3,"mode": AI_MODES.AC},
                       4: {"channel": AI_CHANNELS.AI_4,"mode": AI_MODES.AC},
                       5: {"channel": AI_CHANNELS.AI_1,"mode": AI_MODES.DC},
                       6: {"channel": AI_CHANNELS.AI_2,"mode": AI_MODES.DC},
                       7: {"channel": AI_CHANNELS.AI_3,"mode": AI_MODES.DC},
                       8: {"channel": AI_CHANNELS.AI_4,"mode": AI_MODES.DC}
                       }

A0_BOX_CHANNELS = enum(*["ao_ch_{0}".format(i) for i in range(1,17)])


def get_fans_ai_channel_default_params():
    return {
        'mode': AI_MODES.DC,
        'filter_cutoff': FILTER_CUTOFF_FREQUENCIES.f100k,
        'filter_gain': FILTER_GAINS.x1,
        'pga_gain':PGA_GAINS.x1,
        'cs_hold':CS_HOLD.ON
        }

def get_ao_channel_default_params():
    return {
        'selected_output':0,
        'voltage':0,
        'polarity': Bipolar
        
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
    val = cs_hold & pga_gain
    return val



