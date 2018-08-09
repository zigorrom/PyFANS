import os
import numpy as np
import pyfans.utils.ui_helper as uih
from pyfans_analyzer.plot_data_handler import ProxyDataPlotHandler
from pyfans_analyzer.measurement_file_handler import *
import pyfans_analyzer.spectrum_processing as sp
from pyfans.physics.physical_calculations import calculate_thermal_noise #(equivalent_resistance, sample_resistance, load_resistance, temperature, amplifier_input_resistance = 1000000)

# spectral_data = sp.remove50Hz(frequencies, spectral_data)
# frequencies, spectral_data = sp.interpolate_data_log_space(frequencies, spectral_data, points_per_decade=self.points_per_decade) 
# spectral_data = sp.subtract_thermal_noise(spectral_data, self.thermal_noise)
class NoiseModel():
    def __init__(self):
        self.flickerNoise = None
        self.grList = list()
        self.thermalNoise = None
    



class AnalyzerModel(uih.NotifyPropertyChanged):
    def __init__(self, analyzer_window=None):
        super().__init__()
        self.__remove_pickups = None
        self.__smoothing_enabled = None
        self.__smoothing_winsize = None
        self.__cutoff_correction = None
        self.__cutoff_correction_capacity = None
        self.__multiply_by_frequency = None
        self.__start_crop_frequency = None
        self.__end_crop_frequency = None
        self.__thermal_enabled = None
        self.__equivalen_resistance = None
        self.__temperature = None
        self.__subtract_thermal_noise = None
        self.__flicker_enabled = None
        self.__flicker_amplitude = None
        self.__flicker_alpha = None
        self.__gr_enabled = None
        self.__gr_frequency = None
        self.__gr_amplitude = None
        self.__selected_gr_index = None
        self.__working_directory = None

        self.__measurement_file = None

        # self._original_data = None
        # self._display_data = None
        self.thermal_noise = None
        # self._originalFreq = None
        # self._originalData=None
        # self._displayFreq = None
        # self._displayData = None

        self.freq_column_name = None
        self.data_column_name = None


        self.analyzerWindow = None #analyzer_window
        self.setwindow(analyzer_window)
        self.proxyDataPlotHandler=ProxyDataPlotHandler(self.analyzerWindow.plotter)

        

    def setwindow(self, analyzer_window):
        self.analyzerWindow = analyzer_window
        self.connect_to_signals()

    def connect_to_signals(self):
        if self.analyzerWindow is None:
            return

        self.analyzerWindow.sigOpenFileTriggered.connect(self.on_file_open_triggered)
        self.analyzerWindow.sigSaveFileTriggered.connect(self.on_file_save_triggered)
        self.analyzerWindow.sigNextTriggered.connect(self.on_next_triggered)
        self.analyzerWindow.sigPrevTriggered.connect(self.on_prev_triggered)
        self.analyzerWindow.sigCropTriggered.connect(self.on_crop_triggered)
        self.analyzerWindow.sigCropUndoTriggered.connect(self.on_undo_crop_triggered)
        self.analyzerWindow.sigFlickerResetTriggered.connect(self.on_flicker_noise_reset_triggered)
        self.analyzerWindow.sigAddGRTriggered.connect(self.on_add_gr_noise_triggered)
        self.analyzerWindow.sigRemoveGRTriggered.connect(self.on_remove_gr_noise_triggered)
        self.analyzerWindow.sigResetGRTriggered.connect(self.on_reset_gr_noise_triggered)
        self.analyzerWindow.sigFitTriggered.connect(self.on_fit_data_triggered)
        self.analyzerWindow.sigSelectedGRChanged.connect(self.on_selected_gr_changed)
    

    

    def on_file_open_triggered(self, filename):
        wd, fn = os.path.split(filename)
        self.working_directory = wd
        self.__measurement_file = MeasurementInfoFile(filename)
        print(self.__measurement_file.columns)
        print(self.__measurement_file.row_count)
        self.working_directory = os.path.dirname(filename)
        self.__measurement_file.print_rows()
        self.load_measurement_data(self.__measurement_file.current_measurement_info.measurement_filename)
        
    def load_measurement_data(self, filename):
        print("opening file {0}".format(filename))
        try:
            self.setupParams()
            params = self.__measurement_file.current_measurement_info
# (equivalent_resistance, sample_resistance, load_resistance, temperature, amplifier_input_resistance = 1000000)
            self.thermal_noise = calculate_thermal_noise(
                params.equivalent_resistance_end, 
                params.sample_resistance_end, 
                params.load_resistance, 
                params.temperature_end)

            filename =  os.path.join(self.working_directory, filename)
            data = pd.read_csv(filename, delimiter="\t", index_col=None ) #header=[0,1]
            columns = list(data)
            
            self.freq_column_name, self.data_column_name = columns[0:2]
            temp = data[[self.freq_column_name, self.data_column_name]]
            freq = temp[self.freq_column_name].values
            data = temp[self.data_column_name].values
            
            self.proxyDataPlotHandler.setOriginalData(freq, data)
            self.proxyDataPlotHandler.thermalNoise = self.thermal_noise

            self.start_crop_frequency =freq[0]
            self.end_crop_frequency =freq[-1]
            

        except Exception as e:
            print("Exception occured while loading measurement data")
            print(str(e))
            print(20*'*')

    # def proxy_plot_curve(self):
        
    #     plotter = self.analyzer_window.plotter
    #     plotter.updata_resulting_spectrum(self._displayFreq, self._displayData)


    def on_file_save_triggered(self, filename):
        pass

    def setupParams(self):
        currentRow = self.__measurement_file.current_measurement_info
        self.equivalen_resistance = currentRow.equivalent_resistance_end
        self.temperature = currentRow.temperature_end

    def on_next_triggered(self):
        meas_info = self.__measurement_file.next_row()
        print(meas_info)
        self.load_measurement_data(meas_info.measurement_filename)

    def on_prev_triggered(self):
        meas_info = self.__measurement_file.prev_row()
        print(meas_info)
        self.load_measurement_data(meas_info.measurement_filename)

    def on_crop_triggered(self):
        self.proxyDataPlotHandler.beginUpdate()
        self.proxyDataPlotHandler.crop_start = self.start_crop_frequency
        # print(self.proxyDataPlotHandler.crop_end)
        self.proxyDataPlotHandler.crop_end = self.end_crop_frequency
        self.proxyDataPlotHandler.use_crop = True
        self.proxyDataPlotHandler.endUpdate()
    
        # self.proxyDataPlotHandler

    def on_undo_crop_triggered(self):
        self.proxyDataPlotHandler.use_crop = False

    def on_flicker_noise_reset_triggered(self):
        self.flicker_amplitude = 0
        self.flicker_alpha = 0

    def on_add_gr_noise_triggered(self):
        pass

    def on_remove_gr_noise_triggered(self):
        pass

    def on_reset_gr_noise_triggered(self):
        pass

    def on_fit_data_triggered(self):
        pass

    def on_selected_gr_changed(self):
        print("selection changed")
        
    @property
    def working_directory(self):
        return self.__working_directory

    @working_directory.setter
    def working_directory(self, value):
        self.__working_directory = value

    @property
    def analyzer_window(self):
        return self.analyzerWindow

    @property
    def selected_gr_index(self):
        return self.__selected_gr_index

    @selected_gr_index.setter
    @uih.assert_integer_argument
    def selected_gr_index(self, value):
        if self.__selected_gr_index == value:
            return 

        self.__selected_gr_index = value
        self.onPropertyChanged("selected_gr_index", self, value)

    @property
    def remove_pickups(self):
        return self.__remove_pickups

    @remove_pickups.setter
    @uih.assert_boolean_argument
    def remove_pickups(self, value):
        if self.__remove_pickups == value:
            return 

        self.__remove_pickups = value
        self.onPropertyChanged("remove_pickups", self, value)

        self.proxyDataPlotHandler.remove_pickups = value
        
    @property
    def smoothing_winsize(self):
        return self.__smoothing_winsize

    @smoothing_winsize.setter
    @uih.assert_integer_argument
    def smoothing_winsize(self, value):
        if self.__smoothing_winsize == value:
            return 

        self.__smoothing_winsize = value
        self.onPropertyChanged("smoothing_winsize", self, value)
        self.proxyDataPlotHandler.smoothing_winsize = value

    @property
    def smoothing_enabled(self):
        return self.__smoothing_enabled

    @smoothing_enabled.setter
    @uih.assert_boolean_argument
    def smoothing_enabled(self, value):
        if self.__smoothing_enabled == value:
            return 

        self.__smoothing_enabled = value
        self.onPropertyChanged("smoothing_enabled", self, value)

        self.proxyDataPlotHandler.smoothing = value
     
    @property
    def cutoff_correction(self):
        return self.__cutoff_correction

    @cutoff_correction.setter
    @uih.assert_boolean_argument
    def cutoff_correction(self, value):
        if self.__cutoff_correction == value:
            return 

        self.__cutoff_correction = value
        self.onPropertyChanged("cutoff_correction", self, value)

    @property
    def cutoff_correction_capacity(self):
        return self.__cutoff_correction

    @cutoff_correction_capacity.setter
    @uih.assert_int_or_float_argument
    def cutoff_correction_capacity(self, value):
        if self.__cutoff_correction_capacity == value:
            return 

        self.__cutoff_correction_capacity = value
        self.onPropertyChanged("cutoff_correction_capacity", self, value)
        
    @property
    def multiply_by_frequency(self):
        return self.__multiply_by_frequency

    @multiply_by_frequency.setter
    @uih.assert_boolean_argument
    def multiply_by_frequency(self, value):
        if self.__multiply_by_frequency == value:
            return 

        self.__multiply_by_frequency = value
        self.onPropertyChanged("multiply_by_frequency", self, value)
        self.proxyDataPlotHandler.multiply_by_frequency = value
        
    @property
    def start_crop_frequency(self):
        return self.__start_crop_frequency

    @start_crop_frequency.setter
    @uih.assert_int_or_float_argument
    def start_crop_frequency(self, value):
        if self.__start_crop_frequency == value:
            return 

        self.__start_crop_frequency = value
        self.onPropertyChanged("start_crop_frequency", self, value)
        
    @property
    def end_crop_frequency(self):
        return self.__end_crop_frequency

    @end_crop_frequency.setter
    @uih.assert_int_or_float_argument
    def end_crop_frequency(self, value):
        if self.__end_crop_frequency == value:
            return 

        self.__end_crop_frequency = value
        self.onPropertyChanged("end_crop_frequency", self, value)
      
    @property
    def thermal_enabled(self):
        return self.__thermal_enabled

    @thermal_enabled.setter
    @uih.assert_boolean_argument
    def thermal_enabled(self, value):
        if self.__thermal_enabled == value:
            return 

        self.__thermal_enabled = value
        self.onPropertyChanged("thermal_enabled", self, value)
    
    @property
    def equivalen_resistance(self):
        return self.__equivalen_resistance

    @equivalen_resistance.setter
    @uih.assert_int_or_float_argument
    def equivalen_resistance(self, value):
        if self.__equivalen_resistance == value:
            return 

        self.__equivalen_resistance = value
        self.onPropertyChanged("equivalent_resistance", self, value)
    
    @property
    def temperature(self):
        return self.__temperature

    @temperature.setter
    @uih.assert_int_or_float_argument
    def temperature(self, value):
        if self.__temperature == value:
            return 

        self.__temperature = value
        self.onPropertyChanged("temperature", self, value)
    
    @property
    def subtract_thermal_noise(self):
        return self.__subtract_thermal_noise

    @subtract_thermal_noise.setter
    @uih.assert_boolean_argument
    def subtract_thermal_noise(self, value):
        if self.__subtract_thermal_noise == value:
            return 

        self.__subtract_thermal_noise = value
        self.onPropertyChanged("subtract_thermal_noise", self, value)
        self.proxyDataPlotHandler.substract_thermal_noise = value
    
    @property
    def flicker_enabled(self):
        return self.__flicker_enabled

    @flicker_enabled.setter
    @uih.assert_boolean_argument
    def flicker_enabled(self, value):
        if self.__flicker_enabled == value:
            return 

        self.__flicker_enabled = value
        self.onPropertyChanged("flicker_enabled", self, value)
    
    @property
    def flicker_amplitude(self):
        return self.__flicker_amplitude

    @flicker_amplitude.setter
    @uih.assert_int_or_float_argument
    def flicker_amplitude(self, value):
        if self.__flicker_amplitude == value:
            return 

        self.__flicker_amplitude = value
        self.onPropertyChanged("flicker_amplitude", self, value)
    
    @property
    def flicker_alpha(self):
        return self.__flicker_alpha

    @flicker_alpha.setter
    @uih.assert_int_or_float_argument
    def flicker_alpha(self, value):
        if self.__flicker_alpha == value:
            return 

        self.__flicker_alpha = value
        self.onPropertyChanged("flicker_alpha", self, value)
    
    @property
    def gr_enabled(self):
        return self.__gr_enabled

    @gr_enabled.setter
    @uih.assert_boolean_argument
    def gr_enabled(self, value):
        if self.__gr_enabled == value:
            return 

        self.__gr_enabled = value
        self.onPropertyChanged("gr_enabled", self, value)
    
    @property
    def gr_frequency(self):
        return self.__gr_frequency

    @gr_frequency.setter
    @uih.assert_int_or_float_argument
    def gr_frequency(self, value):
        if self.__gr_frequency == value:
            return 

        self.__gr_frequency = value
        self.onPropertyChanged("gr_frequency", self, value)
    
    @property
    def gr_amplitude(self):
        return self.__gr_amplitude

    @gr_amplitude.setter
    @uih.assert_int_or_float_argument
    def gr_amplitude(self, value):
        if self.__gr_amplitude == value:
            return 

        self.__gr_amplitude = value
        self.onPropertyChanged("gr_amplitude", self, value)
    

    def openFile(self):
        pass