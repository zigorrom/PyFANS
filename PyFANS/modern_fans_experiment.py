import time
import numpy as np
import experiment_handler as eh
import modern_fans_controller as mfans
import modern_agilent_u2542a as mdaq
import modern_fans_smu as msmu
import temperature_controller as tc
import math
from configuration import Configuration
from multiprocessing import Process, Event
from scipy.signal import periodogram
from scipy.signal import decimate
from nodes import ExperimentSettings, ValueRange, HardwareSettings
from process_communication_protocol import *

def get_fans_ai_channels_from_number(number):
    assert isinstance(number, int), "Number should be integer"
    assert (number>0 and number<9),"Wrong channel number!"
    return mfans.FANS_AI_CHANNELS(number)

def get_fans_ao_channels_from_number(number):
    assert isinstance(number, int), "Number should be integer"
    assert (number>0 and number<17),"Wrong channel number!"
    return mfans.FANS_AO_CHANNELS(number)

class FANSExperimentHandler(Process):
    def __init__(self, input_data_queue = None):
        super().__init__()
        self._exit = Event()
        self._experiment  = None
        self._input_data_queue = input_data_queue

    def stop(self):
        self._exit.set()

    def run(self):
        #if self._input_data_queue:
        #sys.stdout = eh.LoggingQueuedStream(self._input_data_queue) #open("log.txt", "w")
        #else:
        #    sys.stdout = open("log.txt", "w")

        cfg = Configuration()
        exp_settings = cfg.get_node_from_path("Settings.ExperimentSettings")
        assert isinstance(exp_settings, ExperimentSettings)
        simulate = exp_settings.simulate_experiment

        if simulate:
            self._experiment = eh.SimulateExperiment(self._input_data_queue, self._exit)
        else:
            self._experiment = FANSExperiment(self._input_data_queue, self._exit)
        
        self._experiment.initialize_settings(cfg)
        self._experiment.initialize_hardware()
        self._experiment.initialize_calibration()
        self._experiment.perform_experiment()


class FANSExperiment(eh.Experiment):
    def __init__(self, input_data_queue = None, stop_event = None):
        super().__init__(False, input_data_queue, stop_event)
        self._spectrum_ranges = {0: (0,5000,1),1:(0,250000,10)}
        self._spectrum_linking_frequencies = {0:(1,3000),1:(3000,250000)}
        self._frequencies = self._get_frequencies(self._spectrum_ranges)
        self._frequency_indexes = self._get_frequency_linking_indexes(self._spectrum_ranges, self._spectrum_linking_frequencies)
        pass
        #eh.Experiment.__init__(False, input_data_queue, stop_event)
         
    def initialize_hardware(self):
        resource = self.hardware_settings.fans_controller_resource
        self.fans_controller = mfans.FANS_CONTROLLER(resource)

        sample_motor_pin = get_fans_ao_channels_from_number(self.hardware_settings.sample_motor_channel)
        gate_motor_pin = get_fans_ao_channels_from_number(self.hardware_settings.gate_motor_channel)
        sample_relay = get_fans_ao_channels_from_number(self.hardware_settings.sample_relay_channel)
        gate_relay = get_fans_ao_channels_from_number(self.hardware_settings.gate_relay_channel)

        #sample_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_6
        #gate_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_7
        #main_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_8
        #self.acquistion_channel = mfans.FANS_AI_CHANNELS.AI_CH_1 ### here should be 1

        sample_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_6
        gate_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_8
        main_feedback_pin = mfans.FANS_AI_CHANNELS.AI_CH_7
        self.acquistion_channel = mfans.FANS_AI_CHANNELS.AI_CH_1 ### here should be 1

        drain_source_voltage_switch_channel = mfans.FANS_AO_CHANNELS.AO_CH_10

        self.load_resistance = self.experiment_settings.load_resistance
        self.sample_rate = 500000
        self.points_per_shot = 50000

        #self.fans_smu = msmu.FANS_SMU(self.fans_controller, sample_motor_pin, sample_relay, sample_feedback_pin, gate_motor_pin, gate_relay, gate_feedback_pin, main_feedback_pin)
        self.fans_smu = msmu.FANS_SMU_Specialized(self.fans_controller, sample_motor_pin, sample_relay, sample_feedback_pin, gate_motor_pin, gate_relay, gate_feedback_pin, main_feedback_pin, drain_source_voltage_switch_channel)
        self.fans_smu.set_smu_parameters(100, self.load_resistance)

        self.fans_acquisition = mfans.FANS_ACQUISITION(self.fans_controller)
        #self.temperature_controller = tc.LakeShore211TemperatureSensor("COM9")
       
    
              
         
    def prepare_to_set_voltages(self):
        self.fans_smu.init_smu_mode()

    def prepare_to_measure_voltages(self):
        self.fans_smu.init_smu_mode()
        self.wait_for_stabilization_after_switch(10)
    
    

    def prepare_to_measure_spectrum(self):
        self.fans_acquisition.initialize_acquisition(self.acquistion_channel, mfans.FILTER_CUTOFF_FREQUENCIES.F150, mfans.FILTER_GAINS.G1, mfans.PGA_GAINS.PGA_1)
        #self.fans_acquisition.initialize_acquisition(self.acquistion_channel, mfans.FILTER_CUTOFF_FREQUENCIES.F150, mfans.FILTER_GAINS.G1, mfans.PGA_GAINS.PGA_1)
        self.fans_acquisition.initialize_acquisition_params(self.sample_rate, self.points_per_shot, mfans.ACQUISITION_TYPE.CONT) 
        #switch off all output to the control circuit in order to reduce noiseness of the system
        self.fans_controller.switch_all_fans_output_state(mfans.SWITCH_STATES.OFF)
        self.wait_for_stabilization_after_switch(30)

    def prepare_to_measure_timetrace(self):
        return super().prepare_to_measure_timetrace()

    def perform_param_measurement(self):
        (sample_voltage,main_voltage, gate_voltage) = self.fans_smu.read_feedback_voltages()
        #temperature = self.temperature_controller.temperature
        return (sample_voltage,main_voltage, gate_voltage, 0)

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
        #counter = 0
        screen_update = self.experiment_settings.display_refresh  #10;
        total_averaging = self.experiment_settings.averages;
        adc = self.fans_acquisition

        fs = self.sample_rate
        npoints = self.points_per_shot

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


if __name__ == "__main__":

    cfg = Configuration()
    handl = FANSExperimentHandler(None)
    handl.run()