import os
import pickle
import pandas as pd



class MeasurementInfo(object):
    DRAIN_SOURCE_VOLTAGE_START_OPTION = "Vds (start)"
    DRAIN_SOURCE_VOLTAGE_END_OPTION = "Vds (end)"

    MAIN_VOLTAGE_START_OPTION = "Vmain (start)"
    MAIN_VOLTAGE_END_OPTION = "Vmain (end)"

    GATE_VOLTAGE_START_OPTION = "Vgate (start)"
    GATE_VOLTAGE_END_OPTION = "Vgate (end)"

    DRAIN_CURRENT_START_OPTION = "Id (start)"
    DRAIN_CURRENT_END_OPTION = "Id (end)"

    EQUIVALENT_RESISTANCE_START_OPTION = "Req (start)"
    EQUIVALENT_RESISTANCE_END_OPTION = "Req (end)"

    FILENAME_OPTION = "Filename"
    LOAD_RESISTANCE_OPTION = "Rload"

    SAMPLE_RESISTANCE_START_OPTION = "Rs (start)"
    SAMPLE_RESISTANCE_END_OPTION = "Rs (end)"

    TEMPERATURE_START_OPTION = "T (start)"
    TEMPERATURE_END_OPTION = "T (end)"

    AMPLIFICATION_OPTION = "Kampl"
    AVERAGING_OPTION = "Naver"

    def __init__(self, **kwargs):
        self._measurement_data_dictionary = kwargs
        # self._drain_source_voltage_start = kwargs.get(self.DRAIN_SOURCE_VOLTAGE_START_OPTION, None)
        # self._drain_source_voltage_end = kwargs.get(self.DRAIN_SOURCE_VOLTAGE_END_OPTION, None)

        # self._main_voltage_start = kwargs.get(self.MAIN_VOLTAGE_START_OPTION, None)
        # self._main_voltage_end = kwargs.get(self.MAIN_VOLTAGE_END_OPTION, None)

        # self._gate_voltage_start = kwargs.get(self.GATE_VOLTAGE_START_OPTION, None)
        # self._gate_voltage_end = kwargs.get(self.GATE_VOLTAGE_END_OPTION, None)

        # self._drain_current_start = kwargs.get(self.DRAIN_CURRENT_START_OPTION, None)
        # self._drain_current_end = kwargs.get(self.DRAIN_CURRENT_END_OPTION, None)

        # self._equivalent_resistance_start = kwargs.get(self.EQUIVALENT_RESISTANCE_START_OPTION, None)
        # self._equivalent_resistance_end = kwargs.get(self.EQUIVALENT_RESISTANCE_END_OPTION, None)

        # self._measurement_filename = kwargs.get(self.FILENAME_OPTION, "")
        # self._load_resistance = kwargs.get(self.LOAD_RESISTANCE_OPTION, None)

        # self._sample_resistance_start = kwargs.get(self.SAMPLE_RESISTANCE_START_OPTION, None)
        # self._sample_resistance_end = kwargs.get(self.SAMPLE_RESISTANCE_END_OPTION, None)

        # self._temperature_start = kwargs.get(self.TEMPERATURE_START_OPTION, None)
        # self._temperature_end = kwargs.get(self.TEMPERATURE_END_OPTION, None)

        # self._amplification = kwargs.get(self.AMPLIFICATION_OPTION, None)
        # self._averaging = kwargs.get(self.AVERAGING_OPTION, None)

        # print(kwargs)

    @property
    def drain_source_voltage_start(self):
        return self._measurement_data_dictionary.get(self.DRAIN_SOURCE_VOLTAGE_START_OPTION, None)
        # return self._drain_source_voltage_start
    
    @property
    def drain_source_voltage_end(self):
        return self._measurement_data_dictionary.get(self.DRAIN_SOURCE_VOLTAGE_END_OPTION, None)
        # return self._drain_source_voltage_end

    @property
    def main_voltage_start(self):
        return self._measurement_data_dictionary.get(self.MAIN_VOLTAGE_START_OPTION, None)
        # return self._main_voltage_start

    @property
    def main_voltage_end(self):
        return self._measurement_data_dictionary.get(self.MAIN_VOLTAGE_END_OPTION, None)
        # return self._main_voltage_end

    @property
    def gate_voltage_start(self):
        return self._measurement_data_dictionary.get(self.GATE_VOLTAGE_START_OPTION, None)
        # return self._gate_voltage_start

    @property
    def gate_voltage_end(self):
        return self._measurement_data_dictionary.get(self.GATE_VOLTAGE_END_OPTION, None)
        # return self._gate_voltage_end

    @property
    def drain_current_start(self):
        return self._measurement_data_dictionary.get(self.DRAIN_CURRENT_START_OPTION, None)
        # return self._drain_current_start
    
    @property
    def drain_current_end(self):
        return self._measurement_data_dictionary.get(self.DRAIN_CURRENT_END_OPTION, None)
        # return self._drain_current_end

    @property
    def equivalent_resistance_start(self):
        return self._measurement_data_dictionary.get(self.EQUIVALENT_RESISTANCE_START_OPTION, None)
        # return self._equivalent_resistance_start

    @property
    def equivalent_resistance_end(self):
        return self._measurement_data_dictionary.get(self.EQUIVALENT_RESISTANCE_END_OPTION, None)
        # return self._equivalent_resistance_end

    @property
    def measurement_filename(self):
        return self._measurement_data_dictionary.get(self.FILENAME_OPTION, "")
        # return self._measurement_filename
    
    @property
    def load_resistance(self):
        return self._measurement_data_dictionary.get(self.LOAD_RESISTANCE_OPTION, None)
        # return self._load_resistance

    @property
    def sample_resistance_start(self):
        return self._measurement_data_dictionary.get(self.SAMPLE_RESISTANCE_START_OPTION, None)
        # return self._sample_resistance_start
    
    @property
    def sample_resistance_end(self):
        return self._measurement_data_dictionary.get(self.SAMPLE_RESISTANCE_END_OPTION, None)
        # return self._sample_resistance_end

    @property
    def temperature_start(self):
        return self._measurement_data_dictionary.get(self.TEMPERATURE_START_OPTION, None)
        # return self._temperature_start

    @property
    def temperature_end(self):
        return self._measurement_data_dictionary.get(self.TEMPERATURE_END_OPTION, None)
        # return self._temperature_end

    @property
    def amplification(self):
        return self._measurement_data_dictionary.get(self.AMPLIFICATION_OPTION, None)
        # return self._amplification

    @property
    def averaging(self):
        return self._measurement_data_dictionary.get(self.AVERAGING_OPTION, None)
        # return self._averaging
    
    def __str__(self):
        return str(self._measurement_data_dictionary)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return self._measurement_data_dictionary.get(key)

    def __setitem__(self, key, item):
        self._measurement_data_dictionary[key] = item
    
    def as_dict(self):
        return self._measurement_data_dictionary


class MeasurementInfoFile(object):
    def __init__(self, measurement_info_filename):
        if not os.path.isfile(measurement_info_filename):
            raise FileExistsError()
        
        self._measurement_info_filename = measurement_info_filename
        self._measurement_info = pd.read_csv(measurement_info_filename, delimiter="\t", index_col=None ) #header=[0,1]
        self._noise_params = dict()
        filepath, basename = os.path.split(measurement_info_filename)
        filename, extension = os.path.splitext(basename)
        noise_params_filename = os.path.join(filepath, filename + ".npar")
        self._noise_params_filename = noise_params_filename
        self.loadNoiseParams(noise_params_filename)

        self.reset()

    def loadNoiseParams(self, noise_params_filename):
        if os.path.isfile(noise_params_filename):
            try:
                with open(noise_params_filename, "rb") as file:
                    self._noise_params = pickle.load(file)
            except Exception as e:
                print("exception while loading pickled data")
    #def __del__(self):
    #    self.saveNoiseParams()

    def saveNoiseParams(self):
        if self._noise_params_filename and self._noise_params:
            with open(self._noise_params_filename, "wb") as file:
                pickle.dump(self._noise_params, file)

    
    @property
    def columns(self):
        return list(self._measurement_info)

    @property
    def row_count(self):
        return len(self._measurement_info)
    
    def reset(self):
        self._current_row = 0

    def next_row(self):
        self._current_row += 1
        if self._current_row > (self.row_count - 1):
            self._current_row = self.row_count - 1
        return self.current_measurement_info

    def prev_row(self):
        self._current_row -=1
        if self._current_row < 0:
            self._current_row = 0
        return self.current_measurement_info


    def print_rows(self):
        for index, row in self._measurement_info.iterrows():
            info = MeasurementInfo(**row)

    @property
    def current_measurement_info(self):
        params = self._measurement_info.iloc[self._current_row]
        return MeasurementInfo(**params)
    
    @property
    def current_noise_parameters(self):
        meas_info = self.current_measurement_info
        if not meas_info:
            return None
        
        filename = meas_info.measurement_filename
        # params = {NoiseAnalysisParametersObject.THERMAL_NOISE_NODE_NAME:{"temperature": meas_info.temperature_end, "resistance": meas_info.equivalent_resistance_end}}

        noise_params = self._noise_params.get(filename)
        # if not noise_params:
        #     noise_params  = NoiseAnalysisParametersObject(filename, **params)
        #     self._noise_params[filename] = noise_params
            
        # noise_params.set_params(**params)

        return noise_params


class DataHandler(object): #QtCore.QObject): #object): # QtCore.QObject):
    #modelChanged = QtCore.pyqtSignal()#NoiseDataModel)

    def __init__(self):
        super().__init__()
        self._measurement_data_filename = None
        # self._model = None
        
        self._original_data = None
        self._analysis_data = None
        self._resulting_data = None
        
        self._measurement_info = None
        self._current_noise_params = None

        self._measurement_frequencies = None
        self._measurement_data = None

        self._working_directory = ""
        self._measurement_data_filename = ""

        self._selected_gr_index = None

    def reset(self):
        self._measurement_data_filename = None
        # self._model = None
        
        self._original_data = None
        self._analysis_data = None
        self._resulting_data = None
        
        self._measurement_info = None
        self._current_noise_params = None

        self._measurement_frequencies = None
        self._measurement_data = None

        self._working_directory = ""
        self._measurement_data_filename = ""

        self._selected_gr_index = None
        

    @property
    def current_noise_params(self):
        if self._measurement_info:
            return self._measurement_info.current_noise_parameters
        else:
            return None
        #else:
        #    return NoiseAnalysisParametersObject("temp_noise_parameters", **{NoiseAnalysisParametersObject.THERMAL_NOISE_NODE_NAME : {"temperature": 300, "resistance": 10002}})

        # if self._measurement_info:
        #     self._current_noise_params = self._measurement_info.current_noise_parameters
        # else:
        #         self._current_noise_params = NoiseAnalysisParametersObject("temp_noise_parameters", **{NoiseAnalysisParametersObject.THERMAL_NOISE_NODE_NAME : {"temperature": 300, "resistance": 10002}})

        # return self._current_noise_params

    def set_measurement_data(self, frequency, data):
        self._measurement_frequencies = frequency
        self._measurement_data = data
        
    @property
    def measurement_frequencies(self):
        return self._measurement_frequencies

    @property
    def measurement_data(self):
        return self._measurement_data

    @property
    def working_directory(self):
        return self._working_directory

    @working_directory.setter
    def working_directory(self, value):
        self._working_directory = value

    def refresh_curves(self):
        print(self.current_noise_params)


        # print("refreshing curves")
        # print(10*"*")
        # freq = self.measurement_frequencies
        # result = np.zeros_like(freq)
        # for name, node in self._model:
        #     if not isinstance(node, NoiseModelNode):
        #         continue
        #     if node.enabled:
        #         data = node.get_model_data(freq)
        #         self._plotter.set_curve_data(freq, data, name)
        #         result = result + data
            
        # self._plotter.set_resulting_data(freq, result)
        # print(10*"*")
        # result = 

    def saveState(self):
        if self._measurement_info:
            self._measurement_info.saveNoiseParams()

    def open_measurement_info_file(self, filename):
        print("FILENAME: {0}".format(filename))
        self.saveState()
        self.reset()

        self._measurement_info = MeasurementInfoFile(filename)
        print(self._measurement_info.columns)
        print(self._measurement_info.row_count)
        self.working_directory = os.path.dirname(filename)
        self._measurement_info.print_rows()
        self.load_measurement_data(self._measurement_info.current_measurement_info.measurement_filename)
        # self.next_measurement_file()
    
    def next_measurement_file(self):
        meas_info = self._measurement_info.next_row()
        print(meas_info)
        self.load_measurement_data(meas_info.measurement_filename)
    
    def prev_measurement_file(self):
        meas_info = self._measurement_info.prev_row()
        print(meas_info)
        self.load_measurement_data(meas_info.measurement_filename)
    
    def crop_data_for_analysis(self, start_frequency, stop_frequency):
        pass
    
    def load_measurement_data(self, filename):
        try:
            filename =  os.path.join(self.working_directory, filename)
            # data = pd.read_csv(filename, delimiter = "\t", skiprows=2)
            data = pd.read_csv(filename, delimiter="\t", index_col=None ) #header=[0,1]
            columns = list(data)
            #print("All columns read from file")
            #print(columns)
            
            freq_column_name, data_column_name = columns[0:2]
            self._original_data = data[[freq_column_name, data_column_name ]]
            frequencies = self._original_data[freq_column_name].values
            meas_data = self._original_data[data_column_name].values
            #print(frequencies)
            #print(meas_data)
            self.set_measurement_data(frequencies, meas_data)

        except Exception as e:
            print("Exception occured while loading measurement data")
            print(str(e))
            print(20*'*')
    
    def update_all_curve_data(self):
        pass
