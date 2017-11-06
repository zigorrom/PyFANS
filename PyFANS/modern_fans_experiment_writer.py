from os.path import join, isfile
import numpy as np
from measurement_data_structures import MeasurementInfo,generate_measurement_info_filename


class FANSExperimentWriter():
    def __init__(self, working_directory, experiment_name = None, measurement_name = None, measurement_counter = 0):
        self._working_directory = working_directory
        self._experiment_name = experiment_name
        self._measurement_name = measurement_name
        self._measurement_counter = measurement_counter
        self.__experiment_file_extension = "dat"
        self.__measurement_file_extension = "dat"
        self._experiment_file = None
        self._measurement_file = None
        #self._experiment_info_data = np.asarray([
        #    ["U\_sample","V"],
        #    ["Current", "A"],
        #    ["R\_equivalent", "Ohm"],
        #    ["Filename","str"],
        #    ["R\_load","Ohm"],
        #    ["U\_whole","V"],
        #    ["U\_0sample", "V"],
        #    ["U\_0whole","V"],
        #    ["R\-(0sample)","Ohm"],
        #    ["R\-(Esample)","Ohm"],
        #    ["Temperature\-(0)","K"],
        #    ["Temperature\-(E)","K"],
        #    ["k\-(ampl)","int"],
        #    ["N\-(aver)","int"],
        #    ["V\-(0Gate)","V"],
        #    ["V\-(EGate)","V"],
        #    ["Current\_0", "A"],
        #    ]).transpose()
        #self._measurement_info_data = np.asarray([["Frequency","Hz"],["Sv","V2/Hz"]]).transpose()
        #    ]
#       U\-(sample)	Current	R\-(Eq)	Filename	R\-(load)	U\-(Whole)	U\-(0sample)	U\-(0Whole)	R\-(0sample)	R\-(Esample)	Temperature\-(0)	Temperature\-(E)	k\-(ampl)	N\-(aver)	V\-(Gate)
#       V	A	\g(W)		\g(W)	V	V	V	\g(W)	\g(W)	K	K			V

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
        np.savetxt(self._experiment_file,self._experiment_info_data,'%s','\t')

    def _write_measurement_header(self):
        np.savetxt(self._measurement_file,self._measurement_info_data,'%s','\t')
        

    def close_measurement(self):
        if self._measurement_file and not self._measurement_file.closed:
            self._measurement_file.close()


    def write_measurement_info(self,info):
        assert isinstance(info, MeasurementInfo)
        assert self._experiment_file, "Experiment was not properly initialized"
        #if not self._experiment_file:
        #    return 

        if isinstance(info, MeasurementInfo):
            data_list = [info.end_sample_voltage,
                         info.sample_current_end, 
                         info.equivalent_resistance_end, 
                         generate_measurement_info_filename(info.measurement_filename, info.measurement_count,info._measurement_file_extension),
                         info._load_resistance,
                         info.end_main_voltage,
                         info.start_sample_voltage,
                         info.start_main_voltage,
                         info.sample_resistance_start,
                         info.sample_resistance_end,
                         info.start_temperature,
                         info.end_temperature,
                         info.second_amplifier_gain,
                         None,
                         info.start_gate_voltage,
                         info.end_gate_voltage,
                         info.sample_current_start
                         ]
            representation = "\t".join(map(str,data_list)) + '\n'
            

            self._experiment_file.write(representation.encode())
            self._experiment_file.flush()

    def write_measurement(self,data):
        if self._measurement_file:
            np.savetxt(self._measurement_file,data,delimiter='\t')

    def write_noise_spectrum(self, data):
        if self._measurement_file:
            np.savetxt(self._measurement_file,data,delimiter='\t')

    



    
    

if __name__=="__main__":
   w = ExperimentWriter("D:\\Testdata")
   w.open_experiment("test_exp")
   for i in range(10):
       w.open_measurement("meas".format(i),i)
       w.write_measurement([1,2,3,4,5])
       w.close_measurement()
   w.close_experiment()