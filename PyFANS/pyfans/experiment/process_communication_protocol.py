﻿#from n_enum import enum
from enum import IntEnum, unique

@unique
class ExperimentCommands(IntEnum):
    EXPERIMENT_STARTED = 1
    EXPERIMENT_FINISHED = 2
    DATA = 3
    MESSAGE = 4
    MEASUREMENT_STARTED = 5
    MEASUREMENT_FINISHED = 6
    SPECTRUM_DATA = 7
    TIMETRACE_DATA = 8
    EXPERIMENT_INFO = 9
    MEASUREMENT_INFO = 10
    MEASUREMENT_INFO_START = 11
    MEASUREMENT_INFO_END = 12
    ABORT = 13 
    ERROR = 14
    LOG_MESSAGE = 15
    PROGRESS_CHANGED = 16
    THERMAL_NOISE = 17
    VOLTAGE_SETTING_STARTED = 18
    VOLTAGE_SETTING_STOPPED = 19
    DRAIN_SOURCE_VOLTAGE_CHANGED = 20
    GATE_SOURCE_VOLTAGE_CHANGED = 21
    EXPERIMENT_TIME_UPDATE = 22

#ExperimentCommands = enum("EXPERIMENT_STARTED","EXPERIMENT_STOPPED","DATA","MESSAGE", "MEASUREMENT_STARTED", "MEASUREMENT_FINISHED", "SPECTRUM_DATA", "TIMETRACE_DATA","EXPERIMENT_INFO", "MEASUREMENT_INFO","MEASUREMENT_INFO_START","MEASUREMENT_INFO_END", "ABORT", "ERROR", "LOG_MESSAGE")

COMMAND = 'c'
PARAMETER = 'p'
DATA = 'd'
AVERAGES = 'avg'
SPECTRUM_RANGE = 'r'
FREQUENCIES = 'f'
INDEX = 'i'


if __name__ == "__main__":
    print (ExperimentCommands.EXPERIMENT_STARTED)