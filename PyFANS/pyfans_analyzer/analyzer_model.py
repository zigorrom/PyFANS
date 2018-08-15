import os
import numpy as np
from functools import reduce
from pyqtgraph import intColor, mkPen

import pyfans.utils.ui_helper as uih
# from pyfans_analyzer.plot_data_handler import ProxyDataPlotHandler
from pyfans_analyzer.measurement_file_handler import *
import pyfans_analyzer.spectrum_processing as sp
from pyfans.physics.physical_calculations import calculate_thermal_noise #(equivalent_resistance, sample_resistance, load_resistance, temperature, amplifier_input_resistance = 1000000)
from pyfans.plot import FlickerHandle, GRHandle
from pyfans_analyzer.noise_model import FlickerNoiseComponent, GenerationRecombinationNoiseComponent, ThermalNoiseComponent, BaseNoiseComponent
from pyfans_analyzer.coordinate_transform import MultipliedXYTransformation

from lmfit import Model, CompositeModel, Parameters

class AnalyzerModel(uih.NotifyPropertyChanged):
    xLabel = "Frequency, f(Hz)"
    yLabel = "S<sub>V</sub>"
    xyLabel = "fS<sub>V</sub>"
    originalCurveName = "original_data_curve"
    displayCurveName = "display_data_curve"
    flickerNoiseName = "flicker"
    thermalNoiseName = "thermal"
    resultingNoiseName = "resulting"
    initFitName = "init_fit"
    bestFitName = "best_fit"

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
        self.__use_crop_range = False
        self.__thermal_enabled = None
        self.__equivalent_resistance = None
        self.__temperature = None
        self.__subtract_thermal_noise = None
        self.__flicker_enabled = None
        self.__flicker_amplitude = None
        self.__flicker_alpha = None
        self.__flicker_frequency = None
        self.__gr_enabled = None
        self.__gr_frequency = None
        self.__gr_amplitude = None
        self.__selected_gr_index = None
        self.__working_directory = None
        self.__measurement_file = None
        self.__isMultipliedByFrequency = False
        self.__autofit = False

        self._coordinate_transform = MultipliedXYTransformation()
        self._coordinate_transform.sigTransformChanged.connect(self.on_coordinate_transform_changed)
        
        self.__hide_original=False
        self._originalDataCurve = None
        self._originalFreq = None
        self._originalData = None

        self._displayDataCurve = None
        self._displayFreq = None
        self._displayData = None

        self._resultingDataCurve = None
        self._initFitDataCurve = None
        self._bestFitDataCurve = None  

        self.freq_column_name = None
        self.data_column_name = None

        self.analyzerWindow = None 
        self.setwindow(analyzer_window)
        self.setupMainCurvesOnPlotter()

        self.thermal_noise = None
        # self._noise_model_handles = dict()
        
        self.noise_components = dict()
        self.add_flicker_noise()
        self.add_thermal_noise()


    def setwindow(self, analyzer_window):
        self.analyzerWindow = analyzer_window
        self.connect_to_signals()

    def setPlotterXLabel(self):
        self.plotter.setXLabel(self.xLabel)

    def setPlotterYLabel(self):
        self.plotter.setYLabel(self.yLabel)

    def setPlotterXYLabel(self):
        self.plotter.setYLabel(self.xyLabel)

    def setupMainCurvesOnPlotter(self):
        original_curve_name = self.originalCurveName
        display_curve_name = self.displayCurveName
        curve = self.plotter.get_curve_by_name(original_curve_name)
        if curve is None:
            curve = self.plotter.create_curve(original_curve_name, pen=mkPen("r", width=1),zValue=900, visible=False)
            # curve.setVisible(False)
            self._originalDataCurve=curve
            
        else:
            curve.setVisible(False)

        curve = self.plotter.get_curve_by_name(display_curve_name)
        if curve is None:
            curve = self.plotter.create_curve(display_curve_name, pen=mkPen("g", width=1),zValue=1000, visible=True) #symbol="o", symbolPen="g", symbolBrush="g", size=10, pxMode=True)
            self._displayDataCurve=curve

        curve = self.plotter.get_curve_by_name(self.resultingNoiseName)
        if curve is None:
            curve = self.plotter.create_curve(self.resultingNoiseName, pen=mkPen("m", width=1),zValue=1001, visible=True)
            self._resultingDataCurve=curve

        curve = self.plotter.get_curve_by_name(self.initFitName)
        if curve is None:
            curve = self.plotter.create_curve(self.initFitName, pen=mkPen("y", width=3),zValue=1001, visible=True)
            self._initFitDataCurve=curve
        
        curve = self.plotter.get_curve_by_name(self.bestFitName)
        if curve is None:
            curve = self.plotter.create_curve(self.bestFitName, pen=mkPen("k", width=3),zValue=1002, visible=True)
            self._bestFitDataCurve=curve


        self.setPlotterXLabel()
        self.setPlotterYLabel()


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
            self.thermal_noise = calculate_thermal_noise(
                params.equivalent_resistance_end, 
                params.sample_resistance_end, 
                params.load_resistance, 
                params.temperature_end)
            
            print("thermal noise calculated")
            filename =  os.path.join(self.working_directory, filename)
            data = pd.read_csv(filename, delimiter="\t", index_col=None) #header=[0,1]
            columns = list(data)
            print("data is read")
            self.freq_column_name, self.data_column_name = columns[0:2]
            temp = data[[self.freq_column_name, self.data_column_name]]
            freq = temp[self.freq_column_name].values
            data = temp[self.data_column_name].values
            print("setting original data")
            self.setOriginalData(freq, data)
            print("original data set")
            if self.start_crop_frequency is None:
                self.start_crop_frequency = freq[0]
            if self.end_crop_frequency is None:
                self.end_crop_frequency = freq[-1]

            self.start_crop_frequency=max(self.start_crop_frequency, freq[0])
            self.end_crop_frequency=min(self.end_crop_frequency, freq[-1])
            
            thermal = self.noise_components.get(self.thermalNoiseName, None)
            if thermal is not None:
                thermal.thermal_noise_level = self.thermal_noise

        except Exception as e:
            print("Exception occured while loading measurement data")
            print(str(e))
            print(20*'*')

    def setOriginalData(self, frequency, data):
        self._originalFreq = frequency
        self._originalData = data
        self.isMultipliedByFrequency = False
        self.updateDisplayData()
        self.updateOriginalDataPlot()
        
    def updateOriginalAndDisplayPlots(self):
        self.updateOriginalDataPlot()
        self.updateDisplayDataPlot()

    def updateDisplayDataPlot(self):
        if self._displayDataCurve is None:
            return 

        print("updating display data curve")
        self._displayDataCurve.setData(self._displayFreq,self._displayData)


    def updateOriginalDataPlot(self):
        if self._originalDataCurve is None:
            return 
        
        self._originalDataCurve.setVisible(not self.hide_original)

        print("updating original data curve")
        # self._originalDataCurve.setVisible(False)
        self._originalDataCurve.setData(self._originalFreq,self._originalData)
 
    def on_coordinate_transform_changed(self):
        print("changing coordinate")

    def updateDisplayData(self):
        print("updating display data")

        self._displayFreq = self._originalFreq
        self._displayData = self._originalData

        if self.subtract_thermal_noise:
            self.perform_subtract_thermal_noise()

        self.update_multiply_by_frequency()

        if self.remove_pickups == True:
            try:
                self._displayData = sp.remove50Hz(self._displayFreq, self._displayData)

            except Exception as e:
                print("Exception in remove_pickups")
                print(e)
                
        
        if self.smoothing_enabled == True:
            try:
                self._displayFreq, self._displayData = sp.interpolate_data_log_space( self._displayFreq, self._displayData, points_per_decade=21, convolution_winsize=self.smoothing_winsize) 
                
            except Exception as e:
                print("Exception in remove_pickups")
                print(e)
        
        if self.cutoff_correction == True:
            try:
                self.perform_cutoff_correction()
            except Exception as e:
                print("Exception in cutoff correction")
                print(e)

        if self.use_crop_range == True:
            print("start cropping")
            print("start {0}".format(self.start_crop_frequency))
            if isinstance(self.start_crop_frequency , (int,float)):
                try:
                    idxs = np.where((self._displayFreq>=self.start_crop_frequency)) #&(self._originalFreq<=self.end_crop_frequency))
                    print(idxs)
                    self._displayFreq = self._displayFreq[idxs]
                    self._displayData = self._displayData[idxs]
                except Exception as e:
                    print("Exception in crop start")
                    print(e)
                    self._displayFreq = self._originalFreq
                    self._displayData = self._originalData

            print("end {0}".format(self.end_crop_frequency))
            if isinstance(self.end_crop_frequency , (int,float)):
                try:
                    idxs = np.where((self._displayFreq<=self.end_crop_frequency)) #&(self._originalFreq<=self.end_crop_frequency))
                    self._displayFreq = self._displayFreq[idxs]
                    self._displayData = self._displayData[idxs]
                except Exception as e:
                    print("Exception in crop end")
                    print(e)
                    self._displayFreq = self._originalFreq
                    self._displayData = self._originalData
            
            print("finish cropping")
                
        self.updateDisplayDataPlot()


    def update_multiply_by_frequency(self):
        
        if self.multiply_by_frequency:
            if not self.isMultipliedByFrequency:
                self._displayData = np.multiply(self._displayFreq, self._displayData)
                self._originalData = np.multiply(self._originalFreq, self._originalData)
                self.isMultipliedByFrequency = True
                self.setPlotterXYLabel()
            else: 
                pass
        else:
            if self.isMultipliedByFrequency:
                self._displayData = np.divide(self._displayData, self._displayFreq)
                self._originalData = np.divide(self._originalData, self._originalFreq)
                self.isMultipliedByFrequency = False
                self.setPlotterYLabel()
            else:
                pass
        
        self.updateOriginalAndDisplayPlots()

    def perform_subtract_thermal_noise(self):
        if not self.subtract_thermal_noise:
            return 

        if self.isMultipliedByFrequency:
            converted_back = np.divide(self._displayData, self._displayFreq)
            converted_back = sp.subtract_thermal_noise(converted_back, self.thermal_noise)
            self._displayData = np.multiply(self._displayFreq, converted_back)
            
        else:
            self._displayData = sp.subtract_thermal_noise(self._displayData, self.thermal_noise)
        
        self.updateDisplayDataPlot()

    def perform_cutoff_correction(self):
        if not self.cutoff_correction:
            return
        
        self._displayData = sp.cutoffCorrection(self._displayFreq, self._displayData, self.equivalen_resistance, self.cutoff_correction_capacity)

    def on_file_save_triggered(self, filename):
        pass

    def on_noise_component_update_required(self):
        print("updating resulting curve")
        try:
            resulting_array = np.zeros_like(self._displayFreq)
            for name, component in self.noise_components.items():
                if not component.enabled:
                    continue
                func = component.getModelFunction()
                array = func(self._displayFreq)
                resulting_array = np.add(resulting_array, array)

            self._resultingDataCurve.setData(self._displayFreq, resulting_array)
        except Exception as e:
            print("Error when updating resulting spectrum")
            print(e)

    def setupParams(self):
        currentRow = self.__measurement_file.current_measurement_info
        self.equivalen_resistance = currentRow.equivalent_resistance_end
        self.temperature = currentRow.temperature_end

    def on_next_triggered(self):
        meas_info = self.__measurement_file.next_row()
        print(meas_info)
        self.load_measurement_data(meas_info.measurement_filename)
        if self.autofit:
            self.on_fit_data_triggered()

    def on_prev_triggered(self):
        meas_info = self.__measurement_file.prev_row()
        print(meas_info)
        self.load_measurement_data(meas_info.measurement_filename)
        if self.autofit:
            self.on_fit_data_triggered()

    def on_crop_triggered(self):
        self.use_crop_range = True
        xmin = np.log10(self.start_crop_frequency)
        xmax = np.log10(self.end_crop_frequency)
        self.plotter.setXRange(xmin,xmax)
        self.updateDisplayData()
        

    def on_undo_crop_triggered(self):
        self.use_crop_range = False
        self.updateDisplayData()
        

    def on_flicker_noise_reset_triggered(self):
        self.flicker_amplitude = 0
        self.flicker_alpha = 0
        self.flicker_frequency = 0

    def add_thermal_noise(self):
        thermal_name = self.thermalNoiseName
        if thermal_name in self.noise_components:
            return 

        thermal = ThermalNoiseComponent(thermal_name, True, self.plotter, coordinate_transform=self.coordinate_transform)
        self.noise_components[thermal_name] = thermal

    def add_flicker_noise(self):
        flicker_name = self.flickerNoiseName
        if flicker_name in self.noise_components:
            return 
        
        flicker = FlickerNoiseComponent(flicker_name, True, self.plotter, pen="g", coordinate_transform=self.coordinate_transform)
        flicker.sigAmplitudeChanged.connect(self.on_flicker_handle_position_changed)
        flicker.sigNoiseUpdateRequired.connect(self.on_noise_component_update_required)
        self.noise_components[flicker_name] = flicker
        
    def on_flicker_handle_position_changed(self, flicker, amplitude):
        self.flicker_amplitude = amplitude
        self.flicker_alpha = flicker.alpha_flicker
        self.flicker_frequency = flicker.frequency
        self.flicker_enabled = flicker.enabled
        
    def on_add_gr_noise_triggered(self):
        count = self.analyzer_window.get_gr_component_count()
        gr_name = "GR_{0}".format(count)
        pen = intColor(count)

        if gr_name in self.noise_components:
            return
        
        gr = GenerationRecombinationNoiseComponent(gr_name, True, self.plotter, pen=pen, coordinate_transform=self.coordinate_transform)
        gr.sigPositionChanged.connect(self.on_gr_handle_position_changed)
        gr.sigNoiseUpdateRequired.connect(self.on_noise_component_update_required)
        # gr.sigPositionChanged.connect()
        self.noise_components[gr_name] = gr
        self.analyzer_window.add_gr_component(gr_name)
        self.selected_gr_index = count
        

    def on_gr_handle_position_changed(self, handle, frequency, amplitude):
        # name = self.analyzer_window.remove_gr_name_by_index(self.selected_gr_index )
        # if handle.name != name:
        #     return
        print(handle.name)
        self.selected_gr_index = self.analyzer_window.getIndexFromGRname(handle.name)
        self.gr_amplitude = amplitude
        self.gr_frequency = frequency
        self.gr_enabled = handle.enabled

    


    def on_remove_gr_noise_triggered(self):
        selected_item_name = self.analyzer_window.remove_gr_name_by_index(self.selected_gr_index)
        item = self.noise_components.pop(selected_item_name)
        item.remove_handle()

 

    def on_reset_gr_noise_triggered(self):
        pass

    

    def on_selected_gr_changed(self):
        print("selection changed")
        name = self.analyzer_window.getSelectedGRitemText()
        component = self.noise_components.get(name, None)
        if component is None:
            return
        self.gr_enabled = component.enabled
        self.gr_amplitude = component.amplitude
        self.gr_frequency = component.frequency

       

        
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
    def plotter(self):
        return self.analyzer_window.plotter

    @property
    def isMultipliedByFrequency(self):
        return self.__isMultipliedByFrequency

    @isMultipliedByFrequency.setter
    def isMultipliedByFrequency(self, value):
        if self.__isMultipliedByFrequency == value:
            return
        self.__isMultipliedByFrequency = value
        # update view here

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
        self.updateDisplayData()
        

    @property
    def hide_original(self):
        return self.__hide_original

    @hide_original.setter
    @uih.assert_boolean_argument
    def hide_original(self, value):
        if self.__hide_original == value:
            return 

        self.__hide_original = value
        self._originalDataCurve.setVisible(not value)
        self.onPropertyChanged("hide_original", self, value)
        # self.updateDisplayData()


        
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
        self.updateDisplayData()
        

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
        self.updateDisplayData()
        
     
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
        self.updateDisplayData()

    @property
    def cutoff_correction_capacity(self):
        return self.__cutoff_correction_capacity

    @cutoff_correction_capacity.setter
    @uih.assert_int_or_float_argument
    def cutoff_correction_capacity(self, value):
        if self.__cutoff_correction_capacity == value:
            return 

        self.__cutoff_correction_capacity = value
        self.onPropertyChanged("cutoff_correction_capacity", self, value)
        self.updateDisplayData()
        
    @property
    def multiply_by_frequency(self):
        # return self.__multiply_by_frequency
        return self.coordinate_transform.is_multiplied

    @multiply_by_frequency.setter
    @uih.assert_boolean_argument
    def multiply_by_frequency(self, value):
        # if self.__multiply_by_frequency == value:
        if self.multiply_by_frequency == value:
            return 

        # self.__multiply_by_frequency = value
        self.coordinate_transform.is_multiplied = value
        self.onPropertyChanged("multiply_by_frequency", self, value)
        self.updateDisplayData()
        
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
        self.updateDisplayData()
        
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
        self.updateDisplayData()
      
    @property
    def use_crop_range(self):
        return self.__use_crop_range

    @use_crop_range.setter
    def use_crop_range(self, value):
        if self.__use_crop_range == value:
            return 

        self.__use_crop_range = value
        self.updateDisplayData()
    
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
        self.updateDisplayData()
        try:
            thermal = self.noise_components[self.thermalNoiseName]
            thermal.enabled = value
        except Exception as e:
            print("Exception while enabling flicker")
            print(e)
    
    @property
    def equivalen_resistance(self):
        return self.__equivalent_resistance

    @equivalen_resistance.setter
    @uih.assert_int_or_float_argument
    def equivalen_resistance(self, value):
        if self.__equivalent_resistance == value:
            return 

        self.__equivalent_resistance = value
        self.onPropertyChanged("equivalent_resistance", self, value)
        # self.updateDisplayData()
    
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
        # self.updateDisplayData()
    
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
        self.updateDisplayData()
        # self.proxyDataPlotHandler.substract_thermal_noise = value
    
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
        try:
            flicker = self.noise_components[self.flickerNoiseName]
            flicker.enabled = value
        except Exception as e:
            print("Exception while enabling flicker")
            print(e)

    
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
        try:
            flicker = self.noise_components[self.flickerNoiseName]
            flicker.absolute_amplitude = value
        except Exception as e:
            print("Exception while setting flicker amplitude")
            print(e)
    
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
        try:
            flicker = self.noise_components[self.flickerNoiseName]
            flicker.alpha_flicker = value
        except Exception as e:
            print("Exception while setting flicker amplitude")
            print(e)
    
    @property
    def flicker_frequency(self):
        return self.__flicker_frequency

    @flicker_frequency.setter
    @uih.assert_int_or_float_argument
    def flicker_frequency(self, value):
        if self.__flicker_frequency == value:
            return 

        self.__flicker_frequency = value
        self.onPropertyChanged("flicker_frequency", self, value)
        try:
            flicker = self.noise_components[self.flickerNoiseName]
            flicker.frequency = value
        except Exception as e:
            print("Exception while setting flicker amplitude")
            print(e)

    # 
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
        name = self.analyzer_window.getSelectedGRitemText()
        component = self.noise_components.get(name, None)
        if component is None:
            return
        component.enabled = value
        

    
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
        name = self.analyzer_window.getSelectedGRitemText()
        component = self.noise_components.get(name, None)
        if component is None:
            return
        component.frequency = value
        print("frequency updated")
        
        



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
        name = self.analyzer_window.getSelectedGRitemText()
        component = self.noise_components.get(name, None)
        if component is None:
            return
        component.amplitude = value

    @property
    def coordinate_transform(self):
        return self._coordinate_transform

    @property
    def autofit(self):
        return self.__autofit

    @autofit.setter
    def autofit(self, value):
        if self.__autofit == value:
            return 

        self.__autofit = value
        self.onPropertyChanged("autofit", self, value)

    
    def on_fit_data_triggered(self):
        print("start fitting")
        import operator
        # list_of_models = [Model(v.getModelFunction(),prefix=k, nan_policy="propagate") for k,v in self.noise_components.items()] 
        list_of_models = list()
        list_of_params = list()
        for name,component in self.noise_components.items():
            if not component.enabled:
                continue
            model, param = component.getFittingModelAndParams(logMode=False)
            list_of_models.append(model)
            parameters = list(param.values())
            list_of_params.extend(parameters)
            # print()
        # list_of_models = [v.getFittingModelAndParams for k,v in self.noise_components.items()]
        # print("list of parameters")
        print(list_of_params)
        fit_model = reduce(operator.add, list_of_models)
        fit_parameters = Parameters()
        fit_parameters.add_many(*list_of_params)
        print()
        print(fit_parameters)
        # print()
        # # # fit_model = reduce()
        # # # params = comp_model.make_params()
        # print(fit_model)

        # params = fit_model.make_params()
        # print(params)
        # print(self._displayData)
        data = self._displayData
        # data = np.log10(self._displayData)
        # print(data)
        result = fit_model.fit(data, fit_parameters, f=self._displayFreq)
        print(result.fit_report())
        print("best values")
        print(result.params)
        # print(result.init_fit)
        # print("init fit")
        # print(result.init_fit)
        # print("best fit")
        # print(result.best_fit)
        # freq, data_converted = self.coordinate_transform.convert(self._displayFreq, result.init_fit)
        # self._initFitDataCurve.setData(freq, data_converted)
        # freq, data_converted = self.coordinate_transform.convert(self._displayFreq, result.best_fit)
        # self._bestFitDataCurve.setData(freq, data_converted)
        
        for name, param in result.best_values.items(): #items():
            try:
                component_name, param_name = name.split(BaseNoiseComponent.PREFIX_SPLITTER)
                component = self.noise_components[component_name]
                setattr(component, param_name, param)

            except Exception as e:
                print("exception while setting fitted values")
                print(e)
            
            

        # result_data = result.eval_components() 
        # for name, data in result_data.items():
        #     curve = self.plotter.get_curve_by_name(name)
        #     # data = np.power(10,data)
        #     curve.setData(self._displayFreq, data)
        # print(result.eval_components())