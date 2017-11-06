import serial
class LakeShore211TemperatureSensor:
    def __init__(self, resource):
        
        #rm = visa.ResourceManager()
        #self.instrument = rm.open_resource(resource, write_termination='\n', read_termination = '\n') #write termination
        self.instrument = serial.Serial(resource, baudrate = 9800,  parity=serial.PARITY_ODD, bytesize = serial.SEVENBITS , stopbits=serial.STOPBITS_ONE, xonxoff = True)
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


class TemperatureController:
    def __init__(self, temperature_sensor):
        self.temperature_sensor = temperature_sensor

    def set_temperature(self,temperature):
        pass




    




if __name__ == "__main__":
    import time

    ts = LakeShore211TemperatureSensor("COM9")
    for i in range(100):
        print(ts.temperature)
        time.sleep(0.5)
          