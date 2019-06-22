import measurement_data_structures as mds
import modern_fans_controller as mfc
import modern_fans_smu as msmu
import fans_experiment_settings as fes

class MessageHandler(object):
    """ 
    This object is supposed to be used for sending messages to UI from measurement and experiment
    """

    def __init__(self):
        pass

class CancellationToken(object):
    def __init__(self):
        pass

class ProgressReport(object):
    def __init__(self):
        pass

class NotInitializedMeasurementError(Exception):
    pass

class FANSMeasurement(object):
    def __init__(self, measurement_name, measurement_counter, fans_controller, fans_smu, experiment_settings, message_handler = None):
        assert isinstance(experiment_settings, fes.ExperimentSettings)
        assert isinstance(fans_controller, mfc.FANS_CONTROLLER)
        assert isinstance(fans_smu, msmu.FANS_SMU)

        self._measurement_name = measurement_name
        self._measurement_counter = measurement_counter
        self._measurement_info = None
        self._measurement_is_opened = False
        self._fans_controller = fans_controller
        self._fans_smu = fans_smu
        self._experiment_settings = experiment_settings
        self._message_handler = message_handler

    @property
    def measurement_name(self):
        return self._measurement_name
    
    @measurement_name.setter
    def measurement_name(self, value):
        if isinstance(value, str):
            self._measurement_name = value

    @property
    def measurement_counter(self):
        return self._measurement_counter

    @measurement_counter.setter
    def measurement_counter(self, value):
        if isinstance(value, int):
            self._measurement_counter = value

    @property
    def measurement_info(self):
        return self._measurement_info

    def assert_ready_to_start(self):
        if not self._measurement_is_opened:
            raise NotInitializedMeasurementError()

    def __enter__(self):
        self.open_measurement()
        return self

    def __exit__(self,type,value,traceback):
        #check for errors
        self.close_measurement()

    def open_measurement(self):
        #1. create measurement_info
        self._measurement_info = mds.MeasurementInfo(self.measurement_name, self.measurement_counter, load_resistance = self._experiment_settings.load_resistance, second_amplifier_gain = self._experiment_settings.second_amp_coeff)
        #2. open files for saving data

        self._measurement_is_opened = True
        pass

    def close_measurement(self):
        # close files for saving data
        self._measurement_is_opened = False
        pass

    def execute_measurement(self, cancellation_token = None, progress_reporter = None):
        self.assert_ready_to_start()
        #with open measurement data file

        
            


    
    