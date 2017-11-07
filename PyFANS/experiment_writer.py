from os.path import join, isfile

import numpy as np
from measurement_data_structures import MeasurementInfo,generate_measurement_info_filename


class ExperimentWriter():
    def __init__(self, working_directory, experiment_name = None, measurement_name = None, measurement_counter = 0):
        self._working_directory = working_directory
        self._experiment_name = experiment_name
        self._measurement_name = measurement_name
        self._measurement_counter = measurement_counter
        self.__experiment_file_extension = "dat"
        self.__measurement_file_extension = "dat"

        self._experiment_file = None
        self._measurement_file = None
       
        
        self._experiment_header = "\t".join(list(map(str,MeasurementInfo.header_options())))
        self._measurement_header = "Frequency, f(Hz)\tSv (V2/Hz)"

    @property
    def working_directory(self):
        return self._working_directory

    @working_directory.setter
    def working_directory(self,value):
        self._working_directory = value

    def open_experiment(self, experiment_name):
        if self._experiment_file: 
            self.close_experiment()
        
        file_exists = False
        self._experiment_name = experiment_name
        filepath = join(self._working_directory, "{0}.{1}".format(self._experiment_name,self.__experiment_file_extension))
        file_exists = isfile(filepath)
        self._experiment_file = open(filepath, 'ab')
        
        if not file_exists:
            self._write_experiment_header()


    def close_experiment(self):
        if self._experiment_file and not self._experiment_file.closed:
            self._experiment_file.close()
            


    def open_measurement(self, measurement_name, measurement_counter):
        if self._measurement_file:
            self.close_measurement()

        self._measurement_name = measurement_name
        self._measurement_counter = measurement_counter
        filepath = join(self._working_directory, generate_measurement_info_filename(self._measurement_name,self._measurement_counter, self.__measurement_file_extension))
        self._measurement_file = open(filepath,"wb")
        self._write_measurement_header()
        

    def _write_experiment_header(self):
        self._experiment_file.write(self._experiment_header.encode())
        #np.savetxt(self._experiment_file,self._experiment_header,'%s','\t')

    def _write_measurement_header(self):
        self._measurement_file.write(self._measurement_header.encode())
        #np.savetxt(self._measurement_file,self._measurement_header,'%s','\t')
        

    def close_measurement(self):
        if self._measurement_file and not self._measurement_file.closed:
            self._measurement_file.close()

    def write_measurement_info(self,info):
        if not self._experiment_file:
            return 

        if isinstance(info, MeasurementInfo):
            data_dict = info.to_dict()
            datalist = (data_dict[opt] for opt in MeasurementInfo.header_options())
            representation = "\t".join(map(str,data_list)) + '\n'
            self._experiment_file.write(representation.encode())
            self._experiment_file.flush()

    def write_measurement(self,data):
        if self._measurement_file:
            np.savetxt(self._measurement_file,data,delimiter='\t')

    



class TestClass(dict):
    def __init__(self):
        super().__init__()
    
    
    

if __name__=="__main__":
   w = ExperimentWriter("D:\\Testdata")
   w.open_experiment("test_exp")
   for i in range(10):
       w.open_measurement("meas".format(i),i)
       w.write_measurement([1,2,3,4,5])
       w.close_measurement()
   w.close_experiment()