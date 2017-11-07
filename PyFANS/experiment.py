﻿import os
import time
import math
import numpy as np

import process_communication_protocol as pcp
import nodes as ns
import configuration as cfg
import experiment_writer as ew
import calibration as calib
import measurement_data_structures as mds

class Experiment:
    def __init__(self, simulate = False, input_data_queue = None, stop_event = None):
        self.__config = None
        self.__exp_settings = None
        self.__hardware_settings = None
        self._simulate = simulate
        self._execution_function = None
        self._input_data_queue = input_data_queue
        self._working_directory = ""
        self._data_handler = None
        self._stop_event = stop_event
        self._measurement_info = None
        self._spectrum_ranges = {0: (0,1600,1),1:(0,102400,64)}
        self._spectrum_linking_frequencies = {0:(1,1600),1:(1600,102400)}
        self._frequencies = self._get_frequencies(self._spectrum_ranges)
        self._frequency_indexes = self._get_frequency_linking_indexes(self._spectrum_ranges, self._spectrum_linking_frequencies)
        self._spectrum_data = {}
        self._measurement_counter = 0
        self._experiment_writer = None    
        self._calibration = None
                                                                                                                                             
    
    @property
    def need_exit(self):
        if self._stop_event:
            return self._stop_event.is_set()
        return False

    @property
    def calibration(self):
        return self._calibration

    @property
    def configuration(self):
        return self.__config

    @property
    def experiment_settings(self):
        return self.__exp_settings 

    @property
    def hardware_settings(self):
        return self.__hardware_settings

    @property
    def simulate(self):
        return self._simulate

    #@property
    #def data_handler(self):
    #    return self._data_handler
    def _get_frequencies(self, spectrum_ranges):
        result = {}
        for k,v in spectrum_ranges.items():
            start,stop,step = v
            nlines = 1+(stop-start)/step
            result[k] = np.linspace(start,stop, nlines, True)
        return result

    def _get_frequency_linking_indexes(self, spectrum_ranges, linking_frequencies):
        result = {}
        for rng, vals in spectrum_ranges.items():
            start,stop,step = vals
            start_freq, stop_freq = linking_frequencies[rng]
            start_freq_idx =  math.ceil((start_freq-start)/step) 
            stop_freq_idx = math.floor((stop_freq-start)/step)
            result[rng] = (start_freq_idx, stop_freq_idx)
        return result


    def initialize_settings(self, configuration):
        self.__config = configuration
        assert isinstance(configuration, cfg.Configuration)
        self.__exp_settings = configuration.get_node_from_path("Settings.ExperimentSettings")
        assert isinstance(self.__exp_settings, ns.ExperimentSettings)
        self.__hardware_settings = configuration.get_node_from_path("Settings.HardwareSettings")
        assert isinstance(self.__hardware_settings, ns.HardwareSettings)
        self._working_directory = self.__exp_settings.working_directory
        
        #self._data_handler = DataHandler(self._working_directory,input_data_queue = self._input_data_queue)

    def initialize_hardware(self):
        pass
    
    def initialize_calibration(self):
        #dir = os.path.dirname(__file__)
        #self._calibration = calib.Calibration(os.path.join(dir,"calibration_data"))
        #self._calibration = calib.CalibrationSimple(os.path.join(dir,"calibration_data"))
        #self._calibration.init_values()
        pass

    def get_meas_ranges(self):
        fg_range = self.__config.get_node_from_path("front_gate_range")
        if self.__exp_settings.use_set_vfg_range:
            assert isinstance(fg_range, ns.ValueRange)
        ds_range = self.__config.get_node_from_path("drain_source_range")
        if self.__exp_settings.use_set_vds_range:
            assert isinstance(fg_range, ns.ValueRange)
        return ds_range, fg_range

    def output_curve_measurement_function(self):
        try:
            ds_range, fg_range = self.get_meas_ranges()
        
            if (not self.__exp_settings.use_set_vfg_range) and (not self.__exp_settings.use_set_vds_range) and not self.need_exit:
                self.single_value_measurement(self.__exp_settings.drain_source_voltage,self.__exp_settings.front_gate_voltage)

            elif self.__exp_settings.use_set_vds_range and self.__exp_settings.use_set_vfg_range and not self.need_exit:
                for vfg in fg_range.get_range_handler():
                    if self.need_exit:
                        return
                    for vds in ds_range.get_range_handler():
                        if self.need_exit:
                            return
                        self.single_value_measurement(vds, vfg)
           
            elif not self.__exp_settings.use_set_vfg_range:
                for vds in ds_range.get_range_handler():
                    if self.need_exit:
                        return
                    self.single_value_measurement(vds, self.__exp_settings.front_gate_voltage)
                    
            elif not self.__exp_settings.use_set_vds_range:
                for vfg in fg_range.get_range_handler():
                    if self.need_exit:
                        return
                    self.single_value_measurement(self.__exp_settings.drain_source_voltage, vfg)
            else:
                raise ValueError("range handlers are not properly defined")
        except:
            pass
        finally:
            self.set_voltages_to_zero()


    def transfer_curve_measurement_function(self):
        try:
            ds_range, fg_range = self.get_meas_ranges()
            if (not self.__exp_settings.use_set_vds_range) and (not self.__exp_settings.use_set_vfg_range) and not self.need_exit:
                 self.single_value_measurement(self.__exp_settings.drain_source_voltage,self.__exp_settings.front_gate_voltage)

            elif self.__exp_settings.use_set_vds_range and self.__exp_settings.use_set_vfg_range:
                for vds in ds_range.get_range_handler():
                    if self.need_exit:
                        return
                    for vfg in fg_range.get_range_handler():
                        if self.need_exit:
                            return
                        self.single_value_measurement(vds, vfg)
           
            elif not self.__exp_settings.use_set_vfg_range:
                for vds in ds_range.get_range_handler():
                    if self.need_exit:
                        return
                    self.single_value_measurement(vds, self.__exp_settings.front_gate_voltage)
                    
            elif not self.__exp_settings.use_set_vds_range:
                 for vfg in fg_range.get_range_handler():
                     if self.need_exit:
                        return
                     self.single_value_measurement(self.__exp_settings.drain_source_voltage, vfg)
            else:
                raise ValueError("range handlers are not properly defined")
        except:
            pass
        finally:
            self.set_voltages_to_zero()


    def non_gated_structure_meaurement_function(self):
        try:
            if self.__exp_settings.use_set_vds_range:
                 for vds in self.__exp_settings.vds_range:
                     if self.need_exit:
                        return
                     self.non_gated_single_value_measurement(vds)
            else:
                self.non_gated_single_value_measurement(self.__exp_settings.drain_source_voltage)
        except:
            pass
        finally:
            self.set_drain_source_voltage(0)

        
    def set_voltages_to_zero(self):
        self.set_drain_source_voltage(0)
        self.set_front_gate_voltage(0)

    def handle_measurement_abort(self):
        raise NotImplementedError()

    def switch_transistor(self,transistor):
        raise NotImplementedError()

    def wait_for_stabilization_after_switch(self, time_to_wait_sec = 5 ):
        print("waiting for stabilization")
        time.sleep(time_to_wait_sec)
    #value: sample or main
    def switch_voltage_measurement_relay_to(self, value):
        raise NotImplementedError()

    def prepare_to_set_voltages(self):
        raise NotImplementedError()

    def prepare_to_measure_voltages(self):
        raise NotImplementedError()

    def perform_start_param_measurement(self):
        raise NotImplementedError()

    def perform_end_param_measurement(self):
        raise NotImplementedError()

    def prepare_to_measure_spectrum(self):
        raise NotImplementedError()

    def prepare_to_measure_timetrace(self):
        raise NotImplementedError()

    def set_front_gate_voltage(self,voltage):
        raise NotImplementedError()

    def set_drain_source_voltage(self,voltage):
        raise NotImplementedError()

    def perform_single_value_measurement(self):
        raise NotImplementedError()

    def perform_non_gated_single_value_measurement(self):
        raise NotImplementedError()


    ##replace name to prepare_single_value_measurement
    def single_value_measurement(self, drain_source_voltage, gate_voltage):
        if self.need_exit:
            return
        
        self.open_measurement()
        
        #assert isinstance(self.experiment_settings, ExperimentSettings)
        if self.experiment_settings.use_automated_voltage_control:
            self.prepare_to_set_voltages()
            self.set_drain_source_voltage(drain_source_voltage)
            self.set_front_gate_voltage(gate_voltage)
            #specific of measurement setup!!!
            self.set_drain_source_voltage(drain_source_voltage)
        
        self.prepare_to_measure_voltages()
        self.perform_start_param_measurement()
        self.prepare_to_measure_spectrum()
        self.perform_single_value_measurement()
        self.perform_end_param_measurement()
        
        self.save_measurement_info()
        
        self.close_measurement()


    def save_measurement_info(self):
        self._experiment_writer.write_measurement_info(self._measurement_info)


    ##replace name to prepare_non_gated_single_value_measurement
    def non_gated_single_value_measurement(self, drain_source_voltage):
        if self.need_exit:
            return
        self.open_measurement()
        
        if self.experiment_settings.use_automated_voltage_control:
            self.prepare_to_set_voltages()
            self.set_drain_source_voltage(drain_source_voltage)
        
        self.prepare_to_measure_voltages()
        self.perform_start_param_measurement()
        self.prepare_to_measure_spectrum()
        self.perform_non_gated_single_value_measurement()
        self.perform_end_param_measurement()
        self.save_measurement_info()
        self.close_measurement()



    def _send_command(self,command):
        q = self._input_data_queue
        if q:
            q.put_nowait({pcp.COMMAND: command})

    def _send_command_with_param(self,command,param):
        q = self._input_data_queue
        if q:
            q.put_nowait({pcp.COMMAND:command, pcp.PARAMETER:param})

    def _send_command_with_params(self,command, **kwargs):
        q = self._input_data_queue
        params = {pcp.COMMAND: command}
        if kwargs:
            params[pcp.PARAMETER] = kwargs
        #params.update(kwargs)
        if q:
            q.put_nowait(params)   

    def create_experiment_writer(self):
        return ew.ExperimentWriter(self._working_directory)

    def open_experiment(self):
        experiment_name = self.__exp_settings.experiment_name
        self._send_command_with_params(pcp.ExperimentCommands.EXPERIMENT_STARTED, experiment_name = experiment_name)
        self._measurement_counter = self.__exp_settings.measurement_count
        exp_writer = self.create_experiment_writer()
        assert isinstance(exp_writer, ew.ExperimentWriter), "Experiment writer is not inherited from ExperimentWriterType"
        self._experiment_writer = exp_writer #ew.ExperimentWriter(self._working_directory)
        self._experiment_writer.open_experiment(experiment_name)

    def close_experiment(self):
        self._send_command(pcp.ExperimentCommands.EXPERIMENT_STOPPED)
        self._experiment_writer.close_experiment()

    def open_measurement(self):
        #print("simulate open measurement")
        measurement_name = self.__exp_settings.measurement_name
        measurement_counter = self._measurement_counter
        assert isinstance(self.__exp_settings, ns.ExperimentSettings)
        self._measurement_info = mds.MeasurementInfo(measurement_name, measurement_counter, load_resistance = self.__exp_settings.load_resistance, second_amplifier_gain = self.__exp_settings.second_amp_coeff)
        #self._measurement_info.second_amplifier_gain = self.__exp_settings.second_amp_coeff
        self._send_command_with_params(pcp.ExperimentCommands.MEASUREMENT_STARTED, measurement_name = measurement_name, measurement_count = measurement_counter) 

        self._experiment_writer.open_measurement(measurement_name,measurement_counter)

    def close_measurement(self):
        #print("simulate close measurement")
        self._measurement_counter+=1
        self._send_command(pcp.ExperimentCommands.MEASUREMENT_FINISHED)
        self._spectrum_data = dict()
        

        self._experiment_writer.close_measurement()

    def send_measurement_info(self):
        self._send_command_with_param(pcp.ExperimentCommands.MEASUREMENT_INFO, self._measurement_info)

    def send_start_measurement_info(self):
        self._send_command_with_param(pcp.ExperimentCommands.MEASUREMENT_INFO_START, self._measurement_info)

    def send_end_measurement_info(self):
        self._send_command_with_param(pcp.ExperimentCommands.MEASUREMENT_INFO_END, self._measurement_info)

    def update_spectrum(self, data,rang = 0, averages = 1):
        #range numeration from 0:   0 - 0 to 1600HZ
        #                           1 - 0 to 102,4KHZ
        current_data_dict = self._spectrum_data.get(rang)
        average_data = data
        if not current_data_dict:
            self._spectrum_data[rang] = {pcp.AVERAGES: averages,pcp.DATA: data}
        else:
            current_average = current_data_dict[pcp.AVERAGES]
            current_data = current_data_dict[pcp.DATA]
            #self.average = np.average((self.average, data['p']), axis=0, weights=(self.average_counter - 1, 1))

            average_data = np.average((current_data, data),axis = 0, weights = (current_average, averages))
            current_average += averages

            self._spectrum_data[rang] = {pcp.AVERAGES: current_average,pcp.DATA: average_data}
             
        #self._spectrum_data[rang] = data
        q = self._input_data_queue
        freq = self._frequencies[rang] 
        
        result = {pcp.COMMAND: pcp.ExperimentCommands.DATA, pcp.SPECTRUM_RANGE: rang, pcp.FREQUENCIES: freq, pcp.DATA:average_data, pcp.INDEX: 1}#data, 'i': 1}
        if q:
            q.put_nowait(result) 
            
    def update_resulting_spectrum(self):
        freq, data = spectrum = self.get_resulting_spectrum()



        result = {pcp.COMMAND: pcp.ExperimentCommands.SPECTRUM_DATA, pcp.FREQUENCIES: freq, pcp.DATA: data}
        q = self._input_data_queue
        if q:
            q.put_nowait(result)

        return spectrum

    def get_resulting_spectrum(self):
        list_of_spectrum_slices = []
        list_of_frequency_slices= []
        for rng, spectrum_data in self._spectrum_data.items():
            start_idx, stop_idx = self._frequency_indexes[rng]
            data = spectrum_data[pcp.DATA][start_idx:stop_idx]
            freq = self._frequencies[rng][start_idx:stop_idx]
            list_of_spectrum_slices.append(data)
            list_of_frequency_slices.append(freq)
        result_freq = np.hstack(list_of_frequency_slices)
        result_data = np.hstack(list_of_spectrum_slices)
        data = np.vstack((result_freq,result_data))
        #if self.calibration:
        #    self.calibration.set_amplifier_gain("second_amp",self._measurement_info.second_amplifier_gain)
        #    data = self.calibration.apply_calibration(data) 

        #self._calibration.apply_calibration(data, 178, self._measurement_info.second_amplifier_gain)

        #if self._calibration:
        #    data = self._calibration.apply_calibration(data)

        return data #(result_freq,result_data)
        #frequencies = np.vstack(

    def generate_experiment_function(self):
        func = None
        print(self.__exp_settings.meas_gated_structure)
        print(self.__exp_settings.meas_characteristic_type)
        print(self.__exp_settings.use_transistor_selector)
        print(self.__exp_settings.use_automated_voltage_control)

        if not self.__exp_settings.use_automated_voltage_control:
            func = lambda: self.single_value_measurement(None,None)
        elif not self.__exp_settings.meas_gated_structure:# non gated structure measurement
            func = self.non_gated_structure_meaurement_function
        elif self.__exp_settings.meas_characteristic_type == 0: #output curve
            func = self.output_curve_measurement_function
        elif self.__exp_settings.meas_characteristic_type == 1: #transfer curve
            func = self.transfer_curve_measurement_function
        else: 
            raise AssertionError("function was not selected properly")

        if self.__exp_settings.use_transistor_selector:
            def execution_function(self):
                for transistor in self.__exp_settings.transistor_list:
                    self.switch_transistor(transistor)
                    func(self)
            self._execution_function = execution_function
        self._execution_function = func
        
    def perform_experiment(self):
        self.generate_experiment_function()
        self.open_experiment()
        self._execution_function()
        self.close_experiment()




class SimulateExperiment(Experiment):
    def __init__(self, input_data_queue = None, stop_event = None):
        Experiment.__init__(self,True, input_data_queue, stop_event)

    def initialize_hardware(self):
        print("simulating hardware init")

    def switch_transistor(self, transistor):
        print("simulating switch transistor")

    def set_front_gate_voltage(self, voltage):
        print("simulate setting fg voltage: {0}".format(voltage))
    
    def set_drain_source_voltage(self, voltage):
        print("simulate setting ds voltage: {0}".format(voltage))

    def single_value_measurement(self, drain_source_voltage, gate_voltage):
        self.open_measurement()
        print("simulating single measurement vds:{0} vg:{1}".format(drain_source_voltage, gate_voltage))
        #self.send_measurement_info()
        self._measurement_info.start_sample_voltage = np.random.random_sample()
        self._measurement_info.start_main_voltage = np.random.random_sample()
        
        self.send_start_measurement_info()

        counter = 0
        max_counter = 100
        
        while counter < max_counter: #(not need_exit()) and counter < max_counter:
            data = 10**-3 * np.random.random(1600)
            self.update_spectrum(data,0)
            self.update_spectrum(data,1)
            counter+=1
            time.sleep(0.02)
        
        #frequency, spectrum = self.update_resulting_spectrum()
        data = self.update_resulting_spectrum()
        #data = np.vstack(self.update_resulting_spectrum()).transpose()
        #freq,spectrum = np.vstack(self.update_resulting_spectrum()).transpose()
        

        data = data.transpose()
        self._experiment_writer.write_measurement(data)   ##.write_measurement()
        self._experiment_writer.write_measurement_info(self._measurement_info)
        #self.get_resulting_spectrum()
        #self.send_measurement_info()
        self._measurement_info.end_sample_voltage = np.random.random_sample()
        self._measurement_info.end_main_voltage = np.random.random_sample()
        
        self.send_end_measurement_info()
        
        self.close_measurement()

    def non_gated_single_value_measurement(self, drain_source_voltage):
        self.open_measurement()
        print("simulating non gated single measurement vds:{0}".format(drain_source_voltage))
        self.close_measurement()