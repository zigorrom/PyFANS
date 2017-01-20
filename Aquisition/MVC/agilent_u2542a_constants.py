from n_enum import enum

##
##  DAQ CONSTANTS
##

##DAQ_AI_CHANNELS = enum('ai_101','ai_102','ai_103','ai_104')
ai_all_channels = ['101','102','103','104']
##AI_CHANNELS = enum(*["ai_{0}".format(i) for i in ai_all_channels])
AI_1,AI_2, AI_3, AI_4 = ai_all_channels


ao_all_channels = ['201','202']
##AO_CHANNELS = enum(*["ao_{0}".format(i) for i in ao_all_channels])
AO_1,AO_2 = ao_all_channels

ai_all_ranges = ['10','5','2.5','1.25']
Range_10, Range_5, Range_2_5,Range_1_25 = ai_all_ranges
ai_all_fRanges = [float(i) for i in ai_all_ranges]

ai_all_polarities = ['BIP','UNIP']
Bipolar,Unipolar = ai_all_polarities
##
##  END DAQ CONSTANTS
##

##
##  DIGITAL CONSTANTS
##

dig_all_channels = ['501','502','503','504']
DIG_1, DIG_2,DIG_3,DIG_4 = dig_all_channels
dig_channel_bits = [8,8,4,4]

dig_directions = ['INP','OUTP']
DIG_INP, DIG_OUTP = dig_directions


##
##  END DIGITAL CONSTANTS
##

states = ['ON','OFF']
STATE_ON, STATE_OFF = states
