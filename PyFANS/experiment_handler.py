import sys
import os
import time
import math
import numpy as np
from collections import deque
from os.path import join
from PyQt4 import QtCore
import pyqtgraph as pg

import multiprocessing
from multiprocessing import JoinableQueue
from multiprocessing import Process
from multiprocessing import Event

import plot as plt 
import process_communication_protocol as pcp
from nodes import ExperimentSettings, ValueRange, HardwareSettings
import configuration as config

from measurement_data_structures import MeasurementInfo
from experiment_writer import ExperimentWriter
from calibration import Calibration, CalibrationSimple
import experiment as exp


class ExperimentController(QtCore.QObject):
    def __init__(self, spectrum_plot=None, timetrace_plot=None, status_object = None, measurement_ranges = {0: (0,1600,1),1:(0,102400,64)},  parent = None):
        super().__init__(parent)
        if spectrum_plot:
            assert isinstance(spectrum_plot, plt.SpectrumPlotWidget)
        self._spectrum_plot = spectrum_plot
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
        experiment_thread = self.get_experiment_handler()
        assert isinstance(experiment_thread, ExperimentHandler)
        self._experiment_thread = experiment_thread  #ExperimentHandler(self._input_data_queue) #ExperimentProcess(self._input_data_queue,True)

    def get_experiment_handler(self):
        raise NotImplementedError()

    def _command_received(self,cmd):
        assert isinstance(cmd, pcp.ExperimentCommands), "Command not found"
        self._status_object.send_message("Command received: {0}".format(cmd.name)) #pcp.ExperimentCommands[cmd]))

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

    def _on_progress_changed_received(self, progress_value):
        print("progress changed received")
        self._status_object.send_progress_changed(progress_value)

    #def _on_measurement_info_arrived(self,measurement_info):
    #    print("measurement_info_arrived")
    #    self._status_object.send_measurement_info_changed(measurement_info)
    #    #if isinstance(data_dict, dict):
        #    for k,v in data_dict.items():
                #self._status_object.send_value_changed(k,v)

    def _on_update_resulting_spectrum(self,data):
        frequency = data[pcp.FREQUENCIES]
        spectrum_data = data[pcp.DATA]
        self._spectrum_plot.updata_resulting_spectrum(frequency,spectrum_data)


    def _update_gui(self):
        try:
            #print("refreshing: {0}".format(self._counter))
            self._counter+=1
            data = self._visualization_deque.popleft()
            cmd_format = "{0} command received"

            cmd = data.get(pcp.COMMAND)
            #print(cmd_format.format(ExperimentCommands[cmd]))
            
            if cmd is pcp.ExperimentCommands.DATA:
                index = data[pcp.INDEX]
                rang = data[pcp.SPECTRUM_RANGE]
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

    def wait_all_threads(self):
        pass

class ProcessingThread(QtCore.QThread):
    
    threadStarted = QtCore.pyqtSignal()
    threadStopped = QtCore.pyqtSignal()
    commandReceived = QtCore.pyqtSignal(pcp.ExperimentCommands) #int)
    experimentStarted = QtCore.pyqtSignal(dict)
    experimentFinished = QtCore.pyqtSignal()
    measurementStarted = QtCore.pyqtSignal(dict)
    measurementFinished = QtCore.pyqtSignal()
    measurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    startMeasurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    endMeasurementDataArrived = QtCore.pyqtSignal(MeasurementInfo)
    resulting_spectrum_update = QtCore.pyqtSignal(dict)
    log_message_received = QtCore.pyqtSignal(str)
    progressChanged = QtCore.pyqtSignal(int)

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
                cmd = data.get(pcp.COMMAND)
                param = data.get(pcp.PARAMETER)
                
                #print(cmd_format.format(ExperimentCommands[cmd]))
                if cmd is None:
                    continue
                elif cmd is pcp.ExperimentCommands.EXPERIMENT_STARTED:
                    self.commandReceived.emit(pcp.ExperimentCommands.EXPERIMENT_STARTED)
                    self.experimentStarted.emit(param)
                    continue

                elif cmd is pcp.ExperimentCommands.EXPERIMENT_FINISHED:
                    self.alive = False
                    self.commandReceived.emit(pcp.ExperimentCommands.EXPERIMENT_FINISHED)
                    self.experimentFinished.emit()
                    break

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_STARTED:
                    self.commandReceived.emit(pcp.ExperimentCommands.MEASUREMENT_STARTED)
                    self.measurementStarted.emit(param)
                    continue

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_FINISHED:
                    self.commandReceived.emit(pcp.ExperimentCommands.MEASUREMENT_FINISHED)
                    self.measurementFinished.emit()
                    continue

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_INFO:
                    self.measurementDataArrived.emit(param)

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_INFO_START:
                    self.startMeasurementDataArrived.emit(param)

                elif cmd is pcp.ExperimentCommands.MEASUREMENT_INFO_END:
                    self.endMeasurementDataArrived.emit(param)

                elif cmd is pcp.ExperimentCommands.DATA:
                    self._visualization_queue.append(data)   
                     
                elif cmd is pcp.ExperimentCommands.SPECTRUM_DATA:
                    self.resulting_spectrum_update.emit(data)
                
                elif cmd is pcp.ExperimentCommands.LOG_MESSAGE:
                    self.log_message_received.emit(param)

                elif cmd is pcp.ExperimentCommands.PROGRESS_CHANGED:
                    self.progressChanged.emit(param)

            except EOFError as e:
                print(str(e))
                break
            except:
                pass

        self.alive = False


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
    def __init__(self, input_data_queue = None):
        super().__init__()
        self._exit = Event()
        self._experiment  = None
        self._input_data_queue = input_data_queue

    def stop(self):
        self._exit.set()

    def run(self):
        #if self._input_data_queue:
        #sys.stdout = LoggingQueuedStream(self._input_data_queue) #open("log.txt", "w")
        #else:
        #    sys.stdout = open("log.txt", "w")

        cfg = config.Configuration()
        exp_settings = cfg.get_node_from_path("Settings.ExperimentSettings")
        assert isinstance(exp_settings, ExperimentSettings)
        simulate = exp_settings.simulate_experiment

        if simulate:
            self._experiment = exp.SimulateExperiment(self._input_data_queue, self._exit)
        else:
            #self._experiment = PerformExperiment(self._input_data_queue, self._exit)
            experiment = self.get_experiment()
            #assert isinstance(exp.Experiment), "Experiment has wrong type"
            assert isinstance(experiment, exp.Experiment), "Experiment is not inherited from Experiment type"
            self._experiment = experiment #mfe.FANSExperiment(self._input_data_queue, self._exit)
        
        self._experiment.initialize_settings(cfg)
        self._experiment.initialize_hardware()
        self._experiment.initialize_calibration()
        self._experiment.perform_experiment()

    def get_experiment(self):
        raise NotImplementedError()



####
####this import should be after experiment class since it is required in modern_fans_experiment for import 
#import modern_fans_experiment as mfe

if __name__ == "__main__":
    
    #cfg = Configuration()
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
    


 ### LEGACY setup
    
#class PerformExperiment(Experiment):
#    def __init__(self, input_data_queue = None, stop_event = None):
#        Experiment.__init__(self,False, input_data_queue, stop_event)  

#    def initialize_hardware(self):
#        assert isinstance(self.hardware_settings, HardwareSettings)

#        resource = self.hardware_settings.fans_controller_resource
#        #resource =  "USB0::0x0957::0x1718::TW52524501::INSTR"    #self._gpib_resources[selected_resource]
#        self._fans_controller = FANS_CONTROLLER(resource)
#        resource = self.hardware_settings.main_sample_multimeter_resource
#        #resource = "GPIB0::23::INSTR" #self._gpib_resources[selected_resource]
#        self.ds_mult = HP34401A(resource)
#        resource = self.hardware_settings.gate_multimeter_resource
#        self.gs_mult = HP34401A(resource)

#        sample_motor_pin = get_ao_box_channel_from_number(self.hardware_settings.sample_motor_channel)
#        gate_motor_pin = get_ao_box_channel_from_number(self.hardware_settings.gate_motor_channel)
#        sample_relay = get_ao_box_channel_from_number(self.hardware_settings.sample_relay_channel)
#        gate_relay = get_ao_box_channel_from_number(self.hardware_settings.gate_relay_channel)

#        self._fans_smu = HybridSMU_System(self._fans_controller, AO_BOX_CHANNELS.ao_ch_1, AO_BOX_CHANNELS.ao_ch_4, self.ds_mult, AO_BOX_CHANNELS.ao_ch_9, AO_BOX_CHANNELS.ao_ch_12, self.gs_mult, self.ds_mult, 5000)
#        #self._fans_smu = ManualSMU(self._fans_controller, AO_BOX_CHANNELS.ao_ch_1, AO_BOX_CHANNELS.ao_ch_4,AO_BOX_CHANNELS.ao_ch_9, AO_BOX_CHANNELS.ao_ch_12, 5000)
#        resource = self.hardware_settings.dsa_resource
#        self.analyzer = HP3567A(resource)
#        self.voltage_measurement_switch = VoltageMeasurementSwitch(self.analyzer)

#        self.temperature_controller = LakeShore211TemperatureSensor("COM9")

#        self.init_analyzer()

#    def init_analyzer(self):
#        dev = self.analyzer
#        dev.abort()
#        dev.calibrate()
#        dev.set_source_voltage(6.6)
#        #dev.output_state(True)
#        #time.sleep(2)
#        #dev.output_state(False)
#        #print(HP35670A_MODES.FFT)
#        dev.select_instrument_mode(HP35670A_MODES.FFT)
#        dev.switch_input(HP35670A_INPUTS.INP2, False)
#        dev.select_active_traces(HP35670A_CALC.CALC1, HP35670A_TRACES.A)
#        #dev.select_real_format(64)
#        dev.select_ascii_format()
#        dev.select_power_spectrum_function(HP35670A_CALC.CALC1)
#        dev.select_voltage_unit(HP35670A_CALC.CALC1)
#        dev.switch_calibration(False)
#        #dev.set_average_count(50)
#        #dev.set_display_update_rate(1)
#        #dev.set_frequency_resolution(1600)
#        #dev.set_frequency_start(0)
#        #dev.set_frequency_stop(102.4,"KHZ")
#        #print(dev.get_points_number(HP35670A_CALC.CALC1))
#        #dev.init_instrument()
#        #dev.wait_operation_complete()
#        #print(dev.get_data(HP35670A_CALC.CALC1))
        
#    def init_timetrace_measurement(self):
##OUTPUT @Analyzer;"FREQ:STAR 0"
##OUTPUT @Analyzer;"FREQ:STOP "&VAL$(Freqstopvalue)&" HZ"
##OUTPUT @Analyzer;"CALC1:UNIT:VOLT 'V'"

##Timestep=400/(Freqstopvalue-0)/1024

##OUTPUT @Analyzer;"MEM:DEL:ALL"
##OUTPUT @Analyzer;"TCAP:LENG "&VAL$(Blocks)&" BLK"
##CONTROL @Sys;SET ("*NAME":"Noisepanel/Status")
##CONTROL @Sys;SET ("PEN":24)
##CONTROL @Sys;SET ("VALUE":"Getting data...")
##OUTPUT @Analyzer;"TCAP:MALL"
##OUTPUT @Analyzer;"TCAP;*WAI"
##OUTPUT @Analyzer;"FORM REAL,64"
##OUTPUT @Analyzer;"SENSE:DATA? TCAP1;*WAI"
##ENTER @Analyzer USING "%,A,D";Term$,Ii
##ENTER @Analyzer USING "%,"&VAL$(Ii)&"D";Bytes
##P=Bytes/8
##Records=P/1024
##!PRINT Records
##REDIM Y(1:Blocks,1:1024)
##Step=INT(P/30000)+1
##!REDIM Ydata(1:30000)
##!REDIM Xdata(1:30000)
##CONTROL @Sys;SET ("*NAME":"Noisepanel/Noisespectrum","POINT CAPACITY":30000)
##IF Step=1 THEN
##REDIM Ydata(1:INT(P))
##REDIM Xdata(1:INT(P))
##END IF
##ENTER @Analyzer_bin;Y(*)
##ENTER @Analyzer;Term$
##CREATE Directory$&F$&Part$,20
##ASSIGN @File TO Directory$&F$&Part$;FORMAT ON

#        pass

    
#    def switch_voltage_measurement_relay_to(self, value):
#        if value == "sample":
#            self.voltage_measurement_switch.switch_to_sample_gate()
#            #self.analyzer.output_state(True)
#            #self.wait_for_stabilization_after_switch()
#        elif value == "main":
#            self.voltage_measurement_switch.switch_to_main()
#            #self.analyzer.output_state(False)
#            #self.wait_for_stabilization_after_switch()
#        else:
#            return

#    def prepare_to_set_voltages(self):
#        self.switch_voltage_measurement_relay_to("sample")
#        #### set averaging to low values
#        self.ds_mult.set_nplc(0.02)
#        self.ds_mult.set_trigger_count(5)
#        self.ds_mult.switch_high_ohmic_mode(True)
#        self.ds_mult.set_function(HP34401A_FUNCTIONS.AVER)
#        # switching averafing off
#        self.ds_mult.switch_stat(False)
#        self.ds_mult.switch_autorange(True)

#        self.gs_mult.set_nplc(0.02)
#        self.gs_mult.set_trigger_count(5)
#        self.gs_mult.switch_high_ohmic_mode(True)
#        self.gs_mult.set_function(HP34401A_FUNCTIONS.AVER)
#        # switching averafing off
#        self.gs_mult.switch_stat(False)
#        self.gs_mult.switch_autorange(True)


#    def prepare_to_measure_voltages(self):
#        ### set averaging to high values
#        self.ds_mult.set_nplc(10)
#        self.ds_mult.set_trigger_count(10)
#        self.ds_mult.switch_high_ohmic_mode(True)
#        self.ds_mult.set_function(HP34401A_FUNCTIONS.AVER)
#        # switching averafing on
#        self.ds_mult.switch_stat(True)
#        self.ds_mult.switch_autorange(True)

#        self.gs_mult.set_nplc(10)
#        self.gs_mult.set_trigger_count(10)
#        self.gs_mult.switch_high_ohmic_mode(True)
#        self.gs_mult.set_function(HP34401A_FUNCTIONS.AVER)
#        # switching averafing on
#        self.gs_mult.switch_stat(True)
#        self.gs_mult.switch_autorange(True)


#    def prepare_to_measure_spectrum(self):
#        self.switch_voltage_measurement_relay_to("main")
#        self.wait_for_stabilization_after_switch()
        

#    def prepare_to_measure_timetrace(self):
#        self.switch_voltage_measurement_relay_to("main")
#        self.wait_for_stabilization_after_switch()

#    def perform_param_measurement(self, measure_average = True):
#        self.switch_voltage_measurement_relay_to("sample")
#        self.wait_for_stabilization_after_switch()
#        sample_voltage = self._fans_smu.read_drain_source_voltage(measure_average)
#        gate_voltage = self._fans_smu.read_gate_voltage(measure_average)
#        self.switch_voltage_measurement_relay_to("main")
#        self.wait_for_stabilization_after_switch()
#        main_voltage = self._fans_smu.read_main_voltage(measure_average)
#        temperature = self.temperature_controller.temperature
#        return (sample_voltage,main_voltage, gate_voltage, temperature)

#    def perform_start_param_measurement(self):
#        #self.switch_voltage_measurement_relay_to("sample")
#        #self.wait_for_stabilization_after_switch()
#        #sample_voltage = self._fans_smu.read_drain_source_voltage()
#        #gate_voltage = self._fans_smu.read_gate_voltage()
#        #self.switch_voltage_measurement_relay_to("main")
#        #self.wait_for_stabilization_after_switch()
#        #main_voltage = self._fans_smu.read_main_voltage()
#        #temperature = self.temperature_controller.temperature
#        sample_voltage,main_voltage, gate_voltage, temperature = self.perform_param_measurement(True)
#        self._measurement_info.update_start_values(main_voltage, sample_voltage, gate_voltage,temperature)
#        #self._measurement_info.start_sample_voltage = sample_voltage #np.random.random_sample()
#        #self._measurement_info.start_main_voltage = main_voltage #np.random.random_sample()
#        #self._measurement_info.start_gate_voltage = gate_voltage
#        self.send_start_measurement_info()

#    def perform_end_param_measurement(self):
#        #self.switch_voltage_measurement_relay_to("sample")
#        #sample_voltage = self._fans_smu.read_drain_source_voltage()
#        #gate_voltage = self._fans_smu.read_gate_voltage()
#        #self.switch_voltage_measurement_relay_to("main")
#        #main_voltage = self._fans_smu.read_main_voltage()
#        #temperature = self.temperature_controller.temperature
#        sample_voltage,main_voltage, gate_voltage, temperature = self.perform_param_measurement(True)
#        self._measurement_info.update_end_values(main_voltage, sample_voltage, gate_voltage,temperature)
#        #self._measurement_info.end_sample_voltage = sample_voltage #= np.random.random_sample()
#        #self._measurement_info.end_main_voltage = main_voltage #= np.random.random_sample()
#        #self._measurement_info.end_gate_voltage = gate_voltage
#        self.send_end_measurement_info()

#    def perform_single_value_measurement(self):
#        assert isinstance(self.experiment_settings, ExperimentSettings)
#        #counter = 0
#        screen_update = self.experiment_settings.display_refresh  #10;
#        total_averaging = self.experiment_settings.averages;
#        dev = self.analyzer
        
#        #self._spectrum_ranges = {0: (1,1600,1),1:(64,102400,64)}
#        for rng, (start,stop,step) in self._spectrum_ranges.items():
#            dev.set_average_count(total_averaging)
#            dev.set_display_update_rate(screen_update)
#            resolution = int(stop/step)
#            dev.set_frequency_resolution(resolution)
#            dev.set_frequency_start(start)
#            dev.set_frequency_stop(stop)
                
#            print(dev.get_points_number(HP35670A_CALC.CALC1))

#            dev.init_instrument()
#            dev.wait_operation_complete()
#            data = dev.get_data(HP35670A_CALC.CALC1)
#            self.update_spectrum(data, rng, screen_update)

#        data = self.update_resulting_spectrum()
#        #if self.calibration:
#        #    self.calibration.set_amplifier_gain("second_amp",self._measurement_info.second_amplifier_gain)
#        #    data = self.calibration.apply_calibration(data) 
            
#        data = data.transpose()
#        self._experiment_writer.write_measurement(data)   ##.write_measurement()
        
       
       
    
        
       

#    def perform_non_gated_single_value_measurement(self):
#        raise NotImplementedError()



#    def switch_transistor(self, transistor):
#        print("performing switch transistor")

#    def set_front_gate_voltage(self, voltage):
#        print("performing setting fg voltage: {0}".format(voltage))
#        self._fans_smu.smu_set_gate_voltage(voltage)
#        print("done setting ds value")

    
#    def set_drain_source_voltage(self, voltage):
#        print("performing setting ds voltage: {0}".format(voltage))
#        self._fans_smu.smu_set_drain_source_voltage(voltage)
#        print("done setting gs value")

   