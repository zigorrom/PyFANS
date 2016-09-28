import visa
import numpy as np
import time
import os
import sys
import timeit
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
    maxInt16div2 = 32768
    def BipolarConversionFunction(range_value, data_code):
        return (data_code*range_value)/ConvertionFunction.maxInt16div2

    def UnipolarConversionFunction(range_value, data_code):
        return (data_code/ConvertionFunction.maxInt16+0.5)*range_value

class AI_Channel:
        def __init__(self, ch_name, ch_enabled, ch_range, ch_polarity,ch_resolution = ConvertionFunction.maxInt16):
##            sys.stdout = open("agi_"+str(os.getpid()) + ".txt", "w")
            self.name = ch_name
            self.enabled = ch_enabled
            self.range = ch_range
            self.fRange = float(self.range)
            self.polarity = ch_polarity
            if self.polarity == Polarity.Unipolar:
                self.cf = ConvertionFunction.UnipolarConversionFunction
            elif self.polarity == Polarity.Bipolar:
                self.cf = ConvertionFunction.BipolarConversionFunction
##            self.vcf = np.vectorize(self.ai_convertion_function,otypes=[np.float])
            self.vcf = np.vectorize(self.cf,otypes=[np.float])

        def ai_is_enabled(self):
            return int(self.enabled)>0

        def ai_enabled(self):
            return self.enabled

        def ai_range(self):
            return self.range

        def ai_polarity(self):
            return self.polarity

        def from_tuple(tuple):
            return AI_Channel(tuple[0],tuple[1],tuple[2],tuple[3])

        def ai_get_val_tuple(self):
            return (self.name,self.enabled,self.range,self.polarity,)

        def ai_get_val_str(self):
            return "name = {n}, en = {0}, rang = {1}, pol = {2}".format(self.enabled,self.range,self.polarity,n = self.name)

        def ai_convertion_function(self,int16_value):
            return self.cf(self.fRange, int16_value)

        def ai_vect_cf(self,int16_value):
            return self.vcf(int16_value)

        def ai_get_cf_parans(self):
            return (self.fRange, self.vcf)

        



class AgilentU2542A:
    def __init__(self,resource):
        rm = visa.ResourceManager()
        self.instrument = rm.open_resource(resource, write_termination='\n', read_termination = '\n') #write termination

    def daq_idn(self):
        return self.instrument.ask("*IDN?")


    def daq_setup(self, srate,points):
        self.instrument.write("ACQ:SRAT {0}".format(srate))
        self.instrument.write("WAV:POIN {0}".format(points))

    def daq_reset(self):
        self.instrument.write("*RST")
        self.instrument.write("*CLS")

    def daq_enable_channels(self, channels):
        self.instrument.write("ROUT:ENAB OFF,(@101:104)")
        self.instrument.write("ROUT:ENAB ON,(@{0})".format( ",".join(channels)))
        self.daq_init_channels()

    def daq_setpolarity(self,polarity, channels):
        self.instrument.write("ROUT:CHAN:POL {0}, (@{1})".format(polarity,",".join(channels)))

    def daq_set_unipolar(self,channels):
        self.daq_setpolarity(Polarity.Unipolar,channels)

    def daq_set_bipolar(self,channels):
        self.daq_setpolarity(Polarity.Bipolar,channels)

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
            print(self.daq_channels[i].ai_get_val_str())
        self.enabled_ai_channels = self.daq_get_enabled_channels()

    def daq_get_enabled_channels(self):
        result = []
        for ch in self.daq_channels:
            if ch.ai_is_enabled():
                result.append(ch)
        return result

    def daq_run(self):
        self.daq_init_channels()
        self.instrument.write("RUN")


    def daq_stop(self):
        self.instrument.write("STOP")

    def daq_get_status(self):
        return self.instrument.ask("WAV:STAT?")

    def daq_is_data_ready(self):
        r = self.daq_get_status()
##        print(r)
        if r== "DATA":
            return True
        elif r == "OVER":
            raise Exception('overload')
        return False

    def daq_read_raw(self):
        self.instrument.write("WAV:DATA?")
        return self.instrument.read_raw()

    def daq_read_binary(self):
        pass

    def daq_read_data(self):
        self.instrument.write("WAV:DATA?")
        raw_data = self.instrument.read_raw()
        len_from_header = int(raw_data[2:10])
        data = raw_data[10:]
        enabled_channels = self.enabled_ai_channels#self.daq_get_enabled_channels()
        nchan = len(enabled_channels)
        narr = np.fromstring(data, dtype = '<i2') #np.uint16)     #np.uint16)'<u2'
        data_len = narr.size
        single_channel_data_len = int(data_len/nchan)
##        print("sc data len:{0}".format(single_channel_data_len))
        package = []
        counter = 0
        

##https://wiki.python.org/moin/PythonSpeed/PerformanceTips
        chan_desc = [c.ai_get_val_tuple() for c in enabled_channels]
        func_arr = [c.ai_get_cf_parans() for c in enabled_channels]
        
        for ch in range(nchan):
            arr = narr[ch::nchan]
        package.append((chan_desc[ch],func_arr[ch][1](func_arr[ch][0],narr),))
        package.append((chan_desc[0],func_arr[0][1](func_arr[0][0],narr),))
        return package
##        return narr

    





if __name__ == "__main__":

    def main():
        d = AgilentU2542A('ADC')  
        try:
            
            counter = 0
            d.daq_reset()
            d.daq_setup(500000,50000)
            d.daq_enable_channels([AI_Channels.AI_1,AI_Channels.AI_2,AI_Channels.AI_3,AI_Channels.AI_4])
            d.daq_run()
            print("started")
            init_time = time.time()
            max_count = 1000
            while counter < max_count:
                try:
                    if d.daq_is_data_ready():

                        counter += 1
                        t = time.time()-init_time

                        data = d.daq_read_data()
                        print(t)

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

    main()
##    import profile
##    profile.run('main()')
   



















##    d.daq_enable_channels([AI_Channels.AI_1,AI_Channels.AI_2,AI_Channels.AI_4])
####    print(d.daq_get_enabled_channels())
##
##    print(d.daq_parse_raw('#800000006\xeb\xff\xea\xff\xeb\xff'))
##    f = ConvertionFunction.UnipolarConversionFunction
##    print("convertion value {0}".format(f(10,56000)))
##    print(ConvertionFunction.maxInt16)
####    d.daq_init_channels()
##    en = d.daq_get_enabled_channels()
##    print(en[0].ai_convertion_function(43971))
####    ai = AI_Channel(



















