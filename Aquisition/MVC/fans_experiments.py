import os
import numpy as np
from node_configuration import Configuration
from fans_controller import FANS_controller
from fans_smu import fans_smu
import math
from PyQt4 import QtCore
from flask import Flask
from flask.views import MethodView

class fans_fet_noise_experiment:
    def __init__(self, fans_controller, fans_smu, configuration):
        self._fans_controller = fans_controller
        self._fans_smu = fans_smu
        self._configuration = configuration
        self._filename = "unnamed"
        self._experiment_data_filename = "MeasurData"
        self._file_extention = ".dat"
        self._working_directory = os.getcwd()

        self.initialize_experiment()


    def initialize_experiment(self):
        pass

    def start_experiment(self):
        pass

    def stop_experiment(self):
        pass

    def set_drain_source_voltage_range(self):
        pass

    def set_gate_voltage_range(self):
        pass

    def set_filename(self, filename):
        self._filename = filename

    def set_working_directory(self, working_directory):
        self._working_directory = working_directory

    def set_sample_rate(self,sample_rate):
        pass

    def set_points_per_shot(self, points_per_shot):
        pass

    




RANGE_HANDLERS = ["normal","back_forth","zero_start","zero_start_back_forth"]
NORMAL_RANGE_HANDLER, BACK_FORTH_RANGE_HANDLER, ZERO_START_RANGE_HANDLER, ZERO_START_BACK_FORTH = RANGE_HANDLERS

class fans_range(object):
    def __init__(self,start, stop, len = -1, handler = NORMAL_RANGE_HANDLER):
        self._start = start
        self._stop = stop
        self._step = step
        self._direction = 1 if stop > start else -1


        self.__min_value = self._start
        self.__max_value = self._stop
        self.start_index = 0

        if self._start > self._stop:
            self.__min_value = self._stop
            self.__max_value = self._start
            self.start_index = -1

        self.__values = np.linspace(self._start,self._stop,len,endpoint= True, retstep = True)
        
        self.current_idx = 0

        if handler == NORMAL_RANGE_HANDLER:
            pass
        elif handler == BACK_FORTH_RANGE_HANDLER:
            pass
        elif handler == ZERO_START_RANGE_HANDLER:
            pass
        elif handler == ZERO_START_BACK_FORTH:
            pass
        
        #self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.high:
            raise StopIteration
        else:
            self.current += 1
            return self.current
    







class TestClass():
    def __init__(self):
        self.value = "Hello world"

    def get_value(self):
        return self.value

    

class UserAPI(MethodView):
    def __init__(self, test_value):
        self.test = test_value
    
    def get(self):
        return self.test.value

       




if __name__ == "__main__":
    #cfg = Configuration()
    #f = FANS_controller("ADC",configuration=cfg)
    #smu = fans_smu(f)
    #exp = fans_fet_noise_experiment(f,smu,cfg)

    #rng = fans_range(-2,2,0.002)
    
    #l1 = np.linspace(0,0,200)
    #print(l1)

    #l1 = np.linspace(2,-1,10)
    #print(l1)

    #l1 = np.linspace(0,2,0.35)
    #print(l1)


    #t = TestClass()
    #uapi = UserAPI(t)
    #app = Flask(__name__)
    #app.add_url_rule('/users/', view_func=uapi.as_view('users'))
    #app.run()
 