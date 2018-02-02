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
    def __init__(self, resource):
        self.instrument = serial.Serial(resource, baudrate = 9600, parity=serial.PARITY_EVEN, bytesize=serial.SEVENBITS,stopbits=serial.STOPBITS_ONE)

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


class TemperatureController:
    def __init__(self, temperature_sensor):
        self.temperature_sensor = temperature_sensor

    def set_temperature(self,temperature):
        pass




    
def test_sensor():
    import time

    ts = LakeShore211TemperatureSensor("COM9")
    for i in range(100):
        print(ts.temperature)
        time.sleep(0.5)
    

def test_cooler():
    c = LeyboldStirlingCooler("COM11")
    c.read_info()
    c.write_to_device()


if __name__ == "__main__":
    #test_sensor()      
    test_cooler()