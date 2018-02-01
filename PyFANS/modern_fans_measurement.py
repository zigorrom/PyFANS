class MessageHandler(object):
    """ 
    This object is supposed to be used for sending messages to UI from measurement and experiment
    """

    def __init__(self):
        pass




class Measurement(object):
    def __init__(self, measurement_name, measurement_counter, load_resistance, second_amplifier_gain, message_handler = None):
        self._measurement_name = measurement_name
        self._measurement_counter = measurement_counter
        self._load_resistance = load_resistance
        self._second_amplifier_gain = second_amplifier_gain
        self._measurement_info = None
        self._measurement_is_opened = False
        self._message_handler = message_handler

    def is_ready_to_start(self):
        return self._measurement_is_opened

    def execute_measurement(self):
        if not self.is_ready_to_start():
            pass


        pass

    def __enter__(self):
        self.open_measurement()
        return self

    def __exit__(self,type,value,traceback):
        #check for errors
        self.close_measurement()

    def open_measurement(self):
        #1. create measurement_info
        #2. open files for saving data
        self._measurement_is_opened = True
        pass

    def close_measurement(self):
        # close files for saving data
        self._measurement_is_opened = False
        pass


    
    