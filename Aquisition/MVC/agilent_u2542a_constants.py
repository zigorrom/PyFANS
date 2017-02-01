from n_enum import enum

##
##  DAQ CONSTANTS
##

AI_CHANNELS = enum("101","102","103","104", name_prefix = "AI_")
AO_CHANNELS = enum("201","202", name_prefix = "AO_")

DAQ_RANGES = enum('10','5','2.5','1.25' , name_prefix = "RANGE_")
ai_all_fRanges = [float(i) for i in DAQ_RANGES.values]

POLARITIES = enum("BIP","UNIP")

DIGITAL_CHANNELS = enum("501","502","503","504",name_prefix = "DIG_")
dig_channel_bits = (8,8,4,4)


DIGITAL_DIRECTIONS = enum("INP","OUTP")

STATES = enum("OFF","ON")


 