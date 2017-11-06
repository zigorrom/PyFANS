import sys
import os
from nodes import ExperimentSettings, ValueRange, HardwareSettings
from configuration import Configuration
from hp34401a_multimeter import HP34401A,HP34401A_FUNCTIONS
from hp35670a_dsa import HP3567A, HP35670A_MODES,HP35670A_CALC, HP35670A_TRACES,HP35670A_INPUTS
from arduino_controller import ArduinoController
from fans_smu import HybridSMU_System
from fans_controller import FANS_AO_channel, FANS_CONTROLLER
from fans_constants import *
from hp35670a_dsa import HP3567A, VoltageMeasurementSwitch
from temperature_controller import LakeShore211TemperatureSensor

from motorized_potentiometer import MotorizedPotentiometer
import numpy as np
from n_enum import enum
from PyQt4 import QtCore
from os.path import join

import pyqtgraph as pg
from multiprocessing import JoinableQueue
from multiprocessing import Process
from multiprocessing import Event
import multiprocessing
from collections import deque
from plot import SpectrumPlotWidget
import time
import math

from measurement_data_structures import MeasurementInfo
from experiment_writer import ExperimentWriter
from process_communication_protocol import *
from calibration import Calibration, CalibrationSimple


class ExperimentController(QtCore.QObject):
    def __init__(self, spectrum_plot=None, timetrace_plot=None, status_object = None, measurement_ranges = {0: (0,1600,1),1:(0,102400,64)},  parent = None):
        super().__init__(parent)
        if spectrum_plot:
            assert isinstance(spectrum_plot, SpectrumPlotWidget)
        self._spectrum_plot = spectrum_plot
        #self._spectrum_plot
        self._running = False

        self._visualization_deque = deque(maxlen = 100)
        self._input_data_queue = JoinableQueue()

        self._status_object = status_object

        ## pass configuration to threads

        self._processing_thread = None # ProcessingThread(self._input_data_queue, self._visualization_deque)
        self._experiment_thread = None # Experiment(self._input_data_queue)

        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.setInterval(20)
        self._refresh_timer.timeout.connect(self._update_gui)
        self._counter = 0

    def __init_process_thread(self):
        self._processing_thread = ProcessingThread(self._input_data_queue, self._visualization_deque)
        self._processing_thread.experimentStarted.connect(self._on_experiment_started)
        self._processing_thread.experimentFinished.connect(self._on_experiment_finished)
        self._processing_thread.measurementStarted.connect(self._on_measurement_started)
        self._processing_thread.measurementFinished.connect(self._on_measurement_finished)
        #self._processing_thread.measurementDataArrived.connect(self._on_measurement_info_arrived)

        self._processing_thread.startMeasurementDataArrived.connect(self._on_start_measurement_info_received)
        self._processing_thread.endMeasurementDataArrived.connect(self._on_end_measurement_info_received)
        
        self._processing_thread.resulting_spectrum_update.connect(self._on_update_resulting_spectrum)
        self._processing_thread.log_message_received.connect(self._on_log_message_received)

        self._processing_thread.commandReceived.connect(self._command_received)

    def __init_experiment_thread(self):
        #self._experiment_thread = ExperimentHandler(self._input_data_queue) #ExperimentProcess(self._input_data_queue,True)
        self._experiment_thread = ExperimentHandler(self._input_data_queue) #ExperimentProcess(self._input_data_queue,True)

    def _command_received(self,cmd):
        self._status_object.send_message("Command received: {0}".format(ExperimentCommands[cmd]))

    def _on_log_message_received(self, message):
        if message:
            print("received log message")
            print(message)
            self._status_object.send_message(message)

    def _on_experiment_started(self, params): #experiment_name = "", **kwargs):
        
        experiment_name = params.get("experiment_name")
        msg = "Experiment \"{0}\" started".format(experiment_name)
        print(msg)
        self._status_object.send_message(msg)
        self._status_object.send_multiple_param_changed(params)

    def _on_experiment_finished(self):
        print("Experiment finished")
        self.stop()

    def _on_measurement_started(self,  params):
        measurement_name = params.get("measurement_name")
        measurement_count = params.get("measurement_count")
        msg = "Measurement \"{0}:{1}\" started".format(measurement_name, measurement_count)
        print(msg)
        self._status_object.send_message(msg)
        self._status_object.send_multiple_param_changed(params)

    def _on_measurement_finished(self):
        print("Measurement finished")

    def _on_start_measurement_info_received(self,measurement_info):
        print("start measurement_info_arrived")
        self._status_object.send_refresh_measurement_start_data(measurement_info)

    def _on_end_measurement_info_received(self,measurement_info):
        print("end measurement_info_arrived")
        self._status_object.send_refresh_measurement_end_data(measurement_info)

    #def _on_measurement_info_arrived(self,measurement_info):
    #    print("measurement_info_arrived")
    #    self._status_object.send_measurement_info_changed(measurement_info)
    #    #if isinstance(data_dict, dict):
        #    for k,v in data_dict.items():
                #self._status_object.send_value_changed(k,v)

    def _on_update_resulting_spectrum(self,data):
        frequency = data[FREQUENCIES]
        spectrum_data = data[DATA]
        self._spectrum_plot.updata_resulting_spectrum(frequency,spectrum_data)


    def _update_gui(self):
        try:
            #print("refreshing: {0}".format(self._counter))
            self._counter+=1
            data = self._visualization_deque.popleft()
            cmd_format = "{0} command received"

            cmd = data.get(COMMAND)
            #print(cmd_format.format(ExperimentCommands[cmd]))
            
            if cmd is ExperimentCommands.DATA:
                index = data[INDEX]
                rang = data[SPECTRUM_RANGE]
                #print("visualized data index: {0}".format(index))
                self._spectrum_plot.update_spectrum(rang ,data)
           
                #self._spectrum_plot
            
        except Exception as e:
            pass
            #print(str(e))

    def start(self):
        if self._running:
            return
        self.__init_process_thread()
        self.__init_experiment_thread()
        self._refresh_timer.start()
        self._experiment_thread.start()
        self._processing_thread.start()
        self._running = True

    def stop(self):
        if not self._running:
            return
        self._refresh_timer.stop()
        self._experiment_thread.stop()
        self._experiment_thread.join()
        self._input_data_queue.join()
        #self._input_data_queue
        self._processing_thread.stop()
        self._running = False

class ProcessingThread(QtCore.QThread):
    
    threadStarted = QtCore.pyqtSignal()
    threadStopped = QtCore.pyqtSignal()
    commandReceived = QtCore.pyqtSignal(int)
    experimentStarted = QtCore.pyqtSignal(dict)
    experimentFinished = QtCore.pyqtSignal()
    measurementStarted = QtCore.pyqtSignal(dict)
    measurementFinished = QtCore.pyqtSignal()
    measurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    startMeasurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    endMeasurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    resulting_spectrum_update = QtCore.pyqtSignal(dict)
    log_message_received = QtCore.pyqtSignal(str)

    def __init__(self, input_data_queue = None,visualization_queue = None, parent = None):
        super().__init__(parent)
        self.alive = False
        assert isinstance(visualization_queue, deque)
        self._visualization_queue = visualization_queue
        #assert isinstance(input_data_queue, JoinableQueue)
        self._input_data_queue = input_data_queue

    def stop(self):
        self.alive = False
        self.wait()

    def run(self):
        self.alive = True
        #while self.alive
        while self.alive or (not self._input_data_queue.empty()):
            try:
                data = self._input_data_queue.get(timeout = 1)
                self._input_data_queue.task_done()
                cmd_format = "{0} command received"
                cmd = data.get(COMMAND)
                param = data.get(PARAMETER)
                
                #print(cmd_format.format(ExperimentCommands[cmd]))
                if cmd is None:
                    continue
                elif cmd is ExperimentCommands.EXPERIMENT_STARTED:
                    self.commandReceived.emit(ExperimentCommands.EXPERIMENT_STARTED)
                    self.experimentStarted.emit(param)
                    continue

                elif cmd is ExperimentCommands.EXPERIMENT_STOPPED:
                    self.alive = False
                    self.commandReceived.emit(ExperimentCommands.EXPERIMENT_STOPPED)
                    self.experimentFinished.emit()
                    break

                elif cmd is ExperimentCommands.MEASUREMENT_STARTED:
                    self.commandReceived.emit(ExperimentCommands.MEASUREMENT_STARTED)
                    self.measurementStarted.emit(param)
                    continue

                elif cmd is ExperimentCommands.MEASUREMENT_FINISHED:
                    self.commandReceived.emit(ExperimentCommands.MEASUREMENT_FINISHED)
                    self.measurementFinished.emit()
                    continue

                elif cmd is ExperimentCommands.MEASUREMENT_INFO:
                    self.measurementDataArrived.emit(param)

                elif cmd is ExperimentCommands.MEASUREMENT_INFO_START:
                    self.startMeasurementDataArrived.emit(param)

                elif cmd is ExperimentCommands.MEASUREMENT_INFO_END:
                    self.endMeasurementDataArrived.emit(param)

                elif cmd is ExperimentCommands.DATA:
                    self._visualization_queue.append(data)   
                     
                elif cmd is ExperimentCommands.SPECTRUM_DATA:
                    self.resulting_spectrum_update.emit(data)
                
                elif cmd is ExperimentCommands.LOG_MESSAGE:
                    self.log_message_received.emit(param)



            except EOFError as e:
                print(str(e))
                break
            except:
                pass

        self.alive = False

#ExperimentCommands = enum("EXPERIMENT_STARTED","EXPERIMENT_STOPPED","DATA","MESSAGE", "MEASUREMENT_STARTED", "MEASUREMENT_FINISHED", "SPECTRUM_DATA", "TIMETRACE_DATA","EXPERIMENT_INFO", "MEASUREMENT_INFO", "ABORT", "ERROR")
MeasurementTypes = enum("spectrum", "timetrace", "time_spectrum")


class LoggingQueuedStream:
    def __init__(self, data_queue = None):
        self._log_queue = data_queue

    def write(self, txt, skip_new_line = True):
        if (txt != '\n') and skip_new_line:
            if self._log_queue:
                self._log_queue.put_nowait({COMMAND:ExperimentCommands.LOG_MESSAGE, PARAMETER:txt})
        
    def flush(self):
        pass


class ExperimentHandler(Process):
    def __init__(self, input_data_queue = None):
        super().__init__()
        self._exit = Event()
        self._experiment  = None
        self._input_data_queue = input_data_queue

    def stop(self):
        self._exit.set()

    def run(self):
        #if self._input_data_queue:
        sys.stdout = LoggingQueuedStream(self._input_data_queue) #open("log.txt", "w")
        #else:
        #    sys.stdout = open("log.txt", "w")

        cfg = Configuration()
        exp_settings = cfg.get_node_from_path("Settings.ExperimentSettings")
        assert isinstance(exp_settings, ExperimentSettings)
        simulate = exp_settings.simulate_experiment

        if simulate:
            self._experiment = SimulateExperiment(self._input_data_queue, self._exit)
        else:
            #self._experiment = PerformExperiment(self._input_data_queue, self._exit)
            self._experiment = mfe.FANSExperiment(self._input_data_queue, self._exit)
        
        self._experiment.initialize_settings(cfg)
        self._experiment.initialize_hardware()
        self._experiment.initialize_calibration()
        self._experiment.perform_experiment()

class Measurement:
    def __init__(self):
        pass

    def new_measurement(self):
        pass

    

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
        assert isinstance(configuration, Configuration)
        self.__exp_settings = configuration.get_node_from_path("Settings.ExperimentSettings")
        assert isinstance(self.__exp_settings, ExperimentSettings)
        self.__hardware_settings = configuration.get_node_from_path("Settings.HardwareSettings")
        assert isinstance(self.__hardware_settings, HardwareSettings)
        self._working_directory = self.__exp_settings.working_directory
        
        #self._data_handler = DataHandler(self._working_directory,input_data_queue = self._input_data_queue)

    def initialize_hardware(self):
        if self.__exp_settings.use_transistor_selector or self.__exp_settings.use_automated_voltage_control:
            self.__arduino_controller = ArduinoController(self.__hardware_settings.arduino_controller_resource)

        self.__dynamic_signal_analyzer = HP3567A(self.__hardware_settings.dsa_resource)
        self.__sample_multimeter = HP34401A(self.__hardware_settings.sample_multimeter_resource)
        self.__main_gate_multimeter = HP34401A(self.__hardware_settings.main_gate_multimeter_resource)
    
    def initialize_calibration(self):
        dir = os.path.dirname(__file__)
        #self._calibration = Calibration(os.path.join(dir,"calibration_data"))
        self._calibration = CalibrationSimple(os.path.join(dir,"calibration_data"))
        self._calibration.init_values()
   

    def get_meas_ranges(self):
        fg_range = self.__config.get_node_from_path("front_gate_range")
        if self.__exp_settings.use_set_vfg_range:
            assert isinstance(fg_range, ValueRange)
        ds_range = self.__config.get_node_from_path("drain_source_range")
        if self.__exp_settings.use_set_vds_range:
            assert isinstance(fg_range, ValueRange)
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
            q.put_nowait({'c': command})

    def _send_command_with_param(self,command,param):
        q = self._input_data_queue
        if q:
            q.put_nowait({COMMAND:command, PARAMETER:param})

    def _send_command_with_params(self,command, **kwargs):
        q = self._input_data_queue
        params = {COMMAND: command}
        if kwargs:
            params[PARAMETER] = kwargs
        #params.update(kwargs)
        if q:
            q.put_nowait(params)   

    def open_experiment(self):
        experiment_name = self.__exp_settings.experiment_name
        self._send_command_with_params(ExperimentCommands.EXPERIMENT_STARTED, experiment_name = experiment_name)
        self._measurement_counter = self.__exp_settings.measurement_count
        self._experiment_writer = ExperimentWriter(self._working_directory)
        self._experiment_writer.open_experiment(experiment_name)

    def close_experiment(self):
        self._send_command(ExperimentCommands.EXPERIMENT_STOPPED)
        self._experiment_writer.close_experiment()

    def open_measurement(self):
        #print("simulate open measurement")
        measurement_name = self.__exp_settings.measurement_name
        measurement_counter = self._measurement_counter
        assert isinstance(self.__exp_settings, ExperimentSettings)
        self._measurement_info = MeasurementInfo(measurement_name, measurement_counter, load_resistance = self.__exp_settings.load_resistance, second_amplifier_gain = self.__exp_settings.second_amp_coeff)
        #self._measurement_info.second_amplifier_gain = self.__exp_settings.second_amp_coeff
        self._send_command_with_params(ExperimentCommands.MEASUREMENT_STARTED, measurement_name = measurement_name, measurement_count = measurement_counter) 

        self._experiment_writer.open_measurement(measurement_name,measurement_counter)

    def close_measurement(self):
        #print("simulate close measurement")
        self._measurement_counter+=1
        self._send_command(ExperimentCommands.MEASUREMENT_FINISHED)
        self._spectrum_data = dict()
        

        self._experiment_writer.close_measurement()

    def send_measurement_info(self):
        self._send_command_with_param(ExperimentCommands.MEASUREMENT_INFO, self._measurement_info)

    def send_start_measurement_info(self):
        self._send_command_with_param(ExperimentCommands.MEASUREMENT_INFO_START, self._measurement_info)

    def send_end_measurement_info(self):
        self._send_command_with_param(ExperimentCommands.MEASUREMENT_INFO_END, self._measurement_info)

    def update_spectrum(self, data,rang = 0, averages = 1):
        #range numeration from 0:   0 - 0 to 1600HZ
        #                           1 - 0 to 102,4KHZ
        current_data_dict = self._spectrum_data.get(rang)
        average_data = data
        if not current_data_dict:
            self._spectrum_data[rang] = {AVERAGES: averages,DATA: data}
        else:
            current_average = current_data_dict[AVERAGES]
            current_data = current_data_dict[DATA]
            #self.average = np.average((self.average, data['p']), axis=0, weights=(self.average_counter - 1, 1))

            average_data = np.average((current_data, data),axis = 0, weights = (current_average, averages))
            current_average += averages

            self._spectrum_data[rang] = {AVERAGES: current_average,DATA: average_data}
             
        #self._spectrum_data[rang] = data
        q = self._input_data_queue
        freq = self._frequencies[rang] 
        
        result = {COMMAND: ExperimentCommands.DATA, SPECTRUM_RANGE: rang, FREQUENCIES: freq, DATA:average_data, INDEX: 1}#data, 'i': 1}
        if q:
            q.put_nowait(result) 
            
    def update_resulting_spectrum(self):
        freq, data = spectrum = self.get_resulting_spectrum()



        result = {COMMAND: ExperimentCommands.SPECTRUM_DATA, FREQUENCIES: freq, DATA: data}
        q = self._input_data_queue
        if q:
            q.put_nowait(result)

        return spectrum

    def get_resulting_spectrum(self):
        list_of_spectrum_slices = []
        list_of_frequency_slices= []
        for rng, spectrum_data in self._spectrum_data.items():
            start_idx, stop_idx = self._frequency_indexes[rng]
            data = spectrum_data[DATA][start_idx:stop_idx]
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

####
####this import should be after experiment class since it is required in modern_fans_experiment for import 
import modern_fans_experiment as mfe

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





class PerformExperiment(Experiment):
    def __init__(self, input_data_queue = None, stop_event = None):
        Experiment.__init__(self,False, input_data_queue, stop_event)  

    def initialize_hardware(self):
        assert isinstance(self.hardware_settings, HardwareSettings)

        resource = self.hardware_settings.fans_controller_resource
        #resource =  "USB0::0x0957::0x1718::TW52524501::INSTR"    #self._gpib_resources[selected_resource]
        self._fans_controller = FANS_CONTROLLER(resource)
        resource = self.hardware_settings.main_sample_multimeter_resource
        #resource = "GPIB0::23::INSTR" #self._gpib_resources[selected_resource]
        self.ds_mult = HP34401A(resource)
        resource = self.hardware_settings.gate_multimeter_resource
        self.gs_mult = HP34401A(resource)

        sample_motor_pin = get_ao_box_channel_from_number(self.hardware_settings.sample_motor_channel)
        gate_motor_pin = get_ao_box_channel_from_number(self.hardware_settings.gate_motor_channel)
        sample_relay = get_ao_box_channel_from_number(self.hardware_settings.sample_relay_channel)
        gate_relay = get_ao_box_channel_from_number(self.hardware_settings.gate_relay_channel)

        self._fans_smu = HybridSMU_System(self._fans_controller, AO_BOX_CHANNELS.ao_ch_1, AO_BOX_CHANNELS.ao_ch_4, self.ds_mult, AO_BOX_CHANNELS.ao_ch_9, AO_BOX_CHANNELS.ao_ch_12, self.gs_mult, self.ds_mult, 5000)
        #self._fans_smu = ManualSMU(self._fans_controller, AO_BOX_CHANNELS.ao_ch_1, AO_BOX_CHANNELS.ao_ch_4,AO_BOX_CHANNELS.ao_ch_9, AO_BOX_CHANNELS.ao_ch_12, 5000)
        resource = self.hardware_settings.dsa_resource
        self.analyzer = HP3567A(resource)
        self.voltage_measurement_switch = VoltageMeasurementSwitch(self.analyzer)

        self.temperature_controller = LakeShore211TemperatureSensor("COM9")

        self.init_analyzer()

    def init_analyzer(self):
        dev = self.analyzer
        dev.abort()
        dev.calibrate()
        dev.set_source_voltage(6.6)
        #dev.output_state(True)
        #time.sleep(2)
        #dev.output_state(False)
        #print(HP35670A_MODES.FFT)
        dev.select_instrument_mode(HP35670A_MODES.FFT)
        dev.switch_input(HP35670A_INPUTS.INP2, False)
        dev.select_active_traces(HP35670A_CALC.CALC1, HP35670A_TRACES.A)
        #dev.select_real_format(64)
        dev.select_ascii_format()
        dev.select_power_spectrum_function(HP35670A_CALC.CALC1)
        dev.select_voltage_unit(HP35670A_CALC.CALC1)
        dev.switch_calibration(False)
        #dev.set_average_count(50)
        #dev.set_display_update_rate(1)
        #dev.set_frequency_resolution(1600)
        #dev.set_frequency_start(0)
        #dev.set_frequency_stop(102.4,"KHZ")
        #print(dev.get_points_number(HP35670A_CALC.CALC1))
        #dev.init_instrument()
        #dev.wait_operation_complete()
        #print(dev.get_data(HP35670A_CALC.CALC1))
        
    def init_timetrace_measurement(self):
#OUTPUT @Analyzer;"FREQ:STAR 0"
#OUTPUT @Analyzer;"FREQ:STOP "&VAL$(Freqstopvalue)&" HZ"
#OUTPUT @Analyzer;"CALC1:UNIT:VOLT 'V'"

#Timestep=400/(Freqstopvalue-0)/1024

#OUTPUT @Analyzer;"MEM:DEL:ALL"
#OUTPUT @Analyzer;"TCAP:LENG "&VAL$(Blocks)&" BLK"
#CONTROL @Sys;SET ("*NAME":"Noisepanel/Status")
#CONTROL @Sys;SET ("PEN":24)
#CONTROL @Sys;SET ("VALUE":"Getting data...")
#OUTPUT @Analyzer;"TCAP:MALL"
#OUTPUT @Analyzer;"TCAP;*WAI"
#OUTPUT @Analyzer;"FORM REAL,64"
#OUTPUT @Analyzer;"SENSE:DATA? TCAP1;*WAI"
#ENTER @Analyzer USING "%,A,D";Term$,Ii
#ENTER @Analyzer USING "%,"&VAL$(Ii)&"D";Bytes
#P=Bytes/8
#Records=P/1024
#!PRINT Records
#REDIM Y(1:Blocks,1:1024)
#Step=INT(P/30000)+1
#!REDIM Ydata(1:30000)
#!REDIM Xdata(1:30000)
#CONTROL @Sys;SET ("*NAME":"Noisepanel/Noisespectrum","POINT CAPACITY":30000)
#IF Step=1 THEN
#REDIM Ydata(1:INT(P))
#REDIM Xdata(1:INT(P))
#END IF
#ENTER @Analyzer_bin;Y(*)
#ENTER @Analyzer;Term$
#CREATE Directory$&F$&Part$,20
#ASSIGN @File TO Directory$&F$&Part$;FORMAT ON

        pass

    
    def switch_voltage_measurement_relay_to(self, value):
        if value == "sample":
            self.voltage_measurement_switch.switch_to_sample_gate()
            #self.analyzer.output_state(True)
            #self.wait_for_stabilization_after_switch()
        elif value == "main":
            self.voltage_measurement_switch.switch_to_main()
            #self.analyzer.output_state(False)
            #self.wait_for_stabilization_after_switch()
        else:
            return

    def prepare_to_set_voltages(self):
        self.switch_voltage_measurement_relay_to("sample")
        #### set averaging to low values
        self.ds_mult.set_nplc(0.02)
        self.ds_mult.set_trigger_count(5)
        self.ds_mult.switch_high_ohmic_mode(True)
        self.ds_mult.set_function(HP34401A_FUNCTIONS.AVER)
        # switching averafing off
        self.ds_mult.switch_stat(False)
        self.ds_mult.switch_autorange(True)

        self.gs_mult.set_nplc(0.02)
        self.gs_mult.set_trigger_count(5)
        self.gs_mult.switch_high_ohmic_mode(True)
        self.gs_mult.set_function(HP34401A_FUNCTIONS.AVER)
        # switching averafing off
        self.gs_mult.switch_stat(False)
        self.gs_mult.switch_autorange(True)


    def prepare_to_measure_voltages(self):
        ### set averaging to high values
        self.ds_mult.set_nplc(10)
        self.ds_mult.set_trigger_count(10)
        self.ds_mult.switch_high_ohmic_mode(True)
        self.ds_mult.set_function(HP34401A_FUNCTIONS.AVER)
        # switching averafing on
        self.ds_mult.switch_stat(True)
        self.ds_mult.switch_autorange(True)

        self.gs_mult.set_nplc(10)
        self.gs_mult.set_trigger_count(10)
        self.gs_mult.switch_high_ohmic_mode(True)
        self.gs_mult.set_function(HP34401A_FUNCTIONS.AVER)
        # switching averafing on
        self.gs_mult.switch_stat(True)
        self.gs_mult.switch_autorange(True)


    def prepare_to_measure_spectrum(self):
        self.switch_voltage_measurement_relay_to("main")
        self.wait_for_stabilization_after_switch()
        

    def prepare_to_measure_timetrace(self):
        self.switch_voltage_measurement_relay_to("main")
        self.wait_for_stabilization_after_switch()

    def perform_param_measurement(self, measure_average = True):
        self.switch_voltage_measurement_relay_to("sample")
        self.wait_for_stabilization_after_switch()
        sample_voltage = self._fans_smu.read_drain_source_voltage(measure_average)
        gate_voltage = self._fans_smu.read_gate_voltage(measure_average)
        self.switch_voltage_measurement_relay_to("main")
        self.wait_for_stabilization_after_switch()
        main_voltage = self._fans_smu.read_main_voltage(measure_average)
        temperature = self.temperature_controller.temperature
        return (sample_voltage,main_voltage, gate_voltage, temperature)

    def perform_start_param_measurement(self):
        #self.switch_voltage_measurement_relay_to("sample")
        #self.wait_for_stabilization_after_switch()
        #sample_voltage = self._fans_smu.read_drain_source_voltage()
        #gate_voltage = self._fans_smu.read_gate_voltage()
        #self.switch_voltage_measurement_relay_to("main")
        #self.wait_for_stabilization_after_switch()
        #main_voltage = self._fans_smu.read_main_voltage()
        #temperature = self.temperature_controller.temperature
        sample_voltage,main_voltage, gate_voltage, temperature = self.perform_param_measurement(True)
        self._measurement_info.update_start_values(main_voltage, sample_voltage, gate_voltage,temperature)
        #self._measurement_info.start_sample_voltage = sample_voltage #np.random.random_sample()
        #self._measurement_info.start_main_voltage = main_voltage #np.random.random_sample()
        #self._measurement_info.start_gate_voltage = gate_voltage
        self.send_start_measurement_info()

    def perform_end_param_measurement(self):
        #self.switch_voltage_measurement_relay_to("sample")
        #sample_voltage = self._fans_smu.read_drain_source_voltage()
        #gate_voltage = self._fans_smu.read_gate_voltage()
        #self.switch_voltage_measurement_relay_to("main")
        #main_voltage = self._fans_smu.read_main_voltage()
        #temperature = self.temperature_controller.temperature
        sample_voltage,main_voltage, gate_voltage, temperature = self.perform_param_measurement(True)
        self._measurement_info.update_end_values(main_voltage, sample_voltage, gate_voltage,temperature)
        #self._measurement_info.end_sample_voltage = sample_voltage #= np.random.random_sample()
        #self._measurement_info.end_main_voltage = main_voltage #= np.random.random_sample()
        #self._measurement_info.end_gate_voltage = gate_voltage
        self.send_end_measurement_info()

    def perform_single_value_measurement(self):
        assert isinstance(self.experiment_settings, ExperimentSettings)
        #counter = 0
        screen_update = self.experiment_settings.display_refresh  #10;
        total_averaging = self.experiment_settings.averages;
        dev = self.analyzer
        
        #self._spectrum_ranges = {0: (1,1600,1),1:(64,102400,64)}
        for rng, (start,stop,step) in self._spectrum_ranges.items():
            dev.set_average_count(total_averaging)
            dev.set_display_update_rate(screen_update)
            resolution = int(stop/step)
            dev.set_frequency_resolution(resolution)
            dev.set_frequency_start(start)
            dev.set_frequency_stop(stop)
                
            print(dev.get_points_number(HP35670A_CALC.CALC1))

            dev.init_instrument()
            dev.wait_operation_complete()
            data = dev.get_data(HP35670A_CALC.CALC1)
            self.update_spectrum(data, rng, screen_update)

        data = self.update_resulting_spectrum()
        #if self.calibration:
        #    self.calibration.set_amplifier_gain("second_amp",self._measurement_info.second_amplifier_gain)
        #    data = self.calibration.apply_calibration(data) 
            
        data = data.transpose()
        self._experiment_writer.write_measurement(data)   ##.write_measurement()
        
       
       
    
        
       

    def perform_non_gated_single_value_measurement(self):
        raise NotImplementedError()



    def switch_transistor(self, transistor):
        print("performing switch transistor")

    def set_front_gate_voltage(self, voltage):
        print("performing setting fg voltage: {0}".format(voltage))
        self._fans_smu.smu_set_gate_voltage(voltage)
        print("done setting ds value")

    
    def set_drain_source_voltage(self, voltage):
        print("performing setting ds voltage: {0}".format(voltage))
        self._fans_smu.smu_set_drain_source_voltage(voltage)
        print("done setting gs value")

   









if __name__ == "__main__":
    
    cfg = Configuration()
    #exp = SimulateExperiment(None,None)

    eh = ExperimentHandler(None)
    eh.run()
    
    #exp = PerformExperiment(None,None)
    #exp.initialize_settings(cfg)
    #exp.initialize_hardware()
    #exp.initialize_calibration()

    #exp.perform_experiment()





    #cfg = Configuration()
    #exp = ExperimentProcess(simulate = True)
    #exp.initialize_settings(cfg)
    #exp.perform_experiment()
    


 