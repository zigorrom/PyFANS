from datetime import timedelta
#import pandas as pd
import numpy as np
from numpy.random import randn

from os.path import isfile, join
from os import getcwd


class NoiseExperimentWriter:
    def __init__(self, working_folder = "", use_next_available_name = True, noise_buffer_size = -1, timetrace_buffer_size = -1):
        self._workingFolder = working_folder
        if not working_folder:
            self._workingFolder = getcwd()
        
        print(self.working_directory)

        self._noise_buffer_size = noise_buffer_size
        self._timetrace_buffer_size = timetrace_buffer_size

        self._measurement_file_extention = "dat"
        self._measurement_file_postfix = "meas"

        self._timetrace_file_extention = "dat"
        self._timetrace_file_postfix = "timetrace"

        self._noise_file_extention = "dat"
        self._noise_file_postifix = "noise"

        self._measurement_data_file = None
        self._timetrace_file = None
        self._noise_file = None

        self._use_next_available_name = use_next_available_name
    
    #def __enter__(self):
    #    pass
        
    #def __exit__(self, type, value, traceback):
    #    self.close_experiment()

    @property
    def use_next_available_filename(self):
        return self._use_next_available_name

    @use_next_available_filename.setter
    def use_next_available_filename(self,value):
        self._use_next_available_name = value


    @property
    def working_directory(self):
        return self._workingFolder

    @working_directory.setter
    def working_directory(self,value):
        self._workingFolder = value

    @property
    def experiment_opened(self):
        return not self._measurement_data_file.closed

    @property
    def measurement_opened(self):
        return not (self._noise_file.closed or self._timetrace_file.closed)

    def _generate_filename(self, path, name, postfix,extention):
        return join(path, "{0}_{1}.{2}".format(name,postfix,extention))

    def open_experiment(self, experiment_name):
        dir = self.working_directory
        meas_fname = self._generate_filename(dir, experiment_name, self._measurement_file_postfix, self._measurement_file_extention)
        self._measurement_data_file = open(meas_fname,"ab")

    def close_experiment(self):
        self.close_measurement()
        if not self._measurement_data_file.closed:
            self._measurement_data_file.close()
    


    def __get_next_available_name(self,path, measurement_name, postfix,extention):
        fname = self._generate_filename(path, measurement_name, postfix, extention)
        counter = 0
        while isfile(fname):
            fname = self._generate_filename(path,"{0}_{1}".format(measurement_name,counter), postfix,extention)
            counter += 1
        return fname


    def open_measurement(self, measurement_name, async_writing = False, *args,**kwargs):
        dir = self.working_directory
        noise_fname = self._generate_filename(dir, measurement_name, self._noise_file_postifix,self._noise_file_extention)
        timetrace_fname = self._generate_filename(dir, measurement_name, self._timetrace_file_postfix, self._timetrace_file_extention)
        if self.use_next_available_filename:
            noise_fname = self.__get_next_available_name(dir, measurement_name, self._noise_file_postifix, self._noise_file_extention)
            timetrace_fname = self.__get_next_available_name(dir, measurement_name, self._timetrace_file_postfix, self._timetrace_file_extention)
        else:
            if isfile(noise_fname):
                raise FileExistsError("File already exists: {0}".format(noise_fname))
            if isfile(timetrace_fname):
                raise FileExistsError("File already exists: {0}".format(timetrace_fname))

        self._noise_file = open(noise_fname, "ab",buffering = self._noise_buffer_size)
        self._timetrace_file = open(timetrace_fname, "ab", buffering = self._timetrace_buffer_size)
        self.__write_measurement_data(measurement_name, *args,**kwargs)
        #if async_writing:
        #    self._


    def close_measurement(self):
        if not self._noise_file.closed:
            self._noise_file.close()

        if not self._timetrace_file.closed:
            self._timetrace_file.close()


    
    def __write_measurement_data(self,measurement_name, *args,**kwargs):
        self._measurement_data_file.write("filename: {0}\n".format(  measurement_name).encode('ascii'))
        #print("filename: {0}\n".format(  measurement_name), file= self._measurement_data_file)

        #self._measurement_data_file.write("filename: {0}\n".format(  measurement_name))

    def write_timetrace_data(self,timetrace):
        shape = np.shape(timetrace)
        if len(shape) != 2:
            raise ValueError("Timetrace should be a time - value pair")

        l, pair = shape
        if pair != 2:
            raise ValueError("Timetrace should be a time - value pair")
        #print(timetrace)
        np.savetxt(self._timetrace_file, timetrace)

    def write_timetrace_async(self,timetrace):
        pass


    def write_noise_data(self, noise):
        shape = np.shape(noise)
        if len(shape) != 2:
            raise ValueError("Noise should be a frequency - value pair")

        l, pair = shape
        if pair != 2:
            raise ValueError("Noise should be a noise - value pair")
        #print(noise)
        np.savetxt(self._noise_file, noise)
    
    def write_noise_async(self, noise):
        pass


def main():
    
    
    writer = NoiseExperimentWriter("F:\\TestData")
    writer.open_experiment("experiment")
    
    for n_meas in range(10):
        writer.open_measurement("meas_{0}".format(n_meas),"asdasdad", petro = "asdasd")
        for x in range(10):
            writer.write_timetrace_data(np.ones((100,2),dtype = np.float))
            writer.write_noise_data(np.ones((100,2), dtype = np.float))
        
    writer.close_experiment()

    
    



    #store = pd.HDFStore("store.h5")
    #print(store)
    
    ##del store['df']
    ##del store['s']
    ##del store['wp']
    #np.random.seed(1234)
    #times = 10
    #index = pd.date_range('1/1/2000', periods=times)
    ##df = pd.DataFrame(index=index,columns=['amplitude'])
    
    #nsamples = 50000
    #period = 1 #sec
    #current_time = 0
    #df = pd.DataFrame()
    
    #for i in range(times):
    #    arr = np.random.random(nsamples)
    #    times = np.linspace(current_time, current_time+period, nsamples, False)

    #    ser = pd.Series(data=arr,index=times)
    #    df.append(ser,ignore_index=True)

    #    current_time+=period
        
    #print(df)
    
    ##store['df'] = df
    
    
    
    

    
    #dftd = pd.DataFrame(dict(A = pd.Timestamp('20130101'), B = [ pd.Timestamp('20130101') + timedelta(days=i,seconds=10) for i in range(10) ]))

    #dftd['C'] = dftd['A']-dftd['B']

    #print(dftd)

    #store.append('dftd',dftd,data_columns=True)

    #print(store.select('dftd',"C<'-3.5D'"))
    #print(store)
    #store.close()

if __name__ == "__main__":
    main()