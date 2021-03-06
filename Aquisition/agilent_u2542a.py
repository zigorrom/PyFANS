import visa
import numpy as np
#install all necessary files from here http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
from scipy import signal
import time
import os
import sys
import matplotlib.pyplot as plt
from math import pow
from multiprocessing import Process, Queue


##
##  DAQ CONSTANTS
##
ai_all_channels = ['101','102','103','104']
AI_1,AI_2, AI_3, AI_4 = ai_all_channels

ao_all_channels = ['201','202']
AO_1,AO_2 = ao_all_channels

ai_all_ranges = ['10','5','2.5','1.25']
Range_10, Range_5, Range_2_5,Range_1_25 = ai_all_ranges
ai_all_fRanges = [float(i) for i in ai_all_ranges]

ai_all_polarities = ['BIP','UNIP']
Bipolar,Unipolar = ai_all_polarities

maxInt16 = 65536
maxInt16div2 = 32768
def BipolarConversionFunction(range_value, data_code):
    return (data_code*range_value)/maxInt16div2

def UnipolarConversionFunction(range_value, data_code):
    return (data_code/maxInt16+0.5)*range_value
### maybe optimization of execution speed
### IMPORTANT ORDER OF FUNCTIONS IN LIST -> CORRESPONDS TO ORDER IN AI_ALL_POLARITIES
ai_convertion_functions = [BipolarConversionFunction,UnipolarConversionFunction]
##ai_vect_convertion_functions = [np.vectorize(BipolarConversionFunction, otypes = [np.float]),np.vectorize(UnipolarConversionFunction, otypes = [np.float])]

def Convertion(a):
    pol_idx = a[2]
    range_val = ai_all_fRanges[a[1]]
    f = ai_convertion_functions[pol_idx]
    # starting from 4 since the header has 4 items
    timetrace = f(range_val,a[4:])
##    fft = np.fft.fft(timetrace)
##    res = np.concatenate(timetrace,fft).reshape((timetrace.size,2))
    return timetrace



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



class AI_Channel:
    def __init__(self, ch_name, ch_enabled, ch_range, ch_polarity,ch_resolution = maxInt16):
##            sys.stdout = open("agi_"+str(os.getpid()) + ".txt", "w")
        try:
            self.ch_name_idx = ai_all_channels.index(ch_name)
            self.ch_enabled = ch_enabled      
            self.ch_range_idx = ai_all_ranges.index(ch_range)
            self.ch_polarity_idx = ai_all_polarities.index(ch_polarity)
##                self.conv_func = ai_convertion_functions[self.ch_polarity_idx]
##                self.vect_conv_func = ai_vect_convertion_functions[self.ch_polarity_idx]
        except ValueError as e:
            print(str(e))

    def ai_name(self):
        return ai_all_channels[self.ch_name_idx]

    def ai_is_enabled(self):
        return int(self.ch_enabled)>0
        
    def ai_enabled(self):
        return self.ch_enabled

    def ai_range(self):
        return ai_all_ranges[self.ch_range_idx]

    def ai_polarity(self):
        return ai_all_polarities[self.ch_polarity_idx]

    def from_tuple(tuple):
        return AI_Channel(tuple[0],tuple[1],tuple[2],tuple[3])

    def ai_get_valsIdx(self):
        return [self.ch_name_idx,self.ch_range_idx,self.ch_polarity_idx]

    def ai_get_val_str(self):
        return "name = {0}, en = {1}, rang = {2}, pol = {3}".format(self.ai_name(),self.ai_enabled(),self.ai_range(),self.ai_polarity())

 

class AgilentU2542A:
    def __init__(self,resource):
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(resource, write_termination='\n', read_termination = '\n') #write termination
        self.conversion_header = None
        self.daq_channels = []
##        print(self.daq_idn())
    def daq_idn(self):
        return self.instrument.ask("*IDN?")

##
##      ADC acquisition REGION
##

    ## SET POINTS PER SHOT
    ## SET SAMPLE RATE
    def daq_setup(self, srate,points):
        self.instrument.write("ACQ:SRAT {0}".format(srate))
        self.instrument.write("ACQ:POIN {0}".format(points))
        self.instrument.write("WAV:POIN {0}".format(points))

    ##RESET DEVICE
    def daq_reset(self):
        self.instrument.write("*RST")
        self.instrument.write("*CLS")
    ##ENABLE CHANNELS
    def daq_enable_channels(self, channels):
        self.instrument.write("ROUT:ENAB OFF,(@101:104)")
        self.instrument.write("ROUT:ENAB ON,(@{0})".format( ",".join(channels)))
        self.daq_init_channels()
    ##SET POLARITY FOR CHANNELS
    def daq_setpolarity(self,polarity, channels):
        self.instrument.write("ROUT:CHAN:POL {0}, (@{1})".format(polarity,",".join(channels)))
    ##SET UNIPOLAR TO CHANNELS
    def daq_set_unipolar(self,channels):
        self.daq_setpolarity(Unipolar,channels)
    ##SET BIPOLAR TO CHANNELS
    def daq_set_bipolar(self,channels):
        self.daq_setpolarity(Bipolar,channels)


    def daq_set_range(self,rang,channels):
        self.instrument.write("ROUT:RANG {0}, (@{1})".format(rang,channels))
        
    ##READ PARAMETERS FROM DEVICE AND INITIALIZE SOFTWARE CHANNELS
    def daq_init_channels(self):
        
        channels = "(@101:104)"
        range_response = self.instrument.ask("ROUT:CHAN:RANG? {0}".format(channels))
        polarity_response = self.instrument.ask("ROUT:CHAN:POL? {0}".format(channels))
        enabled_response = self.instrument.ask("ROUT:ENAB? {0}".format(channels))
        channel_range = range_response.split(',')
        channel_polarity = polarity_response.split(',')
        channel_enabled = enabled_response.split(',')
        self.daq_channels = []
        for i in range(4):
            self.daq_channels.append(AI_Channel(ch_name = ai_all_channels[i], ch_enabled=channel_enabled[i],ch_range = channel_range[i],ch_polarity = channel_polarity[i]))
            print(self.daq_channels[i].ai_get_val_str())
        self.enabled_ai_channels = self.daq_get_enabled_channels()
        n_enabled_ch = len(self.enabled_ai_channels)
        arr = np.arange(n_enabled_ch).reshape((n_enabled_ch,1))
        self.conversion_header = np.hstack((arr,np.asarray([ch.ai_get_valsIdx() for ch in self.enabled_ai_channels])))
        print( self.conversion_header )
    ##GET ENABLED CHANNELS
    def daq_get_enabled_channels(self):### list( myBigList[i] for i in [87, 342, 217, 998, 500] )
        result = []
        for ch in self.daq_channels:
            if ch.ai_is_enabled():
                result.append(ch)        
        return result
    ##RUN ACQUISITION
    def daq_run(self):
        self.daq_init_channels()
        self.instrument.write("RUN")

    ##STOP ACQUISITION
    def daq_stop(self):
        self.instrument.write("STOP")
    ##GET ACQUISITION STATUS
    def daq_get_status(self):
        return self.instrument.ask("WAV:STAT?")
    ##CHECK IF DATA IS READY
    def daq_is_data_ready(self):
        r = self.instrument.ask("WAV:STAT?")
        if r== "DATA":
            return True
        elif r == "OVER":
            raise Exception('overload')
        return False
    ##READ RAW DATA
    def daq_read_raw(self):
        self.instrument.write("WAV:DATA?")
        return self.instrument.read_raw()

    ##READ DATA AS FLOAT
    def daq_read_data(self):
        self.instrument.write("WAV:DATA?")
        raw_data = self.instrument.read_raw()
        len_from_header = int(raw_data[2:10])
        data = raw_data[10:]
        enabled_channels = self.enabled_ai_channels
        nchan = len(enabled_channels)
        print("nchan {0}".format(nchan))
        narr = np.fromstring(data, dtype = '<i2')
        print(len(narr))
        single_channel_data_len = int(narr.size/nchan)
        narr = np.hstack((self.conversion_header, narr.reshape((single_channel_data_len,nchan)).transpose()))
        print(len(narr))
        res = np.apply_along_axis(Convertion,1,narr)
##        res_fft = np.apply_along_axis(signal.periodogram,1,narr,fs = 500000)
        return res

##    def daq_single_channel_read_data(self):
##        self.instrument.write("WAV:DATA?")
##        raw_data = self.instrument.read_raw()
##        len_from_header = int(raw_data[2:10])
##        data = raw_data[10:]
####        enabled_channels = self.enabled_ai_channels
####        nchan = len(enabled_channels)
####        print("nchan {0}".format(nchan))
##        narr = np.fromstring(data, dtype = '<i2')
##        print(len(narr))
##        single_channel_data_len = int(narr.size/nchan)
##        narr = np.hstack((self.conversion_header, narr.reshape((single_channel_data_len,nchan)).transpose()))
##        print(len(narr))
##        res = np.apply_along_axis(Convertion,1,narr)
####        res_fft = np.apply_along_axis(signal.periodogram,1,narr,fs = 500000)
##        return res

    def daq_single_shot_read_data(self):
        self.instrument.write("DIG")
        while self.instrument.ask("WAV:COMP?")=="NO":
            pass
        return self.daq_read_data()
        
        
##
##  END ADC acquisition REGION
##

##
##  SET - MEASURE REGION
##    

    def dig_set_direction(self,direction,channels):
        self.instrument.write("CONF:DIG:DIR {0},(@{1})".format(direction, ",".join(channels)))

    def dig_write_channels(self,data,channels):
        self.instrument.write("SOUR:DIG:DATA {0},(@{1})".format(data,",".join(channels)))

    def dig_write_channel(self,data,channel):
        print(data)
        print(channel)
        self.instrument.write("SOUR:DIG:DATA {0},(@{1})".format(data,channel))
                              
    def dig_write_bit_channels(self,value,bit,channels):
        msg =  "SOUR:DIG:DATA:BIT {0}, {1}, (@{2})".format(value,bit,",".join(channels))
        print(msg)
        self.instrument.write(msg)
        
    def dig_write_bit_channel(self,value,bit,channel):
        msg =  "SOUR:DIG:DATA:BIT {0}, {1}, (@{2})".format(value,bit,channel)
        print("writing value {0} to bit{1}".format(value,bit))
        self.instrument.write(msg)

    def adc_set_voltage_range(self,rang,channels):
        self.instrument.write("VOLT:RANG {0}, (@{1})".format(rang,",".join(channels)))

    def adc_set_voltage_polarity(self,pol,channels):
        self.instrument.write("VOLT:POL {0}, (@{1})".format(pol,",".join(channels)))

    def adc_set_voltage_average(self,aver):
        self.instrument.write("VOLT:AVER {0}".format(aver))
    
    def adc_measure(self,channels):
        vals = self.instrument.ask("MEAS? (@{0})".format(",".join(channels))).split(',')
        if len(vals) != len(channels):
            raise Exception("non equal lengths")
        res = { ch: val for ch in channels for val in vals }
        return res

    def dig_measure(self,channels):
        vals = self.instrument.ask("MEAS:DIG? (@{0})".format(",".join(channels))).split(',')
        if len(vals) != len(channels):
            raise Exception("non equal lengths")
        res = {ch: val for ch in channels for val in vals}
        return res

    def dig_bit_measure(self,bit,channels):
        vals = self.instrument.ask("MEAS:DIG:BIT? {0}, (@{1})".format(bit,",".join(channels))).split(',')
        if len(vals) != len(channels):
            raise Exception("non equal lengths")
        res = {ch: val for ch in channels for val in vals}
        return res

    
    def dac_set_output(self, state):
        if state in states:
            self.instrument.write("OUTPUT {0}".format(state))
    
    def dac_source_voltage(self, value, channels):
        self.instrument.write("SOUR:VOLT {0}, (@{1})".format(value,",".join(channels)))

    def dac_set_polarity(self,polarity,channels):
        self.instrument.write("SOUR:VOLT:POL {0}, (@{1})".format(polarity,",".join(channels)))

##
##  END SET - MEASURE REGION
##
    

def main():
        d = AgilentU2542A('ADC')
##        plt.ion()
        try:
            
            counter = 0
            d.daq_reset()
            d.daq_setup(500000,50000)
            d.daq_enable_channels([AI_1,AI_2,AI_3,AI_4])
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
                        print(len(data))
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
            d.daq_reset()
            print("finished")

def proc(q):
    pass

if __name__ == "__main__":


##
##
##
##          USE PIPES!!!
##
##
##

##    q = Queue()
##    p = Process(target = main,args=(q,))
##    p.start()
##    while True:
##        try:
##            print(q.get())
##        except:
##            print("***")
    main()
    os.system("pause")

    
##    import profile
##    profile.run('main()')
   
