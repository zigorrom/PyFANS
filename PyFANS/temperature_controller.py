import modern_fans_pid_controller as mfpid

import serial
class LakeShore211TemperatureSensor:
    def __init__(self, resource):
        
        #rm = visa.ResourceManager()
        #self.instrument = rm.open_resource(resource, write_termination='\n', read_termination = '\n') #write termination
        self.instrument = serial.Serial(resource, baudrate = 9600,  parity=serial.PARITY_ODD, bytesize = serial.SEVENBITS , stopbits=serial.STOPBITS_ONE, xonxoff = True)
        self._last_temperature = 300
        
    def _read_temperature(self):
        self.instrument.write("KRDG?\r\n".encode())
        result = self.instrument.readline()
        value = float(result)
        self._last_temperature = value
        return value


    @property
    def temperature(self):
        return self._read_temperature()

    @property
    def last_temperature(self):
        return self._last_temperature

class LeyboldStirlingCooler(object):
    MIN_ALLOWABLE_TEMP = 70
    MAX_ALLOWABLE_TEMP = 300

    STATE_ON, STATE_OFF, RESET = STATES = (1,0,3)
    START_CHAR = chr(2)
    END_CHAR = chr(13)

    def __init__(self, resource, drive_number = 18):
        self.instrument = serial.Serial(resource, baudrate = 9600, parity=serial.PARITY_EVEN, bytesize=serial.SEVENBITS,stopbits=serial.STOPBITS_ONE)
        self._drive_number = drive_number
    
    def write(self, message):
        #if not isinstance(message, str):
        #    message = str(message).encode()
        self.instrument.write(message)

    def readline(self):
        return self.instrument.readline()

    def set_state(self, state):
        assert state in self.STATES, "wrong state"
        query = "{0}SYS{1}{2}{3}".format(self.START_CHAR,self._drive_number,state, END_CHAR)
        self.write(query.encode())
        result = self.readline()
        print(result)

    def switch_on(self):
        self.set_state(self.STATE_ON)

    def switch_off(self):
        self.set_state(self.STATE_OFF)

    def set_temperature_setpoint(self, temperature):
        if temperature< self.MIN_ALLOWABLE_TEMP:
            temperature = self.MIN_ALLOWABLE_TEMP
        elif temperature> self.MAX_ALLOWABLE_TEMP:
            temperature = self.MAX_ALLOWABLE_TEMP

        temperature = round(temperature*10)

        query = "{0}TMP{1}{2}{3}".format(start_char,self._drive_number,temperature ,end_char)
        self.write(query.encode())
        print("RESULT")
        result = self.instrument.readline()
        print(result)


    def read_info(self):
        start_char = chr(2)
        end_char = chr(13)
        query = "{0}SYS181{1}".format(start_char,end_char)
        print(query)
        #print(query.encode())
        self.instrument.write(query.encode())
        print("RESULT")
        result = self.instrument.readline()
        print(result)

    def set_temperature_value(self, temp):
        if temp< self.MIN_ALLOWABLE_TEMP:
            temp = self.MIN_ALLOWABLE_TEMP
        elif temp> self.MAX_ALLOWABLE_TEMP:
            temp = self.MAX_ALLOWABLE_TEMP

        temp = round(temp*10)

        start_char = chr(2)
        end_char = chr(13)
        query = "{0}TMP18{1}{2}".format(start_char,temp,end_char)
        self.instrument.write(query.encode())
        print("RESULT")
        result = self.instrument.readline()
        print(result)


class TemperatureController(mfpid.FANS_PID):
    def __init__(self, temperature_sensor, temperature_setter, filename = None):
        super().__init__(1,1,0,0.02, 60, 1200)
        self.sampling_time = 1.0
        self.guard = 10
        assert isinstance(temperature_sensor, LakeShore211TemperatureSensor), "Wrong type of temperature sensor"
        assert isinstance(temperature_setter, LeyboldStirlingCooler), "Wrong type of cooler"

        self._temperature_sensor = temperature_sensor
        self._temperature_setter = temperature_setter
        self._filename = filename


    def get_temperature(self):
        return self._temperature_sensor.temperature

    def set_temperature(self,temperature):
        try:
            self.SetPoint = temperature
            counter = 0
            last_update = self._temperature_sensor.temperature
            while True:
                print("reading feedback")
                feedback = self._temperature_sensor.temperature
                print("updating pid")
                update = self.update(feedback) + last_update
                print("setting temperature")
                self._temperature_setter.set_temperature_value(update)
                last_update = update
                counter +=1 
                print("{0} - CURRENT TEMPERATURE: {1}".format(counter,feedback))


        except mfpid.PID_ErrorNotChangingException as e:
            print("error not changing")
        except mfpid.PID_ReachedDesiredErrorException as e:
            print("temperature is set")
        except mfpid.PID_ReachedMaximumAllowedUpdatesException as e:
            print("max counts reached")
        finally:
            return True



    
def test_sensor():
    import time

    ts = LakeShore211TemperatureSensor("COM9")
    for i in range(100):
        print(ts.temperature)
        time.sleep(0.5)
    

def test_cooler():
    c = LeyboldStirlingCooler("COM11")
    c.read_info()
    c.set_temperature_value(170)

def test_controller():
    ts = LakeShore211TemperatureSensor("COM9")
    c = LeyboldStirlingCooler("COM11")
    controller = TemperatureController(ts, c)
    controller.set_temperature(150)



if __name__ == "__main__":
    #test_sensor()      
##    test_cooler()
    test_controller()
