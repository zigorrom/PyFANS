from os.path import join, isfile
import numpy as np
from measurement_data_structures import MeasurementInfo,generate_measurement_info_filename
import experiment_writer as expw

def generate_timetrace_measurement_filename(measurement_name, measurement_count, file_extension = "dat"):
    return "{0}_{1}_timetrace.{2}".format(measurement_name,measurement_count, file_extension)

class FANSExperimentWriter(expw.ExperimentWriter):
    def __init__(self, working_directory, experiment_name = None, measurement_name = None, measurement_counter = 0, sample_rate = 500000):
        super().__init__(working_directory, experiment_name, measurement_name, measurement_counter)
        
        #self.__experiment_file_extension = "dat"
        #self.__measurement_file_extension = "dat"
        self.__sample_rate = sample_rate
        self.__timetrace_measurement_file_extension = "dat"

        self._timetrace_measurement_file = None

        self._timetrace_header = "Fs={0}".format(sample_rate)
        
    
    def open_measurement(self, measurement_name, measurement_counter):
        super().open_measurement(measurement_name, measurement_counter)
        filepath = join(self.working_directory, generate_timetrace_measurement_filename(measurement_name,measurement_counter, self.__timetrace_measurement_file_extension))
        self._timetrace_measurement_file = open(filepath, "wb")
        self._timetrace_measurement_file.write(self._timetrace_header.encode())

    def close_measurement(self):
        super().close_measurement()
        if self._timetrace_measurement_file and not self._timetrace_measurement_file.closed:
            self._timetrace_measurement_file.close()

    def write_noise_spectrum(self, data):
        super().write_measurement(data)

    def write_timetrace_data(self, data):
        if self._timetrace_measurement_file:
            np.savetxt(self._timetrace_measurement_file, data, delimiter = "\t")
    



    
    

if __name__=="__main__":
   w = FANSExperimentWriter("D:\\Testdata",sample_rate = 500000)
   w.open_experiment("test_exp")
   for i in range(10):
       w.open_measurement("meas".format(i),i)
       w.write_measurement([1,2,3,4,5])
       w.write_timetrace_data(())
       w.close_measurement()
   w.close_experiment()