import os
import time
import math

import numpy as np
import calibration as calib
import modern_fans_controller as mfans
#import modern_agilent_u2542a as mdaq
import modern_fans_smu as msmu
import temperature_controller as tc


from multiprocessing import Process, Event
from scipy.signal import periodogram
from scipy.signal import decimate

from fans_hardware_settings import HardwareSettings
from fans_experiment_settings import ExperimentSettings

import modern_fans_experiment_writer as mfew
import pickle
import process_communication_protocol as pcp
import experiment_writer as ew
import measurement_data_structures as mds
#def get_fans_ai_channels_from_number(number):
#    assert isinstance(number, int), "Number should be integer"
#    assert (number>0 and number<9),"Wrong channel number!"
#    return mfans.FANS_AI_CHANNELS(number)

#def get_fans_ao_channels_from_number(number):
#    assert isinstance(number, int), "Number should be integer"
#    assert (number>0 and number<17),"Wrong channel number!"
#    return mfans.FANS_AO_CHANNELS(number)

class StopExperiment(Exception):
    pass


class Experiment:
    def __init__(self, simulate = False, input_data_queue = None, stop_event = None):
        #self.__config = None
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

    #@property
    #def configuration(self):
    #    return self.__config

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


    def initialize_settings(self, experiment_settings, hardware_settings):
        assert isinstance(experiment_settings, ExperimentSettings)
        self.__exp_settings = experiment_settings #configuration.get_node_from_path("Settings.ExperimentSettings")
        
        assert isinstance(hardware_settings, HardwareSettings)
        self.__hardware_settings = hardware_settings
        
        self._working_directory = self.__exp_settings.working_directory
        

    def initialize_hardware(self):
        raise NotImplementedError()

    def create_calibration(self):
        raise NotImplementedError()

    def initialize_calibration(self):
        self._calibration = self.create_calibration()
        #dir = os.path.dirname(__file__)
        #self._calibration = self.create_calibration(dir)
        #self._calibration = calib.Calibration(os.path.join(dir,"calibration_data"))
        #self._calibration = calib.CalibrationSimple(os.path.join(dir,"calibration_data"))
        #self._calibration.init_values()
        #pass
    
    #def assert_need_exit(self):
    #    if self.need_exit:
    #        raise StopExperiment("Experiment stop was raised")

    def get_meas_ranges(self):
        fg_range = self.experiment_settings.vfg_range
        ds_range = self.experiment_settings.vds_range
        #fg_range = self.__config.get_node_from_path("front_gate_range")
        #if self.__exp_settings.use_set_vfg_range:
        #    assert isinstance(fg_range, ns.ValueRange)
        #ds_range = self.__config.get_node_from_path("drain_source_range")
        #if self.__exp_settings.use_set_vds_range:
        #    assert isinstance(fg_range, ns.ValueRange)
        return (ds_range, fg_range)

    def output_curve_measurement_function(self):
        try:
            ds_range, fg_range = self.get_meas_ranges()
        
            if (not self.__exp_settings.use_set_vfg_range) and (not self.__exp_settings.use_set_vds_range) and (not self.need_exit):
                self.single_value_measurement(self.__exp_settings.drain_source_voltage,self.__exp_settings.front_gate_voltage)

            elif self.__exp_settings.use_set_vds_range and self.__exp_settings.use_set_vfg_range and (not self.need_exit):
                for vfg in fg_range: #fg_range.get_range_handler():
                    if self.need_exit:
                        return
                    for vds in ds_range:  #.get_range_handler():
                        if self.need_exit:
                            return
                        self.single_value_measurement(vds, vfg)
           
            elif not self.__exp_settings.use_set_vfg_range:
                for vds in ds_range: #.get_range_handler():
                    if self.need_exit:
                        return
                    self.single_value_measurement(vds, self.__exp_settings.front_gate_voltage)
                    
            elif not self.__exp_settings.use_set_vds_range:
                for vfg in fg_range: #.get_range_handler():
                    if self.need_exit:
                        return
                    self.single_value_measurement(self.__exp_settings.drain_source_voltage, vfg)
            else:
                raise ValueError("range handlers are not properly defined")

        except StopExperiment:
            print("Stop experiment exception raised")
        except Exception as exc:
            print(str(exc))
            #pass
        finally:
            self.set_voltages_to_zero()


    def transfer_curve_measurement_function(self):
        try:
            ds_range, fg_range = self.get_meas_ranges()
            if (not self.__exp_settings.use_set_vds_range) and (not self.__exp_settings.use_set_vfg_range) and not self.need_exit:
                 self.single_value_measurement(self.__exp_settings.drain_source_voltage,self.__exp_settings.front_gate_voltage)

            elif self.__exp_settings.use_set_vds_range and self.__exp_settings.use_set_vfg_range:
                for vds in ds_range: #.get_range_handler():
                    if self.need_exit:
                        return
                    for vfg in fg_range: #.get_range_handler():
                        if self.need_exit:
                            return
                        self.single_value_measurement(vds, vfg)
           
            elif not self.__exp_settings.use_set_vfg_range:
                for vds in ds_range: #.get_range_handler():
                    if self.need_exit:
                        return
                    self.single_value_measurement(vds, self.__exp_settings.front_gate_voltage)
                    
            elif not self.__exp_settings.use_set_vds_range:
                 for vfg in fg_range: #.get_range_handler():
                     if self.need_exit:
                        return
                     self.single_value_measurement(self.__exp_settings.drain_source_voltage, vfg)
            else:
                raise ValueError("range handlers are not properly defined")

        except StopExperiment:
            print("Stop experiment exception raised")
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
        except StopExperiment:
            print("Stop experiment exception raised")
        except:
            pass
        finally:
            self.set_drain_source_voltage(0)

        
    def set_voltages_to_zero(self):
        #print("setting to zero is off")
        print("Setting DS to 0")
        self.set_drain_source_voltage(0)
        print("Setting GS to 0")
        self.set_front_gate_voltage(0)
        print("Setting 0 completed!")


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

    def assert_experiment_abort(self):
        if self.need_exit:
            raise StopExperiment()
        #raise NotImplementedError()

    def report_progress(self, progress):
        raise NotImplementedError()

    ##replace name to prepare_single_value_measurement
    def single_value_measurement(self, drain_source_voltage, gate_voltage):
        #if self.need_exit:
        #    return
        self.assert_experiment_abort()

        # utilize here with statement to be sure all files are properly opened and closed
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
        self.assert_experiment_abort()
        #self.assert_need_exit()
        #if self.need_exit:
        #    return
        self.open_measurement()
        
        if self.experiment_settings.use_automated_voltage_control:
            self.prepare_to_set_voltages()
            self.set_drain_source_voltage(drain_source_voltage)
        
        self.prepare_to_measure_voltages()
        self.perform_start_param_measurement()
        self.prepare_to_measure_spectrum()
        self.perform_single_value_measurement()
        #self.perform_non_gated_single_value_measurement()
        self.perform_end_param_measurement()
        self.save_measurement_info()
        self.close_measurement()

    def send_progress_changed(self, progress_value):
        print("Progress changed: {0}".format(progress_value))
        self._send_command_with_param(pcp.ExperimentCommands.PROGRESS_CHANGED, progress_value)

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
        self._send_command(pcp.ExperimentCommands.EXPERIMENT_FINISHED)
        self._experiment_writer.close_experiment()

    def open_measurement(self):
        #print("simulate open measurement")
        measurement_name = self.__exp_settings.measurement_name
        measurement_counter = self._measurement_counter
        assert isinstance(self.__exp_settings, ExperimentSettings)
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
        #data = np.vstack((result_freq,result_data))
        
        if self.calibration:
            result_data = self.calibration.apply_calibration(result_data)

        data = np.vstack((result_freq,result_data))
        
        return data 
        

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

class FANSExperiment(Experiment):
    def __init__(self, input_data_queue = None, stop_event = None):
        super().__init__(False, input_data_queue, stop_event)
        self._spectrum_ranges = {0: (0,5000,1),1:(0,250000,10)}
        self._spectrum_linking_frequencies = {0:(1,3000),1:(3000,250000)}
        self._frequencies = self._get_frequencies(self._spectrum_ranges)
        self._frequency_indexes = self._get_frequency_linking_indexes(self._spectrum_ranges, self._spectrum_linking_frequencies)
        self._max_timetrace_length = -1 # -1 - means all data, 0 - means no data, number means number seconds


         
    def initialize_hardware(self):
        resource = self.hardware_settings.fans_controller_resource
        self.fans_controller = mfans.FANS_CONTROLLER(resource)

        sample_motor_pin = self.hardware_settings.sample_motor_channel #get_fans_ao_channels_from_number(self.hardware_settings.sample_motor_channel)
        gate_motor_pin = self.hardware_settings.gate_motor_channel #get_fans_ao_channels_from_number(self.hardware_settings.gate_motor_channel)
        sample_relay = self.hardware_settings.sample_relay_channel #get_fans_ao_channels_from_number(self.hardware_settings.sample_relay_channel)
        gate_relay = self.hardware_settings.gate_relay_channel #get_fans_ao_channels_from_number(self.hardware_settings.gate_relay_channel)

        sample_feedback_pin = self.hardware_settings.sample_feedback_channel  #mfans.FANS_AI_CHANNELS.AI_CH_6
        gate_feedback_pin = self.hardware_settings.gate_feedback_channel #mfans.FANS_AI_CHANNELS.AI_CH_8
        main_feedback_pin = self.hardware_settings.main_feedback_channel #mfans.FANS_AI_CHANNELS.AI_CH_7
        self.acquistion_channel = self.hardware_settings.acquisition_channel #mfans.FANS_AI_CHANNELS.AI_CH_1 ### here should be 1

        drain_source_voltage_switch_channel = mfans.FANS_AO_CHANNELS.AO_CH_10

        self.load_resistance = self.experiment_settings.load_resistance
        self.sample_rate = 500000
        self.points_per_shot = 50000
        #self.fans_smu = msmu.FANS_SMU_PID(self.fans_controller, sample_motor_pin, sample_relay, sample_feedback_pin, gate_motor_pin, gate_relay, gate_feedback_pin, main_feedback_pin, drain_source_voltage_switch_channel)
        self.fans_smu = msmu.FANS_SMU_Specialized(self.fans_controller, sample_motor_pin, sample_relay, sample_feedback_pin, gate_motor_pin, gate_relay, gate_feedback_pin, main_feedback_pin, drain_source_voltage_switch_channel)
        self.fans_smu.set_smu_parameters(100, self.load_resistance)

        self.fans_acquisition = mfans.FANS_ACQUISITION(self.fans_controller)
        self.temperature_controller = tc.LakeShore211TemperatureSensor("COM9")
     
    def create_calibration(self):
        dir = os.path.join(os.path.dirname(__file__), "calibration_data")
        calibration = calib.FANSCalibration(dir)
        calibration.second_amplifier_gain = self.experiment_settings.second_amp_coeff
        calibration.initialize_calibration()
        return calibration

    def create_experiment_writer(self):
        return mfew.FANSExperimentWriter(self._working_directory, sample_rate = self.sample_rate)
            
    def prepare_to_set_voltages(self):
        self.fans_smu.init_smu_mode()

    def prepare_to_measure_voltages(self):
        self.fans_smu.init_smu_mode()
        self.wait_for_stabilization_after_switch(10)
    
    

    def prepare_to_measure_spectrum(self):
        self.fans_acquisition.initialize_acquisition(self.acquistion_channel, mfans.FILTER_CUTOFF_FREQUENCIES.F150, mfans.FILTER_GAINS.G1, mfans.PGA_GAINS.PGA_1)
        self.fans_acquisition.initialize_acquisition_params(self.sample_rate, self.points_per_shot, mfans.ACQUISITION_TYPE.CONT) 
        #switch off all output to the control circuit in order to reduce noiseness of the system
        self.fans_controller.switch_all_fans_output_state(mfans.SWITCH_STATES.OFF)

        #HARDCODE
        ch = self.fans_controller.get_fans_output_channel(mfans.FANS_AO_CHANNELS.AO_CH_7)
        ch.analog_write(8.4)
        time.sleep(5)
        ch.analog_write(0)

        # drain_source_switch_channel.analog_write(self._drain_source_switch_voltage)
        #print ("stabilizing voltages after drain switch on. waiting...")
        #time.sleep(5)
        #result = super().read_all_test() 
        #drain_source_switch_channel.analog_write(0)

        self.wait_for_stabilization_after_switch(30)

    def prepare_to_measure_timetrace(self):
        return super().prepare_to_measure_timetrace()

    def perform_param_measurement(self):
        (sample_voltage,main_voltage, gate_voltage) = self.fans_smu.read_feedback_voltages()
        
        temperature = self.temperature_controller.temperature
        return (sample_voltage,main_voltage, gate_voltage, temperature)

    def perform_start_param_measurement(self):
        sample_voltage,main_voltage, gate_voltage, temperature = self.perform_param_measurement()
        self._measurement_info.update_start_values(main_voltage, sample_voltage, gate_voltage,temperature)
        self.send_start_measurement_info()
        
    def perform_end_param_measurement(self):
        sample_voltage,main_voltage, gate_voltage, temperature = self.perform_param_measurement()
        self._measurement_info.update_end_values(main_voltage, sample_voltage, gate_voltage,temperature)
        self.send_end_measurement_info()

    

    def perform_single_value_measurement(self):
        assert isinstance(self.experiment_settings, ExperimentSettings)
        
        screen_update = self.experiment_settings.display_refresh  #10;
        total_averaging = self.experiment_settings.averages;
        adc = self.fans_acquisition
        
        fs = self.sample_rate
        npoints = self.points_per_shot

        seconds_counter = 0.0
        max_seconds_to_write = self._max_timetrace_length
        time_step_sec = npoints * 1.0 / fs

        write_timetrace_confition = lambda: False
        if max_seconds_to_write < 0:
            write_timetrace_confition = lambda: True
        elif max_seconds_to_write == 0:
            write_timetrace_confition = lambda: False
        else: 
            write_timetrace_confition = lambda: seconds_counter < max_seconds_to_write

        counter = 0
        read_data = adc.read_acquisition_data_when_ready

        f1_max = 3000
        new_fs = 10000
        decimation_factor = int(fs / new_fs)
        new_fs = int(fs/ decimation_factor)
        total_array = np.zeros((1,fs))
        total_array = np.zeros(fs)

        df1 = 1
        df2 = fs / npoints

        freq1_idx = math.floor(f1_max/df1)+1
        freq2_idx = math.ceil(f1_max/df2)+1

        second_range = None
        first_range = None
        freq_2 = None
        freq_1 = None
        #f1_aver_counter = 0
        f2_aver_counter = 0
        fill_value = 0

        adc.start()
        
        while counter < total_averaging:
            try:
                
                #f2_aver_counter += 1
                new_fill_value = fill_value + npoints
                data = read_data()[0]
                total_array[fill_value:new_fill_value] = data
                fill_value = new_fill_value

                f, psd = periodogram(data, fs)
                self.update_spectrum(psd,1,1)

                if new_fill_value % fs == 0:
                    decimated = decimate(total_array,decimation_factor,n=8,ftype="iir",axis = 0 ,zero_phase=True)
                    f, psd = periodogram(decimated, new_fs)
                    self.update_spectrum(psd, 0,1)
                    fill_value = 0
                    counter+=1
               
                if write_timetrace_confition() :
                    self._experiment_writer.write_timetrace_data(data)
                    seconds_counter += time_step_sec

            except Exception as e:
                print(e)
                break
        adc.stop()
        data = self.update_resulting_spectrum()
        data = data.transpose()
        self._experiment_writer.write_measurement(data)

        adc.clear_buffer()

    
    def perform_non_gated_single_value_measurement(self):
        return super().perform_non_gated_single_value_measurement()

    def switch_transistor(self, transistor):
        return super().switch_transistor(transistor)

    def set_front_gate_voltage(self, voltage):
        print("setting gate voltage")
        self.fans_smu.smu_set_gate_voltage(voltage)

    def set_drain_source_voltage(self, voltage):
        print("setting drain voltage")
        self.fans_smu.smu_set_drain_source_voltage(voltage)

class LoggingQueuedStream:
    def __init__(self, data_queue = None):
        self._log_queue = data_queue

    def write(self, txt, skip_new_line = True):
        if (txt != '\n') and skip_new_line:
            if self._log_queue:
                self._log_queue.put_nowait({pcp.COMMAND:pcp.ExperimentCommands.LOG_MESSAGE, pcp.PARAMETER:txt})
        
    def flush(self):
        pass

class ExperimentHandler(Process):
    def __init__(self, input_data_queue = None, experiment_settings = None, hardware_settings = None):
        super().__init__()
        self._exit = Event()
        self._experiment  = None
        self._input_data_queue = input_data_queue
        
        assert isinstance(hardware_settings, HardwareSettings)
        self._hardware_settings = hardware_settings

        assert isinstance(experiment_settings, ExperimentSettings)
        self._experiment_settings = experiment_settings

    def stop(self):
        self._exit.set()

    def run(self):
        #if self._input_data_queue:
        #sys.stdout = LoggingQueuedStream(self._input_data_queue) #open("log.txt", "w")
        #else:
        #    sys.stdout = open("log.txt", "w")

        simulate = self._experiment_settings.simulate_experiment

        if simulate:
            self._experiment = SimulateExperiment(self._input_data_queue, self._exit)
        else:
            #self._experiment = PerformExperiment(self._input_data_queue, self._exit)
            experiment = self.get_experiment()
            #assert isinstance(exp.Experiment), "Experiment has wrong type"
            assert isinstance(experiment, Experiment), "Experiment is not inherited from Experiment type"
            self._experiment = experiment #mfe.FANSExperiment(self._input_data_queue, self._exit)
        
        self._experiment.initialize_settings(self._experiment_settings, self._hardware_settings)
        self._experiment.initialize_hardware()
        self._experiment.initialize_calibration()
        self._experiment.perform_experiment()

    def get_experiment(self):
        raise NotImplementedError()

class FANSExperimentHandler(ExperimentHandler):
    def __init__(self, input_data_queue = None, experiment_settings = None, hardware_settings = None ):
        super().__init__(input_data_queue, experiment_settings, hardware_settings)
        
    def get_experiment(self):
        return FANSExperiment(self._input_data_queue, self._exit)

__settings_filename__ = "settings.cfg"
def load_settings_from_file():
        if not os.path.isfile(__settings_filename__):
            print("creating new settings")
            experiment_settings = ExperimentSettings()
            hardware_settings = HardwareSettings()
            return (experiment_settings, hardware_settings)
        else:
            print("loading settings from file")
            with open(__settings_filename__,"rb") as f:
                settings = pickle.load(f)
                return settings


if __name__ == "__main__":
    settings = load_settings_from_file()
    
    handl = FANSExperimentHandler(None, settings[0], settings[1])
    handl.run()