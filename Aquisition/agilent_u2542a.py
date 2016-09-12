import visa
import numpy as np
import time
from math import pow

class AI_Channels:
    all_channels = ['101','102','103','104']
    AI_1,AI_2, AI_3, AI_4 = all_channels 

class AO_Channels:
    all_channels = ['201','202']
    AO_1,AO_2 = all_channels 

class Polarity:
    all_polarities = ['BIP','UNIP']
    Bipolar,Unipolar = all_polarities

class Range:
    all_ranges = ['10','5','2.5','1.25']
    Range_10, Range_5, Range_2_5,Range_1_25 = all_ranges

class ConvertionFunction:
    maxInt16 = 65536
    def BipolarConversionFunction(range_value, data_code):
        return (2*data_code*range_value)/ConvertionFunction.maxInt16
        
    def UnipolarConversionFunction(range_value, data_code):
        return (data_code/ConvertionFunction.maxInt16+0.5)*range_value

class AI_Channel:
        def __init__(self, ch_name, ch_enabled, ch_range, ch_polarity,ch_resolution = ConvertionFunction.maxInt16):
            self.name = ch_name
            self.enabled = ch_enabled
            self.range = ch_range
            self.polarity = ch_polarity
            

        def ai_get_val_str(self):
            return "name = {n}, en = {0}, rang = {1}, pol = {2}".format(self.enabled,self.range,self.polarity,n = self.name)

        def ai_convertion_function(self,int16_value):
            

        


class AgilentU2542A:
    def __init__(self,resource):
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(resource, write_termination='\n', read_termination = '\n') #write termination
        
        self.daq_channels_enabled = []
        self.daq_init_channel_enabled()
        self.daq_channel_polarities = []
        self.daq_init_polarities()
        self.daq_channel_ranges = []
        self.daq_init_ranges()

    def daq_init_channels(self):
        self.daq_channels = []
        channels = "(@101:104)"
        range_response = self.instrument.ask("ROUT:CHAN:RANG? {0}".format(channels))
        polarity_response = self.instrument.ask("ROUT:CHAN:POL? {0}".format(channels))
        enabled_response = self.instrument.ask("ROUT:ENAB? {0}".format(channels))
        channel_range = range_response.split(',')
        channel_polarity = polarity_response.split(',')
        channel_enabled = enabled_response.split(',')
        for i in range(4):
            self.daq_channels.append(AI_Channel(ch_name = AI_Channels.all_channels[i], ch_enabled=channel_enabled[i],ch_range = channel_range[i],ch_polarity = channel_polarity[i]))
##            print(self.daq_channels[i].ai_get_val_str())

    def daq_idn(self):
        return self.instrument.ask("*IDN?")
    
    
    def daq_setup(self, srate,points):
        self.instrument.write("ACQ:SRAT {0}".format(srate))
        self.instrument.write("WAV:POIN {0}".format(points))

    def daq_reset(self):
        self.instrument.write("*RST")
        self.instrument.write("*CLS")

    def daq_get_enabled_channels(self):
        return self.daq_channels_enabled

    def daq_init_polarities(self):
        pass
            
        
    
    def daq_enable_channels(self, channels):
        self.instrument.write("ROUT:ENAB OFF,(@101:104)")
        self.instrument.write("ROUT:ENAB ON,(@{0})".format( ",".join(channels)))
        self.daq_init_channel_enabled()
    
    def daq_init_channel_enabled(self):
        r = self.instrument.ask("ROUT:ENAB? (@101:104)")
        self.daq_channels_enabled[:]=[]
        a = r.split(',')
        for i in range(len(a)):
            if int(a[i])>0:
                self.daq_channels_enabled.append(AI_Channels.all_channels[i])
        return self.daq_channels_enabled

    def daq_init_ranges(self):
        pass
        
   
    def daq_run(self):
        self.daq_init_channel_enabled()
        self.instrument.write("RUN")


    def daq_stop(self):
        self.instrument.write("STOP")
        
    def daq_get_status(self):
        return self.instrument.ask("WAV:STAT?")

    def daq_is_data_ready(self):
        r = self.daq_get_status()
        if r== "DATA":
            return True
        return False

    def daq_read_raw(self):
        self.instrument.write("WAV:DATA?")
        return self.instrument.read_raw()
    
    def daq_parse_raw(self, raw_data):
        len_from_header = int(raw_data[2:10])
        data = raw_data[10:]
        nchan = len(self.daq_channels_enabled)
        narr = np.fromstring(data, dtype = np.uint16)
        package = []
        for ch in range(nchan):
            package.append((AI_Channels.all_channels[ch],narr[ch::nchan],))
        return package

    
    def daq_read_data(self):
        raw = self.daq_read_raw()
        package = self.daq_parse_raw(raw)
        return package
        
    



if __name__ == "__main__":
    d = AgilentU2542A('ADC')
    
    d.daq_enable_channels([AI_Channels.AI_1,AI_Channels.AI_2,AI_Channels.AI_4])
    print(d.daq_get_enabled_channels())
    print(repr(d.daq_init_channel_enabled()))
    print(d.daq_parse_raw('#800000006\xeb\xff\xea\xff\xeb\xff'))
    t = ('asd','sgreg',)
    f = ConvertionFunction.UnipolarConversionFunction
    print("convertion value {0}".format(f(10,56000)))
    print(ConvertionFunction.maxInt16)
    d.daq_init_channels()










































        

##print(AI_Channels.AI_1)



    
##    def daq_run(self):
##        self.instrument.write("RUN")
##        
##        counter = 0
##        data = ""
##        maxCount= 100
##        maxCountOne = maxCount+1
##        while counter <maxCountOne:
##            if counter == maxCount:
##                self.instrument.write("STOP")
##                print("stopping")
##                 
##            r = self.instrument.ask("WAV:STAT?")
##            if r == "DATA":
##                print(r)
##                self.instrument.write("WAV:DATA?")
##                data = self.instrument.read_raw()
##                print("counter = {}".format(counter))
##                print(data[:10])
##                counter += 1
##
##       
##        print("stopped")

##print (__name__)
##        
##if __name__ == '__main__':
##    agi = AgilentU2542A('ADC')
##    print(agi.daq_enable_channels([AI_Channels.AI_1,AI_Channels.AI_2]))
##    print(agi.instr())
##    counter = 0
##    agi.daq_setup(500000,50000)
##    agi.daq_run()
##    while counter<100:
##        if agi.daq_is_data_ready():
##            data = agi.daq_read_raw()[:10]
##            print(data)
##            counter += 1
##    agi.daq_stop()
    
   
